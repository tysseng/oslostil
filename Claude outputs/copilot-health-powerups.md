# Copilot task: health power-ups

The art is in `assets/sprites/powerups.png` + `powerups-light.png` + `powerups.json` (from `tools/sprites/powerups.py`):
- one row per power-up, 4 frames each, 32 × 32 cells, bottom-centred
- `powerups.json` gives `{name: {row, frames, fps, w, h, hearts}}`; `w × h` is the hitbox
- `powerups-light.png` is a glow on the same grid, one per frame; draw it with `'screen'` in front, like the lamp lights

The power-ups are drawn somewhat larger than life, about 13–21 px against the girls' 30 px, so they read clearly. Don't scale them.

| Type | Part of the song | Hearts | Animation |
|---|---|---|---|
| `cocoa` | Sandvika: intro to level 2 (bars 1–33) | +1 | steam curls, 6 fps |
| `neon_heart` | Neon Oslo, level 3 (bars 34–41) | +1 | pulses, 8 fps, pink glow |
| `bun` | British Oslo, level 4 until the colour change (`COLOR_T`) | +1 | sparkle, 6 fps |
| `nigiri` | Tokyoslo, after `COLOR_T` until the boss (rare) | +2 | sparkle, 6 fps |
| `bubble_tea` | Tokyoslo, after `COLOR_T` until the boss | +1 | pearls drift, sparkle, 6 fps |

Behaviour:
- **New pickup kinds.** Each is a pickup like `ticket`/`coin` (`pickup: true`, own speed 0). The y comes from the level event, about 20–40 px above the ground, so they need a jump. Bob ±2 px on a sine (`sin(t·4)`).
- **Collecting:**
  - Heal by `hearts`, capped at `PLAYER_MAX_HP`.
  - Show a floating «+1 ♥» / «+2 ♥» award (reuse `award`).
  - Make a short white flash on the player.
  - Play a sound sample if you like.
  - At full health, still collect it, but give 200 points instead of healing.
- **Neon heart bonus:** if it's collected within the PERFECT window of a beat, heal to full instead of +1.
- **Rarity:** 1–2 per part. Put them where they cost something: high, after a hard pattern, or right before a dense wave. Don't put any in the boss fight.
- **Editor and dev panel:** add the four types to the editor palette (icon = frame 0) and load `powerups.json` generically, like props/lamps, so new power-ups need no code.

Done when: each part of the song has its own health pickup (Tokyoslo has two: bubble tea is the common one, nigiri the rare +2), they heal correctly, and `tsc --noEmit -p .` passes.
