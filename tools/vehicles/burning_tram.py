#!/usr/bin/env python3
"""The burning, slightly wrecked trams in the background of Kollektivkaos (stage 5–6).

The short (3-section) new light-blue tram from trams.py, in the same vector style, with damage on top:
blown-out windows with fire glow inside and glass shards in the frames, soot over the body and roof,
dents, a door hanging off its rail, a torn roof box and a cracked, dark destination sign.
The flames themselves are NOT in this image: they are pixel-art sprites (tools/sprites/fire.py) drawn
by the game at the points listed in FLAMES below.

Usage: python3 tools/vehicles/burning_tram.py  → assets/vehicles/hires/tram-burning.svg + .png
"""
import json
from common import HIRES, H, INK, render
from trams import NT, new_tram

TOP, BOT = 70, 242          # module body top/bottom in trams.module
# x of each module in the 3-section plan: cabL 0..360, short 374..524, cabR 538..898
CAB_L, SHORT, CAB_R = 0, 374, 538
WINDOWS = [(CAB_L + 92, 'big'), (CAB_L + 170, 'small'), (SHORT + 45, 'big'), (CAB_R + 130, 'small')]
WIN_Y, WIN_W, WIN_H = TOP + 32, 60, 74

# Flame anchors for the game: (x, y) in SVG units (x from the tram's left end, y down from the top of
# the SVG coordinate system; wheel bottoms are at y = H = 262), and the sprite to use.
FLAMES = [
    {'x': CAB_L + 122, 'y': WIN_Y + WIN_H, 'kind': 'big'},
    {'x': CAB_L + 200, 'y': WIN_Y + WIN_H, 'kind': 'small'},
    {'x': SHORT + 75, 'y': WIN_Y + WIN_H, 'kind': 'big'},
    {'x': CAB_R + 160, 'y': WIN_Y + WIN_H, 'kind': 'small'},
    {'x': CAB_L + 170, 'y': 56, 'kind': 'big'},          # on the roof, where the roof box burned through
    {'x': CAB_R + 200, 'y': 58, 'kind': 'small'},
    {'x': CAB_R + 330, 'y': 150, 'kind': 'small'},       # in the smashed windscreen
]
SMOKE = [{'x': CAB_L + 170, 'y': 30}, {'x': SHORT + 75, 'y': 40}]


