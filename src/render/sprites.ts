// Characters and enemies from sprite sheets; the boss and the tram are still drawn rectangle by rectangle.
import { GROUND, H, W } from '../config';
import { TREES, TREE_CELL_W, TREE_CELL_H, isTree, LAMPS, LAMP_CELL_W, LAMP_CELL_H, isLamp, PROPS, PROP_CELL_W, PROP_CELL_H, isProp, SHEET, SHEET_CELL, TRAM_PPM, type SheetKind } from '../schedule';
import { enemyHeight, enemyX, type Enemy } from '../state';
import { NINJA_CELL_W, NINJA_CELL_H, THUGS, fighterRow, isFighter, isNinjaKind, ninjaColumn } from '../ninjas';
import { PASSENGER_CELL_W, PASSENGER_CELL_H, PASSENGERS, isPassenger, passengerColumn } from '../passengers';
import { R, ctx, drawVehicle, loadImage, ready, text, meta, HIRES_PPM } from './draw';

import friendUrl from '../../assets/sprites/friend.png';
import victoriaUrl from '../../assets/sprites/victoria.png';
import automatUrl from '../../assets/sprites/automat.png';
import enemiesUrl from '../../assets/sprites/enemies.png';
import propsUrl from '../../assets/sprites/props.png';
import lampsUrl from '../../assets/sprites/lamps.png';
import lightsUrl from '../../assets/sprites/lamps-light.png';
import ninjasUrl from '../../assets/sprites/ninjas.png';
import thugsUrl from '../../assets/sprites/thugs.png';
import passengersUrl from '../../assets/sprites/passengers.png';
import propLightsUrl from '../../assets/sprites/props-light.png';
import treesUrl from '../../assets/sprites/trees.png';
import tramUrl from '../../assets/vehicles/hires/tram-new.png';
import tokyoTramUrl from '../../assets/vehicles/hires/tram-tokyo.png';
import { COLOR_T } from '../timeline';
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
 * The bidirectional light-blue tram (hi-res master tram-new.png) at TRAM_PPM, without mirroring.
 * x = leading end (left end), wheels on y.
 */
const TRAM_IMG = loadImage(tramUrl);
/** Tokyoslo's two-car green-and-cream tram (tools/vehicles/trams.py): same size, so the same physics. */
const TOKYO_TRAM_IMG = loadImage(tokyoTramUrl);

function drawTram(x: number, y: number, t: number, tokyo = false): void {
  if (x > W && Math.floor(t * 8) % 2) text('!', W - 12, GROUND - 52, '#ff4040', 16); // warning before it rolls in
  drawVehicle(tokyo && ready(TOKYO_TRAM_IMG) ? TOKYO_TRAM_IMG : TRAM_IMG, x, y, TRAM_PPM);
}

/** Enemies, obstacles, pickups and boss shots: one sheet row per kind (tools/sprites/enemies.py). */
const ENEMIES = loadImage(enemiesUrl);
const PROP_IMAGE = loadImage(propsUrl);
const LAMP_IMAGE = loadImage(lampsUrl), LIGHT_IMAGE = loadImage(lightsUrl);

export function drawLampLights(enemies: Enemy[], t: number): void {
  ctx.save();
  if (ready(TRAM_IMG)) {
    const [, , width, height] = meta(TRAM_IMG).box, scale = TRAM_PPM / HIRES_PPM;
    for (const e of enemies) {
      if (e.dead || e.type !== 'tram') continue;
      ctx.beginPath();
      ctx.rect(0, 0, W, H);
      ctx.rect(enemyX(e, t), GROUND - e.y - height * scale, width * scale, height * scale);
      ctx.clip('evenodd');
    }
  }
  for (const e of enemies) if (!e.dead) drawLampLight(e, enemyX(e, t));
  ctx.restore();
}
const NINJA_IMAGE = loadImage(ninjasUrl), THUG_IMAGE = loadImage(thugsUrl), PASSENGER_IMAGE = loadImage(passengersUrl);
const PROP_LIGHT_IMAGE = loadImage(propLightsUrl), TREE_IMAGE = loadImage(treesUrl);

/** Light from lamps and lit props (the dusk kiosk), drawn in front of the characters. */
export function drawLampLight(e: Enemy, x: number): void {
  if (isProp(e.type) && ready(PROP_LIGHT_IMAGE)) {
    ctx.save();
    ctx.globalCompositeOperation = 'screen';
    ctx.drawImage(PROP_LIGHT_IMAGE, 0, PROPS[e.type].row * PROP_CELL_H, PROP_CELL_W, PROP_CELL_H,
      Math.round(x - PROP_CELL_W / 2), Math.round(GROUND - e.y - PROP_CELL_H), PROP_CELL_W, PROP_CELL_H);
    ctx.restore();
    return;
  }
  if (!isLamp(e.type) || !ready(LIGHT_IMAGE)) return;
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  ctx.drawImage(LIGHT_IMAGE, 0, LAMPS[e.type].row * LAMP_CELL_H, LAMP_CELL_W, LAMP_CELL_H,
    Math.round(x - LAMP_CELL_W / 2), Math.round(GROUND - e.y - LAMP_CELL_H), LAMP_CELL_W, LAMP_CELL_H);
  ctx.restore();
}

/** Draw one frame of an enemy-sheet sprite with its base at (x, y) (also used for the HUD ticket icon). */
export function drawEnemySprite(kind: SheetKind, x: number, y: number, t: number): void {
  if (!ready(ENEMIES)) return;
  const sp = SHEET[kind], f = Math.floor(t * sp.fps) % sp.frames, C = SHEET_CELL;
  ctx.drawImage(ENEMIES, f * C, sp.row * C, C, C, Math.round(x - C / 2), Math.round(y) - C, C, C);
}

