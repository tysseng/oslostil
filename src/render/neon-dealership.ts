import { DEALERSHIP } from '../schedule';
import { ctx, loadImage, ready } from './draw';
import buildingUrl from '../../assets/backgrounds/neon-dealership.png';
import lightUrl from '../../assets/backgrounds/neon-dealership-light.png';
import beamsUrl from '../../assets/backgrounds/neon-dealership-beams.png';

export const DEALERSHIP_IMAGES = {
  building: loadImage(buildingUrl),
  light: loadImage(lightUrl),
  beams: loadImage(beamsUrl),
};

function origin(x: number, base: number): [number, number] {
  return [Math.round(x - DEALERSHIP.w / 2), Math.round(base - DEALERSHIP.h)];
}

export function drawDealership(x: number, base: number): void {
  const [left, top] = origin(x, base), { padding } = DEALERSHIP.light;
  if (ready(DEALERSHIP_IMAGES.light)) ctx.drawImage(DEALERSHIP_IMAGES.light, left - padding, top - padding);
  if (ready(DEALERSHIP_IMAGES.building)) ctx.drawImage(DEALERSHIP_IMAGES.building, left, top);
}

export function drawDealershipBeams(x: number, base: number): void {
  if (!ready(DEALERSHIP_IMAGES.beams)) return;
  const [left, top] = origin(x, base), [dx, dy] = DEALERSHIP.beams.offset;
  ctx.drawImage(DEALERSHIP_IMAGES.beams, left + dx, top + dy);
}
