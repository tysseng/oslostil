#!/usr/bin/env python3
"""Recolor the tram's blue and yellow accents for Neon Oslo."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/vehicles/hires/tram-new.png"
OUTPUT = ROOT / "assets/vehicles/hires/tram-neon.png"


def main():
    image = Image.open(SOURCE).convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if a and b > g > r and b - r > 0.35 * b and g - r > 0.25 * (b - r):
                pixels[x, y] = tuple(min(255, round(b * channel / 224)) for channel in (43, 240, 255)) + (a,)
            elif a and r > 20 and g > 15 and r > g * 1.08 and g > b * 1.5:
                pixels[x, y] = tuple(min(255, round(r * channel / 242)) for channel in (255, 43, 214)) + (a,)
    image.save(OUTPUT)


if __name__ == "__main__":
    main()
