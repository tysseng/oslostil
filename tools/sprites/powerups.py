#!/usr/bin/env python3
"""Health power-ups, one per part of the song. Drawn larger than life (not to girl scale) so they read
clearly at 1:1: 13–20 px against the girls' 30 px (Joakim: 66 % of the first, larger version).

  cocoa       Sandvika (intro – level 2): a paper cup of hot chocolate with a heart on the sleeve; steam curls
  neon_heart  Neon Oslo: a pink neon-tube heart with a cyan core, pulses (light in powerups-light.png)
  bun         British Oslo: a «skolebolle» – sweet bun, white icing ring, custard middle, coconut; sparkles
  nigiri      Tokyoslo: salmon nigiri, a draped slice of salmon on rice (+2); sparkles
  bubble_tea  Tokyoslo: a clear cup of milk tea, tapioca pearls, domed lid, fat pink straw (+1); pearls drift

Sheet assets/sprites/powerups.png: one row per power-up, 4 frames each, cells 32 × 32, bottom-centred
(base on the bottom row, centre on x = 16). powerups-light.png: the same grid, a glow for every frame.
powerups.json: {name: {row, frames, fps, w, h, hearts}} (w × h = visible size = hitbox).
No brands or logos. Usage: python3 tools/sprites/powerups.py
"""
import json
import math
from pathlib import Path
from PIL import Image
from props import Canvas, RAMP, rgb, mix, field_image

CELL = 32
R = lambda *c: [rgb(x) for x in c]
RAMP.update({
    'cup':   R('#5a4a3a', '#a8998a', '#d8cdbf', '#f2ece2', '#fbf8f2', '#ffffff'),
    'lid':   R('#1a1418', '#2c2228', '#3e3238', '#54464c', '#6e6066', '#8e8086'),
    'sleeve': R('#3a1a0c', '#6a3418', '#8e4a24', '#b06232', '#cc8048', '#e8a46a'),
    'choc':  R('#1e0c06', '#3a1a0c', '#5a2c14', '#7a3e1e', '#9a5630', '#c07a4e'),
    'steam': R('#8a94a8', '#b8c2d2', '#d8e0ea', '#eef2f8', '#f8fbff', '#ffffff'),
    'heart': R('#5a0a24', '#a8124a', '#e0206a', '#ff4a8e', '#ff8ab6', '#ffd0e2'),
    'neonP': R('#3a0420', '#8a0c4a', '#e0207a', '#ff4aa8', '#ff9ad0', '#ffe6f4'),
    'neonC': R('#04262e', '#0a5a68', '#14a0b4', '#30e0f0', '#9af6ff', '#ffffff'),
    'bun':   R('#4a2208', '#8a4414', '#b8641e', '#d8862c', '#ecaa48', '#f8d080'),
    'icing': R('#8a8a96', '#c4c6d0', '#e4e6ee', '#f6f7fb', '#ffffff', '#ffffff'),
    'custard': R('#7a5a08', '#c09018', '#e8b828', '#ffd84a', '#ffe98a', '#fff6c8'),
    'rice':  R('#7a7c86', '#b4b8c4', '#d8dce6', '#eef0f6', '#fafbff', '#ffffff'),
    'nori':  R('#04100a', '#0a1e14', '#12301e', '#1a4228', '#26583a', '#3a7450'),
    'salmon': R('#5a1a08', '#a83a14', '#e0602a', '#ff7e3e', '#ffa56a', '#ffe2cc'),
    'plastic': R('#6a7484', '#a8b4c4', '#cbd6e2', '#e2eaf2', '#f2f6fa', '#ffffff'),
    'tea':   R('#4a3020', '#8a6440', '#b08a60', '#ccaa80', '#e0c49e', '#f2e2c8'),
    'pearl': R('#08060a', '#140e14', '#22181e', '#30222a', '#4a3640', '#6a5260'),
    'straw': R('#5a0a34', '#a8125e', '#e0207e', '#ff4aa0', '#ff8ac4', '#ffd0e6'),
})
WHITE = rgb('#ffffff')
SPARK = [rgb('#ffffff'), rgb('#fff3b0')]


def finish(cv):
    cv.outline()
    cv.soften()
    return cv


def disc(cv, cx, cy, rx, ry, mat, tone_fn):
    for y in range(cv.h):
        for x in range(cv.w):
            dx, dy = (x + .5 - cx) / rx, (y + .5 - cy) / ry
            d = dx * dx + dy * dy
            if d <= 1:
                cv.set(x, y, mat, tone_fn(dx, dy, d))


def sparkle(cv, x, y, f):
    """A 4-step twinkle drawn after the outline (bare bright pixels)."""
    s = [(0,), (0, 1), (0, 1, 2), (0, 1)][f % 4]
    for r in s:
        for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
            cv.c(x + dx, y + dy, SPARK[0] if r == 0 else SPARK[1], 'icing')


