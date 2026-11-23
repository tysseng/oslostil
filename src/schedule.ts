// Every enemy and pickup is scheduled to reach the player's spot exactly on a beat.
import { BEAT, barT, rng } from './config';
import sheetJson from '../assets/sprites/enemies.json';

export type EnemyKind =
  | 'suitcase' | 'snow' | 'pigeon' | 'ticket' | 'blob' | 'ninja' | 'drone'
  | 'tram' | 'bot' | 'terminal' | 'fire' | 'coin' | 'shot' | 'fireball';

/** One row of the enemy sprite sheet (assets/sprites/enemies.png, 32 × 32 bottom-centred cells). */
export interface SheetRow {
  row: number;
  frames: number;
  fps: number;
  /** visible size in game px */
  w: number;
  h: number;
}
/** Every kind except the tram (still drawn in code) has a row in the sheet. */
export type SheetKind = Exclude<EnemyKind, 'tram'>;
export const SHEET: Record<SheetKind, SheetRow> = sheetJson;
export const SHEET_CELL = 32;

export interface EnemyType {
  w: number;
  h: number;
  /** height above the ground */
  y: number;
  hp: number;
  /** own speed added to the scroll speed */
  own: number;
  pickup?: boolean;
  /** can't be destroyed – jump or slide */
  solid?: boolean;
}

/**
 * The tram is a full-length moving platform (new light-blue tram, 30.5 m at TRAM_PPM).
 * Its x is the nose (left end), which reaches the player's spot on the beat. If it hits the player she is
 * thrown up in the air; she can land on the roof and ride it until it leaves the screen.
 */
/** drawn at the trains' scale (game px per metre) */
export const TRAM_PPM = 10;
/** 30.5 m long (tram-new.png) */
export const TRAM_LEN = 305;
/** walkable roof height above the ground: the roof line is 3.84 m above the wheel bottoms (the roof boxes stick up a bit more) */
export const TRAM_ROOF = 38;
/** own speed on top of the scroll speed (px/s); lower = longer rides */
export const TRAM_OWN = 40;
/** a rider standing still is carried back to this screen x, then falls off when the tail passes */
export const TRAM_EDGE = 8;
/** seconds of «!» warning before the nose enters the screen */
export const TRAM_WARN = 1.2;

/** Hitbox size (w, h) comes from the sprite's visible size in enemies.json. */
const fromSheet = (k: SheetKind, rest: Omit<EnemyType, 'w' | 'h'>): EnemyType => ({ w: SHEET[k].w, h: SHEET[k].h, ...rest });

export const TYPES: Record<EnemyKind, EnemyType> = {
  suitcase: fromSheet('suitcase', { y: 0, hp: 1, own: 0 }),
  snow: fromSheet('snow', { y: 0, hp: 1, own: 0 }),
  pigeon: fromSheet('pigeon', { y: 26, hp: 1, own: 40 }),
  ticket: fromSheet('ticket', { y: 34, hp: 0, own: 0, pickup: true }), // collected = one more throw
  blob: fromSheet('blob', { y: 0, hp: 1, own: 20 }),
  ninja: fromSheet('ninja', { y: 0, hp: 1, own: 50 }),
  drone: fromSheet('drone', { y: 30, hp: 1, own: 30 }),
  tram: { w: TRAM_LEN, h: TRAM_ROOF, y: 0, hp: 99, own: TRAM_OWN, solid: true },
  bot: fromSheet('bot', { y: 0, hp: 2, own: 25 }),
  terminal: fromSheet('terminal', { y: 30, hp: 0, own: 0, pickup: true }),
  fire: fromSheet('fire', { y: 0, hp: 99, own: 0, solid: true }),
  coin: fromSheet('coin', { y: 38, hp: 0, own: 0, pickup: true }),
  shot: fromSheet('shot', { y: 6, hp: 1, own: 120 }),
  fireball: fromSheet('fireball', { y: 28, hp: 1, own: 120 }),
};

export interface ScheduledEvent {
  /** time it reaches the player's spot */
  arr: number;
  type: EnemyKind;
  y?: number;
  label?: string;
  fromBoss?: boolean;
  /** Fixed relative speed for manually positioned items. */
  rel?: number;
}

const LABELS = ['CHILD', 'ADULT', 'STUDENT', 'SENIOR'];

/**
 * Tickets are the ammo, and they only appear at Sandvika stasjon (bars 2–25, intro and verse 1).
 * Lots of them, in little patterns at different heights: low rows to run through, arcs that follow a
 * jump, staircases and high pairs that need a double jump. Collect them early – they must last the song.
 * Heights are px above the platform (single jump reaches ≈50, double jump ≈85).
 */
