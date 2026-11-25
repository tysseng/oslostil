#!/usr/bin/env python3
"""Generate an original waving-tail ghost and matching alpha-shaped glow frames."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
CELL, FRAMES, PAD = 32, 8, 16


def frame(index):
    image = Image.new('RGBA', (CELL, CELL))
    draw = ImageDraw.Draw(image)
    phase = index * math.tau / FRAMES
    upper, lower = [], []
    for x in range(4, 22):
        taper = (x - 4) / 17
        wave = round(math.sin(phase - x * .38) * 3 * (1 - taper))
        centre = 27 + wave - round(taper * 3)
        radius = max(0, round(taper * 4))
        upper.append((x, centre - radius))
        lower.append((x, min(31, centre + radius)))
    draw.polygon(upper + lower[::-1], fill='#71bda0')
    draw.ellipse((14, 15, 27, 29), fill='#71bda0')
    draw.ellipse((15, 15, 26, 27), fill='#d4ffe3')
    draw.polygon([(5, upper[1][1]), (14, 23), (21, 24), (14, 27)],
                 fill='#a4ebc1')
    draw.rectangle((22, 19, 24, 22), fill='#142e31')
    draw.point((24, 19), fill='#ffffff')
    draw.rectangle((25, 24, 26, 25), fill='#498b75')
    return image


def glow(image):
    size = CELL + PAD * 2
    alpha = Image.new('L', (size, size))
    alpha.paste(image.getchannel('A'), (PAD, PAD))
    soft = alpha.filter(ImageFilter.GaussianBlur(6))
    near = alpha.filter(ImageFilter.GaussianBlur(2))
    combined = Image.new('L', (size, size))
    combined.putdata([min(230, round(a * .85 + b * .45))
                      for a, b in zip(soft.getdata(), near.getdata())])
    result = Image.new('RGBA', (size, size), (55, 255, 100, 0))
    result.putalpha(combined)
    return result


if __name__ == '__main__':
    sprites = Image.new('RGBA', (CELL * FRAMES, CELL))
    lights = Image.new('RGBA', ((CELL + PAD * 2) * FRAMES, CELL + PAD * 2))
    for i in range(FRAMES):
        sprite = ImageOps.mirror(frame(i))
        sprites.alpha_composite(sprite, (i * CELL, 0))
        lights.alpha_composite(glow(sprite), (i * (CELL + PAD * 2), 0))
    sprites.save(ROOT / 'ghost.png')
    lights.save(ROOT / 'ghost-light.png')
