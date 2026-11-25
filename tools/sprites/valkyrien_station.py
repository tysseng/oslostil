#!/usr/bin/env python3
"""Original native-pixel station masonry, enamel sign and period advertisements."""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
FONT = {
    'V': ['11011', '11011', '11011', '11011', '11011', '01110', '00100'],
    'A': ['01110', '11011', '11011', '11111', '11011', '11011', '11011'],
    'L': ['11000', '11000', '11000', '11000', '11000', '11000', '11111'],
    'K': ['11011', '11011', '11110', '11100', '11110', '11011', '11011'],
    'Y': ['11011', '11011', '01110', '00100', '00100', '00100', '00100'],
    'R': ['11110', '11011', '11011', '11110', '11100', '11010', '11011'],
    'I': ['11111', '00100', '00100', '00100', '00100', '00100', '11111'],
    'E': ['11111', '11000', '11000', '11110', '11000', '11000', '11111'],
    'P': ['11110', '11011', '11011', '11110', '11000', '11000', '11000'],
    'S': ['01111', '11000', '11000', '01110', '00011', '00011', '11110'],
}


def sign():
    image = Image.new('RGBA', (104, 15), '#36382f')
    d = ImageDraw.Draw(image)
    d.rectangle((1, 1, 102, 13), fill='#e8deb2')
    d.line((2, 2, 101, 2), fill='#f4edce')
    for i, letter in enumerate('VALKYRIE PLASS'):
        if letter == ' ':
            continue
        for y, row in enumerate(FONT[letter]):
            for x, pixel in enumerate(row):
                if pixel == '1':
                    d.point((10 + i * 6 + x, y + 4), fill='#161914')
    for x in (3, 100):
        d.point((x, 7), fill='#737162')
    return image


def ceiling_lamp():
    image = Image.new('RGBA', (40, 20))
    d = ImageDraw.Draw(image)
    for x in (8, 31):
        d.rectangle((x - 1, 0, x + 1, 1), fill='#43564a')
        d.line((x, 2, x, 12), fill='#65776b')
    d.rectangle((1, 12, 38, 15), fill='#102d20')
    d.line((3, 12, 36, 12), fill='#3c674b')
    d.rectangle((4, 16, 35, 18), fill='#bccdb3')
    d.rectangle((5, 16, 34, 17), fill='#f1f5d6')
    d.line((1, 15, 2, 18), fill='#244a33', width=2)
    d.line((37, 15, 38, 18), fill='#244a33', width=2)
    return image


def tube_light():
    image = Image.new('RGBA', (100 * 4, 104 * 4))
    pixels = image.load()
    for y in range(image.height):
        depth = (y + .5) / image.height
        radius = 17 + 32 * min(1, depth / .6) - 25 * max(0, (depth - .6) / .4)
        for x in range(image.width):
            distance = abs((x + .5) / 4 - 50)
            edge = max(0, min(1, (radius - distance) / 12))
            fade = max(0, min(1, (1 - depth) / .4))
            pixels[x, y] = (255, 255, 255, round(255 * edge * edge * (3 - 2 * edge) * fade * fade * (3 - 2 * fade)))
    return image


def sign_lights():
    fixtures = Image.new('RGBA', (104, 12))
    glow = Image.new('RGBA', (128, 48))
    d, g = ImageDraw.Draw(fixtures), ImageDraw.Draw(glow)
    for x in (16, 52, 88):
        d.line((x, 2, x, 6), fill='#43564a', width=2)
        d.rectangle((x - 3, 5, x + 3, 8), fill='#163c29')
        d.line((x - 2, 9, x + 2, 9), fill='#f2ebc5')
        g.polygon([(x + 10, 10), (x + 14, 10), (x + 28, 44), (x - 4, 44)], fill=(255, 239, 191, 100))
    return fixtures, glow.filter(ImageFilter.GaussianBlur(3))


