#!/usr/bin/env python3
"""
AomE — generate_transition.py  (v2 — Wan FLF2V → RIFE chained, length-controlled)
---------------------------------------------------------------------------------
Generates a transition between two LOCKED plates and (optionally) extends/smooths
it to a user-defined length, all in one command.

  Stage 1: Wan 2.2 FLF2V — start plate + end plate → short motion clip
  Stage 2: RIFE VFI       — interpolate to reach the target seconds at 25fps

DURATION: --seconds N picks BOTH the Wan frame count and the RIFE multiplier so the
result lands near-exact at a locked 25fps cadence (not by changing fps).

QUALITY PRESETS (--quality):
  master   ProRes              (clean edit-ready master; default for keepers)
  preview  h264-mp4 crf 20     (quick small file)
  draft    h264-mp4 crf 28 + low Wan steps (cheapest look-see)
  lossless ffv1-mkv            (zero-loss, huge files)
Raw overrides: --crf N, --format "video/..." , --multiplier N, --steps N, --seed N

ENV (set once per terminal):
  export RUNCOMFY_API_TOKEN="..."
  export RUNCOMFY_DEPLOY_FLF2V="wan-deployment-id"
  export RUNCOMFY_DEPLOY_RIFE="rife-deployment-id"

Usage (from project root):
  python3 skills/generate-plate/tools/generate_transition.py T_day_to_dusk --seconds 12
  python3 skills/generate-plate/tools/generate_transition.py T_day_to_dusk --seconds 8 --quality preview
  python3 skills/generate-plate/tools/generate_transition.py T_day_to_dusk            # raw Wan only, no interp
  python3 skills/generate-plate/tools/generate_transition.py --interp-only clip.mp4 --multiplier 4
  python3 skills/generate-plate/tools/generate_transition.py --list
"""

import os, re, sys, json, time, base64, subprocess, requests
from pathlib import Path
from getpass import getpass

def notify_done(success=True, quiet=False):
    """Play a short macOS system sound so Sam can hear a render finish from
    another room and start the next one while the machine is still warm.
    Silently does nothing on non-mac systems or if the sound file is missing —
    never raises, never blocks the actual pipeline result."""
    if quiet:
        return
    sound = "/System/Library/Sounds/Glass.aiff" if success else "/System/Library/Sounds/Basso.aiff"
    try:
        subprocess.run(["afplay", sound], timeout=5, capture_output=True)
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BASE_URL = "https://api.runcomfy.net"
FPS = 25
WAN_MIN, WAN_MAX = 16, 81   # Wan FLF2V comfortable frame range

API_TOKEN = os.environ.get("RUNCOMFY_API_TOKEN") or getpass("RunComfy API token: ")
HEADERS = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}
DEPLOY_FLF2V = os.environ.get("RUNCOMFY_DEPLOY_FLF2V", "")
DEPLOY_RIFE  = os.environ.get("RUNCOMFY_DEPLOY_RIFE", "")

# Node maps from the deployed workflow_api.json files
WAN = {"start": "52", "end": "72", "pos": "6", "neg": "7", "wan": "83", "ksampler": "90", "video": "92"}
RIFE = {"loadvideo": "10", "rife": "16", "video": "19"}

DEFAULT_NEGATIVE = ("camera pan, camera zoom, dolly, camera shake, warping, morphing, distortion, "
    "flickering, frozen still image, moving terrain, drifting mountains, shifting horizon, "
    "people, animals, text, watermark, low quality, blurry, overexposed")

QUALITY = {
    "master":   {"format": "video/ProRes",    "crf": None, "wan_steps": None},
    "preview":  {"format": "video/h264-mp4",   "crf": 20,   "wan_steps": None},
    "draft":    {"format": "video/h264-mp4",   "crf": 28,   "wan_steps": 8},
    "lossless": {"format": "video/ffv1-mkv",   "crf": None, "wan_steps": None},
}
GEN_TIMEOUT = 2400

