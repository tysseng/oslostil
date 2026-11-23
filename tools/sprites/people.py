#!/usr/bin/env python3
"""Street enemies drawn from one human skeleton (the ninjas' pose system), facing LEFT.

1) Thugs, used in place of the ninjas before ninja mode — same frame layout as ninjas.png, so the
   game can run them with the same code (src/ninjas.ts):
     thug    shaved head, black leather jacket, white tee, dark jeans, boots; punches
     punk    pink mohawk, studded denim vest, red tartan trousers, boots; punches with a studded cuff
     tagger  orange hoodie (hood up), bandana, baggy jeans, a spray can; sprays a pink burst
   plus an extra row for the tagger's spray mode (painting the subway): 4 frames with a slightly
   transparent pink mist.
   → assets/sprites/thugs.png + thugs.json

2) Zombie passengers, replacing the ticket bot and its CHILD/ADULT/STUDENT/SENIOR label: ordinary
   clothes, pallid skin and red glowing eyes; they shamble with their arms out.
     adult    grown woman, yellow bob, beige trench coat, handbag ............ 30 px
     child    small child, red cap, striped tee, shorts ...................... 21 px
     senior   old man, grey fringe, brown cardigan, rolled-up newspaper ...... 28 px, stooped
     student  teenager, beanie, green hoodie, backpack, a joint with smoke ... 29 px
   → assets/sprites/passengers.png + passengers.json

Cells are 40 × 32 like the ninjas: body centred on x = 20, feet on the bottom row.
Usage: python3 tools/sprites/people.py
"""
import json
import math
import random
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from props import RAMP, rgb, mix  # noqa: E402
from ninjas import N, pose as ninja_pose, COLS as NINJA_COLS, ANIMS as NINJA_ANIMS, FPS as NINJA_FPS, CELL_W, CELL_H  # noqa: E402

CX = CELL_W // 2
GY = CELL_H - 2

