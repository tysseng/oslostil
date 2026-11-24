"""Classic Oslo (level 4) and station props, drawn into the props sheet by tools/sprites/props.py.
Same style and scale as the other props: front view, girl scale, tinted outlines, hand-AA'd corners.

  bench_park     park bench: dark green cast-iron ends, wooden slats, backrest ......... 17 px (one jump)
  bench_station  Sandvika station bench: steel frame, light wood slats, armrests ....... 15 px (one jump)
  fountain       tiered stone fountain, darker at night, pulsing water with an arch to each side (8 frames)
                 lit from the water upwards (props-light.png) ......................... 42 px; the basin
                 rim (13 px) is the standable top

  ad_column      advertising column with posters lit by two small lamps ................... 48 px
  railing        low cast-iron park railing on a stone kerb (not standable) ............... 16 px
  statue         equestrian bronze statue on a granite plinth (stand on the plinth, 26) ... 60 px
  planter        stone planter with dim night flowers .................................... 17 px
  bikes          a hoop bike rack with two parked bikes (not standable) .................. 20 px
All of these are coloured for the night street of level 4 (dark, low contrast; only the column's lamps glow).

Each entry: (name, frames function, fps, top or None = visible height, light function or None).
A frame may carry `post(im)`: drawn after the outline (semi-transparent water).
"""
import math
from pathlib import Path
from PIL import Image
from props import Canvas, RAMP, rgb, mix

R = lambda *c: [rgb(x) for x in c]
RAMP.update({
    'iron':   R('#06100c', '#0e1e16', '#183024', '#224432', '#305c44', '#4a7a5e'),
    'slat':   R('#1e1008', '#3e2412', '#5e381c', '#7e4e2a', '#a06a3c', '#c89060'),
    'slatL':  R('#3a2a14', '#7a5a30', '#a8844c', '#c8a468', '#e0c084', '#f4dcaa'),
    'steelB': R('#14181e', '#2c323c', '#4a525e', '#6c7684', '#96a0ae', '#c4ccd6'),
    'stoneW': R('#1c1a18', '#3c3a36', '#5c5852', '#7c7870', '#9e9a90', '#c4c0b4'),
    'stoneF': R('#121416', '#24272c', '#363a40', '#4a4e55', '#60646c', '#80848c'),   # fountain stone, at night
    'water':  R('#0a2a3a', '#1a5a78', '#3a8ab0', '#6ab8dc', '#a8dcf4', '#ffffff'),
})


def finish(cv):
    cv.outline()
    cv.soften()
    return cv


# --------------------------------------------------------------------------- park bench
def bench_park():
    W, H = 38, 19
    cv = Canvas(W, H)
    # backrest: three slats
    for y in (1, 4, 7):
        cv.rect(4, y, 33, y + 1, 'slat', 3)
        cv.hline(4, 33, y, 'slat', 4)
        for x in range(7, 33, 7):
            cv.set(x, y + 1, 'slat', 2)                     # plank joints
    # seat: two slats seen a little from above
    cv.rect(2, 10, 35, 11, 'slat', 4); cv.hline(2, 35, 10, 'slat', 5)
    cv.rect(2, 12, 35, 12, 'slat', 2)
    # cast-iron ends with a scroll armrest and curved feet
    for x0, s in ((3, 1), (34, -1)):
        cv.vline(x0, 1, 16, 'iron', 3); cv.vline(x0 + s, 9, 16, 'iron', 2)
        cv.set(x0 - s, 8, 'iron', 4); cv.set(x0 - s, 9, 'iron', 3)   # armrest scroll
        cv.set(x0 - s * 2, 9, 'iron', 4)
        cv.set(x0 - s, 16, 'iron', 3); cv.set(x0 + s * 2, 16, 'iron', 3)   # feet
        cv.set(x0, 0, 'iron', 4)
    cv.rect(4, 13, 33, 13, 'iron', 1)                       # shadow under the seat
    return [finish(cv)]


