#!/usr/bin/env python3
"""Pixel-art fire for the burning trams in Kollektivkaos: animated flames and smoke, 1:1 game pixels.

Sheet layout (assets/sprites/fire.png + fire.json): one row per sprite, frames left to right in
cells of CELL × CELL, each sprite bottom-centred in its cell (the flame's base on the bottom row).
  big    20 × 30, 8 frames   flames out of a window or through the roof
  small  12 × 18, 8 frames
  smoke  16 × 16, 8 frames   a puff that rises and fades (the game moves it up as well)
Usage: python3 tools/sprites/fire.py
"""
import json
import math
import random
from pathlib import Path
from PIL import Image

CELL = 32
FIRE = [(0xff, 0xf6, 0xc8), (0xff, 0xd8, 0x4a), (0xff, 0x8a, 0x1a), (0xe2, 0x40, 0x1a), (0x8a, 0x18, 0x10)]
SMOKE = [(0x5a, 0x50, 0x56), (0x46, 0x3e, 0x44), (0x34, 0x2e, 0x34)]
SPRITES = {'big': (20, 30), 'small': (12, 18), 'smoke': (16, 16)}
FRAMES = 8


def flame(w, h, f, seed):
    """One frame of a flame: a flickering teardrop with a hot core and a few loose tongues."""
    im = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    r = random.Random(seed * 100 + f)
    ph = f / FRAMES * 2 * math.pi
    cx0 = CELL / 2
    for y in range(h):
        t = y / (h - 1)                                    # 0 at the base, 1 at the tip
        half = w / 2 * (1 - t ** 1.25) * (0.85 + 0.15 * math.sin(ph * 2 + t * 6)) + 0.6
        sway = math.sin(ph + t * 4.5) * 2.2 * t + math.sin(ph * 3 + t * 9) * 0.7 * t
        cx = cx0 + sway
        for x in range(int(cx - half - 1), int(cx + half + 2)):
            d = abs(x + 0.5 - cx) / max(half, 0.6)
            if d > 1:
                continue
            heat = (1 - d) * (1 - t * 0.85)                 # hottest at the centre of the base
            heat += r.uniform(-0.08, 0.08)
            c = FIRE[0] if heat > 0.7 else FIRE[1] if heat > 0.45 else FIRE[2] if heat > 0.25 else FIRE[3] if heat > 0.1 else FIRE[4]
            im.putpixel((x, CELL - 1 - y), c + (255,))
    for _ in range(2):                                     # loose tongues above the tip
        tx = int(cx0 + math.sin(ph + r.random() * 6) * w / 4)
        ty = CELL - 1 - h - r.randint(0, 3)
        for k in range(r.randint(1, 3)):
            if 0 <= ty - k < CELL:
                im.putpixel((tx, ty - k), FIRE[2 + (k > 0)] + (255,))
    return im


def smoke(w, h, f):
    im = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    t = f / (FRAMES - 1)
    rad = 3 + t * (w / 2 - 3)
    cx, cy = CELL / 2, CELL - 1 - rad - t * 4
    alpha = int(200 * (1 - t) + 40)
    for y in range(CELL):
        for x in range(CELL):
            for ox, oy, rr in ((0, 0, rad), (-rad * .5, rad * .3, rad * .7), (rad * .5, rad * .2, rad * .6)):
                d = math.hypot(x + .5 - (cx + ox), y + .5 - (cy + oy))
                if d <= rr:
                    shade = SMOKE[0] if d < rr * .5 and y < cy else SMOKE[1] if d < rr * .85 else SMOKE[2]
                    im.putpixel((x, y), shade + (alpha,))
                    break
    return im


def main():
    root = Path(__file__).resolve().parents[2]
    names = list(SPRITES)
    sheet = Image.new('RGBA', (CELL * FRAMES, CELL * len(names)), (0, 0, 0, 0))
    meta = {}
    for row, name in enumerate(names):
        w, h = SPRITES[name]
        for f in range(FRAMES):
            cell = smoke(w, h, f) if name == 'smoke' else flame(w, h, f, row + 1)
            sheet.alpha_composite(cell, (f * CELL, row * CELL))
        meta[name] = {'row': row, 'frames': FRAMES, 'fps': 6 if name == 'smoke' else 12, 'w': w, 'h': h}
    out = root / 'assets' / 'sprites' / 'fire.png'
    sheet.save(out)
    (out.with_suffix('.json')).write_text(json.dumps({'cell': CELL, 'sprites': meta}, indent=1) + '\n')
    print(out, sheet.size)


if __name__ == '__main__':
    main()
