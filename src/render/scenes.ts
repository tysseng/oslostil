// Scrolling backgrounds, one per part of the story.
import { GROUND, H, W, barT, rng } from '../config';
import { COLOR_T, MACHINES_T, SECTIONS, sectionAt, STATION_VX, VICTORIA_WAKE_T, machineCenter, machinesX, type SceneName } from '../timeline';
import trainGreenUrl from '../../assets/vehicles/hires/local-train-green.png';
import trainTomatoUrl from '../../assets/vehicles/hires/local-train-tomato-soup.png';
import airportExpressUrl from '../../assets/vehicles/hires/airport-express.png';
import busGreenUrl from '../../assets/vehicles/hires/bus-green.png';
import busRedUrl from '../../assets/vehicles/hires/bus-red.png';
import tokyoStreetUrl from '../../assets/backgrounds/tokyoslo-buildings.png';
import tokyoFarUrl from '../../assets/backgrounds/tokyoslo-far.png';
import { R, ctx, loadImage, ready, text } from './draw';
import { drawPlatformMachine } from './sprites';

export const SKY: Record<SceneName, [string, string]> = {
  station: ['#0b1030', '#26305e'], glitch: ['#170a2e', '#3c1a5c'], neon: ['#12002b', '#5b0f6e'], map: ['#06222b', '#0f5c5a'],
  map2: ['#2a0610', '#7a1430'], chaos: ['#2a0700', '#a33a06'], boss: ['#160012', '#5a0d2d'],
};
const GROUND_COLOR: Record<SceneName, string> = {
  station: '#2b2f45', glitch: '#2b1f45', neon: '#160022', boss: '#160012', map: '#0a2e33', map2: '#330a14', chaos: '#2a1206',
};
const PLACES = ['TJUVHOLMEN', 'KAMPEN', 'SKULLERUD', 'VULKAN', 'TORSHOV', 'VALHALL', 'ORMØYA', 'SINSEN'];
// Trains passing through Sandvika stasjon: the hi-res masters (100 px per metre), trimmed and drawn smoothly at
// TRAIN_PPM. Pixel-art versions (pixel_trains.py) are parked until new sprites are made.
const TRAIN_GREEN = loadImage(trainGreenUrl);
const TRAIN_TOMATO = loadImage(trainTomatoUrl);
const AIRPORT_EXPRESS = loadImage(airportExpressUrl);
/** game px per metre for the trains: a bit taller than before (8) but lower than the buses (BUS_PPM) */
const TRAIN_PPM = 10;
/** The trains run alongside the platform the girls walk on: the tops of the wheels are level with the
 * walking surface (GROUND), and the wheels themselves are hidden behind the platform edge. */
const WHEEL_M = 0.875; // metres from the wheel bottoms (the image's bottom row) up to the wheel tops
/** Screen x of the train's left end at time t, or null when it isn't running. */
type TrainPath = (t: number, width: number) => number | null;
interface TrainRun { img: HTMLImageElement; path: TrainPath }

/** Constant screen speed: at x0 at time t0, moving vx px/s (negative = towards the left). */
const passing = (t0: number, x0: number, vx: number): TrainPath => (t) => (t < t0 ? null : x0 + vx * (t - t0));

/**
 * Verse 1: the green train overtakes the girls, brakes, stops with its nose by the three machines,
 * then stands still at the platform – so it drifts off to the left with the station.
 * Worked out in the station's frame (where the machines are fixed), then converted to screen x.
 */
const STOP_T = MACHINES_T + 2.5;   // stands still from here (machines mid-screen)
const BRAKE = 5;                   // seconds of braking
const APPROACH = 150;              // px/s relative to the station before braking
const NOSE_STOP = W + 40 - 12;     // station-frame x where the nose stops: just before the machines
const stoppingTrain: TrainPath = (t, width) => {
  const before = STOP_T - t;
  let nose: number;
  if (before <= 0) nose = NOSE_STOP;
  else if (before <= BRAKE) nose = NOSE_STOP - (APPROACH * before * before) / (2 * BRAKE); // constant deceleration
  else nose = NOSE_STOP - (APPROACH * BRAKE) / 2 - APPROACH * (before - BRAKE);
  const x = nose - width - (t - MACHINES_T) * STATION_VX; // station frame → screen
  return t < barT(9) || t > barT(20) ? null : x;
};

