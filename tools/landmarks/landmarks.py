#!/usr/bin/env python3
"""Oslo landmarks as flat hi-res elevations (SVG masters + PNG renders).

Flat colour, no outlines, 3-4 tones per material. Everything is drawn in METRES with y up
(ground y = 0); the SVG viewBox is in metres and the files are written at 10 px/m
(PNGs at 2x = 20 px/m), so all landmarks share one scale.

Each SVG has named layers so later tools can derive silhouettes, night versions and lit windows:
  <g id="base">    main masses (union of everything = the silhouette)
  <g id="shade">   shading and secondary planes
  <g id="trim">    cornices, bands, frames, columns
  <g id="win">     windows and glazing (recolour for lit night windows)
  <g id="detail">  fine lines: ribs, lattice, mullions, reliefs, flags

Usage: python3 tools/landmarks/landmarks.py  → assets/landmarks/hires/<name>.svg + .png
"""
import math
import random
import re
from pathlib import Path

S = 10            # SVG px per metre
LAYERS = ('base', 'shade', 'trim', 'win', 'detail')
OUT = Path(__file__).resolve().parents[2] / 'assets' / 'landmarks' / 'hires'


def f(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


class B:
    """One landmark. Coordinates in metres, y up, ground at 0."""

    def __init__(self, name, title):
        self.name, self.title = name, title
        self.g = {k: [] for k in LAYERS}
        self.defs = []
        self.n = 0
        self.xs, self.ys = [], [0.0]
        self.k = 1.0          # uniform scale applied at output (e.g. 1.5 for an enlarged landmark)

    def _pts(self, pts):
        for x, y in pts:
            self.xs.append(x)
            self.ys.append(y)
        return ' '.join(f'{f(x)},{f(-y)}' for x, y in pts)

    def poly(self, pts, fill, layer='base', extra=''):
        self.g[layer].append(f'<polygon points="{self._pts(pts)}" fill="{fill}"{extra}/>')

    def rect(self, x, y, w, h, fill, layer='base', extra=''):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], fill, layer, extra)

    def line(self, x1, y1, x2, y2, col, w=0.15, layer='detail', extra=''):
        self._pts([(x1, y1), (x2, y2)])
        self.g[layer].append(f'<line x1="{f(x1)}" y1="{f(-y1)}" x2="{f(x2)}" y2="{f(-y2)}" stroke="{col}" stroke-width="{f(w)}"{extra}/>')

    def pline(self, pts, col, w=0.15, layer='detail', extra=''):
        self.g[layer].append(f'<polyline points="{self._pts(pts)}" fill="none" stroke="{col}" stroke-width="{f(w)}" '
                             f'stroke-linejoin="round" stroke-linecap="round"{extra}/>')

    def circle(self, cx, cy, r, fill, layer='base', extra=''):
        self._pts([(cx - r, cy - r), (cx + r, cy + r)])
        self.g[layer].append(f'<circle cx="{f(cx)}" cy="{f(-cy)}" r="{f(r)}" fill="{fill}"{extra}/>')

    def ellipse(self, cx, cy, rx, ry, fill, layer='base', rot=0):
        self._pts([(cx - rx, cy - ry), (cx + rx, cy + ry)])
        tr = f' transform="rotate({f(-rot)} {f(cx)} {f(-cy)})"' if rot else ''
        self.g[layer].append(f'<ellipse cx="{f(cx)}" cy="{f(-cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}"{tr}/>')

    def clip(self, pts):
        self.n += 1
        cid = f'{self.name}-c{self.n}'
        self.defs.append(f'<clipPath id="{cid}"><polygon points="{" ".join(f"{f(x)},{f(-y)}" for x, y in pts)}"/></clipPath>')
        return f' clip-path="url(#{cid})"'

    def group(self, layer, inner, extra):
        """Wrap the last `inner` elements of a layer in a <g> (e.g. for a clip)."""
        items = self.g[layer][-inner:]
        del self.g[layer][-inner:]
        self.g[layer].append(f'<g{extra}>{"".join(items)}</g>')

    # composite shapes -------------------------------------------------
    def arch_pts(self, x, y, w, h, n=14):
        """Round-headed opening: x,y bottom-left, total height h (arch included)."""
        r = w / 2
        pts = [(x, y), (x + w, y), (x + w, y + h - r)]
        for i in range(1, n):
            a = math.pi * i / n
            pts.append((x + r + r * math.cos(a), y + h - r + r * math.sin(a)))
        pts.append((x, y + h - r))
        return pts

    def arch(self, x, y, w, h, fill, layer='win'):
        self.poly(self.arch_pts(x, y, w, h), fill, layer)

    def window(self, x, y, w, h, glass, frame=None, fw=0.25, mull=None, layer='win'):
        if frame:
            self.rect(x - fw, y - fw, w + 2 * fw, h + 2 * fw, frame, 'trim')
        self.rect(x, y, w, h, glass, layer)
        if mull:
            self.line(x + w / 2, y, x + w / 2, y + h, mull, 0.12)
            self.line(x, y + h * .62, x + w, y + h * .62, mull, 0.12)

    def svg(self, pad=2.0):
        k = self.k
        x0, x1 = min(self.xs) * k - pad, max(self.xs) * k + pad
        top = max(self.ys) * k + pad
        w, h = x1 - x0, top + pad * .5
        tr = f' transform="scale({f(k)})"' if k != 1 else ''
        body = ''.join(f'<g id="{n}"{tr}>{"".join(v)}</g>' for n, v in self.g.items())
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(x0)} {f(-top)} {f(w)} {f(h)}" '
                f'width="{f(w * S)}" height="{f(h * S)}" shape-rendering="geometricPrecision">'
                f'<title>{self.title}</title><defs>{"".join(self.defs)}</defs>{body}</svg>')


def balustrade(b, x0, x1, y, h, col, gap, post=0.35):
    b.rect(x0, y + h - 0.3, x1 - x0, 0.3, col, 'trim')
    b.rect(x0, y, x1 - x0, 0.25, col, 'trim')
    x = x0 + 0.2
    while x < x1 - 0.2:
        b.rect(x, y, post, h, col, 'trim')
        x += gap


def flag(b, x, y, h, col='#c8323a', pole='#d8d8d8', w=3.0):
    b.rect(x - 0.12, y, 0.24, h, pole, 'trim')
    fy = y + h - 0.3
    b.poly([(x + .12, fy), (x + .12 + w * .5, fy - .25), (x + .12 + w, fy + .1), (x + .12 + w * .95, fy - w * .6),
            (x + .12 + w * .45, fy - w * .7), (x + .12, fy - w * .6)], col, 'detail')


# ---------------------------------------------------------------- landmarks

def holmenkollen():
    """Holmenkollbakken, side view. The S-curve is the roof line traced from «landmark holmenkollen 1»;
    the inrun is one constant thickness, and both ends run out dead flat (horizontal). No supports."""
    b = B('holmenkollen', 'Holmenkollbakken')
    C = dict(tube='#cfd6de', tube_lo='#aab4c0', lattice='#7c8896', truss='#5f6a78', head='#46505c', head_hi='#6b7886')
    T = 4.0                                                         # thickness (m), the same all the way
    # roof line in photo px (2x crop), with flat run-outs added at both ends
    top_px = [(-150, 345), (-90, 345), (-30, 341), (40, 327), (110, 313), (170, 299), (230, 287), (300, 276),
              (370, 266), (430, 256), (475, 244), (515, 224), (565, 190), (630, 146), (690, 105), (745, 70), (790, 50),
              (835, 42), (880, 41), (940, 41)]
    m = lambda p: ((p[0] + 150) * 0.15, (345 - p[1]) * 0.15 + T)
    top = smooth([m(p) for p in top_px], 8)
    y_end = top[-1][1]
    top = [(x, min(y, y_end)) for x, y in top]                     # never above the flat top
    top = [(x, max(y, T)) for x, y in top]                         # never below the flat bottom run
    # constant-thickness offset along the normal
    bot = []
    for i, (x, y) in enumerate(top):
        a, c = top[max(i - 1, 0)], top[min(i + 1, len(top) - 1)]
        dx, dy = c[0] - a[0], c[1] - a[1]
        n = math.hypot(dx, dy)
        bot.append((x + T * dy / n, y - T * dx / n))
    # trim the offset so both ends stay square (vertical end caps)
    x0, x1 = top[0][0], top[-1][0]
    bot = [p for p in bot if x0 <= p[0] <= x1]
    bot = [(x0, top[0][1] - T)] + bot + [(x1, y_end - T)]
    outline = top + bot[::-1]
    b.poly(outline, C['tube'])
    cl = b.clip(outline)
    N = 110
    Tt, Bt = resample(top, N), resample(bot, N)
    mid = [((a[0] * .35 + c[0] * .65), (a[1] * .35 + c[1] * .65)) for a, c in zip(Tt, Bt)]
    b.poly(mid + Bt[::-1], C['tube_lo'], 'shade')
    b.group('shade', 1, cl)
    k = 0
    b.pline(mid, C['truss'], 0.22)
    k += 1
    for i in range(0, N - 2, 2):
        b.line(*Tt[i], *mid[i + 1], C['lattice'], 0.14)
        b.line(*mid[i + 1], *Tt[i + 2], C['lattice'], 0.14)
        b.line(*mid[i], *Bt[i + 1], C['truss'], 0.12)
        b.line(*Bt[i + 1], *mid[i + 2], C['truss'], 0.12)
        k += 4
    for i in range(0, N, 3):
        b.line(*Tt[i], *Bt[i], C['lattice'], 0.08)
        k += 1
    b.pline(top, C['tube_lo'], 0.3)
    k += 1
    b.group('detail', k, cl)
    # glazed start house in the flat top end
    hx0 = x1 - 14
    b.poly([(hx0, y_end - 0.6), (x1 - 0.6, y_end - 0.6), (x1 - 0.6, y_end - T + 0.6), (hx0 - 2, y_end - T + 0.6)], C['head'], 'win')
    b.poly([(hx0 + 1, y_end - 0.9), (hx0 + 5, y_end - 0.9), (hx0 + 1.5, y_end - T + 1)], C['head_hi'], 'win')
    # railing along the flat top
    b.line(hx0 - 4, y_end + 0.9, x1, y_end + 0.9, C['lattice'], 0.12)
    for i in range(10):
        x = hx0 - 4 + i * (x1 - hx0 + 4) / 9
        b.line(x, y_end, x, y_end + 0.9, C['lattice'], 0.08)
    return b


