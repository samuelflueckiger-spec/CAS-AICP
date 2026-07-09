#!/usr/bin/env python3
"""
AomE — generate_plate.py  (v6.2 — batch mode added)
-------------------------------------------------------
Generates plates via the RunComfy Serverless API.

  • text_to_image : fresh base reference (Flux.2 Text-to-Image deployment)
  • image_edit    : variant from a locked base (Flux.2 UNIFIED edit deployment)

Unified edit: ONE edit deployment handles both plain and masked edits.
  - Plate has no "mask_path"      -> script sends an all-white mask -> whole-image
                                     edit (full regeneration; used for relights etc.)
  - Plate has a "mask_path" PNG   -> that painted mask protects the locked regions
                                     (white = editable, black = protected), and the
                                     protected pixels are composited back bit-exactly.

Speed via Turbo LoRA toggle: Turbo (8 steps) for iteration, Full (20) for finals.
Outputs saved versioned (_v001, _v002 ...) + stable; fit to 1920x1080.

SECURITY: the API token is read from the environment variable RUNCOMFY_API_TOKEN —
never hardcoded (this script lives in a public GitHub repo). Set once per terminal:
    export RUNCOMFY_API_TOKEN="your-token"
    export RUNCOMFY_DEPLOY_T2I="text-to-image-deployment-id"
    export RUNCOMFY_DEPLOY_EDIT="unified-edit-deployment-id"

Usage (from AomE project root):
    python3 skills/generate-plate/tools/generate_plate.py A1_plate_pristine_day
    python3 skills/generate-plate/tools/generate_plate.py A1_plate_pristine_dusk
    python3 skills/generate-plate/tools/generate_plate.py A1_plate_terraced
    python3 skills/generate-plate/tools/generate_plate.py --list
    python3 skills/generate-plate/tools/generate_plate.py A1_plate_B3_pristine_dusk --batch 5
    python3 skills/generate-plate/tools/generate_plate.py A1_plate_B3_pristine_dawn --batch 3 --force
"""

import os
import io
import re
import sys
import json
import time
import base64
import requests
from pathlib import Path
from getpass import getpass

# ── PATHS / API ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BASE_URL = "https://api.runcomfy.net"

API_TOKEN = os.environ.get("RUNCOMFY_API_TOKEN") or getpass("RunComfy API token: ")
HEADERS = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}

# One deployment per workflow. The edit deployment is now the UNIFIED edit workflow.
DEPLOYMENTS = {
    "text_to_image": os.environ.get("RUNCOMFY_DEPLOY_T2I", ""),
    "image_edit":    os.environ.get("RUNCOMFY_DEPLOY_EDIT", ""),
}

# Node-ID override maps (from each workflow's Export-API JSON).
T2I_NODES = {
    "prompt":     "98:6",
    "seed":       "98:25",
    "size_nodes": ["98:47", "98:48"],
    "turbo":      "98:104",
}
EDIT_NODES = {
    "image":       "3",     # LoadImage — base plate
    "mask":        "24",    # LoadImage — mask (white=edit, black=protect)
    "instruction": "4",     # CLIPTextEncode — positive prompt (edit instruction)
    "seed":        "11",    # RandomNoise — noise_seed
    "turbo":       "23",    # "Enable 8 steps lora" PrimitiveBoolean — value
}

T2I_WIDTH, T2I_HEIGHT = 1536, 864
TURBO       = True
GEN_TIMEOUT = 900

# ── JSON HELPERS ─────────────────────────────────────────────────────────────

def find_json():
    cands = list(PROJECT_ROOT.glob("AomE_beats_v*.json"))
    if not cands:
        return None
    def key(p):
        m = re.search(r"v(\d+)_(\d+)", p.name)
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    return max(cands, key=key)

def load_data(p):
    with open(p) as f:
        return json.load(f)

def save_data(d, p):
    with open(p, "w") as f:
        json.dump(d, f, indent=2)

def get_base_plate_file(base_id, data):
    base = data.get("plates", {}).get(base_id)
    if not base:
        return None
    path = PROJECT_ROOT / base.get("asset_path", f"plates/{base_id}.png")
    return path if path.exists() else None

# ── MASK (painted file, or auto all-white for plain edits) ───────────────────