const TRAIN_RUNS: TrainRun[] = [
  { img: TRAIN_GREEN, path: stoppingTrain },                         // verse 1: overtakes, brakes, stops by the machines
  { img: AIRPORT_EXPRESS, path: passing(41.0, W + 10, -620) },       // after the machines: whisks past right to left
  { img: TRAIN_TOMATO, path: passing(barT(26) + 0.5, W + 10, -210) }, // pre-chorus 1: another one the other way
];

function drawTrains(t: number): void {
  for (const run of TRAIN_RUNS) {
    if (!ready(run.img)) continue;
    const x = run.path(t, (meta(run.img).box[2] * TRAIN_PPM) / HIRES_PPM); // width in game px
    if (x !== null) drawVehicle(run.img, x, GROUND + WHEEL_M * TRAIN_PPM, TRAIN_PPM); // the ground strip, drawn later, covers the wheels
  }
}

/**
 * Intro: a bus terminal before Sandvika stasjon. Three buses wait at the stops (they move with the terminal
 * roof), and a red bus drives through behind them the other way, from the right edge out at the left.
 * They use the hi-res masters (100 px per metre, front on the right), trimmed to the bus and drawn smoothly.
 * The buses are drawn bigger than the trains (BUS_PPM) so the doors are taller than the girls; their wheel
 * bottoms are on the walking surface (GROUND).
 */
const BUS_GREEN = loadImage(busGreenUrl);
const BUS_RED = loadImage(busRedUrl);
const HIRES_PPM = 100;
/** game px per metre for the buses: a 2.7 m door becomes about 36 px, a bit taller than a girl */
const BUS_PPM = 13.2;
interface VehicleMeta { box: [number, number, number, number]; sign: [number, number, number, number] | null }
const metas = new Map<HTMLImageElement, VehicleMeta>();
/**
 * The bounding box of the non-transparent pixels (the bottom row is the wheel bottoms) and of the amber
 * destination sign (so a mirrored bus can have its sign drawn the right way round).
 */
function meta(img: HTMLImageElement): VehicleMeta {
  let m = metas.get(img);
  if (!m) {
    const c = document.createElement('canvas');
    c.width = img.naturalWidth; c.height = img.naturalHeight;
    const x = c.getContext('2d', { willReadFrequently: true })!;
    x.drawImage(img, 0, 0);
    const d = x.getImageData(0, 0, c.width, c.height).data;
    const box = [c.width, c.height, 0, 0], sign = [c.width, c.height, 0, 0];
    const grow = (b: number[], i: number, y: number) => { b[0] = Math.min(b[0], i); b[1] = Math.min(b[1], y); b[2] = Math.max(b[2], i); b[3] = Math.max(b[3], y); };
    for (let y = 0; y < c.height; y++) for (let i = 0; i < c.width; i++) {
      const o = (y * c.width + i) * 4;
      if (d[o + 3] > 8) grow(box, i, y);
      if (d[o + 3] > 200 && d[o] > 200 && d[o + 1] > 130 && d[o + 1] < 210 && d[o + 2] < 90) grow(sign, i, y); // amber text
    }
    const pad = 14; // the dark sign box around the text
    m = {
      box: [box[0], box[1], box[2] - box[0] + 1, box[3] - box[1] + 1],
      sign: sign[2] > 0 ? [sign[0] - pad, sign[1] - pad, sign[2] - sign[0] + 1 + 2 * pad, sign[3] - sign[1] + 1 + 2 * pad] : null,
    };
    metas.set(img, m);
  }
  return m;
}
/**
 * Draw a hi-res vehicle with its left end at screen x and its wheel bottoms on y. `flip` mirrors it (front on
 * the left) but keeps the destination sign readable.
 */