# --------------------------------------------------------------------------- station bench
def bench_station():
    W, H = 44, 17
    cv = Canvas(W, H)
    cv.rect(4, 1, 39, 6, 'slatL', 3)                        # backrest panel of light wood slats
    for y in (1, 3, 5):
        cv.hline(4, 39, y, 'slatL', 4)
    for x in (4, 39):
        cv.vline(x, 1, 6, 'steelB', 3)
    cv.rect(2, 8, 41, 9, 'slatL', 4); cv.hline(2, 41, 8, 'slatL', 5)   # seat
    cv.hline(2, 41, 10, 'steelB', 2)                        # steel rail under the seat
    for x in (3, 21, 40):                                   # three steel legs with armrests at the ends
        cv.rect(x - 1, 7, x, 15, 'steelB', 3); cv.vline(x - 1, 7, 15, 'steelB', 4)
        cv.hline(x - 2, x + 1, 15, 'steelB', 2)
    for x in (3, 40):
        cv.rect(x - 1, 6, x, 6, 'steelB', 5)
    cv.hline(5, 38, 7, 'steelB', 1)                         # gap between back and seat
    return [finish(cv)]


# --------------------------------------------------------------------------- fountain
def fountain():
    frames = []
    W, H = 66, 42
    for f in range(FRAMES):
        cv = Canvas(W, H)
        # big round basin: stone rim, front wall with panels
        cv.rect(2, 28, 63, 29, 'stoneF', 4); cv.hline(3, 62, 28, 'stoneF', 5)
        cv.rect(3, 30, 62, 39, 'stoneF', 3)
        cv.vline(3, 30, 39, 'stoneF', 4); cv.vline(62, 30, 39, 'stoneF', 2)
        for x in range(8, 54, 12):                          # panels
            cv.rect(x, 32, x + 7, 37, 'stoneF', 2); cv.hline(x, x + 7, 32, 'stoneF', 1)
            cv.hline(x, x + 7, 37, 'stoneF', 4)
        cv.rect(2, 40, 63, 40, 'stoneF', 2)
        # pedestal
        cv.rect(29, 14, 36, 27, 'stoneF', 3); cv.vline(29, 14, 27, 'stoneF', 4); cv.vline(36, 14, 27, 'stoneF', 2)
        cv.rect(28, 20, 37, 21, 'stoneF', 4)
        # upper bowl
        cv.rect(19, 11, 46, 12, 'stoneF', 4); cv.hline(20, 45, 11, 'stoneF', 5)
        for y, (a, b) in zip((13, 14, 15), ((21, 44), (24, 41), (27, 38))):
            cv.hline(a, b, y, 'stoneF', 3); cv.set(b, y, 'stoneF', 2)
        # finial
        cv.rect(31, 6, 34, 10, 'stoneF', 3); cv.vline(31, 6, 10, 'stoneF', 4)
        cv.rect(32, 4, 33, 5, 'stoneF', 4)
        # make headroom for the jet and the arches: move everything down by TOP rows
        cv.h += TOP
        cv.px = [[None] * W for _ in range(TOP)] + cv.px
        cv.mat = [[None] * W for _ in range(TOP)] + cv.mat
        finish(cv)
        cv.post = (lambda im, f=f: water(im, f))
        frames.append(cv)
    return frames


FRAMES, TOP = 8, 10      # fountain animation frames; headroom above the finial


def fountain_light(w, h):
    """light rising from the water: a glow over the basin surface that climbs the column and lights the
    jets and the falling water, fading upwards"""
    import tokyo_props as tp
    A = tp.field(w, h)
    for y in range(h):
        for x in range(w):
            dy = 27 + TOP - y                                     # height above the water surface
            if dy < -2:
                continue
            spread = 28 - max(0, dy) * 0.35                 # narrows a little going up
            u = abs(x - 32) / max(4, spread)
            if u >= 1:
                continue
            a = 0.42 * (1 - u ** 1.6) * max(0.0, 1 - max(0, dy) / (27 + TOP)) ** 1.3
            tp.put(A, x, y, a)
    tp.radial(A, 32, 12 + TOP, 11, 0.32)                            # the upper bowl and the jet catch the light
    return A, rgb('#bfe6ff')


