import { GROUND, H, PX } from './config';
import type { GameState } from './state';

export const VALKYRIEN_ENTRY = 87;
export const VALKYRIEN_EXIT = 95;
export const VALKYRIEN_DEPTH = H;
export const VALKYRIEN_FLOOR = GROUND + VALKYRIEN_DEPTH;
export const VALKYRIEN_CEILING = VALKYRIEN_FLOOR - 110;
export const CHUTE_HALF_WIDTH = 22;
export const STAIRS_WIDTH = 140;
const SPEED = 145;

export interface ValkyrienState {
  phase: 'surface' | 'chute' | 'underground' | 'run-in' | 'stairs' | 'exit';
  camera: number;
  openedAt?: number;
  coverRider?: boolean;
  ascendingAt?: number;
}

export const manholeX = (t: number): number => PX + (VALKYRIEN_ENTRY - t) * SPEED;
export const exitX = (t: number): number => PX + (VALKYRIEN_EXIT - t) * SPEED;
export const belowSurface = (s: GameState): boolean =>
  s.valkyrien.phase !== 'surface' && s.valkyrien.phase !== 'exit';
export const routeControlsPlayer = (s: GameState): boolean =>
  !!s.valkyrien.coverRider || ['chute', 'run-in', 'stairs'].includes(s.valkyrien.phase);
export const playerFloor = (s: GameState): number => belowSurface(s) ? VALKYRIEN_FLOOR : GROUND;

/** Resolve the optional route after ordinary gravity, instead of surface ground landing. */
export function resolveValkyrien(s: GameState, t: number, dt: number, previousY: number): void {
  const r = s.valkyrien, p = s.p;
  if (r.coverRider) {
    if (p.vy < 0 || Math.abs(p.x - manholeX(t)) > 25) r.coverRider = false;
    else p.x = manholeX(t);
  }
  const hole = Math.abs(p.x - manholeX(t)) < 18;
  if (r.phase === 'surface' && s.down <= 0 && p.vy > 0 && previousY <= GROUND && p.y >= GROUND && hole) {
    if (r.openedAt === undefined && previousY < GROUND - 1) {
      r.openedAt = t;
      p.y = GROUND;
      r.coverRider = true;
      p.vy = 0;
      p.jumps = 0;
      p.slide = 0;
    } else if (r.openedAt !== undefined && t - r.openedAt >= 0.22) {
      r.phase = 'chute';
      r.coverRider = false;
      p.ride = undefined;
      p.propRide = undefined;
      p.machineRide = undefined;
      p.slide = 0;
      p.vy = 650;
    }
  }
  if (r.phase === 'chute') {
    p.x = manholeX(t);
    p.vy = Math.max(650, p.vy);
    if (p.y - 32 >= VALKYRIEN_CEILING) r.phase = 'underground';
  }
  if (r.phase === 'run-in') {
    p.x = Math.min(PX, p.x + 260 * dt);
    if (p.x === PX) r.phase = 'underground';
  }
  if (r.phase === 'underground' && (t >= VALKYRIEN_EXIT ||
    p.x >= exitX(t) - STAIRS_WIDTH && p.y >= VALKYRIEN_FLOOR - 3)) {
    r.phase = 'stairs';
    r.ascendingAt = t;
    p.slide = 0;
    p.ride = undefined;
    p.propRide = undefined;
    p.machineRide = undefined;
  }
  if (r.phase === 'stairs' && r.ascendingAt !== undefined) {
    const u = Math.min(1, Math.max(0, t - r.ascendingAt));
    p.x = exitX(t) - STAIRS_WIDTH * (1 - u);
    p.y = VALKYRIEN_FLOOR - VALKYRIEN_DEPTH * u;
    p.vy = 0;
    p.jumps = 0;
    r.camera = VALKYRIEN_DEPTH * (1 - u);
    if (u === 1) r.phase = 'exit';
  } else {
    const target = belowSurface(s) ? VALKYRIEN_DEPTH : 0;
    r.camera += (target - r.camera) * Math.min(1, dt * 20);
    if (Math.abs(target - r.camera) < 0.01) r.camera = target;
    const floor = playerFloor(s);
    if (s.down <= 0 && p.y >= floor && p.vy >= 0) {
      p.y = floor;
      p.vy = 0;
      p.jumps = 0;
      s.bounceChain = 0;
      if (r.phase === 'underground' && previousY < floor && p.x < 0) r.phase = 'run-in';
    }
  }
}