R = lambda *c: [rgb(x) for x in c]
RAMP.update({
    'skinT':   R('#4a2a1c', '#8a5a40', '#c08a68', '#e0ac88', '#f4c8a6', '#ffe4cc'),   # thugs
    'pale':    R('#2a3028', '#5a6656', '#86927e', '#a8b49c', '#c8d2b8', '#e4ecd4'),   # zombie skin
    'eyeR':    R('#3a0000', '#8a0000', '#d00010', '#ff2020', '#ff8070', '#ffffff'),
    'leather': R('#0a0a0e', '#16161c', '#24242c', '#34343e', '#4c4c5a', '#787888'),
    'tee':     R('#4a4a50', '#9a9aa4', '#c8c8d0', '#e8e8ee', '#f8f8fc', '#ffffff'),
    'jeans':   R('#0e1626', '#1c2a46', '#2a3e66', '#3a5488', '#5272ac', '#86a2d0'),
    'boot':    R('#0c0806', '#1e140e', '#2e2016', '#422e20', '#5a4030', '#7a5a44'),
    'denim':   R('#14223a', '#284268', '#3a5c8c', '#5078ac', '#6e96c8', '#a8c4e4'),
    'tartan':  R('#2a0408', '#5a0a12', '#900e1c', '#c01c2a', '#e04048', '#ff8a8a'),
    'mohawk':  R('#4a0a30', '#8a1458', '#c81e80', '#ff3aa8', '#ff7ac8', '#ffc4e6'),
    'hoodie':  R('#3a1404', '#7a2c08', '#b04410', '#e0661c', '#ff8a3a', '#ffc08a'),
    'band':    R('#04141e', '#0a2a3c', '#124058', '#1c5a7a', '#3080a8', '#70b8dc'),
    'can':     R('#101418', '#2a3038', '#5a6470', '#8a96a4', '#c0c8d2', '#ffffff'),
    'pink':    R('#5a0a34', '#a01a5e', '#e0308a', '#ff5aa8', '#ff9acc', '#ffd6ec'),
    'trench':  R('#3a2a14', '#6a5230', '#9a7c4e', '#c8a874', '#e4c898', '#fff0c8'),
    'blonde':  R('#4a3008', '#8a6010', '#c8961c', '#f0c030', '#ffe070', '#fff6c0'),
    'bag':     R('#1a0610', '#3a0c22', '#5a1236', '#7e1c4c', '#a8306a', '#d070a0'),
    'cap':     R('#3a0606', '#7a0c0c', '#b81414', '#e02424', '#ff5a4a', '#ffa090'),
    'stripe':  R('#0a2240', '#14427a', '#2064b0', '#3a8ae0', '#e8eef4', '#ffffff'),
    'shorts':  R('#1a2414', '#2e4024', '#405a34', '#587a48', '#78a064', '#a8cc90'),
    'cardi':   R('#1e1008', '#3e2414', '#5e3a22', '#7e5032', '#a06c48', '#c89470'),
    'slacks':  R('#14161c', '#2a2e38', '#424856', '#5c6474', '#7c8698', '#a4aebe'),
    'grey':    R('#3a3a3e', '#6a6a70', '#9a9aa2', '#c4c4cc', '#e4e4ea', '#ffffff'),
    'paper':   R('#4a4a40', '#8a8a7c', '#b8b8a8', '#dcdccc', '#f0f0e4', '#ffffff'),
    'green':   R('#0a2010', '#16401e', '#22602c', '#30803c', '#48a454', '#80cc88'),
    'beanie':  R('#1a0a2a', '#341650', '#4e2276', '#6a309c', '#8a4cc0', '#b886e0'),
    'pack':    R('#1a1a08', '#3a3a14', '#5a5a20', '#7a7a30', '#9c9c48', '#c8c878'),
    'sneaker': R('#3a3a40', '#8a8a94', '#c4c4cc', '#eeeef4', '#ffffff', '#ffffff'),
    'joint':   R('#4a4030', '#a09070', '#d8ccb0', '#f4ecd8', '#ffffff', '#ffffff'),
    'ember':   R('#3a0a00', '#8a2000', '#e04000', '#ff7a1a', '#ffc040', '#ffffff'),
    'stud':    R('#3a3a40', '#6a6a74', '#a4a4b0', '#d4d4dc', '#f4f4f8', '#ffffff'),
})


