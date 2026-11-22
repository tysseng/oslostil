#!/usr/bin/env python3
"""Hand-built pixel art of the local trains, redrawn on a pixel grid from the hi-res designs.

Not an image downscale: every shape is re-rasterised without anti-aliasing at the target scale,
details get fixed pixel sizes (windows, doors, wheels), and outlines are exactly 1 px.
Scale: 8 px per metre (the hi-res masters use 50 units per metre).

Usage: python3 tools/vehicles/pixel_trains.py  → assets/sprites/train-green.png, train-tomato.png (+ preview)
"""
from pathlib import Path
from PIL import Image, ImageDraw

S = 8 / 50                      # pixels per hi-res unit
INK = (21, 26, 34, 255)
OUT = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'


def hexc(h, a=255):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def p(v):
    return int(round(v * S))


def sample_path(d):
    """Polyline points (hi-res units) for an SVG path made of M/L/Q/Z commands."""
    toks = d.replace(',', ' ').split()
    pts, i, cur = [], 0, (0, 0)
    while i < len(toks):
        t = toks[i]
        cmd, rest = t[0], t[1:]
        if cmd in 'MLQ':
            nums = [float(rest)] if rest else []
            i += 1
            need = 2 if cmd in 'ML' else 4
            while len(nums) < need:
                nums.append(float(toks[i])); i += 1
            if cmd in 'ML':
                cur = (nums[0], nums[1]); pts.append(cur)
            else:
                (cx, cy, x, y), (x0, y0) = nums, cur
                for k in range(1, 9):
                    u = k / 8
                    pts.append(((1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y))
                cur = (x, y)
        else:
            i += 1
    return pts


class Pix:
    def __init__(self, w, h):
        self.img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def mask(self, d):
        m = Image.new('1', self.img.size, 0)
        ImageDraw.Draw(m).polygon([(p(x), p(y)) for x, y in sample_path(d)], fill=1)
        return m

    def fill(self, m, color):
        self.img.paste(Image.new('RGBA', self.img.size, color), (0, 0), m)

    def rect(self, x, y, w, h, color, clip=None):
        """x, y, w, h in pixels."""
        if w <= 0 or h <= 0:
            return
        if clip is None:
            self.d.rectangle([x, y, x + w - 1, y + h - 1], fill=color)
        else:
            m = Image.new('1', self.img.size, 0)
            ImageDraw.Draw(m).rectangle([x, y, x + w - 1, y + h - 1], fill=1)
            self.img.paste(Image.new('RGBA', self.img.size, color), (0, 0), Image.composite(m, Image.new('1', m.size, 0), clip))

    def poly(self, pts_px, color, clip=None):
        m = Image.new('1', self.img.size, 0)
        ImageDraw.Draw(m).polygon(pts_px, fill=1)
        if clip is not None:
            m = Image.composite(m, Image.new('1', m.size, 0), clip)
        self.img.paste(Image.new('RGBA', self.img.size, color), (0, 0), m)

    def outline(self, m, color=INK):
        """1 px outline on the inside edge of a mask."""
        w, h = m.size
        px = m.load()
        for y in range(h):
            for x in range(w):
                if px[x, y] and any(not (0 <= x + dx < w and 0 <= y + dy < h) or not px[x + dx, y + dy]
                                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    self.img.putpixel((x, y), color)

    def window(self, x, y, w, h, glass, shine, frame=INK):
        self.rect(x, y, w, h, frame)
        self.rect(x + 1, y + 1, w - 2, h - 2, glass)
        for k in range(h - 2):                      # one diagonal glint line
            gx = x + 2 + (h - 3 - k) // 2 + 1
            if x + 1 <= gx < x + w - 1:
                self.img.putpixel((gx, y + 1 + k), shine)

    def wheel(self, cx, by, tyre=(43, 46, 54, 255), hub=(139, 145, 156, 255)):
        """7×7 pixel wheel standing on row by."""
        rows = ['..###..', '.#####.', '###H###', '##HHH##', '###H###', '.#####.', '..###..']
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch != '.':
                    self.img.putpixel((cx - 3 + i, by - 6 + j), hub if ch == 'H' else tyre)
        # outline around the wheel
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch == '#' and (i in (0, 6) or j in (0, 6) or r[i - 1] == '.' or r[i + 1] == '.'):
                    self.img.putpixel((cx - 3 + i, by - 6 + j), INK)

    def bogie(self, cx, by, span, frame):
        self.rect(cx - span // 2 - 6, by - 8, span + 12, 4, INK)
        self.rect(cx - span // 2 - 5, by - 7, span + 10, 2, frame)
        self.wheel(cx - span // 2, by)
        self.wheel(cx + span // 2, by)


# ---------------------------------------------------------------- green local train (FLIRT style)
FL = {k: hexc(v) for k, v in dict(green='#0f6153', green_hi='#1f7d6b', green_lo='#0a4339', roof='#c6cbd0', roof_lo='#9aa1a8',
                                   door='#17725f', door_frame='#2b3a3e', glass='#1d2a33', shine='#4b6b78', line='#3f9483').items()}


def flirt_path(x0, L, kind, top=26, bot=226, nose=170):
    if kind == 'cab':
        return (f'M{x0 + nose},{top} L{x0 + L - 14},{top} Q{x0 + L},{top} {x0 + L},{top + 14} L{x0 + L},{bot} '
                f'L{x0 + 34},{bot} Q{x0 + 2},{bot} {x0 + 4},{bot - 30} L{x0 + 14},{bot - 82} Q{x0 + 52},{top + 22} {x0 + nose},{top} Z')
    if kind == 'tail':
        xe = x0 + L
        return (f'M{xe - nose},{top} L{x0 + 14},{top} Q{x0},{top} {x0},{top + 14} L{x0},{bot} '
                f'L{xe - 34},{bot} Q{xe - 2},{bot} {xe - 4},{bot - 30} L{xe - 14},{bot - 82} Q{xe - 52},{top + 22} {xe - nose},{top} Z')
    return f'M{x0 + 14},{top} L{x0 + L - 14},{top} Q{x0 + L},{top} {x0 + L},{top + 14} L{x0 + L},{bot} L{x0},{bot} L{x0},{top + 14} Q{x0},{top} {x0 + 14},{top} Z'


def green_train(cars=3):
    L, gap = 1000, 18
    xs = [i * (L + gap) for i in range(cars)]
    kinds = ['cab'] + ['mid'] * (cars - 2) + ['tail']
    W, Hh = p(cars * L + (cars - 1) * gap) + 1, 43
    pix = Pix(W, Hh)
    by = 42                                            # wheel bottom row (rail level)
    # bogies behind: end bogies + shared bogies at the joints
    for cx in [xs[0] + 240] + [x + L + gap / 2 for x in xs[:-1]] + [xs[-1] + L - 240]:
        pix.bogie(p(cx), by, 14, hexc('#30343d'))
    for x in xs[:-1]:                                  # rubber connection
        pix.rect(p(x + L) - 1, 7, p(gap) + 3, 29, INK)
        pix.rect(p(x + L), 8, p(gap) + 1, 27, hexc('#2a2d34'))
    for x, k in zip(xs, kinds):
        m = pix.mask(flirt_path(x, L, k))
        x0 = p(x)
        pix.fill(m, FL['green'])
        pix.rect(x0 - 2, 0, p(L) + 4, 10, FL['roof'], m)              # grey roof
        pix.rect(x0 - 2, 10, p(L) + 4, 1, FL['roof_lo'], m)
        pix.rect(x0 - 2, 11, p(L) + 4, 1, FL['green_hi'], m)
        pix.rect(x0 - 2, 25, p(L) + 4, 1, FL['line'], m)              # thin light line
        pix.rect(x0 - 2, 33, p(L) + 4, 3, FL['green_lo'], m)
        if k == 'mid':
            doors, wins = [.22, .72], [.05, .37, .48, .59, .86]
        elif k == 'cab':
            doors, wins = [.62], [.44, .78, .89]
        else:
            doors, wins = [.30], [.05, .16, .48]
        for wx in wins:
            pix.window(x0 + p(L * wx), 13, 12, 9, FL['glass'], FL['shine'])
        for dx in doors:
            dxp = x0 + p(L * dx)
            pix.rect(dxp - 2, 9, 17, 27, FL['door_frame'], m)
            for lx in (dxp, dxp + 7):
                pix.rect(lx, 11, 6, 25, INK)
                pix.rect(lx + 1, 12, 4, 24, FL['door'])
                pix.window(lx + 1, 13, 4, 11, FL['glass'], FL['shine'])
            pix.rect(dxp + 5, 27, 3, 1, hexc('#d8f3ea'))
        # cab: sloping side window, cab door window
        if k in ('cab', 'tail'):
            if k == 'cab':
                pts = [(x0 + 6, 24), (x0 + 13, 13), (x0 + 19, 9), (x0 + 29, 9), (x0 + 29, 24)]
                cdx = x0 + p(200)
            else:
                xe = p(x + L)
                pts = [(xe - 6, 24), (xe - 13, 13), (xe - 19, 9), (xe - 29, 9), (xe - 29, 24)]
                cdx = xe - p(254)
            pix.poly(pts, INK, m)
            inner = [(a + (1 if k == 'cab' else -1) * (1 if i == 0 else 0), b + (0 if i in (3, 4) else 0)) for i, (a, b) in enumerate(pts)]
            pix.poly([(a + (1 if k == 'cab' else -1), b + 1) if i < 3 else (a + (-1 if k == 'cab' else 1), b + (1 if i == 3 else -1)) for i, (a, b) in enumerate(pts)], FL['glass'], m)
            for t in range(7):  # glint
                gx = (x0 + 16 - t // 2 + 3) if k == 'cab' else (p(x + L) - 21 + t // 2)
                pix.img.putpixel((gx, 11 + t), FL['shine'])
            pix.window(cdx, 13, 9, 9, FL['glass'], FL['shine'])
        pix.outline(m)
        # roof equipment (outside the body)
        for rx in ([.3, .62] if k == 'mid' else ([.5] if k == 'cab' else [.32])):
            ax = x0 + p(L * rx)
            pix.rect(ax, 1, 24, 4, INK)
            pix.rect(ax + 1, 2, 22, 2, FL['roof_lo'])
        # skirt
        sx = x0 + (p(60) if k == 'cab' else p(30))
        pix.rect(sx, 36, p(L - 90 if k != 'mid' else L - 60), 2, INK)
    return pix.img


# ---------------------------------------------------------------- tomato soup (NSB type 69 style)
TS = {k: hexc(v) for k, v in dict(red='#e2392b', red_lo='#b52a20', red_hi='#f0604e', grey='#b8bdc2', grey_lo='#8e959c', roof='#d3d6d9',
                                   door='#f47b29', door_lo='#c95e18', stripe='#e9e6e2', glass='#262b33', shine='#59656f', frame='#9da3a9').items()}


def t69_path(x0, L, kind, top=30, bot=226):
    if kind == 'cab':
        return (f'M{x0 + 46},{top} L{x0 + L - 12},{top} Q{x0 + L},{top} {x0 + L},{top + 12} L{x0 + L},{bot} '
                f'L{x0 + 18},{bot} Q{x0 + 4},{bot} {x0 + 4},{bot - 14} L{x0 + 8},{top + 60} Q{x0 + 12},{top} {x0 + 46},{top} Z')
    if kind == 'tail':
        xe = x0 + L
        return (f'M{xe - 46},{top} L{x0 + 12},{top} Q{x0},{top} {x0},{top + 12} L{x0},{bot} '
                f'L{xe - 18},{bot} Q{xe - 4},{bot} {xe - 4},{bot - 14} L{xe - 8},{top + 60} Q{xe - 12},{top} {xe - 46},{top} Z')
    return f'M{x0 + 12},{top} L{x0 + L - 12},{top} Q{x0 + L},{top} {x0 + L},{top + 12} L{x0 + L},{bot} L{x0},{bot} L{x0},{top + 12} Q{x0},{top} {x0 + 12},{top} Z'


def tomato_train(cars=3):
    L, gap = 900, 26
    xs = [i * (L + gap) for i in range(cars)]
    kinds = ['cab'] + ['mid'] * (cars - 2) + ['tail']
    W, Hh = p(cars * L + (cars - 1) * gap) + 1, 43
    pix = Pix(W, Hh)
    by = 42
    for x in xs:  # two bogies per car, behind the body
        pix.bogie(p(x + 150), by, 14, hexc('#3b3f47'))
        pix.bogie(p(x + L - 150), by, 14, hexc('#3b3f47'))
    for x in xs[:-1]:
        pix.rect(p(x + L) - 1, 9, p(gap) + 3, 27, INK)
        pix.rect(p(x + L), 10, p(gap) + 1, 25, hexc('#2a2d34'))
    for x, k in zip(xs, kinds):
        m = pix.mask(t69_path(x, L, k))
        x0 = p(x)
        pix.fill(m, TS['red'])
        pix.rect(x0 - 2, 0, p(L) + 4, 8, TS['roof'], m)
        pix.rect(x0 - 2, 8, p(L) + 4, 2, TS['red'], m)               # red band under the roof
        pix.rect(x0 - 2, 10, p(L) + 4, 15, TS['grey'], m)            # grey window band
        pix.rect(x0 - 2, 10, p(L) + 4, 1, TS['grey_lo'], m)
        pix.rect(x0 - 2, 25, p(L) + 4, 1, TS['red_hi'], m)
        for y in (29, 31):
            pix.rect(x0 - 2, y, p(L) + 4, 1, TS['stripe'], m)       # pinstripes
        pix.rect(x0 - 2, 34, p(L) + 4, 2, TS['red_lo'], m)
        if k == 'cab':
            doors, wins = [.17, .84], [.30 + .1 * i for i in range(5)]
        elif k == 'tail':
            doors, wins = [.05, .72], [.18 + .1 * i for i in range(5)]
        else:
            doors, wins = [.05, .86], [.17 + .1 * i for i in range(6)]
        for wx in wins:
            pix.window(x0 + p(L * wx), 12, 11, 10, TS['glass'], TS['shine'], frame=INK)
        for dx in doors:
            dxp = x0 + p(L * dx)
            pix.rect(dxp, 8, 14, 28, INK, m)
            pix.rect(dxp + 1, 9, 12, 27, TS['door'], m)
            pix.rect(dxp + 7, 9, 1, 27, INK, m)
            pix.rect(dxp + 1, 33, 12, 2, TS['door_lo'], m)
            pix.window(dxp + 2, 12, 4, 11, TS['glass'], TS['shine'])
            pix.window(dxp + 9, 12, 4, 11, TS['glass'], TS['shine'])
        if k in ('cab', 'tail'):  # grey cab end + cab side window
            if k == 'cab':
                pix.rect(x0, 0, 5, 40, TS['grey'], m)
                pix.rect(x0 + 4, 10, 1, 22, TS['grey_lo'], m)
                pix.window(x0 + p(54), 12, 12, 10, TS['glass'], TS['shine'])
            else:
                xe = p(x + L)
                pix.rect(xe - 5, 0, 6, 40, TS['grey'], m)
                pix.rect(xe - 5, 10, 1, 22, TS['grey_lo'], m)
                pix.window(xe - p(126), 12, 12, 10, TS['glass'], TS['shine'])
        pix.outline(m)
        for vx in [.25 + .18 * i for i in range(4)]:   # roof vents
            ax = x0 + p(L * vx)
            pix.rect(ax, 2, 8, 3, INK)
            pix.rect(ax + 1, 3, 6, 1, hexc('#9aa1a8'))
        for bx in (.32, .52):                           # underfloor boxes
            pix.rect(x0 + p(L * bx), 36, p(130), 3, INK)
    return pix.img


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    g, t = green_train(3), tomato_train(3)
    g.save(OUT / 'train-green.png')
    t.save(OUT / 'train-tomato.png')
    print('wrote', OUT / 'train-green.png', g.size)
    print('wrote', OUT / 'train-tomato.png', t.size)
