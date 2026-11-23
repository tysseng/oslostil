// Screen, tempo and the bar grid. Everything in the game is a function of the song clock.
export const W = 320;
export const H = 180;
export const GROUND = 150;
export const PLAYER_MAX_HP = 10;
/** x position where scheduled events "arrive" (the player's home spot). */
export const PX = 80;

export const BPM = 122;
export const BEAT = 60 / BPM;
export const BAR = 4 * BEAT;
/** Bar 1 starts this many seconds into the song file. */
export const PH = 0.038;

/** Time of a bar (1-based) plus an optional number of 16th steps. */
export const barT = (bar: number, step = 0): number => PH + (bar - 1) * BAR + (step * BEAT) / 4;
/** 1-based bar number at time t. */
export const barAt = (t: number): number => Math.floor((t - PH) / BAR) + 1;

/** The final orchestra hit on «-STIL» (2:27.6). */
export const FINAL_HIT = barT(76);
export const WIN_AT = FINAL_HIT + 2.2;

export const FONT = '"Press Start 2P", ui-monospace, monospace';

/** Small seeded PRNG (mulberry32) so the level layout is the same every run. */
export function rng(seed: number): () => number {
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
