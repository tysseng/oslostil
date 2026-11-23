// Game rules: spawning, physics, combat, scoring and keyboard controls.
import { AudioEngine } from './audio';
import { BAR, BEAT, FINAL_HIT, GROUND, H, PH, PX, W, WIN_AT, barT } from './config';
import { TRAM_EDGE, TRAM_LEN, TRAM_ROOF, TYPES } from './schedule';
import { loadDefaultLevel } from './level';
import { createEnemy, createState, enemyX, spawnTime, type Enemy, type GameState } from './state';
import { VICTORIA_WAKE_T, WAKE_HOPS, bossVisible, bossX, isNinja, machineCenter, sectionAt } from './timeline';

/** seconds she is gone after losing her last heart */
const DEATH_TIME = 0.55;
/** seconds of white flashing (and invincibility) after she drops back in */
const RESPAWN_FLASH = 1.2;
/** she drops back in from this height (screen y of her feet) */
const DROP_Y = GROUND - 100;

export type Mode = 'loading' | 'title' | 'play' | 'pause' | 'win' | 'editor';
const BEST_KEY = 'oslostil-best';

export class Game {
  level = loadDefaultLevel();
  s: GameState = createState(this.level);
  mode: Mode = 'loading';
  readonly keys = new Set<string>();
  /** seconds left of the on-screen sync readout */
  syncToast = 0;
  /** seconds left of the on-screen music on/off readout */
  musicToast = 0;
  /** called by the development time-mark shortcut */
  onMark: (t: number) => void = () => {};

  constructor(readonly audio: AudioEngine) {}

  start(): void { this.seek(0); }

  /** Jump the song and the game to time t (also used by the debug panel). */
  seek(t: number): void {
    t = Math.max(0, Math.min(WIN_AT - 0.5, t));
    this.s = createState(this.level);
    this.s.lastT = t;
    this.s.bgx = scrollAt(t);
    this.audio.play(t);
    this.mode = 'play';
  }

  edit(t = this.s.lastT): void {
    this.audio.pause();
    this.keys.clear();
    this.s = createState(this.level);
    this.s.lastT = Math.max(0, Math.min(WIN_AT - 0.5, t));
    this.s.bgx = scrollAt(this.s.lastT);
    this.mode = 'editor';
  }

  pause(): void { if (this.mode === 'play') { this.mode = 'pause'; this.audio.pause(); } }
  resume(): void { if (this.mode === 'pause') { this.mode = 'play'; this.audio.resume(); } }

