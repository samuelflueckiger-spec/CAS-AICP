#!/usr/bin/env python3
"""
generate_audio.py — text-to-audio via the ElevenLabs API.
Replaces the old MMAudio (video-to-audio) script. Four modes:

  sfx       short sound effects (whooshes, impacts, UI cues)      -> /v1/sound-generation
  ambience  looping atmospheres / beds (wind, room tone, drones)  -> /v1/sound-generation (loop)
  music     original instrumental/scored tracks from a prompt     -> /v1/music
  voice     text-to-speech narration in a chosen voice            -> /v1/text-to-speech/{voice_id}

Setup (one-time):
    export ELEVENLABS_API_KEY=your_key_here      # add to ~/.zshrc

Usage:
    python3 skills/generate-plate/tools/generate_audio.py sfx "fast whoosh, air rushing past"
    python3 .../generate_audio.py sfx "cinematic swoosh" --duration 1.2 --influence 0.4 --format wav
    python3 .../generate_audio.py ambience "gentle high-altitude Andean wind" --duration 25
    python3 .../generate_audio.py music "slow ambient andean flute, sparse" --duration 30
    python3 .../generate_audio.py voice "A single plant endures." --voice Rachel
    python3 .../generate_audio.py --list-voices
    python3 .../generate_audio.py sfx "swoosh" --batch 4

Files versioned per mode in audio/{mode}/ (never overwritten) + sidecar .json.
"""
import os, re, sys, json, time, subprocess, requests
from pathlib import Path

API = "https://api.elevenlabs.io/v1"
KEY = os.environ.get("ELEVENLABS_API_KEY")
ROOT = Path(__file__).resolve().parents[2] if (Path(__file__).resolve().parents[2] / "skills").exists() else Path.cwd()
AUDIO = ROOT / "audio"

FORMATS = {"mp3": "mp3_44100_192", "wav": "pcm_44100", "flac": None}  # wav/pcm_44100 needs Pro tier; flac = mp3 then transcode
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

def notify(ok=True):
    snd = "/System/Library/Sounds/Glass.aiff" if ok else "/System/Library/Sounds/Basso.aiff"
    try: subprocess.run(["afplay", snd], timeout=5, capture_output=True)
    except Exception: pass

def slug(t):
    s = re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")
    return s[:40] or "audio"

def next_version(folder, stem):
    folder.mkdir(parents=True, exist_ok=True)
    nums = [int(m.group(1)) for f in folder.glob(f"{stem}_v*")
            if (m := re.search(r"_v(\d+)$", f.stem))]
    return (max(nums) + 1) if nums else 1

def save(mode, text, audio_bytes, out_format, meta_extra, name_ref=None):
    folder = AUDIO / mode
    stem = slug(name_ref) if name_ref else slug(text)
    vnum = next_version(folder, stem)
    base = folder / f"{stem}_v{vnum:03d}"
    raw_ext = "mp3" if out_format in ("mp3", "flac") else "wav"
    raw = base.with_suffix("." + raw_ext)
    raw.write_bytes(audio_bytes)
    final = raw
    if out_format == "flac":
        import shutil
        if shutil.which("ffmpeg"):
            fl = base.with_suffix(".flac")
            r = subprocess.run(["ffmpeg", "-y", "-i", str(raw), str(fl)], capture_output=True, text=True)
            if r.returncode == 0 and fl.exists():
                raw.unlink(missing_ok=True); final = fl
            else:
                print("  (flac transcode failed; kept mp3)")
        else:
            print("  (ffmpeg not found; kept mp3)")
    base.with_suffix(".json").write_text(json.dumps({
        "mode": mode, "text": text, "output_format": out_format,
        "file": final.name, "version": vnum, "date": time.strftime("%Y-%m-%d %H:%M"),
        **meta_extra,
    }, indent=2))
    print(f"  Saved: audio/{mode}/{final.name} (v{vnum:03d})  [+ sidecar .json]")
    return vnum

