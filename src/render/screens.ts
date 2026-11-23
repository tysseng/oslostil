// Composes a full frame: game view + HUD, title screen, win screen.
import { BAR, BEAT, FINAL_HIT, GROUND, H, PH, PLAYER_MAX_HP, W, barAt, barT } from '../config';
import type { Game } from '../game';
import { enemyX } from '../state';
import { itemLayer } from '../schedule';
import { BANNERS, BANNER_TIME, COLOR_T, NINJA_T, SECTIONS, VICTORIA_WAKE_T, WAKE_HOPS, WAKE_RISE, beatPhase, BOSS_AT, bossVisible, bossX, isNinja, lyricAt, sectionAt, victoriaBob, victoriaLift } from '../timeline';
import { R, ctx, drawHiRes, flash, loadImage, ready, resetTransform, text } from './draw';
import { SKY, drawScene, sky } from './scenes';
import { drawBoss, drawEnemy, drawEnemySprite, drawGirl, drawLampLights, drawMachine, type Mood } from './sprites';
import titleLogoUrl from '../../assets/ui/title-logo.png';

const TITLE_LOGO = loadImage(titleLogoUrl);

export function drawGame(g: Game, t: number, dev: boolean): void {
  const s = g.s, sec = sectionAt(t), beatFlash = Math.max(0, 1 - beatPhase(t, BEAT) * 4);
  if (s.shake > 0) resetTransform(Math.round((Math.random() - 0.5) * 24 * s.shake), Math.round((Math.random() - 0.5) * 24 * s.shake));
  drawScene(sec.scene, t, s.bgx, beatFlash, s.taggerStoppedAt);
  const prev = SECTIONS[SECTIONS.indexOf(sec) - 1];
  if (prev && prev.scene !== sec.scene) flash(t, barT(sec.a), 0.25, '#fff'); // scene cut on the downbeat
  flash(t, COLOR_T, 0.35, '#ff2b4a'); // «skjermen skifter farge»
  flash(t, NINJA_T, 0.4, '#fff'); // ninja transformation
  for (const layer of [0, 1]) {
    for (const e of s.enemies) if (!e.dead && itemLayer(e.type) === layer) drawEnemy(e, enemyX(e, t), t);
  }
  if (bossVisible(t)) {
    // walks in for a bar, then fires its coupler cannon on every beat and idles in between
    const walking = t - BOSS_AT < BAR, ph = beatPhase(t, BEAT);
    const [anim, at] = walking ? ['walk', ((t - BOSS_AT) / (2 * BEAT)) % 1] as const
      : ph < 0.4 ? ['attack', ph / 0.4] as const : ['idle', ((t * 4) % 4) / 4] as const;
    drawBoss(bossX(t), s.boss.hit > 0, s.boss.hp, s.boss.max, anim, at);
  }
  for (const e of s.enemies) if (!e.dead && itemLayer(e.type) === 2) drawEnemy(e, enemyX(e, t), t);
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
  // companions
  if (!s.deathFlight?.machine && t >= VICTORIA_WAKE_T) drawMachine(s.mx, GROUND - victoriaLift(t), t, machineMood(t), victoriaBob(t), t >= VICTORIA_WAKE_T + WAKE_HOPS);
  const ninja = isNinja(t), f = s.friend, fy = f.yHist.length ? f.yHist[0] : GROUND;
  const fRising = f.yHist.length > 1 && f.yHist[1] < f.yHist[0];
  if (!s.deathFlight?.friend) drawGirl('friend', s.fx, fy, t + 0.13, { ninja, air: fy < GROUND, rising: fRising, atk: f.atk > 0 });
  // gone while dead; after respawning she flashes white, after an ordinary hit she blinks
  const white = s.respawn > 0 && Math.floor(s.respawn * 8) % 2 === 1;
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
  if (s.down <= 0 && (s.respawn > 0 || !(s.inv > 0 && Math.floor(t * 20) % 2))) {
    drawGirl('victoria', s.p.x, s.p.y, t, { white, ninja, air: s.p.y < GROUND, rising: s.p.vy < 0, slide: s.p.slide > 0, atk: s.p.atk > 0 });
  }
  for (const st of s.stars) {
    ctx.save(); ctx.translate(st.x, st.y); ctx.rotate(st.a);
    if (st.ninja) { R(-3, -1, 6, 2, '#dfe6ee'); R(-1, -3, 2, 6, '#dfe6ee'); } // shuriken
    else { R(-4, -2, 8, 5, '#3a2a10'); R(-3, -1, 6, 3, '#ffd84a'); R(-3, 1, 6, 1, '#e0a91c'); } // thrown ticket
    ctx.restore();
  }
  for (const q of s.parts) R(q.x, q.y, 2, 2, q.c);
  drawLampLights(s.enemies, t);
  for (const q of s.pops) text(q.txt, q.x, q.y, q.c, 6, 'center');
  resetTransform();

  if (t >= FINAL_HIT) { // «-STIL!»
    const k = Math.min(1, (t - FINAL_HIT) * 3);
    flash(t, FINAL_HIT, 0.5, '#fff');
    text('OSLO-STIL!', W / 2, 70 - k * 10, '#ff2bd6', 16 + Math.round(k * 4), 'center', '#2bf0ff');
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
  if (g.musicToast > 0) text(g.audio.musicMuted ? 'MUSIKK AV · MUSIC OFF' : 'MUSIKK PÅ · MUSIC ON', W - 4, 18, '#7cf', 5, 'right');
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
  text('P / ENTER: FORTSETT · RESUME', W / 2, 104, '#ccc', 6, 'center');
}

function drawStartupBackdrop(t: number, titleLogo = false): void {
  sky(SKY.neon);
  for (let i = 0; i < 12; i++) R((((i * 32 - t * 60) % 384) + 384) % 384 - 32, GROUND, 1, H - GROUND, '#ff4fd8');
  R(0, GROUND, W, H - GROUND, '#160022'); R(0, GROUND, W, 1, '#ff4fd8');
  if (titleLogo) {
    if (ready(TITLE_LOGO)) drawHiRes(TITLE_LOGO, 54.4, 11.6, 211.2, 70.4);
  } else text('OSLO-STIL', W / 2, 28, '#ffe14a', 24, 'center', '#ff2bd6');
}

export function drawTitle(t: number, loading: boolean): void {
  drawStartupBackdrop(t, true);
  text('AN AUTOMAT VICTORIA ADVENTURE', W / 2, 80, '#2bf0ff', 6, 'center');
  drawGirl('friend', 130, GROUND, t, { ninja: false, idle: true });
  drawGirl('victoria', 152, GROUND, t + 0.5, { ninja: false, idle: true });
  drawMachine(184, GROUND - 4, t, 'idle', 2, true);
  const promptY = Math.round((80 + 6 + GROUND - 32 - 7) / 2);
  if (loading) text('LASTER SPILL …', W / 2, promptY, '#fff', 6, 'center');
  else if (Math.floor(t * 2) % 2) text('Trykk enter for å aktivere tekst-til-tale.', W / 2, promptY, '#fff', 7, 'center');
  text('SPACE/↑ HOPP·JUMP   ↓ SKLI·SLIDE   X SLÅ·HIT', W / 2, GROUND + 8, '#ccc', 5, 'center');
  text('C KAST·THROW   ←→ FLYTT·MOVE   P PAUSE   M MUSIKK·MUSIC', W / 2, GROUND + 18, '#ccc', 5, 'center');
}

export function drawWin(g: Game, t: number, place: number): void {
  const s = g.s;
  sky(SKY.neon); R(0, GROUND, W, H - GROUND, '#160022');
  for (let i = 0; i < 24; i++) {
    const a = (i / 24) * Math.PI * 2 + t;
    R(W / 2 + Math.cos(a) * (60 + Math.sin(t * 3 + i) * 10), 78 + Math.sin(a) * 40, 2, 2, ['#ff2bd6', '#2bf0ff', '#ffe14a'][i % 3]);
  }
  text('DU VANT!', W / 2, 16, '#ffe14a', 16, 'center', '#ff2bd6');
  text('YOU WIN!', W / 2, 38, '#2bf0ff', 8, 'center');
  const rows: [string, number][] = [
    ['SCORE', s.score], ['FIENDER · ENEMIES', s.kills], ['BILLETTER · TICKETS', s.tickets],
    ['PERFECT', s.perfect], ['CONTINUES', s.continues], ['BEST', s.best ?? s.score],
  ];
  rows.forEach(([k, v], i) => { text(k, 70, 58 + i * 11, '#ccc', 6); text(String(v), 250, 58 + i * 11, '#fff', 6, 'right'); });
  const rank = s.continues === 0 && s.score > 30000 ? 'OSLOSTIL-MESTER' : s.continues <= 1 ? 'TIGERSTADEN-NINJA' : 'TRIKKETURIST';
  text(rank, W / 2, 128, '#ff2bd6', 8, 'center');
  drawGirl('friend', 16, GROUND, t, { ninja: true, idle: true });
  drawGirl('victoria', 42, GROUND, t + 0.2, { ninja: true, idle: true, atk: Math.floor(t * 2) % 2 === 1 });
  drawMachine(286, GROUND - 4, t, 'cheer', 2, true);
  text(place > 10 ? 'GAME OVER' : place === 1 ? 'NEW HIGHSCORE!' : `YOU PLACED #${place}`, W / 2, 154, place === 1 ? '#ffe14a' : '#ccc', 6, 'center');
  if (Math.floor(t * 2) % 2) text('ENTER: HIGHSCORE', W / 2, 166, '#fff', 5, 'center');
}

export function drawHighscore(t: number): void {
  drawStartupBackdrop(t);
}
