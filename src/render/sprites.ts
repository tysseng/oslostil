// Characters and enemies from sprite sheets; the boss and the tram are still drawn rectangle by rectangle.
import { GROUND, W } from '../config';
import { SHEET, SHEET_CELL, TRAM_PPM, type SheetKind } from '../schedule';
import type { Enemy } from '../state';
import { R, ctx, drawVehicle, loadImage, ready, text } from './draw';

import friendUrl from '../../assets/sprites/friend.png';
import victoriaUrl from '../../assets/sprites/victoria.png';
import automatUrl from '../../assets/sprites/automat.png';
import enemiesUrl from '../../assets/sprites/enemies.png';
import tramUrl from '../../assets/vehicles/hires/tram-new.png';
import bossUrl from '../../assets/sprites/kaostrikken.png';
import bossMeta from '../../assets/sprites/kaostrikken.json';

// The girls are pixel-art sprite sheets (made by tools/sprites/girls.py, editable in any pixel editor):
// 24×32 frames, row 0 = normal clothes, row 1 = ninja; feet on the bottom row, body centred on x = 12.
const FRAME_W = 24, FRAME_H = 32;
const FRAMES = ['idle0', 'idle1', 'run0', 'run1', 'run2', 'run3', 'jumpUp', 'jumpDown', 'slide', 'attack'] as const;
type FrameName = (typeof FRAMES)[number];

export type Girl = 'victoria' | 'friend';
const SHEETS: Record<Girl, HTMLImageElement> = { victoria: sheet(victoriaUrl), friend: sheet(friendUrl) };
/** ninja trim colour, used for the second line of the katana slash */
const TRIM: Record<Girl, string> = { victoria: '#ff3b6b', friend: '#a64dff' };

function sheet(url: string): HTMLImageElement {
  const img = new Image();
  img.src = url;
  return img;
}

export interface Pose { white?: boolean; ninja: boolean; air?: boolean; rising?: boolean; slide?: boolean; atk?: boolean; idle?: boolean }

function frameFor(t: number, st: Pose): FrameName {
  if (st.slide) return 'slide';
  if (st.atk) return 'attack';
  if (st.air) return st.rising ? 'jumpUp' : 'jumpDown';
  if (st.idle) return Math.floor(t * 2) % 2 ? 'idle1' : 'idle0';
  return FRAMES[2 + (Math.floor(t * 12) % 4)];
}

/** All-white copies of the girls' sheets, for the respawn flashing (made once the sheet has loaded). */
const WHITE: Partial<Record<Girl, HTMLCanvasElement>> = {};
function whiteSheet(girl: Girl): HTMLCanvasElement {
  let c = WHITE[girl];
  if (!c) {
    const img = SHEETS[girl];
    c = WHITE[girl] = document.createElement('canvas');
    c.width = img.naturalWidth; c.height = img.naturalHeight;
    const x = c.getContext('2d')!;
    x.drawImage(img, 0, 0);
    x.globalCompositeOperation = 'source-in';
    x.fillStyle = '#fff'; x.fillRect(0, 0, c.width, c.height);
  }
  return c;
}

/** One of the girls, feet at (x, y). */
export function drawGirl(girl: Girl, x: number, y: number, t: number, st: Pose): void {
  const sheetImg = SHEETS[girl];
  if (!sheetImg.complete || !sheetImg.naturalWidth) return;
  const img = st.white ? whiteSheet(girl) : sheetImg;
  const col = FRAMES.indexOf(frameFor(t, st)), row = st.ninja ? 1 : 0;
  ctx.drawImage(img, col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H, Math.round(x - 12), Math.round(y - FRAME_H), FRAME_W, FRAME_H);
  if (st.atk && st.ninja && !st.slide) { // katana slash
    ctx.strokeStyle = '#e8fbff'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x + 3, y - 14, 16, -1.2, 1.0); ctx.stroke();
    ctx.strokeStyle = TRIM[girl]; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(x + 3, y - 14, 13, -1.0, 0.8); ctx.stroke();
  }
}

/** Automat Victoria, the ticket-machine companion (sprite sheet from tools/sprites/automat.py). */
const AUTOMAT = loadImage(automatUrl);
const AUTOMAT_FRAMES = ['idle0', 'idle1', 'talk0', 'talk1', 'cheer0', 'cheer1', 'plain'] as const;
export type Mood = 'idle' | 'talk' | 'cheer';

/** An ordinary ticket machine on the platform (same style as Victoria, no face, no arms), base at (x, y). */
export function drawPlatformMachine(x: number, y: number): void {
  if (!ready(AUTOMAT)) return;
  ctx.drawImage(AUTOMAT, AUTOMAT_FRAMES.indexOf('plain') * 24, 0, 24, 32, Math.round(x - 12), Math.round(y) - 32, 24, 32);
}

