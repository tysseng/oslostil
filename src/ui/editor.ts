import { GROUND, H, PX, W, WIN_AT } from '../config';
import type { Game } from '../game';
import { loadDefaultLevel, parseLevel } from '../level';
import { canvas, ctx, resetTransform } from '../render/draw';
import { drawScene } from '../render/scenes';
import { drawEnemy, drawLampLights } from '../render/sprites';
import { NINJAS, NINJA_CELL_W, NINJA_CELL_H, THUGS, fighterRow, isFighter, isNinjaKind } from '../ninjas';
import { PASSENGERS, PASSENGER_CELL_W, PASSENGER_CELL_H, isPassenger } from '../passengers';
import { LAMPS, LAMP_CELL_W, LAMP_CELL_H, isLamp, itemLayer, PROPS, PROP_CELL_W, PROP_CELL_H, isProp, SHEET, TYPES, type EnemyKind, type ScheduledEvent } from '../schedule';
import { createEnemy, enemyX, eventSpeed } from '../state';
import { sectionAt } from '../timeline';
import { fmtTime } from './devpanel';
import enemiesUrl from '../../assets/sprites/enemies.png';
import tramUrl from '../../assets/vehicles/hires/tram-new.png';
import propsUrl from '../../assets/sprites/props.png';
import lampsUrl from '../../assets/sprites/lamps.png';
import lightsUrl from '../../assets/sprites/lamps-light.png';
import ninjasUrl from '../../assets/sprites/ninjas.png';
import thugsUrl from '../../assets/sprites/thugs.png';
import passengersUrl from '../../assets/sprites/passengers.png';
import './editor.css';

const STORAGE_KEY = 'oslostil-level-v1';
const kinds = Object.keys(TYPES) as EnemyKind[];

interface Drag {
  event: ScheduledEvent;
  dx: number;
  dy: number;
  before: ScheduledEvent;
  pointer: number;
}

export class LevelEditor {
  private readonly entry = document.createElement('button');
  private readonly panel = document.createElement('section');
  private readonly slider: HTMLInputElement;
  private readonly time: HTMLOutputElement;
  private readonly status: HTMLElement;
  private readonly tools: HTMLButtonElement[] = [];
  private selected: EnemyKind | null = null;
  private hovered: ScheduledEvent | null = null;
  private drag: Drag | null = null;
  private testing = false;
  private editTime = 0;

