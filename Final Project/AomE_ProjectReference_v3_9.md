# AomE — Project Reference Document
**Apple of my Earth** | Samuel Flückiger | CAS in AI in Creative Practices
Last updated: 2026-07-07 | Version: 3.9

---

---
# 🔴 RESUME HERE (updated 2026-07-03)

**Latest beat JSON: `AomE_beats_v1_10.json`** — always use the highest-numbered version present in project files.

**Locked B3-set plates (Act 1, current anchors — these are now Day 1 of a planned 5-day timelapse cycle):**
| State | File | Seed |
|---|---|---|
| B3 day (Day 1 anchor) | A1_andean_B3_pristine_day_v003.png | 1782480124 |
| B3 dusk (Day 1 anchor) | A1_andean_B3_pristine_dusk_v002_v003.png | embedded in file |
| B3 night (Day 1 anchor) | A1_andean_B3_pristine_night_v005.png | not recorded (pre-metadata) |
| B3 dawn (Day 1 anchor) | A1_andean_B3_pristine_dawn_v024.png | 1782735541 |
| B3 terraced (OLD single-mask, flawed) | A1_andean_B3_terraced_v007.png | 1782708061 — kept as fallback only |

A-set (original camera height) remains fully locked as a separate fallback: day/dusk/night/dawn, seeds under `A1_plate_pristine_*`.

**🎯 ACTIVE TASK 1 — sequential multi-mask terraced rebuild (`A1_plate_B3_terraced_v2`):**
Single-mask edits kept causing drift (volcano jumping, wall vanishing, slopes changing). New method: small sequential masked passes, each locked before the next. Pass 1 = left slope only, mask `masks/A1_andean_B3_pristine_day_v003-Pass1-SlopeLeft.png`. Mask-cutting technique — REFINED (2026-07-03), this is the current best method: first make a PRECISE selection of the editable region (Select Sky or similar), fill white on the selection / black on the inverse (Edit → Fill, Select → Inverse, Edit → Fill, Deselect) to get a hard, exact boundary. THEN, with a soft round brush (used: 134px size, 10% hardness), paint white OVER the boundary so the soft feather extends INWARD into the already-protected (black) area — never the other way. This keeps the editable region's precise boundary exact where it matters while softening the transition on the protected side, avoiding both the hard-edge seam and the white-bleeding-into-protected-area problem in one move. Foreground bushes must stay protected (painted black) or they get removed. NEXT: judge current Pass 1 batch, lock best, move to Pass 2 (right slope), then Pass 3 (wall).

