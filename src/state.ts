import { BEAT, GROUND, PH, PLAYER_MAX_HP, PX, W, rng } from './config';
import { BLOB_HOP, BROKEN_BOARD, isGhost, isPowerup, isTree, isWallPoster, itemLayer, treeDepth, TRAM_WARN, TYPES, type ScheduledEvent } from './schedule';
import { loadDefaultLevel } from './level';
import { sectionAt } from './timeline';
import type { ValkyrienState } from './valkyrien';
import { VALKYRIEN_CEILING, VALKYRIEN_FLOOR } from './valkyrien';

/** Throws you start with, before collecting any tickets. */
export const START_AMMO = 3;

export interface DeathFlight { x: number; y: number; vx: number; vy: number; angle: number }

export interface Enemy extends ScheduledEvent {
  /** speed relative to the player */
  rel: number;
  hp: number;
  y: number;
  /** a ninja's base height; y is this plus its jump */
  y0?: number;
  dropIn?: number;
  crumbledAt?: number;
  weighed?: boolean;
  dead?: boolean;
  gone?: boolean;
  ghost?: { x: number; base: number; vx: number; following: boolean; gaveUp?: boolean };
}

export interface Star { x: number; y: number; vx: number; vy: number; a: number; ninja: boolean; gone?: boolean }
export interface Particle { x: number; y: number; vx: number; vy: number; life: number; c: string }
export interface Pop { x: number; y: number; txt: string; life: number; c: string }
export interface KnockedEnemy { enemy: Enemy; x: number; y: number; vx: number; vy: number; splash: boolean; squash?: number }
export interface Dropping { x: number; y: number; vy: number; life: number; landed: boolean; floor?: number }
export interface BlobPop { x: number; y: number; age: number }
export interface RainbowPoint { x: number; y: number; t: number }
export interface RainbowState {
  x: number;
  y: number;
  vx: number;
  vy: number;
  blend: number;
  path: RainbowPoint[];
  sparkles: { x: number; y: number; age: number }[];
  beat: number;
  landing?: { x: number; y: number; length: number };
}

export interface Player {
  x: number;
  y: number;
  vy: number;
  jumps: number;
  slide: number;
  slideDirection: -1 | 1;
  atk: number;
  cd: number;
  star: number;
  /** the tram she is standing on */
  ride?: Enemy;
  /** One-way prop platform supporting her. */
  propRide?: Enemy;
  /** Index of the stationary Sandvika machine supporting her. */
  machineRide?: number;
}

export interface GameState {
  valkyrien: ValkyrienState;
  ev: ScheduledEvent[];
  /** index of the next event to spawn */
  ei: number;
  enemies: Enemy[];
  stars: Star[];
  parts: Particle[];
  pops: Pop[];
  knocked: KnockedEnemy[];
  droppings: Dropping[];
  blobPops: BlobPop[];
  boardShake: number;
  taggerStoppedAt?: number;
  score: number;
  kills: number;
  tickets: number;
  /** throws left: every collected ticket is one throw */
  ammo: number;
  perfect: number;
  continues: number;
  combo: number;
  /** Consecutive stomps without landing or taking damage. */
  bounceChain: number;
  hp: number;
  inv: number;
  healFlash: number;
  /** friend and machine x positions (they ease after the player) */
  fx: number;
  mx: number;
  rainbow?: RainbowState;
  p: Player;
  friend: { yHist: number[]; atk: number; cd: number };
  /** background scroll distance */
  bgx: number;
  /** song time of the last update */
  lastT: number;
  shake: number;
  /** triple-throw power-up active until this time */
  power: number;
  /** Tram-hit party animation, independent of the respawn positions. */
  deathFlight?: DeathFlight & { friend?: DeathFlight; machine?: DeathFlight };
  /** seconds before respawning after death (counted after any death flight exits) */
  down: number;
  /** seconds left of the white respawn flashing (also invincible) */
  respawn: number;
  boss: { hp: number; max: number; hit: number };
  final: boolean;
  won: boolean;
  celebration?: {
    elapsed: number;
    bgx: number;
    victoria: { x: number; y: number };
    friend: { x: number; y: number };
    machine: { x: number; y: number };
  };
  best?: number;
}

export const eventSpeed = (e: ScheduledEvent): number =>
  e.rel ?? (sectionAt(e.arr).speed + TYPES[e.type].own) * (e.type === 'tram' ? 1.2 : 1);
const movementSpeed = (e: ScheduledEvent): number =>
  (e.y ?? 0) < 0 ? (isWallPoster(e.type) ? 145 * 0.85 : 145)
  : eventSpeed(e) * (isTree(e.type) ? 0.5 + treeDepth(e) * 0.25 : 1);
export const spawnTime = (e: ScheduledEvent): number =>
  e.arr - (W + 100 - PX + (e.type === 'blob_hop' ? 40 * BEAT : 0)) / movementSpeed(e) - (e.type === 'tram' ? TRAM_WARN : 0);

export function createEnemy(e: ScheduledEvent): Enemy {
  return { ...e, rel: movementSpeed(e), hp: TYPES[e.type].hp, y: e.y ?? TYPES[e.type].y };
}

export function compareItems(a: Enemy, b: Enemy): number {
  return itemLayer(a.type) - itemLayer(b.type)
    || (isTree(a.type) && isTree(b.type) ? a.rel - b.rel : 0);
}

