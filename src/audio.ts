// Web Audio: the song is the master clock, plus a few synthesized sound effects.
export type Sfx = 'jump' | 'hit' | 'slash' | 'coin' | 'hurt' | 'star' | 'die' | 'respawn';
type Sweep = [number, number, number, OscillatorType];

const SFX: Record<Exclude<Sfx, 'die' | 'respawn'>, Sweep> = {
  jump: [520, 880, 0.08, 'square'],
  hit: [220, 70, 0.1, 'sawtooth'],
  slash: [900, 300, 0.06, 'triangle'],
  coin: [990, 1480, 0.09, 'square'],
  hurt: [160, 60, 0.25, 'sawtooth'],
  star: [1400, 900, 0.05, 'square'],
};
/** Short arcade jingles: [note frequencies, seconds per note, waveform]. */
const JINGLES: Record<'die' | 'respawn', [number[], number, OscillatorType]> = {
  // falling «game over» arpeggio that bends down at the end
  die: [[988, 784, 622, 523, 392, 311, 233, 165], 0.075, 'square'],
  // rising sparkle as she drops back in
  respawn: [[523, 659, 784, 1047, 1319, 1568], 0.05, 'triangle'],
};
const SYNC_KEY = 'oslostil-sync';

export class AudioEngine {
  private ctx: AudioContext | null = null;
  /** everything goes through this */
  private gain: GainNode | null = null;
  /** the soundtrack only, so it can be muted while the effects keep playing */
  private music: GainNode | null = null;
  private song: AudioBuffer | null = null;
  private src: AudioBufferSourceNode | null = null;
  /** context time at which song time 0 plays */
  private t0 = 0;
  /** fallback clock (performance.now based) when there's no song */
  private clock0: number | null = null;
  private pausedAt: number | null = null;
  /** soundtrack muted (effects still play); starts muted */
  musicMuted = true;
  /** user-adjustable audio/visual offset, seconds */
  syncOffset = 0;

  constructor() {
    try { this.syncOffset = Number(localStorage.getItem(SYNC_KEY)) || 0; } catch { /* storage blocked */ }
  }

  private ensure(): AudioContext {
    if (!this.ctx) {
      this.ctx = new AudioContext();
      this.gain = this.ctx.createGain();
      this.gain.connect(this.ctx.destination);
      this.music = this.ctx.createGain();
      this.music.gain.value = this.musicMuted ? 0 : 1;
      this.music.connect(this.gain);
    }
    return this.ctx;
  }

  async load(url: string): Promise<void> {
    const ctx = this.ensure();
    const buf = await (await fetch(url)).arrayBuffer();
    this.song = await ctx.decodeAudioData(buf);
  }

  /** Start the song at `from` seconds. Falls back to a silent clock if the song didn't load. */
  play(from = 0): void {
    const ctx = this.ensure();
    if (ctx.state === 'suspended') void ctx.resume();
    this.stopSource();
    this.pausedAt = null;
    if (this.song && this.music) {
      this.clock0 = null;
      const src = ctx.createBufferSource();
      src.buffer = this.song;
      src.connect(this.music);
      const when = ctx.currentTime + 0.05;
      src.start(when, from);
      this.src = src;
      this.t0 = when - from;
    } else {
      this.clock0 = performance.now() / 1000 - from;
    }
  }

  private stopSource(): void {
    if (this.src) { try { this.src.stop(); } catch { /* already stopped */ } this.src = null; }
  }

  /** Current song time in seconds, as heard. */
  time(): number {
    if (this.pausedAt !== null) return this.pausedAt;
    if (this.clock0 !== null) return performance.now() / 1000 - this.clock0;
    if (!this.ctx || !this.src) return 0;
    return this.ctx.currentTime - this.t0 - (this.ctx.outputLatency || 0) + this.syncOffset;
  }

  pause(): void {
    this.pausedAt = this.time();
    if (this.ctx) void this.ctx.suspend();
  }

  resume(): void {
    if (this.pausedAt !== null && this.clock0 !== null) this.clock0 = performance.now() / 1000 - this.pausedAt;
    this.pausedAt = null;
    if (this.ctx) void this.ctx.resume();
  }

  /** Soundtrack on/off. The song keeps running silently (it is still the clock); effects are not affected. */
  toggleMusic(): void {
    this.musicMuted = !this.musicMuted;
    if (this.music) this.music.gain.value = this.musicMuted ? 0 : 1;
  }

  nudgeSync(delta: number): void {
    this.syncOffset = Math.round((this.syncOffset + delta) * 100) / 100;
    try { localStorage.setItem(SYNC_KEY, String(this.syncOffset)); } catch { /* storage blocked */ }
  }

  sfx(kind: Sfx): void {
    const ctx = this.ctx;
    if (!ctx || !this.gain) return;
    const n = ctx.currentTime;
    if (kind === 'die' || kind === 'respawn') {
      const [notes, step, type] = JINGLES[kind];
      notes.forEach((f, i) => {
        const last = i === notes.length - 1;
        this.tone(ctx, last && kind === 'die' ? [f, f / 2, step * 4, type] : [f, f * 1.01, step * 1.4, type], n + i * step);
      });
      return;
    }
    this.tone(ctx, SFX[kind], n);
  }

  private tone(ctx: AudioContext, [f0, f1, dur, type]: Sweep, at: number): void {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.type = type;
    o.frequency.setValueAtTime(f0, at);
    o.frequency.exponentialRampToValueAtTime(f1, at + dur);
    g.gain.setValueAtTime(0.05, at);
    g.gain.exponentialRampToValueAtTime(0.0005, at + dur);
    o.connect(g); g.connect(this.gain!);
    o.start(at); o.stop(at + dur + 0.02);
  }
}