**🎯 ACTIVE TASK 2 — five-day timelapse cycle (NEW, 2026-07-03):**
Goal: the Act 1 exhibition loop shows 5 cycles of day→dusk→night→dawn, not 1, for a richer VHS/CRT timelapse. Decision made: do NOT regenerate full landscapes 5× (breaks pixel-lock, reintroduces drift). Instead: current locked plates become Day 1 anchors (`A1_plate_B3_day_1` etc., already wired in JSON). Days 2–5 are siblings — same locked prompt per state, fresh seed each — generated via `--batch`. ALL lighting variants (dusk/night/dawn, every day) relight from the single locked `A1_plate_B3_day1_source` (day 1's plate) to guarantee zero composition drift across all 20 plates. NEXT: batch-generate `A1_plate_B3_day_2` through `_5`, then `dusk_2..5`, `night_2..5`, `dawn_2..5`, one state at a time, picking and locking the best of each batch.

**Also pending / parked:**
- Cultivated terraced (potato/quinoa/oca, no maize, no trees) — instruction written and masked (protects volcano/sky/foreground); apply the same sequential-mask method once bare terraced_v2 is solid.
- Charred — instruction updated (no embers/smolder, no trees, derives from cultivated once locked). Still blocked on cultivated being locked.
- Dawn light direction (sun from wrong side vs. dusk) — text-relight (multiple approaches tried, including shadow-forward wording) could not reliably fix it without also destabilizing the volcano. PARKED. Documented fix: **IC-Light V1** (light-map method, Apache 2.0, deployable on RunComfy) as a dedicated LATER relighting pass. Current locked dawn v024 has light direction as-landed; acceptable for now.
- **Foreground fauna motion (grass/bushes)** — tested extensively in Wan FLF2V transitions (weak wording, then research-backed motion-first + chained-verb + negative-prompt wording). Result: terrain stays perfectly stable but grass shows ZERO movement — FLF2V interpolates only what differs between its two endpoints, and near-identical foregrounds give it nothing to animate. PARKED. Leading alternative: animate in After Effects (displacement/turbulence on a masked foreground layer) — reliable, zero landscape risk, full control over intensity. Alternative: generate foreground as a separate Wan I2V (not FLF2V) element and composite.
- Video transitions (B3): `T_day_to_dusk` VALIDATED end-to-end (Wan 81 frames + RIFE ×4) — first successful B3 transition. `T_dusk_to_night`, `T_night_to_dawn`, `T_dawn_to_day` written but not yet generated. A transition-queue batch function (run several different transitions back-to-back) still not built — worth building once the day-cycle set is complete.
- generate_audio.py (v1.1) — MMAudio integrated and VALIDATED end-to-end (first successful ambient-audio generation on `T_day_to_dusk_v003.mp4`). Now supports: audio-only (default) or `--mux` to also produce a video-with-audio copy (source file untouched); reads `audio_prompt`/`audio_negative` from beat-JSON transitions when given a transition ID instead of `--video`; logs seed/steps/cfg/date to a sidecar `.json` and an `audio_log` array per transition. ffmpeg + Homebrew were installed this session as prerequisites.
- Mentor report (`AomE_Mentor_Report.docx`) — 4-page Word doc built: 3-page reflective essay (approach, ML models used, learnings, VHS/CRT exhibition rationale, authorship) + appendix (skills/models list, exhibition deliverables, open technical hurdles). Delivered for a mentor check-in.

**Working rules (always):**
- Never overwrite a file — always bump the version number, even for tiny edits.
- Never edit the project doc without asking Sam first.
- Switch to Opus for: new prompt crafting from scratch, judgment-heavy creative decisions, major architecture calls. Routine execution (scripts, wiring, status updates) stays on Sonnet.
- generate_plate.py v6.3+ embeds seed + full metadata into every saved PNG and writes a sidecar .json — recover any future seed with `--read-seed path/to/file.png`. Pre-v6.2 files have no embedded seed.
- Known filename gotcha: locking a plate whose asset_path is already a versioned filename can double the suffix (e.g. `_v002_v003.png`) if not careful — check `generate_transition.py`'s `plate_image_file()` expects locked_version to be a plain int OR asset_path to point directly at the real file (locked_version can then be left null).

---


> ⚠️ **Sections 1–4b below (Project Identity through Format & Codec Pipeline) describe the ORIGINAL May-2026 plan — ComfyUI Cloud, FLUX.1 Kontext, Flux.1 Dev, editorial-only transitions.** This was superseded by the RunComfy + Flux.2 pivot (see "Platform & Model Stack — LOCKED v2.0" onward, and the changelog). Kept for historical record per this doc's own versioning practice, but treat everything from "Production Scope & Milestones" onward, plus the RESUME HERE section above, as current. In particular: video transitions ARE generated (Wan FLF2V), not editorial-only as Section 4b states; the model stack is Flux.2 + Wan + RIFE + MMAudio, not Flux.1 Dev/Kontext.

---

## 1. Project Identity

| Field | Value |
|---|---|
| Title | Apple of my Earth (AomE) |
| Author | Samuel Flückiger |
| Institution | University of Bern / ZHdK |
| Programme | CAS in AI in Creative Practices |
| Mentor | Mykhailo Vladymyrov |
| GenAI Expert | Paulina Zybinska |
| GitHub | https://github.com/samuelflueckiger-spec/CAS-AICP.git |
| Project sheet date | 2026-03-02 |

**Hardware (production):**
- MacBook Pro M2 Max, 32GB unified memory (company computer, restricted, some terminal access, ComfyUI works)
- MacBook Air 2026, 24GB unified memory (personal, unrestricted, Claude Code installed here)
- Generation runs on **ComfyUI Cloud** (Blackwell RTX 6000 Pro GPUs) — not local
- Rationale: Apple Silicon Macs have no CUDA (NVIDIA's GPU compute platform); local generation of Flux.1 Dev and Wan 2.2 is impractical on Apple Silicon

**Equipment (exhibition):** CRT (Cathode Ray Tube) television, VHS recorder, headphones, table, chair
**Exhibition:** ZHdK, Gallerie 1, Thu 09.07. (setup) + Fri 10.07.2026 (presentation)

**Exhibition delivery chain (confirmed):**
- VHS transfer service organised — accepts MOV or MP4
- Empty VHS tapes purchased
- CRT TV: sourcing on Ricardo (Swiss marketplace) — 4:3 format, intentional
- Final deliverable: film will be produced in 16:9 throughout production, then converted to 4:3 at the correct CRT resolution in Premiere Pro as the final step before VHS transfer

**Claude Code setup (confirmed 2026-05-31):**
- Installed on MacBook Air, connected to ~/Documents/CAS_AICP/AomE/
- Reads Beat JSON and Project Reference automatically on launch from project folder
- ComfyUI Cloud API key configured via X-API-Key header (local config only — never in chat or project files)
- MCP connection: pending beta access (waitlist submitted). API key is ready for when access is granted.
- Active fallback: direct REST API runner scripts (Python) — does not require MCP beta

**Two viewing modes:**
- **Solo / intended experience** — headphones, one viewer at a time, intimate and immersive
- **Group / presentation** — CRT TV built-in speakers, room listening

**Sound design implication:** Mix must work in both contexts. Headphone mix can be detailed and spatial; CRT speaker mix needs midrange presence (small TV speakers have limited bass and treble). Consider this during sound design phase.

**Curatorial note (relevant for paper):** The intended experience (solo, headphones) vs the presented experience (group, speakers) is a real tension worth reflecting on.

---

## 2. Deliverables

### Practical: Final Film
- AI-generated short film, all audiovisual material generated via generative AI models within a node-based pipeline (ComfyUI)
- Screenplay written by Samuel — retains clear artistic authorship over narrative and thematic intent
- Exhibition format: VHS via CRT + headphones + table/chair
- Distribution format: H.264 MP4
- GitHub repository must be linked and contain at minimum the assessment material

### Written: Reflection Paper
- **Length: 2–3 pages** *(Note: user mentioned 3–4 — official docs say 2–3. Do not over-deliver.)*
- Relates to AI, art, and the practical work
- See Section 5 for full brief and accumulated notes

### Beat JSON (machine-readable production metadata)
- Current version: `AomE_beats_v0.1-draft`
- Living document, versioned per session
- Drives prompts, layer routing, timing, and generation targets

---

## 3. Project Schedule & Milestones

| Date | Milestone | Status |
|---|---|---|
| 2026-01-09 | First version of project sheet | ✅ Done |
| 2026-03-02 | Submission of final project sheet | ✅ Done |
| 2026-04-07 | Mentor meeting (Mykhailo Vladymyrov) | ✅ Done |
| **2026-05-19** | **Mid-term presentation + Phase 1 complete (script & storyboard)** | ✅ Complete |
| **2026-05-31** | **Meeting with GenAI visuals expert (Paulina Zybinska)** | 🔜 11 days |
| 2026-06-15 | Mentor meeting (Mykhailo Vladymyrov) | 🔜 |
| 2026-06-15 | Phase 2 complete: image & sound generation | 🔜 |
| 2026-07-01 | Phase 3 complete: editing & post-production | 🔜 |
| 2026-07-09 | Phase 4 complete: exhibition preparation | 🔜 |
| 2026-07-09 | ZHdK setup day | 🔜 |
| 2026-07-10 | Exhibition at ZHdK, Gallerie 1 | 🔜 |
| 2026-08-02 | Poster session registration deadline (tentative) | 🔜 |
| 2026-08-24 | Poster upload deadline | 🔜 |
| 2026-08-28 | Graduation event + poster session, Bern | 🔜 |

---

## 4. Production Pipeline (Current State)

```
Screenplay (Final Draft)
        ↓
Beat JSON (LLM-orchestrated, versioned) — provides parameters
        ↓
Claude Code (on MacBook Air) + ComfyUI skill (SKILL.md)
        ↓
Runner script (Python) — calls a SMALL set of PRE-TESTED workflow templates
        ↓
ComfyUI Cloud (executes on cloud GPU):
  • PLATE GENERATION — FLUX.1 Kontext Dev (reference image → composition-guided generation)
  • Layer generation — Flux.1 Dev (text-to-image for layers not needing composition control)
  • Matting / background removal — ComfyUI-RMBG (unified node: BiRefNet, RMBG-2.0, SAM3, BEN2, etc.)
  • Selective: Nano Banana Pro (partner node, photorealistic detail passes)
  • Lighting harmonisation — IC-Light V1 (Apache 2.0, commercial-safe)
  • Motion / video — Wan 2.2 (image-to-video)
  • Music / cinematic audio — Stable Audio 2.5/3.0 (text-to-audio)
  • Diegetic / ambient sound — MMAudio (video-to-audio, syncs to generated footage)
        ↓
Auto-download script → local project folder → GitHub
        ↓  [fallback: After Effects if IC-Light insufficient]
Deterministic stacking + per-beat compositing — After Effects
        ↓
Final edit + audio mix + 4:3 conversion — Premiere Pro
        ↓
Exhibition master → VHS → CRT installation
```

**Orchestration approach — composable Claude Skills + ComfyUI Cloud templates:**
Building on critical review of two sources — (1) the Maciej Dziuba tutorial (which identified fragility in on-demand graph generation), and (2) Anthropic engineers' "Claude Skills" methodology (Skills paradigm, late 2025–2026) — the project uses a composable Skills architecture.

**Architecture:**
1. Stable, tested workflow templates live in ComfyUI Cloud (one per generation task)
2. A library of Claude Skills lives on the MacBook Air — each skill has three layers: description (auto-trigger), instructions (playbook), tools (Python scripts + template references)
3. Beat JSON supplies parameters (prompts, references, settings)
4. Claude Code auto-invokes the right skill based on the request; skills chain together for full beats
5. Auto-download script retrieves outputs

**Planned skills (composable, not monolithic):**

*Generation skills:*
- `/generate-plate` — background plate via Flux.1 Dev
- `/generate-foreground-layer` — foreground element + matting via ComfyUI-RMBG
- `/relight-layer` — LBM Relighting harmonisation pass
- `/animate-still` — image-to-video via Wan 2.2
- `/generate-music` — text-to-audio via Stable Audio
- `/generate-ambient` — video-to-audio via MMAudio

*Utility skills:*
- `/read-beat` — parse Beat JSON, return parameters for one beat
- `/beat-status` — report what is generated vs pending
- `/log-discovery` — record insights, failures, edge cases (feeds the paper)

**Why composable beats monolithic:**
- Localised failures: if matting breaks, only `/generate-foreground-layer` is affected
- Compounding improvements: fix `/animate-still` once, every beat using it gets the fix
- Auditable: each skill documents one methodological choice — directly useful for the paper
- Skills improve session over session: after each use, the discovery is whether it's a one-time fix or a permanent skill update

**Why this is right for AomE specifically:**
- Removes node-graph debugging from the author's plate (no workflow expertise needed)
- Keeps generation consistent (Skills + tested templates eliminate on-demand graph generation fragility)
- Provides a learning system, not a one-shot tool — relevant paper material

**Model rationale:**
- **FLUX.1 Kontext Dev** (Black Forest Labs, 12B parameter Diffusion Transformer): primary model for PLATE GENERATION. Takes a reference image + text prompt as input. Preserves composition structure (camera angle, element positions) while applying changes (lighting, atmosphere, era). Solves composition control without ControlNet. Available on ComfyUI Cloud as commercially cleared model. License note: Dev version is Non-Commercial per Black Forest Labs, but ComfyUI Cloud's stated policy clears all hosted models for commercial use — platform's responsibility to manage.
- **Flux.1 Dev** (Black Forest Labs): used for layer generation (foreground elements, subjects, effects) where composition control via reference image is not needed.
- **ComfyUI-RMBG v3.0.0** (unified node, updated Jan 2026): provides matting and background removal across multiple models — RMBG-2.0, INSPYRENET, BEN, BEN2, BiRefNet, SDMatte, SAM, SAM2, SAM3, GroundingDINO. Tested per layer type to find best fit. Replaces standalone BiRefNet for flexibility.
- **IC-Light V1** (lvmin Zhang, 2024, Apache 2.0): primary lighting harmonisation model. Commercial-safe for exhibition and post-CAS online distribution.
- **LBM Relighting (JasperAI) — REMOVED:** CC BY-NC 4.0 license (non-commercial only). Incompatible with planned post-CAS online distribution. Same issue as IC-Light V2 which was previously excluded for the same reason.
- **IC-Light V2 — REMOVED:** non-commercial license, same incompatibility.
- **Wan 2.2** (Alibaba): primary video/motion generator. Strong temporal coherence (frame-to-frame consistency).
- **Nano Banana Pro** (Google, partner node on ComfyUI Cloud): used selectively for photorealistic detail passes where its strengths matter most.
- **Stable Audio 2.5 / 3.0** (Stability AI, ComfyUI Cloud partner node): text-to-audio for music and cinematic atmosphere.
- **MMAudio** (video-to-audio): synchronised ambient sound matched to scene content. Used for diegetic and atmospheric sound layers.
- **LayerDiffuse — REMOVED:** does not support Flux.1 Dev (SD15/SDXL only). Approach changed to Flux generation + ComfyUI-RMBG matting. Simpler, more reliable, no functional loss.

**Compositing philosophy:**
Generative models (LayerDiffuse, IC-Light) handle layer generation and lighting integration. After Effects handles deterministic stacking, timing, and grade. IC-Light is the primary compositing harmonisation tool; AE is the confirmed fallback if lighting consistency cannot be achieved generatively.

---

## 4b. Format & Codec Pipeline (IMPORTANT)

**Key principle (UPDATED 2026-07-05): the deployed ComfyUI Video Combine node CAN output ProRes directly — this was confirmed and is now used in production, including for the Wan→RIFE intermediate.** The original assumption (models only emit MP4, ProRes made only in post) proved too conservative. Plates are still PNG; final delivery is still H.264 MP4 for the VHS transfer. But the master-quality path is lossless from Wan onward, not h264-until-post — see the full fix story below (FFV1 → ProRes+413 → URL hand-off).

### What each tool outputs

| Tool | Output format |
|---|---|
| Flux.1 Dev (image generation) | PNG |
| LayerDiffuse (transparent layers) | PNG with alpha (transparency) |
| BiRefNet (background removal) | PNG with alpha |
| IC-Light (lighting harmonisation) | PNG (with alpha if input had it) |
| Nano Banana Pro (detail passes) | PNG |
| Wan 2.2 (video/motion) | MP4 |
| After Effects (compositing) | ProRes 4444 (preserves alpha) / ProRes 422 HQ |
| Premiere Pro (final edit) | ProRes 422 HQ (master) → H.264 MP4 (delivery) |

### Worked example — Beat A1_B001 "Fade in on untouched Andean valley"

This beat has three elements, each with a different path:

**Element 1 — Background plate (the valley):**
Generate in ComfyUI Cloud (Flux.1 Dev) → PNG → import to After Effects. Simplest path.

**Element 2 — Soil patch (static foreground, needs transparency):**
1. Generate (Flux.1 Dev) → PNG
2. Cut out background (BiRefNet) → PNG with alpha
3. Light-match to plate (IC-Light) → PNG with alpha
4. Import & stack in After Effects

**Element 3 — Smoke plume (moving element):**
1. Generate still frame (Flux.1 Dev) → PNG
2. Animate (Wan 2.2) → MP4
3. Import, anchor to volcano summit, set "screen" blend in After Effects

### The in-between steps the author manages

**ComfyUI Cloud (via Claude Code + runner):** generate elements → outputs auto-download to local project folder as PNGs and MP4s.

**After Effects (per-beat assembly):** stack plate + alpha layers + video → apply timing/transitions → **export finished beat as ProRes 4444** (4444 chosen to preserve transparency for potential reuse).

**Premiere Pro (final, much later):** edit all finished beats together → add sound → export **16:9 master (ProRes 422 HQ)** for archive/online → convert to **4:3 at CRT resolution → H.264 MP4** → VHS transfer service.

### One-sentence summary
ComfyUI gives PNGs and MP4s. After Effects turns layers into finished beats (ProRes). Premiere turns beats into the film (ProRes master → MP4 for VHS).

### Plate philosophy & lighting variants

**Plates are single, clean, static environmental states.** One lighting condition each. No smoke, no plant, no animals, no humans, no transitions, no time passing. Anything that moves or changes is a separate layer.

**Plate generation method: FLUX.1 Kontext**
Reference image fed directly to Kontext → text prompt specifies changes only (remove smoke, change to dusk lighting, change to moonlit night). Composition is preserved structurally by the model. This replaces both ControlNet (not available on ComfyUI Cloud — commercial-cleared policy excludes non-commercial models) and basic img2img (which was evaluated but superseded by Kontext's superior composition preservation).

**Lighting variants:** When a location appears across multiple lighting states, generate a separate plate per state. Example — the Andean pristine valley exists as four plates:
- `A1_plate_pristine_day` (B001, B002)
- `A1_plate_pristine_dusk` (B003)
- `A1_plate_pristine_night` (B004–B007)
- `A1_plate_pristine_dawn` (B008)

**Time-lapse / day-to-night transitions** are handled editorially in AE/Premiere by transitioning between two plate variants — NOT generated as single plates. Flagged beats: A1_B009 (pristine→terraced), A2_B005 (regrowth cycle).

**Total plates: 17** (11 base states + 6 lighting/atmosphere variants). Generation is cheap (~30s each); the work is prompt quality, which is why prompts are written and reviewed in the JSON before generation.

### Transitions & timing — AE/Premiere only

**Principle:** Fades, dissolves, crossfades, hold frames, and all time-based transitions are handled exclusively in After Effects (per-beat) and Premiere Pro (final edit). Generation models produce full-visibility, full-opacity content.

**Why:** Asking AI models to produce a fade is wasteful (each iteration costs GPU time, loses precision, can't be adjusted without regeneration). AE/Premiere give frame-precise control that can be tweaked freely.

**Distinction in the JSON:**
- `transition_in` / `transition_out` / `transition_in_duration_sec` — AE/Premiere stage directives. Documented in the JSON for the director's intent, but never prompted into generation.
- `opacity` values on layers — kept for generation as final blend states (e.g. smoke at 0.7 means semi-transparent against sky in the final composite, not a fade).
- `motion: flower_bloom_then_fade` — content motion sent to Wan 2.2 (the flower visually wilting within the shot). "Fade" here is content, not a transition.

This separation keeps generation prompts simple and creative control where it belongs.

---

## Production Scope & Milestones

The film is delivered in two milestones:

**Milestone 1 — July 10 exhibition (ZHdK Gallerie 1): Act 1 complete**
A fully realised, polished Act 1 (~90 seconds, 12 beats). Act 1 is a complete narrative arc on its own — pristine valley through plant growth, harvest, terrace-building, volcanic eruption, to aftermath and rebirth — and expresses the full "protection gap" theme independently. This is the firm exhibition deliverable. Scoping to one complete act prioritises quality over runtime and de-risks the deadline. The full pipeline is proven end to end on Act 1.

**Milestone 2 — August 28 poster presentation + graduation (Bern): Full film**
All three acts complete. Act 1's proven pipeline and architecture extend directly to Acts 2 and 3 (Alpine valley, Mars chamber) — nothing built for Act 1 is discarded. The reference images, Kontext instructions, and plate prompts for all three acts already exist in the Beat JSON.

**If Act 1 finishes early:** extend into Acts 2-3 before July rather than waiting. The phasing is a priority order, not a hard wall between the acts.

## Platform & Model Stack — LOCKED (v2.0)

**Platform: RunComfy (single platform).** Chosen over a ComfyUI-Cloud / RunComfy hybrid because RunComfy is a true superset — full Flux.2 Dev support plus ControlNet, depth, inpaint, and a broad open-model library — so one platform does everything with no routing complexity and no cross-platform look mismatch. The one thing forfeited is ComfyUI Cloud's commercial licensing clearance; irrelevant for the CAS (academic), a separate bridge only if the film is ever distributed commercially.

**Ethical constraint: Tier 1 — open-weights models only, no closed proprietary APIs.** Every model in the pipeline has openly available, runnable, inspectable weights. No Kling / Seedance / Flux.2 Pro / Nano Banana black boxes. This makes the whole pipeline transparent and reproducible — a clean narrative for the paper.

### The locked stack

| Stage | Model | License |
|---|---|---|
| Base generation | Flux.2 Dev (text-to-image) | Open weights, non-commercial |
| Variant editing (primary) | Flux.2 Dev (image edit) | Open weights, non-commercial |
| Variant editing (alt, structural) | Qwen-Image-Edit-2511 | Apache 2.0 |
| Structural control | ControlNet depth + Depth Anything V2 + inpaint | Open |
| Segmentation / matting | BiRefNet / SAM 3 / RMBG-2.0 | Open |
| Relighting | IC-Light V2 | CC BY-NC (open weights) |
| Video / motion | Wan 2.2 | Apache 2.0 |
| Music | Stable Audio Open | Open weights |
| Ambient audio | MMAudio | Open |

**Location-invariance technique (the reason for the platform move):** depth + inpaint. A mask protects the locked regions (volcano, sky, valley); new content (terraces, atmosphere) is generated only inside the mask. The protected pixels come straight from the locked base, so they cannot drift. Optionally test Qwen-Image-Edit-2511 against Flux.2-edit for structure-critical edits — its region-preservation may hold the location with less masking.

**Two ethics footnotes for the paper:**
1. Flux.2 Dev and IC-Light V2 are open-weights but non-commercial — academic use permitted; this is the one licensing asterisk on an otherwise fully-open stack.
2. Openness secures transparency, access, and reproducibility, but does NOT resolve training-data provenance and consent — that applies equally across all these models and must be named directly, not glossed by "open."

## Location Invariance — Core Structural Principle

**STATUS UPDATE (2026-06-12): Act 1 pristine base LOCKED — v018, seed 1781266837, Full quality, RunComfy.**
The establishing plate for the entire Act 1 location is final. Composition: very low ground-level camera
on an elevated hillside, steep slopes framing a narrow valley, layered receding ridges in aerial haze,
small distant snow-capped volcano center-right on the far horizon (flat-summit profile), completely clear
cloudless sky (sky is a composited layer), reddish-brown soil foreground with an angled off-center upper
edge and open bottom-center for the plant anchor. Locked after 18 iterations across two platforms.
All other Act 1 states now derive from this plate.


**Within each act, the location never changes.** This is mandatory to the film's concept: the audience watches a single fixed place transform through time.

- **Act 1:** the same Andean valley across pristine → terraced → volcanic → charred
- **Act 2:** the same Swiss Alpine valley across pristine → evening → evacuated → destroyed → submerged
- **Act 3:** the same Mars chamber — and crucially the same landscape seen through its windows — across thriving → decaying → failing → destroyed

**Production consequence:** each act has exactly ONE fresh base plate, generated via Flux.2 text-to-image and then locked. Every other state in that act is produced by Flux.2 image edit *from that locked base* (or from an already-locked intermediate). The location is never re-generated, so it cannot drift between states.

This means only **three fresh generations for the whole film** (one establishing plate per act). All 14 remaining plates are edits. Derivation chains are locked stepwise — e.g. Act 1: pristine_day (locked) → terraced (locked) → volcanic/charred — so each edit starts from an approved, fixed ancestor.

This principle also strengthens the paper: it reframes the pipeline as *one authored location per act, deterministically transformed*, rather than a series of independently generated images that merely resemble each other.

## Reference Generation Strategy (v1.6 — key change)

**Problem identified:** Kontext is an editing model. For low-change plates it stays very close to the source image and faithfully reproduces source artifacts (the ChatGPT references' lego-brick soil, unnatural grass, white dots). A reference's flaws become the plate's flaws.

**Solution:** Generate the base references *fresh* via Flux text-to-image instead of editing the ChatGPT images. Flux produces clean, photorealistic output with no inherited ChatGPT artifacts, at native 16:9 resolution (sidestepping the Kontext stitch/scaling issue entirely). The ChatGPT references are demoted to *composition guides* — used to author the generation prompts, not as pixel sources.

**Four fresh base references** (generated text-to-image, then locked):
- `A1_plate_pristine_day` — Andean pristine valley
- `A1_plate_terraced` — Andean terraced valley (structurally distinct, generated fresh rather than Kontext-transformed)
- `A2_plate_pristine` — 1930s Swiss Alpine valley
- `A3_plate_chamber_thriving` — Mars agricultural chamber

**All other plates (13) derive from a locked base via Kontext.** Because the base is now clean Flux output, Kontext preserves clean content — its preservation behavior becomes an asset.

**The generation prompts live in the Beat JSON** (`generation_prompt` field on each base plate). They are the source of truth; nothing is copy-pasted. The script reads them directly.

**Model:** base generation currently uses Flux.1 Dev text-to-image (high quality, available, proven). Optional future upgrade: if Flux.2 text-to-image is available on ComfyUI Cloud, export its template and swap it in for an even higher quality ceiling on the four hero references.

**This keeps the project on ComfyUI Cloud.** The RunComfy + ControlNet-depth pivot remains the documented fallback if fresh text-to-image generation + curation cannot produce a usable composition for a given act (precise composition control is the one thing text-to-image can't guarantee).

## Refinement Techniques Catalogue

A living record of approaches developed to adjust generated content during production. Each entry documents the problem it solves, how to use it, and when to prefer it over alternatives. Starts with plate refinement; video/motion techniques will be added as that phase begins.

---

### PLATES

#### RT-01 — Prompt Refinement + Seed Reuse
**Problem:** A generated base plate has good composition but a specific element needs changing (wrong shape, missing detail, inaccurate character).
**Approach:**
1. Edit the `generation_prompt` in the Beat JSON for the plate
2. Run with `--reuse-seed` to keep the same starting noise
3. Flux.2's Mistral text encoder responds to the updated description while the seed preserves large-scale composition (volcano placement, valley structure, soil distribution)
4. Choose Turbo for fast iteration; once the element reads correctly, run Full to lock quality

**When to use:** Small-to-medium changes to a specific element where the surrounding composition is already good. Works best when the change is descriptive (shape, quality, character) rather than positional (moving an element to a different part of the frame).
**Limitation:** --reuse-seed is not a guarantee of identical composition — same noise + different prompt = similar but not pixel-locked. Large prompt changes will drift the composition.
**Example used — Act 1 pristine base (A1_plate_pristine_day), locked at v007:**
This base took seven iterations and surfaced several reusable prompt-craft findings:

1. *Volcano summit shape.* "Crater opening at the tip" made Flux render a bowl facing the camera — geologically wrong from a distant profile view. Lesson: never use crater/opening language when the viewpoint doesn't permit seeing into the crater. The phrasing that worked: "seen in profile with a barely perceptible flat summit rather than a sharp point, in silhouette against the sky." Describe the silhouette edge, not the interior.

2. *Element distance and scale.* "Far horizon / small and distant" pushed Sabancaya too far back and shrank its presence (it is the film's central threat and must stay readable). "Set a little deeper beyond the valley" was the calibrated middle — more depth without losing presence. Lesson: distance adjectives are strong levers; "a little deeper" beats "far."

3. *Cinematic depth of field.* "Strong shallow depth of field / pronounced bokeh" over-blurred the frame. "Shallow depth of field — foreground soil in sharp focus, middle ground and background gently softening with a natural falloff" gave the cinematic look without losing the volcano. Lesson: "gentle / natural falloff" beats "strong / pronounced" for landscape plates where the background still needs to read.

4. *Process.* Composition-level changes (volcano distance, DoF) held well under --reuse-seed because the underlying noise was preserved — the same composition refined rather than reshuffled. This makes --reuse-seed the right tool for tuning an already-good frame, and a fresh seed the right tool for finding a new composition.

Final locked frame: Sabancaya at believable distance with a subtly flattened summit, sharp reddish foreground soil with open bottom-center for the plant anchor, gentle depth falloff into a hazy valley. Generated at Full (20-step) quality.

---

#### RT-02 — Flux.2 Image Edit (Surgical Element Change)
**Problem:** A generated base plate is very close to final but has one specific element to fix, and a full regeneration risks losing the rest of the composition.
**Approach:**
1. Load the approved plate image directly into the Flux.2 Image Edit workflow in ComfyUI Cloud's web UI
2. Write a targeted edit instruction: "Keep this composition exactly. Change only: [specific element]. Everything else unchanged."
3. Flux.2's ReferenceLatent mechanism preserves the composition while responding to the targeted change
4. Download the result; if better, use it as the new base

**When to use:** When the composition is locked and only one element needs surgical correction. More precise than prompt refinement for small, localised details. Particularly useful after a base has been approved at Full quality (regenerating at Full is slow; a surgical edit preserves the investment).
**Limitation:** Works best for surface/appearance changes. Structural/positional changes (moving the volcano to the other side of the frame) require a full regeneration instead.
**Example use case:** Planned for use if --reuse-seed + prompt refinement (RT-01) drifts the composition unacceptably while fixing the volcano summit.

---

#### RT-03 — Location-Invariant Structural Edit (Depth + Inpaint)

**Problem:** add or change structure within a locked location (e.g. terraces on the slopes) without the protected regions (volcano, sky, valley) drifting. Whole-image editing fails this — it regenerates the whole frame and the volcano jumps.

**Approach (RunComfy):** combine two controls. An **inpaint mask** protects the locked regions — those pixels are copied untouched from the locked base, so they cannot move. **ControlNet depth** (from Depth Anything V2) governs the masked region so new structure follows the real slope contours. Only the masked area is regenerated; everything else is pixel-identical to the base.

**When to use:** any structural change inside a locked location — terraces, erosion, new landforms. Also test Qwen-Image-Edit-2511 (Apache, region-preserving) as a possibly-simpler alternative for edits that need less masking.

**Status — IMPLEMENTED as workflow (2026-06-12), awaiting first validation on the terraced plate.**
`flux2_masked_edit.json` built on the production Flux.2 image-edit graph. v1 design decisions:

1. **Root cause fixed:** the stock edit workflow samples from an *empty latent* (pure noise), regenerating
   every pixel — that is why whole-image edits drifted. The masked workflow samples from the *VAE-encoded
   locked base* with `SetLatentNoiseMask`: only the white (editable) mask region is renoised and
   regenerated; protected regions stay anchored.
2. **Mathematical invariance guarantee:** a final `ImageCompositeMasked` node copies all protected pixels
   bit-exactly from the locked base back over the result. Invariance does not depend on model behavior —
   the model's only job is good content in the editable region and a clean seam (soft Photoshop mask
   edges feather the blend).
3. **Zero custom nodes (v1):** all core ComfyUI nodes — deploys on RunComfy with no installs. ControlNet
   depth deliberately deferred: the masked region regenerates with the full original as reference, which
   may already produce contour-following terraces. **Escalation path (v2) if terraces ignore slope
   geometry:** add Flux.2 depth control (Alibaba FLUX.2-dev-Fun-Controlnet-Union + community node,
   fp8-verified, or depth map as additional ReferenceLatent — zero-node fallback).
4. **Masks are production assets:** painted once per locked base in Photoshop (white = editable,
   black = protected, soft edges), kept as versioned PSD/PNG, reused for all structural edits on that
   base (terraced, volcanic, charred) and as template logic for Acts 2–3.

**Test protocol:** interactive RunComfy session first (visual debugging of mask + instruction), then
Export (API) → serverless deployment (24G A10G/A5000, min 0, max 1, queue 1, keep-warm 180–300s during
iteration) → new `masked_edit` mode in generate_plate.py.

---

### VIDEO / MOTION

#### RT-04 — Dynamic Atmosphere as a Composited Layer (sky, smoke, pyroclastic cloud)

**Principle:** nothing dynamic is baked into the plate. The plate is a still stage; every moving element — sky/clouds, volcanic smoke, the pyroclastic cloud — is a separate layer composited over it in After Effects. This gives full per-beat art direction and keeps the locked location untouched.

**Sky/clouds:** base plates are generated with a CLEAR cloudless sky. Clouds are added as their own moving layer, so cloud motion, density, and per-time-of-day character are controlled directly, and the sky can darken/be overtaken as the eruption builds. Note: the sun and moon discs are NEVER part of this layer — see 'Celestial Bodies — Out of Frame'. Only their light appears, baked into the relit plates.

**Pyroclastic cloud workflow:**
1. Generate the ash column / pyroclastic flow as its own video element in Wan 2.2, against a plain or dark background for easy isolation.
2. Use the locked base's **depth map** to place it in 3D: correct occlusion (the flow passes behind the near framing ridges, spills into the valley) and correct scale (huge near camera, small at the distant summit).
3. Composite over the still plate in After Effects, masked by the foreground terrain, with matching haze and color.
4. As it advances toward camera it fills the frame and overtakes the composited sky layer — the serene sky consumed by ash, a direct visual of the protection-gap theme.

**Why depth matters here:** the same depth map generated once per locked base serves both the structural plate edits (RT-03) and the video-layer placement — shared infrastructure, generated once, reused throughout.

---

---

## Platform Strategy & Pivot Plan

### Current decision: ComfyUI Cloud first

The project runs on **ComfyUI Cloud** as the primary platform. Rationale:
- Pipeline already proven end to end (REST API, upload, generate, download all working)
- FLUX.1 Kontext Dev available and confirmed working
- Every model on the platform is stated to be cleared for commercial use — important for post-CAS distribution
- No migration cost; work continues immediately

### Known limitations that may force a pivot to RunComfy

These are documented in advance so the decision to switch is evidence-based, not reactive:

1. **No ControlNet for Flux** — ComfyUI Cloud's commercial-cleared policy excludes the (non-commercial) Flux ControlNet models. Composition control relies entirely on Kontext's reference-image preservation.
2. **No depth maps** — DepthAnything V2 and similar preprocessors are not available, so explicit spatial/depth control is not possible.
3. **Resolution control with Kontext** — Kontext's FluxKontextImageScale auto-scales to ~700px per side, requiring upscaling to reach 1920×1080. Native high-resolution control is limited.
4. **API deployment** — ComfyUI Cloud's programmatic API is more limited than RunComfy's one-click workflow-to-API deployment (as of mid-2026).
5. **Model selection** — curated commercial-only set; newer or specialised models may be unavailable.

### Pivot triggers — when we switch to RunComfy

The switch to RunComfy happens when **either** of these is true:

- **Quality/creative wall:** Sam is unhappy with results that cannot be resolved on ComfyUI Cloud — composition drifts unacceptably, resolution is insufficient, or required control is impossible.
- **Technical wall:** Claude identifies that a needed capability (ControlNet, depth maps, higher native resolution, finer control) is genuinely unavailable on ComfyUI Cloud and is blocking progress.

When a trigger is hit, Claude flags it explicitly and recommends the switch. RunComfy provides: Flux ControlNet (depth/canny), depth map preprocessors, broader model selection, and one-click workflow-to-API deployment. The runner script migrates with a one-line URL change since RunComfy uses the same standard ComfyUI REST API.

### What carries over if we pivot

- The Beat JSON (single source of truth) — unchanged
- The Kontext workflow and instructions — work on RunComfy too
- The runner script — one-line endpoint change
- All reference images and plate prompts — unchanged

The pivot is low-friction by design. Starting on ComfyUI Cloud is not a commitment that's expensive to reverse.

## Video Model & Transition Method — LOCKED (v2.3)

**Video model: Wan 2.2 (Apache 2.0, open weights, on RunComfy).** Locked for the whole film.

**Transition method: Wan 2.2 FLF2V (First-Last Frame to Video).** Each transition between two states is generated as a video clip whose first and last frames are pinned to our two relit plates; the model generates coherent in-betweens following a text prompt. This is why the small inter-plate drift (a few px) is a non-issue: FLF2V enforces both plates as ground-truth boundaries and absorbs the drift into generated motion across the clip — no still-to-still cross-dissolve, no swimming.

Consequences:
- **Lower-denoise relighting is NOT needed** (kept only as a fallback). Full relights keep their drama; the video stage handles geometric continuity.
- **Seamless loop for free:** because adjacent transitions share a boundary plate (dusk is the end of day→dusk and the start of dusk→night), segments chain with no seams — day→dusk→night→dawn→day. This is the CRT loop, expressed by the pipeline.
- FLF2V is explicitly suited to "sunrise to sunset" lighting journeys — our exact use case.


**Opus signals for AomE:** B-set prompt crafting; new plate prompts from scratch; major film architecture decisions; plant generation prompts. Switch to Opus when getting the prompt wrong costs an expensive render.

## B-Set Plates — Exploratory Parallel Set (v2.9)

**Decision (2026-06-24):** The mask-editing approach to derive a B-set pristine from the terraced v011 was abandoned — masked edits of v011 could not reliably reconstruct a consistent foreground. The B-set will be generated as a **fresh text-to-image set**, not derived from any existing plate.

**What the B-set aims to achieve vs the locked A-set:**
1. **Camera lower to the ground** — more pronounced ground-level intimacy, the soil fills a larger/closer foreground band, creating a more layered depth-of-field falloff (sharp FG soil → soft background).
2. **Narrower effective frame** — camera so low that humans and animals interacting with the plant are only partially visible (legs, hands, partial torso) — reinforcing the film's formal constraint.
3. **Cinematic DoF quality** — the reference image (AomE_ReferenceContext_Act01.png) and terraced v011 (seed 1782221056) are the visual targets for these qualities.

**What must stay the same as the A-set:**
- Same Andean valley composition — the two framing slopes, the V-shaped valley, Sabancaya volcano in the distance, reddish-brown volcanic soil, high-altitude daylight.
- Same pixel-precise derivation chain once the B-day plate is locked: B-dusk, B-night, B-dawn, B-terraced all derive from B-day via the same masked-edit workflow.

**A-set stays locked and untouched** — it is the fallback. B-set plates only replace A-set if Sam is genuinely satisfied. Nothing in the A-set is deleted or overwritten until that decision is made.

**B-set plate IDs:** A1_plate_B_pristine_day, A1_plate_B_pristine_dusk, A1_plate_B_pristine_night, A1_plate_B_pristine_dawn, A1_plate_B_terraced.
**B-set file paths:** plates/A1_andean_B_*.png (never overwrite A-set files).

**Next action for B-set:** craft the t2i prompt for A1_plate_B_pristine_day, targeting the v011/reference-image camera height + DoF + partial-figure framing. Switch to Opus for prompt crafting (judgment-heavy creative decision).

## Plant Workflow — Architecture (v2.8, grounded in screenplay)

**Source of truth:** the 12-beat screenplay (AotE_V01_20260515). The plant's full arc is now encoded into the beat JSON per-beat as `plant_state` (narrative state — was already present) + `plant_production` (production spec — added v0.47). Future sessions read the plant requirements from the beat JSON, not the screenplay file directly.

**The plant is a generated-video protagonist, not a still asset.** 9 of 12 Act 1 beats are MOTION (generated as video elements via Wan FLF2V, same pipeline as the lighting transitions); only B004 and B007 are near-still holds; B001 has no plant. Decision (Sam): plant motion = generated video elements, not AE composite-animation.

**Per-beat plant method (Act 1):**
- B001 none (absent) · B002 video (hero growth: bare soil→mature plant) · B003 video (flowering + bee layer) · B004 still/subtle (+llama partial) · B005 video (leaves stirred by llama/puma) · B006 video (digging reveals tubers) · B007 still/subtle (exposed papas hold) · B008 video (uprooting by woman's hands) · B009 video (heal→regrow, ties to terraced plate) · B010 video (trembling, volcanic plate states) · B011 video (incineration→charred) · B012 video (rebirth seedling→Act 2 morph)

**Three NEW assets the screenplay demands (were not previously tracked):**
1. **Underground tuber layer** (B006, B008) — the papas beneath the soil, revealed by digging and dangling when uprooted; must read as belonging to THIS plant.
2. **Charred plant state** (B011) — plant incinerated by the pyroclastic wave.
3. **Rebirth seedling** (B012) — fresh green sprout against charred earth, mirrors B002.

**Multi-layer choreography:** the plant interacts with separate partial-figure layers (bee, llama, puma, woman's hands), and in several beats those layers physically drive the plant's motion (digging, uprooting, brushing). Not just plant-over-plate.

**Pipeline per plant element:** generate (Flux/Wan) → matte to alpha (ComfyUI-RMBG, fine leaf edges) → relight per lighting state (IC-Light) → composite at anchor [0.5,0.78] in AE. Motion elements use Wan FLF2V (first/last frame) + RIFE, exactly as transitions.

**Identity continuity is the central challenge:** must read as the SAME plant across growth/bloom/uproot/char/rebirth. Next action when starting plant work: B002 hero growth shot first — it establishes the identity all later beats must maintain.

## Video Generation — Operational Findings (v2.7)

**Wan frame ceiling is a VRAM question:**
- A6000 (48GB): chokes above ~25 frames at 720p — 67 frames caused CPU-offload thrashing (102s/step, 34-min render) and DEGRADED output (first plate → gray). Do NOT use A6000 for Wan beyond ~25 frames.
- A100 (2X Large, 80GB): renders Wan's full native **81 frames cleanly** (validated). **81 frames = the no-compromise ceiling** (model's training max, 5s @16fps). Wan deployment now on A100.

**The keeper recipe:** 81 real Wan frames + RIFE multiplier for length (maximal real motion, minimal interpolation). Validated end-to-end: 81 Wan → RIFE ×4 → ~13s @25fps, clean, no flaws.

**Origin of the RIFE stage — Sam's contribution:** Wan FLF2V has a hard native ceiling (81 frames, ~3.2s at 25fps) that cannot be extended by prompting or settings. When this length ceiling became a real blocker for usable transition clips, Sam proposed chaining a frame-interpolation pass after Wan rather than accepting the short native length — this is what led to adopting RIFE as the second pipeline stage, turning a hard model limitation into a solved, tunable length-control system (`--seconds N`).
- Default planning should generate 81 Wan frames then RIFE-bridge to target (script change pending — see next actions).

**Cost discipline (A100 = $3.99/hr, video is the expensive stage):**
- Keep-warm bills the full hourly rate during the warm window, job running or not. Use **600s while batching**, **drop to 60s when stopping** (biggest leak: A100 left warm idle/overnight).
- Iterate cheap (`--quality draft`, 8 steps), finalize expensive (`--quality master`, 20 steps ProRes) ONCE per keeper. Lock seeds so masters never get re-rolled.
- RIFE stage is negligible cost (16GB machine, fast).

**Robustness fixes:** transition script now retries on network blips (a dropped poll no longer kills a render — job is safe on server 7 days, recover via /result curl with the request ID). Added `--wan-frames N` (force frame count) and confirmed `--quality draft|preview|master`.

**Audible render-complete notification — Sam's idea:** Sam proposed a sound alert on render completion so he could step away from the machine during long Wan/RIFE renders and hear from another room when it was safe to start the next one, keeping the GPU instance warm rather than idling between jobs. Implemented via macOS's built-in `afplay` (no new dependency): a chime on success, a distinct lower tone on failure, disableable with `--quiet-sound`.

**Prompt finding — motion direction must be explicit:** vague "shadows lengthening" let the model crawl shadows the WRONG way (down = sunrise) on a dusk transition. Fixed by naming direction: sun SETTING low-right, shadows CLIMB UP. Seed also affects motion — re-roll seed if direction wrong, then lock it. Foreground life ("faint breeze in grass") added without breaking the static-camera hold.

## Video Pipeline — BUILT & VALIDATED (v2.6)

The full transition-video pipeline is operational and script-driven (terminal, no browser needed for routine runs).

**Two RunComfy deployments, chained by the script:**
- **Wan 2.2 FLF2V** (env `RUNCOMFY_DEPLOY_FLF2V`) — first-frame + last-frame → short motion clip. Node map: start=52, end=72, positive=6, negative=7, WanFLF2V=83 (width/height/length), KSampler=90 (seed/steps), VideoCombine=92. Deployed on 48GB tier. VALIDATED on day→dusk at 20 steps — geometry holds, drift absorbed into motion.
- **RIFE VFI** (env `RUNCOMFY_DEPLOY_RIFE`) — hand-built workflow: Load Video → Get Video Components → RIFE VFI (rife47.pth) → Video Combine. Node map: LoadVideo=10, RIFE=16 (multiplier), VideoCombine=19 (crf/format/frame_rate). Deployed on Medium (16GB) tier. Custom node packs installed via Manager: ComfyUI-Frame-Interpolation (RIFE) + ComfyUI-VideoHelperSuite (codec control). VALIDATED — clean interpolation, no added artifacts.

**Lossless intermediate fix (2026-07-05) — full story, three attempts:** the Wan deployment's Video Combine (node 92 in the FLF2V workflow) was saving the Wan→RIFE intermediate as `h264-mp4, crf 19, yuv420p` — lossy compression AND 4:2:0 chroma subsampling — so RIFE interpolated from already-degraded frames and the ProRes master inherited loss from two steps upstream.
1. **Tried FFV1 lossless** (`video/ffv1-mkv`) — FAILED: the Wan deployment's Video Combine format list doesn't include FFV1 (`value_not_in_list` error; available formats confirmed via the error payload: ProRes, h264/h265-mp4, av1/webm, png sequences, nvenc variants — no ffv1-mkv).
2. **Switched intermediate to ProRes** — Wan succeeded (37MB `_wan_raw.mov`), but RIFE then FAILED with `413 Request Entity Too Large`: the script base64-embeds the intermediate into the RIFE request body, and a 37MB file (~50MB base64) exceeded the request size limit.
3. **Solution — pass the Wan output by URL instead of embedding it.** Tested and confirmed: RIFE's LoadVideo node accepts a URL directly in its `file` field (`test_rife_url.py`, kept for reference). `run_wan` now returns the RunComfy result URL (no local download needed) with the intermediate set to full ProRes; `run_rife` passes that URL straight through — no size limit, no download/re-upload round trip. This is the final, working fix: the master path is now genuinely lossless end to end. `run_rife` also still accepts a local file path (base64) for the `--interp-only` mode.

**Length control:** `generate_transition.py --seconds N` picks BOTH the Wan frame count AND the RIFE multiplier so the result lands within ~0.1s of target at a locked 25fps cadence. Always maximizes real Wan frames first to minimize interpolation; warns when multiplier >8. Wan frame range 16–81.

**Quality presets (--quality):** master = ProRes (default, edit-ready, and now the Wan→RIFE intermediate too — see lossless intermediate fix above); preview = h264-mp4 crf 20; draft = h264-mp4 crf 28 + low Wan steps; lossless = ffv1-mkv (NOTE: FFV1 confirmed unavailable on the Wan deployment specifically — this preset still works for the RIFE/final-output stage, just not as the Wan intermediate). Raw overrides: --crf, --format, --multiplier, --steps, --seed. Also `--interp-only FILE` for standalone RIFE on any clip.

**Final format chain confirmed:** plates PNG 1920×1080 → Wan MP4 720p → RIFE → ProRes master (the project's stated transcode target) → VHS-on-CRT exhibition. 720p is deliberate: VHS resolves ~480 lines, so higher res is wasted; ProRes keepers, h264 previews.

**LTX-2.3 flagged for later:** native long-clip (up to 20s, 25fps, FLF, Apache 2.0) — designated test candidate for the motion-heavy beats (eruption, animals) where RIFE can't invent motion. NOT needed for slow lighting transitions (Wan+RIFE covers those).

**Codec menu available in Video Combine** (for reference): ProRes, ffv1-mkv (lossless), 16/8bit-png (frame sequences), h264-mp4, h265-mp4, nvenc variants, av1/webm, gif/webp.

## Celestial Bodies — Out of Frame (LOCKED, v2.4)

**Rule: the sun and the moon are never visible in frame. We see only their light — edge glow, directional shadow, and ambient illumination — never the discs themselves.**

**Justification (geometric, not a cheat):** the camera is a fixed, low, plant's-eye view facing the volcano. The sun rises in the east (frame LEFT → dawn), climbs steeply overhead toward midday (above and BEHIND the viewpoint), and sets in the west (frame RIGHT → dusk). The moon tracks the same arc. Their discs pass over the top and off the sides of a frame that looks at the volcano — they never cross the field of view. This is exactly consistent with the light directions already baked into the plates (dusk glow right, dawn light left).

**Consequences:**
- Unifies all four lighting states under one rule: glow + directional light + ambient, no disc — already how dusk and dawn behave; now extended to night (empty sky, moonlit land).
- Eliminates baked-moon balancing, composited-moon generation/animation, sun/moon disc-position continuity, and moonrise animation. Earlier plans to either bake or composite the moon are SUPERSEDED.
- Concept: reinforces the plant's rooted, limited perspective — it feels light arrive and leave from sources beyond its view — and keeps the volcano the sole object on the skyline. The forces acting on the plant stay off-screen and indifferent: the protection gap, made visual.
- B004 "a bright moon rises" is rendered as moonlight flooding in during the dusk→night FLF2V transition — implied by the changing light, not a shown disc.

**Sky-layer scope (updated):** the composited sky layer carries only the gradient (inherited from each relit plate), clouds, volcanic smoke/ash, and optional stars. No sun or moon disc is ever generated or composited.

## Act 1 Plate Manifest & Generation Tracker

**ACT 1 LIGHTING SET COMPLETE (2026-06-16):** all four time-of-day states locked — day v018/1781266837, dusk v001/1781586599, night v008/1781714035, dawn v002/1781715506. The lighting spine of Act 1 is reproducible and done. Remaining Act 1 work is the structural branch (terraced → volcanic → charred). **Terraced mask is now PAINTED (2026-06-18) — the structural branch is UNBLOCKED and terraced is the next plate to generate.**

Live generation status is written per-plate into the beat JSON (`generation_status`, `version_log`, `last_seed`). This manifest is the plan and dependency map. Variance principle: each lighting state is used for a specific narrative purpose, NOT looped — so one version per state suffices except where flagged.

| Plate | State | Used in beats | Derives from | Mask? | Versions needed | Status |
|---|---|---|---|---|---|---|
| A1_plate_pristine_day | midday | B001, B002 | text-to-image | — | 1 (LOCKED v018) | ✅ locked |
| A1_plate_pristine_dusk | warm afternoon/golden (light from right) | B003 | pristine_day | no | 1 | ✅ LOCKED v001 · seed 1781586599 |
| A1_plate_pristine_night | cool night, empty sky | B004–B007 (one held night) | pristine_day | no | 1 | ✅ LOCKED v008 · seed 1781714035 |
| A1_plate_pristine_dawn | first light (light from left) | B008 | pristine_day | no | 1 | ✅ LOCKED v002 · seed 1781715506 |
| A1_plate_terraced | terraced day | B009 | pristine_day | YES ✅ mask painted | 1 | ▶ READY TO GENERATE |
| A1_plate_terraced_volcanic_grey | ash daylight | B010 | terraced | relight (no mask) | 1 | blocked: terraced |
| A1_plate_terraced_volcanic_orange | eruption glow | B011 | terraced | relight (no mask) | 1 | blocked: terraced |
| A1_plate_charred | aftermath | B012 | terraced | YES (structural) | 1 | blocked: terraced |

**Conditional (assess only after terraced is locked):** B009's rapid day/night time-lapse may want 2–3 terraced-lighting variants (e.g. terraced_dusk/night) for cycling. Decision deferred — variance there is expected to come mainly from the composited sky layer + FLF2V seed variation, so extra plates may not be needed. Do not pre-generate.

**Variant naming convention (only where the manifest flags >1 version):** `A1_plate_{state}_{NN}` — e.g. `A1_plate_terraced_night_02`. Single-version states keep their plain name.

**▶ SOON / NEXT ACTIONS (updated 2026-06-19):**
1. **Lock the terraced plate** — regenerated with raised foreground soil band (v0.45 instruction) to match the low ground-level camera of the locked day plate; terracing now edge-to-edge + distant valley. Assess latest render; lock when camera height matches. Unblocks volcanic_grey, volcanic_orange, charred.
2. ✅ DONE — `--seconds` planner now defaults to 81 Wan frames + RIFE multiplier rounded UP (never undershoots, keeps all frames, prints overage for editor to trim). Also added `--wan-frames` override.
3. **Begin plant work — B002 hero growth shot first** (bare soil → mature plant via FLF2V). Establishes plant identity for all later beats. See Plant Workflow Architecture section.
4. **Parked: foreground DoF.** Locked plates have soft foreground; can't fix by seed-locked regen (seed doesn't pin composition — proven) nor by sharpening soft pixels. Decision deferred until the plant exists and DoF can be judged in the actual composite (sharp plant may make plate-foreground softness moot).
3. **Generate the other 3 transitions** (dusk→night, night→dawn, dawn→day) — apply the same explicit-direction prompt discipline; lock seeds; render masters. Then assess the full day→dusk→night→dawn→day loop as a seamless CRT cycle.
4. **Generate the terraced plate** (parallel track, mask painted, READY) — wire `mask_path: masks/A1_mask_terraced_v01.png` into the terraced plate, run via unified edit deployment, judge contours-vs-depth, lock. Unblocks volcanic_grey, volcanic_orange, charred.
5. **Plant layer** — generate the potato plant as its own element, segment (BiRefNet/RMBG), relight per state (IC-Light), composite at anchor [0.5,0.78].

**⚠ Session-end reminder:** drop Wan deployment keep-warm back to 60s (A100 @ $3.99/hr should not sit warm idle).

**🧹 HOUSEKEEPING TO-DO (low priority, do deliberately — not mid-render):**
- Rename `skills/generate-plate/` → `skills/generate/` (now holds both generate_plate.py AND generate_transition.py; "generate-plate" name too narrow). Commands change to `skills/generate/tools/...`. Verify scripts' PROJECT_ROOT path still resolves (same folder depth, should be fine) and update any SKILL/DESCRIPTION/INSTRUCTIONS .md referencing old name.
- Delete `skills/read-beat/` — never used as intended; currently contains only a stray duplicate of generate_plate.py. Dead scaffolding.

## 5. Beat JSON Changelog

### v0.1 — 2026-05-19
- Initial schema created
- Global project parameters, codec strategy, global visual rules
- Plate registry
- Full beat list Acts 1–3 with: timing, plant_state, human_presence, animal_presence, environment_state, event_state, camera_state, spatial_layers, generation_plan, composition_strategy, layers

**VERSIONING RULE (always, no exceptions):** Never overwrite a file in place. Every change to the beat JSON or project doc gets a NEW version number — even a tiny edit bumps a sub-decimal (e.g. v0_83 → v0_83_1) or the next integer. Sam prefers keeping every version on disk over overwriting. This applies going forward to all project files.

### v3.1 — session 2026-06-26
**B-set pristine day plate — long iteration, key learnings:**

- **Working anchor: A1_plate_B3_pristine_day** — Sam's hand-edited prompt (from v0.61 base, DoF changed to "moderate-to-deep", dropping heavy background blur). Liked result: v015, seed 1782403143. Foreground diagonal pinned: higher right, drops noticeably lower left.
- **DoF decision: do NOT bake DoF into plates.** Apply depth-map-driven DoF in After Effects instead — non-destructive, fully controllable, adjustable per shot. Keep all plates as sharp as possible. This applies to ALL plates (A-set and B-set).
- **The relight-sharpen-relight trick** (relighting a plate bakes in sharpness as a side effect, then relighting back to neutral): tried with B-dusk v002 and v003 as sources. Interesting concept but resolution/quality not convincing enough. Abandoned.
- **Mask editing v011 to remove terraces (B2):** produced clean bare slopes but foreground "closeness" was permanently fixed to v011's camera height — couldn't be made closer. Abandoned for B-pristine use.
- **Soft volcano problem:** soft DoF in v010 didn't survive relights — the relight model sharpens the background as a side effect, creating mismatch. Decision: keep plates sharp (distance via haze, not blur), let DoF be applied in post from depth map.
- **Foreground "field" problem:** when the protected foreground includes the stone retaining wall area, the result reads as an agricultural field floor, not a natural elevated soil patch. The wall is the key culprit — it must always be in the editable (white) mask region.
- **Seed vs prompt changes:** changing ANY wording in a t2i prompt changes the full composition — the seed does NOT pin composition across different prompts. Only the exact same prompt + seed reproduces the exact same image.
- **Comparative language in prompts is ineffective** ("larger", "further", "more") — the model has no prior state to compare against. Always use absolute terms ("lower third of the frame", "upper third", "50 percent").
- **Horizon position** is a useful lever for foreground size: "horizon in the upper third" implicitly expands the foreground below it, since it forces the camera to look more across the ground.
- **B-set candidate tracker (all on disk):**
  - B (original): locked v010, seed 1782322540, soft volcano — fallback
  - B2: masked de-terrace of v011
  - B3: Sam's hand-edited prompt, working anchor, liked v015 seed 1782403143
  - B4: relight dusk v003 → back to midday (abandoned)
  - B5: relight dusk v002 → back to midday (abandoned)

**Sun position — Act 1 locked convention (NEVER change):**
Camera faces roughly northeast down the valley toward the volcano.
Sun travels LEFT → RIGHT across the frame (east to west) — consistent for timelapse acceleration.

| State | Sun position | Shadow direction |
|-------|-------------|-----------------|
| Dawn | Low camera-LEFT (east) | Shadows fall RIGHT |
| Day | High overhead, slight camera-right bias | Near-neutral |
| Dusk | Low camera-RIGHT (west) | Shadows fall LEFT |
| Night | No directional sun | — |

This convention applies to ALL derived plates: terraced, charred, volcanic, B-set, A-set. Never reverse it.
Sun is always ON CAMERA (visible side faces camera) — never backlit.

**version_log (generate_plate.py v6.2):** every generation now records {version, seed, quality, date} into the plate's `version_log` in the JSON. This recovered terraced v007's seed (1782708061) after a timeout blip hid it from the terminal — the seed was safe in the log. To read any plate's history: `python3 -c "import json,glob,re; f=max(glob.glob('AomE_beats_v0_*.json'),key=lambda p:[int(x) for x in re.findall(r'\d+',p)]); d=json.load(open(f)); [print(e) for e in d['plates']['PLATE_ID'].get('version_log',[])]"`

**B3-set locked plates (Act 1):**
- B3 pristine day: v003, seed 1782480124 (anchor)
- B3 terraced: v007, seed 1782708061 (foreground protected, slopes terraced + large close wall)
- B3 dusk / night / dawn: locking from batch results (sun convention: dusk-right, dawn-left)
- B3 charred: next — derives from locked terraced v007

**Batch generation (generate_plate.py v6.2):**
`--batch N` flag runs N generations back-to-back with fresh seeds, no prompts between them, versioned files saved after each. Use for seed-hunting on lighting plates (dusk/dawn sun direction, snow retention etc.) without manual re-running. Example: `python3 skills/generate-plate/tools/generate_plate.py A1_plate_B3_pristine_dusk --batch 5`. Also added: network-retry in the poll loop (prints `x` on a blip, keeps going instead of crashing) — matching the robustness already in generate_transition.py.

**Depth map generation (pending — ComfyUI):**
Generate a per-plate depth map in ComfyUI (e.g. via MiDaS or ZoeDepth node) aligned pixel-perfect to each locked plate. Use the depth map in After Effects to drive lens blur/DoF — non-destructive, fully adjustable per beat. This replaces any need to bake DoF into generated plates. TO-DO: build a ComfyUI depth-map workflow and add a RunComfy deployment for it. All plates should be kept sharp; DoF applied entirely in post from the depth map.

**Next steps:**
1. Generate B3 with strengthened diagonal, lock on next good seed
2. Build ComfyUI depth-map workflow (MiDaS/ZoeDepth) + RunComfy deployment for it
2. Generate depth map for B-pristine-day (for After Effects DoF)
3. Generate depth maps for all locked plates
4. Derive B-dusk, B-night, B-dawn, B-terraced from locked B3
4. Begin plate-to-plate video generation (Wan FLF2V transitions)

### v3.9 — session 2026-07-07 (audio engine swap, ControlNet progress, VHS specs, demo plan)
- **Audio engine fully swapped MMAudio -> ElevenLabs.** MMAudio (video-to-audio) is retired (backup kept as `generate_audio_mmaudio_backup.py`); the old approach gave weak results and hit 413 limits on master files. New `generate_audio.py` is a unified ElevenLabs text-to-audio tool with four modes: **sfx** (`/v1/sound-generation`), **ambience** (same endpoint + loop, fixed 25s bed), **music** (`/v1/music`), **voice** (`/v1/text-to-speech`). Versioned per mode in `audio/{mode}/`, sidecar JSON, completion chime, batch, peak-normalize to -6dB (`--target-db`), `--from-transition`/`--from-sfx` pull prompts from the beat JSON, files named by transition/sfx ID.
  - **Music generation: SUCCESS.** 3-min abstract Andean valley score generated cleanly.
  - **SFX / sound design: SUCCESS.** Swooshes (single, accelerating, 25s accelerating sequence) all clean; stored in beat JSON `sfx` section (`swoosh_accel`, `swoosh_large`) and pullable via `--from-sfx`.
  - **Ambience: partial.** Works, but needed prompt-robustness fixes — prompts describing SILENCE/absence ("still cold air," "fading to silence") corrupted the generation; rewriting all four transition ambiences as ACTIVE continuous atmospheres (steady wind + concrete elements: crickets at night, birdsong by day) fixed it. Capped ambience at fixed 25s (detached from transition length; 30s cap was corrupting). Still "work a bit more later" but acceptable for now.
  - Tier note: ElevenLabs sound-generation endpoint caps at 128kbps MP3 regardless of tier (fine for diffuse ambience/sfx); music/voice honour higher quality on Creator tier. WAV/pcm_44100 needs Pro tier.
- **Depth-as-ReferenceLatent: DOCUMENTED FAILURE.** Flux.2 ReferenceLatent conditions on APPEARANCE, not spatial structure — feeding a depth map as a second reference had no effect on preserving slope contour during terracing. Negative result, documented (`DEPTH_WORKFLOW_HANDOFF.md`).
- **Moved to real ControlNet** (`FLUX.2-dev-Fun-Controlnet-Union`, 7.7GB, `comfyui-flux2fun-controlnet` node). Graph wired on a copy (`A1_edit_flux2_controlnet_v1/v2`): depth map -> control_image, mask -> ControlNet mask, chained through ReferenceLatent -> Basic Guider. Requires 24G+ GPU (confirmed RTX A6000 48GB), Turbo LoRA OFF (full 20 steps). CURRENT BLOCKER: `AttributeError: multigpu_clones` — ComfyUI core v0.25.1 added multi-GPU support the v1.1.0 node predates; patch attempted, node pack currently showing broken; next step is View Log for the import traceback. See `CONTROLNET_WORKFLOW_HANDOFF.md`. This is the path to geometry-preserving terraced/charred plates.
- **VHS export spec locked (PAL 4:3):** 720×576, 25fps, DAR 4:3, PAR 1.0940 (D1/DV PAL 4:3, Premiere's value) for the hardware/VHS-transfer chain; square-pixel equivalent is 768×576 @ PAR 1.0. Master at 720×576/PAR 1.0940 and let the VHS deck impose analog character.
- **Exhibition demo:** for the July deadline, exhibiting an edited DEMO VIDEO (showcasing the engine — generate_plate, generate_transition, generate_audio) exported to VHS, NOT the full act. Printed screenplay on the table beside it. Presentable/printable deliverables set: Screenplay, Project Document, Paper, Skills Manual, Beat JSON (not the Python source).
### v3.8 — session 2026-07-05 (audio robustness + editing features)
- **Master-file versioning bug FIXED (Sam caught it)**: `next_version` only scanned `.mp4`, so ProRes `.mov` masters never saw each other and every render silently overwrote `_v001.mov`. Now scans all video extensions (mp4/mov/mkv/webm). Sam identified the overwrite behaviour as a catastrophic design flaw.
- **generate_audio.py auto-proxy for large files**: master `.mov` files hit MMAudio's 413 request-size limit (base64 embed). Since MMAudio only needs MOTION to generate sound, the script now auto-makes a small 512px ffmpeg proxy for anything over 8MB, generates from that, deletes it — identical audio, master untouched.
- **Audio format choice**: `--audio-format flac|wav` (both lossless, 44.1kHz from mmaudio_large_44k_v2). flac default.
- **Mirrored audio handles (Sam's idea)**: `--handles N` produces an extra audio file with N seconds of MIRRORED ambient added each end, so sound at each cut point matches perfectly for seamless crossfades when assembling the exhibition loop. Sam requested this specifically for seamless audio transitions between day-cycle clips. Audio-only — meant to bleed under the adjacent clip's picture during a crossfade.

### v3.7 — session 2026-07-05 (URL hand-off quality fix)
- Corrected the lossless-intermediate record to the real final fix: FFV1 rejected by Wan deployment → ProRes hit RIFE's 413 → solved by passing the Wan output BY URL to RIFE (confirmed LoadVideo accepts URLs). Master path now genuinely lossless Wan→RIFE.

### v3.6 — session 2026-07-05 (codec/quality fixes)
- **Lossless Wan→RIFE intermediate** (three-attempt fix, see 4b for full story): discovered the Wan intermediate was h264/crf19/yuv420p, degrading every master. FFV1 unavailable on the Wan deployment → ProRes worked but hit RIFE's 413 request-size limit → fixed properly by passing the Wan output BY URL instead of base64-embedding it (confirmed RIFE's LoadVideo accepts URLs). Master path is now genuinely lossless Wan→RIFE.
- **Confirmed ProRes master is genuine**: verified via ffprobe that master output is real ProRes (Lavc prores), not silently-fallback h264 — the earlier `avc1` scare was a specific file, not a systemic bug.
- **Per-video sidecar JSON + `--read-settings`** added to transitions (seed, prompts, deployment IDs, all settings) — mirrors the plate sidecar system.
- **Plate sidecar enriched**: now also records base_plate_file, mask_file, deployment_id.
- **Audible completion chime** (`afplay`, macOS) on render finish/failure, `--quiet-sound` to disable — Sam's idea, to keep the GPU warm between jobs.
- **Transition prompt tuning + revert**: shadow-physics/golden edits caused a seam between cycle clips; reverted dusk→night and night→dawn to original wording, kept only the day→dusk oversaturation fix. Baseline pre-edit JSON = v1_12; current = v1_15.
- **Depth-conditioning exploration** (parked, in progress in a separate chat): building a depth-map + reference-latent variant of the edit workflow to preserve slope geometry during terracing. See `DEPTH_WORKFLOW_HANDOFF.md`. Depth map via kijai DepthAnythingV2 (vitl); native Flux.2 chained-ReferenceLatent approach (not the unstable Fun-ControlNet). Manual UI wiring proved painful without screen access — next step is to finish wiring + export workflow_api.json, then script a `--depth` flag.
- **generate_audio.py --mux + beat-JSON integration + logging**; MMAudio validated end-to-end.
- Mask technique refined: precise selection cut, THEN soft brush painted inward into the protected side only (avoids both hard-edge seam and bleed-into-editable).

### v3.2 — session 2026-07-03
- **B3 dawn LOCKED** (v024, seed 1782735541) — clean stable relight after resetting an over-loaded instruction that was destabilizing the volcano; light direction accepted as-landed (deferred to IC-Light).
- **B3 dusk LOCKED** (upgraded to a batch-generated file with embedded seed, replacing the original pre-metadata v002).
- **Terraced rebuild restarted as sequential multi-mask** (`A1_plate_B3_terraced_v2`): single large masked edits kept causing drift (volcano, wall, slopes) even on a second full attempt. New method — small sequential passes (left slope → right slope → wall), each locked before the next. Pass 1 in progress; found and fixed a mask-edge seam issue (feather/hard-edge tradeoff at the ridgeline; solution: hard-edge cut via Photoshop selection + fill, undershoot rather than overshoot the boundary).
- **First B3 video transition VALIDATED end-to-end**: `T_day_to_dusk` (Wan 81 frames + RIFE ×4) — light shifts cleanly, terrain holds. Caught and fixed a filename bug (doubled version suffix from a locking mistake) that crashed `generate_transition.py`.
- **Foreground wind/motion experiments**: multiple attempts to animate foreground grass in Wan FLF2V transitions, including a deep research pass on Wan prompting (motion-first ordering, chained verbs, negative prompts). Conclusion: FLF2V will not animate near-identical foreground regions between two endpoint frames — terrain stays stable but grass shows zero motion regardless of wording. PARKED; recommended fix is After Effects displacement on a masked foreground layer.
- **generate_audio.py built and VALIDATED end-to-end** — first successful MMAudio ambient-sound generation, on `T_day_to_dusk_v003.mp4`. Homebrew + ffmpeg installed as prerequisites. Upgraded same session: optional `--mux` (audio-only remains default), beat-JSON `audio_prompt`/`audio_negative` integration, seed/steps/cfg logging to sidecar JSON + `audio_log`.
- **5-day timelapse cycle planned and scaffolded**: exhibition loop will show 5 day/night cycles, not 1. Decision: do NOT regenerate full landscapes 5×es (breaks pixel-lock). Current locked plates become Day 1 anchors; Days 2–5 are same-prompt/fresh-seed siblings, all lighting states relighting from the single locked Day-1 base to guarantee zero drift across all 20 plates.
- **generate_plate.py**: added `--read-seed` command to recover a seed from any PNG's embedded metadata.
- **Mentor report built**: `AomE_Mentor_Report.docx`, 4 pages (reflective essay + appendix: skills/models list, exhibition deliverables, open technical hurdles).
- **Full document reconciliation** (this entry): corrected a stale header (date/version mismatch), flagged Sections 1–4b as superseded (original ComfyUI Cloud/Kontext plan), rewrote Section 6.1 to match the actual current model stack, replaced Section 8's open-questions list with current accurate status.

### v3.0 — session 2026-06-24 (later)
- **B-SET DAY PLATE LOCKED:** A1_plate_B_pristine_day, seed 1782322540, file A1_andean_B_pristine_day_v010.png. Fresh text-to-image from the v018 prompt with camera lowered, soil receding into depth, foreground ~lower 40-45%, strengthened DoF falloff. This is the official B-set pristine-day anchor — all other B-set plates derive from it. NEVER regenerate/overwrite.
- **TWO-SET STRATEGY CONFIRMED (deliberate, not temporary):** Keep BOTH the A-set (locked, original camera height) AND the B-set (lower camera, more cinematic DoF). Rationale (Sam): having two complete plate sets is insurance — if one set hits a roadblock during video generation (plate-to-plate Wan transitions), the other is a ready fallback. Do NOT discard the A-set when the B-set is complete.
- **Next steps (agreed):** (1) Generate the full B-set for Act 1 — derive B-dusk, B-night, B-dawn from B-day (relight edits), then B-terraced (masked edit), then B-charred, plus the volcanic states. (2) Once B-set plates exist, begin plate-to-plate video generation (Wan FLF2V transitions between plate states), following the validated Wan→RIFE pipeline.

### v2.9 — session 2026-06-24
- B-set plate strategy decided: fresh text-to-image (not mask-editing from v011). Mask approach abandoned after repeated failures to reliably reconstruct foreground. A-set stays locked as fallback.
- B-set goals: lower camera to ground, more layered DoF, narrower frame (humans/animals partial figures only). Visual targets: AomE_ReferenceContext_Act01.png + terraced v011 (seed 1782221056).
- Terraced plate iteration: v011 (seed 1782221056) confirmed as the best terraced result — good foreground depth, cinematic, correct slope/volcano. Not yet locked (B-set exploration ongoing).
- Critical file-safety lesson: the unversioned base file (e.g. A1_andean_pristine_day.png) gets overwritten by every new generation — the DoF experiment clobbered the A-set base mid-session. Fix: always cp locked versioned file → unversioned base before any edit run. This is a script bug to fix (should not auto-overwrite unversioned unless explicitly locked).
- Opus-switching rule clarified: signal "switch to Opus" for B-set prompt crafting, new plate prompts from scratch, major architectural decisions, plant generation prompts.

### v2.8 — session 2026-06-22
- READ THE SCREENPLAY (AotE_V01_20260515 — note: file is a .pdf-named ZIP bundle of 12 beat text+image files; must unzip, not pdf-parse). Encoded the plant's full arc into the beat JSON: plant_state (already present, accurate) + new plant_production specs per Act 1 beat (v0.47).
- Plant architecture defined: generated-video protagonist (9/12 beats motion via Wan FLF2V), not still layers. Three new assets identified: underground tuber layer (B006/B008), charred plant (B011), rebirth seedling (B012). Multi-layer choreography with bee/llama/puma/woman partial figures.
- Terraced plate: closed the un-terraced-gap problem via explicit edge-to-edge + distant-valley instruction; then caught a camera-height drift (foreground soil band too low/thin vs locked plates) — fixed with explicit foreground-soil-band instruction (v0.45). Confirmed: big structural edits drift the camera; seed does NOT pin composition (proven twice — DoF trial returned a totally new image at the locked seed).
- DoF correction attempted and PARKED: cannot regenerate a locked plate with only-DoF-changed (seed doesn't lock composition), cannot sharpen genuinely-soft pixels. Deferred until plant compositing reveals whether it matters.
- Transition planner improved: default 81 Wan frames + multiplier rounded up, all frames kept, prints overage (editor trims). Network-blip retry confirmed working (recovered a render after wifi drop via /result curl).
- Revised the 3 remaining transition prompts (dusk→night, night→dawn, dawn→day) with explicit light direction + foreground breeze (v0.46), pre-empting the wrong-shadow-direction problem.
- Beat JSON v0.47 (plant_production specs). Housekeeping: skills folder rename (generate-plate→generate) + delete dead read-beat still pending.

### v2.7 — session 2026-06-19
- Wan frame ceiling diagnosed: A6000 fails above ~25 frames (VRAM offload → degraded "gray" output, 102s/step). Moved Wan deployment to A100 (80GB) → renders full 81 frames cleanly. 81 = no-compromise ceiling (model training max).
- Keeper recipe validated end-to-end: 81 Wan frames → RIFE ×4 → ~13s @25fps, clean.
- RIFE chain confirmed working in production script (Wan→RIFE→ProRes) at both 25-frame and 81-frame bases.
- Script robustness: network-blip retry in wait() (dropped poll no longer kills a render); added --wan-frames override; quality presets draft/preview/master confirmed.
- Cost model understood: A100 keep-warm bills full rate during warm window; discipline = 600s batching / 60s idle, draft-iterate + master-once, lock seeds.
- Prompt finding: motion DIRECTION must be explicit (shadows were crawling wrong way = sunrise on a dusk shot). v0.41 fixes T_day_to_dusk: sun setting low-right, shadows climb up, + faint breeze in foreground grass.
- Beat JSON v0.41 (T_day_to_dusk motion prompt revised). Terraced mask painted (structural branch ready).

### v2.6 — session 2026-06-18
- Video pipeline BUILT & VALIDATED end-to-end: Wan 2.2 FLF2V + RIFE VFI, two RunComfy deployments chained by generate_transition.py
- RIFE workflow hand-built on canvas (Load Video → Get Video Components → RIFE VFI rife47 → Video Combine); installed ComfyUI-Frame-Interpolation + VideoHelperSuite via Manager; deployed on Medium tier
- generate_transition.py v2: --seconds length control (picks Wan frames + RIFE multiplier together, ~0.1s accuracy at locked 25fps), quality presets (master=ProRes / preview / draft / lossless), raw overrides, --interp-only mode
- Beat JSON v0.40: added 'transitions' section (4 cycle transitions, locked plates as boundary frames)
- Terraced mask PAINTED — structural branch unblocked, terraced plate ready to generate
- Confirmed format chain: PNG 1080p plates → Wan 720p → RIFE → ProRes master → VHS; 720p deliberate (VHS resolves ~480 lines)
- LTX-2.3 noted as later candidate for motion-heavy beats (eruption, animals)
- Fixed: stale plate_resolution reference context; flag-parsing in transition script

### v2.5 — session 2026-06-16 (later)
- **MILESTONE: Act 1 lighting set fully LOCKED** — day (v018/1781266837), dusk (v001/1781586599), night (v008/1781714035), dawn (v002/1781715506). All four time-of-day corners reproducible from the locked pristine base via the unified edit deployment.
- Night solved after extended iteration. Key findings (paper-worthy): (1) diffusion negation summons — naming "moon"/"sun"/"star" even to forbid them caused the model to render them; removing the words entirely produced the empty sky. (2) Lighting *relationships* ("darker earth beneath a lighter sky") work where absolute brightness targets fail. (3) A horizon-glow instruction reads as twilight afterglow; an even sky tone reads as true night.
- Beat JSON v0.39: lighting locks written with reproduction notes; manifest statuses updated
- Sun/moon: confirmed handled by the no-celestial-bodies-in-frame principle (light quality only)
- Next: terraced mask (office) → terraced plate; Wan 2.2 FLF2V deployment (parallel) → first day→dusk transition video

### v2.4 — session 2026-06-16 (later)
- Celestial bodies LOCKED out of frame: sun and moon never visible; only their light (glow, directional shadow, ambient). Geometric justification via the fixed plant's-eye camera facing the volcano (sunrise east=left/dawn, sunset west=right/dusk, midday overhead-behind)
- SUPERSEDES both the "bake the moon" and "composite the moon" options — neither needed; night = moonlit land under an empty sky
- Night plate instruction finalized: empty dark-blue sky, even moonlight across the whole scene (volcano snow softly lit, not blown out), land readable not crushed to black
- Sky-layer scope clarified: gradient + clouds + smoke + optional stars only; no sun/moon disc
- B004 moonrise reinterpreted as moonlight arriving during the dusk→night transition

### v2.3 — session 2026-06-16
- Video model LOCKED: Wan 2.2 (Apache 2.0, on RunComfy)
- Transition method LOCKED: Wan 2.2 FLF2V (first-last-frame) — relit plates are boundary frames; absorbs inter-plate drift; chained shared boundaries give a seamless day→dusk→night→dawn→day loop (the CRT loop)
- Lower-denoise relighting downgraded to fallback (not needed; video stage handles continuity)
- Dusk relight validated on Full — geometry held, directional light + cast shadow achieved; Path A (image-edit relight) confirmed, no depth needed for lighting
- Night + dawn relight instructions refined (sun arc: dusk=right, dawn=left)
- Lighting variance assessment from beats: Act 1 is one day→night→dawn arc told once; each state used purposefully, not looped. ~8 core plates needed, not a library. Only B009 time-lapse may want cycling variants (deferred)
- Act 1 Plate Manifest & Generation Tracker added
- Unified edit workflow deployed on RunComfy; generate_plate.py v6.1 (node IDs aligned to deployed workflow_api.json, real error surfacing)

### v2.2 — session 2026-06-12
- **MILESTONE: Act 1 pristine base LOCKED** (A1_plate_pristine_day v018, seed 1781266837, Full, RunComfy)
  after 18 iterations; clear-sky, shrunk distant volcano center-right, layered ridges, angled foreground edge
- Beat JSON v0.29: lock recorded (locked: true, locked_version: 18, reproduction note), stale Flux.1/Nano
  Banana model references cleaned, user version_log history preserved via upload-merge
- RT-03 implemented as `flux2_masked_edit.json` (workflows/): masked inpaint from encoded base +
  pixel-exact composite-back; zero custom nodes in v1; depth control deferred to v2 escalation
- Empty-latent root cause of edit drift identified and documented
- Mask workflow defined: Photoshop-painted per-base production asset (white = editable, soft edges)
- RunComfy deployment settings standard recorded (24G, min 0 / max 1 / queue 1, keep-warm 180–300s bursts)
- Next: paint terraced mask → interactive validation → deploy → masked_edit mode in generate_plate.py

### v2.1 — session 2026-06-11
- Sky decision: base plates generated with CLEAR cloudless sky; sky/clouds become a separate composited layer for full per-beat control (consistent with smoke and plant layering)
- A1 pristine prompt updated to cloudless sky (ridge aerial haze kept for depth)
- RT-03 added: Location-Invariant Structural Edit (depth + inpaint) — formalized
- RT-04 added: Dynamic Atmosphere as Composited Layer — sky, smoke, and pyroclastic cloud workflow; depth map as shared infrastructure for both structural edits and video placement
- VIDEO / MOTION section of the catalogue opened with RT-04

### v2.0 — session 2026-06-10 (later)
- PLATFORM LOCKED: RunComfy (single platform), replacing the ComfyUI-Cloud / hybrid plan — RunComfy is a true superset (Flux.2 + ControlNet + depth + inpaint)
- ETHICAL CONSTRAINT LOCKED: Tier 1, open-weights models only, no closed proprietary APIs
- Final model stack locked (see Platform & Model Stack section)
- Relighting upgraded IC-Light V1 → V2 (now permissible, non-commercial)
- Qwen-Image-Edit-2511 (Apache) added as structural-edit alternative to test vs Flux.2 edit
- Two ethics footnotes recorded for the paper (non-commercial weights; training-data provenance)
- Next: RunComfy account setup, then clean pipeline rebuild (API, workflows, depth+inpaint, runner, JSON routing)

### v1.9 — session 2026-06-10
- Added Location Invariance core principle: each act has ONE fresh base; all other states are image-edits from it
- Confirmed mandatory for all three acts (Andean valley, Alpine valley, Mars chamber + window landscape)
- A1_plate_terraced switched from fresh base → image edit derived from locked A1_plate_pristine_day
- Only three fresh generations for the whole film; 14 plates are edits
- Derivation chains lock stepwise (pristine → terraced → volcanic/charred)

### v1.8 — session 2026-06-09 (later)
- RT-01 expanded with four reusable prompt-craft findings from locking the Act 1 pristine base (v007):
  volcano summit silhouette language, distance calibration, gentle DoF falloff, --reuse-seed for composition tuning
- Act 1 pristine base (A1_plate_pristine_day) LOCKED at v007, Full quality — first locked base of the film
- These phrasings to be reused for consistency across the remaining three bases

### v1.7 — session 2026-06-09
- Added Refinement Techniques Catalogue section (living document, grows with production)
- RT-01 (Prompt Refinement + Seed Reuse): first entry, documented from Act 1 volcano summit adjustment
- RT-02 (Flux.2 Image Edit / Surgical): second entry, documented as planned fallback for locked compositions
- Video/motion techniques section stubbed, to be filled during video phase

### v1.6 — session 2026-06-08
- KEY CHANGE: base references now generated fresh via Flux text-to-image, not edited from ChatGPT images
- Reason: Kontext (editing model) preserves source artifacts on low-change plates; fresh generation removes them at root
- Four fresh base references defined (Act1 pristine, Act1 terraced, Act2, Act3); 13 variants derive via Kontext from locked bases
- Generation prompts authored and embedded directly in Beat JSON generation_prompt fields (no copy-paste)
- Native 16:9 generation (1920×1088 → 1080) also resolves the Kontext stitch/scaling artifact
- generate_plate.py v3: two modes (text_to_image + kontext), base-by-plate-id resolution, output versioning (_vNNN + stable)
- Stays on ComfyUI Cloud; RunComfy + ControlNet-depth remains documented fallback if composition control proves insufficient
- Base generation uses Flux.1 Dev now; optional Flux.2 upgrade if its t2i template is available

### v1.5 — session 2026-06-06 (later)
- Production scope formalised into two milestones:
  - July 10 exhibition: Act 1 complete and polished (firm deliverable)
  - August 28 poster + graduation: full film, all three acts
- Act 1 confirmed as complete standalone narrative expressing the full protection-gap theme
- Acts 2-3 are extensions, not separate builds — pipeline and architecture carry over directly
- Rationale: quality over runtime, de-risk July deadline, prove full pipeline on one act
- Action: confirm scope with mentor (Mykhailo) at next check-in

### v1.4 — session 2026-06-06
- Decision: commit to ComfyUI Cloud first, with documented pivot triggers to RunComfy
- Added Platform Strategy & Pivot Plan section
- Confirmed commercial-use position on ComfyUI Cloud (platform clears all hosted models; verification recommended for commercial release)
- Kontext pipeline working end to end: upload + generate + download proven
- generate_plate.py v2: image upload, Kontext workflow, auto-crop stitch, auto-resize to 1920×1080
- All 17 plates given Kontext instructions (preserve composition + change instruction) and base_reference fields
- Pivot trigger established: switch to RunComfy when quality/creative wall OR technical wall is hit, on Claude's explicit recommendation

### v1.3 — session 2026-06-04
- FLUX.1 Kontext Dev confirmed available on ComfyUI Cloud
- Kontext adopted as primary plate generation model — replaces text-to-image Flux.1 Dev for plates
- ControlNet: confirmed not on ComfyUI Cloud (commercial-cleared policy confirmed via official docs)
- img2img: evaluated and superseded by Kontext
- Flux.1 Dev retained for layer generation (non-plate elements)
- Model quality assessment: Flux matches and exceeds ChatGPT image generation for landscapes
- Kontext license noted: Dev = Non-Commercial per BFL, but ComfyUI Cloud commercially clears all hosted models
- Act 2 + Act 3 reference images: pending
- Kontext workflow to build next session
- Added two paper discoveries: ControlNet unavailability as finding; Kontext for film pipelines

### v1.2 — session 2026-06-03 (later)
- Built /read-beat skill — reads any beat's parameters from the JSON (tested, working)
- Cleaned runner_test.py to production version (removed debug output)
- Added generation prompts + negative prompts to all plates
- Established plate philosophy: plates are clean single-state; moving/changing elements are layers
- Smoke plume confirmed as a layer, not baked into plate
- Added lighting variants: 11 base plates → 17 total (day/dusk/night/dawn for Andean pristine, volcanic variants for terraced, evening for Alpine)
- Time-lapse beats (A1_B009, A2_B005) flagged for AE/Premiere transition handling
- Updated all beat plate references to point to correct lighting variants
- LBM Relighting excluded (CC BY-NC), IC-Light V1 confirmed primary (Apache 2.0)

### v1.1 — session 2026-06-03
- LBM Relighting excluded: CC BY-NC 4.0 (non-commercial) license conflicts with post-CAS online distribution
- IC-Light V1 (Apache 2.0) confirmed as primary relighting model
- License rule formalised: only Apache 2.0, MIT, CC BY permitted in production pipeline
- Added license compatibility as paper discovery
- Added license rule to Key Creative Constraints

### v1.0 — session 2026-06-02
**MILESTONE: Full pipeline proven end to end.**

- Python runner script (`runner_test.py`) fully operational
- ComfyUI Cloud REST API integration confirmed:
  - `POST /api/prompt` → submits workflow, returns job ID ✅
  - `GET /api/job/{id}/status` → returns `"success"` when done ✅
  - `GET /api/jobs/{id}` → returns full job data including output filenames ✅
  - `GET /api/view?filename=X` → 302 redirect to signed download URL ✅
- Two API quirks documented:
  - Status endpoint returns `"success"`, jobs endpoint returns `"completed"` — different words, both handled
  - `/api/history/{id}` not available on Cloud — use `/api/jobs/{id}` instead
- First test image generated: Flux.1 Dev, Andean landscape, AomE prompt ✅
- Image auto-downloaded to `generated/` folder ✅
- SSL warning (LibreSSL vs OpenSSL) is harmless — no action needed
- MCP beta: still pending. REST API path confirmed as production approach going forward.

### v0.9 — session 2026-05-31
- Claude Code launched successfully in ~/Documents/CAS_AICP/AomE/ — reads project files automatically
- ComfyUI Cloud MCP connection attempted and blocked: closed beta, per-user feature flag gating
- API key method configured correctly in local config (claude mcp add --transport http with X-API-Key header)
- Waitlist submitted for MCP beta access with strong use case description
- Path B (direct REST API runner) confirmed as active fallback — not dependent on MCP beta
- API key security lesson: keys must never appear in chat or project files — treat like passwords
- Paper material: beta-gated infrastructure as a real production constraint documented

### v0.8 — session 2026-05-30 (closing)
- Added explicit transition/timing principle: fades, dissolves, hold frames handled in AE/Premiere only, never in generation
- Audited JSON for fade/transition fields — kept documented as AE/Premiere directives, clearly flagged so no generation skill tries to prompt them
- Distinguished content-opacity (final blend, kept for generation) from transition-opacity (AE stage)
- Distinguished content-motion (e.g. flower wilting on screen, Wan 2.2) from transition-fade (AE stage)

### v0.7 — session 2026-05-30 (later)
- Model verification pass: switched to LBM Relighting (better than IC-Light), dropped LayerDiffuse (Flux-incompatible), switched to ComfyUI-RMBG (unified matting toolkit)
- Orchestration upgraded from monolithic runner to composable Claude Skills architecture (per Anthropic engineers' Skills methodology)
- Phase 2 first task restructured around skills, not workflow templates alone
- Added "model recommendations age faster than pipeline" as paper discovery
- Added "Skills paradigm: orchestration as authorship" as paper discovery
- LBM commercial license added as open question

### v0.6 — session 2026-05-30
- Audio generation added to pipeline: Stable Audio 2.5/3.0 + MMAudio (both in ComfyUI Cloud)
- Generative compositing investigated → deliberately excluded as first step (paper framing prepared)
- Pipeline diagram updated to reflect full content-generation-in-Cloud, deterministic-assembly-locally

### v0.3+ — session 2026-05-28
- Model stack updated: Flux.1 Dev (image), Wan 2.2 (video), Nano Banana Pro (selective). SDXL/AnimateDiff/SVD deprecated.
- Compute moved to ComfyUI Cloud (Apple Silicon = no CUDA)
- Orchestration: runner script + pre-tested templates (not on-demand graph generation)
- Added Format & Codec Pipeline section (4b) — clarifies model outputs (PNG/MP4) vs pipeline codecs (ProRes/H.264)
- Exhibition: intentional 4:3 CRT, 16:9 master retained for future online use
- Claude Code installed on MacBook Air

### v0.2 — session 2026-05-20
Pending changes:
- [x] **Change 01:** Replace `"compositing_tool": "after_effects"` with two-tier `"compositing_strategy"` object:
  ```json
  "compositing_strategy": {
    "generative_passes": ["layer_diffuse", "ic_light"],
    "deterministic_compositor": "after_effects",
    "fallback": "after_effects_full",
    "approach": "generative_layer_generation_plus_deterministic_stacking",
    "notes": "IC-Light handles lighting harmonisation between generated layers. AE fallback if IC-Light insufficient."
  }
  ```
- [ ] *(further changes to be added this session)*

---

## 6. CAS Reflection Paper Brief

**Format:** 2–3 pages
**Formal criteria (from CAS documentation):**
- Acceptable grammar and syntax
- Organised with title, author, affiliation, contact information, references
- Illustrations, tables, numerical presentations properly labelled and referenced
- Data sources and previous works sufficiently referenced
- Applies terminology, methods, and best practices taught in the CAS
- Data sets, metadata, and data quality sufficiently described
- Applied methods sufficiently described
- Practical work critically reflected

### 6.1 Usage of Machine Learning
*Notes accumulated — reflects the CURRENT locked stack (RunComfy platform, from v2.0 onward):*
- **Flux.2 (text-to-image)** — primary base-plate generator. Produces the one fresh establishing plate per act; every other state in that act derives from it via masked editing, so composition is never re-rolled.
- **Flux.2 (image edit, unified/masked)** — primary variant generator. Relights locked plates for different times of day and carves structural changes (terracing) inside hand-painted masks that protect everything else pixel-for-pixel.
- **Wan (FLF2V — first-last-frame video)** — primary motion generator. Interpolates between two locked, relit plates to produce the transitions between times of day; validated end-to-end on the day→dusk transition.
- **RIFE (frame interpolation)** — smooths Wan's native output to a higher effective frame rate for the final clip.
- **MMAudio (video-to-audio)** — generates ambient/diegetic sound directly from a finished video clip; validated end-to-end on the day→dusk transition.
- **IC-Light V1** (planned, not yet built) — dedicated relighting model for deterministic light-DIRECTION control (via a light map), to correct dawn/dusk sun direction where text-based relighting could not reliably do so.
- **Claude (Sonnet / Opus)** — screenplay-to-JSON conversion, prompt orchestration, pipeline architecture and scripting, diagnostic partner for reading model failure modes.
- **ChatGPT image generation** — used only for early reference/composition-guide images, never as a pixel source in the final pipeline.

*Models evaluated and rejected (documented for the paper's methodology discussion):*
- **FLUX.1 Kontext Dev / Flux.1 Dev** — the original May-2026 plan (ComfyUI Cloud platform). Superseded by the RunComfy + Flux.2 pivot, which offered a true superset (no separate ControlNet/depth restriction) on one platform.
- **LBM Relighting** (JasperAI) — evaluated for lighting harmonisation, excluded: CC BY-NC 4.0 (non-commercial) license conflicts with post-CAS distribution.
- **IC-Light V2** — same non-commercial licensing issue; V1 (Apache 2.0) adopted instead.
- **LayerDiffuse** — supports only SD15/SDXL, incompatible with Flux; replaced by Flux generation + matting.
- **SD 3.5** — tested and abandoned; repeatedly failed to include plant + landscape in one shot.
- **SDXL** — superseded by Flux after evaluation.
- **AnimateDiff / SVD** — superseded by Wan for video/motion.

### 6.2 Technical Discoveries for Filmmaking Practice
*Notes accumulated:*
- **JSON as cinematic control layer** — the screenplay becomes machine-readable metadata that drives generation; a genuinely new kind of production document
- **Locked camera as generative discipline** — fixing the camera is not just an aesthetic choice; it enables layer reuse and temporal consistency across beats
- **Layering as the only viable control strategy** — no single model can generate a full composite frame with reliable multi-element control; layer separation enforces creative intent
- **LLM image generation cannot produce precision storyboards** — no reliable shot repeatability, no controlled composition, artefacts, and generic "slop" outputs are a consistent failure mode. Act 1 storyboard produced with ChatGPT; one anchor reference image per act. Treated as complete given these structural limitations.
- **IC-Light as a bridge tool** — if proven, generative lighting harmonisation removes a key seam between generated and composited layers
- **License compatibility as a first-class production constraint.** Multiple state-of-the-art models (IC-Light V2, LBM Relighting) were evaluated and excluded specifically because their CC BY-NC 4.0 licenses prohibit commercial use — despite being technically superior alternatives. For a film intended for post-academic public distribution, model license must be verified before pipeline integration, not after. Established rule: only Apache 2.0, MIT, or CC BY permitted in the production stack.
- **REST API as the robust production layer.** The official MCP connection was blocked by beta gating. The direct REST API approach (Python script calling ComfyUI Cloud endpoints) proved more reliable, more controllable, and better aligned with the "runner + pre-tested templates" architecture. This is a practical finding: the lower-level tool (direct API) outperformed the higher-level convenience layer (MCP) for production use — because it removed a dependency on infrastructure the author doesn't control.
- **Beta-gated infrastructure as a production constraint.** The official ComfyUI Cloud MCP server is invite-only with per-user feature flag gating. Having a valid account and API key is insufficient — access requires specific beta enablement. Lesson: when building with emerging AI tools, always design fallback paths that don't depend on a single point of access. For AomE, the REST API runner approach (direct Python calls to the ComfyUI Cloud API) is that fallback — it works with the same API key, no beta required.
- **API key security in a production pipeline.** Working with real credentials (API keys) requires treating them like passwords: never paste in chat, never store in project files, never share. The correct storage is local only — either in a password manager or as a configured environment variable. This is a practical security lesson directly relevant to professional AI-assisted production.
- **The Skills paradigm: orchestration as authorship.** Following Anthropic engineers' Claude Skills methodology, the project orchestrates ComfyUI Cloud via a library of composable skills rather than one-shot prompts or monolithic scripts. Three concrete observations: (1) the tools layer (saved Python scripts, template references) is where most leverage lives, not the prompt itself; (2) composable skills compound — improvements to one skill propagate everywhere it's used; (3) skills improve session over session, making the tooling itself part of the authorship. This reframes AI-assisted filmmaking from "AI generates assets" to "the filmmaker builds a learning system that generates assets."
- **ControlNet unavailability as a finding.** ComfyUI Cloud's commercial-cleared model policy (every model cleared for commercial use, no exceptions) excludes non-commercial ControlNet models. This platform constraint forced evaluation of alternatives, leading to FLUX.1 Kontext — a model that arguably serves the project better than ControlNet would have. A deliberate commercial licensing policy produced a technically better outcome. This is a genuine discovery about how platform constraints shape generative workflows.
- **FLUX.1 Kontext as a breakthrough for film production pipelines.** Kontext takes text AND image as input, preserving composition while responding to change instructions. For a fixed-camera film with multiple lighting states, this means: generate once with the reference, iterate lighting variants with text instructions. Dramatically more efficient and consistent than text-only generation for multi-state environments.
- **Model recommendations age faster than pipeline architecture.** Within a 3-month design window for this project (March–May 2026), recommendations shifted significantly: SDXL → Flux.1 Dev (image), AnimateDiff/SVD → Wan 2.2 (video), IC-Light → LBM Relighting (harmonisation), LayerDiffuse dropped entirely (Flux incompatibility), BiRefNet → ComfyUI-RMBG (unified matting). The pipeline architecture stayed stable; the models inside it changed. Documenting this is itself a finding about generative-AI filmmaking: methodology endures, model choices do not.
- **Generative compositing was evaluated and deliberately excluded as a first step.** Tools exist (ComfyUI-AE-Animation provides timeline + keyframes + layers; VHS nodes support multi-layer video composition with mask blending; NVIDIA documents image deconstruction into alpha-masked layers). Excluded for this project due to: (a) 6-week timeline to exhibition; (b) compositing demands precision that ComfyUI's silent-failure modes (identified from tutorial review) cannot reliably deliver; (c) author already commands After Effects and Premiere from filmmaking practice. Framed as a deliberate engineering decision — generative for content, deterministic for assembly — not a limitation. Door left open for post-CAS exploration.
- **The "AI builds everything in plain English" promise vs. reality** — current tutorials promote letting Claude Code generate complex ComfyUI workflows from scratch on demand. Critical testing (and the tutorials' own footage) reveals consistent failure modes: silent format mismatches (local JSON vs cloud graph format), dropped scenes reported as successes, scrambled scene order, and character/subject consistency drift. The engineered workaround — a small set of pre-tested workflow templates driven by a Python "runner" script — is itself a technical discovery: robustness comes from constraining the AI's role to parameterisation, not open-ended generation.

### 6.3 Discoveries about pipeline boundaries

The investigation identified a clear seam in current generative pipelines: **generation is mature, compositing is not (yet).**

Generative content production — image, video, lighting harmonisation, music, ambient sound — can all run inside one node-based environment (ComfyUI Cloud). Generative *compositing* tools exist (ComfyUI-AE-Animation, VHS composition nodes) but trade precision and reliability for methodological purity. For a graded film on a 6-week timeline, the engineering decision was: **fully generative pipeline for content, deterministic tools (After Effects, Premiere Pro) for final assembly.** Not a failure of the generative paradigm — a mapping of where its frontier currently sits.

### 6.4 Limitations
*Notes accumulated:*
- No mature generative compositor exists for full layer stacking with z-depth, occlusion, and motion blur — deterministic fallback always needed
- IC-Light promising but may not handle all layer combinations reliably
- SD 3.5 failed at multi-subject composition (plant + landscape simultaneously)
- Temporal consistency across beats remains a structural challenge; mitigated by anchor frames and `continuity_reference` fields in JSON
- LLM orchestration is not fully automated — human review of every prompt and JSON field is required
- AI-generated ComfyUI workflows are fragile — silent failures (wrong output format, missing generations) require active verification; cannot be trusted blindly. Mitigated by the pre-tested-template + runner approach.

### 6.5 Ethical Issues

**Copyright:**
- All generated assets produced from diffusion models trained on large-scale image datasets with opaque provenance
- AomE explicitly avoids style imitation (`no_style_imitation: true` in JSON) — deliberate ethical and aesthetic choice
- Distribution of generated film carries unresolved IP questions depending on jurisdiction
- *Discussion point: does the LLM-orchestrated pipeline create sufficient transformative distance from training data?*

**Cultural Bias:**
- Act 1 depicts Andean/Inca cultural landscape — risk of reductive or stereotyped visual representation
- Models trained predominantly on Western image datasets may produce inaccurate representations of Andean terraces, Quechua material culture, and Andean landscape
- Mitigation: highly specific prompts, reference image grounding, human review of all generated frames
- *Discussion point: what is the filmmaker's responsibility when using generative tools to depict non-Western historical cultures?*

**Labour and ecology:**
- Computational cost of diffusion model inference is non-trivial
- *Discussion point: carbon footprint of a generative film pipeline vs. traditional production*

---

## 7. Key Creative Constraints (Do Not Drift)

- Camera locked. No pan, tilt, zoom. Ever.
- Plant centered. Always plant_001. Always foreground dominant.
- No full human faces. No full human bodies.
- No style imitation. Photorealistic, cinematic, documentary-like.
- Motion must feel like a still image becoming unstable — not animation.
- Three acts = three eras = three systems failing. One plant persists.
- Screenplay authorship stays with Samuel — AI generates assets, not narrative.
- All models in the production pipeline must have commercial-safe licenses (Apache 2.0, MIT, or CC BY). NC (non-commercial) licenses are excluded regardless of model quality.

---

## 8. Open Questions / Decisions Pending — CURRENT (2026-07-03)

- [ ] **Sequential multi-mask terraced rebuild** (`A1_plate_B3_terraced_v2`) — Pass 1 (left slope) in progress; Pass 2 (right slope) and Pass 3 (wall) still to do.
- [ ] **5-day timelapse cycle** — Day 1 anchors locked; Days 2–5 (16 plates) to be batch-generated, one state at a time.
- [ ] **Cultivated terraced state** (potato/quinoa/oca) — written and masked, blocked on terraced_v2 being solid first.
- [ ] **Charred state** — instruction ready, blocked on cultivated being locked.
- [ ] **Dawn light direction** — parked; deterministic fix is IC-Light V1 (not yet built).
- [ ] **Foreground fauna motion** (grass/bushes) — parked; Wan FLF2V cannot animate near-identical foregrounds; leading alternative is After Effects displacement, not yet implemented.
- [ ] **Remaining day-cycle transitions** (dusk→night, night→dawn, dawn→day) — prompts written, not yet generated.
- [ ] **Transition-queue batch function** — not yet built; worth building once the day-cycle transition set is complete.
- [ ] **IC-Light V1 build** — deployment + skill not yet started.
- [ ] **Plant work** — not yet started; B002 (hero growth shot) is the planned first beat, since it establishes the plant's visual identity for all later beats.
- [ ] **Act 2 + Act 3** — not started; architecture is designed to extend directly once Act 1 is proven, per the two-milestone plan.

**Resolved and superseded (kept for record, no longer open):**
- ✅ Platform: RunComfy (single platform, not the original ComfyUI Cloud plan)
- ✅ Base model: Flux.2 (text-to-image + edit), not Flux.1 Dev/Kontext
- ✅ Video: Wan FLF2V + RIFE, validated end-to-end
- ✅ Ambient audio: MMAudio, validated end-to-end (`generate_audio.py`, audio-only default + optional `--mux`)
- ✅ Orchestration: `generate_plate.py` / `generate_transition.py` / `generate_audio.py`, driven by the beat JSON — not the originally-planned composable `/generate-plate` etc. skill-file architecture
- ✅ Seed/metadata loss: solved — every plate embeds seed+metadata in the PNG plus a sidecar JSON (`--read-seed` to recover)
- ✅ Versioning discipline: never overwrite, always bump version — enforced throughout
- ✅ Relighting license: IC-Light V1 (Apache 2.0) chosen over V2/LBM Relighting (both non-commercial)
- ✅ Composition drift: solved via sequential small masked passes rather than single large edits
- ✅ MCP beta gating — moot; the REST-API-driven scripts are the actual production approach, not a fallback

---

*This document is a living reference. Update after every working session. Download and re-upload to project files to persist.*
