import { GROUND } from './config';
import defaultLevel from './level.json';
import { isTree, treeDepth, TYPES, type ScheduledEvent } from './schedule';

function isEvent(value: unknown): value is ScheduledEvent {
  if (!value || typeof value !== 'object') return false;
  const e = value as Record<string, unknown>;
  return typeof e.type === 'string' && Object.hasOwn(TYPES, e.type)
    && typeof e.arr === 'number' && Number.isFinite(e.arr)
    && (e.y === undefined || (typeof e.y === 'number' && Number.isFinite(e.y) && e.y >= 0 && e.y <= GROUND))
    && (e.rel === undefined || (typeof e.rel === 'number' && Number.isFinite(e.rel) && e.rel > 0))
    && (e.depth === undefined || (typeof e.depth === 'number' && Number.isFinite(e.depth) && e.depth >= 0 && e.depth <= 1))
    && (e.hop === undefined || e.hop === 'low' || e.hop === 'high' || e.hop === 'double')
    && (e.label === undefined || typeof e.label === 'string')
    && (e.fromBoss === undefined || typeof e.fromBoss === 'boolean');
}

/** Validate external data and keep only fields understood by the game. */
export function parseLevel(value: unknown): ScheduledEvent[] {
  if (!Array.isArray(value) || !value.every(isEvent)) {
    throw new Error('Expected a JSON array of level items with a valid type, arrival time and optional height/speed.');
  }
  return value.map(({ type, arr, y, rel, label, fromBoss, depth, hop }) => {
    const e: ScheduledEvent = { type, arr, y, rel, label, fromBoss, hop };
    if (isTree(type)) e.depth = treeDepth({ ...e, depth });
    return e;
  });
}

/** Each load returns a fresh copy of the bundled layout. */
export function loadDefaultLevel(): ScheduledEvent[] {
  return parseLevel(defaultLevel);
}
