#!/usr/bin/env python3
"""Pixel-art sprite sheet for Kaos-trikken, the boss: the new light-blue tram transformed into a mechanoid.

Head = the tram's front (dark raked windscreen as a visor, «KAOS» on the destination display, the blue
nose with two glowing red ring lights as evil eyes, the coupler as a jaw). Torso = a tram section with the
dark window band and a door with yellow handrails as the chest. Arms and legs = tram sections and bogies,
wheels as knees, hands and feet. Inspiration: inspiration/nytrikk det onde øyet.jpg, inspiration/vehicles/new tram/.

Sheet: 4 frames of 96 × 96 in one row: idle0 idle1 attack hit. Base on the bottom row, centred on x = 48.
Usage: python3 tools/sprites/boss.py  → assets/sprites/kaostrikken.png
"""
from pathlib import Path
from PIL import Image, ImageDraw

C = 96
FRAMES = ['idle0', 'idle1', 'attack', 'hit']
COL = dict(
    blue='#3fa3e0', blue_hi='#86c9f1', blue_lo='#2a7fb8', blue_dk='#1f5f8c',
    black='#1c2027', glass='#252b34', shine='#5d6c7a', grey='#454b56', steel='#8b919c', steel_dk='#30343d',
    rail='#f2c200', amber='#ffb21a', red='#ff2a2a', red_dk='#a80d1a', red_glow='#ff8a8a', white='#ffffff', mouth='#ff7a1a',
)
FONT = {'K': ['101', '101', '110', '101', '101'], 'A': ['010', '101', '111', '101', '101'],
        'O': ['111', '101', '101', '101', '111'], 'S': ['111', '100', '111', '001', '111']}


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def frame(name):
    im = Image.new('RGBA', (C, C), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    R = lambda x, y, w, h, c: d.rectangle([x, y, x + w - 1, y + h - 1], fill=rgb(COL[c]))
    attack, hit = name == 'attack', name == 'hit'
    sway = 1 if name == 'idle1' else 0
    arms_up = attack

    def wheel(cx, cy, r=4):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb(COL['steel_dk']))
        d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], fill=rgb(COL['steel']))
        d.point((cx, cy), fill=rgb(COL['black']))

    # ---- legs: blue thigh section, bogie shin, wheel knee and wheel feet
    for lx in (27, 55):
        R(lx, 64, 14, 12, 'blue'); R(lx, 64, 14, 2, 'blue_hi'); R(lx, 72, 14, 4, 'blue_lo')
        R(lx + 2, 76, 10, 12, 'steel_dk'); R(lx + 3, 78, 8, 2, 'grey')
        wheel(lx + 7, 77, 4)                                   # knee
        R(lx - 3, 88, 20, 5, 'steel_dk')                       # foot: bogie frame …
        wheel(lx + 1, 92, 3); wheel(lx + 13, 92, 3)            # … on two wheels
    # ---- pelvis with hazard handrail stripes
    R(25, 58, 46, 8, 'grey'); R(25, 58, 46, 1, 'steel')
    for k in range(5):
        R(30 + k * 8, 60, 4, 4, 'rail')
    # ---- arms (tram sections) and wheel-claw hands
    for side in (-1, 1):
        sx = 48 + side * 39
        if arms_up:  # raised, reaching forward
            R(sx - 7, 12 + sway, 14, 22, 'blue'); R(sx - 7, 16, 14, 8, 'black'); R(sx - 7, 12, 14, 2, 'blue_hi')
            R(sx - 5, 6, 10, 7, 'steel_dk'); wheel(sx - 3, 6, 3); wheel(sx + 3, 6, 3)
        else:
            R(sx - 7, 26 + sway, 14, 26, 'blue'); R(sx - 7, 30 + sway, 14, 9, 'black'); R(sx - 7, 26 + sway, 14, 2, 'blue_hi')
            R(sx - 7, 46 + sway, 14, 6, 'blue_lo')
            R(sx - 5, 52 + sway, 10, 6, 'steel_dk'); wheel(sx - 3, 59 + sway, 3); wheel(sx + 3, 59 + sway, 3)
        # shoulder joint
        R(sx - 4 - side * 8, 27, 8, 5, 'grey')
    # ---- torso: a tram section with a door as the chest
    R(21, 24, 54, 36, 'blue'); R(21, 24, 54, 2, 'blue_hi'); R(21, 54, 54, 6, 'blue_lo')
    R(21, 28, 54, 16, 'black')                                  # dark window band
    for wx in (23, 32, 58, 66):
        R(wx, 30, 8, 11, 'glass'); d.line([wx + 5, 31, wx + 2, 39], fill=rgb(COL['shine']))
        if attack:
            R(wx + 1, 37, 6, 3, 'red_dk')                       # fiery glow inside when attacking
    R(40, 27, 16, 31, 'grey'); R(41, 29, 6, 27, 'glass'); R(49, 29, 6, 27, 'glass')   # chest door
    R(43, 31, 1, 22, 'rail'); R(51, 31, 1, 22, 'rail')          # yellow handrails
    # ---- head: the tram front (black top with the raked windscreen as a visor, blue nose with the red ring lights)
    hx, hy, hw = 25, 0 + sway, 46
    R(hx + 4, hy, hw - 8, 7, 'black')                           # destination display
    tx = hx + 4 + (hw - 8 - 19) // 2
    for ch in 'KAOS':
        for j, row in enumerate(FONT[ch]):
            for i, bit in enumerate(row):
                if bit == '1':
                    d.point((tx + i, hy + 1 + j), fill=rgb(COL['amber']))
        tx += 5
    d.polygon([(hx, hy + 7), (hx + hw - 1, hy + 7), (hx + hw - 4, hy + 18), (hx + 3, hy + 18)], fill=rgb(COL['glass']))   # visor
    for k in (12, 16):
        d.line([hx + k, hy + 8, hx + k - 4, hy + 17], fill=rgb(COL['shine']))
    R(hx, hy + 18, hw, 10, 'blue'); R(hx, hy + 18, hw, 1, 'blue_hi'); R(hx, hy + 26, hw, 2, 'blue_lo')   # blue nose
    for ex in (hx + 4, hx + hw - 13):                           # evil eyes: the red ring lights
        ey = hy + 19
        if hit:
            R(ex, ey + 3, 9, 2, 'red')                          # squinting
            continue
        glow = 'red_glow' if (name == 'idle1' or attack) else 'red'
        d.ellipse([ex - 1, ey - 1, ex + 9, ey + 7], fill=rgb(COL['red_dk']))      # halo
        d.ellipse([ex, ey, ex + 8, ey + 6], outline=rgb(COL[glow]), fill=rgb(COL['black']))   # the red ring
        R(ex + 3, ey + 2, 3, 3, 'red')                          # glowing pupil
    jx = hx + hw // 2                                            # jaw: the coupler, open and glowing when attacking
    if attack:
        R(jx - 7, hy + 24, 14, 7, 'black'); R(jx - 5, hy + 26, 10, 4, 'mouth')
    else:
        R(jx - 6, hy + 24, 12, 3, 'steel_dk'); R(jx - 5, hy + 25, 10, 1, 'steel')
    # ---- selective outline
    px = im.load()
    out = im.copy(); po = out.load()
    for y in range(C):
        for x in range(C):
            if px[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < C and 0 <= ny < C and px[nx, ny][3]:
                    r, g, b, _ = px[nx, ny]
                    po[x, y] = (int(r * .22) + 10, int(g * .22) + 10, int(b * .28) + 16, 255)
                    break
    if hit:  # flash: brighten everything
        for y in range(C):
            for x in range(C):
                r, g, b, a = po[x, y]
                if a:
                    po[x, y] = (min(255, r + 110), min(255, g + 110), min(255, b + 110), a)
    return out


if __name__ == '__main__':
    sheet = Image.new('RGBA', (C * len(FRAMES), C), (0, 0, 0, 0))
    for i, n in enumerate(FRAMES):
        sheet.paste(frame(n), (i * C, 0))
    out = Path(__file__).resolve().parents[2] / 'assets' / 'sprites' / 'kaostrikken.png'
    sheet.save(out)
    print('wrote', out, sheet.size)
