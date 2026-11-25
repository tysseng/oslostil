#!/usr/bin/env python3
"""Native pixel side elevation of the Valkyrien exit pavilion."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from valkyrien_entrance import FONT

ROOT = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'


def house():
    image = Image.new('RGBA', (104, 64))
    d = ImageDraw.Draw(image)
    green, ink = '#174730', '#081e15'
    d.rectangle((2, 47, 101, 63), fill='#383d42')
    d.rectangle((3, 49, 100, 61), fill='#73797b')
    for x in range(4, 101, 16):
        d.rectangle((x + 1, 50, x + 12, 60), fill='#53595c')
        d.rectangle((x + 2, 51, x + 11, 59), fill='#73797b')
        d.line((x + 2, 51, x + 11, 51), fill='#929897')
        d.line((x + 2, 51, x + 2, 59), fill='#929897')
    d.rectangle((1, 46, 102, 48), fill='#a4aaa6')
    d.line((2, 63, 101, 63), fill='#a4aaa6')
    d.rectangle((2, 30, 101, 45), fill=ink)
    for x in range(5, 100, 16):
        d.rectangle((x, 32, min(x + 12, 98), 41), fill='#111d21')
        d.line((x + 1, 33, min(x + 11, 97), 33), fill='#243337')
        d.line((x + 2, 34, min(x + 5, 97), 39), fill='#1b2b30')
    for x in range(3, 102, 16):
        d.rectangle((x, 30, x + 1, 45), fill=green)
        d.line((x, 31, x, 44), fill='#2c6045')
    d.rectangle((1, 43, 102, 45), fill=green)
    d.line((1, 45, 102, 45), fill=ink)
    d.rectangle((1, 16, 102, 29), fill=green)
    d.line((1, 16, 102, 16), fill='#2c6045')
    for x in range(4, 103, 8):
        d.line((x, 17, x, 29), fill=ink)
        d.line((x + 1, 17, x + 1, 28), fill='#285a3e')
    d.rectangle((0, 29, 103, 31), fill=ink)
    d.line((0, 29, 103, 29), fill='#2c6045')
    d.rectangle((19, 7, 84, 15), fill=ink)
    d.rectangle((20, 8, 83, 14), fill='#17221c')
    font = {**FONT, 'G': ['111', '100', '101', '101', '111']}
    for i, letter in enumerate('VALKYRIEN GRILL'):
        if letter == ' ':
            continue
        for y, row in enumerate(font[letter]):
            for x, pixel in enumerate(row):
                if pixel == '1':
                    d.point((24 + i * 4 + x, 9 + y), fill='#e4dfc5')
    for x in (28, 52, 76):
        d.line((x, 4, x, 6), fill=ink)
        d.rectangle((x - 3, 1, x + 3, 3), fill='#27332c')
        d.line((x - 2, 3, x + 2, 3), fill='#f1e2b2')
    return ImageEnhance.Brightness(image).enhance(.85)


def foreground(image):
    image = image.copy()
    d = ImageDraw.Draw(image)
    for x in range(5, 100, 16):
        d.rectangle((x, 32, min(x + 12, 98), 41), fill=(12, 24, 27, 85))
    return image


def lights():
    alpha = Image.new('L', (136, 96))
    d = ImageDraw.Draw(alpha)
    for x in (28, 52, 76):
        d.polygon([(x + 14, 20), (x + 18, 20),
                   (x + 32, 77), (x, 77)], fill=65)
    alpha = alpha.filter(ImageFilter.GaussianBlur(3))
    image = Image.new('RGBA', alpha.size, (255, 235, 182, 0))
    image.putalpha(alpha)
    return image


if __name__ == '__main__':
    image = house()
    image.save(ROOT / 'valkyrien-house.png')
    foreground(image).save(ROOT / 'valkyrien-house-front.png')
    lights().save(ROOT / 'valkyrien-house-light.png')
