#!/usr/bin/env python3
"""Victory celebration sprites for the ending: the two girls in their ninja outfits and Automat Victoria.

The ending: scrolling slows to a stop, the characters walk to centre stage, turn to face the viewer,
wave and jump. The girls' normal sheets (victoria.png, friend.png) are left untouched; these are separate
sheets in the same 24 × 32 frame size, feet on the bottom row, body centred on x = 12, built from the
same palette letters and the same selective outline as tools/sprites/girls.py.

assets/sprites/celebrate.png  row 0 = Victoria (ninja), row 1 = friend (ninja); 12 columns:
   0 turn0   side-facing (the ninja idle frame from the normal sheet, copied as is)
   1 turn1   three-quarter view
   2 front0  3 front1          front-facing idle (breathing)
   4–7 wave0…wave3             a looping wave with her left hand (viewer's right), happy eyes
   8 takeoff  9 rise  10 fall  11 land   front-facing celebration jump
assets/sprites/automat-celebrate.png  one row, 10 columns (Automat Victoria already faces the viewer):
   0 front (happy)  1–4 wave0…wave3 (one arm waving, the other down)  5 takeoff  6 rise  7 fall  8 land
   9 front (blink)
assets/sprites/celebrate.json  frame layout, animations and timing for both sheets.
In-air jump frames are bottom-aligned like the rest: the game lifts the sprite along its jump arc.
Usage: python3 tools/sprites/celebrate.py
"""
import json
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import girls      # noqa: E402  (parts, palettes, stamp)
import automat    # noqa: E402

FW, FH = 24, 32
P, stamp = girls.P, girls.stamp
COLS = ['turn0', 'turn1', 'front0', 'front1', 'wave0', 'wave1', 'wave2', 'wave3', 'takeoff', 'rise', 'fall', 'land']

FHEAD = P("""
..NNNNNN..
.NMMMNNNN.
NNNNNNNNNn
NNSSSSSSNn
NSSSSSSSSn
NSeSSSSeSn
NSeSSSSeSn
NMMMMMMMMn
.nMMMMMMn.
""")
QHEAD = P("""
..NNNNNN..
.NMMMNNNN.
NNNNNNNNNN
nNNSSSSSSN
nNSSSSSSSS
nNSeSSSeSS
nNSeSSSeSS
nnMMMMMMMM
.nnMMMMMM.
""")
FTORSO = P("""
..nNNn..
.NNMMNN.
NNNMMNNN
NNNNMMNN
NNNNNMNN
NNNNNNNN
TTTTTTTT
nnnnnnnn
""")
LEGS = {
    'stand': (P("""
.NNNNNNNN.
.NNNnnNNN.
.NNN..NNN.
.NNn..NNn.
.NNn..NNn.
.WWW..WWW.
.WWW..WWW.
.NNn..NNn.
.NNn..NNn.
.NNn..NNn.
DDDD..DDDD
dddd..dddd
"""), 7),
    'crouch': (P("""
.NNNNNNNN.
NNNNnnNNNN
NNN....NNN
NNn....NNn
WWW....WWW
WWW....WWW
.NNn..NNn.
.NNn..NNn.
DDDD..DDDD
dddd..dddd
"""), 7),
    'tuck': (P("""
.NNNNNNNN.
NNNNnnNNNN
NNN....NNN
WWW....WWW
WWW....WWW
NNn....NNn
.NNn..NNn.
DDDD..DDDD
dddd..dddd
"""), 7),
    'spread': (P("""
..NNNNNNNN..
..NNNnnNNN..
..NNN..NNN..
.NNn....NNn.
.NNn....NNn.
.WWW....WWW.
.WWW....WWW.
NNn......NNn
NNn......NNn
DDDD....DDDD
dddd....dddd
"""), 6),
}
PONY_FRONT = P("""
.H
HH
hH
.h
""")
PONY_Q = P("""
H.
HH
Hh
h.
""")


def line(g, a, b, ch, w=2):
    n = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
    for i in range(n + 1):
        x = round(a[0] + (b[0] - a[0]) * i / n)
        y = round(a[1] + (b[1] - a[1]) * i / n)
        for dx in range(w):
            if 0 <= y < FH and 0 <= x + dx < FW:
                g[y][x + dx] = ch


