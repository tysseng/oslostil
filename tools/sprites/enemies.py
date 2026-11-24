#!/usr/bin/env python3
"""Pixel-art sprite sheet for enemies, obstacles, pickups and projectiles.

Hand-drawn as ASCII (one letter per palette colour), then given a selective dark outline.
Every sprite sits in a 32 × 32 cell, bottom-centred (its base on the bottom row, centre on x = 16).
One row per sprite, one column per animation frame.

Writes assets/sprites/enemies.png and assets/sprites/enemies.json
({name: {row, frames, fps, w, h}}; w × h is the visible size incl. outline, used as the hitbox).
Usage: python3 tools/sprites/enemies.py
"""
import json
import random
from pathlib import Path
from PIL import Image

CELL = 32
PAL = {
    # luggage
    'r': '#c0392b', 'd': '#8e2a20', 'l': '#e85a4a', 'y': '#ffd84a', 'h': '#3a2a2a', 'k': '#1e1e24', 'c': '#5a1f18', 'w': '#ffffff',
    # snow
    'W': '#f4f8ff', 'b': '#c9dbf2', 's': '#93add2', '*': '#ffffff',
    # pigeon
    'g': '#8a8f9a', 'G': '#666b76', 'L': '#b8bdc6', 'n': '#4fae86', 'p': '#8a5fb0', 'o': '#ff8a00', 'e': '#111111', 'B': '#e8c49a', 'f': '#e87a8a',
    # ticket
    'a': '#ffd84a', '~': '#e0a91c', 'D': '#c08a12', 'v': '#fff6c4', 'K': '#1a1a22',
    # ninja
    'P': '#2b1747', 'q': '#1a0c2e', 'H': '#4a2c78', 'S': '#e0b0a0', 'E': '#ff2020', 'Z': '#d8dde6', 'z': '#6b4a2a', 'F': '#111111', 'A': '#c0233b',
    # drone / bot / terminal
    'm': '#5b5f72', 'M': '#3a3d4c', 'i': '#9aa0b8', 'C': '#2bf0ff', 'O': '#ff3030', 'u': '#ffb000', 'U': '#ffd36a', 'j': '#4a5160', 'J': '#353a46', 'Q': '#6a7386',
    'V': '#3dff7a', 'X': '#2a2e38', 'Y': '#5fd0ff', 'N': '#1c6fb0',
    # fire / coin / shots
    '1': '#ffd000', '2': '#ff7b00', '3': '#e03a00', '4': '#5a1a00', '5': '#fff3a0', '6': '#ffcf3a', '7': '#c99400', '8': '#ff2b6b', '9': '#ffd0e0', '0': '#ff5a00',
    '!': '#fff07a',
}

S = {}  # name -> list of frames (each a list of strings)


def art(s):
    rows = s.strip('\n').split('\n')
    w = max(len(r) for r in rows)
    return [r.ljust(w, '.') for r in rows]


S['suitcase'] = [art("""
.....hhhhhh.....
.....h....h.....
.....h....h.....
cdrrrrrrrrrrrrlc
drrrrrrrrrrrrrll
drrrrrrrrwwwrrll
drrrrrrrrwKKwrll
drrrrrrrrwwwrrll
yyyyyyyyyyyyyyyy
drrrrrrrrrrrrrll
drrrrrrrrrrrrrll
drrrrrrrrrrrrrll
drrrrrrrrrrrrrll
cddddddddddddddc
.kk..........kk.
""")]

S['snow'] = [art("""
.......WWWW.........
.....WWWWWWWW.......
....WWWWWWWWWWW.....
...WWWWW*WWWWWWWW...
..WWWWWWWWWWWWWWWW..
.WWWWWWWWWWWWWWWWWWb
WWWWWWWWWWWWWWWWWbbb
bWWWWWWWWWWWWWWbbbbb
sbbbbbbbbbbbbbbbbbbs
.sssssssssssssssss..
"""), art("""
.......WWWW.........
.....WWWWWWWW..*....
....WWWWWWWWWWW.....
...WWWWWWWWWWWWWW...
..WWWWWWWWWWWWWWWW..
.WWWWW*WWWWWWWWWWWWb
WWWWWWWWWWWWWWWWWbbb
bWWWWWWWWWWWWWWbbbbb
sbbbbbbbbbbbbbbbbbbs
.sssssssssssssssss..
""")]

