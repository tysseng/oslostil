#!/usr/bin/env python3
"""Draw a Bekk HQ study beside the approved Knowit highrise."""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from neon_cars_preview import CYAN, GLOW_PAD, PINK, PINK_MID, glow_layer
from neon_highrise_preview import BLACK, CYAN_DARK, CYAN_MID


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "previews" / "neon-bekk"
ASSETS = ROOT / "assets" / "backgrounds"
W, H = 153, 45


def bekk():
    building = Image.new("RGBA", (W, H))
    lines = Image.new("RGBA", (W, H))
    d, l = ImageDraw.Draw(building), ImageDraw.Draw(lines)
    roof = [(0, 5), (24, 5)]
    for x in (24, 56, 88, 120):
        roof.extend(((x + 16, 0), (x + 32, 5)))
    roof[-1] = (W - 1, 5)
    d.polygon(roof + [(W - 1, H - 1), (0, H - 1)], fill=BLACK)
    l.line([(0, H - 1)] + roof, fill=PINK_MID)
    l.line(roof, fill=PINK)
    l.line((W - 1, 5, W - 1, H - 1, 0, H - 1), fill=CYAN_MID)

    lit_windows = {(27, 11), (47, 11), (59, 11), (101, 11), (143, 11)}
    lit_interiors = []
    window_light = Image.new("L", (W + 2 * GLOW_PAD, H + 2 * GLOW_PAD))
    wd = ImageDraw.Draw(window_light)

    def window(x, y, width, height):
        right, bottom = x + width - 1, y + height - 1
        lit = (x, y) in lit_windows
        l.line((x, bottom, x, y, right, y), fill=CYAN_MID)
        edge = CYAN if lit else CYAN_MID if (x, y) == (37, 11) else PINK_MID
        l.line((right, y + 1, right, bottom, x + 1, bottom), fill=edge)
        if lit:
            bounds = (x + 1, y + 1, right - 1, bottom - 1)
            lit_interiors.append(bounds)
            wd.rectangle(tuple(v + GLOW_PAD for v in bounds), fill=180)

    window(11, 11, 9, 8)
    for x in (24, 56, 88, 120):
        for offset in (3, 13, 23):
            window(x + offset, 11, 7, 8)
        l.line((x, 6, x, 22), fill=PINK_MID)
        l.line((x + 1, 6, x + 1, 22), fill=CYAN_DARK)
        l.line((x + 2, 27, x + 30, 27), fill=CYAN_MID)
        l.line((x + 2, 28, x + 2, 43), fill=CYAN_DARK)
        l.line((x + 30, 28, x + 30, 43), fill=PINK_MID)
    l.line((24, 24, W - 1, 24), fill=PINK_MID)

    beams = Image.new("RGBA", (W, H), CYAN[:3] + (0,))
    mask = Image.new("L", (W, H))
    m = ImageDraw.Draw(mask)
    for x in (40, 104):
        m.polygon([(x, 4), (x + 1, 4), (x + 10, H + 2), (x - 10, H + 2)], fill=100)
        l.line((x - 1, 3, x + 1, 3), fill=PINK)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    mask = Image.composite(mask, Image.new("L", (W, H)), building.getchannel("A"))
    beams.putalpha(mask)
    building.alpha_composite(beams)

    glow = glow_layer(lines)
    side_beam = Image.new("RGBA", glow.size, CYAN[:3] + (0,))
    side_mask = Image.new("L", glow.size)
    ImageDraw.Draw(side_mask).polygon(
        [(GLOW_PAD - 2, GLOW_PAD + 21), (GLOW_PAD - 1, GLOW_PAD + 21),
         (GLOW_PAD + 4, GLOW_PAD + H + 3), (2, GLOW_PAD + H + 3)],
        fill=100,
    )
    side_mask = side_mask.filter(ImageFilter.GaussianBlur(2))
    ImageDraw.Draw(side_mask).rectangle(
        (0, GLOW_PAD + H + 1, glow.width - 1, glow.height - 1), fill=0
    )
    ImageDraw.Draw(side_mask).rectangle(
        (GLOW_PAD, 0, glow.width - 1, glow.height - 1), fill=0
    )
    fade = Image.new("L", glow.size, 255)
    f = ImageDraw.Draw(fade)
    for x in range(6):
        f.line((x, 0, x, glow.height - 1), fill=round(x * 255 / 6))
    side_beam.putalpha(ImageChops.multiply(side_mask, fade))
    glow.alpha_composite(side_beam)
    side_lamp = Image.new("RGBA", glow.size)
    ImageDraw.Draw(side_lamp).line(
        (GLOW_PAD - 2, GLOW_PAD + 20, GLOW_PAD - 1, GLOW_PAD + 20), fill=PINK
    )
    lamp_glow = glow_layer(side_lamp).crop(
        (GLOW_PAD, GLOW_PAD, glow.width + GLOW_PAD, glow.height + GLOW_PAD)
    )
    glow.alpha_composite(lamp_glow)
    glow.alpha_composite(side_lamp)
    window_glow = Image.new("RGBA", glow.size, (66, 221, 239, 0))
    window_glow.putalpha(window_light.filter(ImageFilter.GaussianBlur(5)).point(
        lambda alpha: min(255, round(alpha * 5))
    ))
    glow.alpha_composite(window_glow)
    inner = glow.crop((GLOW_PAD, GLOW_PAD, W + GLOW_PAD, H + GLOW_PAD))
    inner.putalpha(Image.composite(inner.getchannel("A"), Image.new("L", (W, H)), building.getchannel("A")))
    building.alpha_composite(inner)
    building.alpha_composite(lines)

    text = Image.new("RGBA", (W, H))
    td = ImageDraw.Draw(text)
    letters = {
        "B": ("1110", "1001", "1001", "1110", "1001", "1001", "1110"),
        "e": ("0000", "0000", "0110", "1001", "1111", "1000", "0111"),
        "k": ("1000", "1000", "1001", "1010", "1100", "1010", "1001"),
    }
    for i, char in enumerate("Bekk"):
        for dy, row in enumerate(letters[char]):
            for dx, pixel in enumerate(row):
                if pixel == "1":
                    td.point((4 + 5 * i + dx, 29 + dy), fill=PINK)
    text_glow = glow_layer(text).filter(ImageFilter.GaussianBlur(2)).crop(
        (GLOW_PAD, GLOW_PAD, W + GLOW_PAD, H + GLOW_PAD)
    )
    text_glow.putalpha(text_glow.getchannel("A").point(lambda alpha: min(255, round(alpha * 1.7))))
    building.alpha_composite(text_glow)
    building.alpha_composite(text)
    for bounds in lit_interiors:
        d.rectangle(bounds, fill=CYAN)
    return building, glow


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    building, glow = bekk()
    building.save(OUT / "bekk-draft.png")
    glow.save(OUT / "bekk-draft-light.png")
    building.save(ASSETS / "neon-highrise-3.png")
    glow.save(ASSETS / "neon-highrise-3-light.png")
    knowit = Image.open(ROOT / "assets/backgrounds/neon-highrise-1.png").convert("RGBA")
    knowit_light = Image.open(ROOT / "assets/backgrounds/neon-highrise-1-light.png").convert("RGBA")
    scene = Image.new("RGBA", (330, 110), (25, 13, 37, 255))
    ground = 92
    for image, light, x in ((knowit, knowit_light, 16), (building, glow, 155)):
        y = ground - image.height
        scene.alpha_composite(light, (x - GLOW_PAD, y - GLOW_PAD))
        scene.alpha_composite(image, (x, y))
    ImageDraw.Draw(scene).line((5, ground, 324, ground), fill=(90, 60, 109, 255))
    scene.convert("RGB").resize((scene.width * 4, scene.height * 4), Image.Resampling.NEAREST).save(
        OUT / "bekk-comparison-4x.png"
    )


if __name__ == "__main__":
    main()
