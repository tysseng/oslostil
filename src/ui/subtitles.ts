// Lyric subtitles are HTML on top of the canvas, so they render sharp at the display resolution.
import './subtitles.css';

export class Subtitles {
  private readonly el = document.createElement('div');
  private current: string | null = null;

  constructor(wrap: HTMLElement) {
    this.el.className = 'subtitle';
    this.el.hidden = true;
    wrap.append(this.el);
  }

  set(line: string | null): void {
    if (line === this.current) return;
    this.current = line;
    this.el.hidden = !line;
    if (line) this.el.textContent = line;
  }

  /** @param scale CSS pixels per game pixel */
  fit(scale: number): void {
    this.el.style.fontSize = Math.max(10, Math.round(scale * 6.5)) + 'px';
    this.el.style.bottom = Math.round(scale * 3) + 'px';
  }
}
