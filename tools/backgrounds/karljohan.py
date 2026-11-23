#!/usr/bin/env python3
"""Level 4's street of classic Oslo buildings, drawn twice from ONE layout: «classic» (British-style
Oslo under the teal sky, bar 42 → 1:42.0) and «tokyo» (Tokyoslo under the red sky, 1:42.0 → the end).
Every building has the same position, width and body height in both; only the style, roofs, signs
and colours change, so the switch at 1:42.0 swaps style in place (STAGE_DESIGN.md).

Rules (STAGE_DESIGN.md, «Backgrounds stay behind the action»):
- dark and low in contrast, so the foreground stands out;
- tall buildings with the detail high up;
- the band from the ground to 40 px above it stays quiet and dark (no neon, no lanterns, few dim windows).

Drawn 1:1 in game pixels, 150 px tall with the bottom row on GROUND (y = 150 on the 320 × 180 screen).
Outputs (transparent PNGs, same size):
  assets/backgrounds/oslo-classic-buildings.png
  assets/backgrounds/tokyoslo-v2-buildings.png
The first Tokyoslo draft (tools/backgrounds/tokyoslo.py → tokyoslo-buildings.png) is kept as it was.
Usage: python3 tools/backgrounds/karljohan.py
"""
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops

H = 150
G = H - 1            # ground row
QUIET = G - 40       # nothing bright below this row


def rgb(h, a=255):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


PAL = {
    # British-style Oslo at night under the teal sky (#06222b → #0f5c5a): cool, dark stone and slate,
    # verdigris copper roofs, dim warm windows.
    'classic': dict(
        out='#03100f', body='#0b2629', body2='#0e2e32', body_hi='#164046', plinth='#071a1c', void='#041011',
        brick='#1e2226', brick2='#262a2e', brick_hi='#343a3e',
        trim='#1d4a4e', trim_hi='#2a6064', roof='#08181c', roof2='#0d2226', roof_hi='#18363a',
        copper='#1c5a50', copper2='#24705f', copper_hi='#358a74', gold='#8a7a48',
        win='#a88848', win2='#7a6438', win_off='#061416', clock='#9aa890',
    ),
    # Tokyoslo under the red sky (#2a0610 → #7a1430): dark plum walls, black tile roofs with dim gold
    # trim, dim windows; neon and lanterns only high up and toned down.
    'tokyo': dict(
        out='#0c0308', body='#200a14', body2='#280d19', body_hi='#3a1626', plinth='#14050c', void='#0a0206',
        brick='#2a0c14', brick2='#34101a', brick_hi='#461a26',
        trim='#4a1c2a', trim_hi='#5e2636', roof='#10060c', roof2='#1a0a14', roof_hi='#3a1c2e',
        copper='#10060c', copper2='#1a0a14', copper_hi='#3a1c2e', gold='#9a6a2e',
        win='#b07438', win2='#804e2a', win_off='#120408', clock='#b8a080',
    ),
}
NEON = [rgb(c, 225) for c in ('#e0388f', '#38c8d8', '#e0c040', '#58d080', '#b860e0')]
LAN, LAN_HI, LAN_DK = rgb('#b81e30'), rgb('#e0a848'), rgb('#6a0c18')

FONT = {
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    'K': ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
    'Y': ['10001', '10001', '01010', '00100', '00100', '00100', '00100'],
    'S': ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
}


