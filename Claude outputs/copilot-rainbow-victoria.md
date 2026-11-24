# Copilot task: Automat Victoria goes rainbow in the glitch level

## What should happen

In level 2 «TEKST-TIL-TALE GLITCH» (section `pre1`, bars 26–33, `barT(26)` → `barT(34)`), Automat Victoria breaks loose:

1. **Take-off (bar 26, about 1 beat):** she shoots up from her normal follow spot behind the player (`s.mx`, `GROUND - victoriaLift(t)`), rises and flies **up past the player** to the upper right of the player.
2. **Rubber band (bars 26–33):** she moves freely around the upper part of the screen as if tied to the player by an elastic band. Use a damped spring, not a lerp: she has her own velocity, is pulled towards an anchor point relative to the player, overshoots, swings and lags behind when the player moves. Feel: excited, bouncy, a bit out of control.
   - Anchor: `(p.x + 20, p.y - 55)`, plus a wandering offset so she doesn't just hang there, e.g. `20·sin(t·1.7)` in x and `12·sin(t·2.3 + 1)` in y.
   - Spring: `a = k·(anchor − pos) − c·vel` with roughly k = 28, c = 4.5 (tune to taste). Add a small kick on every beat (`beatPhase`), e.g. a random ±60 px/s impulse, so she «hakker» on the beat.
   - Rest length about 20 px: inside that distance, no pull.
   - Clamp her inside the screen (x 14 … W − 14, y 36 … GROUND − 20) with a soft bounce.
   - She is purely visual: no collisions, she can't be hit and isn't a platform.
3. **Rainbow ribbon:** while she flies, she trails a stepped pixel rainbow (sprites below) along the path she has flown.
4. **Landing (bar 34, «INN I SPILLET: OSLO NEON»):** over about 1 s she switches back to her normal sprite, the ribbon shrinks away from the tail end, and she flies back to her usual follow position and height (`p.x − 46`, `GROUND − victoriaLift(t)`) with the existing bobbing. After that, everything is as today.

Her mood, talking and cheering logic stays as is outside this window. Her `deathFlight` (tram hit) can't happen in level 2; skip the rainbow mode if `s.deathFlight.machine` is set.

## Sprites (already in the repo, from `tools/sprites/rainbow.py`; sizes in `assets/sprites/rainbow.json`)

| File | Layout | Use |
|---|---|---|
| `assets/sprites/automat-rainbow.png` | 4 frames of 28 × 32 in one row: `fly0 fly1 glitch0 glitch1`. Base centre at (14, 32) | Victoria while flying. Alternate `fly0`/`fly1` at 6 fps. On each beat, show `glitch0`, then `glitch1`, for one frame each (≈ 80 ms) for the pink/cyan split. Mirror horizontally when she flies left (`vel.x < −20`). |
| `assets/sprites/rainbow-tail.png` | 4 cells of 6 × 14: `seg0 seg1 fade0 fade1`. Band centre at y = 7 | The ribbon (see below) |
| `assets/sprites/rainbow-tail-light.png` | 18 × 26, centre (9, 13) | A soft glow per segment, drawn with `globalCompositeOperation = 'screen'` **before** the ribbon and before Victoria, so it doesn't wash over them |
| `assets/sprites/rainbow-sparkle.png` | 4 frames of 7 × 7, centre (3, 3), 12 fps | Sparkles left behind along the ribbon |

### Drawing the ribbon

- Every frame, record her position into a path history, including when she stands still. Keep about 1.2 s of history, or a path length of max 150 px.
- Walk back along the path from her **tail anchor**, which is the cell point (8, 17) of the fly sprite: about 6 px behind her centre and 15 px above her base. Mirror it when she is mirrored. Place a segment every 6 px of **path length** (not of time), so the ribbon keeps an even density at any speed.
- Draw each segment at its point with **integer** coordinates, `seg` top-left = `(round(x) − 3, round(y) − 7)`. Don't rotate the segments: the stepped look comes from drawing them upright.
- Alternate `seg0`/`seg1` along the chain (`(index + parity) % 2`), and flip `parity` on every beat. That gives the classic stepped wave that pulses with the song.
- Use `fade0` and `fade1` for the last two links at the tail end.
- Draw order: glow (screen), then ribbon segments from the tail end to her, then Victoria, then sparkles.
- **Sparkles:** every beat, drop 1–2 sparkles at random points along the ribbon. They drift left with the scroll (`− speed·dt`), play their 4 frames once (12 fps) and disappear.
- **Shrinking at the end:** when she lands at bar 34, cut the history from the tail end so the ribbon shortens to 0 over 0.6 s.

## Where in the code

- **Movement:** `src/game.ts`, around the companion follow code (`s.mx += (p.x - 46 - s.mx) * …`, line ≈ 328). Add rainbow state to `state.ts`: position, velocity, path history, sparkles, and a `rainbow` blend 0…1 for the take-off and landing. When `rainbow > 0`, the companion position used everywhere (`companions` in game.ts ≈ 314 and the snapshot ≈ 485) must be the flying position, not `s.mx`/`victoriaLift`.
- **Drawing:** `src/render/screens.ts` line ≈ 52 calls `drawMachine(...)` for the companion; in the rainbow window, call a new `drawRainbowMachine(...)` in `src/render/sprites.ts` instead. Load the new PNGs and `rainbow.json` there, like `automat.png`/`AUTOMAT_FRAMES`.
- **Timing:** use the existing helpers `barT`, `beatPhase` and `sectionAt` from `timeline.ts`/`config.ts`. Start = `barT(26)`, end = `barT(34)`. Put both in constants, e.g. `RAINBOW_T0`/`RAINBOW_T1` in `timeline.ts`.
- **Pixel rules:** draw sprites at integer positions, unscaled, with `imageSmoothingEnabled = false` (as for the other sprites). 1 sprite px = 1 game px.

## Done when

- At bar 26 she visibly rises past the player and then swings around above the player on the elastic band, with a rainbow that follows her actual path and steps on the beat.
- Player movement (←/→, jumps) makes her lag, swing and overshoot.
- At bar 34 she lands back in her normal spot and looks exactly as before, with no rainbow left on screen.
- `tsc --noEmit -p .` passes and the editor/dev panel still works.
