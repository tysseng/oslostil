import { GROUND, H, W } from '../config';
import { STAIRS_WIDTH, VALKYRIEN_BOTTOM, VALKYRIEN_CEILING, VALKYRIEN_DEPTH, VALKYRIEN_ENTRY, VALKYRIEN_FLOOR, VALKYRIEN_HEIGHT, exitX, stationEntryX, valkyrienTrainNose } from '../valkyrien';
import { enemyHeight, enemyX, type Enemy } from '../state';
import { HIRES_PPM, RES, R, ctx, drawToContext, drawVehicle, horizontalBounds, loadImage, meta, ready, text } from './draw';
import subwayOldUrl from '../../assets/vehicles/hires/subway-old.png';

const SUBWAY_OLD = loadImage(subwayOldUrl);
const SUBWAY_PPM = 10;
const LIGHT_SPACING = 140;
const CONE_WIDTH = 100;
const CONE_HEIGHT = VALKYRIEN_HEIGHT + 24;
let lightCone: HTMLCanvasElement | null = null;
const darkness = document.createElement('canvas');
const darknessCtx = darkness.getContext('2d')!;
let trainCone: HTMLCanvasElement | null = null;
let rearCone: HTMLCanvasElement | null = null;
let windowGlow: HTMLCanvasElement | null = null;
const windowLayer = document.createElement('canvas');
const windowLayerCtx = windowLayer.getContext('2d')!;
const windowOcclusion = document.createElement('canvas');
const windowOcclusionCtx = windowOcclusion.getContext('2d')!;
let ghostGlow: HTMLCanvasElement | null = null;

function ghostLight(): HTMLCanvasElement {
  if (ghostGlow) return ghostGlow;
  const bitmap = document.createElement('canvas');
  bitmap.width = bitmap.height = 72 * RES;
  const c = bitmap.getContext('2d')!;
  const gradient = c.createRadialGradient(36 * RES, 36 * RES, 0, 36 * RES, 36 * RES, 36 * RES);
  gradient.addColorStop(0, 'rgba(80, 255, 100, 0.85)');
  gradient.addColorStop(0.35, 'rgba(50, 240, 80, 0.5)');
  gradient.addColorStop(1, 'rgba(30, 220, 60, 0)');
  c.fillStyle = gradient;
  c.fillRect(0, 0, bitmap.width, bitmap.height);
  ghostGlow = bitmap;
  return bitmap;
}

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
  const start = stationEntryX(t) + 20;
  const count = Math.max(0, Math.ceil((exitX(t) + 45 - start) / LIGHT_SPACING) - 1);
  return Array.from({ length: count }, (_, i) => start + i * LIGHT_SPACING + 32.5);
}

function ceilingLightCone(): HTMLCanvasElement {
  if (lightCone) return lightCone;
  const bitmap = document.createElement('canvas');
  bitmap.width = CONE_WIDTH * RES;
  bitmap.height = CONE_HEIGHT * RES;
  const c = bitmap.getContext('2d')!;
  const pixels = c.createImageData(bitmap.width, bitmap.height);
  for (let y = 0; y < bitmap.height; y++) {
    const depth = y / bitmap.height, radius = 1 + depth * 47;
    for (let x = 0; x < bitmap.width; x++) {
      const distance = Math.abs((x + 0.5) / RES - CONE_WIDTH / 2);
      const edge = Math.max(0, Math.min(1, (radius - distance) / Math.min(24, radius)));
      const bottomFade = Math.max(0, Math.min(1, (1 - depth) / 0.35));
      const topFade = Math.min(1, depth / 0.025);
      const alpha = edge * edge * (3 - 2 * edge) * bottomFade * bottomFade * (3 - 2 * bottomFade) * topFade;
      const i = (y * bitmap.width + x) * 4;
      pixels.data[i] = pixels.data[i + 1] = pixels.data[i + 2] = 255;
      pixels.data[i + 3] = Math.round(alpha * 255);
    }
  }
  c.putImageData(pixels, 0, 0);
  lightCone = bitmap;
  return bitmap;
}