def put(g, x, y, ch):
    if 0 <= y < FH and 0 <= x < FW:
        g[y][x] = ch


def hand(g, x, y):
    for dx in (0, 1):
        put(g, x + dx, y, 'W')
        put(g, x + dx, y - 1, 'S'); put(g, x + dx, y - 2, 'S')


def arm(g, side, kind, oy, k=0):
    """side 'L' = viewer's left (her right hand), 'R' = viewer's right. Shoulders at x 6 / 16."""
    s = -1 if side == 'L' else 1
    sx = 6 if side == 'L' else 16
    sy = 13 + oy
    if kind == 'down':
        for y in range(sy, sy + 6):
            put(g, sx, y, 'n' if side == 'L' else 'N'); put(g, sx + 1, y, 'N' if side == 'L' else 'n')
        put(g, sx, sy + 6, 'W'); put(g, sx + 1, sy + 6, 'W')
        put(g, sx, sy + 7, 'S'); put(g, sx + 1, sy + 7, 'S')
    elif kind == 'back':          # down and a little out (take-off, landing)
        line(g, (sx, sy), (sx + s * 1, sy + 5), 'N')
        put(g, sx + s, sy + 6, 'W'); put(g, sx + s + 1, sy + 6, 'W')
        put(g, sx + s, sy + 7, 'S'); put(g, sx + s + 1, sy + 7, 'S')
    elif kind == 'up':            # a V over the head
        hx = sx + s * 3
        line(g, (sx, sy), (hx, sy - 7), 'N')
        put(g, hx, sy - 8, 'W'); put(g, hx + 1, sy - 8, 'W')
        put(g, hx, sy - 9, 'S'); put(g, hx + 1, sy - 9, 'S'); put(g, hx, sy - 10, 'S'); put(g, hx + 1, sy - 10, 'S')
    elif kind == 'out':           # out to the side
        hx = sx + s * 4
        line(g, (sx, sy), (hx, sy - 1), 'N')
        put(g, hx + s * 2 if s > 0 else hx - 1, sy - 1, 'S')
        put(g, hx + (2 if s > 0 else -1), sy - 2, 'S')
    elif kind == 'wave':          # elbow out, forearm up, the hand swings: k = 0…3
        ex, ey = sx + s * 3, sy - 2
        line(g, (sx, sy), (ex, ey), 'N')
        dx = (0, 1, 0, -1)[k]
        hx, hy = ex + dx, ey - 5
        line(g, (ex, ey), (hx, hy + 1), 'N')
        put(g, hx, hy + 1, 'W'); put(g, hx + 1, hy + 1, 'W')
        for yy in (hy, hy - 1):
            put(g, hx, yy, 'S'); put(g, hx + 1, yy, 'S')
        put(g, hx + (2 if dx >= 0 else -1), hy - 1, 'S')     # spread fingers / thumb
        if dx:                                              # motion marks beside the hand
            put(g, hx + (3 if dx > 0 else -2), hy, 'Y')


def happy(g, hx, hy):
    """^ ^ eyes on a front head stamped at (hx, hy)"""
    for ex in (2, 7):
        put(g, hx + ex, hy + 5, 'e'); put(g, hx + ex, hy + 6, 'S')
        put(g, hx + ex - 1, hy + 6, 'e'); put(g, hx + ex + 1, hy + 6, 'e')


POSE = {
    #          oy  legs      armL    armR    eyes
    'turn1':  (0, 'stand',  'down', 'down', 'open'),
    'front0': (0, 'stand',  'down', 'down', 'open'),
    'front1': (1, 'stand',  'down', 'down', 'open'),
    'wave0':  (0, 'stand',  'down', 'wave', 'happy'),
    'wave1':  (0, 'stand',  'down', 'wave', 'happy'),
    'wave2':  (0, 'stand',  'down', 'wave', 'happy'),
    'wave3':  (0, 'stand',  'down', 'wave', 'happy'),
    'takeoff': (2, 'crouch', 'back', 'back', 'open'),
    'rise':   (3, 'tuck',   'up',   'up',   'happy'),
    'fall':   (1, 'spread', 'out',  'out',  'happy'),
    'land':   (2, 'crouch', 'out',  'out',  'happy'),
}


