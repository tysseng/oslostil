#!/usr/bin/env python3
"""Buses: today's red city bus (single and articulated) and the lime-green 3-axle regional bus. (old_bus() is kept but not exported.)

No company marks or logos. Front faces right.
Usage: python3 tools/vehicles/road.py  → assets/vehicles/hires/*.svg + .png
"""
from common import HIRES, H, INK, SW, Svg, check_clear, rect, render, window


def road_wheel(cx, r=27, rim='#8b919c', hubcol='#5b616d'):
    cy = H - r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#24262c" stroke="{INK}" stroke-width="4"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .58:.1f}" fill="{rim}" stroke="{INK}" stroke-width="2.5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .3:.1f}" fill="{hubcol}"/>'
            + ''.join(f'<circle cx="{cx + r * .42 * c:.1f}" cy="{cy + r * .42 * s:.1f}" r="2.2" fill="{INK}"/>'
                      for c, s in ((1, 0), (-1, 0), (0, 1), (0, -1))))


def arch(cx, r, col='#1a1c22'):
    """Dark wheel arch cut into the body (drawn inside the body clip)."""
    return f'<path d="M{cx - r - 9},{H + 2} L{cx - r - 9},{H - r} A{r + 9},{r + 9} 0 0 1 {cx + r + 9},{H - r} L{cx + r + 9},{H + 2} Z" fill="{col}"/>'


def dest_sign(x, y, w, h, txt):
    return (rect(x, y, w, h, '#14161a', 3, sw=3) +
            f'<text x="{x + w / 2}" y="{y + h * .74:.1f}" font-family="monospace" font-weight="700" font-size="{h * .7:.1f}" '
            f'fill="#ffb21a" text-anchor="middle">{txt}</text>')


# =====================================================================================
# Modern red city bus: red body, continuous dark glazing, glazed doors
# =====================================================================================
RB = dict(red='#e0262d', red_hi='#f0525a', red_lo='#a8161c', glass='#1a1d24', shine='#4a5560', roof='#c8202a', skirt='#2a2c32', pod='#b81c24')
# lime-green regional bus («grønn buss»), same build as the red one; keys keep the red bus's names
GB = dict(red='#8cc63f', red_hi='#b6e26a', red_lo='#5f9425', glass='#1a1d24', shine='#4a5560', roof='#7ab32f', skirt='#2a2c32', pod='#6fa52a')


def city_body(svg, x0, L, front, rear, top=98, bot=244):
    """One rigid section. front/rear: True if this section has the bus front/rear end."""
    rf, rr = (34 if front else 6), (18 if rear else 6)
    d = (f'M{x0 + rr},{top} L{x0 + L - rf},{top} Q{x0 + L},{top} {x0 + L},{top + rf} L{x0 + L},{bot - 8} Q{x0 + L},{bot} {x0 + L - 8},{bot} '
         f'L{x0 + 8},{bot} Q{x0},{bot} {x0},{bot - 8} L{x0},{top + rr} Q{x0},{top} {x0 + rr},{top} Z')
    return d


