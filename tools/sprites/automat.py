#!/usr/bin/env python3
"""Pixel-art sprite sheet for Automat Victoria, the ticket-machine companion.

Based on the real machine (inspiration/automat/): tall dark-blue cabinet, a big blue touch screen
(here it is her face), card reader and ticket tray, plain blue edges and a stainless-steel kick plate. No logos. Drawn directly on the pixel grid with a selective outline.

Sheet: 7 frames of 24 × 32 in one row: idle0 idle1(blink) talk0 talk1 cheer0 cheer1 plain.
'plain' is an ordinary machine on the platform: same style, no face and no arms, the screen shows the ticket menu.
Base on the bottom row, cabinet centred on x = 12.
Usage: python3 tools/sprites/automat.py  → assets/sprites/automat.png
"""
from pathlib import Path
from PIL import Image

FW, FH = 24, 32
FRAMES = ['idle0', 'idle1', 'talk0', 'talk1', 'cheer0', 'cheer1', 'plain']
PAL = {
    'N': '#28338f', 'n': '#1c2468', 'M': '#3b48b4',          # cabinet navy, shadow, highlight
    'S': '#2f66e8', 's': '#1f4cc0', 'L': '#7fb0ff',          # screen, screen shade, screen top bar
    'W': '#ffffff', 'w': '#cfe0ff', 'P': '#10163a',          # white, pale, pupil
    'B': '#ff8fb4', 'm': '#0f1a4a', 'T': '#ff5a7a',          # blush, mouth, tongue
    'K': '#151827', 'R': '#2c3142', 'r': '#555c70',          # slots, card reader, reader light
    'G': '#c3c9cf', 'g': '#8f979f', 'H': '#eef1f4',          # stainless kick plate
    'Y': '#ffe14a',                                          # sparkle
}


def hexrgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def frame(name):
    g = [['.'] * FW for _ in range(FH)]

    def R(x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < FW and 0 <= yy < FH:
                    g[yy][xx] = c

    cheer = name.startswith('cheer')
    plain = name == 'plain'
    hop = 1 if name == 'cheer1' else 0          # little jump when cheering
    y0 = 1 - hop
    # --- arms (behind the cabinet): stubby, raised when cheering
    if plain:
        pass
    elif cheer:
        R(2, y0 + 8, 2, 6, 'N'); R(1, y0 + 6, 2, 3, 'N'); R(1, y0 + 5, 2, 1, 'W')
        R(20, y0 + 8, 2, 6, 'N'); R(21, y0 + 6, 2, 3, 'N'); R(21, y0 + 5, 2, 1, 'W')
    else:
        R(2, y0 + 14, 2, 6, 'n'); R(2, y0 + 20, 2, 1, 'W')
        R(20, y0 + 14, 2, 6, 'n'); R(20, y0 + 20, 2, 1, 'W')
    # --- upper unit (screen head), slightly wider than the cabinet
    R(3, y0, 18, 17, 'N')
    R(3, y0, 18, 1, 'M')                       # top edge highlight
    R(3, y0, 1, 17, 'n')                       # left shade
    R(20, y0 + 1, 1, 16, 'n')                  # blue edge (no side light strip: we only see the front)
    # screen = face
    R(5, y0 + 2, 11, 11, 'S')
    R(5, y0 + 2, 11, 1, 'L')                   # status bar
    R(5, y0 + 12, 11, 1, 's')
    if plain:  # ticket menu instead of a face
        R(6, y0 + 4, 7, 1, 'W')                # «Hvor skal du reise?»
        R(6, y0 + 6, 4, 1, 'w')
        for (bx, by) in ((6, 8), (11, 8), (6, 10), (11, 10)):
            R(bx, y0 + by, 4, 1, 'w')          # destination buttons
    else:
        # eyes
        if name == 'idle1':                        # blink
            R(7, y0 + 6, 2, 1, 'P'); R(12, y0 + 6, 2, 1, 'P')
        elif cheer:                                # happy ^ ^ eyes
            g[y0 + 6][7] = 'W'; g[y0 + 5][8] = 'W'; g[y0 + 6][9] = 'W'
            g[y0 + 6][11] = 'W'; g[y0 + 5][12] = 'W'; g[y0 + 6][13] = 'W'
        else:
            R(7, y0 + 5, 2, 3, 'W'); R(12, y0 + 5, 2, 3, 'W')
            R(8, y0 + 6, 1, 2, 'P'); R(13, y0 + 6, 1, 2, 'P')
        # blush
        g[y0 + 9][6] = 'B'; g[y0 + 9][14] = 'B'
        # mouth
        if name == 'talk0':
            R(9, y0 + 9, 3, 2, 'm'); g[y0 + 10][10] = 'T'
        elif name == 'talk1':
            R(9, y0 + 10, 3, 1, 'm')
        elif cheer:
            R(8, y0 + 9, 5, 1, 'm'); R(9, y0 + 10, 3, 1, 'm'); g[y0 + 10][10] = 'T'
        else:                                      # small smile
            g[y0 + 9][8] = 'm'; R(9, y0 + 10, 3, 1, 'm'); g[y0 + 9][12] = 'm'
    # «Billetter» label (white text lines) and the card reader on the right
    R(17, y0 + 2, 2, 1, 'W'); R(17, y0 + 4, 2, 1, 'w')
    R(16, y0 + 7, 3, 5, 'R'); R(17, y0 + 8, 1, 3, 'K'); g[y0 + 11][18] = 'r'
    # ticket tray
    R(7, y0 + 14, 9, 2, 'K'); R(7, y0 + 14, 9, 1, 'R')
    # --- lower cabinet
    R(4, y0 + 17, 16, 10, 'N')
    R(4, y0 + 17, 16, 1, 'n')                  # shadow under the head
    R(4, y0 + 17, 1, 10, 'n')
    R(6, y0 + 20, 5, 1, 'W'); R(6, y0 + 22, 4, 1, 'w')   # «Billetter / Tickets» lines
    R(17, y0 + 19, 1, 4, 'M')                  # door handle
    # --- stainless kick plate
    R(4, y0 + 27, 16, 4 + hop, 'G')
    R(4, y0 + 27, 16, 1, 'H')
    R(4, y0 + 27, 1, 4 + hop, 'g')
    # cheering sparkles
    if cheer:
        for (sx, sy) in ((0, 1), (22, 2)) if name == 'cheer0' else ((1, 3), (21, 0)):
            if 0 <= sy < FH:
                g[sy][sx] = 'Y'
    return g


def render():
    sheet = Image.new('RGBA', (FW * len(FRAMES), FH), (0, 0, 0, 0))
    for c, name in enumerate(FRAMES):
        g = frame(name)
        img = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
        for y in range(FH):
            for x in range(FW):
                if g[y][x] != '.':
                    img.putpixel((x, y), hexrgb(PAL[g[y][x]]))
        out = img.copy()  # selective outline: darkened copy of the neighbouring colour
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
        sheet.paste(out, (c * FW, 0))
    return sheet


if __name__ == '__main__':
    out = Path(__file__).resolve().parents[2] / 'assets' / 'sprites' / 'automat.png'
    render().save(out)
    print('wrote', out)