# ----------------------------------------------------------------------------- the figure
def figure(S, P, extra=None):
    """Draw one person. S = spec (materials and style), P = pose (ninja-style dict)."""
    cv = N()
    s = S.get('scale', 1.0)
    Y = lambda y: GY - (GY - y) * s
    X = lambda dx: CX + dx
    oy = P['bob'] + P['squat'] + S.get('stoop', 0)
    lx = P['lean'] + S.get('lean', 0)
    hipY = Y(21 + P['squat'])
    sh = Y(13) + oy
    tw0, tw1 = S.get('torso', (-4, 3))

    def leg(pts, back):
        knee, foot = pts
        hip = (X(1 if back else -1) + lx * 0.3, hipY + 1)
        k = (X(knee[0]), Y(knee[1] + P['squat'] * 0.4))
        f = (X(foot[0]), min(GY, Y(foot[1])))
        t = 2 if back else 3
        cv.seg(hip, k, S['legs'], t, 3 if S.get('wide_legs', True) else 2)
        cv.seg(k, f, S['legs'], t - (1 if back else 0), 2)
        if S.get('bare_shins'):
            cv.seg(((k[0] + f[0]) / 2, (k[1] + f[1]) / 2 + 1), f, S['skin'], t, 2)
        fx, fy = round(f[0]), round(f[1])
        shoe = S['shoes']
        cv.rect(fx - 2, fy, fx + 1, fy, shoe, 2 if back else 3)
        cv.rect(fx - 1, fy - 1, fx + 1, fy - 1, shoe, 2 if back else 3)
        cv.set(fx - 2, fy, shoe, 1 if back else 4)

    def arm(pts, back):
        el, hand = pts
        sx = X(tw0 + 2 if not back else tw1) + lx
        a = (sx, sh + 2)
        e = (X(el[0]) + lx, Y(el[1]) + oy)
        h = (X(hand[0]) + lx, Y(hand[1]) + oy)
        cv.seg(a, e, S['sleeve'], 2 if back else 4, 2)
        cv.seg(e, h, S['sleeve'], 1 if back else 3, 2)
        cv.dot(h[0], h[1], S['skin'], 2 if back else 3, 2)
        return h

    def torso():
        x0, x1 = X(tw0) + lx, X(tw1) + lx
        y0, y1 = round(sh), round(hipY)
        top, st = S['top'], S.get('style')
        bottom = round(Y(S['coat_to'])) if S.get('coat_to') else y1
        cv.rect(x0, y0, x1, bottom, top, 3)
        cv.vline(x0, y0, bottom, top, 4); cv.vline(x1, y0, bottom, top, 2)
        if st == 'leather':
            cv.rect(x0 + 1, y0, x0 + 2, y0 + 5, 'tee', 4)          # white tee at the open front
            cv.vline(x0 + 3, y0, y1, 'leather', 1)                  # zip edge
            cv.set(x0 + 1, y0 + 1, 'leather', 5)
            cv.hline(x0, x1, y1 - 1, 'leather', 2)                  # waistband
        elif st == 'vest':
            cv.rect(x0 + 1, y0, x0 + 3, y1, 'leather', 2)           # black tee under the open vest
            for yy in range(y0 + 1, y1, 2):
                cv.set(x0 + 4, yy, 'stud', 4)                       # studs along the edge
            cv.set(x1 - 1, y0 + 2, 'stud', 4); cv.set(x1 - 2, y0 + 4, 'stud', 3)
        elif st == 'hoodie':
            cv.rect(x0 + 1, y1 - 4, x1 - 2, y1 - 2, top, 2)         # kangaroo pocket
            cv.hline(x0 + 1, x1 - 2, y1 - 4, top, 4)
            cv.set(x0 + 2, y0 + 1, 'tee', 3); cv.set(x0 + 2, y0 + 2, 'tee', 2)   # drawstring
            cv.hline(x0, x1, y1, top, 1)
        elif st == 'trench':
            cv.vline(x0 + 2, y0 + 1, bottom, top, 1)                # overlap edge
            cv.set(x0 + 4, y0 + 3, 'boot', 3); cv.set(x0 + 4, y0 + 6, 'boot', 3)   # buttons
            cv.hline(x0, x1, y1 - 2, top, 2); cv.hline(x0, x1, y1 - 1, 'trench', 1)  # belt
            cv.set(x0 + 1, y0, 'trench', 5); cv.set(x0 + 1, y0 + 1, 'trench', 4)   # lapel
        elif st == 'stripes':
            for yy in range(y0 + 1, y1, 2):
                cv.hline(x0 + 1, x1 - 1, yy, 'stripe', 4)
        elif st == 'cardigan':
            cv.rect(x0 + 1, y0, x0 + 2, y0 + 3, 'tee', 3)           # shirt collar
            cv.vline(x0 + 3, y0, y1, top, 1)
            for yy in range(y0 + 2, y1, 2):
                cv.set(x0 + 3, yy, 'paper', 2)                      # buttons
        elif st == 'hoodie2':
            cv.set(x0 + 2, y0 + 1, 'tee', 3); cv.set(x0 + 2, y0 + 2, 'tee', 2)
            cv.rect(x0 + 1, y1 - 3, x1 - 2, y1 - 2, top, 2)
        if not S.get('coat_to'):
            cv.rect(x0, y1, x1, y1 + 1, S['legs'], 2)               # trousers top

    # ---- back to front
    if 'back' in S:
        S['back'](cv, X(tw1 + 1) + lx, sh, S)
    hb = arm(P['armB'], True)
    if S.get('backprop'):
        S['backprop'](cv, hb, P)
    leg(P['legB'], True)
    if S.get('coat_to'):
        leg(P['legF'], False)
        torso()
    else:
        torso()
        leg(P['legF'], False)
    S['head'](cv, X(-1) + lx, sh, S, P)
    hf = arm(P['armF'], False)
    if S.get('prop'):
        S['prop'](cv, hf, P)
    cv.outline()
    cv.soften()
    im = cv.image()
    if extra:
        extra(im, hf, P)
    return im