def normalize(audio_path, target_db=-6.0):
    """Peak-normalize so the loudest point sits at target_db (dBFS). Ambience from the
    SFX model comes out quiet; this brings it to a consistent usable level. In-place."""
    import shutil
    if not shutil.which("ffmpeg"):
        return
    ap = Path(audio_path)
    # Measure current peak, then apply the exact gain to reach target_db.
    probe = subprocess.run(
        ["ffmpeg", "-i", str(ap), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True)
    m = re.search(r"max_volume:\s*(-?[\d.]+) dB", probe.stderr)
    if not m:
        print("  (couldn't measure level; skipping normalize)"); return
    current_peak = float(m.group(1))
    gain = target_db - current_peak      # dB to add to reach target
    tmp = ap.with_name(ap.stem + "_norm").with_suffix(ap.suffix)
    acodec = "flac" if ap.suffix == ".flac" else ("pcm_s16le" if ap.suffix == ".wav" else "libmp3lame")
    extra = ["-b:a", "192k"] if ap.suffix == ".mp3" else []
    r = subprocess.run(["ffmpeg", "-y", "-i", str(ap),
                        "-af", f"volume={gain:.2f}dB",
                        "-acodec", acodec, *extra, str(tmp)],
                       capture_output=True, text=True)
    if r.returncode == 0 and tmp.exists():
        tmp.replace(ap)
        print(f"  Normalized: peak {current_peak:.1f}dB -> {target_db:.0f}dB (gain {gain:+.1f}dB)")
    else:
        tmp.unlink(missing_ok=True)
        print("  (normalize failed; file kept at original level)")

def hdr(json_ct=True):
    h = {"xi-api-key": KEY}
    if json_ct: h["Content-Type"] = "application/json"
    return h

def prompt_from_sfx(sid):
    """Return (prompt, duration, influence) for an sfx ID from the latest beat JSON."""
    jp = find_beat_json()
    if not jp: return None, None, None
    data = json.loads(jp.read_text())
    s = data.get("sfx", {}).get(sid)
    if not s: return None, None, None
    return s.get("prompt"), s.get("duration"), s.get("influence")

def find_beat_json():
    c = sorted(ROOT.glob("AomE_beats_v*.json"))
    return c[-1] if c else None

def prompt_from_transition(tid):
    """Return (audio_prompt, seconds) for a transition ID from the latest beat JSON.
    seconds is estimated from wan_frames*multiplier in the transition's render_log
    if present, else None (model auto-guesses)."""
    jp = find_beat_json()
    if not jp: return None, None
    data = json.loads(jp.read_text())
    tr = data.get("transitions", {}).get(tid)
    if not tr: return None, None
    prompt = tr.get("audio_prompt")
    secs = None
    log = tr.get("render_log", [])
    if log:
        last = log[-1]
        wf, mult = last.get("wan_frames"), last.get("multiplier")
        if wf and mult:
            secs = round(wf * mult / 25.0, 1)   # 25 fps
    return prompt, secs

def add_handles(audio_path, out_format, handles):
    """Write a sibling file with `handles` seconds of MIRRORED audio prepended and
    appended, so the sound at each cut matches perfectly for seamless crossfades."""
    import shutil
    if not shutil.which("ffmpeg"):
        print("  (ffmpeg not found; skipping handles)"); return
    ap = Path(audio_path)
    acodec = "flac" if out_format == "flac" else ("pcm_s16le" if out_format == "wav" else "libmp3lame")
    handled = ap.with_name(ap.stem + "_handles").with_suffix(ap.suffix)
    fc = (f"[0:a]atrim=0:{handles},areverse[lead];"
          f"[0:a]areverse,atrim=0:{handles}[tailrev];"
          f"[lead][0:a][tailrev]concat=n=3:v=0:a=1[out]")
    r = subprocess.run(["ffmpeg", "-y", "-i", str(ap), "-filter_complex", fc,
                        "-map", "[out]", "-acodec", acodec, str(handled)],
                       capture_output=True, text=True)
    if r.returncode == 0 and handled.exists():
        print(f"  + Handles: audio/{handled.parent.name}/{handled.name}  ({handles}s mirrored each end)")
    else:
        print("  Handles failed:", r.stderr[-200:])

def gen_sfx(text, duration, influence, loop, out_format, mode="sfx", handles=0.0, name_ref=None, target_db=-6.0):
    el_fmt = FORMATS["mp3"] if out_format == "flac" else FORMATS[out_format]
    body = {"text": text, "prompt_influence": influence,
            "model_id": "eleven_text_to_sound_v2", "output_format": el_fmt}
    if duration is not None: body["duration_seconds"] = duration
    if loop: body["loop"] = True
    r = requests.post(f"{API}/sound-generation", headers=hdr(), json=body, timeout=180)
    if r.status_code != 200:
        print(f"  \u2717 error {r.status_code}: {r.text[:300]}"); return None
    vnum = save(mode, text, r.content, out_format,
                {"duration_seconds": duration, "prompt_influence": influence, "loop": loop,
                 "handles_sec": handles, "target_db": target_db}, name_ref=name_ref)
    if vnum is not None:
        folder = AUDIO / mode
        stem = slug(name_ref) if name_ref else slug(text)
        ext = out_format if out_format in ("wav", "flac") else "mp3"
        saved = folder / f"{stem}_v{vnum:03d}.{ext}"
        if saved.exists():
            if target_db is not None:
                normalize(saved, target_db)          # normalize BASE before handles
            if handles and handles > 0:
                add_handles(saved, out_format, handles)   # handles inherit normalized level
    return vnum

def gen_music(text, duration, out_format):
    el_fmt = FORMATS["mp3"] if out_format == "flac" else FORMATS[out_format]
    body = {"prompt": text, "output_format": el_fmt}
    if duration is not None:
        body["music_length_ms"] = int(duration * 1000)
    r = requests.post(f"{API}/music", headers=hdr(), json=body, timeout=300)
    if r.status_code != 200:
        print(f"  \u2717 error {r.status_code}: {r.text[:300]}"); return None
    return save("music", text, r.content, out_format, {"duration_seconds": duration})

def list_voices():
    r = requests.get(f"{API}/voices", headers=hdr(json_ct=False), timeout=60)
    if r.status_code != 200:
        print(f"  \u2717 error {r.status_code}: {r.text[:200]}"); return
    for v in r.json().get("voices", []):
        print(f"  {v.get('name'):20} {v.get('voice_id')}  ({v.get('category','')})")

def resolve_voice(name_or_id):
    if not name_or_id: return DEFAULT_VOICE_ID
    if re.fullmatch(r"[A-Za-z0-9]{20}", name_or_id): return name_or_id
    r = requests.get(f"{API}/voices", headers=hdr(json_ct=False), timeout=60)
    if r.status_code == 200:
        for v in r.json().get("voices", []):
            if v.get("name", "").lower() == name_or_id.lower():
                return v.get("voice_id")
    print(f"  Voice '{name_or_id}' not found; using default. (--list-voices to see options)")
    return DEFAULT_VOICE_ID

def gen_voice(text, voice, out_format):
    el_fmt = FORMATS["mp3"] if out_format == "flac" else FORMATS[out_format]
    vid = resolve_voice(voice)
    body = {"text": text, "model_id": "eleven_multilingual_v2", "output_format": el_fmt}
    r = requests.post(f"{API}/text-to-speech/{vid}", headers=hdr(), json=body, timeout=180)
    if r.status_code != 200:
        print(f"  \u2717 error {r.status_code}: {r.text[:300]}"); return None
    return save("voice", text, r.content, out_format, {"voice": voice or "default", "voice_id": vid})

def main():
    if not KEY:
        print("Set ELEVENLABS_API_KEY first (export ELEVENLABS_API_KEY=... in ~/.zshrc)."); return
    args = sys.argv[1:]
    if not args:
        print(__doc__); return

    def take(flag, cast=str, default=None):
        if flag in args:
            i = args.index(flag); val = args[i + 1]; del args[i:i + 2]; return cast(val)
        return default

    if "--list-voices" in args:
        list_voices(); return

    duration  = take("--duration", float, None)
    influence = take("--influence", float, 0.3)
    out_format = take("--format", str, "mp3")
    if out_format not in FORMATS:
        print(f"  --format must be one of {list(FORMATS)}; using mp3."); out_format = "mp3"
    voice     = take("--voice", str, None)
    batch     = take("--batch", int, 1)
    handles   = take("--handles", float, 0.0)
    target_db = take("--target-db", float, -6.0)
    if "--no-normalize" in args:
        args.remove("--no-normalize"); target_db = None
    from_tr   = take("--from-transition", str, None)
    from_sfx  = take("--from-sfx", str, None)
    loop      = "--loop" in args
    if loop: args.remove("--loop")

    mode = "sfx"
    if args and args[0] in ("sfx", "ambience", "music", "voice"):
        mode = args.pop(0)

    # Pull an SFX recipe (prompt + duration + influence) from the beat JSON.
    if from_sfx:
        p, dur, inf = prompt_from_sfx(from_sfx)
        if not p:
            print(f"  No sfx entry found for '{from_sfx}'."); return
        args = [p]
        mode = "sfx"
        if duration is None and dur is not None: duration = dur
        if inf is not None: influence = inf
        from_tr = from_tr  # keep name_ref below using from_sfx
        print(f"  Using sfx '{from_sfx}' from JSON (dur {duration}s, influence {influence})")

    # Pull prompt (and estimated length) from a transition in the beat JSON.
    if from_tr:
        p, secs = prompt_from_transition(from_tr)
        if not p:
            print(f"  No audio_prompt found for transition '{from_tr}'."); return
        args = [p]
        if duration is None and secs:
            duration = secs
        print(f"  Using audio_prompt from transition '{from_tr}'"
              + (f" (len ~{duration}s)" if duration else ""))

    # Round any duration UP to a whole second.
    if duration is not None:
        import math
        duration = float(math.ceil(duration))

    # If handles requested, generate 6s longer (real audio, no mirroring). ElevenLabs
    # caps ambience/sfx at 30s, so clamp there.
    handles_added = False
    if handles and handles > 0 and duration is not None:
        duration = min(duration + 6, 30.0)
        handles_added = True
        handles = 0.0   # disable the old mirror-based handles; length IS the handle now
        print(f"  Handles: generating 6s longer -> {int(duration)}s total (capped at 30s)")

    if mode == "ambience":
        loop = True
        duration = 25.0        # fixed 25s bed — detached from source length, easily
                               # trimmed/looped in the edit. Avoids the 30s-cap corruption.
        handles = 0.0          # no handles for ambience (length is fixed, edit in NLE)

    text = " ".join(args).strip()
    if not text:
        print("Provide a prompt/text, or --from-transition ID."); return

    ellipsis = "\u2026" if len(text) > 70 else ""
    print(f"\n[{mode}] \"{text[:70]}{ellipsis}\"")
    ok = 0
    for i in range(batch):
        if batch > 1: print(f"\u2500\u2500 {i+1}/{batch} \u2500\u2500")
        if mode in ("sfx", "ambience"):
            res = gen_sfx(text, duration, influence, loop, out_format, mode=mode,
                          handles=handles, name_ref=(from_sfx or from_tr), target_db=target_db)
        elif mode == "music":
            res = gen_music(text, duration, out_format)
        elif mode == "voice":
            res = gen_voice(text, voice, out_format)
        if res is not None: ok += 1
        if batch > 1 and i < batch - 1: time.sleep(2)
    if batch > 1: print(f"\n  Done: {ok}/{batch} succeeded.")
    notify(ok > 0)

if __name__ == "__main__":
    main()
