#!/usr/bin/env python3
"""Rainbow mode for Automat Victoria (level 2, the glitch): she breaks loose, flies up past the player on a
rubber band and trails a stepped pixel rainbow. Our own design: a plain six-band rainbow ribbon, sparkles
and Victoria's own cheer frames with a pink/cyan glitch split. No cat, nothing copied from other games.

Writes, in assets/sprites/:
  automat-rainbow.png        Victoria flying: 4 frames of 28 × 32 in one row:
                             fly0 fly1 (her cheer frames, arms up) and glitch0 glitch1 (the same with a
                             pink/cyan channel split). Base on the bottom row, cabinet centred on x = 14.
  rainbow-tail.png           the ribbon, drawn by the code as a chain of segments along her past positions.
                             4 cells of 6 × 14 in one row: seg0 seg1 (the same segment, bands 1 px apart:
                             alternate them along the chain and swap every beat for the classic stepped wave),
                             fade0 fade1 (broken-up segments for the last few links of the tail).
                             The band centre is y = 7 in every cell.
  rainbow-tail-light.png     soft glow for one segment, 18 × 26, centre (9, 13); draw with 'screen'
                             at the segment's centre, smooth, no dither.
  rainbow-sparkle.png        4 frames of 7 × 7: a twinkle (dot → plus → star → plus), centre (3, 3).
  rainbow.json               sizes, anchors and frame names.
Usage: python3 tools/sprites/rainbow.py
"""
import json
import random
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
PINK, CYAN = (255, 43, 214), (43, 240, 255)
BANDS = ['#ff3048', '#ff8a1e', '#ffe23a', '#3ee05a', '#2ba8ff', '#8a4bff']   # 2 px each, top to bottom
SEG_W, SEG_H, BAND = 6, 14, 2
FW, FH = 28, 32


def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def silhouette(im, col):
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    px, op = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][3]:
                op[x, y] = col + (255,)
    return out


def segment(dy, broken=0.0, seed=0):
    """One 6-px slice of the ribbon; bands start at y = 1 + dy. broken: share of pixels knocked out."""
    rnd = random.Random(seed)
    im = Image.new('RGBA', (SEG_W, SEG_H), (0, 0, 0, 0))
    px = im.load()
    for i, c in enumerate(BANDS):
        for y in range(BAND):
            for x in range(SEG_W):
                if rnd.random() >= broken:
                    px[x, 1 + dy + i * BAND + y] = rgb(c) + (255,)
    if broken:   # a few glitch pixels drifting off the broken end
        for _ in range(3):
            px[rnd.randrange(SEG_W), rnd.randrange(SEG_H)] = (PINK if rnd.random() < .5 else CYAN) + (255,)
    return im


def tail_sheet():
    cells = [segment(0), segment(1), segment(0, 0.35, 3), segment(1, 0.6, 4)]
    sheet = Image.new('RGBA', (SEG_W * len(cells), SEG_H), (0, 0, 0, 0))
    for i, c in enumerate(cells):
        sheet.alpha_composite(c, (i * SEG_W, 0))
    return sheet


def tail_light():
    w, h = 18, 26
    a = Image.new('L', (w, h), 0)
    px = a.load()
    for y in range(h):
        for x in range(w):
            dx, dy = (x - 8.5) / 9.0, (y - 12.5) / 11.0
            v = max(0.0, 1 - (dx * dx * 0.35 + dy * dy))
            px[x, y] = round(150 * v ** 1.4)
    a = a.filter(ImageFilter.GaussianBlur(1.6))
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ip = im.load()
    for y in range(h):          # the glow takes the band colour of its row (soft rainbow halo)
        band = min(5, max(0, (y - 7) // 2))
        c = rgb(BANDS[band])
        c = tuple(round(c[k] * .6 + 255 * .4) for k in range(3))
        for x in range(w):
            v = a.getpixel((x, y))
            if v:
                ip[x, y] = c + (v,)
    return im


SPARK = [
    ['.......', '.......', '.......', '...W...', '.......', '.......', '.......'],
    ['.......', '.......', '...Y...', '..YWY..', '...Y...', '.......', '.......'],
    ['...Y...', '...Y...', '..YWY..', 'YYWWWYY', '..YWY..', '...Y...', '...Y...'],
    ['.......', '...Y...', '...W...', '.YWWWY.', '...W...', '...Y...', '.......'],
]


def sparkle_sheet():
    cols = {'W': (255, 255, 255), 'Y': (255, 236, 140)}
    sheet = Image.new('RGBA', (7 * len(SPARK), 7), (0, 0, 0, 0))
    px = sheet.load()
    for f, rows in enumerate(SPARK):
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch in cols:
                    px[f * 7 + x, y] = cols[ch] + (255,)
    return sheet


def fly_sheet():
    src = Image.open(ROOT / 'automat.png').convert('RGBA')
    cheer = [src.crop((c * 24, 0, c * 24 + 24, 32)) for c in (4, 5)]
    frames = []
    for m in cheer:                                  # fly0, fly1: her cheer frames, centred on a 28-wide cell
        f = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
        f.alpha_composite(m, (2, 0))
        frames.append(f)
    for i, m in enumerate(cheer):                    # glitch0, glitch1: pink left / cyan right split
        d = 2 if i == 0 else 1
        f = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
        f.alpha_composite(silhouette(m, PINK), (2 - d, 0))
        f.alpha_composite(silhouette(m, CYAN), (2 + d, 0))
        f.alpha_composite(m, (2, 0))
        frames.append(f)
    sheet = Image.new('RGBA', (FW * len(frames), FH), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.alpha_composite(f, (i * FW, 0))
    return sheet


if __name__ == '__main__':
    fly_sheet().save(ROOT / 'automat-rainbow.png')
    tail_sheet().save(ROOT / 'rainbow-tail.png')
    tail_light().save(ROOT / 'rainbow-tail-light.png')
    sparkle_sheet().save(ROOT / 'rainbow-sparkle.png')
    meta = {
        'fly': {'file': 'automat-rainbow.png', 'w': FW, 'h': FH, 'frames': ['fly0', 'fly1', 'glitch0', 'glitch1'],
                'fps': 6, 'anchor': [14, 32], 'tail_anchor': [8, 17],
                'note': 'anchor = base centre; tail_anchor = where the ribbon leaves her (cell px, behind the cabinet)'},
        'tail': {'file': 'rainbow-tail.png', 'w': SEG_W, 'h': SEG_H, 'frames': ['seg0', 'seg1', 'fade0', 'fade1'],
                 'centre_y': 7, 'spacing': SEG_W, 'swap': 'every beat',
                 'note': 'chain of segments along her past positions, every 6 px of path; alternate seg0/seg1 '
                         'along the chain and swap the parity on each beat; the last 2 links use fade0, fade1'},
        'tail_light': {'file': 'rainbow-tail-light.png', 'w': 18, 'h': 26, 'centre': [9, 13], 'blend': 'screen'},
        'sparkle': {'file': 'rainbow-sparkle.png', 'w': 7, 'h': 7, 'frames': 4, 'fps': 12, 'centre': [3, 3]},
    }
    (ROOT / 'rainbow.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote automat-rainbow.png, rainbow-tail.png, rainbow-tail-light.png, rainbow-sparkle.png, rainbow.json')
