#!/usr/bin/env python3
"""Subway (T-bane) trains: today's white/grey metro and the old red-and-blue one.

No company marks or logos. Front (cab) on the left of the first car and the right of the last car.
Usage: python3 tools/vehicles/subways.py  → assets/vehicles/hires/*.svg + .png
"""
from common import HIRES, H, INK, SW, Svg, bellows, bogie, check_clear, rect, render, window


def body_path(x0, L, kind, top, bot, r_cab, r_end=10, lean=0):
    """Box body; the cab end gets a big rounded top corner (r_cab) and an optional lean at the front."""
    xe = x0 + L
    if kind == 'cab':
        return (f'M{x0 + r_cab},{top} L{xe - r_end},{top} Q{xe},{top} {xe},{top + r_end} L{xe},{bot} L{x0 + 10 + lean},{bot} '
                f'Q{x0 + lean},{bot} {x0 + lean},{bot - 10} L{x0},{top + r_cab} Q{x0},{top} {x0 + r_cab},{top} Z')
    if kind == 'tail':
        return (f'M{xe - r_cab},{top} L{x0 + r_end},{top} Q{x0},{top} {x0},{top + r_end} L{x0},{bot} L{xe - 10 - lean},{bot} '
                f'Q{xe - lean},{bot} {xe - lean},{bot - 10} L{xe},{top + r_cab} Q{xe},{top} {xe - r_cab},{top} Z')
    return (f'M{x0 + r_end},{top} L{xe - r_end},{top} Q{xe},{top} {xe},{top + r_end} L{xe},{bot} L{x0},{bot} '
            f'L{x0},{top + r_end} Q{x0},{top} {x0 + r_end},{top} Z')


# =====================================================================================
# New metro: light grey/white body, dark window line, grey sliding doors, warm lit interior
# =====================================================================================
MX = dict(body='#e8eaeb', body_hi='#f7f8f8', body_lo='#c3c7cb', roof='#d4d7da', band='#3b4048', door='#626973', door_lo='#4b515a', glass='#2a2f36', lit='#f3c76a', lit_hi='#ffe3a3', shine='#59636e', under='#2c3036')


def lit_window(x, y, w, h, rx=6):
    """Window with a warm, lit interior (as the new metro looks in the photos)."""
    s = rect(x, y, w, h, MX['lit'], rx, sw=3)
    s += rect(x + 3, y + 3, w - 6, h * .3, MX['lit_hi'], rx - 2, stroke=False)
    s += f'<line x1="{x + w * .3:.1f}" y1="{y + h * .45:.1f}" x2="{x + w * .3:.1f}" y2="{y + h - 3:.1f}" stroke="#c98d2b" stroke-width="3"/>'  # pole
    s += f'<path d="M{x + w * .55:.1f},{y + 3} L{x + w * .7:.1f},{y + 3} L{x + w * .45:.1f},{y + h - 3} L{x + w * .3:.1f},{y + h - 3} Z" fill="#ffffff" opacity=".25"/>'
    return s


