import { NEON_CARS, type NeonCarKind } from '../schedule';
import { ctx, loadImage, ready } from './draw';
import countachUrl from '../../assets/sprites/neon-countach.png';
import countachLightUrl from '../../assets/sprites/neon-countach-light.png';
import testarossaUrl from '../../assets/sprites/neon-testarossa.png';
import testarossaLightUrl from '../../assets/sprites/neon-testarossa-light.png';

export const NEON_CAR_IMAGES: Record<NeonCarKind, { sprite: HTMLImageElement; light: HTMLImageElement }> = {
  neon_countach: { sprite: loadImage(countachUrl), light: loadImage(countachLightUrl) },
  neon_testarossa: { sprite: loadImage(testarossaUrl), light: loadImage(testarossaLightUrl) },
};

export function drawNeonCar(kind: NeonCarKind, x: number, base: number): void {
  const { sprite, light } = NEON_CAR_IMAGES[kind];
  const { w, h, light: { padding, cell: [lw, lh] } } = NEON_CARS[kind];
  const left = Math.round(x - w / 2), top = Math.round(base - h);
  if (ready(light)) ctx.drawImage(light, left - padding, top - padding, lw, lh);
  if (ready(sprite)) ctx.drawImage(sprite, left, top, w, h);
}
