// Scrolling backgrounds, one per part of the story.
import { GROUND, H, W, barT, rng } from '../config';
import { COLOR_T, MACHINES_T, SECTIONS, sectionAt, STATION_VX, VICTORIA_WAKE_T, machineCenter, platformMachines, subwayNose, subwayTaggerX, TAGGER_RUN, TAGGER_SPRAY, type SceneName } from '../timeline';
import trainGreenUrl from '../../assets/vehicles/hires/local-train-green.png';
import trainTomatoUrl from '../../assets/vehicles/hires/local-train-tomato-soup.png';
import airportExpressUrl from '../../assets/vehicles/hires/airport-express.png';
import subwayUrl from '../../assets/vehicles/hires/subway-new.png';
import busGreenUrl from '../../assets/vehicles/hires/bus-green.png';
import busRedUrl from '../../assets/vehicles/hires/bus-red.png';
import tokyoStreetUrl from '../../assets/backgrounds/tokyoslo-buildings.png';
import tokyoFarUrl from '../../assets/backgrounds/tokyoslo-far.png';
import classicStreetUrl from '../../assets/backgrounds/oslo-classic-buildings.png';
import tokyoStreetV2Url from '../../assets/backgrounds/tokyoslo-v2-buildings.png';
import burningTramUrl from '../../assets/vehicles/hires/tram-burning.png';
import burningTram from '../../assets/vehicles/hires/tram-burning.json';
import fireUrl from '../../assets/sprites/fire.png';
import fireMeta from '../../assets/sprites/fire.json';
import { HIRES_PPM, R, ctx, drawVehicle, horizontalBounds, loadImage, meta, ready, text } from './draw';
import { drawEnemy, drawPlatformMachine } from './sprites';
import { createEnemy } from '../state';

export const SKY: Record<SceneName, [string, string]> = {
  station: ['#0b1030', '#26305e'], glitch: ['#170a2e', '#3c1a5c'], neon: ['#12002b', '#5b0f6e'], map: ['#06222b', '#0f5c5a'],
  map2: ['#2a0610', '#7a1430'], chaos: ['#2a0700', '#a33a06'], boss: ['#160012', '#5a0d2d'],
};
const GROUND_COLOR: Record<SceneName, string> = {
  station: '#2b2f45', glitch: '#2b1f45', neon: '#160022', boss: '#160012', map: '#0a2e33', map2: '#330a14', chaos: '#2a1206',
};
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

/**
 * Level 4 (bar 42, «LANGUAGE CHANGED»): a 3-car T-bane train arrives from the left and comes to a stop.
 * Worked out in the frame of the map background (it rests at SUBWAY.rest px/s to the left on screen):
 * it comes in at `approach` px/s, brakes evenly for `brake` s and then stands still, drifting off with the city.
 * The nose peaks just inside the right edge.
 */
