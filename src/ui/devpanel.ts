// Dev mode: seek slider, jump buttons and time marks under the game. Toggle with the key left of «1».
import { BAR, BEAT, PH, WIN_AT } from '../config';
import type { Game } from '../game';
import { JUMPS } from '../timeline';
import './devpanel.css';

/** The key left of «1»: `Backquote` on US/Windows layouts, `IntlBackslash` (§) on Nordic Mac keyboards. */
export const DEV_KEYS = ['Backquote', 'IntlBackslash'];

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
      <div class="row"><span>T = mark time · § / \` = dev mode on/off</span><span class="marks"></span></div>`;
    after.after(this.el);
    this.slider = this.el.querySelector('input')!;
    this.time = this.el.querySelector('.time')!;
    this.marksEl = this.el.querySelector('.marks')!;
    const refocus = () => { (document.activeElement as HTMLElement | null)?.blur(); focusTarget.focus(); };
    this.slider.addEventListener('input', () => { this.dragging = true; this.showTime(+this.slider.value); });
    this.slider.addEventListener('change', () => { this.dragging = false; game.seek(+this.slider.value); refocus(); });
    const jumps = this.el.querySelector('.jumps')!;
    for (const [name, t] of JUMPS) {
      const b = document.createElement('button');
      b.textContent = name;
      b.addEventListener('click', () => { game.seek(t); refocus(); });
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

  toggle(): void { this.enabled = !this.enabled; this.el.hidden = !this.enabled; }

  private showTime(t: number): void { this.time.textContent = `${fmtTime(t)} · ${barLabel(t)}`; }

  tick(): void {
    if (!this.enabled || this.dragging) return;
    if (this.game.mode === 'play' || this.game.mode === 'pause') {
      this.slider.value = String(this.game.s.lastT);
      this.showTime(this.game.s.lastT);
    }
  }
}
