import { GROUND, W } from '../config';
import type { ValkyrienState } from '../valkyrien';
import { CHUTE_HALF_WIDTH, STAIRS_WIDTH, VALKYRIEN_CEILING, VALKYRIEN_DEPTH, VALKYRIEN_FLOOR, exitX, manholeX } from '../valkyrien';
import { R, ctx, text } from './draw';

function polygon(points: [number, number][], color: string): void {
  ctx.fillStyle = color;
  ctx.beginPath();
  points.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
  ctx.closePath();
  ctx.fill();
}

export function drawValkyrien(t: number, route?: ValkyrienState): void {
  const entry = manholeX(t), exit = exitX(t), left = Math.max(-10, entry - 50);
  if (exit < -100 || left > W) return;
  R(left, GROUND + 30, exit + 45 - left, VALKYRIEN_DEPTH + 30, '#55595c');
  R(left, VALKYRIEN_CEILING, exit + 45 - left, 110, '#898d8f');
  for (let x = entry - 50; x < Math.min(exit + 45, W + 70); x += 70) {
    if (x < -70) continue;
    R(x, VALKYRIEN_CEILING, 1, 110, '#64696c');
    R(x + 15, VALKYRIEN_CEILING + 6, 35, 3, '#e2e4da');
    R(x + 27, VALKYRIEN_CEILING + 70, 8, 40, '#6b7073');
  }
  const sign = Math.max(25, Math.min(W - 100, entry + 170));
  R(sign, VALKYRIEN_CEILING + 26, 80, 17, '#35393c');
  text('VALKYRIEN', sign + 40, VALKYRIEN_CEILING + 31, '#eee', 7, 'center');
  R(left, VALKYRIEN_FLOOR, Math.max(0, exit - STAIRS_WIDTH - left), 6, '#bec1bf');
  R(left, VALKYRIEN_FLOOR + 6, Math.max(0, exit - left), 20, '#454a4d');
  R(left, VALKYRIEN_FLOOR - 2, Math.max(0, exit - STAIRS_WIDTH - left), 2, '#d6cd85');
  const bottom = exit - STAIRS_WIDTH;
  ctx.save();
  ctx.beginPath();
  ctx.rect(bottom, GROUND + 30, STAIRS_WIDTH + 10, VALKYRIEN_DEPTH);
  ctx.clip();
  polygon([[bottom, VALKYRIEN_FLOOR], [exit, GROUND], [exit, VALKYRIEN_FLOOR + 30], [bottom, VALKYRIEN_FLOOR + 30]], '#73787b');
  for (let i = 0; i < 20; i++) {
    const u = i / 20;
    R(bottom + STAIRS_WIDTH * u, VALKYRIEN_FLOOR - VALKYRIEN_DEPTH * u, STAIRS_WIDTH / 20, 2, '#c2c5c4');
  }
  ctx.restore();
  if (entry > -30 && entry < W + 30) {
    if (route?.openedAt !== undefined) {
      R(entry - CHUTE_HALF_WIDTH, GROUND, CHUTE_HALF_WIDTH * 2, VALKYRIEN_CEILING - GROUND, '#202529');
      R(entry - CHUTE_HALF_WIDTH - 2, GROUND, 2, VALKYRIEN_CEILING - GROUND, '#a4a8a9');
      R(entry + CHUTE_HALF_WIDTH, GROUND, 2, VALKYRIEN_CEILING - GROUND, '#a4a8a9');
    }
    const fall = route?.openedAt === undefined ? 0 : Math.min(1, (t - route.openedAt) / 0.22);
    ctx.save();
    ctx.translate(entry, GROUND + fall * (VALKYRIEN_CEILING - GROUND));
    ctx.scale(1, 1 - fall * 0.85);
    ctx.fillStyle = '#a5aaad';
    ctx.beginPath(); ctx.ellipse(0, -2, 22, 4, 0, 0, Math.PI * 2); ctx.fill();
    for (let x = -14; x <= 14; x += 7) R(x, -4, 2, 4, '#51585c');
    ctx.restore();
  }
}

export function drawValkyrienBalustrade(t: number): void {
  const top = exitX(t), bottom = top - STAIRS_WIDTH;
  if (top < -50 || bottom > W) return;
  ctx.save();
  ctx.beginPath();
  ctx.rect(bottom - 2, GROUND + 30, STAIRS_WIDTH + 4, VALKYRIEN_DEPTH + 30);
  ctx.clip();
  polygon([[bottom, VALKYRIEN_FLOOR - 12], [top, GROUND - 12],
    [top, VALKYRIEN_FLOOR + 30], [bottom, VALKYRIEN_FLOOR + 30]], '#93989a');
  ctx.strokeStyle = '#d1d3d2';
  ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(bottom, VALKYRIEN_FLOOR - 12); ctx.lineTo(top, GROUND - 12); ctx.stroke();
  ctx.restore();
}

/** Opaque front wall deliberately hides the party while they emerge inside the house. */
export function drawValkyrienHouse(t: number): void {
  const x = exitX(t);
  if (x < -100 || x > W + 80) return;
  R(x - 22, GROUND - 45, 60, 45, '#a6a7a2');
  polygon([[x - 28, GROUND - 45], [x + 8, GROUND - 68], [x + 44, GROUND - 45]], '#494f53');
  R(x - 13, GROUND - 36, 15, 17, '#516b73');
  R(x + 13, GROUND - 33, 19, 33, '#343a3d');
  R(x + 26, GROUND - 17, 2, 2, '#dad3a0');
  R(x - 24, GROUND - 2, 64, 2, '#d0d0c8');
}