def smooth(pts, n=6):
    """Catmull-Rom through the points (n samples per span)."""
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                                   + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
    out.append(pts[-1])
    return out


def resample(pts, n):
    d = [0.0]
    for a, c in zip(pts, pts[1:]):
        d.append(d[-1] + math.dist(a, c))
    out, j = [], 0
    for i in range(n):
        t = d[-1] * i / (n - 1)
        while j < len(d) - 2 and d[j + 1] < t:
            j += 1
        u = (t - d[j]) / max(d[j + 1] - d[j], 1e-9)
        out.append((pts[j][0] + (pts[j + 1][0] - pts[j][0]) * u, pts[j][1] + (pts[j + 1][1] - pts[j][1]) * u))
    return out


def munch():
    """MUNCH (the museum), seen from the fjord: the tower's upper part leans left, both sides at the same angle."""
    b = B('munch', 'MUNCH museum')
    C = dict(alu='#bdbcb6', alu_lo='#9d9c96', rib='#8b8a85', rib_hi='#d4d3ce', glass='#22303f', glass_hi='#3d5468',
             mull='#566b7d', dark='#2a2f35')
    W, YK, TOP = 29.0, 37.5, 60.0
    lean = -7.2 / (TOP - YK)                   # dx per metre of height above the kink, same on both sides
    xl = lambda y: 0 if y <= YK else (y - YK) * lean
    tower = [(0, 0), (W, 0), (W, YK), (W + xl(TOP), TOP), (xl(TOP), TOP), (0, YK)]
    wing = [(-38, 0), (0.5, 0), (0.5, 16), (-38, 16)]
    b.poly(wing, C['alu'])
    b.poly(tower, C['alu'])
    # shaded strip along the right edge, following the lean
    b.poly([(W, 0), (W, YK), (W + xl(TOP), TOP), (W + xl(TOP) - 1.4, TOP), (W - 1.4, YK), (W - 1.4, 0)], C['alu_lo'], 'shade')
    # ribs: horizontal louvres every 0.75 m (under the glazing)
    for poly in (tower, wing):
        cl = b.clip(poly)
        k = 0
        y = 0.6
        while y < TOP:
            b.line(-40, y, 31, y, C['rib'], 0.16, 'shade')
            b.line(-40, y + 0.2, 31, y + 0.2, C['rib_hi'], 0.06, 'shade')
            y += 0.75
            k += 2
        b.group('shade', k, cl)
    # glazed head: a band parallel to the lean, top-left
    ga, gb = 43.2, 58.4
    g = [(xl(gb) + 0.9, gb), (xl(gb) + 13.0, gb), (xl(ga) + 13.0, ga), (xl(ga) + 0.9, ga)]
    b.poly(g, C['glass'], 'win')
    for i in range(1, 6):
        t = i / 6
        b.line(g[0][0] + (g[1][0] - g[0][0]) * t, gb, g[3][0] + (g[2][0] - g[3][0]) * t, ga, C['mull'], 0.12)
    for yy in (46.2, 49.2, 52.2, 55.2):
        b.line(xl(yy) + 0.9, yy, xl(yy) + 13.0, yy, C['mull'], 0.12)
    b.poly([g[0], (g[0][0] + 3.4, gb), (xl(49.5) + 1.2, 49.5)], C['glass_hi'], 'win')
    # glazed corridor down the left edge
    cor = [(xl(ga) + 0.3, ga), (xl(ga) + 1.6, ga), (1.6, YK), (1.6, 14), (0.3, 14), (0.3, YK)]
    b.poly(cor, C['glass'], 'win')
    for yy in range(16, 43, 3):
        b.line(xl(yy) + 0.3, yy, xl(yy) + 1.6, yy, C['mull'], 0.1)
    # roof slab
    b.poly([(xl(TOP), TOP), (W + xl(TOP), TOP), (W + xl(TOP - .6), TOP - .6), (xl(TOP - .6), TOP - .6)], C['rib_hi'], 'trim')
    b.rect(-38, 15.6, 38.5, 0.4, C['rib_hi'], 'trim')
    # glazed ground floors
    b.rect(-38, 0, 38.5, 4.2, C['glass'], 'win')
    b.rect(0.5, 0, W - 0.5, 4.2, C['glass'], 'win')
    for x in range(-37, 29, 2):
        b.line(x, 0, x, 4.2, C['mull'], 0.12)
    b.rect(-38, 4.2, 67, 0.4, C['rib_hi'], 'trim')
    # dark band of lower office floors on the tower's right
    b.rect(14, 5.2, 15, 9.5, C['glass'], 'win')
    for y in (7.6, 10.0, 12.4):
        b.line(14, y, 29, y, C['mull'], 0.12)
    for x in range(15, 29, 2):
        b.line(x, 5.2, x, 14.7, C['mull'], 0.1)
    return b


def monolitten():
    b = B('monolitten', 'Monolitten, Vigelandsparken')
    b.k = 1.5                      # Joakim, 24 Nov: 50 % larger than life
    C = dict(st='#d3d4d0', st_lo='#a9aba7', st_dk='#83868a', fig='#c3c4bf', fig_lo='#989a96', step='#c9cac6')
    rnd = random.Random(7)
    # stepped platform
    n, h, inset = 14, 0.42, 0.72
    for i in range(n):
        x0 = -17 + i * inset
        b.rect(x0, i * h, -2 * x0, h, C['step'] if i % 2 else C['st'])
        b.rect(x0, i * h + h - 0.08, -2 * x0, 0.08, C['st_lo'], 'shade')
    ptop = n * h
    # pedestals with figure groups along the steps
    for side in (-1, 1):
        for px, step in ((12.5, 2), (8.4, 7)):
            y0 = step * h
            x = side * px
            b.rect(x - 1.2, y0, 2.4, 2.0, C['st'])
            b.rect(x + (0.4 if side > 0 else -1.2), y0, 0.8, 2.0, C['st_lo'], 'shade')
            b.rect(x - 1.35, y0 + 1.85, 2.7, 0.25, C['st_lo'], 'trim')
            for _ in range(7):
                b.ellipse(x + rnd.uniform(-0.9, 0.9), y0 + 2.1 + rnd.uniform(0.2, 1.5), rnd.uniform(.25, .5),
                          rnd.uniform(.4, .8), C['fig'], 'base', rnd.uniform(-30, 30))
            for _ in range(5):
                b.ellipse(x + rnd.uniform(-0.8, 0.8), y0 + 2.1 + rnd.uniform(0.2, 1.4), rnd.uniform(.12, .25),
                          rnd.uniform(.3, .55), C['fig_lo'], 'shade', rnd.uniform(-40, 40))
    # plinth
    b.rect(-2.3, ptop, 4.6, 4.2, C['st'])
    b.rect(0.9, ptop, 1.4, 4.2, C['st_lo'], 'shade')
    b.rect(-2.5, ptop + 3.9, 5.0, 0.35, C['st_lo'], 'trim')
    # the column: a bumpy outline of tangled figures
    y0, y1 = ptop + 4.25, ptop + 4.25 + 14.2
    left, right = [], []
    y = y0
    while y <= y1:
        t = (y - y0) / (y1 - y0)
        r = 1.65 - 0.25 * t
        left.append((-r - rnd.uniform(0, 0.35), y))
        right.append((r + rnd.uniform(0, 0.35), y))
        y += 0.45
    crown = []
    for i in range(11):
        a = math.pi * (1 - i / 10)
        crown.append((1.4 * math.cos(a) + rnd.uniform(-.15, .15), y1 + 0.9 * math.sin(a) + rnd.uniform(0, .5)))
    col = left + crown + right[::-1]
    b.poly(col, C['fig'])
    cl = b.clip(col)
    b.rect(0.55, y0, 2.2, y1 - y0 + 2, C['fig_lo'], 'shade')
    b.group('shade', 1, cl)
    k = 0
    for _ in range(150):
        cx, cy = rnd.uniform(-1.9, 1.9), rnd.uniform(y0 + .2, y1 + .8)
        rx, ry, ang = rnd.uniform(.14, .26), rnd.uniform(.45, .9), rnd.uniform(-70, 70)
        lit = C['fig'] if cx < 0.6 else C['fig_lo']
        b.ellipse(cx + .07, cy - .09, rx, ry, C['st_dk'], 'detail', ang)
        b.ellipse(cx, cy, rx, ry, lit, 'detail', ang)
        if rnd.random() < .4:
            b.circle(cx + .3 * math.sin(math.radians(-ang)) * ry * 1.2, cy + ry * .95, .17, lit, 'detail')
    k = sum(1 for e in b.g['detail'])
    b.group('detail', k, cl)
    return b


