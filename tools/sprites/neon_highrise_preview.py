#!/usr/bin/env python3
"""Draw a front-elevation study of the first Neon Oslo highrise."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from neon_cars_preview import CYAN, PINK, PINK_DARK, PINK_MID, GLOW_PAD, glow_layer


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "previews" / "neon-highrise"
ASSETS = ROOT / "assets" / "backgrounds"
W, H = 136, 76
BLACK = (5, 3, 10, 255)
CYAN_MID = (22, 126, 145, 255)
CYAN_DARK = (11, 59, 76, 255)
SIGN = {
    "k": ("100", "100", "101", "110", "110", "101", "101"),
    "n": ("000", "000", "110", "101", "101", "101", "101"),
    "o": ("000", "000", "010", "101", "101", "101", "010"),
    "w": ("000", "000", "101", "101", "101", "111", "101"),
    "i": ("010", "000", "110", "010", "010", "010", "111"),
    "t": ("010", "010", "111", "010", "010", "010", "001"),
}


def highrise():
    building = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(building)
    # Four floors on the left; a fifth spans the opening and the right wing.
    d.polygon([(18, 15), (54, 15), (54, 0), (W - 2, 0), (W - 2, H - 1),
               (18, H - 1)], fill=BLACK)
    d.rectangle((59, 33, 90, 59), fill=(0, 0, 0, 0))
    for y0, y1 in ((3, 12), (19, 28), (33, 42)):
        d.rectangle((133, y0, W - 2, y1), fill=(0, 0, 0, 0))

    lines = Image.new("RGBA", (W, H))
    l = ImageDraw.Draw(lines)
    l.line([(18, H - 1), (18, 15), (54, 15), (54, 0), (W - 2, 0)], fill=PINK_MID)
    l.line((19, 15, 53, 15), fill=PINK)
    l.line((54, 15, W - 2, 15), fill=PINK_MID)
    l.line((55, 0, W - 2, 0), fill=PINK)
    l.line((W - 2, 1, W - 2, H - 1), fill=CYAN_MID)
    # Keep the outer cyan edge only in the spaces above and between windows.
    for y0, y1 in ((2, 13), (18, 29), (32, 43)):
        l.line((W - 2, y0, W - 2, y1), fill=(0, 0, 0, 0))
    l.line((18, H - 1, W - 2, H - 1), fill=CYAN_MID)
    # The opening crosses floors two and three and is open to the background.
    l.line((58, 32, 58, 59), fill=CYAN_MID)
    l.line((91, 32, 91, 59), fill=PINK_MID)
    l.line((59, 32, 90, 32), fill=CYAN)

    window_interiors = []
    lit_windows = {
        (22, 62), (31, 62), (40, 62),
        (31, 18), (40, 18), (75, 18), (84, 18), (93, 18), (102, 18),
        (49, 48), (68, 62), (75, 3), (120, 33), (129, 18),
    }
    window_light = Image.new("L", (W + 2 * GLOW_PAD, H + 2 * GLOW_PAD))
    wd = ImageDraw.Draw(window_light)
    def window(x, y, row, width=6, right_color=PINK_MID, horizontal_end=None):
        lit = (x, y) in lit_windows
        x1, y1 = x + width - 1, y + 10 + (1 if row in (2, 4) else 0)
        line_end = x1 if horizontal_end is None else horizontal_end
        if row in (1, 3):
            y -= 1
        l.line((x, y, line_end, y), fill=CYAN_MID)
        l.line((x, y, x, y1), fill=CYAN_MID)
        l.line((x1, y + 1, x1, y1), fill=CYAN if lit else right_color)
        l.line((x + 1, y1, line_end, y1), fill=CYAN if lit else PINK_MID)
        bounds = (x + 1, y + 1, x1 - 1, y1 - 1)
        window_interiors.append((bounds, lit))
        if lit:
            wd.rectangle(tuple(v + GLOW_PAD for v in bounds), fill=180)

    for floor in range(4):
        y = 18 + floor * 15 - (1 if floor == 3 else 0)
        for x in (22, 31, 40, 49):
            window(x, y, floor + 2)
    for y, row in ((3, 1), (18, 2), (62, 5)):
        for x in ((59, 68, 77, 86) if row == 5 else (57, 66, 75, 84)):
            window(x, y, row)
    for y, row in ((3, 1), (18, 2), (33, 3)):
        for x in (93, 102, 111, 120):
            window(x, y, row)
        window(129, y, row, width=4, right_color=PINK_DARK, horizontal_end=W - 2)

    # Open colonnade on the right, continuing through the two lower floors.
    for x in (94, 104, 114, 124, 134):
        l.line((x, 45, x, 74), fill=PINK_MID)
        if x + 1 < W - 1:
            l.line((x + 1, 45, x + 1, 74), fill=CYAN_DARK)
    l.line((94, 45, W - 2, 45), fill=PINK_DARK)
    l.line((59, 60, 90, 60), fill=PINK_MID)
    l.line((W - 2, 45, W - 2, H - 1), fill=CYAN_MID)

    # A small suspended sign sits in front of the colonnade.
    l.line((101, 46, 101, 48), fill=PINK_MID)
    l.line((127, 46, 127, 48), fill=PINK_MID)
    l.rectangle((99, 48, 129, 58), fill=BLACK)
    l.line((99, 48, 129, 48), fill=PINK_MID)
    l.line((99, 49, 99, 58), fill=PINK_DARK)
    l.line((100, 58, 129, 58), fill=CYAN_MID)
    l.line((129, 49, 129, 58), fill=CYAN_MID)
    text = Image.new("RGBA", (W, H))
    td = ImageDraw.Draw(text)
    for i, char in enumerate("knowit"):
        for dy, row in enumerate(SIGN[char]):
            for dx, pixel in enumerate(row):
                if pixel == "1":
                    td.point((103 + 4 * i + dx, 50 + dy), fill=PINK)

    glow = glow_layer(lines)
    window_glow = Image.new("RGBA", glow.size, (66, 221, 239, 0))
    window_glow.putalpha(window_light.filter(ImageFilter.GaussianBlur(5)).point(
        lambda alpha: min(255, round(alpha * 5))
    ))
    glow.alpha_composite(window_glow)
    inner = glow.crop((GLOW_PAD, GLOW_PAD, W + GLOW_PAD, H + GLOW_PAD))
    inner.putalpha(Image.composite(inner.getchannel("A"), Image.new("L", (W, H)), building.getchannel("A")))
    building.alpha_composite(inner)
    building.alpha_composite(lines)
    text_glow = glow_layer(text).filter(ImageFilter.GaussianBlur(2)).crop(
        (GLOW_PAD, GLOW_PAD, W + GLOW_PAD, H + GLOW_PAD)
    )
    text_glow.putalpha(text_glow.getchannel("A").point(lambda alpha: min(255, round(alpha * 2.2))))
    building.alpha_composite(text_glow)
    building.alpha_composite(text)
    d = ImageDraw.Draw(building)
    for bounds, lit in window_interiors:
        d.rectangle(bounds, fill=CYAN if lit else BLACK)
    return building, glow


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    building, glow = highrise()
    building.save(OUT / "highrise-1.png")
    glow.save(OUT / "highrise-1-light.png")
    building.crop((18, 0, W - 1, H)).save(ASSETS / "neon-highrise-1.png")
    glow.crop((18, 0, W - 1 + 2 * GLOW_PAD, H + 2 * GLOW_PAD)).save(
        ASSETS / "neon-highrise-1-light.png"
    )

    scene = Image.new("RGBA", (254, 185), (25, 13, 37, 255))
    d = ImageDraw.Draw(scene)
    d.line((10, 92, 244, 92), fill=(90, 60, 109, 255))
    x, y = 59, 16
    scene.alpha_composite(glow, (x - GLOW_PAD, y - GLOW_PAD))
    scene.alpha_composite(building, (x, y))
    shop = Image.open(ROOT / "assets/backgrounds/neon-dealership.png").convert("RGBA")
    shop_light = Image.open(ROOT / "assets/backgrounds/neon-dealership-light.png").convert("RGBA")
    shop_beams = Image.open(ROOT / "assets/backgrounds/neon-dealership-beams.png").convert("RGBA")
    scene.alpha_composite(shop_light, (28 - GLOW_PAD, 177 - 61 - GLOW_PAD))
    scene.alpha_composite(shop, (28, 177 - 61))
    scene.alpha_composite(shop_beams, (28, 177 - 61))
    d.line((10, 177, 244, 177), fill=(90, 60, 109, 255))
    scene.convert("RGB").resize((scene.width * 4, scene.height * 4), Image.Resampling.NEAREST).save(
        OUT / "highrise-1-comparison-4x.png"
    )


if __name__ == "__main__":
    main()