def frame(name, girl):
    g = girls.blank()
    oy, legs, aL, aR, eyes = POSE[name]
    if name == 'front1':          # breathing: legs stay, upper body dips 1 px
        oy = 0
    hy = 3 + oy + (1 if name == 'front1' else 0)
    by = oy + (1 if name == 'front1' else 0)
    q = name == 'turn1'
    # behind: katana hilt over her left shoulder, ponytail, scarf tails
    put(g, 18, 9 + by, 'g'); put(g, 17, 10 + by, 'g'); put(g, 17, 11 + by, 'r')
    stamp(g, PONY_Q if q else PONY_FRONT, 4 if q else 16, hy + 1)
    lg, lx = LEGS[legs]
    stamp(g, lg, lx, FH - len(lg))
    stamp(g, FTORSO, 8 + (1 if q else 0), 12 + by)
    k = int(name[4]) if name.startswith('wave') else 0
    arm(g, 'L', aL, by)
    arm(g, 'R', aR, by, k)
    # scarf knot at the neck and a tail hanging over the chest (it flutters while waving)
    for x in range(9, 14):
        put(g, x + (1 if q else 0), 12 + by, 'Y')
    tail = 9 + (k % 2) if name.startswith('wave') else 9
    put(g, tail, 13 + by, 'Y'); put(g, tail, 14 + by, 'T'); put(g, tail - (k % 2), 15 + by, 'Y')
    stamp(g, QHEAD if q else FHEAD, 7 + (1 if q else 0), hy)
    if eyes == 'happy':
        happy(g, 7, hy)
    for row in g:                 # ninja colours, as in girls.py
        for i, ch in enumerate(row):
            row[i] = girls.NINJA_MAP.get(ch, ch)
    return g