def metro_car(svg, x0, L, kind):
    top, bot = 52, 226
    xe = x0 + L
    slant = 24  # the cab ends lean back (steeply): the roof edge sits further in than the bottom
    if kind == 'cab':
        d = (f'M{x0 + slant + 12},{top} L{xe - 10},{top} Q{xe},{top} {xe},{top + 10} L{xe},{bot} L{x0 + 8},{bot} '
             f'Q{x0},{bot} {x0},{bot - 8} L{x0},{bot - 40} L{x0 + slant},{top + 12} Q{x0 + slant + 2},{top} {x0 + slant + 12},{top} Z')
    elif kind == 'tail':
        d = (f'M{xe - slant - 12},{top} L{x0 + 10},{top} Q{x0},{top} {x0},{top + 10} L{x0},{bot} L{xe - 8},{bot} '
             f'Q{xe},{bot} {xe},{bot - 8} L{xe},{bot - 40} L{xe - slant},{top + 12} Q{xe - slant - 2},{top} {xe - slant - 12},{top} Z')
    else:
        d = body_path(x0, L, kind, top, bot, r_cab=10)
    cid = svg.clip(d)
    g = [f'<path d="{d}" fill="{MX["body"]}"/>', f'<g clip-path="url(#{cid})">']
    g.append(rect(x0 - 20, top - 10, L + 40, 26, MX['roof'], stroke=False))
    g.append(rect(x0 - 20, top + 16, L + 40, 6, MX['body_hi'], stroke=False))
    g.append(rect(x0 - 20, top + 30, L + 40, 66, MX['band'], stroke=False))       # dark window line
    g.append(rect(x0 - 20, bot - 26, L + 40, 32, MX['body_lo'], stroke=False))
    g.append(rect(x0 - 20, bot - 8, L + 40, 14, MX['under'], stroke=False))
    # layout in hi-res units for a 900-long car (doors 100 wide, windows 100 wide)
    if kind == 'cab':
        doors, wins = [216, 558], [330, 440, 680]
    elif kind == 'tail':  # mirror of the cab car
        doors, wins = [L - 316, L - 658], [L - 430, L - 540, L - 780]
    else:
        doors, wins = [180, 558], [30, 296, 416, 690]
    ws = sorted(wins)
    assert all(b - a >= 104 for a, b in zip(ws, ws[1:])), f'metro {kind}: windows overlap'
    check_clear('metro ' + kind, L, doors, 100, wins, 100)
    for wx in wins:
        g.append(lit_window(x0 + wx, top + 35, 100, 58))
    for dx in doors:  # grey double sliding doors, full height, with tall windows
        x = x0 + dx
        g.append(rect(x, top + 24, 100, bot - top - 26, MX['door'], 6))
        g.append(f'<line x1="{x + 50}" y1="{top + 26}" x2="{x + 50}" y2="{bot - 4}" stroke="{INK}" stroke-width="3"/>')
        for lx in (x + 10, x + 58):
            g.append(lit_window(lx, top + 34, 32, 76, rx=5))
        g.append(rect(x + 4, bot - 24, 92, 10, MX['door_lo'], 3, stroke=False))
    if kind in ('cab', 'tail'):  # small cab side window, body colour all the way to the slanted end
        cx = x0 + 70 if kind == 'cab' else xe - 130
        bx0, bx1 = (x0 - 20, cx + 74) if kind == 'cab' else (cx - 14, xe + 20)
        g.append(rect(bx0, top + 26, bx1 - bx0, 74, MX['body'], 0, stroke=False))   # dark band stops before the cab
        g.append(window(cx, top + 34, 60, 64, glass=MX['glass'], shine=MX['shine'], rx=10))
    g.append('</g>')
    g.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{SW + 1}" stroke-linejoin="round"/>')
    # roof equipment
    for rx_ in ([L * .3] if kind != 'mid' else [L * .25, L * .6]):
        g.append(rect(x0 + rx_, top - 16, 170, 18, '#b8bdc2', 7, sw=3))
    g.append(rect(x0 + L * .3, bot, L * .4, 16, '#3a3f48', 4, sw=3))              # underfloor box
    svg.add(''.join(g))


def metro_new(cars=3):
    svg = Svg()
    L, gap = 900, 20
    xs = [i * (L + gap) for i in range(cars)]
    kinds = ['cab'] + ['mid'] * (cars - 2) + ['tail']
    for x in xs:
        svg.add(bogie(x + 170, 90, frame='#2c3036') + bogie(x + L - 170, 90, frame='#2c3036'))
    for x in xs[:-1]:  # full-width gangway bellows
        svg.add(bellows(x + L - 8, gap + 16, 64, 224, col='#3a3f48'))
    for x, k in zip(xs, kinds):
        metro_car(svg, x, L, k)
    w = cars * L + (cars - 1) * gap
    return svg.doc(w, H, 'Metro train, new (light grey)'), w


# =====================================================================================
# Old metro: red body, blue panels around windows and doors, rounded cab roof
# =====================================================================================
OT = dict(red='#d9362b', red_hi='#ec5f52', red_lo='#a3251d', roof='#c22f25', blue='#2f56b5', blue_lo='#22408a', blue_hi='#4a72d1',
          glass='#273039', shine='#64748a', under='#2c2e34')


