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
4. **Trains and buses in the game use the hi-res masters for now** (`tools/vehicles/game_hd.py`), because Joakim found the pixel versions not good enough. When pixel versions are made later, they are **redrawn, never just scaled**. Shapes are re-rasterised on the pixel grid with no blending, details get fixed pixel sizes, and outlines are exactly 1 px. See `tools/vehicles/pixel_trains.py`. The approved Neon Oslo cars are separate, hand-drawn pixel sprites; see their style below.
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

### Enemy ninjas and the seagull (Joakim, 23 Nov)

- **Enemy ninjas are the girls' height (30 px)** and must look **clearly different from the girls in ninja mode** (navy, pink or purple scarf, ponytail): different colours, headgear and silhouettes, no ponytail. Three kinds: Shadow (ash grey, black hood, red headband, yellow eyes), Oni (crimson, white horned mask, katana), Wanderer (teal, straw kasa hat, ochre scarf, short sword). They face left.
- **Elaborate animation:** idle ×2, run ×6, crouch, jump up, jump down, attack ×3 (`tools/sprites/ninjas.py`, 40 × 32 cells, layout in `ninjas.json`).
- **Seagull** replaces the drone: bigger than the pigeon, about drone size in body, white with grey wings and black tips, an 8-frame flap.

### Thugs and zombie passengers (Joakim, 23 Nov)

- **Before ninja mode** the enemies are street thugs, not ninjas: a classic thug, a punk and a tagger. The tagger has a spray mode for the subway: pink spray, slightly transparent.
- **The passengers** (they replace the ticket bot and its label) are ordinary people in normal clothes with **red glowing eyes**, like zombies or robots: an adult woman with yellow hair, a small child in a red cap, an old man with a rolled-up newspaper, and a teenager smoking a joint.
- All are drawn by `tools/sprites/people.py` on the ninjas' skeleton (40 × 32 cells, facing left).

### Tokyoslo tram (Joakim, 23 Nov)

Green and cream like the Japanese references. **Identical cars chained** with a coupler (no bellows), **vertical end walls**, only small rounded corners, **single doors** split cream/green like the body. Two cars match `tram-new` in length and roof height. No pantograph.

### Celebration sprites (ending)

Front-facing frames for both girls in ninja outfits (turn from side to front, idle, a 4-frame wave, a jump: takeoff, rise, fall, land) and for Automat Victoria (her cheer frames raise both arms, so a one-arm wave and a squash/stretch jump were added). Separate sheets; existing frames and indices are unchanged.

### Ticket machines

Automat Victoria and the platform machines are seen from the front. They have **plain blue edges and no white side light strip**: that strip is only visible from the side.

### Characters (the girls)

9. **No headbands.**
10. **Before ninja mode** (1:40) they look like normal girls, with nothing martial-arts about them. Victoria is blonde with a ponytail, an indigo jacket with a pink zip, light jeans and a teal backpack. Her friend has brown hair, a cream jacket and a purple scarf.
11. **Ninja look:** hood and mask with the ponytail sticking out, coloured sash and scarf, a katana on the back and wraps.
12. **Rich colour:** use varied colours and shading. Flat, simplistic sprites were rejected.

### Street props (from Joakim, 23 Nov 2026)

- **Front view only**, flat 2D, in the girls' style: dark outlines tinted per material (not one flat black), 3–4 tone shading, rich colour.
- **Hand anti-aliasing:** curves and corners get hand-placed in-between tones (opaque pixels), never a scaled-down or blurred image. This replaces the «no blended edge pixels» rule for props only.
- **The kiosk is at dusk** (Joakim, 23 Nov): darker outside, lit windows and name plate, and a light cone each side of the centre. The light is in `props-light.png` (same grid as `props.png`), made like the lamp light.
- **Tokyoslo props** (`tools/sprites/tokyo_props.py`, drawn into the same props sheet): lacquer red, black and gold, paper lanterns, neon in pink and cyan with invented glyphs (no real words). Props can now animate (one sheet column per frame, `frames`/`fps` in the JSON), and `top` 0 means not standable.
- **Trees** (Joakim, 23 Nov): leaf trees in the dark for classic Oslo (one bare, two in leaf), cherry blossom trees for Tokyoslo.
- **Heights relative to a girl (30 px):** round trash bin ≈ 55 % (17 px), recycling bin > girl (36 px), phone booth between recycling and kiosk (44 px), kiosk ≈ 2 × girl (61 px).
- No real marks: the kiosk is a generic «KIOSK» (after narvesen 3, colours from the other kiosk photos); the textile bin is plain red with dots for writing, no Red Cross logo.

