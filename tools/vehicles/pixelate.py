#!/usr/bin/env python3
"""Make pixel-art versions of the hi-res vehicle renders.

All masters share one scale (about 50 SVG units per metre; the PNGs are rendered at 2×, so 100 px per metre).
Usage:
  python3 tools/vehicles/pixelate.py --ppm 8 [names…]     → assets/vehicles/ppm8/   (same scale for every vehicle; 8 px per metre)
  python3 tools/vehicles/pixelate.py --height 36 [names…] → assets/vehicles/px36/   (every vehicle 36 px tall)
Downscales with area averaging, snaps alpha to on/off, and reduces to a small palette so it reads as pixel art.
"""
import argparse
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2] / 'assets' / 'vehicles'
MASTER_PPM = 100  # pixels per metre in the hi-res PNGs


def pixelate(src: Path, *, height: int | None = None, ppm: float | None = None, colors: int = 20) -> Image.Image:
    im = Image.open(src).convert('RGBA')
    im = im.crop(im.getbbox())
    k = height / im.height if height else ppm / MASTER_PPM
    size = (max(1, round(im.width * k)), max(1, round(im.height * k)))
    small = im.resize(size, Image.Resampling.BOX)
    alpha = small.getchannel('A').point(lambda a: 255 if a >= 110 else 0)
    rgb = Image.new('RGB', small.size, (0, 0, 0))
    rgb.paste(small.convert('RGB'), mask=small.getchannel('A'))
    q = rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGBA')
    q.putalpha(alpha)
    return q


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--ppm', type=float, help='pixels per metre (keeps relative sizes)')
    g.add_argument('--height', type=int, help='fixed height in pixels')
    ap.add_argument('names', nargs='*')
    a = ap.parse_args()
    names = a.names or [p.stem for p in sorted((ROOT / 'hires').glob('*.png'))]
    out = ROOT / (f'ppm{a.ppm:g}' if a.ppm else f'px{a.height}')
    out.mkdir(parents=True, exist_ok=True)
    for n in names:
        img = pixelate(ROOT / 'hires' / f'{n}.png', height=a.height, ppm=a.ppm)
        img.save(out / f'{n}.png')
        print('wrote', out / f'{n}.png', img.size)
