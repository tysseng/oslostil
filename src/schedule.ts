// Enemy and pickup types for the layout in level.json.
import sheetJson from '../assets/sprites/enemies.json';
import propsJson from '../assets/sprites/props.json';
import lampsJson from '../assets/sprites/lamps.json';
import treesJson from '../assets/sprites/trees.json';
import boardJson from '../assets/sprites/board-broken.json';
import powerupsJson from '../assets/sprites/powerups.json';
import ghostJson from '../assets/sprites/ghost.json';
import bedsheetGhostJson from '../assets/sprites/ghost-bedsheet.json';
import conductorGhostJson from '../assets/sprites/ghost-slime.json';
import stationAssetsJson from '../assets/sprites/station-assets.json';
import { NINJAS, THUGS, type NinjaKind, type ThugKind } from './ninjas';
import { PASSENGERS, type PassengerKind } from './passengers';

export type LampKind = keyof typeof lampsJson;
export const LAMPS = lampsJson;
export const LAMP_CELL_W = 96, LAMP_CELL_H = 80;
export const isLamp = (kind: EnemyKind): kind is LampKind => Object.hasOwn(LAMPS, kind);
export const STATION_ASSETS = stationAssetsJson;
export type StationAssetKind = keyof typeof STATION_ASSETS;
export const isStationAsset = (kind: EnemyKind): kind is StationAssetKind => Object.hasOwn(STATION_ASSETS, kind);
export const isWallPoster = (kind: EnemyKind): boolean => isStationAsset(kind) && STATION_ASSETS[kind].wall;
export const itemLayer = (kind: EnemyKind): number => isWallPoster(kind) ? -2 : isTree(kind) ? -1 : kind === 'tram' ? 1 : isStationAsset(kind) || isProp(kind) || isLamp(kind) || kind === 'board_broken' ? 0 : 2;
export const BROKEN_BOARD = boardJson;
export const BLOB_HOP = sheetJson.blob_hop;
export const GHOST = ghostJson;
export const GHOSTS = { ghost: ghostJson, ghost_bedsheet: bedsheetGhostJson, ghost_conductor: conductorGhostJson };
export type GhostKind = keyof typeof GHOSTS;
export const isGhost = (kind: EnemyKind): kind is GhostKind => Object.hasOwn(GHOSTS, kind);
export const BLOB_POP = sheetJson.blob_pop;
export const POWERUPS = powerupsJson;
export type PowerupKind = keyof typeof powerupsJson;
export const isPowerup = (kind: EnemyKind): kind is PowerupKind => Object.hasOwn(POWERUPS, kind);

/** Trees (tools/sprites/trees.py): scenery behind the characters, not standable. */
export type TreeKind = keyof typeof treesJson;
export const TREES = treesJson;
export const TREE_CELL_W = 100, TREE_CELL_H = 100;
export const isTree = (kind: EnemyKind): kind is TreeKind => Object.hasOwn(TREES, kind);

export type PropKind = keyof typeof propsJson;
export const PROPS = propsJson;
export const PROP_CELL_W = 112, PROP_CELL_H = 64;
export const isProp = (kind: EnemyKind): kind is PropKind => Object.hasOwn(PROPS, kind);

export type EnemyKind =
  | 'suitcase' | 'snow' | 'pigeon' | 'ticket' | 'blob' | 'blob_hop' | 'board_broken' | 'ninja' | 'drone' | 'gull' | 'ghost'
  | 'tram' | 'bot' | 'terminal' | 'fire' | 'coin' | 'shot' | 'fireball' | GhostKind | PowerupKind | PropKind | LampKind | NinjaKind | ThugKind | PassengerKind | 'tagger_spray' | TreeKind | StationAssetKind;

/** One row of the enemy sprite sheet (assets/sprites/enemies.png, 32 × 32 bottom-centred cells). */
export interface SheetRow {
  row: number;
  frames: number;
  fps: number;
  /** visible size in game px */
  w: number;
  h: number;
  /** draw the cell this many px below the base (the gull: its wings sweep far below the body) */
  dy?: number;
}
/** Enemies and pickups use this sheet; trams and props have separate artwork. */
export type SheetKind = Exclude<EnemyKind, GhostKind | 'tram' | 'board_broken' | PowerupKind | PropKind | LampKind | Exclude<NinjaKind, 'ninja'> | ThugKind | PassengerKind | 'tagger_spray' | TreeKind | StationAssetKind>;
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

/** Solid, harmless scenery types for every entry of a props/lamps/trees JSON table. */
function scenery<K extends string>(table: Record<K, { w: number; h: number }>): Record<K, EnemyType> {
  return Object.fromEntries((Object.entries(table) as [K, { w: number; h: number }][])
    .map(([k, v]) => [k, { w: v.w, h: v.h, y: 0, hp: 0, own: 0, solid: true }])) as Record<K, EnemyType>;
}

