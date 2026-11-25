#!/usr/bin/env python3
"""Native pixel entrance artwork, at the same one-pixel scale as the girls."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
PAD = 64
FONT = {
    'V': ['101', '101', '101', '101', '010'],
    'A': ['010', '101', '111', '101', '101'],
    'L': ['100', '100', '100', '100', '111'],
    'K': ['101', '101', '110', '101', '101'],
    'Y': ['101', '101', '010', '010', '010'],
    'R': ['110', '101', '110', '101', '101'],
    'I': ['111', '010', '010', '010', '111'],
    'E': ['111', '100', '110', '100', '111'],
    'N': ['101', '111', '111', '111', '101'],
}


def entrance():
    image = Image.new('RGBA', (64, 64))
    d = ImageDraw.Draw(image)
    green, ink = '#226646', '#0b2a1c'
    # Flat concrete walls, 17 pixels high like the street trashcan.
    for x in (5, 51):
        d.rectangle((x, 47, x + 7, 63), fill='#383d42')
        d.rectangle((x + 1, 49, x + 6, 61), fill='#73797b')
        d.line((x + 2, 50, x + 2, 60), fill='#929897')
        d.rectangle((x - 1, 46, x + 8, 48), fill='#a4aaa6')
        d.line((x, 63, x + 7, 63), fill='#a4aaa6')
    d.rectangle((13, 48, 50, 63), fill='#171c1e')
    for x in range(15, 50, 4):
        d.line((x, 49, x, 63), fill='#343b3e')
        d.line((x + 1, 49, x + 1, 63), fill='#232a2d')
    for y in (48, 59):
        d.line((13, y, 50, y), fill='#3d4548')
        d.line((13, y + 1, 50, y + 1), fill='#252c2f')
    for x in (8, 53):
        d.rectangle((x, 23, x + 2, 45), fill=ink)
        d.line((x + 1, 24, x + 1, 44), fill='#4aa874')
        d.rectangle((x - 1, 42, x + 3, 45), fill=green)
        d.line((x - 1, 45, x + 3, 45), fill=ink)
    # Sign lower edge at y=25 leaves 38 pixels for 32-pixel girls.
    d.rectangle((6, 16, 57, 25), fill=ink)
    d.rectangle((7, 17, 56, 24), fill=green)
    d.line((7, 17, 56, 17), fill='#4aa874')
    for i, letter in enumerate('VALKYRIEN'):
        for y, row in enumerate(FONT[letter]):
            for x, pixel in enumerate(row):
                if pixel == '1':
                    d.point((14 + i * 4 + x, 19 + y), fill='#e4ead8')
    d.line([(9, 16), (24, 10), (39, 10), (54, 16)], fill=ink, width=2)
    d.ellipse((23, 0, 40, 17), fill='#214493')
    d.ellipse((26, 3, 37, 14), fill='#ffffff')
    d.rectangle((28, 6, 35, 7), fill='#214493')
    d.rectangle((31, 7, 32, 12), fill='#214493')
    image = ImageEnhance.Brightness(image).enhance(.85)
    d = ImageDraw.Draw(image)
    for x in (9, 54):
        d.rectangle((x - 1, 14, x + 1, 16), fill='#173e2b')
        d.ellipse((x - 3, 8, x + 3, 14), fill='#b9b69b')
        d.ellipse((x - 2, 9, x + 2, 13), fill='#fff2c9')
    return image


def glow():
    alpha = Image.new('L', (64 + PAD * 2, 64 + PAD * 2))
    d = ImageDraw.Draw(alpha)
    for x in (9, 54):
        d.ellipse((x - 8 + PAD, 3 + PAD, x + 8 + PAD, 19 + PAD), fill=255)
    soft = alpha.filter(ImageFilter.GaussianBlur(24))
    near = alpha.filter(ImageFilter.GaussianBlur(8))
    combined = Image.new('L', alpha.size)
    combined.putdata([min(220, round(a * .85 + b * .6))
                      for a, b in zip(soft.getdata(), near.getdata())])
    image = Image.new('RGBA', alpha.size, (255, 232, 170, 0))
    image.putalpha(combined)
    return image


if __name__ == '__main__':
    entrance().save(ROOT / 'valkyrien-entrance.png')
    glow().save(ROOT / 'valkyrien-entrance-light.png')
