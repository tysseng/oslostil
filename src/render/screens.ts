// Composes a full frame: game view + HUD, title screen, win screen.
import { BAR, BEAT, FINAL_HIT, FONT, GROUND, H, PH, PLAYER_MAX_HP, W, barAt, barT } from '../config';
import type { Game } from '../game';
import { compareItems, enemyX } from '../state';
import { isBackgroundBuilding, isDealership, isTree, isWallPoster, itemLayer } from '../schedule';
import { drawDealershipBeams } from './neon-dealership';
import { BANNERS, BANNER_TIME, COLOR_T, NINJA_T, SECTIONS, VICTORIA_WAKE_T, WAKE_HOPS, WAKE_RISE, beatPhase, BOSS_AT, bossVisible, bossX, isNinja, lyricAt, sectionAt } from '../timeline';
import { R, ctx, flash, loadImage, ready, resetTransform, text } from './draw';
import { SKY, drawScene, sky } from './scenes';
import { drawBlobPop, drawBoss, drawCelebrating, drawEnemy, drawEnemySprite, drawGirl, drawLampLights, drawMachine, drawRainbowMachine, type Mood } from './sprites';
import titleLogoUrl from '../../assets/ui/title-logo-pixel.png';
import titleLogoLightUrl from '../../assets/ui/title-logo-pixel-light.png';
import { ENTRY_HALF_WIDTH, EXIT_HOUSE_RIGHT, STAIRS_WIDTH, VALKYRIEN_CEILING, clampStationY, exitSurfaceClip, exitX, stationEntryX, playerFloor, stairCompanionPosition } from '../valkyrien';
import { machinePosition } from '../rainbow';
import { drawUndergroundFill, drawValkyrien, drawValkyrienBalustrade, drawValkyrienDarkness, drawValkyrienHouse } from './valkyrien';
import { drawRainbowBoost } from './rainbow-boost';

const TITLE_LOGO = loadImage(titleLogoUrl);
const TITLE_LOGO_LIGHT = loadImage(titleLogoLightUrl); // 16 px padding on every side