class Street:
    def __init__(self, style, w):
        self.style = style
        self.c = {k: rgb(v) for k, v in PAL[style].items()}
        self.im = Image.new('RGBA', (w, H), (0, 0, 0, 0))
        self.neon = Image.new('RGBA', (w, H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.n = ImageDraw.Draw(self.neon)
        self.tokyo = style == 'tokyo'

    # ---- primitives
    def rect(self, x0, y0, x1, y1, c, outline=None):
        if x1 >= x0 and y1 >= y0:
            self.d.rectangle([x0, y0, x1, y1], fill=self.c[c] if isinstance(c, str) else c,
                             outline=self.c[outline] if isinstance(outline, str) else outline)

    def px(self, x, y, c):
        self.d.point((x, y), fill=self.c[c] if isinstance(c, str) else c)

    def line(self, pts, c):
        self.d.line(pts, fill=self.c[c] if isinstance(c, str) else c)

    # ---- shared building body: identical in both styles
    def body(self, x0, top, x1, kind='body', seed=0, ww=3, wh=5, gx=3, gy=5, lit=0.45, arch=False):
        c2, hi = kind + '2', kind + '_hi'
        self.rect(x0, top, x1, G, kind, 'out')
        for y in range(top + 4, QUIET, 4):                              # stone courses, upper part only
            self.line([(x0 + 1, y), (x1 - 1, y)], c2)
        self.line([(x0 + 1, top + 1), (x1 - 1, top + 1)], hi)
        self.rect(x0 + 1, QUIET, x1 - 1, G, 'plinth')                   # quiet, dark ground floor
        self.line([(x0 + 1, QUIET), (x1 - 1, QUIET)], 'trim')
        self.windows(x0 + 4, top + 6, x1 - 4, QUIET - 4, ww, wh, gx, gy, lit, seed, arch)

    def windows(self, x0, y0, x1, y1, w, h, gx, gy, lit, seed, arch=False):
        r = random.Random(seed)
        y = y0
        while y + h <= y1:
            x = x0
            while x + w <= x1:
                on = r.random() < lit
                self.rect(x, y, x + w - 1, y + h - 1, ('win' if r.random() < 0.7 else 'win2') if on else 'win_off')
                if arch:
                    self.px(x, y, 'out'); self.px(x + w - 1, y, 'out')
                x += w + gx
            y += h + gy

    def doors(self, x0, x1, n=1, arch=True):
        step = (x1 - x0) / (n + 1)
        for i in range(n):
            cx = round(x0 + step * (i + 1))
            self.rect(cx - 3, G - 14, cx + 3, G, 'void')
            if arch:
                self.px(cx - 3, G - 14, 'plinth'); self.px(cx + 3, G - 14, 'plinth')
            # a dim fanlight high in the plinth band; kept dark
            self.rect(cx - 2, G - 13, cx + 2, G - 12, 'win2' if not self.tokyo else 'win_off')

    def cornice(self, x0, x1, y):
        self.rect(x0 - 2, y - 1, x1 + 2, y, 'trim')
        self.line([(x0 - 2, y - 1), (x1 + 2, y - 1)], 'trim_hi')

    # ---- classic (British-style) tops
    def mansard(self, x0, x1, y, h=9, dormers=True, chimneys=True, seed=0):
        for k in range(h):
            self.line([(x0 + k // 2, y - k), (x1 - k // 2, y - k)], 'roof')
        self.line([(x0 + h // 2, y - h), (x1 - h // 2, y - h)], 'roof_hi')
        if dormers:
            for x in range(x0 + 5, x1 - 5, 8):
                self.rect(x, y - h + 3, x + 2, y - 2, 'body_hi')
                self.rect(x, y - h + 4, x + 2, y - 2, 'win2' if (x // 8 + seed) % 3 == 0 else 'win_off')
        if chimneys:
            r = random.Random(seed)
            for _ in range(2):
                cx = r.randint(x0 + 4, x1 - 6)
                self.rect(cx, y - h - 5, cx + 3, y - h, 'brick', 'out')
                self.rect(cx - 1, y - h - 6, cx + 4, y - h - 5, 'brick_hi')

    def pediment(self, x0, x1, y, h):
        cx = (x0 + x1) / 2
        for k in range(h):
            half = (x1 - x0) / 2 * (1 - k / h)
            self.line([(round(cx - half), y - k), (round(cx + half), y - k)], 'body2')
        self.line([(x0, y), (round(cx), y - h)], 'trim_hi')
        self.line([(round(cx), y - h), (x1, y)], 'trim_hi')
        self.line([(x0, y), (x1, y)], 'trim')

    def dome(self, cx, y, r):
        self.d.pieslice([cx - r, y - r, cx + r, y + r], 180, 360, fill=self.c['copper'], outline=self.c['out'])
        for k in range(-r + 2, r - 1, 3):
            top = y - round(math.sqrt(max(0, r * r - k * k)))
            self.line([(cx + k, top + 1), (cx + k, y - 1)], 'copper2')
        self.d.arc([cx - r + 1, y - r + 1, cx + r - 1, y + r - 1], 200, 250, fill=self.c['copper_hi'])
        self.rect(cx - 2, y - r - 5, cx + 2, y - r, 'copper2', 'out')          # lantern
        self.line([(cx, y - r - 6), (cx, y - r - 10)], 'gold')

    def balustrade(self, x0, x1, y):
        self.line([(x0, y), (x1, y)], 'trim_hi')
        for x in range(x0 + 1, x1, 2):
            self.px(x, y + 1, 'trim')
        self.line([(x0, y + 2), (x1, y + 2)], 'trim')

    def copper_pyramid(self, cx, y, half, h):
        for k in range(h):
            hw = round(half * (1 - k / h))
            self.line([(cx - hw, y - k), (cx + hw, y - k)], 'copper' if k % 3 else 'copper2')
        self.line([(cx - half, y), (cx, y - h)], 'copper_hi')
        self.line([(cx, y - h), (cx, y - h - 5)], 'gold')

    # ---- tokyo tops
    def roof(self, cx, base, half, height, up=3, ridge=True):
        top = {}
        for x in range(cx - half, cx + half + 1):
            t = abs(x - cx) / half
            yt = base - height + height * (t ** 0.55) - up * (t ** 7)
            yb = base - up * (t ** 4) + 2 * (1 - t ** 3)
            top[x] = (round(yt), round(yb))
            self.line([(x, round(yt)), (x, round(yb))], 'roof')
            if (x - cx) % 3 == 0 and abs(x - cx) < half - 1:
                self.line([(x, round(yt) + 1), (x, round(yb) - 1)], 'roof2')
        for x, (yt, yb) in top.items():
            self.px(x, yt, 'roof_hi')
            self.px(x, yb, 'gold')
        for s in (-1, 1):
            x = cx + s * half
            self.px(x + s, top[x][0] - 1, 'gold'); self.px(x + s, top[x][0] - 2, 'gold')
        if ridge:
            yt = top[cx][0]
            self.line([(cx - half // 3, yt - 1), (cx + half // 3, yt - 1)], 'out')
            for s in (-1, 1):
                self.px(cx + s * (half // 3), yt - 2, 'gold')
        return top[cx][0]

    def pagoda(self, cx, base, width, tiers, tier_h=8):
        y, w = base, width
        for i in range(tiers):
            bw = max(4, int(w * 0.55))
            self.rect(cx - bw // 2, y - tier_h, cx + bw // 2, y, 'brick', 'out')
            if tier_h >= 7:
                self.rect(cx - bw // 2 + 2, y - tier_h + 3, cx + bw // 2 - 2, y - 3, 'win2')
            y = self.roof(cx, y - tier_h + 2, w // 2, max(4, tier_h - 2), up=2, ridge=i == tiers - 1)
            w = int(w * 0.75)
        self.line([(cx, y - 1), (cx, y - 7)], 'gold')
        return y - 8

    def glyph(self, x, y, c, r):
        g = [[0] * 5 for _ in range(5)]
        for _ in range(r.randint(2, 3)):
            if r.random() < 0.5:
                row = r.randint(0, 4); a, b = sorted((r.randint(0, 1), r.randint(3, 4)))
                for i in range(a, b + 1): g[row][i] = 1
            else:
                col = r.randint(0, 4); a, b = sorted((r.randint(0, 1), r.randint(3, 4)))
                for i in range(a, b + 1): g[i][col] = 1
        g[0][2] = 1
        for j in range(5):
            for i in range(5):
                if g[j][i]:
                    self.n.point((x + i, y + j), fill=c)

    def vsign(self, x, y, n, c, r):
        """Vertical neon sign; its bottom must stay above QUIET."""
        hgt = n * 7 + 3
        y = min(y, QUIET - 4 - hgt)
        self.rect(x, y, x + 8, y + hgt, 'out')
        self.n.rectangle([x, y, x + 8, y + hgt], outline=c)
        for i in range(n):
            self.glyph(x + 2, y + 2 + i * 7, c, r)

    def lanterns(self, x0, x1, y, sag=5, gap=7):
        pts = []
        for x in range(x0, x1 + 1):
            t = (x - x0) / max(1, x1 - x0)
            pts.append((x, round(y + sag * 4 * t * (1 - t))))
        self.d.line(pts, fill=self.c['out'])
        for i, (x, yy) in enumerate(pts):
            if i % gap == gap // 2 and 0 < i < len(pts) - 1 and yy + 4 < QUIET:
                self.d.rectangle([x - 1, yy + 1, x + 1, yy + 4], fill=LAN)
                self.d.point((x, yy + 2), fill=LAN_HI)
                self.d.point((x + 1, yy + 4), fill=LAN_DK)

    def text(self, x, y, s, c):
        for ch in s:
            for j, row in enumerate(FONT[ch]):
                for i, b in enumerate(row):
                    if b == '1':
                        self.n.point((x + i, y + j), fill=c)
            x += 6

    def finish(self):
        a = self.neon.split()[3]
        halo = self.neon.filter(ImageFilter.MaxFilter(3))
        r, g, b, ha = halo.split()
        ha = ImageChops.subtract(ha.point(lambda v: 70 if v else 0), a.point(lambda v: 255 if v else 0))
        out = self.im.copy()
        out.alpha_composite(Image.merge('RGBA', (r, g, b, ha)))
        out.alpha_composite(self.neon)
        return out


# ---------------------------------------------------------------- buildings (x, width fixed by the layout)
def townhouse(S, x, w, h, seed):
    """Tall terraced building (filler)."""
    r = random.Random(seed)
    top = G - h
    S.body(x, top, x + w, seed=seed, lit=0.4)
    S.doors(x, x + w, 1)
    if S.tokyo:
        S.roof(x + w // 2, top, w // 2 + 3, 7, up=2, ridge=False)
        if r.random() < 0.7:
            side = x + w - 10 if r.random() < 0.5 else x + 1
            S.vsign(side, top + 6, r.randint(3, 5), r.choice(NEON), r)
    else:
        S.cornice(x, x + w, top)
        S.mansard(x + 1, x + w - 1, top - 1, h=8, seed=seed)


def billboard_house(S, x, w, h, seed):
    """Townhouse with a large sign panel high on the facade: dark painted panel in classic Oslo,
    the TOKYOSLO neon in Tokyoslo."""
    r = random.Random(seed)
    top = G - h
    S.body(x, top, x + w, seed=seed, lit=0.35)
    S.doors(x, x + w, 2)
    py = top + 8
    S.rect(x + 4, py, x + w - 4, py + 18, 'out')
    if S.tokyo:
        S.roof(x + w // 2, top, w // 2 + 3, 7, up=2)
        S.n.rectangle([x + 4, py, x + w - 4, py + 18], outline=NEON[1])
        S.text(x + (w - 47) // 2, py + 3, 'TOKYOSLO', NEON[0])
        for i in range(5):
            S.glyph(x + (w - 44) // 2 + i * 9, py + 12, NEON[2], r)
    else:
        S.cornice(x, x + w, top)
        S.mansard(x + 1, x + w - 1, top - 1, h=8, seed=seed)
        S.rect(x + 5, py + 1, x + w - 5, py + 17, 'body2')
        for k in range(3):                                   # faded painted stripes, no text
            S.line([(x + 8, py + 5 + k * 4), (x + w - 8, py + 5 + k * 4)], 'trim')


def raadhuset(S, x, w, h, seed):
    """Two brick towers with clocks and a lower block between."""
    tw = 30
    block_top = G - 70
    S.body(x + tw - 2, block_top, x + w - tw + 2, kind='brick', seed=seed, lit=0.35)
    S.doors(x + tw, x + w - tw, 2)
    if S.tokyo:
        S.roof(x + w // 2, block_top, (w - 2 * tw) // 2 + 4, 6, up=2, ridge=False)
        S.lanterns(x + tw, x + w - tw, block_top + 6)
    else:
        S.balustrade(x + tw, x + w - tw, block_top - 2)
    for tx in (x, x + w - tw):
        top = G - h
        S.body(tx, top, tx + tw, kind='brick', seed=seed + tx, ww=2, wh=6, gx=4, gy=5, lit=0.3)
        cx = tx + tw // 2
        S.d.ellipse([cx - 5, top + 4, cx + 5, top + 14], fill=S.c['clock'], outline=S.c['out'])
        S.line([(cx, top + 9), (cx, top + 6)], 'out'); S.line([(cx, top + 9), (cx + 2, top + 10)], 'out')
        if S.tokyo:
            S.pagoda(cx, top, 40, 3, tier_h=7)
        else:
            S.cornice(tx, tx + tw, top)
            S.copper_pyramid(cx, top - 2, 9, 12)
            for k in (tx + 1, tx + tw - 3):                     # corner turrets
                S.rect(k, top - 6, k + 2, top - 1, 'brick_hi', 'out')


def stortinget(S, x, w, h, seed):
    """Wings and a round central hall."""
    wing_top = G - 62
    S.body(x, wing_top, x + w, kind='brick', seed=seed, lit=0.4, arch=True)
    S.doors(x, x + w, 1)
    cx = x + w // 2
    hall_top = G - h
    S.body(cx - 22, hall_top, cx + 22, kind='brick', seed=seed + 1, ww=4, wh=8, gx=4, gy=6, lit=0.6, arch=True)
    if S.tokyo:
        S.roof(x + 22, wing_top, 26, 8, up=3)
        S.roof(x + w - 22, wing_top, 26, 8, up=3)
        ry = S.roof(cx, hall_top, 30, 10, up=4)
        S.pagoda(cx, ry, 22, 1, tier_h=6)
    else:
        S.balustrade(x + 1, cx - 23, wing_top - 2)
        S.balustrade(cx + 23, x + w - 1, wing_top - 2)
        S.cornice(cx - 22, cx + 22, hall_top)
        S.rect(cx - 16, hall_top - 6, cx + 16, hall_top - 1, 'brick2', 'out')   # drum
        S.dome(cx, hall_top - 6, 15)


def slottet(S, x, w, h, seed):
    """The long palace front with a column portico."""
    top = G - h
    S.body(x, top, x + w, seed=seed, ww=3, wh=6, gx=5, gy=6, lit=0.45)
    cx = x + w // 2
    S.rect(cx - 18, top + 4, cx + 18, G, 'void')
    for i in range(6):                                        # columns, dark
        px = cx - 15 + i * 6
        S.rect(px - 1, top + 6, px, QUIET, 'body_hi')
        S.rect(px - 1, QUIET + 1, px, G - 1, 'body2')
    if S.tokyo:
        S.roof(cx, top, w // 2 + 4, 12, up=5)
        for i in range(-20, 21):                               # cusped gable over the portico
            t = abs(i) / 20
            yb = top - 3 + 2 * t
            yt = yb - 10 * (math.cos(t * math.pi / 2) ** 0.7)
            S.line([(cx + i, round(yt)), (cx + i, round(yb))], 'roof2')
            S.px(cx + i, round(yt), 'gold')
        S.lanterns(x + 6, cx - 22, top + 8, sag=4)
        S.lanterns(cx + 22, x + w - 6, top + 8, sag=4)
    else:
        S.cornice(x, x + w, top)
        S.balustrade(x + 2, x + w - 2, top - 4)
        S.pediment(cx - 22, cx + 22, top - 1, 11)


def universitetet(S, x, w, h, seed):
    """Neoclassical front with a pediment over six columns."""
    top = G - h
    S.body(x, top, x + w, kind='body', seed=seed, ww=3, wh=7, gx=4, gy=5, lit=0.5, arch=True)
    cx = x + w // 2
    S.rect(cx - 20, top + 6, cx + 20, G, 'void')
    for i in range(6):
        px = cx - 17 + i * 7
        S.rect(px - 1, top + 8, px, QUIET, 'body_hi')
        S.rect(px - 1, QUIET + 1, px, G - 1, 'body2')
    if S.tokyo:
        S.roof(x + 18, top, 21, 7, up=3)
        S.roof(x + w - 18, top, 21, 7, up=3)
        S.roof(cx, top, 28, 16, up=5)
        S.vsign(x + w - 12, top + 8, 4, NEON[2], random.Random(seed))
    else:
        S.cornice(x, x + w, top)
        S.pediment(cx - 26, cx + 26, top - 1, 14)
        S.balustrade(x + 2, cx - 27, top - 3)
        S.balustrade(cx + 27, x + w - 2, top - 3)


def nationaltheatret(S, x, w, h, seed):
    """Arched front with a central tower."""
    top = G - 78
    S.body(x, top, x + w, kind='brick', seed=seed, ww=5, wh=10, gx=7, gy=8, lit=0.55, arch=True)
    S.doors(x, x + w, 3)
    cx = x + w // 2
    ttop = G - h
    S.body(cx - 11, ttop, cx + 11, kind='brick', seed=seed + 1, ww=3, wh=6, gx=4, gy=5, lit=0.5)
    if S.tokyo:
        S.roof(cx, top, w // 2 + 3, 9, up=4)
        S.pagoda(cx, ttop, 32, 3, tier_h=7)
        S.lanterns(x + 2, x + w - 2, top + 8, sag=7)
    else:
        S.cornice(x, x + w, top)
        S.balustrade(x + 2, x + w - 2, top - 3)
        S.cornice(cx - 11, cx + 11, ttop)
        S.dome(cx, ttop - 1, 10)


LAYOUT_SEED = 23
BUILDERS = dict(townhouse=townhouse, billboard=billboard_house, raadhuset=raadhuset, stortinget=stortinget,
                slottet=slottet, universitetet=universitetet, nationaltheatret=nationaltheatret)
# kind, width, height (px above the ground to the top of the body; roofs and towers go above it)
LANDMARKS = [('raadhuset', 112, 100), ('billboard', 60, 104), ('stortinget', 128, 84), ('slottet', 160, 74),
             ('universitetet', 108, 78), ('nationaltheatret', 96, 104)]


def layout():
    """One street, used by both styles: tall townhouses packed between the landmarks."""
    r = random.Random(LAYOUT_SEED)
    items, x = [], 0
    for lm in LANDMARKS:
        for _ in range(r.randint(1, 3)):
            w, h = r.randint(28, 40), r.randint(86, 116)
            items.append(('townhouse', x, w, h, r.randint(0, 10 ** 6)))
            x += w + 1
        kind, w, h = lm
        items.append((kind, x, w, h, r.randint(0, 10 ** 6)))
        x += w + 1
    return items, x + 1


def render(style):
    items, width = layout()
    S = Street(style, width)
    for kind, x, w, h, seed in items:
        BUILDERS[kind](S, x, w, h, seed)
    return S.finish()


def main():
    root = Path(__file__).resolve().parents[2]
    out = root / 'assets' / 'backgrounds'
    out.mkdir(parents=True, exist_ok=True)
    for style, name in (('classic', 'oslo-classic-buildings.png'), ('tokyo', 'tokyoslo-v2-buildings.png')):
        im = render(style)
        im.save(out / name)
        print(out / name, im.size)


if __name__ == '__main__':
    main()