def water(im, f):
    """semi-transparent water whose pressure pulses over the FRAMES-frame loop: the centre jet rises and
    falls, two arches leap out from the top to each side and land in the basin (reaching further when
    the pressure is high), beads of water run along the arches, curtains fall from the bowl and the
    basin surface ripples and splashes where the arches land"""
    import math
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    wc = RAMP['water']
    T = TOP

    def px(x, y, tone, a):
        x, y = round(x), round(y)
        if 0 <= x < im.width and 0 <= y < im.height:
            old = lay.getpixel((x, y))
            if a > old[3]:
                lay.putpixel((x, y), wc[tone] + (a,))

    p = 0.5 + 0.5 * math.sin(2 * math.pi * f / FRAMES)       # pressure 0…1
    cx, top = 32.5, 4 + T                                    # the finial's tip
    # centre jet: its height pulses
    jh = 3 + round(7 * p)
    for i in range(jh):
        px(cx - 0.5, top - 1 - i, 5 if i > jh - 3 else 4, 230)
        px(cx + 0.5, top - 1 - i, 4, 200)
    px(cx - 1.5, top - jh, 5, 170); px(cx + 1.5, top - jh, 5, 170)   # the crown of the jet
    # two arches to the sides, landing in the basin
    land = 27 + T
    reach = 17 + 8 * p
    rise = 3 + 5 * p
    for s_ in (-1, 1):
        n = 60
        for i in range(n + 1):
            t = i / n
            x = cx + s_ * reach * t
            y = (top - jh * 0.5) + (land - top + jh * 0.5) * t * t - rise * 4 * t * (1 - t)
            bead = ((t * 8 - f) % 2) < 0.7                   # beads running outwards with the frames
            px(x, y, 5 if bead else 4, 225 if bead else 175)
            if 0.15 < t < 0.9 and i % 2 == 0:
                px(x, y + 1, 3, 120)                         # a thin second line: a sheet of water
        # splash where the arch lands
        lx = cx + s_ * reach
        for k in range(3):
            px(lx + s_ * (k - 1), land - 1 - ((k + f) % 3), 5, 200)
        px(lx - s_, land - 2 - (f % 2), 4, 170)
    # curtains falling from the upper bowl, thicker when the pressure is high
    for s_, x0 in ((-1, 19), (1, 46)):
        for i in range(17):
            x = x0 + s_ * (0.5 + 0.3 * p) * i ** 0.85
            y = 12 + T + i
            px(x, y, 5 if (i + f) % 4 == 0 else 4, 200)
            if p > 0.4 and (i + f) % 2 == 0:
                px(x + s_, y, 3, 130)
    for x in range(20, 46):                                  # thin sheet over the bowl rim
        px(x, 13 + T + (1 if (x + f) % 5 == 0 else 0), 4, 140)
    # the basin surface: ripples travelling out
    for x in range(5, 61):
        ph = (abs(x - cx) - f * 1.5) % 8
        px(x, 27 + T, 5 if ph < 1 else 4 if ph < 3 else 3, 210)
        if ph < 1:
            px(x, 26 + T, 4, 150)
    im.alpha_composite(lay)