function drawVehicle(img: HTMLImageElement, x: number, y: number, ppm: number, flip = false): void {
  if (!ready(img)) return;
  const { box: [sx, sy, sw, sh], sign } = meta(img), k = ppm / HIRES_PPM, w = sw * k, h = sh * k;
  if (x > W || x + w < 0) return;
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  if (!flip) ctx.drawImage(img, sx, sy, sw, sh, x, y - h, w, h);
  else {
    ctx.save(); ctx.translate(x + w, 0); ctx.scale(-1, 1);
    ctx.drawImage(img, sx, sy, sw, sh, 0, y - h, w, h);
    ctx.restore();
    if (sign) {
      const [ax, ay, aw, ah] = sign;
      ctx.drawImage(img, ax, ay, aw, ah, x + (sx + sw - ax - aw) * k, y - h + (ay - sy) * k, aw * k, ah * k);
    }
  }
  ctx.imageSmoothingEnabled = false;
}
/** Buses waiting at the terminal stops: roof-layer x of the left end. The first is on screen at the start. */
const WAITING_BUSES: [HTMLImageElement, number][] = [[BUS_GREEN, 120], [BUS_RED, 560], [BUS_GREEN, 950]];
/** The red bus driving through behind them, right to left: start time and screen speed. */
const DRIVING_BUS = { t0: 1.5, vx: -170, ppm: BUS_PPM * 0.8 }; // a bit smaller: it's further away
function drawBuses(t: number, bx: number): void {
  if (t > barT(10) + 8) return;
  drawVehicle(BUS_RED, W + (t - DRIVING_BUS.t0) * DRIVING_BUS.vx, GROUND, DRIVING_BUS.ppm, true); // behind the waiting ones
  for (const [img, x] of WAITING_BUSES) drawVehicle(img, x - bx * ROOF_PARALLAX, GROUND, BUS_PPM);
}

/**
 * The canopy behind the girls, in sections with gaps, high enough for everything that flies to pass under it
 * or in front of it. During the intro it is the lower roof of the bus terminal (no signs; its last section is as
 * high as the station's, to make room for the arriving train). Sandvika stasjon's
 * higher platform canopy starts right after it: its first section scrolls in from the right as verse 1 begins
 * and the green train arrives, and it has «OSLO S» departure boards hanging under every section.
 */
interface RoofKind { y: number; section: number; gap: number; boards: boolean }
const TERMINAL: RoofKind = { y: 84, section: 190, gap: 60, boards: false }; // clears the buses (top ≈ 48 px up)
const STATION: RoofKind = { y: 76, section: 250, gap: 70, boards: true };
const ROOF_PARALLAX = 0.6, PILLAR_EVERY = 62, BOARD_EVERY = 84;
/** Roof-layer x where the station canopy starts. The intro scrolls at a constant speed, so it's exact. */
const STATION_START = SECTIONS[0].speed * barT(10) * ROOF_PARALLAX + W;
/** Number of terminal roof sections that fit before the station. */
const TERMINAL_COUNT = Math.floor((STATION_START - 30 + TERMINAL.gap) / (TERMINAL.section + TERMINAL.gap));

function drawPlatformRoof(bx: number): void {
  const scroll = bx * ROOF_PARALLAX - 30; // the first terminal section starts 30 px left of the screen
  for (let i = 0; i < TERMINAL_COUNT; i++) { // the last one is as high as the station, to make room for the train
    roofSection(i < TERMINAL_COUNT - 1 ? TERMINAL : { ...TERMINAL, y: STATION.y }, i * (TERMINAL.section + TERMINAL.gap) - scroll);
  }
  const period = STATION.section + STATION.gap;
  for (let i = Math.max(0, Math.floor((scroll + 30 - STATION_START) / period) - 1); ; i++) {
    const x = STATION_START - 30 + i * period - scroll;
    if (x > W) break;
    roofSection(STATION, x);
  }
}

function roofSection(k: RoofKind, x: number): void {
  x = Math.round(x);
  const y = k.y, L = k.section;
  if (x > W || x + L < -2) return;
  // pillars down to the platform (drawn first, under the roof)
  for (let px = x + 18; px < x + L - 10; px += PILLAR_EVERY) {
    R(px, y + 10, 4, GROUND - y - 10, '#252b52'); R(px + 1, y + 10, 1, GROUND - y - 10, '#3a4377');
    R(px - 2, y + 9, 8, 2, '#252b52'); // bracket
  }
  // the roof slab: light edge, body, dark underside with lamps
  R(x, y - 3, L, 2, '#6f7ab0');
  R(x, y - 1, L, 8, '#3a4377');
  R(x, y + 7, L, 3, '#1f2547');
  for (let lx = x + 10; lx < x + L - 6; lx += 24) R(lx, y + 10, 4, 1, '#ffe9a8');
  R(x - 2, y - 3, 2, 13, '#2a3160'); R(x + L, y - 3, 2, 13, '#2a3160'); // end caps
  if (k.boards) { // «OSLO S» departure boards hanging under the roof
    for (let b = x + 20; b + 44 < x + L - 4; b += BOARD_EVERY) {
      R(b + 6, y + 10, 1, 4, '#252b52'); R(b + 36, y + 10, 1, 4, '#252b52');
      R(b, y + 14, 44, 12, '#111');
      text('OSLO S', b + 3, y + 17, '#ffb000', 4, 'left', null);
    }
  }
}

