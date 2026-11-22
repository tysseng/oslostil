#!/usr/bin/env python3
"""Trains: Vy-style green local train (FLIRT), the «tomatsuppe» (NSB type 69) and the airport express.

Usage: python3 tools/vehicles/trains.py  → assets/vehicles/hires/*.svg + .png
"""
from common import *  # noqa: F401,F403
from common import HIRES, H, INK, SW, Svg, bellows, bogie, check_clear, rect, render, window

# =====================================================================================
# Vy «grønt lokaltog» – Stadler FLIRT (type 75), dark green with grey roof
# =====================================================================================
FL = dict(green='#0f6153', green_hi='#1f7d6b', green_lo='#0a4339', roof='#c6cbd0', roof_lo='#9aa1a8',
          door='#17725f', door_frame='#2b3a3e', skirt='#1f2a2e')


def flirt_car(svg, x0, L, kind):
    """kind: 'cab' (nose on the left), 'mid', or 'tail' (nose on the right)."""
    top, bot = 26, 226
    nose = 170
    if kind == 'cab':
        d = (f'M{x0 + nose},{top} L{x0 + L - 14},{top} Q{x0 + L},{top} {x0 + L},{top + 14} L{x0 + L},{bot} '
             f'L{x0 + 34},{bot} Q{x0 + 2},{bot} {x0 + 4},{bot - 30} L{x0 + 14},{bot - 82} '
             f'Q{x0 + 52},{top + 22} {x0 + nose},{top} Z')
    elif kind == 'tail':
        xe = x0 + L
        d = (f'M{xe - nose},{top} L{x0 + 14},{top} Q{x0},{top} {x0},{top + 14} L{x0},{bot} '
             f'L{xe - 34},{bot} Q{xe - 2},{bot} {xe - 4},{bot - 30} L{xe - 14},{bot - 82} '
             f'Q{xe - 52},{top + 22} {xe - nose},{top} Z')
    else:
        d = f'M{x0 + 14},{top} L{x0 + L - 14},{top} Q{x0 + L},{top} {x0 + L},{top + 14} L{x0 + L},{bot} L{x0},{bot} L{x0},{top + 14} Q{x0},{top} {x0 + 14},{top} Z'
    cid = svg.clip(d)
    g = [f'<path d="{d}" fill="{FL["green"]}"/>', f'<g clip-path="url(#{cid})">']
    g.append(rect(x0 - 20, top - 10, L + 40, 50, FL['roof'], stroke=False))           # grey roof
    g.append(rect(x0 - 20, top + 34, L + 40, 6, FL['roof_lo'], stroke=False))
    g.append(rect(x0 - 20, top + 40, L + 40, 10, FL['green_hi'], stroke=False))       # light edge under the roof
    g.append(rect(x0 - 20, bot - 22, L + 40, 30, FL['green_lo'], stroke=False))       # darker lower edge
    g.append(rect(x0 - 20, 158, L + 40, 4, '#5fa898', stroke=False, extra=' opacity=".7"'))  # thin light line
    # windows and doors
    if kind == 'mid':
        doors, wins = [L * .22, L * .72], [L * .05, L * .37, L * .48, L * .59, L * .86]
    elif kind == 'cab':
        doors, wins = [L * .62], [L * .44, L * .78, L * .89]
    else:
        doors, wins = [L * .30], [L * .05, L * .16, L * .48]
    check_clear('flirt ' + kind, L, [d - 10 for d in doors], 104, wins, 78)
    for wx in wins:
        g.append(window(x0 + wx, 74, 78, 66, frame='#24363a'))
    for dx in doors:
        x = x0 + dx
        g.append(rect(x - 10, top + 30, 104, bot - top - 26, FL['door_frame'], 6, stroke=False))   # dark surround
        g.append(rect(x, top + 42, 41, bot - top - 46, FL['door'], 5, sw=3))
        g.append(rect(x + 43, top + 42, 41, bot - top - 46, FL['door'], 5, sw=3))
        g.append(window(x + 7, 80, 27, 74, rx=5))
        g.append(window(x + 50, 80, 27, 74, rx=5))
        g.append(rect(x + 30, 170, 24, 8, '#d8f3ea', 3, sw=2))                       # door button strip
    # cab: side window along the sloping nose
    if kind in ('cab', 'tail'):
        if kind == 'cab':
            g.append(f'<path d="M{x0 + 40},{150} L{x0 + 86},{78} Q{x0 + 120},{56} {x0 + 178},{54} L{x0 + 186},{54} L{x0 + 186},{150} Z" fill="#1d2a33" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
            g.append(f'<path d="M{x0 + 120},{60} L{x0 + 150},{58} L{x0 + 96},{146} L{x0 + 70},{146} Z" fill="#4b6b78" opacity=".7"/>')
            g.append(rect(x0 + 200, 74, 54, 66, '#1d2a33', 7, sw=3))                     # cab door window
            g.append(f'<line x1="{x0 + 194}" y1="{top + 40}" x2="{x0 + 194}" y2="{bot - 6}" stroke="{FL["green_lo"]}" stroke-width="4"/>')
            g.append(f'<line x1="{x0 + 262}" y1="{top + 40}" x2="{x0 + 262}" y2="{bot - 6}" stroke="{FL["green_lo"]}" stroke-width="4"/>')
        else:
            xe = x0 + L
            g.append(f'<path d="M{xe - 40},{150} L{xe - 86},{78} Q{xe - 120},{56} {xe - 178},{54} L{xe - 186},{54} L{xe - 186},{150} Z" fill="#1d2a33" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
            g.append(f'<path d="M{xe - 128},{58} L{xe - 104},{58} L{xe - 154},{146} L{xe - 178},{146} Z" fill="#4b6b78" opacity=".7"/>')
            g.append(rect(xe - 254, 74, 54, 66, '#1d2a33', 7, sw=3))
            g.append(f'<line x1="{xe - 194}" y1="{top + 40}" x2="{xe - 194}" y2="{bot - 6}" stroke="{FL["green_lo"]}" stroke-width="4"/>')
            g.append(f'<line x1="{xe - 262}" y1="{top + 40}" x2="{xe - 262}" y2="{bot - 6}" stroke="{FL["green_lo"]}" stroke-width="4"/>')
    g.append('</g>')
    g.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{SW + 1}" stroke-linejoin="round"/>')
    # roof equipment (AC units)
    for k, rx_ in enumerate([L * .3, L * .62] if kind == 'mid' else ([L * .5] if kind == 'cab' else [L * .32])):
        g.append(rect(x0 + rx_, top - 18, 150, 20, FL['roof_lo'], 6, sw=3))
        g.append(rect(x0 + rx_ + 14, top - 14, 40, 8, '#7d848c', 3, stroke=False))
        g.append(rect(x0 + rx_ + 90, top - 14, 40, 8, '#7d848c', 3, stroke=False))
    # skirt + underfloor boxes
    nx = x0 + (60 if kind == 'cab' else 30)
    g.append(rect(nx, bot - 2, L - 90 if kind != 'mid' else L - 60, 14, FL['skirt'], 4, sw=3))
    for bx in ([L * .35, L * .55] if kind == 'mid' else [L * .4]):
        g.append(rect(x0 + bx, bot + 8, 110, 16, '#3a3f48', 4, sw=3))
    svg.add(''.join(g))


def flirt_train(cars=3):
    svg = Svg()
    L, gap = 1000, 18
    kinds = ['cab'] + ['mid'] * (cars - 2) + ['tail']
    xs = [i * (L + gap) for i in range(cars)]
    # bogies: end bogies under the cabs, shared (Jacobs) bogies at the joints
    under = [bogie(xs[0] + 240)] + [bogie(x + L + gap / 2) for x in xs[:-1]] + [bogie(xs[-1] + L - 240)]
    svg.add(''.join(under))  # behind the body
    for x in xs[:-1]:
        svg.add(bellows(x + L - 6, gap + 12, 44, 222))
    for x, k in zip(xs, kinds):
        flirt_car(svg, x, L, k)
    w = cars * L + (cars - 1) * gap
    return svg.doc(w, H, 'Vy local train (FLIRT, green)'), w


# =====================================================================================
# NSB type 69 «tomatsuppe» – red/orange lower body, grey window band, orange doors
# =====================================================================================
TS = dict(red='#e2392b', red_lo='#b52a20', red_hi='#f0604e', grey='#b8bdc2', grey_lo='#8e959c', roof='#d3d6d9',
          door='#f47b29', door_lo='#c95e18', stripe='#e9e6e2')


def t69_car(svg, x0, L, kind):
    top, bot = 30, 226
    if kind == 'cab':
        d = (f'M{x0 + 46},{top} L{x0 + L - 12},{top} Q{x0 + L},{top} {x0 + L},{top + 12} L{x0 + L},{bot} '
             f'L{x0 + 18},{bot} Q{x0 + 4},{bot} {x0 + 4},{bot - 14} L{x0 + 8},{top + 60} Q{x0 + 12},{top} {x0 + 46},{top} Z')
    elif kind == 'tail':
        xe = x0 + L
        d = (f'M{xe - 46},{top} L{x0 + 12},{top} Q{x0},{top} {x0},{top + 12} L{x0},{bot} '
             f'L{xe - 18},{bot} Q{xe - 4},{bot} {xe - 4},{bot - 14} L{xe - 8},{top + 60} Q{xe - 12},{top} {xe - 46},{top} Z')
    else:
        d = f'M{x0 + 12},{top} L{x0 + L - 12},{top} Q{x0 + L},{top} {x0 + L},{top + 12} L{x0 + L},{bot} L{x0},{bot} L{x0},{top + 12} Q{x0},{top} {x0 + 12},{top} Z'
    cid = svg.clip(d)
    g = [f'<path d="{d}" fill="{TS["red"]}"/>', f'<g clip-path="url(#{cid})">']
    g.append(rect(x0 - 20, top - 10, L + 40, 30, TS['roof'], stroke=False))          # light grey roof edge
    g.append(rect(x0 - 20, top + 20, L + 40, 14, TS['red'], stroke=False))           # red band under the roof
    g.append(rect(x0 - 20, top + 34, L + 40, 98, TS['grey'], stroke=False))          # grey window band
    g.append(rect(x0 - 20, top + 34, L + 40, 5, TS['grey_lo'], stroke=False))
    g.append(rect(x0 - 20, top + 128, L + 40, 6, TS['red_hi'], stroke=False))
    for y in (182, 196):                                                              # thin pinstripes
        g.append(rect(x0 - 20, y, L + 40, 3, TS['stripe'], stroke=False, extra=' opacity=".85"'))
    g.append(rect(x0 - 20, bot - 14, L + 40, 20, TS['red_lo'], stroke=False))
    # doors near both ends of every car (double-leaf, orange)
    if kind == 'cab':
        doors = [L * .17, L * .84]
        wins = [L * (.30 + .1 * i) for i in range(5)]
    elif kind == 'tail':
        doors = [L * .05, L * .72]
        wins = [L * (.18 + .1 * i) for i in range(5)]
    else:
        doors = [L * .05, L * .86]
        wins = [L * (.17 + .1 * i) for i in range(6)]
    check_clear('type69 ' + kind, L, doors, 84, wins, 74)
    for wx in wins:
        g.append(window(x0 + wx, 74, 74, 60, glass='#262b33', shine='#59656f', rx=6, frame='#9da3a9'))
    for dx in doors:
        x = x0 + dx
        g.append(rect(x, top + 22, 84, bot - top - 18, TS['door'], 5))
        g.append(f'<line x1="{x + 42}" y1="{top + 24}" x2="{x + 42}" y2="{bot - 2}" stroke="{INK}" stroke-width="3"/>')
        g.append(rect(x + 2, bot - 18, 80, 12, TS['door_lo'], 3, stroke=False))
        g.append(window(x + 9, 76, 25, 66, glass='#262b33', shine='#59656f', rx=5))
        g.append(window(x + 50, 76, 25, 66, glass='#262b33', shine='#59656f', rx=5))
    if kind in ('cab', 'tail'):  # cab side window + grey cab end
        if kind == 'cab':
            g.append(rect(x0 - 10, top - 10, 40, bot - top + 20, TS['grey'], stroke=False))
            g.append(rect(x0 + 26, top + 34, 8, 140, TS['grey_lo'], stroke=False, extra=' opacity=".6"'))
            g.append(window(x0 + 54, 72, 72, 64, glass='#262b33', shine='#59656f', rx=8, frame='#9da3a9'))
        else:
            xe = x0 + L
            g.append(rect(xe - 30, top - 10, 40, bot - top + 20, TS['grey'], stroke=False))
            g.append(rect(xe - 34, top + 34, 8, 140, TS['grey_lo'], stroke=False, extra=' opacity=".6"'))
            g.append(window(xe - 126, 72, 72, 64, glass='#262b33', shine='#59656f', rx=8, frame='#9da3a9'))
    g.append('</g>')
    g.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{SW + 1}" stroke-linejoin="round"/>')
    # roof ventilators
    for vx in [L * (.25 + .18 * i) for i in range(4)]:
        g.append(rect(x0 + vx, top - 10, 46, 12, '#9aa1a8', 5, sw=3))
    # underfloor
    for bx in [L * .32, L * .52]:
        g.append(rect(x0 + bx, bot + 2, 130, 18, '#3a3f48', 4, sw=3))
    svg.add(''.join(g))


def t69_train(cars=3):
    svg = Svg()
    L, gap = 900, 26
    kinds = ['cab'] + ['mid'] * (cars - 2) + ['tail']
    xs = [i * (L + gap) for i in range(cars)]
    for x in xs[:-1]:
        svg.add(bellows(x + L - 6, gap + 12, 60, 222))
    for x in xs:  # two bogies per car, drawn first so they sit behind the body
        svg.add(bogie(x + 150, 86, frame='#3b3f47') + bogie(x + L - 150, 86, frame='#3b3f47'))
    for i, (x, k) in enumerate(zip(xs, kinds)):
        t69_car(svg, x, L, k)
    w = cars * L + (cars - 1) * gap
    return svg.doc(w, H, 'NSB type 69 local train («tomatsuppe»)'), w


# =====================================================================================
# Airport express – silver with a long nose, charcoal mask and orange outlines
# =====================================================================================
AX = dict(silver='#aeb4ba', silver_hi='#c9ced3', silver_lo='#8b9198', roof='#d5d9dc', dark='#2c3036',
          band='#474d55', orange='#ff6a13')


def airport_car(svg, x0, L, kind):
    """kind: 'cab' (long nose on the left) or 'mid'. The tail cab is the cab mirrored (see airport_train)."""
    top, bot = 30, 226
    nose = 340
    if kind == 'cab':
        d = (f'M{x0 + nose},{top} L{x0 + L - 14},{top} Q{x0 + L},{top} {x0 + L},{top + 14} L{x0 + L},{bot} '
             f'L{x0 + 70},{bot} Q{x0 + 6},{bot} {x0 + 2},{bot - 36} Q{x0},{bot - 84} {x0 + 70},{bot - 112} '
             f'Q{x0 + 210},{top + 4} {x0 + nose},{top} Z')
    else:
        d = f'M{x0 + 14},{top} L{x0 + L - 14},{top} Q{x0 + L},{top} {x0 + L},{top + 14} L{x0 + L},{bot} L{x0},{bot} L{x0},{top + 14} Q{x0},{top} {x0 + 14},{top} Z'
    cid = svg.clip(d)
    g = [f'<path d="{d}" fill="{AX["silver"]}"/>', f'<g clip-path="url(#{cid})">']
    g.append(rect(x0 - 20, top - 10, L + 40, 38, AX['roof'], stroke=False))
    g.append(rect(x0 - 20, top + 28, L + 40, 9, AX['silver_lo'], stroke=False))
    for i in range(int(L / 26) + 2):  # orange hatched stripe along the roof edge
        x = x0 - 10 + i * 26
        g.append(f'<path d="M{x},{top + 37} L{x + 12},{top + 28} L{x + 22},{top + 28} L{x + 10},{top + 37} Z" fill="{AX["orange"]}"/>')
    g.append(rect(x0 - 20, top + 40, L + 40, 12, AX['silver_hi'], stroke=False))      # shine
    g.append(rect(x0 - 20, bot - 38, L + 40, 46, AX['dark'], stroke=False))           # charcoal lower band
    g.append(rect(x0 - 20, bot - 42, L + 40, 4, AX['silver_lo'], stroke=False))
    if kind == 'cab':
        # charcoal mask from the nose, along the cab, outlined in orange
        mask = (f'M{x0 + 24},{bot - 46} Q{x0 + 70},{bot - 112} {x0 + 170},{top + 58} L{x0 + 330},{top + 46} '
                f'L{x0 + 452},{top + 46} L{x0 + 452},{bot - 38} L{x0 + 60},{bot - 38} Q{x0 + 34},{bot - 38} {x0 + 24},{bot - 46} Z')
        g.append(f'<path d="{mask}" fill="{AX["dark"]}" stroke="{AX["orange"]}" stroke-width="9" stroke-linejoin="round"/>')
        # windscreen: a glass strip along the upper edge of the mask
        g.append(f'<path d="M{x0 + 96},{bot - 104} Q{x0 + 170},{top + 66} {x0 + 236},{top + 58} L{x0 + 242},{top + 82} '
                 f'Q{x0 + 180},{top + 90} {x0 + 118},{bot - 90} Z" fill="#1b2026" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
        g.append(f'<path d="M{x0 + 170},{top + 70} L{x0 + 196},{top + 64} L{x0 + 150},{top + 96} L{x0 + 132},{top + 102} Z" fill="#5d6a76" opacity=".7"/>')
        g.append(window(x0 + 240, 86, 62, 56, glass='#1b2026', shine='#5d6a76', rx=10))   # cab side window
        doors, wins = [L * .5, L * .86], [L * .63, L * .73]
    else:
        doors, wins = [L * .1, L * .8], [L * (.22 + .11 * i) for i in range(5)]
    g.append(rect(x0 + (L * .58 if kind == 'cab' else L * .2), 82, (L * .2 if kind == 'cab' else L * .56), 70, AX['band'], 10, stroke=False))
    check_clear('airport ' + kind, L, [d - 8 for d in doors], 106, wins, 74)
    for wx in wins:
        g.append(window(x0 + wx, 88, 74, 58, glass='#1b2026', shine='#5d6a76', rx=12))
    for dx in doors:
        x = x0 + dx
        g.append(rect(x, top + 44, 90, bot - top - 48, AX['dark'], 8, stroke=False, extra=f' stroke="{AX["orange"]}" stroke-width="8"'))
        g.append(window(x + 20, 86, 50, 62, glass='#1b2026', shine='#5d6a76', rx=8))
        g.append(rect(x + 30, 166, 30, 5, '#8b9198', 2, stroke=False))
    g.append('</g>')
    g.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{SW + 1}" stroke-linejoin="round"/>')
    g.append(rect(x0 + (L * .45 if kind == 'cab' else L * .35), top - 14, 200, 16, '#b9bec3', 8, sw=3))  # roof fairing
    return ''.join(g)


def airport_train(cars=3):
    svg = Svg()
    L, gap = 1000, 18
    w = cars * L + (cars - 1) * gap
    xs = [i * (L + gap) for i in range(cars)]
    for x in xs:
        svg.add(bogie(x + 230, 96, frame='#2c3036') + bogie(x + L - 170, 96, frame='#2c3036'))
    for x in xs[:-1]:
        svg.add(bellows(x + L - 6, gap + 12, 48, 222))
    for i, x in enumerate(xs):
        if i == 0:
            svg.add(airport_car(svg, x, L, 'cab'))
        elif i == cars - 1:  # the tail cab is the front cab mirrored
            svg.add(f'<g transform="translate({2 * x + L},0) scale(-1,1)">{airport_car(svg, x, L, "cab")}</g>')
        else:
            svg.add(airport_car(svg, x, L, 'mid'))
    return svg.doc(w, H, 'Airport express train'), w


if __name__ == '__main__':
    render(HIRES, {
        'local-train-green.svg': flirt_train(3)[0],
        'local-train-green-cab.svg': flirt_train(2)[0],
        'local-train-tomato-soup.svg': t69_train(3)[0],
        'local-train-tomato-soup-cab.svg': t69_train(2)[0],
        'airport-express.svg': airport_train(3)[0],
        'airport-express-cab.svg': airport_train(2)[0],
    })
