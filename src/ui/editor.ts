import { GROUND, H, W, WIN_AT } from '../config';
import type { Game } from '../game';
import { loadDefaultLevel, parseLevel } from '../level';
import { RES, canvas, ctx, resetTransform } from '../render/draw';
import { drawScene } from '../render/scenes';
import { drawEnemy, drawLampLights } from '../render/sprites';
import { GHOST_IMAGES } from '../render/ghost';
import { STATION_IMAGES } from '../render/station-assets';
import { NEON_CARS, STATION_ASSETS, isNeonCar, isStationAsset, isWallPoster } from '../schedule';
import { NEON_CAR_IMAGES } from '../render/neon-cars';
import { NINJAS, NINJA_CELL_W, NINJA_CELL_H, THUGS, fighterRow, isFighter, isNinjaKind } from '../ninjas';
import { PASSENGERS, PASSENGER_CELL_W, PASSENGER_CELL_H, isPassenger } from '../passengers';
import { GHOSTS, isGhost, POWERUPS, isPowerup, BROKEN_BOARD, TREES, TREE_CELL_W, TREE_CELL_H, isTree, treeDepth, LAMPS, LAMP_CELL_W, LAMP_CELL_H, isLamp, PROPS, PROP_CELL_W, PROP_CELL_H, isProp, SHEET, TYPES, type EnemyKind, type ScheduledEvent } from '../schedule';
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
import { VALKYRIEN_CAMERA, VALKYRIEN_DEPTH, VALKYRIEN_ENTRY, VALKYRIEN_FLOOR, stationPlacement } from '../valkyrien';
import { drawValkyrien, drawValkyrienBalustrade, drawValkyrienDarkness, drawValkyrienHouse } from '../render/valkyrien';

const STORAGE_KEY = 'oslostil-level-v1';
const kinds = Object.keys(TYPES) as EnemyKind[];
const categories = ['Tunnel', 'Enemies', 'Power-ups', 'Tickets & coins', 'Lights', 'Props & platforms', 'Trees', 'Vehicles', 'Hazards'] as const;
type Category = (typeof categories)[number];