# ── helpers ──────────────────────────────────────────────────────────────────

def find_json():
    c = list(PROJECT_ROOT.glob("AomE_beats_v*.json"))
    if not c: return None
    return max(c, key=lambda p:(lambda m:(int(m.group(1)),int(m.group(2))) if m else (0,0))(re.search(r"v(\d+)_(\d+)",p.name)))

def plate_image_file(plate_id, data):
    p = data.get("plates", {}).get(plate_id)
    if not p: return None
    stable = PROJECT_ROOT / p.get("asset_path", f"plates/{plate_id}.png")
    lv = p.get("locked_version")
    if lv:
        v = stable.parent / f"{stable.stem}_v{int(lv):03d}.png"
        if v.exists(): return v
    return stable if stable.exists() else None

def b64_image(path):
    return f"data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}"

def b64_video(path):
    return f"data:video/mp4;base64,{base64.b64encode(path.read_bytes()).decode()}"

def plan_chain(seconds):
    # Maximize REAL Wan motion: always generate at the 81-frame ceiling, then choose the
    # RIFE multiplier that lands AT or just ABOVE the requested length (never short, so the
    # editor always has at least what they asked + a little extra to trim). Keep every frame.
    import math
    target = round(seconds * FPS)
    W = WAN_MAX                                  # 81 = Wan's no-compromise ceiling
    M = max(2, math.ceil(target / W))            # round UP so we never undershoot
    actual = round(W * M / FPS, 2)
    return W, M, actual

def submit(deploy, payload):
    r = requests.post(f"{BASE_URL}/prod/v2/deployments/{deploy}/inference", headers=HEADERS, json=payload)
    if r.status_code not in (200, 201):
        print(f"  Submit failed: {r.status_code} — {r.text[:300]}"); return None
    d = r.json(); print(f"  Request ID: {d.get('request_id')}"); return d

def wait(status_url, label="Rendering"):
    print(f"  {label}", end="", flush=True); start = time.time()
    fails = 0
    while time.time() - start < GEN_TIMEOUT:
        try:
            r = requests.get(status_url, headers=HEADERS, timeout=30)
            fails = 0
            if r.status_code == 200:
                st = r.json().get("status", "")
                if st in ("completed", "succeeded"): print(" ✓"); return True
                if st in ("failed", "error", "cancelled", "canceled"): print(f" ✗ ({st})"); return True
        except Exception:
            fails += 1
            print("x", end="", flush=True)   # network blip — keep trying, job is safe on server
            if fails > 40:                    # ~3+ min of solid failure → give up locally
                print(" (lost connection; job may still be running — recover with --resume)"); return False
        print(".", end="", flush=True); time.sleep(5)
    print(" timed out"); return False

def fetch_video(result_url, out_path):
    r = requests.get(result_url, headers=HEADERS)
    if r.status_code != 200:
        print(f"  Result fetch failed: HTTP {r.status_code}"); return False
    data = r.json()
    if data.get("status") in ("failed", "error"):
        print("  ✗ FAILED on the server:")
        for e in (data.get("error", []) if isinstance(data.get("error"), list) else [data.get("error")]):
            msg = (e.get("details") or e.get("error")) if isinstance(e, dict) else str(e)
            print(f"    - {msg}")
        if data.get("log_url"): print(f"    log: {data['log_url']}")
        return False
    outputs = data.get("outputs") or data.get("result") or {}
    nodes = outputs.values() if isinstance(outputs, dict) else outputs
    for out in nodes:
        if not isinstance(out, dict): continue
        for key in ("gifs", "videos", "images"):
            for item in out.get(key, []):
                url, fn = item.get("url"), item.get("filename", "")
                if url: raw = requests.get(url).content
                elif fn:
                    view = f"{BASE_URL}/api/view?filename={fn}&subfolder={item.get('subfolder','')}&type={item.get('type','output')}"
                    vr = requests.get(view, headers=HEADERS, allow_redirects=False)
                    raw = requests.get(vr.headers["location"]).content if vr.headers.get("location") else vr.content
                else: continue
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(raw)
                print(f"  Saved: {out_path.name} ({len(raw)//1024} KB)")
                return True
    print("  No video in result. Raw (first 1200 chars):"); print("   ", json.dumps(data, indent=2)[:1200])
    return False