S['pigeon'] = [art("""
.......LLL.....
......LLGGL....
.......LGGGL...
..nn....GGG....
.onnp..gggg....
BBnnggggggggGG.
..ggggggggggGGG
...ggggggggGGG.
....gggggggg...
......f..f.....
......f..f.....
"""), art("""
...............
...............
..nn...........
.onnp..gggg....
BBnnggggggggGG.
..ggggGGGGggGGG
...gggGGGGGgGG.
....ggGGGGGg...
.......GGG.....
......f..f.....
......f..f.....
""")]

# the ticket: a small classic yellow tear-off ticket (rounded notches, perforation) that spins in the air
S['ticket'] = [art("""
aaaaaaaaaaaaaa
aaaaaaaaaaDaaa
.aaaaaaaaaaaa.
.aaaaaaaaaDaa.
aaaaaaaaaaaaa~
~~~~~~~~~~~~~~
"""), art("""
.aaaaaaaaa.
.aaaaaaaDa.
..aaaaaaa..
..aaaaaaD..
.aaaaaaaa~.
.~~~~~~~~~.
"""), art("""
...aa...
...aa...
...aa...
...aa...
...a~...
...~~...
"""), art("""
.aaaaaaaaa.
.aDaaaaaaa.
..aaaaaaa..
..Daaaaaa..
.~aaaaaaaa.
.~~~~~~~~~.
""")]

S['ninja'] = [art("""
......HPPPPH.......
.....PPPPPPPP......
.....PSSSSSSP......
.....PSESSESP......
.....PPPPPPPPAA....
......PPPPPP..AA...
....qPPPPPPPPq.....
...qqPPPPPPPPqq....
ZZZzqPPPPPPPPqq....
ZZ..qPPAAAAAPPq....
....qPPPPPPPPq.....
....qPPPPPPPPq.....
.....PPPPPPPP......
.....PPPPPPPP......
....PPPP..PPP......
...PPPP....PPP.....
..PPPP......PPP....
..PPP........PPP...
.FFFF........FFFF..
"""), art("""
......HPPPPH.......
.....PPPPPPPP......
.....PSSSSSSP......
.....PSESSESP......
.....PPPPPPPPA.....
......PPPPPP.AAA...
....qPPPPPPPPq.....
...qqPPPPPPPPqq....
ZZZzqPPPPPPPPqq....
ZZ..qPPAAAAAPPq....
....qPPPPPPPPq.....
....qPPPPPPPPq.....
.....PPPPPPPP......
.....PPPPPPPP......
......PPPPPP.......
......PPP.PP.......
.....PPP..PPP......
.....PPP..PPP......
....FFFF..FFFF.....
""")]

S['drone'] = [art("""
iiiiii..........iiiiii
...M..............M...
...MMmmmmmmmmmmmmMM...
..mmmmmmmmmmmmmmmmmm..
.mmmCCCmmmmmmmmmmmmmm.
.mmmmmmmmmmmmmmmmmmmm.
..MMMMMMMMMMMMMMMMMM..
........MMMMMM........
.........MOOM.........
..........MM..........
"""), art("""
..iiii..........iiii..
...M..............M...
...MMmmmmmmmmmmmmMM...
..mmmmmmmmmmmmmmmmmm..
.mmmCCCmmmmmmmmmmmmmm.
.mmmmmmmmmmmmmmmmmmmm.
..MMMMMMMMMMMMMMMMMM..
........MMMMMM........
.........MKKM.........
..........MM..........
""")]

