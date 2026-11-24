#!/usr/bin/env python3
"""Pixel-art street props at «girl scale» (the girls are 30 px tall, about 19 px per metre).

Front views only, drawn directly on the pixel grid (never scaled), in the girls' style:
dark outlines tinted per material, 3–4 tone shading, and hand-placed anti-aliasing pixels
(in-between tones on rounded corners and curves), all opaque. References: inspiration/assets/.

Props (visible height incl. outline):
  trash      round slatted street bin, dark green ......... 17 px  (≈ 55 % of a girl)
  recycling  single red textile bin, no logo .............. 36 px
  phonebooth red Oslo «TELEFON» kiosk ..................... 44 px
  kiosk      freestanding news kiosk (after narvesen 3) .... 60 px  (≈ 2 × a girl)

Sheet: one prop per row, one column per frame, CELL_W × CELL_H cells, each prop bottom-centred
(base on the bottom row, centre on x = CELL_W // 2).
Writes assets/sprites/props.png (one column per animation frame), assets/sprites/props-light.png
(the same grid, column 0: light to draw in front of the characters) and assets/sprites/props.json.
The Tokyoslo props are drawn in tools/sprites/tokyo_props.py. top 0 = not standable.
({name: {row, frames, fps, w, h, top}}; w × h is the visible size, top is the height of the
walkable top surface above the base, in px).
Usage: python3 tools/sprites/props.py
"""
import json
from pathlib import Path
from PIL import Image

CELL_W, CELL_H = 112, 64


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t=0.5):
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


# material ramps: [outline, dark, shade, base, light, highlight]
RAMP = {
    'red':    ['#3c0b14', '#7a1420', '#b51f26', '#e0322c', '#ff6450', '#ffb0a0'],
    'steel':  ['#262a38', '#4a5163', '#7d8596', '#aab2bf', '#d3d9e1', '#f4f7fa'],
    'glass':  ['#1f2f45', '#3c5674', '#6489ad', '#97bcd8', '#c8e2f2', '#ffffff'],
    'dark':   ['#121522', '#1e2232', '#2b3043', '#3a4058', '#50587a', '#6a74a0'],
    'green':  ['#0a2219', '#12382a', '#1c4e3a', '#28684c', '#3f8a66', '#7cc29a'],
    'kgreen': ['#0b2a1c', '#174a32', '#226646', '#2f845a', '#4aa874', '#8ed6a6'],
    'cream':  ['#3e3428', '#8c7c62', '#c9b897', '#eee2c6', '#fbf4e2', '#ffffff'],
    'navy':   ['#101438', '#1c2468', '#28338f', '#3b48b4', '#6a7ae0', '#c8d0ff'],
    'warm':   ['#4a2a10', '#9a5a1a', '#d98a2a', '#ffc35a', '#ffe08a', '#fff6cc'],
    'rust':   ['#24140e', '#3e2216', '#5a3220', '#7a4a2e', '#9a6640', '#c08a5a'],
    'paper':  ['#5a4a20', '#b89a3a', '#e0c050', '#ffe170', '#fff3b0', '#ffffff'],
}
RAMP = {k: [rgb(c) for c in v] for k, v in RAMP.items()}
MAG = [rgb(c) for c in ('#ff4f8b', '#ffd84a', '#2bc8b0', '#ff8a2a', '#8f6ae8', '#5fb0ff', '#f4f4f4', '#e0322c')]


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[None] * w for _ in range(h)]    # (r, g, b) or None
        self.mat = [[None] * w for _ in range(h)]   # material name, for auto outline

    def set(self, x, y, mat, tone):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = RAMP[mat][tone] if isinstance(tone, int) else tone
            self.mat[y][x] = mat

    def c(self, x, y, col, mat='dark'):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = col
            self.mat[y][x] = mat

    def rect(self, x0, y0, x1, y1, mat, tone):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, mat, tone)

    def hline(self, x0, x1, y, mat, tone):
        self.rect(x0, y, x1, y, mat, tone)

    def vline(self, x, y0, y1, mat, tone):
        self.rect(x, y0, x, y1, mat, tone)

    def clear(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = None
            self.mat[y][x] = None

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < self.w and 0 <= y < self.h else None

    def outline(self):
        """1 px outline around the silhouette, in the outline tone of the neighbouring material."""
        add = []
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x] is not None:
                    continue
                for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and self.px[ny][nx] is not None:
                        add.append((x, y, self.mat[ny][nx]))
                        break
        for x, y, m in add:
            self.set(x, y, m, 0)

    def soften(self):
        """Hand-style AA on the silhouette: an outline pixel on an outer corner (open on two
        adjacent sides) becomes a tone between the outline and the fill it wraps."""
        ch = []
        for y in range(self.h):
            for x in range(self.w):
                p = self.px[y][x]
                m = self.mat[y][x]
                if p is None or p != RAMP[m][0]:
                    continue
                o = lambda dx, dy: self.get(x + dx, y + dy) is None
                if (o(-1, 0) or o(1, 0)) and (o(0, -1) or o(0, 1)) and not (o(-1, 0) and o(1, 0)) and not (o(0, -1) and o(0, 1)):
                    ch.append((x, y, mix(RAMP[m][0], RAMP[m][2], 0.45), m))
        for x, y, col, m in ch:
            self.c(x, y, col, m)

    def image(self):
        im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x] is not None:
                    im.putpixel((x, y), self.px[y][x] + (255,))
        return im


