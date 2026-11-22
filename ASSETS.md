# Assets

Status of every visual in the game: converted to a pixel-art sprite, or still drawn in code from rectangles.

✅ sprite in the game · 🎨 sprite made, not yet wired into the game · ⬜ drawn in code · — stays in code on purpose

**How the art and code sides work together:** see `ART_BRIEF.md`.
- **Code side:** adds a row under **Requests** when the game needs an asset.
- **Art side:** delivers it, updates the tables below and moves the row to **Done**.

## Requests

| # | Asset | File | Size / layout | For | Status |
|---|---|---|---|---|---|
| 1 | Remaining vehicle masters: tram SL79, old tram, Italian tram | `assets/vehicles/hires/tram-sl79.svg` … | hi-res, same scale as the others | later scenes | open |
| 2 | Tram obstacle, **full length** (rolls in fast; the players get thrown onto it or jump on and ride it) | `assets/sprites/tram-hd.png` | the 5-section new light-blue tram (`tram-new`) through `game_hd.py` (8 game px/m = 32 canvas px/m, ≈ 970 × 140 canvas px), side view, trimmed, wheel bottoms on the last row. The game treats the roof as walkable 31 game px above the wheel bottoms and the length as 242 game px; tell the code side if yours differs | chorus 1 → chorus 2 (`drawTram`) | open |

### Done

| Asset | File |
|---|---|
| The two girls | `assets/sprites/victoria.png`, `friend.png` |
| Local trains (pixel) | `assets/sprites/train-green.png`, `train-tomato.png` |
| Automat Victoria | `assets/sprites/automat.png` |


Sizes are in game pixels; the screen is 320 × 180. For a code-drawn asset the size is how big it is drawn now, which is a sensible frame size for its sprite.

## Characters

| Asset | Status | Size | File / code | Notes |
|---|---|---|---|---|
| Victoria | ✅ | 24 × 32 frames | `assets/sprites/victoria.png` | idle ×2, run ×4, jump up/down, slide, attack; normal + ninja |
| Friend | ✅ | 24 × 32 frames | `assets/sprites/friend.png` | same layout as Victoria |
| Automat Victoria (companion) | ✅ | 24 × 32 frames | `assets/sprites/automat.png` (`tools/sprites/automat.py`) | idle0 idle1(blink) talk0 talk1 cheer0 cheer1 plain; talks when the lyrics are about her, cheers on the chorus calls and the win screen |
| Kaos-trikken (boss) | ⬜ | 80 × 70 | `drawBoss` in `src/render/sprites.ts` | white hit flash; damage and explosion frames |

## Enemies and obstacles

New pixel sprites, bigger and clearer than before, are in `assets/sprites/enemies.png` with `enemies.json`, made by `tools/sprites/enemies.py`. The JSON gives row, frames, fps and visible size per type; the cells are 32 × 32 and bottom-centred. Wiring them into the game is the code side's first open task (see `CODE_BRIEF.md`).

All in `drawEnemy` (`src/render/sprites.ts`).

| Asset | Status | Size | Appears | Notes |
|---|---|---|---|---|
| Suitcase | 🎨 | 12 × 12 | intro, verse 1 | |
| Snow pile | 🎨 | 16 × 7 | intro, verse 1 | |
| Pigeon | 🎨 | 10 × 8 | verse 1, pre-chorus 1 | 2-frame wing flap |
| Glitch blob | 🎨 | 11 × 11 | pre-chorus 1 | flickering pixels |
| Enemy ninja | 🎨 | 15 × 22 | chorus 1 → end | |
| Drone | 🎨 | 18 × 8 | chorus 1 → end | 2-frame blinking light |
| Ticket bot | 🎨 | 12 × 22 | verse 2, chorus 2 | label (CHILD/ADULT/STUDENT/SENIOR/KAOS) is text above it |
| Tram | ⬜ | 92 × 33 | several times | jump over it; «!» warning is text |
| Fire | 🎨 | 14 × 9 | pre-chorus 2 | animated flames |
| Boss shot | 🎨 | 8 × 8 | boss phase | |
| Boss fireball | 🎨 | 12 × 8 | boss phase | |