def next_version(folder, stem):
    folder.mkdir(parents=True, exist_ok=True)
    # Scan ALL video extensions, not just .mp4 — otherwise ProRes (.mov) masters
    # never see each other and every render saves as _v001, overwriting the last.
    nums = []
    for ext in ("mp4", "mov", "mkv", "webm"):
        for f in folder.glob(f"{stem}_v*.{ext}"):
            if (m := re.search(r"_v(\d+)$", f.stem)):
                nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1

# ── stages ───────────────────────────────────────────────────────────────────

def get_result_url(result_url):
    """Return the RunComfy storage URL of a finished job's video output (no download)."""
    r = requests.get(result_url, headers=HEADERS)
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("status") in ("failed", "error"):
        print("  ✗ FAILED on the server:")
        for e in (data.get("error", []) if isinstance(data.get("error"), list) else [data.get("error")]):
            msg = (e.get("details") or e.get("error")) if isinstance(e, dict) else str(e)
            print(f"    - {msg}")
        if data.get("log_url"): print(f"    log: {data['log_url']}")
        return None
    outputs = data.get("outputs") or data.get("result") or {}
    nodes = outputs.values() if isinstance(outputs, dict) else outputs
    for out in nodes:
        if not isinstance(out, dict): continue
        for key in ("gifs", "videos", "images"):
            for item in out.get(key, []):
                if item.get("url"): return item["url"]
    return None

def run_wan(t, start_f, end_f, W, steps, seed, lossless_intermediate=True):
    ov = {"overrides": {
        WAN["start"]: {"inputs": {"image": b64_image(start_f)}},
        WAN["end"]:   {"inputs": {"image": b64_image(end_f)}},
        WAN["pos"]:   {"inputs": {"text": t.get("motion_prompt", "")}},
        WAN["neg"]:   {"inputs": {"text": t.get("negative_prompt", DEFAULT_NEGATIVE)}},
        WAN["wan"]:   {"inputs": {"width": 1280, "height": 720, "length": W}},
        WAN["ksampler"]: {"inputs": {"seed": seed, "steps": steps}},
    }}
    # RIFE fetches the intermediate by URL (confirmed working), so request-body size
    # is no longer a constraint — we can use a TRULY LOSSLESS ProRes intermediate for
    # master/lossless quality. RIFE then interpolates from pristine frames and the
    # final master is genuinely full-quality end to end. Preview/draft keep h264.
    if lossless_intermediate:
        ov["overrides"][WAN["video"]] = {"inputs": {"format": "video/ProRes"}}
    else:
        ov["overrides"][WAN["video"]] = {"inputs": {"format": "video/h264-mp4", "crf": 20}}
    print(f"  [Wan] {W} frames, {steps} steps, seed {seed}"
          + ("  (lossless ProRes intermediate)" if lossless_intermediate else ""))
    resp = submit(DEPLOY_FLF2V, ov)
    if not resp or not wait(resp["status_url"], "  Wan rendering"): return None
    url = get_result_url(resp["result_url"])
    if not url:
        print("  ✗ Could not get Wan output URL."); return None
    return url