### Glitch level (Joakim, 24 Nov)

- In level 2 Automat Victoria goes rainbow (Joakim, 24 Nov): she flies free on a rubber band tied to the player, trailing a stepped six-band pixel rainbow with sparkles, and returns to normal at Neon Oslo. Our own design: plain rainbow ribbon, no cat or other borrowed character.
- Level 2 (Sandvika, glitching) gets animated glitched copies of the ticket machines to stand on (`tools/sprites/glitch_props.py`, drawn into the props sheet). Built from the real «plain» machine frame so they match; glitch = slipping row slices, pink `#ff2bd6` / cyan `#2bf0ff` channel split, screen static, «A-A-A», magenta/black missing-texture checker. Solid pixels only; the base and the top row never move, so `top` stays valid in every frame.

### Neon Oslo (synthwave)

- The scene is late-80s synthwave: saturated pink is the main colour, cyan is secondary, with yellow and dark-purple accents.
- Use dark surfaces, bright neon edges and high-shine highlights. The background has a striped sun, a far skyline, well-known Oslo landmarks on middle layers and scenery/props in the foreground.
- The main atmosphere reference is `inspiration/synthwave/sw3.JPG`; use the other `sw*.jpg`, `sw*.jpeg` and `sw*.avif` references for supporting palette and composition.
- **Approved neon asset style:** use near-black opaque surfaces with bright pink linework and darker pink shades for form and hand-placed pixel antialiasing. Use cyan for selective accents and separate pink/cyan glow behind the sharp artwork, not baked into it. Keep silhouettes recognisable from their references.
- Neon buildings should be mostly black, with pink toward the top and cyan toward the bottom. Keep the pixel artwork crisp while using glow and softened corners to give the neon a soft appearance.
- The approved SHORTSH/FT dealership is in `assets/backgrounds/neon-dealership.png` (198 × 61), with a 16 px padded exterior glow and an aligned, separate spotlight-beam image. The beams must be drawn over the players; see `ASSETS.md` for the layer contract.
- The approved Knowit highrise is in `assets/backgrounds/neon-highrise-1.png` (117 × 76), with a separate 16 px padded glow. It sits behind the dealership and scrolls more slowly.
- The approved Entur highrise is in `assets/backgrounds/neon-highrise-2.png` (108 × 85 including its sign), with a separate 16 px padded glow. It shares the Knowit highrise's background layer and speed.
- The approved Countach and Testarossa are examples in `assets/sprites/neon-countach*.png` and `neon-testarossa*.png`, generated by `python3 tools/sprites/neon_cars_preview.py`. Each has a separate pink/cyan light image padded by 16 px on every side; draw it behind the sprite at `(x - 16, y - 16)`. Use `inspiration/cars/silhouettes/` for profiles and `inspiration/cars/synthwave/` for line style.
- The cars have dark windows and are shortened horizontally for a cartoon-like game scale while keeping their height and round wheels. Their solid dark tires have cyan lower outlines and no hubcaps; cyan lines along the lower body stop short of the ends and tires. The Countach's rear underside slopes upward; the Testarossa's underside is flat and black.

### Power-ups (Joakim, 24 Nov)

- Pickups must be large enough to read clearly, so they are NOT in proportion to the girls, but not huge either: 66 % of the first version, ≈ 13–21 px against 30. One health item per part: hot chocolate (Sandvika), neon heart (Neon Oslo), skolebolle (British Oslo), salmon nigiri and bubble tea (Tokyoslo). No brands.

### Landmarks (Joakim, 24 Nov)

