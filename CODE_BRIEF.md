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
7. The final hit lands on «Oslo-STIL!» at 2:27.6, then the win screen.

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
4. `src/schedule.ts`: enemy types (`TYPES`: size, height above ground, hp, own speed, pickup/solid), the enemy sprite sheet layout (`SHEET`, imported from `assets/sprites/enemies.json`; hitbox `w`/`h` come from it) and `buildSchedule()`. Every enemy is scheduled to arrive at the player's spot exactly on a beat.
5. `src/state.ts`: `GameState`, `createState()`, `enemyX(e, t)`.
6. `src/game.ts`: the rules:
   - `seek`, pause and resume, keyboard;
   - attack, throw, scoring with PERFECT on the beat, combo, dying and respawning (`die`, `respawn`);
   - the triple-throw power-up from the terminal;
   - the friend's assist from chorus 1, boss damage, the final hit and the win.
7. `src/audio.ts`: song playback is the **master clock** (`time() = ctx.currentTime − t0 − outputLatency + syncOffset`), plus synth sound effects. The song plays through its own `music` gain node, so **M** mutes only the soundtrack (`toggleMusic`, `musicMuted`, starts muted); the effects always play. The muted song keeps running as the clock.
8. `src/main.ts`: wiring, the frame loop, dev-mode key, resize/fit, resume-after-reload, the `window.__oslo` test hook.
9. `src/render/`:
   - **`draw.ts`:** `RES = 4` canvas px per game px. `R()` snaps to game pixels; also `text`, `flash`, `resetTransform`, `drawHiRes` and `loadImage`/`ready`.
   - **`sprites.ts`:** the girls', Automat Victoria's and the enemies' sprite sheets, `drawPlatformMachine`, `drawEnemy` (sheet cell bottom-centred at `(x, GROUND − e.y)`, frame `floor(t × fps) % frames`), `drawTram` (HD image or placeholder, x = nose) and `drawBoss` (still rectangles).
   - **`scenes.ts`:** backgrounds per scene, plus the Sandvika trains (`TRAIN_RUNS`, `stoppingTrain`) and the platform machines.
   - **`screens.ts`:** the game frame (scene, flashes, enemies, companions, HUD, banners, chorus calls), Victoria's wake animation and moods, and the pause, title and win screens.
10. `src/ui/`: `subtitles.ts` (HTML layer over the canvas, sharp text) and `devpanel.ts`.
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
- **Vehicles use smooth hi-res images for now** (`*-hd.png`, `drawHiRes`). Joakim didn't like the pixel versions; new vehicle sprites come later.
- **Sprites** are sheets of fixed-size cells, bottom-aligned (feet, base or wheels on the bottom row) and horizontally centred.
- **Banners:** only the newest one is shown, so a new beat replaces the previous one at once.
- **Lyric subtitles** are an HTML overlay, not canvas. They use white text with a black outline and no background box.

### Dev mode