def damage():
    s = []
    defs = (
        '<linearGradient id="fireglow" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#1a0806"/><stop offset=".55" stop-color="#7a1e0c"/>'
        '<stop offset="1" stop-color="#ff8a24"/></linearGradient>'
        '<radialGradient id="soot"><stop offset="0" stop-color="#0d0b0c" stop-opacity=".85"/>'
        '<stop offset="1" stop-color="#0d0b0c" stop-opacity="0"/></radialGradient>'
    )
    # blown-out windows: fire glow inside, jagged shards left in the frames
    for wx, _ in WINDOWS:
        x, y = wx, WIN_Y
        s.append(f'<rect x="{x}" y="{y}" width="{WIN_W}" height="{WIN_H}" rx="6" fill="url(#fireglow)" stroke="{INK}" stroke-width="3"/>')
        s.append(f'<path d="M{x + 2},{y + 2} L{x + 22},{y + 2} L{x + 9},{y + 20} L{x + 13},{y + 9} Z" fill="{NT["shine"]}" opacity=".8"/>')
        s.append(f'<path d="M{x + WIN_W - 2},{y + WIN_H - 2} L{x + WIN_W - 26},{y + WIN_H - 2} L{x + WIN_W - 8},{y + WIN_H - 18} Z" fill="{NT["glass"]}"/>')
        s.append(f'<path d="M{x + WIN_W - 2},{y + 2} L{x + WIN_W - 14},{y + 2} L{x + WIN_W - 2},{y + 16} Z" fill="{NT["glass"]}"/>')
    # smashed windscreen on the front cab
    xe = CAB_R + 360
    s.append(f'<path d="M{xe - 60},{TOP + 8} L{xe - 32},{TOP + 8} L{xe - 2},{BOT - 64} L{xe - 60},{BOT - 64} Z" fill="url(#fireglow)" opacity=".9"/>')
    s.append(f'<path d="M{xe - 60},{TOP + 8} L{xe - 40},{TOP + 8} L{xe - 52},{TOP + 40} Z M{xe - 20},{BOT - 70} L{xe - 6},{BOT - 70} L{xe - 30},{BOT - 100} Z" fill="{NT["glass"]}"/>')
    # soot blooms above the windows and on the roof
    for cx, cy, rx, ry in [(122, 92, 70, 40), (200, 80, 50, 34), (449, 86, 60, 40), (698, 88, 54, 36),
                           (170, 60, 80, 22), (738, 62, 60, 18), (860, 120, 40, 50)]:
        s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#soot)"/>')
    # dents and scuffs in the lower blue panels (clear of doors): an irregular darker hollow with a crease
    for x, y, w, h in [(160, 196, 44, 20), (430, 200, 40, 18), (760, 194, 50, 22)]:
        s.append(f'<path d="M{x},{y + h * .4} L{x + w * .3},{y} L{x + w * .8},{y + h * .2} L{x + w},{y + h * .7} '
                 f'L{x + w * .5},{y + h} L{x + w * .1},{y + h * .8} Z" fill="{NT["blue_lo"]}" opacity=".75"/>')
        s.append(f'<path d="M{x + w * .2},{y + h * .5} L{x + w * .55},{y + h * .35} L{x + w * .85},{y + h * .6}" '
                 f'fill="none" stroke="{INK}" stroke-width="2" opacity=".55"/>')
    # the rear cab's door hangs off its top rail
    dx = CAB_L + 248
    s.append(f'<rect x="{dx}" y="{TOP + 26}" width="90" height="{BOT - TOP - 26}" fill="#120a0a"/>')
    s.append(f'<g transform="rotate(9 {dx + 4} {TOP + 30})"><rect x="{dx + 4}" y="{TOP + 30}" width="84" height="{BOT - TOP - 30}" rx="6" '
             f'fill="{NT["door"]}" stroke="{INK}" stroke-width="4"/>'
             f'<rect x="{dx + 12}" y="{TOP + 40}" width="30" height="96" rx="4" fill="{NT["glass"]}"/>'
             f'<line x1="{dx + 54}" y1="{TOP + 44}" x2="{dx + 54}" y2="{BOT - 44}" stroke="{NT["rail"]}" stroke-width="4"/></g>')
    # torn roof box on the rear cab, cracked destination sign on the front cab
    s.append(f'<path d="M{CAB_L + 130},{54} L{CAB_L + 150},{46} L{CAB_L + 162},{56} L{CAB_L + 180},{44} L{CAB_L + 196},{54} '
             f'L{CAB_L + 210},{48} L{CAB_L + 210},{72} L{CAB_L + 130},{72} Z" fill="#141012" stroke="{INK}" stroke-width="3"/>')
    fx = CAB_R
    s.append(f'<rect x="{fx + 206}" y="106" width="84" height="22" rx="3" fill="#0e0f12" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M{fx + 214},{108} L{fx + 236},{126} M{fx + 250},{108} L{fx + 240},{120} L{fx + 262},{126}" stroke="#3a3e46" stroke-width="2"/>')
    # a dangling cable from the torn roof
    s.append(f'<path d="M{CAB_L + 200},{60} Q{CAB_L + 214},{90} {CAB_L + 206},{120}" fill="none" stroke="{INK}" stroke-width="3"/>')
    return defs, ''.join(s)


def burning_tram():
    doc, L = new_tram(3)
    defs, body = damage()
    doc = doc.replace('<defs>', '<defs>' + defs, 1).replace('</svg>', body + '</svg>')
    return doc, L


if __name__ == '__main__':
    svg, L = burning_tram()
    render(HIRES, {'tram-burning.svg': svg})
    meta = {'length': L, 'rail': H, 'unitsPerMetre': 50, 'flames': FLAMES, 'smoke': SMOKE}
    (HIRES / 'tram-burning.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote', HIRES / 'tram-burning.json')