def city_bus(articulated=False, pal=None, three_axle=False, sign='31 SANDVIKA', title='Red city bus'):
    """City/regional bus. articulated = 18 m bendy bus; three_axle = 15 m bus with a tag axle behind the rear axle."""
    RB = pal or globals()['RB']
    svg = Svg()
    top, bot = 98, 244
    if three_axle:
        secs = [(0, 750, True, True)]
        L = 750
        axles = [150, 212, L - 165]   # driven axle + tag axle close together at the back
        doors = [(360, 'mid'), (L - 110, 'front')]   # one door between the wheels
    elif articulated:
        secs = [(0, 330, False, True), (348, 560, True, False)]   # (x, length, front, rear)
        L = 908
        axles = [125, 480, L - 168]   # rear axle well forward: a long rear overhang
        doors = [(196, 'rear'), (356, 'mid'), (560, 'mid'), (L - 110, 'front')]
    else:
        secs = [(0, 600, True, True)]
        L = 600
        axles = [150, L - 165]
        doors = [(250, 'mid'), (L - 110, 'front')]
    # doors and wheel arches must not overlap
    check_clear('city bus', L, [d for d, _ in doors], 84, [a - 36 for a in axles], 72, extra=[])
    if articulated:  # turntable bellows
        svg.add(rect(326, top + 8, 26, bot - top - 16, '#24262c', 4))
        for i in range(1, 8):
            y = top + 8 + (bot - top - 16) * i / 8
            svg.add(f'<line x1="329" y1="{y:.1f}" x2="349" y2="{y:.1f}" stroke="#4a4e58" stroke-width="3"/>')
    for sx, sl, front, rear in secs:
        d = city_body(svg, sx, sl, front, rear, top, bot)
        cid = svg.clip(d)
        g = [f'<path d="{d}" fill="{RB["red"]}"/>', f'<g clip-path="url(#{cid})">']
        g.append(rect(sx - 10, top - 10, sl + 20, 22, RB['roof'], stroke=False))
        g.append(rect(sx - 10, top + 12, sl + 20, 6, RB['red_hi'], stroke=False))
        g.append(rect(sx - 10, top + 20, sl + 20, 74, RB['glass'], stroke=False))    # continuous dark glazing
        for k in range(int(sl / 90) + 1):                                              # pillars + reflections
            px = sx + 40 + k * 90
            g.append(f'<path d="M{px},{top + 22} L{px + 26},{top + 22} L{px + 6},{top + 92} L{px - 20},{top + 92} Z" fill="{RB["shine"]}" opacity=".55"/>')
        g.append(rect(sx - 10, top + 94, sl + 20, 4, RB['red_lo'], stroke=False))
        g.append(rect(sx - 10, bot - 14, sl + 20, 20, RB['skirt'], stroke=False))
        for a in axles:
            if sx - 40 < a < sx + sl + 40:
                g.append(arch(a, 27))
        if front:  # deep windscreen seen from the side
            g.append(f'<path d="M{sx + sl - 30},{top + 4} L{sx + sl + 10},{top + 4} L{sx + sl + 10},{bot - 40} L{sx + sl - 18},{bot - 40} Z" fill="{RB["glass"]}"/>')
            g.append(f'<path d="M{sx + sl - 14},{top + 24} L{sx + sl - 4},{top + 24} L{sx + sl - 12},{bot - 60} L{sx + sl - 22},{bot - 60} Z" fill="{RB["shine"]}" opacity=".7"/>')
        g.append('</g>')
        g.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{SW + 1}" stroke-linejoin="round"/>')
        svg.add(''.join(g))
    # doors: glazed double doors with a red frame
    for dx, _ in doors:
        x = dx
        svg.add(rect(x, top + 14, 84, bot - top - 20, RB['red_lo'], 6, sw=4))
        for lx in (x + 6, x + 44):
            svg.add(window(lx, top + 20, 34, bot - top - 46, glass=RB['glass'], shine=RB['shine'], rx=4))
        svg.add(rect(x + 4, bot - 24, 76, 8, RB['skirt'], 2, stroke=False))
    # destination sign over the front door, roof pods
    fx = L - 118
    ds = sorted(d for d, _ in doors)
    sx_ = ds[-2] + 90                       # between the last two doors, over the glazing
    sw_ = min(140, ds[-1] - 6 - sx_)
    check_clear('city bus sign', L, [d for d, _ in doors], 84, [sx_], sw_)   # the sign must not sit on a door
    svg.add(dest_sign(sx_, top + 26, sw_, 24, sign))
    for rx_ in ([60, 520] if articulated else ([90, 430] if three_axle else [80, 330])):
        svg.add(rect(rx_, top - 16, 180, 18, RB['pod'], 8, sw=3))
    for a in axles:  # wheels in front of the dark arches
        svg.add(road_wheel(a))
    svg.add(rect(L - 10, bot - 30, 14, 12, '#ffe7a8', 3, sw=2))          # headlight edge
    svg.add(rect(-4, bot - 50, 10, 22, '#ff3030', 3, sw=2))              # tail light edge
    return svg.doc(L, H, title + (' (articulated)' if articulated else '')), L


