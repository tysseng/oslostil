#!/usr/bin/env python3
"""Trees at girl scale, front view, drawn on the pixel grid in the props style.

  oslo_bare    level 4 (British-style Oslo, at night): a bare deciduous tree ......... ≈ 90 px
  oslo_leafy   a tall linden-like tree with an oval crown, dark night greens .......... ≈ 92 px
  oslo_leafy2  a broader, rounder crown (chestnut/maple-like) ......................... ≈ 84 px
  sakura       Tokyoslo: a spreading cherry tree in full pink bloom (no loose petals) . ≈ 70 px
  sakura2      a smaller, rounder cherry tree ......................................... ≈ 63 px

Branches are grown from a seeded recursive skeleton; crowns are unions of leaf/blossom clumps,
each shaded from the top left (4 tones), with an irregular edge, a tinted outline and hand-AA'd
corners. Trees are scenery: not standable (top 0), drawn behind the characters.
Sheet assets/sprites/trees.png: one tree per row, CELL_W × CELL_H cells, trunk centred on
x = CELL_W // 2, base on the bottom row. JSON assets/sprites/trees.json: {name: {row, frames, fps, w, h, top}}.
Usage: python3 tools/sprites/trees.py
"""
import json
import math
import random
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from props import Canvas, RAMP, rgb, mix  # noqa: E402

CELL_W, CELL_H = 100, 100
CX, GY = CELL_W // 2, CELL_H - 2

R = lambda *c: [rgb(x) for x in c]
RAMP.update({
    'barkN':  R('#050607', '#0e1112', '#181c1e', '#23282a', '#30363a', '#444c50'),
    'leafN':  R('#040c0a', '#0a1a14', '#10281e', '#18382a', '#224a38', '#33624c'),
    'leafN2': R('#060c06', '#0e1a0e', '#162816', '#203a20', '#2c4e2a', '#40663a'),
    'barkS':  R('#0a0406', '#1a0c10', '#2a141a', '#3a1e24', '#4e2a30', '#6a3a42'),
    'sakura': R('#3a0c22', '#8a2e5a', '#c45a8a', '#e888b0', '#ffb6d2', '#ffe2ee'),
})


def grow(seed, trunk_h, spread, depth, length, shrink=0.72, lean=0.0, wide=1.0):
    """branch skeleton: list of (x0, y0, x1, y1, width) and the tips"""
    rnd = random.Random(seed)
    segs, tips = [], []

    def branch(x, y, ang, ln, w, d):
        x1 = x + math.sin(ang) * ln * wide
        y1 = y - math.cos(ang) * ln
        segs.append((x, y, x1, y1, w))
        if d == 0:
            tips.append((x1, y1))
            return
        n = 2 if rnd.random() < 0.75 else 3
        for i in range(n):
            a = ang + (i - (n - 1) / 2) * spread + rnd.uniform(-0.18, 0.18)
            branch(x1, y1, a, ln * rnd.uniform(shrink - 0.08, shrink + 0.06), max(1, w * 0.62), d - 1)

    segs.append((CX, GY, CX + lean, GY - trunk_h, 6))
    for a in (-spread * 0.8, spread * 0.15, spread * 0.9):   # the trunk splits into three limbs
        branch(CX + lean, GY - trunk_h, a + rnd.uniform(-0.1, 0.1), length, 3.6, depth)
    return segs, tips


def draw_wood(cv, segs, mat):
    for x0, y0, x1, y1, w in segs:
        n = max(1, round(max(abs(x1 - x0), abs(y1 - y0))))
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            ww = w if w < 5 else w - (w - 4) * t           # the trunk tapers
            half = ww / 2
            for dx in range(-math.ceil(half), math.ceil(half) + 1):
                if abs(dx) <= half:
                    rel = (dx + half) / max(1, 2 * half)
                    tone = 4 if rel < 0.3 else 3 if rel < 0.65 else 2
                    if ww < 2:
                        tone = 3
                    cv.set(round(x + dx), round(y), mat, tone)
    # flared roots
    for dx, t in ((-5, 2), (-4, 3), (4, 2), (5, 1)):
        cv.set(CX + dx, GY, mat, t)
    cv.set(CX - 4, GY - 1, mat, 3); cv.set(CX + 4, GY - 1, mat, 2)


