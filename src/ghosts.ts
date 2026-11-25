import { GROUND } from './config';
import { TYPES, isGhost } from './schedule';
import { enemyHeight, enemyX, type GameState } from './state';
import { VALKYRIEN_CEILING, VALKYRIEN_FLOOR, exitX, stationEntryX } from './valkyrien';

export function updateGhosts(s: GameState, t: number, dt: number): void {
  for (const e of s.enemies) {
    if (!isGhost(e.type) || e.dead) continue;
    const x = enemyX(e, t);
    if (!e.ghost && ['underground', 'run-in'].includes(s.valkyrien.phase) && s.down <= 0
      && x <= s.p.x && x >= stationEntryX(t) - 50) {
      e.ghost = { x, base: GROUND - enemyHeight(e, t), vx: -e.rel, following: true };
    }
    const ghost = e.ghost;
    if (!ghost) continue;
    const following = !ghost.gaveUp && ['underground', 'run-in'].includes(s.valkyrien.phase);
    ghost.following = following;
    const targetVelocity = following ? Math.max(-65, Math.min(65, (s.p.x - ghost.x) * 2)) : -e.rel;
    ghost.vx += (targetVelocity - ghost.vx) * (1 - Math.exp(-4 * dt));
    ghost.x += ghost.vx * dt;
    const targetBase = following ? s.p.y - 8 : GROUND - e.y;
    ghost.base += (targetBase - ghost.base) * (1 - Math.exp(-2 * dt));
    ghost.base = Math.max(VALKYRIEN_CEILING + TYPES[e.type].h, Math.min(VALKYRIEN_FLOOR - 4, ghost.base));
    ghost.x = Math.max(stationEntryX(t) - 50 + TYPES[e.type].w / 2,
      Math.min(exitX(t) - TYPES[e.type].w / 2, ghost.x));
  }
}
