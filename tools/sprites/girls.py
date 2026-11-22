#!/usr/bin/env python3
"""Generate the pixel-art sprite sheets for the two girls.

Each sheet is 10 columns x 2 rows of 24x32 frames (row 0 = normal clothes, row 1 = ninja).
Columns: idle0 idle1 run0 run1 run2 run3 jumpUp jumpDown slide attack.
Feet touch the bottom row; the body's centre line is x = 12.

The art is composed from small hand-drawn parts (ASCII, one letter per palette slot),
recoloured per girl and outfit, then given a selective dark outline.
Usage: python3 tools/sprites/girls.py   (writes assets/sprites/*.png)
"""
from pathlib import Path
from PIL import Image

FW, FH = 24, 32
COLS = ['idle0', 'idle1', 'run0', 'run1', 'run2', 'run3', 'jumpUp', 'jumpDown', 'slide', 'attack']

def P(s):
    rows = [r for r in s.strip('\n').split('\n')]
    w = max(len(r) for r in rows)
    return [r.ljust(w, '.') for r in rows]

# ---------------- parts (facing right) ----------------
HEAD = P("""
..HHHHHH..
.HLLLLHHH.
HHHHHHHHHH
hHHHHHSHHH
hHHHHSSSSS
hHHHSeSSeS
hhHHSeSSeS
hhHHSSSSbS
.hhsSSSmS.
""")
HOOD = P("""
..NNNNNN..
.NMMMMNNN.
NNNNNNNNNN
nNNNNNNNNN
nNNNSSSSSS
nNNNSeSSeS
nnNNMMMMMM
nnNNMMMMMM
.nnnMMMMM.
""")
PONY = [P("""
...hH
..hHH
.hHH.
.hH..
hH...
hh...
"""), P("""
..hHH
.hHHH
hHH..
hH...
h....
.....
""")]
NPONY = [P("""
..hH
.hHH
hHH.
hH..
"""), P("""
.hHH
hHHH
hH..
....
""")]
BACKHAIR = P("""
.hHH
hHHH
hHHh
hhHh
hhh.
.h..
""")
NECK = P("ss")
TORSO = P("""
.jJJJZJ.
jjJJJZJJ
jjJJJZKJ
jjJJJZKJ
jjJJJZJJ
jjjjjZjj
""")
NTORSO = P("""
.nNNNNN.
nnMNNNNN
nnNMNNMN
nnNNMMNN
nTTTTTTT
nnnnnnnn
""")
SCARF = P("""
.CCCCCC.
CCCCCCCx
..xCCx..
...Cx...
...C....
""")
NSCARF_TAIL = [P("""
YY......
.TYYTY..
....YTYT
"""), P("""
YY......
.TYYT...
...YTYTY
""")]
BAG = P("""
cBB
BBB
BcB
BBB
BBB
BBB
.B.
""")
KATANA = P("""
r..
gk.
gk.
gk.
gk.
gk.
gk.
gk.
.g.
""")
ARM = {
 'down': (P("""
JK
JK
JJ
jJ
jJ
ZZ
SS
"""), 11, 13),
 'fwd': (P("""
JK..
JJK.
.jJJ
..jJ
..ZZ
..SS
"""), 11, 13),
 'back': (P("""
..KJ
.KJJ
JJj.
Jj..
ZZ..
SS..
"""), 8, 13),
 'up': (P("""
..SS
..ZZ
.JJ.
JJ..
JK..
"""), 11, 9),
 'attack': (P("""
JJJJZSS
jjjjZSS
"""), 11, 14),
}
CARD = P("""
UUUU
uuuU
UUUU
""")
LEGS = {
 'stand': P("""
....PPPPPPP...
....PPPPPPP...
....pPPP.PP...
....pPP..PP...
....pPP..PP...
....pPP..PP...
....pPP..PP...
....pPP..PP...
....pPP..PP...
....pPP..PP...
...FFFF.FFFF..
...ffff.ffff..
"""),
 'run0': P("""
....PPPPPPP...
....PPPPPPPP..
....pPPP..PPP.
...ppP.....PP.
...pp......PP.
..pp........PP
..pp........PP
.pp.........PP
.pp........FFF
pp.........FFF
FFF.........ff
ff............
"""),
 'run1': P("""
....PPPPPPP...
....PPPPPPP...
....pPPPPPPP..
....pPP.PPPPP.
....pPP...PPP.
....pPP....PP.
....pPP...PP..
....pPP..FFF..
....pPP..fff..
....pPP.......
...FFFF.......
...ffff.......
"""),
 'run2': P("""
....PPPPPPP...
...PPPPPPPPp..
...PPPP..ppp..
...PPP....pp..
..PP......pp..
..PP.......pp.
.PP........pp.
.PP.........pp
PP..........pp
PP.........FFF
FF.........fff
F.............
"""),
 'run3': P("""
....PPPPPPP...
....PPPPPPP...
....PPPPpppp..
....PPP.ppppp.
....PPP...ppp.
....PPP....pp.
....PPP...pp..
....PPP..FFF..
....PPP..fff..
....PPP.......
...FFFF.......
...ffff.......
"""),
 'tuck': P("""
....PPPPPPP...
....PPPPPPPP..
....pPPPPPPPP.
....pPP..PPPP.
....ppP...PPP.
.....pp..PP...
.....pp.FFF...
....FFF.fff...
....fff.......
..............
..............
..............
"""),
 'fall': P("""
....PPPPPPP...
....PPPPPPP...
....pPPP.PPP..
...ppP....PP..
...pp.....PP..
..pp.......PP.
..pp.......PP.
.FFF.......FFF
.fff.......fff
..............
..............
..............
"""),
}
SLIDE_BODY = P("""
..........jJJJJZJKJ.....
.........jjJJJJZJJJJ....
..PPPPPPPPpjJJJJZJJJ....
FPPPPPPPPPPjjjjjZjjj....
FfpppppppPP.............
""")

