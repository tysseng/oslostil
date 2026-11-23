// Enemy ninjas: three kinds from assets/sprites/ninjas.png (tools/sprites/ninjas.py), facing left,
// with idle, run, crouch, jump and attack frames. Their jumps are a pure function of song time,
// like everything else, so seeking and the editor show the same thing as play.
import ninjasJson from '../assets/sprites/ninjas.json';
import thugsJson from '../assets/sprites/thugs.json';

export const NINJAS = ninjasJson;
export type NinjaKind = keyof typeof ninjasJson.kinds;
export const NINJA_CELL_W = ninjasJson.cell[0], NINJA_CELL_H = ninjasJson.cell[1];
export const isNinjaKind = (kind: string): kind is NinjaKind => Object.hasOwn(NINJAS.kinds, kind);

/** Street thugs (assets/sprites/thugs.png, tools/sprites/people.py) stand in for the ninjas before ninja
 * mode. Same 40 × 32 cells and columns as the ninjas, so the same frame logic drives them; they don't jump. */
export const THUGS = thugsJson;
export type ThugKind = keyof typeof thugsJson.kinds;
export const isThugKind = (kind: string): kind is ThugKind => Object.hasOwn(THUGS.kinds, kind);
export type FighterKind = NinjaKind | ThugKind;
export const isFighter = (kind: string): kind is FighterKind => isNinjaKind(kind) || isThugKind(kind);
export const fighterRow = (kind: FighterKind): number => isNinjaKind(kind) ? NINJAS.kinds[kind].row : THUGS.kinds[kind].row;

interface Hop { start: number; dur: number; peak: number }

/**
 * The hop a ninja is in (or is about to take) at u = t − arr (negative before it reaches the player).
 * ninja:      one hop on the way in;
 * ninja_oni:  a leaping slash that lands on the player;
 * ninja_kasa: keeps hopping all the way.
 */
function hopAt(kind: FighterKind, u: number): Hop | undefined {
  if (isThugKind(kind)) return undefined;
  if (kind === 'ninja') return { start: -1.1, dur: 0.45, peak: 18 };
  if (kind === 'ninja_oni') return { start: -0.6, dur: 0.55, peak: 22 };
  const period = 0.9, start = -3 + Math.floor((u + 3) / period) * period;
  return u < -3 ? undefined : { start, dur: 0.42, peak: 14 };
}

/** Height above its base (game px) and where in the jump the ninja is. */
export function ninjaJump(kind: FighterKind, u: number): { lift: number; phase: number; crouch: boolean } {
  const hop = hopAt(kind, u);
  if (!hop) return { lift: 0, phase: -1, crouch: false };
  const f = (u - hop.start) / hop.dur;
  if (f > 0 && f < 1) return { lift: Math.round(hop.peak * 4 * f * (1 - f)), phase: f, crouch: false };
  const near = (f <= 0 && f > -0.18) || (f >= 1 && f < 1.2);  // take-off and landing
  return { lift: 0, phase: -1, crouch: near };
}

/** Sheet column for a ninja at song time t (u = t − arr). */
export function ninjaColumn(kind: FighterKind, u: number, t: number, seed: number): number {
  const a = NINJAS.anims, j = ninjaJump(kind, u);
  if (j.lift > 0) return j.phase < 0.5 ? a.jumpUp[0] : a.jumpDown[0];
  if (j.crouch) return a.crouch[0];
  if (u > -0.3 && u < 0.3) return a.attack[Math.min(2, Math.floor((u + 0.3) / 0.2))];
  const run = a.run;
  return run[Math.floor(t * NINJAS.fps.run + seed * 7) % run.length];
}