# --------------------------------------------------------------------------- hot chocolate
def cocoa(f):
    cv = Canvas(16, 20)
    top, bot = 7, 18
    for y in range(top, bot + 1):                     # cup tapers towards the base
        half = 5 - (y - top) * 1.2 / (bot - top)
        x0, x1 = round(8 - half), round(8 + half)
        for x in range(x0, x1):
            k = (x - x0) / max(1, x1 - x0)
            mat = 'sleeve' if 10 <= y <= 14 else 'cup'
            cv.set(x, y, mat, 4 if k < .25 else (3 if k < .7 else 2))
    for j, row in enumerate(['101', '111', '010']):   # heart on the sleeve = health
        for i, b in enumerate(row):
            if b == '1':
                cv.set(6 + i, 11 + j, 'heart', 4 if (i, j) == (0, 0) else 3)
    cv.rect(2, 5, 13, 6, 'lid', 3)                     # lid rim
    cv.hline(3, 12, 5, 'lid', 4)
    cv.rect(4, 4, 11, 4, 'lid', 2)                     # lid top
    cv.set(9, 3, 'lid', 1)
    for i, (sx, ph) in enumerate(((6, 0), (10, 1.7))):  # steam curls
        for y in range(1, 3):
            x = sx + round(math.sin((y + f) * 1.5 + ph))
            if (y + f + i) % 3 != 2:
                cv.set(x, y, 'steam', 3 if y > 0 else 4)
    return finish(cv)


def cocoa_light(w, h, f, cx, cy):
    import tokyo_props as tp
    A = tp.field(w, h)
    tp.radial(A, cx, cy + 2, 10, 0.3)
    return A, rgb('#ffcf8a')


# --------------------------------------------------------------------------- neon heart
def neon_heart(f):
    cv = Canvas(20, 18)
    ox, oy = 2, 2
    HW, HH = 16, 14
    inside = set()
    for y in range(HH):
        for x in range(HW):
            u = (x + .5 - HW / 2) / (HW / 2) * 1.18
            v = -((y + .5) / HH * 2.5 - 1.3)
            if (u * u + v * v - 1) ** 3 - u * u * v ** 3 <= 0:
                inside.add((x, y))

    def ring(x, y, r):
        return any((x + dx, y + dy) not in inside for dx in range(-r, r + 1) for dy in range(-r, r + 1))
    bright = [5, 4, 4, 3][f]
    for (x, y) in inside:
        if ring(x, y, 1) and any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            cv.set(ox + x, oy + y, 'neonP', bright)             # the tube
        elif ring(x, y, 1):
            cv.set(ox + x, oy + y, 'neonP', 1)                  # dark glass
        else:
            cv.set(ox + x, oy + y, 'neonC', [4, 3, 3, 2][f])    # glowing core
    for hx, hy in ((3, 2), (4, 1)):
        if (hx, hy) in inside:
            cv.set(ox + hx, oy + hy, 'neonP', 5)
    cv.outline()
    cv.soften()
    if f == 0:
        sparkle(cv, ox + 12, oy + 2, 1)
    return cv


def neon_heart_light(w, h, f, cx, cy):
    import tokyo_props as tp
    A = tp.field(w, h)
    tp.radial(A, cx, cy, 12, [0.7, 0.55, 0.45, 0.38][f])
    return A, rgb('#ff5ab8')


# --------------------------------------------------------------------------- skolebolle
def bun(f):
    """3/4 view so it reads as a bun: a golden dome, a white icing cap with coconut, custard in the middle."""
    cv = Canvas(19, 15)
    cx = 9.5
    disc(cv, cx, 8.6, 8.2, 5.6, 'bun', lambda dx, dy, d: 5 if (dy < -.6 and dx < -.2) else (4 if dy < -.2 else (3 if dy < .5 else 2)))
    for x in range(cv.w):                              # flat bottom
        for y in range(13, cv.h):
            cv.clear(x, y)
    disc(cv, cx, 6.2, 5.9, 2.9, 'icing', lambda dx, dy, d: 4 if dy < -.3 else (3 if d < .75 else 2))
    for x, y in ((5, 8), (13, 8)):                     # icing drips
        if cv.mat[y - 1][x] == 'icing':
            cv.set(x, y, 'icing', 2)
    disc(cv, cx, 5.6, 2.6, 1.3, 'custard', lambda dx, dy, d: 4 if dy < 0 else 3)
    for x, y in ((6, 6), (13, 5), (7, 7), (12, 7)):    # coconut flakes
        if cv.mat[y][x] == 'icing':
            cv.c(x, y, rgb('#d8c8a8'), 'icing')
    finish(cv)
    sparkle(cv, [5, 14, 11, 7][f], [4, 4, 2, 3][f], f % 2)
    return cv