# ---------------------------------------------------------------- night street furniture (level 4 is dark)
RAMP.update({
    'stoneN':  R('#0a0b0e', '#16181c', '#22252b', '#30343b', '#40454e', '#565c68'),
    'gbronze': R('#0c0604', '#24160a', '#40280e', '#664218', '#946628', '#c4964a'),   # gilded bronze, at night
    'bronze':  R('#040e0c', '#0a1e1a', '#12302a', '#1c443c', '#285a50', '#3e786a'),
    'ironN':   R('#040806', '#0a120e', '#121c16', '#1a2820', '#24362c', '#34483c'),
    'colN':    R('#0a1010', '#142020', '#1c2e2e', '#263c3c', '#324c4c', '#466464'),
    'leafD':   R('#040a06', '#08140c', '#0e2014', '#142c1c', '#1c3a26', '#2a4e34'),
    'bikeR':   R('#2a0610', '#6a1020', '#a01c30', '#d0304a', '#f05a6a', '#ff9aa4'),
    'bikeB':   R('#06102a', '#123070', '#1c48a8', '#2a66d8', '#4a8af0', '#8ab8ff'),
    'tyre':    R('#06060a', '#121218', '#1e1e26', '#2c2c36', '#3c3c48', '#56566a'),
})
POSTER = [rgb(c) for c in ('#e04a5a', '#f0c048', '#4ab0d0', '#e8e0c8', '#8a5ad0', '#58b070')]


def ad_column():
    """an advertising column (plakatsøyle): dark green cast iron, a domed cap, posters lit by two small
    lamps on arms just above them"""
    W, H = 48, 48          # wide canvas: the column is 18 px, the rest is room for the lamps' glow
    cv = Canvas(W, H)
    cx = 24
    # domed cap with a finial
    cv.set(cx, 1, 'colN', 4); cv.rect(cx - 1, 2, cx, 2, 'colN', 4)
    for y, half in ((3, 3), (4, 5), (5, 7), (6, 8)):
        cv.hline(cx - half, cx + half - 1, y, 'colN', 3)
        cv.set(cx - half, y, 'colN', 4); cv.set(cx + half - 1, y, 'colN', 2)
    cv.hline(cx - 9, cx + 8, 7, 'colN', 4); cv.hline(cx - 9, cx + 8, 8, 'colN', 1)
    # lamp arms with small lamps over the posters
    for lx, s in ((cx - 9, -1), (cx + 8, 1)):
        cv.set(lx + s, 9, 'colN', 3); cv.set(lx + s * 2, 9, 'colN', 3)
        cv.rect(min(lx + s * 2, lx + s * 3), 10, max(lx + s * 2, lx + s * 3), 10, 'colN', 2)
        cv.set(lx + s * 2, 11, 'warm', 5); cv.set(lx + s * 3, 11, 'warm', 4)
    # the drum: a cylinder, posters on most of it
    x0, x1 = cx - 7, cx + 6
    cv.rect(x0, 9, x1, 40, 'colN', 3)
    rnd = __import__('random').Random(12)
    y = 11
    for ph in (9, 8, 9):                                     # three poster bands, lit warm at the top
        x = x0 + 1
        while x <= x1 - 1:
            w = min(rnd.choice((4, 5, 6)), x1 - x)
            col = POSTER[rnd.randrange(len(POSTER))]
            for yy in range(y, y + ph - 1):
                fade = (yy - 11) / 28                        # the lamps light the top best
                for xx in range(x, x + w):
                    rel = (xx - x0) / (x1 - x0)
                    shade = 0.02 + 0.42 * fade + (0.25 if rel > 0.75 else 0.08 if rel < 0.12 else 0)
                    c = mix(col, (14, 18, 26), min(0.8, shade))
                    cv.c(xx, yy, c, 'colN')
            for k in range(2):                               # «headlines» as dark dots
                cv.c(x + 1 + k, y + 1, mix(col, (10, 10, 14), 0.75), 'colN')
            x += w
        y += ph
    cv.vline(x0, 9, 40, 'colN', 4); cv.vline(x1, 9, 40, 'colN', 2)
    # base: a stepped plinth
    cv.rect(x0 - 1, 41, x1 + 1, 43, 'colN', 2); cv.hline(x0 - 1, x1 + 1, 41, 'colN', 4)
    cv.rect(x0 - 2, 44, x1 + 2, 46, 'stoneN', 3); cv.hline(x0 - 2, x1 + 2, 44, 'stoneN', 4)
    return [finish(cv)]