def blank():
    return [['.'] * FW for _ in range(FH)]

def stamp(g, part, x, y):
    for j, row in enumerate(part):
        for i, ch in enumerate(row):
            if ch != '.' and 0 <= y + j < FH and 0 <= x + i < FW:
                g[y + j][x + i] = ch

NINJA_MAP = {'J': 'N', 'j': 'n', 'K': 'M', 'Z': 'W', 'P': 'N', 'p': 'n', 'F': 'D', 'f': 'd'}

def frame(name, girl, ninja):
    g = blank()
    run = name.startswith('run')
    bob = {'run0': 1, 'run2': 1, 'idle1': 1}.get(name, 0)
    sway = 1 if name in ('run1', 'run3', 'jumpDown', 'idle1') else 0
    if name == 'slide':
        stamp(g, SLIDE_BODY, 0, 25)
        if ninja:
            stamp(g, NSCARF_TAIL[0], 2, 22)
        stamp(g, HOOD if ninja else HEAD, 14, 21)
        if girl == 'victoria' or ninja:
            stamp(g, (NPONY if ninja else PONY)[1], 11, 21)
        else:
            stamp(g, BACKHAIR, 11, 24)
        if ninja:
            for row in g:
                for i, ch in enumerate(row): row[i] = NINJA_MAP.get(ch, ch)
        return g
    hy = 3 + bob
    # behind the body
    if ninja:
        stamp(g, KATANA, 7, 12 + bob)
        stamp(g, NSCARF_TAIL[sway], 1, 13 + bob)
        stamp(g, NPONY[sway], 4, hy + 2)
    elif girl == 'victoria':
        stamp(g, PONY[sway], 3, hy + 1)
        stamp(g, BAG, 6, 13 + bob)
    else:
        stamp(g, BACKHAIR, 5, hy + 5)
    legs = {'idle0': 'stand', 'idle1': 'stand', 'jumpUp': 'tuck', 'jumpDown': 'fall', 'attack': 'stand'}.get(name, name)
    lg = [r for r in LEGS[legs]]
    if ninja:  # shin wraps
        lg = [''.join('W' if (k in (5, 6) and ch in 'Pp') else ch for ch in r) for k, r in enumerate(lg)]
    stamp(g, lg, 5, 20)
    stamp(g, NTORSO if ninja else TORSO, 8, 13 + bob)
    stamp(g, NECK, 12, 12 + bob)
    if girl == 'friend' and not ninja:
        stamp(g, SCARF, 8, 12 + bob)
    arm = {'run0': 'back', 'run1': 'down', 'run2': 'fwd', 'run3': 'down', 'jumpUp': 'up', 'jumpDown': 'back', 'attack': 'attack'}.get(name, 'down')
    part, ax, ay = ARM[arm]
    stamp(g, part, ax, ay + bob)
    if name == 'attack' and not ninja:
        stamp(g, CARD, 18, 13)
    if name == 'attack' and ninja:
        stamp(g, P("kkkkk"), 18, 14); stamp(g, P("ggggg"), 18, 15)
    stamp(g, HOOD if ninja else HEAD, 7, hy)
    if ninja:
        for row in g:
            for i, ch in enumerate(row): row[i] = NINJA_MAP.get(ch, ch)
    return g