## Pickups and projectiles

| Asset | Status | Size | Code | Notes |
|---|---|---|---|---|
| Paper ticket (pickup) | 🎨 | 8 × 6 | `drawEnemy` | will also be the ammo (see IDEAS.md) |
| Coin | 🎨 | 7 × 7 | `drawEnemy` | could spin |
| Ticket terminal (power-up) | 🎨 | 10 × 14 | `drawEnemy` | «Kort mot terminalen» |
| Thrown ticket | ⬜ | 6 × 4 | `drawGame` in `src/render/screens.ts` | rotates in flight |
| Shuriken | ⬜ | 6 × 6 | `drawGame` | ninja-mode projectile |

## Effects and HUD

| Asset | Status | Size | Code | Notes |
|---|---|---|---|---|
| Katana slash arc | ⬜ | ~20 × 30 | `drawGirl` in `src/render/sprites.ts` | canvas strokes; could be a 3–4 frame sprite |
| Hit sparks / particles | ⬜ | 2 × 2 | `drawGame` | could be small burst sprites |
| Hearts (HUD) | ⬜ | 7 × 6 | `drawGame` | pixel hearts, or tickets if they become ammo |
| Power-up ★★★ (HUD) | ⬜ | text | `drawGame` | |
| Progress bar (HUD) | — | 30 × 4 | `drawGame` | |
| Screen flashes (scene cut, ninja, colour change, final hit) | — | full screen | `flash` in `src/render/draw.ts` | |
| Text: banners, score, pop-ups, title, win screen | — | | `text` in `src/render/draw.ts` | font: Press Start 2P |
| Lyric subtitles | — | | `src/ui/subtitles.ts` | HTML layer, not canvas |

## Vehicles

The hi-res masters are cartoon side views in `assets/vehicles/hires/`: SVG files plus PNGs rendered at 2×. All share one scale, about 50 SVG units per metre (100 px per metre in the PNGs), and stand on the same ground line.

| Vehicle type | Generator |
|---|---|
| Trains | `tools/vehicles/trains.py` |
| Subways | `tools/vehicles/subways.py` |
| Buses | `tools/vehicles/road.py` |
| Trams | `tools/vehicles/trams.py` |

Shared helpers are in `common.py`. The generators refuse to build a vehicle whose windows or wheel arches overlap a door.

**For now, vehicles use their hi-res masters in the game.** The pixel versions didn't look good enough. `tools/vehicles/game_hd.py` renders a master at the in-game size into `assets/sprites/<name>-hd.png`, at 32 canvas px per metre, which is 8 game px per metre on the 4× canvas. The game draws it smoothly. New pixel sprites can come later.

The parked pixel approach: game sprites are redrawn on the pixel grid, not scaled down. `tools/vehicles/pixel_trains.py` re-rasterises the same designs at 8 px per metre with no anti-aliasing. Details get fixed pixel sizes and outlines are exactly 1 px. Other vehicles will get the same treatment.

Quick previews (a plain downscale) come from `tools/vehicles/pixelate.py`:

- **`--ppm 8`:** 8 pixels per metre, which keeps relative sizes. Output goes to `assets/vehicles/ppm8/`.
- **`--height 36`:** every vehicle 36 px tall. Output goes to `assets/vehicles/px36/`.

`preview-pixelated.png` shows them at 8 px per metre. Every vehicle is seen from the side only.

No company marks or logos on the vehicles. References are in `inspiration/vehicles/`.

✅ sprite in the game · 🎨 hi-res master made · ⬜ not started · ✖ dropped