/** positive modulo, for wrapping parallax layers */
const wrap = (v: number, m: number) => ((v % m) + m) % m;

/**
 * Tokyoslo: from the colour change (COLOR_T, 1:42.0) to the end of the song the city is Oslo with Asian
 * features (STAGE_DESIGN.md). Two pixel-art layers from tools/backgrounds/tokyoslo.py, bottom row on GROUND:
 * a far skyline and the street of landmarks with neon signs and the TOKYOSLO billboard.
 */
const TOKYO_FAR = loadImage(tokyoFarUrl);
const TOKYO_STREET = loadImage(tokyoStreetUrl);
const TOKYO_FAR_PARALLAX = 0.15, TOKYO_STREET_PARALLAX = 0.45;
/** screen x of the street's left end at COLOR_T, so the billboard is in view when Tokyoslo appears */
const TOKYO_STREET_X0 = 30;
let tokyoBx0: number | undefined;
/** background scroll at COLOR_T (the same integration as scrollAt in game.ts) */
function tokyoStartBx(): number {
  if (tokyoBx0 === undefined) {
    let x = 0;
    for (let u = 0; u < COLOR_T; u += 0.05) x += sectionAt(u).speed * Math.min(0.05, COLOR_T - u);
    tokyoBx0 = x;
  }
  return tokyoBx0;
}
/** Repeat an image horizontally across the screen with its bottom on GROUND. */
function tileLayer(img: HTMLImageElement, x0: number): void {
  if (!ready(img)) return;
  const w = img.naturalWidth;
  for (let x = wrap(x0, w) - w; x < W; x += w) ctx.drawImage(img, Math.round(x), GROUND - img.naturalHeight);
}
function drawTokyoslo(bx: number): void {
  const d = bx - tokyoStartBx();
  tileLayer(TOKYO_FAR, -d * TOKYO_FAR_PARALLAX);
  tileLayer(TOKYO_STREET, TOKYO_STREET_X0 - d * TOKYO_STREET_PARALLAX);
}

export function sky(c: [string, string]): void {
  const g = ctx.createLinearGradient(0, 0, 0, GROUND);
  g.addColorStop(0, c[0]); g.addColorStop(1, c[1]);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, GROUND);
}

