import { GROUND, H, W } from '../config';
import { EXIT_HOUSE_LEFT, EXIT_HOUSE_RIGHT, STAIRS_WIDTH, VALKYRIEN_BOTTOM, VALKYRIEN_CEILING, VALKYRIEN_DEPTH, VALKYRIEN_ENTRY, VALKYRIEN_FLOOR, VALKYRIEN_HEIGHT, exitX, platformStartX, stationEntryX, valkyrienTrainNose } from '../valkyrien';
import { enemyHeight, enemyX, type Enemy } from '../state';
import { HIRES_PPM, RES, R, ctx, drawToContext, drawVehicle, horizontalBounds, loadImage, meta, ready } from './draw';
import subwayOldUrl from '../../assets/vehicles/hires/subway-old.png';
import entranceUrl from '../../assets/sprites/valkyrien-entrance.png';
import entranceLightUrl from '../../assets/sprites/valkyrien-entrance-light.png';
import houseUrl from '../../assets/sprites/valkyrien-house.png';
import houseFrontUrl from '../../assets/sprites/valkyrien-house-front.png';
import houseLightUrl from '../../assets/sprites/valkyrien-house-light.png';
import wallUrl from '../../assets/sprites/valkyrien-wall.png';
import signUrl from '../../assets/sprites/valkyrien-sign.png';
import ceilingLampUrl from '../../assets/sprites/valkyrien-ceiling-lamp.png';
import tubeLightUrl from '../../assets/sprites/valkyrien-tube-light.png';
import signLampsUrl from '../../assets/sprites/valkyrien-sign-lamps.png';
import signLightUrl from '../../assets/sprites/valkyrien-sign-light.png';
import { drawGhost } from './ghost';
import { isGhost } from '../schedule';

const SUBWAY_OLD = loadImage(subwayOldUrl);
const ENTRANCE = loadImage(entranceUrl);
const ENTRANCE_LIGHT = loadImage(entranceLightUrl);
const HOUSE = loadImage(houseUrl);
const HOUSE_FRONT = loadImage(houseFrontUrl);
const HOUSE_LIGHT = loadImage(houseLightUrl);
const WALL = loadImage(wallUrl);
const SIGN = loadImage(signUrl);
const CEILING_LAMP = loadImage(ceilingLampUrl);
const TUBE_LIGHT = loadImage(tubeLightUrl);
const SIGN_LAMPS = loadImage(signLampsUrl);
const SIGN_LIGHT = loadImage(signLightUrl);
const SUBWAY_PPM = 10;
const LIGHT_SPACING = 140;
const CONE_WIDTH = 100;
const CONE_HEIGHT = VALKYRIEN_HEIGHT + 24;
const STATION_SPEED = 145;
const WALL_SPEED = STATION_SPEED * 0.85;
const LIGHT_SPEED = WALL_SPEED * 1.08;
const darkness = document.createElement('canvas');
const darknessCtx = darkness.getContext('2d')!;
let trainCone: HTMLCanvasElement | null = null;
let rearCone: HTMLCanvasElement | null = null;
let windowGlow: HTMLCanvasElement | null = null;
const windowLayer = document.createElement('canvas');
const windowLayerCtx = windowLayer.getContext('2d')!;
const windowOcclusion = document.createElement('canvas');
const windowOcclusionCtx = windowOcclusion.getContext('2d')!;

