import assert from 'node:assert/strict';
import { after, test } from 'node:test';
import { createServer } from 'vite';

const server = await createServer({ server: { middlewareMode: true }, appType: 'custom', logLevel: 'silent' });
after(() => server.close());
const { Game } = await server.ssrLoadModule('/src/game.ts');
const { RAINBOW_BOOST_EFFECT_DURATION, ribbonContact, ribbonLength, ribbonPoints } = await server.ssrLoadModule('/src/rainbow.ts');
const { RAINBOW_T0, RAINBOW_T1 } = await server.ssrLoadModule('/src/timeline.ts');
const { BEAT, GROUND, H, PH, PX, W, barT } = await server.ssrLoadModule('/src/config.ts');
const { EXIT_HOUSE_LEFT, exitSurfaceClip, exitX, VALKYRIEN_CEILING, VALKYRIEN_FLOOR } = await server.ssrLoadModule('/src/valkyrien.ts');
const t = RAINBOW_T0 + 1;
const rainbow = () => ({
  x: 120, y: 110, vx: 0, vy: 0, blend: 1,
  path: [{ x: 60, y: 95, t }], sparkles: [], beat: 0,
});
const setup = () => {
  const sounds = [];
  const game = new Game({ sfx: name => sounds.push(name) });
  game.mode = 'play';
  game.s.ev = [];
  game.s.lastT = t;
  game.s.rainbow = rainbow();
  return { game, sounds };
};

test('airborne contact boosts once, with a cooldown between separate contacts', () => {
  const { game, sounds } = setup();
  const p = game.s.p;
  const point = ribbonPoints(game.s.rainbow)[2];
  p.x = point.x; p.y = point.y + 10; p.vy = 120; p.jumps = 2;
  game.update(t, 0);
  assert.equal(p.vy, -420);
  assert.equal(p.jumps, 2);
  assert.deepEqual(sounds, ['jump']);
  assert.equal(game.s.rainbowBoosts.length, 1);
  assert.equal(game.s.rainbowBoosts[0].age, 0);
  p.vy = -200;
  game.update(t, 0);
  assert.equal(p.vy, -200);
  p.x = 200;
  game.update(t, 0);
  p.x = point.x;
  game.update(t, 0);
  assert.equal(p.vy, -200);
  assert.deepEqual(sounds, ['jump']);
  assert.equal(game.s.rainbowBoosts.length, 1);
  p.x = 200;
  for (let i = 1; i <= 31; i++) game.update(t + i * 0.05, 0.05);
  game.s.rainbow = rainbow();
  game.s.rainbow.path[0].t = t + 1.55;
  game.s.rainbow.beat = Math.floor((t + 1.55 - PH) / BEAT);
  const nextPoint = ribbonPoints(game.s.rainbow)[2];
  p.x = nextPoint.x; p.y = nextPoint.y + 10; p.vy = 120; p.jumps = 2;
  game.update(t + 1.55, 0);
  assert.equal(p.vy, -420);
  assert.deepEqual(sounds, ['jump', 'jump']);
  assert.equal(game.s.rainbowBoosts.length, 1);
});

test('grounded, dead and scripted players are not boosted', () => {
  for (const condition of ['grounded', 'dead', 'scripted']) {
    const { game, sounds } = setup();
    const point = ribbonPoints(game.s.rainbow)[2];
    game.s.p.x = point.x; game.s.p.y = point.y + 10; game.s.p.jumps = condition === 'grounded' ? 0 : 1;
    if (condition === 'dead') game.s.down = 1;
    if (condition === 'scripted') game.s.valkyrien.phase = 'house';
    game.update(t, 0);
    assert.equal(game.s.p.vy, 0, condition);
    assert.deepEqual(sounds, [], condition);
    assert.equal(game.s.rainbowBoosts.length, 0, condition);
  }
});

test('collision uses the visible segments and catches fast crossings', () => {
  const r = rainbow(), point = ribbonPoints(r)[2];
  const crossing = ribbonContact(r, t, { x: point.x, y: point.y + 50 }, { x: point.x, y: point.y - 30 });
  assert.equal(crossing.hit, true);
  assert.ok(crossing.point);
  assert.ok(ribbonPoints(r).some(segment =>
    Math.abs(crossing.point.x - segment.x) <= 3 && Math.abs(crossing.point.y - segment.y) <= 7));
  assert.equal(ribbonContact(r, t, { x: 250, y: 30 }, { x: 250, y: 100 }).hit, false);
  r.landing = { x: r.x, y: r.y, length: 60 };
  assert.equal(ribbonLength(r, RAINBOW_T1 + 0.61), 0);
  assert.equal(ribbonContact(r, RAINBOW_T1 + 0.61, point, point).hit, false);
  r.blend = 0;
  assert.equal(ribbonContact(r, t, point, point).hit, false);
});

