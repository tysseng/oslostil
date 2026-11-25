#!/usr/bin/env python3
"""Two original ghost candidates; does not modify the active ghost artwork."""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
FRAMES, PAD = 8, 16


def bedsheet(index):
    image = Image.new('RGBA', (32, 40))
    d = ImageDraw.Draw(image)
    phase = index * math.tau / FRAMES
    sway = round(math.sin(phase) * 2)
    hem = [(x, 33 + round(math.sin(phase - x * .55) * 2))
           for x in range(5, 28, 2)]
    outline = [(5, 29), (8, 20), (9 + sway, 11), (12 + sway, 6),
               (17 + sway, 4), (22 + sway, 6), (25 + sway, 11),
               (26, 22), (28, 30)] + hem[::-1]
    d.polygon(outline, fill='#758f9f')
    d.polygon([(7, 29), (10, 20), (11 + sway, 11), (14 + sway, 7),
               (18 + sway, 6), (22 + sway, 8), (23 + sway, 12),
               (24, 23), (26, 30)] + [(x, y - 1) for x, y in hem[::-1]],
              fill='#e7f3ee')
    d.polygon([(12 + sway, 16), (13 + sway, 22), (10, 32),
               (13, 30), (15, 23)], fill='#b0c9cd')
    d.polygon([(22 + sway, 17), (22, 25), (25, 32), (23, 30),
               (20, 23)], fill='#b0c9cd')
    d.line([(16 + sway, 8), (14 + sway, 11), (13 + sway, 16)],
           fill='#ffffff', width=2)
    d.rectangle((14 + sway, 13, 16 + sway, 17), fill='#19313f')
    d.rectangle((20 + sway, 13, 22 + sway, 17), fill='#19313f')
    d.rectangle((18 + sway, 20, 19 + sway, 23), fill='#607a87')
    return image


def slime(index):
    image = Image.new('RGBA', (24, 29))
    d = ImageDraw.Draw(image)
    phase = index * math.tau / FRAMES
    sway = round(math.sin(phase))
    tail = round(math.sin(phase + 1) * 2)
    dark, coat, trim = '#123e30', '#237b43', '#88ef44'
    # Redrawn at native small resolution: preserve the face, cap and torn coat.
    d.polygon([(8, 15), (11, 13), (16, 13), (18, 15),
               (19, 21), (17, 20), (17, 24), (14, 23),
               (12, 27), (10, 25), (6, 28), (4, 26 + tail),
               (8, 23), (8, 19), (6, 22), (5, 20)], fill=dark)
    d.polygon([(9, 16), (12, 15), (16, 15), (17, 18),
               (15, 19), (15, 23), (12, 25), (10, 23),
               (6, 26 + tail), (10, 21)], fill=coat)
    d.polygon([(10, 14), (12, 17), (15, 14)], fill=trim)
    for y in (20, 23):
        d.point((11, y), fill='#deff7b')
    d.polygon([(8 + sway, 7), (15 + sway, 7), (17, 10),
               (16, 13), (13, 15), (10, 14), (9, 12),
               (7, 11)], fill=dark)
    d.polygon([(10 + sway, 8), (15, 8), (16, 11),
               (14, 13), (11, 13), (10, 11)], fill=trim)
    d.rectangle((10, 9, 12, 11), fill=dark)
    d.rectangle((14, 9, 16, 11), fill=dark)
    d.point((11, 10), fill='#efffc1')
    d.point((15, 10), fill='#efffc1')
    d.line([(11, 13), (14, 13)], fill=dark)
    d.polygon([(7, 4), (9, 2), (15, 2), (17, 4),
               (16, 7), (8, 7)], fill=dark)
    d.rectangle((9, 3, 15, 5), fill=coat)
    d.line([(8, 6), (16, 6)], fill=trim)
    d.polygon([(9, 7), (18, 7), (19, 8), (16, 9),
               (13, 8), (9, 8)], fill=dark)
    d.point((12, 4), fill='#deff7b')
    return image


def light(sprite, color):
    alpha = Image.new('L', (sprite.width + PAD * 2, sprite.height + PAD * 2))
    alpha.paste(sprite.getchannel('A'), (PAD, PAD))
    wide = alpha.filter(ImageFilter.GaussianBlur(6))
    near = alpha.filter(ImageFilter.GaussianBlur(2))
    combined = Image.new('L', alpha.size)
    combined.putdata([min(230, round(a * .85 + b * .45))
                      for a, b in zip(wide.getdata(), near.getdata())])
    image = Image.new('RGBA', alpha.size, color + (0,))
    image.putalpha(combined)
    return image


def write(name, make_frame, color):
    frames = [ImageOps.mirror(make_frame(i)) for i in range(FRAMES)]
    w, h = frames[0].size
    sheet = Image.new('RGBA', (w * FRAMES, h))
    glows = Image.new('RGBA', ((w + PAD * 2) * FRAMES, h + PAD * 2))
    for i, frame in enumerate(frames):
        sheet.alpha_composite(frame, (i * w, 0))
        glows.alpha_composite(light(frame, color), (i * (w + PAD * 2), 0))
    sheet.save(ROOT / f'{name}.png')
    glows.save(ROOT / f'{name}-light.png')
    bounds = [frame.getbbox() for frame in frames]
    metadata = {
        'file': f'{name}.png', 'cell': [w, h], 'row': 0,
        'frames': FRAMES, 'fps': 10,
        'w': max(b[2] for b in bounds) - min(b[0] for b in bounds),
        'h': h - min(b[1] for b in bounds),
        'light': {'file': f'{name}-light.png',
                  'cell': [w + PAD * 2, h + PAD * 2], 'padding': PAD},
        'note': 'Left-facing ghost, bottom-centred cell; separate animated glow follows frame alpha.'
    }
    (ROOT / f'{name}.json').write_text(json.dumps(metadata, indent=2) + '\n')


if __name__ == '__main__':
    write('ghost-bedsheet', bedsheet, (120, 255, 180))
    write('ghost-slime', slime, (100, 255, 25))
