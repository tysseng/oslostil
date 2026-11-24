# Copilot tasks: departure boards and the hopping glitch

The art is already in the repo. Sizes and frames are in the JSON files listed under each task. 1 sprite px = 1 game px; draw at integer positions with `imageSmoothingEnabled = false`.

---

## 1. Normal departure board (level 1, Sandvika stasjon)

`departure_board` is a new entry in `assets/sprites/props.json` (row 23, 54 × 46, `top` 45). Its amber glow is in `props-light.png`, column 0 of the same row.

- It already works as standable scenery through the generic props code (`scenery(PROPS)` in `schedule.ts`). Nothing to code except placing it.
- Place 2–3 of them along the platform in level 1. They sit at one-jump height (45), so put tickets on top and just above them.
- Draw its light like the other lit props (kiosk, ad column).

---

## 2. Broken departure board (level 2, the glitch): falls down and becomes a platform

Files:
- `assets/sprites/board-broken.png`: 10 frames of 64 × 52 in one row, bottom-centred, base on the bottom row minus the 1-px outline. Same base convention as the props.
- `assets/sprites/board-broken-light.png`: the same grid, **one glow per frame**. Draw it with `'screen'` in front, like `drawLampLight`.
- `assets/sprites/board-broken.json`:
  - `frames`: `glitch0 glitch1 glitch2 buckle0 buckle1 drop impact bounce rest0 rest1`
  - `top`: walkable height per frame, `[45, 45, 45, 38, 27, 22, 12, 16, 15, 15]`
  - `phases`:
    - `glitch`: frames 0–2, loop, 8 fps
    - `fall`: frames 3–7, play once, 12 fps (≈ 0.42 s, one beat)
    - `rest`: frames 8–9, loop, 4 fps
  - `w`: 54

Behaviour:
- **New scheduled type `board_broken`.** It scrolls with the world like a prop (own speed 0) and is solid scenery. Its walkable top is `top[currentFrame]`, not a fixed value, and the horizontal span is ±w/2.
- **States:** it arrives in the `glitch` phase. It starts `fall` at a trigger time: a new optional field `fallAt` (song seconds) in the level event, which defaults to one beat before the board reaches the player's x. Put `fallAt` on a beat, so the `impact` frame lands one beat later, on the next beat. After `fall` it loops `rest` forever.
- **Player standing on it while it falls:** she rides it down. Each frame, set her y to the board's current top while she is on it and not jumping; the existing `propRide` logic should handle this once `top` comes from the frame. On the `impact` frame, give a small screen shake (2 px, 0.1 s) and, if she is on it, a tiny hop (vy ≈ −120).
- **Player under it when it lands:** no damage. If her feet are below the board's falling bottom, push her out to the nearest side. It's a platform, not a trap.
- **Editor:** add `board_broken` to the editor palette with a `fallAt` field. Use the first frame as its icon.
- **Placement:**
  - 2–3 in level 2, e.g. one at bar 27 that falls on beat 1 of bar 28, and one at bar 30.
  - Put pigeons or hopping glitches right after them, so the low platform (top 15) is useful.
  - Put tickets high above a standing board, so the player has to be on it before it falls.

---

## 3. The hopping glitch (level 2): squash, bounce and move left on the beat

Files: `assets/sprites/enemies.png` + `enemies.json`. Two new rows, appended; the existing rows are unchanged:

| Row | Frames | fps | Notes |
|---|---|---|---|
| `blob_hop` | 8 | 16 | hitbox 16 × 14; JSON has `air: [3, 7]`, `land: 0`, `frames_per_hop: 8`. Frames: land (squashed), recover, crouch, launch (stretched), rise, apex, fall, pre-land |
| `blob_pop` | 5 | 16 | death burst, play once and remove |

Behaviour (new type `blob_hop`, or replace `blob` in level 2):
- **One hop per beat, landing exactly on the beat.** Frame index = `floor(beatPhase · 8)`, where `beatPhase` is 0 on the beat. That makes frame 0 (land) hit on the beat. Use the 16-fps value only as a fallback when the song clock isn't running.
- **Hop arc:** the sprite only changes shape; the code moves it. In the air frames (3–7), lift it along a parabola: `y = 4·H·u·(1−u)` with u going 0→1 across frames 3–7 and H ≈ 26 px. So it clears a sliding player but not a jumping one.
- **Leftward movement:** it moves left only while airborne, 40 px/s on top of the scroll during frames 3–7, and stands still on frames 0–2. It still has to reach the player's x on its scheduled `arr` beat: compute its spawn x from the average speed (scroll + 40 · 5/8).
- **Variants** (an optional `hop` field in level events):
  - `low`: H 14. Jump over it.
  - `high`: H 34. Slide or run under it while it's in the air.
  - `double`: two hops per beat, `frame = floor(beatPhase · 16) % 8`, H 18.
- **Stomp:** landing on it from above (as for pigeons and suitcases) bounces the player (vy −300) and plays `blob_pop`. Hitting it (X) or throwing at it also plays `blob_pop`. A hit on frame 0 (landing, on the beat) counts as PERFECT as usual.
- **Damage:** touching it from the side hurts as `blob` does today. It does no damage on frames 0–1 while it is squashed flat (`h` ≈ 8), so a player who walks onto it on the beat can step over it.
- **Placement:**
  - In level 2, replace most of the 12 static `blob`s with `blob_hop`. Mix `low`/`high`, so the player has to read whether to jump or slide from the hop height.
  - Keep one or two static `blob`s for contrast.

## Done when

- The broken board glitches, collapses on the beat and becomes a low platform the player can ride down and stand on. Its light follows it down.
- Glitch blobs hop left in time with the music, squash on every beat and pop when stomped or hit.
- `tsc --noEmit -p .` passes and the editor still loads.
