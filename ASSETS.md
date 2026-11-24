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
| 2 | Tram obstacle, **full length** (rolls in fast; the players get thrown onto it or jump on and ride it) | `assets/sprites/tram-hd.png` | the 5-section new light-blue tram (`tram-new`) through `game_hd.py` (8 game px/m = 32 canvas px/m, ≈ 970 × 140 canvas px), side view, trimmed, wheel bottoms on the last row. The game treats the roof as walkable 31 game px above the wheel bottoms and the length as 242 game px; tell the code side if yours differs | chorus 1 → chorus 2 (`drawTram`) | withdrawn: the game now draws the `tram-new.png` master directly |
| 3 | **Code:** add standable props (`props.png`/`props.json`): solid top at `top` px above the base, place them in the stages. Today only trams have standing physics | `assets/sprites/props.png` + `.json` | cells 112 × 64, bottom-centred; trash 15×17, recycling 24×36, phone booth 21×44, kiosk 106×61 | level 4 street, stations | open (code side) |
| 4 | **Code:** street lamps: draw `lamps.png` behind the characters and `lamps-light.png` (same grid, pole centred on x = 48) in front of them; heads are standable at `top` over `top_span` | `assets/sprites/lamps*.png` + `lamps.json` | cells 96 × 80 | level 4 street, subway stations | open (code side) |
| 5 | **Code:** before ninja mode use the thugs (`thug`, `punk`, `tagger`) where the ninjas are; same frame layout as `ninjas.png`, so `src/ninjas.ts` can drive them. The tagger's spray row (row 3, 4 frames, body at x = 32 in the cell) is for the subway scene | `assets/sprites/thugs.png` + `.json` | 40 × 32 cells | before 1:40 | done: wired in (`src/ninjas.ts`); the 16 ninjas before 1:40.15 are now thug/punk/tagger, and `tagger_spray` is an editor item for the subway |
| 6 | **Code:** replace the ticket bot + text label with the zombie passengers; `passengers.json` maps each kind to its label (ADULT, CHILD, SENIOR, STUDENT). Frames: idle ×2, walk ×4, attack ×2 | `assets/sprites/passengers.png` + `.json` | 40 × 32 cells | verse 2, chorus 2 | done: `src/passengers.ts`; the 25 labelled bots are now passengers (label kept above them, in red); the 9 KAOS bots stay bots |

### Done

| Asset | File |
|---|---|
| The two girls | `assets/sprites/victoria.png`, `friend.png` |
| Local trains (pixel) | `assets/sprites/train-green.png`, `train-tomato.png` |
| Automat Victoria | `assets/sprites/automat.png` |
| Street props: trash bin, recycling bin, phone booth, kiosk | `assets/sprites/props.png` + `props.json` |
| Street lamps + light | `assets/sprites/lamps.png`, `lamps-light.png`, `lamps.json` |


Sizes are in game pixels; the screen is 320 × 180. For a code-drawn asset the size is how big it is drawn now, which is a sensible frame size for its sprite.

## Characters

