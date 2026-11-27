"""Oslostil title logo, pixel art at 1 image px = 1 game px.

Writes assets/ui/title-logo-pixel.png (212 x 70) and title-logo-pixel-light.png (244 x 102: the
lamp light, 16 px padding on every side; draw it in front of the logo at (x - 16, y - 16)).

Approved composition (Joakim, 27 Nov 2026): a striped synthwave sun; MUNCH (tower only, upper part
leaning left) as the tallest block of a black skyline silhouette with single-colour lit windows (none
on Munch); two neon street lamps aimed so their light falls diagonally across the word; «Oslostil» in
chrome, Russo One-style letters rebuilt by hand on the grid and squashed (cap 24, x-height 18), sharp
blue-to-pink split, black behind the word and in the gaps between the letters (down to 1 px below the
baseline), no pink edge. Lamp light only falls down/out of the lens, never back onto the lamp.

Run from the repo root:  python3 tools/logo/title_logo.py
"""
import sys
import numpy as np
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else 'assets/ui'
W, H = 212, 70

SS = 8

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)

INK = hexc('#1a0533')     # outline / silhouette

HORIZON = 49

SKYAA = hexc('#3a0a5a')   # tone that edge AA leans to (game sky)

def sun_cov(r):
    n = 2 * r; yy, xx = np.mgrid[0:n * SS, 0:n * SS]
    c = (n * SS - 1) / 2
    m = ((xx - c) ** 2 + (yy - c) ** 2 <= (r * SS) ** 2).astype(np.float32)
    return m.reshape(n, SS, n, SS).mean((1, 3))

class Canvas:
    def __init__(s): s.a = np.zeros((H, W, 4), np.uint8)
    def put(s, x, y, rgba):
        if 0 <= x < W and 0 <= y < H: s.a[y, x] = rgba
    def img(s): return Image.fromarray(s.a, 'RGBA')

def mix(c1, c2, t):
    return (c1[:3] * (1 - t) + c2[:3] * t).round().astype(np.uint8).tolist() + [255]

SUN = [hexc(c) for c in ('#ffe96a', '#ffa04a', '#ff5a8a', '#ff2bb0', '#e0169c', '#a00c7a')]

def GAPROWS(r):
    """sun stripes from near the top: bands shrink, gaps grow downward"""
    rows, y = set(), int(r * 0.25)
    for b, g in ((4, 1), (3, 1), (3, 1), (3, 2), (2, 2), (2, 2), (2, 3), (1, 3), (1, 4)):
        y += b
        for k in range(g): rows.add(y + k)
        y += g
    return rows

def draw_sun(cv, cx, cy, r, gaps=True):
    cov = sun_cov(r); n = 2 * r
    for j in range(n):
        t = j / (n - 1); k = min(len(SUN) - 2, int(t * (len(SUN) - 1))); f = t * (len(SUN) - 1) - k
        col = mix(SUN[k], SUN[k + 1], f)
        # stepped stripes from near the top, gaps growing downward
        if gaps and j in GAPROWS(r): continue
        if cy - r + j > HORIZON: break
        for i in range(n):
            v = cov[j, i]
            if v >= 0.7: cv.put(cx - r + i, cy - r + j, col)
            elif v >= 0.25: cv.put(cx - r + i, cy - r + j, mix(np.array(col), SKYAA, 0.45))

CHROME = [('#eaffff', 0.0), ('#7ff3ff', 0.22), ('#2bb7ff', 0.45), ('#ff4aa8', 0.4501),
          ('#ff4aa8', 0.52), ('#ff2bd6', 0.68), ('#ff9a3c', 0.86), ('#ffe14a', 1.0)]

def grad(stops, t):
    for (c1, t1), (c2, t2) in zip(stops, stops[1:]):
        if t <= t2:
            f = 0 if t2 == t1 else (t - t1) / (t2 - t1)
            # step (no smooth blend) for the chrome horizon, blend elsewhere in 2 steps
            f = round(f * 3) / 3
            return mix(hexc(c1), hexc(c2), f)
    return hexc(stops[-1][0]).tolist()

