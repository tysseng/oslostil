#!/usr/bin/env python3
"""Platform departure boards for Sandvika: a normal one (level 1) and a broken one that glitches,
collapses and lands as a platform (level 2, the glitch).

The board: a dark steel housing on two posts, an amber dot-matrix screen («OSLO S 21:04» / «SPOR 2»).
Same scale and style as the other props (girl scale ≈ 19 px/m, outlines tinted per material).

  departure_board         drawn into the props sheet by props.py (static, amber glow in props-light.png);
                          46 px tall, top 45: one jump
  board-broken.png        its own sheet (this script): 10 frames of 64 × 52, one row, bottom-centred
  board-broken-light.png  the same grid, one light per frame (the screen's glow follows the board down)
  board-broken.json       frame names, per-frame walkable top, and the three phases:
                            glitch 0–2 (loop, 8 fps)  →  fall 3–7 (once, 12 fps ≈ one beat)  →  rest 8–9 (loop, 4 fps)
Usage: python3 tools/sprites/boards.py   (props.py also imports BOARDS for the normal board)
"""
import json
import math
import random
from pathlib import Path
from PIL import Image
from props import Canvas, RAMP, rgb, mix

PINK, CYAN = rgb('#ff2bd6'), rgb('#2bf0ff')
AMBER, AMBER_D, AMBER_L = rgb('#ffb000'), rgb('#7a4e08'), rgb('#ffd36a')
SCREEN = rgb('#0a0b10')
BW, BH = 52, 16                       # housing incl. its frame (the canvas outline adds 1 px round it)

FONT = {
    'O': ['010', '101', '101', '101', '010'], 'S': ['011', '100', '010', '001', '110'],
    'L': ['100', '100', '100', '100', '111'], 'P': ['110', '101', '110', '100', '100'],
    'R': ['110', '101', '110', '101', '101'], '0': ['111', '101', '101', '101', '111'],
    '1': ['010', '110', '010', '010', '111'], '2': ['110', '001', '010', '100', '111'],
    '4': ['101', '101', '111', '001', '001'], '8': ['111', '101', '111', '101', '111'],
    'A': ['010', '101', '111', '101', '101'], '-': ['000', '000', '111', '000', '000'],
    ':': ['0', '1', '0', '1', '0'], ' ': ['00', '00', '00', '00', '00'],
}
GARBLE = [['101', '010', '111', '010', '101'], ['111', '001', '110', '100', '011'], ['011', '110', '001', '111', '100'],
          ['110', '011', '101', '110', '001'], ['001', '111', '100', '011', '110']]


def glyphs(s):
    return [FONT[c] for c in s]


def write(grid, gl, x, y, col):
    for g in gl:
        for j, row in enumerate(g):
            for i, b in enumerate(row):
                if b == '1' and 0 <= y + j < BH and 0 <= x + i < BW:
                    grid[y + j][x + i] = ('screen', col)
        x += len(g[0]) + 1
    return x


def board_grid(mode='ok', rnd=None):
    """The housing as a grid of (material, colour) cells. mode: ok | garble | split | static | aaa | dim."""
    g = [[None] * BW for _ in range(BH)]
    for y in range(BH):
        for x in range(BW):
            if y <= 1:
                g[y][x] = ('steel', RAMP['steel'][3] if y == 0 else RAMP['steel'][2])      # top cap
            elif y >= BH - 2 or x <= 1 or x >= BW - 2:
                g[y][x] = ('dark', RAMP['dark'][3] if (x <= 1 or y >= BH - 2) else RAMP['dark'][2])
            else:
                g[y][x] = ('screen', SCREEN)
    for x in range(2, BW - 2):            # a faint reflection along the top of the glass
        g[2][x] = ('screen', rgb('#1a1c26'))
    if mode in ('ok', 'dim'):
        a = AMBER if mode == 'ok' else AMBER_D
        write(g, glyphs('OSLO S'), 4, 4, a)
        write(g, glyphs('21:04'), BW - 4 - 17, 4, a)
        write(g, glyphs('SPOR 2'), 4, 10, AMBER_D if mode == 'ok' else rgb('#4a3006'))
        for x in range(BW - 14, BW - 4, 2):               # «on time» dots
            g[12][x] = ('screen', AMBER_D)
    elif mode == 'garble':
        x = 4
        for i in range(6):
            x = write(g, [rnd.choice(GARBLE)], x, 4, AMBER if i % 3 else PINK)
        write(g, glyphs('88:88'), BW - 4 - 17, 4, AMBER)
        x = 4
        for i in range(5):
            x = write(g, [rnd.choice(GARBLE)], x, 10, AMBER_D if i % 2 else CYAN)
    elif mode == 'aaa':
        write(g, glyphs('A-A-A'), 4, 4, PINK)
        write(g, glyphs('88:88'), BW - 4 - 17, 4, AMBER)
        write(g, glyphs('A-A-A'), 4, 10, CYAN)
    elif mode == 'static':
        for y in range(3, BH - 2):
            for x in range(2, BW - 2):
                if rnd.random() < .45:
                    g[y][x] = ('screen', rnd.choice([AMBER, AMBER_D, PINK, CYAN, rgb('#2a2c38')]))
    elif mode == 'flash':
        for y in range(3, BH - 2):
            for x in range(2, BW - 2):
                g[y][x] = ('screen', AMBER_L if (x + y) % 5 else rgb('#ffffff'))
    return g


