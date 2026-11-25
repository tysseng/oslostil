import { BEAT, GROUND, PH, W } from './config';
import type { GameState, RainbowPoint, RainbowState } from './state';
import { RAINBOW_T0, RAINBOW_T1, sectionAt, victoriaBob, victoriaLift } from './timeline';
import rainbowMeta from '../assets/sprites/rainbow.json';
import { EXIT_HOUSE_RIGHT, belowSurface, clampStationY, exitX, playerFloor, stairCompanionPosition } from './valkyrien';

const LANDING_TIME = 1;
const TRAIL_TIME = 1.2;
const TRAIL_LENGTH = 150;

export function machinePosition(s: GameState, t: number): { x: number; y: number } {
  const stairs = stairCompanionPosition(s, s.mx, t);
  if (stairs) return stairs;
  if (s.valkyrien.ascendingAt !== undefined) {
    const progress = Math.max(0, Math.min(1, (s.mx - 16 - (exitX(t) + EXIT_HOUSE_RIGHT)) / 100));
    const ease = progress * progress * (3 - 2 * progress);
    return { x: s.mx, y: GROUND + (-victoriaLift(t) + Math.sin(t * 3) * victoriaBob(t)) * ease };
  }
  if (s.rainbow && !s.deathFlight?.machine) return { x: s.rainbow.x, y: clampStationY(s, s.rainbow.y, 32) };
  return { x: s.mx, y: clampStationY(s, (belowSurface(s) ? s.p.y : GROUND) - victoriaLift(t) + Math.sin(t * 3) * victoriaBob(t), 32) };
}

function anchor(r: RainbowState): RainbowPoint {
  const [ax, ay] = rainbowMeta.fly.anchor, [tx, ty] = rainbowMeta.fly.tail_anchor;
  return { x: r.x + (r.vx < -20 ? ax - tx : tx - ax), y: r.y + ty - ay, t: 0 };
}

/** Points are newest first; interpolation keeps segment spacing independent of frame rate. */
export function ribbonPoints(r: RainbowState, maxLength = TRAIL_LENGTH): RainbowPoint[] {
  const points: RainbowPoint[] = [], start = anchor(r);
  const time = r.path[0]?.t ?? 0;
  let prev = start, distance = 0, next = rainbowMeta.tail.spacing;
  for (const point of r.path) {
    const dx = point.x - prev.x, dy = point.y - prev.y, length = Math.hypot(dx, dy);
    while (length > 0 && next <= distance + length && next <= maxLength) {
      const u = (next - distance) / length;
      const wave = Math.sin(next * 0.075 - time * 6) * 5 * Math.min(1, next / 24);
      points.push({ x: prev.x + dx * u, y: prev.y + dy * u + wave, t: point.t });
      next += rainbowMeta.tail.spacing;
    }
    distance += length;
    if (distance >= maxLength) break;
    prev = point;
  }
  return points;
}

function pathLength(r: RainbowState): number {
  let prev = anchor(r), length = 0;
  for (const p of r.path) {
    length += Math.hypot(p.x - prev.x, p.y - prev.y);
    if (length >= TRAIL_LENGTH) return TRAIL_LENGTH;
    prev = p;
  }
  return length;
}

function trimPath(r: RainbowState, t: number): void {
  let prev = anchor(r), length = 0;
  for (let i = 0; i < r.path.length; i++) {
    const p = r.path[i], segment = Math.hypot(p.x - prev.x, p.y - prev.y);
    if (t - p.t > TRAIL_TIME || length + segment > TRAIL_LENGTH) {
      if (length < TRAIL_LENGTH && segment > 0 && t - p.t <= TRAIL_TIME) {
        const u = (TRAIL_LENGTH - length) / segment;
        r.path[i] = { x: prev.x + (p.x - prev.x) * u, y: prev.y + (p.y - prev.y) * u, t: p.t };
        r.path.length = i + 1;
      } else r.path.length = i;
      break;
    }
    length += segment;
    prev = p;
  }
}

function newFlight(s: GameState, t: number): RainbowState {
  const normal = machinePosition(s, t);
  return { ...normal, vx: 220, vy: -200, blend: 0, path: [], sparkles: [], beat: Math.floor((t - PH) / BEAT) - 1 };
}

