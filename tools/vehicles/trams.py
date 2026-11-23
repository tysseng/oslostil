#!/usr/bin/env python3
"""Trams: the new light-blue Oslo tram (multi-section, low floor) and the two-car Tokyoslo tram.

No company marks or logos. Front faces right.
Usage: python3 tools/vehicles/trams.py  → assets/vehicles/hires/*.svg + .png
"""
from common import HIRES, H, INK, SW, Svg, check_clear, rect, render, window

NT = dict(blue='#3fa3e0', blue_hi='#86c9f1', blue_lo='#2a7fb8', black='#1c2027', glass='#252b34', shine='#5d6c7a',
          door='#2a2f38', rail='#f2c200', roof_box='#2f8ccc')


def small_wheel(cx, r=17):
    cy = H - r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#2b2e36" stroke="{INK}" stroke-width="4"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .45:.1f}" fill="#8b919c" stroke="{INK}" stroke-width="2"/>')


def tram_bogie(cx):
    return rect(cx - 62, H - 38, 124, 22, '#30343d', 6) + small_wheel(cx - 34) + small_wheel(cx + 34)


def module(svg, x0, L, kind, top=70, bot=242):
    """kind: 'cabL' (rear cab, nose left), 'cabR' (front cab, nose right), 'short' (over a bogie) or 'long'."""
    if kind == 'cabR':
        xe = x0 + L
        d = (f'M{x0 + 10},{top} L{xe - 70},{top} Q{xe - 40},{top} {xe - 26},{top + 30} L{xe - 2},{bot - 50} '
             f'Q{xe + 4},{bot - 30} {xe - 4},{bot - 8} Q{xe - 8},{bot} {xe - 20},{bot} L{x0},{bot} L{x0},{top + 10} Q{x0},{top} {x0 + 10},{top} Z')
    elif kind == 'cabL':
        xe = x0 + L
        d = (f'M{xe - 10},{top} L{x0 + 70},{top} Q{x0 + 40},{top} {x0 + 26},{top + 30} L{x0 + 2},{bot - 50} '
             f'Q{x0 - 4},{bot - 30} {x0 + 4},{bot - 8} Q{x0 + 8},{bot} {x0 + 20},{bot} L{xe},{bot} L{xe},{top + 10} Q{xe},{top} {xe - 10},{top} Z')
    else:
        d = f'M{x0 + 8},{top} L{x0 + L - 8},{top} Q{x0 + L},{top} {x0 + L},{top + 8} L{x0 + L},{bot} L{x0},{bot} L{x0},{top + 8} Q{x0},{top} {x0 + 8},{top} Z'
    cid = svg.clip(d)
    g = [f'<path d="{d}" fill="{NT["blue"]}"/>', f'<g clip-path="url(#{cid})">']
    g.append(rect(x0 - 20, top + 14, L + 40, 6, NT['blue_hi'], stroke=False))
    g.append(rect(x0 - 20, top + 24, L + 40, 92, NT['black'], stroke=False))       # dark window band
    g.append(rect(x0 - 20, bot - 16, L + 40, 22, NT['blue_lo'], stroke=False))
    # windows in the dark band (pillars + reflections)
    # explicit layout per module: door x positions and window x positions (windows are 60 wide)
    doors, wins = {
        'long': ([88, 317], [14, 190, 250]),
        'short': ([], [45]),
        'cabL': ([248], [92, 170]),
        'cabR': ([29], [130]),
    }[kind]
    check_clear('tram ' + kind, L, doors, 90, wins, 60, extra=[212] if kind == 'cabR' else [])
    for wx in wins:
        g.append(window(x0 + wx, top + 32, 60, 74, glass=NT['glass'], shine=NT['shine'], rx=6))
    for dx in doors:
        x = x0 + dx
        g.append(rect(x, top + 26, 90, bot - top - 26, NT['door'], 6, sw=4))
        for lx in (x + 6, x + 47):
            g.append(window(lx, top + 34, 37, bot - top - 70, glass=NT['glass'], shine=NT['shine'], rx=4))
        g.append(f'<line x1="{x + 30}" y1="{top + 40}" x2="{x + 30}" y2="{bot - 40}" stroke="{NT["rail"]}" stroke-width="4"/>')
        g.append(f'<line x1="{x + 60}" y1="{top + 40}" x2="{x + 60}" y2="{bot - 40}" stroke="{NT["rail"]}" stroke-width="4"/>')
        g.append(rect(x + 4, bot - 30, 82, 8, '#454b56', 2, stroke=False))
    if kind in ('cabR', 'cabL'):  # raked windscreen seen from the side
        if kind == 'cabR':
            xe = x0 + L
            g.append(f'<path d="M{xe - 64},{top + 4} L{xe - 30},{top + 4} L{xe + 2},{bot - 62} L{xe - 64},{bot - 62} Z" fill="{NT["glass"]}"/>')
            g.append(f'<path d="M{xe - 40},{top + 16} L{xe - 30},{top + 16} L{xe - 10},{bot - 76} L{xe - 20},{bot - 76} Z" fill="{NT["shine"]}" opacity=".7"/>')
        else:
            g.append(f'<path d="M{x0 + 64},{top + 4} L{x0 + 30},{top + 4} L{x0 - 2},{bot - 62} L{x0 + 64},{bot - 62} Z" fill="{NT["glass"]}"/>')
    g.append('</g>')
    g.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{SW + 1}" stroke-linejoin="round"/>')
    svg.add(''.join(g))