def run_rife(clip, M, fmt, crf, out_path):
    # `clip` may be a RunComfy URL (from run_wan — passed straight through, no size
    # limit) OR a local file path (--interp-only — base64-embedded as before).
    if isinstance(clip, str) and clip.startswith("http"):
        file_input = clip
    else:
        file_input = b64_video(Path(clip))
    vid = {"inputs": {"crf": crf, "format": fmt, "frame_rate": FPS}} if crf is not None \
          else {"inputs": {"format": fmt, "frame_rate": FPS}}
    ov = {"overrides": {
        RIFE["loadvideo"]: {"inputs": {"file": file_input}},
        RIFE["rife"]:      {"inputs": {"multiplier": M}},
        RIFE["video"]:     vid,
    }}
    print(f"  [RIFE] multiplier {M}, {fmt}" + (f", crf {crf}" if crf is not None else ""))
    resp = submit(DEPLOY_RIFE, ov)
    if not resp or not wait(resp["status_url"], "  RIFE rendering"): return False
    return fetch_video(resp["result_url"], out_path)

# ── main ─────────────────────────────────────────────────────────────────────

def getflag(flags, name, default=None, cast=str):
    for i, f in enumerate(flags):
        if f.startswith(name + "="):                      # --name=value
            return cast(f.split("=", 1)[1])
        if f == name:                                      # --name value  OR  bare --name
            nxt = flags[i+1] if i+1 < len(flags) else None
            if nxt is not None and not nxt.startswith("--"):
                return cast(nxt)
            return True                                    # bare boolean flag
    return default