def get_mask_data_uri(plate, base_file):
    """Return (data_uri, description). Painted mask if 'mask_path' set and present;
    otherwise an all-white mask matching the base size (= plain whole-image edit)."""
    mask_rel = plate.get("mask_path")
    if mask_rel:
        mask_path = PROJECT_ROOT / mask_rel
        if mask_path.exists():
            b64 = base64.b64encode(mask_path.read_bytes()).decode()
            return f"data:image/png;base64,{b64}", f"painted ({mask_rel})"
        print(f"  ⚠  mask_path '{mask_rel}' not found — using all-white (plain edit).")
    try:
        from PIL import Image
        w, h = Image.open(base_file).size
        white = Image.new("RGB", (w, h), (255, 255, 255))
        buf = io.BytesIO()
        white.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{b64}", "all-white (plain edit)"
    except ImportError:
        print("  Pillow required to auto-generate the mask. Install: pip3 install pillow --break-system-packages")
        return None, None

# ── OVERRIDES ────────────────────────────────────────────────────────────────

def build_t2i_overrides(plate, seed):
    n = T2I_NODES
    ov = {
        n["prompt"]: {"inputs": {"text": plate.get("generation_prompt", "")}},
        n["seed"]:   {"inputs": {"noise_seed": seed}},
        n["turbo"]:  {"inputs": {"value": TURBO}},
    }
    for node in n["size_nodes"]:
        ov[node] = {"inputs": {"width": T2I_WIDTH, "height": T2I_HEIGHT}}
    return {"overrides": ov}

def build_edit_overrides(plate, seed, base_file):
    base_uri = f"data:image/png;base64,{base64.b64encode(base_file.read_bytes()).decode()}"
    mask_uri, mask_kind = get_mask_data_uri(plate, base_file)
    if mask_uri is None:
        return None
    print(f"  Mask: {mask_kind}")
    n = EDIT_NODES
    ov = {
        n["image"]:       {"inputs": {"image": base_uri}},
        n["mask"]:        {"inputs": {"image": mask_uri}},
        n["instruction"]: {"inputs": {"text": plate.get("edit_instruction", "")}},
        n["seed"]:        {"inputs": {"noise_seed": seed}},
        n["turbo"]:       {"inputs": {"value": TURBO}},
    }
    return {"overrides": ov}

# ── API CALLS ────────────────────────────────────────────────────────────────

def submit(deployment_id, payload):
    url = f"{BASE_URL}/prod/v2/deployments/{deployment_id}/inference"
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.status_code not in (200, 201):
        print(f"  Submit failed: {r.status_code} — {r.text[:300]}")
        return None
    d = r.json()
    print(f"  Request ID: {d.get('request_id')}")
    return d

