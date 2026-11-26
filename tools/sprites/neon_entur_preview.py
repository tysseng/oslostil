#!/usr/bin/env python3
"""Draw a front-elevation study of the Entur office alongside the Knowit highrise."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from neon_cars_preview import CYAN, GLOW_PAD, PINK, PINK_DARK, PINK_MID, glow_layer
from neon_highrise_preview import BLACK, CYAN_DARK, CYAN_MID


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "previews" / "neon-highrise"
ASSETS = ROOT / "assets" / "backgrounds"
W, H = 97, 85


def entur():
    building = Image.new("RGBA", (W, H), BLACK)
    ImageDraw.Draw(building).rectangle((91, 58, W - 1, H - 1), fill=(0, 0, 0, 0))
    lines = Image.new("RGBA", (W, H))
    l = ImageDraw.Draw(lines)
    interiors = []
    lit_windows = {(14, 2), (36, 2), (49, 2), (83, 2), (4, 30), (61, 30), (71, 30), (91, 30)}
    window_light = Image.new("L", (W + 2 * GLOW_PAD, H + 2 * GLOW_PAD))
    wd = ImageDraw.Draw(window_light)

    l.line((0, H - 1, 0, 0, W - 1, 0), fill=PINK_MID)
    l.line((1, 0, W - 2, 0), fill=PINK)
    l.line((0, H - 1, 90, H - 1), fill=CYAN_MID)
    l.line((W - 1, 1, W - 1, 57), fill=CYAN_MID)

    def window(x, right, top, bottom, split, corner=False):
        lit = (x, top) in lit_windows
        l.line((x, top, right, top), fill=CYAN_MID)
        l.line((x, top, x, bottom), fill=CYAN_MID)
        l.line((right, top + 1, right, bottom), fill=CYAN if lit else PINK_DARK if corner else PINK_MID)
        l.line((x + 1, bottom, W - 1 if corner else right, bottom), fill=CYAN if lit else PINK_MID)
        if not lit:
            l.line((x + 1, split, right - 1, split), fill=CYAN_DARK)
        if corner:
            l.line((right, top, W - 1, top), fill=CYAN_MID)
            l.line((W - 1, top + 1, W - 1, bottom - 1), fill=(0, 0, 0, 0))
            ImageDraw.Draw(building).rectangle((right + 1, top + 1, W - 1, bottom - 1),
                                              fill=(0, 0, 0, 0))
        for bounds in ((x + 1, top + 1, right - 1, split - 1),
                       (x + 1, split + 1, right - 1, bottom - 1)):
            interiors.append((bounds, lit))
            if lit:
                wd.rectangle(tuple(v + GLOW_PAD for v in bounds), fill=180)
        if lit:
            interiors.append(((x + 1, split, right - 1, split), True))

    for left, right in ((4, 10), (14, 23), (27, 32), (36, 45),
                        (49, 55), (59, 68), (72, 79), (83, 88)):
        window(left, right, 2, 25, 14)
    window(91, 94, 2, 25, 14, corner=True)

    for left, right in ((4, 12), (16, 22), (26, 34), (38, 43),
                        (47, 57), (61, 67), (71, 80), (84, 88)):
        window(left, right, 30, 53, 42)
    window(91, 94, 30, 53, 42, corner=True)

    # Broad, dark glazing between the full-height ground-floor columns.
    for left, right in ((5, 29), (34, 59), (64, 85)):
        window(left, right, 58, 83, 71)
    for x in (0, 29, 59, 85):
        l.rectangle((x, 57, x + 5, 83), fill=BLACK)
        l.line((x, 57, x, 83), fill=PINK_MID)
        l.line((x + 5, 57, x + 5, 83), fill=CYAN_MID)
    l.line((0, 57, W - 1, 57), fill=PINK_MID)

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
    d = ImageDraw.Draw(building)
    for bounds, lit in interiors:
        d.rectangle(bounds, fill=CYAN if lit else BLACK)
    for left, right in ((5, 29), (34, 59), (64, 85)):
        for x in (left + (right - left) // 3, left + 2 * (right - left) // 3):
            d.line((x, 59, x, 82), fill=CYAN_DARK)

    sign_width = 108
    extended = Image.new("RGBA", (sign_width, H))
    extended.alpha_composite(building)
    extended_glow = Image.new("RGBA", (sign_width + 2 * GLOW_PAD, H + 2 * GLOW_PAD))
    extended_glow.alpha_composite(glow)
    sign = Image.new("RGBA", (sign_width, H))
    sd = ImageDraw.Draw(sign)
    sd.line((91, 62, 92, 62), fill=PINK_MID)
    sd.line((91, 70, 92, 70), fill=PINK_MID)
    sd.rectangle((93, 59, 107, 72), fill=BLACK, outline=PINK_MID)
    logo = Image.new("RGBA", (sign_width, H))
    ld = ImageDraw.Draw(logo)
    for x, letter in ((96, ("1111", "1000", "1110", "1000", "1111")),
                      (101, ("1001", "1101", "1011", "1001", "1001"))):
        for dy, row in enumerate(letter):
            for dx, pixel in enumerate(row):
                if pixel == "1":
                    ld.point((x + dx, 62 + dy), fill=CYAN)
    ld.line((96, 69, 104, 69), fill=PINK)
    logo_glow = glow_layer(logo).filter(ImageFilter.GaussianBlur(2))
    logo_glow.putalpha(logo_glow.getchannel("A").point(lambda alpha: min(255, round(alpha * 2.2))))
    extended_glow.alpha_composite(logo_glow)
    extended.alpha_composite(sign)
    extended.alpha_composite(logo_glow.crop((GLOW_PAD, GLOW_PAD, sign_width + GLOW_PAD, H + GLOW_PAD)))
    extended.alpha_composite(logo)
    return extended, extended_glow


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    building, glow = entur()
    building.save(OUT / "entur-draft.png")
    glow.save(OUT / "entur-draft-light.png")
    building.save(ASSETS / "neon-highrise-2.png")
    glow.save(ASSETS / "neon-highrise-2-light.png")

    knowit = Image.open(ROOT / "assets/backgrounds/neon-highrise-1.png").convert("RGBA")
    knowit_glow = Image.open(ROOT / "assets/backgrounds/neon-highrise-1-light.png").convert("RGBA")
    scene = Image.new("RGBA", (300, 117), (25, 13, 37, 255))
    ground = 100
    for image, light, x in ((knowit, knowit_glow, 17), (building, glow, 155)):
        y = ground - image.height
        scene.alpha_composite(light, (x - GLOW_PAD, y - GLOW_PAD))
        scene.alpha_composite(image, (x, y))
    ImageDraw.Draw(scene).line((5, ground, 294, ground), fill=(90, 60, 109, 255))
    scene.convert("RGB").resize((scene.width * 4, scene.height * 4), Image.Resampling.NEAREST).save(
        OUT / "entur-comparison-4x.png"
    )


if __name__ == "__main__":
    main()
