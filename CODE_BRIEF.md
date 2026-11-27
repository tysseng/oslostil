# Code brief: how the Oslo-stil game is built

This is the handover for whoever (human or AI) writes the game code. Read it fully, then read the files in **«Read first»** before changing anything. Art is made in a separate session; see `ART_BRIEF.md` and `ASSETS.md`.

## What the game is

**Oslo-stil** is a side-scrolling rhythm game and music video in the browser, built around Joakim's late-80s Miami freestyle song «Oslostil» (122 BPM, E minor, 2:27.6).

**The story follows the lyrics:**
1. Two girls, Victoria and her friend, are at Sandvika stasjon.
2. The ticket machine «Automat Victoria» wakes up and joins them.
3. They are pulled into a glitching neon «coin-op» Oslo.
4. They turn into ninjas at 1:40 («Plutselig er vi ninjaer»).
5. The screen changes colour at 1:42.
6. The fighting intensifies through the second chorus, with a boss (Kaos-trikken) at the end.
7. The final hit lands on «Oslo-STIL!» at 2:27.6, immediately braking into the celebration, then the win summary.

**How it plays:** auto-run with keyboard actions. The text is bilingual, Norwegian and English.

## Stack and commands

- **Code:** TypeScript (strict) + Vite 8 + Canvas 2D + Web Audio. No game framework.
- **Package manager:** pnpm, pinned in `package.json` (`corepack enable`; `mise.toml` also provides pnpm).

| Command | What it does |
|---|---|
| `pnpm install` | install dependencies |
| `pnpm dev` | dev server at http://localhost:5173 with instant reload; after a reload the game resumes **paused** at the same song time, and P continues |
| `pnpm typecheck` | `tsc --noEmit`; keep it clean |
| `pnpm build` | typecheck, then `dist/dev/index.html` (dev mode on at start) and `dist/release/index.html` (dev mode off): single self-contained files with JS, CSS, images and the song inlined |

## Who owns what

| Area | Owner |
|---|---|
| `src/`, `index.html`, `vite.config.ts`, `tsconfig.json`, `package.json`, `README.md`, `CODE_BRIEF.md` | **code** |
| `assets/`, `tools/`, `ART_BRIEF.md`, the status tables in `ASSETS.md` | art (never edit these from the code side) |
| `inspiration/`, `IDEAS.md` | Joakim |

**When the code needs a new asset:** add a row to **Requests** in `ASSETS.md`, with file name, size and frame layout. When the art side changes a PNG, Vite reloads it automatically.

## Read first, in this order

1. `README.md`: overview, controls, layout, build.
2. `src/config.ts`: screen size (320 × 180 game px), tempo, bar grid (`barT`, `barAt`), `FINAL_HIT`, the seeded RNG.
3. `src/timeline.ts`: **the song's story beats**:
   - `SECTIONS` (scenes and scroll speeds per bar range);
   - measured lyric times (`LYRICS_RAW`), `NINJA_T`, `COLOR_T` and `BANNERS`;
   - the Sandvika ticket machines and Victoria's wake-up (`MACHINES_T`, `machineCenter`, `VICTORIA_WAKE_T`, `WAKE_HOPS`, `WAKE_RISE`);
   - the boss timing and the dev `JUMPS`.
4. `src/schedule.ts`: enemy types (`TYPES`: size, height above ground, hp, own speed, pickup/solid) and the enemy sprite sheet layout (`SHEET`, imported from `assets/sprites/enemies.json`; hitbox `w`/`h` come from it). `src/level.json` contains the complete default schedule, materialized from the original generator without changing its timings or order.
5. `src/state.ts`: `GameState`, `createState()`, `enemyX(e, t)`.
6. `src/game.ts`: the rules:
   - `seek`, pause and resume, keyboard;
   - attack, throw, scoring with PERFECT on the beat, combo, dying and respawning (`die`, `respawn`);
   - the triple-throw power-up from the terminal;
   - the friend's assist from chorus 1, boss damage, the final hit and the win.
7. `src/audio.ts`: song playback is the **master clock** (`time() = ctx.currentTime − t0 − outputLatency + syncOffset`), plus synth sound effects. The song plays through its own `music` gain node, so **M** toggles only the soundtrack (`toggleMusic`, `musicMuted`, starts muted); the title screen shows its current state. The effects always play, and the muted song keeps running as the clock.
8. `src/main.ts`: wiring, the frame loop, dev-mode key, resize/fit, resume-after-reload, the `window.__oslo` test hook.
9. `src/render/`:
   - **`draw.ts`:** `RES = 4` canvas px per game px. `R()` snaps to game pixels; also `text`, `flash`, `resetTransform`, `drawHiRes` and `loadImage`/`ready`.
   - **`sprites.ts`:** the girls', Automat Victoria's and the enemies' sprite sheets, `drawPlatformMachine`, `drawEnemy` (sheet cell bottom-centred at `(x, GROUND − e.y)`, frame `floor(t × fps) % frames`), `drawTram` (HD image or placeholder, x = nose) and `drawBoss` (still rectangles).
   - **`scenes.ts`:** backgrounds per scene, plus the Sandvika trains (`TRAIN_RUNS`, `stoppingTrain`) and the platform machines.
   - **`screens.ts`:** the game frame (scene, flashes, enemies, companions, HUD, banners, chorus calls), Victoria's wake animation and moods, and the pause, title and win screens.