function trainWindowLights(t: number): { bitmap: HTMLCanvasElement; x: number; y: number; width: number; height: number } | null {
  const nose = valkyrienTrainNose(t);
  if (nose === null || !ready(SUBWAY_OLD)) return null;
  const [sx, sy, sw, sh] = meta(SUBWAY_OLD).box;
  const scale = SUBWAY_PPM / HIRES_PPM;
  const width = sw * scale, height = sh * scale;
  if (!windowGlow) {
    const bitmap = document.createElement('canvas');
    bitmap.width = Math.ceil(width * RES);
    bitmap.height = Math.ceil(height * RES);
    const c = bitmap.getContext('2d')!;
    const pixels = c.createImageData(bitmap.width, bitmap.height);
    // Window positions in the source SVG's -10,-40 viewBox, including door glass.
    const windows: [number[], number, number, number][] = [
      [[28.5, 204.5, 268.5, 447.5, 511.5, 575.5, 764.5, 1030.5, 1094.5, 1158.5, 1338, 1402, 1466, 1655, 1819.5, 2008.5, 2072.5, 2136.5, 2315.5, 2379.5, 2555.5], 96, 52, 58],
      [[108, 148, 353, 393, 658, 698, 936, 976, 1241, 1281, 1551, 1591, 1914, 1954, 2219, 2259, 2464, 2504], 86, 24, 70],
    ];
    const sourceScale = SUBWAY_OLD.naturalWidth / 2656;
    for (const [positions, y, w, h] of windows) for (const x of positions) {
      const cx = ((x + 10 + w / 2) * sourceScale - sx) * scale;
      const cy = ((y + 40 + h / 2) * sourceScale - sy) * scale;
      const halfW = w * sourceScale * scale / 2, halfH = h * sourceScale * scale / 2;
      const radius = 0.8, falloff = 4;
      for (let py = Math.max(0, Math.floor((cy - halfH - falloff) * RES)); py < Math.min(bitmap.height, (cy + halfH + falloff) * RES); py++) {
        for (let px = Math.max(0, Math.floor((cx - halfW - falloff) * RES)); px < Math.min(bitmap.width, (cx + halfW + falloff) * RES); px++) {
          const dx = Math.abs((px + 0.5) / RES - cx) - halfW + radius;
          const dy = Math.abs((py + 0.5) / RES - cy) - halfH + radius;
          const distance = Math.hypot(Math.max(0, dx), Math.max(0, dy)) + Math.min(0, Math.max(dx, dy)) - radius;
          const edge = Math.max(0, 1 - Math.max(0, distance) / falloff);
          const i = (py * bitmap.width + px) * 4;
          pixels.data[i] = 255; pixels.data[i + 1] = 220; pixels.data[i + 2] = 80;
          pixels.data[i + 3] = Math.max(pixels.data[i + 3], Math.round(0.85 * edge ** 3 * 255));
        }
      }
    }
    c.putImageData(pixels, 0, 0);
    windowGlow = bitmap;
  }
  return { bitmap: windowGlow, x: nose - width, y: VALKYRIEN_FLOOR + 8.75 + trainBump(t) - height, width, height };
}

function rearLightCone(): HTMLCanvasElement {
  if (rearCone) return rearCone;
  const source = trainLightCone();
  const bitmap = document.createElement('canvas');
  bitmap.width = source.width;
  bitmap.height = source.height;
  const c = bitmap.getContext('2d')!;
  c.drawImage(source, 0, 0);
  c.globalCompositeOperation = 'source-in';
  c.fillStyle = '#ff2319';
  c.fillRect(0, 0, bitmap.width, bitmap.height);
  rearCone = bitmap;
  return bitmap;
}

function lightIntensity(t: number, index: number): number {
  const block = Math.floor(index / 3);
  const period = 2.2 + block * 0.15;
  const clock = t - VALKYRIEN_ENTRY - block * 0.85;
  if (clock < 0) return 1;
  const cycle = ((clock % period) + period) % period;
  const burst = Math.floor(clock / period);
  const pulses = burst % 2 === 0 ? 3 : 2;
  for (let i = 0; i < pulses; i++) {
    const start = i * 0.34;
    if (cycle >= start && cycle < start + 0.22) {
      return (burst + i + block) % 3 === 0 ? 0 : 0.18 + 0.12 * ((burst + i) % 3);
    }
  }
  return 0.94 + 0.06 * Math.sin(t * 7.1 + block * 4.7);
}

function trainBump(t: number): number {
  const phase = ((t - VALKYRIEN_ENTRY) % 1.25 + 1.25) % 1.25;
  const pulse = (start: number): number => {
    const u = (phase - start) / 0.085;
    return u >= 0 && u <= 1 ? -1.3 * Math.sin(u * Math.PI) : 0;
  };
  return pulse(0) + pulse(0.15);
}

function trainLightCone(): HTMLCanvasElement {
  if (trainCone) return trainCone;
  const bitmap = document.createElement('canvas');
  bitmap.width = 120 * RES; bitmap.height = 60 * RES;
  const c = bitmap.getContext('2d')!, pixels = c.createImageData(bitmap.width, bitmap.height);
  for (let y = 0; y < bitmap.height; y++) for (let x = 0; x < bitmap.width; x++) {
    const u = x / bitmap.width, dy = Math.abs(y / RES - 30);
    const radius = 1 + u * 26;
    const edge = Math.max(0, 1 - dy / radius);
    const alpha = edge * edge * (3 - 2 * edge) * (1 - u) ** 2 * Math.min(1, u * 20);
    const i = (y * bitmap.width + x) * 4;
    pixels.data[i] = pixels.data[i + 1] = pixels.data[i + 2] = 255;
    pixels.data[i + 3] = Math.round(alpha * 255);
  }
  c.putImageData(pixels, 0, 0);
  trainCone = bitmap;
  return bitmap;
}

