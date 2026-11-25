import { STATION_ASSETS, type StationAssetKind } from '../schedule';
import { ctx, loadImage, ready } from './draw';
import tobaccoUrl from '../../assets/sprites/poster-tobacco.png';
import sodaUrl from '../../assets/sprites/poster-soda.png';
import coffeeUrl from '../../assets/sprites/poster-coffee.png';
import tobaccoWornUrl from '../../assets/sprites/poster-tobacco-worn.png';
import sodaWornUrl from '../../assets/sprites/poster-soda-worn.png';
import coffeeWornUrl from '../../assets/sprites/poster-coffee-worn.png';
import scaleUrl from '../../assets/sprites/vintage-scale.png';

export const STATION_IMAGES = {
  poster_tobacco: loadImage(tobaccoUrl),
  poster_soda: loadImage(sodaUrl),
  poster_coffee: loadImage(coffeeUrl),
  poster_tobacco_worn: loadImage(tobaccoWornUrl),
  poster_soda_worn: loadImage(sodaWornUrl),
  poster_coffee_worn: loadImage(coffeeWornUrl),
  vintage_scale: loadImage(scaleUrl),
};

export function drawStationAsset(kind: StationAssetKind, x: number, base: number): void {
  const image = STATION_IMAGES[kind], { w, h } = STATION_ASSETS[kind];
  if (ready(image)) ctx.drawImage(image, Math.round(x - w / 2), Math.round(base - h), w, h);
}