def wait(status_url, timeout):
    print("  Generating", end="", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(status_url, headers=HEADERS)
            if r.status_code == 200:
                st = r.json().get("status", "")
                if st in ("completed", "succeeded"):
                    print(" ✓"); return True
                if st in ("failed", "error", "cancelled", "canceled"):
                    print(f" ✗ ({st})"); return False
        except Exception:
            print("x", end="", flush=True)
            time.sleep(5); continue
        print(".", end="", flush=True)
        time.sleep(3)
    print(" Timed out")
    return False

def fetch_result_and_save(result_url, stable_path, meta=None):
    r = requests.get(result_url, headers=HEADERS)
    if r.status_code != 200:
        print(f"  Result fetch failed: HTTP {r.status_code}")
        return None
    data = r.json()

    if data.get("status") in ("failed", "error"):
        print("  ✗ Generation FAILED on the server:")
        errs = data.get("error", [])
        for e in (errs if isinstance(errs, list) else [errs]):
            msg = (e.get("details") or e.get("error")) if isinstance(e, dict) else str(e)
            print(f"    - {msg}")
        if data.get("log_url"):
            print(f"    log: {data['log_url']}")
        return None

    outputs = data.get("outputs") or data.get("result") or data.get("output") or {}
    nodes = outputs.values() if isinstance(outputs, dict) else outputs
    for out in nodes:
        if not isinstance(out, dict):
            continue
        for img in out.get("images", []):
            url = img.get("url")
            if url:
                return save_processed(requests.get(url).content, stable_path, meta)
            fn = img.get("filename")
            if fn:
                view = (f"{BASE_URL}/api/view?filename={fn}"
                        f"&subfolder={img.get('subfolder','')}&type={img.get('type','output')}")
                vr = requests.get(view, headers=HEADERS, allow_redirects=False)
                signed = vr.headers.get("location")
                raw = requests.get(signed).content if signed else vr.content
                return save_processed(raw, stable_path, meta)

    print("  No image found in result.")
    return None

# ── SAVE (versioned + stable, fit to 1920x1080) ──────────────────────────────

def _next_version_path(stable_path):
    stem, parent = stable_path.stem, stable_path.parent
    nums = [int(m.group(1)) for f in parent.glob(f"{stem}_v*.png")
            if (m := re.search(r"_v(\d+)$", f.stem))]
    n = (max(nums) + 1) if nums else 1
    return parent / f"{stem}_v{n:03d}.png", n

def save_processed(raw, stable_path, meta=None):
    """Save versioned + stable. Embeds seed/metadata into the PNG (survives the
    Pillow re-save that previously stripped ComfyUI metadata) AND writes a
    human-readable sidecar .json next to the versioned file. meta = dict with
    plate_id, seed, quality, mode, prompt, date."""
    stable_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image, PngImagePlugin
        img = Image.open(io.BytesIO(raw))
        w, h = img.size
        if (w, h) != (1920, 1080):
            print(f"  Fitting {w}×{h} → 1920×1080...")
            scale = max(1920 / w, 1080 / h)
            nw, nh = int(w * scale), int(h * scale)
            img = img.resize((nw, nh), Image.LANCZOS)
            l, t = (nw - 1920) // 2, (nh - 1080) // 2
            img = img.crop((l, t, l + 1920, t + 1080))

        # Build PNG metadata so the seed travels INSIDE the file.
        pnginfo = PngImagePlugin.PngInfo()
        if meta:
            for k, v in meta.items():
                if v is not None:
                    pnginfo.add_text(f"aome_{k}", str(v))
            pnginfo.add_text("aome_meta", json.dumps(meta))

        vpath, vnum = _next_version_path(stable_path)
        img.save(str(vpath), pnginfo=pnginfo)
        img.save(str(stable_path), pnginfo=pnginfo)

        # Sidecar JSON (belt and suspenders, human-readable)
        if meta:
            sidecar = vpath.with_suffix(".json")
            sidecar.write_text(json.dumps({**meta, "version": vnum,
                                           "file": vpath.name}, indent=2))

        print(f"  Saved: {vpath.name} (v{vnum:03d}) + {stable_path.name}")
        if meta and meta.get("seed") is not None:
            print(f"  Seed {meta['seed']} embedded in PNG + sidecar .json")
        return vnum
    except ImportError:
        stable_path.write_bytes(raw)
        print(f"  Pillow missing — saved raw to {stable_path.name}")
        return 0


def read_png_seed(png_path):
    """Recover the seed from a PNG's embedded aome metadata, if present."""
    try:
        from PIL import Image
        info = Image.open(png_path).info
        if "aome_seed" in info:
            return info["aome_seed"]
        if "aome_meta" in info:
            return json.loads(info["aome_meta"]).get("seed")
    except Exception:
        pass
    return None

# ── PLATE MANAGEMENT ─────────────────────────────────────────────────────────

def list_plates(data):
    plates = data.get("plates", {})
    print(f"\nPlates ({len(plates)} total):\n")
    for pid, p in plates.items():
        icon = "✓" if p.get("generation_status") == "completed" else "○"
        mode = p.get("generation_mode", "image_edit")
        tag  = "BASE (t2i)" if mode == "text_to_image" else f"← {p.get('derives_from_plate','?')}"
        mask = "  [masked]" if p.get("mask_path") else ""
        lock = "  🔒" if p.get("locked") else ""
        print(f"  {icon} {pid:36} {tag}{mask}{lock}")
    print("\n  ✓ = completed   ○ = not started   🔒 = locked")

def ask_speed():
    global TURBO, GEN_TIMEOUT
    print("\n  Generation quality:")
    print("  [1] Turbo — 8 steps,  fast iteration")
    print("  [2] Full  — 20 steps, best quality")
    if input("  Choose 1 or 2 [default: 1]: ").strip() == "2":
        TURBO, GEN_TIMEOUT = False, 1500
        print("  → Full (20 steps)\n")
    else:
        TURBO, GEN_TIMEOUT = True, 900
        print("  → Turbo (8 steps)\n")

def generate_plate(plate_id, data, json_path, force=False, batch=False):
    plate = data.get("plates", {}).get(plate_id)
    if not plate:
        print(f"Plate '{plate_id}' not found."); return False
    if plate.get("locked") and not force:
        if not batch:
            if input(f"\n'{plate_id}' is LOCKED. Regenerate anyway? (y/n): ").strip().lower() != "y":
                print("Skipped."); return False
    elif plate.get("generation_status") == "completed" and not force and not batch:
        if input(f"\n'{plate_id}' already completed. Regenerate? (y/n): ").strip().lower() != "y":
            print("Skipped."); return False

    mode = plate.get("generation_mode", "image_edit")
    deployment_id = DEPLOYMENTS.get("text_to_image" if mode == "text_to_image" else "image_edit", "")
    if not deployment_id:
        var = "RUNCOMFY_DEPLOY_T2I" if mode == "text_to_image" else "RUNCOMFY_DEPLOY_EDIT"
        print(f"  No deployment ID set for mode '{mode}'. Set the {var} environment variable.")
        return False

    seed = int(time.time())
    print(f"\nGenerating: {plate_id}  [{mode}]  ({'turbo' if TURBO else 'full'})  seed {seed}")

    if mode == "text_to_image":
        payload = build_t2i_overrides(plate, seed)
        base_file, mask_used = None, None
    else:
        base_id   = plate.get("base_reference") or plate.get("derives_from_plate")
        base_file = get_base_plate_file(base_id, data)
        if not base_file:
            print(f"  Base plate '{base_id}' not generated yet."); return False
        payload = build_edit_overrides(plate, seed, base_file)
        mask_used = plate.get("mask_path")  # None = all-white plain edit, else the painted mask's path
    if not payload:
        return False

    resp = submit(deployment_id, payload)
    if not resp:
        return False
    if not wait(resp["status_url"], GEN_TIMEOUT):
        return False

    stable_path = PROJECT_ROOT / plate.get("asset_path", f"plates/{plate_id}.png")
    meta = {
        "plate_id": plate_id,
        "seed": seed,
        "quality": "turbo" if TURBO else "full",
        "mode": mode,
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "prompt": plate.get("generation_prompt") or plate.get("edit_instruction", ""),
        "base_plate_file": base_file.name if base_file else None,
        "mask_file": mask_used,
        "deployment_id": deployment_id,
    }
    vnum = fetch_result_and_save(resp["result_url"], stable_path, meta)
    if vnum is not None:
        p = data["plates"][plate_id]
        p["generation_status"] = "completed"
        p["last_seed"] = seed
        p["latest_version"] = vnum
        log = p.get("version_log", [])
        log.append({"version": vnum, "seed": seed,
                    "quality": "turbo" if TURBO else "full",
                    "date": time.strftime("%Y-%m-%d %H:%M")})
        p["version_log"] = log
        save_data(data, json_path)
        print(f"  Status → completed  |  v{vnum:03d}  |  seed {seed}")
        return True
    return False

# ── ENTRY ────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    if not args or "--help" in args:
        print(__doc__); return

    force = "--force" in args
    args = [a for a in args if a != "--force"]

    # --batch N
    batch_count = 1
    if "--batch" in args:
        idx = args.index("--batch")
        try:
            batch_count = int(args[idx + 1])
            args.pop(idx + 1); args.pop(idx)
        except (IndexError, ValueError):
            print("Usage: --batch N  (where N is an integer)"); return

    json_path = find_json()
    if not json_path:
        print("ERROR: Beat JSON not found."); return
    data = load_data(json_path)
    print(f"Using: {json_path.name}")

    if "--read-seed" in args:
        idx = args.index("--read-seed")
        try:
            png = args[idx + 1]
        except IndexError:
            print("Usage: --read-seed path/to/file.png"); return
        p = Path(png)
        if not p.is_absolute():
            p = PROJECT_ROOT / png
        seed = read_png_seed(p)
        print(f"Seed for {p.name}: {seed if seed else 'NOT FOUND in PNG metadata (pre-metadata file)'}")
        return

    if "--list" in args:
        list_plates(data); return

    ask_speed()

    if batch_count > 1:
        print(f"\n  Batch mode: {batch_count} generations back-to-back.\n")
        ok = 0
        for i in range(batch_count):
            print(f"── Batch {i+1}/{batch_count} ──────────────────────────")
            if generate_plate(args[0], data, json_path, force=True, batch=True):
                ok += 1
            time.sleep(10)  # give the server time to fully reset between jobs
        print(f"\n  Batch complete: {ok}/{batch_count} succeeded.")
    else:
        generate_plate(args[0], data, json_path, force=force)

if __name__ == "__main__":
    main()