# =====================================================================================
# Old 1960s red bus: rounded roof, framed windows, roof destination box, chrome strip
# =====================================================================================
OB = dict(red='#d8352a', red_lo='#9e2219', red_hi='#ec6a5c', roof='#c42f25', chrome='#d7dade', glass='#2a3038', shine='#6c7a86', cream='#efe6cf')


def old_bus():
    svg = Svg()
    L, top, bot = 560, 104, 238
    axles = [118, 340]
    d = (f'M{40},{top} L{L - 54},{top} Q{L - 6},{top} {L - 2},{top + 50} L{L + 4},{bot - 14} Q{L + 4},{bot} {L - 10},{bot} '
         f'L{14},{bot} Q{0},{bot} {0},{bot - 14} L{0},{top + 44} Q{2},{top} {40},{top} Z')
    cid = svg.clip(d)
    g = [f'<path d="{d}" fill="{OB["red"]}"/>', f'<g clip-path="url(#{cid})">']
    g.append(rect(-10, top - 10, L + 30, 26, OB['roof'], stroke=False))
    g.append(rect(-10, top + 16, L + 30, 6, OB['red_hi'], stroke=False))
    g.append(rect(-10, top + 92, L + 30, 5, OB['chrome'], stroke=False))     # chrome belt line
    g.append(rect(-10, bot - 12, L + 30, 18, OB['red_lo'], stroke=False))
    for a in axles:
        g.append(arch(a, 26, col='#2a1a18'))
    g.append('</g>')
    g.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{SW + 1}" stroke-linejoin="round"/>')
    svg.add(''.join(g))
    doors = [170, L - 136]
    wins = [20, 72, 250, 302, 354]
    check_clear('old bus', L, doors, 70, wins, 46)
    check_clear('old bus arches', L, doors, 70, [a - 35 for a in axles], 70)
    for wx in wins:
        svg.add(window(wx, top + 26, 46, 56, glass=OB['glass'], shine=OB['shine'], rx=9, frame=OB['chrome']))
    for dx in doors:  # folding doors: four narrow glazed panels
        svg.add(rect(dx, top + 22, 70, bot - top - 30, OB['red_lo'], 4, sw=4))
        for k in range(2):
            svg.add(window(dx + 6 + k * 32, top + 28, 26, 58, glass=OB['glass'], shine=OB['shine'], rx=5))
            svg.add(window(dx + 6 + k * 32, top + 94, 26, 36, glass=OB['glass'], shine=OB['shine'], rx=5))
    svg.add(window(L - 46, top + 22, 40, 64, glass=OB['glass'], shine=OB['shine'], rx=10))   # windscreen edge
    svg.add(dest_sign(L - 230, top - 26, 96, 26, 'KAMPEN'))                                     # roof destination box
    svg.add(rect(L - 238, top - 32, 112, 34, 'none', 6, sw=4))
    for a in axles:
        svg.add(road_wheel(a, 26, rim=OB['red'], hubcol=OB['red_lo']))
    svg.add(rect(L - 6, bot - 22, 16, 10, OB['chrome'], 3, sw=2))   # bumpers
    svg.add(rect(-8, bot - 22, 16, 10, OB['chrome'], 3, sw=2))
    return svg.doc(L, H, 'Old red bus (1960s)'), L


if __name__ == '__main__':
    render(HIRES, {
        'bus-red.svg': city_bus(False)[0],
        'bus-red-articulated.svg': city_bus(True)[0],
        'bus-green.svg': city_bus(pal=GB, three_axle=True, sign='79 ÅSBRÅTEN', title='Green regional bus')[0],
    })
