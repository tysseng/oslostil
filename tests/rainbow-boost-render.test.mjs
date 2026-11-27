import assert from 'node:assert/strict';
import { after, test } from 'node:test';
import { createServer } from 'vite';

const rectangles = [], labels = [], images = [];
const context = {
  setTransform() {}, save() {}, restore() {},
  fillRect(x, y, w, h) { rectangles.push({ x, y, w, h, color: this.fillStyle, alpha: this.globalAlpha, blend: this.globalCompositeOperation }); },
  fillText(label, x, y) { labels.push({ label, x, y, color: this.fillStyle }); },
  drawImage(image, x, y, w, h) { images.push({ image, x, y, w, h, alpha: this.globalAlpha, blend: this.globalCompositeOperation }); },
};
globalThis.document = { getElementById: () => ({ getContext: () => context }) };
globalThis.Image = class { complete = true; naturalWidth = 18; };
const server = await createServer({ server: { middlewareMode: true }, appType: 'custom', logLevel: 'silent' });
after(() => server.close());
const { drawRainbowBoost } = await server.ssrLoadModule('/src/render/rainbow-boost.ts');

test('draws fast-expanding rainbow rings with glow and a text-only Tailstrike label', () => {
  drawRainbowBoost({ x: 80, y: 80, age: 0.1 }, 0);
  const colors = new Set(rectangles.map(rect => rect.color));
  for (const color of ['#ff4a7c', '#ffb43b', '#fff45a', '#65ff90', '#36eaff', '#c17aff']) {
    assert.ok(colors.has(color), color);
  }
  assert.ok(labels.every(label => label.label === 'Tailstrike!'));
  assert.equal(labels.length, 2);
  assert.ok(rectangles.every(rect => rect.w === 2 && rect.h === 2));
  assert.ok(rectangles.some(rect => rect.color === '#ff4a7c' && rect.x >= 100));
  assert.ok(images.length > 0);
  assert.ok(images.every(image => image.blend === 'screen' && image.w === 18 && image.h === 26));
  assert.ok(images.every(image => image.image.src.includes('rainbow-tail-light.png')));
  const earlyAlpha = rectangles[0].alpha;
  rectangles.length = 0;
  images.length = 0;
  drawRainbowBoost({ x: 80, y: 80, age: 0.3 }, 0);
  assert.ok(rectangles[0].alpha < earlyAlpha / 2);
  assert.ok(rectangles.some(rect => rect.color === '#ff4a7c' && rect.x >= 115));
  rectangles.length = 0;
  labels.length = 0;
  images.length = 0;
  drawRainbowBoost({ x: 2, y: 3, age: 0.5 }, 0);
  assert.equal(rectangles.length, 0);
  assert.equal(images.length, 0);
  assert.ok(labels.some(label => label.label === 'Tailstrike!' && label.x >= 44 && label.y >= 17));
});
