# Art brief: how art is made for Oslo-stil

This is the handover for anyone (human or AI) making art for the game. Read it fully before drawing anything. It holds the style rules Joakim has given so far; follow them even when a reference photo shows something different.

## The game in one paragraph

**Oslo-stil** is a side-scrolling rhythm game and music video in the browser, built around the song «Oslostil» (122 BPM, late-80s freestyle).

- **The story:** two girls, Victoria and her friend, and the ticket machine «Automat Victoria» run from Sandvika stasjon through a glitching neon Oslo. They become ninjas and finish with a boss fight against Kaos-trikken.
- **The screen:** 320 × 180 pixels, scaled up with hard pixel edges. A girl is about 30 px tall.
- **The code:** TypeScript + Vite + Canvas 2D in `src/`, served with `pnpm dev`.

## Who owns what

| Area | Owner | Notes |
|---|---|---|
| `assets/` (sprites, vehicles, audio) | art | |
| `tools/sprites/`, `tools/vehicles/` | art | the generators that make the art |
| `ASSETS.md` | art | keep the status tables current |
| `ART_BRIEF.md` | art | add new rules here when Joakim gives them |
| `src/`, `index.html`, config files, `README.md` | code | the art side never edits these |
| `inspiration/` | Joakim | reference photos; read only |

The two sides meet in `ASSETS.md`:
- The code side adds rows to **Requests** with a file name, size and frame layout.
- The art side delivers the file and ticks the row off.

When a PNG in `assets/` changes, the running dev server reloads it straight away, with no code change.

## Style rules (from Joakim's feedback)

### Everywhere

1. **No real company marks.** No Vy, Ruter, Flytoget, Sporveien or similar logos, and no «#» Ruter mark. Our own «VT» mark was also dropped because it doesn't scale. Vehicles carry **no logos at all**.
2. **Side views only.** The front of a vehicle is never seen head-on, though a sloping or slanted nose is fine in profile.
3. **Cartoon look:** clean shapes, a dark outline (`#151a22`) and simple two- or three-tone shading. Every detail should survive shrinking.
4. **Vehicles in the game use the hi-res masters for now** (`tools/vehicles/game_hd.py`), because Joakim found the pixel versions not good enough. When pixel versions are made later, they are **redrawn, never just scaled**. Shapes are re-rasterised on the pixel grid with no blending, details get fixed pixel sizes, and outlines are exactly 1 px. See `tools/vehicles/pixel_trains.py`.
   - `tools/vehicles/pixelate.py` is a plain downscale. Use it for quick previews only, never for game sprites.

### Vehicles

5. **Wheels:**
   - **Buses:** wheels are drawn **in front of** the body, sitting in dark wheel arches.
   - **Trains, subways and trams:** wheel sets (bogies) are drawn **behind** the body.
6. **Doors** must never overlap a wheel or wheel arch, and **windows** must never sit behind a door or overlap each other. The generators check this with `check_clear`; keep using it.
7. **No pantographs** on trains or trams for now, because they didn't look good.
8. **Destination signs** with amber text are fine, for example «31 SANDVIKA» and «17 SINSEN».

### Vehicle-specific fixes

| Vehicle | Rule |
|---|---|
| New subway | **Steeply** slanted front and back in **body colour**, with no black cab end (see `inspiration/vehicles/subway new/tbane7.JPG`). The dark window band stops before the cab. All windows, cab windows included, are lit warm yellow from inside (`lit_window`). |
| Old subway | Square ends, not a curved roof start or end. Window frames are black, not white. Blue window panels fill the space right up to the doors, and the single cab-end windows have blue panels too. These are **single-carriage units**: no gangways or connections between the cars. Windows, including those in the doors, are lit warm yellow like the new subway. |
| Articulated bus | The body extends about 2.5 m behind the rear wheel. |
| Old bus | Dropped. |

### Enemies and pickups

- **Ticket:** a classic **yellow tear-off ticket**, almost one colour, with rounded notches on both sides and a perforation line. It's not a modern paper ticket with a red band and barcode.
- **Glitch blob:** loose pink and cyan 2 × 2 pixel squares that jump around, with no outline and no face, like the first version.
- **Size:** all enemies are a bit bigger and clearer than the original rectangles.

### Ticket machines

Automat Victoria and the platform machines are seen from the front. They have **plain blue edges and no white side light strip**: that strip is only visible from the side.

### Characters (the girls)

9. **No headbands.**
10. **Before ninja mode** (1:40) they look like normal girls, with nothing martial-arts about them. Victoria is blonde with a ponytail, an indigo jacket with a pink zip, light jeans and a teal backpack. Her friend has brown hair, a cream jacket and a purple scarf.
11. **Ninja look:** hood and mask with the ponytail sticking out, coloured sash and scarf, a katana on the back and wraps.
12. **Rich colour:** use varied colours and shading. Flat, simplistic sprites were rejected.

## Technical contract

### Scale