| Asset | Status | Size | File / code | Notes |
|---|---|---|---|---|
| Victoria | ✅ | 24 × 32 frames | `assets/sprites/victoria.png` | idle ×2, run ×4, jump up/down, slide, attack; normal + ninja |
| Friend | ✅ | 24 × 32 frames | `assets/sprites/friend.png` | same layout as Victoria |
| Automat Victoria (companion) | ✅ | 24 × 32 frames | `assets/sprites/automat.png` (`tools/sprites/automat.py`) | idle0 idle1(blink) talk0 talk1 cheer0 cheer1 plain; talks when the lyrics are about her, cheers on the chorus calls and the win screen |
| Celebration (ending): both girls in ninja outfits, Automat Victoria | ✅ | 24 × 32 frames | `assets/sprites/celebrate.png` (rows Victoria, friend: turn ×3, front idle ×2, wave ×4, jump takeoff/rise/fall/land), `automat-celebrate.png` (front, wave ×4, jump ×4, blink) + `celebrate.json` (layout, fps, jump timing), from `tools/sprites/celebrate.py`; used for the centered ending celebration and score summary |
| Automat Victoria, rainbow mode (level 2) | ✅ | 28 × 32 frames + ribbon | `assets/sprites/automat-rainbow.png` (fly0 fly1 glitch0 glitch1), `rainbow-tail.png` (6 × 14 segments seg0 seg1 fade0 fade1), `rainbow-tail-light.png`, `rainbow-sparkle.png`, `rainbow.json` (`tools/sprites/rainbow.py`) | she flies on a rubber band above the player through bars 26–33 trailing a stepped rainbow, lands back at bar 34 |
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
| Enemy ninjas: Shadow (`ninja`), Oni (`ninja_oni`, katana, 2 hp), Wanderer (`ninja_kasa`, straw hat, short sword) | ✅ | 18 × 30 (40 × 32 cells) | chorus 1 → end | `assets/sprites/ninjas.png` + `.json` (`tools/sprites/ninjas.py`): idle, run ×6, crouch, jump up/down, attack ×3; facing left. Jumps and frame choice in `src/ninjas.ts`: Shadow hops once on the way in, Oni leaps and slashes, Wanderer keeps hopping. The level's 82 ninjas are spread evenly over the three kinds |
| Drone | ✖ | 18 × 8 | | replaced by the seagull (the sprite stays in the sheet) |
| Seagull (`gull`) | ✅ | 22 × 12 body (wings 26 × 31) | chorus 1 → end | `enemies.png` row 13: 8-frame flap at 14 fps, out of step per gull; JSON `dy` 11 draws the cell lower so the body sits on the base; stompable like the pigeon. All drones in `level.json` are now gulls |
| Ticket bot | 🎨 | 12 × 22 | verse 2, chorus 2 | label (CHILD/ADULT/STUDENT/SENIOR/KAOS) is text above it; to be replaced by the zombie passengers |
| Zombie passengers: adult (yellow bob, trench coat, handbag), child (red cap), senior (newspaper), student (beanie, joint) | ✅ | 18 × 30 / 25 / 27 / 30 | verse 2, chorus 2 | `assets/sprites/passengers.png` + `.json` (`tools/sprites/people.py`): pallid skin, red glowing eyes, ordinary clothes; idle ×2, shambling walk ×4 with arms out, attack ×2 (the senior swats with his paper); request 6 |
| Thugs: thug (leather jacket), punk (pink mohawk), tagger (orange hoodie, spray can) | ✅ | 18 × 30 (punk 32 with the mohawk) | before ninja mode | `assets/sprites/thugs.png` + `.json`: same 14 columns as the ninjas; row 3 = the tagger's spray mode, 4 frames with a slightly transparent pink mist (body at x = 32 so the mist fits); request 5 |
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

## Street props

Pixel sprites at girl scale, front view, in `assets/sprites/props.png` + `props.json` (`tools/sprites/props.py`; 112 × 64 cells, bottom-centred; JSON adds `top`, the walkable height). Wiring them in is request 3.