# ----------------------------------------------------------------------------- heads
def eyes(cv, x0, y, S):
    if S.get('red'):
        cv.set(x0 + 1, y, 'eyeR', 4); cv.set(x0 + 4, y, 'eyeR', 3)
        cv.set(x0 + 1, y - 1, 'eyeR', 1); cv.set(x0 + 4, y - 1, 'eyeR', 1)   # dark sockets
    else:
        cv.set(x0 + 1, y, 'boot', 0); cv.set(x0 + 4, y, 'boot', 0)


def face(cv, x0, x1, y0, y1, S):
    sk = S['skin']
    cv.rect(x0, y0, x1, y1, sk, 3)
    cv.vline(x1, y0, y1, sk, 2)
    cv.set(x0, y1, sk, 2)


def head_thug(cv, cx, sh, S, P):
    x0, x1, y0, y1 = cx - 4, cx + 4, round(sh) - 9, round(sh) - 1
    face(cv, x0, x1, y0 + 1, y1, S)
    cv.hline(x0 + 1, x1 - 1, y0, 'skinT', 2)                 # shaved: stubble on top and the back
    cv.rect(x1 - 3, y0 + 1, x1, y0 + 4, 'skinT', 2)
    cv.set(x0 + 2, y0, 'skinT', 4)
    cv.hline(x0, x0 + 4, y0 + 4, 'boot', 1)                   # heavy brow
    eyes(cv, x0, y0 + 5, S)
    cv.hline(x0, x0 + 3, y1 - 1, 'skinT', 1)                  # stubble jaw
    cv.set(x0 + 2, y1 - 2, 'tartan', 2)                       # a scar
    cv.set(x1 - 2, y0 + 5, 'skinT', 4)                        # ear


def head_punk(cv, cx, sh, S, P):
    x0, x1, y0, y1 = cx - 4, cx + 4, round(sh) - 8, round(sh) - 1
    face(cv, x0, x1, y0, y1, S)
    cv.rect(x1 - 3, y0, x1, y0 + 3, 'skinT', 2)               # shaved sides
    # pink mohawk, combed back in spikes
    for i, h in enumerate((3, 4, 4, 3, 2)):
        x = x0 + 2 + i
        for k in range(h):
            cv.set(x + (1 if k >= 2 else 0), y0 - 1 - k, 'mohawk', 4 if k == h - 1 else 3)
        cv.set(x, y0 - 1, 'mohawk', 2)
    eyes(cv, x0, y0 + 4, S)
    cv.set(x0 + 1, y0 + 3, 'leather', 1)                      # eyeliner
    cv.set(x1 - 2, y0 + 5, 'stud', 4); cv.set(x0 + 1, y1 - 1, 'stud', 3)   # earring, lip ring


def head_tagger(cv, cx, sh, S, P):
    x0, x1, y0, y1 = cx - 4, cx + 4, round(sh) - 9, round(sh) - 1
    cv.rect(x0, y0, x1, y1, 'hoodie', 3)                      # the hood
    cv.hline(x0 + 1, x1 - 1, y0, 'hoodie', 4); cv.vline(x1, y0, y1, 'hoodie', 2)
    cv.clear(x0, y0); cv.clear(x1, y0)
    face(cv, x0, x0 + 4, y0 + 3, y1, S)
    cv.vline(x0 + 5, y0 + 2, y1, 'hoodie', 1)                 # hood rim shadow
    eyes(cv, x0, y0 + 5, S)
    cv.rect(x0, y0 + 6, x0 + 4, y1, 'band', 3)                # bandana over the mouth
    cv.hline(x0, x0 + 4, y0 + 6, 'band', 4)
    cv.set(x0 + 1, y0 + 7, 'tee', 4); cv.set(x0 + 3, y1, 'tee', 3)          # paisley dots


