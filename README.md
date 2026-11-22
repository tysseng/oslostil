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

## Dev mode

Toggle it with the key left of «1» (§ on a Nordic Mac keyboard, ` on US layouts), in every build. It is on by default in `pnpm dev` and the dev build. It shows:

- a seek slider that jumps the song and the game to any point, with the time and bar number;
- jump buttons for the story beats (Verse 1, Ninja, Farge, Boss …);
- time marks: press **T** while playing to note the current song time, which is handy for timing lyrics and events by ear;
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
| P / Esc | pause |
| M | soundtrack on/off (starts off; sound effects always play) |
| `[` `]` | nudge the audio/visual sync ±50 ms (saved in the browser) |
| § / ` | dev mode on/off |
| T | mark the current time (dev mode) |

## Layout

```
index.html                 page shell
src/main.ts                entry: wiring, frame loop, resume-after-reload
src/config.ts              screen size, tempo, bar grid, seeded RNG
src/timeline.ts            song sections, lyric timings, banners, ninja/colour-change moments, boss timing
src/schedule.ts            enemy types and the beat-synced spawn schedule
src/state.ts               game state types
src/game.ts                rules: physics, combat, scoring, keyboard
src/audio.ts               song playback (the master clock) and sound effects
src/render/draw.ts         canvas primitives
src/render/sprites.ts      girls, Automat Victoria and enemies (sprite sheets), boss
src/render/scenes.ts       backgrounds
src/render/screens.ts      game frame + HUD, title, pause and win screens
src/ui/subtitles.ts        HTML lyric layer over the canvas
src/ui/devpanel.ts         dev mode panel
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