def nationaltheatret():
    b = B('nationaltheatret', 'Nationaltheatret')
    C = dict(brick='#cf9862', brick_lo='#b27c4b', stone='#e7dcc7', stone_lo='#c8baa0', stone_dk='#a8987e',
             win='#2c2f36', win_hi='#4a4f5a', curtain='#7a3b37', roof='#6b7178', bronze='#4f8a77', door='#6e4428')
    # wings
    for s in (-1, 1):
        x0, x1 = sorted((s * 15.2, s * 27.4))
        b.rect(x0, 0, x1 - x0, 19.5, C['brick'])
        b.rect(x0, 0, x1 - x0, 1.2, C['stone_lo'], 'trim')
        b.rect(x0, 9.0, x1 - x0, 0.6, C['stone'], 'trim')           # string course
        b.rect(x0, 15.0, x1 - x0, 1.5, C['stone'], 'trim')          # frieze
        for k in range(4):
            px = x0 + 1.2 + k * (x1 - x0 - 2.4) / 3.6
            b.rect(px, 15.25, 2.0, 1.0, C['stone_lo'], 'detail')
        b.rect(x0 - .4, 18.5, x1 - x0 + .8, 1.0, C['stone'], 'trim')  # cornice
        b.rect(x0 - .4, 18.3, x1 - x0 + .8, 0.25, C['stone_dk'], 'shade')
        balustrade(b, x0, x1, 19.5, 1.0, C['stone'], 0.7, 0.3)
        for ux in (x0 + 1, x1 - 1) if s < 0 else (x0 + 1, x1 - 1):
            if (s < 0 and ux < x0 + 2) or (s > 0 and ux > x1 - 2):
                b.rect(ux - .5, 20.5, 1.0, 0.6, C['stone'], 'trim')
                b.ellipse(ux, 21.6, 0.5, 0.7, C['stone'], 'trim')
                b.rect(ux - .12, 22.2, .24, .5, C['stone'], 'trim')
        cx = (x0 + x1) / 2
        # upper window with pediment
        b.window(cx - 1.2, 10.8, 2.4, 3.6, C['win'], C['stone'], 0.4, C['win_hi'])
        b.poly([(cx - 1.9, 14.6), (cx + 1.9, 14.6), (cx, 15.2)], C['stone'], 'trim')
        # ground floor: rusticated pier, arched doorway, small windows
        b.arch(cx - 1.4 + s * 2.6, 1.2, 2.8, 5.6, C['door'])
        b.rect(cx - 2.6 - s * 2.0, 3.0, 2.0, 2.8, C['win'], 'win')
        b.rect(x0, 1.2, x1 - x0, 0.15, C['brick_lo'], 'shade')
        for yy in (3, 5, 7):
            b.line(x0 + .3, yy, x1 - .3, yy, C['brick_lo'], 0.08)
    # central block
    b.rect(-16, 0, 32, 25, C['stone'])
    b.rect(-16, 0, 32, 1.2, C['stone_lo'], 'trim')
    # rusticated piers + arcade
    for i, x in enumerate((-9.6, -3.2, 3.2, 9.6)):
        b.rect(x - 1.3, 1.2, 2.6, 7.8, C['stone_lo'], 'shade')
        for yy in range(2, 9, 1):
            b.line(x - 1.3, yy + .2, x + 1.3, yy + .2, C['stone_dk'], 0.1)
    for x in (-6.4, 0, 6.4):
        b.arch(x - 1.8, 1.2, 3.6, 6.8, C['win'])
        b.rect(x - 1.5, 1.2, 3.0, 4.2, C['door'], 'win')
        b.line(x, 1.2, x, 5.4, C['brick_lo'], 0.1)
    for x in (-13.2, 13.2):
        b.arch(x - 1.2, 1.2, 2.4, 5.6, C['door'])
    # balcony
    b.rect(-16.4, 9.0, 32.8, 0.7, C['stone_dk'], 'trim')
    balustrade(b, -16, 16, 9.7, 1.1, C['stone'], 0.65, 0.3)
    # pilasters at the corners of the portico, columns, arched windows
    for s in (-1, 1):
        b.rect(s * 16 - (2.6 if s > 0 else 0), 9.7, 2.6, 14.0, C['stone'], 'trim')
        b.rect(s * 16 - (2.6 if s > 0 else 0) + (1.8 if s > 0 else 0), 9.7, 0.8, 14.0, C['stone_lo'], 'shade')
    for x in (-9.6, -3.2, 3.2, 9.6):
        b.rect(x - 0.75, 10.8, 1.5, 11.2, C['stone'], 'trim')
        b.rect(x + 0.25, 10.8, 0.5, 11.2, C['stone_lo'], 'shade')
        b.rect(x - 1.0, 10.8, 2.0, 0.5, C['stone_dk'], 'trim')      # base
        b.rect(x - 1.1, 21.8, 2.2, 0.9, C['stone_dk'], 'trim')      # capital
        for dx in (-.4, 0, .4):
            b.line(x + dx, 11.4, x + dx, 21.6, C['stone_lo'], 0.07)
    for x in (-6.4, 0, 6.4):
        b.arch(x - 1.55, 11.0, 3.1, 6.4, C['win'])
        b.poly([(x - 1.3, 11.0), (x + 1.3, 11.0), (x + 1.3, 15.8), (x, 16.8), (x - 1.3, 15.8)], C['curtain'], 'win')
        b.rect(x - 1.9, 17.6, 3.8, 0.7, C['stone_lo'], 'detail')    # name plaque (blank)
        for dx in (-.9, .9):
            b.rect(x + dx - .55, 18.8, 1.1, 1.6, C['win'], 'win')
    # entablature, sign plaque (blank), pediment
    b.rect(-16.4, 22.7, 32.8, 2.3, C['stone'], 'trim')
    b.rect(-16.4, 22.7, 32.8, 0.3, C['stone_dk'], 'shade')
    b.rect(-7.5, 23.1, 15, 1.4, C['stone_lo'], 'detail')
    b.rect(-16.8, 24.8, 33.6, 0.5, C['stone_dk'], 'trim')
    for s in (-1, 1):                                               # corner towers + statues
        x0 = s * 14.5 - (3.2 if s > 0 else 0)
        b.rect(x0, 25, 3.2, 3.6, C['stone'])
        b.rect(x0 - .2, 28.4, 3.6, 0.4, C['stone_dk'], 'trim')
        cx = x0 + 1.6
        b.ellipse(cx, 29.6, 0.7, 1.0, C['bronze'])
        b.ellipse(cx + .2, 30.8, 0.35, 0.4, C['bronze'])
        b.poly([(cx - .3, 30.4), (cx - 1.5, 31.6), (cx - 1.2, 31.8), (cx, 30.8)], C['bronze'])
        b.poly([(cx + .4, 30.2), (cx + 1.4, 31.2), (cx + 1.1, 31.4), (cx + .2, 30.6)], C['bronze'])
    b.poly([(-14, 25.3), (14, 25.3), (0, 29.6)], C['stone'])
    b.poly([(-12.2, 25.8), (12.2, 25.8), (0, 29.0)], C['stone_lo'], 'shade')
    for i in range(9):                                              # relief figures
        x = -6 + i * 1.5
        hgt = 2.4 - abs(x) * 0.22
        b.ellipse(x, 25.8 + hgt * .45, 0.45, hgt * .45, C['stone'], 'detail')
    b.poly([(-14.6, 25.2), (0, 29.8), (14.6, 25.2), (14.6, 25.5), (0, 30.2), (-14.6, 25.5)], C['stone_dk'], 'trim')
    b.ellipse(0, 30.6, 0.6, 0.6, C['stone'], 'trim')
    return b


def opera():
    """Operahuset, side elevation traced from «opera3» (checked against «opera seaside», «opera1», «opera2»):
    the marble ramp rising left to right in front of the foyer, the foyer glass under a roof that rises
    towards the LEFT, the fly tower behind, the top plateau and the white office block on the right."""
    b = B('opera', 'Operahuset')
    C = dict(mar='#eef0f1', mar_lo='#d0d6dc', mar_dk='#aeb7c0', glass='#3f8f9e', glass_hi='#7cc0c8', glass_ln='#2f6f7c',
             dk='#2c3944', dk_ln='#40505e', alu='#e6e8ea', alu_lo='#cdd1d5', slat='#9aa3ad', win='#3a4652')
    m = lambda x, y: ((x - 80) * 0.075, (520 - y) * 0.1)            # opera3 px -> metres (x a little compressed)
    X = lambda x: m(x, 0)[0]
    Y = lambda y: m(0, y)[1]
    # ramp top line: steep-ish run-in from the ground, then the long straight rise
    ra, rb, rc = m(80, 520), m(480, 368), m(2505, 182)

    def ramp(x):
        if x <= rb[0]:
            return ra[1] + (rb[1] - ra[1]) * (x - ra[0]) / (rb[0] - ra[0])
        return rb[1] + (rc[1] - rb[1]) * (x - rb[0]) / (rc[0] - rb[0])

    th = 2.0
    gx0, gx1 = X(464), X(1550)
    roof = lambda x: Y(160) + (Y(195) - Y(160)) * (x - gx0) / (gx1 - gx0)    # rises to the left
    # rear stage block + fly tower (behind)
    b.rect(X(600), 20, X(1060) - X(600), 18.0, C['alu'])
    b.rect(X(1000), 20, X(1060) - X(1000), 18.0, C['alu_lo'], 'shade')
    for i in range(1, 10):
        b.line(X(600), 38.0 - i * 1.4, X(1000), 38.0 - i * 1.4, C['alu_lo'], 0.1, 'shade')
    fx0, fx1, ftop = X(1088), X(1432), 54.0
    b.rect(fx0, 20, fx1 - fx0, ftop - 20, C['alu'])
    b.rect(fx1 - 4, 20, 4, ftop - 20, C['alu_lo'], 'shade')
    for i in range(1, 16):
        b.line(fx0, ftop - i * 1.5, fx1 - 4, ftop - i * 1.5, C['alu_lo'], 0.1, 'shade')
    # foyer glass
    gl = [(gx0, ramp(gx0)), (gx1, ramp(gx1)), (gx1, roof(gx1)), (gx0, roof(gx0))]
    b.poly(gl, C['glass'], 'win')
    cl = b.clip(gl)
    b.poly([(gx0 + 18, 40), (gx0 + 26, 40), (gx0 + 14, 0), (gx0 + 6, 0)], C['glass_hi'], 'win', ' opacity=".35"')
    b.group('win', 1, cl)
    k = 0
    x = gx0 + 1.6
    while x < gx1:
        b.line(x, 0, x, 40, C['glass_ln'], 0.14)
        x += 2.4
        k += 1
    for dy in (4, 8):
        b.line(gx0, roof(gx0) - dy, gx1, roof(gx1) - dy, C['glass_ln'], 0.14)
        k += 1
    b.group('detail', k, cl)
    rf = [(gx0 - .5, roof(gx0)), (gx1, roof(gx1)), (gx1, roof(gx1) + 1.4), (gx0 - .5, roof(gx0) + 1.4)]
    b.poly(rf, C['mar'], 'trim')
    b.poly(rf[:2] + [(gx1, roof(gx1) + .35), (gx0 - .5, roof(gx0) + .35)], C['mar_lo'], 'shade')
    b.rect(gx0 - .5, ramp(gx0), .5, roof(gx0) - ramp(gx0), C['mar_lo'], 'trim')
    # office block (right) + top plateau where the ramp ends
    ox0, ox1, otop = X(1547), X(2984), Y(243)
    b.rect(ox0, 0, ox1 - ox0, otop, C['alu'])
    b.rect(ox1 - 1.2, 0, 1.2, otop, C['alu_lo'], 'shade')
    px0, px1 = X(2505), X(2805)
    b.rect(px0, otop, px1 - px0, Y(172) - otop, C['mar'])
    b.rect(px0, Y(227), px1 - px0, 0.6, C['mar_lo'], 'shade')
    n = 0
    rows = [(3.0, 5.4, 'win'), (8.0, 10.4, 'win'), (13.0, 15.6, 'slat'), (17.8, 20.6, 'slat'), (22.6, 25.2, 'slat')]
    for ya, yb, kind in rows:
        x = ox0 + 2
        i = 0
        while x < ox1 - 3:
            w = 6.0 if kind == 'slat' else 2.6
            col = C['slat'] if kind == 'slat' else C['win']
            if not (kind == 'slat' and i % 4 == 3):
                b.rect(x, ya, w, yb - ya, col, 'win')
                n += 1
            x += w + (1.4 if kind == 'slat' else 0.8)
            i += 1
    for ya, yb, kind in rows:
        if kind == 'slat':
            y = ya + .45
            while y < yb:
                b.line(ox0, y, ox1, y, C['alu_lo'], 0.08)
                y += .5
    # dark lower glazing under the ramp
    dx0 = X(300)
    b.poly([(dx0, 1.2), (ox0, 1.2), (ox0, ramp(ox0) - th + .3), (rb[0], rb[1] - th + .3), (dx0, max(1.2, ramp(dx0) - th + .3))],
           C['dk'], 'win')
    for x in range(int(dx0) + 2, int(ox0), 3):
        b.line(x, 1.2, x, ramp(x) - th, C['dk_ln'], 0.12)
    # the ramp slab (in front of everything), ending at the plateau
    xs = [ra[0], rb[0], px0]
    top = [(x, ramp(x)) for x in xs]
    slab = top + [(px0, ramp(px0) - th), (rb[0], rb[1] - th), (ra[0] + th / ((rb[1] - ra[1]) / (rb[0] - ra[0])), 0)]
    b.poly(slab, C['mar'], 'trim')
    b.poly(top + [(px0, ramp(px0) - .45), (rb[0], rb[1] - .45), (ra[0] + .45 / ((rb[1] - ra[1]) / (rb[0] - ra[0])), 0)],
           C['mar_lo'], 'shade')
    # quay / plinth
    b.rect(-6, 0, ox1 + 8, 1.2, C['mar'])
    b.rect(-6, 0, ox1 + 8, 0.3, C['mar_dk'], 'shade')
    return b