S['bot'] = [art("""
.......OO.......
.......QQ.......
.......QQ.......
..jjjjjjjjjjjj..
..jJuuuuuuuuQj..
..jJuKKuuKKuQj..
..jJuKKuuKKuQj..
..jJuuuuuuuuQj..
..jjjjjjjjjjjj..
.jjjjjjjjjjjjjj.
QJjjXXXXXXXXjjQQ
QJjjXVXXXXOXjjQQ
QJjjXXXXXXXXjjQQ
.Jjjjjjjjjjjjjj.
..jjjjjjjjjjjj..
..JJJ......JJJ..
.XXXXX....XXXXX.
.XKXKX....XKXKX.
.XXXXX....XXXXX.
"""), art("""
.......KK.......
.......QQ.......
.......QQ.......
..jjjjjjjjjjjj..
..jJuuuuuuuuQj..
..jJuuuuuuuuQj..
..jJuKKuuKKuQj..
..jJuuuuuuuuQj..
..jjjjjjjjjjjj..
.jjjjjjjjjjjjjj.
QJjjXXXXXXXXjjQQ
QJjjXXXXXXXXjjQQ
QJjjXVXXXXOXjjQQ
.Jjjjjjjjjjjjjj.
..jjjjjjjjjjjj..
..JJJ......JJJ..
.XXXXX....XXXXX.
.XKXKX....XKXKX.
.XXXXX....XXXXX.
""")]

# the card terminal power-up: a reader on a short post with a glowing blue screen
S['terminal'] = [art("""
.XXXXXXXXXXXX.
XXYYYYYYYYYYXX
XXYwwYYYYYYYXX
XXYYYYYYYYYYXX
XXYYYYNNYYYYXX
XXYYYYYYYYYYXX
XXXXXXXXXXXXXX
XXXKKKKKKKKXXX
XXXXXXXXXXXXXX
.....XXXX.....
.....XXXX.....
.....XXXX.....
.....XXXX.....
.....XXXX.....
.....XXXX.....
...XXXXXXXX...
"""), art("""
.XXXXXXXXXXXX.
XXwwwwwwwwwwXX
XXwYYYYYYYYwXX
XXwYYYYYYYYwXX
XXwYYYNNYYYwXX
XXwwwwwwwwwwXX
XXXXXXXXXXXXXX
XXXKKKKKKKKXXX
XXXXXXXXXXXXXX
.....XXXX.....
.....XXXX.....
.....XXXX.....
.....XXXX.....
.....XXXX.....
.....XXXX.....
...XXXXXXXX...
""")]

S['fire'] = [art("""
.....1.........1...
....121.......12...
....122...1...121..
...1222..121.1221..
..12232.12221222...
..1223322223322221.
.122333322333322221
.123333333333333321
1223333333333333221
4444444444444444444
"""), art("""
........1..........
..1....121....1....
.121..1221...121...
.1221.12221.12221..
12232.1223321223...
1223322223333222...
1223333223333322221
1233333333333333321
1223333333333333221
4444444444444444444
"""), art("""
...1.......1.......
..121.....121...1..
..1221...1221..121.
.12221..12231.1221.
.122332122331.12221
1223333222333222321
1233333333333333321
1233333333333333321
1223333333333333221
4444444444444444444
""")]

S['coin'] = [art("""
...6666...
..655556..
.65666656.
6556777656
6566777656
6566777656
6556777656
.65666656.
..657756..
...6666...
"""), art("""
...666....
..65556...
..656656..
.6567756..
.6567756..
.6567756..
.6567756..
..656656..
..65776...
...666....
"""), art("""
....66....
....56....
....56....
....56....
....56....
....56....
....56....
....56....
....57....
....66....
"""), art("""
....666...
...65556..
..656656..
..6577656.
..6577656.
..6577656.
..6577656.
..656656..
...67756..
....666...
""")]

S['shot'] = [art("""
...8888...
..899998..
.89999998.
8999999998
8999999998
8999999998
8999999998
.89999998.
..899998..
...8888...
"""), art("""
..........
...8888...
..899998..
.89999998.
.89999998.
.89999998.
.89999998.
..899998..
...8888...
..........
""")]

S['fireball'] = [art("""
....2222......
..22111122.0..
.211!!!1122.00
21!!!!!!1122..
21!!!!!!11220.
21!!!!!!1122..
.211!!!1122.00
..22111122.0..
....2222......
"""), art("""
....2222....0.
..22111122.00.
.211!!!1122...
21!!!!!!11220.
21!!!!!!112200
21!!!!!!11220.
.211!!!1122...
..22111122.00.
....2222....0.
""")]


