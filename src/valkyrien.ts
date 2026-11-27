import { GROUND, H, PX, W } from './config';
import type { GameState } from './state';

const PLATFORM_ENTRY = 87.8;
export const STAIRS_WIDTH = 140;
export const VALKYRIEN_ENTRY = PLATFORM_ENTRY - STAIRS_WIDTH / 145;
// Include the 50-pixel entrance and 45-pixel end margins in the station length.
export const VALKYRIEN_EXIT = PLATFORM_ENTRY + (1882.5 * 0.95 - 95) / 145;
export const SURFACE_STRIP_HEIGHT = H - GROUND;
export const VALKYRIEN_CAMERA = GROUND - SURFACE_STRIP_HEIGHT / 2 - 14;
export const VALKYRIEN_CEILING = H + SURFACE_STRIP_HEIGHT / 2;
export const VALKYRIEN_BOTTOM = 26;
export const VALKYRIEN_FLOOR = VALKYRIEN_CAMERA + H - VALKYRIEN_BOTTOM;
export const VALKYRIEN_DEPTH = VALKYRIEN_FLOOR - GROUND;
export const VALKYRIEN_HEIGHT = VALKYRIEN_FLOOR - VALKYRIEN_CEILING;
export const ENTRY_HALF_WIDTH = 22;
export const EXIT_HOUSE_LEFT = -40;
export const EXIT_HOUSE_RIGHT = 64;
export const EXIT_HOUSE_ROOF = GROUND - 48;
const SPEED = 145;
export const stationPlacement = (x: number, base: number, width: number, height: number, t: number): boolean =>
  base <= VALKYRIEN_FLOOR && base - height >= VALKYRIEN_CEILING
  && x - width / 2 >= platformStartX(t) && x + width / 2 <= exitX(t) - STAIRS_WIDTH;

export interface ValkyrienState {
  phase: 'surface' | 'chute' | 'underground' | 'run-in' | 'stairs' | 'house' | 'exit';
  camera: number;
  ascendingAt?: number;
  descendingAt?: number;
  roofRide?: boolean;
}

export const stationEntryX = (t: number): number => PX + (VALKYRIEN_ENTRY - t) * SPEED;
export const platformStartX = (t: number): number => stationEntryX(t) + STAIRS_WIDTH;
export const exitX = (t: number): number => PX + (VALKYRIEN_EXIT - t) * SPEED;
export function exitSurfaceClip(t: number): { x: number; width: number } {
  const x = exitX(t) + EXIT_HOUSE_LEFT;
  return { x, width: Math.max(0, W - x) };
}
export const VALKYRIEN_TRAIN_START = PLATFORM_ENTRY + (PX - 20) / SPEED;
export function valkyrienTrainNose(t: number): number | null {
  if (t < VALKYRIEN_TRAIN_START) return null;
  return platformStartX(t) - 50 + 360 * (t - VALKYRIEN_TRAIN_START);
}
export const belowSurface = (s: GameState): boolean =>
  !['surface', 'house', 'exit'].includes(s.valkyrien.phase);
export const routeControlsPlayer = (s: GameState): boolean =>
  ['chute', 'run-in', 'stairs', 'house'].includes(s.valkyrien.phase);
export const playerFloor = (s: GameState): number => belowSurface(s) ? VALKYRIEN_FLOOR : GROUND;
export const clampStationY = (s: GameState, base: number, height: number): number =>
  ['underground', 'run-in'].includes(s.valkyrien.phase) ? Math.max(VALKYRIEN_CEILING + height, base) : base;

export function stairCompanionPosition(s: GameState, x: number, t: number): { x: number; y: number } | null {
  if (s.valkyrien.descendingAt !== undefined && s.valkyrien.ascendingAt === undefined
    && x - 16 <= platformStartX(t)) {
    const progress = Math.max(0, Math.min(1, (x - stationEntryX(t)) / STAIRS_WIDTH));
    return { x, y: GROUND + VALKYRIEN_DEPTH * progress };
  }
  if (s.valkyrien.ascendingAt === undefined || x - 16 > exitX(t) + EXIT_HOUSE_RIGHT) return null;
  const progress = Math.max(0, Math.min(1, (x - exitX(t) + STAIRS_WIDTH) / STAIRS_WIDTH));
  return { x, y: VALKYRIEN_FLOOR - VALKYRIEN_DEPTH * progress };
}

export function enterValkyrien(s: GameState): boolean {
  const p = s.p;
  if (s.valkyrien.phase !== 'surface' || s.down > 0 || Math.abs(p.x - stationEntryX(s.lastT)) > ENTRY_HALF_WIDTH
    || Math.abs(p.y - GROUND) > 2 || p.vy < 0) return false;
  s.valkyrien.phase = 'chute';
  s.valkyrien.descendingAt = s.lastT;
  p.x = stationEntryX(s.lastT);
  p.y = GROUND;
  p.vy = 0;
  p.slide = 0;
  p.jumps = 0;
  p.ride = undefined;
  p.propRide = undefined;
  p.machineRide = undefined;
  return true;
}

/** Resolve the optional route after ordinary gravity, instead of surface ground landing. */
export function resolveValkyrien(s: GameState, t: number, dt: number, previousY: number): void {
  const r = s.valkyrien, p = s.p;
  r.roofRide = r.phase === 'surface' && s.down <= 0 && p.vy >= 0
    && previousY <= EXIT_HOUSE_ROOF + 0.5 && p.y >= EXIT_HOUSE_ROOF
    && p.x + 4 > exitX(t) + EXIT_HOUSE_LEFT + 1 && p.x - 4 < exitX(t) + EXIT_HOUSE_RIGHT - 1;
  if (r.roofRide) {
    p.y = EXIT_HOUSE_ROOF;
    p.vy = 0;
    p.jumps = 0;
    p.ride = undefined;
    p.propRide = undefined;
    p.machineRide = undefined;
    s.bounceChain = 0;
  }
  if (r.phase === 'house') {
    p.y = GROUND;
    p.vy = 0;
    p.x += 130 * dt;
    if (p.x - 16 > exitX(t) + EXIT_HOUSE_RIGHT) r.phase = 'exit';
  }
  if (r.phase === 'chute' && r.descendingAt !== undefined) {
    const u = Math.max(0, Math.min(1, t - r.descendingAt));
    p.x = stationEntryX(t) + STAIRS_WIDTH * u;
    p.y = GROUND + VALKYRIEN_DEPTH * u;
    p.vy = 0;
    p.jumps = 0;
    r.camera = VALKYRIEN_CAMERA * (u * u * (3 - 2 * u));
    if (u < 1) return;
    r.phase = p.x < PX ? 'run-in' : 'underground';
  }
  if (r.phase === 'run-in') {
    p.x = Math.min(PX, p.x + 260 * dt);
    if (p.x === PX) r.phase = 'underground';
  }
  if (s.down <= 0) {
    const base = clampStationY(s, p.y, 32);
    if (base !== p.y) {
      p.y = base;
      p.vy = Math.max(0, p.vy);
      p.ride = undefined;
      p.propRide = undefined;
      p.machineRide = undefined;
    }
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
    r.camera = VALKYRIEN_CAMERA * (1 - u);
    if (u === 1) r.phase = 'house';
  } else {
    const target = belowSurface(s) ? VALKYRIEN_CAMERA : 0;
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