def plaza():
    """Radisson Blu Plaza: only the knife-edge sliver, its slanted top ending in a sharp point."""
    b = B('plaza', 'Radisson Blu Plaza')
    C = dict(g='#1f3e69', g_lo='#183256', g_hi='#5f88bf', g_ln='#3b6398', edge='#8fb2dc', crown='#c9d2dc')
    W, HL, HP = 13.0, 104.0, 117.0
    sl = [(0, 0), (W, 0), (W, HP), (0, HL)]
    b.poly(sl, C['g'])
    b.poly([(W - 2.4, 0), (W, 0), (W, HP), (W - 2.4, HP - 2.4 * (HP - HL) / W)], C['g_lo'], 'shade')
    cl = b.clip(sl)
    k = 0
    y = 3.1
    while y < HP:
        b.line(-1, y, W + 1, y, C['g_ln'], 0.12)
        y += 3.1
        k += 1
    x = 1.3
    while x < W:
        b.line(x, 0, x, HP, C['g_ln'], 0.1)
        x += 1.3
        k += 1
    b.group('detail', k, cl)
    cl = b.clip(sl)
    b.poly([(0, 46), (W, 58), (W, 62), (0, 50)], C['g_hi'], 'win', ' opacity=".4"')
    b.poly([(0, 20), (W, 32), (W, 33.5), (0, 21.5)], C['g_hi'], 'win', ' opacity=".3"')
    b.group('win', 2, cl)
    b.rect(W - .45, 0, 0.45, HP, C['edge'], 'trim')                # the sharp edge catches the light
    b.pline([(0, HL), (W, HP)], C['crown'], 0.3, 'trim')
    return b


def radhuset():
    b = B('radhuset', 'Oslo rådhus')
    C = dict(br='#8c3d2d', br_lo='#71301f', br_dk='#5b2419', mortar='#7c3426', stone='#cbc2b2', stone_lo='#a99f8d',
             win='#29303a', win_hi='#4b5462', gold='#c9a23f', gold_lo='#9c7b2c', clock='#2d2f33', bronze='#3e4a45')
    # two towers of the same size, each 12 m in from the end of the main block, but each with its own face
    # (west: tall slit + spire, east: clock) (Joakim, 24 Nov)
    for x0, top, clock in ((-36, 66, False), (18, 66, True)):
        b.rect(x0, 30, 18, top - 30, C['br'])
        b.rect(x0 + 13.5, 44, 4.5, top - 44, C['br_lo'], 'shade')
        b.rect(x0 - .2, top - 0.7, 18.4, 0.7, C['stone'], 'trim')
        for k in range(5):                                       # brick courses
            pass
        yy = 45
        while yy < top - 1:
            b.line(x0, yy, x0 + 18, yy, C['mortar'], 0.06)
            yy += 1.2
        # top row of small windows
        for i in range(6):
            b.rect(x0 + 1.6 + i * 2.7, top - 3.2, 1.2, 1.9, C['win'], 'win')
        if clock:
            cx, cy = x0 + 9, top - 10
            b.circle(cx, cy, 3.6, C['gold_lo'], 'trim')
            b.circle(cx, cy, 3.2, C['clock'], 'trim')
            for i in range(12):
                a = math.pi * 2 * i / 12
                b.rect(cx + 2.7 * math.cos(a) - .2, cy + 2.7 * math.sin(a) - .2, .4, .4, C['gold'], 'detail')
            b.line(cx, cy, cx + 1.2, cy + 2.0, C['gold'], 0.3)
            b.line(cx, cy, cx - 1.8, cy - 0.6, C['gold'], 0.3)
            for i in range(4):
                b.rect(x0 + 2.2 + i * 3.9, 46, 1.6, 4.8, C['win'], 'win')
                b.rect(x0 + 2.2 + i * 3.9, 45.6, 1.6, 0.4, C['stone'], 'trim')
            b.rect(x0 - .6, 45.2, 19.2, 0.5, C['stone'], 'trim')    # little balcony
        else:
            b.rect(x0 + 8.2, 44.5, 1.6, top - 49, C['win'], 'win')    # tall slit
            for i in range(4):
                if i in (1, 2):
                    continue
                b.rect(x0 + 2.0 + i * 4.2, 46, 1.6, 4.8, C['win'], 'win')
            for i in range(4):
                b.rect(x0 + 2.0 + i * 4.2, 52.5, 1.6, 3.2, C['win'], 'win')
            b.rect(x0 + 8.85, top, 0.3, 7, C['br_dk'], 'trim')        # spire / mast
            b.rect(x0 + 8.4, top + 6.6, 1.2, 0.3, C['br_dk'], 'trim')
    # main block
    b.rect(-48, 0, 96, 44, C['br'])
    yy = 22.5
    while yy < 43.5:
        b.line(-48, yy, 48, yy, C['mortar'], 0.06)
        yy += 1.2
    b.rect(-48.2, 43.4, 96.4, 0.6, C['stone'], 'trim')
    # relief figure + two small reliefs (east)
    b.ellipse(28, 33, 1.1, 3.4, C['bronze'], 'detail')
    b.ellipse(28, 37.3, 0.7, 0.8, C['bronze'], 'detail')
    b.poly([(27.2, 35.8), (25.0, 38.8), (25.6, 39.2), (27.6, 36.6)], C['bronze'], 'detail')
    b.poly([(28.8, 35.8), (31.0, 38.8), (30.4, 39.2), (28.4, 36.6)], C['bronze'], 'detail')
    b.poly([(27.0, 29.6), (29.0, 29.6), (28.0, 28.0)], C['bronze'], 'detail')
    for x in (23, 33):
        b.ellipse(x, 31.0, 1.1, 0.8, C['bronze'], 'detail')
    # upper storey: deep window row with stone surround + balustrade band
    b.rect(-47, 15.0, 94, 0.9, C['stone'], 'trim')
    n = 15
    for i in range(n):
        x = -45 + i * (90 / (n - 1)) - 1.6
        b.rect(x - .3, 16.0, 3.8, 5.8, C['br_dk'], 'shade')
        b.window(x, 16.2, 3.2, 5.2, C['win'], None, 0, C['win_hi'])
    b.rect(-48, 21.8, 96, 0.5, C['br_lo'], 'shade')
    for i in range(n):
        x = -45 + i * (90 / (n - 1)) - 1.2
        b.window(x, 10.2, 2.4, 3.0, C['win'], C['stone'], 0.25)
    b.rect(-48, 13.8, 96, 0.4, C['br_lo'], 'shade')
    # ground floor: stone colonnade, gold reliefs
    b.rect(-48, 0, 96, 8.6, C['stone'])                          # same width as the brick block above
    b.rect(-48, 0, 96, 0.8, C['stone_lo'], 'shade')
    b.rect(-48.2, 8.2, 96.4, 0.7, C['stone_lo'], 'trim')
    for i in range(16):
        x = -46.3 + i * (89 / 15)
        b.rect(x, 1.2, 3.6, 5.6, C['win'], 'win')
        b.line(x + 1.8, 1.2, x + 1.8, 6.8, C['win_hi'], 0.12)
        b.line(x, 4.6, x + 3.6, 4.6, C['win_hi'], 0.12)
    for x in (-38, -4, 30):
        b.rect(x, 7.0, 6, 1.1, C['gold'], 'detail')
        b.rect(x + .4, 7.25, 5.2, 0.6, C['gold_lo'], 'detail')
    return b