const SUBWAY_IMG = loadImage(subwayUrl);
function drawSubway(t: number, taggerStoppedAt?: number): void {
  if (t < barT(42) - 0.5 || !ready(SUBWAY_IMG)) return;
  const nose = subwayNose(t);
  const w = (meta(SUBWAY_IMG).box[2] * TRAIN_PPM) / HIRES_PPM;
  drawVehicle(SUBWAY_IMG, nose - w, GROUND + WHEEL_M * TRAIN_PPM, TRAIN_PPM); // the ground strip covers the wheels
  const paintTime = Math.min(t, taggerStoppedAt ?? t) - TAGGER_SPRAY, target = nose - 70;
  if (paintTime >= 0) {
    ctx.save();
    ctx.beginPath();
    ctx.rect(nose - w, GROUND - 26, w - 24, 24);
    ctx.clip();
    for (let i = 0; i < 5; i++) {
      const progress = Math.max(0, Math.min(1, (paintTime - i * 0.18) / 0.18));
      if (!progress) continue;
      const x = target - 24 + i * 5, y = GROUND - 24 + (i % 2) * 3;
      R(x, y, 3, 16 * progress, '#ff2bd6');
      if (progress === 1) R(x + 1, y + 15, 1, 3 + i % 3, '#d51ca5');
    }
    ctx.restore();
  }
  const x = subwayTaggerX(t);
  if (x !== null && taggerStoppedAt === undefined) {
    const tagger = createEnemy({ type: t >= TAGGER_SPRAY ? 'tagger_spray' : 'tagger', arr: TAGGER_RUN - 1 });
    drawEnemy(tagger, x, t);
  }
}

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
/** game px per metre for the buses: a 2.7 m door becomes about 36 px, a bit taller than a girl */
const BUS_PPM = 13.2;
/** Buses waiting at the terminal stops: roof-layer x of the left end. The first is on screen at the start. */
const WAITING_BUSES: [HTMLImageElement, number][] = [[BUS_GREEN, 120], [BUS_RED, 560], [BUS_GREEN, 950]];
/** The red bus driving through behind them, right to left: start time and screen speed. */
const DRIVING_BUS = { t0: 1.5, vx: -170, ppm: BUS_PPM * 0.8 }; // a bit smaller: it's further away
function drawBuses(t: number, bx: number): void {
  if (t > barT(10) + 8) return;
  const bounce = Math.sin((t - DRIVING_BUS.t0) * 18) * 0.35;
  ctx.save();
  ctx.filter = 'brightness(80%)';
  drawVehicle(BUS_RED, W + (t - DRIVING_BUS.t0) * DRIVING_BUS.vx, GROUND + bounce, DRIVING_BUS.ppm, true); // behind the waiting ones
  ctx.restore();
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
  const bounds = horizontalBounds();
  const scroll = bx * ROOF_PARALLAX - 30; // the first terminal section starts 30 px left of the screen
  for (let i = 0; i < TERMINAL_COUNT; i++) { // the last one is as high as the station, to make room for the train
    roofSection(i < TERMINAL_COUNT - 1 ? TERMINAL : { ...TERMINAL, y: STATION.y }, i * (TERMINAL.section + TERMINAL.gap) - scroll);
  }
  const period = STATION.section + STATION.gap;
  for (let i = Math.max(0, Math.floor((scroll + 30 - STATION_START + bounds.left) / period) - 1); ; i++) {
    const x = STATION_START - 30 + i * period - scroll;
    if (x > bounds.right) break;
    roofSection(STATION, x);
  }
}