def ad_column_light(w, h):
    import tokyo_props as tp
    A = tp.field(w, h)
    for lx in (14, 34):
        tp.radial(A, lx, 11, 12, 0.5, down=1.3)
    for lx in (19, 29):                                      # wash of light down the posters
        tp.cone(A, lx, 11, 32, 8, 0.32)
    return A, rgb('#ffd08a')


def railing():
    """low cast-iron park railing: bars with spear tips between posts, on a stone kerb (not standable)"""
    W, H = 62, 16
    cv = Canvas(W, H)
    cv.rect(1, 12, 60, 14, 'stoneN', 3); cv.hline(1, 60, 12, 'stoneN', 4)
    cv.hline(2, 59, 3, 'ironN', 3); cv.hline(2, 59, 9, 'ironN', 3)
    for x in range(3, 59, 3):
        cv.vline(x, 2, 11, 'ironN', 4)
        cv.set(x, 1, 'ironN', 5)                             # spear tip
    for x in (1, 30, 60):                                    # posts with ball tops
        cv.rect(x - 1, 2, x, 11, 'ironN', 2); cv.vline(x - 1, 2, 11, 'ironN', 4)
        cv.rect(x - 1, 0, x, 1, 'ironN', 5)
    return [finish(cv)]


def tiger_from_photo(height):
    """Trace the walking tiger statue in tools/sprites/ref/tiger.png (Joakim's photo, 600 × 600, the tiger
    facing right in a garden). The bronze is found by colour (brown/gold or very dark, never green or
    pale grey), closed and opened to join the carved stripes into one body, the largest piece kept and
    its holes filled; a few patches of brownish grass that touch it are cut away. It is mirrored to face
    left, put on the pixel grid by majority coverage, and shaded with five bronze tones from the photo's
    own light, so the carved stripes show."""
    from collections import deque
    from PIL import ImageFilter
    src = Image.open(Path(__file__).resolve().parent / 'ref' / 'tiger.png').convert('RGB')
    W0, H0 = src.size
    mk = Image.new('L', (W0, H0), 0)
    for y in range(H0):
        for x in range(W0):
            r, g, b = src.getpixel((x, y)); mx, mn = max(r, g, b), min(r, g, b)
            sat = (mx - mn) / mx if mx else 0
            lum = 0.3 * r + 0.59 * g + 0.11 * b
            if (r >= g and r > b * 1.05 and not (sat < 0.18 and lum > 110)) or (lum < 45 and r >= g * 0.95):
                mk.putpixel((x, y), 255)
    mk = mk.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    mk = mk.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    for (ax, ay, bx, by) in ((0, 270, 78, 398), (0, 0, 600, 205), (300, 0, 600, 212)):   # grass that leaked in
        mk.paste(0, (ax, ay, bx, by))
    m = [[mk.getpixel((x, y)) > 0 for x in range(W0)] for y in range(H0)]
    lab = [[0] * W0 for _ in range(H0)]; best, cid = (0, 0), 0
    for y in range(H0):
        for x in range(W0):
            if m[y][x] and not lab[y][x]:
                cid += 1; q = deque([(x, y)]); lab[y][x] = cid; n = 0
                while q:
                    cx, cy = q.popleft(); n += 1
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < W0 and 0 <= ny < H0 and m[ny][nx] and not lab[ny][nx]:
                            lab[ny][nx] = cid; q.append((nx, ny))
                if n > best[0]:
                    best = (n, cid)
    out = [[True] * W0 for _ in range(H0)]                  # True = outside
    q = deque([(0, 0)]); seen = {(0, 0)}
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W0 and 0 <= ny < H0 and (nx, ny) not in seen and lab[ny][nx] != best[1]:
                seen.add((nx, ny)); q.append((nx, ny))
    inside = lambda x, y: (x, y) not in seen
    pts = [(x, y) for y in range(H0) for x in range(W0) if inside(x, y)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts) + 1
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts) + 1
    k = (y1 - y0) / height
    w = round((x1 - x0) / k)
    shade = src.filter(ImageFilter.GaussianBlur(k * 0.45))
    cells = []
    for gy in range(height):
        row = []
        for gx in range(w):
            ax, bx = int(x0 + gx * k), int(x0 + (gx + 1) * k)
            ay, by = int(y0 + gy * k), int(y0 + (gy + 1) * k)
            n = ins = 0; lum = 0.0
            for yy in range(ay, max(ay + 1, by)):
                for xx in range(ax, max(ax + 1, bx)):
                    if xx < W0 and yy < H0:
                        n += 1
                        if inside(xx, yy):
                            ins += 1
                            r, g, b = shade.getpixel((xx, yy)); lum += 0.3 * r + 0.59 * g + 0.11 * b
            row.append(lum / ins if n and ins * 2 >= n else None)
        cells.append(row[::-1])                            # mirror: face left
    vals = sorted(v for row in cells for v in row if v is not None)
    cut = [vals[int(len(vals) * f)] for f in (0.2, 0.45, 0.72, 0.92)]
    return [[None if v is None else 1 + sum(v >= c for c in cut) for v in row] for row in cells]