def slottet():
    b = B('slottet', 'Det kongelige slott')
    C = dict(y='#ecd7a3', y_lo='#d5bc83', wt='#f4efe2', wt_lo='#ddd5c3', gr='#c8c3b8', gr_lo='#a7a298', win='#2b3340',
             win_hi='#4a5464', roof='#3a3f47', door='#4b3426')
    W = 55
    b.rect(-W + .6, 24, 2 * W - 1.2, 1.6, C['roof'])                 # roof just visible
    b.rect(-W, 0, 2 * W, 9.5, C['gr'])
    b.rect(-W, 9.5, 2 * W, 14.5, C['y'])
    b.rect(-W, 0, 2 * W, 0.8, C['gr_lo'], 'shade')
    b.rect(-W - .2, 9.2, 2 * W + .4, 0.5, C['wt_lo'], 'trim')
    b.rect(-W - .3, 23.0, 2 * W + .6, 1.2, C['wt'], 'trim')
    b.rect(-W - .3, 22.8, 2 * W + .6, 0.3, C['wt_lo'], 'shade')
    b.rect(-W, 17.0, 2 * W, 0.35, C['wt'], 'trim')
    # end pavilions, a little taller
    for s in (-1, 1):
        x0 = -W if s < 0 else W - 16.5
        b.rect(x0, 24.2, 16.5, 2.2, C['y'])
        b.rect(x0 - .3, 26.2, 17.1, 0.6, C['wt'], 'trim')
        for px in (x0, x0 + 15.9):
            b.rect(px, 9.5, 0.6, 16.7, C['y_lo'], 'shade')
        b.rect(x0 + 16.5 if s < 0 else x0 - 0.6, 9.5, 0.6, 14.7, C['y_lo'], 'shade')
    # window columns: 3 on each pavilion, 5 on each wing
    cols = []
    for s in (-1, 1):
        cols += [s * x for x in (52.2, 46.8, 41.4)]
        cols += [s * x for x in (35.6, 30.6, 25.6, 20.6, 15.6)]
    for x in cols:
        b.arch(x - 0.9, 2.2, 1.8, 4.2, C['win'])                   # ground floor
        b.window(x - 1.0, 11.0, 2.0, 4.0, C['win'], C['wt'], 0.3, C['win_hi'])
        b.rect(x - 1.5, 15.2, 3.0, 0.45, C['wt'], 'trim')          # window head
        b.window(x - 1.0, 18.3, 2.0, 3.0, C['win'], C['wt'], 0.3, C['win_hi'])
        b.rect(x - 0.8, 0.8, 1.6, 0.5, C['gr_lo'], 'detail')
    # central portico
    b.rect(-15, 0, 30, 9.5, C['gr'])
    b.rect(-15, 0, 30, 0.8, C['gr_lo'], 'shade')
    for i, x in enumerate((-10.7, -5.35, 0, 5.35, 10.7)):
        w = 3.4 if i == 2 else 3.0
        b.arch(x - w / 2, 0.8, w, 6.8 if i == 2 else 6.2, C['win'])
        if i == 2:
            b.rect(x - 1.3, 0.8, 2.6, 4.8, C['door'], 'win')
    b.rect(-15.3, 9.2, 30.6, 0.6, C['wt_lo'], 'trim')
    b.rect(-15, 9.8, 30, 14.2, C['y_lo'], 'shade')                 # recessed wall behind columns
    for x in (-10.7, -5.35, 0, 5.35, 10.7):
        b.window(x - 1.0, 11.0, 2.0, 4.0, C['win'], None, 0, C['win_hi'])
        b.window(x - 1.0, 18.0, 2.0, 3.0, C['win'], None, 0, C['win_hi'])
    balustrade(b, -15, 15, 9.8, 1.0, C['wt'], 0.6, 0.25)
    for x in (-13.35, -8.0, -2.7, 2.7, 8.0, 13.35):
        b.rect(x - .75, 10.8, 1.5, 12.0, C['wt'], 'trim')
        b.rect(x + .3, 10.8, .45, 12.0, C['wt_lo'], 'shade')
        b.rect(x - 1.0, 22.5, 2.0, 0.6, C['wt'], 'trim')
        b.rect(x - 1.0, 10.8, 2.0, 0.45, C['wt_lo'], 'trim')
    b.rect(-15.4, 23.0, 30.8, 2.6, C['wt'], 'trim')
    b.rect(-15.4, 23.0, 30.8, 0.4, C['wt_lo'], 'shade')
    b.poly([(-15.6, 25.6), (15.6, 25.6), (0, 30.6)], C['wt'])
    b.poly([(-13.4, 26.0), (13.4, 26.0), (0, 30.0)], C['y'], 'shade')
    b.poly([(-15.8, 25.5), (0, 30.6), (15.8, 25.5), (15.8, 25.9), (0, 31.0), (-15.8, 25.9)], C['wt_lo'], 'trim')
    b.ellipse(0, 31.3, 0.5, 0.5, C['wt'], 'trim')
    return b


def stortinget():
    b = B('stortinget', 'Stortinget')
    C = dict(y='#e3cd9a', y_lo='#c9b07c', y_dk='#ad945f', gr='#cdbdab', gr_lo='#ab9b89', win='#2b3340', win_hi='#4b5565',
             roof='#5b6670', roof_lo='#48525b', door='#7a4a2a')
    # connecting sections with slate roofs
    for s in (-1, 1):
        x0, x1 = sorted((s * 13.6, s * 21.0))
        b.rect(x0, 0, x1 - x0, 13.2, C['y'])
        b.poly([(x0 - .2, 13.2), (x1 + .2, 13.2), (x1 - .8, 15.0), (x0 + .8, 15.0)], C['roof'])
        b.rect(x0, 12.6, x1 - x0, 0.6, C['gr'], 'trim')
        for k in range(2):
            xx = x0 + 1.3 + k * 3.4
            b.arch(xx, 2.0, 1.6, 3.6, C['win'])
            b.arch(xx, 7.3, 1.6, 3.8, C['win'])
        b.rect(x0, 0, x1 - x0, 1.4, C['gr'], 'trim')
    # gabled end wings
    for s in (-1, 1):
        x0, x1 = sorted((s * 20.4, s * 37.2))
        cx = (x0 + x1) / 2
        b.rect(x0, 0, x1 - x0, 16.2, C['y'])
        gable = [(x0, 16.2), (x0 + 1.4, 16.2), (x0 + 1.4, 17.0)]
        for i in range(11):                                         # curved gable
            t = i / 10
            gx = x0 + 1.4 + (cx - x0 - 1.4) * t
            gable.append((gx, 17.0 + 2.0 * math.sin(t * math.pi / 2)))
        gable += [(2 * cx - p[0], p[1]) for p in gable[::-1]]
        b.poly(gable, C['y'])
        b.pline(gable[2:-2], C['gr'], 0.35, 'trim')
        b.rect(cx - .4, 19.0, .8, 1.0, C['gr'], 'trim')
        b.ellipse(cx, 20.3, .45, .45, C['gr'], 'trim')
        for px in (x0, x1 - .9):
            b.rect(px, 0, 0.9, 16.2, C['y_lo'], 'shade')
            b.rect(px - .1, 16.0, 1.1, 1.3, C['gr'], 'trim')
        b.rect(x0, 0, x1 - x0, 1.4, C['gr'], 'trim')
        b.rect(x0 - .2, 15.6, x1 - x0 + .4, 0.6, C['gr'], 'trim')
        b.rect(x0, 6.6, x1 - x0, 0.45, C['gr'], 'trim')
        for k in (-1, 0, 1):
            xx = cx + k * 3.6
            b.arch(xx - .9, 9.6, 1.8, 4.6, C['win'])
            b.rect(xx - 1.15, 9.3, 2.3, 0.3, C['gr'], 'trim')
            b.arch(xx - .8, 2.4, 1.6, 3.6, C['win'])
        b.arch(cx - 1.5, 17.0, 3.0, 1.6, C['win'])                  # little gable lunette
    # central drum
    b.rect(-13.6, 0, 27.2, 19.6, C['y'])
    b.rect(-13.6, 0, 3.2, 19.6, C['y_lo'], 'shade')
    b.rect(10.4, 0, 3.2, 19.6, C['y_lo'], 'shade')
    b.rect(-13.6, 0, 1.2, 19.6, C['y_dk'], 'shade')
    b.rect(12.4, 0, 1.2, 19.6, C['y_dk'], 'shade')
    b.poly([(-13.2, 19.6), (13.2, 19.6), (10, 20.5), (-10, 20.5)], C['roof'])
    b.rect(-13.9, 19.1, 27.8, 0.6, C['gr'], 'trim')
    b.rect(-13.6, 0, 27.2, 1.4, C['gr'], 'trim')
    b.rect(-13.6, 7.6, 27.2, 0.5, C['gr'], 'trim')
    b.rect(-13.6, 15.2, 27.2, 0.5, C['gr'], 'trim')
    for k in range(-2, 3):                                          # ground arcade
        x = k * 4.6
        if k == 0:
            b.arch(x - 1.6, 1.4, 3.2, 5.4, C['gr_lo'], 'trim')
            b.arch(x - 1.2, 1.4, 2.4, 4.8, C['door'])
        else:
            b.arch(x - 1.3, 1.4, 2.6, 4.9, C['win'])
    for k in (-2, -1, 0, 1, 2):                                     # paired arched windows
        x = k * 4.6
        for dx in (-.85, .85):
            b.arch(x + dx - .65, 9.0, 1.3, 4.6, C['win'])
        b.arch(x - 1.9, 8.6, 3.8, 5.6, C['gr'], 'trim')
    # re-draw paired windows over their surrounds
    for k in (-2, -1, 0, 1, 2):
        x = k * 4.6
        for dx in (-.85, .85):
            b.arch(x + dx - .65, 9.0, 1.3, 4.6, C['win'])
    for k in range(-4, 5):                                          # small top-row windows
        x = k * 2.6
        b.arch(x - .55, 16.2, 1.1, 2.2, C['win'])
    # front terrace balustrade
    balustrade(b, -30, 30, 0, 1.1, C['gr'], 0.8, 0.3)
    return b