def draw_text(cv, cov, x0, y0, stops, outline=INK, outline2=None, hi=True):
    h, w = cov.shape
    solid = cov >= 0.6; aa = (cov >= 0.22) & ~solid
    shape = solid | aa
    # outline = 1 px ring (4-neigh + diagonals) around shape
    pad = np.pad(shape, ((2, 4), (2, 2)))
    ring = np.zeros_like(pad)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ring |= np.roll(np.roll(pad, dy, 0), dx, 1)
    ring2 = np.zeros_like(pad)
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            if abs(dy) + abs(dx) <= 3: ring2 |= np.roll(np.roll(pad, dy, 0), dx, 1)
    # drop shadow 2 px down
    sh = np.roll(ring, 2, 0)
    for j in range(h + 6):
        for i in range(w + 4):
            X, Y = x0 + i - 2, y0 + j - 2
            if outline2 is not None and ring2[j, i] and not ring[j, i]: cv.put(X, Y, outline2.tolist())
            if sh[j, i] and not ring[j, i]: cv.put(X, Y, hexc('#0b0118').tolist())
            if ring[j, i]: cv.put(X, Y, outline.tolist())
    for j in range(h):
        col = np.array(grad(stops, j / (h - 1)), np.uint8)
        for i in range(w):
            if solid[j, i]:
                c = col
                if hi and j < h * 0.4 and (j == 0 or not shape[j - 1, i]): c = hexc('#ffffff')
                cv.put(x0 + i, y0 + j, c.tolist())
            elif aa[j, i]:
                cv.put(x0 + i, y0 + j, mix(col, outline, 0.5))

MUNCH_INK = hexc('#0b0114'); BLD = hexc('#2a0b4a'); BLD_EDGE = hexc('#4a1670')

MUNCH_INK = hexc('#0b0114'); BLD = hexc('#2a0b4a'); BLD_EDGE = hexc('#4a1670')

MUNCH_INK = hexc('#0b0114'); BLD = hexc('#2a0b4a'); BLD_EDGE = hexc('#4a1670')

def munch_tower(cv, x0, top, base, width=16, lean_h=13, lean_dx=4):
    """MUNCH tower only (no low wing): vertical lower part, upper part leaning left.
    Drawn as an explicit pixel staircase so the left and right lean edges step identically."""
    ink = MUNCH_INK.tolist()
    for y in range(top, base):
        sh = -int(np.ceil((top + lean_h - y) * lean_dx / lean_h - 0.5)) if y < top + lean_h else 0
        for x in range(x0 + sh, x0 + width + sh): cv.put(x, y, ink)

WIN = hexc('#ffe14a')

