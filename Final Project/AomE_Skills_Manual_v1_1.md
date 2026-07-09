# AomE — Skills Command Manual

**Apple of my Earth** | Samuel Flückiger | Reference for `generate_plate.py`, `generate_transition.py`, `generate_audio.py`
Version 1.1 · 2026-07-07

All three scripts live in `skills/generate-plate/tools/` and are run from the AomE project root. Each auto-detects and uses the **highest-numbered** `AomE_beats_v*.json` in the folder.

---

## 1. `generate_plate.py` — landscape plates (text-to-image + masked edits)

### Basic usage
```
python3 skills/generate-plate/tools/generate_plate.py PLATE_ID
```
Prompts you to choose quality (Turbo/Full), then generates. If the plate is locked or already completed, asks before regenerating.

### Flags

| Flag | Effect |
|---|---|
| `--batch N` | Runs N generations back-to-back, fresh seed each, no prompts between them. Quality is chosen once at the start. 10-second pause between runs. |
| `--force` | Skips the "already locked/completed, regenerate?" confirmation. |
| `--list` | Lists every plate in the JSON with its status (✓ completed / ○ not started / 🔒 locked) and whether it's masked. |
| `--read-seed PATH` | Reads the seed embedded in a PNG's metadata (works for any plate generated with this script, v6.2+). Pre-v6.2 files return "not found." |
| `--help` | Prints the script's docstring. |

### Examples
```
# Single generation, asks Turbo/Full
python3 skills/generate-plate/tools/generate_plate.py A1_plate_B3_pristine_dusk

# Batch of 5, for seed-hunting a lighting variant
python3 skills/generate-plate/tools/generate_plate.py A1_plate_B3_pristine_dawn --batch 5

# Force-regenerate a locked plate without the confirmation prompt
python3 skills/generate-plate/tools/generate_plate.py A1_plate_B3_terraced --force

# Recover a lost seed from an existing file
python3 skills/generate-plate/tools/generate_plate.py --read-seed plates/A1_andean_B3_pristine_dusk_v002.png

# See every plate's status at a glance
python3 skills/generate-plate/tools/generate_plate.py --list
```

### What gets saved
- A versioned file (`PLATE_v0NN.png`) and a stable pointer copy (no version number).
- The seed + full generation metadata **embedded directly in the PNG** (survives the 1920×1080 fit/resize).
- A **sidecar `.json`** next to the versioned file with: plate_id, seed, quality, mode, prompt, date, **base_plate_file** (what it was edited from), **mask_file** (which mask, if any), **deployment_id**.
- The plate's entry in the beat JSON gets a `version_log` array appended (same info, for cross-plate lookup without opening every sidecar).

---

## 2. `generate_transition.py` — video transitions (Wan FLF2V → RIFE)

### Basic usage
```
python3 skills/generate-plate/tools/generate_transition.py TRANSITION_ID
```
Defaults to **master** quality if no flags given.

### Flags

| Flag | Effect |
|---|---|
| `--seconds N` | **Recommended.** Target duration in seconds — the script auto-picks the Wan frame count and RIFE multiplier to hit it. Above an ~8× multiplier (≈26s) print a softness warning. |
| `--wan-frames N` | Force an exact Wan frame count directly (diagnostic / manual control), instead of letting `--seconds` plan it. |
| `--multiplier N` | Force the RIFE interpolation multiplier directly. Combine with `--wan-frames` for full manual control. |
| `--quality X` | One of `draft`, `preview`, `master` (default), `lossless` — see table below. |
| `--format X` | Override the container/codec the quality preset would normally choose. |
| `--crf N` | Override the compression level directly (h264 only). |
| `--steps N` | Override Wan's diffusion steps directly (quality presets set sensible defaults; draft forces 8). |
| `--seed N` | Use a specific seed instead of a fresh one — for reproducing an earlier result at a different quality/length. |
| `--interp-only PATH` | Skip Wan entirely; just run RIFE interpolation on an existing video file. |
| `--quiet-sound` | Disable the completion/failure chime for this run. |
| `--read-settings PATH` | Prints the full saved settings (seed, prompts, deployment IDs, etc.) for a given output video, if it has a sidecar. |
| `--list` | Lists all transitions and their status. |