export function drawGame(g: Game, t: number, dev: boolean): void {
  const s = g.s, sec = sectionAt(t), beatFlash = Math.max(0, 1 - beatPhase(t, BEAT) * 4);
  if (s.shake > 0) resetTransform(Math.round((Math.random() - 0.5) * 24 * s.shake), Math.round((Math.random() - 0.5) * 24 * s.shake));
  else if (s.boardShake > 0) resetTransform(Math.round((Math.random() - 0.5) * 4), Math.round((Math.random() - 0.5) * 4));
  ctx.translate(0, -s.valkyrien.camera);
  const items = s.enemies.slice().sort(compareItems);
  drawScene(sec.scene, t, s.bgx, beatFlash, s.taggerStoppedAt, () => {
    for (const e of items) if (!e.dead && (isTree(e.type) || isBackgroundBuilding(e.type))) drawEnemy(e, enemyX(e, t), t);
  });
  drawValkyrien(t, 0, W, () => {
    for (const e of items) if (!e.dead && isWallPoster(e.type)) drawEnemy(e, enemyX(e, t), t);
  });
  drawValkyrienHouse(t);
  const prev = SECTIONS[SECTIONS.indexOf(sec) - 1];
  if (prev && prev.scene !== sec.scene) flash(t, barT(sec.a), 0.25, '#fff'); // scene cut on the downbeat
  flash(t, COLOR_T, 0.35, '#ff2b4a'); // «skjermen skifter farge»
  flash(t, NINJA_T, 0.4, '#fff'); // ninja transformation
  for (const e of items) if (!e.dead && !isTree(e.type) && !isBackgroundBuilding(e.type) && !isWallPoster(e.type) && itemLayer(e.type) <= 1) drawEnemy(e, enemyX(e, t), t);
  if (bossVisible(t)) {
    // walks in for a bar, then fires its coupler cannon on every beat and idles in between
    const walking = t - BOSS_AT < BAR, ph = beatPhase(t, BEAT);
    const [anim, at] = walking ? ['walk', ((t - BOSS_AT) / (2 * BEAT)) % 1] as const
      : ph < 0.4 ? ['attack', ph / 0.4] as const : ['idle', ((t * 4) % 4) / 4] as const;
    drawBoss(bossX(t), s.boss.hit > 0, s.boss.hp, s.boss.max, anim, at);
  }
  for (const e of s.enemies) if (!e.dead && itemLayer(e.type) === 2) drawEnemy(e, enemyX(e, t), t);
  for (const pop of s.blobPops) drawBlobPop(pop);
  for (const drop of s.droppings) {
    if (drop.landed) {
      R(drop.x - 5, drop.y - 2, 10, 2, '#dce3c8');
      R(drop.x - 2, drop.y - 3, 4, 2, '#fffce9');
      R(drop.x + 1, drop.y - 2, 2, 1, '#7b8556');
    } else {
      R(drop.x - 1, drop.y - 3, 2, 5, '#fffce9');
      R(drop.x - 2, drop.y, 4, 2, '#dce3c8');
    }
  }
  for (const q of s.knocked) {
    ctx.save();
    if (q.squash !== undefined) {
      ctx.translate(q.x, q.y);
      ctx.scale(1.4, 0.25);
      ctx.translate(-q.x, -q.y);
    }
    drawEnemy({ ...q.enemy, y: GROUND - q.y }, q.x, t);
    ctx.restore();
  }
  const friendStairs = stairCompanionPosition(s, s.fx, t);
  if (s.valkyrien.ascendingAt !== undefined && (s.valkyrien.phase === 'stairs' || stairCompanionPosition(s, s.mx, t) || friendStairs)) {
    ctx.save();
    ctx.beginPath();
    ctx.rect(exitX(t) - STAIRS_WIDTH - 24, 0, STAIRS_WIDTH + 24 + EXIT_HOUSE_RIGHT, GROUND + 30);
    ctx.clip();
    drawScene(sec.scene, t, s.bgx, beatFlash, s.taggerStoppedAt);
    drawValkyrienHouse(t);
    ctx.restore();
    drawUndergroundFill(exitX(t) - STAIRS_WIDTH - 24, GROUND, STAIRS_WIDTH + 24 + EXIT_HOUSE_RIGHT,
      VALKYRIEN_CEILING - GROUND);
  }
  // companions
  const inChute = s.valkyrien.phase === 'chute';
  const entering = s.valkyrien.descendingAt !== undefined && s.valkyrien.ascendingAt === undefined
    && (inChute || friendStairs !== null || stairCompanionPosition(s, s.mx, t) !== null);
  ctx.save();
  if (entering) {
    ctx.beginPath();
    ctx.rect(-1000, VALKYRIEN_CEILING, 2000, 1000);
    ctx.rect(stationEntryX(t) - ENTRY_HALF_WIDTH, 0, ENTRY_HALF_WIDTH * 2, GROUND);
    ctx.clip();
  }
  if (s.valkyrien.ascendingAt !== undefined) {
    const clip = exitSurfaceClip(t);
    ctx.beginPath();
    ctx.rect(-1000, VALKYRIEN_CEILING, 2000, 1000);
    ctx.rect(clip.x, 0, clip.width, GROUND);
    ctx.clip();
  }
  if (!s.deathFlight?.machine && t >= VICTORIA_WAKE_T) {
    if (s.rainbow) drawRainbowMachine(s.rainbow, t, machineMood(t));
    else {
      const machine = machinePosition(s, t);
      drawMachine(machine.x, machine.y, t, machineMood(t), 0, t >= VICTORIA_WAKE_T + WAKE_HOPS);
    }
  }
  const ninja = isNinja(t), f = s.friend, fy = friendStairs?.y ?? clampStationY(s, f.yHist.length ? f.yHist[0] : GROUND, 32);
  const fRising = f.yHist.length > 1 && f.yHist[1] < f.yHist[0];
  if (!s.deathFlight?.friend) drawGirl('friend', s.fx, fy, t + 0.13, { ninja, air: !friendStairs && fy < playerFloor(s) && s.valkyrien.phase !== 'stairs', rising: fRising, atk: f.atk > 0 });
  // gone while dead; after respawning she flashes white, after an ordinary hit she blinks
  const white = s.healFlash > 0 || s.respawn > 0 && Math.floor(s.respawn * 8) % 2 === 1;
  if (s.deathFlight) {
    const flight = s.deathFlight;
    for (const member of ['victoria', 'friend', 'machine'] as const) {
      const motion = member === 'victoria' ? flight : flight[member];
      if (!motion) continue;
      ctx.save();
      ctx.translate(motion.x, motion.y - 16);
      ctx.rotate(motion.angle);
      if (member === 'machine') drawMachine(0, 16, t, machineMood(t), 0);
      else drawGirl(member, 0, 16, t, { ninja, air: true });
      ctx.restore();
    }
  }
  if (s.down <= 0 && (s.healFlash > 0 || s.respawn > 0 || !(s.inv > 0 && Math.floor(t * 20) % 2))) {
    drawGirl('victoria', s.p.x, s.p.y, t, { white, ninja, air: s.p.y < playerFloor(s) && s.valkyrien.phase !== 'stairs' && !inChute, rising: s.p.vy < 0, slide: s.p.slide > 0, atk: s.p.atk > 0 });
  }
  ctx.restore();
  for (const st of s.stars) {
    ctx.save(); ctx.translate(st.x, st.y); ctx.rotate(st.a);
    if (st.ninja) { R(-3, -1, 6, 2, '#dfe6ee'); R(-1, -3, 2, 6, '#dfe6ee'); } // shuriken
    else { R(-4, -2, 8, 5, '#3a2a10'); R(-3, -1, 6, 3, '#ffd84a'); R(-3, 1, 6, 1, '#e0a91c'); } // thrown ticket
    ctx.restore();
  }
  for (const q of s.parts) R(q.x, q.y, 2, 2, q.c);
  for (const e of items) if (!e.dead && isDealership(e.type)) drawDealershipBeams(enemyX(e, t), GROUND - e.y);
  drawLampLights(s.enemies, t);
  for (const q of s.pops) text(q.txt, q.x, q.y, q.c, 6, 'center');
  drawValkyrienBalustrade(t);
  if (s.valkyrien.ascendingAt !== undefined) drawValkyrienHouse(t, 0, W, true);
  drawValkyrienDarkness(t, () => {
    for (const e of s.enemies) if (!e.dead && !isWallPoster(e.type)) drawEnemy(e, enemyX(e, t), t);
    for (const q of s.knocked) {
      ctx.save();
      if (q.squash !== undefined) {
        ctx.translate(q.x, q.y);
        ctx.scale(1.4, 0.25);
        ctx.translate(-q.x, -q.y);
      }
      drawEnemy({ ...q.enemy, y: GROUND - q.y }, q.x, t);
      ctx.restore();
    }
    drawValkyrienBalustrade(t);
  }, s.enemies);
  for (const effect of s.rainbowBoosts) drawRainbowBoost(effect, s.valkyrien.camera);
  resetTransform();

  if (t >= FINAL_HIT) { // «-STIL!»
    const k = Math.min(1, (t - FINAL_HIT) * 3);
    flash(t, FINAL_HIT, 0.5, '#fff');
    text('OSLOSTIL!', W / 2, 70 - k * 10, '#ff2bd6', 16 + Math.round(k * 4), 'center', '#2bf0ff');
  }
  // HUD
  R(0, 0, W, 14, '#000000aa');
  text('SCORE ' + String(s.score).padStart(6, '0'), 4, 3, '#fff', 6);
  R(109, 2, 45, 8, '#ff2bd6');
  R(110, 3, 43, 6, '#300b3b');
  R(111, 4, 41 * Math.max(0, Math.min(1, s.hp / PLAYER_MAX_HP)), 4, '#7028b8');
  if (s.combo > 3) text('COMBO x' + s.combo, 202, 3, '#ffe14a', 6);
  if (s.power > t) text('★★★', 262, 3, '#7cf', 6);
  drawEnemySprite('ticket', 168, 10, 0); // ammo: tickets left to throw
  text('×' + s.ammo, 177, 3, s.ammo > 0 ? '#ffd84a' : '#ff6060', 6);
  R(286, 5, 30, 4, '#333'); R(286, 5, 30 * Math.min(1, t / FINAL_HIT), 4, '#2bf0ff');
  if (dev) text('DEV', 286, 11, '#ff2bd6', 4, 'left', null);
  // banner: only the newest one, so a new beat replaces the previous at once
  let banner: (typeof BANNERS)[number] | undefined;
  for (const b of BANNERS) if (t > b[0]) banner = b;
  if (banner && t - banner[0] < BANNER_TIME) {
    const y = 34 + Math.max(0, (0.12 - (t - banner[0])) * 200);
    text(banner[1], W / 2, y, '#ffe14a', 10, 'center', '#ff2bd6');
    text(banner[2], W / 2, y + 15, '#fff', 6, 'center');
  }
  // chorus «OSLOSTIL!» calls
  if (sec.id.startsWith('chorus') && [1, 3, 5].includes(barAt(t) - sec.a) && (((t - PH) % BAR) + BAR) % BAR < 0.5) {
    text('OSLOSTIL!', W - 6, 20, '#2bf0ff', 8, 'right', '#ff2bd6');
  }
  if (g.musicToast > 0) text(g.audio.musicMuted ? 'MUSIKK AV' : 'MUSIKK PÅ', W - 4, 18, '#7cf', 5, 'right');
  else if (g.syncToast > 0) {
    const off = g.audio.syncOffset;
    text('SYNC ' + (off >= 0 ? '+' : '') + Math.round(off * 1000) + ' MS', W - 4, 18, '#7cf', 5, 'right');
  }
}