export function updateRainbow(s: GameState, t: number, dt: number): void {
  if (t < RAINBOW_T0 || t >= RAINBOW_T1 + LANDING_TIME || s.deathFlight?.machine) {
    s.rainbow = undefined;
    return;
  }
  const r = s.rainbow ??= newFlight(s, t);
  for (const sparkle of r.sparkles) {
    sparkle.x -= sectionAt(t).speed * dt;
    sparkle.age += dt;
  }
  r.sparkles = r.sparkles.filter(p => p.age < rainbowMeta.sparkle.frames / rainbowMeta.sparkle.fps);

  if (t >= RAINBOW_T1) {
    r.landing ??= { x: r.x, y: r.y, length: pathLength(r) };
    const u = Math.min(1, (t - RAINBOW_T1) / LANDING_TIME), ease = u * u * (3 - 2 * u);
    r.blend = 1 - ease;
    r.x = r.landing.x + (s.mx - r.landing.x) * ease;
    const targetY = (belowSurface(s) ? s.p.y : GROUND) - victoriaLift(t) + Math.sin(t * 3) * victoriaBob(t);
    r.y = clampStationY(s, r.landing.y + (targetY - r.landing.y) * ease, 32);
    r.path.unshift({ ...anchor(r), t });
    trimPath(r, t);
    return;
  }

  r.blend = Math.min(1, Math.max(0, (t - RAINBOW_T0) / BEAT));
  const beat = Math.floor((t - PH) / BEAT);
  if (beat !== r.beat) {
    r.beat = beat;
    r.vx += Math.sin(beat * 12.9898) * 60;
    r.vy += Math.sin(beat * 7.233) * 35;
    const points = ribbonPoints(r);
    if (points.length) {
      const index = Math.floor((0.5 + 0.5 * Math.sin(beat * 9.17)) * (points.length - 1));
      r.sparkles.push({ x: points[index].x, y: points[index].y, age: 0 });
    }
  }
  const ax = s.p.x + 20 + 30 * Math.sin(t * 2.1) + 10 * Math.sin(t * 3.7);
  const ay = s.p.y - 55 + 20 * Math.sin(t * 2.6 + 1) + 7 * Math.sin(t * 4.1);
  const dx = ax - r.x, dy = ay - r.y, distance = Math.hypot(dx, dy);
  const pull = distance > 12 ? 34 * (distance - 12) / distance : 0;
  r.vx += (pull * dx - 4 * r.vx) * dt;
  r.vy += (pull * dy - 4 * r.vy) * dt;
  r.x += r.vx * dt;
  r.y += r.vy * dt;
  if (r.x < 14 || r.x > W - 14) {
    r.x = Math.max(14, Math.min(W - 14, r.x));
    r.vx *= -0.5;
  }
  const minY = clampStationY(s, 36, 32), maxY = playerFloor(s) - 20;
  if (r.y < minY || r.y > maxY) {
    r.y = Math.max(minY, Math.min(maxY, r.y));
    r.vy *= -0.5;
  }
  r.path.unshift({ ...anchor(r), t });
  trimPath(r, t);
  if (Math.floor(t / 0.12) !== Math.floor((t - dt) / 0.12)) {
    const points = ribbonPoints(r);
    if (points.length) {
      const point = points[Math.floor(Math.random() * points.length)];
      r.sparkles.push({ x: point.x, y: point.y + (Math.random() < 0.5 ? -9 : 9), age: 0 });
    }
  }
}

/** Reconstruct visual history for debug seeks without simulating gameplay. */
export function seekRainbow(s: GameState, t: number): void {
  s.rainbow = undefined;
  if (t < RAINBOW_T0 || t >= RAINBOW_T1 + LANDING_TIME) return;
  const step = 1 / 60;
  updateRainbow(s, RAINBOW_T0, 0);
  for (let at = RAINBOW_T0; at < t;) {
    const next = Math.min(t, at + step, at < RAINBOW_T1 ? RAINBOW_T1 : t);
    updateRainbow(s, next, next - at);
    at = next;
  }
}

export function ribbonLength(r: RainbowState, t: number): number {
  return r.landing ? r.landing.length * Math.max(0, 1 - (t - RAINBOW_T1) / 0.6) : TRAIL_LENGTH;
}
