#!/usr/bin/env python3
"""Health power-ups, one per part of the song. Drawn larger than life (not to girl scale) so they read
clearly at 1:1: about 20 px against the girls' 30 px.

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
    cv = Canvas(22, 28)
    top, bot = 9, 26
    for y in range(top, bot + 1):                     # cup tapers towards the base
        t = (y - top) / (bot - top)
        half = 8 - round(2 * t)
        for x in range(11 - half, 11 + half):
            k = (x - (11 - half)) / (2 * half)
            tone = 4 if k < .25 else (3 if k < .7 else 2)
            cv.set(x, y, 'cup', tone)
    for y in range(14, 22):                           # sleeve
        t = (y - top) / (bot - top)
        half = 8 - round(2 * t)
        for x in range(11 - half, 11 + half):
            k = (x - (11 - half)) / (2 * half)
            cv.set(x, y, 'sleeve', 4 if k < .25 else (3 if k < .7 else 2))
    heart = ['01010', '11111', '11111', '01110', '00100']    # a heart on the sleeve = health
    for j, row in enumerate(heart):
        for i, b in enumerate(row):
            if b == '1':
                cv.set(9 + i, 15 + j, 'heart', 3 if (i, j) != (1, 1) else 5)
    cv.rect(2, 7, 19, 8, 'lid', 3)                     # lid rim
    cv.hline(3, 18, 7, 'lid', 4)
    cv.rect(4, 5, 17, 6, 'lid', 2)                     # lid top
    cv.hline(5, 16, 5, 'lid', 4)
    cv.rect(12, 4, 14, 4, 'lid', 1)                    # sip hole bump
    for i, (sx, ph) in enumerate(((8, 0), (13, 1.7))):  # steam curls
        for y in range(0, 4):
            x = sx + round(1.4 * math.sin((y + f) * 1.4 + ph))
            if (y + f + i) % 4 != 3:
                cv.set(x, y, 'steam', 3 if y > 1 else 4)
    return finish(cv)


def cocoa_light(w, h, f, cx, cy):
    import tokyo_props as tp
    A = tp.field(w, h)
    tp.radial(A, cx, cy + 2, 14, 0.3)
    return A, rgb('#ffcf8a')


# --------------------------------------------------------------------------- neon heart


def neon_heart(f):
    cv = Canvas(28, 26)
    ox, oy = 2, 2
    HW, HH = 24, 22
    inside = set()
    for y in range(HH):
        for x in range(HW):
            u = (x + .5 - HW / 2) / (HW / 2) * 1.18
            v = -((y + .5) / HH * 2.5 - 1.3)
            if (u * u + v * v - 1) ** 3 - u * u * v ** 3 <= 0:
                inside.add((x, y))

    def edge(x, y):
        return any((x + dx, y + dy) not in inside for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    bright = [5, 4, 4, 3][f]
    for (x, y) in inside:
        if edge(x, y):
            cv.set(ox + x, oy + y, 'neonP', bright if (x + y) % 5 else 5)
        else:
            d = min(abs(x - 11.5), 9)
            inner = any((x + dx, y + dy) not in inside for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2))
            if inner:
                cv.set(ox + x, oy + y, 'neonP', 1)          # dark glass between tube and core
            else:
                cv.set(ox + x, oy + y, 'neonC', [4, 3, 3, 2][f] if d < 3 else [3, 2, 2, 1][f])
    for hx, hy in ((4, 3), (5, 2), (6, 2)):                 # hot spots on the tube
        if (hx, hy) in inside:
            cv.set(ox + hx, oy + hy, 'neonP', 5)
    cv.outline()
    cv.soften()
    if f == 0:
        sparkle(cv, ox + 19, oy + 3, 2)
    return cv


def neon_heart_light(w, h, f, cx, cy):
    import tokyo_props as tp
    A = tp.field(w, h)
    tp.radial(A, cx, cy, 16, [0.75, 0.6, 0.5, 0.42][f])
    return A, rgb('#ff5ab8')


# --------------------------------------------------------------------------- skolebolle
def bun(f):
    """3/4 view so it reads as a bun: a golden dome, a white icing cap with coconut, custard in the middle."""
    cv = Canvas(26, 22)
    cx = 13
    disc(cv, cx, 13, 12, 8, 'bun', lambda dx, dy, d: 5 if (dy < -.6 and dx < -.2) else (4 if dy < -.2 else (3 if dy < .5 else (2 if d < .9 else 1))))
    for x in range(cv.w):                              # flat bottom
        for y in range(19, cv.h):
            cv.clear(x, y)
    disc(cv, cx, 9.5, 8.5, 4.2, 'icing', lambda dx, dy, d: 4 if dy < -.35 else (3 if d < .75 else 2))
    for x, y in ((6, 11), (9, 13), (18, 12), (20, 11), (14, 13)):   # icing drips over the edge
        if cv.mat[y - 1][x] == 'icing':
            cv.set(x, y, 'icing', 2)
    disc(cv, cx, 8.6, 3.8, 1.9, 'custard', lambda dx, dy, d: 4 if dy < -.2 else (3 if d < .7 else 2))
    for x, y in ((7, 9), (18, 8), (10, 11), (16, 11), (8, 7), (19, 10), (12, 12)):   # coconut flakes
        if cv.mat[y][x] == 'icing':
            cv.c(x, y, rgb('#d8c8a8'), 'icing')
    finish(cv)
    sparkle(cv, [6, 20, 15, 9][f], [7, 6, 3, 5][f], f)
    return cv


# --------------------------------------------------------------------------- onigiri
def nigiri(f):
    """Salmon nigiri in 3/4 view: a block of rice under a draped slice of salmon with white fat lines."""
    cv = Canvas(28, 18)
    for y in range(8, 17):                            # rice block, rounded ends
        inset = {8: 2, 9: 1, 16: 1}.get(y, 0)
        for x in range(4 + inset, 24 - inset):
            k = (x - 4) / 20
            tone = 4 if (y < 11 and k < .7) else (3 if k < .8 else 2)
            cv.set(x, y, 'rice', tone)
    for x, y in ((7, 12), (11, 14), (15, 11), (19, 13), (21, 15), (9, 10), (17, 15)):   # grains
        cv.set(x, y, 'rice', 2)
    for x in range(1, 27):                            # the salmon slice drapes over the rice
        t = (x - 13.5) / 12.5
        ytop = 2 + round(4 * t * t)
        ybot = ytop + 6 - round(abs(t) * 1.5)
        for y in range(ytop, ybot + 1):
            tone = 4 if y <= ytop + 1 else (3 if y < ybot - 1 else 2)
            if (x - (y - ytop) // 2) % 5 == 0 and ytop < y < ybot:      # white fat lines, diagonal
                tone = 5
            cv.set(x, y, 'salmon', tone)
    finish(cv)
    sparkle(cv, [20, 6, 14, 24][f], [3, 6, 1, 7][f], f)
    return cv


def bubble_tea(f):
    """A clear cup of milk tea with dark tapioca pearls, a domed lid and a fat pink straw; the pearls drift."""
    cv = Canvas(22, 32)
    top, bot = 11, 30
    for y in range(top, bot + 1):                     # cup: milk tea inside clear plastic
        t = (y - top) / (bot - top)
        half = 8 - round(1.8 * t)
        for x in range(11 - half, 11 + half):
            k = (x - (11 - half)) / (2 * half)
            if x in (11 - half, 11 + half - 1):
                cv.set(x, y, 'plastic', 3 if k < .5 else 2)            # cup wall
            else:
                cv.set(x, y, 'tea', 4 if k < .3 else (3 if k < .75 else 2))
    for x in range(4, 18):                            # air gap under the lid
        if cv.mat[top][x] == 'tea':
            cv.set(x, top, 'plastic', 4)
    import random
    rnd = random.Random(5)
    pearls = [(x, y) for y in (28, 26, 24) for x in range(5 + (y // 2) % 2, 16, 3)]      # packed at the bottom
    pearls += [(rnd.randrange(5, 15), rnd.randrange(16, 22)) for _ in range(3)]          # a few floating up
    for i, (px, py) in enumerate(pearls):             # tapioca pearls, drifting a little each frame
        if py < 23:
            py -= f % 3
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            if cv.mat[py + dy][px + dx] == 'tea':
                cv.set(px + dx, py + dy, 'pearl', 2 if (dx, dy) != (0, 0) else 4)
    for y in range(7, 11):                            # domed lid
        half = {7: 4, 8: 6, 9: 7, 10: 8}[y]
        for x in range(11 - half, 11 + half):
            cv.set(x, y, 'plastic', 5 if (y == 8 and x < 9) else 4)
    cv.hline(2, 19, 10, 'plastic', 3)
    for y in range(3, 12):                            # fat pink straw, slightly tilted
        x = 13 + (11 - y) // 5
        cv.set(x - 1, y, 'straw', 4)
        cv.set(x, y, 'straw', 3)
        cv.set(x + 1, y, 'straw', 2)
    finish(cv)
    sparkle(cv, [4, 18, 6, 17][f], [14, 18, 24, 12][f], f)
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
