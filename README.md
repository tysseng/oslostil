# oslostil
A game based music video for a 80s freestyle hit

**OSLO-STIL** is a side-scrolling rhythm game in the browser, built around the song «Oslostil» (122 BPM, E minor). Victoria, her friend and the ticket machine «Automat Victoria» run from Sandvika stasjon through a glitching, neon Oslo. Halfway through they turn into ninjas, and the game ends with a boss fight against Kaos-trikken. Everything is synced to the song clock.

TypeScript + [Vite](https://vite.dev), managed with [pnpm](https://pnpm.io) (`corepack enable` picks the pinned version). No game framework: Canvas 2D at 320×180 and the Web Audio API.

## Art and code

Art and game code are worked on separately:

- **`ART_BRIEF.md`:** style rules, tools, scale and file contract for everything in `assets/` and `tools/`.
- **`ASSETS.md`:** what has been converted, plus the **Requests** table where the code side asks for new assets.
- **`CODE_BRIEF.md`:** architecture, timing system, story beats, rules and open tasks for the game code.

The code side only touches `src/` and the config files.

## Develop

```sh
pnpm install
pnpm dev           # http://localhost:5173 – reloads instantly when you save
```

After a code change the page reloads and comes back **paused at the same point in the song**. Press P to continue (the browser needs a key press before it plays sound).

```sh
pnpm typecheck     # tsc --noEmit
```

## Build

```sh
pnpm build
```

This typechecks and writes two self-contained single files, with the JS, CSS and song inlined. They work offline and straight from disk:

| File | Dev mode at start |
|---|---|
| `dist/dev/index.html` | on |
| `dist/release/index.html` | off |

You can also build just one with `pnpm build:dev` or `pnpm build:release`. `pnpm preview` serves the release build.

## Play online (GitHub Pages)

The game is published at **https://tysseng.github.io/oslostil/** (the dev build, with the dev panel on, is at `/dev/`).

- `.github/workflows/pages.yml` builds both single-file builds and deploys them on every push to `main` (or by hand: Actions → «Deploy to GitHub Pages» → Run workflow).
- One-time setup: in the repo on GitHub, **Settings → Pages → Build and deployment → Source: GitHub Actions**. Pages needs a public repo on a free plan.
- Everything (code, sprites, the song) is inlined in one `index.html`, so no base path or asset setup is needed. Only the Press Start 2P font is loaded from Google Fonts.

## Dev mode

The panel and its shortcuts are available only in `pnpm dev` and the dev build, not in the release build. It starts visible; press **1** to toggle it. It shows:

- a seek slider that jumps the song and the game to any point, with the time and bar number;
- jump buttons for the story beats (Verse 1, Ninja, Farge, Boss …);
- time marks: press **2** while playing, paused or editing to note the current song time (with the panel enabled), which is handy for timing lyrics and events by ear;
- a small DEV tag in the HUD.

## Controls

| Key | Action |
|---|---|
| Enter | start / play again |
| Space / ↑ | jump (double jump) |
| ↓ | slide (or fast fall in the air) |
| X | hit |
| C | throw a ticket, or a shuriken in ninja mode. Every throw uses a ticket: collect them at Sandvika stasjon. |
| ← → | move |
| P / Esc | pause; P or Enter resumes, Esc returns to the intro |
| M | soundtrack on/off (starts off; sound effects always play) |
| 1 | toggle dev panel (dev builds only) |
| 2 | mark the current time with the dev panel enabled (dev builds only) |
| 3 / 4 | nudge the audio/visual sync -/+50 ms, saved in the browser (dev builds only) |
| 5 | toggle clean pause without dimming or pause text; keeps subtitles visible (dev builds only) |

The startup prompt reads “Trykk enter for å aktivere tekst-til-tale.” The win summary shows your leaderboard place, or “NEW HIGHSCORE!” for first. After seven seconds (or Enter), qualifying top-ten runs automatically enter three initials, saved with Enter. Initials entry shows placement without repeating the announcement; tied scores follow existing runs. Non-qualifying runs go directly to the list. All ten places are shown, with `---` / `------` for unplayed slots, and no placement announcement above the list. The game returns to startup automatically seven seconds after submission or viewing a non-qualifying result, without a return message or button. Initials entry has no timeout; storage failures are shown on screen.

Initials start as **AAA**, with the first letter selected and flashing between its letter and `_`. Enter initials by typing, or use **↑ / ↓** to cycle A–Z and **← / →** to move between the three slots. **Enter** saves. Entry uses an arcade control, not a browser login/form input. Both screens retain the startup frame position and use canvas-scaled typography.

Landing on a pigeon or drone bounces you upward without damage; it falls and splashes on the ground. Landing on a suitcase squashes it and bounces you safely. Each stomp awards 100 base points, with the usual combo and PERFECT bonuses. Sliding into a suitcase launches it in your slide direction. Walking into a suitcase still causes ordinary collision damage.

Moving backward uses the current scroll speed plus 80 px/s, so you can move left faster than the scenery in every section. Movement stops at the left screen edge.

At Sandvika you can land on the ticket-machine tops, walk across them, and jump off. They carry you with the platform scroll. Victoria stops being a platform when she wakes and joins the group.

Consecutive airborne stomps multiply the stomp award by ×1, ×2, ×3, and so on, including mixed suitcase/pigeon/drone chains. This stacks with combo and PERFECT bonuses. Landing on the ground or a tram roof, or taking damage, resets the bounce multiplier; sliding and ordinary attacks do not receive it.

## Level editor

Click **Level editor** on the title screen to edit the bundled layout. Scrub **Song position** to reach any part of the level; the scene stays frozen while editing.

- Drag an existing item to move it, or right-click it to delete it.
- Select a sprite in the visual palette, then click empty space to place copies. The selected tool stays active; **Move** or **Esc** stops placing. Existing items remain draggable with any tool selected.
- The **Vehicles** palette includes the neon Countach and Testarossa as harmless, non-standable scenery, with their glow rendered behind them.
- The **Backgrounds** palette includes the SHORTSH/FT dealership and the Knowit, Entur and Bekk buildings. The dealership has a walkable roof and spotlights that shine over the players; the other buildings scroll more slowly and sit behind it.
- **Play level** starts the edited level from the beginning. **Back to editor** returns to the editing position.
- Changes save automatically in this browser and are used for subsequent games, including after reload. They do not change the repository or other browsers.
- **Download level** exports the current layout as `level.json`. **Import level** opens a previously downloaded JSON layout, validates it, and asks before replacing your draft.
- To make a downloaded layout the default for everyone, replace **`src/level.json`** with that file, then rebuild/deploy. The file contains all 350 original items with their exact timings and ships bundled with both builds (no server needed). The layout is a JSON array; `[]` means an empty level.
- **Use default level** discards your browser-local draft and loads the bundled default. Use this after publishing a new default if your browser still has an older draft; existing drafts otherwise take precedence.

The editor covers enemies, pickups, hazards and rideable trams, not background scenery, companions or the scripted boss.

## Layout

```
index.html                 page shell
src/main.ts                entry: wiring, frame loop, resume-after-reload
src/config.ts              screen size, tempo, bar grid, seeded RNG
src/timeline.ts            song sections, lyric timings, banners, ninja/colour-change moments, boss timing
src/schedule.ts            enemy types and sprite metadata
src/level.ts               shared level validation and bundled-default loading
src/level.json             complete published level layout
src/state.ts               game state types
src/game.ts                rules: physics, combat, scoring, keyboard
src/audio.ts               song playback (the master clock) and sound effects
src/render/draw.ts         canvas primitives
src/render/sprites.ts      girls, Automat Victoria and enemies (sprite sheets), boss
src/render/scenes.ts       backgrounds
src/render/screens.ts      game frame + HUD, title, pause and win screens
src/ui/subtitles.ts        HTML lyric layer over the canvas
src/ui/devpanel.ts         dev mode panel
src/ui/editor.ts           level editor, item palette and browser-local layout saving
src/ui/highscores.ts       three-letter initials entry and browser-local top ten scores
assets/oslostil.mp3        the song (final mix v8, first 150 s, 128 kbps)
assets/sprites/            pixel-art sprite sheets (girls, automat, enemies.png + enemies.json)
tools/sprites/girls.py     generator for the girls' sprite sheets
tools/timing/              Whisper-based measurement of when each lyric line is sung
```

## How timing works

- **Song clock:** `songTime = audioContext.currentTime − start − outputLatency + syncOffset`. Every position in the game is a function of that clock, so nothing drifts.
- **Bar grid:** `barT(bar, step)` gives the time of any bar or 16th step (bar 1 starts at 0.038 s, one bar = 1.967 s). Enemies are scheduled to arrive exactly on beats.
- **Sections:** the backing-track sections (`SECTIONS`) drive the scene changes and enemy waves.
- **Lyric timing:** the subtitles, ninja mode (`NINJA_T`, 1:40.15) and the screen colour change (`COLOR_T`, 1:42.0) use times measured from the vocal rather than the bar grid, because Suno's phrasing doesn't follow the grid. The colour change time was set by ear.

## Sprites

The girls are sprite sheets in `assets/sprites/`. Each is 10 columns × 2 rows of 24×32 frames:

- **Rows:** normal clothes, then ninja.
- **Columns:** `idle0 idle1 run0 run1 run2 run3 jumpUp jumpDown slide attack`.
- **Alignment:** feet are on the bottom row and the body is centred on x = 12.

You can edit the PNGs directly in any pixel editor (Aseprite, Piskel …). `tools/sprites/girls.py` made the first version from ASCII parts. If you re-run it, it overwrites the PNGs.