function trainLights(t: number): { x: number; y: number; rear: boolean }[] {
  const nose = valkyrienTrainNose(t);
  if (nose === null || !ready(SUBWAY_OLD)) return [];
  const width = meta(SUBWAY_OLD).box[2] * SUBWAY_PPM / HIRES_PPM;
  const y = VALKYRIEN_FLOOR - 14 + trainBump(t);
  return [{ x: nose - 3, y, rear: false }, { x: nose - width + 3, y, rear: true }];
}

function stationLights(t: number): number[] {
  const start = platformStartX(VALKYRIEN_ENTRY) + 70;
  const platformRight = exitX(VALKYRIEN_ENTRY) - STAIRS_WIDTH;
  const count = Math.max(0, Math.ceil((platformRight - start) / LIGHT_SPACING));
  const drift = -(t - VALKYRIEN_ENTRY) * LIGHT_SPEED;
  return Array.from({ length: count }, (_, i) => start + i * LIGHT_SPACING + drift);
}

function stationSigns(t: number): number[] {
  const width = exitX(VALKYRIEN_ENTRY) - STAIRS_WIDTH - platformStartX(VALKYRIEN_ENTRY);
  const anchor = platformStartX(VALKYRIEN_ENTRY) + (width - 12 * 128) / 2;
  const drift = -(t - VALKYRIEN_ENTRY) * WALL_SPEED;
  return Array.from({ length: 3 }, (_, i) => anchor + drift + (1.5 + i * 4) * 128);
}

function stairSilhouette(t: number): void {
  const top = exitX(t), bottom = top - STAIRS_WIDTH;
  ctx.moveTo(bottom, VALKYRIEN_FLOOR - 12);
  ctx.lineTo(top, GROUND - 12);
  ctx.lineTo(top, VALKYRIEN_FLOOR + 6);
  ctx.lineTo(bottom, VALKYRIEN_FLOOR + 6);
  ctx.closePath();
  ctx.rect(top, VALKYRIEN_CEILING, 45, VALKYRIEN_HEIGHT + 6);
  const entry = stationEntryX(t), landing = platformStartX(t);
  ctx.moveTo(entry, GROUND - 12);
  ctx.lineTo(landing, VALKYRIEN_FLOOR - 12);
  ctx.lineTo(landing, VALKYRIEN_FLOOR + 6);
  ctx.lineTo(entry, VALKYRIEN_FLOOR + 6);
  ctx.closePath();
  ctx.rect(entry - 50, VALKYRIEN_CEILING, 50, VALKYRIEN_HEIGHT + 6);
}

function clipOutsideStairs(t: number, left: number, width: number, height: number): void {
  ctx.beginPath();
  ctx.rect(left, VALKYRIEN_CEILING, width, height);
  stairSilhouette(t);
  ctx.clip('evenodd');
}