/** Hitbox size (w, h) comes from the sprite's visible size in enemies.json. */
const fromSheet = (k: SheetKind, rest: Omit<EnemyType, 'w' | 'h'>): EnemyType => ({ w: SHEET[k].w, h: SHEET[k].h, ...rest });

export const TYPES: Record<EnemyKind, EnemyType> = {
  suitcase: fromSheet('suitcase', { y: 0, hp: 1, own: 0 }),
  snow: fromSheet('snow', { y: 0, hp: 1, own: 0 }),
  pigeon: fromSheet('pigeon', { y: 26, hp: 1, own: 40 }),
  ticket: fromSheet('ticket', { y: 34, hp: 0, own: 0, pickup: true }), // collected = one more throw
  blob: fromSheet('blob', { y: 0, hp: 1, own: 20 }),
  ghost: { w: GHOST.w, h: GHOST.h, y: 30, hp: 2, own: 0 },
  ghost_bedsheet: { w: GHOSTS.ghost_bedsheet.w, h: GHOSTS.ghost_bedsheet.h, y: 30, hp: 2, own: 0 },
  ghost_conductor: { w: GHOSTS.ghost_conductor.w, h: GHOSTS.ghost_conductor.h, y: 30, hp: 2, own: 0 },
  blob_hop: fromSheet('blob_hop', { y: 0, hp: 1, own: 40 * 5 / 8 }),
  board_broken: { w: BROKEN_BOARD.w, h: Math.max(...BROKEN_BOARD.top), y: 0, hp: 0, own: 0, solid: true },
  ninja: { ...NINJAS.kinds.ninja, y: 0, hp: 1, own: 50 },
  ninja_oni: { ...NINJAS.kinds.ninja_oni, y: 0, hp: 2, own: 45 },
  ninja_kasa: { ...NINJAS.kinds.ninja_kasa, y: 0, hp: 1, own: 60 },
  thug: { ...THUGS.kinds.thug, y: 0, hp: 2, own: 40 },
  punk: { ...THUGS.kinds.punk, y: 0, hp: 1, own: 55 },
  tagger: { ...THUGS.kinds.tagger, y: 0, hp: 1, own: 50 },
  /** the tagger in spray mode, painting the subway: stands still */
  tagger_spray: { w: THUGS.kinds.tagger.w, h: THUGS.kinds.tagger.h, y: 0, hp: 1, own: 0 },
  adult: { ...PASSENGERS.kinds.adult, y: 0, hp: 2, own: 25 },
  child: { ...PASSENGERS.kinds.child, y: 0, hp: 1, own: 35 },
  senior: { ...PASSENGERS.kinds.senior, y: 0, hp: 2, own: 15 },
  student: { ...PASSENGERS.kinds.student, y: 0, hp: 2, own: 25 },
  drone: fromSheet('drone', { y: 30, hp: 1, own: 30 }),
  gull: fromSheet('gull', { y: 30, hp: 1, own: 30 }),
  tram: { w: TRAM_LEN, h: TRAM_ROOF, y: 0, hp: 99, own: TRAM_OWN, solid: true },
  bot: fromSheet('bot', { y: 0, hp: 2, own: 25 }),
  terminal: fromSheet('terminal', { y: 30, hp: 0, own: 0, pickup: true }),
  fire: fromSheet('fire', { y: 0, hp: 99, own: 0, solid: true }),
  coin: fromSheet('coin', { y: 38, hp: 0, own: 0, pickup: true }),
  shot: fromSheet('shot', { y: 6, hp: 1, own: 120 }),
  fireball: fromSheet('fireball', { y: 28, hp: 1, own: 120 }),
  // every prop, lamp and tree in its JSON becomes solid scenery (new art needs no code change)
  ...scenery(PROPS), ...scenery(LAMPS), ...scenery(TREES), ...scenery(STATION_ASSETS),
  ...Object.fromEntries((Object.keys(POWERUPS) as PowerupKind[]).map(kind =>
    [kind, { w: POWERUPS[kind].w, h: POWERUPS[kind].h, y: 30, hp: 0, own: 0, pickup: true }])) as Record<PowerupKind, EnemyType>,
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
  /** Tree depth: 0 is farthest away, 1 is nearest. */
  depth?: number;
  hop?: 'low' | 'high' | 'double';
}

export function treeDepth(e: ScheduledEvent): number {
  if (e.depth !== undefined) return e.depth;
  const seed = Math.imul(Math.round(e.arr * 1000), 73856093) ^ Math.imul(Math.round((e.y ?? 0) * 1000), 19349663)
    ^ Math.imul(isTree(e.type) ? TREES[e.type].row + 1 : 0, 83492791);
  return (seed >>> 0) / 0xffffffff;
}