# 3 × 5 pixel font for the few real letters
FONT = {
    'K': ['101', '110', '100', '110', '101'], 'I': ['111', '010', '010', '010', '111'],
    'O': ['010', '101', '101', '101', '010'], 'S': ['011', '100', '010', '001', '110'],
}


def text(cv, s, x, y, col):
    for ch in s:
        for j, row in enumerate(FONT[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    cv.c(x + i, y + j, col)
        x += 4


def scribble(cv, x0, x1, y, col, seed, gap_col=None):
    """A line of dots and dashes that reads as small writing."""
    import random
    r = random.Random(seed)
    x = x0
    while x <= x1:
        n = r.choice((1, 2, 2, 3, 4))
        for i in range(n):
            if x + i <= x1:
                cv.c(x + i, y, col)
        x += n + 1


# --------------------------------------------------------------------------- trash
def trash():
    W, H = 15, 17
    cv = Canvas(W, H)
    # body: slightly tapered cylinder, y 4..15, x 2..12 at top, 3..11 at bottom
    for y in range(4, 14):
        inset = 1 if y >= 9 else 0
        x0, x1 = 2 + inset, 12 - inset
        for x in range(x0, x1 + 1):
            cv.set(x, y, 'green', 1)                        # gaps between slats
        # vertical slats on even columns, shaded as a cylinder: light left of centre, dark at the sides
        for x in range(x0, x1 + 1):
            if (x - 2) % 2 == 0:
                rel = (x - x0) / max(1, x1 - x0)
                tone = 2 if rel < 0.1 or rel > 0.85 else 5 if 0.2 <= rel < 0.35 else 4 if rel < 0.5 else 3
                cv.set(x, y, 'green', tone)
    # inside opening seen through the top slats
    cv.hline(3, 11, 4, 'green', 0)
    # mid band (hoop)
    cv.hline(2, 12, 8, 'green', 3); cv.set(4, 8, 'green', 4); cv.set(5, 8, 'green', 5); cv.set(11, 8, 'green', 2); cv.set(12, 8, 'green', 2)
    # flared rim y 1..3: wider than the body
    cv.hline(1, 13, 3, 'green', 2)
    cv.hline(1, 13, 2, 'green', 3)
    cv.hline(2, 12, 1, 'green', 4)
    for x in (4, 5, 6):
        cv.set(x, 1, 'green', 5)
    cv.set(12, 2, 'green', 2); cv.set(13, 2, 'green', 1); cv.set(13, 3, 'green', 1); cv.set(12, 3, 'green', 1)
    # dark base ring
    cv.hline(3, 11, 14, 'rust', 2); cv.set(4, 14, 'rust', 3); cv.set(5, 14, 'rust', 3); cv.set(11, 14, 'rust', 1)
    cv.hline(4, 10, 15, 'rust', 1)
    cv.outline()
    cv.soften()
    # manual AA where the rim flares out over the body
    cv.c(1, 4, mix(RAMP['green'][0], RAMP['green'][1]), 'green'); cv.c(13, 4, mix(RAMP['green'][0], RAMP['green'][1]), 'green')
    cv.c(0, 2, mix(RAMP['green'][0], RAMP['green'][2], 0.35), 'green'); cv.c(14, 2, mix(RAMP['green'][0], RAMP['green'][2], 0.25), 'green')
    return cv


# --------------------------------------------------------------------------- recycling
def recycling():
    W, H = 24, 36
    cv = Canvas(W, H)
    L, R = 1, 22
    # hood y 1..10: rounded top, sloped look by shading
    cv.rect(L + 1, 1, R - 1, 1, 'red', 4)
    cv.rect(L, 2, R, 10, 'red', 3)
    cv.hline(L, R, 2, 'red', 4)
    for x in range(L + 2, L + 8):
        cv.set(x, 1, 'red', 5)
    cv.vline(L, 2, 10, 'red', 4); cv.vline(R, 2, 10, 'red', 2)
    # chute opening with a dark interior and a black label strip above it
    cv.rect(L + 3, 3, R - 3, 4, 'dark', 2)
    scribble(cv, L + 4, R - 6, 3, RAMP['cream'][4], 3)          # «tusen takk» as dots
    cv.rect(L + 3, 6, R - 3, 9, 'dark', 0)
    cv.hline(L + 3, R - 3, 6, 'red', 1)                          # flap edge in shadow
    cv.hline(L + 4, R - 4, 9, 'dark', 1)
    # lip
    cv.hline(L, R, 11, 'red', 1)
    # body y 12..33
    cv.rect(L, 12, R, 31, 'red', 3)
    cv.vline(L, 12, 31, 'red', 4); cv.vline(L + 1, 12, 31, 'red', 4); cv.vline(R, 12, 31, 'red', 2)
    # dark graphic panel with dotted writing and a white plate where the logo was
    cv.rect(L + 3, 13, R - 3, 29, 'dark', 1)
    cv.vline(R - 3, 13, 29, 'dark', 0)
    cv.hline(L + 3, R - 3, 13, 'dark', 2)
    # little shirt icon
    sx, sy = L + 4, 15
    shirt = ['1.1', '111', '.1.']
    for j, row in enumerate(['11.11', '11111', '.111.', '.111.']):
        for i, b in enumerate(row):
            if b == '1':
                cv.c(sx + i, sy + j, RAMP['warm'][3])
    scribble(cv, L + 10, R - 5, 15, RAMP['cream'][4], 7)
    scribble(cv, L + 10, R - 6, 17, RAMP['cream'][3], 8)
    scribble(cv, L + 4, R - 5, 19, RAMP['cream'][2], 9)
    # white plate (no cross, no name): grey dots as writing
    cv.rect(L + 5, 21, R - 5, 25, 'cream', 4)
    cv.hline(L + 5, R - 5, 25, 'cream', 2)
    cv.vline(R - 5, 21, 25, 'cream', 2)
    scribble(cv, L + 7, R - 7, 23, RAMP['steel'][1], 4)
    scribble(cv, L + 4, R - 5, 27, RAMP['cream'][2], 12)
    # base rim and legs
    cv.hline(L, R, 31, 'red', 1)
    cv.hline(L, R, 32, 'dark', 2)
    cv.rect(L + 1, 33, L + 2, 34, 'dark', 1); cv.rect(R - 2, 33, R - 1, 34, 'dark', 1)
    cv.set(L + 1, 33, 'dark', 3)
    cv.outline()
    cv.soften()
    # manual AA on the rounded hood corners
    cv.c(L, 1, mix(RAMP['red'][0], RAMP['red'][3], 0.4), 'red'); cv.c(R, 1, mix(RAMP['red'][0], RAMP['red'][2], 0.3), 'red')
    cv.c(L + 1, 1, RAMP['red'][3], 'red'); cv.c(R - 1, 1, RAMP['red'][2], 'red')
    return cv


# --------------------------------------------------------------------------- phone booth
def phonebooth():
    W, H = 21, 44
    cv = Canvas(W, H)
    L, R = 2, 18
    # roof cap: grey metal plate, wider than the box
    cv.rect(L - 1, 1, R + 1, 2, 'steel', 3)
    cv.hline(L, R, 1, 'steel', 4)
    for x in range(L + 1, L + 6):
        cv.set(x, 1, 'steel', 5)
    cv.hline(L - 1, R + 1, 3, 'steel', 1)
    # red body
    cv.rect(L, 4, R, 40, 'red', 3)
    cv.vline(L, 4, 40, 'red', 4); cv.vline(L + 1, 4, 40, 'red', 4)
    cv.vline(R, 4, 40, 'red', 2); cv.vline(R - 1, 4, 40, 'red', 2)
    # header with «TELEFON» as pale dots
    cv.hline(L + 2, R - 2, 4, 'red', 4)
    scribble(cv, L + 3, R - 3, 6, RAMP['cream'][4], 21)
    cv.hline(L + 2, R - 2, 8, 'red', 1)
    # door: steel frame, glass in the upper part, louvres below
    dx0, dx1 = L + 2, R - 2
    cv.rect(dx0, 9, dx1, 38, 'steel', 2)
    cv.vline(dx0, 9, 38, 'steel', 4); cv.vline(dx1, 9, 38, 'steel', 1)
    cv.hline(dx0, dx1, 9, 'steel', 4)
    # glass y 10..27
    gx0, gx1 = dx0 + 1, dx1 - 1
    cv.rect(gx0, 10, gx1, 27, 'glass', 2)
    cv.rect(gx0, 22, gx1, 27, 'glass', 1)
    cv.rect(gx0, 10, gx1, 11, 'glass', 3)
    # the pay phone inside, a red box with a dark handset
    cv.rect(gx0 + 4, 15, gx0 + 8, 21, 'red', 2)
    cv.rect(gx0 + 5, 16, gx0 + 7, 18, 'dark', 3)
    cv.set(gx0 + 4, 15, 'red', 3); cv.set(gx0 + 5, 15, 'red', 3)
    cv.vline(gx0 + 3, 16, 20, 'dark', 1)
    cv.set(gx0 + 6, 20, 'warm', 3)
    # diagonal reflection streaks on the glass (hand-AA: bright core with mid-tone neighbours)
    for i in range(7):
        x, y = gx0 + 1 + i // 2, 25 - i * 2
        cv.set(x, y, 'glass', 4); cv.set(x, y - 1, 'glass', 3)
    for i in range(4):
        x, y = gx0 + 2 + i // 2, 27 - i * 2
        cv.set(x, y, 'glass', 3)
    cv.set(gx1, 12, 'glass', 3); cv.set(gx1 - 1, 13, 'glass', 2)
    # door handle
    cv.vline(dx1 - 1, 18, 21, 'steel', 5); cv.vline(dx1 - 2, 18, 21, 'steel', 0)
    # louvres y 29..39
    cv.hline(gx0, gx1, 28, 'steel', 1)
    for y in range(29, 38):
        cv.hline(gx0, gx1, y, 'steel', 4 if (y - 29) % 2 == 0 else 1)
        if (y - 29) % 2 == 0:
            cv.set(gx0, y, 'steel', 5); cv.set(gx1, y, 'steel', 2)
    # plinth and feet
    cv.hline(L, R, 41, 'steel', 1)
    cv.rect(L + 1, 42, L + 2, 42, 'dark', 1); cv.rect(R - 2, 42, R - 1, 42, 'dark', 1)
    cv.outline()
    cv.soften()
    # roof cap overhang AA
    cv.c(L - 1, 4, mix(RAMP['steel'][0], RAMP['red'][0]), 'red'); cv.c(R + 1, 4, mix(RAMP['steel'][0], RAMP['red'][0]), 'red')
    return cv


# --------------------------------------------------------------------------- kiosk
def kiosk():
    W, H = 106, 62
    cv = Canvas(W, H)
    # body x 18..100, roof x 1..104 (overhangs left over a slim pole, like narvesen 3)
    BL, BR = 20, 98
    RL, RR = 1, 104
    # flat roof slab y 1..5: cream top edge, green fascia, dark underside
    cv.rect(RL, 1, RR, 2, 'cream', 4)
    cv.hline(RL + 1, RR - 1, 1, 'cream', 5)
    cv.rect(RL, 3, RR, 5, 'kgreen', 3)
    cv.hline(RL, RR, 3, 'kgreen', 4)
    cv.hline(RL, RR, 5, 'kgreen', 2)
    cv.hline(RL, RR, 6, 'kgreen', 1)
    # pole holding the overhang
    cv.vline(5, 7, 58, 'kgreen', 2); cv.vline(6, 7, 58, 'kgreen', 3); cv.vline(7, 7, 58, 'kgreen', 1)
    cv.set(6, 8, 'kgreen', 4); cv.set(6, 9, 'kgreen', 4)
    cv.rect(4, 59, 8, 59, 'steel', 1)
    # under-roof shadow strip
    cv.rect(8, 7, BL - 1, 7, 'dark', 1)
    # sign band y 7..15 on the body: cream with a red and a green stripe, navy oval name plate
    cv.rect(BL, 7, BR, 15, 'cream', 3)
    cv.hline(BL, BR, 7, 'dark', 2)
    cv.hline(BL, BR, 8, 'cream', 4)
    cv.hline(BL, BR, 12, 'red', 3); cv.hline(BL, BR, 13, 'kgreen', 3)
    cv.hline(BL, BR, 15, 'cream', 1)
    cx = (BL + BR) // 2
    px0, px1 = cx - 12, cx + 12
    cv.rect(px0, 8, px1, 14, 'navy', 3)
    cv.hline(px0 + 1, px1 - 1, 7, 'navy', 3)
    cv.hline(px0 + 1, px1 - 1, 15, 'navy', 2)
    cv.hline(px0 + 2, px1 - 2, 8, 'navy', 4)
    cv.vline(px0 - 1, 9, 13, 'navy', 2); cv.vline(px1 + 1, 9, 13, 'navy', 1)
    # hand AA on the oval ends
    for (x, y) in ((px0, 7), (px1, 7), (px0, 15), (px1, 15), (px0 - 1, 8), (px1 + 1, 8), (px0 - 1, 14), (px1 + 1, 14)):
        cv.c(x, y, mix(RAMP['navy'][2], RAMP['cream'][3], 0.45), 'navy')
    cv.hline(px0 + 1, px1 - 1, 7, 'cream', 1); cv.hline(px0 + 2, px1 - 2, 7, 'navy', 2)
    text(cv, 'KIOSK', cx - 9, 9, LETTER if DUSK_ON else RAMP['cream'][5])
    if DUSK_ON:
        # the name plate is lit from inside: a bright core and a light rim
        for x in range(px0 + 1, px1):
            for y in (9, 13):
                if cv.get(x, y) == RAMP['navy'][3]:
                    cv.set(x, y, 'navy', 4)
        cv.hline(px0 + 2, px1 - 2, 8, 'navy', 5)
        # two downlights under the sign band, one each side of the centre (they cast the cones)
        for lx in (cx - 21, cx + 21):
            cv.hline(lx - 2, lx + 2, 16, 'steel', 2)
            cv.hline(lx - 1, lx + 1, 17, 'warm', 5)
            cv.set(lx - 2, 17, 'warm', 3); cv.set(lx + 2, 17, 'warm', 3)
    # walls: green frame, glass bays full of magazines, lit warm inside
    cv.rect(BL, 16, BR, 57, 'kgreen', 3)
    cv.vline(BL, 16, 57, 'kgreen', 4); cv.vline(BR, 16, 57, 'kgreen', 2)
    bays = 5
    bw = (BR - BL - 2) // bays
    import random
    rnd = random.Random(5)
    for b in range(bays):
        x0 = BL + 2 + b * bw
        x1 = x0 + bw - 3
        y0, y1 = 18, 46
        hatch = b == 2
        # window glass: warm interior
        cv.rect(x0, y0, x1, y1, 'warm', 3)
        cv.hline(x0, x1, y0, 'warm', 1)
        cv.vline(x0, y0, y1, 'warm', 2)
        if hatch:
            # service hatch: counter with the seller's window open
            cv.rect(x0 + 1, y0 + 1, x1, 36, 'warm', 4)
            cv.rect(x0 + 2, 26, x1 - 1, 36, 'warm', 2)              # dark back of the kiosk
            for sy in (21, 27, 31):                                  # goods on the back wall
                for x in range(x0 + 2, x1 - 1, 2):
                    col = MAG[rnd.randrange(len(MAG))]
                    cv.c(x, sy, col); cv.c(x, sy + 1, mix(col, (0, 0, 0), 0.3))
                cv.hline(x0 + 2, x1 - 1, sy + 2, 'warm', 1)
            # the counter
            cv.hline(x0 - 1, x1 + 1, 37, 'cream', 4); cv.hline(x0 - 1, x1 + 1, 38, 'cream', 2)
            # sweets and gum on the counter
            for i, x in enumerate(range(x0 + 1, x1, 2)):
                col = MAG[(i * 3) % len(MAG)]
                cv.c(x, 36, col); cv.c(x, 35, col)
            cv.rect(x0, 39, x1, y1, 'warm', 2)
            for y in (41, 44):
                for x in range(x0 + 1, x1, 3):
                    col = MAG[rnd.randrange(len(MAG))]
                    cv.c(x, y, col); cv.c(x + 1, y, col); cv.c(x, y + 1, mix(col, (0, 0, 0), 0.3))
            continue
        # shelves with magazines: rows of small coloured covers
        for sy in range(y0 + 2, y1 - 1, 6):
            x = x0 + 1
            while x + 2 <= x1:
                col = MAG[rnd.randrange(len(MAG))]
                w = rnd.choice((2, 3, 3))
                for xx in range(x, min(x + w, x1 + 1)):
                    cv.c(xx, sy, mix(col, (255, 255, 255), 0.25))
                    cv.c(xx, sy + 1, col)
                    cv.c(xx, sy + 2, col)
                    cv.c(xx, sy + 3, mix(col, (0, 0, 0), 0.35))
                if rnd.random() < 0.5:
                    cv.c(x, sy + 1, RAMP['cream'][5])             # a headline
                x += w + 1
            cv.hline(x0 + 1, x1, sy + 4, 'warm', 1)                  # shelf
        # glass reflection: two hand-AA'd diagonal streaks
        for i in range(5):
            cv.c(x0 + 2 + i, y0 + 8 - i, mix(RAMP['warm'][5], RAMP['glass'][5], 0.5))
            cv.c(x0 + 2 + i, y0 + 9 - i, RAMP['warm'][4])
    # mullions between bays
    for b in range(bays + 1):
        x = BL + 1 + b * bw - (1 if b else 0)
        if BL < x < BR:
            cv.vline(x, 17, 47, 'kgreen', 4)
            cv.vline(x + 1, 17, 47, 'kgreen', 2)
    cv.hline(BL + 1, BR - 1, 17, 'kgreen', 2)
    # lower panel (kick plate) y 48..57 with a lighter rail
    cv.hline(BL + 1, BR - 1, 47, 'kgreen', 5)
    cv.hline(BL + 1, BR - 1, 48, 'kgreen', 4)
    cv.rect(BL + 1, 49, BR - 1, 57, 'kgreen', 2)
    for b in range(bays):
        x0 = BL + 3 + b * bw
        cv.rect(x0, 50, x0 + bw - 5, 55, 'kgreen', 3)
        cv.hline(x0, x0 + bw - 5, 50, 'kgreen', 4)
        cv.vline(x0 + bw - 5, 50, 55, 'kgreen', 1)
    # plinth
    cv.rect(BL - 1, 58, BR + 1, 59, 'steel', 2)
    cv.hline(BL - 1, BR + 1, 58, 'steel', 3)
    # a newspaper board («løpeseddel») leaning by the pole, pixel writing only
    sx0, sx1 = 9, 17
    cv.rect(sx0, 44, sx1, 57, 'paper', 3)
    cv.hline(sx0, sx1, 44, 'paper', 4)
    cv.vline(sx1, 44, 57, 'paper', 2)
    cv.rect(sx0 + 1, 46, sx1 - 1, 48, 'red', 3)
    scribble(cv, sx0 + 1, sx1 - 2, 47, RAMP['cream'][5], 2)
    for y in (50, 52, 54):
        scribble(cv, sx0 + 1, sx1 - 1, y, RAMP['dark'][1], y)
    cv.rect(sx0, 58, sx0 + 1, 59, 'dark', 1); cv.rect(sx1 - 1, 58, sx1, 59, 'dark', 1)
    cv.outline()
    cv.soften()
    # roof slab ends: rounded with in-between tones
    for x, y, t in ((RL - 1, 1, 0.55), (RR + 1, 1, 0.55), (RL - 1, 6, 0.4), (RR + 1, 6, 0.4)):
        m = 'cream' if y == 1 else 'kgreen'
        cv.c(x, y, mix(RAMP[m][0], RAMP[m][2], t), m)
    return cv


# ---- the kiosk at dusk: the outside darkened towards the evening blue, the inside, the windows and
# the name plate lit; its light (two downlight cones and a glow round the sign) is on a separate sheet
NIGHT = rgb('#121830')
DUSK = {'kgreen': 0.5, 'cream': 0.55, 'steel': 0.5, 'paper': 0.45, 'red': 0.45, 'dark': 0.3, 'glass': 0.4}
LETTER = rgb('#fffbe8')
DUSK_ON = False
KIOSK_GEOM = dict(cx=59, lamps=(59 - 21, 59 + 21), lamp_y=17, sign=(59, 11), ground=60)


def kiosk_dusk():
    global DUSK_ON
    saved = {m: RAMP[m] for m in DUSK}
    for m, f in DUSK.items():
        RAMP[m] = [mix(c, NIGHT, f) for c in RAMP[m]]
    DUSK_ON = True
    try:
        return kiosk()
    finally:
        DUSK_ON = False
        RAMP.update(saved)


def kiosk_light(w, h):
    """Warm light for the dusk kiosk in its own canvas coordinates: a smooth downward cone from each
    downlight and a soft glow round the name plate, blurred edges, no dither (like lamps-light.png)."""
    import math
    from PIL import ImageFilter
    A = [[0.0] * w for _ in range(h)]
    g = KIOSK_GEOM
    ss = lambda e0, e1, v: (lambda t: t * t * (3 - 2 * t))(max(0.0, min(1.0, (v - e0) / (e1 - e0))))
    for lx in g['lamps']:
        y0 = g['lamp_y']
        for y in range(y0 + 1, g['ground'] + 1):
            t = (y - y0) / (g['ground'] - y0)
            half = 3 + 13 * t
            for x in range(w):
                u = abs(x - lx) / half
                if u < 1.2:
                    A[y][x] = max(A[y][x], 0.62 * (1 - 0.45 * t) * (1 - ss(0.55, 1.2, u)))
        for y in range(g['ground'] - 3, g['ground'] + 1):           # pool on the ground
            for x in range(w):
                e = ((x - lx) / 18) ** 2 + ((y - g['ground']) / 2.5) ** 2
                if e < 1:
                    A[y][x] = max(A[y][x], 0.4 * (1 - e) ** 0.8)
    sx, sy = g['sign']
    for y in range(h):
        for x in range(w):
            d = math.hypot((x - sx) / 1.9, y - sy)
            if d < 9:
                A[y][x] = max(A[y][x], 0.6 * (1 - d / 9) ** 1.3)
    a = Image.new('L', (w, h))
    a.putdata([max(0, min(255, round(v * 255))) for row in A for v in row])
    a = a.filter(ImageFilter.GaussianBlur(1.4))
    col = rgb('#ffd88a')
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            v = a.getpixel((x, y))
            if v:
                im.putpixel((x, y), mix(col, (255, 255, 255), min(0.6, v / 255 * 0.9)) + (v,))
    return im


PROPS = [('trash', trash), ('recycling', recycling), ('phonebooth', phonebooth), ('kiosk', kiosk_dusk)]
LIGHTS = {'kiosk': kiosk_light}
# every prop has a flat top (rim, lid, roof cap, roof slab), so top = visible height


def trimmed(cv):
    im = cv.image()
    return im.crop(im.getbbox())


def field_image(A, col, blur=1.4):
    """float alpha field → RGBA light: smooth gradient, blurred edges, brightest parts towards white"""
    from PIL import ImageFilter
    h, w = len(A), len(A[0])
    a = Image.new('L', (w, h))
    a.putdata([max(0, min(255, round(v * 255))) for row in A for v in row])
    a = a.filter(ImageFilter.GaussianBlur(blur))
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            v = a.getpixel((x, y))
            if v:
                im.putpixel((x, y), mix(col, (255, 255, 255), min(0.6, v / 255 * 0.9)) + (v,))
    return im


if __name__ == '__main__':
    import tokyo_props
    import oslo_props
    import glitch_props
    import boards
    # (name, frames, fps, top, light image) for every prop; Tokyoslo props come from tokyo_props.py
    entries = []
    for name, fn in PROPS:
        cv = fn()
        full = cv.image()
        entries.append((name, [full], 1, None, LIGHTS[name](full.width, full.height) if name in LIGHTS else None))
    for name, fn, fps, top, lf in tokyo_props.TOKYO + oslo_props.OSLO + glitch_props.GLITCH + boards.BOARDS:
        frames = []
        for cv in fn():
            im = cv.image()
            if hasattr(cv, 'steam'):
                tokyo_props.yatai_steam(im, cv.steam)
            if hasattr(cv, 'post'):
                cv.post(im)
            frames.append(im)
        lit = None
        if lf:
            A, col = lf(frames[0].width, frames[0].height)
            lit = field_image(A, col)
        entries.append((name, frames, fps, top, lit))
    cols = max(len(e[1]) for e in entries)
    root = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
    sheet = Image.new('RGBA', (CELL_W * cols, CELL_H * len(entries)), (0, 0, 0, 0))
    light = Image.new('RGBA', sheet.size, (0, 0, 0, 0))
    meta = {}
    for row, (name, frames, fps, top, lit) in enumerate(entries):
        boxes = [f.getbbox() for f in frames]
        box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        w, h = box[2] - box[0], box[3] - box[1]
        assert w <= CELL_W and h <= CELL_H, (name, w, h)
        ox, oy = CELL_W // 2 - w // 2 - box[0], CELL_H - h - box[1]   # same placement for every frame
        for c, f in enumerate(frames):
            cell = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
            cell.alpha_composite(f.crop(box), (ox + box[0], oy + box[1]))
            sheet.alpha_composite(cell, (c * CELL_W, row * CELL_H))
        if lit is not None:   # same placement as the sprite, so both sheets share one grid (light: column 0 only)
            cell = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
            lx, ly = ox, oy
            src = lit
            if lx < 0 or ly < 0:   # the light may reach outside the sprite's canvas edge: clip
                src = lit.crop((max(0, -lx), max(0, -ly), lit.width, lit.height)); lx, ly = max(0, lx), max(0, ly)
            cell.alpha_composite(src, (lx, ly))
            light.alpha_composite(cell, (0, row * CELL_H))
        meta[name] = {'row': row, 'frames': len(frames), 'fps': fps, 'w': w, 'h': h, 'top': h if top is None else top}
    sheet.save(root / 'props.png')
    light.save(root / 'props-light.png')
    (root / 'props.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote', root / 'props.png', sheet.size)
    for n in meta:
        print(f"  {n:11s} {meta[n]['w']:3d} × {meta[n]['h']:2d}  top {meta[n]['top']}  frames {meta[n]['frames']}")