10. `src/ui/`: `subtitles.ts` (HTML layer over the canvas, sharp text), `devpanel.ts` and `editor.ts` (frozen playfield, visual palette, dragging, deletion and browser-local layout saving).
11. `ASSETS.md`: every visual and its status. `ART_BRIEF.md`: the art rules, which also matter when you place art in the game.

## Key concepts

### Time is everything

- **No game clock:** every position is a function of song time `t`.
  - Enemies: `x = 80 + (arrival − t) × relativeSpeed`.
  - The background scroll `bgx` is integrated from the section speeds (`scrollAt` in `game.ts`, which `seek` uses).
- **Bar grid:** bar 1 starts at 0.038 s, one bar is 1.967 s, and `barT(bar, sixteenthStep)` gives the time of any step.
- **The vocals don't follow the bar grid.** That's why lyrics, ninja mode and the colour change use **measured** times instead:
  - Whisper over sliding windows of the vocal stem (`tools/timing/whisper_windows.py`);
  - or set by ear: `COLOR_T = 102.0` came from Joakim.
- **Known mismatch, left as it is:** `SECTIONS` follow the *backing track*. The vocal pre-chorus 2 starts at 1:44 and chorus 2 at 1:54.5, earlier than the backing sections (bar 58 = 1:52, bar 66 = 2:08). Scenes and banners for those parts follow the backing. Joakim said the scene changes feel right; ask before moving them.

### Rendering

- **Two resolutions:** the canvas is 1280 × 720 (320 × 180 game px × `RES` 4).
  - Rectangles and pixel sprites are drawn in game px with no smoothing, so they stay blocky.
  - Text and hi-res images keep their detail.
- **Vehicles use smooth hi-res images for now.** Trains and buses are drawn straight from the masters in `assets/vehicles/hires/` (100 px per metre) with `drawVehicle` in `scenes.ts`, which trims them at load. Sizes: trains `TRAIN_PPM` 10 game px per metre, waiting buses `BUS_PPM` 13.2, the driving bus 80 % of that (it's further back). Joakim didn't like the pixel versions; new vehicle sprites come later. The bidirectional tram obstacle (`drawTram` in `sprites.ts`) uses `tram-new.png` unmirrored at `TRAM_PPM` 10, preserving the original door and sign positions. `meta`, `drawVehicle` and `HIRES_PPM` live in `draw.ts`.
- **Sprites** are sheets of fixed-size cells, bottom-aligned (feet, base or wheels on the bottom row) and horizontally centred.
- **Tram deaths:** the player tumbles backward; each companion launches independently when the tram's nose crosses it (swept between frames, including the player's impact frame), never from overlap with the middle. Struck companions remain hidden until respawn; unstruck companions stay visible. `deathFlight` holds visual-only motion; other deaths keep the ordinary delay.
- **Boss:** enters from the right over one bar, then patrols between x=192 and x=256 on a four-bar cycle. Projectile hits deal 2 damage and use bounded body coordinates at that position. The unlabelled health bar follows the head's per-frame offsets (mirrored from `tools/sprites/boss.py` in `BOSS_HEAD_OFFSETS`), with a tram-blue frame and dark empty track behind the shrinking red fill.
- **Flying Automat Victoria** has two flickering downward exhaust flames, enabled after her wake-up hops and on the hovering title/summary poses.
- **Banners:** only the newest one is shown, so a new beat replaces the previous one at once.
- **Stomps and slides:** sliding moves the player at 220 px/s for 0.15 s, then decelerates to a stop over 0.45 s; it goes right by default or left if left is held when starting. Platform carry remains separate, and jumping cancels the slide. Descending onto a pigeon/drone/suitcase top bounces the player without damage and awards 100 base points plus normal bonuses. Birds/drones fall and splash; suitcases flatten for 0.6 seconds. Sliding into a suitcase awards a kill and launches it in the slide direction; walking retains ordinary damage. `GameState.knocked` holds these non-colliding sprite effects separately from scheduled enemies.
- **Bounce chains:** `bounceChain` counts consecutive airborne stomps across all three types and multiplies their awards by 1, 2, 3, etc., stacking with combo/PERFECT. Ground/tram landing and damage reset it. Ground landing is resolved after stomp crossings so fast falls do not lose valid stomps.
- **Lyric subtitles** are an HTML overlay, not canvas. They use white text with a black outline and no background box.

### Dev mode