/** Automat Victoria talks when the lyrics are about her, and cheers on the chorus «OSLOSTIL!» calls and the final hit. */
function machineMood(t: number): Mood {
  if (t >= FINAL_HIT) return 'cheer';
  const sec = sectionAt(t);
  if (sec.id.startsWith('chorus') && [1, 3, 5].includes(barAt(t) - sec.a) && (((t - PH) % BAR) + BAR) % BAR < 0.8) return 'cheer';
  const line = lyricAt(t)?.text ?? '';
  if (t >= VICTORIA_WAKE_T && t < VICTORIA_WAKE_T + WAKE_HOPS + WAKE_RISE) return 'cheer'; // waking up
  if (/automat|(^|[\s«])hun\s/i.test(line) || (t > VICTORIA_WAKE_T && t < VICTORIA_WAKE_T + BANNER_TIME)) return 'talk';
  return 'idle';
}

export function drawPause(): void {
  ctx.globalAlpha = 0.6; R(0, 0, W, H, '#000'); ctx.globalAlpha = 1;
  text('PAUSE', W / 2, 80, '#fff', 16, 'center');
  text('P / ENTER: FORTSETT', W / 2, 104, '#ccc', 6, 'center');
  text('ESC: TIL INTRO', W / 2, 115, '#ccc', 6, 'center');
}