# --------------------------------------------------------------------------- salmon nigiri
def nigiri(f):
    """Salmon nigiri in 3/4 view: a block of rice under a draped slice of salmon with white fat lines."""
    cv = Canvas(21, 13)
    for y in range(6, 12):                            # rice block, rounded ends
        inset = {6: 1, 11: 1}.get(y, 0)
        for x in range(4 + inset, 17 - inset):
            k = (x - 4) / 13
            cv.set(x, y, 'rice', 4 if (y < 8 and k < .7) else (3 if k < .8 else 2))
    for x, y in ((6, 9), (10, 10), (14, 8)):
        cv.set(x, y, 'rice', 2)
    for x in range(2, 19):                            # the salmon slice drapes over the rice
        t = (x - 10) / 8
        ytop = 1 + round(3 * t * t)
        ybot = ytop + 4 - round(abs(t))
        for y in range(ytop, ybot + 1):
            tone = 4 if y == ytop else (3 if y < ybot else 2)
            if (x - (y - ytop) // 2) % 4 == 0 and ytop < y < ybot:      # white fat lines, diagonal
                tone = 5
            cv.set(x, y, 'salmon', tone)
    finish(cv)
    sparkle(cv, [14, 5, 10, 17][f], [1, 3, 0, 4][f], f % 2)
    return cv


# --------------------------------------------------------------------------- bubble tea
def bubble_tea(f):
    """A clear cup of milk tea with dark tapioca pearls, a domed lid and a fat pink straw; the pearls drift."""
    cv = Canvas(15, 22)
    top, bot = 8, 20
    for y in range(top, bot + 1):
        half = 5.5 - 1.2 * (y - top) / (bot - top)
        x0, x1 = round(7.5 - half), round(7.5 + half)
        for x in range(x0, x1):
            k = (x - x0) / max(1, x1 - x0)
            if x in (x0, x1 - 1):
                cv.set(x, y, 'plastic', 3 if k < .5 else 2)            # cup wall
            else:
                cv.set(x, y, 'tea', 4 if k < .3 else (3 if k < .75 else 2))
    pearls = [(x, y) for y in (19, 17) for x in range(3 + (y // 2) % 2, 12, 2)]          # packed at the bottom
    pearls += [(5, 13), (9, 12)]                                                           # a few floating up
    for i, (px, py) in enumerate(pearls):
        if py < 16:
            py -= f % 2
        if cv.mat[py][px] == 'tea':
            cv.set(px, py, 'pearl', 3 if (px + py) % 2 else 2)
    for y, half in ((5, 3), (6, 5), (7, 6)):          # domed lid
        for x in range(round(7.5 - half), round(7.5 + half)):
            cv.set(x, y, 'plastic', 5 if (y == 6 and x < 6) else 4)
    for y in range(2, 8):                             # fat pink straw, slightly tilted
        x = 9 + (8 - y) // 4
        cv.set(x - 1, y, 'straw', 4)
        cv.set(x, y, 'straw', 2)
    finish(cv)
    sparkle(cv, [3, 12, 4, 11][f], [11, 14, 16, 10][f], f % 2)
    return cv


ITEMS = [  # name, draw(frame), fps, hearts, light(w, h, frame) or None
    ('cocoa', cocoa, 6, 1, cocoa_light),
    ('neon_heart', neon_heart, 8, 1, neon_heart_light),
    ('bun', bun, 6, 1, None),
    ('nigiri', nigiri, 6, 2, None),
    ('bubble_tea', bubble_tea, 6, 1, None),
]
FRAMES = 4


def main():
    root = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
    sheet = Image.new('RGBA', (CELL * FRAMES, CELL * len(ITEMS)), (0, 0, 0, 0))
    light = Image.new('RGBA', sheet.size, (0, 0, 0, 0))
    meta = {}
    for row, (name, fn, fps, hearts, lf) in enumerate(ITEMS):
        ims = [fn(f).image() for f in range(FRAMES)]
        boxes = [im.getbbox() for im in ims]
        box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        w, h = box[2] - box[0], box[3] - box[1]
        ox, oy = CELL // 2 - w // 2 - box[0], CELL - h - box[1]
        for c, im in enumerate(ims):
            sheet.alpha_composite(im, (c * CELL + ox, row * CELL + oy))
            if lf:
                A, col = lf(CELL, CELL, c, CELL / 2, CELL - h / 2)     # glow on the whole cell, centred on the item
                light.alpha_composite(field_image(A, col, blur=1.8), (c * CELL, row * CELL))
        meta[name] = {'row': row, 'frames': FRAMES, 'fps': fps, 'w': w, 'h': h, 'hearts': hearts}
    sheet.save(root / 'powerups.png')
    light.save(root / 'powerups-light.png')
    (root / 'powerups.json').write_text(json.dumps(meta, indent=1) + '\n')
    for n, m in meta.items():
        print(f'  {n:10s} {m["w"]:2d} × {m["h"]:2d}  +{m["hearts"]}')


if __name__ == '__main__':
    main()