/** @param bx background scroll distance  @param beatFlash 0..1, peaks on each beat */
export function drawScene(scene: SceneName, t: number, bx: number, beatFlash: number): void {
  const name: SceneName = scene === 'map' && t >= COLOR_T ? 'map2' : scene;
  sky(SKY[name]);
  const r = rng(7);
  if (name === 'station' || name === 'glitch') {
    for (let i = 0; i < 40; i++) { // snow
      const sx = (r() * W * 2 - bx * 0.1) % W, sy = (r() * GROUND + t * (20 + r() * 20)) % GROUND;
      R((sx + W) % W, sy, 1, 1, '#dfe8ff');
    }
    for (let i = 0; i < 8; i++) { // houses
      const hx = wrap(i * 70 - bx * 0.25, 560) - 60;
      R(hx, GROUND - 60, 50, 60, '#1a2148');
      for (let w = 0; w < 6; w++) R(hx + 6 + (w % 3) * 14, GROUND - 52 + Math.floor(w / 3) * 16, 6, 6, (i + w) % 3 ? '#f6d36b' : '#2a3366');
    }
    drawBuses(t, bx);
    drawTrains(t);
    drawPlatformRoof(bx);
    if (t > MACHINES_T && t < barT(20)) { // «tre blå maskiner» – the left one is Victoria until she wakes up
      for (let k = t < VICTORIA_WAKE_T ? 0 : 1; k < 3; k++) drawPlatformMachine(machineCenter(t, k), GROUND);
      if (t < VICTORIA_WAKE_T) text('VICTORIA', machinesX(t) + 1, GROUND - 42, '#ffcc33', 4, 'left');
    }

    if (name === 'glitch') {
      for (let i = 0; i < 6; i++) {
        const gy = (r() * GROUND + t * 90) % GROUND;
        ctx.globalAlpha = 0.35; R(0, gy, W, 2 + r() * 4, r() < 0.5 ? '#ff2bd6' : '#2bf0ff'); ctx.globalAlpha = 1;
      }
      if (Math.floor(t * 4) % 2) text('A-A-A-AUTOMAT', W / 2, 60, '#ff2bd6', 8, 'center');
    }
  } else if (name === 'neon' || name === 'boss') {
    R(W / 2 - 30, 40, 60, 30, name === 'boss' ? '#ff3366' : '#ff7ad9'); // sun
    for (let i = 0; i < 5; i++) R(W / 2 - 30, 52 + i * 4, 60, 1, SKY[name][1]);
    if (name === 'boss') drawTokyoslo(bx); // the boss fight is in Tokyoslo
    else {
      for (let i = 0; i < 12; i++) { // barcode skyline
        const hx = wrap(i * 40 - bx * 0.3, 480) - 40, hh = 30 + ((i * 17) % 50);
        R(hx, GROUND - hh, 26, hh, '#1a0533'); R(hx, GROUND - hh, 26, 1, '#ff4fd8');
      }
      const jx = wrap(300 - bx * 0.15, 700) - 100; // Holmenkollen jump
      ctx.strokeStyle = '#4ff3ff'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(jx, GROUND - 90); ctx.lineTo(jx + 60, GROUND - 10); ctx.stroke();
    }
    for (let i = 0; i < 12; i++) R(wrap(i * 32 - bx, 384) - 32, GROUND, 1, H - GROUND, '#ff4fd8'); // neon grid floor
  } else if (name === 'map' || name === 'map2') {
    const line = name === 'map' ? '#2fe0c0' : '#ff6b6b';
    for (let i = 0; i < 20; i++) {
      const mx = wrap(i * 50 - bx * 0.2, 1000) - 50;
      R(mx, 20 + ((i * 37) % 100), 40, 1, line); R(mx + 20, 20 + ((i * 37) % 100), 1, 30, line);
    }
    if (name === 'map2') drawTokyoslo(bx); // 1:42.0: the city turns into Tokyoslo
    else for (let i = 0; i < PLACES.length; i++) { // «hele Oslo på en skjerm» – place signs
      const sx = i * 260 + 200 - (bx - barT(42) * 145) * 0.8;
      if (sx > -80 && sx < W + 40) { R(sx, GROUND - 40, 2, 40, '#ccc'); R(sx - 30, GROUND - 52, 62, 12, '#0b3d91'); text(PLACES[i], sx + 1, GROUND - 49, '#fff', 4, 'center', null); }
    }
  } else if (name === 'chaos') { // «brennende trikker og busser på skrå» – in burning Tokyoslo
    drawTokyoslo(bx);
    for (let i = 0; i < 6; i++) {
      const bx2 = wrap(i * 110 - bx * 0.35, 660) - 80;
      ctx.save(); ctx.translate(bx2 + 40, GROUND - 20); ctx.rotate(-0.18 + (i % 3) * 0.12);
      R(-40, -20, 80, 22, i % 2 ? '#c0352b' : '#1b56c8');
      for (let w = 0; w < 5; w++) R(-36 + w * 15, -16, 10, 7, '#ffb347');
      ctx.restore();
      for (let k = 0; k < 6; k++) R(bx2 + 20 + k * 8, GROUND - 46 - ((k * 11 + Math.floor(t * 12)) % 18), 5, 8, k % 2 ? '#ff7b00' : '#ffd000');
    }
    for (let i = 0; i < 30; i++) R(wrap(r() * W - bx * 0.05, W), wrap(r() * GROUND - t * 40, GROUND), 1, 1, '#ffb347'); // embers
  }
  R(0, GROUND, W, H - GROUND, GROUND_COLOR[name]);
  R(0, GROUND, W, 2, beatFlash > 0.5 ? '#ffffff' : '#ffcc33');
  for (let i = 0; i < 11; i++) R(wrap(i * 32 - bx, 352) - 32, GROUND + 6, 16, 2, '#00000055');
}