| Vehicle | Status | Files | Planned use |
|---|---|---|---|
| Local train, green | ✅ | hi-res: `local-train-green.svg` (3 cars), `-cab.svg` (2 cars) · **in game:** `assets/sprites/train-green-hd.png` (hi-res, drawn smoothly at 8 px per metre) · parked pixel version: `train-green.png` | Sandvika stasjon background (verse 1: brakes and stops by the machines) |
| Local train, tomato soup (type 69) | ✅ | hi-res: `local-train-tomato-soup.svg` (3 cars), `-cab.svg` (2 cars) · **in game:** `assets/sprites/train-tomato-hd.png` · parked pixel version: `train-tomato.png` | Sandvika stasjon background (intro, pre-chorus 1) |
| Airport express train | 🎨 | `airport-express.svg` (3 cars), `-cab.svg` (2 cars) | |
| Bus, red | 🎨 | `bus-red.svg` | |
| Bus, red, articulated | 🎨 | `bus-red-articulated.svg` | burning buses in pre-chorus 2? |
| Bus, green (3 axles, lime) | 🎨 | `bus-green.svg` | |
| Bus, old | ✖ | | dropped |
| Tram, new (light blue) | 🎨 | `tram-new.svg` (5 sections), `tram-new-short.svg` (3) | in-game tram obstacle? |
| Subway, new (light grey) | 🎨 | `subway-new.svg` (3 cars), `subway-new-2.svg` (2 cars) | |
| Subway, old (red and blue) | 🎨 | `subway-old.svg` (3 cars), `subway-old-2.svg` (2 cars) | |
| Tram, SL79 | ⬜ | | |
| Tram, old | ⬜ | | |
| Tram, Italian | ⬜ | | |
| Tram in the game (enemy obstacle) | ⬜ | `drawEnemy` | could use the new tram master |
| Kaos-trikken (boss) | ⬜ | `drawBoss` | could build on one of the tram masters |

## Backgrounds

All in `drawScene` (`src/render/scenes.ts`). These are kept as they are for now; they're listed for later.

| Asset | Status | Scene | Notes |
|---|---|---|---|
| Sky gradients | — | all | |
| Falling snow | ⬜ | station, glitch | |
| Houses with lit windows | ⬜ | station, glitch | parallax layer |
| Platform roof + «OSLO S» departure boards | ⬜ | station, glitch | canopy sections with regular gaps, pillars and lamps; only 2 boards (`drawPlatformRoof`) |
| The three blue ticket machines | ✅ | verse 1 | «tre blå maskiner»: the `plain` frame of `automat.png` (same style as Victoria, no face or arms). The left one is Victoria; she wakes up and follows the girls when they reach her. |
| Glitch stripes + «A-A-A-AUTOMAT» | ⬜ | glitch | |
| Sun, barcode skyline, Holmenkollen jump, neon grid floor | ⬜ | neon, boss | |
| Map lines + place-name signs | ⬜ | map | Tjuvholmen, Kampen … |
| Burning trams and buses, embers | ⬜ | chaos | |
| Ground strip and beat line | — | all | |
| Eplehuset | ⬜ | (new) | idea: tram crashes into it |
| Entur logo billboard | ⬜ | (new) | idea: pixelated logo on a building or station |
| Tokyoslo street: Rådhuset, Stortinget, Slottet, Universitetet, Nationaltheatret with pagoda roofs, lanterns, neon signs, TOKYOSLO billboard | ✅ in game | Tokyoslo (stage 4 from 1:42.0, stages 5–7) | `assets/backgrounds/tokyoslo-buildings.png` (902 × 150, transparent, bottom row on `GROUND`) from `tools/backgrounds/tokyoslo.py`; drawn by `drawTokyoslo` in `scenes.ts` (parallax 0.45) in map after 1:42.0, chaos and boss |
| Tokyoslo far skyline | 🟡 draft | Tokyoslo | `assets/backgrounds/tokyoslo-far.png` (640 × 150, tiles horizontally, parallax 0.15), same script; to be made full level width |