function drawStartupBackdrop(t: number, titleLogo = false): void {
  sky(SKY.neon);
  for (let i = 0; i < 12; i++) R((((i * 32 - t * 60) % 384) + 384) % 384 - 32, GROUND, 1, H - GROUND, '#ff4fd8');
  R(0, GROUND, W, H - GROUND, '#160022'); R(0, GROUND, W, 1, '#ff4fd8');
  if (titleLogo) {
    // Pixel-art logo, 1 image px = 1 game px, unsmoothed at whole pixels; lamp light in front.
    if (ready(TITLE_LOGO)) ctx.drawImage(TITLE_LOGO, 54, 12);
    if (ready(TITLE_LOGO_LIGHT)) ctx.drawImage(TITLE_LOGO_LIGHT, 54 - 16, 12 - 16);
  } else text('OSLOSTIL', W / 2, 28, '#ffe14a', 24, 'center', '#ff2bd6');
}

function drawTitleControls(musicMuted: boolean): void {
  const y = GROUND + 18, size = 5, color = '#ccc';
  const prefix = 'C KAST   ', suffix = ` LØP   P PAUSE   M MUSIKK (${musicMuted ? 'AV' : 'PÅ'})`;
  ctx.font = `${size}px ${FONT}`;
  const arrowWidth = ctx.measureText('↑').width;
  const prefixWidth = ctx.measureText(prefix).width;
  const slashWidth = ctx.measureText('/').width;
  const padding = 1;
  const left = Math.round((W - prefixWidth - 2 * arrowWidth - slashWidth - 2 * padding - ctx.measureText(suffix).width) / 2);
  text(prefix, left, y, color, size);
  const arrow = (x: number, leftward: boolean) => {
    ctx.save();
    ctx.translate(x + arrowWidth / 2, y + size / 2);
    if (leftward) ctx.scale(-1, 1);
    ctx.rotate(Math.PI / 2);
    text('↑', 0, -size / 2, color, size, 'center');
    ctx.restore();
  };
  arrow(left + prefixWidth, true);
  text('/', left + prefixWidth + arrowWidth + padding, y, color, size);
  arrow(left + prefixWidth + arrowWidth + slashWidth + 2 * padding, false);
  text(suffix, left + prefixWidth + 2 * arrowWidth + slashWidth + 2 * padding, y, color, size);
}