| Prop | Status | Size | Notes |
|---|---|---|---|
| Round trash bin (dark green, slatted) | 🎨 | 15 × 17 | |
| Textile recycling bin (red, no logo) | 🎨 | 24 × 36 | |
| Phone booth (red «TELEFON») | 🎨 | 21 × 44 | top 44: one jump |
| Kiosk (freestanding, «KIOSK»), at dusk | ✅ | 106 × 61 | top 61: double jump; roof overhangs a pole on the left. Dark outside, lit windows and name plate, two downlights; its light (two warm cones + sign glow) is in `props-light.png` (same grid as `props.png`), drawn in front of the characters by `drawLampLight` |
| Street lamp, roadside, one arm | 🎨 | 31 × 62 | `lamps.png` row 0; arm points left, mirror for right; cool LED light |
| Street lamp, roadside, two arms | 🎨 | 53 × 62 | row 1 |
| Street lamp, round globe | 🎨 | 13 × 58 | row 2; warm light |
| Street lamp, vintage lantern | 🎨 | 17 × 46 | row 3; warm light |
| Subway platform lamp, two rising arms | 🎨 | 55 × 74 | row 4; cool light |
| Lamp light (smooth gradients: cones, radial glow, ground pool) | 🎨 | 96 × 80 cells | `lamps-light.png`, same grid as `lamps.png`; draw in front of the characters |
| Tokyoslo: red lacquer bin (`bin_tokyo`) | ✅ | 13 × 17 | `props.png`; one jump |
| Tokyoslo: two vending machines (`vending`) | ✅ | 31 × 43 | lit fronts, cool glow in `props-light.png`; one jump |
| Tokyoslo: lantern string between bamboo poles (`lanterns`) | ✅ | 92 × 51 | 2 frames sway/glow; warm-red glow; `top` 0 = not standable |
| Tokyoslo: vertical neon sign (`neon`) | ✅ | 18 × 53 | 3 frames flicker (one glyph drops out); pink glow; invented glyphs; not standable |
| Tokyoslo: ramen cart (`yatai`) | ✅ | 48 × 37 | 3 frames (noren flutter, steam); lantern glow + counter light; one jump |
| Tokyoslo: konbini (`konbini`) | ✅ | 102 × 59 | bright windows, lit «KONBINI» band, two cool cones; double jump |
| Tokyoslo lamp: vermilion post with red paper lantern (`tokyo_lamp`) | ✅ | 24 × 62 | `lamps.png` row 5; warm-red radial light |
| Tokyoslo stone lantern (`toro`) | ✅ | 19 × 37 | `lamps.png` row 6; firelight sideways and down; flat top, one jump |
| Park bench, European (`bench_park`) | ✅ | 38 × 18 | dark green cast-iron ends, wooden slats; one jump |
| Station bench, Sandvika (`bench_station`) | ✅ | 43 × 17 | steel frame, light wood slats; one jump |
| Glitched machine clone (`glitch_machine`) | ✅ | 28 × 32 | level 2 glitch: the plain ticket machine breaking up, 8 frames @ 8 fps (slipping slices, pink/cyan split, screen static, «A-A-A», missing-texture blocks); top 31, one jump; screen glow in props-light |
| Copy-pasted machines (`glitch_machine_stack`) | ✅ | 32 × 64 | level 2: a clone pasted on top of another, the top copy slips sideways; top 63, double jump |
| Smeared machine (`glitch_machine_smear`) | ✅ | 66 × 32 | level 2: a clone dragging three echoes to the left; a long platform, top 31 |
| Fountain, classic Oslo (`fountain`) | ✅ | 64 × 48 | tiered stone, darker for the night; 8 frames of pulsing semi-transparent water (centre jet + an arch to each side); lit from the water upwards (`props-light.png`); stand on the basin rim (`top` 13) |
| Advertising column, night (`ad_column`) | ✅ | 26 × 48 (48-px-wide canvas so the lamps' glow fits) | posters lit by two small lamps above them (light in `props-light.png`); top 46 = double jump |
| Cast-iron park railing, night (`railing`) | ✅ | 62 × 16 | spear tips; not standable |
| Tiger statue on a wide granite plinth, night (`statue`) | ✅ | 72 × 45 | a walking gilded-bronze tiger traced from Joakim's photo (`tools/sprites/ref/tiger.png`), facing left; the carved stripes come through as five bronze tones; stand on the plinth (`top` 17). Replaces the horse |
| Stone planter with flowers, night (`planter`) | ✅ | 28 × 16 | brighter flowers; `top` 9 |
| Bike rack with two bikes, night (`bikes`) | ✅ | 57 × 21 | red and blue bikes in profile, silver rims and spokes; not standable |
| Tea-house bench under a red parasol, Tokyoslo (`bench_asian`) | ✅ | 35 × 43 | red felt seat (`top` 13) |
| Old wooden shop, Tokyoslo (`shop_wood`) | ✅ | 84 × 54 | tiled roof, lattice, indigo noren, paper lanterns; warm light |
| Konbini light | ✅ | | sign band and light dimmed (Joakim: too bright) |
| Trees: `oslo_bare`, `oslo_leafy`, `oslo_leafy2` (night), `sakura`, `sakura2` | ✅ | 88 × 88, 80 × 97, 79 × 86, 89 × 70, 74 × 63 | `assets/sprites/trees.png` + `.json` (`tools/sprites/trees.py`), 100 × 100 cells, trunk centred; scenery behind the characters, not standable |

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
| Tram, Tokyoslo (two identical green-and-cream cars, chained) | ✅ | `tram-tokyo.svg/.png` (`tools/vehicles/trams.py`, `tokyo_tram()`) | the tram obstacle for trams due after 1:42 (`drawTram`); same length and roof height as `tram-new`, so the physics are unchanged |
| Tram, SL79 | ⬜ | | |
| Tram, old | ⬜ | | |
| Tram, Italian | ⬜ | | |
| Tram in the game (enemy obstacle) | ⬜ | `drawEnemy` | could use the new tram master |
| Kaos-trikken (boss) | ⬜ | `drawBoss` | could build on one of the tram masters |

## Landmarks (hi-res masters, for the title logo, silhouettes and backgrounds)

Flat elevations from `tools/landmarks/landmarks.py` → `assets/landmarks/hires/<name>.svg` + `.png` (10 SVG px/m, PNG 20 px/m, one shared scale; layers `base`/`shade`/`trim`/`win`/`detail`). Approved versions are frozen as `<name>.v1.svg/.png`; the generator only rewrites the unversioned files. Contact sheet: `python3 tools/landmarks/contact.py <out.png>`.

| Landmark | Status | Size (m) | File | Notes |
|---|---|---|---|---|
| MUNCH | ✅ v1 | 67 × 60 | `munch.v1.*` | upper third leans left, both sides at the same angle; low wing to the left |
| Radisson Blu Plaza | ✅ v1 | 13 × 117 | `plaza.v1.*` | only the knife-edge sliver, slanted top to a sharp point |
| Tryvannstårnet | ✅ v1 | 16 × 118 | `tryvann.v1.*` | |
| Rådhuset | ✅ v2 | 96 × 73 | `radhuset.v2.*` (v1 superseded) | towers the same size (18 × 66 m), 12 m in from each end, each with its own face (west: slit + spire, east: clock); stone ground floor as wide as the brick block |
| Slottet | ✅ v1 | 110 × 31 | `slottet.v1.*` | no flag |
| Stortinget | ✅ v1 | 74 × 21 | `stortinget.v1.*` | no flag |
| Nationaltheatret | ✅ v1 | 55 × 32 | `nationaltheatret.v1.*` | no flag, blank name plaques |
| Universitetet | ✅ v1 | 81 × 24 | `universitetet.v1.*` | |
| Monolitten | ✅ v1 | 1.5 × life (51 × 33) | `monolitten.v1.*` | |
| Holmenkollbakken | 🎨 redo | | `holmenkollen.*` | to redo later (Joakim may trace the shape); current: constant-thickness S-curve, flat ends, no supports |
| Operahuset | 🎨 redo | | `opera.*` | to redo later (Joakim may trace the shape); the foyer glass roof rises towards the left |
| Domkirken | ✅ v1 | 44 × 57 | `domkirken.v1.*` | west front: brick tower, clock, portal, copper spire; nave wings + stair turret |
| Grand Hotel | ✅ v1 | 96 × 47 | `grand.v1.*` | white facade, mansard with green dormers, corner turret, clock tower + copper cupola; grey annex right. No flags |
| Postgirobygget | ✅ v1 | 69 × 111 | `postgiro.v1.*` | two bronze/glass slabs, 32.4 m wide each (103 m / 111 m) + glazed core just below the left one; window bands stop at the same height on both, glass above; no signs |
| Oslostil title logo | ⬜ | | `assets/ui/title-logo.png` | redo: smoother, same pixel size as the sprites (measure from the displayed logo), synthwave/80s neon, «Oslostil», sun in the middle, Munch + Holmenkollen silhouettes instead of palm trees |

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
| Burning trams, embers | ✅ in game | chaos | `assets/vehicles/hires/tram-burning.png` (+ `.json` with flame/smoke anchors) from `tools/vehicles/burning_tram.py`: the new light-blue 3-section tram, damaged (blown-out windows, soot, hanging door, torn roof box), darkened in game, 4 per 760 px at parallax 0.35, tilted |
| Fire and smoke sprites | ✅ in game | chaos | `assets/sprites/fire.png` + `.json` from `tools/sprites/fire.py`: pixel-art flames big 20×30 and small 12×18 (8 frames, 12 fps), smoke puff 16×16 (8 frames) |
| Burning buses | ⬜ | chaos | |
| Ground strip and beat line | — | all | |
| Eplehuset | ⬜ | (new) | idea: tram crashes into it |
| Entur logo billboard | ⬜ | (new) | idea: pixelated logo on a building or station |
| Tokyoslo street: Rådhuset, Stortinget, Slottet, Universitetet, Nationaltheatret with pagoda roofs, lanterns, neon signs, TOKYOSLO billboard | 🟡 kept (v1) | Tokyoslo (stage 4 from 1:42.0, stages 5–7) | `assets/backgrounds/tokyoslo-buildings.png` (902 × 150, transparent, bottom row on `GROUND`) from `tools/backgrounds/tokyoslo.py`; first draft, kept for comparison: set `TOKYO_VERSION = 1` in `scenes.ts` |
| Level 4 street, classic British-style Oslo | ✅ in game | map, bar 42 → 1:42.0 | `assets/backgrounds/oslo-classic-buildings.png` (1203 × 150) from `tools/backgrounds/karljohan.py`: Rådhuset, Stortinget, Slottet, Universitetet, Nationaltheatret and tall townhouses; dark, detail high up, quiet bottom 40 px |
| Tokyoslo street v2 | ✅ in game | map after 1:42.0, chaos, boss | `assets/backgrounds/tokyoslo-v2-buildings.png`, same script and the same layout as the classic street, so the buildings swap style in place at 1:42.0 |
| Tokyoslo far skyline | 🟡 draft | Tokyoslo | `assets/backgrounds/tokyoslo-far.png` (640 × 150, tiles horizontally, parallax 0.15), same script; to be made full level width |
