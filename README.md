<p align="center">
  <img src="assets/icon.svg" width="88" height="88" alt="Snow Patrol" />
</p>

<h1 align="center">SNOW PATROL</h1>

<p align="center">
  <strong>Sprite-Stacked 3D Three.js Alpine Snowplow Game</strong><br>
  Real-time deformable snow physics · 5 scalable mountain shifts · FixedSeed/Robin 48 kHz expressive radio voices · Procedural synth + vocal-choir soundtrack · Native controller + rumble
</p>

<p align="center">
  <a href="https://nearbycoder.github.io/snow-patrol/"><strong>🌐 Marketing Site &amp; Live Demo</strong></a> ·
  <a href="https://nearbycoder.github.io/snow-patrol/play.html"><strong>▶ Play Fullscreen</strong></a>
</p>

---

## Highlights

- **Volumetric Sprite-Stacking in Three.js** (inspired by [`danielwh2/sprite-stacking`](https://github.com/danielwh2/sprite-stacking)) — Every vehicle part, chalet, gondola cabin, husky, pine tree, boulder, and rescue helicopter is built as ground-to-roof 2D pixel slice strips with computed 3D occupancy normals, upper-neighbor AO, emissive masks, and upward-facing `normZ` snow caps. Includes a live **Slice Strip Inspector (`V`)** and **3D Exploded Slice Mode (`X`)**.
- **Real-Time `128×128` Deformable Snow Physics** — Scoop powder into 15 blade bins, push a churning rolling snow wave ahead of the moldboard, cast angled windrow berms sideways (`Q`/`E`), lift the blade (`Space`), and carve corduroy tracks.
- **5 Scalable Alpine Shifts (`60m` → `110m`)**:
  1. **Cabin Driveway** (`SMALL · 60m` · Alpenglow Sunset)
  2. **Summit Ski Plaza** (`MEDIUM · 74m` · Alpenglow Sunset + Overhead Gondolas + Black Ice)
  3. **Chalet Village Court** (`MED-LG · 84m` · Crisp Alpine Day + 3 Guest SUVs)
  4. **Pine Ridge Pass** (`LARGE · 96m` · Dusk Blizzard S-Curve Highway + Deep Drifts)
  5. **Avalanche Helipad** (`MASSIVE · 110m` · Aurora Midnight Blizzard + Live Rescue Helicopter Finale)
- **Expressive 48 kHz Character Voice Cast ([`FixedSeed/Robin`](https://huggingface.co/FixedSeed/Robin))** — 24 embedded broadcast-mastered lines across **Chief Maren** (Base Dispatch), **Gus** (Snowcat Garage), and **Outraged Lodge Guest** (Channel 4), directed with per-line emotional prompts & inline acting tags (`[laughs]`, `[shouting]`) and routed through selectable Web Audio radio EQ with automatic music ducking.
- **Snowcat Garage & Live Paint Shop (`G`)** — 4 mechanical upgrades (Wide-Wing Blade, Twin-Turbo Diesel, Heated Ice-Grip Tracks, Rotary Powder Thrower) + 5 shader-remapped Snowcat liveries.
- **Native Gamepad Support + Dual-Motor Rumble** — Analog RT/LT throttle, Left Stick steering, Right Stick 360° camera orbit, and continuous snow-carving haptics.
- **Full Audio & Visual Settings Menu (`O`)** — Master/Music/Radio/SFX volumes, Radio EQ presets, 1x–4x pixel scale, dynamic shadows, 1px silhouette outline & emissive bloom sliders, persisted to `localStorage`.

## Controls

| Action | Keyboard / Mouse | Controller (Xbox / PS / Steam Deck) |
| :--- | :--- | :--- |
| Drive / Reverse | `W` `S` / `↑` `↓` | `RT` / `LT` (or Left Stick) |
| Steer Tracks | `A` `D` / `←` `→` | `Left Stick` |
| Angle Plow Blade | `Q` / `E` | `LB` / `RB` |
| Lift / Drop Blade | `Space` | `A` (`✕`) |
| Twin-Turbo Boost | `Shift` | `X` (`□`) or `L3` |
| Alpine Air Horn | `H` | `B` (`○`) |
| Camera Orbit / Mode | Drag / Wheel / `C` | `Right Stick` / `Y` (`△`) |
| Settings / Garage / Slices | `O` / `G` / `V` / `X` | `Start` / `Select` |

## Project Structure

- [`index.html`](index.html) — Animated pixel-art marketing landing page with living alpine diorama, 3D sprite-stack turntable, embedded playable stage, and live FixedSeed/Robin voice auditions
- [`play.html`](play.html) — Standalone single-file Three.js game (with all 24 48 kHz FixedSeed/Robin audio clips embedded)
- [`scripts/generate_voices.py`](scripts/generate_voices.py) — Reproducible [`FixedSeed/Robin`](https://huggingface.co/FixedSeed/Robin) 48 kHz character voice synthesis & mastering script
- [`assets/voices/`](assets/voices/) — Individual mastered `.mp3` clips for the marketing site audio auditions

## Attribution & Licenses

- **Sprite-Stacking Technique**: Inspired by [`danielwh2/sprite-stacking`](https://github.com/danielwh2/sprite-stacking) (MIT)
- **Neural Voices**: Synthesized at 48 kHz with [`FixedSeed/Robin`](https://huggingface.co/FixedSeed/Robin) by Fixed Seed Research Laboratory (Fixed Seed Open License)
- **3D Engine**: [Three.js](https://threejs.org/) (MIT)