### Quality presets (exact definitions)

| Preset | Format | Compression | Wan steps | Use for |
|---|---|---|---|---|
| `draft` | h264-mp4 | crf 28 | 8 (forced, fast) | Quick composition/motion checks |
| `preview` | h264-mp4 | crf 20 | default (20) | Everyday review, sharing, judging results |
| `master` | ProRes | none | default (20) | **Default.** Final/locked deliverables |
| `lossless` | FFV1-mkv | none | default (20) | Archival, further post-processing |

### Examples
```
# Simplest, recommended: 25-second master-quality transition
python3 skills/generate-plate/tools/generate_transition.py T_day_to_dusk --seconds 25

# Cheaper/faster check before committing to master
python3 skills/generate-plate/tools/generate_transition.py T_day_to_dusk --seconds 15 --quality preview

# Manual control: exact Wan frames + RIFE multiplier (diagnostic)
python3 skills/generate-plate/tools/generate_transition.py T_day_to_dusk --wan-frames 81 --multiplier 4 --quality preview

# Reproduce an earlier result's exact motion at full quality
python3 skills/generate-plate/tools/generate_transition.py T_day_to_dusk --seconds 25 --seed 1783022412

# Silent run (no completion chime)
python3 skills/generate-plate/tools/generate_transition.py T_dusk_to_night --seconds 25 --quiet-sound

# Look up exactly how a past clip was made
python3 skills/generate-plate/tools/generate_transition.py --read-settings transitions/T_day_to_dusk_v003.mp4
```

### What gets saved
- `transitions/TRANSITION_ID_v0NN.mp4` (or the format the quality preset dictates).
- A **sidecar `.json`** with: transition_id, version, seed, wan_frames, multiplier, seconds_requested, quality, format, crf, wan_steps, start/end plate IDs **and exact file names used**, motion_prompt, negative_prompt, deployment IDs, output filename, date.
- The same record appended to `render_log` in the beat JSON.
- A discardable `_wan_raw.mp4` — the pre-RIFE intermediate. Always shorter and generically named; the real deliverable is the properly-named file in `transitions/`.
- A sound: a chime on success, a lower tone on failure (disable with `--quiet-sound`).

### Recovering an interrupted render
If your terminal disconnects mid-render, the job is safe on the server for 7 days. Grab the `Request ID:` printed before the disconnect, then:
```
curl -s -H "Authorization: Bearer $RUNCOMFY_API_TOKEN" "https://api.runcomfy.net/prod/v2/deployments/$RUNCOMFY_DEPLOY_FLF2V/requests/REQUEST_ID/result"
```
(Use `$RUNCOMFY_DEPLOY_RIFE` instead if it disconnected during the RIFE step.) If `"status":"succeeded"`, download the URL it returns with `curl -s -o filename.mp4 "URL"`.

---

## 3. `generate_audio.py` — text-to-audio (ElevenLabs)

Generates all of the film's sound from **text prompts** via the ElevenLabs API. Four modes: `sfx`, `ambience`, `music`, `voice`. (Replaced the earlier MMAudio video-to-audio tool; a backup of that is kept as `generate_audio_mmaudio_backup.py`.)

### Setup (one-time)
```
export ELEVENLABS_API_KEY=your_key_here      # add to ~/.zshrc, then: source ~/.zshrc
```

### Basic usage
```
python3 skills/generate-plate/tools/generate_audio.py MODE "your prompt" [flags]
```
MODE is one of `sfx` (default), `ambience`, `music`, `voice`.

### Flags