function itemCategory(kind: EnemyKind): Category {
  if (isGhost(kind) || isStationAsset(kind)) return 'Tunnel';
  if (isPowerup(kind) || kind === 'terminal') return 'Power-ups';
  if (isLamp(kind)) return 'Lights';
  if (isTree(kind)) return 'Trees';
  if (isProp(kind) || kind === 'board_broken') return 'Props & platforms';
  if (kind === 'tram' || isNeonCar(kind)) return 'Vehicles';
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
  private cameraY = 0;
  private showOutlines = true;
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
        <button type="button" data-action="valkyrien">Valkyrien</button>
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
      <p>Left/right arrows or scrolling move through time. Up/down arrows or Shift + scrolling pan vertically to view Valkyrien.</p>
      <p>Press O to toggle asset outlines for a clean level preview. Placement, dragging and deletion still work with outlines hidden.</p>
      <p>Broken boards crumble when landed on. Select a hopping glitch to edit its hop variant; tool settings also apply to new copies.</p>
      <p>Ghosts can only be placed inside Valkyrien. They glow green, damage on contact and start following after you pass them. Press Down/S at the square surface entrance to enter the station.</p>
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
    this.panel.querySelector('[data-action="valkyrien"]')!.addEventListener('click', () => {
      if (this.drag) return;
      game.edit(VALKYRIEN_ENTRY);
      this.cameraY = VALKYRIEN_CAMERA;
      this.hovered = null;
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
      const button = addTool(kind === 'ghost_bedsheet' ? 'Bedsheet ghost' : kind === 'ghost_conductor' ? 'Conductor ghost' : kind[0].toUpperCase() + kind.slice(1), kind);
      if (kind === 'tram') {
        const img = document.createElement('img');
        img.src = tramUrl;
        img.alt = '';
        button.prepend(img);
      } else if (isNeonCar(kind)) {
        const preview = document.createElement('canvas'), { sprite, light } = NEON_CAR_IMAGES[kind];
        const { w, h, light: { padding, cell: [lw, lh] } } = NEON_CARS[kind];
        preview.width = 64; preview.height = 40;
        const draw = () => {
          const c = preview.getContext('2d')!, scale = 56 / w;
          c.clearRect(0, 0, preview.width, preview.height);
          c.imageSmoothingEnabled = false;
          const x = (preview.width - w * scale) / 2, y = 31 - h * scale;
          if (light.complete && light.naturalWidth) c.drawImage(light, x - padding * scale, y - padding * scale, lw * scale, lh * scale);
          if (sprite.complete && sprite.naturalWidth) c.drawImage(sprite, x, y, w * scale, h * scale);
        };
        sprite.addEventListener('load', draw, { once: true });
        light.addEventListener('load', draw, { once: true });
        draw();
        button.prepend(preview);
      } else if (isStationAsset(kind)) {
        const preview = document.createElement('canvas'), image = STATION_IMAGES[kind];
        preview.width = 64; preview.height = 48;
        const draw = () => {
          const c = preview.getContext('2d')!, { w, h } = STATION_ASSETS[kind];
          c.imageSmoothingEnabled = false;
          c.clearRect(0, 0, 64, 48);
          c.drawImage(image, (64 - w) / 2, 48 - h, w, h);
        };
        if (image.complete && image.naturalWidth) draw();
        else image.addEventListener('load', draw, { once: true });
        button.prepend(preview);
      } else if (isGhost(kind)) {
        const GHOST = GHOSTS[kind];
        const { sprite: GHOST_IMAGE, light: GHOST_LIGHT_IMAGE } = GHOST_IMAGES[kind];
        const preview = document.createElement('canvas');
        preview.width = 64; preview.height = 40;
        const draw = () => {
          const c = preview.getContext('2d')!, [w, h] = GHOST.cell;
          c.imageSmoothingEnabled = false;
          c.clearRect(0, 0, preview.width, preview.height);
          c.save();
          const scale = Math.min(1, preview.height / GHOST.cell[1]);
          c.translate(preview.width / 2, preview.height);
          c.scale(scale, scale);
          if (GHOST_LIGHT_IMAGE.complete && GHOST_LIGHT_IMAGE.naturalWidth) {
            const [lw, lh] = GHOST.light.cell;
            c.drawImage(GHOST_LIGHT_IMAGE, 0, 0, lw, lh, -lw / 2, -h - GHOST.light.padding, lw, lh);
          }
          c.drawImage(GHOST_IMAGE, 0, GHOST.row * h, w, h, -w / 2, -h, w, h);
          c.restore();
        };
        if (GHOST_IMAGE.complete && GHOST_IMAGE.naturalWidth) draw();
        else GHOST_IMAGE.addEventListener('load', draw, { once: true });
        GHOST_LIGHT_IMAGE.addEventListener('load', draw, { once: true });
        button.prepend(preview);
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
      if (e.shiftKey) this.pan(delta * scale * 100);
      else this.scrub(delta * scale);
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
    if (e.code === 'KeyO' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      e.preventDefault();
      if (!e.repeat) this.showOutlines = !this.showOutlines;
      return true;
    }
    if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(e.code) && !e.ctrlKey && !e.metaKey && !e.altKey) {
      if (e.target instanceof HTMLElement && e.target.closest('select')) return true;
      e.preventDefault();
      if (e.code === 'ArrowUp' || e.code === 'ArrowDown') this.pan(e.code === 'ArrowDown' ? 10 : -10);
      else this.scrub(e.code === 'ArrowRight' ? 0.1 : -0.1);
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

  private pan(delta: number): void {
    if (this.drag || delta === 0) return;
    this.cameraY = Math.max(0, Math.min(VALKYRIEN_DEPTH, this.cameraY + delta));
    this.hovered = null;
  }

  private point(e: MouseEvent): [number, number] {
    const rect = canvas.getBoundingClientRect();
    return [
      ((e.clientX - rect.left) * canvas.offsetWidth / rect.width - canvas.clientLeft) / canvas.clientWidth * this.viewWidth - this.viewOffset,
      ((e.clientY - rect.top) * canvas.offsetHeight / rect.height - canvas.clientTop) / canvas.clientHeight * H + this.cameraY,
    ];
  }

  private get viewWidth(): number { return canvas.width / RES; }
  private get viewOffset(): number { return (this.viewWidth - W) / 2; }

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

  private position(e: ScheduledEvent, x: number, base: number): boolean {
    const underground = base > GROUND;
    if ((isGhost(e.type) || isStationAsset(e.type)) && !underground) return false;
    if (underground) {
      const clearance = isPowerup(e.type) ? 2 : e.type === 'ticket' ? 1 : 0;
      base = Math.min(VALKYRIEN_FLOOR - clearance, Math.round(base));
    }
    if (underground && !stationPlacement(x, base, TYPES[e.type].w, TYPES[e.type].h, this.game.s.lastT)) {
      return false;
    }
    if (isTree(e.type)) e.depth = treeDepth(e);
    e.rel = underground ? 145 : eventSpeed(e);
    e.y = Math.round(underground ? GROUND - base : Math.max(0, Math.min(GROUND - TYPES[e.type].h, GROUND - base)));
    e.arr = eventArrival(e, this.game.s.lastT, x);
    this.status.textContent = '';
    return true;
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
      if (y > VALKYRIEN_FLOOR) return;
      const event: ScheduledEvent = { type: this.selected, arr: this.game.s.lastT };
      if (event.type === 'blob_hop') event.hop = this.hopVariant();
      if (isTree(event.type)) event.depth = treeDepth({ ...event, arr: event.arr + x / W });
      const enemy = createEnemy(event);
      const lift = event.type === 'blob_hop' || isPowerup(event.type) ? enemyHeight(enemy, this.game.s.lastT) - enemy.y : 0;
      if (!this.position(event, x - (event.type === 'tram' ? TYPES.tram.w / 2 : 0), y + enemyBodyHeight(enemy, this.game.s.lastT) / 2 + lift)) return;
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
    ctx.translate(this.viewOffset, 0);
    ctx.translate(0, -this.cameraY);
    const events = this.layeredEvents();
    const drawEvent = (event: ScheduledEvent): void => {
      const b = this.bounds(event);
      const padding = isNeonCar(event.type) ? NEON_CARS[event.type].light.padding : 0;
      if (b.x - padding > W + this.viewOffset || b.x + b.w + padding < -this.viewOffset) return;
      const enemy = createEnemy(event);
      drawEnemy(enemy, enemyX(enemy, t), t);
    };
    drawScene(sectionAt(t).scene, t, this.game.s.bgx, 0, undefined, () => {
      for (const event of events) if (isTree(event.type)) drawEvent(event);
    });
    drawValkyrien(t, -this.viewOffset, W + this.viewOffset, () => {
      for (const event of events) if (isWallPoster(event.type)) drawEvent(event);
    });
    for (const event of events) if (!isTree(event.type) && !isWallPoster(event.type)) drawEvent(event);
    drawLampLights(events.map(createEnemy), t);
    drawValkyrienBalustrade(t, -this.viewOffset, W + this.viewOffset);
    drawValkyrienHouse(t, -this.viewOffset, W + this.viewOffset);
    drawValkyrienDarkness(t, () => {
      for (const event of events) {
        if (isWallPoster(event.type)) continue;
        const enemy = createEnemy(event);
        drawEnemy(enemy, enemyX(enemy, t), t);
      }
      drawValkyrienBalustrade(t, -this.viewOffset, W + this.viewOffset);
    }, events.map(createEnemy));
    if (!this.showOutlines) return;
    for (const event of events) {
      const b = this.bounds(event);
      if (b.x > W + this.viewOffset || b.x + b.w < -this.viewOffset) continue;
      ctx.strokeStyle = event === this.drag?.event || event === this.hovered ? '#ffe14a' : '#2bf0ff88';
      ctx.lineWidth = 0.5;
      ctx.strokeRect(b.x - 1, b.y - 1, b.w + 2, b.h + 2);
    }
  }
}