def tryvann():
    b = B('tryvann', 'Tryvannstårnet')
    C = dict(c='#ddd6c6', c_hi='#ece7da', c_lo='#bdb5a3', c_dk='#9b937f', win='#2d3540', steel='#9aa0a8', steel_dk='#6c727b',
             red='#c8453a', dish='#e9ebee', dish_lo='#c4c8cd')

    def cyl(x0, x1, y0, y1, layer='base'):
        w = x1 - x0
        b.rect(x0, y0, w, y1 - y0, C['c'], layer)
        b.rect(x0 + w * .12, y0, w * .14, y1 - y0, C['c_hi'], 'shade')
        b.rect(x1 - w * .28, y0, w * .28, y1 - y0, C['c_lo'], 'shade')
        b.rect(x1 - w * .1, y0, w * .1, y1 - y0, C['c_dk'], 'shade')

    cyl(-3.7, 3.7, 0, 20.5)
    b.poly([(-3.7, 20.0), (3.7, 20.0), (7.0, 21.6), (-7.0, 21.6)], C['c_lo'])
    cyl(-7.0, 7.0, 21.5, 49.8)
    for y in range(24, 49, 3):
        b.line(-7, y, 7, y, C['c_lo'], 0.08)
    b.rect(-7.6, 49.8, 15.2, 3.4, C['c'])
    b.rect(-7.6, 50.5, 15.2, 1.9, C['win'], 'win')
    for x in range(-7, 8, 1):
        b.line(x, 50.5, x, 52.4, C['c_lo'], 0.1)
    b.rect(-7.9, 53.0, 15.8, 0.35, C['steel_dk'], 'trim')
    balustrade(b, -7.8, 7.8, 53.3, 1.0, C['steel'], 0.8, 0.12)
    # antenna platform
    b.rect(-1.6, 53.3, 3.2, 9.0, C['c'])
    b.rect(0.6, 53.3, 1.0, 9.0, C['c_lo'], 'shade')
    for dx, dy, r in ((-3.4, 56.6, 1.3), (3.2, 57.4, 1.2), (-2.8, 59.6, 0.9), (2.9, 60.1, 1.0)):
        b.ellipse(dx, dy, r * .55, r, C['dish'], 'trim')
        b.ellipse(dx + (0.25 if dx > 0 else -0.25), dy, r * .3, r * .8, C['dish_lo'], 'detail')
        b.line(0, dy, dx, dy, C['steel_dk'], 0.18)
    b.rect(-5.2, 61.8, 10.4, 0.6, C['steel_dk'], 'trim')
    for x in (-4.8, -2.4, 2.4, 4.8):
        b.line(x, 61.8, x * .4, 63.5, C['steel_dk'], 0.12)
    # lattice mast, red/white sections
    y0, y1 = 62.4, 111.0
    wb, wt = 1.25, 0.35

    def wx(y):
        return wb + (wt - wb) * (y - y0) / (y1 - y0)

    mast = [(-wb, y0), (wb, y0), (wt, y1), (-wt, y1)]
    b.poly(mast, C['steel'])
    nseg = 8
    for i in range(nseg):
        ya, yb = y0 + (y1 - y0) * i / nseg, y0 + (y1 - y0) * (i + 1) / nseg
        if i % 2 == 0:
            b.poly([(-wx(ya), ya), (wx(ya), ya), (wx(yb), yb), (-wx(yb), yb)], C['red'], 'trim')
    y = y0
    s = 1
    while y < y1 - 1:
        y2 = y + 1.6
        b.line(-wx(y) * s, y, wx(y2) * s, y2, C['steel_dk'], 0.09)
        y, s = y2, -s
    b.rect(-0.12, y1, 0.24, 7.0, C['steel_dk'], 'trim')
    b.circle(0, y1 + 7.1, 0.25, C['red'], 'detail')
    return b


def universitetet():
    b = B('universitetet', 'Universitetet (Domus Media)')
    C = dict(cr='#ece2c8', cr_lo='#d3c6a5', tr='#f6f1e3', tr_lo='#ddd5c1', gran='#c7ab95', gran_lo='#a98f7b',
             gran_dk='#8e7563', dark='#3b3633', win='#2b3340', win_hi='#4b5565', roof='#8b929a', roof_lo='#6f767e')
    for s in (-1, 1):
        x0, x1 = sorted((s * 13.2, s * 40.7))
        b.poly([(x0 + .5, 16.7), (x1 - .5, 16.7), (x1 - 1.2, 18.4), (x0 + 1.2, 18.4)], C['roof'])
        for cx in (x0 + 6, x1 - 8):
            b.rect(cx, 18.0, 1.0, 1.6, C['roof_lo'])
        b.rect(x0, 0, x1 - x0, 16.7, C['cr'])
        b.rect(x0, 0, x1 - x0, 1.4, C['cr_lo'], 'shade')
        b.rect(x0 - .3, 15.8, x1 - x0 + .6, 0.9, C['tr'], 'trim')
        b.rect(x0, 7.0, x1 - x0, 0.4, C['tr'], 'trim')
        for px in (x0, x1 - .9) if s < 0 else (x0, x1 - .9):
            b.rect(px, 1.4, 0.9, 14.4, C['cr_lo'], 'shade')
        n = 6
        for i in range(n):
            x = x0 + 2.6 + i * (x1 - x0 - 5.2) / (n - 1)
            b.window(x - 1.0, 9.0, 2.0, 4.6, C['win'], C['tr'], 0.25, C['win_hi'])
            b.rect(x - 1.4, 13.85, 2.8, 0.35, C['tr'], 'trim')
            b.window(x - 1.0, 2.4, 2.0, 3.6, C['win'], C['tr'], 0.25, C['win_hi'])
    # portico
    b.rect(-13.6, 0, 27.2, 16.8, C['dark'])
    for x in (-4.6, 0, 4.6):
        b.rect(x - 1.1, 1.0, 2.2, 4.0, '#4a3e34', 'win')
        b.rect(x - 1.1, 6.5, 2.2, 3.0, C['win'], 'win')
    b.rect(-13.6, 9.8, 27.2, 0.5, '#2c2826', 'shade')
    for s in (-1, 1):
        x0 = s * 13.6 - (2.6 if s > 0 else 0)
        b.rect(x0, 0, 2.6, 14.4, C['gran'], 'trim')
        b.rect(x0 + (1.8 if s > 0 else 0), 0, 0.8, 14.4, C['gran_lo'], 'shade')
        b.rect(x0 - .2, 13.6, 3.0, 0.8, C['gran_dk'], 'trim')
    for x in (-7.2, -2.4, 2.4, 7.2):
        b.poly([(x - .9, 1.1), (x + .9, 1.1), (x + .75, 13.4), (x - .75, 13.4)], C['gran'], 'trim')
        b.rect(x + .2, 1.1, .5, 12.3, C['gran_lo'], 'shade')
        b.rect(x - 1.1, 0.6, 2.2, 0.55, C['gran_dk'], 'trim')
        b.rect(x - 1.25, 13.4, 2.5, 0.5, C['gran_dk'], 'trim')     # ionic capital
        b.circle(x - 1.0, 13.3, .35, C['gran_dk'], 'trim')
        b.circle(x + 1.0, 13.3, .35, C['gran_dk'], 'trim')
        for dx in (-.45, 0, .45):
            b.line(x + dx, 1.5, x + dx, 13.0, C['gran_lo'], 0.07)
    b.rect(-14, 14.3, 28, 2.5, C['gran'], 'trim')
    b.rect(-14, 14.3, 28, 0.35, C['gran_dk'], 'shade')
    b.rect(-14.3, 16.5, 28.6, 0.45, C['gran_dk'], 'trim')
    b.poly([(-14.3, 16.9), (14.3, 16.9), (0, 22.4)], C['gran'])
    b.poly([(-12.2, 17.3), (12.2, 17.3), (0, 21.6)], C['gran_lo'], 'shade')
    for i in range(11):
        x = -7.5 + i * 1.5
        hgt = 3.2 - abs(x) * 0.38
        if hgt > 0.6:
            b.ellipse(x, 17.3 + hgt * .45, 0.42, hgt * .45, C['gran'], 'detail')
    b.poly([(-14.6, 16.8), (0, 22.5), (14.6, 16.8), (14.6, 17.2), (0, 22.9), (-14.6, 17.2)], C['gran_dk'], 'trim')
    b.poly([(-1.0, 22.6), (1.0, 22.6), (0.6, 23.8), (0, 24.2), (-0.6, 23.8)], C['tr'], 'trim')    # acroteria
    for s in (-1, 1):
        b.poly([(s * 14.3, 16.9), (s * 13.2, 16.9), (s * 13.6, 18.2)], C['tr'], 'trim')
    # steps
    for i in range(3):
        b.rect(-15 + i * .3, i * .35, 30 - i * .6, 0.35, C['gran_lo'] if i % 2 else C['gran'], 'trim')
    return b