def slip(g, y0, y1, dx):
    """Rows y0..y1 of the screen slip dx px sideways (the frame stays)."""
    for y in range(y0, y1 + 1):
        row = [g[y][x] for x in range(2, BW - 2)]
        row = row[-dx:] + row[:-dx] if dx > 0 else row[-dx:] + row[:-dx]
        for i, c in enumerate(row):
            g[y][2 + i] = c


RAMP.setdefault('screen', [rgb('#05060a'), rgb('#0a0b10'), rgb('#14161e'), rgb('#1c1f2a'), rgb('#2a2e3c'), rgb('#3a4050')])


def blit(cv, g, x0, y0, tilt=0.0, squash=0):
    """Draw the housing with its top-left at (x0, y0). tilt: px the right end sits lower than the left
    (stepped column offsets, no rotation). squash: rows removed from the middle (impact)."""
    rows = list(range(BH))
    if squash:
        mid = BH // 2
        rows = rows[:mid - squash // 2] + rows[mid + (squash - squash // 2):]
    for x in range(BW):
        dy = round(tilt * (x - BW / 2) / BW)
        for j, y in enumerate(rows):
            c = g[y][x]
            if c:
                cv.c(x0 + x, y0 + j + dy, c[1], c[0])


def post(cv, pts):
    """A 3-px steel post along a polyline (light, mid, dark columns)."""
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(abs(xb - xa), abs(yb - ya), 1)
        for k in range(n + 1):
            x = round(xa + (xb - xa) * k / n)
            y = round(ya + (yb - ya) * k / n)
            for i, tone in enumerate((4, 3, 2)):
                cv.set(x - 1 + i, y, 'steel', tone)


def base_plate(cv, cx, y):
    cv.rect(cx - 3, y - 1, cx + 3, y, 'dark', 3)
    cv.hline(cx - 3, cx + 3, y - 1, 'dark', 4)


def finish(cv):
    cv.outline()
    cv.soften()
    return cv


# --------------------------------------------------------------------------- the normal board (props sheet)
H_OK = 46


def departure_board():
    W = BW + 2
    cv = Canvas(W, H_OK)
    g = board_grid('ok')
    by = 1
    for px in (11, W - 12):
        post(cv, [(px, by + BH), (px, H_OK - 2)])
        base_plate(cv, px, H_OK - 2)
    blit(cv, g, 1, by)
    return [finish(cv)]


def departure_board_light(w, h):
    import tokyo_props as tp
    A = tp.field(w, h)
    tp.radial(A, w // 2, 9, 30, 0.42, squash=0.32)
    tp.pool(A, w // 2, h - 2, 18, 0.18)
    return A, rgb('#ffb347')


BOARDS = [('departure_board', departure_board, 1, 45, departure_board_light)]


# --------------------------------------------------------------------------- the broken board (own sheet)
CW, CH = 64, 52
FRAMES = ['glitch0', 'glitch1', 'glitch2', 'buckle0', 'buckle1', 'drop', 'impact', 'bounce', 'rest0', 'rest1']


def broken_frame(name, rnd):
    cv = Canvas(CW, CH)
    G = CH - 2                       # ground row (outline goes below it)
    bx = (CW - BW) // 2
    pl, pr = bx + 10, bx + BW - 11   # post x
    sparks = []
    if name.startswith('glitch'):
        i = int(name[-1])
        g = board_grid(['garble', 'aaa', 'static'][i], rnd)
        if i == 0:
            slip(g, 4, 8, 3)
        if i == 2:
            slip(g, 9, 12, -4)
        top = G - 45
        for px in (pl, pr):
            post(cv, [(px, top + BH), (px, G)])
            base_plate(cv, px, G)
        blit(cv, g, bx, top)
        if i == 1:                                        # pink/cyan split on the housing edges
            for y in range(top, top + BH):
                cv.c(bx - 1, y, PINK, 'dark')
                cv.c(bx + BW, y, CYAN, 'dark')
        if i == 2:
            sparks = [(pl + 2, top + BH + 3), (pl + 4, top + BH + 1), (pl + 1, top + BH + 6)]
        rect_top = 45
    elif name in ('buckle0', 'buckle1'):
        k = 1 if name == 'buckle0' else 2
        drop = 7 if k == 1 else 18
        top = G - 45 + drop
        knee = (G + top + BH) // 2
        for px, s in ((pl, -1), (pr, 1)):
            post(cv, [(px, top + BH), (px + s * (2 * k + 1), knee), (px, G)])
            base_plate(cv, px, G)
        g = board_grid('static' if k == 1 else 'garble', rnd)
        blit(cv, g, bx, top, tilt=3 if k == 1 else -4)
        sparks = [(pl + 4, knee), (pr - 4, knee - 2)] if k == 2 else [(pl + 3, knee)]
        rect_top = 45 - drop
    elif name == 'drop':
        top = G - BH - 6
        for px, s in ((pl, -1), (pr, 1)):                 # posts folded flat, splayed out
            post(cv, [(px + s * 6, G - 4), (px + s * 1, G - 1)])
            base_plate(cv, px, G)
        g = board_grid('garble', rnd)
        blit(cv, g, bx, top, tilt=2)
        for x in range(bx + 4, bx + BW - 4, 7):          # speed streaks above it
            for y in range(top - 8, top - 2):
                if (x + y) % 3:
                    cv.c(x, y, PINK if (x // 7) % 2 else CYAN, 'dark')
        rect_top = 22
    elif name == 'impact':
        top = G - (BH - 4) - 1
        for px, s in ((pl, -1), (pr, 1)):
            post(cv, [(px + s * 8, G), (px + s * 2, G - 1)])
        g = board_grid('flash', rnd)
        blit(cv, g, bx - 1, top, squash=4)
        for s in (-1, 1):                                  # dust and sparks out to the sides
            for d in range(5):
                cv.c((bx - 3 if s < 0 else bx + BW + 2) + s * d, G - (d % 3), rgb('#c9c3b5') if d % 2 else AMBER_L, 'dark')
        sparks = [(bx - 4, G - 8), (bx + BW + 3, G - 9), (bx + 8, top - 3), (bx + BW - 8, top - 4)]
        rect_top = 12
    elif name == 'bounce':
        top = G - BH - 2
        for px, s in ((pl, -1), (pr, 1)):
            post(cv, [(px + s * 7, G), (px + s * 1, G - 3), (px + s * 1, top + BH)])
        g = board_grid('dim', rnd)
        slip(g, 4, 6, 2)
        blit(cv, g, bx, top, tilt=-2)
        rect_top = 16
    else:                                                  # rest0 / rest1: lying on its folded legs
        i = int(name[-1])
        top = G - BH - 1
        for px, s in ((pl, -1), (pr, 1)):
            post(cv, [(px + s * 8, G), (px + s * 2, G - 1), (px + s * 1, top + BH)])
        g = board_grid('aaa' if i == 0 else 'dim', rnd)
        if i == 1:
            slip(g, 10, 12, 3)
        blit(cv, g, bx, top)
        rect_top = 15
    finish(cv)
    for x, y in sparks:                                     # sparks after the outline: bare bright pixels
        for dx, dy, c in ((0, 0, rgb('#ffffff')), (1, 0, AMBER_L), (-1, 0, AMBER_L), (0, -1, AMBER), (0, 1, AMBER)):
            cv.c(x + dx, y + dy, c, 'dark')
    return cv, rect_top


def broken_light(name, img):
    """Glow centred on the screen wherever it is in this frame (found from the amber/pink pixels)."""
    import tokyo_props as tp
    px = img.load()
    pts = [(x, y) for y in range(img.height) for x in range(img.width)
           if px[x, y][3] and px[x, y][:3] in (AMBER, AMBER_L, PINK, CYAN, (255, 255, 255))]
    A = tp.field(img.width, img.height)
    if pts:
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        k = 0.75 if name == 'impact' else (0.25 if name in ('rest1', 'bounce') else 0.4)
        tp.radial(A, cx, cy, 28, k, squash=0.4)
        if name in ('rest0', 'rest1', 'bounce', 'impact'):
            tp.pool(A, cx, img.height - 2, 22, k * 0.5)
    col = rgb('#ff8ad8') if name in ('glitch1', 'rest0') else rgb('#ffb347')
    return A, col


def main():
    from props import field_image
    root = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
    rnd = random.Random(33)
    sheet = Image.new('RGBA', (CW * len(FRAMES), CH), (0, 0, 0, 0))
    light = Image.new('RGBA', sheet.size, (0, 0, 0, 0))
    tops = []
    for i, name in enumerate(FRAMES):
        cv, top = broken_frame(name, rnd)
        im = cv.image()
        sheet.alpha_composite(im, (i * CW, 0))
        A, col = broken_light(name, im)
        light.alpha_composite(field_image(A, col, blur=1.6), (i * CW, 0))
        tops.append(top)
    sheet.save(root / 'board-broken.png')
    light.save(root / 'board-broken-light.png')
    meta = {'cell': [CW, CH], 'frames': FRAMES, 'top': tops, 'w': BW + 2,
            'phases': {'glitch': {'frames': [0, 1, 2], 'fps': 8, 'loop': True},
                       'fall': {'frames': [3, 4, 5, 6, 7], 'fps': 12, 'loop': False},
                       'rest': {'frames': [8, 9], 'fps': 4, 'loop': True}},
            'note': 'bottom-centred, base on the bottom row minus the 1-px outline; top = walkable height above the '
                    'base in each frame (0 = none). The light sheet has one glow per frame on the same grid.'}
    (root / 'board-broken.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote board-broken.png', sheet.size, 'tops', tops)


if __name__ == '__main__':
    main()
