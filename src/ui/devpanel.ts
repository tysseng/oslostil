// Development-only seek slider, jump buttons and time marks.
import { BAR, BEAT, PH, WIN_AT } from '../config';
import type { Game } from '../game';
import { JUMPS } from '../timeline';
import './devpanel.css';

export const fmtTime = (t: number): string => {
  const m = Math.floor(t / 60);
  return m + ':' + (t - m * 60).toFixed(2).padStart(5, '0');
};
const barLabel = (t: number): string => {
  const b = Math.floor((t - PH) / BAR) + 1, beat = Math.floor((((t - PH) % BAR + BAR) % BAR) / BEAT) + 1;
  return `bar ${Math.max(1, b)}.${beat}`;
};

export class DevPanel {
  private readonly el = document.createElement('div');
  private readonly slider: HTMLInputElement;
  private readonly time: HTMLElement;
  private readonly marksEl: HTMLElement;
  private readonly marks: number[] = [];
  private dragging = false;
  enabled: boolean;

  constructor(private readonly game: Game, after: HTMLElement, focusTarget: HTMLElement, enabled: boolean) {
    this.el.className = 'devpanel';
    this.el.innerHTML = `
      <div class="row"><span class="tag">DEV</span>
        <input type="range" min="0" max="${(WIN_AT - 0.5).toFixed(1)}" step="0.05" value="0" aria-label="Song position">
        <span class="time">0:00.00 · bar 1.1</span></div>
      <div class="row jumps"></div>
      <div class="row"><span>1 = dev panel · 2 = mark time · 3 / 4 = sync - / +50 ms · 5 = clean pause</span><span class="marks"></span></div>`;
    after.after(this.el);
    this.slider = this.el.querySelector('input')!;
    this.time = this.el.querySelector('.time')!;
    this.marksEl = this.el.querySelector('.marks')!;
    const refocus = () => { (document.activeElement as HTMLElement | null)?.blur(); focusTarget.focus(); };
    this.slider.addEventListener('input', () => { this.dragging = true; this.showTime(+this.slider.value); });
    const seek = (t: number) => game.mode === 'editor' ? game.edit(t) : game.seek(t);
    this.slider.addEventListener('change', () => { this.dragging = false; seek(+this.slider.value); refocus(); });
    const jumps = this.el.querySelector('.jumps')!;
    for (const [name, t] of JUMPS) {
      const b = document.createElement('button');
      b.textContent = name;
      b.addEventListener('click', () => { seek(t); refocus(); });
      jumps.append(b);
    }
    game.onMark = (t) => {
      if (!this.enabled) return;
      this.marks.push(t);
      this.marksEl.textContent = this.marks.slice(-8).map(fmtTime).join('  ');
    };
    this.enabled = enabled;
    this.el.hidden = !enabled;
  }

  toggle(): void {
    if (!__DEV_MODE_DEFAULT__) return;
    this.enabled = !this.enabled;
    this.el.hidden = !this.enabled;
  }

  keyDown(e: KeyboardEvent): boolean {
    if (!__DEV_MODE_DEFAULT__ || e.ctrlKey || e.metaKey || e.altKey || e.shiftKey) return false;
    const key = e.key;
    if (!['1', '2', '3', '4', '5'].includes(key)) return false;
    e.preventDefault();
    if (e.repeat) return true;
    if (key === '1') this.toggle();
    else if (key === '2') {
      if (this.game.mode === 'play' || this.game.mode === 'pause' || this.game.mode === 'editor') this.game.onMark(this.game.s.lastT);
    } else if (key === '5') {
      if (this.game.mode === 'pause' && this.game.cleanPause) this.game.resume();
      else this.game.pause(true);
    } else {
      this.game.audio.nudgeSync(key === '4' ? 0.05 : -0.05);
      this.game.syncToast = 1.5;
    }
    return true;
  }

  private showTime(t: number): void { this.time.textContent = `${fmtTime(t)} · ${barLabel(t)}`; }

  tick(): void {
    if (!this.enabled || this.dragging) return;
    if (this.game.mode === 'play' || this.game.mode === 'pause' || this.game.mode === 'editor') {
      this.slider.value = String(this.game.s.lastT);
      this.showTime(this.game.s.lastT);
    }
  }
}