def blob_frames(n=4):
    """The glitch: like the first version, a cloud of loose pink and cyan 2 × 2 pixel squares that jump around."""
    out = []
    for f in range(n):
        rnd = random.Random(11 + f)
        grid = [['.'] * 16 for _ in range(16)]
        for i in range(13):
            x, y = rnd.randrange(0, 15), rnd.randrange(0, 15)
            c = '8' if i % 2 else 'C'
            for dx in (0, 1):
                for dy in (0, 1):
                    grid[y + dy][x + dx] = c
        out.append([''.join(r) for r in grid])
    return out


S['blob'] = blob_frames()


# The glitch, hopping version (level 2): the same loose pink/cyan 2 × 2 squares, packed into a blob that
# squashes, stretches and hops leftwards, one hop per beat. 8 frames per hop (≈ 16 fps at 122 BPM):
#   0 land (squashed flat, squares spilling out)  1 recover  2 crouch  3 launch (stretched tall)
#   4 rise (stragglers left behind)  5 apex (loose)  6 fall (stragglers above)  7 about to land
# The sprite only changes shape; the code moves it along the hop arc (airborne in frames 3–7).
HOP_SHAPES = [(22, 8, .95, 0), (18, 12, .9, 0), (20, 10, .95, 0), (12, 20, .9, 0),
              (14, 18, .85, 2), (16, 16, .7, 0), (14, 18, .85, -2), (16, 14, .9, 0)]