function stairSilhouette(t: number): void {
  const top = exitX(t), bottom = top - STAIRS_WIDTH;
  ctx.moveTo(bottom, VALKYRIEN_FLOOR - 12);
  ctx.lineTo(top, GROUND - 12);
  ctx.lineTo(top, VALKYRIEN_FLOOR + 6);
  ctx.lineTo(bottom, VALKYRIEN_FLOOR + 6);
  ctx.closePath();
  ctx.rect(top, VALKYRIEN_CEILING, 45, VALKYRIEN_HEIGHT + 6);
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
  const cone = ceilingLightCone();
  const lights = stationLights(t);
  for (const [i, center] of lights.entries()) {
    if (center + CONE_WIDTH / 2 < left) continue;
    if (center - CONE_WIDTH / 2 > right) break;
    darknessCtx.save();
    darknessCtx.globalAlpha = lightIntensity(t, i);
    if (i === lights.length - 1) {
      darknessCtx.translate(-left, -VALKYRIEN_CEILING);
      drawToContext(darknessCtx, () => clipOutsideStairs(t, left, width / RES, height));
      darknessCtx.translate(left, VALKYRIEN_CEILING);
    }
    darknessCtx.drawImage(cone, center - left - CONE_WIDTH / 2, 6, CONE_WIDTH, CONE_HEIGHT);
    darknessCtx.restore();
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
  const ghosts = enemies.filter(e => e.type === 'ghost' && !e.dead);
  for (const ghost of ghosts) {
    darknessCtx.drawImage(ghostLight(), enemyX(ghost, t) - left - 36,
      GROUND - enemyHeight(ghost, t) - VALKYRIEN_CEILING - 44, 72, 72);
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
    ctx.drawImage(ghostLight(), enemyX(ghost, t) - 36, GROUND - enemyHeight(ghost, t) - 44, 72, 72);
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

export function drawUndergroundFill(x = 0, y = H, width = W, height = VALKYRIEN_DEPTH + 30): void {
  const gradient = ctx.createLinearGradient(0, H, 0, VALKYRIEN_FLOOR + VALKYRIEN_BOTTOM);
  gradient.addColorStop(0, '#0a2e33');
  gradient.addColorStop(1, '#000');
  ctx.fillStyle = gradient;
  ctx.fillRect(x, y, width, height);
}

export function drawValkyrien(t: number, minX = 0, maxX = W): void {
  const entry = stationEntryX(t), exit = exitX(t), left = Math.max(minX - 10, entry - 50);
  drawUndergroundFill(minX, H, maxX - minX);
  if (exit < minX - 100 || left > maxX) return;
  R(left, VALKYRIEN_CEILING, exit + 45 - left, VALKYRIEN_HEIGHT, '#898d8f');
  const wallAnchor = entry - 50 + (t - VALKYRIEN_ENTRY) * 145 * 0.15;
  ctx.save();
  ctx.beginPath();
  ctx.rect(left, VALKYRIEN_CEILING, exit + 45 - left, VALKYRIEN_HEIGHT);
  ctx.clip();
  const wallStart = wallAnchor + Math.floor((left - wallAnchor) / 70) * 70;
  for (let x = wallStart; x < Math.min(exit + 45, maxX + 70); x += 70) {
    R(x, VALKYRIEN_CEILING, 1, VALKYRIEN_HEIGHT, '#64696c');
    R(x + 27, VALKYRIEN_FLOOR - 40, 8, 40, '#6b7073');
  }
  const sign = wallAnchor + 220;
  R(sign, VALKYRIEN_CEILING + 26, 80, 17, '#35393c');
  text('VALKYRIEN', sign + 40, VALKYRIEN_CEILING + 31, '#eee', 7, 'center');
  ctx.restore();
  for (const [i, center] of stationLights(t).entries()) {
    if (center + 17.5 < minX || center - 17.5 > maxX) continue;
    ctx.save();
    ctx.globalAlpha = lightIntensity(t, i);
    R(center - 17.5, VALKYRIEN_CEILING + 6, 35, 3, '#e2e4da');
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
  R(left, VALKYRIEN_FLOOR, Math.max(0, exit - STAIRS_WIDTH - left), 6, '#bec1bf');
  R(left, VALKYRIEN_FLOOR + 6, Math.max(0, exit - STAIRS_WIDTH - left), 20, '#454a4d');
  R(left, VALKYRIEN_FLOOR - 2, Math.max(0, exit - STAIRS_WIDTH - left), 2, '#d6cd85');
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
  if (entry > minX - 30 && entry < maxX + 30) {
    R(entry - 20, GROUND - 40, 40, 40, '#858b8e');
    R(entry - 16, GROUND - 36, 32, 36, '#202b30');
    text('T', entry, GROUND - 31, '#d8e5dd', 12, 'center');
    text('v', entry, GROUND - 14, '#d8e5dd', 8, 'center');
  }
}

export function drawValkyrienBalustrade(t: number, minX = 0, maxX = W): void {
  const top = exitX(t), bottom = top - STAIRS_WIDTH;
  if (top + 45 < minX || bottom > maxX) return;
  ctx.save();
  ctx.beginPath();
  ctx.rect(bottom - 2, VALKYRIEN_CEILING, STAIRS_WIDTH + 47, VALKYRIEN_HEIGHT + 6);
  ctx.clip();
  ctx.fillStyle = '#93989a';
  ctx.beginPath();
  stairSilhouette(t);
  ctx.fill();
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