type Add = (arr: number, type: EnemyKind, extra?: Partial<ScheduledEvent>) => void;
function addTickets(add: Add, r: () => number): void {
  const at = (bar: number, s16: number) => barT(bar, s16);
  const patterns: ((bar: number, s: number) => void)[] = [
    (bar, s) => { for (let i = 0; i < 4; i++) add(at(bar, s + i * 2), 'ticket', { y: 12 }); },                // low row
    (bar, s) => { [14, 30, 40, 30, 14].forEach((y, i) => add(at(bar, s + i * 2), 'ticket', { y })); },         // jump arc
    (bar, s) => { [36, 46, 56].forEach((y, i) => add(at(bar, s + i * 2), 'ticket', { y })); },                 // staircase up
    (bar, s) => { add(at(bar, s), 'ticket', { y: 66 }); add(at(bar, s + 2), 'ticket', { y: 70 }); },          // double-jump pair
    (bar, s) => { for (let i = 0; i < 3; i++) add(at(bar, s + i * 2), 'ticket', { y: 26 }); },                // mid row
  ];
  // one pattern per bar, starting off the downbeat so it doesn't sit on top of the obstacles
  for (let bar = 2; bar <= 25; bar++) patterns[Math.floor(r() * patterns.length)](bar, 2 + 2 * Math.floor(r() * 2));
}

export function buildSchedule(): ScheduledEvent[] {
  const ev: ScheduledEvent[] = [];
  const r = rng(2026);
  const add = (arr: number, type: EnemyKind, extra: Partial<ScheduledEvent> = {}) => ev.push({ arr, type, ...extra });
  const beats = (a: number, b: number) => {
    const out: { bar: number; k: number; t: number }[] = [];
    for (let bar = a; bar <= b; bar++) for (let k = 0; k < 4; k++) out.push({ bar, k, t: barT(bar, k * 4) });
    return out;
  };

  // intro + verse 1: Sandvika stasjon
  for (const { k, t } of beats(3, 9)) {
    if (k % 2 === 0) add(t, r() < 0.5 ? 'suitcase' : 'snow');
  }
  for (const { k, t } of beats(10, 25)) {
    if (k === 0 && r() < 0.75) add(t, r() < 0.5 ? 'suitcase' : 'snow');
    else if (k === 2 && r() < 0.55) add(t, 'pigeon');
  }
  addTickets(add, r);
  // pre-chorus 1: glitch blobs
  for (const { k, t } of beats(26, 31)) {
    if (k % 2 === 0) add(t, 'blob');
    else if (r() < 0.5) add(t, 'pigeon');
  }
  add(barT(32), 'suitcase');
  // chorus 1: inside the game
  for (const { k, t } of beats(34, 41)) {
    add(t, k % 2 ? 'drone' : 'ninja');
    if (k === 2 && r() < 0.5) add(t + BEAT / 2, 'coin', { y: 40 });
  }
  for (const b of [36, 40]) add(barT(b, 8), 'tram');
  // verse 2: «Choose travellers» – ticket-category bots
  for (const { bar, k, t } of beats(42, 57)) {
    if (bar === 49 && k === 2) { add(t, 'terminal'); continue; }
    if (k === 0 || (k === 2 && r() < 0.6)) add(t, 'bot', { label: LABELS[(bar + k) % 4] });
    else if (k === 3 && r() < 0.6) add(t, 'drone');
    else if (r() < 0.3) add(t, 'coin', { y: 34 + r() * 12 });
  }
  add(barT(47), 'tram'); // a little later than bar 46.5, after the T-bane train has gone
  add(barT(54, 8), 'tram');
  // pre-chorus 2: burning trams
  for (const { k, t } of beats(58, 65)) {
    add(t, k % 2 ? (r() < 0.5 ? 'drone' : 'ninja') : r() < 0.35 ? 'fire' : 'ninja');
    if (r() < 0.35) add(t + BEAT / 2, 'ninja');
  }
  for (const b of [60, 64]) add(barT(b, 8), 'tram');
  // chorus 2: final wave, boss shoots from bar 70
  for (const { bar, k, t } of beats(66, 73)) {
    add(t, r() < 0.3 ? 'bot' : 'ninja', { label: 'KAOS' });
    add(t + BEAT / 2, r() < 0.55 ? 'drone' : 'ninja');
    if (bar >= 70 && k % 2 === 0) add(t + BEAT / 4, k === 0 ? 'shot' : 'fireball', { fromBoss: true });
  }
  add(barT(68, 8), 'tram');
  for (const { k, t } of beats(74, 75)) {
    add(t, k % 2 ? 'fireball' : 'shot', { fromBoss: true });
    add(t + BEAT / 2, 'drone');
  }
  return ev.sort((a, b) => a.arr - b.arr);
}
