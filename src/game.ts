// Game rules: spawning, physics, combat, scoring and keyboard controls.
import { AudioEngine } from './audio';
import { BAR, BEAT, FINAL_HIT, GROUND, H, PH, PLAYER_MAX_HP, PX, W, WIN_AT, barT } from './config';
import { BLOB_POP, LAMPS, POWERUPS, PROPS, isLamp, isPowerup, isProp, isTree, TRAM_EDGE, TRAM_LEN, TRAM_ROOF, TYPES, type PowerupKind } from './schedule';
import { loadDefaultLevel } from './level';
import { boardImpactAt, boardTop, createEnemy, createState, enemyBodyHeight, enemyHeight, enemyX, hopPose, spawnTime, type Enemy, type GameState } from './state';
import { isFighter, isNinjaKind, ninjaJump } from './ninjas';
import { isPassenger } from './passengers';
import { machinePosition, seekRainbow, updateRainbow } from './rainbow';
import { VALKYRIEN_FLOOR, belowSurface, playerFloor, resolveValkyrien, routeControlsPlayer } from './valkyrien';
import { MACHINE_HEIGHT, MACHINE_WIDTH, RAINBOW_T0, RAINBOW_T1, STATION_VX, VICTORIA_WAKE_T, WAKE_HOPS, bossVisible, bossX, isNinja, machineCenter, platformMachines, sectionAt, subwayTaggerX } from './timeline';

/** seconds she is gone after losing her last heart */
const DEATH_TIME = 0.85;
/** seconds of white flashing (and invincibility) after she drops back in */
const RESPAWN_FLASH = 1.2;
/** she drops back in from this height (screen y of her feet) */
const DROP_Y = GROUND - 100;

export type Mode = 'loading' | 'title' | 'play' | 'pause' | 'celebrate' | 'win' | 'editor' | 'highscore';
const BEST_KEY = 'oslostil-best';

export class Game {
  level = loadDefaultLevel();
  s: GameState = createState(this.level);
  mode: Mode = 'loading';
  cleanPause = false;
  private winReturnAt = 0;
  readonly keys = new Set<string>();
  /** seconds left of the on-screen sync readout */
  syncToast = 0;
  /** seconds left of the on-screen music on/off readout */
  musicToast = 0;
  /** called by the development time-mark shortcut */
  onMark: (t: number) => void = () => {};

  constructor(readonly audio: AudioEngine) {}

  start(): void { this.seek(0); }

  intro(): void {
    this.audio.pause();
    this.keys.clear();
    this.cleanPause = false;
    this.winReturnAt = 0;
    this.mode = 'title';
  }

  private showWin(now: number): void {
    this.mode = 'win';
    this.winReturnAt = now + 7000;
  }

  tickWin(now: number, dt = 0): void {
    if (this.mode === 'celebrate' && this.s.celebration) {
      const c = this.s.celebration;
      c.elapsed += dt;
      this.s.shake = Math.max(0, this.s.shake - dt);
      this.updateParticles(dt);
      const braking = Math.min(1, c.elapsed / 0.25);
      this.s.bgx = c.bgx + sectionAt(FINAL_HIT).speed * 0.25 / 3 * (1 - (1 - braking) ** 3);
      if (c.elapsed >= 7) {
        this.showWin(now);
      }
      return;
    }
    if (this.mode !== 'win' || now < this.winReturnAt) return;
    this.audio.pause();
    this.keys.clear();
    this.mode = 'highscore';
  }

  /** Jump the song and the game to time t (also used by the debug panel). */
  seek(t: number): void {
    t = Math.max(0, Math.min(WIN_AT - 0.5, t));
    this.s = createState(this.level);
    this.s.lastT = t;
    this.s.bgx = scrollAt(t);
    seekRainbow(this.s, t);
    this.audio.play(t);
    this.mode = 'play';
    this.cleanPause = false;
  }

  edit(t = this.s.lastT): void {
    this.audio.pause();
    this.keys.clear();
    this.s = createState(this.level);
    this.s.lastT = Math.max(0, Math.min(WIN_AT - 0.5, t));
    this.s.bgx = scrollAt(this.s.lastT);
    this.mode = 'editor';
  }