def head_adult(cv, cx, sh, S, P):
    x0, x1, y0, y1 = cx - 4, cx + 4, round(sh) - 9, round(sh) - 1
    face(cv, x0, x1, y0 + 1, y1, S)
    # yellow bob: a side parting, chin length, longer at the back
    cv.rect(x0, y0, x1 + 1, y0 + 2, 'blonde', 3)
    cv.hline(x0 + 1, x1, y0 - 1, 'blonde', 4)
    cv.rect(x1 - 3, y0 + 2, x1 + 1, y1 + 1, 'blonde', 3)
    cv.vline(x1 + 1, y0 + 1, y1 + 1, 'blonde', 2)
    cv.set(x0, y0 + 3, 'blonde', 3); cv.set(x0 + 2, y0, 'blonde', 5); cv.set(x0 + 3, y0 - 1, 'blonde', 5)
    eyes(cv, x0, y0 + 5, S)
    cv.set(x0, y1 - 1, 'tartan', 3)                           # lipstick
    cv.set(x1 - 2, y0 + 6, 'gold', 4)                         # earring


def head_child(cv, cx, sh, S, P):
    x0, x1, y0, y1 = cx - 4, cx + 3, round(sh) - 8, round(sh) - 1
    face(cv, x0, x1, y0 + 1, y1, S)
    cv.rect(x1 - 2, y0 + 2, x1, y0 + 4, 'boot', 3)            # hair at the back
    # red cap with the peak forward
    cv.rect(x0, y0 - 1, x1, y0 + 1, 'cap', 3)
    cv.hline(x0 + 1, x1 - 1, y0 - 2, 'cap', 4)
    cv.set(x0 + 2, y0 - 2, 'cap', 5)
    cv.hline(x0 - 3, x0, y0 + 1, 'cap', 2)                    # peak
    cv.set(x0 - 3, y0 + 1, 'cap', 1)
    cv.set(x1 - 1, y0 - 1, 'tee', 4)                          # button
    eyes(cv, x0, y0 + 4, S)


def head_senior(cv, cx, sh, S, P):
    x0, x1, y0, y1 = cx - 4, cx + 4, round(sh) - 9, round(sh) - 1
    face(cv, x0, x1, y0, y1, S)
    cv.hline(x0 + 2, x1 - 1, y0, S['skin'], 4)                # bald top
    cv.rect(x1 - 3, y0 + 2, x1, y0 + 6, 'grey', 4)            # grey fringe round the back
    cv.vline(x1, y0 + 2, y0 + 6, 'grey', 2)
    cv.hline(x0, x0 + 3, y0 + 3, 'grey', 4)                   # bushy brows
    eyes(cv, x0, y0 + 4, S)
    cv.rect(x0, y1 - 2, x0 + 3, y1 - 1, 'grey', 4)            # moustache
    cv.set(x0 - 1, y0 + 5, S['skin'], 2)                      # big nose
    cv.hline(x0 + 1, x0 + 2, y0 + 3, 'grey', 3)


def head_student(cv, cx, sh, S, P):
    x0, x1, y0, y1 = cx - 4, cx + 4, round(sh) - 9, round(sh) - 1
    face(cv, x0, x1, y0 + 2, y1, S)
    cv.rect(x1 - 3, y0 + 3, x1, y0 + 6, 'boot', 4)            # messy hair under the beanie
    cv.set(x0, y0 + 3, 'boot', 4); cv.set(x0 + 1, y0 + 3, 'boot', 3)
    cv.rect(x0, y0, x1, y0 + 2, 'beanie', 3)                  # beanie with a folded brim
    cv.hline(x0 + 1, x1 - 1, y0 - 1, 'beanie', 4)
    cv.hline(x0, x1, y0 + 2, 'beanie', 2)
    cv.set(x0 + 3, y0 - 2, 'beanie', 4); cv.set(x0 + 4, y0 - 2, 'beanie', 3)
    eyes(cv, x0, y0 + 5, S)
    # the joint in the corner of the mouth, ember at the tip
    cv.hline(x0 - 3, x0 - 1, y1 - 1, 'joint', 3)
    cv.set(x0 - 4, y1 - 1, 'ember', 4 if P.get('glow') else 3)


