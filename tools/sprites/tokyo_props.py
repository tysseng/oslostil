"""Tokyoslo street props, drawn into the props sheet by tools/sprites/props.py (same style and scale:
front views, girl scale ≈ 19 px/m, outlines tinted per material, hand-AA'd corners).

  bin_tokyo   red lacquer bin with gold bands and a black lid ................ 17 px
  vending     two vending machines side by side, lit fronts .................. 42 px (one jump)
  lanterns    a string of red paper lanterns between two bamboo poles, sways .. 52 px (not standable)
  neon        a vertical neon sign on a pole, flickers, invented glyphs ....... 52 px (not standable)
  yatai       a ramen cart with a red lantern, noren and steam ............... 36 px (one jump)
  konbini     a night-time convenience store, bright windows ................. 58 px (double jump)
  bench_asian a red-felt tea-house bench under a red paper parasol ............ 43 px; the seat (12) is the top
  shop_wood   a small old wooden shop: tiled roof, lattice, noren, lanterns ... 55 px (double jump)

Each entry: (draw function → list of frames, fps, top or 0 when not standable, light function or None).
Light functions return a float alpha field and a colour; props.py turns them into props-light.png.
"""
import math
import random
from props import Canvas, RAMP, rgb, mix

R = lambda *c: [rgb(x) for x in c]
RAMP.update({
    'lacq':   R('#2a0406', '#5a0a10', '#8e1018', '#c41c22', '#e8423a', '#ff8a70'),
    'lblk':   R('#050406', '#0e0a0e', '#1a141a', '#282028', '#3a303a', '#584a58'),
    'tgold':  R('#3a2606', '#7a5410', '#b07c1c', '#e0aa30', '#ffd560', '#fff2b0'),
    'bamboo': R('#14100a', '#2a2214', '#40341e', '#5a4a2a', '#76643a', '#9c8a54'),
    'paperR': R('#3a0606', '#8a1010', '#c81e1e', '#ff3a2a', '#ff8a5a', '#ffd8a0'),
    'neonP':  R('#3a0420', '#8a0c4a', '#e0207a', '#ff4aa8', '#ff9ad0', '#ffe6f4'),
    'neonC':  R('#04262e', '#0a5a68', '#14a0b4', '#30e0f0', '#9af6ff', '#ffffff'),
    'plum':   R('#0a0408', '#160a12', '#22101c', '#301828', '#442238', '#5e3250'),
    'wood':   R('#1a0e06', '#3a220e', '#5a3618', '#7a4c24', '#9c6634', '#c48a50'),
    'woodD':  R('#100804', '#22140a', '#341e10', '#482a16', '#5e3a20', '#7a4e2e'),
    'noren':  R('#1a0408', '#4a0a14', '#7a1020', '#a81a2c', '#d03040', '#f07080'),
    'pot':    R('#1a1e24', '#3a424e', '#5e6a7a', '#8a96a8', '#b8c2d0', '#e6ecf4'),
    'vmR':    R('#2a0408', '#5e0a12', '#9a121e', '#cc1e2a', '#ee4a4a', '#ff8a80'),
    'vmW':    R('#2a2e38', '#5a6070', '#8a92a4', '#b8c0d0', '#dfe6f0', '#ffffff'),
    'vmB':    R('#06142e', '#0e2a5a', '#184490', '#2a62c0', '#4a88e8', '#8ab8ff'),
    'lit':    R('#4a6074', '#8aa8c4', '#bcd6ec', '#e2f0fc', '#f6fbff', '#ffffff'),
    'wall':   R('#0a0c12', '#141820', '#1e2430', '#2a3242', '#3a4458', '#52607a'),
    'stone':  R('#16161a', '#2e2e34', '#46464e', '#60606a', '#7e7e88', '#a4a4ae'),
})
MAG = [rgb(c) for c in ('#ff4f8b', '#ffd84a', '#2bc8b0', '#ff8a2a', '#8f6ae8', '#5fb0ff', '#f4f4f4', '#e0322c', '#7ee05a')]
FONT = {
    'K': ['101', '110', '100', '110', '101'], 'O': ['010', '101', '101', '101', '010'],
    'N': ['1001', '1101', '1011', '1001', '1001'], 'B': ['110', '101', '110', '101', '110'],
    'I': ['111', '010', '010', '010', '111'],
}