def domkirken():
    """Oslo domkirke, west front: brick tower with clock, portal and the copper spire; the nave wings either side."""
    b = B('domkirken', 'Oslo domkirke')
    C = dict(br='#c9ad88', br_lo='#a98c69', br_dk='#8d7354', st='#ddd6c6', st_lo='#bdb3a0', roof='#3b3f47', roof_lo='#2d3138',
             cu='#4f4c47', cu_hi='#6e6a63', cu_dk='#3a3834', win='#2b3038', clock='#f2f0ea', door='#3d2e24', gold='#c9a23f')
    m = 0.09                                                       # photo px -> m (tower 157 px ≈ 14 m)
    X = lambda x: (x - 226) * m
    Y = lambda y: (655 - y) * m
    # nave wings (behind the tower)
    for s in (-1, 1):
        xo, xi = (X(30), X(150)) if s < 0 else (X(430), X(302))
        x0, x1 = min(xo, xi), max(xo, xi)
        b.rect(x0, 0, x1 - x0, Y(540), C['br'])
        b.poly([(xo, Y(540)), (xi, Y(540)), (xi, Y(482)), (xo - s * 2.6, Y(482))], C['roof'])
        b.poly([(xo, Y(540)), (xo + s * 1.2, Y(540)), (xo - s * 1.4, Y(482)), (xo - s * 2.6, Y(482))], C['roof_lo'], 'shade')
        b.rect(x0, Y(545), x1 - x0, 0.5, C['st'], 'trim')
        b.rect(x0, 0, x1 - x0, 0.9, C['st_lo'], 'trim')
        for k in range(3):
            cx = xo - s * (2.6 + k * 3.4)
            b.arch(cx - .8, 1.6, 1.6, 5.2, C['win'])
            b.rect(cx - 1.0, 1.4, 2.0, 0.25, C['st'], 'trim')
        # corner pinnacle
        px = xo + s * 0.2
        b.rect(px - .35, Y(540), .7, 1.6, C['st'])
        b.poly([(px - .35, Y(540) + 1.6), (px + .35, Y(540) + 1.6), (px, Y(540) + 4.2)], C['st'])
        yy = 1.2
        while yy < Y(540):
            b.line(x0, yy, x1, yy, C['br_lo'], 0.04)
            yy += 0.6
    # round stair turret on the north side (right)
    tx = X(323)
    b.rect(tx - 1.4, 0, 2.8, Y(520), C['br'])
    b.rect(tx + .5, 0, .9, Y(520), C['br_lo'], 'shade')
    b.poly([(tx - 1.5, Y(520))] + [(tx + 1.5 * math.cos(a), Y(520) + 1.6 * math.sin(a)) for a in
                                    [math.pi * i / 10 for i in range(11)]][::-1] + [(tx + 1.5, Y(520))], C['cu'])
    b.rect(tx - .08, Y(520) + 1.6, .16, 1.2, C['cu_dk'], 'trim')
    for y in (2.0, 5.0, 8.0):
        b.rect(tx - .25, y, .5, 1.2, C['win'], 'win')
    # tower
    tw0, tw1 = X(148), X(305)
    b.rect(tw0, 0, tw1 - tw0, Y(268), C['br'])
    b.rect(tw1 - 1.8, 0, 1.8, Y(268), C['br_lo'], 'shade')
    yy = 1.2
    while yy < Y(290):
        b.line(tw0, yy, tw1, yy, C['br_lo'], 0.04)
        yy += 0.6
    for xb in (tw0, tw1 - 1.1):                                    # stone buttress edges
        b.rect(xb, 0, 1.1, Y(500), C['st'], 'trim')
        b.rect(xb + .8, 0, .3, Y(500), C['st_lo'], 'shade')
        b.poly([(xb, Y(500)), (xb + 1.1, Y(500)), (xb + .55, Y(500) + 1.4)], C['st'], 'trim')
    b.rect(tw0, 0, tw1 - tw0, 1.0, C['st_lo'], 'trim')
    b.rect(tw0 - .3, Y(290), tw1 - tw0 + .6, 0.4, C['st'], 'trim')          # string course under the frieze
    for i in range(14):                                            # corbel frieze
        x = tw0 + .5 + i * (tw1 - tw0 - 1) / 13.0
        b.arch(x - .35, Y(285), .7, 1.0, C['br_dk'], 'detail')
    b.rect(tw0 - .5, Y(272), tw1 - tw0 + 1.0, 0.45, C['st'], 'trim')        # cornice
    b.rect(tw0 - .3, Y(334), tw1 - tw0 + .6, 0.35, C['st'], 'trim')         # course under the clock
    b.circle(0, Y(310), 1.7, C['st_lo'], 'trim')
    b.circle(0, Y(310), 1.5, C['clock'], 'trim')
    b.line(0, Y(310), 0.05, Y(310) + 1.1, C['win'], 0.14)
    b.line(0, Y(310), 0.85, Y(310) + 0.25, C['win'], 0.14)
    for x in (X(152 + 30), X(268)):                                 # slit windows beside the clock
        b.rect(x - .2, Y(322), .4, 1.2, C['win'], 'win')
    for x in (X(195), X(253)):                                      # belfry openings
        b.arch(x - .95, Y(415), 1.9, Y(352) - Y(415), C['st_lo'], 'trim')
        b.arch(x - .75, Y(413), 1.5, Y(352) - Y(415) - .3, C['win'])
        for k in range(1, 6):
            yy = Y(413) + k * 0.6
            b.line(x - .7, yy, x + .7, yy, C['br_dk'], 0.12)
    b.rect(-.25, Y(470), .5, 1.6, C['win'], 'win')
    # portal: pointed gable with pinnacles, rose window, round-arched door
    b.rect(X(186), 0, X(266) - X(186), Y(560), C['st'])
    b.poly([(X(184), Y(560)), (X(268), Y(560)), (0, Y(480))], C['st'])
    b.poly([(X(190), Y(562)), (X(262), Y(562)), (0, Y(488))], C['st_lo'], 'shade')
    for x in (X(184), X(268)):
        b.rect(x - .4, Y(560), .8, 2.6, C['st'], 'trim')
        b.poly([(x - .4, Y(560) + 2.6), (x + .4, Y(560) + 2.6), (x, Y(560) + 4.4)], C['st'], 'trim')
    b.circle(0, Y(530), 1.5, C['st'], 'trim')
    b.circle(0, Y(530), 1.15, C['win'], 'win')
    for i in range(6):
        a = math.pi * 2 * i / 6
        b.line(0, Y(530), 1.15 * math.cos(a), Y(530) + 1.15 * math.sin(a), C['st'], 0.12)
    b.arch(X(196), 0.9, X(256) - X(196), Y(568) - 0.9, C['st_lo'], 'trim')
    b.arch(X(203), 0.9, X(249) - X(203), Y(575) - 0.9, C['door'])
    b.line(0, 0.9, 0, Y(600), C['br_dk'], 0.1)
    # copper spire: bell, dormers, lantern, small bell, upper lantern, cap, finial
    bell = [(X(166), Y(268)), (X(286), Y(268))]
    for i in range(9):
        t = i / 8
        w = (X(286) - X(258)) * (1 - math.sin(t * math.pi / 2)) + (X(258) - 0)
        y = Y(268) + (Y(205) - Y(268)) * (1 - math.cos(t * math.pi / 2)) ** 0.8
        bell.append((w * (1 if True else 1), y))
    rb = bell[2:]
    bell_pts = [(X(166), Y(268)), (X(286), Y(268))] + rb + [(-x, y) for x, y in rb[::-1]]
    b.poly(bell_pts, C['cu'])
    b.poly([(0.8, Y(268))] + [(x * .55 + 1.6, y) for x, y in rb] + [(1.4, Y(205))], C['cu_hi'], 'shade')
    for x in (X(184), X(226), X(266)):                             # dormers
        y0 = Y(250)
        b.rect(x - .55, y0, 1.1, 1.6, C['cu'], 'trim')
        b.poly([(x - .75, y0 + 1.6), (x + .75, y0 + 1.6), (x, y0 + 2.6)], C['cu_dk'], 'trim')
        b.rect(x - .3, y0 + .2, .6, 1.0, C['win'], 'win')
        b.rect(x - .06, y0 + 2.6, .12, 1.0, C['cu_dk'], 'trim')
    for x in (X(172), X(280)):                                     # corner spikes
        b.poly([(x - .3, Y(262)), (x + .3, Y(262)), (x, Y(262) + 3.2)], C['cu_dk'], 'trim')
    lx = X(258)
    b.rect(-lx, Y(205), 2 * lx, Y(135) - Y(205), C['cu'])
    b.rect(lx - 1.0, Y(205), 1.0, Y(135) - Y(205), C['cu_dk'], 'shade')
    b.rect(-lx - .25, Y(205), 2 * lx + .5, .4, C['cu_dk'], 'trim')
    for x in (-1.3, 0, 1.3):
        b.arch(x - .4, Y(195), .8, 2.8, C['win'])
    b.rect(-lx - .3, Y(137), 2 * lx + .6, .5, C['cu_dk'], 'trim')
    sb = [(-lx, Y(135)), (lx, Y(135)), (X(243), Y(112)), (X(209), Y(112))]
    b.poly(sb, C['cu'])
    b.poly([(lx - .9, Y(135)), (lx, Y(135)), (X(243), Y(112)), (X(243) - .5, Y(112))], C['cu_dk'], 'shade')
    ux = X(242)
    b.rect(-ux, Y(112), 2 * ux, Y(84) - Y(112), C['cu'])
    b.rect(ux - .5, Y(112), .5, Y(84) - Y(112), C['cu_dk'], 'shade')
    for x in (-.55, .55):
        b.arch(x - .25, Y(108), .5, 1.6, C['win'])
    b.rect(-ux - .2, Y(86), 2 * ux + .4, .35, C['cu_dk'], 'trim')
    b.poly([(-ux, Y(84)), (ux, Y(84)), (.25, Y(52)), (-.25, Y(52))], C['cu'])
    b.poly([(ux - .4, Y(84)), (ux, Y(84)), (.25, Y(52)), (.1, Y(52))], C['cu_dk'], 'shade')
    b.rect(-.07, Y(52), .14, Y(20) - Y(52), C['cu_dk'], 'trim')
    b.circle(0, Y(40), .3, C['gold'], 'trim')
    b.poly([(0.07, Y(22)), (1.3, Y(24)), (1.1, Y(28)), (0.07, Y(28))], C['gold'], 'detail')       # weathervane
    return b