# ---------------- palettes ----------------
COMMON = {'e': '#1d1a2e', 'm': '#c8616b', 'U': '#3a8dff', 'u': '#ffffff', 'g': '#7d8496', 'k': '#e6edf5', 'r': '#5a3a1a', 'D': '#26222e', 'd': '#121016'}
LOOKS = {
  'victoria': {'H': '#f0c75e', 'L': '#fff1a8', 'h': '#b8862e', 'S': '#f6cfae', 's': '#dca383', 'b': '#ff9a9a',
               'J': '#3b3f8f', 'j': '#262a63', 'K': '#6a72d6', 'Z': '#ff4f8b', 'P': '#8fb8ec', 'p': '#5f86c0',
               'F': '#f7f7f7', 'f': '#ff4f8b', 'B': '#21b8a0', 'c': '#6ff0d6',
               'N': '#2a2450', 'n': '#16122e', 'M': '#4a4290', 'T': '#ff3b6b', 'Y': '#ff3b6b', 'W': '#ffd84a'},
  'friend':   {'H': '#b9763d', 'L': '#e8b07a', 'h': '#7e4c22', 'S': '#eebf98', 's': '#cf9873', 'b': '#ff8f86',
               'J': '#f2efe6', 'j': '#c9c2b0', 'K': '#ffffff', 'Z': '#36c6f0', 'P': '#2b3a6e', 'p': '#1a2448',
               'F': '#ff8a3d', 'f': '#ffffff', 'C': '#a64dff', 'x': '#6f2bb8',
               'N': '#e9e9f4', 'n': '#b3b3cc', 'M': '#ffffff', 'T': '#a64dff', 'Y': '#36c6f0', 'W': '#a64dff'},
}

def hexrgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def render(girl):
    pal = {**COMMON, **LOOKS[girl]}
    sheet = Image.new('RGBA', (FW * len(COLS), FH * 2), (0, 0, 0, 0))
    for row, ninja in enumerate((False, True)):
        for col, name in enumerate(COLS):
            g = frame(name, girl, ninja)
            img = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
            for y in range(FH):
                for x in range(FW):
                    ch = g[y][x]
                    if ch != '.':
                        img.putpixel((x, y), hexrgb(pal[ch]) + (255,))
            # selective outline: darkened copy of the neighbouring colour
            out = img.copy()
            for y in range(FH):
                for x in range(FW):
                    if img.getpixel((x, y))[3]: continue
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < FW and 0 <= ny < FH and img.getpixel((nx, ny))[3]:
                            r, gg, b, _ = img.getpixel((nx, ny))
                            out.putpixel((x, y), (int(r * .28) + 8, int(gg * .22) + 6, int(b * .3) + 14, 255)); break
            sheet.paste(out, (col * FW, row * FH))
    return sheet

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
    root.mkdir(parents=True, exist_ok=True)
    for girl in LOOKS:
        render(girl).save(root / f'{girl}.png')
        print('wrote', root / f'{girl}.png')
