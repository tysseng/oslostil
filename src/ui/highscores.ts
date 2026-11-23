import type { Game } from '../game';
import './highscores.css';

interface Highscore { initials: string; score: number }
const STORAGE_KEY = 'oslostil-highscores-v1';
const LIMIT = 10;

export class Highscores {
  private readonly el = document.createElement('section');
  private readonly form: HTMLFormElement;
  private readonly input: HTMLInputElement;
  private readonly letters: HTMLElement[];
  private letterIndex = 0;
  private readonly score: HTMLElement;
  private readonly rows: HTMLElement;
  private readonly status: HTMLElement;
  private readonly done: HTMLButtonElement;
  private scores: Highscore[] = [];
  private active = false;
  private returnAt: number | null = null;
  private loadError = '';

  constructor(private readonly game: Game, screen: HTMLElement) {
    this.el.className = 'highscores';
    this.el.hidden = true;
    this.el.setAttribute('aria-label', 'Highscores');
    this.el.innerHTML = `
      <h2>HIGHSCORE</h2>
      <form><label for="score-initials">TRE BOKSTAVER / THREE LETTERS</label>
        <div class="score-entry"><div class="arcade-initials"><input id="score-initials" name="initials" type="text" maxlength="3"
          pattern="[A-Za-z]{3}" required autocomplete="off" autocapitalize="characters" spellcheck="false"
          aria-label="Three player initials" aria-describedby="initials-help"><div class="initials-letters" aria-hidden="true"><span></span><span></span><span></span></div></div>
          <span class="current-score"></span><button type="submit">LAGRE / SAVE</button></div>
        <div id="initials-help">UP / DOWN: LETTER &nbsp; LEFT / RIGHT: SLOT &nbsp; ENTER: SAVE<br>Or type three letters.</div>
      </form>
      <table><thead><tr><th scope="col">PLAYER</th><th scope="col">SCORE</th></tr></thead><tbody></tbody></table>
      <p role="status"></p><button type="button" class="score-done" hidden>STARTUP</button>`;
    screen.append(this.el);
    this.form = this.el.querySelector('form')!;
    this.input = this.el.querySelector('input')!;
    this.letters = Array.from(this.el.querySelectorAll<HTMLElement>('.initials-letters span'));
    this.score = this.el.querySelector('.current-score')!;
    this.rows = this.el.querySelector('tbody')!;
    this.status = this.el.querySelector('[role="status"]')!;
    this.done = this.el.querySelector('.score-done')!;
    this.input.addEventListener('input', () => {
      this.input.value = this.input.value.replace(/[^a-z]/gi, '').toUpperCase();
      this.letterIndex = Math.min(2, this.input.selectionStart ?? 0);
      this.showLetters();
    });
    this.input.addEventListener('click', () => {
      this.selectLetter(Math.min(2, this.input.selectionStart ?? 0));
    });
    this.input.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey || e.shiftKey || !['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) return;
      e.preventDefault();
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        this.selectLetter((this.letterIndex + (e.key === 'ArrowRight' ? 1 : 2)) % 3);
      } else {
        const letters = this.input.value.padEnd(3, 'A').split('');
        const current = letters[this.letterIndex].charCodeAt(0) - 65;
        letters[this.letterIndex] = String.fromCharCode(65 + (current + (e.key === 'ArrowUp' ? 1 : 25)) % 26);
        this.input.value = letters.join('');
        this.selectLetter(this.letterIndex);
      }
    });
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (this.returnAt !== null || !this.form.reportValidity()) return;
      const entry = { initials: this.input.value.toUpperCase(), score: game.s.score };
      this.scores = [...this.scores, entry].sort((a, b) => b.score - a.score).slice(0, LIMIT);
      let message = 'Saved in this browser. Returning to startup in 7 seconds.';
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.scores));
        this.loadError = '';
      } catch (error) {
        console.error('Could not save highscores', error);
        message = 'Save failed. Scores only last while this page is open. Returning in 7 seconds.';
      }
      this.render(entry);
      this.form.hidden = true;
      this.done.hidden = false;
      this.done.focus();
      this.status.textContent = message;
      this.returnAt = performance.now() + 7000;
    });
    this.done.addEventListener('click', () => this.finish());
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored !== null) {
        const value: unknown = JSON.parse(stored);
        if (!Array.isArray(value) || !value.every((row: unknown): row is Highscore => {
          if (!row || typeof row !== 'object') return false;
          const entry = row as Record<string, unknown>;
          return typeof entry.initials === 'string' && /^[A-Z]{3}$/.test(entry.initials)
            && typeof entry.score === 'number' && Number.isSafeInteger(entry.score) && entry.score >= 0;
        })) throw new Error('Invalid saved highscores');
        this.scores = value.sort((a, b) => b.score - a.score).slice(0, LIMIT);
      }
    } catch (error) {
      console.error('Could not load highscores', error);
      this.loadError = 'Could not load saved scores.';
    }
  }

  private selectLetter(index: number): void {
    this.letterIndex = index;
    this.input.setSelectionRange(index, index + 1);
    this.showLetters();
  }

  private showLetters(): void {
    this.letters.forEach((letter, index) => {
      letter.textContent = this.input.value[index] ?? '_';
      letter.classList.toggle('active-letter', index === this.letterIndex);
    });
  }

  private render(current?: Highscore): void {
    this.rows.replaceChildren();
    for (const entry of this.scores) {
      const row = document.createElement('tr');
      if (entry === current) row.className = 'new-score';
      for (const value of [entry.initials, String(entry.score).padStart(6, '0')]) {
        const cell = document.createElement('td');
        cell.textContent = value;
        row.append(cell);
      }
      this.rows.append(row);
    }
    if (!this.scores.length) {
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = 2;
      cell.textContent = 'NO SCORES YET';
      row.append(cell);
      this.rows.append(row);
    }
  }

  private finish(): void {
    this.game.keys.clear();
    this.game.mode = 'title';
    document.getElementById('game')?.focus();
  }

  tick(now: number): void {
    const active = this.game.mode === 'highscore';
    document.body.classList.toggle('showing-highscores', active);
    this.el.hidden = !active;
    if (!active) { this.active = false; return; }
    if (!this.active) {
      this.active = true;
      this.returnAt = null;
      this.input.value = 'AAA';
      this.letterIndex = 0;
      this.showLetters();
      this.form.hidden = false;
      this.done.hidden = true;
      this.score.textContent = String(this.game.s.score).padStart(6, '0');
      this.status.textContent = this.loadError || 'Enter three letters to save your score.';
      this.render();
      this.input.focus();
      this.selectLetter(0);
    }
    if (this.returnAt !== null && now >= this.returnAt) {
      this.finish();
      this.el.hidden = true;
      this.active = false;
    }
  }
}