def metro_old_car(svg, x0, L, kind):
    top, bot = 56, 226
    d = body_path(x0, L, kind, top, bot, r_cab=8, r_end=8)
    cid = svg.clip(d)
    g = [f'<path d="{d}" fill="{OT["red"]}"/>', f'<g clip-path="url(#{cid})">']
    g.append(rect(x0 - 20, top - 10, L + 40, 26, OT['roof'], stroke=False))
    g.append(rect(x0 - 20, top + 16, L + 40, 5, OT['red_hi'], stroke=False))
    g.append(rect(x0 - 20, bot - 22, L + 40, 28, OT['red_lo'], stroke=False))
    # Blue panels fill the space between the doors (and out towards the car ends); windows sit centred in them.
    # Layout in hi-res units for an 860-long car: door positions (80 wide) and the window count of each segment.
    if kind == 'cab':
        doors, counts = [100, 345, 650], [1, 2, 3, 1]
    elif kind == 'tail':  # mirror of the cab car
        doors, counts = [130, 435, 680], [1, 3, 2, 1]
    else:
        doors, counts = [40, 345, 655], [0, 3, 3, 1]
    edges = [0] + [e for d in doors for e in (d, d + 80)] + [L]
    for i, n in enumerate(counts):
        a_, b_ = edges[2 * i], edges[2 * i + 1]
        if n == 0:
            continue
        pa = a_ + (16 if a_ == 0 else 7)
        pb = b_ - (16 if b_ == L else 7)
        check_clear('old metro ' + kind, L, doors, 80, [pa], pb - pa)
        g.append(rect(x0 + pa, top + 28, pb - pa, 84, OT['blue'], 4, sw=3))
        g.append(rect(x0 + pa + 2, top + 30, pb - pa - 4, 5, OT['blue_hi'], 2, stroke=False))
        total = n * 52 + (n - 1) * 12
        assert total <= pb - pa - 8, f'old metro {kind}: {n} windows do not fit between {a_} and {b_}'
        wx0 = (pa + pb) / 2 - total / 2
        for k in range(n):
            g.append(window(x0 + wx0 + k * 64, top + 40, 52, 58, glass=OT['glass'], shine=OT['shine'], rx=6))
    for dx in doors:  # blue double doors
        x = x0 + dx
        g.append(rect(x, top + 20, 80, bot - top - 22, OT['blue'], 4))
        g.append(f'<line x1="{x + 40}" y1="{top + 22}" x2="{x + 40}" y2="{bot - 2}" stroke="{INK}" stroke-width="3"/>')
        g.append(window(x + 8, top + 30, 24, 70, glass=OT['glass'], shine=OT['shine'], rx=4))
        g.append(window(x + 48, top + 30, 24, 70, glass=OT['glass'], shine=OT['shine'], rx=4))
        g.append(rect(x + 2, bot - 20, 76, 10, OT['blue_lo'], 2, stroke=False))
    g.append('</g>')
    g.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{SW + 1}" stroke-linejoin="round"/>')
    for vx in [L * (.2 + .2 * i) for i in range(4)]:  # roof vents
        g.append(rect(x0 + vx, top - 10, 50, 12, '#a8261d', 5, sw=3))
    g.append(rect(x0 + L * .3, bot, L * .4, 16, OT['under'], 4, sw=3))
    svg.add(''.join(g))


def metro_old(cars=3):
    svg = Svg()
    L, gap = 860, 28
    xs = [i * (L + gap) for i in range(cars)]
    kinds = ['cab'] + ['mid'] * (cars - 2) + ['tail']
    for x in xs:
        svg.add(bogie(x + 150, 86, frame='#33363d') + bogie(x + L - 150, 86, frame='#33363d'))
    # single-carriage units: no gangways between the cars
    for x, k in zip(xs, kinds):
        metro_old_car(svg, x, L, k)
    w = cars * L + (cars - 1) * gap
    return svg.doc(w, H, 'Metro train, old (red and blue)'), w


if __name__ == '__main__':
    render(HIRES, {
        'subway-new.svg': metro_new(3)[0],
        'subway-new-2.svg': metro_new(2)[0],
        'subway-old.svg': metro_old(3)[0],
        'subway-old-2.svg': metro_old(2)[0],
    })