def building(cv, x, w, top, base, roof=None, windows=None):
    """black silhouette block, no outline; optional single-colour lit window dots"""
    ink = MUNCH_INK.tolist()
    for y in range(top, base):
        for i in range(w): cv.put(x + i, y, ink)
    if roof == 'antenna':
        for y in range(top - 5, top): cv.put(x + w // 2, y, ink)
    if roof == 'step':
        for y in range(top - 3, top):
            for i in range(2, w - 2): cv.put(x + i, y, ink)
    if windows is not None and w >= 4:
        for y in range(top + 2, base - 1, 3):
            for i in range(1, w - 1, 2):
                if windows.random() < 0.4: cv.put(x + i, y, WIN.tolist())

PAD = 16

def light_layer(heads, bottom=67, col=(255, 228, 150), block=None):
    """smooth light, no dither, padded 16 px: hot core at each lens and a beam along the head's
    tilt, reaching almost to the bottom of the letters. heads = [(x, y, ux, uy)]"""
    w, h = W + 2 * PAD, H + 2 * PAD
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.zeros((h, w), np.float32)
    for hx, hy, ux, uy in heads:
        X, Y = hx + PAD, hy + PAD
        L = (bottom - hy) / uy
        along = (xx - X) * ux + (yy - Y) * uy
        # light only goes down/out of the lens: nothing on the lamp itself or above it
        # starts right at the lens; the lamp's own housing/arm/pole pixels are cut out in final_logo
        t = np.clip((along + 2.5) / 2.0, 0, 1); down = t * t * (3 - 2 * t)
        a += 0.8 * np.exp(-(np.hypot(xx - X + 1.5 * ux, yy - Y + 1.5 * uy) / 4.0) ** 2) * down
        perp = np.abs(-(xx - X) * uy + (yy - Y) * ux)
        half = 2.0 + 0.30 * np.clip(along, 0, None)
        fade = np.clip((L - along) / (0.25 * L), 0, 1) ** 1.5         # full strength, then out by the bottom
        a += 0.40 * np.exp(-(perp / half) ** 2) * fade * down
    a = np.clip(a, 0, 0.85)
    if block is not None: a[PAD:PAD + H, PAD:PAD + W][block] = 0     # never light the lamp itself
    rgb = np.zeros((h, w, 3), np.float32); rgb[...] = col
    return Image.fromarray(np.dstack([rgb, a * 255]).round().astype(np.uint8), 'RGBA')

def text_backfill(cv, cov, x0, y0, open_bottom):
    """black behind the word: counters, plus the gaps between letters from x-height down to
    `open_bottom` px above the baseline (negative = below it, into the outline rows)"""
    shape = cov >= 0.22; h, w = shape.shape
    ink = MUNCH_INK.tolist()
    # counters = background not reachable from the border (flood fill, no scipy needed)
    outside = np.zeros((h + 2, w + 2), bool); pad = np.pad(shape, 1)
    stack = [(0, 0)]; outside[0, 0] = True
    while stack:
        y, x = stack.pop()
        for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= yy < h + 2 and 0 <= xx < w + 2 and not outside[yy, xx] and not pad[yy, xx]:
                outside[yy, xx] = True; stack.append((yy, xx))
    holes = ~outside[1:-1, 1:-1] & ~shape
    cnt = shape.sum(1); xh = int(np.argmax(cnt >= 0.6 * cnt.max()))
    for j in range(xh, h - open_bottom):
        xs = np.nonzero(shape[min(j, h - 1)])[0]
        if len(xs):
            for i in range(xs[0], xs[-1] + 1): cv.put(x0 + i, y0 + j, ink)
    for j, i in zip(*np.nonzero(holes)): cv.put(x0 + i, y0 + j, ink)

CAP, XH, BASE = 0, 6, 24            # squashed (was 0, 7, 27): rows cap top, x-height top, baseline (excl.)
CORNERS = {   # top-left orientation; '#' keep, '+' AA tone, '.' cut
    4: ['..+#', '.+##', '+###', '####'],
    3: ['.+#', '+##', '###'],
    2: ['.+', '+#'],
    1: ['+'],
}

def glyph(w, rects, corners=(), holes=(), hole_corners=()):
    """rects: (x, y, w, h) solid. corners: (x, y, quadrant, r) outer corner at the rect corner pixel
    (x, y), quadrant in 'tl tr bl br'. holes: counters cut out; hole_corners: (x, y) AA tone pixels."""
    g = np.zeros((BASE, w), np.float32)
    for x, y, rw, rh in rects: g[y:y + rh, x:x + rw] = 1
    for x, y, rw, rh in holes: g[y:y + rh, x:x + rw] = 0
    for x, y, q, r in corners:
        t = CORNERS[r]
        for j in range(r):
            for i in range(r):
                ch = t[j][i]
                X = x + i if q[1] == 'l' else x - i
                Y = y + j if q[0] == 't' else y - j
                g[Y, X] = 0 if ch == '.' else 0.4 if ch == '+' else g[Y, X]
    for x, y in hole_corners: g[y, x] = 0.4
    return g

def corners4(x0, y0, x1, y1, r, which='tl tr bl br'):
    m = {'tl': (x0, y0), 'tr': (x1, y0), 'bl': (x0, y1), 'br': (x1, y1)}
    return [(m[q][0], m[q][1], q, r) for q in which.split()]

# Glyphs squashed bottom-up (Joakim, 27 Nov): cap height 24, x-height 18, horizontal bars 4,
# vertical stems 7.
def G_O():
    return glyph(25, [(0, CAP, 25, 24)], corners4(0, 0, 24, 23, 4),
                 holes=[(7, 4, 11, 16)], hole_corners=[(7, 4), (17, 4), (7, 19), (17, 19)])

def G_o():
    return glyph(21, [(0, XH, 21, 18)], corners4(0, XH, 20, 23, 4),
                 holes=[(7, 10, 7, 10)], hole_corners=[(7, 10), (13, 10), (7, 19), (13, 19)])

def G_s():
    # top bar 4, left stem 3, middle bar 4, right stem 3, bottom bar 4; flat terminals
    r = [(0, 6, 20, 4), (0, 10, 7, 3), (0, 13, 20, 4), (13, 17, 7, 3), (0, 20, 20, 4)]
    c = [(0, 6, 'tl', 4), (19, 6, 'tr', 1), (19, 9, 'br', 1), (19, 13, 'tr', 3), (0, 16, 'bl', 3),
         (0, 20, 'tl', 1), (0, 23, 'bl', 1), (19, 23, 'br', 4)]
    g = glyph(20, r, c)
    for x, y in ((7, 10), (12, 19)): g[y, x] = 0.4     # inner joints
    return g

def G_l():
    g = glyph(10, [(0, CAP, 7, 20), (0, 20, 10, 4)],
              [(0, 0, 'tl', 1), (6, 0, 'tr', 1), (0, 23, 'bl', 3), (9, 20, 'tr', 1), (9, 23, 'br', 1)])
    g[19, 7] = 0.4
    return g

def G_t():
    g = glyph(14, [(1, 2, 7, 18), (0, 6, 14, 4), (1, 20, 13, 4)],
              [(1, 2, 'tl', 1), (7, 2, 'tr', 1), (0, 6, 'tl', 1), (0, 9, 'bl', 1), (13, 6, 'tr', 1),
               (13, 9, 'br', 1), (1, 23, 'bl', 3), (13, 20, 'tr', 1), (13, 23, 'br', 1)])
    g[19, 8] = 0.4; g[10, 8] = 0.4
    return g

def G_i():
    return glyph(7, [(0, 0, 7, 4), (0, 6, 7, 18)],
                 corners4(0, 0, 6, 3, 1) + [(0, 6, 'tl', 1), (6, 6, 'tr', 1), (0, 23, 'bl', 1), (6, 23, 'br', 1)])

def word_cov(gap=4):
    gs = [G_O(), G_s(), G_l(), G_o(), G_s(), G_t(), G_i(), G_l()]
    w = sum(g.shape[1] for g in gs) + gap * (len(gs) - 1)
    out = np.zeros((BASE, w), np.float32); x = 0
    for g in gs: out[:, x:x + g.shape[1]] = g; x += g.shape[1] + gap
    return out

LAMP = {'C': '#2bf0ff', 'D': '#1a8fb0', 'P': '#ff4aa8', 'Q': '#b0187a', 'Y': '#fff27a', 'O': '#ffb34a'}

def pixel_lamp(cv, heads, px, base, top, face, arm=4, head=8, pal=LAMP):
    """Street lamp on exact 2:1 steps: pole, then arm and head on one line rising toward the centre
    (≈27°); housing on top, lens below; the beam leaves the lens perpendicular to it (≈63° down)."""
    def put(x, y, k): cv.put(px + face * x, y, hexc(pal[k]).tolist())
    for y in range(top + 2, base):
        put(0, y, 'C'); put(1, y, 'D')
    for y in range(base - 2, base):
        for x in (-1, 0, 1, 2): put(x, y, 'D')
    put(1, top + 1, 'C')                                # rounded bend: vertical -> 1:1 steps -> 2:1 arm
    for k in range(arm):
        x, y = 2 + k, top - (k + 1) // 2
        put(x, y, 'C'); put(x, y + 1, 'D')
    for k in range(arm, arm + head):
        x, y = 2 + k, top - (k + 1) // 2
        end = k in (arm, arm + head - 1)
        put(x, y - 1, 'Q' if end else 'P'); put(x, y, 'P')
        put(x, y + 1, 'O' if end else 'Y')
    k = arm + head // 2; x, y = 2 + k, top - (k + 1) // 2 + 1
    b = np.hypot(1, 2)
    heads.append((px + face * x + 0.5, y + 0.5, face / b, 2 / b))

LAMP_PINK = dict(LAMP, Y='#ffd6f0', O='#ff9ad0')
LIGHT_WARM, LIGHT_PINK = (255, 228, 150), (255, 110, 210)

def final_logo(pink=False):
    """approved composition (study B8): Munch tallest in a lit black skyline in front of the
    striped sun, two neon lamps lighting the word diagonally, Russo One-style chrome lettering
    with black behind the word, no pink edge."""
    cv = Canvas(); cx = 106; heads = []
    draw_sun(cv, cx, 31, 26)
    B = 49; rng = np.random.default_rng(7)
    for x, w, t in [(58, 7, 39), (64, 9, 37), (72, 20, 37), (91, 30, 36), (120, 24, 37), (143, 9, 37), (151, 6, 39)]:
        building(cv, x, w, t, B, None, rng)
    for x, w, t, roof in [(72, 5, 33, None), (78, 6, 30, 'antenna'), (86, 4, 32, None),
                          (91, 6, 27, 'step'), (99, 4, 31, None),
                          (117, 5, 29, None), (123, 6, 32, 'antenna'), (131, 4, 27, 'step'),
                          (137, 6, 33, None)]:
        building(cv, x, w, t, B, roof, rng)
    munch_tower(cv, cx, 17, B, width=14, lean_h=12, lean_dx=4)
    pal = LAMP_PINK if pink else LAMP
    lamps = Canvas()
    pixel_lamp(lamps, heads, 42, 52, 23, +1, pal=pal)
    pixel_lamp(lamps, heads, 169, 52, 23, -1, pal=pal)
    lens = np.isin(lamps.a[..., :3].astype(np.int32) @ np.array([65536, 256, 1]),
                   [int(pal[k][1:], 16) for k in 'YO'])
    block = (lamps.a[..., 3] > 0) & ~lens
    on = lamps.a[..., 3] > 0; cv.a[on] = lamps.a[on]
    t = word_cov()
    x0, y0 = cx - t.shape[1] // 2, 40                  # top kept where it was; squashed from below
    text_backfill(cv, t, x0, y0, -1)                   # black runs 1 px below the baseline
    draw_text(cv, t, x0, y0, CHROME)
    return cv.img(), light_layer(heads, bottom=y0 + BASE - 2, col=LIGHT_PINK if pink else LIGHT_WARM, block=block)


if __name__ == '__main__':
    im, li = final_logo()          # warm light approved; final_logo(pink=True) gives the pink-light variant
    im.save(f'{OUT}/title-logo-pixel.png'); li.save(f'{OUT}/title-logo-pixel-light.png')
