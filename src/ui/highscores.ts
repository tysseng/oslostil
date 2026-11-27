import type { Game } from '../game';
import './highscores.css';

interface Highscore { initials: string; score: number }
const STORAGE_KEY = 'oslostil-highscores-v1';
const LIMIT = 10;

export class Highscores {
  private readonly el = document.createElement('section');
  private readonly entry: HTMLElement;
  private readonly input: HTMLElement;
  private initials = 'AAA';
  private readonly letters: HTMLElement[];
  private letterIndex = 0;
  private readonly score: HTMLElement;
  private readonly rows: HTMLElement;
  private readonly table: HTMLTableElement;
  private readonly heading: HTMLElement;
  private readonly placement: HTMLElement;
  private readonly status: HTMLElement;
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
      <div class="score-placement"></div>
      <div class="initials-entry">
        <div class="score-entry"><div id="score-initials" class="arcade-initials" tabindex="0" role="textbox"
          aria-label="Tre initialer" aria-describedby="initials-help"><div class="initials-letters" aria-hidden="true"><span></span><span></span><span></span></div></div>
          <span class="current-score"></span></div>
        <div id="initials-help">OPP/NED: BOKSTAV &nbsp; VENSTRE/HØYRE: PLASS</div>
      </div>
      <table><thead><tr><th scope="col">PLACE</th><th scope="col">PLAYER</th><th scope="col">SCORE</th></tr></thead><tbody></tbody></table>
      <p role="status"></p>`;
    screen.append(this.el);
    this.entry = this.el.querySelector('.initials-entry')!;
    this.input = this.el.querySelector('#score-initials')!;
    this.letters = Array.from(this.el.querySelectorAll<HTMLElement>('.initials-letters span'));
    this.score = this.el.querySelector('.current-score')!;
    this.rows = this.el.querySelector('tbody')!;
    this.table = this.el.querySelector('table')!;
    this.heading = this.el.querySelector('h2')!;
    this.placement = this.el.querySelector('.score-placement')!;
    this.status = this.el.querySelector('[role="status"]')!;
    this.letters.forEach((letter, index) => {
      letter.addEventListener('click', () => {
        this.input.focus();
        this.selectLetter(index);
      });
    });
    this.input.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (/^[a-z]$/i.test(e.key)) {
        e.preventDefault();
        this.initials = this.initials.slice(0, this.letterIndex) + e.key.toUpperCase() + this.initials.slice(this.letterIndex + 1);
        this.selectLetter(Math.min(2, this.letterIndex + 1));
        return;
      }
      if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) return;
      e.preventDefault();
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        this.selectLetter((this.letterIndex + (e.key === 'ArrowRight' ? 1 : 2)) % 3);
      } else {
        const letters = this.initials.split('');
        const current = letters[this.letterIndex].charCodeAt(0) - 65;
        letters[this.letterIndex] = String.fromCharCode(65 + (current + (e.key === 'ArrowUp' ? 1 : 25)) % 26);
        this.initials = letters.join('');
        this.selectLetter(this.letterIndex);
      }
    });
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
      this.loadError = 'Kunne ikke laste lagrede poengsummer.';
    }
  }

  place(score: number): number {
    return 1 + this.scores.filter((entry) => entry.score >= score).length;
  }

  keyDown(e: KeyboardEvent): boolean {
    if (this.game.mode !== 'highscore') return false;
    if (e.code === 'Enter' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      e.preventDefault();
      if (!e.repeat) {
        this.tick(performance.now());
        if (this.returnAt === null) this.save();
        else this.finish();
      }
    }
    return true;
  }

  private save(): void {
    if (this.returnAt !== null) return;
    const entry = { initials: this.initials, score: this.game.s.score };
    this.scores = [...this.scores, entry].sort((a, b) => b.score - a.score).slice(0, LIMIT);
    let message = '';
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.scores));
      this.loadError = '';
    } catch (error) {
      console.error('Could not save highscores', error);
      message = 'Kunne ikke lagre. Poengsummene er midlertidige.';
    }
    this.showTable(performance.now(), message, entry);
  }

  private showTable(now: number, message: string, current?: Highscore): void {
    this.placement.hidden = true;
    this.render(current);
    this.entry.hidden = true;
    this.table.hidden = false;
    this.el.classList.remove('entering-score');
    this.heading.textContent = 'HIGHSCORES';
    document.getElementById('game')?.focus();
    this.status.textContent = message;
    this.returnAt = now + 7000;
  }

  private selectLetter(index: number): void {
    this.letterIndex = index;
    this.showLetters();
  }

  private showLetters(): void {
    this.letters.forEach((letter, index) => {
      letter.replaceChildren();
      const character = document.createElement('span');
      character.className = 'letter-character';
      character.textContent = this.initials[index];
      const blank = document.createElement('span');
      blank.className = 'letter-blank';
      blank.textContent = '_';
      letter.append(character, blank);
      letter.classList.toggle('active-letter', index === this.letterIndex);
    });
    this.input.setAttribute('aria-label', `Initialer ${this.initials}, bokstav ${this.letterIndex + 1} er valgt. Bruk piltastene eller skriv bokstaver.`);
  }

  private render(current?: Highscore): void {
    this.rows.replaceChildren();
    for (let index = 0; index < LIMIT; index++) {
      const entry = this.scores[index];
      const row = document.createElement('tr');
      if (entry && entry === current) row.className = 'new-score';
      for (const value of [String(index + 1).padStart(2, '0'), entry?.initials ?? '---', entry ? String(entry.score).padStart(6, '0') : '------']) {
        const cell = document.createElement('td');
        cell.textContent = value;
        row.append(cell);
      }
      this.rows.append(row);
    }
  }

  private finish(): void {
    this.game.intro();
    this.active = false;
    this.el.hidden = true;
    document.body.classList.remove('showing-highscores');
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
      this.initials = 'AAA';
      this.letterIndex = 0;
      this.showLetters();
      this.entry.hidden = false;
      this.table.hidden = true;
      this.el.classList.add('entering-score');
      this.heading.textContent = 'SKRIV INITIALER';
      this.score.textContent = String(this.game.s.score).padStart(6, '0');
      this.status.textContent = this.loadError;
      this.render();
      this.input.focus();
      this.selectLetter(0);
      const place = this.place(this.game.s.score);
      this.placement.textContent = `YOU PLACED #${place}`;
      this.placement.hidden = false;
      this.placement.classList.toggle('first-place', place === 1);
      if (place > LIMIT) this.showTable(now, this.loadError);
    }
    if (this.returnAt !== null && now >= this.returnAt) {
      this.finish();
      this.el.hidden = true;
      this.active = false;
    }
  }
}