def grand():
    """Grand Hotel on Karl Johan: white facade, mansard roof with green-capped dormers, corner turret and the
    clock tower with its copper cupola; the newer grey annex on the right. No flags."""
    b = B('grand', 'Grand Hotel')
    C = dict(w='#eeebe4', w_lo='#d6d1c6', w_dk='#bdb6a8', roof='#3e434b', roof_lo='#30343b', cu='#6fae95', cu_lo='#4f8b74',
             cu_dk='#3e6f5d', win='#2b3038', win_hi='#4b5462', bal='#5b6068', grey='#c9ccce', grey_lo='#a9adb0',
             gwin='#4a5866', shop='#2f3238')
    m = 0.22
    X = lambda x: (x - 133) * m
    Y = lambda y: (245 - y) * m
    W0, W1, CORN = X(133), X(455), Y(142)
    # annex (right)
    a0, a1, ac = X(455), X(568), Y(150)
    b.rect(a0, 0, a1 - a0, ac, C['grey'])
    b.poly([(a0, ac), (a1, ac), (a1 - 1.5, ac + 4.2), (a0 + .5, ac + 4.6)], C['roof'])
    for k in range(2):
        b.rect(a0 + 1, ac + 0.8 + k * 1.8, a1 - a0 - 2.5, 1.0, C['gwin'], 'win')
    b.rect(a0, ac - .6, a1 - a0, .6, C['grey_lo'], 'trim')
    for r in range(6):
        y = 4.0 + r * 3.1
        x = a0 + 1.2
        while x < a1 - 1.5:
            b.rect(x, y, 1.6, 2.0, C['gwin'], 'win')
            x += 2.6
    b.rect(a0, 0, a1 - a0, 3.2, C['grey_lo'], 'shade')
    # main building
    b.rect(W0, 0, W1 - W0, CORN, C['w'])
    b.poly([(W0 + .3, CORN), (W1 - .3, CORN), (W1 - 2.2, CORN + 7.8), (W0 + 2.2, CORN + 7.8)], C['roof'])
    b.poly([(W0 + .3, CORN), (W0 + 2.2, CORN + 7.8), (W0 + 3.2, CORN + 7.8), (W0 + 1.6, CORN)], C['roof_lo'], 'shade')
    b.rect(W0 - .3, CORN - .7, W1 - W0 + .6, .8, C['w_lo'], 'trim')
    b.rect(W0, CORN - 1.2, W1 - W0, .3, C['w_dk'], 'shade')
    # floors: 5 rows of windows + shop floor
    cols = [W0 + 2.4 + i * 3.32 for i in range(21)]
    for r in range(5):
        y = 6.2 + r * 3.55
        for x in cols:
            b.window(x - .7, y, 1.4, 2.3, C['win'], C['w_lo'], 0.18, C['win_hi'])
        b.rect(W0, y - .45, W1 - W0, .22, C['w_lo'], 'trim')
    for x in cols[3::5]:                                           # balconies on floors 2 and 4
        for r in (1, 3):
            y = 6.2 + r * 3.55 - .5
            b.rect(x - 1.3, y, 2.6, .35, C['bal'], 'trim')
            b.line(x - 1.3, y + .9, x + 1.3, y + .9, C['bal'], 0.1)
            for dx in (-1.2, -.4, .4, 1.2):
                b.line(x + dx, y + .35, x + dx, y + .9, C['bal'], 0.07)
    b.rect(W0, 0, W1 - W0, 5.0, C['w_lo'])
    for x in cols[::2]:
        b.arch(x - 1.2, 0.4, 2.4, 3.9, C['shop'])
    b.rect(W0, 5.0, W1 - W0, .4, C['w_dk'], 'trim')
    # dormers with green copper gables
    for x in [W0 + 5 + i * 9.6 for i in range(8)]:
        if X(300) < x < X(372) or x < X(150) + 4.5 or x > W1 - 3:
            continue
        y0 = CORN + 1.4
        b.rect(x - 1.3, y0, 2.6, 2.6, C['w'], 'trim')
        b.rect(x - .7, y0 + .3, 1.4, 1.7, C['win'], 'win')
        b.poly([(x - 1.7, y0 + 2.6), (x + 1.7, y0 + 2.6), (x, y0 + 4.4)], C['cu'], 'trim')
        b.poly([(x, y0 + 2.6), (x + 1.7, y0 + 2.6), (x, y0 + 4.4)], C['cu_lo'], 'shade')
    # left corner turret with copper cap
    tx = X(150)
    b.rect(tx - 2.4, CORN, 4.8, 2.4, C['w'])
    b.poly([(tx - 2.6, CORN + 2.4)] + [(tx + 2.6 * math.cos(a), CORN + 2.4 + 3.6 * math.sin(a)) for a in
                                        [math.pi * i / 12 for i in range(13)]][::-1][:-1] + [(tx + 2.6, CORN + 2.4)], C['cu'])
    b.rect(tx - .1, CORN + 6.0, .2, 1.2, C['cu_dk'], 'trim')
    b.rect(tx - .5, CORN + .5, 1.0, 1.4, C['win'], 'win')
    # central clock tower
    t0, t1 = X(312), X(360)
    tt = Y(75)
    b.rect(t0, CORN, t1 - t0, tt - CORN, C['w'])
    b.rect(t1 - 1.4, CORN, 1.4, tt - CORN, C['w_lo'], 'shade')
    b.rect(t0 - .3, tt - .6, t1 - t0 + .6, .6, C['w_lo'], 'trim')
    cx = (t0 + t1) / 2
    b.arch(cx - 1.4, CORN + 1.2, 2.8, 4.6, C['win'])
    b.circle(cx, CORN + 8.2, 1.4, C['w_dk'], 'trim')
    b.circle(cx, CORN + 8.2, 1.2, '#f6f4ee', 'trim')
    b.line(cx, CORN + 8.2, cx + .1, CORN + 9.1, C['win'], 0.12)
    b.line(cx, CORN + 8.2, cx + .7, CORN + 8.0, C['win'], 0.12)
    for x in (t0 + .8, t1 - 1.6):
        b.rect(x, CORN + 2, .8, 3.4, C['win'], 'win')
    for x in range(3):
        b.rect(cx - 2.6 + x * 2.2, CORN - .2, .9, .8, C['w_dk'], 'detail')
    # cupola: drum, bell dome, lantern, spike
    d0, d1 = cx - 3.6, cx + 3.6
    b.rect(d0, tt, d1 - d0, 1.8, C['w'])
    for x in (-2.4, 0, 2.4):
        b.arch(cx + x - .45, tt + .2, .9, 1.4, C['win'])
    dome = [(cx + 3.9 * math.cos(a), tt + 1.8 + 4.6 * math.sin(a) ** 1.3) for a in [math.pi * i / 16 for i in range(17)]]
    b.poly(dome, C['cu'])
    b.poly([(cx + 1.0, tt + 1.8)] + [p for p in dome[:8]], C['cu_lo'], 'shade')
    b.rect(cx - .7, tt + 6.2, 1.4, 1.6, C['cu_lo'])
    b.poly([(cx - .9, tt + 7.8), (cx + .9, tt + 7.8), (cx, tt + 9.4)], C['cu'])
    b.rect(cx - .06, tt + 9.4, .12, 1.4, C['cu_dk'], 'trim')
    return b


def postgiro():
    """Postgirobygget: two slab towers, the right one taller, joined by a glazed core; bronze spandrels
    alternate with window bands; the top floors are all glass. No signs."""
    b = B('postgiro', 'Postgirobygget')
    C = dict(br='#8a7560', br_lo='#6f5d4b', br_hi='#a48e76', gl='#5b7590', gl_hi='#8fa9c2', gl_dk='#3e536a',
             core='#3f5a70', core_ln='#6d8ba5', mull='#c4ccd4')
    L0, L1, LT = 0.0, 32.4, 103.0                      # left tower
    C0, C1, CT = 32.4, 36.4, 101.5                     # glazed core, just below the left tower
    R0, R1, RT = 36.4, 68.8, 111.0                     # right tower
    glass_from = LT - 12.0                             # window bands stop at the same height on both towers
    for x0, x1, top in ((L0, L1, LT), (R0, R1, RT)):
        b.rect(x0, 0, x1 - x0, top, C['br'])
        y = 4.0
        while y < glass_from:
            b.rect(x0, y + 1.6, x1 - x0, 1.75, C['gl'], 'win')
            y += 3.55
        b.rect(x0, glass_from, x1 - x0, top - glass_from, C['gl_dk'], 'win')
        b.poly([(x0, glass_from + 3), (x1, glass_from + 9), (x1, glass_from + 10), (x0, glass_from + 4)], C['gl_hi'], 'win',
               ' opacity=".4"')
        k = 0
        x = x0 + 1.2
        while x < x1:
            b.line(x, 4.0, x, top, C['mull'], 0.07)
            x += 1.2
            k += 1
        b.rect(x1 - 1.2, 0, 1.2, top, C['br_lo'], 'shade')
        b.rect(x0, top - .4, x1 - x0, .4, C['br_hi'], 'trim')
        b.rect(x0, 0, x1 - x0, 4.0, C['gl_dk'], 'win')
    b.rect(C0, 0, C1 - C0, CT, C['core'])
    for y in range(2, int(CT), 3):
        b.line(C0, y, C1, y, C['core_ln'], 0.08)
    b.line((C0 + C1) / 2, 0, (C0 + C1) / 2, CT, C['core_ln'], 0.1)
    b.rect(R0 + 8, RT, 0.25, 4.0, C['br_lo'], 'trim')            # antenna stub
    return b


LANDMARKS = [holmenkollen, munch, plaza, tryvann, radhuset, opera, slottet, stortinget, nationaltheatret, universitetet,
             monolitten, domkirken, grand, postgiro]


def render(files):
    OUT.mkdir(parents=True, exist_ok=True)
    for name, svg in files.items():
        (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        for name, svg in files.items():
            w, h = map(float, re.search(r'width="([\d.]+)" height="([\d.]+)"', svg).groups())
            pg = br.new_page(viewport={'width': math.ceil(w), 'height': math.ceil(h)}, device_scale_factor=2)
            pg.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
            pg.locator('svg').screenshot(path=str(OUT / f'{name}.png'), omit_background=True)
            pg.close()
            print('wrote', OUT / f'{name}.svg', '+ .png')
        br.close()


if __name__ == '__main__':
    import sys
    only = set(sys.argv[1:])
    render({b.name: b.svg() for b in (fn() for fn in LANDMARKS) if not only or b.name in only})
