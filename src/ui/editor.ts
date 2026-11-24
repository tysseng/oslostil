import { GROUND, H, W, WIN_AT } from '../config';
import type { Game } from '../game';
import { loadDefaultLevel, parseLevel } from '../level';
import { canvas, ctx, resetTransform } from '../render/draw';
import { drawScene } from '../render/scenes';
import { drawEnemy, drawLampLights } from '../render/sprites';
import { NINJAS, NINJA_CELL_W, NINJA_CELL_H, THUGS, fighterRow, isFighter, isNinjaKind } from '../ninjas';
import { PASSENGERS, PASSENGER_CELL_W, PASSENGER_CELL_H, isPassenger } from '../passengers';
import { POWERUPS, isPowerup, BROKEN_BOARD, TREES, TREE_CELL_W, TREE_CELL_H, isTree, treeDepth, LAMPS, LAMP_CELL_W, LAMP_CELL_H, isLamp, PROPS, PROP_CELL_W, PROP_CELL_H, isProp, SHEET, TYPES, type EnemyKind, type ScheduledEvent } from '../schedule';
import { compareItems, createEnemy, enemyBodyHeight, enemyHeight, enemyX, eventArrival, eventSpeed } from '../state';
import { sectionAt } from '../timeline';
import { fmtTime } from './devpanel';
import enemiesUrl from '../../assets/sprites/enemies.png';
import tramUrl from '../../assets/vehicles/hires/tram-new.png';
import propsUrl from '../../assets/sprites/props.png';
import lampsUrl from '../../assets/sprites/lamps.png';
import lightsUrl from '../../assets/sprites/lamps-light.png';
import ninjasUrl from '../../assets/sprites/ninjas.png';
import thugsUrl from '../../assets/sprites/thugs.png';
import treesUrl from '../../assets/sprites/trees.png';
import passengersUrl from '../../assets/sprites/passengers.png';
import boardUrl from '../../assets/sprites/board-broken.png';
import powerupsUrl from '../../assets/sprites/powerups.png';
import './editor.css';
import { drawValkyrien, drawValkyrienBalustrade, drawValkyrienHouse } from '../render/valkyrien';

const STORAGE_KEY = 'oslostil-level-v1';
const kinds = Object.keys(TYPES) as EnemyKind[];
const categories = ['Enemies', 'Power-ups', 'Tickets & coins', 'Lights', 'Props & platforms', 'Trees', 'Vehicles', 'Hazards'] as const;
type Category = (typeof categories)[number];

function itemCategory(kind: EnemyKind): Category {
  if (isPowerup(kind) || kind === 'terminal') return 'Power-ups';
  if (isLamp(kind)) return 'Lights';
  if (isTree(kind)) return 'Trees';
  if (isProp(kind) || kind === 'board_broken') return 'Props & platforms';
  if (kind === 'tram') return 'Vehicles';
  if (TYPES[kind].pickup) return 'Tickets & coins';
  if (kind === 'suitcase' || kind === 'snow' || kind === 'fire' || kind === 'shot' || kind === 'fireball') return 'Hazards';
  return 'Enemies';
}

interface Drag {
  event: ScheduledEvent;
  dx: number;
  dy: number;
  before: ScheduledEvent;
  pointer: number;
}

export class LevelEditor {
  private readonly entry = document.createElement('button');
  private readonly intro = document.createElement('button');
  private readonly panel = document.createElement('section');
  private readonly slider: HTMLInputElement;
  private readonly time: HTMLOutputElement;
  private readonly status: HTMLElement;
  private readonly tools: HTMLButtonElement[] = [];
  private selected: EnemyKind | null = null;
  private hovered: ScheduledEvent | null = null;
  private drag: Drag | null = null;
  private inspected: ScheduledEvent | null = null;
  private readonly hopInput: HTMLSelectElement;

