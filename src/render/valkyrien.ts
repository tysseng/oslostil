import { GROUND, H, W } from '../config';
import type { ValkyrienState } from '../valkyrien';
import { CHUTE_HALF_WIDTH, STAIRS_WIDTH, VALKYRIEN_BOTTOM, VALKYRIEN_CEILING, VALKYRIEN_DEPTH, VALKYRIEN_FLOOR, VALKYRIEN_HEIGHT, exitX, manholeX } from '../valkyrien';
import { R, ctx, text } from './draw';

function polygon(points: [number, number][], color: string): void {
  ctx.fillStyle = color;
  ctx.beginPath();
  points.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
  ctx.closePath();
  ctx.fill();
}

export function drawUndergroundFill(x = 0, y = H, width = W, height = VALKYRIEN_DEPTH + 30): void {
  const gradient = ctx.createLinearGradient(0, H, 0, VALKYRIEN_FLOOR + VALKYRIEN_BOTTOM);
  gradient.addColorStop(0, '#0a2e33');
  gradient.addColorStop(1, '#000');
  ctx.fillStyle = gradient;
  ctx.fillRect(x, y, width, height);
}

export function drawValkyrien(t: number, route?: ValkyrienState, minX = 0, maxX = W): void {
  const entry = manholeX(t), exit = exitX(t), left = Math.max(minX - 10, entry - 50);
  drawUndergroundFill(minX, H, maxX - minX);
  if (exit < minX - 100 || left > maxX) return;
  R(left, VALKYRIEN_CEILING, exit + 45 - left, VALKYRIEN_HEIGHT, '#898d8f');
  for (let x = entry - 50; x < Math.min(exit + 45, maxX + 70); x += 70) {
    if (x < minX - 70) continue;
    R(x, VALKYRIEN_CEILING, 1, VALKYRIEN_HEIGHT, '#64696c');
    R(x + 15, VALKYRIEN_CEILING + 6, 35, 3, '#e2e4da');
    R(x + 27, VALKYRIEN_FLOOR - 40, 8, 40, '#6b7073');
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
  ctx.rect(bottom, VALKYRIEN_CEILING, STAIRS_WIDTH + 10, VALKYRIEN_HEIGHT + 30);
  ctx.clip();
  polygon([[bottom, VALKYRIEN_FLOOR], [exit, GROUND], [exit, VALKYRIEN_FLOOR + 30], [bottom, VALKYRIEN_FLOOR + 30]], '#73787b');
  for (let i = 0; i < 20; i++) {
    const u = i / 20;
    R(bottom + STAIRS_WIDTH * u, VALKYRIEN_FLOOR - VALKYRIEN_DEPTH * u, STAIRS_WIDTH / 20, 2, '#c2c5c4');
  }
  ctx.restore();
  if (entry > minX - 30 && entry < maxX + 30) {
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

export function drawValkyrienBalustrade(t: number, minX = 0, maxX = W): void {
  const top = exitX(t), bottom = top - STAIRS_WIDTH;
  if (top < minX - 50 || bottom > maxX) return;
  ctx.save();
  ctx.beginPath();
  ctx.rect(bottom - 2, VALKYRIEN_CEILING, STAIRS_WIDTH + 4, VALKYRIEN_HEIGHT + 30);
  ctx.clip();
  polygon([[bottom, VALKYRIEN_FLOOR - 12], [top, GROUND - 12],
    [top, VALKYRIEN_FLOOR + 30], [bottom, VALKYRIEN_FLOOR + 30]], '#93989a');
  ctx.strokeStyle = '#d1d3d2';
  ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(bottom, VALKYRIEN_FLOOR - 12); ctx.lineTo(top, GROUND - 12); ctx.stroke();
  ctx.restore();
}

/** Opaque front wall deliberately hides the party while they emerge inside the house. */
export function drawValkyrienHouse(t: number, minX = 0, maxX = W): void {
  const x = exitX(t);
  if (x < minX - 100 || x > maxX + 80) return;
  R(x - 22, GROUND - 45, 60, 45, '#a6a7a2');
  polygon([[x - 28, GROUND - 45], [x + 8, GROUND - 68], [x + 44, GROUND - 45]], '#494f53');
  R(x - 13, GROUND - 36, 15, 17, '#516b73');
  R(x + 13, GROUND - 33, 19, 33, '#343a3d');
  R(x + 26, GROUND - 17, 2, 2, '#dad3a0');
  R(x - 24, GROUND - 2, 64, 2, '#d0d0c8');
}