def walls():
    # Platform 275 minus ceiling 195: exactly 80 native pixels, without light fixtures.
    image = Image.new('RGBA', (768, 80))
    d = ImageDraw.Draw(image)
    for tile in range(6):
        start = tile * 128
        for y in range(40):
            curve = math.sin(y / 39 * math.pi / 2)
            for x in range(128):
                grain = ((x * 17 + y * 31) % 13 - 6) // 3
                mottling = round(2 * math.sin(x * .21 + y * .14) + 2 * math.sin(x * .07 - y * .31))
                value = round(18 + 179 * curve) + grain + mottling
                d.point((start + x, y), fill=(value, value - 1, value - 10, 255))
        d.rectangle((start, 40, start + 127, 79), fill='#a1a395')
        d.line((start, 44, start, 78), fill='#b9bcab')
        d.line((start + 127, 44, start + 127, 78), fill='#62695e')
        if tile % 2 == 0:
            for offset in (8, 48, 88):
                x = start + offset
                d.rectangle((x, 48, x + 31, 63), fill='#636b60')
                d.rectangle((x + 1, 49, x + 30, 62), fill='#adb09d' if tile != 4 else '#727b70')
                d.line((x + 1, 63, x + 31, 63), fill='#c4c6b4')
                d.line((x + 31, 49, x + 31, 63), fill='#c4c6b4')
                if tile == 4:
                    for y in (52, 56, 60):
                        d.line((x + 2, y, x + 29, y), fill='#626d63')
        d.line((start, 39, start + 127, 39), fill='#d2d0b9')
        d.line((start, 40, start + 127, 40), fill='#555e54')
        d.line((start, 42, start + 127, 42), fill='#b8bca7')
        d.line((start, 79, start + 127, 79), fill='#596256')
    return image


def poster(kind):
    image = Image.new('RGBA', (24, 32), '#353b32')
    d = ImageDraw.Draw(image)
    d.rectangle((1, 1, 22, 30), fill='#b6aa80')
    paper = ['#d9d3b3', '#e7c879', '#d2bc93'][kind]
    d.rectangle((2, 2, 21, 29), fill=paper)
    if kind == 0:
        d.polygon([(2, 12), (21, 3), (21, 29), (2, 29)], fill='#20496b')
        d.polygon([(6, 12), (16, 10), (18, 24), (8, 26)], fill='#e9e3cb')
        d.polygon([(6, 12), (16, 10), (17, 15), (7, 17)], fill='#30658b')
        d.line((9, 20, 16, 19), fill='#4e7491', width=2)
        d.line((5, 25, 16, 7), fill='#f6ead0', width=2)
        d.line((5, 25, 7, 22), fill='#a26a36', width=2)
        d.arc((10, 3, 19, 11), 140, 280, fill='#a9b5b1')
    elif kind == 1:
        d.ellipse((2, 7, 20, 25), fill='#dc792c')
        d.ellipse((3, 18, 10, 25), fill='#f5b444')
        d.line((4, 21, 9, 22), fill='#fae1a1')
        d.rectangle((13, 9, 16, 13), fill='#797031')
        d.rounded_rectangle((11, 12, 18, 27), radius=2, fill='#ad591d')
        d.line((12, 14, 12, 24), fill='#f0c05e')
        d.rectangle((12, 18, 17, 23), fill='#edbd35')
        d.line((13, 20, 16, 19), fill='#b24225')
        d.rectangle((13, 8, 16, 9), fill='#d4cbb0')
    else:
        d.polygon([(2, 8), (21, 15), (21, 28), (2, 28)], fill='#8e382b')
        d.polygon([(5, 12), (13, 9), (15, 21), (7, 23)], fill='#47392c')
        d.polygon([(5, 12), (13, 9), (15, 12), (7, 15)], fill='#927342')
        d.rectangle((8, 15, 12, 19), fill='#cdb16e')
        d.ellipse((12, 22, 20, 25), fill='#eee0b7')
        d.rectangle((13, 20, 19, 23), fill='#eee0b7')
        d.ellipse((13, 19, 19, 21), fill='#503726')
        d.arc((15, 12, 20, 19), 110, 260, fill='#b49b73')
    # Broken display strokes suggest period lettering without readable copy.
    for x, w in ((4, 3), (8, 2), (11, 4), (16, 3)):
        d.rectangle((x, 4, x + w - 1, 5), fill='#334b54' if kind == 0 else '#97492b')
    for x in (5, 9, 14, 17):
        d.line((x, 28, x + 1, 28), fill='#ddd0a4')
    return image