  constructor(private readonly game: Game, screen: HTMLElement) {
    this.entry.className = 'editor-entry';
    this.entry.textContent = 'Level editor';
    this.entry.addEventListener('click', () => {
      game.edit(game.mode === 'title' ? 0 : game.s.lastT);
      canvas.focus();
      this.tick();
    });
    screen.after(this.entry);
    this.intro.className = 'editor-entry';
    this.intro.textContent = 'Intro';
    this.intro.addEventListener('click', () => {
      game.intro();
      canvas.focus();
      this.tick();
    });
    this.entry.after(this.intro);
    this.panel.className = 'level-editor';
    this.panel.hidden = true;
    this.panel.setAttribute('aria-label', 'Level editor');
    this.panel.innerHTML = `
      <div class="editor-row">
        <button type="button" data-action="title">Title</button>
        <button type="button" data-action="test">Play level</button>
        <button type="button" data-action="download">Download level</button>
        <button type="button" data-action="import">Import level</button>
        <input type="file" accept=".json,application/json" hidden aria-label="Import level JSON">
        <button type="button" data-action="default">Use default level</button>
        <output class="editor-status" role="status"></output>
      </div>
      <div class="editor-row">
        <label for="editor-time">Song position</label>
        <input id="editor-time" type="range" min="0" max="${WIN_AT - 0.5}" step="0.01" value="0">
        <output class="editor-time"></output>
      </div>
      <div class="editor-palette" role="group" aria-label="Items" tabindex="0"></div>
      <div class="editor-row editor-item-options" hidden>
        <label class="editor-hop" hidden>Hop
          <select aria-label="Glitch hop variant"><option value="">Normal</option><option value="low">Low</option><option value="high">High</option><option value="double">Double</option></select></label>
      </div>
      <details class="editor-help">
      <summary>Editor help</summary>
      <p>To publish this layout as the default: download it, replace src/level.json with the downloaded file, then rebuild/deploy. Use default level discards the browser draft.</p>
      <p>Drag any item to move it. Right-click an item to delete it. Select an item below, then click empty space to place copies. Move / Esc stops placing.</p>
      <p>Broken boards crumble when landed on. Select a hopping glitch to edit its hop variant; tool settings also apply to new copies.</p>
      </details>`;
    this.entry.after(this.panel);
    this.slider = this.panel.querySelector('input[type="range"]')!;
    this.time = this.panel.querySelector('.editor-time')!;
    this.status = this.panel.querySelector('.editor-status')!;
    this.hopInput = this.panel.querySelector('.editor-hop select')!;
    this.hopInput.addEventListener('change', () => {
      if (this.inspected?.type !== 'blob_hop') return;
      this.inspected.hop = this.hopVariant();
      this.save();
    });
    this.slider.addEventListener('input', () => {
      game.edit(Number(this.slider.value));
      this.hovered = null;
      this.tick();
    });
    this.panel.querySelector('[data-action="title"]')!.addEventListener('click', () => {
      game.intro();
      canvas.focus();
      this.tick();
    });
    this.panel.querySelector('[data-action="test"]')!.addEventListener('click', () => {
      game.keys.clear();
      game.seek(game.s.lastT);
      canvas.focus();
      this.tick();
    });
    this.panel.querySelector('[data-action="download"]')!.addEventListener('click', () => {
      const url = URL.createObjectURL(new Blob([JSON.stringify(game.level, null, 2) + '\n'], { type: 'application/json' }));
      const link = document.createElement('a');
      link.href = url;
      link.download = 'level.json';
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      this.status.textContent = 'Download requested: level.json';
    });
    const fileInput = this.panel.querySelector<HTMLInputElement>('input[type="file"]')!;
    this.panel.querySelector('[data-action="import"]')!.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
      const file = fileInput.files?.[0];
      fileInput.value = '';
      if (file) void this.importLevel(file);
    });
    this.panel.querySelector('[data-action="default"]')!.addEventListener('click', () => {
      if (!confirm('Discard the browser draft and use the bundled default level?')) return;
      try {
        const level = loadDefaultLevel();
        localStorage.removeItem(STORAGE_KEY);
        game.level = level;
        this.inspect(null);
        this.hovered = null;
        game.edit();
        this.status.textContent = 'Using bundled default level';
      } catch (error) {
        console.error('Could not restore default level', error);
        this.status.textContent = 'Could not restore default level. Current layout is unchanged.';
      }
    });
    const palette = this.panel.querySelector('.editor-palette')!;
    const groups = new Map<Category, HTMLElement>();
    const addTool = (name: string, kind: EnemyKind | null): HTMLButtonElement => {
      const button = document.createElement('button');
      button.type = 'button';
      button.setAttribute('aria-pressed', String(kind === null));
      button.addEventListener('click', () => {
        this.selected = kind;
        this.inspect(null);
        this.tools.forEach((tool) => tool.setAttribute('aria-pressed', String(tool === button)));
        canvas.focus();
      });
      const label = document.createElement('span');
      label.textContent = name;
      button.append(label);
      this.tools.push(button);
      (kind === null ? palette : groups.get(itemCategory(kind))!).append(button);
      return button;
    };
    addTool('Move', null);
    for (const category of categories) {
      if (!kinds.some(kind => itemCategory(kind) === category)) continue;
      const group = document.createElement('fieldset');
      group.className = 'editor-category';
      const heading = document.createElement('legend');
      heading.textContent = category;
      group.append(heading);
      groups.set(category, group);
      palette.append(group);
    }
    const sheet = new Image();
    sheet.src = enemiesUrl;
    const props = new Image();
    props.src = propsUrl;
    const lamps = new Image(), lights = new Image(), ninjas = new Image();
    ninjas.src = ninjasUrl;
    const thugs = new Image(), passengers = new Image(), trees = new Image();
    const board = new Image();
    board.src = boardUrl;
    const powerups = new Image();
    powerups.src = powerupsUrl;
    trees.src = treesUrl;
    thugs.src = thugsUrl; passengers.src = passengersUrl;
    lamps.src = lampsUrl; lights.src = lightsUrl;
    for (const kind of kinds) {
      const button = addTool(kind[0].toUpperCase() + kind.slice(1), kind);
      if (kind === 'tram') {
        const img = document.createElement('img');
        img.src = tramUrl;
        img.alt = '';
        button.prepend(img);
      } else if (isPowerup(kind)) {
        const preview = document.createElement('canvas');
        preview.width = 64; preview.height = 40;
        const draw = () => {
          const c = preview.getContext('2d')!;
          c.imageSmoothingEnabled = false;
          c.drawImage(powerups, 0, POWERUPS[kind].row * 32, 32, 32, 16, 4, 32, 32);
        };
        if (powerups.complete && powerups.naturalWidth) draw();
        else powerups.addEventListener('load', draw, { once: true });
        button.prepend(preview);
      } else if (kind === 'board_broken') {
        const preview = document.createElement('canvas');
        preview.width = 64; preview.height = 52;
        const draw = () => {
          const [w, h] = BROKEN_BOARD.cell;
          preview.getContext('2d')!.drawImage(board, 0, 0, w, h, 0, 0, w, h);
        };
        if (board.complete && board.naturalWidth) draw();
        else board.addEventListener('load', draw, { once: true });
        button.prepend(preview);
      } else if (isTree(kind)) {
        const preview = document.createElement('canvas');
        preview.width = 64; preview.height = 40;
        const draw = () => {
          const c = preview.getContext('2d')!;
          c.imageSmoothingEnabled = false;
          c.drawImage(trees, 0, TREES[kind].row * TREE_CELL_H, TREE_CELL_W, TREE_CELL_H, 12, 0, 40, 40);
        };
        if (trees.complete && trees.naturalWidth) draw();
        else trees.addEventListener('load', draw, { once: true });
        button.prepend(preview);
      } else if (isLamp(kind)) {
        const preview = document.createElement('canvas');
        preview.width = 64; preview.height = 40;
        const draw = () => {
          const c = preview.getContext('2d')!;
          c.clearRect(0, 0, 64, 40);
          c.imageSmoothingEnabled = false;
          for (const image of [lamps, lights]) {
            if (image.complete && image.naturalWidth) c.drawImage(image, 0, LAMPS[kind].row * LAMP_CELL_H,
              LAMP_CELL_W, LAMP_CELL_H, 8, 0, 48, 40);
          }
        };
        lamps.addEventListener('load', draw, { once: true });
        lights.addEventListener('load', draw, { once: true });
        draw();
        button.prepend(preview);
      } else if (isFighter(kind) || isPassenger(kind) || kind === 'tagger_spray') {
        const preview = document.createElement('canvas');
        preview.width = 64; preview.height = 40;
        const img = isNinjaKind(kind) ? ninjas : isPassenger(kind) ? passengers : thugs;
        const draw = () => {
          const c = preview.getContext('2d')!;
          c.imageSmoothingEnabled = false;
          if (isFighter(kind)) c.drawImage(img, NINJAS.anims.run[0] * NINJA_CELL_W, fighterRow(kind) * NINJA_CELL_H,
            NINJA_CELL_W, NINJA_CELL_H, 12, 4, 40, 32);
          else if (isPassenger(kind)) c.drawImage(img, PASSENGERS.anims.walk[0] * PASSENGER_CELL_W,
            PASSENGERS.kinds[kind].row * PASSENGER_CELL_H, PASSENGER_CELL_W, PASSENGER_CELL_H, 12, 4, 40, 32);
          else c.drawImage(img, 0, THUGS.spray.row * NINJA_CELL_H, NINJA_CELL_W, NINJA_CELL_H, 12, 4, 40, 32);
        };
        if (img.complete && img.naturalWidth) draw();
        else img.addEventListener('load', draw, { once: true });
        button.prepend(preview);
      } else if (isProp(kind)) {
        const preview = document.createElement('canvas');
        preview.width = 64; preview.height = 40;
        const draw = () => {
          const c = preview.getContext('2d')!;
          c.imageSmoothingEnabled = false;
          c.drawImage(props, 0, PROPS[kind].row * PROP_CELL_H, PROP_CELL_W, PROP_CELL_H, 4, 4, 56, 32);
        };
        if (props.complete && props.naturalWidth) draw();
        else props.addEventListener('load', draw, { once: true });
        button.prepend(preview);
      } else {
        const preview = document.createElement('canvas');
        preview.width = 64;
        preview.height = 40;
        const draw = () => {
          const c = preview.getContext('2d')!;
          c.imageSmoothingEnabled = false;
          c.drawImage(sheet, 0, SHEET[kind].row * 32, 32, 32, 16, 4, 32, 32);
        };
        if (sheet.complete && sheet.naturalWidth) draw();
        else sheet.addEventListener('load', draw, { once: true });
        button.prepend(preview);
      }
    }
    canvas.addEventListener('pointerdown', (e) => this.pointerDown(e));
    canvas.addEventListener('pointermove', (e) => this.pointerMove(e));
    canvas.addEventListener('pointerup', (e) => this.finishDrag(e, false));
    canvas.addEventListener('pointercancel', (e) => this.finishDrag(e, true));
    canvas.addEventListener('lostpointercapture', (e) => this.finishDrag(e, true));
    canvas.addEventListener('pointerleave', () => { if (!this.drag) this.hovered = null; });
    canvas.addEventListener('wheel', (e) => {
      if (game.mode !== 'editor' || e.ctrlKey || e.metaKey) return;
      e.preventDefault();
      const delta = e.deltaY || e.deltaX;
      const scale = e.deltaMode === 1 ? 0.03 : e.deltaMode === 2 ? 1 : 0.001;
      this.scrub(delta * scale);
    }, { passive: false });
    canvas.addEventListener('contextmenu', (e) => {
      if (game.mode !== 'editor') return;
      e.preventDefault();
      const hit = this.hit(...this.point(e));
      if (!hit) return;
      game.level.splice(game.level.indexOf(hit), 1);
      if (this.inspected === hit) this.inspect(null);
      this.hovered = null;
      this.save();
    });
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved !== null) {
        game.level = parseLevel(JSON.parse(saved));
        this.status.textContent = 'Saved layout loaded';
      }
    } catch (error) {
      console.error('Could not load edited level', error);
      this.status.textContent = 'Could not load saved layout. Bundled default is in use.';
    }
    this.tick();
  }

  private async importLevel(file: File): Promise<void> {
    try {
      const level = parseLevel(JSON.parse(await file.text()));
      if (!confirm(`Replace the current layout with ${level.length} items from ${file.name}?`)) return;
      this.game.level = level;
      this.inspect(null);
      this.hovered = null;
      this.game.edit();
      this.save();
    } catch (error) {
      console.error('Could not import level', error);
      this.status.textContent = 'Import failed: invalid or unreadable level JSON. Current layout is unchanged.';
    }
  }

  keyDown(e: KeyboardEvent): boolean {
    if (this.game.mode !== 'editor') return false;
    if ((e.code === 'ArrowLeft' || e.code === 'ArrowRight') && !e.ctrlKey && !e.metaKey && !e.altKey) {
      if (e.target instanceof HTMLElement && e.target.closest('select')) return true;
      e.preventDefault();
      this.scrub(e.code === 'ArrowRight' ? 0.1 : -0.1);
    }
    if (e.code === 'Escape') {
      this.selected = null;
      this.inspect(null);
      this.tools.forEach((tool, i) => tool.setAttribute('aria-pressed', String(i === 0)));
    }
    return true;
  }

  private scrub(delta: number): void {
    if (this.drag || delta === 0) return;
    this.game.edit(this.game.s.lastT + delta);
    this.hovered = null;
    this.tick();
  }

  private point(e: MouseEvent): [number, number] {
    const rect = canvas.getBoundingClientRect();
    return [
      ((e.clientX - rect.left) * canvas.offsetWidth / rect.width - canvas.clientLeft) / canvas.clientWidth * W,
      ((e.clientY - rect.top) * canvas.offsetHeight / rect.height - canvas.clientTop) / canvas.clientHeight * H,
    ];
  }

  private bounds(e: ScheduledEvent): { x: number; y: number; w: number; h: number } {
    const type = TYPES[e.type], enemy = createEnemy(e), h = enemyBodyHeight(enemy, this.game.s.lastT);
    return {
      x: enemyX(createEnemy(e), this.game.s.lastT) - (e.type === 'tram' ? 0 : isLamp(e.type) ? LAMP_CELL_W / 2 : type.w / 2),
      y: GROUND - enemyHeight(enemy, this.game.s.lastT) - h,
      w: isLamp(e.type) ? LAMP_CELL_W : type.w, h,
    };
  }

  private layeredEvents(): ScheduledEvent[] {
    return this.game.level.slice().sort((a, b) => compareItems(createEnemy(a), createEnemy(b)));
  }

  private hit(x: number, y: number): ScheduledEvent | null {
    return this.layeredEvents().reverse().find((e) => {
      const b = this.bounds(e);
      return x >= b.x - 2 && x <= b.x + b.w + 2 && y >= b.y - 2 && y <= b.y + b.h + 2;
    }) ?? null;
  }

  private position(e: ScheduledEvent, x: number, base: number): void {
    if (isTree(e.type)) e.depth = treeDepth(e);
    e.rel = eventSpeed(e);
    e.arr = eventArrival(e, this.game.s.lastT, x);
    e.y = Math.round(Math.max(0, Math.min(GROUND - TYPES[e.type].h, GROUND - base)));
  }

  private pointerDown(e: PointerEvent): void {
    if (this.game.mode !== 'editor' || e.button !== 0 || this.drag) return;
    e.preventDefault();
    canvas.focus();
    const [x, y] = this.point(e), hit = this.hit(x, y);
    if (hit) {
      this.inspect(hit);
      this.drag = {
        event: hit, dx: x - enemyX(createEnemy(hit), this.game.s.lastT),
        dy: y - (GROUND - (hit.y ?? TYPES[hit.type].y)), before: { ...hit }, pointer: e.pointerId,
      };
      canvas.setPointerCapture(e.pointerId);
    } else if (this.selected) {
      const event: ScheduledEvent = { type: this.selected, arr: this.game.s.lastT };
      if (event.type === 'blob_hop') event.hop = this.hopVariant();
      if (isTree(event.type)) event.depth = treeDepth({ ...event, arr: event.arr + x / W });
      const enemy = createEnemy(event);
      const lift = event.type === 'blob_hop' || isPowerup(event.type) ? enemyHeight(enemy, this.game.s.lastT) - enemy.y : 0;
      this.position(event, x - (event.type === 'tram' ? TYPES.tram.w / 2 : 0), y + enemyBodyHeight(enemy, this.game.s.lastT) / 2 + lift);
      this.game.level.push(event);
      this.hovered = event;
      this.save();
    }
  }

  private pointerMove(e: PointerEvent): void {
    if (this.game.mode !== 'editor') return;
    const [x, y] = this.point(e);
    if (this.drag && e.pointerId === this.drag.pointer) {
      this.position(this.drag.event, x - this.drag.dx, y - this.drag.dy);
    }
    this.hovered = this.hit(x, y);
  }

  private finishDrag(e: PointerEvent, cancel: boolean): void {
    const drag = this.drag;
    if (!drag || drag.pointer !== e.pointerId) return;
    this.drag = null;
    if (cancel) {
      delete drag.event.rel;
      delete drag.event.y;
      delete drag.event.depth;
      Object.assign(drag.event, drag.before);
    } else this.save();
    this.inspect(drag.event);
    if (canvas.hasPointerCapture(e.pointerId)) canvas.releasePointerCapture(e.pointerId);
  }

  private save(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.game.level));
      this.status.textContent = 'Saved in this browser';
    } catch (error) {
      console.error('Could not save edited level', error);
      this.status.textContent = 'Save failed. Edits only last until this page is closed.';
    }
  }

  private hopVariant(): ScheduledEvent['hop'] {
    const value = this.hopInput.value;
    return value === 'low' || value === 'high' || value === 'double' ? value : undefined;
  }

  private inspect(event: ScheduledEvent | null): void {
    this.inspected = event;
    const kind = event?.type ?? this.selected;
    this.panel.querySelector<HTMLElement>('.editor-item-options')!.hidden = kind !== 'blob_hop';
    this.panel.querySelector<HTMLElement>('.editor-hop')!.hidden = kind !== 'blob_hop';
    this.hopInput.value = event?.hop ?? '';
  }

  tick(): void {
    const mode = this.game.mode, editing = mode === 'editor';
    this.panel.hidden = !editing;
    this.entry.hidden = !(mode === 'title' || mode === 'play' || mode === 'pause');
    this.intro.hidden = mode === 'loading' || mode === 'title' || editing;
    document.body.classList.toggle('editing', editing);
    canvas.style.touchAction = editing ? 'none' : '';
    canvas.style.cursor = editing ? (this.drag ? 'grabbing' : this.hovered ? 'grab' : this.selected ? 'crosshair' : 'default') : '';
    if (editing) {
      this.slider.value = String(this.game.s.lastT);
      this.time.value = fmtTime(this.game.s.lastT);
    }
  }

  draw(): void {
    const t = this.game.s.lastT;
    resetTransform();
    drawScene(sectionAt(t).scene, t, this.game.s.bgx, 0);
    drawValkyrien(t);
    const events = this.layeredEvents();
    for (const event of events) {
      const b = this.bounds(event);
      if (b.x > W || b.x + b.w < 0) continue;
      const enemy = createEnemy(event);
      drawEnemy(enemy, enemyX(enemy, t), t);
    }
    drawLampLights(events.map(createEnemy), t);
    drawValkyrienBalustrade(t);
    drawValkyrienHouse(t);
    for (const event of events) {
      const b = this.bounds(event);
      if (b.x > W || b.x + b.w < 0) continue;
      ctx.strokeStyle = event === this.drag?.event || event === this.hovered ? '#ffe14a' : '#2bf0ff88';
      ctx.lineWidth = 0.5;
      ctx.strokeRect(b.x - 1, b.y - 1, b.w + 2, b.h + 2);
    }
  }
}
