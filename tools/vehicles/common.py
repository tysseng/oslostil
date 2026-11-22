"""Shared drawing helpers for the vehicle masters (cartoon side views as SVG).

Scale: about 50 SVG units per metre. Wheels stand on y = H (rail/road level).
"""
import re
from pathlib import Path

INK = '#151a22'          # outline colour
SW = 5                   # outline width
H = 262                  # rail level (wheel bottoms)


class Svg:
    def __init__(self):
        self.defs, self.body, self.n = [], [], 0

    def uid(self, p):
        self.n += 1
        return f'{p}{self.n}'

    def add(self, s):
        self.body.append(s)

    def clip(self, d):
        cid = self.uid('c')
        self.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        return cid

    def doc(self, w, h, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -40 {w + 20} {h + 50}" width="{w + 20}" height="{h + 50}">'
                f'<title>{title}</title><defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>')


def rect(x, y, w, h, fill, rx=0, stroke=True, sw=SW, extra=''):
    st = f' stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ''
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{st}{extra}/>'


def window(x, y, w, h, glass='#1d2a33', shine='#4b6b78', rx=7, frame=None):
    s = ''
    if frame:
        s += rect(x - 5, y - 5, w + 10, h + 10, frame, rx + 4, stroke=False)
    s += rect(x, y, w, h, glass, rx, sw=3)
    # diagonal reflection
    s += f'<path d="M{x + w * .18:.1f},{y + 3} L{x + w * .42:.1f},{y + 3} L{x + w * .12:.1f},{y + h - 3} L{x + 3:.1f},{y + h - 3} L{x + 3:.1f},{y + h * .55:.1f} Z" fill="{shine}" opacity=".75"/>'
    s += f'<path d="M{x + w * .55:.1f},{y + 3} L{x + w * .64:.1f},{y + 3} L{x + w * .34:.1f},{y + h - 3} L{x + w * .25:.1f},{y + h - 3} Z" fill="{shine}" opacity=".45"/>'
    return s


def wheel(cx, r=21, tyre='#2b2e36', hub='#8b919c'):
    cy = H - r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{tyre}" stroke="{INK}" stroke-width="4"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .45:.1f}" fill="{hub}" stroke="{INK}" stroke-width="2.5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .15:.1f}" fill="{INK}"/>')


def bogie(cx, span=96, frame='#30343d', spring='#5b616d'):
    y = H - 42
    s = rect(cx - span / 2 - 34, y - 6, span + 68, 26, frame, 8)
    s += wheel(cx - span / 2) + wheel(cx + span / 2)
    s += rect(cx - 14, y - 16, 28, 18, spring, 4, sw=3)   # bolster / spring
    s += rect(cx - span / 2 - 30, y + 2, 16, 10, '#1f2229', 3, stroke=False) + rect(cx + span / 2 + 14, y + 2, 16, 10, '#1f2229', 3, stroke=False)
    return s


def bellows(x, w, top, bot, col='#2a2d34'):
    s = rect(x, top, w, bot - top, col, 4)
    for i in range(1, 4):
        s += f'<line x1="{x + 3}" y1="{top + (bot - top) * i / 4:.1f}" x2="{x + w - 3}" y2="{top + (bot - top) * i / 4:.1f}" stroke="#4a4e58" stroke-width="3"/>'
    return s


def check_clear(kind, L, doors, door_w, wins, win_w, extra=()):
    """Windows (and anything else listed) must never overlap a door."""
    for wx in list(wins) + list(extra):
        for dx in doors:
            assert wx + win_w <= dx - 4 or wx >= dx + door_w + 4, f'{kind}: window at {wx:.0f} overlaps door at {dx:.0f}'



def render(out: Path, files: dict[str, str]) -> None:
    """Write SVGs, then PNG renders at 2× through a headless browser (Playwright) if available."""
    out.mkdir(parents=True, exist_ok=True)
    for name, svg in files.items():
        (out / name).write_text(svg, encoding='utf-8')
        print('wrote', out / name)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('playwright not installed – SVGs only')
        return
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name in files:
            svg = (out / name).read_text(encoding='utf-8')
            w, h = map(float, re.search(r'width="([\d.]+)" height="([\d.]+)"', svg).groups())
            pg = b.new_page(viewport={'width': int(w), 'height': int(h)}, device_scale_factor=2)
            pg.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
            pg.locator('svg').screenshot(path=str(out / name.replace('.svg', '.png')), omit_background=True)
            pg.close()
            print('wrote', out / name.replace('.svg', '.png'))
        b.close()


HIRES = Path(__file__).resolve().parents[2] / 'assets' / 'vehicles' / 'hires'
