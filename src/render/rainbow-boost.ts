import { H, W } from '../config';
import { RAINBOW_BOOST_EFFECT_DURATION, RAINBOW_BOOST_LABEL_DURATION } from '../rainbow';
import type { RainbowBoostEffect } from '../state';
import rainbowMeta from '../../assets/sprites/rainbow.json';
import { R, ctx, ready, text } from './draw';
import { RAINBOW_LIGHT } from './rainbow-light';

const COLORS = ['#ff4a7c', '#ffb43b', '#fff45a', '#65ff90', '#36eaff', '#c17aff'];

export function drawRainbowBoost(effect: RainbowBoostEffect, camera: number): void {
  const progress = Math.min(1, effect.age / RAINBOW_BOOST_EFFECT_DURATION);
  const radius = 4 + 39 * (1 - (1 - progress) ** 2);
  const alpha = (1 - progress) ** 1.5;
  ctx.save();
  if (progress < 1 && ready(RAINBOW_LIGHT)) {
    const { w, h, centre } = rainbowMeta.tail_light;
    const count = Math.max(6, Math.ceil(2 * Math.PI * radius / 12));
    ctx.globalCompositeOperation = 'screen';
    ctx.globalAlpha = alpha * 0.3;
    for (let i = 0; i < count; i++) {
      const angle = i * Math.PI * 2 / count;
      ctx.drawImage(RAINBOW_LIGHT, Math.round(effect.x + Math.cos(angle) * radius) - centre[0],
        Math.round(effect.y + Math.sin(angle) * radius) - centre[1], w, h);
    }
    ctx.globalCompositeOperation = 'source-over';
  }
  ctx.globalAlpha = alpha * 0.75;
  if (progress < 1) {
    for (let ring = 0; ring < COLORS.length; ring++) {
      const r = Math.max(0, radius - ring * 2);
      for (let i = 0; i < 80; i++) {
        const angle = i * Math.PI * 2 / 80;
        R(effect.x + Math.cos(angle) * r - 1, effect.y + Math.sin(angle) * r - 1, 2, 2, COLORS[ring]);
      }
    }
  }
  const x = Math.max(44, Math.min(W - 44, effect.x));
  const y = camera + Math.max(17, Math.min(H - 12, effect.y - camera - 28 - effect.age * 12));
  ctx.globalAlpha = Math.min(1, (RAINBOW_BOOST_LABEL_DURATION - effect.age) / 0.2);
  text('Tailstrike!', x, y, '#fff45a', 8, 'center', '#ff2bd6');
  ctx.restore();
}