def new_tram(sections=5):
    svg = Svg()
    plan = [('cabL', 360), ('short', 150), ('long', 440), ('short', 150), ('cabR', 360)] if sections == 5 else \
           [('cabL', 360), ('short', 150), ('cabR', 360)]
    gap = 14
    xs, x = [], 0
    for _, l in plan:
        xs.append(x); x += l + gap
    L = x - gap
    # bogies behind the body: under the outer end of each cab and under each short module
    for (k, l), x0 in zip(plan, xs):
        if k == 'short':
            svg.add(tram_bogie(x0 + l / 2))
        elif k == 'cabL':
            svg.add(tram_bogie(x0 + 120))
        elif k == 'cabR':
            svg.add(tram_bogie(x0 + l - 120))
    for x0, (_, l) in zip(xs[1:], plan[1:]):  # articulation joints
        svg.add(rect(x0 - gap - 2, 92, gap + 4, 140, '#2a2d34', 3))
    for (k, l), x0 in zip(plan, xs):
        module(svg, x0, l, k)
    # roof equipment boxes
    for (k, l), x0 in zip(plan, xs):
        if k == 'short':
            svg.add(rect(x0 + 10, 52, l - 20, 20, NT['roof_box'], 6, sw=3))
        elif k.startswith('cab'):
            svg.add(rect(x0 + (110 if k == 'cabR' else 90), 54, 160, 18, NT['roof_box'], 6, sw=3))
    mid = xs[len(plan) // 2] + plan[len(plan) // 2][1] / 2
    svg.add(rect(mid - 90, 54, 180, 18, NT['roof_box'], 6, sw=3))   # roof equipment on the middle module
    # destination sign near the front
    fx = xs[-1]
    svg.add(rect(fx + 206, 106, 84, 22, '#14161a', 3, sw=3))   # side destination sign, in its own slot
    svg.add(f'<text x="{fx + 248}" y="122" font-family="monospace" font-weight="700" font-size="14" fill="#ffb21a" text-anchor="middle">17 SINSEN</text>')
    return svg.doc(L, H, 'New Oslo tram (light blue)'), L


JT = dict(green='#2f7a45', green_hi='#4a9a5e', green_lo='#1f5a32', cream='#efe0b0', cream_lo='#d4c08a',
          roof='#2c5e3a', glass='#f2c25a', shine='#ffeab0', door='#2a6a3c', skirt='#1c2a22')


def jcar(svg, x0, L, nose, top=70, bot=242):
    """one car of the Tokyoslo tram: green and cream, rounded nose at the outer end (nose = 'L' or 'R')"""
    xe = x0 + L
    if nose == 'L':
        d = (f'M{x0 + 64},{top} L{xe - 8},{top} Q{xe},{top} {xe},{top + 8} L{xe},{bot} L{x0 + 30},{bot} '
             f'Q{x0 + 2},{bot} {x0 + 2},{bot - 30} L{x0 + 8},{top + 44} Q{x0 + 14},{top} {x0 + 64},{top} Z')
    else:
        d = (f'M{xe - 64},{top} L{x0 + 8},{top} Q{x0},{top} {x0},{top + 8} L{x0},{bot} L{xe - 30},{bot} '
             f'Q{xe - 2},{bot} {xe - 2},{bot - 30} L{xe - 8},{top + 44} Q{xe - 14},{top} {xe - 64},{top} Z')
    cid = svg.clip(d)
    g = [f'<path d="{d}" fill="{JT["green"]}"/>', f'<g clip-path="url(#{cid})">']
    g.append(rect(x0 - 20, top, L + 40, 22, JT['roof'], stroke=False))                 # roof band
    g.append(rect(x0 - 20, top + 22, L + 40, 88, JT['cream'], stroke=False))           # cream window band
    g.append(rect(x0 - 20, top + 102, L + 40, 8, JT['cream_lo'], stroke=False))
    g.append(rect(x0 - 20, top + 110, L + 40, 6, JT['green_lo'], stroke=False))        # thin dark stripe
    g.append(rect(x0 - 20, top + 118, L + 40, 5, JT['green_hi'], stroke=False))
    g.append(rect(x0 - 20, bot - 14, L + 40, 20, JT['skirt'], stroke=False))
    # mirrored layout for the right-hand car
    doors_l, wins_l = [150, 520], [64, 240, 306, 372, 438, 610, 676]
    if nose == 'L':
        doors, wins = doors_l, wins_l
    else:
        doors, wins = [L - x - 80 for x in doors_l], [L - x - 56 for x in wins_l]
    check_clear('tokyo tram', L, doors, 80, wins, 56)
    for wx in wins:   # warm lit windows like the subways
        g.append(window(x0 + wx, top + 32, 56, 64, glass=JT['glass'], shine=JT['shine'], rx=10))
    for dx in doors:
        x = x0 + dx
        g.append(rect(x, top + 26, 80, bot - top - 30, JT['door'], 6, sw=4))
        for lx in (x + 8, x + 44):
            g.append(window(lx, top + 34, 28, 92, glass=JT['glass'], shine=JT['shine'], rx=6))
        g.append(f'<line x1="{x + 40}" y1="{top + 30}" x2="{x + 40}" y2="{bot - 8}" stroke="{INK}" stroke-width="3"/>')
    # the windscreen wrapping round the nose, a headlight and a destination sign
    if nose == 'L':
        g.append(f'<path d="M{x0 + 56},{top + 28} L{x0 + 16},{top + 28} Q{x0 + 8},{top + 30} {x0 + 6},{top + 46} L{x0 + 4},{top + 100} L{x0 + 56},{top + 100} Z" fill="{JT["glass"]}"/>')
        g.append(f'<circle cx="{x0 + 22}" cy="{top + 140}" r="9" fill="#fff6d0" stroke="{INK}" stroke-width="3"/>')
    else:
        g.append(f'<path d="M{xe - 56},{top + 28} L{xe - 16},{top + 28} Q{xe - 8},{top + 30} {xe - 6},{top + 46} L{xe - 4},{top + 100} L{xe - 56},{top + 100} Z" fill="{JT["glass"]}"/>')
        g.append(f'<circle cx="{xe - 22}" cy="{top + 140}" r="9" fill="#fff6d0" stroke="{INK}" stroke-width="3"/>')
    g.append('</g>')
    g.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{SW + 1}" stroke-linejoin="round"/>')
    svg.add(''.join(g))


def tokyo_tram():
    """Tokyoslo tram: two green-and-cream cars, inspired by inspiration/vehicles/Japanese tram.
    Same length (30.3 m) and roof height as tram-new, so the game's tram physics fit unchanged. No pantograph."""
    from common import bogie, bellows
    svg = Svg()
    L, gap = 750, 16
    xs = [0, L + gap]
    for x0 in xs:   # bogies behind the body
        svg.add(bogie(x0 + 150, span=90))
        svg.add(bogie(x0 + L - 150, span=90))
    svg.add(bellows(L - 4, gap + 8, 96, 236))
    jcar(svg, xs[0], L, 'L')
    jcar(svg, xs[1], L, 'R')
    for x0 in xs:   # small roof boxes (no pantograph)
        svg.add(rect(x0 + 260, 56, 120, 16, JT['roof'], 5, sw=3))
        svg.add(rect(x0 + L - 330, 58, 70, 14, '#5a6a5e', 4, sw=3))
    # destination signs in the roof band at both ends
    for sx in (40, 2 * L + gap - 160):
        svg.add(rect(sx + 20, 74, 100, 18, '#14161a', 3, sw=3))
        svg.add(f'<text x="{sx + 70}" y="88" font-family="monospace" font-weight="700" font-size="13" fill="#ffb21a" text-anchor="middle">1 TOKYOSLO</text>')
    Lt = 2 * L + gap
    return svg.doc(Lt, H, 'Tokyoslo tram (two cars, green and cream)'), Lt


if __name__ == '__main__':
    render(HIRES, {
        'tram-new.svg': new_tram(5)[0],
        'tram-new-short.svg': new_tram(3)[0],
        'tram-tokyo.svg': tokyo_tram()[0],
    })