def text(cv, s, x, y, col):
    for ch in s:
        for j, row in enumerate(FONT[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    cv.c(x + i, y + j, col)
        x += len(FONT[ch][0]) + 1


def field(w, h):
    return [[0.0] * w for _ in range(h)]


def put(A, x, y, a):
    if 0 <= y < len(A) and 0 <= x < len(A[0]) and a > A[y][x]:
        A[y][x] = a


def radial(A, cx, cy, r, power, down=1.0, up=1.0, squash=1.0):
    for y in range(len(A)):
        for x in range(len(A[0])):
            dx, dy = x - cx, (y - cy) * squash
            d = math.hypot(dx, dy)
            if d >= r:
                continue
            c = dy / d if d else 0
            w = 1 + (down - 1) * c if c > 0 else 1 + (up - 1) * -c
            put(A, x, y, power * w * (1 - d / r) ** 1.5)


def cone(A, cx, y0, ground, spread, power):
    for y in range(y0 + 1, ground + 1):
        t = (y - y0) / max(1, ground - y0)
        half = 2.5 + (spread - 2.5) * t
        for x in range(len(A[0])):
            u = abs(x - cx) / half
            if u < 1.2:
                e = max(0.0, min(1.0, (u - 0.55) / 0.65))
                put(A, x, y, power * (1 - 0.5 * t) * (1 - e * e * (3 - 2 * e)))


def pool(A, cx, ground, half, power):
    for y in range(ground - 3, ground + 1):
        for x in range(len(A[0])):
            e = ((x - cx) / half) ** 2 + ((y - ground) / 2.5) ** 2
            if e < 1:
                put(A, x, y, power * (1 - e) ** 0.8)


def finish(cv):
    cv.outline()
    cv.soften()
    return cv


# --------------------------------------------------------------------------- red lacquer bin
def bin_tokyo():
    cv = Canvas(15, 17)
    for y in range(4, 14):
        for x in range(2, 13):
            rel = (x - 2) / 10
            t = 2 if rel < 0.08 or rel > 0.85 else 5 if 0.18 <= rel < 0.3 else 4 if rel < 0.5 else 3
            cv.set(x, y, 'lacq', t)
    for y in (5, 12):                                       # gold bands
        for x in range(2, 13):
            rel = (x - 2) / 10
            cv.set(x, y, 'tgold', 4 if 0.15 < rel < 0.4 else 3 if rel < 0.8 else 2)
    cv.rect(6, 8, 8, 9, 'tgold', 3); cv.set(6, 8, 'tgold', 5)   # round crest
    cv.rect(3, 2, 11, 3, 'lblk', 3); cv.hline(4, 10, 1, 'lblk', 4)   # domed lid
    cv.set(5, 1, 'lblk', 5); cv.hline(2, 12, 3, 'lblk', 2)
    cv.hline(6, 8, 3, 'lblk', 0)                            # the slot
    cv.hline(3, 11, 14, 'lblk', 2); cv.hline(4, 10, 15, 'lblk', 1)
    return [finish(cv)]


# --------------------------------------------------------------------------- vending machines
def vending():
    W, H = 32, 43
    cv = Canvas(W, H)
    rnd = random.Random(4)
    for k, (x0, body) in enumerate(((1, 'vmR'), (16, 'vmW'))):
        x1 = x0 + 13
        cv.rect(x0, 1, x1, 40, body, 3)
        cv.vline(x0, 1, 40, body, 4); cv.vline(x1, 1, 40, body, 2)
        cv.hline(x0, x1, 1, body, 4)
        cv.rect(x0 + 1, 2, x1 - 1, 3, 'lit', 4)             # lit header strip with dot «writing»
        for x in range(x0 + 2, x1 - 1, 2):
            cv.set(x, 3, 'vmB' if k else 'vmR', 3)
        # display window with three shelves of cans and price lights
        cv.rect(x0 + 1, 5, x1 - 1, 22, 'lit', 3)
        cv.vline(x0 + 1, 5, 22, 'lit', 4)
        for row, sy in enumerate((6, 12, 18)):
            for x in range(x0 + 2, x1 - 1, 3):
                col = MAG[rnd.randrange(len(MAG))]
                for yy in range(sy, sy + 3):
                    cv.c(x, yy, mix(col, (255, 255, 255), 0.25) if yy == sy else col, 'lit')
                    cv.c(x + 1, yy, mix(col, (0, 0, 0), 0.25), 'lit')
                cv.c(x, sy + 4, rgb('#3dff7a') if rnd.random() < 0.7 else rgb('#ff3030'), 'lit')
            cv.hline(x0 + 1, x1 - 1, sy + 3, 'lit', 1)
        # buttons, coin slot, note slot
        cv.rect(x0 + 1, 24, x1 - 1, 29, body, 2)
        for x in range(x0 + 2, x1 - 1, 2):
            cv.set(x, 25, 'lit', 5)
        cv.rect(x1 - 4, 27, x1 - 2, 28, 'lblk', 1); cv.set(x1 - 3, 27, 'tgold', 4)
        # dispenser opening
        cv.rect(x0 + 2, 32, x1 - 2, 36, 'lblk', 1)
        cv.hline(x0 + 2, x1 - 2, 32, body, 1)
        cv.hline(x0 + 3, x1 - 3, 35, 'lblk', 3)
        cv.rect(x0, 39, x1, 41, 'lblk', 2)
    return [finish(cv)]


def vending_light(w, h):
    A = field(w, h)
    for cx in (8, 23):
        radial(A, cx, 14, 15, 0.45, down=1.2, squash=0.8)
        pool(A, cx, h - 2, 12, 0.35)
    return A, rgb('#d8ecff')


# --------------------------------------------------------------------------- lantern string
def lanterns():
    frames = []
    W, H = 92, 52
    xs = (15, 27, 39, 52, 64, 76)
    for f in range(2):
        cv = Canvas(W, H)
        for px in (2, W - 4):                               # bamboo poles with nodes
            cv.rect(px, 3, px + 1, H - 2, 'bamboo', 3)
            cv.vline(px, 3, H - 2, 'bamboo', 4)
            for y in range(10, H - 2, 9):
                cv.hline(px, px + 1, y, 'bamboo', 1)
            cv.rect(px - 1, 2, px + 2, 2, 'bamboo', 2)
        rope = lambda x: 4 + round(7 * (1 - ((x - W / 2) / (W / 2 - 4)) ** 2))
        for x in range(4, W - 4):
            cv.set(x, rope(x), 'lblk', 3)
        for i, lx in enumerate(xs):
            sway = (1 if (i + f) % 2 else -1) if i % 3 else 0
            top = rope(lx) + 1
            cv.vline(lx, top, top + 1, 'lblk', 3)
            x0, y0 = lx - 3 + sway, top + 2
            cv.hline(x0 + 1, x0 + 5, y0, 'tgold', 3); cv.hline(x0 + 2, x0 + 4, y0 - 0, 'lblk', 2)
            for j, half in enumerate((2, 3, 3, 3, 3, 3, 2)):
                y = y0 + 1 + j
                for x in range(lx - half + sway, lx + half + 1 + sway):
                    rel = (x - (lx - half + sway)) / (2 * half)
                    t = 5 if 0.3 < rel < 0.6 and 2 <= j <= 4 else 4 if 0.2 < rel < 0.7 else 3 if rel < 0.85 else 2
                    if f == 1 and t == 4:
                        t = 5 if i % 2 else 4
                    cv.set(x, y, 'paperR', t)
                if j in (1, 3, 5):                           # ribs
                    cv.set(lx - half + sway, y, 'paperR', 1)
            cv.hline(x0 + 1, x0 + 5, y0 + 8, 'lblk', 2); cv.set(lx + sway, y0 + 9, 'tgold', 3)
        frames.append(finish(cv))
    return frames


def lanterns_light(w, h):
    A = field(w, h)
    rope = lambda x: 4 + round(7 * (1 - ((x - 46) / 42) ** 2))
    for lx in (15, 27, 39, 52, 64, 76):
        radial(A, lx, rope(lx) + 7, 11, 0.5, down=1.3)
    return A, rgb('#ff8a5a')


# --------------------------------------------------------------------------- vertical neon sign
GLYPHS = [  # invented, kana-looking shapes (not real words)
    ['111110', '000010', '011110', '010000', '010000', '011111'],
    ['010010', '111111', '010010', '010010', '100010', '000100'],
    ['001000', '111111', '001000', '011100', '101010', '001000'],
    ['100000', '111110', '100010', '000010', '000100', '011000'],
]


def neon():
    frames = []
    W, H = 20, 53
    for f in range(3):
        cv = Canvas(W, H)
        cv.rect(9, 30, 10, H - 2, 'lblk', 3); cv.vline(9, 30, H - 2, 'lblk', 4)   # pole
        cv.rect(7, H - 3, 12, H - 2, 'lblk', 2)
        cv.rect(8, 30, 11, 31, 'lblk', 2)                    # bracket
        cv.rect(2, 1, 17, 30, 'plum', 2)                     # sign box
        cv.vline(2, 1, 30, 'plum', 3); cv.vline(17, 1, 30, 'plum', 1)
        on_c = 4 if f == 1 else 3
        for y in (2, 29):                                    # cyan frame tube
            cv.hline(3, 16, y, 'neonC', on_c)
        for x in (3, 16):
            cv.vline(x, 2, 29, 'neonC', on_c)
        for g, gy in enumerate((4, 11, 18)):
            lit = not (f == 2 and g == 1)
            for j, row in enumerate(GLYPHS[(g + 1) % 4]):
                for i, b in enumerate(row):
                    if b == '1':
                        cv.set(7 + i, gy + j, 'neonP', (4 if (i + j) % 3 else 5) if lit else 1)
        cv.set(9, 25, 'neonC', 5); cv.set(10, 25, 'neonC', 5)
        frames.append(finish(cv))
    return frames


def neon_light(w, h):
    A = field(w, h)
    radial(A, 10, 15, 16, 0.55, squash=0.55)
    return A, rgb('#ff5ab0')


# --------------------------------------------------------------------------- ramen cart (yatai)
def yatai():
    frames = []
    W, H = 48, 37
    for f in range(3):
        cv = Canvas(W, H)
        # roof: a dark wooden board with a slight upturn at the ends; flat top
        cv.rect(2, 2, 45, 5, 'woodD', 3)
        cv.hline(2, 45, 2, 'woodD', 4); cv.hline(2, 45, 5, 'woodD', 1)
        cv.set(1, 1, 'woodD', 4); cv.set(46, 1, 'woodD', 2)
        # posts
        for px in (6, 41):
            cv.rect(px, 6, px + 1, 22, 'wood', 3); cv.vline(px, 6, 22, 'wood', 4)
        # noren: five red cloth panels with pale dot «writing»
        for i in range(5):
            x0 = 9 + i * 6
            cv.rect(x0, 6, x0 + 4, 12 + (i + f) % 2, 'noren', 3)
            cv.vline(x0, 6, 12, 'noren', 4); cv.vline(x0 + 4, 6, 12, 'noren', 2)
            cv.set(x0 + 2, 8, 'paper', 4); cv.set(x0 + 2, 10, 'paper', 3)
        # counter and the cart body
        cv.rect(3, 22, 44, 23, 'wood', 5); cv.hline(3, 44, 23, 'wood', 3)
        cv.rect(4, 24, 43, 33, 'wood', 3)
        for x in range(8, 43, 6):                            # planks
            cv.vline(x, 24, 33, 'wood', 2)
        cv.hline(4, 43, 24, 'wood', 1)
        cv.rect(18, 27, 29, 30, 'noren', 3); cv.hline(18, 29, 27, 'noren', 4)   # a little sign board
        for x in range(19, 29, 2):
            cv.set(x, 29, 'paper', 4)
        # wheels at both ends, seen edge-on
        for wx in (1, 45):
            cv.rect(wx, 26, wx + 1, 35, 'woodD', 3); cv.vline(wx, 26, 35, 'woodD', 4)
        cv.rect(5, 34, 42, 35, 'woodD', 2)
        # pot on the counter
        cv.rect(31, 17, 37, 21, 'pot', 3); cv.vline(31, 17, 21, 'pot', 4); cv.hline(31, 37, 17, 'pot', 5)
        cv.hline(30, 38, 16, 'pot', 2)
        cv.rect(11, 19, 14, 21, 'paper', 4); cv.hline(11, 14, 19, 'paper', 5)   # bowls
        cv.rect(17, 20, 19, 21, 'paper', 3)
        # red lantern hanging from the roof corner
        cv.vline(4, 6, 7, 'lblk', 3)
        for j, half in enumerate((1, 2, 2, 2, 2, 1)):
            for x in range(4 - half, 4 + half + 1):
                cv.set(x, 8 + j, 'paperR', 5 if x == 4 and 1 <= j <= 3 else 4 if x <= 4 else 3)
        cv.hline(3, 5, 14, 'lblk', 2)
        finish(cv)
        # steam rising from the pot (semi-transparent, drawn after the outline)
        cv.steam = f
        frames.append(cv)
    return frames


def yatai_steam(im, f):
    from PIL import Image
    for i in range(9):
        x = 34 + round(math.sin(i * 0.8 + f * 2.1) * 1.6)
        y = 15 - i
        if (i + f) % 3 != 2 and 0 <= y:
            im.alpha_composite(Image.new('RGBA', (1, 1), (236, 240, 246, 190 - i * 18)), (x, y))
            if i % 2:
                im.alpha_composite(Image.new('RGBA', (1, 1), (236, 240, 246, 120 - i * 10)), (x + 1, y))


def yatai_light(w, h):
    A = field(w, h)
    radial(A, 4, 11, 12, 0.55, down=1.3)
    cone(A, 24, 6, h - 2, 20, 0.32)
    return A, rgb('#ffb070')


# --------------------------------------------------------------------------- konbini
def konbini():
    W, H = 102, 59
    cv = Canvas(W, H)
    L, Rr = 2, 99
    cv.rect(L - 1, 1, Rr + 1, 3, 'wall', 3); cv.hline(L - 1, Rr + 1, 1, 'wall', 4)   # roof slab
    # lit sign band with two stripes and the name
    cv.rect(L, 4, Rr, 12, 'lit', 2)
    cv.hline(L, Rr, 4, 'lit', 3)
    cv.hline(L, Rr, 10, 'neonC', 3); cv.hline(L, Rr, 11, 'neonP', 3); cv.hline(L, Rr, 12, 'wall', 1)
    cx = (L + Rr) // 2
    text(cv, 'KONBINI', cx - 14, 5, rgb('#1c2a46'))
    # walls and windows
    cv.rect(L, 13, Rr, 55, 'wall', 3)
    cv.vline(L, 13, 55, 'wall', 4); cv.vline(Rr, 13, 55, 'wall', 2)
    rnd = random.Random(9)
    bays = [(L + 3, cx - 9), (cx + 9, Rr - 3)]
    for x0, x1 in bays:
        cv.rect(x0, 15, x1, 46, 'lit', 3)
        cv.hline(x0, x1, 15, 'lit', 5)
        for sy in (18, 25, 32, 39):                          # shelves of brightly packed goods
            x = x0 + 1
            while x + 2 <= x1:
                col = MAG[rnd.randrange(len(MAG))]
                w = rnd.choice((2, 2, 3))
                for xx in range(x, min(x + w, x1)):
                    for yy in range(sy, sy + 4):
                        cv.c(xx, yy, mix(col, (255, 255, 255), 0.3) if yy == sy else col if yy < sy + 3 else mix(col, (0, 0, 0), 0.3), 'lit')
                x += w + 1
            cv.hline(x0, x1, sy + 4, 'lit', 1)
        for xm in range(x0 + 11, x1, 12):                     # mullions
            cv.vline(xm, 15, 46, 'wall', 2)
        cv.rect(x0, 47, x1, 54, 'wall', 2)                   # low wall
        cv.hline(x0, x1, 47, 'wall', 4)
        for i in range(4):                                   # reflections
            cv.c(x0 + 3 + i, 22 - i, rgb('#ffffff'), 'lit')
    # sliding doors in the middle, lit inside, with a mat
    cv.rect(cx - 7, 15, cx + 7, 54, 'lit', 2)
    cv.vline(cx, 15, 54, 'wall', 2)
    cv.vline(cx - 7, 15, 54, 'wall', 1); cv.vline(cx + 7, 15, 54, 'wall', 1)
    cv.hline(cx - 7, cx + 7, 15, 'wall', 2)
    cv.rect(cx - 6, 30, cx - 1, 54, 'lit', 3); cv.rect(cx + 1, 30, cx + 6, 54, 'lit', 3)
    cv.hline(cx - 6, cx + 6, 28, 'neonP', 3)                  # door stripe
    cv.set(cx - 2, 38, 'wall', 0); cv.set(cx + 2, 38, 'wall', 0)   # handles
    cv.rect(L - 1, 56, Rr + 1, 57, 'stone', 2); cv.hline(L - 1, Rr + 1, 56, 'stone', 3)
    return [finish(cv)]


def konbini_light(w, h):
    A = field(w, h)
    cx = 50
    for lx in (cx - 26, cx + 26):
        cone(A, lx, 14, h - 2, 18, 0.3)
        pool(A, lx, h - 2, 20, 0.24)
    for x in range(w):                                        # glow round the lit sign band
        for y in range(0, 20):
            d = abs(y - 8) / 7
            if d < 1 and 1 <= x < w - 1:
                put(A, x, y, 0.16 * (1 - d) ** 1.5)
    radial(A, cx, 40, 16, 0.22, squash=0.6)
    return A, rgb('#cfe4f8')


# --------------------------------------------------------------------------- tea-house bench + parasol
def bench_asian():
    """a low wooden bench covered with red felt (like a tea-house bench) under a red paper parasol"""
    W, H = 36, 43
    cv = Canvas(W, H)
    # parasol: a wide shallow cone of red paper with ribs, on a bamboo pole
    cx = 18
    for i, half in enumerate((2, 5, 8, 11, 14, 16)):
        y = 1 + i
        for x in range(cx - half, cx + half + 1):
            rel = (x - (cx - half)) / (2 * half)
            t = 4 if rel < 0.35 else 3 if rel < 0.75 else 2
            cv.set(x, y, 'lacq', t)
    for x in range(cx - 16, cx + 17, 4):                    # ribs and a scalloped edge
        cv.set(x, 6, 'lacq', 1)
    cv.hline(cx - 16, cx + 16, 7, 'lacq', 2)
    cv.set(cx, 0, 'tgold', 4)
    cv.rect(cx, 8, cx, 32, 'bamboo', 4)                     # pole (behind the bench)
    # bench: red felt top hanging over the edges, dark wooden legs
    cv.rect(3, 31, 32, 33, 'noren', 4); cv.hline(3, 32, 31, 'noren', 5)
    cv.rect(3, 34, 32, 35, 'noren', 3)
    cv.hline(3, 32, 35, 'noren', 2)
    for x in (5, 30):
        cv.rect(x - 1, 36, x, 41, 'woodD', 3); cv.vline(x - 1, 36, 41, 'woodD', 4)
    cv.hline(5, 30, 37, 'woodD', 2)
    return [finish(cv)]


# --------------------------------------------------------------------------- classic wooden shop
def shop_wood():
    """a small old-style wooden shop (machiya): tiled roof, dark wooden lattice, indigo noren in the
    doorway, a vertical sign board with invented glyphs and two paper lanterns; warm light inside"""
    W, H = 84, 55
    cv = Canvas(W, H)
    # tiled roof with a ridge and slightly upturned ends
    cv.rect(4, 3, 79, 4, 'stone', 4)                        # ridge
    cv.hline(5, 78, 2, 'stone', 5)
    for y, (a, b) in zip(range(5, 11), ((3, 80), (2, 81), (2, 81), (1, 82), (1, 82), (0, 83))):
        cv.hline(a, b, y, 'stone', 3 if y % 2 else 2)
        for x in range(a + 1, b, 4):                        # tile rows
            cv.set(x, y, 'stone', 1 if y % 2 else 4)
    cv.set(0, 9, 'stone', 4); cv.set(83, 9, 'stone', 3)
    cv.hline(1, 82, 11, 'lblk', 2)                          # eave shadow
    # wooden front
    cv.rect(4, 12, 79, 51, 'woodD', 3)
    cv.vline(4, 12, 51, 'woodD', 4); cv.vline(79, 12, 51, 'woodD', 2)
    cv.hline(4, 79, 12, 'woodD', 1)
    # lattice windows (koshi) left and right, warm light glowing between the slats
    for x0, x1 in ((7, 30), (53, 76)):
        cv.rect(x0, 16, x1, 44, 'warm', 3)
        cv.hline(x0, x1, 16, 'warm', 4)
        for x in range(x0, x1 + 1, 2):
            cv.vline(x, 16, 44, 'woodD', 2 if x % 4 else 4)
        cv.hline(x0, x1, 30, 'woodD', 3)
        cv.rect(x0, 45, x1, 49, 'woodD', 2); cv.hline(x0, x1, 45, 'woodD', 4)
    # doorway with an indigo noren (split into three panels), lit inside
    d0, d1 = 34, 49
    cv.rect(d0, 14, d1, 51, 'warm', 2)
    cv.rect(d0 + 2, 30, d1 - 2, 51, 'warm', 3)
    for i in range(3):
        x = d0 + i * 5 + 1
        cv.rect(x, 14, x + 3, 26, 'vmB', 2); cv.vline(x, 14, 26, 'vmB', 3)
    cv.rect(d0 + 6, 19, d0 + 9, 21, 'paper', 4); cv.set(d0 + 7, 20, 'vmB', 2)   # white crest
    cv.vline(d0 - 1, 13, 51, 'woodD', 4); cv.vline(d1 + 1, 13, 51, 'woodD', 2)
    # vertical sign board left of the door with invented strokes
    cv.rect(31, 14, 33, 34, 'wood', 4); cv.vline(33, 14, 34, 'wood', 2)
    for y in (16, 19, 20, 23, 26, 27, 30):
        cv.set(32, y, 'lblk', 2)
    cv.hline(31, 33, 22, 'lblk', 3)
    # two paper lanterns hanging under the eave, white with a red band
    for lx in (8, 75):
        cv.vline(lx, 12, 13, 'lblk', 3)
        for j, half in enumerate((1, 2, 2, 2, 2, 1)):
            for x in range(lx - half, lx + half + 1):
                cv.set(x, 14 + j, 'paper', 5 if x == lx else 4 if x < lx else 3)
        cv.hline(lx - 2, lx + 2, 16, 'paperR', 3)
        cv.hline(lx - 1, lx + 1, 20, 'lblk', 2)
    # stone step and a potted plant
    cv.rect(32, 52, 51, 53, 'stone', 4)
    cv.rect(2, 47, 5, 51, 'stone', 3); cv.rect(2, 42, 5, 46, 'green', 3); cv.set(3, 42, 'green', 5)
    return [finish(cv)]


def shop_wood_light(w, h):
    A = field(w, h)
    for lx in (8, 75):
        radial(A, lx, 17, 11, 0.45, down=1.3)
    cone(A, 41, 26, h - 2, 14, 0.28)
    pool(A, 41, h - 2, 14, 0.3)
    return A, rgb('#ffc070')


TOKYO = [
    # name, frames function, fps, top (0 = not standable), light
    ('bin_tokyo', bin_tokyo, 1, None, None),
    ('vending', vending, 1, None, vending_light),
    ('lanterns', lanterns, 2, 0, lanterns_light),
    ('neon', neon, 6, 0, neon_light),
    ('yatai', yatai, 6, None, yatai_light),
    ('konbini', konbini, 1, None, konbini_light),
    ('bench_asian', bench_asian, 1, 13, None),
    ('shop_wood', shop_wood, 1, None, shop_wood_light),
]