- **Clean pause:** **5** freezes gameplay/audio without the pause overlay or text, retaining subtitles. Press **5**, **P**, **Escape** or **Enter** to resume. From ordinary pause, **5** switches to clean pause. Both the shortcut and clean rendering flag are gated to dev builds.
- **Pause screen:** P or Escape pauses; P or Enter resumes, and Escape returns to the intro.
- **Toggle:** **1**. The panel and shortcuts are available only in `pnpm dev` and the dev build, gated by `__DEV_MODE_DEFAULT__`; the release build cannot activate them.
- **What it shows:** a seek slider and jump buttons (they seek the audio *and* the game state), and **2** to mark the current time while playing, paused or editing with the panel enabled. **3 / 4** adjust sync -/+50 ms. `DevPanel.keyDown` handles these before gameplay/editor input and UI button focus checks; text/file inputs and modifier combinations are ignored.
- **Testing hook:** `window.__oslo.seek(t)`, `window.__oslo.snap(t, lead = 1.5)` and `window.__oslo.game` (state, `pause()`, `resume()`).
  - To check a moment: `snap(t)` seeks to `t − lead`, simulates to `t` at 60 fps with no input, pauses, draws the frame without the pause overlay and returns a PNG data URL. It works even when the tab is hidden (where `requestAnimationFrame` stops, so seek + wait doesn't advance). The canvas keeps that frame until the next animation frame.
  - Without input the player gets hit, so she may be blinking (invisible) in a snap.
  - Audio only starts after a key press (browser rule); `seek` handles a suspended context.

### Level editor

- The Vehicles palette includes the neon Countach and Testarossa. Both are harmless, non-standable scenery, with separate pink/cyan glow rendered behind their sprites in the editor and game. They can be positioned, saved and imported like other level items; the default level is unchanged.
- The Backgrounds palette includes the SHORTSH/FT dealership (`neon_dealership`): harmless surface scenery at 75% foreground speed, drawn behind foreground items. Its roof is a one-way moving platform; its separate beam layer is aligned to the building and rendered over the characters. It is not in the default level.
- The tram uses the cyan `tram-neon.png` variant while the current scene is Neon Oslo; its normal blue and Tokyoslo appearances remain unchanged elsewhere.
- The Knowit, Entur and Bekk buildings (`neon_highrise_1`, `neon_highrise_2` and `neon_highrise_3`) are also in Backgrounds: harmless, non-standable surface scenery at 60% foreground speed, behind the dealership, with separate padded glows. They are not in the default level.
- Valkyrien entrance uses a native 64x64 transparent bitmap, with 17-pixel concrete side walls, green columns, a five-pixel VALKYRIEN sign, T roundel and a dark iron-fence back without visible steps or handrails. The slightly darkened facade has a round lamp above each pole, with a separate padded 192x192 soft-glow bitmap and four times the original glow radius. The sign leaves 38 pixels of headroom. Generate both layers with `tools/sprites/valkyrien_entrance.py`.
- Entry uses a 140-pixel descending staircase beginning at 86.8345 seconds (0.9655 seconds earlier). Down/S starts a one-second walking descent; companions follow the same slope at their own x positions. Surface ground masks the party until they reach the underground chamber. Existing platform items, train arrival and exit timing are unchanged.
- Station wall artwork measures 80 pixels from ceiling to platform. Its 128-pixel panels alternate three embossed sections (16 pixels tall) with a blank sign panel; every third embossed panel has blinded sections. The upper vault grades from near-black to warm light grey with subtle mottling and a horizontal border above the panels. Three bitmap VALKYRIE PLASS signs, with thick black lettering on cream enamel, occupy evenly spaced blank panels. Walls, signs, stairs and posters share station scrolling without relative parallax drift.
- `tools/sprites/valkyrien_station.py` generates the wall/sign bitmaps, three separate original period-style posters (blue cigarette pack, orange soda and coffee; no readable copy), and a 46-pixel white coin-operated weighing machine. Posters and the scale are editable Tunnel assets, saved in the level JSON and restricted to the underground platform; posters render on the back wall behind the train.
- Each station sign has three green spotlights with a separate soft beam bitmap. Ceiling fixtures are native 40x20 pixel fluorescent lamps suspended from the original ceiling anchors; tubes sit 17 pixels lower than the old strips. Their bitmap light starts across the full tube width, widens into a soft rhombus and fades below the platform; grouped flicker and stair occlusion are retained.
- Each poster also has a separate `_worn` Tunnel asset, preserving the clean originals: tobacco has ragged edge tears, soda has a folded upper-right corner, and coffee has a folded lower-left corner plus a small right-edge tear. Missing paper is transparent so the wall shows through.
- Hanging ceiling lamps and their full-width beams scroll 8% faster than the wall to suggest a nearer plane; wall-mounted sign lights remain fixed to the panels. Landing on a vintage scale's footstand (6 pixels above its base), not its dial, bounces the player and rings a prominent synthesized bell; each scale awards 200 points once per run (subsequent landings still ring).
- The exit pavilion is a native 104x64 side-view bitmap with matching concrete, dark green-framed windows and a vertically seamed green metal roof starting at entrance-sign height, without a visible gable end. Generate with `tools/sprites/valkyrien_house.py`. Party clearance and Automat Victoria's hover recovery use its wider right edge.
- Pavilion concrete has embossed square panels; a VALKYRIEN GRILL roof sign has three downward spotlights in a separate glow bitmap. Surface-route players render in front and can land on the moving roof (48 pixels high). Returning underground players render behind the facade but remain visible through translucent window panes; the opaque background and windowed foreground are separate bitmap layers.
- During stair ascent, the entire party stays behind the surface ground strip, including beneath the exit pavilion; only above-ground portions inside the pavilion can show through its windows.

- Automat Victoria follows the stair slope without hovering, then smoothly rises to her normal bobbing height over 100 pixels after her full sprite clears the exit house. The surface foreground hides the ascent until all companions are through.

- All three ghosts are available in the Tunnel palette: Ghost, Bedsheet ghost (32x40), and Conductor ghost (24x29, redrawn at approximately 60% of its original size, not resized). They share pursuit and single-hit behavior, with separate animated light sheets. Generated sprite/light frames face left by default; only chasing mirrors them in code.
- Friend and Automat Victoria follow the stair slope at their own horizontal positions and stay hidden above the station ceiling until their full sprites clear the foreground exit house, even after the player exits.

- Ghosts use original eight-frame pixel artwork with a waving tail (`ghost.png`). Matching `ghost-light.png` frames are blurred from each sprite's alpha, not generated at runtime; sprite and glow share frame selection, positioning and chase mirroring. Regenerate both with `python3 tools/sprites/ghost.py` (Pillow).

- O toggles all asset outlines in the editor without affecting scene rendering, lighting or item editing; held-key repeats do not retrigger the toggle.

- The upper world's teal bottom strip fades to black from y=150 to y=180; everything surrounding the subway below that strip is black, including the entry/exit foreground masks.

- The original platform/train timeline remains anchored at 87.8 seconds; the added entrance staircase extends 140 pixels earlier without moving the existing platform layout.

- Each ghost gives up permanently after its first successful contact hit, stops pursuing, drifts away with the station and cannot deal another contact hit. Touching an invincible player does not consume its hit.
- Other pursuing ghosts continue after a hit, including during the player's respawn delay; giving up is tracked separately for each ghost.
- Ghost sprite/glow frames face left initially and flip right when pursuing; giving up restores the initial direction. Editor previews match the initial direction.

- Valkyrien stairs retain a solid concrete body with a horizontal lower edge and a right wall extending to the station end. Their silhouette blocks subway headlight/rear beams and circular glows; window lights use the same rendered stair/wall alpha mask.

- The old subway uses the modern subway's yellow lit-window interiors. Ceiling cones extend 24 pixels beyond the chamber height so their soft bottom falloff still illuminates the floor.

- Underground jumps stop at the Valkyrien ceiling using the full 32-pixel sprite height. Victoria's floating/bobbing position and the following girl's delayed position share that ceiling limit; chute entry and automatic stair/house exit remain unrestricted by it.

- Subway window lights follow the exact passenger and door glass positions and the train's bumps. Cached yellow rounded-rectangle bitmaps lighten the station mask, with a four-pixel cubic falloff outside the windows. Foreground asset sprite alpha masks both the glow and its darkness cutout in gameplay and the editor, preserving transparent gaps.

- The subway's rear beam uses a red-tinted copy of the soft cone bitmap, retaining its alpha falloff while coloring the entire beam, not only the circular glow.

- The Valkyrien subway has subtle paired vertical track-joint bumps, a pale forward headlight and red rear light with soft falloff that reduce the darkness mask. Ceiling fixture brightness and cone strength flicker together on independently phased, deterministic cycles.
- Flicker cycles are spaced 2.2+ seconds apart, alternating double/triple pulses with mixed dimming and complete blackouts. Consecutive groups of three fixtures share a cycle, starting at the leftmost group at the station entrance and progressing right at 0.85-second intervals. Temporary cones start at narrow points and fade at their top, sides and bottom; train bumps peak at 1.3 pixels. Circular train-light glow is centered on each end of the car with a 32-pixel radius.

- Valkyrien wall joints, columns and signage scroll at 85% of the station speed; ceiling lights and their cones stay anchored to the station. Underground placement clamps item bases above the platform, reserving downward bob clearance for pickups so grounded objects can still be dragged sideways.

- Ceiling lights start one 70-pixel tile later and omit the final fixture. The last remaining cone excludes the foreground stair silhouette, illuminating behind it. Stairs and their balustrade stop at the platform's six-pixel light edge instead of extending into its dark underside.

- The editor's **Valkyrien** button jumps to its 1:26.83 entrance and pans down to the station view.

- Valkyrien has an 82%-opaque black foreground mask over the station, including trains, objects and characters. Cached temporary RGBA cone bitmaps erase portions of that mask with `destination-out`, with a 24-pixel edge falloff. Ceiling lights are spaced 140 pixels apart; their 100-pixel cones do not overlap, leaving dark gaps. Gameplay and editor share the effect; editor selection outlines and the HUD remain clear. Replace the generated cone bitmap in `ceilingLightCone()` when final artwork is available.

- Valkyrien's `subway-old` train enters from the station's left when the entrance center reaches x=20 in the playfield. It continues through the whole station at a constant 360 px/s relative to the station, without braking or stopping; it renders behind platform items/characters in gameplay and the editor.

- Assets can be placed/dragged below the surface only when their bounds fit inside Valkyrien's chamber before the stairs. Invalid placement is blocked without a message and leaves the item unchanged. Underground items use negative `y`, validated on import, and move with the station at 145 px/s; they interact only with underground players. Surface placement is unchanged.

- The editor canvas extends to both viewport edges at the normal editor scale. A centered pink frame marks the actual 320-pixel play area; assets outside it remain visible and editable, and pointer coordinates account for the extended view. The time slider layout is unchanged.
- The widened view renders one continuous scene at the original song time and scroll distance. Background layers extend using their own repeat periods/parallax; trains, buses and scripted encounters retain their single gameplay positions rather than repeating at the play-area borders.

- The upper Valkyrien stairs and balustrade are clipped below the surface ground. During ascent, the surface scene overlays the party at the top of the stairs; the foreground house hides their arrival until they emerge to its right.
- Valkyrien's ceiling sits 15 pixels below the 30-pixel surface strip. The underground camera shows 15 pixels of moving surface scenery below the HUD, the complete surface strip, the 15-pixel dark gap, the station chamber and its unchanged 26-pixel bottom. Camera offset and physical station depth are independent. Stairs continue behind the ceiling band; ascent and the subsequent walk through the house lock jumping until the player's full sprite clears its right side.
- Underground space outside the concrete chamber fades vertically from the surface strip's teal (`#0a2e33`) to black at the station bottom. The ceiling's foreground mask uses the same world-aligned gradient, avoiding seams during stair ascent.
- The final-hit explosion particles, screen shake and half-second white flash continue rendering and advancing during the immediate celebration transition, synchronized to the final musical hit.

- **Valkyrien prototype:** a pixel-art surface entrance reaches the player at 1:26.83. Press Down/S while standing in front to walk down the entrance stairs; jumping/landing does not activate the route. The surface ground hides the descent above the underground ceiling. The world pans upward while the HUD stays fixed and a strip of moving surface scenery remains visible. The party follows the descending slope; an offscreen player runs back to x=80 after landing. The optional surface route remains unchanged if skipped. The station is 1928.375 pixels long including entrance/end margins and the new 140-pixel entry stairs; the original platform layout and exit timing are preserved. Concrete stairs near 1:39 lead into a foreground pavilion with translucent windows, then back to the surface. Stair balustrades hide the lower half of the party and extend solidly to the underground ground. `valkyrien.ts` owns route geometry/state/landing and `render/valkyrien.ts` draws the station and entrance, also visible in the editor. Seeking/restarting resets the route; surface enemies cannot interact with underground players.
- During ordinary gameplay, a player completely outside the camera view for two seconds is returned with her companions, without a death penalty. Scripted station routes and death animations are exempt.
- **Tunnel ghosts:** editor-placeable underground enemies in the first palette category, Tunnel, with two hit points and ordinary contact damage. They bob at their authored position until passed, then slow from station scroll speed into a capped 65 px/s pursuit, staying inside the chamber. A soft green glow illuminates the wall and foreground elements. `ghosts.ts` owns pursuit; `assets/sprites/ghost.json` defines the dedicated sprite/glow sheet metadata. Editor previews stay at authored positions; saved levels contain no runtime chase state.

- The palette groups items under Enemies, Power-ups, Tickets & coins, Lights, Props & platforms, Trees, Backgrounds, Vehicles and Hazards. Move stays above the groups, and selecting any item clears selection across all categories.
- The editor fits within the viewport: the level canvas uses at most half the viewport height, and the palette scrolls independently below the fixed action/time controls. Help is collapsible so it does not push the level map out of view.
- Left/right arrows scrub the editor song position by 0.1 seconds per keypress; holding an arrow repeats. Time stays within the song-position slider bounds, and scrubbing is disabled during item dragging.
- Scrolling over the level canvas also scrubs time (down/right advances, up/left rewinds), with normalized wheel/trackpad deltas. Scrolling over the asset picker still scrolls only the picker; Ctrl/Command wheel gestures retain browser zoom.
- Up/down arrows pan the editor vertically in 10-pixel steps; Shift + wheel over the canvas pans smoothly instead of scrubbing time. The independent camera ranges from the surface to Valkyrien, persists while scrubbing, and pointer hit-testing/dragging uses the panned world coordinates.

- Health pickups are generated from `powerups.json` and use their own 32-pixel sprite/glow sheets, shared bobbing and editor previews. Cocoa, neon heart, bun and bubble tea restore 1 HP; nigiri restores 2, capped at 10. A PERFECT neon heart restores full health. Full-health pickups give 200 points instead; collection never adds ammo, tickets, kills or combo. Pickups flash the player white and show the actual healing amount. Sparse default placements follow each scene and stop before the boss.

- `board_broken` uses `board-broken.json` for its changing platform top and matching glow frame. It glitches until the player lands on it, then crumbles at twice the original speed (impact after half a beat). Runtime-only `crumbledAt` resets when seeking or restarting; legacy `fallAt` fields are ignored on import. Riders follow the collapsing top, then receive a -120 vy hop and 0.1-second, 2-pixel shake. Bystanders are pushed safely aside without damage.
- `blob_hop` lands on each beat (twice for `hop: "double"`), only adds 40 px/s while airborne, and uses a shared integrated motion curve anchored at arrival for gameplay and editor placement. Variants are normal/low/high/double. Squashed frames 0-1 do no side damage; stomps, melee and projectiles trigger the once-only `blob_pop` burst. The default glitch section mixes ten hopping blobs with two static blobs and two falling boards; Sandvika has two ordinary departure boards with tickets above them.

- In bars 26–33, `rainbow.ts` simulates Automat Victoria's spring flight with a wandering anchor and beat impulses, even while the player stands still. Touching the rendered ribbon while airborne boosts the player upward at 420 px/s once per contact, with a 1.5-second cooldown between boosts and without resetting her jumps. Each boost displays a fast-expanding rainbow shockwave at the contact point, using the tail's screen-blended glow and fading over 0.4 seconds, plus a text-only `Tailstrike!` label for 0.8 seconds. A time-varying wave offsets the path-length-spaced ribbon; it shrinks for 0.6 seconds and she returns to her ordinary follow position over one second after bar 34. Debug seeks reconstruct her visual history, and tram death flight overrides rainbow mode.
- The rainbow ribbon and glow use 75% opacity; Victoria and the sprite sparkles retain full brightness. Sparkles appear on the beat and every 0.12 seconds beside the ribbon so they remain visible between beats.

- Trees move at 50-75% of their authored speed, varied by a stable per-tree `depth` (0-1, seeded for older layouts). Trees are drawn back-to-front by their actual adjusted speed, so the front tree always moves faster, even across different authored speeds. All trees stay behind the subway, props and trams in gameplay and the editor. Spawn timing and editor positioning use the same adjusted speed; saved `rel` remains unscaled, and depth survives dragging and JSON round trips.

- Pigeons and gulls use `enemyHeight` for deterministic smooth flight: two blended sine waves seeded by authored arrival time and height, at 2.8–6 radians/second for visible swoops during short screen crossings. Height varies up to 48 px above the safe base, never below 24 px off the ground. Rendering, attacks, stomps, droppings and editor bounds share the same position; defeated birds use their separate falling animation.

- Subway tagger runs in three seconds before the train stops and starts spraying one second before it stops. Shared timeline helpers drive his position and paint. Shooting him during either phase removes him and awards 300 base points with normal combo/PERFECT bonuses, once only. `taggerStoppedAt` freezes existing train-anchored paint and prevents further spraying; seek/restart resets it. He does not damage the player.

- Seagulls drop at randomized intervals while onscreen (first 0.2–0.6 seconds, then 0.45–1 second). Droppings fall under gravity, scroll with the world and leave six-second ground splats. Airborne contact or stepping in a splat deals 0.25 health with normal damage invincibility; droplets survive their gull's defeat and reset on seek/restart.

- Lamps (`roadside`, `roadside2`, `round`, `vintage`, `subway`) are single one-way platform items using `lamps.json` and aligned 96 × 80 cells in `lamps.png` / `lamps-light.png`. Players can land on their metadata-defined `top` / `top_span`, ride and jump off, without side or underside collision. Posts render with scenery, then trams, then enemies/characters. Light uses screen blending over sprites with tram bounds excluded so it remains behind trams. The editor uses the same layering and previews both sheets as one item.

- Props render behind trams and other enemies in gameplay and the editor; editor hit-testing selects the visually frontmost item.

- The palette includes `trash`, `recycling`, `phonebooth` and `kiosk` from `assets/sprites/props.png` (112 × 64 cells, geometry in `props.json`). Props are indestructible one-way platforms: descending players can stand/walk/jump on top, while sides and undersides never block or hurt them. `Player.propRide` provides scrolling carry; landing resets jumps and bounce chains. Props use the existing level JSON import/export and browser-draft paths.

- **Level editor** is available on the title screen and during play/pause. During a game it opens at the current song position; **Play level** rebuilds gameplay from the edited schedule at the editor's exact song position, rather than restarting the song. Its own song-position slider changes the frozen scene without running physics or playing audio.
- `Game.intro()` pauses audio, clears held controls and returns to the intro from any mode. **Home** works throughout the game/editor/ending screens; an **Intro** button is available outside the title screen (the editor has its own Title button).
- `Game.level` holds the editable schedule. `seek` and `start` always use it. `editor.ts` saves it under `oslostil-level-v1` in local storage and validates it on load; failures appear in the editor status.
- `level.ts` validates imported JSON and loads the complete schedule from `src/level.json` as a fresh copy. There is no runtime level generator or `null` fallback; `[]` is an empty level. Download level exports that same array format as `level.json`; replace the repository file and rebuild/deploy to publish it. Import level validates before asking to replace the draft. Browser drafts override the bundled default until Use default level discards them.
- Manual positioning stores `arr`, height `y`, and fixed relative speed `rel`, so dragging across a section boundary does not change the item's screen position. `eventSpeed`, `createEnemy` and `spawnTime` in `state.ts` are shared with gameplay; spawn order is based on entry time, not arrival time.
- Default tram movement is 20% faster than the combined section scroll and tram own speed; editor-saved explicit `rel` speeds remain unchanged.
- Trams can also be raised: rendering and ride/side-hit collision both use their edited height. Scripted scenery, companions and the boss are not editable.

### Highscores

- Seven seconds on the win screen (or Enter) advances to `highscore` mode. `Game.tickWin` uses wall-clock time; gameplay and dev shortcuts do not handle keys during initials entry.
- On the final hit, `celebrate` mode starts immediately and lasts seven seconds (Enter advances early): background scrolling brakes to a stop in 0.25 seconds, the party walks to the center in 1.8 seconds, then turns forward, waves and jumps once using `celebrate.json` and the two celebration sheets. They keep waving afterward. Gameplay/collisions are frozen; the summary's seven-second timer starts afterward.
- The win summary keeps both girls at the left edge and Automat Victoria at the right, clear of the centered results.
- `ui/highscores.ts` offers a focusable arcade letter control (no login/form input) only for top-ten runs, starting AAA and saving on Enter. Its shared `place(score)` calculation drives summary and entry placement. Only the win summary announces NEW HIGHSCORE for first place; runs outside the top ten show GAME OVER instead of placement. The leaderboard has no placement announcement. It stores scores descending under `oslostil-highscores-v1` and shows ten rows with placeholders. Ties follow existing scores; storage errors are shown explicitly.
- Entry has no timeout. Enter advances from summary to initials, saves initials to show the table, then returns from the table to intro. Held Enter never skips multiple screens, and no Enter prompts are displayed. After submission the table also returns to startup automatically after seven seconds. The win screen's existing BEST value remains separate for compatibility.

## Story beats already built

| Time | What happens | Where in code |
|---|---|---|
| 0:00 → 0:17.7 (intro) | Bus terminal before the station: lower roof with no signs; three buses wait at the stops and a red bus drives through right to left behind them | `drawBuses`, `TERMINAL` in `scenes.ts` |
| 0:17.7 (verse 1) | Sandvika stasjon's higher canopy scrolls in from the right, with «OSLO S» boards hanging under every section | `STATION`, `STATION_START` |
| 0:17 → 0:24.2 | Green local train overtakes the girls, brakes and stops with its nose just before the three ticket machines, then stands still and slides off left with the station | `stoppingTrain` |
| 0:21.7 | Three ticket machines roll in on the platform; the left one is Victoria, with a «VICTORIA» label | `MACHINES_T`, `drawPlatformMachine` |
| ≈0:26.4 | The girls reach her: she gets a face and arms, hops 3 times, shoots up past floating height and settles, then follows. Banner «AUTOMAT VICTORIA BLIR MED!» | `VICTORIA_WAKE_T`, `victoriaLift`, `machineMood` |
| after that | She talks on lyrics about her («automat», «hun …»), cheers on chorus «OSLOSTIL!» calls and the final hit, and cheers on the win screen | `machineMood` |
| 0:41 | Airport express whisks through right to left (620 px/s) | `TRAIN_RUNS` |
| 0:50 | Tomato soup | `TRAIN_RUNS` |
| 1:20.7 (level 4) | A 3-car T-bane train (`subway-new.png`) arrives from the left, brakes and stops, then drifts off with the city | `drawSubway`, `SUBWAY` in `scenes.ts` |
| 1:20.7 → 1:42.0 | Level 4 street: classic British-style Oslo (`oslo-classic-buildings.png`) | `drawClassicOslo` in `scenes.ts` |
| 1:42.0 → end | The same street swaps to Tokyoslo style in place (`tokyoslo-v2-buildings.png`, same layout and scroll anchor) plus the far skyline; also in Kollektivkaos and the boss. `TOKYO_VERSION = 1` brings back the first draft | `drawTokyoslo`, `streetX` |
| 1:40.15 | Ninja mode, white flash, girls switch to ninja sprites | `NINJA_T` |
| 1:42.0 | Screen changes colour (map → red), red flash, no text | `COLOR_T` |
| bar 70 → 76 | Boss Kaos-trikken, final hit 2:27.6 immediately starts the seven-second celebration before the win summary | `BOSS_AT`, `FINAL_HIT` |

## Joakim's rules so far (gameplay and presentation)

- **Lyrics and story timing:**
  - Subtitles must match the singing; timing changes are judged by ear.
  - No headbands on the girls. They look like ordinary girls until ninja mode.
  - The player can move across the whole screen width, not just the left half.
- **Text:**
  - The title is «OSLO-STIL».
  - Banners must never overlap; only the newest is shown.
  - The colour change has no text banner.
- **Trains at Sandvika:**
  - They run alongside the walking platform. The **tops of the wheels are level with the walking surface** (`GROUND`) and the wheels are hidden behind the platform edge, because the ground strip is drawn after the trains.
- **Platform machines:** the same style as Victoria, but with no face and no arms.
- **Intro and Sandvika (`drawPlatformRoof`, `drawBuses` in `scenes.ts`, 22 Nov):**
  - the intro is a bus terminal: a lower roof (`TERMINAL`, y 84) with no signs, except that its **last section is as high as the station's** to make room for the arriving train; no train runs through the intro;
  - **buses** (`WAITING_BUSES`, `DRIVING_BUS`): green, red and green wait at the stops (they move with the roof layer), and a red bus drives through behind them from the right edge out at the left. All have their **wheel bottoms on `GROUND`** and are drawn at `BUS_PPM` 13.2 px per metre (not the trains' 8) so the doors are taller than the girls; the terminal roof is high enough to clear them;
  - Sandvika stasjon only starts with verse 1, when the green train arrives: the higher canopy (`STATION`, y 76) begins at `STATION_START`, so its first section enters from the right at bar 10;
  - «OSLO S» departure boards hang under every station section, every 84 px;
  - the buses use the hi-res masters in `assets/vehicles/hires/` directly (front on the right), trimmed at load and drawn smoothly. `drawVehicle(…, flip)` mirrors one to drive left and redraws its destination sign unmirrored (the sign is found by its amber pixels).
- **Tram:** full length; it kills the player at once if she doesn't jump onto it, she can ride it, and standing still carries her back to the left edge until she falls off as it leaves.
- **Dying:** no «INSERT COIN» overlay. Losing the last heart (or a tram hit) makes her burst and vanish, then she drops back in from above (landing on a passing tram's roof if there is one) and flashes white a few times. Own sound effects for both.
- **Text in the pixel font:** Press Start 2P lacks −, ★, ▶, ← and →. Use ASCII (`-`) or draw icons; the typographic minus showed as «?».
- **Art rules:** no company logos; vehicles are side views only. Full list in `ART_BRIEF.md`.

## Open tasks for the code side

1. **Enemy sprites: done** (22 Nov). `drawEnemy` draws `assets/sprites/enemies.png` using `SHEET` from `enemies.json`; `TYPES` `w`/`h` follow the JSON, so a regenerated sheet needs no code change unless rows are added. Heights (`y`) are unchanged and still work: standing clears pigeons, drones and fireballs; shots, suitcases, snow and fire need a jump; every pickup is reachable with one jump. **Left:** the tram's art (see below).
   - **Tram (22 Nov, Joakim):** full length, a moving platform. Constants in `schedule.ts` (`TRAM_PPM` 10, `TRAM_LEN` 305, `TRAM_ROOF` 38, `TRAM_OWN` 40, `TRAM_EDGE`, `TRAM_WARN`); the rules are `Game.tram()`.
     - The tram's x is its **nose** (left end), which reaches the player's spot on the beat. It spawns `TRAM_WARN` s early so the blinking «!» shows before it enters.
     - **Side hit:** if the player is below roof height when the body reaches her, she dies at once (`die()`), unless she is invincible, in which case she passes through.
     - **Riding:** landing on the roof sets `p.ride`; the tram carries her left at its relative speed down to `TRAM_EDGE`, she can jump and slide there, and when the tail passes she falls to the ground.
     - **Art:** the new light-blue tram, `assets/vehicles/hires/tram-new.png`.
     - **Times:** 1:09.9, 1:17.7, 1:30.5 (moved from 1:29.5, after the T-bane train), 1:45.3, 1:57.1, 2:05.0, 2:12.8.
2. **Kaos-trikken boss sprite:** request it from the art side via `ASSETS.md`.
3. **Ideas in `IDEAS.md`** (Joakim decides the order):
   - a tram crashing into Eplehuset;
   - tickets as limited ammo, shown at the top, turning into ninja stars in ninja mode;
   - an Entur logo billboard;
   - all sound effects from the ticket-machine samples.
4. **Keep `README.md` and this brief current** when the structure changes.

## Done 22 Nov: tickets as ammo (merged by the art session)

These are now in the code; kept here as the spec:

1. **Tickets are the ammo.**
   - Each collected ticket gives **one throw**; throwing (C) uses one; with none left, show «TOM! · EMPTY» and don't throw.
   - Start with a few throws, for example 3.
   - Show the ammo in the HUD as a small ticket icon plus «×N». The `ticket` sprite frame 0 works as the icon.
   - In ninja mode the thrown thing is a shuriken, but it still costs a ticket.
2. **Many more tickets, only at Sandvika stasjon** (intro and verse 1, bars 2–25), at **different heights** so you have to jump for them:
   - low rows to run through;
   - arcs that follow a jump;
   - staircases going up;
   - high pairs that need a double jump.
   - Heights are px above `GROUND`: single jump ≈ 50, double jump ≈ 85.
   - Keep them off the obstacle beats. No tickets after Sandvika.
3. **The ticket sprite is now smaller (16 × 8) and spins:** 4 frames at 8 fps, from `enemies.json`. Let each ticket spin out of step (time offset per ticket) and bob gently. The thrown ticket can be a small yellow ticket too.
4. **The Sandvika platform roof is too high.** Lower it: `ROOF.y` in `scenes.ts` from 46 to about 76. Flying things (pigeons at y 26, the highest tickets at about 70 above ground) must still pass under it or in front of it.

Where they live:

- `addTickets` in `schedule.ts`;
- `ammo` and `START_AMMO` in `state.ts`;
- `throwStar` and the pickup in `game.ts`;
- `drawEnemySprite` and the ticket spin/bob in `sprites.ts`;
- the HUD ammo and the thrown ticket in `screens.ts`;
- `ROOF.y = 76` in `scenes.ts`.

## Dying and respawning

- `hurt()` takes a heart; at 0 it calls `die()`. A tram side hit calls `die()` directly.
- `die()`: `s.down = DEATH_TIME` (0.85 s), hearts 0, combo reset, −1000 points (pop-up), continue counted, burst particles, `sfx('die')` (falling arpeggio). While `s.down > 0` she has no control and can't collide; tram deaths show the tumbling sprite before counting down the respawn delay.
- Player health starts and respawns at `PLAYER_MAX_HP` (10). The HUD uses a purple bar with a neon-pink frame and dark-purple empty track. The health bar and ticket icon are vertically centered with the HUD text. Tram side hits remain instantly fatal.
- `respawn()`: x = max(x, `PX`), feet at `DROP_Y` (100 px up), full health, `s.inv = s.respawn = RESPAWN_FLASH` (1.2 s), `sfx('respawn')` (rising sparkle). Normal physics land her on the ground or a tram roof. `screens.ts` draws her as a white silhouette every other 1/8 s while `s.respawn > 0` (`Pose.white`, `whiteSheet` in `sprites.ts`).
- With no input, a tram death at the beat lands her on that tram's roof about 1.2 s later.

## Gotchas

- **`pnpm typecheck` in the Linux VM:** TypeScript 7 is a native binary and `node_modules` only has the macOS one. From the Linux side, install `typescript@7.0.2` + `@typescript/typescript-linux-arm64@7.0.2` in a scratch folder outside the repo and run that `tsc --noEmit -p .` in the repo.
- **JSON imports** need `resolveJsonModule` (set in `tsconfig.json`).

- **Saving into Joakim's folder from another environment:**
  - verify the file on disk actually changed (compare checksums);
  - a re-used staging path has delivered a stale copy before;
  - check `git status` before and after.
- **The song file** is `assets/oslostil.mp3`: the final mix trimmed to 150 s.
- **`outputLatency`** is subtracted in the clock. **3 / 4** nudge sync by -/+50 ms in dev builds, saved per browser.
- **Testing at a specific moment:** seek a bit before it, because `seek` resets the game state (score, enemies) by design.
