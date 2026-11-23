#!/usr/bin/env python3
"""Pixel-art street lamps at «girl scale» (girls are 30 px tall), plus their light on a separate sheet.

Front views, drawn 1:1 on the pixel grid in the props style (tools/sprites/props.py): outlines tinted
per material, 3–4 tone shading, hand-placed in-between tones on curves. References: inspiration/lamps/.

  roadside   modern road lamp, one curved arm (points left; mirror for right) ... ≈ 2 × girl
  roadside2  the same pole with two arms ........................................ ≈ 2 × girl
  round      milky globe on an ornate black pole ................................ a bit lower
  vintage    lantern on a dark green cast-iron pole with a ladder bar ........... ≈ phone booth
  subway     T-bane platform lamp, two rising arms, seen from the front  
  tokyo_lamp Tokyoslo: vermilion lacquer post, red paper lantern on a curved arm .. ≈ 2 × girl
  toro       Tokyoslo: stone lantern (tōrō), lit fire box, flat top ............. 36 px, one jump ......... taller than roadside

Two sheets with the SAME grid (CELL_W × CELL_H, one lamp per row):
  assets/sprites/lamps.png        the lamps (opaque pixels). Draw behind the characters.
  assets/sprites/lamps-light.png  the light: smooth semi-transparent gradients with softly blurred
                                  edges (no dither). Roadside/subway: downward cones; round: radial,
                                  strongest downwards; vintage: sideways and down from the panes,
                                  cut by the roof. Plus a pool on the ground. Draw in front of the characters at the same
                                  position (normal alpha works; 'screen' or 'lighter' is brighter).
Each lamp's POLE (not its bounding box) is centred on x = CELL_W // 2, base on the bottom row.
JSON assets/sprites/lamps.json: {name: {row, frames, fps, w, h, top, top_span, heads}}
  w × h     visible size of the lamp (not the light)
  top       height of the highest walkable surface (a lamp head) above the base, px
  top_span  [dx0, dx1]: that surface's extent relative to the pole centre, px
  heads     [[dx, height], …]: light sources relative to the pole base (for glow / effects)
Usage: python3 tools/sprites/lamps.py
"""
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from props import Canvas, RAMP, rgb, mix  # noqa: E402

CELL_W, CELL_H = 96, 80
PX = CELL_W // 2          # pole centre
YB = CELL_H - 2           # lowest drawn row (outline goes on the bottom row)

RAMP.update({
    'pole':   [rgb(c) for c in ('#1a1f2a', '#3a4252', '#5a6476', '#7d889a', '#a6b0c0', '#d4dbe6')],   # galvanised grey
    'iron':   [rgb(c) for c in ('#0c0f14', '#171b24', '#232936', '#323a4a', '#4a5468', '#6c7890')],   # black cast iron
    'vgreen': [rgb(c) for c in ('#08170f', '#11281c', '#1a3a29', '#245038', '#356c4c', '#5c9a74')],   # old lamp green
    'lampW':  [rgb(c) for c in ('#6a5a3a', '#c8a860', '#f0cc78', '#ffe6a0', '#fff4cc', '#ffffff')],   # warm lit glass
    'lampC':  [rgb(c) for c in ('#40506a', '#8aa4c8', '#c0d8f0', '#e4f2ff', '#f4faff', '#ffffff')],   # cool LED
    'globe':  [rgb(c) for c in ('#5a5040', '#b8a888', '#e0d4b8', '#f8f0dc', '#fffaf0', '#ffffff')],   # milky globe
})

WARM, COOL = rgb('#ffd27a'), rgb('#d6ecff')


def at(dx, h):
    """cell coords from (offset from pole centre, height above base)"""
    return PX + dx, YB - h


