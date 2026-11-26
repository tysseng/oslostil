import { HIGHRISES, type HighriseKind } from '../schedule';
import { ctx, loadImage, ready } from './draw';
import buildingUrl from '../../assets/backgrounds/neon-highrise-1.png';
import lightUrl from '../../assets/backgrounds/neon-highrise-1-light.png';
import enturBuildingUrl from '../../assets/backgrounds/neon-highrise-2.png';
import enturLightUrl from '../../assets/backgrounds/neon-highrise-2-light.png';

export const HIGHRISE_IMAGES: Record<HighriseKind, { building: HTMLImageElement; light: HTMLImageElement }> = {
  neon_highrise_1: { building: loadImage(buildingUrl), light: loadImage(lightUrl) },
  neon_highrise_2: { building: loadImage(enturBuildingUrl), light: loadImage(enturLightUrl) },
};

export function drawHighrise(kind: HighriseKind, x: number, base: number): void {
  const asset = HIGHRISES[kind], { building, light } = HIGHRISE_IMAGES[kind];
  const left = Math.round(x - asset.w / 2), top = Math.round(base - asset.h);
  const { padding } = asset.light;
  if (ready(light)) ctx.drawImage(light, left - padding, top - padding);
  if (ready(building)) ctx.drawImage(building, left, top);
}