def blob_hop_frames():
    out = []
    G = 24
    for f, (w, h, dens, trail) in enumerate(HOP_SHAPES):
        rnd = random.Random(40 + f)
        grid = [['.'] * G for _ in range(G)]

        def sq(x, y, c):
            for dx in (0, 1):
                for dy in (0, 1):
                    if 0 <= x + dx < G and 0 <= y + dy < G:
                        grid[y + dy][x + dx] = c
        cx, cy = G / 2, G - h / 2
        n = 0
        for y in range(G - 2, -1, -2):
            for x in range(0, G - 1, 2):
                dx, dy = (x + 1 - cx) / (w / 2), (y + 1 - cy) / (h / 2)
                if dx * dx + dy * dy <= 1.0 and rnd.random() < dens:
                    sq(x + rnd.choice((0, 0, 1)) - (1 if f % 2 else 0) * (y % 4 == 0), y, '8' if (x // 2 + y // 2 + f) % 2 else 'C')
                    n += 1
        if f == 0:                                       # landing: squares spill out sideways
            for x, c in ((0, 'C'), (1, '8'), (G - 3, '8'), (G - 2, 'C')):
                sq(x, G - 2 - rnd.randrange(0, 3), c)
        if trail:                                        # stragglers: below on the way up, above on the way down
            for i in range(4):
                x = int(cx) - 6 + rnd.randrange(0, 12)
                y = (G - 2 - rnd.randrange(0, 3)) if trail > 0 else max(0, int(cy - h / 2) - 3 - 2 * i)
                sq(x, y, '8' if i % 2 else 'C')
        out.append([''.join(r) for r in grid])
    return out


def blob_pop_frames():
    """Hit: the blob bursts into squares that fly out and shrink to single pixels."""
    out = []
    G = 24
    rnd0 = random.Random(77)
    parts = [(rnd0.uniform(0, 6.283), rnd0.uniform(.5, 1.0), '8' if i % 2 else 'C') for i in range(16)]
    import math
    for f in range(5):
        grid = [['.'] * G for _ in range(G)]
        r = 3 + f * 2.6
        size = 2 if f < 3 else 1
        for a, sp, c in parts:
            if f == 4 and sp < .7:
                continue
            x = int(G / 2 + math.cos(a) * r * sp)
            y = int(G - 8 + math.sin(a) * r * sp * .8)
            for dx in range(size):
                for dy in range(size):
                    if 0 <= x + dx < G and 0 <= y + dy < G:
                        grid[y + dy][x + dx] = c
        out.append([''.join(r_) for r_ in grid])
    return out


S['blob_hop'] = blob_hop_frames()
S['blob_pop'] = blob_pop_frames()

def gull_frames(n=8):
    """The seagull (replaces the drone): white head and body, grey back and wings, black wing tips,
    yellow beak with a red spot. Side view facing left, an 8-frame flap: the near wing sweeps from high
    above the back to low under the belly, the far wing shows behind the body on the upstroke."""
    import math
    W_, H_ = 28, 29
    out = []
    for f in range(n):
        g = [['.'] * W_ for _ in range(H_)]

        def put(x, y, c):
            y += 3
            if 0 <= x < W_ and 0 <= y < H_:
                g[y][x] = c

        def tri(p0, p1, p2, fill, shade=None):
            xs = [p0[0], p1[0], p2[0]]; ys = [p0[1], p1[1], p2[1]]
            for y in range(math.floor(min(ys)), math.ceil(max(ys)) + 1):
                for x in range(math.floor(min(xs)), math.ceil(max(xs)) + 1):
                    px, py = x + 0.5, y + 0.5
                    d = lambda a, b: (b[0] - a[0]) * (py - a[1]) - (b[1] - a[1]) * (px - a[0])
                    s1, s2, s3 = d(p0, p1), d(p1, p2), d(p2, p0)
                    if (s1 >= 0 and s2 >= 0 and s3 >= 0) or (s1 <= 0 and s2 <= 0 and s3 <= 0):
                        put(x, y, fill)

        ang = math.radians(70 * math.cos(2 * math.pi * f / n))     # +70° up … −70° down
        sx, sy = 13, 10                                              # shoulder
        L = 14
        tip = (sx + 7 + 2 * (1 - abs(math.sin(ang))), sy - L * math.sin(ang))
        # far wing (behind the body), only above it on the upstroke
        if ang > 0.2:
            ft = (tip[0] + 2, sy - (L - 2) * math.sin(ang))
            tri((sx - 1, sy), (sx + 5, sy), ft, 'G')
        # tail
        for y in range(9, 12):
            for x in range(19, 23 - abs(y - 10)):
                put(x, y, 'W' if y < 11 else 'b')
        put(22, 10, 'L')
        # body: an oval
        for y in range(7, 14):
            for x in range(5, 21):
                if ((x - 12.5) / 8.2) ** 2 + ((y - 10) / 3.4) ** 2 <= 1:
                    put(x, y, 'b' if y >= 12 else 'W')
        for x in range(10, 19):                                      # grey mantle on the back
            put(x, 7 if 11 <= x <= 16 else 8, 'L')
        # head
        for y in range(5, 11):
            for x in range(3, 10):
                if ((x - 6) / 3.3) ** 2 + ((y - 7.6) / 2.8) ** 2 <= 1:
                    put(x, y, 'W')
        put(4, 7, 'e'); put(5, 6, 'b')                               # eye
        put(2, 8, 'y'); put(1, 8, 'y'); put(0, 9, 'D'); put(1, 9, 'r'); put(2, 9, 'y')   # beak
        put(14, 14, 'f')                                             # legs tucked under the belly
        # near wing: grey with a darker leading edge and a black tip with a white spot
        sn = math.sin(ang)
        wf = (sx - 1, sy - 0.62 * L * sn)                            # wrist, leading edge
        wb = (sx + 6, sy - 0.55 * L * sn)                            # wrist, trailing edge
        tri((sx - 3, sy - 1), (sx + 6, sy - 1), wb, 'L')
        tri((sx - 3, sy - 1), wf, wb, 'L')
        tri(wf, wb, tip, 'L')
        tri((sx - 3, sy - 1), (sx - 2, sy), wf, 'g')                 # darker leading edge
        tri(wf, (wf[0] + 1, wf[1]), tip, 'g')
        for i in range(1, 6):                                        # secondary feathers: a white trailing edge
            t = i / 6
            put(round(sx + 6 + (wb[0] - sx - 6) * t) + 1, round(sy - 1 + (wb[1] - sy + 1) * t), 'W')
        tx, ty = round(tip[0]), round(tip[1])
        dy = -1 if ang > 0 else 1
        for i in range(3):
            put(tx - (1 if i == 2 else 0), ty + dy * -i, 'k') if 0 else None
        for i in range(4):                                           # the black tip
            yy = ty - dy * i * -1
            yy = ty + (i if ang > 0 else -i)
            put(tx, yy, 'k'); put(tx + 1, yy, 'k' if i < 2 else 'L')
        put(tx, ty + (1 if ang > 0 else -1), 'W')
        if abs(ang) < 0.3:                                           # level: wing seen almost edge-on
            for x in range(sx - 2, sx + 9):
                put(x, sy - 1, 'L'); put(x, sy, 'g')
            put(sx + 9, sy - 1, 'k'); put(sx + 10, sy - 1, 'k')
        out.append([''.join(r) for r in g])
    return out


S['gull'] = gull_frames()

ORDER = ['suitcase', 'snow', 'pigeon', 'ticket', 'blob', 'ninja', 'drone', 'bot', 'terminal', 'fire', 'coin', 'shot', 'fireball', 'gull',
         'blob_hop', 'blob_pop']
FPS = {'blob_hop': 16, 'blob_pop': 16, 'gull': 14, 'pigeon': 8, 'ticket': 8, 'blob': 20, 'ninja': 8, 'drone': 16, 'bot': 3, 'terminal': 4, 'fire': 10, 'coin': 10, 'shot': 12, 'fireball': 12, 'snow': 2, 'suitcase': 1}


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


NO_OUTLINE = {'blob', 'blob_hop', 'blob_pop'}


def render_cell(rows, outline=True):
    img = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    h, w = len(rows), len(rows[0])
    ox, oy = CELL // 2 - w // 2, CELL - 1 - h      # bottom-centred, one row left free for the outline
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                img.putpixel((ox + i, oy + j), hexrgb(PAL[ch]))
    if not outline:
        return img
    out = img.copy()  # selective outline
    for y in range(CELL):
        for x in range(CELL):
            if img.getpixel((x, y))[3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < CELL and 0 <= ny < CELL and img.getpixel((nx, ny))[3]:
                    r_, g_, b_, _ = img.getpixel((nx, ny))
                    out.putpixel((x, y), (int(r_ * .25) + 10, int(g_ * .22) + 10, int(b_ * .3) + 16, 255))
                    break
    return out


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
    cols = max(len(S[n]) for n in ORDER)
    sheet = Image.new('RGBA', (CELL * cols, CELL * len(ORDER)), (0, 0, 0, 0))
    meta = {}
    for row, name in enumerate(ORDER):
        boxes = []
        for col, rows in enumerate(S[name]):
            cell = render_cell(rows, outline=name not in NO_OUTLINE)
            sheet.paste(cell, (col * CELL, row * CELL))
            boxes.append(cell.getbbox())
        x0 = min(b[0] for b in boxes); x1 = max(b[2] for b in boxes); y0 = min(b[1] for b in boxes)
        meta[name] = {'row': row, 'frames': len(S[name]), 'fps': FPS.get(name, 6), 'w': x1 - x0, 'h': CELL - y0}
    # the gull's wings sweep far above and below its body: its hitbox is the body only, and «dy» is how
    # far below the enemy's base the sheet cell is drawn so that the body's underside sits on the base
    meta['gull'].update({'w': 22, 'h': 12, 'dy': 11})
    # the hopping glitch: hitbox = its resting size; frames 3–7 are in the air (the code moves it on the arc),
    # frame 0 is the landing and should fall on the beat
    meta['blob_hop'].update({'w': 16, 'h': 14, 'air': [3, 7], 'land': 0, 'frames_per_hop': 8})
    sheet.save(root / 'enemies.png')
    (root / 'enemies.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote', root / 'enemies.png', sheet.size)
    for n in ORDER:
        print(f"  {n:9s} {meta[n]['w']:2d} × {meta[n]['h']:2d}  frames {meta[n]['frames']}")