/** Draws her with the base at (x, y), bobbing gently (bob = amplitude in px). */
export function drawMachine(x: number, y: number, t: number, mood: Mood = 'idle', bob = 2, flying = false): void {
  if (!ready(AUTOMAT)) return;
  const oy = Math.round(y + Math.sin(t * 3) * bob);
  if (flying) {
    for (const [i, offset] of [-5, 5].entries()) {
      const length = 7 + Math.floor((Math.sin(t * 39 + i * 2.4) + 1) * 2);
      R(x + offset - 2, oy - 1, 5, 4, '#ff5a24');
      R(x + offset - 1, oy + 3, 3, length - 4, '#ff5a24');
      R(x + offset, oy + length - 1, 1, 2, '#ff5a24');
      R(x + offset - 1, oy - 1, 3, 4, '#ffb52e');
      R(x + offset, oy + 3, 1, length - 4, '#ffb52e');
      R(x + offset, oy - 1, 1, 3, '#fff3a1');
    }
  }
  let frame: (typeof AUTOMAT_FRAMES)[number];
  if (mood === 'talk') frame = Math.floor(t * 8) % 2 ? 'talk0' : 'talk1';
  else if (mood === 'cheer') frame = Math.floor(t * 6) % 2 ? 'cheer0' : 'cheer1';
  else frame = t % 3.2 < 0.15 ? 'idle1' : 'idle0'; // blink every few seconds
  const col = AUTOMAT_FRAMES.indexOf(frame);
  ctx.drawImage(AUTOMAT, col * 24, 0, 24, 32, Math.round(x - 12), oy - 32, 24, 32);
}

/**
 * The tram obstacle: the new light-blue tram (hi-res master tram-new.png) at TRAM_PPM, mirrored so its front
 * leads as it comes at the girls (the sign stays readable). x = nose (left end), wheels on y.
 */
const TRAM_IMG = loadImage(tramUrl);

function drawTram(x: number, y: number, t: number): void {
  if (x > W && Math.floor(t * 8) % 2) text('!', W - 12, GROUND - 52, '#ff4040', 16); // warning before it rolls in
  drawVehicle(TRAM_IMG, x, y, TRAM_PPM, true);
}

/** Enemies, obstacles, pickups and boss shots: one sheet row per kind (tools/sprites/enemies.py). */
const ENEMIES = loadImage(enemiesUrl);

/** Draw one frame of an enemy-sheet sprite with its base at (x, y) (also used for the HUD ticket icon). */
export function drawEnemySprite(kind: SheetKind, x: number, y: number, t: number): void {
  if (!ready(ENEMIES)) return;
  const sp = SHEET[kind], f = Math.floor(t * sp.fps) % sp.frames, C = SHEET_CELL;
  ctx.drawImage(ENEMIES, f * C, sp.row * C, C, C, Math.round(x - C / 2), Math.round(y) - C, C, C);
}

export function drawEnemy(e: Enemy, x: number, t: number): void {
  const y = GROUND - e.y;
  if (e.type === 'tram') { drawTram(x, y, t); return; }
  if (e.type === 'ticket') { // tickets spin out of step with each other and bob gently
    drawEnemySprite('ticket', x, y + Math.round(Math.sin(t * 4 + e.arr * 3)), t + (e.arr * 1.7) % 1);
    return;
  }
  drawEnemySprite(e.type, x, y, t);
  if (e.type === 'bot' && e.label) text(e.label, x, y - SHEET.bot.h - 6, '#ffb000', 4, 'center');
}

/**
 * Kaos-trikken: the new light-blue tram transformed into a robot, facing left (sprite sheet + animation
 * table from tools/sprites/boss.py). Cells are bossMeta.w × bossMeta.h, feet on the bottom row,
 * the body centred on bossMeta.anchorX.
 */
const BOSS = loadImage(bossUrl);
export type BossAnim = keyof typeof bossMeta.anims;

export function drawBoss(x: number, hit: boolean, hp: number, max: number, anim: BossAnim = 'idle', at = 0): void {
  const y = GROUND, shake = hit ? Math.round((Math.random() - 0.5) * 3) : 0;
  const { w, h, anchorX } = bossMeta, a = bossMeta.anims[hit ? 'hit' : anim];
  const f = a.start + Math.min(a.count - 1, Math.max(0, Math.floor(at * a.count)));
  if (ready(BOSS)) ctx.drawImage(BOSS, f * w, 0, w, h, Math.round(x) - anchorX + shake, y - h, w, h);
  text('KAOS-TRIKKEN', x, y - h - 6, '#ff4f6b', 4, 'center');
  R(W / 2 - 60, 22, 120, 5, '#300'); R(W / 2 - 60, 22, (120 * hp) / max, 5, '#ff3366');
}
