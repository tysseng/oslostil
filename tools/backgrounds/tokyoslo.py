#!/usr/bin/env python3
"""Pixel-art background layers for Tokyoslo (stage 4 after 1:42.0, stages 5–7).

Oslo's classic buildings with Asian features: curved, tiered roofs with upturned eaves, lanterns,
neon signs with invented glyphs (no real text or brands) and one rooftop billboard that reads TOKYOSLO.
Drawn 1:1 in game pixels (320 × 180 screen, ground at y = 150), night palette for the red sky
(SKY.map2 #2a0610 → #7a1430).

Outputs (transparent PNGs, bottom row = the ground line):
  assets/backgrounds/tokyoslo-buildings.png   the street of landmarks (mid layer)
  assets/backgrounds/tokyoslo-far.png         distant skyline silhouette (farthest layer)
Usage: python3 tools/backgrounds/tokyoslo.py
"""
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops

H = 150  # layer height; the bottom row sits on GROUND


def rgb(h, a=255):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


P = {k: rgb(v) for k, v in dict(
    out='#0c0410',
    # roofs: dark tiles with a cool highlight and gold trim
    roof='#1a1426', roof2='#251c38', roof_hi='#3d3160', tile='#120d1c', gold='#e0a83e', gold_dk='#8a5a1c',
    # walls at night
    brick='#4a1a22', brick2='#5e2630', brick_hi='#753540',
    stone='#4e3e58', stone2='#625070', stone_hi='#7e6a8c',
    ochre='#5a3c38', ochre2='#704c40', ochre_hi='#8a6050',
    dark='#22101e', dark2='#2e1628', dark_hi='#40203a',
    win='#ffc864', win2='#ff9440', win_off='#150812', clock='#e8dcc0',
    lan='#e8253a', lan_hi='#ffd25a', lan_dk='#8a1020', cord='#2a1020',
    far='#4c1129', far2='#5e1834', far_hi='#74223f', far_win='#d05070',
).items()}
NEON = [rgb(c) for c in ('#ff3ea5', '#3ef0ff', '#ffe14a', '#5dff8a', '#ff5a3c', '#c86bff')]