| Flag | Effect |
|---|---|
| `--from-transition ID` | Pull the prompt from a transition's `audio_prompt` in the beat JSON; names the file after the transition. |
| `--from-sfx ID` | Pull prompt + duration + influence from the `sfx` section of the beat JSON. |
| `--duration N` | Length in seconds (rounds up to whole second). sfx/ambience cap at 30s; ambience is fixed at 25s. |
| `--influence 0–1` | How literally sfx/ambience follow the prompt (default 0.3; raise for specific motion like a swoosh). |
| `--format mp3\|wav\|flac` | Output format (mp3 default; wav/pcm needs Pro tier; flac transcoded locally from mp3). |
| `--target-db N` | Peak-normalise to this level (default −6). `--no-normalize` to keep raw. |
| `--voice NAME` | Voice name or ID for `voice` mode (`--list-voices` to see options). |
| `--batch N` | N variations back-to-back, fresh each. |
| `--list-voices` | Print available voices and their IDs. |

### Examples
```
# SFX — a swoosh (3 takes to pick from)
python3 .../generate_audio.py sfx "fast whoosh, air rushing past" --duration 1.2 --influence 0.5 --batch 3

# Ambience for a transition, prompt pulled from the beat JSON, named by transition
python3 .../generate_audio.py ambience --from-transition T_day_to_dusk

# A stored SFX recipe from the beat JSON
python3 .../generate_audio.py --from-sfx swoosh_accel --batch 3

# Music — a 3-minute abstract score
python3 .../generate_audio.py music "abstract ambient Andean valley score, sparse flute, drones" --duration 180

# Voice narration
python3 .../generate_audio.py voice "A single plant endures." --voice Rachel
```

### What gets saved
- Versioned file in `audio/{mode}/` — e.g. `audio/ambience/T_day_to_dusk_v001.mp3` (named by transition/sfx ID when pulled from JSON, else by prompt text). Never overwrites.
- A sidecar `.json` with mode, prompt, settings, date.
- Peak-normalised to −6dB by default. A completion chime plays when done.

### Notes / limits
- The **sound-generation endpoint (sfx + ambience) caps at 128 kbps MP3** regardless of tier — fine for diffuse ambience and effects. Music and voice honour higher quality on Creator tier.
- **Ambience prompts must describe ACTIVE, continuous sound** (steady wind, crickets, birdsong) — prompts describing silence or absence ("still cold air," "fading to silence") corrupt the generation.

---

## Quick reference — "what do I run for..."

| I want to... | Command |
|---|---|
| Try 5 lighting variants of a plate | `generate_plate.py PLATE_ID --batch 5` |
| Recover a lost seed from a file | `generate_plate.py --read-seed plates/FILE.png` |
| Make a 25s final-quality transition | `generate_transition.py ID --seconds 25` |
| Cheaply preview a transition first | `generate_transition.py ID --seconds 15 --quality preview` |
| Re-render the same motion at higher quality | `generate_transition.py ID --seconds N --seed SEED` |
| Check what settings made a past video | `generate_transition.py --read-settings transitions/FILE.mp4` |
| Make a sound effect (swoosh) | `generate_audio.py sfx "fast whoosh" --duration 1.2 --batch 3` |
| Ambience for a transition (from JSON) | `generate_audio.py ambience --from-transition T_day_to_dusk` |
| A 3-min score | `generate_audio.py music "abstract Andean valley score" --duration 180` |

---

*This manual reflects the scripts as of 2026-07-03. If a flag doesn't behave as documented, the script may have been updated since — check its `--help` output or ask for a refresh of this manual.*


---

## Appendix — VHS / PAL 4:3 export specs

For the exhibition tape-out (PAL 4:3):

| Setting | Value |
|---|---|
| Resolution | 720 × 576 |
| Frame rate | 25 fps |
| Display aspect ratio (DAR) | 4:3 |
| Pixel aspect ratio (PAR) | 1.0940 (Premiere "D1/DV PAL 4:3") for the hardware/VHS chain |
| Square-pixel equivalent | 768 × 576 at PAR 1.0 (safest for computer/preview playback) |

Master at **720×576 / 25fps / PAR 1.0940 / DAR 4:3** and let the VHS deck impose the analog character (interlacing, softness) during the physical tape-out. The exact full-frame PAR for 720×576 is 1.0667 (16:15); 1.0940 is the broadcast-standard value based on the 704-pixel active area and is what PAL hardware expects.
