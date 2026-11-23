import { GROUND, PLAYER_MAX_HP, PX, W } from './config';
import { TRAM_WARN, TYPES, type ScheduledEvent } from './schedule';
import { loadDefaultLevel } from './level';
import { sectionAt } from './timeline';

/** Throws you start with, before collecting any tickets. */
export const START_AMMO = 3;

export interface DeathFlight { x: number; y: number; vx: number; vy: number; angle: number }

export interface Enemy extends ScheduledEvent {
  /** speed relative to the player */
  rel: number;
  hp: number;
  y: number;
  dead?: boolean;
  gone?: boolean;
}

export interface Star { x: number; y: number; vx: number; vy: number; a: number; ninja: boolean; gone?: boolean }
export interface Particle { x: number; y: number; vx: number; vy: number; life: number; c: string }
export interface Pop { x: number; y: number; txt: string; life: number; c: string }
export interface KnockedEnemy { enemy: Enemy; x: number; y: number; vx: number; vy: number; splash: boolean; squash?: number }

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
  ev: ScheduledEvent[];
  /** index of the next event to spawn */
  ei: number;
  enemies: Enemy[];
  stars: Star[];
  parts: Particle[];
  pops: Pop[];
  knocked: KnockedEnemy[];
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
  /** friend and machine x positions (they ease after the player) */
  fx: number;
  mx: number;
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
  best?: number;
}

export const eventSpeed = (e: ScheduledEvent): number =>
  e.rel ?? (sectionAt(e.arr).speed + TYPES[e.type].own) * (e.type === 'tram' ? 1.2 : 1);
export const spawnTime = (e: ScheduledEvent): number =>
  e.arr - (W + 100 - PX) / eventSpeed(e) - (e.type === 'tram' ? TRAM_WARN : 0);

export function createEnemy(e: ScheduledEvent): Enemy {
  return { ...e, rel: eventSpeed(e), hp: TYPES[e.type].hp, y: e.y ?? TYPES[e.type].y };
}

export function createState(events: ScheduledEvent[] = loadDefaultLevel()): GameState {
  return {
    ev: events.slice().sort((a, b) => spawnTime(a) - spawnTime(b)), ei: 0, enemies: [], stars: [], parts: [], pops: [], knocked: [],
    score: 0, kills: 0, tickets: 0, ammo: START_AMMO, perfect: 0, continues: 0, combo: 0, bounceChain: 0,
    hp: PLAYER_MAX_HP, inv: 0, fx: PX - 22, mx: PX - 46,
    p: { x: PX, y: GROUND, vy: 0, jumps: 0, slide: 0, slideDirection: 1, atk: 0, cd: 0, star: 0 },
    friend: { yHist: [], atk: 0, cd: 0 },
    bgx: 0, lastT: 0, shake: 0, power: 0, down: 0, respawn: 0,
    boss: { hp: 60, max: 60, hit: 0 }, final: false, won: false,
  };
}

/** Where an enemy is on screen at song time t. */
export const enemyX = (e: Enemy, t: number): number => PX + (e.arr - t) * e.rel;
