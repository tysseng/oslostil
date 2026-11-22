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