export function drawTitle(t: number, loading: boolean, musicMuted: boolean): void {
  drawStartupBackdrop(t, true);
  text('ET AUTOMAT VICTORIA SPILL', W / 2, 87, '#2bf0ff', 6, 'center');
  drawGirl('friend', 130, GROUND, t, { ninja: false, idle: true });
  drawGirl('victoria', 152, GROUND, t + 0.5, { ninja: false, idle: true });
  drawMachine(184, GROUND - 4, t, 'idle', 2, true);
  const promptY = Math.round((80 + 6 + GROUND - 32 - 7) / 2);
  if (loading) text('LASTER SPILL …', W / 2, promptY, '#fff', 6, 'center');
  else if (t % 1.5 < 1) text('Trykk enter for å aktivere tekst-til-tale.', W / 2, promptY, '#fff', 7, 'center');
  text('SPACE/↑ HOPP   ↓ SKLI/NED   X SLÅ   ESC PAUSE/INTRO', W / 2, GROUND + 8, '#ccc', 5, 'center');
  drawTitleControls(musicMuted);
}

export function drawCelebration(g: Game): void {
  const c = g.s.celebration;
  if (!c) return;
  if (g.s.shake > 0) resetTransform(Math.round((Math.random() - 0.5) * 24 * g.s.shake), Math.round((Math.random() - 0.5) * 24 * g.s.shake));
  drawScene(sectionAt(FINAL_HIT).scene, FINAL_HIT, g.s.bgx, 0, g.s.taggerStoppedAt);
  for (const q of g.s.parts) R(q.x, q.y, 2, 2, q.c);
  flash(FINAL_HIT + c.elapsed, FINAL_HIT, 0.5, '#fff');
  resetTransform();
  text('OSLOSTIL!', W / 2, 45, '#ff2bd6', 20, 'center', '#2bf0ff');
  const walkTime = 1.8, walk = Math.min(1, c.elapsed / walkTime);
  for (const [member, target, delay] of [['friend', 134, 0.15], ['victoria', 160, 0], ['machine', 186, 0.3]] as const) {
    const start = c[member], x = start.x + (target - start.x) * walk;
    const y = start.y + (GROUND - start.y) * Math.min(1, c.elapsed / 0.45);
    if (c.elapsed >= walkTime) drawCelebrating(member, x, GROUND, Math.max(0, c.elapsed - walkTime - delay));
    else if (member === 'machine') drawMachine(x, y, c.elapsed, 'cheer', 0);
    else {
      ctx.save();
      if (target < start.x) { ctx.translate(x * 2, 0); ctx.scale(-1, 1); }
      drawGirl(member, x, y, c.elapsed, { ninja: true, air: y < GROUND, rising: false });
      ctx.restore();
    }
  }
}

export function drawWin(g: Game, t: number, place: number): void {
  const s = g.s;
  sky(SKY.neon); R(0, GROUND, W, H - GROUND, '#160022');
  for (let i = 0; i < 24; i++) {
    const a = (i / 24) * Math.PI * 2 + t;
    R(W / 2 + Math.cos(a) * (60 + Math.sin(t * 3 + i) * 10), 78 + Math.sin(a) * 40, 2, 2, ['#ff2bd6', '#2bf0ff', '#ffe14a'][i % 3]);
  }
  text('DU VANT!', W / 2, 16, '#ffe14a', 16, 'center', '#ff2bd6');
  const rows: [string, number][] = [
    ['SCORE', s.score], ['FIENDER', s.kills], ['BILLETTER', s.tickets],
    ['PERFECT', s.perfect], ['CONTINUES', s.continues], ['BEST', s.best ?? s.score],
  ];
  rows.forEach(([k, v], i) => { text(k, 70, 58 + i * 11, '#ccc', 6); text(String(v), 250, 58 + i * 11, '#fff', 6, 'right'); });
  const rank = s.continues === 0 && s.score > 30000 ? 'OSLOSTIL-MESTER' : s.continues <= 1 ? 'TIGERSTADEN-NINJA' : 'TRIKKETURIST';
  text(rank, W / 2, 128, '#ff2bd6', 8, 'center');
  drawCelebrating('friend', 16, GROUND, t);
  drawCelebrating('victoria', 42, GROUND, t + 0.2);
  drawCelebrating('machine', 286, GROUND, t + 0.4);
  text(place > 10 ? 'GAME OVER' : place === 1 ? 'NEW HIGHSCORE!' : `YOU PLACED #${place}`, W / 2, 154, place === 1 ? '#ffe14a' : '#ccc', 6, 'center');
}

export function drawHighscore(t: number): void {
  drawStartupBackdrop(t);
}
