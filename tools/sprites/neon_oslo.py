#!/usr/bin/env python3
"""Low-colour pixel-art Neon Oslo cars and floating sauna.

Usage: python3 tools/sprites/neon_oslo.py
"""

import json
from pathlib import Path
from PIL import Image


CELL_W = 112
CELL_H = 64

C = {
    'ink': (18, 15, 34, 255),
    'purple': (52, 31, 76, 255),
    'purple_hi': (112, 61, 128, 255),
    'silver': (168, 176, 196, 255),
    'silver_hi': (222, 225, 232, 255),
    'silver_lo': (91, 99, 122, 255),
    'glass': (22, 48, 62, 255),
    'glass_hi': (64, 137, 151, 255),
    'pink': (255, 43, 214, 255),
    'cyan': (43, 240, 255, 255),
    'yellow': (255, 216, 74, 255),
    'cream': (210, 198, 168, 255),
    'white': (238, 237, 224, 255),
    'wood': (72, 48, 52, 255),
    'wood_lo': (43, 32, 43, 255),
    'wood_hi': (116, 76, 65, 255),
}


class Canvas:
    def __init__(self):
        self.p = [[None] * CELL_W for _ in range(CELL_H)]

    def set(self, x, y, name):
        if 0 <= x < CELL_W and 0 <= y < CELL_H:
            self.p[y][x] = C[name]

    def rect(self, x0, y0, x1, y1, name):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, name)

    def h(self, x0, x1, y, name):
        self.rect(x0, y, x1, y, name)

    def v(self, x, y0, y1, name):
        self.rect(x, y0, x, y1, name)

    def poly(self, points, name):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            intersections = []
            for i, (x1, y1) in enumerate(points):
                x2, y2 = points[(i + 1) % len(points)]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    t = (y - y1) / (y2 - y1)
                    intersections.append(x1 + t * (x2 - x1))
            intersections.sort()
            for i in range(0, len(intersections) - 1, 2):
                self.rect(int(intersections[i]), y, int(intersections[i + 1]), y, name)

    def wheel(self, cx, cy, r=7):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                dx, dy = x - cx, y - cy
                d = dx * dx + dy * dy
                if d <= r * r:
                    self.set(x, y, 'ink')
                if d <= (r - 2) * (r - 2):
                    self.set(x, y, 'silver_lo')
        for y in range(cy - 4, cy + 5):
            for x in range(cx - 4, cx + 5):
                dx, dy = x - cx, y - cy
                if dx * dx + dy * dy <= 13:
                    self.set(x, y, 'silver_hi')
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)):
            self.set(cx + dx, cy + dy, 'ink')
        self.set(cx, cy, 'cyan')

    def outline(self):
        add = []
        for y in range(CELL_H):
            for x in range(CELL_W):
                if self.p[y][x] is not None:
                    continue
                if any(0 <= x + dx < CELL_W and 0 <= y + dy < CELL_H
                       and self.p[y + dy][x + dx] is not None
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    add.append((x, y))
        for x, y in add:
            self.set(x, y, 'ink')

    def image(self):
        im = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
        for y in range(CELL_H):
            for x in range(CELL_W):
                if self.p[y][x] is not None:
                    im.putpixel((x, y), self.p[y][x])
        box = im.getbbox()
        crop = im.crop(box)
        placed = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
        placed.alpha_composite(crop, ((CELL_W - crop.width) // 2, CELL_H - crop.height))
        return placed


def countach():
    cv = Canvas()
    # Extremely low wedge: nose, roof and tail follow the Countach silhouette.
    cv.poly([(8, 38), (18, 31), (32, 24), (48, 20), (67, 21),
             (84, 29), (101, 34), (104, 40), (99, 44),
             (14, 44), (7, 42)], 'ink')
    cv.poly([(10, 37), (20, 32), (34, 25), (47, 21), (65, 22),
             (81, 30), (96, 34), (101, 39), (96, 41),
             (16, 41), (9, 40)], 'purple')
    cv.poly([(17, 33), (34, 26), (45, 22), (62, 22), (73, 28),
             (82, 33), (28, 33)], 'purple_hi')
    cv.h(18, 62, 21, 'pink')
    cv.h(62, 79, 27, 'pink')
    cv.h(82, 101, 35, 'pink')
    # dark tinted canopy, sharply sloped windscreen and scissor-door window
    cv.poly([(40, 23), (49, 22), (64, 23), (70, 28), (38, 28)], 'glass')
    cv.h(43, 60, 23, 'glass_hi')
    cv.poly([(72, 29), (79, 32), (82, 34), (69, 34)], 'glass')
    cv.v(69, 28, 35, 'ink')
    # wedge character lines
    cv.poly([(12, 35), (18, 32), (31, 25), (34, 26), (21, 33), (16, 37)], 'purple_hi')
    cv.poly([(34, 28), (70, 28), (72, 30), (34, 31)], 'purple')
    cv.poly([(28, 34), (62, 34), (60, 38), (31, 38)], 'pink')
    cv.v(64, 33, 40, 'ink')
    cv.poly([(66, 34), (82, 34), (88, 36), (81, 38), (67, 37)], 'purple_hi')
    # signature black side intake and small hexagonal vents
    cv.poly([(55, 32), (70, 32), (66, 39), (48, 39)], 'ink')
    cv.h(50, 58, 34, 'purple_hi')
    cv.h(36, 43, 35, 'ink')
    cv.h(37, 42, 36, 'pink')
    # front/rear and lower edge
    cv.h(10, 19, 39, 'cyan')
    cv.rect(96, 36, 101, 38, 'pink')
    cv.poly([(18, 41), (94, 41), (98, 44), (15, 44)], 'ink')
    cv.h(15, 94, 42, 'cyan')
    cv.h(21, 91, 43, 'cyan')
    cv.wheel(27, 43, 7)
    cv.wheel(86, 43, 7)
    cv.h(34, 79, 44, 'ink')
    cv.outline()
    return cv.image()


def testarossa():
    cv = Canvas()
    # The Testarossa is long and low, with a flat sloping nose and broad haunch.
    cv.poly([(9, 38), (22, 30), (42, 25), (67, 25),
             (87, 30), (101, 36), (103, 41), (97, 44),
             (15, 44), (8, 41)], 'ink')
    cv.poly([(11, 37), (23, 31), (43, 26), (66, 26),
             (86, 31), (99, 36), (100, 40), (96, 42),
             (17, 42), (10, 40)], 'pink')
    cv.poly([(16, 33), (31, 27), (42, 24), (57, 24),
             (65, 27), (72, 32), (22, 32)], 'pink')
    cv.h(16, 57, 24, 'cyan')
    cv.h(57, 65, 27, 'cyan')
    cv.h(72, 99, 36, 'cyan')
    # side glass
    cv.poly([(43, 27), (55, 26), (63, 28), (68, 32), (41, 32)], 'glass')
    cv.h(46, 53, 27, 'glass_hi')
    cv.v(64, 27, 33, 'ink')
    cv.poly([(69, 29), (77, 31), (82, 34), (68, 34)], 'glass')
    cv.h(70, 76, 31, 'glass_hi')
    # side character: broad white haunch over dark lower belt
    cv.poly([(25, 34), (52, 34), (74, 33), (91, 37), (94, 40),
             (20, 40), (19, 37)], 'pink')
    cv.h(20, 96, 41, 'cyan')
    cv.h(24, 93, 43, 'ink')
    # signature long side strakes
    cv.rect(47, 34, 82, 40, 'ink')
    for y in range(35, 40):
        cv.h(50, 79, y, 'silver_lo')
    cv.h(52, 78, 35, 'glass_hi')
    cv.h(54, 80, 38, 'pink')
    cv.h(50, 58, 36, 'cyan')
    cv.v(45, 33, 40, 'ink')
    # lamps and tail
    cv.rect(96, 35, 100, 37, 'yellow')
    cv.rect(12, 35, 16, 37, 'pink')
    cv.h(11, 20, 39, 'cyan')
    cv.wheel(29, 43, 7)
    cv.wheel(87, 43, 7)
    cv.h(36, 80, 44, 'ink')
    cv.outline()
    return cv.image()


def sauna():
    cv = Canvas()
    # Wide floating pontoon.
    cv.poly([(12, 50), (20, 47), (91, 47), (100, 51),
             (96, 55), (16, 55)], 'ink')
    cv.rect(18, 49, 94, 52, 'wood_lo')
    cv.h(22, 90, 50, 'wood_hi')
    cv.h(15, 97, 53, 'cyan')
    cv.h(21, 92, 54, 'pink')
    cv.h(28, 84, 56, 'ink')
    cv.h(35, 77, 57, 'wood_lo')
    # Cabin: dark walls, cream trim and one narrow rectangular window.
    cv.rect(20, 24, 88, 48, 'ink')
    cv.rect(22, 26, 86, 47, 'wood')
    cv.rect(24, 28, 84, 45, 'wood_lo')
    cv.v(24, 28, 46, 'wood_hi')
    cv.v(84, 28, 46, 'wood_hi')
    cv.h(24, 84, 46, 'wood_hi')
    cv.h(22, 86, 26, 'cream')
    cv.h(22, 86, 27, 'pink')
    # Strong dark frame around a narrow rectangular window.
    cv.rect(36, 31, 69, 43, 'ink')
    cv.rect(39, 33, 66, 41, 'glass')
    cv.rect(41, 34, 63, 39, 'glass_hi')
    cv.h(43, 61, 40, 'cyan')
    cv.v(39, 33, 41, 'cyan')
    cv.v(66, 33, 41, 'pink')
    cv.rect(31, 29, 34, 45, 'wood_hi')
    cv.rect(71, 29, 74, 45, 'wood_hi')
    cv.h(30, 75, 44, 'cream')
    # Chimney on roof.
    cv.rect(71, 8, 77, 25, 'ink')
    cv.rect(73, 10, 75, 24, 'steel_hi' if 'steel_hi' in C else 'cream')
    cv.rect(69, 7, 79, 9, 'ink')
    cv.h(71, 77, 7, 'cyan')
    cv.rect(72, 6, 76, 6, 'pink')
    # Strong colored roof and safety rail.
    cv.h(18, 92, 22, 'ink')
    cv.h(20, 90, 23, 'cyan')
    cv.v(18, 22, 27, 'cyan')
    cv.v(92, 22, 27, 'pink')
    cv.h(18, 92, 27, 'cream')
    cv.h(18, 92, 48, 'yellow')
    for x in (18, 31, 44, 57, 70, 92):
        cv.v(x, 27, 48, 'cyan' if x % 2 == 0 else 'pink')
    cv.v(92, 27, 48, 'pink')
    cv.h(19, 91, 50, 'yellow')
    # Ladder and right-side railing.
    cv.v(88, 49, 58, 'cyan')
    cv.v(94, 49, 58, 'pink')
    cv.h(88, 94, 52, 'yellow')
    cv.h(88, 94, 56, 'yellow')
    cv.outline()
    return cv.image()


def main():
    root = Path(__file__).resolve().parents[2]
    out = root / 'assets' / 'sprites'
    out.mkdir(parents=True, exist_ok=True)
    names = (
        ('lambo_neon', countach()),
        ('testarossa_neon', testarossa()),
        ('floating_sauna', sauna()),
    )
    sheet = Image.new('RGBA', (CELL_W, CELL_H * len(names)), (0, 0, 0, 0))
    meta = {}
    for row, (name, im) in enumerate(names):
        box = im.getbbox()
        crop = im.crop(box)
        w, h = crop.width, crop.height
        placed = Image.new('RGBA', (CELL_W, CELL_H), (0, 0, 0, 0))
        placed.alpha_composite(crop, ((CELL_W - w) // 2, CELL_H - h))
        sheet.alpha_composite(placed, (0, row * CELL_H))
        meta[name] = {
            'row': row,
            'frames': 1,
            'fps': 1,
            'w': w,
            'h': h,
            'top': h if name != 'floating_sauna' else 29,
        }
    sheet.save(out / 'neon-oslo.png')
    (out / 'neon-oslo.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote', out / 'neon-oslo.png', sheet.size)
    for name, data in meta.items():
        print(f"  {name:18s} {data['w']:3d} x {data['h']:3d}")


if __name__ == '__main__':
    main()
