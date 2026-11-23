#!/usr/bin/env python3
"""Enemy ninjas: three kinds, the girls' height (30 px), facing LEFT (they run at the girls).

Drawn on the pixel grid from a small pose skeleton (hips, knees, feet, shoulders, elbows, hands),
in the props/girls style: outlines tinted per material, 3–4 tone shading, hand-AA'd corners.
They are made to look nothing like the girls in ninja mode (navy, pink scarf, ponytail):
  ninja       «Shadow»: ash-grey gi, black hood, long red headband, glowing yellow eyes; throws stars
  ninja_oni   «Oni»: crimson gi, white horned oni mask, katana
  ninja_kasa  «Wanderer»: teal-olive gi, wide straw kasa hat, ragged ochre scarf, short sword

Sheet assets/sprites/ninjas.png: one kind per row, CELL_W × CELL_H cells, body centred on
x = CELL_W // 2, feet on the bottom row. Columns (the same for every kind):
  0 idle0  1 idle1  2–7 run0…run5  8 crouch (jump take-off / landing)  9 jumpUp  10 jumpDown
  11 atk0 (wind-up)  12 atk1 (strike / throw)  13 atk2 (follow-through)
JSON assets/sprites/ninjas.json: {"cell": [w, h], "anims": {name: [cols]…}, "fps": {…},
  "kinds": {kind: {row, w, h}}}   (w × h = visible size of the run frames, used as the hitbox)
Usage: python3 tools/sprites/ninjas.py
"""
import json
import math
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from props import Canvas, RAMP, rgb, mix  # noqa: E402

CELL_W, CELL_H = 40, 32
CX = CELL_W // 2
GY = CELL_H - 2            # lowest drawn row (the outline takes the bottom row)

COLS = ['idle0', 'idle1', 'run0', 'run1', 'run2', 'run3', 'run4', 'run5', 'crouch', 'jumpUp', 'jumpDown',
        'atk0', 'atk1', 'atk2']
ANIMS = {'idle': [0, 1], 'run': [2, 3, 4, 5, 6, 7], 'crouch': [8], 'jumpUp': [9], 'jumpDown': [10],
         'attack': [11, 12, 13]}
FPS = {'idle': 3, 'run': 12, 'attack': 10}

R = lambda *c: [rgb(x) for x in c]
RAMP.update({
    # Shadow
    'ash':    R('#15161c', '#2c2f3a', '#454a58', '#636a7c', '#8a92a6', '#b8c0d0'),
    'blk':    R('#07080c', '#101219', '#1a1d27', '#262a38', '#363c50', '#4c5470'),
    'band':   R('#3a0608', '#7a0e14', '#b0161e', '#e02a2a', '#ff5a4a', '#ff9a8a'),
    'eyeY':   R('#5a4000', '#a07800', '#e0b000', '#ffe040', '#fff4a0', '#ffffff'),
    # Oni
    'crim':   R('#2a0610', '#5a0c1c', '#8a1428', '#b8203a', '#e04458', '#ff8a9a'),
    'mask':   R('#4a4038', '#9a9080', '#c8c0b0', '#ece6da', '#fbf8f0', '#ffffff'),
    'horn':   R('#3a2a10', '#6a5020', '#9a7a3a', '#c8a85a', '#e8cc80', '#fff0c0'),
    # Wanderer
    'teal':   R('#08201e', '#123a36', '#1c564e', '#2a7468', '#3f9686', '#76c4b0'),
    'straw':  R('#3a2a10', '#7a5a24', '#a88038', '#d0a850', '#ecc870', '#fff0b0'),
    'ochre':  R('#3a2208', '#7a4a12', '#b06e1c', '#e09a2a', '#ffc04a', '#ffe2a0'),
    # shared
    'skin':   R('#4a2a1c', '#9a6a50', '#d0a080', '#f0c8a6', '#ffe0c8', '#fff4ea'),
    'blade':  R('#262a38', '#5a6276', '#9aa4b8', '#cdd6e4', '#eef3fa', '#ffffff'),
    'gold':   R('#3a2808', '#7a5a10', '#b08a1c', '#e0b830', '#ffe070', '#fff6c0'),
    'grip':   R('#0e0c10', '#1e1a22', '#2e2834', '#40384a', '#584e66', '#766a88'),
})