class Lamp(Canvas):
    def __init__(self):
        super().__init__(CELL_W, CELL_H)
        self.heads = []

    def r(self, dx0, h0, dx1, h1, mat, tone):
        """rect between two (dx, height) corners"""
        x0, y1 = at(dx0, h0)
        x1, y0 = at(dx1, h1)
        self.rect(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), mat, tone)

    def p(self, dx, h, mat, tone):
        x, y = at(dx, h)
        self.set(x, y, mat, tone)

    def pole(self, h0, h1, mat, width=3, light_left=True):
        """vertical pole, cylinder shading: highlight left of centre, shade on the right"""
        xs = list(range(-(width // 2), width - width // 2))
        tones = {2: [4, 2], 3: [4, 3, 2], 4: [3, 5, 3, 2], 5: [3, 5, 4, 3, 2]}[width]
        for i, dx in enumerate(xs):
            self.r(dx, h0, dx, h1, mat, tones[i])

    def path(self, pts, mat, tones):
        """thick arm along a list of (dx, height) points; tones[0] is the top edge, tones[-1] the underside"""
        for (ax, ah), (bx, bh) in zip(pts, pts[1:]):
            n = max(abs(bx - ax), abs(bh - ah))
            for i in range(n + 1):
                x = round(ax + (bx - ax) * i / max(1, n))
                h = round(ah + (bh - ah) * i / max(1, n))
                for k, t in enumerate(tones):
                    self.p(x, h - k, mat, t)

    def finish(self):
        self.outline()
        self.soften()
        return self


# --------------------------------------------------------------------------- roadside
def roadside_arm(L, side):
    s = side
    # the arm leaves the pole top, bends over in a smooth curve and runs out almost level
    pts = [(0, 52), (s * 1, 54), (s * 2, 55), (s * 4, 56), (s * 7, 57), (s * 12, 58), (s * 16, 58)]
    L.path(pts, 'pole', [4, 2])
    # luminaire: a flat oval head, light grey shell on top and a lit lens underneath
    hx0, hx1 = (s * 15, s * 25)
    a, b = min(hx0, hx1), max(hx0, hx1)
    L.r(a + 1, 59, b - 1, 59, 'pole', 5)
    L.r(a, 58, b, 57, 'pole', 4)
    L.r(a, 56, b, 56, 'pole', 2)
    L.r(a + 2, 55, b - 2, 55, 'lampC', 4)
    L.p(a + 1, 55, 'lampC', 1); L.p(b - 1, 55, 'lampC', 1)
    for dx in range(a + 1, a + 4):
        L.p(dx, 59, 'pole', 5)
    cx = (a + b) // 2
    L.heads.append((cx, 55))
    return (a, b)


def roadside(double=False):
    L = Lamp()
    L.r(-3, 0, 3, 1, 'pole', 2); L.r(-2, 2, 2, 3, 'pole', 3); L.r(-2, 2, -2, 3, 'pole', 4)  # base flange
    L.pole(4, 30, 'pole', 3)
    L.pole(31, 54, 'pole', 2)
    L.r(-2, 30, 1, 30, 'pole', 1)                                     # joint ring
    span = roadside_arm(L, -1)
    if double:
        span2 = roadside_arm(L, 1)
        L.r(-1, 55, 1, 56, 'pole', 3)
        span = (span[0], span2[1])
    L.finish()
    return L, 59, span


# --------------------------------------------------------------------------- round globe
def round_lamp():
    L = Lamp()
    # flared foot
    L.r(-4, 0, 4, 1, 'iron', 2); L.r(-3, 2, 3, 3, 'iron', 3); L.r(-2, 4, 2, 7, 'iron', 3)
    L.r(-3, 2, -3, 3, 'iron', 4); L.r(-2, 4, -2, 7, 'iron', 4); L.r(2, 4, 2, 7, 'iron', 2)
    L.r(-3, 8, 3, 8, 'iron', 4)
    L.pole(9, 38, 'iron', 3)
    for h in (14, 26):                                                 # rings
        L.r(-2, h, 2, h, 'iron', 4); L.r(2, h, 2, h, 'iron', 2)
    L.pole(39, 42, 'iron', 2)
    L.r(-2, 43, 2, 43, 'iron', 4); L.r(-3, 44, 3, 44, 'iron', 3)      # collar
    # milky globe, 11 px across, lit from inside: bright core, darker rim, hand-AA edge
    cy = 50
    for y in range(-5, 6):
        for x in range(-5, 6):
            d = (x + 0.5) ** 2 + (y - 0.5) ** 2
            if d > 30.5:
                continue
            core = (x + 1.2) ** 2 + (y - 1.5) ** 2
            t = 5 if core < 4 else 4 if core < 12 else 3 if d < 20 else 2
            L.p(x, cy + y, 'globe', t)
    L.heads.append((0, cy))
    L.finish()
    return L, cy + 6, (-2, 2)


# --------------------------------------------------------------------------- vintage lantern
def vintage():
    L = Lamp()
    # square plinth with a stepped top
    L.r(-4, 0, 4, 1, 'vgreen', 2)
    L.r(-3, 2, 3, 9, 'vgreen', 3); L.r(-3, 2, -3, 9, 'vgreen', 4); L.r(3, 2, 3, 9, 'vgreen', 2)
    L.r(-1, 4, 1, 7, 'vgreen', 2)                                      # panel
    L.r(-3, 10, 3, 10, 'vgreen', 4); L.r(-2, 11, 2, 12, 'vgreen', 3)
    L.pole(13, 26, 'vgreen', 3)
    L.r(-2, 20, 2, 20, 'vgreen', 4)                                    # ring
    L.pole(27, 28, 'vgreen', 2)
    # ladder bar under the lantern, with little ball ends
    L.r(-6, 27, 6, 27, 'vgreen', 4); L.r(-6, 26, 6, 26, 'vgreen', 2)
    L.p(-7, 27, 'vgreen', 3); L.p(7, 27, 'vgreen', 3)
    # lantern: tapered bottom, lit panes with dark frames, pointed roof and finial
    L.r(-2, 29, 2, 29, 'vgreen', 3)
    L.r(-3, 30, 3, 30, 'vgreen', 4)
    L.r(-4, 31, 4, 37, 'vgreen', 2)
    L.r(-3, 31, 3, 37, 'lampW', 3)
    L.r(-2, 33, -1, 36, 'lampW', 5); L.r(1, 32, 2, 36, 'lampW', 4)
    L.r(0, 31, 0, 37, 'vgreen', 1)                                     # middle mullion
    L.r(-3, 31, -3, 37, 'lampW', 2); L.r(3, 31, 3, 37, 'lampW', 1)
    L.r(-5, 38, 5, 38, 'vgreen', 4)                                    # roof eave
    L.r(-4, 39, 4, 39, 'vgreen', 3)
    L.r(-3, 40, 3, 40, 'vgreen', 3); L.r(-2, 41, 2, 41, 'vgreen', 4); L.r(-1, 42, 1, 42, 'vgreen', 3)
    L.p(0, 43, 'vgreen', 5)
    L.r(-3, 40, -2, 40, 'vgreen', 4)
    L.heads.append((0, 34))
    L.finish()
    return L, 43, (-1, 1)


# --------------------------------------------------------------------------- subway platform lamp
def subway_arm(L, s):
    # straight arm rising outward at about 25°, from the pole near the top
    L.path([(s * 1, 58), (s * 15, 64)], 'pole', [4, 2])
    # long flat luminaire continuing the arm, lit lens underneath
    for i in range(13):
        x = s * (14 + i)
        h = 64 + round(i * 6 / 14)
        L.p(x, h + 1, 'pole', 5 if 1 <= i <= 4 else 4)
        L.p(x, h, 'pole', 3)
        L.p(x, h - 1, 'lampC', 4 if 1 <= i <= 11 else 2)
    L.heads.append((s * 20, 65))


def subway():
    L = Lamp()
    L.r(-3, 0, 3, 1, 'pole', 2); L.r(-2, 2, 2, 3, 'pole', 3)
    L.pole(4, 70, 'pole', 3)
    L.r(-1, 71, 1, 71, 'pole', 4)
    subway_arm(L, -1)
    subway_arm(L, 1)
    L.finish()
    return L, 72, (-1, 1)


# --------------------------------------------------------------------------- Tokyoslo
import tokyo_props  # noqa: E402,F401  (registers the lacquer, gold, paper and stone ramps)


def tokyo_lamp():
    """vermilion lacquer post with a curved arm and a red paper lantern, a little pagoda cap on top"""
    L = Lamp()
    L.r(-4, 0, 4, 1, 'lblk', 2); L.r(-3, 2, 3, 4, 'lblk', 3); L.r(-3, 2, -3, 4, 'lblk', 4)
    L.pole(5, 54, 'lacq', 3)
    for h in (9, 30, 48):
        L.r(-2, h, 2, h, 'tgold', 4); L.r(2, h, 2, h, 'tgold', 2)
    # pagoda cap with upturned eaves, flat on top
    L.r(-5, 55, 5, 55, 'lblk', 3); L.p(-6, 56, 'lblk', 3); L.p(6, 56, 'lblk', 2)
    L.r(-4, 56, 4, 56, 'lblk', 4); L.r(-2, 57, 2, 58, 'lblk', 3); L.r(-2, 58, 0, 58, 'lblk', 4)
    L.p(0, 59, 'tgold', 5)
    # curved arm to the left with the lantern hanging from its tip
    L.path([(-1, 50), (-3, 52), (-6, 53), (-10, 53), (-12, 52)], 'lacq', [4, 2])
    L.r(-12, 49, -12, 50, 'lblk', 3)
    L.r(-14, 48, -10, 48, 'tgold', 3)
    for j, half in enumerate((2, 3, 3, 3, 3, 3, 3, 2)):
        h = 47 - j
        for dx in range(-half, half + 1):
            rel = (dx + half) / (2 * half)
            t = 5 if abs(dx) <= 1 and 2 <= j <= 5 else 4 if rel < 0.6 else 3 if rel < 0.85 else 2
            L.p(-12 + dx, h, 'paperR', t)
        if j in (1, 3, 5):
            L.p(-12 - half, h, 'paperR', 1)
    L.r(-14, 39, -10, 39, 'tgold', 3); L.p(-12, 38, 'tgold', 4)
    L.heads.append((-12, 43))
    L.finish()
    return L, 59, (-4, 4)


def toro():
    """a stone lantern (tōrō): stepped base, pillar, lit fire box, wide roof with upturned corners, flat top"""
    L = Lamp()
    L.r(-6, 0, 6, 2, 'stone', 2); L.r(-6, 2, 6, 2, 'stone', 3)
    L.r(-5, 3, 5, 4, 'stone', 3); L.r(-5, 4, 5, 4, 'stone', 4)
    L.pole(5, 16, 'stone', 5)
    L.r(-3, 10, 3, 10, 'stone', 4)
    L.r(-5, 17, 5, 18, 'stone', 3); L.r(-5, 18, 5, 18, 'stone', 4)
    L.r(-4, 19, 4, 26, 'stone', 3); L.r(-4, 19, -4, 26, 'stone', 4); L.r(4, 19, 4, 26, 'stone', 2)
    L.r(-2, 20, 2, 25, 'lampW', 3); L.r(-1, 21, 1, 24, 'lampW', 5); L.r(0, 20, 0, 25, 'stone', 2)
    L.p(-1, 22, 'lampW', 5); L.p(1, 23, 'lampW', 4)
    L.r(-7, 27, 7, 28, 'stone', 2); L.r(-7, 28, 7, 28, 'stone', 3)
    L.p(-8, 29, 'stone', 4); L.p(8, 29, 'stone', 3)
    L.r(-6, 29, 6, 30, 'stone', 3); L.r(-6, 30, 6, 30, 'stone', 4)
    L.r(-4, 31, 4, 32, 'stone', 4)
    L.r(-3, 33, 3, 34, 'stone', 3); L.r(-3, 34, 3, 34, 'stone', 5)
    for dx, h in ((-5, 3), (4, 4), (-6, 29), (5, 30), (-3, 17)):
        L.p(dx, h, 'green', 3)                                # moss
    L.heads.append((0, 23))
    L.finish()
    return L, 35, (-4, 4)


# --------------------------------------------------------------------------- light
def _field():
    return [[0.0] * CELL_W for _ in range(CELL_H)]


def _put(A, x, y, a):
    if 0 <= x < CELL_W and 0 <= y < CELL_H and a > A[y][x]:
        A[y][x] = a


def smoothstep(e0, e1, v):
    t = max(0.0, min(1.0, (v - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def cone(A, hx, hy, spread, power=0.45, top_w=2.0):
    """a downward cone from a luminaire: brightest under the head, fading towards the ground and the edges"""
    for y in range(hy + 1, YB + 2):
        t = (y - hy) / max(1, YB - hy)
        half = top_w + (spread - top_w) * t
        for x in range(CELL_W):
            u = abs(x - hx) / half
            if u < 1.2:
                _put(A, x, y, power * (1 - 0.55 * t) * (1 - smoothstep(0.55, 1.2, u)))


def radial(A, hx, hy, radius, power, up=1.0, side=1.0, down=1.0, roof=None):
    """light spreading in all directions from (hx, hy), weighted by direction:
    up / side / down are the strengths straight up, sideways and straight down.
    roof: the row of an eave; above it the light is cut to 15 %."""
    import math
    for y in range(CELL_H):
        for x in range(CELL_W):
            dx, dy = x - hx, y - hy
            d = math.hypot(dx, dy)
            if d > radius:
                continue
            c = dy / d if d else 0.0            # -1 up … 0 sideways … 1 down
            w = side + (down - side) * c if c >= 0 else side + (up - side) * -c
            fall = (1 - d / radius) ** 1.6
            a = power * w * fall
            if roof is not None and y < roof:
                a *= 0.15
            _put(A, x, y, a)


def pool(A, hx, half, power=0.4):
    for y in range(YB - 4, YB + 2):
        for x in range(CELL_W):
            e = ((x - hx) / half) ** 2 + ((y - YB) / 2.5) ** 2
            if e < 1:
                _put(A, x, y, power * (1 - e) ** 0.8)


def render_light(A, col, blur=1.3):
    """float alpha field → RGBA: a smooth gradient (no bands, no dither), edges softened with a
    Gaussian blur; the brightest parts tint towards white."""
    from PIL import ImageFilter
    a_im = Image.new('L', (CELL_W, CELL_H))
    a_im.putdata([max(0, min(255, round(v * 255))) for row in A for v in row])
    a_im = a_im.filter(ImageFilter.GaussianBlur(blur))
    im = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
    for y in range(CELL_H):
        for x in range(CELL_W):
            a = a_im.getpixel((x, y))
            if a:
                c = mix(col, (255, 255, 255), min(0.6, a / 255 * 0.9))
                im.putpixel((x, y), c + (a,))
    return im


def light_for(name, L):
    A = _field()
    if name in ('roadside', 'roadside2', 'subway'):
        for dx, h in L.heads:
            hx, hy = at(dx, h)
            cone(A, hx, hy, 15 if name != 'subway' else 13)
            radial(A, hx, hy, 6, 0.6, up=0.4, side=0.8, down=1.0)       # glow round the lens
            pool(A, hx, 19 if name != 'subway' else 17)
        return render_light(A, COOL)
    if name == 'round':
        # the globe shines all round, much stronger downwards
        (dx, h), = L.heads
        hx, hy = at(dx, h)
        radial(A, hx, hy, 34, 0.55, up=0.35, side=0.5, down=1.0)
        radial(A, hx, hy, 9, 0.7)
        cone(A, hx, hy, 20, power=0.42, top_w=5)
        pool(A, hx, 22, 0.42)
        return render_light(A, WARM, 1.6)
    if name == 'vintage':
        # light leaves through the yellow panes: sideways and down, the roof stops it going up
        (dx, h), = L.heads
        hx, hy = at(dx, h)
        roof = at(0, 38)[1]
        for ox in (-3, 3):
            radial(A, hx + ox, hy, 30, 0.5, up=0.5, side=0.9, down=1.0, roof=roof)
        radial(A, hx, hy, 7, 0.6, roof=roof)
        cone(A, hx, hy + 3, 16, power=0.32, top_w=5)
        pool(A, hx, 18, 0.4)
        return render_light(A, WARM, 1.4)
    if name == 'tokyo_lamp':
        # the paper lantern glows all round, strongest downwards
        (dx, h), = L.heads
        hx, hy = at(dx, h)
        radial(A, hx, hy, 30, 0.5, up=0.4, side=0.55, down=1.0)
        radial(A, hx, hy, 8, 0.7)
        cone(A, hx, hy, 18, power=0.36, top_w=5)
        pool(A, hx, 20, 0.4)
        return render_light(A, rgb('#ff8a5a'), 1.6)
    if name == 'toro':
        # firelight through the small window: sideways and down, the stone roof stops it going up
        (dx, h), = L.heads
        hx, hy = at(dx, h)
        radial(A, hx, hy, 18, 0.5, up=0.3, side=0.9, down=1.0, roof=at(0, 27)[1])
        pool(A, hx, 13, 0.32)
        return render_light(A, rgb('#ffb060'), 1.4)
    raise ValueError(name)


LAMPS = [
    ('roadside',  lambda: roadside(False), COOL, 15),
    ('roadside2', lambda: roadside(True),  COOL, 15),
    ('round',     round_lamp,              WARM, 13),
    ('vintage',   vintage,                 WARM, 11),
    ('subway',    subway,                  COOL, 13),
    ('tokyo_lamp', tokyo_lamp,             WARM, 13),
    ('toro',      toro,                    WARM, 11),
]

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
    sheet = Image.new('RGBA', (CELL_W, CELL_H * len(LAMPS)), (0, 0, 0, 0))
    glow = Image.new('RGBA', (CELL_W, CELL_H * len(LAMPS)), (0, 0, 0, 0))
    meta = {}
    for row, (name, fn, col, spread) in enumerate(LAMPS):
        L, top_h, span = fn()
        im = L.image()
        x0, y0, x1, y1 = im.getbbox()
        assert y1 == CELL_H and x0 > 0 and x1 < CELL_W, (name, im.getbbox())
        sheet.alpha_composite(im, (0, row * CELL_H))
        glow.alpha_composite(light_for(name, L), (0, row * CELL_H))
        meta[name] = {'row': row, 'frames': 1, 'fps': 1, 'w': x1 - x0, 'h': y1 - y0, 'top': top_h + 1,
                      'top_span': list(span), 'heads': [[dx, h] for dx, h in L.heads]}
    sheet.save(root / 'lamps.png')
    glow.save(root / 'lamps-light.png')
    (root / 'lamps.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote', root / 'lamps.png', '+ lamps-light.png', sheet.size)
    for n, *_ in LAMPS:
        m = meta[n]
        print(f"  {n:10s} {m['w']:3d} × {m['h']:2d}  top {m['top']}")