- **Hi-res masters:** about **50 SVG units per metre**. PNGs are rendered at 2×, so 100 px per metre. The ground or rail line is `y = H = 262`.
- **Background vehicles in the game:** **8 game px per metre**. The canvas has 4 canvas pixels per game pixel, so the HD images are 32 px per metre. A local train is about 42 game px tall.
- **Foreground:** the girls' scale is about 19 px per metre, though they are stylised and not to scale.

### Files

- **Hi-res vehicles:** `assets/vehicles/hires/<name>.svg` plus `.png`, with transparent backgrounds.
- **Game sprites:** `assets/sprites/<name>.png` with transparent backgrounds, using only the design's own colours (no blended edge pixels).

### Sprite sheets for characters

- **Grid:** fixed-size frames with no padding between them.
- **The girls:** 24 × 32 frames, 10 columns × 2 rows. Row 0 is normal clothes, row 1 is ninja.
- **Columns:** `idle0 idle1 run0 run1 run2 run3 jumpUp jumpDown slide attack`.
- **Alignment:** feet on the bottom row, body centred on x = 12.
- **Changing the layout** is a code change as well. Add a request note in `ASSETS.md` so the code side follows.

### Vehicle sprites

- **One image per vehicle**, for example a whole 3-car train.
- **Orientation:** nose or front on the left for the first car.
- **Alignment:** wheel bottoms on the last row.

## Tools

You need Python 3 with Pillow, plus Playwright with Chromium for the SVG → PNG renders. In the cloud workspace these are already installed. On a Mac:

```sh
pip install pillow playwright && python -m playwright install chromium
```

| Command | Makes |
|---|---|
| `python3 tools/vehicles/trains.py` | green local train, tomato soup, airport express |
| `python3 tools/vehicles/subways.py` | new and old subway |
| `python3 tools/vehicles/road.py` | red bus, articulated bus and green 3-axle bus |
| `python3 tools/vehicles/trams.py` | new light-blue tram |
| `python3 tools/vehicles/game_hd.py` | in-game HD images `train-green-hd.png`, `train-tomato-hd.png` (used now) |
| `python3 tools/vehicles/pixel_trains.py` | game sprites `train-green.png`, `train-tomato.png` (pixel redraw) |
| `python3 tools/vehicles/pixelate.py --ppm 8` | quick downscaled previews only |
| `python3 tools/sprites/enemies.py` | enemy/obstacle/pickup sheet + JSON (rows, frames, fps, visible size) |
| `python3 tools/sprites/automat.py` | Automat Victoria sheet (7 frames of 24 × 32; the last is the plain platform machine) |
| `python3 tools/sprites/girls.py` | the girls' sheets (**overwrites** any hand edits to the PNGs) |

All generators run from the repo root and write into `assets/`.

**Shared helpers** live in `tools/vehicles/common.py`: `Svg`, `rect`, `window`, `wheel`, `bogie`, `bellows`, `check_clear` and `render`.

**Pattern for a new vehicle type:**
1. Copy the closest existing function.
2. Lay out doors and windows explicitly in hi-res units.
3. Call `check_clear` for doors against windows and wheel arches.
4. Draw wheels behind the body, or in front for buses.
5. Add the file to the generator's `__main__` call to `render`.

## Working loop

1. **Look at the photos** in `inspiration/…`. `.avif`, `.webp` and `.HEIC` can be converted with ffmpeg; make a contact sheet to see them.
2. **Build the hi-res master,** render it, and look at the PNG yourself before showing anyone.
3. **Show Joakim a preview image** on a light background. Expect concrete feedback, apply it, and add any new rule to this file.
4. **Only when the code side asks for a sprite,** redraw it as pixel art at the requested scale. Use `pixel_trains.py` as the model, and put the pixel tool next to it, for example `pixel_buses.py`.
5. **Update `ASSETS.md`:** set the status and fill in the file name and size.

## Where things stand (22 Nov 2026)

- **Hi-res masters done:** green local train, tomato soup, airport express, red bus, articulated bus, green 3-axle bus, new tram, new subway and old subway.
- **In the game:** the two girls (sprite sheets), Automat Victoria (sprite sheet) and the two local trains. The trains are pixel sprites in the Sandvika stasjon background, running alongside the walking platform with their wheels hidden behind its edge.
- **Not started:**
  - vehicles: tram SL79, old tram, Italian tram (photos in `inspiration/vehicles/`);
  - characters: the Kaos-trikken boss, and the effects in `ASSETS.md`.
- **Enemies, obstacles, pickups and projectiles:** made as pixel sprites in `assets/sprites/enemies.png` + `enemies.json` (`tools/sprites/enemies.py`; 32 × 32 bottom-centred cells). Joakim asked for them bigger and clearer than the old rectangles, especially the ticket. Wiring them in is the code side's job. The tram obstacle is not in the sheet.
- **Ideas from `IDEAS.md`** that need art:
  - Eplehuset with a tram crashing into it (`inspiration/eplehusetkrasj*.jpg`);
  - a pixelated Entur logo billboard (this is Joakim's own company, so his explicit wish overrides rule 1 here);
  - tickets as ammo, shown at the top of the screen.