export function drawEnemy(e: Enemy, x: number, t: number): void {
  const y = GROUND - enemyHeight(e, t);
  if (e.type === 'tram') { drawTram(x, y, t, e.arr >= COLOR_T); return; } // trams due after 1:42 are Tokyoslo trams
  if (isLamp(e.type)) {
    if (ready(LAMP_IMAGE)) ctx.drawImage(LAMP_IMAGE, 0, LAMPS[e.type].row * LAMP_CELL_H, LAMP_CELL_W, LAMP_CELL_H,
      Math.round(x - LAMP_CELL_W / 2), Math.round(y - LAMP_CELL_H), LAMP_CELL_W, LAMP_CELL_H);
    return;
  }
  if (isFighter(e.type)) { // ninjas and thugs: run, crouch, jump and attack frames (src/ninjas.ts)
    const img = isNinjaKind(e.type) ? NINJA_IMAGE : THUG_IMAGE;
    if (ready(img)) ctx.drawImage(img, ninjaColumn(e.type, t - e.arr, t, e.arr) * NINJA_CELL_W,
      fighterRow(e.type) * NINJA_CELL_H, NINJA_CELL_W, NINJA_CELL_H,
      Math.round(x - NINJA_CELL_W / 2), Math.round(y - NINJA_CELL_H), NINJA_CELL_W, NINJA_CELL_H);
    return;
  }
  if (e.type === 'tagger_spray') { // the tagger painting the subway; his body sits at spray.body_x in the cell
    const sp = THUGS.spray, f = Math.floor(t * sp.fps + e.arr * 3) % sp.frames;
    if (ready(THUG_IMAGE)) ctx.drawImage(THUG_IMAGE, f * NINJA_CELL_W, sp.row * NINJA_CELL_H, NINJA_CELL_W, NINJA_CELL_H,
      Math.round(x - sp.body_x), Math.round(y - NINJA_CELL_H), NINJA_CELL_W, NINJA_CELL_H);
    return;
  }
  if (isPassenger(e.type)) { // zombie travellers; the label (ADULT, CHILD …) stays above them
    if (ready(PASSENGER_IMAGE)) ctx.drawImage(PASSENGER_IMAGE, passengerColumn(t - e.arr, t, e.arr) * PASSENGER_CELL_W,
      PASSENGERS.kinds[e.type].row * PASSENGER_CELL_H, PASSENGER_CELL_W, PASSENGER_CELL_H,
      Math.round(x - PASSENGER_CELL_W / 2), Math.round(y - PASSENGER_CELL_H), PASSENGER_CELL_W, PASSENGER_CELL_H);
    text(e.label ?? PASSENGERS.kinds[e.type].label, x, y - PASSENGERS.kinds[e.type].h - 6, '#ff4040', 4, 'center');
    return;
  }
  if (e.type === 'gull') { // each gull flaps out of step with the others
    drawEnemySprite('gull', x, y + (SHEET.gull.dy ?? 0), t + (e.arr * 0.37) % 1);
    return;
  }
  if (isTree(e.type)) {
    if (ready(TREE_IMAGE)) ctx.drawImage(TREE_IMAGE, 0, TREES[e.type].row * TREE_CELL_H, TREE_CELL_W, TREE_CELL_H,
      Math.round(x - TREE_CELL_W / 2), Math.round(y - TREE_CELL_H), TREE_CELL_W, TREE_CELL_H);
    return;
  }
  if (isProp(e.type)) { // animated props (lanterns, neon, steam) have one column per frame
    const pr = PROPS[e.type], f = Math.floor(t * pr.fps + e.arr * 3) % pr.frames;
    if (ready(PROP_IMAGE)) ctx.drawImage(PROP_IMAGE, f * PROP_CELL_W, pr.row * PROP_CELL_H, PROP_CELL_W, PROP_CELL_H,
      Math.round(x - PROP_CELL_W / 2), Math.round(y - PROP_CELL_H), PROP_CELL_W, PROP_CELL_H);
    return;
  }
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

// Upper-body offsets baked into each frame by tools/sprites/boss.py.
const BOSS_HEAD_OFFSETS: Record<BossAnim, readonly (readonly [number, number])[]> = {
  walk: [[0, -1], [0, 0], [0, 0], [0, -1], [0, 0], [0, 0]],
  idle: [[0, 0], [0, 0], [0, 1], [0, 1]],
  attack: [[1, 0], [2, 0], [3, 0], [1, 0]],
  hit: [[3, 0], [2, 1]],
};

export function drawBoss(x: number, hit: boolean, hp: number, max: number, anim: BossAnim = 'idle', at = 0): void {
  const y = GROUND, shake = hit ? Math.round((Math.random() - 0.5) * 3) : 0;
  const pose = hit ? 'hit' : anim;
  const { w, h, anchorX } = bossMeta, a = bossMeta.anims[pose];
  const frame = Math.min(a.count - 1, Math.max(0, Math.floor(at * a.count)));
  const f = a.start + frame, [headX, headY] = BOSS_HEAD_OFFSETS[pose][frame];
  if (ready(BOSS)) ctx.drawImage(BOSS, f * w, 0, w, h, Math.round(x) - anchorX + shake, y - h, w, h);
  const center = Math.round(x) + shake - 9 + headX, barY = y - h - 7 + headY, barWidth = 64;
  R(center - barWidth / 2 - 1, barY, barWidth + 2, 7, '#64b8f2');
  R(center - barWidth / 2, barY + 1, barWidth, 5, '#300');
  R(center - barWidth / 2, barY + 1, barWidth * Math.max(0, Math.min(1, hp / max)), 5, '#ff3366');
}