def main():
    args  = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = sys.argv[1:]
    json_path = find_json()
    data = json.load(open(json_path)) if json_path else {}
    if json_path: print(f"Using: {json_path.name}")

    quality = getflag(flags, "--quality", "master")
    qp = QUALITY.get(quality, QUALITY["master"])
    fmt = getflag(flags, "--format", qp["format"])
    crf = getflag(flags, "--crf", qp["crf"], int) if getflag(flags,"--crf") or qp["crf"] is not None else None
    quiet_sound = bool(getflag(flags, "--quiet-sound", False))
    # Lossless intermediate only when the FINAL output is high-quality (master/lossless).
    # For preview/draft the final is lossy h264 anyway, so keep the intermediate h264
    # too — smaller and faster, no point preserving quality for a lossy deliverable.
    # Explicit override still wins: --lossy-intermediate forces h264, --lossless-intermediate forces ffv1.
    lossless_mid = quality in ("master", "lossless")
    if getflag(flags, "--lossy-intermediate", False):
        lossless_mid = False
    if getflag(flags, "--lossless-intermediate", False):
        lossless_mid = True

    # interp-only: just run RIFE on an existing clip
    interp = getflag(flags, "--interp-only")
    if interp:
        if not DEPLOY_RIFE: print("  Set RUNCOMFY_DEPLOY_RIFE first."); return
        clip = Path(interp); M = int(getflag(flags, "--multiplier", 2, int))
        out = clip.parent / f"{clip.stem}_x{M}.mp4"
        print(f"\nInterpolate-only: {clip.name} ×{M}")
        run_rife(clip, M, fmt, crf, out); return

    if "--read-settings" in flags:
        idx = flags.index("--read-settings")
        try:
            vid = Path(flags[idx + 1])
        except IndexError:
            print("Usage: --read-settings path/to/clip.mp4"); return
        sidecar = vid.with_suffix(".json")
        if sidecar.exists():
            print(sidecar.read_text())
        else:
            print(f"No sidecar found at {sidecar}. Only clips rendered with this script version have one.")
        return

    if "--list" in flags or not args:
        ts = data.get("transitions", {})
        print(f"\nTransitions ({len(ts)}):")
        for tid, t in ts.items():
            print(f"  {tid}: {t['start_plate'].split('_')[-1]} → {t['end_plate'].split('_')[-1]}")
        print("\n  add --seconds N (5–20) to set length; --quality master|preview|draft")
        return

    tid = args[0]
    t = data.get("transitions", {}).get(tid)
    if not t: print(f"Transition '{tid}' not found. --list to see options."); return
    if not DEPLOY_FLF2V: print("  Set RUNCOMFY_DEPLOY_FLF2V first."); return

    start_f = plate_image_file(t["start_plate"], data)
    end_f   = plate_image_file(t["end_plate"], data)
    if not start_f or not end_f:
        print(f"  Missing boundary plate image. Generate/lock both plates first."); return

    seconds = getflag(flags, "--seconds", None, float)
    seed = int(getflag(flags, "--seed", int(time.time()), int))
    steps = getflag(flags, "--steps", qp["wan_steps"] or t.get("steps", 20), int)
    force_frames = getflag(flags, "--wan-frames", None, int)

    if force_frames:
        W = force_frames
        M = int(getflag(flags, "--multiplier", 2, int)) if (seconds or getflag(flags, "--multiplier")) else None
        print(f"\nTransition: {tid}  →  FORCED {W} Wan frames (diagnostic)" + (f", RIFE ×{M}" if M else ", no interp"))
    elif seconds:
        W, M, actual = plan_chain(seconds)
        total_frames = W * M
        diff = round(actual - seconds, 2)
        print(f"\nTransition: {tid}  →  {seconds}s requested  (quality: {quality})")
        print(f"  Generating: {W} Wan frames × RIFE {M} = {actual}s @ {FPS}fps  ({total_frames} frames)")
        if diff > 0.05:
            print(f"  ⓘ Nearest step at/above your request — clip will be {diff}s LONGER than asked.")
            print(f"    All frames kept (max real motion); trim to exact length in your editor.")
        if M > 8:
            print(f"  ⚠ High multiplier ({M}×) — heavily interpolated; fine for slow light, watch for softness.")
    else:
        W, M = t.get("length", 49), None
        print(f"\nTransition: {tid}  →  raw Wan only ({W} frames), no interpolation")

    if not DEPLOY_RIFE and seconds:
        print("  Set RUNCOMFY_DEPLOY_RIFE to enable interpolation, or omit --seconds."); return

    raw = run_wan(t, start_f, end_f, W, steps, seed, lossless_intermediate=lossless_mid)
    if not raw:
        notify_done(success=False, quiet=quiet_sound)
        return

    out_folder = PROJECT_ROOT / "transitions"
    vnum = next_version(out_folder, tid)
    ext = "mkv" if "ffv1" in fmt else ("mov" if "ProRes" in fmt else "mp4")
    final = out_folder / f"{tid}_v{vnum:03d}.{ext}"

    if M:  # chain through RIFE
        ok = run_rife(raw, M, fmt, crf, final)
    else:  # raw Wan only — just move it to the versioned name
        raw.rename(final); ok = True; print(f"  Saved: {final.name}")

    if ok:
        settings = {
            "transition_id": tid, "version": vnum, "seed": seed,
            "wan_frames": W, "multiplier": M, "seconds_requested": seconds,
            "quality": quality, "format": fmt, "crf": crf, "wan_steps": steps,
            "start_plate": t["start_plate"], "end_plate": t["end_plate"],
            "start_plate_file": start_f.name, "end_plate_file": end_f.name,
            "motion_prompt": t.get("motion_prompt", ""),
            "negative_prompt": t.get("negative_prompt", DEFAULT_NEGATIVE),
            "deploy_flf2v": DEPLOY_FLF2V, "deploy_rife": DEPLOY_RIFE if M else None,
            "output_file": final.name,
            "date": time.strftime("%Y-%m-%d %H:%M"),
        }
        # 1) log into the shared beat JSON (existing behaviour, now with full settings)
        log = t.get("render_log", [])
        log.append(settings)
        t["render_log"] = log
        json.dump(data, open(json_path, "w"), indent=2)
        # 2) standalone sidecar JSON next to the video (mirrors the plate convention —
        #    lets you find a clip's exact settings without opening the whole beat JSON)
        sidecar = final.with_suffix(".json")
        sidecar.write_text(json.dumps(settings, indent=2))
        print(f"  Done → transitions/{final.name}  [+ sidecar {sidecar.name}]")
        notify_done(success=True, quiet=quiet_sound)
    else:
        notify_done(success=False, quiet=quiet_sound)

if __name__ == "__main__":
    main()