- Flat elevations: flat colour, no outlines, 3–4 tones per material, windows and details on their own layers so silhouettes, night versions and lit windows can be derived.
- No flags on any building. No inscriptions (blank plaques).
- Follow the reference photos closely; when a shape is iconic (ski jump, opera) trace it rather than invent it.
- Approved landmarks are frozen as `<name>.v1.*`; never overwrite a versioned file.

## Technical contract

### Scale

- **Hi-res masters:** about **50 SVG units per metre**. PNGs are rendered at 2×, so 100 px per metre. The ground or rail line is `y = H = 262`.
- **Background vehicles in the game:** **8 game px per metre**. The canvas has 4 canvas pixels per game pixel, so the HD images are 32 px per metre. A local train is about 42 game px tall.
- **Foreground:** the girls' scale is about 19 px per metre, though they are stylised and not to scale.

### Files

- **Hi-res vehicles:** `assets/vehicles/hires/<name>.svg` plus `.png`, with transparent backgrounds.
- **Hi-res landmarks:** `assets/landmarks/hires/<name>.svg` plus `.png` (approved: `<name>.v1.*`), drawn in metres, 10 SVG px/m, PNG 20 px/m, ground at the bottom, transparent background. Made by `python3 tools/landmarks/landmarks.py`.
- **Game sprites:** `assets/sprites/<name>.png` with transparent backgrounds, using only the design's own colours (no blended edge pixels).

### Props (`assets/sprites/props.png` + `props.json`)

- **Made by** `python3 tools/sprites/props.py`. Drawn 1:1 on the pixel grid at girl scale (≈ 19 px per metre); the game draws them unscaled.
- **Cells:** 112 × 64, one prop per row, one column per frame; each prop bottom-centred (base on the bottom row, centre on x = 56).
- **JSON:** `{name: {row, frames, fps, w, h, top}}`. `w × h` is the visible size; `top` is the walkable top surface above the base, in px.
- **Jumps:** a single jump reaches about 50 px, a double about 85 px. Keep `top` ≤ 45 for one-jump props; the kiosk (61) needs a double jump.

### Street lamps (`assets/sprites/lamps.png` + `lamps-light.png` + `lamps.json`)

- **Made by** `python3 tools/sprites/lamps.py` (imports the drawing helpers from `props.py`). Same scale and style as the props, front view.
- **Two sheets with the same grid:** the lamps (draw *behind* the characters) and their light (semi-transparent cones, head glow and a ground pool; draw *in front* at the same position). The light is a **smooth gradient with softly blurred edges, no dither or bands** (Joakim, 23 Nov): roadside and subway lamps cast downward cones; the round globe shines radially, strongest downwards; the vintage lantern shines sideways and down from its yellow panes, and its roof stops the light going up.
- **Cells:** 96 × 80, one lamp per row. The **pole** (not the bounding box) is centred on x = 48, base on the bottom row.
- **JSON:** `{name: {row, frames, fps, w, h, top, top_span, heads}}`. `top_span` = `[dx0, dx1]` of the walkable lamp head relative to the pole; `heads` = `[[dx, height], …]` light sources relative to the pole base.
- **Heights (girl 30):** roadside 62 (≈ 2 ×), round 58, vintage 46 (≈ phone booth), subway 74. All tops need a double jump.

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
| `python3 tools/sprites/props.py` | street props sheet + JSON: trash bin, recycling bin, phone booth, kiosk |
| `python3 tools/sprites/lamps.py` | street lamps + separate light sheet: roadside (1 and 2 arms), round globe, vintage lantern, subway |
| `python3 tools/sprites/ninjas.py` | enemy ninjas sheet + JSON (three kinds, 14 frames each) |
| `python3 tools/sprites/people.py` | thugs (+ tagger spray row) and zombie passengers, sheets + JSON |
| `python3 tools/sprites/trees.py` | trees: three night trees for classic Oslo, two cherry trees for Tokyoslo |
| `python3 tools/sprites/celebrate.py` | celebration sheets for the ending (girls in ninja outfits + Automat), from the girls' and Automat's own parts and palettes; never touches victoria.png/friend.png/automat.png |
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