KIND = {
    'ninja':      dict(gi='ash', hood='blk', trim='band', legs='blk', arms='ash', weapon='star'),
    'ninja_oni':  dict(gi='crim', hood='blk', trim='gold', legs='blk', arms='crim', weapon='katana'),
    'ninja_kasa': dict(gi='teal', hood='teal', trim='ochre', legs='grip', arms='teal', weapon='short'),
}


class N(Canvas):
    def __init__(self):
        super().__init__(CELL_W, CELL_H)

    def dot(self, x, y, mat, tone, w=1):
        for dx in range(w):
            for dy in range(w):
                self.set(round(x) + dx - w // 2, round(y) + dy - w // 2 + (0 if w < 2 else 0), mat, tone)

    def seg(self, a, b, mat, tone, w=2):
        n = max(1, round(max(abs(b[0] - a[0]), abs(b[1] - a[1]))))
        for i in range(n + 1):
            x = a[0] + (b[0] - a[0]) * i / n
            y = a[1] + (b[1] - a[1]) * i / n
            for dx in range(w):
                for dy in range(w):
                    self.set(round(x) - w // 2 + dx, round(y) - w // 2 + dy, mat, tone)


# ----------------------------------------------------------------------------- poses
def pose(col):
    """A pose: offsets relative to the default stance. All x are relative to CX, facing left (−x)."""
    P = dict(lift=0, bob=0, lean=0, legF=((-2, 26), (-3, 30)), legB=((2, 26), (2, 30)),
             armF=((-4, 17), (-6, 20)), armB=((3, 17), (4, 20)), wep='rest', scarf=0, squat=0)
    if col in ('idle0', 'idle1'):
        b = 1 if col == 'idle1' else 0
        P.update(bob=b, legF=((-3, 26), (-4, 30)), legB=((3, 26), (3, 30)),
                 armF=((-5, 17 + b), (-7, 20 + b)), armB=((4, 17 + b), (5, 20 + b)), scarf=b)
    elif col.startswith('run'):
        i = int(col[3:])
        a = 2 * math.pi * i / 6
        def leg(ph):
            fx = -5 * math.cos(ph)                      # foot forward (−x) … back
            fl = max(0.0, 3 * math.sin(ph))             # lift when swinging forward
            kx = fx * 0.4 - (1.5 if fl > 0.5 else 0.5)  # knee leads
            return ((kx, 26 - fl * 0.6), (fx, 30 - fl))
        bob = 0 if i in (0, 3) else -1 if i in (1, 4) else 0
        P.update(bob=bob, lean=-1, legF=leg(a), legB=leg(a + math.pi), scarf=i % 3)
        sw = 4 * math.cos(a)                             # arms swing opposite to the legs
        P.update(armF=((-3 + sw * 0.5, 18), (-4 + sw, 21)), armB=((3 - sw * 0.5, 18), (3 - sw, 21)))
    elif col == 'crouch':
        P.update(squat=3, lean=-1, legF=((-5, 27), (-4, 30)), legB=((4, 27), (3, 30)),
                 armF=((-5, 20), (-7, 23)), armB=((4, 20), (6, 22)))
    elif col == 'jumpUp':
        P.update(lift=0, lean=-1, legF=((-6, 22), (-3, 25)), legB=((1, 24), (5, 26)),
                 armF=((-5, 14), (-7, 11)), armB=((4, 15), (6, 13)), scarf=2)
    elif col == 'jumpDown':
        P.update(legF=((-5, 25), (-7, 29)), legB=((4, 25), (6, 28)),
                 armF=((-6, 16), (-8, 15)), armB=((5, 16), (7, 15)), scarf=1)
    elif col == 'atk0':
        P.update(lean=1, legF=((-4, 26), (-6, 30)), legB=((3, 26), (4, 30)),
                 armF=((-2, 16), (2, 14)), armB=((4, 16), (6, 14)), wep='wind')
    elif col == 'atk1':
        P.update(lean=-2, legF=((-6, 26), (-8, 30)), legB=((3, 26), (5, 30)),
                 armF=((-7, 17), (-11, 17)), armB=((4, 17), (6, 20)), wep='strike', scarf=2)
    elif col == 'atk2':
        P.update(lean=-2, legF=((-6, 26), (-8, 30)), legB=((3, 26), (5, 30)),
                 armF=((-7, 19), (-10, 22)), armB=((4, 18), (6, 21)), wep='follow', scarf=1)
    return P


def draw(kind, col):
    K = KIND[kind]
    P = pose(col)
    cv = N()
    oy = P['bob'] + P['squat']                    # moves the upper body down
    lx = P['lean']
    X = lambda dx: CX + dx
    hipY = 21 + P['squat']
    sh = 13 + oy                                  # shoulder row

    def leg(pts, back):
        knee, foot = pts
        hip = (X(1 if back else -1) + lx * 0.3, hipY + 1)
        k = (X(knee[0]), knee[1] + P['squat'] * 0.4)
        f = (X(foot[0]), min(GY, foot[1]))
        t = 2 if back else 3
        cv.seg(hip, k, K['legs'], t, 3)
        cv.seg(k, f, K['legs'], t - 1 if back else t, 2)
        # shin wraps
        cv.seg(((k[0] + f[0]) / 2, (k[1] + f[1]) / 2), f, K['gi'] if kind != 'ninja' else 'ash', 2 if back else 4, 2)
        # foot (tabi), pointing left
        fx, fy = round(f[0]), round(f[1])
        cv.rect(fx - 2, fy, fx + 1, fy, 'grip', 2 if back else 3)
        cv.set(fx - 2, fy, 'grip', 4 if not back else 2)

    def arm(pts, back):
        el, hand = pts
        s = (X(-2 if not back else 3) + lx, sh + 2)
        e = (X(el[0]) + lx, el[1] + oy)
        h = (X(hand[0]) + lx, hand[1] + oy)
        cv.seg(s, e, K['arms'], 2 if back else 4, 2)
        cv.seg(e, h, K['arms'], 1 if back else 3, 2)
        cv.dot(h[0], h[1], 'grip', 3 if not back else 2, 2)   # glove
        return h

    # scarf / headband tails streaming back (right)
    def tails():
        tm = K['trim']
        y0 = sh - 5 if kind == 'ninja' else sh + 1
        x0 = X(4) + lx
        wav = [0, 1, 1, 0, -1, 0, 1]
        n = 8 if kind != 'ninja_oni' else 0
        for i in range(n):
            y = y0 + i // 3 + ((wav[(i + P['scarf']) % len(wav)]) if i > 1 else 0)
            cv.set(x0 + i, y, tm, 4 if i < 3 else 3)
            if kind == 'ninja_kasa':
                cv.set(x0 + i, y + 1, tm, 2)
            elif i < 6:
                cv.set(x0 + i, y + 1, tm, 2)

    # weapon behind the body (wind-up / rest on the back)
    def weapon(stage, hand):
        w = K['weapon']
        if w == 'star':
            if stage in ('wind', 'strike'):
                hx, hy = round(hand[0]), round(hand[1])
                for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0)):
                    cv.set(hx + dx, hy + dy, 'blade', 4)
                for dx, dy in ((-1, -1), (1, 1), (-1, 1), (1, -1)):
                    cv.set(hx + dx, hy + dy, 'blade', 2)
                cv.set(hx, hy, 'blk', 2)
            return
        long = 12 if w == 'katana' else 8
        hx, hy = hand
        if stage == 'rest':          # held low, pointing forward-down
            d = (-0.85, 0.5)
        elif stage == 'wind':        # raised back over the shoulder
            d = (0.75, -0.65)
        elif stage == 'strike':      # straight forward
            d = (-1, -0.05)
        else:                        # follow-through, low forward
            d = (-0.8, 0.6)
        # grip (2 px) behind the hand, guard, then the blade
        gx, gy = hx - d[0] * 2, hy - d[1] * 2
        cv.seg((gx, gy), (hx, hy), 'grip', 3, 1)
        cv.set(round(hx + d[0]), round(hy + d[1]), 'gold', 4)
        bx, by = hx + d[0] * 2, hy + d[1] * 2
        ex, ey = hx + d[0] * long, hy + d[1] * long
        cv.seg((bx, by), (ex, ey), 'blade', 4, 1)
        # a darker back edge so the blade reads at 1 px
        cv.seg((bx - d[1] * 0.0 + (1 if abs(d[1]) > 0.5 else 0), by + (1 if abs(d[1]) <= 0.5 else 0)),
               (ex + (1 if abs(d[1]) > 0.5 else 0), ey + (1 if abs(d[1]) <= 0.5 else 0)), 'blade', 2, 1)
        cv.set(round(ex), round(ey), 'blade', 5)
        if stage == 'strike':        # speed streak
            for i in range(3, long, 2):
                cv.set(round(hx + d[0] * i), round(hy + d[1] * i) - 2, 'blade', 5)

    # ---- draw back to front
    tails()
    hb = arm(P['armB'], True)
    leg(P['legB'], True)
    # torso: gi with a crossed collar and a sash
    tx0, tx1 = X(-4) + lx, X(3) + lx
    cv.rect(tx0, sh, tx1, hipY, K['gi'], 3)
    cv.vline(tx0, sh, hipY, K['gi'], 4); cv.vline(tx1, sh, hipY, K['gi'], 2)
    cv.set(tx0 + 1, sh + 1, K['gi'], 4)
    for i in range(4):                                   # collar fold
        cv.set(tx0 + 2 + i, sh + i, K['gi'], 1 if i else 2)
    sash = K['trim'] if kind != 'ninja' else 'band'
    cv.rect(tx0, hipY - 2, tx1, hipY - 1, sash, 3)
    cv.hline(tx0, tx1, hipY - 2, sash, 4)
    cv.set(tx1 + 1, hipY - 1, sash, 3); cv.set(tx1 + 2, hipY, sash, 2)    # knot tail
    cv.rect(tx0, hipY, tx1, hipY + 1, K['legs'], 2)                       # hakama top
    leg(P['legF'], False)
    head(cv, kind, X(-1) + lx, sh, P)
    hf = arm(P['armF'], False)
    weapon(P['wep'], hf)
    cv.outline()
    cv.soften()
    return cv