export function drawValkyrienDarkness(t: number, drawWindowOccluders: () => void, enemies: Enemy[] = []): void {
  const bounds = horizontalBounds();
  const left = Math.max(bounds.left, stationEntryX(t) - 50);
  const right = Math.min(bounds.right, exitX(t) + 45);
  if (right <= left) return;
  const height = VALKYRIEN_HEIGHT + VALKYRIEN_BOTTOM;
  const width = Math.ceil((right - left) * RES);
  if (darkness.width !== width || darkness.height !== height * RES) {
    darkness.width = width;
    darkness.height = height * RES;
  }
  darknessCtx.setTransform(RES, 0, 0, RES, 0, 0);
  darknessCtx.globalCompositeOperation = 'source-over';
  darknessCtx.clearRect(0, 0, width / RES, height);
  darknessCtx.fillStyle = 'rgba(0, 0, 0, 0.82)';
  darknessCtx.fillRect(0, 0, width / RES, height);
  darknessCtx.globalCompositeOperation = 'destination-out';
  const lights = stationLights(t);
  for (const [i, center] of lights.entries()) {
    if (!ready(TUBE_LIGHT)) break;
    if (center + CONE_WIDTH / 2 < left) continue;
    if (center - CONE_WIDTH / 2 > right) break;
    darknessCtx.save();
    darknessCtx.globalAlpha = lightIntensity(t, i);
    if (i === lights.length - 1) {
      darknessCtx.translate(-left, -VALKYRIEN_CEILING);
      drawToContext(darknessCtx, () => clipOutsideStairs(t, left, width / RES, height));
      darknessCtx.translate(left, VALKYRIEN_CEILING);
    }
    darknessCtx.drawImage(TUBE_LIGHT, center - left - CONE_WIDTH / 2, 23, CONE_WIDTH, CONE_HEIGHT);
    darknessCtx.restore();
  }
  if (ready(SIGN_LIGHT)) for (const center of stationSigns(t)) {
    darknessCtx.drawImage(SIGN_LIGHT, Math.round(center - 64) - left, 35, 128, 48);
  }
  for (const light of trainLights(t)) {
    darknessCtx.save();
    darknessCtx.translate(-left, -VALKYRIEN_CEILING);
    drawToContext(darknessCtx, () => clipOutsideStairs(t, left, width / RES, height));
    darknessCtx.globalAlpha = light.rear ? 0.5 : 0.9;
    darknessCtx.translate(light.x, light.y);
    if (light.rear) darknessCtx.scale(-1, 1);
    darknessCtx.drawImage(trainLightCone(), 0, -30, 120, 60);
    darknessCtx.restore();
  }
  const ghosts = enemies.filter(e => isGhost(e.type) && !e.dead);
  for (const ghost of ghosts) {
    darknessCtx.save();
    darknessCtx.translate(-left, -VALKYRIEN_CEILING);
    drawToContext(darknessCtx, () => drawGhost(ghost, enemyX(ghost, t), GROUND - enemyHeight(ghost, t), t, true));
    darknessCtx.restore();
  }
  const windows = trainWindowLights(t);
  if (windows) {
    for (const target of [windowLayer, windowOcclusion]) {
      if (target.width !== width || target.height !== height * RES) {
        target.width = width;
        target.height = height * RES;
      }
    }
    windowLayerCtx.setTransform(RES, 0, 0, RES, 0, 0);
    windowLayerCtx.globalCompositeOperation = 'source-over';
    windowLayerCtx.clearRect(0, 0, width / RES, height);
    windowLayerCtx.drawImage(windows.bitmap, windows.x - left, windows.y - VALKYRIEN_CEILING, windows.width, windows.height);
    windowOcclusionCtx.setTransform(RES, 0, 0, RES, 0, 0);
    windowOcclusionCtx.clearRect(0, 0, width / RES, height);
    windowOcclusionCtx.setTransform(RES, 0, 0, RES, -left * RES, -VALKYRIEN_CEILING * RES);
    windowOcclusionCtx.imageSmoothingEnabled = false;
    drawToContext(windowOcclusionCtx, drawWindowOccluders);
    windowLayerCtx.globalCompositeOperation = 'destination-out';
    windowLayerCtx.drawImage(windowOcclusion, 0, 0, width / RES, height);
    windowLayerCtx.globalCompositeOperation = 'source-over';
    darknessCtx.drawImage(windowLayer, 0, 0, width / RES, height);
  }
  darknessCtx.globalCompositeOperation = 'source-over';
  ctx.save();
  ctx.imageSmoothingEnabled = true;
  ctx.drawImage(darkness, left, VALKYRIEN_CEILING, width / RES, height);
  ctx.beginPath();
  ctx.rect(left, VALKYRIEN_CEILING, right - left, VALKYRIEN_HEIGHT);
  ctx.clip();
  ctx.globalCompositeOperation = 'screen';
  for (const ghost of ghosts) {
    ctx.globalAlpha = 0.5;
    drawGhost(ghost, enemyX(ghost, t), GROUND - enemyHeight(ghost, t), t, true);
  }
  ctx.globalAlpha = 1;
  if (windows) {
    ctx.globalAlpha = 0.35;
    ctx.drawImage(windowLayer, left, VALKYRIEN_CEILING, width / RES, height);
    ctx.globalAlpha = 1;
  }
  for (const light of trainLights(t)) {
    ctx.save();
    clipOutsideStairs(t, left, width / RES, height);
    ctx.translate(light.x, light.y);
    if (light.rear) ctx.scale(-1, 1);
    if (light.rear) {
      ctx.globalAlpha = 0.65;
      ctx.drawImage(rearLightCone(), 0, -30, 120, 60);
      ctx.globalAlpha = 1;
    }
    const color = light.rear ? '255, 35, 25' : '255, 245, 200';
    const glow = ctx.createRadialGradient(0, 0, 0, 0, 0, 32);
    glow.addColorStop(0, `rgba(${color}, 0.65)`);
    glow.addColorStop(1, `rgba(${color}, 0)`);
    ctx.fillStyle = glow;
    ctx.fillRect(-32, -32, 64, 64);
    ctx.restore();
  }
  ctx.restore();
}