export function createState(events: ScheduledEvent[] = loadDefaultLevel()): GameState {
  return {
    valkyrien: { phase: 'surface', camera: 0 },
    ev: events.slice().sort((a, b) => spawnTime(a) - spawnTime(b)), ei: 0, enemies: [], stars: [], parts: [], pops: [], knocked: [], droppings: [], blobPops: [], boardShake: 0,
    score: 0, kills: 0, tickets: 0, ammo: START_AMMO, perfect: 0, continues: 0, combo: 0, bounceChain: 0,
    hp: PLAYER_MAX_HP, inv: 0, healFlash: 0, fx: PX - 22, mx: PX - 46,
    p: { x: PX, y: GROUND, vy: 0, jumps: 0, slide: 0, slideDirection: 1, atk: 0, cd: 0, star: 0 },
    friend: { yHist: [], atk: 0, cd: 0 },
    bgx: 0, lastT: 0, shake: 0, power: 0, down: 0, respawn: 0,
    boss: { hp: 60, max: 60, hit: 0 }, final: false, won: false,
  };
}

/** Where an enemy is on screen at song time t. */
export const enemyX = (e: Enemy, t: number): number => e.ghost?.x ?? PX + (e.arr - t) * e.rel
  + (e.type === 'blob_hop' && e.y >= 0 ? 40 * (hopTravel(e, e.arr) - hopTravel(e, t) - 5 / 8 * (e.arr - t)) : 0);

function hopTravel(e: ScheduledEvent, t: number): number {
  const period = BEAT / (e.hop === 'double' ? 2 : 1), cycles = (t - PH) / period;
  return (Math.floor(cycles) * 5 / 8 + Math.max(0, cycles - Math.floor(cycles) - 3 / 8)) * period;
}

export function hopPose(e: ScheduledEvent, t: number): { frame: number; lift: number; h: number } {
  const cycles = (t - PH) / BEAT * (e.hop === 'double' ? 2 : 1);
  const phase = cycles - Math.floor(cycles), frame = Math.floor(phase * BLOB_HOP.frames_per_hop);
  const u = Math.max(0, (phase - BLOB_HOP.air[0] / BLOB_HOP.frames_per_hop) / (5 / 8));
  const height = e.hop === 'low' ? 14 : e.hop === 'high' ? 34 : e.hop === 'double' ? 18 : 26;
  return { frame, lift: 4 * height * u * (1 - u), h: frame < 2 ? 8 : BLOB_HOP.h };
}

export const boardImpactAt = (e: Enemy): number => (e.crumbledAt ?? Infinity) + BEAT / 2;
export function boardFrame(e: Enemy, t: number): number {
  const since = t - (e.crumbledAt ?? Infinity), { glitch, fall, rest } = BROKEN_BOARD.phases;
  if (since <= 0) return glitch.frames[Math.floor(Math.max(0, t) * glitch.fps) % glitch.frames.length];
  const frameTime = BEAT / (2 * fall.frames.indexOf(BROKEN_BOARD.frames.indexOf('impact')));
  const frame = Math.floor((since + 1e-9) / frameTime);
  if (frame < fall.frames.length) return fall.frames[frame];
  return rest.frames[Math.floor((since - frameTime * fall.frames.length) * rest.fps) % rest.frames.length];
}
export const boardTop = (e: Enemy, t: number): number => BROKEN_BOARD.top[boardFrame(e, t)];
export const enemyBodyHeight = (e: Enemy, t: number): number =>
  e.type === 'blob_hop' ? hopPose(e, t).h : e.type === 'board_broken' ? boardTop(e, t) : TYPES[e.type].h;

export function eventArrival(e: ScheduledEvent, t: number, x: number): number {
  const base = t + (x - PX) / createEnemy(e).rel;
  if (e.type !== 'blob_hop') return base;
  let low = base - BEAT, high = base + BEAT;
  for (let i = 0; i < 40; i++) {
    const arr = (low + high) / 2;
    if (enemyX(createEnemy({ ...e, arr }), t) < x) low = arr;
    else high = arr;
  }
  return (low + high) / 2;
}

/** Song-time flight, seeded from the authored position rather than frame/update order. */
export function enemyHeight(e: Enemy, t: number): number {
  if (isGhost(e.type)) {
    if (e.ghost) return GROUND - e.ghost.base;
    return GROUND - Math.max(VALKYRIEN_CEILING + TYPES[e.type].h,
      Math.min(VALKYRIEN_FLOOR - 4, GROUND - e.y + 4 * Math.sin((t - e.arr) * 3)));
  }
  if (isPowerup(e.type)) return e.y + 2 * Math.sin(t * 4);
  if (!e.dead && e.type === 'blob_hop') return e.y + hopPose(e, t).lift;
  if (e.dead || (e.type !== 'pigeon' && e.type !== 'gull')) return e.y;
  const seed = Math.imul(Math.round(e.arr * 1000), 73856093) ^ Math.imul(Math.round(e.y * 1000), 19349663);
  const random = rng(seed);
  const phase1 = random() * Math.PI * 2, phase2 = random() * Math.PI * 2;
  const speed1 = 2.8 + random() * 1.2, speed2 = 4.5 + random() * 1.5;
  const wave = 0.65 * Math.sin((t - e.arr) * speed1 + phase1)
    + 0.35 * Math.sin((t - e.arr) * speed2 + phase2);
  if (e.y < 0) return Math.min(GROUND - VALKYRIEN_CEILING - TYPES[e.type].h, e.y + 24 * (wave + 1));
  return Math.max(24, Math.min(GROUND - TYPES[e.type].h - 52, e.y)) + 24 * (wave + 1);
}