function roofSection(k: RoofKind, x: number): void {
  x = Math.round(x);
  const y = k.y, L = k.section;
  const bounds = horizontalBounds();
  if (x > bounds.right || x + L < bounds.left - 2) return;
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

function* repeatedX(x: number, period: number, width: number): Generator<number> {
  const { left, right } = horizontalBounds();
  for (let n = Math.ceil((left - width - x) / period); x + n * period < right; n++) yield x + n * period;
}

/**
 * Level 4 and Tokyoslo: one street of classic Oslo buildings in two styles (tools/backgrounds/karljohan.py).
 * Classic British-style Oslo under the teal sky from bar 42; at the colour change (COLOR_T, 1:42.0) every
 * building swaps to its Tokyoslo style in place, and Tokyoslo stays for the rest of the song (STAGE_DESIGN.md).
 * Both images share one layout and one scroll anchor (the start of level 4), so nothing moves at the switch.
 * Layers are pixel art, bottom row on GROUND.
 */
const CLASSIC_STREET = loadImage(classicStreetUrl);
const TOKYO_STREET_V2 = loadImage(tokyoStreetV2Url);
/** the first Tokyoslo draft (tools/backgrounds/tokyoslo.py), kept for comparison: set TOKYO_VERSION to 1 */
const TOKYO_STREET_V1 = loadImage(tokyoStreetUrl);
const TOKYO_FAR = loadImage(tokyoFarUrl);
const TOKYO_VERSION = 2 as 1 | 2;
const STREET_PARALLAX = 0.45, TOKYO_FAR_PARALLAX = 0.15;
/** screen x of the street's left end when level 4 starts */
const STREET_X0 = 40;
/** background scroll at a song time (the same integration as scrollAt in game.ts), cached */
const bxCache = new Map<number, number>();
function bxAt(t: number): number {
  let x = bxCache.get(t);
  if (x === undefined) {
    x = 0;
    for (let u = 0; u < t; u += 0.05) x += sectionAt(u).speed * Math.min(0.05, t - u);
    bxCache.set(t, x);
  }
  return x;
}
/** Repeat an image horizontally across the screen with its bottom on GROUND. */
function tileLayer(img: HTMLImageElement, x0: number): void {
  if (!ready(img)) return;
  const w = img.naturalWidth;
  for (const x of repeatedX(x0, w, w)) ctx.drawImage(img, Math.round(x), GROUND - img.naturalHeight);
}
const streetX = (bx: number): number => STREET_X0 - (bx - bxAt(barT(42))) * STREET_PARALLAX;
function drawClassicOslo(bx: number): void {
  tileLayer(CLASSIC_STREET, streetX(bx));
}
function drawTokyoslo(bx: number): void {
  tileLayer(TOKYO_FAR, -(bx - bxAt(COLOR_T)) * TOKYO_FAR_PARALLAX);
  if (TOKYO_VERSION === 2) tileLayer(TOKYO_STREET_V2, streetX(bx));
  else tileLayer(TOKYO_STREET_V1, 30 - (bx - bxAt(COLOR_T)) * 0.45);
}

export function sky(c: [string, string]): void {
  const { left, right } = horizontalBounds();
  const g = ctx.createLinearGradient(0, 0, 0, GROUND);
  g.addColorStop(0, c[0]); g.addColorStop(1, c[1]);
  ctx.fillStyle = g; ctx.fillRect(left, 0, right - left, GROUND);
}

/** @param bx background scroll distance  @param beatFlash 0..1, peaks on each beat */
// ── Kollektivkaos: wrecked, burning trams (vector tram, darkened) with pixel-art flame sprites on top
const BURNING_TRAM = loadImage(burningTramUrl), FIRE = loadImage(fireUrl);
const BT_PPM = 6, BT_PERIOD = 760, BT_PARALLAX = 0.35;
const BT_SET = [ // x within the period, tilt, mirrored, rail height above GROUND
  { x: 0, rot: -0.12, flip: false, lift: 10 },
  { x: 200, rot: 0.08, flip: true, lift: 4 },
  { x: 390, rot: -0.05, flip: false, lift: 14 },
  { x: 580, rot: 0.13, flip: true, lift: 6 },
];
let btDark: HTMLCanvasElement | null = null;
function darkTram(): HTMLCanvasElement | null { // pre-darkened once so the trams stay behind the action
  if (btDark || !ready(BURNING_TRAM)) return btDark;
  const c = document.createElement('canvas'); c.width = BURNING_TRAM.naturalWidth; c.height = BURNING_TRAM.naturalHeight;
  const x = c.getContext('2d')!;
  x.drawImage(BURNING_TRAM, 0, 0);
  x.globalCompositeOperation = 'source-atop'; x.fillStyle = 'rgba(20,6,10,0.42)'; x.fillRect(0, 0, c.width, c.height);
  return (btDark = c);
}
function fireSprite(kind: keyof typeof fireMeta.sprites, gx: number, gy: number, t: number, seed: number): void {
  const sp = fireMeta.sprites[kind], c = fireMeta.cell;
  const f = Math.floor(t * sp.fps + seed * 3.7) % sp.frames;
  ctx.drawImage(FIRE, f * c, sp.row * c, c, c, Math.round(gx - c / 2), Math.round(gy - c), c, c);
}
function drawBurningTrams(t: number, bx: number): void {
  const img = darkTram();
  if (!img || !ready(FIRE)) return;
  const u = BT_PPM / burningTram.unitsPerMetre, k = BT_PPM / HIRES_PPM, len = burningTram.length * u;
  const [vx, vy] = [-10, -40], rail = burningTram.rail; // SVG viewBox origin; PNG is 2 px per SVG unit
  for (let i = 0; i < BT_SET.length; i++) {
    const s = BT_SET[i];
    for (const x0 of repeatedX(s.x - bx * BT_PARALLAX - len, BT_PERIOD, len)) {
      const cx = x0 + len / 2, cy = GROUND - s.lift, cos = Math.cos(s.rot), sin = Math.sin(s.rot), m = s.flip ? -1 : 1;
      ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
      ctx.save(); ctx.translate(cx, cy); ctx.rotate(s.rot); ctx.scale(m, 1);
      ctx.drawImage(img, -len / 2 + vx * u, (vy - rail) * u, img.width * k, img.height * k);
      ctx.restore();
      ctx.imageSmoothingEnabled = false;
      const at = (ax: number, ay: number): [number, number] => { // tram SVG point → game px, following the tilt
        const lx = m * (ax * u - len / 2), ly = (ay - rail) * u;
        return [cx + lx * cos - ly * sin, cy + lx * sin + ly * cos];
      };
      burningTram.smoke.forEach((p, j) => { // puffs rise and drift, two per anchor, staggered
        for (let n = 0; n < 2; n++) {
          const life = (t * 0.6 + j * 0.37 + n * 0.5 + i * 0.13) % 1, [gx, gy] = at(p.x, p.y);
          const sp = fireMeta.sprites.smoke, c = fireMeta.cell, f = Math.min(sp.frames - 1, Math.floor(life * sp.frames));
          ctx.drawImage(FIRE, f * c, sp.row * c, c, c, Math.round(gx - c / 2 + life * 10), Math.round(gy - c - life * 26), c, c);
        }
      });
      burningTram.flames.forEach((p, j) => { const [gx, gy] = at(p.x, p.y); fireSprite(p.kind as 'big' | 'small', gx, gy, t, i * 7 + j); });
    }
  }
}

export function drawScene(scene: SceneName, t: number, bx: number, beatFlash: number, taggerStoppedAt?: number): void {
  const { left, right } = horizontalBounds();
  const name: SceneName = scene === 'map' && t >= COLOR_T ? 'map2' : scene;
  sky(SKY[name]);
  const r = rng(7);
  if (name === 'station' || name === 'glitch') {
    for (let i = 0; i < 40; i++) { // snow
      const sx = (r() * W * 2 - bx * 0.1) % W, sy = (r() * GROUND + t * (20 + r() * 20)) % GROUND;
      for (const x of repeatedX((sx + W) % W, W, 1)) R(x, sy, 1, 1, '#dfe8ff');
    }
    for (let i = 0; i < 8; i++) { // houses
      for (const hx of repeatedX(i * 70 - bx * 0.25 - 60, 560, 50)) {
        R(hx, GROUND - 60, 50, 60, '#1a2148');
        for (let w = 0; w < 6; w++) R(hx + 6 + (w % 3) * 14, GROUND - 52 + Math.floor(w / 3) * 16, 6, 6, (i + w) % 3 ? '#f6d36b' : '#2a3366');
      }
    }
    drawBuses(t, bx);
    drawTrains(t);
    drawPlatformRoof(bx);
    if (t > MACHINES_T && t < barT(20)) { // «tre blå maskiner» – the left one is Victoria until she wakes up
      for (const k of platformMachines(t)) drawPlatformMachine(machineCenter(t, k), GROUND);
      if (t < VICTORIA_WAKE_T) text('VICTORIA', machineCenter(t), GROUND - 42, '#ffcc33', 4, 'center');
    }

    if (name === 'glitch') {
      for (let i = 0; i < 6; i++) {
        const gy = (r() * GROUND + t * 90) % GROUND;
        ctx.globalAlpha = 0.35; R(left, gy, right - left, 2 + r() * 4, r() < 0.5 ? '#ff2bd6' : '#2bf0ff'); ctx.globalAlpha = 1;
      }
      if (Math.floor(t * 4) % 2) text('A-A-A-AUTOMAT', W / 2, 60, '#ff2bd6', 8, 'center');
    }
  } else if (name === 'neon' || name === 'boss') {
    ctx.save();
    ctx.beginPath();
    ctx.arc(W / 2, 55, 30, 0, Math.PI * 2);
    ctx.clip();
    const background = ctx.createLinearGradient(0, 0, 0, GROUND);
    background.addColorStop(0, SKY[name][0]);
    background.addColorStop(1, SKY[name][1]);
    ctx.fillStyle = background;
    ctx.fillRect(W / 2 - 31, 24, 62, 62);
    ctx.fillStyle = name === 'boss' ? '#ff3366' : '#ff7ad9';
    // Draw only the solid bands so clipped edge pixels cannot leave a pink rim in the gaps.
    for (const [y, height] of [[25, 27], [53, 4], [59, 4], [66, 4], [74, 4]]) {
      ctx.fillRect(W / 2 - 30, y, 60, height);
    }
    ctx.restore();
    if (name === 'boss') drawTokyoslo(bx); // the boss fight is in Tokyoslo
    else {
      for (let i = 0; i < 12; i++) { // barcode skyline
        const hh = 30 + ((i * 17) % 50);
        for (const hx of repeatedX(i * 40 - bx * 0.3 - 40, 480, 26)) {
          R(hx, GROUND - hh, 26, hh, '#1a0533'); R(hx, GROUND - hh, 26, 1, '#ff4fd8');
        }
      }
      for (const jx of repeatedX(200 - bx * 0.15, 700, 60)) { // Holmenkollen jump
        ctx.strokeStyle = '#4ff3ff'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(jx, GROUND - 90); ctx.lineTo(jx + 60, GROUND - 10); ctx.stroke();
      }
    }
    for (let i = 0; i < 12; i++) for (const x of repeatedX(i * 32 - bx - 32, 384, 1)) R(x, GROUND, 1, H - GROUND, '#ff4fd8'); // neon grid floor
  } else if (name === 'map' || name === 'map2') {
    const line = name === 'map' ? '#2fe0c0' : '#ff6b6b';
    for (let i = 0; i < 20; i++) {
      for (const mx of repeatedX(i * 50 - bx * 0.2 - 50, 1000, 40)) {
        R(mx, 20 + ((i * 37) % 100), 40, 1, line); R(mx + 20, 20 + ((i * 37) % 100), 1, 30, line);
      }
    }
    // classic British-style Oslo, then at 1:42.0 the same street in Tokyoslo style (no place-name signs)
    if (name === 'map2') drawTokyoslo(bx);
    else drawClassicOslo(bx);
    if (name === 'map') drawSubway(t, taggerStoppedAt); // in front of the buildings
  } else if (name === 'chaos') { // «brennende trikker og busser på skrå» – in burning Tokyoslo
    drawTokyoslo(bx);
    drawBurningTrams(t, bx);
    for (let i = 0; i < 30; i++) {
      const x = wrap(r() * W - bx * 0.05, W), y = wrap(r() * GROUND - t * 40, GROUND);
      for (const copy of repeatedX(x, W, 1)) R(copy, y, 1, 1, '#ffb347'); // embers
    }
  }
  R(left, GROUND, right - left, H - GROUND, GROUND_COLOR[name]);
  R(left, GROUND, right - left, 2, beatFlash > 0.5 ? '#ffffff' : '#ffcc33');
  for (let i = 0; i < 11; i++) for (const x of repeatedX(i * 32 - bx - 32, 352, 16)) R(x, GROUND + 6, 16, 2, '#00000055');
}