- **Toggle:** the key left of «1» (`§` or `` ` ``). It's on by default in `pnpm dev` and the dev build.
- **What it shows:** a seek slider and jump buttons (they seek the audio *and* the game state), and **T** to mark the current time. Joakim uses T to time things by ear.
- **Testing hook:** `window.__oslo.seek(t)`, `window.__oslo.snap(t, lead = 1.5)` and `window.__oslo.game` (state, `pause()`, `resume()`).
  - To check a moment: `snap(t)` seeks to `t − lead`, simulates to `t` at 60 fps with no input, pauses, draws the frame without the pause overlay and returns a PNG data URL. It works even when the tab is hidden (where `requestAnimationFrame` stops, so seek + wait doesn't advance). The canvas keeps that frame until the next animation frame.
  - Without input the player gets hit, so she may be blinking (invisible) in a snap.
  - Audio only starts after a key press (browser rule); `seek` handles a suspended context.

## Story beats already built

| Time | What happens | Where in code |
|---|---|---|
| 0:00 → 0:17.7 (intro) | Bus terminal before the station: lower roof with no signs; three buses wait at the stops and a red bus drives through right to left behind them | `drawBuses`, `TERMINAL` in `scenes.ts` |
| 0:17.7 (verse 1) | Sandvika stasjon's higher canopy scrolls in from the right, with «OSLO S» boards hanging under every section | `STATION`, `STATION_START` |
| 0:17 → 0:24.2 | Green local train overtakes the girls, brakes and stops with its nose just before the three ticket machines, then stands still and slides off left with the station | `stoppingTrain` |
| 0:21.7 | Three ticket machines roll in on the platform; the left one is Victoria, with a «VICTORIA» label | `MACHINES_T`, `drawPlatformMachine` |
| ≈0:26.4 | The girls reach her: she gets a face and arms, hops 3 times, shoots up past floating height and settles, then follows. Banner «AUTOMAT VICTORIA BLIR MED!» | `VICTORIA_WAKE_T`, `victoriaLift`, `machineMood` |
| after that | She talks on lyrics about her («automat», «hun …»), cheers on chorus «OSLOSTIL!» calls and the final hit, and cheers on the win screen | `machineMood` |
| 0:50 | Tomato soup again | `TRAIN_RUNS` |
| 1:40.15 | Ninja mode, white flash, girls switch to ninja sprites | `NINJA_T` |
| 1:42.0 | Screen changes colour (map → red), red flash, no text | `COLOR_T` |
| bar 70 → 76 | Boss Kaos-trikken, final hit 2:27.6, win screen 2.2 s later | `BOSS_AT`, `FINAL_HIT`, `WIN_AT` |

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
   - **Tram (22 Nov, Joakim):** full length, a moving platform. Constants in `schedule.ts` (`TRAM_LEN` 242, `TRAM_ROOF` 31, `TRAM_OWN` 40, `TRAM_EDGE`, `TRAM_WARN`); the rules are `Game.tram()`.
     - The tram's x is its **nose** (left end), which reaches the player's spot on the beat. It spawns `TRAM_WARN` s early so the blinking «!» shows before it enters.
     - **Side hit:** if the player is below roof height when the body reaches her, she dies at once (`die()`), unless she is invincible, in which case she passes through.
     - **Riding:** landing on the roof sets `p.ride`; the tram carries her left at its relative speed down to `TRAM_EDGE`, she can jump and slide there, and when the tail passes she falls to the ground.
     - **Art:** `drawTram` uses `assets/sprites/tram-hd.png` through `import.meta.glob`, so a missing file is fine and falls back to a placeholder of the same size. Requested as Requests #2 in `ASSETS.md`.
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
- `die()`: `s.down = DEATH_TIME` (0.55 s), hearts 0, combo reset, −1000 points (pop-up), continue counted, burst particles, `sfx('die')` (falling arpeggio). While `s.down > 0` she is not drawn, has no control and can't collide.
- `respawn()`: x = max(x, `PX`), feet at `DROP_Y` (100 px up), 3 hearts, `s.inv = s.respawn = RESPAWN_FLASH` (1.2 s), `sfx('respawn')` (rising sparkle). Normal physics land her on the ground or a tram roof. `screens.ts` draws her as a white silhouette every other 1/8 s while `s.respawn > 0` (`Pose.white`, `whiteSheet` in `sprites.ts`).
- With no input, a tram death at the beat lands her on that tram's roof about 1.2 s later.

## Gotchas

- **`pnpm typecheck` in the Linux VM:** TypeScript 7 is a native binary and `node_modules` only has the macOS one. From the Linux side, install `typescript@7.0.2` + `@typescript/typescript-linux-arm64@7.0.2` in a scratch folder outside the repo and run that `tsc --noEmit -p .` in the repo.
- **JSON imports** need `resolveJsonModule` (set in `tsconfig.json`).

- **Saving into Joakim's folder from another environment:**
  - verify the file on disk actually changed (compare checksums);
  - a re-used staging path has delivered a stale copy before;
  - check `git status` before and after.
- **The song file** is `assets/oslostil.mp3`: the final mix trimmed to 150 s.
- **`outputLatency`** is subtracted in the clock. `[` and `]` nudge sync by ±50 ms, saved per browser.
- **Testing at a specific moment:** seek a bit before it, because `seek` resets the game state (score, enemies) by design.
