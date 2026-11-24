// Canvas primitives. All drawing happens on a 320×180 canvas that CSS scales up without smoothing.
import { FONT, H, W } from '../config';

/**
 * The game is laid out in 320 × 180 game pixels, but the canvas has RES canvas pixels per game pixel.
 * Rectangles and sprites still snap to whole game pixels (blocky), while hi-res images (the vehicles,
 * for now) and text keep their detail.
 */
export const RES = 4;
export const canvas = document.getElementById('game') as HTMLCanvasElement;
canvas.width = W * RES;
canvas.height = H * RES;
export const ctx = canvas.getContext('2d')!;
ctx.imageSmoothingEnabled = false;

/** Back to the plain game-pixel transform, optionally shifted (screen shake) by whole game pixels. */
export function resetTransform(dx = 0, dy = 0): void {
  ctx.setTransform(RES, 0, 0, RES, dx * RES, dy * RES);
}
resetTransform();

export function horizontalBounds(): { left: number; right: number } {
  const transform = ctx.getTransform();
  return { left: -transform.e / transform.a, right: (canvas.width - transform.e) / transform.a };
}

/** Draw a hi-res image smoothly at (x, y) with size w × h in game pixels. */
export function drawHiRes(img: HTMLImageElement, x: number, y: number, w: number, h: number): void {
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(img, x, y, w, h);
  ctx.imageSmoothingEnabled = false;
}

/** Filled rectangle snapped to whole pixels. */
export function R(x: number, y: number, w: number, h: number, c: string): void {
  ctx.fillStyle = c;
  ctx.fillRect(Math.round(x), Math.round(y), w, h);
}

export function text(s: string, x: number, y: number, c = '#fff', size = 8, align: CanvasTextAlign = 'left', shadow: string | null = '#000'): void {
  ctx.font = `${size}px ${FONT}`;
  ctx.textAlign = align;
  ctx.textBaseline = 'top';
  if (shadow) { ctx.fillStyle = shadow; ctx.fillText(s, Math.round(x) + 1, Math.round(y) + 1); }
  ctx.fillStyle = c;
  ctx.fillText(s, Math.round(x), Math.round(y));
}

/** Full-screen flash that fades out over `len` seconds after `start`. */
export function flash(t: number, start: number, len: number, color: string): void {
  if (t < start || t - start >= len) return;
  ctx.globalAlpha = 1 - (t - start) / len;
  R(0, 0, W, H, color);
  ctx.globalAlpha = 1;
}

/** Load an image (sprite sheet etc.); draw calls skip it until it has loaded. */
export function loadImage(url: string): HTMLImageElement {
  const img = new Image();
  img.src = url;
  return img;
}

export const ready = (img: HTMLImageElement): boolean => img.complete && img.naturalWidth > 0;

/** The hi-res vehicle masters in assets/vehicles/hires/ are 100 px per metre. */
export const HIRES_PPM = 100;
export interface VehicleMeta { box: [number, number, number, number]; sign: [number, number, number, number] | null }
const metas = new Map<HTMLImageElement, VehicleMeta>();
/**
 * The bounding box of the non-transparent pixels (the bottom row is the wheel bottoms) and of the amber
 * destination sign (so a mirrored bus can have its sign drawn the right way round).
 */
export function meta(img: HTMLImageElement): VehicleMeta {
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
export function drawVehicle(img: HTMLImageElement, x: number, y: number, ppm: number, flip = false): void {
  if (!ready(img)) return;
  const { box: [sx, sy, sw, sh], sign } = meta(img), k = ppm / HIRES_PPM, w = sw * k, h = sh * k;
  const bounds = horizontalBounds();
  if (x > bounds.right || x + w < bounds.left) return;
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
