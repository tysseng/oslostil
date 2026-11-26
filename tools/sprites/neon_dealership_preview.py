#!/usr/bin/env python3
"""Generate the approved Neon Oslo dealership and comparison previews."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from neon_cars_preview import CYAN, PINK, PINK_DARK, PINK_MID, GLOW_PAD, glow_layer


ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / "assets" / "sprites"
OUT = ROOT / "previews" / "neon-dealership"
ASSETS = ROOT / "assets" / "backgrounds"
W, H = 198, 61
BLACK = (5, 3, 10, 255)
GLASS = (8, 5, 16, 255)
GLASS_LINE = (17, 12, 27, 255)
CYAN_MID = (22, 126, 145, 255)
CYAN_DARK = (11, 59, 76, 255)
FRAME = (13, 7, 20, 255)
SIGN_FONT = {
    "S": ("011", "100", "100", "010", "001", "001", "110"),
    "H": ("101", "101", "101", "111", "101", "101", "101"),
    "O": ("010", "101", "101", "101", "101", "101", "010"),
    "R": ("110", "101", "101", "110", "101", "101", "101"),
    "T": ("111", "010", "010", "010", "010", "010", "010"),
    "F": ("111", "100", "100", "110", "100", "100", "100"),
    "/": ("001", "001", "001", "010", "100", "100", "100"),
}


def car(window, name, x, bottom, flip=False):
    sprite = Image.open(SPRITES / f"neon-{name}.png").convert("RGBA")
    light = Image.open(SPRITES / f"neon-{name}-light.png").convert("RGBA")
    if flip:
        sprite = ImageOps.mirror(sprite)
        light = ImageOps.mirror(light)
    y = bottom - sprite.height
    window.alpha_composite(light, (x - GLOW_PAD, y - GLOW_PAD))
    window.alpha_composite(sprite, (x, y))


def info_screen(image, x, floor, side=False, lift=0):
    screen_floor = floor - lift
    if side:
        # Clip the cyan glow to the right-hand side of the slanted screen.
        glow = Image.new("RGBA", image.size)
        mask = Image.new("L", image.size)
        ImageDraw.Draw(mask).line((x - 3, floor - 18, x + 2, floor - 8), fill=255, width=2)
        mask = mask.filter(ImageFilter.GaussianBlur(3))
        mask = mask.point(lambda alpha: min(255, round(alpha * 4)))
        m = mask.load()
        for y in range(image.height):
            edge = x - 3 + (y - (floor - 18)) / 2
            for px in range(max(0, min(image.width, int(edge) + 1))):
                m[px, y] = 0
        glow.paste(CYAN[:3] + (0,), (0, 0, image.width, image.height))
        glow.putalpha(mask)
        image.alpha_composite(glow)
    else:
        glow = Image.new("RGBA", image.size, CYAN[:3] + (0,))
        mask = Image.new("L", image.size)
        ImageDraw.Draw(mask).rectangle((x - 2, screen_floor - 15, x + 2, screen_floor - 9), fill=210)
        mask = mask.filter(ImageFilter.GaussianBlur(3))
        mask = mask.point(lambda alpha: min(255, round(alpha * 4)))
        glow.putalpha(mask)
        image.alpha_composite(glow)

    d = ImageDraw.Draw(image)
    if side:
        d.line((x - 1, floor - 14, x - 1, floor - 1), fill=CYAN)
        d.line((x, floor - 12, x, floor - 1), fill=CYAN_DARK)
        d.line((x - 3, floor - 1, x + 1, floor - 1), fill=CYAN_MID)
        for i in range(11):
            position = x - 3 + i / 2
            left = int(position)
            fraction = position - left
            d.point((left, floor - 18 + i), fill=tuple(
                round(a * (1 - fraction) + b * fraction) for a, b in zip(CYAN, CYAN_DARK)
            ))
            if fraction:
                d.point((left + 1, floor - 18 + i), fill=tuple(
                    round(a * fraction + b * (1 - fraction)) for a, b in zip(CYAN, CYAN_DARK)
                ))
    else:
        d.line((x, screen_floor - 6, x, floor - 1), fill=CYAN_MID)
        d.line((x - 2, floor - 1, x + 2, floor - 1), fill=CYAN_DARK)
        d.rounded_rectangle((x - 3, screen_floor - 17, x + 3, screen_floor - 7), radius=1, fill=BLACK, outline=CYAN)
        d.rectangle((x - 2, screen_floor - 15, x + 2, screen_floor - 9), fill=(12, 38, 49, 255))
        d.line((x - 1, screen_floor - 14, x + 1, screen_floor - 14), fill=CYAN)
        d.line((x - 1, screen_floor - 12, x + 1, screen_floor - 12), fill=CYAN_MID)
        d.point((x, screen_floor - 10), fill=CYAN)


def spotlight(image, x):
    glow = Image.new("RGBA", image.size, CYAN[:3] + (0,))
    mask = Image.new("L", image.size)
    m = ImageDraw.Draw(mask)
    m.polygon([(x - 1, 16), (x + 1, 16), (x + 12, H - 4), (x - 12, H - 4)], fill=55)
    m.line((x, 16, x, H - 4), fill=90, width=2)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    ImageDraw.Draw(mask).rectangle((0, 0, image.width - 1, 15), fill=0)
    ImageDraw.Draw(mask).rectangle((0, H - 4, image.width - 1, H - 1), fill=0)
    glow.putalpha(mask)
    image.alpha_composite(glow)


def make_dealership():
    building = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(building)
    d.rectangle((4, 4, W - 5, H - 1), fill=BLACK)
    d.rectangle((8, 17, W - 9, H - 5), fill=GLASS)

    # Subtle reflections leave the cars clearly visible behind the glass.
    for x in (15, 108):
        d.line((x, 20, x + 7, 20), fill=GLASS_LINE)
        d.line((x, 21, x + 3, 21), fill=GLASS_LINE)

    # The left-hand display is exactly three pixels above the showroom floor.
    stand = Image.new("RGBA", (W, H))
    s = ImageDraw.Draw(stand)
    s.rectangle((11, H - 7, 93, H - 5), fill=FRAME)
    s.line((11, H - 7, 11, H - 5), fill=PINK_DARK)
    s.line((93, H - 7, 93, H - 5), fill=CYAN)
    s.line((11, H - 7, 93, H - 7), fill=PINK)
    stand_glow = glow_layer(stand)
    building.alpha_composite(stand_glow.crop((GLOW_PAD, GLOW_PAD, W + GLOW_PAD, H + GLOW_PAD)))
    building.alpha_composite(stand_glow.crop((GLOW_PAD, GLOW_PAD, W + GLOW_PAD, H + GLOW_PAD)))
    building.alpha_composite(stand)
    interior = Image.new("RGBA", (W, H))
    car(interior, "countach", 12, H - 7, flip=True)
    car(interior, "testarossa", 106, H - 4)
    # Keep the showroom lighting inside the windows, not over the structure.
    building.alpha_composite(interior.crop((8, 17, W - 8, H - 4)), (8, 17))
    info_screen(building, 83, H - 7, side=True)
    info_screen(building, 178, H - 4, lift=2)

    frame = Image.new("RGBA", (W, H))
    f = ImageDraw.Draw(frame)
    # Broad, blank fascia with a row of canopy lights, like a gas station.
    f.polygon([(3, 1), (W - 4, 1), (W - 2, 3), (W - 2, 16),
               (1, 16), (1, 3)], fill=FRAME)
    f.line((3, 1, W - 4, 1), fill=PINK)
    f.line((1, 3, 1, 15), fill=PINK_MID)
    f.line((W - 2, 3, W - 2, 15), fill=PINK_MID)
    f.point((2, 2), fill=PINK_MID)
    f.point((W - 3, 2), fill=PINK_MID)
    f.line((2, 16, W - 3, 16), fill=PINK_MID)
    label = "SHORTSH/FT"
    start = (W - (len(label) * 4 - 1)) // 2
    for i, char in enumerate(label):
        for y, row in enumerate(SIGN_FONT[char]):
            for x, pixel in enumerate(row):
                if pixel == "1":
                    f.point((start + i * 4 + x, 4 + y), fill=CYAN if char == "/" else PINK)
    for x in range(10, W - 10, 14):
        f.line((x, 14, x + 3, 14), fill=PINK)

    columns = ((4, 8), (W // 2 - 2, W // 2 + 2), (W - 9, W - 5))
    for x0, x1 in columns:
        f.rectangle((x0, 17, x1, H - 5), fill=BLACK)
        f.line((x0, 17, x0, H - 5), fill=PINK_MID)
        f.line((x1, 17, x1, H - 5), fill=CYAN_MID)

    f.rectangle((4, H - 4, W - 5, H - 1), fill=FRAME)
    f.line((5, H - 4, W - 6, H - 4), fill=CYAN_MID)
    f.line((5, H - 1, W - 6, H - 1), fill=CYAN)
    f.point((4, H - 2), fill=CYAN_MID)
    f.point((W - 5, H - 2), fill=CYAN_MID)
    building.alpha_composite(frame)
    glow_sources = frame.copy()
    g = ImageDraw.Draw(glow_sources)
    for x0, x1 in columns:
        g.line((x0, 17, x0, H - 5), fill=PINK)
        g.line((x1, 17, x1, H - 5), fill=CYAN)
    light = glow_layer(glow_sources)
    inner_glow = light.crop((GLOW_PAD, GLOW_PAD, W + GLOW_PAD, H + GLOW_PAD))
    inner_mask = Image.new("L", (W, H))
    mask_draw = ImageDraw.Draw(inner_mask)
    mask_draw.polygon([(3, 2), (W - 4, 2), (W - 3, 3), (W - 3, 15),
                       (2, 15), (2, 3)], fill=255)
    mask_draw.rectangle((4, 17, W - 5, H - 5), fill=255)
    inner_glow.putalpha(Image.composite(inner_glow.getchannel("A"), Image.new("L", (W, H)), inner_mask))
    building.alpha_composite(inner_glow)
    highlights = frame.copy()
    highlights.putdata([
        pixel if pixel in (PINK, PINK_MID, PINK_DARK, CYAN, CYAN_MID, CYAN_DARK)
        else (0, 0, 0, 0)
        for pixel in frame.getdata()
    ])
    building.alpha_composite(highlights)
    d = ImageDraw.Draw(building)
    for x in (47, 150):
        d.rounded_rectangle((x - 3, 13, x + 3, 17), radius=1, fill=PINK_DARK, outline=PINK)
        d.line((x - 1, 17, x + 1, 17), fill=CYAN)
    beams = Image.new("RGBA", (W, H))
    for x in (47, 150):
        spotlight(beams, x)
    return building, light, beams


def preview(building, light, beams, show_player=False):
    scene = Image.new("RGBA", (238, 168), (25, 13, 37, 255))
    ground = 76
    scene.alpha_composite(light, (19 - GLOW_PAD, ground - H - GLOW_PAD))
    scene.alpha_composite(building, (19, ground - H))
    victoria = Image.open(SPRITES / "victoria.png").convert("RGBA").crop((0, 0, 24, 32))
    if show_player:
        scene.alpha_composite(victoria, (19 + 47 - 12, ground - 32))
    scene.alpha_composite(beams, (19, ground - H))
    d = ImageDraw.Draw(scene)
    d.line((5, ground, 232, ground), fill=(90, 60, 109, 255))

    props = Image.open(SPRITES / "props.png").convert("RGBA")
    kiosk = props.crop((0, 3 * 64, 112, 4 * 64))
    scene.alpha_composite(kiosk, (5, 96))
    scene.alpha_composite(victoria, (119, 128))
    d.line((5, 160, 232, 160), fill=(90, 60, 109, 255))
    return scene.convert("RGB").resize((scene.width * 4, scene.height * 4), Image.Resampling.NEAREST)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    building, light, beams = make_dealership()
    building.save(OUT / "dealership.png")
    light.save(OUT / "dealership-light.png")
    beams.save(OUT / "dealership-beams.png")
    building.save(ASSETS / "neon-dealership.png")
    light.save(ASSETS / "neon-dealership-light.png")
    beams.save(ASSETS / "neon-dealership-beams.png")
    metadata = {
        "file": "neon-dealership.png",
        "w": W,
        "h": H,
        "top": H - 1,
        "top_span": [3 - W // 2, W - 3 - W // 2],
        "light": {"file": "neon-dealership-light.png", "padding": GLOW_PAD},
        "beams": {"file": "neon-dealership-beams.png", "offset": [0, 0]},
    }
    (ASSETS / "neon-dealership.json").write_text(json.dumps(metadata, indent=2) + "\n")
    preview(building, light, beams).save(OUT / "dealership-scale-4x.png")
    preview(building, light, beams, show_player=True).save(OUT / "dealership-beam-player-4x.png")


if __name__ == "__main__":
    main()