def statue():
    """a bronze tiger statue (walking, facing left), traced from a reference photo
    (tools/sprites/ref/tiger.png), on a wide granite plinth with a dotted plaque. In profile."""
    tones = tiger_from_photo(27)
    tw, th = len(tones[0]), len(tones)
    W = tw + 16
    H = th + 22
    cv = Canvas(W, H)
    L, Rr = 2, W - 3                                         # plinth spans the whole width
    base = H - 2
    cv.rect(L, base - 2, Rr, base, 'stoneN', 3); cv.hline(L, Rr, base - 2, 'stoneN', 4)
    cv.rect(L + 3, base - 12, Rr - 3, base - 3, 'stoneN', 3)
    cv.vline(L + 3, base - 12, base - 3, 'stoneN', 4); cv.vline(Rr - 3, base - 12, base - 3, 'stoneN', 2)
    cv.rect(L + 1, base - 15, Rr - 1, base - 13, 'stoneN', 4); cv.hline(L + 1, Rr - 1, base - 15, 'stoneN', 5)
    pc = (L + Rr) // 2
    cv.rect(pc - 9, base - 10, pc + 9, base - 5, 'gbronze', 2); cv.hline(pc - 9, pc + 9, base - 10, 'gbronze', 4)
    for y in (base - 8, base - 6):
        for x in range(pc - 7, pc + 8, 2):
            cv.set(x, y, 'gbronze', 4)
    top = base - 16                                          # the tiger stands on the plinth's cornice
    ox, oy = (W - tw) // 2, top - th + 1
    for y, row in enumerate(tones):
        for x, t in enumerate(row):
            if t is not None:
                cv.set(ox + x, oy + y, 'gbronze', t)
    return [finish(cv)]


def planter():
    """a stone planter with night-dark flowers and leaves"""
    W, H = 28, 17
    cv = Canvas(W, H)
    cv.rect(2, 8, 25, 14, 'stoneN', 3); cv.hline(1, 26, 8, 'stoneN', 4); cv.hline(1, 26, 9, 'stoneN', 2)
    cv.vline(2, 10, 14, 'stoneN', 4); cv.vline(25, 10, 14, 'stoneN', 2)
    cv.hline(4, 23, 12, 'stoneN', 2)
    rnd = __import__('random').Random(8)
    for x in range(3, 25):                                   # leaves
        top = 4 + rnd.randrange(3)
        for y in range(top, 8):
            cv.set(x, y, 'green', rnd.choice((2, 3, 3, 4)))
    flowers = [rgb('#e04868'), rgb('#a060e0'), rgb('#f0c850'), rgb('#ff7a9a'), rgb('#f4f0e0')]
    for x in range(4, 24, 3):                                # flower heads, dim in the dark
        y = 2 + rnd.randrange(3)
        c = flowers[rnd.randrange(len(flowers))]
        cv.c(x, y, c, 'green'); cv.c(x + 1, y, mix(c, (0, 0, 0), 0.25), 'green')
        cv.c(x - 1, y, mix(c, (0, 0, 0), 0.15), 'green')
        cv.c(x, y + 1, mix(c, (0, 0, 0), 0.3), 'green')
        cv.c(x, y - 1, mix(c, (255, 255, 255), 0.3), 'green')
    return [finish(cv)]