test('shockwave originates at contact and the label expires after 0.8 seconds', () => {
  const { game } = setup();
  const p = game.s.p, point = ribbonPoints(game.s.rainbow)[2];
  p.x = point.x; p.y = point.y + 10; p.jumps = 1; p.vy = 120;
  const contact = ribbonContact(game.s.rainbow, t, p, p);
  game.update(t, 0);
  assert.deepEqual(game.s.rainbowBoosts[0], { ...contact.point, age: 0 });
  assert.equal(RAINBOW_BOOST_EFFECT_DURATION, 0.4);
  game.update(t + 0.2, 0.2);
  assert.equal(game.s.rainbowBoosts[0].age, 0.2);
  game.update(t + 0.4, 0.2);
  assert.equal(game.s.rainbowBoosts[0].age, 0.4);
  game.update(t + 0.8, 0.4);
  assert.equal(game.s.rainbowBoosts.length, 0);
  game.s.rainbowBoosts.push({ x: 1, y: 1, age: 0 });
  game.audio.play = () => {};
  game.seek(t);
  assert.equal(game.s.rainbowBoosts.length, 0);
});

test('a fast fall through a low ribbon boosts before ground landing', () => {
  const { game } = setup();
  const p = game.s.p;
  game.s.rainbow.y = GROUND - 5;
  game.s.rainbow.path = [{ x: 60, y: GROUND - 20, t }];
  const point = ribbonPoints(game.s.rainbow)[2];
  p.x = point.x; p.y = GROUND - 40; p.vy = 500; p.jumps = 1;
  game.update(t + 0.05, 0.05);
  assert.equal(p.vy, -420);
  assert.ok(p.y < GROUND);
});

test('the boost never slows an already faster upward jump', () => {
  const { game } = setup();
  const point = ribbonPoints(game.s.rainbow)[2];
  game.s.p.x = point.x; game.s.p.y = point.y + 10;
  game.s.p.jumps = 1; game.s.p.vy = -500;
  game.update(t, 0);
  assert.equal(game.s.p.vy, -500);
});

test('remaining in the ribbon does not boost again when the cooldown expires', () => {
  const { game, sounds } = setup();
  const p = game.s.p, point = ribbonPoints(game.s.rainbow)[2];
  p.x = point.x; p.y = point.y + 10; p.jumps = 1; p.vy = 120;
  game.update(t, 0);
  p.rainbowCooldown = 0;
  p.vy = -200;
  game.update(t, 0);
  assert.equal(p.vy, -200);
  assert.deepEqual(sounds, ['jump']);
});

test('exit clipping continues to cover the screen after Valkyrien scrolls away', () => {
  for (const time of [barT(54), barT(58), barT(66), barT(76)]) {
    const clip = exitSurfaceClip(time);
    assert.equal(clip.x, exitX(time) + EXIT_HOUSE_LEFT);
    assert.ok(clip.x <= 0);
    assert.equal(clip.x + clip.width, W);
  }
});

test('an offscreen player and companions return after two seconds, without a death', () => {
  const { game } = setup();
  game.s.lastT = barT(58);
  game.s.p.x = -100; game.s.p.y = GROUND; game.s.p.vy = 0;
  for (let i = 0; i < 39; i++) game.update(game.s.lastT + 0.05, 0.05);
  assert.equal(game.s.p.x, -100);
  game.update(game.s.lastT + 0.05, 0.05);
  assert.equal(game.s.p.x, PX);
  assert.equal(game.s.p.y, GROUND - 35);
  assert.equal(game.s.fx, PX - 22);
  assert.equal(game.s.mx, PX - 46);
  assert.equal(game.s.continues, 0);
  assert.equal(game.s.down, 0);
});

test('offscreen recovery uses the camera and resets when the player returns', () => {
  const { game } = setup();
  game.s.valkyrien.phase = 'underground';
  game.s.valkyrien.camera = VALKYRIEN_FLOOR - GROUND;
  game.s.p.x = PX;
  game.s.p.y = VALKYRIEN_CEILING + 32;
  game.s.p.offscreenTime = 1.9;
  game.update(t, 0);
  assert.equal(game.s.p.offscreenTime, 0);
  game.s.p.y = game.s.valkyrien.camera - 20;
  game.s.p.vy = -100;
  game.update(t, 0.05);
  assert.equal(game.s.p.offscreenTime, 0);
});

test('offscreen recovery does not interrupt scripted movement or death', () => {
  for (const condition of ['scripted', 'dead']) {
    const { game } = setup();
    game.s.lastT = barT(58);
    game.s.p.x = -100;
    game.s.p.offscreenTime = 1.99;
    if (condition === 'scripted') game.s.valkyrien.phase = 'house';
    else game.s.down = 1;
    game.update(game.s.lastT + 0.05, 0.05);
    assert.notEqual(game.s.p.x, PX, condition);
    assert.equal(game.s.p.offscreenTime, 0, condition);
  }
});

test('a player completely above the screen is recovered after two seconds', () => {
  const { game } = setup();
  game.s.lastT = barT(58);
  game.s.p.y = -H;
  game.s.p.vy = -10000;
  game.s.p.jumps = 1;
  game.s.p.offscreenTime = 1.99;
  game.update(game.s.lastT + 0.05, 0.05);
  assert.equal(game.s.p.x, PX);
  assert.equal(game.s.p.y, GROUND - 35);
});
