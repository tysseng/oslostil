#!/usr/bin/env python3
"""Render hi-res vehicle masters at the in-game size for the HD canvas layer.

The game canvas is 320 × 180 game pixels drawn at 4 canvas pixels each, so a vehicle at 8 game px per
metre needs 32 canvas px per metre. The masters are 50 SVG units per metre → scale 0.64.
Output is trimmed to the vehicle: the bottom row is the wheel bottoms (rail/road level).

Usage: python3 tools/vehicles/game_hd.py  → assets/sprites/<name>-hd.png
"""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SCALE = 32 / 50
JOBS = {'train-green-hd': 'local-train-green', 'train-tomato-hd': 'local-train-tomato-soup'}

with sync_playwright() as p:
    b = p.chromium.launch()
    for out, src in JOBS.items():
        svg = (ROOT / 'assets/vehicles/hires' / f'{src}.svg').read_text(encoding='utf-8')
        w, h = map(float, re.search(r'width="([\d.]+)" height="([\d.]+)"', svg).groups())
        pg = b.new_page(viewport={'width': int(w), 'height': int(h)}, device_scale_factor=SCALE)
        pg.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
        path = ROOT / 'assets/sprites' / f'{out}.png'
        pg.locator('svg').screenshot(path=str(path), omit_background=True)
        pg.close()
        im = Image.open(path)
        im.crop(im.getbbox()).save(path)
        print('wrote', path, Image.open(path).size)
    b.close()