def bikes():
    """a low steel bike rack with two parked bikes in profile (not standable): big wheels with silver
    rims and spokes, bright frames, saddles and handlebars so they read as bikes even in the dark"""
    import math
    W, H = 58, 24
    cv = Canvas(W, H)
    cv.hline(2, 55, 21, 'steelB', 3); cv.hline(2, 55, 22, 'stoneN', 2)       # rack rail on the ground
    for x in (4, 20, 36, 52):
        cv.vline(x, 14, 21, 'steelB', 4)

    def bike(bx, mat):
        cy, r = 15, 6
        for wx in (bx, bx + 18):
            for a in range(0, 360, 6):                       # tyre and a silver rim
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                cv.set(wx + round(ca * r), cy + round(sa * r), 'tyre', 3)
                cv.set(wx + round(ca * (r - 1)), cy + round(sa * (r - 1)), 'steelB', 4 if a < 180 else 3)
            for a in range(0, 180, 30):                      # spokes
                for k in (-3, -2, 2, 3):
                    cv.set(wx + round(math.cos(math.radians(a)) * k), cy + round(math.sin(math.radians(a)) * k), 'steelB', 3)
            cv.set(wx, cy, 'steelB', 5)
        def ln(p, q, tone=4):
            n = max(abs(q[0] - p[0]), abs(q[1] - p[1]), 1)
            for t in range(n + 1):
                cv.set(round(p[0] + (q[0] - p[0]) * t / n), round(p[1] + (q[1] - p[1]) * t / n), mat, tone)
        crank = (bx + 8, cy)
        seat = (bx + 6, cy - 8)
        head = (bx + 15, cy - 8)
        ln((bx, cy), crank, 3); ln((bx, cy), seat, 4)       # chain stay, seat stay
        ln(crank, seat, 4); ln(seat, head, 5); ln(crank, head, 4)   # the frame triangle
        ln(head, (bx + 18, cy), 4)                           # fork
        cv.rect(seat[0] - 2, seat[1] - 2, seat[0] + 1, seat[1] - 2, 'tyre', 4)   # saddle
        cv.set(seat[0], seat[1] - 1, 'steelB', 4)
        cv.vline(head[0], head[1] - 3, head[1] - 1, 'steelB', 4)                 # stem and bar
        cv.hline(head[0] - 1, head[0] + 2, head[1] - 3, 'tyre', 4)
        cv.set(crank[0], crank[1], 'steelB', 5); cv.set(crank[0] + 1, crank[1] + 1, 'tyre', 4)   # pedal
        cv.set(bx + 21, cy - 5, 'warm', 4)                   # front lamp
    bike(7, 'bikeR')
    bike(31, 'bikeB')
    return [finish(cv)]


OSLO = [
    ('bench_park', bench_park, 1, None, None),
    ('bench_station', bench_station, 1, None, None),
    ('fountain', fountain, 10, 13, fountain_light),
    ('ad_column', ad_column, 1, 46, ad_column_light),
    ('railing', railing, 1, 0, None),
    ('statue', statue, 1, 17, None),
    ('planter', planter, 1, 9, None),
    ('bikes', bikes, 1, 0, None),
]