def crown(cv, tips, mat, seed, r0, r1, extra=0, squash=1.0, holes=0.0):
    """union of round clumps at the branch tips, shaded from the top left"""
    rnd = random.Random(seed)
    clumps = []
    for x, y in tips:
        clumps.append((x + rnd.uniform(-2, 2), y + rnd.uniform(-2, 1), rnd.uniform(r0, r1)))
    for _ in range(extra):                                  # fill between the tips
        a, b = rnd.sample(tips, 2)
        t = rnd.random()
        clumps.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + rnd.uniform(-2, 3), rnd.uniform(r0, r1)))
    clumps.sort(key=lambda c: c[1])                         # upper clumps first, lower ones on top
    for cx, cy, r in clumps:
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
                dx, dy = (x - cx) / r, (y - cy) / (r * squash)
                d = dx * dx + dy * dy
                if d > 1:
                    continue
                if d > 0.75 and ((x * 7 + y * 13) % 5 == 0):  # ragged edge
                    continue
                light = -(dx * 0.55 + dy * 0.85)              # from the top left
                n = (((x * 73856093) ^ (y * 19349663)) % 97) / 97 - 0.5   # leaf texture (hashed, no stripes)
                v = light * 0.7 + n * 0.45 - d * 0.35
                tone = 5 if v > 0.55 else 4 if v > 0.18 else 3 if v > -0.2 else 2 if v > -0.55 else 1
                if holes and rnd.random() < holes and d < 0.6:
                    continue
                cv.set(x, y, mat, tone)


def petals(cv, seed, n, box, mat='sakura'):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        cv.set(rnd.randrange(x0, x1), rnd.randrange(y0, y1), mat, rnd.choice((4, 5)))


def tree(name):
    cv = Canvas(CELL_W, CELL_H)
    if name == 'oslo_bare':
        segs, tips = grow(3, 30, 0.5, 4, 17, shrink=0.78, wide=1.15)
        draw_wood(cv, segs, 'barkN')
    elif name == 'oslo_leafy':
        segs, tips = grow(11, 30, 0.38, 3, 17, shrink=0.82, wide=1.0)
        draw_wood(cv, segs, 'barkN')
        crown(cv, tips, 'leafN', 5, 8, 11, extra=34, squash=1.1)
    elif name == 'oslo_leafy2':
        segs, tips = grow(21, 28, 0.5, 3, 15, shrink=0.78, wide=1.05)
        draw_wood(cv, segs, 'barkN')
        crown(cv, tips, 'leafN2', 8, 8, 12, extra=30, squash=0.9)
    elif name == 'sakura':
        segs, tips = grow(7, 20, 0.58, 3, 14, shrink=0.8, wide=1.25, lean=1)
        draw_wood(cv, segs, 'barkS')
        crown(cv, tips, 'sakura', 2, 7, 10, extra=30, squash=0.8)
    elif name == 'sakura2':
        segs, tips = grow(17, 18, 0.55, 3, 12, shrink=0.8, wide=1.1)
        draw_wood(cv, segs, 'barkS')
        crown(cv, tips, 'sakura', 9, 7, 10, extra=24, squash=0.85)
    # a few of the branches show through the crown, then outline
    if name != 'oslo_bare':
        for x0, y0, x1, y1, w in segs[1:4]:
            pass
    cv.outline()
    cv.soften()
    return cv


ORDER = ['oslo_bare', 'oslo_leafy', 'oslo_leafy2', 'sakura', 'sakura2']

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
    sheet = Image.new('RGBA', (CELL_W, CELL_H * len(ORDER)), (0, 0, 0, 0))
    meta = {}
    for row, name in enumerate(ORDER):
        im = tree(name).image()
        x0, y0, x1, y1 = im.getbbox()
        assert y0 > 0 and x0 > 0 and x1 < CELL_W, (name, im.getbbox())
        sheet.alpha_composite(im, (0, row * CELL_H))
        meta[name] = {'row': row, 'frames': 1, 'fps': 1, 'w': x1 - x0, 'h': CELL_H - y0, 'top': 0}
    sheet.save(root / 'trees.png')
    (root / 'trees.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote', root / 'trees.png', sheet.size)
    for n in ORDER:
        print(f"  {n:12s} {meta[n]['w']:3d} × {meta[n]['h']:3d}")