  constructor(private readonly game: Game, screen: HTMLElement) {
    this.entry.className = 'editor-entry';
    this.entry.textContent = 'Level editor';
    this.entry.addEventListener('click', () => {
      game.edit(this.testing ? this.editTime : 0);
      this.testing = false;
      this.tick();
    });
    screen.after(this.entry);
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
      <div class="editor-palette" role="group" aria-label="Items"></div>
      <p>To publish this layout as the default: download it, replace src/level.json with the downloaded file, then rebuild/deploy. Use default level discards the browser draft.</p>
      <p>Drag any item to move it. Right-click an item to delete it. Select an item below, then click empty space to place copies. Move / Esc stops placing.</p>`;
    this.entry.after(this.panel);
    this.slider = this.panel.querySelector('input[type="range"]')!;
    this.time = this.panel.querySelector('.editor-time')!;
    this.status = this.panel.querySelector('.editor-status')!;
    this.slider.addEventListener('input', () => {
      game.edit(Number(this.slider.value));
      this.hovered = null;
      this.tick();
    });
    this.panel.querySelector('[data-action="title"]')!.addEventListener('click', () => {
      game.audio.pause();
      game.keys.clear();
      game.mode = 'title';
      this.tick();
    });
    this.panel.querySelector('[data-action="test"]')!.addEventListener('click', () => {
      this.editTime = game.s.lastT;
      this.testing = true;
      game.keys.clear();
      game.start();
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
        this.hovered = null;
        game.edit();
        this.status.textContent = 'Using bundled default level';
      } catch (error) {
        console.error('Could not restore default level', error);
        this.status.textContent = 'Could not restore default level. Current layout is unchanged.';
      }
    });
    const palette = this.panel.querySelector('.editor-palette')!;
    const addTool = (name: string, kind: EnemyKind | null): HTMLButtonElement => {
      const button = document.createElement('button');
      button.type = 'button';
      button.setAttribute('aria-pressed', String(kind === null));
      button.addEventListener('click', () => {
        this.selected = kind;
        this.tools.forEach((tool) => tool.setAttribute('aria-pressed', String(tool === button)));
        canvas.focus();
      });
      const label = document.createElement('span');
      label.textContent = name;
      button.append(label);
      this.tools.push(button);
      palette.append(button);
      return button;
    };
    addTool('Move', null);
    const sheet = new Image();
    sheet.src = enemiesUrl;
    const props = new Image();
    props.src = propsUrl;
    const lamps = new Image(), lights = new Image(), ninjas = new Image();
    ninjas.src = ninjasUrl;
    const thugs = new Image(), passengers = new Image();
    thugs.src = thugsUrl; passengers.src = passengersUrl;
    lamps.src = lampsUrl; lights.src = lightsUrl;
    for (const kind of kinds) {
      const button = addTool(kind[0].toUpperCase() + kind.slice(1), kind);
      if (kind === 'tram') {
        const img = document.createElement('img');
        img.src = tramUrl;
        img.alt = '';
        button.prepend(img);
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
    canvas.addEventListener('contextmenu', (e) => {
      if (game.mode !== 'editor') return;
      e.preventDefault();
      const hit = this.hit(...this.point(e));
      if (!hit) return;
      game.level.splice(game.level.indexOf(hit), 1);
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
    if (e.code === 'Escape') {
      this.selected = null;
      this.tools.forEach((tool, i) => tool.setAttribute('aria-pressed', String(i === 0)));
    }
    return true;
  }

  private point(e: MouseEvent): [number, number] {
    const rect = canvas.getBoundingClientRect();
    return [
      ((e.clientX - rect.left) * canvas.offsetWidth / rect.width - canvas.clientLeft) / canvas.clientWidth * W,
      ((e.clientY - rect.top) * canvas.offsetHeight / rect.height - canvas.clientTop) / canvas.clientHeight * H,
    ];
  }

  private bounds(e: ScheduledEvent): { x: number; y: number; w: number; h: number } {
    const type = TYPES[e.type];
    return {
      x: enemyX(createEnemy(e), this.game.s.lastT) - (e.type === 'tram' ? 0 : isLamp(e.type) ? LAMP_CELL_W / 2 : type.w / 2),
      y: GROUND - (e.y ?? type.y) - type.h,
      w: isLamp(e.type) ? LAMP_CELL_W : type.w, h: type.h,
    };
  }

  private layeredEvents(): ScheduledEvent[] {
    return this.game.level.slice().sort((a, b) => itemLayer(a.type) - itemLayer(b.type));
  }

  private hit(x: number, y: number): ScheduledEvent | null {
    return this.layeredEvents().reverse().find((e) => {
      const b = this.bounds(e);
      return x >= b.x - 2 && x <= b.x + b.w + 2 && y >= b.y - 2 && y <= b.y + b.h + 2;
    }) ?? null;
  }

  private position(e: ScheduledEvent, x: number, base: number): void {
    e.rel = eventSpeed(e);
    e.arr = this.game.s.lastT + (x - PX) / e.rel;
    e.y = Math.round(Math.max(0, Math.min(GROUND - TYPES[e.type].h, GROUND - base)));
  }

  private pointerDown(e: PointerEvent): void {
    if (this.game.mode !== 'editor' || e.button !== 0 || this.drag) return;
    e.preventDefault();
    canvas.focus();
    const [x, y] = this.point(e), hit = this.hit(x, y);
    if (hit) {
      this.drag = {
        event: hit, dx: x - enemyX(createEnemy(hit), this.game.s.lastT),
        dy: y - (GROUND - (hit.y ?? TYPES[hit.type].y)), before: { ...hit }, pointer: e.pointerId,
      };
      canvas.setPointerCapture(e.pointerId);
    } else if (this.selected) {
      const event: ScheduledEvent = { type: this.selected, arr: this.game.s.lastT };
      this.position(event, x - (event.type === 'tram' ? TYPES.tram.w / 2 : 0), y + TYPES[event.type].h / 2);
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
      Object.assign(drag.event, drag.before);
    } else this.save();
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

  tick(): void {
    const mode = this.game.mode, editing = mode === 'editor';
    this.panel.hidden = !editing;
    this.entry.hidden = mode === 'loading' || editing || !(mode === 'title' || this.testing);
    this.entry.textContent = this.testing ? 'Back to editor' : 'Level editor';
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
    const events = this.layeredEvents();
    for (const event of events) {
      const b = this.bounds(event);
      if (b.x > W || b.x + b.w < 0) continue;
      const enemy = createEnemy(event);
      drawEnemy(enemy, enemyX(enemy, t), t);
    }
    drawLampLights(events.map(createEnemy), t);
    for (const event of events) {
      const b = this.bounds(event);
      if (b.x > W || b.x + b.w < 0) continue;
      ctx.strokeStyle = event === this.drag?.event || event === this.hovered ? '#ffe14a' : '#2bf0ff88';
      ctx.lineWidth = 0.5;
      ctx.strokeRect(b.x - 1, b.y - 1, b.w + 2, b.h + 2);
    }
  }
}