def to_image(g, pal):
    """the girls' selective outline: a darkened copy of the neighbouring colour"""
    img = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    for y in range(FH):
        for x in range(FW):
            if g[y][x] != '.':
                img.putpixel((x, y), girls.hexrgb(pal[g[y][x]]) + (255,))
    out = img.copy()
    for y in range(FH):
        for x in range(FW):
            if img.getpixel((x, y))[3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < FW and 0 <= ny < FH and img.getpixel((nx, ny))[3]:
                    r, gg, b, _ = img.getpixel((nx, ny))
                    out.putpixel((x, y), (int(r * .28) + 8, int(gg * .22) + 6, int(b * .3) + 14, 255))
                    break
    return out


# ---------------------------------------------------------------- Automat Victoria
ACOLS = ['front', 'wave0', 'wave1', 'wave2', 'wave3', 'takeoff', 'rise', 'fall', 'land', 'blink']


def automat_frame(name):
    """Built from automat.frame(): she already faces the viewer. Her cheer frames raise both arms, so
    the wave (one arm waving, the other down) and the jump squash/stretch are added here."""
    base = {'front': 'cheer0', 'blink': 'idle1', 'takeoff': 'cheer0', 'land': 'cheer0',
            'rise': 'cheer1', 'fall': 'cheer0'}.get(name, 'cheer0')
    g = automat.frame(base)
    if name in ('front', 'blink') or name.startswith('wave') or name in ('takeoff', 'land'):
        for y in range(FH):                     # clear both arms and the sparkles (outside the cabinet)
            for x in (0, 1, 2, 21, 22, 23):
                g[y][x] = '.'
        y0 = 1
        if name.startswith('wave'):             # her right arm (viewer's left) waves, the other hangs
            k = int(name[4])
            hx = (1, 0, 1, 2)[k]
            g_set = lambda x, y, c: (0 <= x < FW and 0 <= y < FH) and g[y].__setitem__(x, c)
            for y in range(y0 + 9, y0 + 14):
                g_set(2, y, 'S')
            for y in range(y0 + 5, y0 + 9):
                g_set(hx, y, 'S'); g_set(hx + 1, y, 'S')
            for y in (y0 + 3, y0 + 4):
                g_set(hx, y, 'W'); g_set(hx + 1, y, 'W')
            g_set((0, 3, 0, 3)[k] if k != 2 else 0, y0 + 2, 'Y') if k in (1, 3) else None
        else:
            for y in range(y0 + 14, y0 + 20):
                g[y][2] = 'n'; g[y][3] = g[y][3] if g[y][3] != '.' else 'n'
            g[y0 + 20][2] = 'W'
        for y in range(y0 + 14, y0 + 20):       # the other arm hangs down
            g[y][20] = 'n'; g[y][21] = 'n'
        g[y0 + 20][20] = 'W'; g[y0 + 20][21] = 'W'
        if name in ('front',) or name.startswith('wave') or name == 'land':
            # happy ^ ^ eyes and an open smile (the cheer face) are already in cheer0
            pass
    if name in ('takeoff', 'land'):            # squash: drop the top row, remove the shadow row under the head
        del g[18]
        g.insert(0, ['.'] * FW)
    return g


def automat_image(g):
    img = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    for y in range(FH):
        for x in range(FW):
            if g[y][x] != '.':
                img.putpixel((x, y), automat.hexrgb(automat.PAL[g[y][x]]))
    out = img.copy()
    for y in range(FH):
        for x in range(FW):
            if img.getpixel((x, y))[3] or g[y][x] == 'Y':
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < FW and 0 <= ny < FH and img.getpixel((nx, ny))[3] and g[ny][nx] != 'Y':
                    r, gg, b, _ = img.getpixel((nx, ny))
                    out.putpixel((x, y), (int(r * .25) + 8, int(gg * .22) + 8, int(b * .3) + 18, 255))
                    break
    return out


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
    sheet = Image.new('RGBA', (FW * len(COLS), FH * 2), (0, 0, 0, 0))
    for row, girl in enumerate(('victoria', 'friend')):
        src = Image.open(root / f'{girl}.png').convert('RGBA')
        sheet.paste(src.crop((0, FH, FW, 2 * FH)), (0, row * FH))      # turn0 = the existing ninja idle0
        pal = {**girls.COMMON, **girls.LOOKS[girl]}
        for c, name in enumerate(COLS[1:], start=1):
            sheet.paste(to_image(frame(name, girl), pal), (c * FW, row * FH))
    sheet.save(root / 'celebrate.png')
    a = Image.new('RGBA', (FW * len(ACOLS), FH), (0, 0, 0, 0))
    for c, name in enumerate(ACOLS):
        a.paste(automat_image(automat_frame(name)), (c * FW, 0))
    a.save(root / 'automat-celebrate.png')
    meta = {
        'girls': {'file': 'celebrate.png', 'frame': [FW, FH], 'rows': {'victoria': 0, 'friend': 1},
                  'columns': COLS,
                  'anims': {'turn': {'frames': [0, 1, 2], 'fps': 10, 'loop': False},
                            'idle': {'frames': [2, 3], 'fps': 2, 'loop': True},
                            'wave': {'frames': [4, 5, 6, 7], 'fps': 8, 'loop': True},
                            'jump': {'frames': [8, 9, 10, 11], 'loop': False,
                                     'durations': [0.1, None, None, 0.14],
                                     'note': 'takeoff and land are timed; rise while going up, fall while coming down'}}},
        'automat': {'file': 'automat-celebrate.png', 'frame': [FW, FH], 'columns': ACOLS,
                    'anims': {'idle': {'frames': [0, 0, 0, 9], 'fps': 3, 'loop': True},
                              'wave': {'frames': [1, 2, 3, 4], 'fps': 8, 'loop': True},
                              'jump': {'frames': [5, 6, 7, 8], 'loop': False, 'durations': [0.1, None, None, 0.14]}}},
        'alignment': 'feet (base) on the bottom row, body centred on x = 12; in-air frames are lifted by the game',
    }
    (root / 'celebrate.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote celebrate.png', sheet.size, 'automat-celebrate.png', a.size, 'celebrate.json')