def worn_poster(kind):
    image = poster(kind)
    d = ImageDraw.Draw(image)
    if kind == 0:
        d.polygon([(0, 14), (3, 15), (2, 17), (7, 18), (4, 20),
                   (5, 22), (1, 23), (0, 25)], fill=(0, 0, 0, 0))
        d.line([(3, 15), (2, 17), (7, 18), (4, 20), (5, 22), (1, 23)],
               fill='#e9dfba')
        d.polygon([(18, 31), (20, 28), (21, 30), (23, 27), (23, 31)],
                  fill=(0, 0, 0, 0))
    elif kind == 1:
        d.polygon([(16, 0), (23, 0), (23, 7)], fill=(0, 0, 0, 0))
        d.line((15, 1, 22, 8), fill='#735a35')
        d.polygon([(16, 1), (16, 7), (22, 7)], fill='#f1e2b9')
        d.line((16, 7, 22, 7), fill='#b9a17c')
    else:
        d.polygon([(0, 24), (0, 31), (8, 31)], fill=(0, 0, 0, 0))
        d.line((1, 23, 9, 30), fill='#684d32')
        d.polygon([(1, 24), (8, 24), (8, 30)], fill='#e8d5ac')
        d.line((8, 24, 8, 30), fill='#ac9168')
        d.polygon([(23, 8), (20, 10), (22, 12), (19, 14), (23, 13)],
                  fill=(0, 0, 0, 0))
        d.line([(20, 10), (22, 12), (19, 14)], fill='#e8d5ac')
    return image


def scale():
    image = Image.new('RGBA', (22, 46))
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((2, 40, 20, 45), radius=2, fill='#3c4846')
    d.rectangle((3, 40, 19, 42), fill='#b4beb2')
    for y in (41, 43):
        d.line((5, y, 17, y), fill='#747e77')
    d.rectangle((8, 13, 14, 40), fill='#a8b2a7')
    d.rectangle((9, 13, 12, 39), fill='#e0dfcb')
    d.line((10, 15, 10, 38), fill='#f3eedb')
    d.rounded_rectangle((2, 0, 20, 18), radius=5, fill='#68766e')
    d.rounded_rectangle((3, 1, 19, 17), radius=4, fill='#e2e1cd')
    d.ellipse((5, 3, 17, 15), fill='#46594f')
    d.ellipse((6, 4, 16, 14), fill='#eee8cd')
    for x, y in ((7, 8), (8, 6), (11, 5), (14, 6), (15, 8)):
        d.point((x, y), fill='#536056')
    d.line((11, 11, 14, 7), fill='#ae4e38')
    d.rectangle((10, 20, 13, 25), fill='#68766e')
    d.line((11, 21, 11, 23), fill='#152e28')
    d.point((13, 26), fill='#9e7640')
    return image


if __name__ == '__main__':
    ceiling_lamp().save(ROOT / 'valkyrien-ceiling-lamp.png')
    tube_light().save(ROOT / 'valkyrien-tube-light.png')
    fixtures, glow = sign_lights()
    fixtures.save(ROOT / 'valkyrien-sign-lamps.png')
    glow.save(ROOT / 'valkyrien-sign-light.png')
    sign().save(ROOT / 'valkyrien-sign.png')
    walls().save(ROOT / 'valkyrien-wall.png')
    assets = {}
    for i, name in enumerate(('poster_tobacco', 'poster_soda', 'poster_coffee')):
        poster(i).save(ROOT / f'{name.replace("_", "-")}.png')
        assets[name] = {'w': 24, 'h': 32, 'wall': True}
        worn_poster(i).save(ROOT / f'{name.replace("_", "-")}-worn.png')
        assets[f'{name}_worn'] = {'w': 24, 'h': 32, 'wall': True}
    scale().save(ROOT / 'vintage-scale.png')
    assets['vintage_scale'] = {'w': 22, 'h': 46, 'wall': False}
    (ROOT / 'station-assets.json').write_text(json.dumps(assets, indent=2) + '\n')