def head(cv, kind, cx, sh, P):
    """Head of 9 × 9 px above the shoulders, face to the left."""
    K = KIND[kind]
    x0, x1, y0, y1 = cx - 4, cx + 4, sh - 9, sh - 1
    if kind == 'ninja':
        cv.rect(x0, y0, x1, y1, 'blk', 3)
        cv.hline(x0 + 1, x1 - 1, y0, 'blk', 4)
        cv.vline(x1, y0 + 1, y1, 'blk', 2)
        cv.set(x0 + 1, y0 + 1, 'blk', 5)
        cv.clear(x0, y0); cv.clear(x1, y0); cv.clear(x1, y1 - 0)   # rounded skull
        cv.set(x0 + 1, y0, 'blk', 4)
        # red headband across the forehead
        cv.hline(x0, x1, y0 + 2, 'band', 3); cv.hline(x0, x1 - 2, y0 + 3, 'band', 2)
        cv.set(x0, y0 + 2, 'band', 4)
        # eye slit with glowing yellow eyes (2 px each, facing left)
        cv.hline(x0, x0 + 5, y0 + 5, 'blk', 0)
        cv.set(x0 + 1, y0 + 5, 'eyeY', 4); cv.set(x0 + 2, y0 + 5, 'eyeY', 3)
        cv.set(x0 + 4, y0 + 5, 'eyeY', 3)
        cv.set(x0 + 1, y0 + 4, 'eyeY', 1)
        # cloth mask folds
        cv.hline(x0 + 1, x0 + 4, y0 + 7, 'blk', 2)
    elif kind == 'ninja_oni':
        cv.rect(x0, y0 + 1, x1, y1, 'blk', 2)
        cv.vline(x1, y0 + 1, y1, 'blk', 1)
        cv.hline(x0 + 2, x1 - 2, y0 + 1, 'blk', 3)
        cv.clear(x0, y0 + 1); cv.clear(x1, y0 + 1)
        # short horns rising from the hood
        for hx in (x0 + 1, x1 - 2):
            cv.set(hx, y0, 'horn', 4); cv.set(hx + 1, y0, 'horn', 2)
        # white oni mask over the front of the face: brows, fangs, red markings
        mx0, mx1 = x0, x0 + 6
        cv.rect(mx0, y0 + 2, mx1, y1 - 1, 'mask', 3)
        cv.hline(mx0 + 1, mx1, y0 + 2, 'mask', 4)
        cv.vline(mx1, y0 + 3, y1 - 1, 'mask', 2)
        cv.hline(mx0, mx0 + 4, y0 + 3, 'crim', 3)          # angry red brows
        cv.set(mx0 + 1, y0 + 4, 'blk', 0); cv.set(mx0 + 4, y0 + 4, 'blk', 0)   # eye holes
        cv.set(mx0 + 1, y0 + 4, 'band', 3)                  # a red glint
        cv.hline(mx0, mx0 + 4, y1 - 2, 'blk', 1)            # mouth
        cv.set(mx0 + 1, y1 - 2, 'mask', 5); cv.set(mx0 + 3, y1 - 2, 'mask', 5)  # fangs
        cv.set(mx0 + 5, y0 + 6, 'crim', 4)                  # cheek mark
    else:  # kasa
        cv.rect(x0 + 1, y0 + 3, x1, y1, 'teal', 2)
        # face in the hat's shadow: dark, one bright eye
        cv.rect(x0, y0 + 4, x0 + 4, y1 - 1, 'grip', 2)
        cv.set(x0 + 1, y0 + 5, 'skin', 4); cv.set(x0 + 2, y0 + 5, 'skin', 3)
        cv.hline(x0, x0 + 4, y1 - 1, 'teal', 1)             # face cloth
        cv.hline(x0, x0 + 5, y1 - 2, 'teal', 3)
        # wide conical straw hat: 15 px across, 4 px tall, slightly tilted forward
        hx = cx
        rows = [(hx - 1, hx + 1), (hx - 3, hx + 3), (hx - 5, hx + 5), (hx - 7, hx + 7)]
        for i, (a, b) in enumerate(rows):
            y = y0 + i
            cv.hline(a, b, y, 'straw', 3)
            cv.set(a, y, 'straw', 4); cv.set(b, y, 'straw', 2)
            if i == 3:
                cv.hline(a, b, y, 'straw', 2); cv.set(a, y, 'straw', 3)
        cv.set(hx, y0, 'straw', 5); cv.set(hx - 2, y0 + 1, 'straw', 4)
        for x in range(hx - 6, hx + 6, 3):                   # weave lines
            cv.set(x, y0 + 2, 'straw', 1)


ORDER = ['ninja', 'ninja_oni', 'ninja_kasa']

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
    sheet = Image.new('RGBA', (CELL_W * len(COLS), CELL_H * len(ORDER)), (0, 0, 0, 0))
    kinds = {}
    for row, kind in enumerate(ORDER):
        boxes = []
        for c, col in enumerate(COLS):
            im = draw(kind, col).image()
            sheet.alpha_composite(im, (c * CELL_W, row * CELL_H))
            if col.startswith('run'):
                boxes.append(im.getbbox())
        x0 = min(b[0] for b in boxes); x1 = max(b[2] for b in boxes); y0 = min(b[1] for b in boxes)
        kinds[kind] = {'row': row, 'w': min(x1 - x0, 18), 'h': CELL_H - y0}
    sheet.save(root / 'ninjas.png')
    meta = {'cell': [CELL_W, CELL_H], 'anims': ANIMS, 'fps': FPS, 'kinds': kinds}
    (root / 'ninjas.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote', root / 'ninjas.png', sheet.size, kinds)
