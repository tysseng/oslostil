// Entry point: wires audio, game, renderer and UI together and runs the frame loop.
import songUrl from '../assets/oslostil.mp3';
import { AudioEngine } from './audio';
import { H, W } from './config';
import { Game } from './game';
import { canvas, resetTransform } from './render/draw';
import { drawGame, drawPause, drawTitle, drawWin } from './render/screens';
import { lyricAt } from './timeline';
import { DevPanel } from './ui/devpanel';
import { Subtitles } from './ui/subtitles';
import { LevelEditor } from './ui/editor';
import './style.css';

const audio = new AudioEngine();
const game = new Game(audio);

// canvas + subtitle layer share a wrapper so the subtitles sit on top of the picture
const screen = document.createElement('div');
screen.className = 'screen';
canvas.before(screen);
screen.append(canvas);
const subtitles = new Subtitles(screen);
const dev = new DevPanel(game, screen, canvas, __DEV_MODE_DEFAULT__);
const editor = new LevelEditor(game, screen);
if (__DEV_MODE_DEFAULT__) {
  const help = document.createElement('span');
  help.innerHTML = ' · <b>1</b> dev panel · <b>2</b> mark time · <b>3 / 4</b> sync';
  document.querySelector('.note')?.append(help);
}

addEventListener('keydown', (e) => {
  if (e.target instanceof HTMLElement && (e.target.isContentEditable || e.target.closest('textarea, input:not([type="range"])'))) return;
  if (dev.keyDown(e)) return;
  if (editor.keyDown(e)) return;
  if (e.target instanceof HTMLElement && e.target.closest('button, input, select, textarea')) return;
  game.keyDown(e);
});
addEventListener('keyup', (e) => game.keyUp(e));
addEventListener('blur', () => game.pause());

function fit(): void {
  const s = Math.max(1, Math.floor(Math.min((innerWidth * 0.96) / W, (innerHeight * 0.7) / H)));
  canvas.style.width = W * s + 'px';
  canvas.style.height = H * s + 'px';
  subtitles.fit(canvas.getBoundingClientRect().width / W);
}
addEventListener('resize', fit);
fit();

let last = performance.now();
function frame(now: number): void {
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;
  resetTransform();
  if (game.mode === 'loading' || game.mode === 'title') { subtitles.set(null); drawTitle(now / 1000, game.mode === 'loading'); }
  else if (game.mode === 'win') { subtitles.set(null); drawWin(game, now / 1000); }
  else if (game.mode === 'editor') { subtitles.set(null); editor.draw(); }
  else {
    if (game.mode === 'play') game.update(audio.time(), dt);
    const t = game.s.lastT;
    drawGame(game, t, dev.enabled);
    subtitles.set(game.mode === 'play' ? lyricAt(t)?.text ?? null : null);
    if (game.mode === 'pause') drawPause();
  }
  dev.tick();
  editor.tick();
  requestAnimationFrame(frame);
}

// hook for automated tests / the console
/**
 * Simulate up to song time t (starting `lead` seconds earlier, at 60 fps, no input), pause there and return
 * the frame as a PNG data URL without the pause overlay. Works even when the tab is hidden and rAF is throttled.
 */
function snap(t: number, lead = 1.5): string {
  game.seek(t - lead);
  game.pause();
  for (let u = t - lead; u < t; u += 1 / 60) game.update(Math.min(u + 1 / 60, t), 1 / 60);
  resetTransform();
  drawGame(game, game.s.lastT, false);
  return canvas.toDataURL();
}
(window as unknown as { __oslo: unknown }).__oslo = { game, seek: (t: number) => game.seek(t), snap };

// Dev server: after a code change the page reloads, so remember where we were and come back paused there.
const RESUME_KEY = 'oslostil-resume';
if (import.meta.hot) {
  import.meta.hot.on('vite:beforeFullReload', () => {
    if (game.mode === 'play' || game.mode === 'pause') sessionStorage.setItem(RESUME_KEY, String(game.s.lastT));
  });
}

async function boot(): Promise<void> {
  await document.fonts?.load('8px "Press Start 2P"').catch(() => undefined);
  requestAnimationFrame(frame);
  try { await audio.load(songUrl); } catch (err) { console.warn('song failed to load', err); }
  game.mode = 'title';
  const resume = import.meta.env.DEV ? sessionStorage.getItem(RESUME_KEY) : null;
  if (resume !== null) {
    sessionStorage.removeItem(RESUME_KEY);
    game.seek(Number(resume));
    game.pause(); // audio can only start after a key press – P continues
  }
}
void boot();
