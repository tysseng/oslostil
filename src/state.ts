import { GROUND, PX } from './config';
import { buildSchedule, type ScheduledEvent } from './schedule';

/** Throws you start with, before collecting any tickets. */
export const START_AMMO = 3;

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

export interface Player {
  x: number;
  y: number;
  vy: number;
  jumps: number;
  slide: number;
  atk: number;
  cd: number;
  star: number;
  /** the tram she is standing on */
  ride?: Enemy;
}

export interface GameState {
  ev: ScheduledEvent[];
  /** index of the next event to spawn */
  ei: number;
  enemies: Enemy[];
  stars: Star[];
  parts: Particle[];
  pops: Pop[];
  score: number;
  kills: number;
  tickets: number;
  /** throws left: every collected ticket is one throw */
  ammo: number;
  perfect: number;
  continues: number;
  combo: number;
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
  /** seconds left of being dead (invisible, no control) after losing the last heart */
  down: number;
  /** seconds left of the white respawn flashing (also invincible) */
  respawn: number;
  boss: { hp: number; max: number; hit: number };
  final: boolean;
  won: boolean;
  best?: number;
}

export function createState(): GameState {
  return {
    ev: buildSchedule(), ei: 0, enemies: [], stars: [], parts: [], pops: [],
    score: 0, kills: 0, tickets: 0, ammo: START_AMMO, perfect: 0, continues: 0, combo: 0,
    hp: 5, inv: 0, fx: PX - 22, mx: PX - 46,
    p: { x: PX, y: GROUND, vy: 0, jumps: 0, slide: 0, atk: 0, cd: 0, star: 0 },
    friend: { yHist: [], atk: 0, cd: 0 },
    bgx: 0, lastT: 0, shake: 0, power: 0, down: 0, respawn: 0,
    boss: { hp: 60, max: 60, hit: 0 }, final: false, won: false,
  };
}

/** Where an enemy is on screen at song time t. */
export const enemyX = (e: Enemy, t: number): number => PX + (e.arr - t) * e.rel;
