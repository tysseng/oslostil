#!/usr/bin/env python3
"""Generate approved synthwave car sprites, glow layers and a size comparison.

Run from the repository root: python3 tools/sprites/neon_cars_preview.py
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "previews" / "neon-cars"
ASSETS = ROOT / "assets" / "sprites"
PINK = (255, 43, 214, 255)
PINK_MID = (181, 30, 151, 255)
PINK_DARK = (101, 18, 88, 255)
BLACK = (5, 3, 10, 255)
CYAN = (43, 240, 255, 255)
GLOW_PAD = 16


class BodyDraw:
    def __init__(self, im, scale):
        self.draw = ImageDraw.Draw(im)
        self.scale = scale

    def points(self, points):
        return [(round(x * self.scale), y) for x, y in points]

    def polygon(self, points, **kwargs):
        self.draw.polygon(self.points(points), **kwargs)

    def line(self, points, **kwargs):
        self.draw.line(self.points(points), **kwargs)

    def point(self, point, **kwargs):
        self.draw.point((round(point[0] * self.scale), point[1]), **kwargs)


def soften_lines(im):
    source = im.copy()
    pixels = source.load()
    for y in range(1, im.height - 1):
        for x in range(1, im.width - 1):
            if pixels[x, y] != BLACK:
                continue
            horizontal = pixels[x - 1, y] == PINK or pixels[x + 1, y] == PINK
            vertical = pixels[x, y - 1] == PINK or pixels[x, y + 1] == PINK
            if horizontal and vertical:
                im.putpixel((x, y), PINK_DARK)


def lower_body(im):
    lowered = Image.new("RGBA", im.size)
    lowered.alpha_composite(im, (0, 1))
    return lowered


def lower_edge(im, centers, rear_slope=False):
    d = ImageDraw.Draw(im)
    start = 3
    for cx in centers:
        d.line((start, 21, cx - 8, 21), fill=CYAN)
        start = cx + 8
    if rear_slope:
        d.line([(start, 19), (start + 1, 19), (im.width - 5, 17)], fill=CYAN)
    else:
        d.line((start, 21, im.width - 5, 21), fill=CYAN)


def wheel(im, cx, cy):
    d = ImageDraw.Draw(im)
    for dy in range(1, 7):
        half_width = int((36 - dy * dy) ** 0.5)
        d.line((cx - half_width, cy + dy, cx + half_width, cy + dy), fill=BLACK)
        d.point((cx - half_width, cy + dy), fill=CYAN)
        d.point((cx + half_width, cy + dy), fill=CYAN)
    d.line((cx - 2, cy + 6, cx + 2, cy + 6), fill=CYAN)


def glow_layer(im):
    pink = Image.new("L", (im.width + 2 * GLOW_PAD, im.height + 2 * GLOW_PAD))
    cyan = Image.new("L", pink.size)
    for y in range(im.height):
        for x in range(im.width):
            color = im.getpixel((x, y))
            intensity = {PINK: 255, PINK_MID: 180, PINK_DARK: 90}.get(color, 0)
            if intensity:
                pink.putpixel((x + GLOW_PAD, y + GLOW_PAD), intensity)
            if color == CYAN:
                cyan.putpixel((x + GLOW_PAD, y + GLOW_PAD), 255)
    glow = Image.new("RGBA", pink.size)
    for mask, color in ((pink, PINK), (cyan, CYAN)):
        mask = mask.filter(ImageFilter.GaussianBlur(radius=3))
        mask = mask.point(lambda alpha: min(255, round(alpha * 1.6)))
        layer = Image.new("RGBA", mask.size, color[:3] + (0,))
        layer.putalpha(mask)
        glow.alpha_composite(layer)
    return glow


def lambo(scale=1):
    im = Image.new("RGBA", (round(102 * scale), 28))
    d = BodyDraw(im, scale)
    # Long wedge, low cabin and raised wing follow the side-on silhouette.
    d.polygon([(1, 18), (9, 14), (18, 11), (25, 9), (34, 6),
               (43, 2), (56, 2), (66, 3), (75, 5), (86, 7),
               (95, 8), (98, 10), (98, 20), (1, 20)], fill=BLACK)
    d.polygon([(83, 6), (86, 3), (91, 2), (93, 1), (100, 1),
               (99, 3), (95, 3), (93, 7)], fill=BLACK)
    d.line([(1, 18), (10, 14), (18, 11), (25, 9), (33, 6),
            (43, 2), (56, 2), (66, 3), (75, 5), (86, 7),
            (95, 8), (98, 10), (98, 17)], fill=PINK)
    d.line([(25, 9), (35, 10), (46, 10), (59, 9), (70, 8), (84, 7)], fill=PINK)
    d.line([(35, 10), (43, 2)], fill=PINK)
    d.line([(39, 6), (56, 5)], fill=PINK)
    d.line([(57, 2), (57, 9)], fill=PINK)
    d.line([(59, 3), (64, 5), (64, 8)], fill=PINK)
    d.polygon([(65, 3), (73, 4), (77, 5), (67, 5)], fill=PINK)
    d.polygon([(49, 12), (57, 10), (61, 10), (61, 14),
               (57, 14), (52, 13), (49, 13)], fill=PINK)
    d.line([(83, 6), (88, 3), (91, 3)], fill=PINK)
    d.line([(84, 2), (93, 1), (100, 1), (99, 2), (93, 2)], fill=PINK)
    d.line([(11, 20), (13, 16), (15, 13), (18, 12), (23, 12),
            (25, 13), (28, 17), (30, 20)], fill=PINK)
    d.line([(72, 20), (74, 16), (77, 13), (80, 12), (85, 12),
            (88, 13), (91, 16), (93, 20)], fill=PINK)
    # Opaque intermediate pixels soften the steps without blurring the pixel grid.
    for x, y in [(3, 18), (6, 16), (12, 14), (15, 12), (21, 11),
                 (29, 9), (32, 7), (38, 5), (41, 3), (68, 4),
                 (73, 6), (78, 6), (90, 8), (97, 9)]:
        d.point((x, y), fill=PINK_MID)
    for x, y in [(12, 19), (14, 15), (16, 13), (24, 13), (27, 16),
                 (29, 19), (73, 19), (75, 15), (78, 13), (86, 13),
                 (89, 15), (92, 19)]:
        d.point((x, y), fill=PINK_DARK)
    soften_lines(im)
    im = lower_body(im)
    centers = (round(20 * scale), round(83 * scale))
    rear_start, rear_end = centers[1] + 7, round(98 * scale)
    for x in range(rear_start, rear_end + 1):
        bottom = round(19 - 4 * (x - rear_start) / (rear_end - rear_start))
        for y in range(bottom + 1, im.height):
            im.putpixel((x, y), (0, 0, 0, 0))
    lower_edge(im, centers, rear_slope=True)
    for cx in centers:
        wheel(im, cx, 19)
    return im


def testarossa(scale=1):
    im = Image.new("RGBA", (round(102 * scale), 28))
    d = BodyDraw(im, scale)
    # Flat nose, compact cabin, long rear deck and distinctive side strakes.
    d.polygon([(1, 15), (10, 12), (20, 10), (27, 9), (36, 5),
               (47, 2), (57, 2), (67, 3), (76, 5), (88, 7),
               (99, 9), (99, 20), (1, 20)], fill=BLACK)
    d.line([(1, 15), (10, 12), (20, 10), (27, 9), (36, 5),
            (47, 2), (57, 2), (67, 3), (76, 5), (88, 7),
            (99, 9), (99, 14)], fill=PINK)
    d.line([(27, 9), (38, 10), (52, 10), (68, 9), (84, 8), (93, 9)], fill=PINK)
    d.line([(28, 9), (39, 5), (47, 2)], fill=PINK)
    d.line([(60, 3), (58, 9)], fill=PINK)
    d.polygon([(67, 3), (74, 4), (87, 7), (69, 7)], fill=PINK)
    d.line([(30, 11), (43, 11), (56, 10), (71, 8)], fill=PINK)
    d.line([(31, 12), (46, 12), (60, 11), (67, 10)], fill=PINK)
    d.line([(37, 13), (68, 12), (67, 18), (65, 19), (37, 19)], fill=PINK)
    for y in (14, 16, 18):
        d.line([(38, y), (66, y - 1)], fill=PINK)
    d.line([(13, 19), (14, 16), (16, 13), (19, 12), (23, 12),
            (26, 13), (29, 17), (30, 19)], fill=PINK)
    d.line([(75, 19), (77, 16), (80, 13), (83, 12), (87, 12),
            (90, 13), (93, 16), (94, 19)], fill=PINK)
    d.line([(99, 10), (100, 10), (100, 15)], fill=PINK)
    for x, y in [(4, 15), (7, 13), (12, 12), (17, 11), (30, 9),
                 (34, 7), (39, 5), (44, 3), (69, 4), (73, 5),
                 (79, 6), (85, 7), (93, 9)]:
        d.point((x, y), fill=PINK_MID)
    for x, y in [(14, 18), (15, 15), (17, 13), (24, 13), (27, 16),
                 (29, 18), (76, 18), (78, 15), (81, 13), (88, 13),
                 (91, 15), (93, 18), (39, 15), (39, 17), (65, 17)]:
        d.point((x, y), fill=PINK_DARK)
    soften_lines(im)
    im = lower_body(im)
    centers = (round(21 * scale), round(85 * scale))
    lower_edge(im, centers)
    for cx in centers:
        wheel(im, cx, 19)
    return im


def delorean(scale=1):
    im = Image.new("RGBA", (round(102 * scale), 28))
    d = BodyDraw(im, scale)
    d.polygon([(1, 18), (3, 14), (30, 11), (34, 11), (49, 5),
               (54, 4), (70, 4), (84, 6), (97, 9), (99, 11),
               (100, 19), (97, 21), (2, 21)], fill=BLACK)
    d.line([(1, 18), (3, 14), (30, 11), (34, 11), (49, 5),
            (54, 4), (70, 4), (84, 6), (97, 9), (99, 11),
            (100, 19)], fill=PINK)
    d.line([(3, 14), (30, 12)], fill=PINK_MID)
    d.line([(34, 11), (48, 6), (54, 5), (68, 5)], fill=PINK)
    d.line([(35, 12), (43, 12), (51, 9), (58, 9),
            (61, 12), (68, 12), (68, 5)], fill=PINK)
    d.line([(35, 13), (68, 13)], fill=PINK_MID)
    d.line([(71, 5), (71, 12), (75, 12), (74, 5)], fill=PINK_MID)
    d.line([(76, 6), (77, 12), (93, 12), (90, 8)], fill=PINK)
    d.line([(34, 12), (36, 17), (66, 17), (69, 13)], fill=PINK_MID)
    d.line([(3, 18), (98, 18)], fill=PINK)
    d.line([(4, 20), (12, 20)], fill=PINK_MID)
    d.line([(29, 20), (71, 20)], fill=PINK_MID)
    d.line([(89, 20), (99, 20)], fill=PINK_MID)
    d.line([(12, 20), (13, 16), (15, 14), (18, 13), (22, 13),
            (25, 14), (28, 17), (29, 20)], fill=PINK)
    d.line([(71, 20), (72, 16), (75, 14), (78, 13), (82, 13),
            (85, 14), (88, 17), (89, 20)], fill=PINK)
    for x, y in [(5, 14), (13, 13), (23, 12), (37, 10), (42, 8),
                 (47, 6), (80, 6), (89, 8), (96, 9), (14, 15),
                 (26, 15), (73, 15), (86, 15)]:
        d.point((x, y), fill=PINK_MID)
    soften_lines(im)
    wheel(im, round(20 * scale), 19)
    wheel(im, round(80 * scale), 19)
    return im


def make_preview(cars):
    preview = Image.new("RGBA", (188, 8 + 55 * len(cars)), (39, 26, 56, 255))
    d = ImageDraw.Draw(preview)
    font = ImageFont.load_default()
    girl = Image.open(ROOT / "assets" / "sprites" / "victoria.png").convert("RGBA").crop((0, 0, 24, 32))
    for i, (name, car) in enumerate(cars):
        top = 7 + 55 * i
        ground = top + 44
        d.text((7, top), name, font=font, fill=(235, 220, 244, 255))
        d.line([(7, ground), (180, ground)], fill=(110, 75, 125, 255))
        preview.alpha_composite(girl, (17, ground - 32))
        box = car.getbbox()
        if box is None:
            raise ValueError(f"{name} has no visible pixels")
        car_y = ground - box[3]
        preview.alpha_composite(glow_layer(car), (63 - GLOW_PAD, car_y - GLOW_PAD))
        preview.alpha_composite(car, (63, car_y))
    return preview


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    models = [("COUNTACH", lambo), ("TESTAROSSA", testarossa)]
    for suffix, scale in (("-short", 0.8),):
        cars = [(name, draw(scale)) for name, draw in models]
        for name, image in cars:
            image.save(OUT / (name.lower() + suffix + ".png"))
            glow_layer(image).save(OUT / (name.lower() + suffix + "-glow.png"))
            box = image.getbbox()
            if box is None:
                raise ValueError(f"{name} has no visible pixels")
            sprite = image.crop(box)
            stem = "neon-" + name.lower()
            sprite.save(ASSETS / (stem + ".png"))
            glow = glow_layer(sprite)
            glow.save(ASSETS / (stem + "-light.png"))
            metadata = {
                "file": stem + ".png",
                "cell": list(sprite.size),
                "frames": 1,
                "w": sprite.width,
                "h": sprite.height,
                "light": {"file": stem + "-light.png", "cell": list(glow.size), "padding": GLOW_PAD},
            }
            (ASSETS / (stem + ".json")).write_text(json.dumps(metadata, indent=2) + "\n")
        preview = make_preview(cars)
        preview.save(OUT / ("size-comparison" + suffix + "-1x.png"))
        preview.resize((preview.width * 4, preview.height * 4), Image.Resampling.NEAREST).save(
            OUT / ("size-comparison" + suffix + "-4x.png")
        )
        for name, image in cars:
            print(f"{name}{suffix}: {image.width}x{image.height} px, visible bounds {image.getbbox()}")


if __name__ == "__main__":
    main()
