import { GHOSTS, isGhost } from '../schedule';
import type { Enemy } from '../state';
import { ctx, loadImage, ready } from './draw';
import ghostUrl from '../../assets/sprites/ghost.png';
import ghostLightUrl from '../../assets/sprites/ghost-light.png';
import bedsheetUrl from '../../assets/sprites/ghost-bedsheet.png';
import bedsheetLightUrl from '../../assets/sprites/ghost-bedsheet-light.png';
import conductorUrl from '../../assets/sprites/ghost-slime.png';
import conductorLightUrl from '../../assets/sprites/ghost-slime-light.png';

export const GHOST_IMAGES = {
  ghost: { sprite: loadImage(ghostUrl), light: loadImage(ghostLightUrl) },
  ghost_bedsheet: { sprite: loadImage(bedsheetUrl), light: loadImage(bedsheetLightUrl) },
  ghost_conductor: { sprite: loadImage(conductorUrl), light: loadImage(conductorLightUrl) },
};

export function drawGhost(e: Enemy, x: number, base: number, t: number, light = false): void {
  if (!isGhost(e.type)) return;
  const GHOST = GHOSTS[e.type];
  const image = light ? GHOST_IMAGES[e.type].light : GHOST_IMAGES[e.type].sprite;
  if (!ready(image)) return;
  const [w, h] = light ? GHOST.light.cell : GHOST.cell;
  const padding = light ? GHOST.light.padding : 0;
  const frame = Math.floor(t * GHOST.fps) % GHOST.frames;
  const left = Math.round(x - GHOST.cell[0] / 2) - padding;
  const top = Math.round(base - GHOST.cell[1]) - padding;
  ctx.save();
  if (e.ghost?.following) {
    ctx.translate(Math.round(x) * 2, 0);
    ctx.scale(-1, 1);
  }
  ctx.drawImage(image, frame * w, light ? 0 : GHOST.row * h, w, h, left, top, w, h);
  ctx.restore();
}
