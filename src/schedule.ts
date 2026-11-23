// Enemy and pickup types for the layout in level.json.
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