function polygon(points: [number, number][], color: string): void {
  ctx.fillStyle = color;
  ctx.beginPath();
  points.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
  ctx.closePath();
  ctx.fill();
}

export function drawUndergroundFill(x = 0, y = GROUND, width = W, height = VALKYRIEN_DEPTH + 30): void {
  const gradient = ctx.createLinearGradient(0, GROUND, 0, H);
  gradient.addColorStop(0, '#0a2e33');
  gradient.addColorStop(1, '#000');
  ctx.fillStyle = gradient;
  ctx.fillRect(x, y, width, height);
}

export function drawValkyrien(t: number, minX = 0, maxX = W, drawWallItems?: () => void): void {
  const entry = stationEntryX(t), exit = exitX(t), left = Math.max(minX - 10, entry - 50);
  drawUndergroundFill(minX, GROUND, maxX - minX);
  if (exit < minX - 100 || left > maxX) return;
  R(left, VALKYRIEN_CEILING, exit + 45 - left, VALKYRIEN_HEIGHT, '#898d8f');
  const platformWidth = exitX(VALKYRIEN_ENTRY) - STAIRS_WIDTH - platformStartX(VALKYRIEN_ENTRY);
  const wallDrift = -(t - VALKYRIEN_ENTRY) * WALL_SPEED;
  const wallAnchor = platformStartX(VALKYRIEN_ENTRY) + wallDrift + (platformWidth - 12 * 128) / 2;
  ctx.save();
  ctx.beginPath();
  ctx.rect(left, VALKYRIEN_CEILING, exit + 45 - left, VALKYRIEN_HEIGHT);
  ctx.clip();
  ctx.imageSmoothingEnabled = false;
  const firstTile = Math.floor((left - wallAnchor) / 128);
  for (let i = firstTile; wallAnchor + i * 128 < Math.min(exit + 45, maxX + 128); i++) {
    const tile = ((i % 6) + 6) % 6;
    if (ready(WALL)) ctx.drawImage(WALL, tile * 128, 0, 128, 80,
      Math.round(wallAnchor + i * 128), VALKYRIEN_CEILING, 128, VALKYRIEN_HEIGHT);
  }
  for (const center of stationSigns(t)) {
    if (ready(SIGN)) ctx.drawImage(SIGN, Math.round(center - 52), VALKYRIEN_CEILING + 47, 104, 15);
    if (ready(SIGN_LAMPS)) ctx.drawImage(SIGN_LAMPS, Math.round(center - 52), VALKYRIEN_CEILING + 35, 104, 12);
    if (ready(SIGN_LIGHT)) {
      ctx.save();
      ctx.globalCompositeOperation = 'screen';
      ctx.imageSmoothingEnabled = true;
      ctx.drawImage(SIGN_LIGHT, Math.round(center - 64), VALKYRIEN_CEILING + 35, 128, 48);
      ctx.restore();
    }
  }
  drawWallItems?.();
  ctx.restore();
  for (const [i, center] of stationLights(t).entries()) {
    if (center + 20 < minX || center - 20 > maxX || !ready(CEILING_LAMP)) continue;
    ctx.save();
    ctx.globalAlpha = lightIntensity(t, i);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(CEILING_LAMP, Math.round(center - 20), VALKYRIEN_CEILING + 6, 40, 20);
    ctx.restore();
  }
  const nose = valkyrienTrainNose(t);
  if (nose !== null && ready(SUBWAY_OLD)) {
    ctx.save();
    ctx.beginPath();
    ctx.rect(left, VALKYRIEN_CEILING, exit + 45 - left, VALKYRIEN_HEIGHT);
    ctx.clip();
    const width = meta(SUBWAY_OLD).box[2] * SUBWAY_PPM / HIRES_PPM;
    drawVehicle(SUBWAY_OLD, nose - width, VALKYRIEN_FLOOR + 8.75 + trainBump(t), SUBWAY_PPM);
    ctx.restore();
  }
  const platformLeft = Math.max(left, platformStartX(t));
  R(platformLeft, VALKYRIEN_FLOOR, Math.max(0, exit - STAIRS_WIDTH - platformLeft), 6, '#bec1bf');
  R(platformLeft, VALKYRIEN_FLOOR + 6, Math.max(0, exit - STAIRS_WIDTH - platformLeft), 20, '#454a4d');
  R(platformLeft, VALKYRIEN_FLOOR - 2, Math.max(0, exit - STAIRS_WIDTH - platformLeft), 2, '#d6cd85');
  const bottom = exit - STAIRS_WIDTH;
  ctx.save();
  ctx.beginPath();
  ctx.rect(bottom, VALKYRIEN_CEILING, STAIRS_WIDTH + 10, VALKYRIEN_HEIGHT + 6);
  ctx.clip();
  polygon([[bottom, VALKYRIEN_FLOOR], [exit, GROUND], [exit, GROUND + 6], [bottom, VALKYRIEN_FLOOR + 6]], '#73787b');
  for (let i = 0; i < 20; i++) {
    const u = i / 20;
    R(bottom + STAIRS_WIDTH * u, VALKYRIEN_FLOOR - VALKYRIEN_DEPTH * u, STAIRS_WIDTH / 20, 2, '#c2c5c4');
  }
  ctx.restore();
  ctx.save();
  ctx.beginPath();
  ctx.rect(entry, VALKYRIEN_CEILING, STAIRS_WIDTH, VALKYRIEN_HEIGHT + 6);
  ctx.clip();
  polygon([[entry, GROUND], [entry + STAIRS_WIDTH, VALKYRIEN_FLOOR],
    [entry + STAIRS_WIDTH, VALKYRIEN_FLOOR + 6], [entry, GROUND + 6]], '#73787b');
  for (let i = 0; i < 20; i++) {
    const u = i / 20;
    R(entry + STAIRS_WIDTH * u, GROUND + VALKYRIEN_DEPTH * u, STAIRS_WIDTH / 20, 2, '#c2c5c4');
  }
  ctx.restore();
  if (entry > minX - 96 && entry < maxX + 96 && ready(ENTRANCE)) {
    ctx.save();
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(ENTRANCE, Math.round(entry - 32), GROUND - 64, 64, 64);
    if (ready(ENTRANCE_LIGHT)) {
      ctx.imageSmoothingEnabled = true;
      ctx.globalCompositeOperation = 'screen';
      ctx.drawImage(ENTRANCE_LIGHT, Math.round(entry - 96), GROUND - 128, 192, 192);
    }
    ctx.restore();
  }
}