class Layer:
    def __init__(self, w, h=H):
        self.w, self.h = w, h
        self.im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        self.neon = Image.new('RGBA', (w, h), (0, 0, 0, 0))   # neon strokes get a pixel halo
        self.d = ImageDraw.Draw(self.im)
        self.n = ImageDraw.Draw(self.neon)

    def rect(self, x0, y0, x1, y1, c, outline=None):
        self.d.rectangle([x0, y0, x1, y1], fill=c, outline=outline)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.d.point((x, y), fill=c)

    def nrect(self, x0, y0, x1, y1, c, outline=None):
        self.n.rectangle([x0, y0, x1, y1], fill=c, outline=outline)

    def npx(self, x, y, c):
        self.n.point((x, y), fill=c)

    # ---- building parts
    def wall(self, x0, y0, x1, y1, kind):
        c, c2, hi = P[kind], P[kind + '2'], P[kind + '_hi']
        self.rect(x0, y0, x1, y1, c, P['out'])
        for y in range(y0 + 3, y1, 4):                       # brick / stone courses
            self.d.line([(x0 + 1, y), (x1 - 1, y)], fill=c2)
        self.d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=hi)

    def windows(self, x0, y0, x1, y1, w=3, h=4, gx=3, gy=4, lit=0.55, seed=0, arch=False):
        r = random.Random(seed)
        y = y0
        while y + h <= y1:
            x = x0
            while x + w <= x1:
                on = r.random() < lit
                c = (P['win'] if r.random() < 0.75 else P['win2']) if on else P['win_off']
                self.rect(x, y, x + w - 1, y + h - 1, c)
                if arch:
                    self.px(x, y, P['out']); self.px(x + w - 1, y, P['out'])
                if on:
                    self.px(x, y + h - 1, P['win2'])
                x += w + gx
            y += h + gy

    def roof(self, cx, base, half, height, up=3, thick=3, gold=True, ridge=True):
        """Curved Asian roof seen from the front: concave slopes, eaves flicking up at the tips."""
        top = {}
        for x in range(cx - half, cx + half + 1):
            t = abs(x - cx) / half
            yt = base - height + height * (t ** 0.55) - up * (t ** 7)
            yb = base - up * (t ** 4) + thick * (1 - t ** 3) * 0.6
            top[x] = (round(yt), round(yb))
            self.d.line([(x, round(yt)), (x, round(yb))], fill=P['roof'])
            if (x - cx) % 3 == 0 and abs(x - cx) < half - 1:   # tile rows
                self.d.line([(x, round(yt) + 1), (x, round(yb) - 1)], fill=P['tile'])
        for x, (yt, yb) in top.items():
            self.px(x, yt, P['roof_hi'])
            self.px(x, yb, P['gold'] if gold else P['roof_hi'])
            self.px(x, yb + 1, P['out'])
        # upturned tips
        for s in (-1, 1):
            x = cx + s * half
            yt, yb = top[x]
            self.px(x + s, yt - 1, P['gold'] if gold else P['roof_hi'])
            self.px(x + s, yt - 2, P['gold'] if gold else P['roof_hi'])
        if ridge:
            yt = top[cx][0]
            self.d.line([(cx - half // 3, yt), (cx + half // 3, yt)], fill=P['roof2'])
            self.d.line([(cx - half // 3, yt - 1), (cx + half // 3, yt - 1)], fill=P['out'])
            for s in (-1, 1):                                # ridge-end ornaments
                ex = cx + s * (half // 3)
                self.px(ex, yt - 2, P['gold']); self.px(ex + s, yt - 3, P['gold'])
        return top[cx][0]

    def pagoda(self, cx, base, width, tiers, tier_h=9, shrink=0.75, body='brick'):
        """Stacked roofs on a narrowing body; returns the y of the top finial."""
        y = base
        w = width
        for i in range(tiers):
            bw = max(4, int(w * 0.55))
            self.wall(cx - bw // 2, y - tier_h, cx + bw // 2, y, body)
            if tier_h >= 7:
                self.rect(cx - bw // 2 + 2, y - tier_h + 3, cx + bw // 2 - 2, y - 3, P['win'])
            ry = self.roof(cx, y - tier_h + 2, w // 2, max(4, tier_h - 2), up=2 + (i == 0), ridge=(i == tiers - 1))
            y = ry
            w = int(w * shrink)
        for k in range(7):                                    # finial
            self.px(cx, y - 1 - k, P['gold'])
        for k in (2, 4):
            self.px(cx - 1, y - 1 - k, P['gold_dk']); self.px(cx + 1, y - 1 - k, P['gold_dk'])
        return y - 8

    def columns(self, x0, x1, y0, y1, n, kind='stone'):
        step = (x1 - x0) / (n - 1)
        for i in range(n):
            x = round(x0 + i * step)
            self.rect(x - 1, y0, x + 1, y1, P[kind + '_hi'])
            self.px(x + 1, y0, P[kind + '2'])
            self.d.line([(x + 1, y0 + 1), (x + 1, y1)], fill=P[kind])
        self.rect(x0 - 3, y0 - 2, x1 + 3, y0 - 1, P[kind + '_hi'])
        self.rect(x0 - 4, y1 + 1, x1 + 4, y1 + 2, P[kind + '2'])
        for x in range(x0, x1):                               # dark gaps between columns
            pass

    def lantern(self, x, y):
        self.px(x, y - 1, P['cord'])
        self.rect(x - 1, y, x + 1, y + 3, P['lan'])
        self.px(x, y + 1, P['lan_hi']); self.px(x, y + 2, P['lan_hi'])
        self.px(x - 1, y, P['lan_dk']); self.px(x + 1, y + 3, P['lan_dk'])
        self.px(x, y + 4, P['gold_dk'])

    def lantern_string(self, x0, y0, x1, y1, sag=6, gap=6):
        pts = []
        for x in range(x0, x1 + 1):
            t = (x - x0) / max(1, x1 - x0)
            y = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
            pts.append((x, round(y)))
        self.d.line(pts, fill=P['cord'])
        for i, (x, y) in enumerate(pts):
            if i % gap == gap // 2 and 0 < i < len(pts) - 1:
                self.lantern(x, y + 1)

    # ---- neon
    def glyph(self, x, y, c, r, size=5):
        """An invented kanji-like glyph: a few straight strokes in a size × size box."""
        g = [[0] * size for _ in range(size)]
        for _ in range(r.randint(2, 3)):
            k = r.random()
            if k < 0.4:
                row = r.randint(0, size - 1)
                a, b = sorted((r.randint(0, 2), r.randint(size - 3, size - 1)))
                for i in range(a, b + 1): g[row][i] = 1
            elif k < 0.8:
                col = r.randint(0, size - 1)
                a, b = sorted((r.randint(0, 2), r.randint(size - 3, size - 1)))
                for i in range(a, b + 1): g[i][col] = 1
            else:
                for i in range(size - 1): g[i][i if r.random() < 0.5 else size - 1 - i] = 1
        g[0][size // 2] = 1
        for j in range(size):
            for i in range(size):
                if g[j][i]:
                    self.npx(x + i, y + j, c)

    def vsign(self, x, y, n, c, r, bg=True):
        """Vertical neon sign: n glyphs stacked, neon frame."""
        h = n * 7 + 3
        if bg:
            self.rect(x, y, x + 8, y + h, P['out'])
        self.nrect(x, y, x + 8, y + h, None, c)
        for i in range(n):
            self.glyph(x + 2, y + 2 + i * 7, NEON[(NEON.index(c) + 2 + i) % len(NEON)] if r.random() < 0.3 else c, r)
        self.px(x + 4, y - 1, P['cord']); self.px(x + 4, y - 2, P['cord'])

    def hsign(self, x, y, n, c, r):
        w = n * 7 + 3
        self.rect(x, y, x + w, y + 8, P['out'])
        self.nrect(x, y, x + w, y + 8, None, c)
        for i in range(n):
            self.glyph(x + 2 + i * 7, y + 2, c, r)

    def text(self, x, y, s, c, scale=1):
        for ch in s:
            rows = FONT[ch]
            for j, row in enumerate(rows):
                for i, b in enumerate(row):
                    if b == '1':
                        self.nrect(x + i * scale, y + j * scale, x + i * scale + scale - 1, y + j * scale + scale - 1, c)
            x += (len(rows[0]) + 1) * scale

    def finish(self):
        # neon halo: dilate the neon layer, dim it, put it under the strokes
        a = self.neon.split()[3]
        halo = self.neon.filter(ImageFilter.MaxFilter(3))
        r, g, b, ha = halo.split()
        ha = ImageChops.subtract(ha.point(lambda v: 110 if v else 0), a.point(lambda v: 255 if v else 0))
        halo = Image.merge('RGBA', (r, g, b, ha))
        out = self.im.copy()
        out.alpha_composite(halo)
        out.alpha_composite(self.neon)
        return out


FONT = {
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    'K': ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
    'Y': ['10001', '10001', '01010', '00100', '00100', '00100', '00100'],
    'S': ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
}


# ---------------------------------------------------------------- landmarks
G = H - 1  # ground row


def raadhuset(L, x, r):
    """Oslo City Hall: two brick towers with clocks, a lower block between, pagoda tops."""
    w = 104
    L.wall(x + 18, G - 44, x + w - 18, G, 'brick')
    L.windows(x + 22, G - 38, x + w - 22, G - 6, w=3, h=5, gx=3, gy=4, seed=r.random())
    L.roof(x + w // 2, G - 44, (w - 36) // 2 + 4, 6, up=2, ridge=False)
    for tx in (x + 2, x + w - 32):
        L.wall(tx, G - 92, tx + 30, G, 'brick')
        for k in range(4):                                     # tall window slits
            L.rect(tx + 4 + k * 7, G - 84, tx + 5 + k * 7, G - 50, P['win'] if r.random() < 0.6 else P['win_off'])
        L.windows(tx + 4, G - 44, tx + 27, G - 6, w=2, h=4, gx=3, gy=4, seed=r.random())
        cx = tx + 15                                           # clock
        L.d.ellipse([cx - 5, G - 98, cx + 5, G - 88], fill=P['clock'], outline=P['gold_dk'])
        L.d.line([(cx, G - 93), (cx, G - 96)], fill=P['out']); L.d.line([(cx, G - 93), (cx + 2, G - 92)], fill=P['out'])
        L.pagoda(cx, G - 99, 40, 3, tier_h=8, body='brick')
    L.lantern_string(x + 32, G - 44, x + w - 32, G - 44, sag=8)
    L.vsign(x + w // 2 - 4, G - 34, 3, NEON[0], r)
    return w


def stortinget(L, x, r):
    """Parliament: yellow-brown brick wings and a round central hall under a curved double roof."""
    w = 124
    L.wall(x, G - 36, x + 44, G, 'ochre'); L.wall(x + w - 44, G - 36, x + w, G, 'ochre')
    L.windows(x + 4, G - 30, x + 40, G - 4, w=3, h=5, seed=r.random(), arch=True)
    L.windows(x + w - 40, G - 30, x + w - 4, G - 4, w=3, h=5, seed=r.random(), arch=True)
    L.roof(x + 22, G - 36, 25, 8, up=3)
    L.roof(x + w - 22, G - 36, 25, 8, up=3)
    cx = x + w // 2
    L.wall(cx - 22, G - 52, cx + 22, G, 'ochre')
    for k in range(5):                                         # arched hall windows
        wx = cx - 18 + k * 8
        L.rect(wx, G - 44, wx + 4, G - 30, P['win'])
        L.px(wx, G - 44, P['ochre']); L.px(wx + 4, G - 44, P['ochre'])
    L.rect(cx - 6, G - 16, cx + 6, G, P['win2'])               # entrance
    ry = L.roof(cx, G - 52, 30, 10, up=4)
    L.wall(cx - 9, ry - 8, cx + 9, ry, 'ochre')
    L.rect(cx - 6, ry - 6, cx + 6, ry - 3, P['win'])
    L.pagoda(cx, ry - 7, 24, 1, tier_h=4)
    L.hsign(x + 6, G - 54, 4, NEON[1], r)
    L.lantern_string(x + 44, G - 30, cx - 22, G - 40, sag=4)
    L.lantern_string(cx + 22, G - 40, x + w - 44, G - 30, sag=4)
    return w


def slottet(L, x, r):
    """The Royal Palace: long pale front, column portico, one long sweeping roof with a cusped gable."""
    w = 156
    L.wall(x, G - 42, x + w, G, 'stone')
    L.windows(x + 5, G - 36, x + 56, G - 4, w=3, h=5, gx=4, gy=5, seed=r.random())
    L.windows(x + w - 56, G - 36, x + w - 5, G - 4, w=3, h=5, gx=4, gy=5, seed=r.random())
    cx = x + w // 2
    L.rect(cx - 18, G - 36, cx + 18, G, P['dark'])
    L.columns(cx - 15, cx + 15, G - 34, G - 2, 6)
    L.roof(cx, G - 42, w // 2 + 4, 12, up=5)
    # karahafu (cusped gable) over the portico
    for i in range(-20, 21):
        t = abs(i) / 20
        yb = G - 42 - 3 + 2 * t
        yt = yb - 10 * (math.cos(t * math.pi / 2) ** 0.7) + 2 * (t ** 6) * 0
        L.d.line([(cx + i, round(yt)), (cx + i, round(yb))], fill=P['roof2'])
        L.px(cx + i, round(yt), P['gold'])
    L.d.ellipse([cx - 3, G - 50, cx + 3, G - 45], fill=P['gold_dk'], outline=P['gold'])
    for lx in range(x + 8, x + w, 16):
        L.lantern(lx, G - 30)
    return w


def universitetet(L, x, r):
    """University (Karl Johan): portico with columns, the pediment turned into a curved gable roof."""
    w = 104
    L.wall(x, G - 40, x + w, G, 'stone')
    L.windows(x + 4, G - 34, x + 30, G - 4, w=3, h=6, gx=3, gy=5, seed=r.random(), arch=True)
    L.windows(x + w - 30, G - 34, x + w - 4, G - 4, w=3, h=6, gx=3, gy=5, seed=r.random(), arch=True)
    cx = x + w // 2
    L.rect(cx - 20, G - 38, cx + 20, G, P['dark'])
    L.windows(cx - 16, G - 30, cx + 16, G - 6, w=4, h=7, gx=5, gy=4, seed=r.random(), lit=0.8)
    L.columns(cx - 18, cx + 18, G - 36, G - 2, 6)
    L.roof(x + 18, G - 40, 21, 7, up=3)
    L.roof(x + w - 18, G - 40, 21, 7, up=3)
    L.roof(cx, G - 40, 28, 16, up=5)
    L.vsign(x + w - 12, G - 70, 4, NEON[2], r)
    return w


def nationaltheatret(L, x, r):
    """National Theatre: arched front, central tower turned into a pagoda with a finial."""
    w = 92
    L.wall(x, G - 46, x + w, G, 'ochre')
    for k in range(6):                                         # big arched windows
        wx = x + 6 + k * 14
        L.rect(wx, G - 36, wx + 7, G - 14, P['win'])
        L.px(wx, G - 36, P['ochre']); L.px(wx + 7, G - 36, P['ochre'])
        L.d.line([(wx + 3, G - 35), (wx + 3, G - 14)], fill=P['win2'])
        L.d.line([(wx, G - 26), (wx + 7, G - 26)], fill=P['win2'])
        L.rect(wx + 1, G - 10, wx + 6, G - 2, P['win2'])
    L.roof(x + w // 2, G - 46, w // 2 + 3, 9, up=4)
    cx = x + w // 2
    L.wall(cx - 10, G - 66, cx + 10, G - 52, 'ochre')
    L.rect(cx - 6, G - 63, cx + 6, G - 56, P['win'])
    L.pagoda(cx, G - 66, 30, 3, tier_h=7)
    L.lantern_string(x + 2, G - 46, x + w - 2, G - 46, sag=10, gap=7)
    L.hsign(x + 4, G - 60, 3, NEON[4], r)
    return w


def filler(L, x, r, w=None, h=None):
    """Narrow side-street buildings packed with neon, air-con units and lit windows."""
    w = w or r.randint(26, 38)
    h = h or r.randint(54, 84)
    L.wall(x, G - h, x + w, G, 'dark')
    L.windows(x + 3, G - h + 5, x + w - 3, G - 4, w=3, h=4, gx=3, gy=4, lit=0.45, seed=r.random())
    L.roof(x + w // 2, G - h, w // 2 + 3, 6, up=2, ridge=False)
    for _ in range(2):                                          # air-con boxes
        ax, ay = x + r.randint(2, w - 7), G - r.randint(10, h - 10)
        L.rect(ax, ay, ax + 4, ay + 3, P['stone2']); L.px(ax + 1, ay + 1, P['out'])
    side = x + w - 10 if r.random() < 0.5 else x + 1
    L.vsign(side, G - h + 8, r.randint(3, 6), r.choice(NEON), r)
    if r.random() < 0.6:
        L.hsign(x + 2, G - 22, max(1, (w - 8) // 7), r.choice(NEON), r)
    return w


def billboard(L, x, r):
    """A rooftop billboard on a short building: TOKYOSLO in pink neon on a cyan frame."""
    w = 72
    L.wall(x + 6, G - 46, x + w - 6, G, 'dark')
    L.windows(x + 10, G - 40, x + w - 10, G - 4, w=3, h=4, gx=3, gy=4, lit=0.5, seed=r.random())
    for lx in (x + 16, x + w - 16):                            # legs
        L.d.line([(lx, G - 47), (lx, G - 58)], fill=P['stone2'])
        L.d.line([(lx - 4, G - 47), (lx, G - 54)], fill=P['stone2'])
    L.rect(x, G - 82, x + w, G - 58, P['out'])
    L.nrect(x, G - 82, x + w, G - 58, None, NEON[1])
    L.nrect(x + 2, G - 80, x + w - 2, G - 60, None, rgb('#1b6f80'))
    L.text(x + 6, G - 77, 'TOKYOSLO', NEON[0], 1)
    for i in range(6):                                          # little glyph strip under the name
        L.glyph(x + 9 + i * 9, G - 68, NEON[2], r, size=5)
    return w


def build_street(seed=8):
    r = random.Random(seed)
    order = [filler, raadhuset, filler, billboard, stortinget, filler, slottet, filler, universitetet,
             filler, nationaltheatret, filler]
    L = Layer(1000)
    x = 2
    for f in order:
        x += f(L, x, r) + r.randint(2, 6)
    im = L.finish().crop((0, 0, x, H))
    return im


def build_far(w=640, seed=3):
    """Distant silhouette: hills, pagoda roofs and towers in dark red, a few dim windows."""
    r = random.Random(seed)
    L = Layer(w)
    # hills
    for x in range(w):
        y = 104 + 10 * math.sin(x / 70) + 6 * math.sin(x / 23 + 1)
        L.d.line([(x, round(y)), (x, G)], fill=P['far'])
    x = 0
    while x < w:
        bw, bh = r.randint(14, 34), r.randint(20, 60)
        L.rect(x, G - bh, x + bw, G, P['far2'])
        L.d.line([(x, G - bh), (x + bw, G - bh)], fill=P['far_hi'])
        for _ in range(r.randint(1, 4)):
            L.px(x + r.randint(2, bw - 2), G - r.randint(4, bh - 4), P['far_win'])
        if r.random() < 0.5:                                    # pagoda-ish roof silhouette
            cx, top = x + bw // 2, G - bh
            for i in range(-bw // 2 - 3, bw // 2 + 4):
                t = abs(i) / (bw / 2 + 3)
                yt = top - 6 + 6 * t ** 0.55 - 2 * t ** 7
                L.d.line([(cx + i, round(yt)), (cx + i, top)], fill=P['far2'])
                L.px(cx + i, round(yt), P['far_hi'])
        if r.random() < 0.25:                                   # a distant neon dot
            L.npx(x + r.randint(2, bw - 2), G - r.randint(8, bh - 2), r.choice(NEON))
        x += bw + r.randint(0, 8)
    return L.finish()


def main():
    root = Path(__file__).resolve().parents[2]
    out = root / 'assets' / 'backgrounds'
    out.mkdir(parents=True, exist_ok=True)
    street = build_street()
    far = build_far()
    street.save(out / 'tokyoslo-buildings.png')
    far.save(out / 'tokyoslo-far.png')
    print(out / 'tokyoslo-buildings.png', street.size, far.size)


if __name__ == '__main__':
    main()