  pause(clean = false): void {
    if (this.mode !== 'play' && this.mode !== 'pause') return;
    if (this.mode === 'pause' && !clean) return;
    this.cleanPause = __DEV_MODE_DEFAULT__ && clean;
    if (this.mode === 'play') { this.mode = 'pause'; this.audio.pause(); }
  }
  resume(): void {
    if (this.mode === 'pause') { this.mode = 'play'; this.cleanPause = false; this.audio.resume(); }
  }

  // ---------- input ----------
  keyDown(e: KeyboardEvent): void {
    if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) e.preventDefault();
    if (e.repeat) return;
    if (this.keys.has(e.code)) return;
    this.keys.add(e.code);
    const c = e.code;
    if (this.mode === 'title' && (c === 'Enter' || c === 'Space')) return this.start();
    if (this.mode === 'celebrate' && c === 'Enter') return this.showWin(performance.now());
    if (this.mode === 'win' && c === 'Enter') {
      this.audio.pause();
      this.keys.clear();
      this.mode = 'highscore';
      return;
    }
    if (c === 'KeyM') { this.audio.toggleMusic(); this.musicToast = 1.5; }
    if (this.mode === 'play' && (c === 'KeyP' || c === 'Escape')) return this.pause();
    if (this.mode === 'pause' && (c === 'KeyP' || c === 'Escape' || c === 'Enter')) return this.resume();
    if (this.mode !== 'play' || this.s.down > 0) return; // no control while dead
    if (routeControlsPlayer(this.s)) return;
    const p = this.s.p;
    if (c === 'Space' || c === 'ArrowUp' || c === 'KeyW') {
      if (p.jumps < 2) { p.vy = p.jumps ? -250 : -300; p.jumps++; p.slide = 0; this.audio.sfx('jump'); }
    }
    if (c === 'ArrowDown' || c === 'KeyS') {
      if (p.y >= playerFloor(this.s) || p.ride || p.propRide || p.machineRide !== undefined) {
        p.slide = 0.45;
        p.slideDirection = this.keys.has('ArrowLeft') || this.keys.has('KeyA') ? -1 : 1;
      } else p.vy = 340;
    }
    if ((c === 'KeyX' || c === 'KeyJ') && p.cd <= 0) { p.atk = 0.18; p.cd = 0.22; this.audio.sfx('slash'); this.attack(); }
    if ((c === 'KeyC' || c === 'KeyK') && p.star <= 0) this.throwStar();
  }

  keyUp(e: KeyboardEvent): void { this.keys.delete(e.code); }

  // ---------- combat ----------
  private attack(): void {
    const { s } = this, p = s.p, reach = isNinja(s.lastT) ? 30 : 20;
    for (const e of s.enemies) {
      const ty = TYPES[e.type];
      if (e.dead || ty.pickup || ty.solid || (e.y < 0) !== belowSurface(s)) continue;
      const ex = enemyX(e, s.lastT), ey = GROUND - enemyHeight(e, s.lastT);
      if (ex > p.x - 4 && ex < p.x + reach + 8 && Math.abs(ey - enemyBodyHeight(e, s.lastT) / 2 - (p.y - 12)) < 26) this.hitEnemy(e, ex, ey, 2);
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
    if (e.hp <= 0) { this.killEnemy(e, x, y); this.award(x, y - 8, e.type === 'bot' || isPassenger(e.type) ? 200 : isNinjaKind(e.type) ? 150 : isFighter(e.type) ? 120 : 100); }
    else this.burst(x, y - 8, '#fff', 4);
  }

  private killEnemy(e: Enemy, x: number, y: number): void {
    e.dead = true;
    if (e.type === 'blob_hop') this.s.blobPops.push({ x, y, age: 0 });
  }

  private collectHealth(kind: PowerupKind, x: number, y: number): void {
    const s = this.s, previousHp = s.hp;
    if (previousHp >= PLAYER_MAX_HP) s.score += 200;
    else s.hp = kind === 'neon_heart' && nearBeat(s.lastT) ? PLAYER_MAX_HP
      : Math.min(PLAYER_MAX_HP, previousHp + POWERUPS[kind].hearts);
    s.healFlash = 0.15;
    s.pops.push({ x, y: y - 8, txt: previousHp >= PLAYER_MAX_HP ? '+200' : `+${Number((s.hp - previousHp).toFixed(2))} ♥`, life: 0.8, c: '#fff' });
  }

  private award(x: number, y: number, base: number, bounceMultiplier = 1): void {
    const { s } = this, perfect = nearBeat(s.lastT);
    s.combo++;
    const pts = base * bounceMultiplier * (1 + Math.min(4, Math.floor(s.combo / 8))) * (perfect ? 2 : 1);
    s.score += pts; s.kills++;
    if (perfect) s.perfect++;
    s.pops.push({ x, y, txt: bounceMultiplier > 1 ? `BOUNCE x${bounceMultiplier} +${pts}` : perfect ? 'PERFECT!' : '+' + pts, life: 0.7, c: perfect ? '#ffe14a' : '#fff' });
    this.burst(x, y, perfect ? '#ffe14a' : '#ff5ad1', 10);
  }

  burst(x: number, y: number, c: string, n: number): void {
    for (let i = 0; i < n; i++) {
      this.s.parts.push({ x, y, vx: (Math.random() - 0.5) * 160, vy: (Math.random() - 0.8) * 140, life: 0.4 + Math.random() * 0.3, c });
    }
  }

  private hurt(damage = 1): void {
    const { s } = this;
    s.bounceChain = 0;
    s.hp = Math.max(0, s.hp - damage);
    if (s.hp <= 0) return this.die();
    s.inv = 1.2; s.combo = 0; s.shake = 0.25;
    this.audio.sfx('hurt');
    this.burst(s.p.x, s.p.y - 12, '#f44', 12);
  }

  /** Tram hits fling her offscreen before the ordinary respawn delay. */
  private die(tramHit = false): void {
    const { s } = this, p = s.p;
    s.bounceChain = 0;
    s.hp = 0; s.down = DEATH_TIME; s.combo = 0; s.shake = 0.35; s.continues++;
    s.score = Math.max(0, s.score - 1000);
    this.audio.sfx('die');
    if (tramHit) s.deathFlight = { x: p.x, y: p.y, vx: -520, vy: -240, angle: 0 };
    for (const c of ['#fff', '#ff3b6b', '#ffd84a', '#2bf0ff']) this.burst(p.x, p.y - 14, c, 8);
    s.pops.push({ x: p.x, y: p.y - 30, txt: '-1000', life: 0.9, c: '#ff3b6b' });
    p.ride = undefined; p.propRide = undefined; p.machineRide = undefined; p.vy = 0; p.slide = 0; p.atk = 0;
  }

  /** She drops in from above (onto a tram roof if one is passing) and flashes white while invincible. */
  private respawn(): void {
    const { s } = this, p = s.p;
    p.x = Math.max(p.x, PX); p.y = playerFloor(s) - 100; p.vy = 0; p.jumps = 1;
    if (s.deathFlight) {
      if (s.deathFlight.friend) {
        s.fx = p.x - 22; s.friend.yHist = [DROP_Y]; s.friend.atk = 0;
      }
      if (s.deathFlight.machine) s.mx = p.x - 46;
      s.deathFlight = undefined;
    }
    s.hp = PLAYER_MAX_HP; s.inv = s.respawn = RESPAWN_FLASH;
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
      if (e.type !== 'tram' || e.dead || (e.y < 0) !== belowSurface(s)) continue;
      const x = enemyX(e, t), base = GROUND - e.y, roof = base - TRAM_ROOF;
      if (p.x + 4 < x || p.x - 4 > x + TRAM_LEN) continue;
      if (p.vy >= 0 && prevY <= roof + 0.5 && p.y >= roof) ride = e; // feet came down on (or stayed on) the roof
      else if (p.y > roof + 2 && p.y - (p.slide > 0 ? 10 : 24) < base && s.inv <= 0) { this.die(true); return; } // hit by the side
    }
    if (ride) { p.y = GROUND - ride.y - TRAM_ROOF; p.vy = 0; p.jumps = 0; s.bounceChain = 0; }
    p.ride = ride;
  }

  private machines(t: number, prevY: number): void {
    const { s } = this, p = s.p, roof = GROUND - MACHINE_HEIGHT;
    p.machineRide = undefined;
    if (s.down > 0 || p.ride || p.propRide || p.vy < 0 || prevY > roof + 0.5 || p.y < roof) return;
    for (const k of platformMachines(t)) {
      if (Math.abs(p.x - machineCenter(t, k)) >= MACHINE_WIDTH / 2 + 4) continue;
      p.y = roof; p.vy = 0; p.jumps = 0; p.machineRide = k; s.bounceChain = 0;
      break;
    }
  }

  private props(t: number, prevT: number, prevY: number): void {
    const { s } = this, p = s.p;
    const previousRide = p.propRide;
    p.propRide = undefined;
    if (s.down > 0 || p.ride || p.vy < 0) return;
    let highest = Infinity;
    for (const e of s.enemies) {
      if (e.dead || (e.y < 0) !== belowSurface(s) || (!isProp(e.type) && !isLamp(e.type) && e.type !== 'board_broken')) continue;
      const height = e.type === 'board_broken' ? boardTop(e, t) : isLamp(e.type) ? LAMPS[e.type].top : PROPS[e.type].top;
      if (!height) continue; // lantern strings, neon signs: nothing to stand on
      const top = GROUND - e.y - height, x = enemyX(e, t);
      const previousTop = e.type === 'board_broken' ? GROUND - e.y - boardTop(e, prevT) : top;
      const riding = e === previousRide && Math.abs(prevY - previousTop) < 0.5;
      const [left, right] = isLamp(e.type) ? LAMPS[e.type].top_span : [-TYPES[e.type].w / 2, TYPES[e.type].w / 2];
      if (p.x + 4 <= x + left || p.x - 4 >= x + right
        || (!riding && (prevY > previousTop + 0.5 || p.y < top)) || top >= highest) continue;
      highest = top; p.propRide = e;
    }
    if (p.propRide) {
      if (p.propRide.type === 'board_broken') p.propRide.crumbledAt ??= t;
      p.y = highest; p.vy = 0; p.jumps = 0; p.machineRide = undefined; s.bounceChain = 0;
    }
  }

  private boardImpacts(t: number, prevT: number): void {
    const { s } = this, p = s.p;
    for (const e of s.enemies) {
      if (e.dead || (e.y < 0) !== belowSurface(s) || e.type !== 'board_broken' || prevT >= boardImpactAt(e) || t < boardImpactAt(e)) continue;
      const x = enemyX(e, t), half = TYPES[e.type].w / 2, bottom = GROUND - e.y;
      if (x + half < 0 || x - half > W) continue;
      s.boardShake = 0.1;
      if (s.down > 0) continue;
      if (p.propRide === e) {
        p.vy = -120; p.jumps = 1; p.slide = 0; p.propRide = undefined;
        this.audio.sfx('jump');
      } else if (Math.abs(p.x - x) < half + 4 && p.y > bottom - boardTop(e, t)
        && p.y - (p.slide > 0 ? 10 : 24) < bottom) {
        const left = x - half - 4, right = x + half + 4;
        p.x = left < TRAM_EDGE ? right : right > W - 30 ? left : p.x < x ? left : right;
      }
    }
  }

  // ---------- update ----------
  update(t: number, dt: number): void {
    const { s } = this, p = s.p;
    const prevT = s.lastT, prevX = p.x, prevY = p.y;
    s.lastT = t;
    s.bgx += sectionAt(t).speed * dt;
    s.boardShake = Math.max(0, s.boardShake - dt);
    for (const pop of s.blobPops) { pop.x -= sectionAt(t).speed * dt; pop.age += dt; }
    s.blobPops = s.blobPops.filter(pop => pop.age < BLOB_POP.frames / BLOB_POP.fps);
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
      if (s.deathFlight) {
        const flight = s.deathFlight;
        for (const member of [flight, flight.friend, flight.machine]) {
          if (!member) continue;
          member.x += member.vx * dt;
          member.vy += 500 * dt;
          member.y += member.vy * dt;
          member.angle -= dt * 12;
        }
      }
      const flight = s.deathFlight;
      if (!flight || [flight, flight.friend, flight.machine].every(member => !member || member.x < -32)) {
        s.down -= dt;
        if (s.down <= 0) this.respawn();
      }
    } else {
      // a tram roof carries her back towards the left edge
      if (p.ride) p.x = Math.max(TRAM_EDGE, p.x - p.ride.rel * dt);
      if (p.propRide && p.vy >= 0) p.x = Math.max(TRAM_EDGE, p.x - p.propRide.rel * dt);
      if (p.machineRide !== undefined && p.vy >= 0 && platformMachines(t).includes(p.machineRide)) {
        p.x = Math.max(TRAM_EDGE, p.x - STATION_VX * dt);
      }
      if (!routeControlsPlayer(s) && (this.keys.has('ArrowLeft') || this.keys.has('KeyA'))) {
        const backwardSpeed = sectionAt(t).speed + 80;
        p.x = Math.max(TRAM_EDGE, p.x - backwardSpeed * dt);
      }
      if (!routeControlsPlayer(s) && (this.keys.has('ArrowRight') || this.keys.has('KeyD'))) p.x = Math.min(W - 30, p.x + 130 * dt);
      if (p.slide > 0 && p.x !== prevX) p.slideDirection = p.x < prevX ? -1 : 1;
      p.vy += 900 * dt; p.y += p.vy * dt;
      if (!routeControlsPlayer(s)) {
        this.tram(t, prevY);
        this.props(t, prevT, prevY);
        this.machines(t, prevY);
      }
    }
    this.boardImpacts(t, prevT);
    if (s.deathFlight) {
      const companions = [
        { key: 'friend' as const, x: s.fx, y: s.friend.yHist[0] ?? GROUND, active: true },
        { key: 'machine' as const, ...machinePosition(s, t), active: t >= VICTORIA_WAKE_T && !(t >= RAINBOW_T0 && t < RAINBOW_T1 + 1) },
      ];
      for (const companion of companions) {
        if (!companion.active || s.deathFlight[companion.key]) continue;
        if (s.enemies.some(e => {
          if (e.type !== 'tram' || e.dead) return false;
          const nose = enemyX(e, t), previousNose = enemyX(e, prevT), base = GROUND - e.y;
          return nose <= companion.x + 4 && previousNose >= companion.x - 4
            && companion.y > base - TRAM_ROOF + 2 && companion.y - 24 < base;
        })) s.deathFlight[companion.key] = { x: companion.x, y: companion.y, vx: -520, vy: -240, angle: 0 };
      }
    }
    s.fx += (p.x - 22 - s.fx) * Math.min(1, dt * 4);
    // Automat Victoria stands on the platform until the girls reach her, then follows them
    if (t < VICTORIA_WAKE_T + WAKE_HOPS) s.mx = machineCenter(t); // stays put while she wakes up and hops
    else s.mx += (p.x - 46 - s.mx) * Math.min(1, dt * 2.5);
    updateRainbow(s, t, dt);
    const dec = (v: number) => Math.max(0, v - dt);
    p.slide = dec(p.slide); p.atk = dec(p.atk); p.cd = dec(p.cd); p.star = dec(p.star);
    s.inv = dec(s.inv); s.shake = dec(s.shake); s.respawn = dec(s.respawn);
    s.healFlash = dec(s.healFlash);

    // friend follows with a delay and helps from chorus 1
    const f = s.friend;
    if (!s.deathFlight) {
      f.yHist.push(s.down > 0 ? GROUND : p.y); if (f.yHist.length > 9) f.yHist.shift();
    }
    f.cd -= dt; f.atk = dec(f.atk);

    for (const st of s.stars) { st.x += st.vx * dt; st.y += st.vy * dt; st.a += dt * 20; }
    s.stars = s.stars.filter((st) => st.x < W + 10 && st.y > 0 && st.y < H + s.valkyrien.camera && !st.gone);
    const taggerX = subwayTaggerX(t), previousTaggerX = subwayTaggerX(prevT) ?? taggerX;
    if (!belowSurface(s) && s.taggerStoppedAt === undefined && taggerX !== null && previousTaggerX !== null) {
      for (const star of s.stars) {
        const previousX = star.x - star.vx * dt, previousY = star.y - star.vy * dt;
        const relative = star.x - taggerX, previousRelative = previousX - previousTaggerX;
        if (star.gone || Math.min(relative, previousRelative) > 13 || Math.max(relative, previousRelative) < -13
          || Math.max(star.y, previousY) < GROUND - 30 || Math.min(star.y, previousY) > GROUND) continue;
        star.gone = true;
        s.taggerStoppedAt = t;
        this.audio.sfx('hit');
        this.award(taggerX, GROUND - 30, 300);
        break;
      }
    }

    for (const q of s.knocked) {
      if (q.squash !== undefined) {
        q.squash -= dt;
        q.x += q.vx * dt;
        continue;
      }
      q.vy += 900 * dt;
      q.x += q.vx * dt;
      q.y += q.vy * dt;
      const floor = q.enemy.y < 0 ? VALKYRIEN_FLOOR : GROUND;
      if (q.splash && q.y >= floor) {
        q.y = floor;
        this.audio.sfx('hit');
        for (let i = 0; i < 14; i++) s.parts.push({
          x: q.x, y: floor - 1, vx: (Math.random() - 0.5) * 180,
          vy: -20 - Math.random() * 70, life: 0.3 + Math.random() * 0.25,
          c: q.enemy.type === 'pigeon' ? '#a9b8ce' : q.enemy.type === 'gull' ? '#f4f8ff' : '#2bf0ff',
        });
      }
    }
    s.knocked = s.knocked.filter((q) => (q.squash !== undefined ? q.squash > 0 : q.y < (q.enemy.y < 0 ? VALKYRIEN_FLOOR : GROUND)) && q.x > -40 && q.x < W + 40);

    // Droppings remain hazardous after their gull has left or been defeated.
    const ph = p.slide > 0 ? 10 : 24;
    for (const drop of s.droppings) {
      const previousY = drop.y;
      const floor = drop.floor ?? GROUND;
      drop.x -= sectionAt(t).speed * dt;
      if (!drop.landed) {
        drop.vy += 500 * dt;
        drop.y += drop.vy * dt;
        if (drop.y >= floor) { drop.y = floor; drop.landed = true; }
      } else drop.life -= dt;
      if ((floor > GROUND) === belowSurface(s) && drop.life > 0 && s.down <= 0 && s.inv <= 0
        && Math.abs(drop.x - p.x) < (drop.landed ? 9 : 6)
        && Math.max(previousY, drop.y) + 2 >= Math.min(prevY, p.y) - ph
        && Math.min(previousY, drop.y) - 2 <= Math.max(prevY, p.y)) this.hurt(0.25);
    }
    s.droppings = s.droppings.filter(drop => drop.life > 0 && drop.x > -12);

    // enemies
    for (const e of s.enemies) {
      if (e.dead) continue;
      if (isFighter(e.type)) { e.y0 ??= e.y; e.y = e.y0 + ninjaJump(e.type, t - e.arr).lift; }
      const ty = TYPES[e.type], x = enemyX(e, t), ey = GROUND - enemyHeight(e, t);
      if (e.type === 'gull' && x >= 0 && x <= W) {
        e.dropIn = (e.dropIn ?? (0.2 + Math.random() * 0.4)) - dt;
        if (e.dropIn <= 0) {
          s.droppings.push({ x, y: ey, vy: 30, life: 6, landed: false, floor: e.y < 0 ? VALKYRIEN_FLOOR : GROUND });
          e.dropIn = 0.45 + Math.random() * 0.55;
        }
      }
      if (x < (e.type === 'tram' ? -TRAM_LEN - 20 : -120)) { e.dead = true; e.gone = true; continue; }
      if ((e.y < 0) !== belowSurface(s)) continue;
      if (e.type === 'tram' || e.type === 'board_broken' || isProp(e.type) || isLamp(e.type) || isTree(e.type)) continue; // scenery has no side damage
      const h = enemyBodyHeight(e, t), top = ey - h;
      const previousTop = GROUND - enemyHeight(e, prevT) - enemyBodyHeight(e, prevT);
      if ((e.type === 'pigeon' || e.type === 'drone' || e.type === 'gull' || e.type === 'suitcase' || e.type === 'blob_hop') && s.down <= 0 && p.vy > 0 && prevY <= previousTop && p.y >= top) {
        const crossing = (previousTop - prevY) / ((p.y - prevY) - (top - previousTop));
        const playerX = prevX + (p.x - prevX) * crossing;
        const ex = enemyX(e, prevT) + (x - enemyX(e, prevT)) * crossing;
        if (Math.abs(ex - playerX) < ty.w / 2 + 4) {
          this.killEnemy(e, x, ey);
          if (e.type === 'suitcase') {
            s.knocked.push({ enemy: e, x, y: ey, vx: -e.rel, vy: 0, splash: false, squash: 0.6 });
          } else if (e.type !== 'blob_hop') {
            s.knocked.push({ enemy: e, x, y: ey, vx: -e.rel, vy: 90, splash: true });
          }
          p.y = top; p.vy = -300; p.jumps = 1; p.slide = 0; p.ride = undefined; p.propRide = undefined; p.machineRide = undefined;
          this.audio.sfx('jump');
          this.award(x, top, 100, ++s.bounceChain);
          continue;
        }
      }
      if (e.type === 'suitcase' && p.slide > 0 && s.down <= 0
        && Math.abs(x - p.x) < ty.w / 2 + 4 && ey > p.y - 10 && top < p.y) {
        e.dead = true;
        s.knocked.push({ enemy: e, x, y: ey, vx: p.slideDirection * 260, vy: -240, splash: false });
        this.audio.sfx('hit');
        this.award(x, top, 100);
        continue;
      }
      for (const st of s.stars) {
        if (!e.dead && !ty.pickup && !ty.solid && !st.gone && Math.abs(st.x - x) < ty.w / 2 + 4 && st.y > ey - h - 3 && st.y < ey + 3) {
          st.gone = true; this.hitEnemy(e, x, ey, 1);
        }
      }
      if (e.dead) continue;
      if (!s.deathFlight?.friend && t > barT(34) && f.cd <= 0 && !ty.pickup && !ty.solid && x > s.fx - 8 && x < s.fx + 16 && e.y === 0) {
        f.cd = 1.1; f.atk = 0.18; this.killEnemy(e, x, ey); this.award(x, ey - 8, 75);
      }
      if (e.dead) continue;
      const overlapX = Math.abs(x - p.x) < ty.w / 2 + 4, overlapY = ey > p.y - ph && ey - h < p.y;
      if (overlapX && overlapY && s.down <= 0) {
        if (ty.pickup) {
          e.dead = true; this.audio.sfx('coin');
          if (isPowerup(e.type)) this.collectHealth(e.type, x, ey);
          else if (e.type === 'terminal') { s.power = t + 8 * BAR; s.pops.push({ x, y: ey - 20, txt: 'PIP! ★★★', life: 1.2, c: '#7cf' }); }
          else { s.tickets++; s.ammo++; s.score += 50; s.pops.push({ x, y: ey - 8, txt: '+1', life: 0.5, c: '#ffd84a' }); }
        } else if (s.inv <= 0 && !(e.type === 'blob_hop' && hopPose(e, t).frame < 2)) this.hurt();
      }
    }
    // Resolve stomp crossings before landing, including fast falls that cross an enemy and the ground in one frame.
    resolveValkyrien(s, t, dt, prevY);
    s.enemies = s.enemies.filter((e) => !e.gone && !(e.dead && enemyX(e, t) < (e.type === 'tram' ? -TRAM_LEN - 20 : -120)));
    if (p.ride?.dead) p.ride = undefined;

    // boss
    if (bossVisible(t)) {
      const bx = bossX(t);
      for (const st of s.stars) {
        if (!st.gone && st.x > bx - 42 && st.x < bx + 42 && st.y > GROUND - 124 && st.y < GROUND) { // the robot's body
          st.gone = true; s.boss.hp = Math.max(0, s.boss.hp - 2); s.boss.hit = 0.1; s.score += 30; this.burst(st.x, st.y, '#ff0', 5);
        }
      }
      s.boss.hit = dec(s.boss.hit);
    }
    if (t >= FINAL_HIT && !s.final) {
      s.final = true; s.shake = 0.6; s.score += 2000 + (s.boss.hp === 0 ? 3000 : 0);
      for (let i = 0; i < 6; i++) this.burst(bossX(t) + (Math.random() - 0.5) * 60, GROUND - 40 + (Math.random() - 0.5) * 50, ['#ff0', '#f5d', '#6ff', '#fff'][i % 4], 24);
      s.enemies.forEach((e) => (e.dead = true));
    }
    if (t >= FINAL_HIT && !s.won) {
      s.won = true; this.mode = 'celebrate';
      this.keys.clear();
      s.celebration = {
        elapsed: 0, bgx: s.bgx,
        victoria: { x: p.x, y: p.y },
        friend: { x: s.fx, y: s.friend.yHist[0] ?? GROUND },
        machine: machinePosition(s, t),
      };
      try { s.best = Math.max(Number(localStorage.getItem(BEST_KEY)) || 0, s.score); localStorage.setItem(BEST_KEY, String(s.best)); }
      catch { s.best = s.score; }
    }

    this.updateParticles(dt);
    for (const q of s.pops) { q.y -= 20 * dt; q.life -= dt; }
    s.pops = s.pops.filter((q) => q.life > 0);
  }

  private updateParticles(dt: number): void {
    for (const q of this.s.parts) { q.x += q.vx * dt; q.y += q.vy * dt; q.vy += 300 * dt; q.life -= dt; }
    this.s.parts = this.s.parts.filter((q) => q.life > 0);
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