  // ---------- input ----------
  keyDown(e: KeyboardEvent): void {
    if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) e.preventDefault();
    if (this.keys.has(e.code)) return;
    this.keys.add(e.code);
    const c = e.code;
    if (this.mode === 'title' && (c === 'Enter' || c === 'Space')) return this.start();
    if (this.mode === 'win' && c === 'Enter') return this.start();
    if (c === 'KeyM') { this.audio.toggleMusic(); this.musicToast = 1.5; }
    if (this.mode === 'play' && (c === 'KeyP' || c === 'Escape')) return this.pause();
    if (this.mode === 'pause' && (c === 'KeyP' || c === 'Escape' || c === 'Enter')) return this.resume();
    if (this.mode !== 'play' || this.s.down > 0) return; // no control while dead
    const p = this.s.p;
    if (c === 'Space' || c === 'ArrowUp' || c === 'KeyW') {
      if (p.jumps < 2) { p.vy = p.jumps ? -250 : -300; p.jumps++; p.slide = 0; this.audio.sfx('jump'); }
    }
    if (c === 'ArrowDown' || c === 'KeyS') { if (p.y >= GROUND || p.ride) p.slide = 0.45; else p.vy = 340; }
    if ((c === 'KeyX' || c === 'KeyJ') && p.cd <= 0) { p.atk = 0.18; p.cd = 0.22; this.audio.sfx('slash'); this.attack(); }
    if ((c === 'KeyC' || c === 'KeyK') && p.star <= 0) this.throwStar();
  }

  keyUp(e: KeyboardEvent): void { this.keys.delete(e.code); }

  // ---------- combat ----------
  private attack(): void {
    const { s } = this, p = s.p, reach = isNinja(s.lastT) ? 30 : 20;
    for (const e of s.enemies) {
      const ty = TYPES[e.type];
      if (e.dead || ty.pickup || ty.solid) continue;
      const ex = enemyX(e, s.lastT), ey = GROUND - e.y;
      if (ex > p.x - 4 && ex < p.x + reach + 8 && Math.abs(ey - ty.h / 2 - (p.y - 12)) < 26) this.hitEnemy(e, ex, ey, 2);
    }
  }

  private throwStar(): void {
    const { s } = this, p = s.p, powered = s.power > s.lastT;
    if (s.ammo <= 0) { // out of tickets
      p.star = 0.3;
      s.pops.push({ x: p.x, y: p.y - 34, txt: 'TOM! · EMPTY', life: 0.6, c: '#ff8080' });
      return;
    }
    s.ammo--;
    p.star = powered ? 0.14 : 0.3;
    this.audio.sfx('star');
    for (const vy of powered ? [-60, 0, 60] : [0]) {
      s.stars.push({ x: p.x + 8, y: p.y - (p.slide > 0 ? 6 : 14), vx: 300, vy, a: 0, ninja: isNinja(s.lastT) });
    }
  }

  private hitEnemy(e: Enemy, x: number, y: number, dmg: number): void {
    e.hp -= dmg;
    this.audio.sfx('hit');
    if (e.hp <= 0) { e.dead = true; this.award(x, y - 8, e.type === 'bot' ? 200 : e.type === 'ninja' ? 150 : 100); }
    else this.burst(x, y - 8, '#fff', 4);
  }

  private award(x: number, y: number, base: number): void {
    const { s } = this, perfect = nearBeat(s.lastT);
    s.combo++;
    const pts = base * (1 + Math.min(4, Math.floor(s.combo / 8))) * (perfect ? 2 : 1);
    s.score += pts; s.kills++;
    if (perfect) s.perfect++;
    s.pops.push({ x, y, txt: perfect ? 'PERFECT!' : '+' + pts, life: 0.7, c: perfect ? '#ffe14a' : '#fff' });
    this.burst(x, y, perfect ? '#ffe14a' : '#ff5ad1', 10);
  }

  burst(x: number, y: number, c: string, n: number): void {
    for (let i = 0; i < n; i++) {
      this.s.parts.push({ x, y, vx: (Math.random() - 0.5) * 160, vy: (Math.random() - 0.8) * 140, life: 0.4 + Math.random() * 0.3, c });
    }
  }

  private hurt(): void {
    const { s } = this;
    s.hp--;
    if (s.hp <= 0) return this.die();
    s.inv = 1.2; s.combo = 0; s.shake = 0.25;
    this.audio.sfx('hurt');
    this.burst(s.p.x, s.p.y - 12, '#f44', 12);
  }

  /** Last heart lost (or hit by a tram): she bursts and is gone for DEATH_TIME, then respawn() drops her back in. */
  private die(): void {
    const { s } = this, p = s.p;
    s.hp = 0; s.down = DEATH_TIME; s.combo = 0; s.shake = 0.35; s.continues++;
    s.score = Math.max(0, s.score - 1000);
    this.audio.sfx('die');
    for (const c of ['#fff', '#ff3b6b', '#ffd84a', '#2bf0ff']) this.burst(p.x, p.y - 14, c, 8);
    s.pops.push({ x: p.x, y: p.y - 30, txt: '-1000', life: 0.9, c: '#ff3b6b' });
    p.ride = undefined; p.vy = 0; p.slide = 0; p.atk = 0;
  }

  /** She drops in from above (onto a tram roof if one is passing) and flashes white while invincible. */
  private respawn(): void {
    const { s } = this, p = s.p;
    p.x = Math.max(p.x, PX); p.y = DROP_Y; p.vy = 0; p.jumps = 1;
    s.hp = 3; s.inv = s.respawn = RESPAWN_FLASH;
    this.audio.sfx('respawn');
  }

  /**
   * Trams: land on the roof (and ride it), or get hit by the side and die at once (unless invincible: then she
   * passes through).
   * Runs after gravity moved the player from prevY to p.y.
   */
  private tram(t: number, prevY: number): void {
    const { s } = this, p = s.p;
    let ride: Enemy | undefined;
    for (const e of s.enemies) {
      if (e.type !== 'tram' || e.dead) continue;
      const x = enemyX(e, t), base = GROUND - e.y, roof = base - TRAM_ROOF;
      if (p.x + 4 < x || p.x - 4 > x + TRAM_LEN) continue;
      if (p.vy >= 0 && prevY <= roof + 0.5 && p.y >= roof) ride = e; // feet came down on (or stayed on) the roof
      else if (p.y > roof + 2 && p.y - (p.slide > 0 ? 10 : 24) < base && s.inv <= 0) { this.die(); return; } // hit by the side
    }
    if (ride) { p.y = GROUND - ride.y - TRAM_ROOF; p.vy = 0; p.jumps = 0; }
    p.ride = ride;
  }

  // ---------- update ----------
  update(t: number, dt: number): void {
    const { s } = this, p = s.p;
    s.lastT = t;
    s.bgx += sectionAt(t).speed * dt;
    this.syncToast = Math.max(0, this.syncToast - dt);
    this.musicToast = Math.max(0, this.musicToast - dt);

    // spawn everything that is about to scroll in
    while (s.ei < s.ev.length) {
      const e = s.ev[s.ei];
      if (spawnTime(e) > t) break;
      s.ei++;
      const enemy = createEnemy(e);
      if (enemyX(enemy, t) + TYPES[e.type].w < 0) continue;
      s.enemies.push(enemy);
    }

    // player: gone for a moment after dying, then dropped back in
    if (s.down > 0) {
      s.down -= dt;
      if (s.down <= 0) this.respawn();
    } else {
      // a tram roof carries her back towards the left edge
      if (p.ride) p.x = Math.max(TRAM_EDGE, p.x - p.ride.rel * dt);
      if (this.keys.has('ArrowLeft') || this.keys.has('KeyA')) p.x = Math.max(Math.min(34, p.x), p.x - 130 * dt);
      if (this.keys.has('ArrowRight') || this.keys.has('KeyD')) p.x = Math.min(W - 30, p.x + 130 * dt);
      const prevY = p.y;
      p.vy += 900 * dt; p.y += p.vy * dt;
      if (p.y >= GROUND) { p.y = GROUND; p.vy = 0; p.jumps = 0; }
      this.tram(t, prevY);
    }
    s.fx += (p.x - 22 - s.fx) * Math.min(1, dt * 4);
    // Automat Victoria stands on the platform until the girls reach her, then follows them
    if (t < VICTORIA_WAKE_T + WAKE_HOPS) s.mx = machineCenter(t); // stays put while she wakes up and hops
    else s.mx += (p.x - 46 - s.mx) * Math.min(1, dt * 2.5);
    const dec = (v: number) => Math.max(0, v - dt);
    p.slide = dec(p.slide); p.atk = dec(p.atk); p.cd = dec(p.cd); p.star = dec(p.star);
    s.inv = dec(s.inv); s.shake = dec(s.shake); s.respawn = dec(s.respawn);

    // friend follows with a delay and helps from chorus 1
    const f = s.friend;
    f.yHist.push(s.down > 0 ? GROUND : p.y); if (f.yHist.length > 9) f.yHist.shift();
    f.cd -= dt; f.atk = dec(f.atk);

    for (const st of s.stars) { st.x += st.vx * dt; st.y += st.vy * dt; st.a += dt * 20; }
    s.stars = s.stars.filter((st) => st.x < W + 10 && st.y > 0 && st.y < H && !st.gone);

    // enemies
    const ph = p.slide > 0 ? 10 : 24;
    for (const e of s.enemies) {
      if (e.dead) continue;
      const ty = TYPES[e.type], x = enemyX(e, t), ey = GROUND - e.y;
      if (x < (e.type === 'tram' ? -TRAM_LEN - 20 : -120)) { e.dead = true; e.gone = true; continue; }
      if (e.type === 'tram') continue; // handled in tram()
      for (const st of s.stars) {
        if (!ty.pickup && !ty.solid && !st.gone && Math.abs(st.x - x) < ty.w / 2 + 4 && st.y > ey - ty.h - 3 && st.y < ey + 3) {
          st.gone = true; this.hitEnemy(e, x, ey, 1);
        }
      }
      if (e.dead) continue;
      if (t > barT(34) && f.cd <= 0 && !ty.pickup && !ty.solid && x > s.fx - 8 && x < s.fx + 16 && e.y === 0) {
        f.cd = 1.1; f.atk = 0.18; e.dead = true; this.award(x, ey - 8, 75);
      }
      if (e.dead) continue;
      const overlapX = Math.abs(x - p.x) < ty.w / 2 + 4, overlapY = ey > p.y - ph && ey - ty.h < p.y;
      if (overlapX && overlapY && s.down <= 0) {
        if (ty.pickup) {
          e.dead = true; this.audio.sfx('coin');
          if (e.type === 'terminal') { s.power = t + 8 * BAR; s.pops.push({ x, y: ey - 20, txt: 'PIP! ★★★', life: 1.2, c: '#7cf' }); }
          else { s.tickets++; s.ammo++; s.score += 50; s.pops.push({ x, y: ey - 8, txt: '+1', life: 0.5, c: '#ffd84a' }); }
        } else if (s.inv <= 0) this.hurt();
      }
    }
    s.enemies = s.enemies.filter((e) => !e.gone && !(e.dead && enemyX(e, t) < (e.type === 'tram' ? -TRAM_LEN - 20 : -120)));
    if (p.ride?.dead) p.ride = undefined;

    // boss
    if (bossVisible(t)) {
      const bx = bossX(t);
      for (const st of s.stars) {
        if (!st.gone && st.x > bx - 42 && st.y > GROUND - 124) { // the robot's body
          st.gone = true; s.boss.hp = Math.max(0, s.boss.hp - 1); s.boss.hit = 0.1; s.score += 30; this.burst(st.x, st.y, '#ff0', 5);
        }
      }
      s.boss.hit = dec(s.boss.hit);
    }
    if (t >= FINAL_HIT && !s.final) {
      s.final = true; s.shake = 0.6; s.score += 2000 + (s.boss.hp === 0 ? 3000 : 0);
      for (let i = 0; i < 6; i++) this.burst(bossX(t) + (Math.random() - 0.5) * 60, GROUND - 40 + (Math.random() - 0.5) * 50, ['#ff0', '#f5d', '#6ff', '#fff'][i % 4], 24);
      s.enemies.forEach((e) => (e.dead = true));
    }
    if (t >= WIN_AT && !s.won) {
      s.won = true; this.mode = 'win';
      try { s.best = Math.max(Number(localStorage.getItem(BEST_KEY)) || 0, s.score); localStorage.setItem(BEST_KEY, String(s.best)); }
      catch { s.best = s.score; }
    }

    for (const q of s.parts) { q.x += q.vx * dt; q.y += q.vy * dt; q.vy += 300 * dt; q.life -= dt; }
    s.parts = s.parts.filter((q) => q.life > 0);
    for (const q of s.pops) { q.y -= 20 * dt; q.life -= dt; }
    s.pops = s.pops.filter((q) => q.life > 0);
  }
}

/** A hit within 90 ms of a beat is PERFECT. */
function nearBeat(t: number): boolean {
  const ph = ((((t - PH) / BEAT) % 1) + 1) % 1;
  return Math.min(ph, 1 - ph) * BEAT < 0.09;
}

/** Background scroll distance at time t (integrates the section speeds). */
function scrollAt(t: number): number {
  let x = 0;
  for (let u = 0; u < t; u += 0.05) x += sectionAt(u).speed * Math.min(0.05, t - u);
  return x;
}