# ----------------------------------------------------------------------------- props
def spray_can(cv, h, P):
    hx, hy = round(h[0]), round(h[1])
    up = P.get('spray')
    if up:   # can held up, nozzle to the left
        cv.rect(hx - 1, hy - 4, hx, hy, 'can', 3)
        cv.vline(hx - 1, hy - 4, hy, 'can', 4)
        cv.hline(hx - 1, hx, hy - 3, 'pink', 3)
        cv.set(hx - 1, hy - 5, 'can', 2); cv.set(hx - 2, hy - 5, 'can', 1)
    else:
        cv.rect(hx - 1, hy, hx, hy + 3, 'can', 3)
        cv.vline(hx - 1, hy, hy + 3, 'can', 4)
        cv.hline(hx - 1, hx, hy + 1, 'pink', 3)


def mist(im, nozzle, f, power=1.0, reach=12, spread=0.5):
    """Slightly transparent pink spray drifting left from the nozzle (alpha ≈ 0.55–0.8)."""
    rnd = random.Random(31 + f)
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    nx, ny = nozzle
    pk = RAMP['pink']
    for i in range(int(90 * power)):
        d = rnd.uniform(1, reach)
        a = rnd.uniform(-spread, spread) + math.pi            # to the left
        x = round(nx + math.cos(a) * d); y = round(ny + math.sin(a) * d * 0.8 - d * 0.08)
        if 0 <= x < im.width and 0 <= y < im.height:
            core = d < reach * 0.45
            c = pk[4] if core else pk[3] if rnd.random() < 0.6 else pk[5]
            al = 215 if core else 170
            lay.putpixel((x, y), c + (al,))
    for i in range(3):                                         # the jet right at the nozzle
        if 0 <= nx - 1 - i < im.width:
            lay.putpixel((nx - 1 - i, ny), pk[5] + (215,))
    im.alpha_composite(lay)


def handbag(cv, h, P):
    hx, hy = round(h[0]), round(h[1])
    cv.rect(hx - 1, hy + 1, hx + 3, hy + 4, 'bag', 3)
    cv.hline(hx - 1, hx + 3, hy + 1, 'bag', 4); cv.vline(hx + 3, hy + 1, hy + 4, 'bag', 2)
    cv.set(hx + 1, hy + 2, 'gold', 4)