export function drawValkyrienBalustrade(t: number, minX = 0, maxX = W): void {
  const top = exitX(t), bottom = top - STAIRS_WIDTH;
  const entry = stationEntryX(t), landing = platformStartX(t);
  if (top + 45 < minX || entry - 50 > maxX) return;
  ctx.save();
  ctx.beginPath();
  ctx.rect(minX, VALKYRIEN_CEILING, maxX - minX, VALKYRIEN_HEIGHT + 6);
  ctx.clip();
  ctx.fillStyle = '#93989a';
  ctx.beginPath();
  stairSilhouette(t);
  ctx.fill();
  ctx.strokeStyle = '#d1d3d2';
  ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(bottom, VALKYRIEN_FLOOR - 12); ctx.lineTo(top, GROUND - 12); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(entry, GROUND - 12); ctx.lineTo(landing, VALKYRIEN_FLOOR - 12); ctx.stroke();
  ctx.restore();
}

export function drawValkyrienHouse(t: number, minX = 0, maxX = W, foreground = false): void {
  const x = exitX(t);
  const image = foreground ? HOUSE_FRONT : HOUSE;
  if (x + EXIT_HOUSE_RIGHT + 16 < minX || x + EXIT_HOUSE_LEFT - 16 > maxX || !ready(image)) return;
  ctx.save();
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(image, Math.round(x + EXIT_HOUSE_LEFT), GROUND - 64, EXIT_HOUSE_RIGHT - EXIT_HOUSE_LEFT, 64);
  if (ready(HOUSE_LIGHT)) {
    ctx.globalCompositeOperation = 'screen';
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(HOUSE_LIGHT, Math.round(x + EXIT_HOUSE_LEFT - 16), GROUND - 80, 136, 96);
  }
  ctx.restore();
}