def newspaper(cv, h, P):
    hx, hy = round(h[0]), round(h[1])
    swat = P.get('swat', 0)
    if swat == 1:     # raised high
        pts = [(hx + i // 2, hy - i) for i in range(1, 8)]
    elif swat == 2:   # swatting down forward
        pts = [(hx - i, hy + i // 2) for i in range(1, 8)]
    else:             # held out forward
        pts = [(hx - i, hy - i // 3) for i in range(1, 7)]
    for i, (x, y) in enumerate(pts):
        cv.set(x, y, 'paper', 4 if i % 3 else 2)
        cv.set(x, y + 1, 'paper', 2)
    x, y = pts[-1]
    cv.set(x, y, 'paper', 5)


def backpack(cv, x, sh, S):
    y = round(sh)
    cv.rect(x - 1, y + 1, x + 2, y + 7, 'pack', 3)
    cv.vline(x + 2, y + 1, y + 7, 'pack', 2); cv.hline(x - 1, x + 1, y + 1, 'pack', 4)
    cv.rect(x, y + 4, x + 1, y + 5, 'pack', 4)


def smoke(im, f, mouth):
    """thin grey smoke curling up from the joint, semi-transparent"""
    mx, my = mouth
    for i in range(7):
        x = mx + round(math.sin(i * 0.9 + f * 1.4) * 1.5) + (i // 3)
        y = my - 2 - i
        if 0 <= x < im.width and 0 <= y < im.height and (i + f) % 4 != 3:
            im.alpha_composite(Image.new('RGBA', (1, 1), (210, 214, 220, 170 - i * 18)), (x, y))


# ----------------------------------------------------------------------------- specs
THUGS = {
    'thug':   dict(skin='skinT', top='leather', style='leather', sleeve='leather', legs='jeans', shoes='boot',
                   head=head_thug, torso=(-5, 4)),
    'punk':   dict(skin='skinT', top='denim', style='vest', sleeve='leather', legs='tartan', shoes='boot',
                   head=head_punk, wide_legs=False, scale=0.94),
    'tagger': dict(skin='skinT', top='hoodie', style='hoodie', sleeve='hoodie', legs='jeans', shoes='sneaker',
                   head=head_tagger, prop=spray_can),
}
PASSENGERS = {
    'adult':   dict(skin='pale', red=True, top='trench', style='trench', sleeve='trench', legs='slacks', shoes='boot',
                    head=head_adult, coat_to=25, wide_legs=False, backprop=handbag),
    'child':   dict(skin='pale', red=True, top='stripe', style='stripes', sleeve='stripe', legs='shorts', shoes='sneaker',
                    head=head_child, scale=0.7, torso=(-3, 3), bare_shins=True, wide_legs=False),
    'senior':  dict(skin='pale', red=True, top='cardi', style='cardigan', sleeve='cardi', legs='slacks', shoes='boot',
                    head=head_senior, stoop=1, lean=-1, scale=0.94, prop=newspaper),
    'student': dict(skin='pale', red=True, top='green', style='hoodie2', sleeve='green', legs='jeans', shoes='sneaker',
                    head=head_student, back=backpack, scale=0.97),
}
LABEL = {'adult': 'ADULT', 'child': 'CHILD', 'senior': 'SENIOR', 'student': 'STUDENT'}


def thug_pose(kind, col):
    P = ninja_pose(col)
    if col.startswith('atk'):
        if kind == 'tagger':   # aims the can at the girls
            P.update(armF=((-6, 15), (-9, 15)), spray=True)
        else:                  # a big punch
            P.update(armF={'atk0': ((1, 16), (4, 18)), 'atk1': ((-7, 16), (-12, 16)),
                           'atk2': ((-6, 17), (-10, 19))}[col])
    return P


def spray_pose(f):
    P = ninja_pose('idle0')
    P.update(bob=f % 2, legF=((-4, 26), (-6, 30)), legB=((3, 26), (4, 30)),
             armF=((-6, 13), (-9, 10 + (f % 2))), armB=((4, 17), (5, 20)), spray=True)
    return P


def zombie_pose(col, kind):
    P = ninja_pose('idle0')
    step = {'walk0': 0, 'walk1': 1, 'walk2': 2, 'walk3': 3}.get(col)
    reach = -10 if kind != 'senior' else -9
    if col in ('idle0', 'idle1'):
        b = 1 if col == 'idle1' else 0
        P.update(bob=b, lean=0, armF=((-6, 16 + b), (-9, 16 + b)), armB=((-3, 17 + b), (-7, 17 + b)))
    elif step is not None:
        a = 2 * math.pi * step / 4
        def leg(ph):
            fx = -3 * math.cos(ph); fl = max(0.0, 1.5 * math.sin(ph))
            return ((fx * 0.4 - 0.5, 26 - fl * 0.5), (fx, 30 - fl))
        P.update(bob=0 if step % 2 else 1, lean=-1, legF=leg(a), legB=leg(a + math.pi),
                 armF=((-6, 16 + (step % 2)), (reach, 16 + (step % 2))),
                 armB=((-3, 17 - (step % 2)), (reach + 3, 17 - (step % 2))), glow=step % 2)
    elif col == 'atk0':
        P.update(lean=1, armF=((-3, 13), (-4, 9)), armB=((0, 15), (-2, 12)), swat=1,
                 legF=((-3, 26), (-4, 30)), legB=((3, 26), (4, 30)))
    elif col == 'atk1':
        P.update(lean=-2, armF=((-7, 16), (-12, 18)), armB=((-4, 17), (-10, 19)), swat=2, glow=1,
                 legF=((-6, 26), (-8, 30)), legB=((3, 26), (5, 30)))
    if kind == 'senior' and col.startswith('walk'):          # a stiff old-man shuffle
        P['armF'] = ((-5, 17), (-8, 17))
    return P


PCOLS = ['idle0', 'idle1', 'walk0', 'walk1', 'walk2', 'walk3', 'atk0', 'atk1']
PANIMS = {'idle': [0, 1], 'walk': [2, 3, 4, 5], 'attack': [6, 7]}
PFPS = {'idle': 3, 'walk': 6, 'attack': 6}


def bbox_meta(frames):
    boxes = [im.getbbox() for im in frames]
    x0 = min(b[0] for b in boxes); x1 = max(b[2] for b in boxes); y0 = min(b[1] for b in boxes)
    return min(x1 - x0, 18), CELL_H - y0


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2] / 'assets' / 'sprites'
    # ---- thugs (+ spray row)
    sheet = Image.new('RGBA', (CELL_W * len(NINJA_COLS), CELL_H * 4), (0, 0, 0, 0))
    kinds = {}
    for row, kind in enumerate(THUGS):
        S = THUGS[kind]
        runs = []
        for c, col in enumerate(NINJA_COLS):
            P = thug_pose(kind, col)
            extra = None
            if kind == 'tagger' and col == 'atk1':
                extra = lambda im, h, P: mist(im, (round(h[0]) - 2, round(h[1]) - 3), 9, power=0.7, reach=9)
            im = figure(S, P, extra)
            sheet.alpha_composite(im, (c * CELL_W, row * CELL_H))
            if col.startswith('run'):
                runs.append(im)
        w, h = bbox_meta(runs)
        kinds[kind] = {'row': row, 'w': w, 'h': h}
    SHIFT = 12      # the spray row is drawn 12 px right of centre so the mist fits in the cell
    for f in range(4):
        def ex(im, h, P, f=f):
            body = im.copy(); im.paste((0, 0, 0, 0), (0, 0, CELL_W, CELL_H))
            im.alpha_composite(body.crop((0, 0, CELL_W - SHIFT, CELL_H)), (SHIFT, 0))
            mist(im, (round(h[0]) - 2 + SHIFT, round(h[1]) - 4), f, power=1.0 + 0.2 * (f % 2), reach=20, spread=0.5)
        im = figure(THUGS['tagger'], spray_pose(f), ex)
        sheet.alpha_composite(im, (f * CELL_W, 3 * CELL_H))
    sheet.save(root / 'thugs.png')
    meta = {'cell': [CELL_W, CELL_H], 'anims': NINJA_ANIMS, 'fps': NINJA_FPS, 'kinds': kinds,
            'spray': {'row': 3, 'frames': 4, 'fps': 10, 'body_x': CX + 12}}
    (root / 'thugs.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote thugs.png', sheet.size, kinds)

    # ---- zombie passengers
    sheet = Image.new('RGBA', (CELL_W * len(PCOLS), CELL_H * len(PASSENGERS)), (0, 0, 0, 0))
    kinds = {}
    for row, kind in enumerate(PASSENGERS):
        S = PASSENGERS[kind]
        walks = []
        for c, col in enumerate(PCOLS):
            P = zombie_pose(col, kind)
            extra = None
            if kind == 'student':
                extra = lambda im, h, P, c=c: smoke(im, c, (CX - 5 - 4 + P['lean'] - 1, 13 + P['bob'] - 2))
            im = figure(S, P, extra)
            sheet.alpha_composite(im, (c * CELL_W, row * CELL_H))
            if col.startswith('walk'):
                walks.append(im)
        w, h = bbox_meta(walks)
        kinds[kind] = {'row': row, 'w': w, 'h': h, 'label': LABEL[kind]}
    sheet.save(root / 'passengers.png')
    meta = {'cell': [CELL_W, CELL_H], 'anims': PANIMS, 'fps': PFPS, 'kinds': kinds}
    (root / 'passengers.json').write_text(json.dumps(meta, indent=1) + '\n')
    print('wrote passengers.png', sheet.size, kinds)
