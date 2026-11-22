#!/usr/bin/env python3
"""Pixel-art sprite sheet for Kaos-trikken, the boss: the new light-blue Oslo tram transformed into a robot.

It faces LEFT (towards the player) in a three-quarter view. The head is the tram's nose: blue roof cap, the
black LED destination band (showing angry amber eyebrows), the big dark windscreen with wipers, the blue
lower nose with the two red ring tail lights as evil eyes, and the black skirt with the coupler as a jaw.
The body is a transformer built from the tram: chest = a tram section with two windows and the door with
yellow handrails, shoulders = roof sections with the window band, wheels as elbows and knees, bogies as
feet, and the coupler as an arm cannon. Inspiration: inspiration/nytrikk det onde øyet.jpg and
inspiration/vehicles/new tram/.

Sheet: one row of 144 × 128 cells, feet on the bottom row; the body's centre is at x = ANCHOR_X in the cell.
Animations (names and frame ranges) are written to kaostrikken.json.
Usage: python3 tools/sprites/boss.py  → assets/sprites/kaostrikken.png + .json
"""
import json
import math
from dataclasses import dataclass, field, replace
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

CW, CH = 144, 128
OX = 22            # the drawing below is laid out for x 0..122; shifted right to leave room for the cannon's flash
ANCHOR_X = OX + 62


def rgb(h, a=255):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


# ramps: hi, lt, md, dk, xd (outline)
BLUE = [rgb(c) for c in ('#a6e0ff', '#64b8f2', '#3d93de', '#24639f', '#11345e')]
BLUE_FAR = [rgb(c) for c in ('#64b8f2', '#3d93de', '#2c74bb', '#1b4b80', '#0d2647')]
GREY = [rgb(c) for c in ('#e2e6ec', '#aeb4be', '#7f8693', '#4f5561', '#262a32')]
GREY_FAR = [rgb(c) for c in ('#aeb4be', '#868d99', '#5f6672', '#3d424c', '#1d2027')]
GLASS, GLASS2, REFL, REFL2 = rgb('#0b1120'), rgb('#18253c'), rgb('#3b587f'), rgb('#7096c4')
BLACK, BLACK2, GRILLE = rgb('#11151d'), rgb('#222936'), rgb('#3b4250')
YEL, YEL_DK = rgb('#ffd23f'), rgb('#b5860a')
RED, RED_BR, RED_WH, RED_DK, RED_IN = rgb('#ff2346'), rgb('#ff7a90'), rgb('#fff0f2'), rgb('#8e0c22'), rgb('#3b0510')
AMBER, AMBER_DIM, LED_BG = rgb('#ffb12a'), rgb('#4a2c06'), rgb('#07080c')
FIRE = [rgb(c) for c in ('#fff6c8', '#ffd84a', '#ff8a1a', '#e2401a')]
SMOKE = [rgb('#9aa0aa', 200), rgb('#6c727c', 170)]
OUT = rgb('#080a10')
WHITE = rgb('#ffffff')


@dataclass
class Pose:
    ux: int = 0; uy: int = 0                       # upper body offset (bob / lean)
    far_el: tuple = (25, 74); far_wr: tuple = (22, 90)
    near_el: tuple = (99, 76); near_wr: tuple = (97, 93)
    far_knee: tuple = (41, 111); far_ankle: tuple = (40, 121)
    near_knee: tuple = (73, 111); near_ankle: tuple = (76, 121)
    far_lift: int = 0; near_lift: int = 0
    eyes: str = 'on'        # on | flare | squint
    glow: float = 1.0
    jaw: int = 0
    led: int = 0
    cannon: bool = False
    flash: int = 0
    smoke: list = field(default_factory=list)
    vent: int = 0
    wheel: float = 0.0
    white: float = 0.0
    sparks: bool = False


class Painter:
    def __init__(self):
        self.im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
        self.glow = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.g = ImageDraw.Draw(self.glow)

    # coordinates are in layout space; OX is added here
    def P(self, pts):
        return [(round(x) + OX, round(y)) for x, y in pts]

    def px(self, x, y, c):
        self.d.point((round(x) + OX, round(y)), fill=c)

    def line(self, a, b, c, w=1):
        self.d.line(self.P([a, b]), fill=c, width=w)

    def rect(self, x0, y0, x1, y1, c, outline=None, r=0):
        if r:
            self.d.rounded_rectangle([x0 + OX, y0, x1 + OX, y1], r, fill=c, outline=outline)
        else:
            self.d.rectangle([x0 + OX, y0, x1 + OX, y1], fill=c, outline=outline)

    def poly(self, pts, c, outline=None):
        self.d.polygon(self.P(pts), fill=c, outline=outline)

    def ellipse(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.ellipse([x0 + OX, y0, x1 + OX, y1], fill=fill, outline=outline, width=width)

    def panel(self, x0, y0, x1, y1, ramp, r=0):
        """Shaded box: light top and left edge, dark bottom and right edge, outlined."""
        hi, lt, md, dk, xd = ramp
        self.rect(x0, y0, x1, y1, md, xd, r)
        self.line((x0 + 1 + (r > 1), y0 + 1), (x1 - 1 - (r > 1), y0 + 1), hi)
        self.line((x0 + 1, y0 + 2), (x0 + 1, y1 - 2), lt)
        self.line((x0 + 2, y1 - 1), (x1 - 1 - (r > 1), y1 - 1), dk)
        self.line((x1 - 1, y0 + 2), (x1 - 1, y1 - 2), dk)

    def limb(self, a, b, w, ramp, cap=True):
        """A shaded beam from joint a to joint b, w px wide."""
        hi, lt, md, dk, xd = ramp
        ax, ay = a; bx, by = b
        L = math.hypot(bx - ax, by - ay) or 1
        nx, ny = -(by - ay) / L, (bx - ax) / L            # unit normal
        if nx + ny > 0:                                   # make n point up-left (towards the light)
            nx, ny = -nx, -ny
        h = w / 2
        q = [(ax + nx * h, ay + ny * h), (bx + nx * h, by + ny * h), (bx - nx * h, by - ny * h), (ax - nx * h, ay - ny * h)]
        self.poly(q, md, xd)
        self.line((ax + nx * (h - 1.2), ay + ny * (h - 1.2)), (bx + nx * (h - 1.2), by + ny * (h - 1.2)), lt)
        self.line((ax - nx * (h - 1.2), ay - ny * (h - 1.2)), (bx - nx * (h - 1.2), by - ny * (h - 1.2)), dk)
        if w >= 8:
            self.line((ax + nx * (h - 2.2), ay + ny * (h - 2.2)), (bx + nx * (h - 2.2), by + ny * (h - 2.2)), hi)

    def piston(self, a, b, ramp=GREY):
        self.line(a, b, ramp[4], 3)
        self.line(a, b, ramp[1], 1)

    def wheel(self, cx, cy, r, rot=0.0, far=False):
        g = GREY_FAR if far else GREY
        self.ellipse(cx - r, cy - r, cx + r, cy + r, fill=BLACK2, outline=OUT)        # tyre
        self.ellipse(cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2, fill=g[2], outline=g[3])   # rim
        if r >= 4:
            for k in range(3):
                a = rot + k * 2 * math.pi / 3
                self.line((cx, cy), (cx + math.cos(a) * (r - 2), cy + math.sin(a) * (r - 2)), g[3])
        self.px(cx, cy, g[0])
        self.px(cx - r + 2, cy - r + 2 + (r > 3), g[0])

    def glow_dot(self, cx, cy, r, c, a):
        for k in range(r, 0, -1):
            al = int(a * (1 - k / (r + 1)) ** 1.3)
            self.g.ellipse([cx - k + OX, cy - k, cx + k + OX, cy + k], fill=c[:3] + (al,))


# ---------------------------------------------------------------- parts
DIGITS = {'6': ['111', '100', '111', '101', '111']}


def head(p: Painter, s: Pose):
    """The tram's nose in three-quarter view, facing left: the front (34 wide) on the left, the side receding right."""
    x, y = 26 + s.ux, 7 + s.uy
    F = [(x + 3, y), (x + 33, y), (x + 34, y + 41), (x, y + 41)]                # front, raked back at the top
    # side of the car
    p.poly([(x + 33, y), (x + 54, y + 3), (x + 54, y + 37), (x + 34, y + 41)], BLUE_FAR[2], BLUE_FAR[4])
    p.poly([(x + 36, y + 3), (x + 53, y + 5), (x + 53, y + 22), (x + 36, y + 23)], BLACK, BLUE_FAR[4])  # black window band
    p.poly([(x + 38, y + 6), (x + 50, y + 7), (x + 50, y + 20), (x + 38, y + 21)], GLASS)
    p.line((x + 40, y + 19), (x + 45, y + 8), REFL); p.line((x + 43, y + 19), (x + 47, y + 11), GLASS2)
    p.line((x + 35, y + 25), (x + 53, y + 24), BLUE_FAR[0])
    p.line((x + 35, y + 33), (x + 53, y + 31), BLUE_FAR[3])
    p.rect(x + 37, y + 28, x + 39, y + 29, RED); p.glow_dot(x + 38, y + 28, 3, RED, 90)       # side marker
    p.line((x + 52, y + 26), (x + 52, y + 35), BLUE_FAR[3])                       # end of the cab
    # roof cap
    p.poly([(x + 6, y - 4), (x + 32, y - 4), (x + 54, y), (x + 54, y + 3), (x + 33, y), (x + 3, y)], BLUE[1], BLUE[4])
    p.line((x + 7, y - 3), (x + 32, y - 3), BLUE[0]); p.line((x + 33, y - 3), (x + 52, y), BLUE[0])
    p.rect(x + 40, y - 6, x + 46, y - 3, GREY[2], GREY[4]); p.px(x + 41, y - 5, GREY[0])  # roof box
    # front
    p.poly(F, BLUE[2], BLUE[4])
    p.line((x + 3, y + 1), (x + 32, y + 1), BLUE[0])
    p.line((x + 2, y + 4), (x + 1, y + 39), BLUE[1])
    p.line((x + 33, y + 3), (x + 33, y + 39), BLUE[3])
    # black frame with the destination display inside the top of the glass
    p.poly([(x + 5, y + 3), (x + 31, y + 3), (x + 32, y + 24), (x + 3, y + 24)], BLACK, BLUE[4])
    for xx in range(x + 6, x + 31):
        for yy in range(y + 4, y + 9):
            if (xx + yy) % 2 == 0:
                p.px(xx, yy, AMBER_DIM)
    for i in range(10):                                                        # angry amber eyebrows
        by = y + 4 + (i * 4) // 9
        for px_ in (x + 7 + i, x + 29 - i):
            on = s.led < 0 or (px_ + s.led) % 7 != 0
            p.px(px_, by, AMBER if on else AMBER_DIM)
            if s.eyes == 'flare':
                p.px(px_, by + 1, AMBER)
    p.poly([(x + 5, y + 10), (x + 31, y + 10), (x + 31, y + 23), (x + 4, y + 23)], GLASS)
    p.line((x + 5, y + 10), (x + 30, y + 10), GLASS2)
    for k, c in ((0, REFL), (3, REFL), (5, GLASS2)):
        p.line((x + 6 + k, y + 22), (x + 12 + k, y + 11), c)
    p.line((x + 25, y + 22), (x + 29, y + 13), REFL2); p.line((x + 27, y + 22), (x + 30, y + 16), REFL)
    p.line((x + 13, y + 22), (x + 8, y + 16), GREY[3]); p.px(x + 13, y + 22, GREY[1])   # wipers in a scowl
    p.line((x + 22, y + 22), (x + 27, y + 16), GREY[3]); p.px(x + 22, y + 22, GREY[1])
    # lower nose with the lamps out at the corners and the fleet number between
    p.line((x + 2, y + 26), (x + 33, y + 26), BLUE[0])
    p.line((x + 2, y + 35), (x + 33, y + 35), BLUE[3])
    eye(p, x + 6, y + 30, s, far=True)
    eye(p, x + 28, y + 30, s)
    for (a, b) in (((x + 1, y + 25), (x + 12, y + 28)), ((x + 22, y + 28), (x + 33, y + 25))):
        p.line(a, b, BLUE[2], 2)
    for n, ch in enumerate('666'):
        for r, row in enumerate(DIGITS[ch]):
            for c, bit in enumerate(row):
                if bit == '1':
                    p.px(x + 12 + n * 4 + c, y + 29 + r, WHITE)
    # skirt + coupler jaw
    j = s.jaw
    if j:
        p.rect(x + 4, y + 36, x + 30, y + 37 + j, FIRE[3])
        p.rect(x + 7, y + 36, x + 27, y + 36 + j, FIRE[2])
        p.rect(x + 11, y + 36, x + 23, y + 35 + j, FIRE[1])
        p.glow_dot(x + 17, y + 38 + j // 2, 10 + j, FIRE[2], 150)
    yy = y + 36 + j
    p.rect(x, yy, x + 34, yy + 5, BLACK, OUT)
    for k in range(x + 2, x + 33, 3):
        p.line((k, yy + 1), (k, yy + 4), GRILLE)
    p.rect(x + 12, yy + 1, x + 22, yy + 6, GREY[2], GREY[4])
    p.line((x + 13, yy + 2), (x + 21, yy + 2), GREY[0])
    p.rect(x + 15, yy + 4, x + 19, yy + 6, BLACK)
    if j:
        for k in range(x + 3, x + 33, 4):
            p.px(k, yy - 1, GREY[1]); p.px(k, y + 36, GREY[1])


def eye(p: Painter, cx, cy, s: Pose, far=False):
    r = 4
    if s.eyes == 'squint':
        p.ellipse(cx - r, cy - 1, cx + r, cy + 2, fill=RED, outline=RED_DK)
        p.line((cx - 2, cy), (cx + 2, cy), RED_WH)
        p.glow_dot(cx, cy, 6, RED, 120)
        return
    flare = s.eyes == 'flare'
    p.glow_dot(cx, cy, 10 if flare else 7, RED, int((200 if flare else 140) * s.glow))
    p.ellipse(cx - r, cy - r, cx + r, cy + r, fill=RED if flare else RED_IN, outline=RED_DK)
    p.ellipse(cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1, outline=RED, width=2 if not flare else 1)
    if flare:
        p.ellipse(cx - 2, cy - 2, cx + 2, cy + 2, fill=RED_BR)
        p.rect(cx - 1, cy - 1, cx + 1, cy + 1, RED_WH)
    else:
        p.rect(cx - 1, cy - 1, cx, cy, RED_BR if s.glow > 0.8 else RED)
    p.px(cx - 2, cy - 3, RED_WH)


def shoulder(p: Painter, s: Pose, near: bool):
    """Roof-section shoulder armour with the black window band."""
    if near:
        x0, y0, x1, y1, R = 72, 43, 103, 63, BLUE
    else:
        x0, y0, x1, y1, R = 22, 47, 42, 62, BLUE_FAR
    x0 += s.ux; x1 += s.ux; y0 += s.uy; y1 += s.uy
    p.panel(x0, y0, x1, y1, R, 4)
    p.line((x0 + 3, y0 + 2), (x1 - 3, y0 + 2), R[0])
    p.rect(x0 + 2, y0 + 6, x1 - 2, y0 + 10, GLASS, R[4])
    for k in range(x0 + 6, x1 - 2, 7):
        p.line((k, y0 + 7), (k, y0 + 9), R[3])
        p.px(k - 3, y0 + 7, REFL)
    p.line((x0 + 2, y1 - 5), (x1 - 2, y1 - 5), R[3])
    p.line((x0 + 2, y1 - 3), (x1 - 2, y1 - 3), BLACK)                          # skirt edge
    if near:
        p.line((x0 + 3, y1 - 4), (x1 - 3, y1 - 4), YEL)
        p.rect(x1 - 5, y0 + 12, x1 - 3, y0 + 14, RED)                           # tail lamp
        p.glow_dot(x1 - 4, y0 + 13, 4, RED, 110)
        for k in range(4):
            p.px(x0 + 4 + k * 7, y0 + 4, R[0])
        # angled spike plate on top (transformer silhouette)
        p.poly([(x0 + 6, y0), (x0 + 12, y0 - 6), (x0 + 22, y0 - 6), (x0 + 26, y0)], R[1], R[4])
        p.line((x0 + 12, y0 - 5), (x0 + 21, y0 - 5), R[0])
    else:
        p.poly([(x0 + 3, y0), (x0 + 7, y0 - 5), (x0 + 15, y0 - 5), (x0 + 18, y0)], R[1], R[4])


def chest(p: Painter, s: Pose):
    ux, uy = s.ux, s.uy
    X = lambda pts: [(a + ux, b + uy) for a, b in pts]
    # side of the chest: the tram's side with a window and the door
    p.poly(X([(72, 49), (94, 54), (91, 80), (70, 83)]), BLUE_FAR[2], BLUE_FAR[4])
    p.poly(X([(74, 56), (88, 59), (88, 70), (74, 71)]), BLACK, BLUE_FAR[4])
    p.poly(X([(76, 58), (82, 59), (82, 69), (76, 69)]), GLASS)
    p.line((77 + ux, 68 + uy), (80 + ux, 60 + uy), REFL)
    p.line((85 + ux, 60 + uy), (85 + ux, 77 + uy), YEL); p.line((87 + ux, 61 + uy), (87 + ux, 76 + uy), YEL_DK)
    p.line((72 + ux, 75 + uy), (91 + ux, 73 + uy), BLUE_FAR[0])
    # front of the chest
    p.poly(X([(35, 49), (72, 49), (70, 83), (41, 83)]), BLUE[2], BLUE[4])
    p.poly(X([(36, 50), (71, 50), (54, 58)]), BLUE[1])                         # V-shaped upper plates
    p.line((36 + ux, 50 + uy), (54 + ux, 58 + uy), BLUE[4]); p.line((54 + ux, 58 + uy), (71 + ux, 50 + uy), BLUE[4])
    p.line((37 + ux, 50 + uy), (70 + ux, 50 + uy), BLUE[0])
    p.line((36 + ux, 52 + uy), (41 + ux, 82 + uy), BLUE[1])
    p.line((71 + ux, 52 + uy), (69 + ux, 82 + uy), BLUE[3])
    for (a, b) in ((40, 51), (57, 68)):                                        # windows
        p.rect(a + ux, 61 + uy, b + ux, 75 + uy, GLASS, BLUE[4])
        p.line((a + 1 + ux, 62 + uy), (b - 1 + ux, 62 + uy), GLASS2)
        p.line((a + 2 + ux, 74 + uy), (a + 7 + ux, 63 + uy), REFL)
        p.line((a + 5 + ux, 74 + uy), (a + 9 + ux, 66 + uy), REFL)
        p.line((b - 2 + ux, 73 + uy), (b - 1 + ux, 70 + uy), REFL2)
    p.rect(52 + ux, 59 + uy, 56 + ux, 77 + uy, BLACK2, BLUE[4])                # door strip with handrails
    p.line((53 + ux, 61 + uy), (53 + ux, 76 + uy), YEL); p.line((55 + ux, 61 + uy), (55 + ux, 76 + uy), YEL)
    p.line((41 + ux, 77 + uy), (69 + ux, 77 + uy), BLUE[3])
    p.line((41 + ux, 78 + uy), (69 + ux, 78 + uy), BLUE[1])
    p.ellipse(50 + ux, 77 + uy, 58 + ux, 84 + uy, fill=BLACK, outline=GREY[3])   # reactor core
    p.ellipse(52 + ux, 79 + uy, 56 + ux, 82 + uy, fill=RED if s.glow > 0.8 or s.eyes == 'flare' else RED_DK)
    p.px(53 + ux, 79 + uy, RED_BR)
    p.glow_dot(54 + ux, 81 + uy, 6, RED, int(110 * s.glow))
    for k in (44, 47, 62, 65):
        p.px(k + ux, 80 + uy, BLUE[0]); p.px(k + ux, 81 + uy, BLUE[3])


def abdomen_pelvis(p: Painter, s: Pose):
    ux, uy = s.ux, s.uy
    p.rect(47 + ux, 82 + uy, 66 + ux, 93 + uy, GREY[2], GREY[4])
    for k in range(85, 93, 3):
        p.line((48 + ux, k + uy), (65 + ux, k + uy), GREY[3])
        p.line((48 + ux, k - 1 + uy), (65 + ux, k - 1 + uy), GREY[1])
    p.piston((45 + ux, 82 + uy), (48 + ux, 94 + uy)); p.piston((68 + ux, 82 + uy), (65 + ux, 94 + uy))
    p.poly([(39 + ux, 92 + uy), (75 + ux, 92 + uy), (72, 101 + uy), (42, 101 + uy)], BLUE[2], BLUE[4])
    p.line((40 + ux, 93 + uy), (74 + ux, 93 + uy), BLUE[1])
    p.line((43, 100 + uy), (71, 100 + uy), BLUE[3])
    p.rect(49 + ux, 94 + uy, 64 + ux, 98 + uy, YEL, OUT)
    for k in range(-4, 16, 4):
        for t in range(2):
            p.line((50 + k + t + ux, 97 + uy), (53 + k + t + ux, 95 + uy), BLACK)
    p.rect(49 + ux, 94 + uy, 64 + ux, 98 + uy, None, OUT)


def hip_plates(p: Painter, s: Pose):
    """Skirt armour hanging over the thighs, like a tram's side skirts."""
    uy = s.uy
    p.poly([(36, 95 + uy), (46, 95 + uy), (45, 107 + uy), (38, 104 + uy)], BLUE_FAR[2], BLUE_FAR[4])
    p.line((37, 96 + uy), (45, 96 + uy), BLUE_FAR[0])
    p.poly([(67, 95 + uy), (78, 95 + uy), (76, 105 + uy), (68, 108 + uy)], BLUE[2], BLUE[4])
    p.line((68, 96 + uy), (77, 96 + uy), BLUE[0]); p.line((69, 105 + uy), (75, 103 + uy), BLACK)


def arm(p: Painter, s: Pose, near: bool):
    G, B = (GREY, BLUE) if near else (GREY_FAR, BLUE_FAR)
    sh = ((92 if near else 32) + s.ux, (58 if near else 57) + s.uy)
    el = s.near_el if near else s.far_el
    wr = s.near_wr if near else s.far_wr
    el = (el[0] + s.ux, el[1] + s.uy); wr = (wr[0] + s.ux, wr[1] + s.uy)
    p.limb(sh, el, 8, G)
    p.piston((sh[0] + 3, sh[1] + 2), (el[0] + 3, el[1] - 2), G)
    if not near and s.cannon:
        cannon(p, s, el, wr)
        p.wheel(el[0], el[1], 5, s.wheel, far=True)
        return
    p.limb(el, wr, 12, B)                                                     # forearm: a tram end
    mx, my = (el[0] * 0.4 + wr[0] * 0.6), (el[1] * 0.4 + wr[1] * 0.6)
    p.line((mx - 4, my), (mx + 4, my), GLASS); p.line((mx - 4, my + 1), (mx + 4, my + 1), GLASS)
    p.wheel(el[0], el[1], 5, s.wheel, far=not near)
    fx, fy = wr
    w, h = (13, 11) if near else (11, 10)
    p.panel(fx - w // 2 - 1, fy - 1, fx + w // 2, fy + h - 1, G, 2)
    for k in range(3):
        p.line((fx - w // 2 + 1, fy + 2 + k * 2), (fx - w // 2 + 5, fy + 2 + k * 2), G[3])
    p.rect(fx + w // 2 - 3, fy + 1, fx + w // 2 - 1, fy + 4, G[1])


def cannon(p: Painter, s: Pose, el, wr):
    """The far forearm folds out into the coupler, pointing left."""
    wx, wy = wr
    p.limb(el, wr, 10, BLUE_FAR)
    p.rect(wx - 12, wy - 4, wx + 1, wy + 4, GREY[2], GREY[4])
    p.line((wx - 11, wy - 3), (wx, wy - 3), GREY[0])
    p.line((wx - 11, wy + 3), (wx, wy + 3), GREY[3])
    p.rect(wx - 15, wy - 5, wx - 12, wy + 5, BLACK, OUT)
    p.rect(wx - 15, wy - 1, wx - 13, wy + 1, RED if s.flash or s.eyes == 'flare' else RED_DK)
    for k in range(wx - 9, wx, 3):
        p.px(k, wy, GREY[3])
    if s.eyes == 'flare' and not s.flash:
        p.glow_dot(wx - 16, wy, 6, RED, 170)
    if s.flash:
        fx, f = wx - 17, s.flash
        p.glow_dot(fx - f // 2, wy, f + 6, FIRE[2], 200)
        p.poly([(fx, wy - f // 2), (fx - f * 1.6, wy), (fx, wy + f // 2)], FIRE[2])
        p.poly([(fx, wy - f // 3), (fx - f * 1.1, wy), (fx, wy + f // 3)], FIRE[1])
        p.poly([(fx - f * 0.3, wy - f * 0.9), (fx - f * 0.6, wy), (fx - f * 0.2, wy + f * 0.9), (fx + 1, wy)], FIRE[2])
        p.ellipse(fx - 3, wy - 2, fx + 1, wy + 2, fill=FIRE[0])


def leg(p: Painter, s: Pose, near: bool):
    G, B = (GREY, BLUE) if near else (GREY_FAR, BLUE_FAR)
    hip = ((67 if near else 47) + s.ux, 99 + s.uy)
    kn = s.near_knee if near else s.far_knee
    an = s.near_ankle if near else s.far_ankle
    lift = s.near_lift if near else s.far_lift
    kn = (kn[0], kn[1] - lift // 2); an = (an[0], an[1] - lift)
    p.limb(hip, kn, 10, G)
    p.piston((hip[0] + 3, hip[1] + 1), (kn[0] + 3, kn[1] - 2), G)
    p.limb(kn, an, 12, B)
    p.line((an[0] - 5, an[1] - 2), (an[0] + 5, an[1] - 2), BLACK)
    p.line((kn[0] - 3, kn[1] + 6), (an[0] - 3, an[1] - 5), B[0])              # crease
    p.wheel(kn[0], kn[1], 5, s.wheel, far=not near)
    fx, fy = an
    p.panel(fx - 13, fy - 1, fx + 8, fy + 3, G, 1)
    p.poly([(fx - 13, fy - 1), (fx - 16, fy + 3), (fx - 13, fy + 3)], G[3], G[4])   # toe
    p.rect(fx - 4, fy - 3, fx + 2, fy - 1, G[3], G[4])
    p.wheel(fx - 8, fy + 3, 3, s.wheel, far=not near)
    p.wheel(fx + 4, fy + 3, 3, s.wheel, far=not near)


def steam(p: Painter, s: Pose):
    for i in range(s.vent):
        x, y = 100 + s.ux + i, 38 + s.uy - i * 3
        p.ellipse(x - 1 - i // 2, y - 1 - i // 2, x + 1 + i // 2, y + 1 + i // 2, fill=SMOKE[i % 2])
    for (x, y, r) in s.smoke:
        p.ellipse(x - r, y - r, x + r, y + r, fill=SMOKE[r % 2])


def sparks(p: Painter):
    for (x, y) in ((30, 30), (96, 40), (62, 74), (20, 90), (88, 100), (50, 20)):
        p.line((x - 2, y), (x + 2, y), FIRE[1]); p.line((x, y - 2), (x, y + 2), FIRE[1]); p.px(x, y, FIRE[0])


def render(s: Pose) -> Image.Image:
    p = Painter()
    arm(p, s, near=False)
    shoulder(p, s, near=False)
    leg(p, s, near=False)
    leg(p, s, near=True)
    abdomen_pelvis(p, s)
    hip_plates(p, s)
    chest(p, s)
    head(p, s)
    shoulder(p, s, near=True)
    arm(p, s, near=True)
    steam(p, s)
    im = p.im
    # outer outline: transparent pixels next to the body
    a = Image.new('L', (CW + 2, CH + 2), 0)                                 # padded so the offsets don't wrap
    a.paste(im.split()[3].point(lambda v: 255 if v > 0 else 0), (1, 1))
    grown = a
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        grown = ImageChops.lighter(grown, ImageChops.offset(a, dx, dy))
    ring = ImageChops.subtract(grown, a).crop((1, 1, CW + 1, CH + 1))
    outline = Image.new('RGBA', im.size, OUT)
    base = Image.new('RGBA', im.size, (0, 0, 0, 0))
    base.paste(outline, (0, 0), ring)
    base.alpha_composite(im)
    if s.white:
        wh = Image.new('RGBA', im.size, (255, 255, 255, 0))
        al = base.split()[3].point(lambda v: int(v * s.white))
        wh.putalpha(al)
        base.alpha_composite(wh)
    # glow goes under the outline but over nothing else; keep it subtle around the sprite
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.alpha_composite(p.glow)
    out.alpha_composite(base)
    gl = p.glow.copy()
    gl.putalpha(gl.split()[3].point(lambda v: v // 2))
    out.alpha_composite(gl)                                                 # glow also spills over the body
    if s.sparks:
        sp = Painter(); sparks(sp); out.alpha_composite(sp.im)
    return out


# ---------------------------------------------------------------- animation
def walk(i, n=6) -> Pose:
    a = 2 * math.pi * i / n
    sw = math.sin(a)
    bob = 1 - round(abs(math.cos(a)) * 2)
    stride = 9
    far_x, near_x = 42 - sw * stride, 74 + sw * stride
    return Pose(
        uy=bob,
        far_ankle=(far_x, 121), near_ankle=(near_x, 121),
        far_knee=((47 + far_x) / 2 - 3, 111 + bob), near_knee=((67 + near_x) / 2 - 3, 111 + bob),
        far_lift=max(0, round(5 * math.cos(a))), near_lift=max(0, round(-5 * math.cos(a))),
        far_wr=(22 + sw * 6, 90), near_wr=(97 - sw * 6, 93),
        far_el=(25 + sw * 3, 74), near_el=(99 - sw * 3, 76),
        wheel=a, led=i, glow=0.9,
    )


def idle(i) -> Pose:
    bob = (0, 0, 1, 1)[i]
    return Pose(uy=bob, far_wr=(22, 90 + bob), near_wr=(97, 93 + bob),
                glow=(1.0, 0.85, 0.7, 0.85)[i], led=-1 if i % 2 == 0 else i * 2, vent=(0, 0, 2, 4)[i])


CANNON_UP = dict(cannon=True, far_el=(17, 62), far_wr=(5, 60))


def attack(i) -> Pose:
    if i == 0:   # wind-up: cannon swings up, eyes flare
        return Pose(**dict(CANNON_UP, far_el=(19, 67), far_wr=(8, 67)), eyes='flare', jaw=1, ux=1)
    if i == 1:   # fire
        return Pose(**CANNON_UP, eyes='flare', jaw=4, flash=12, ux=2)
    if i == 2:   # recoil + smoke
        return Pose(**dict(CANNON_UP, far_el=(19, 62), far_wr=(8, 59)), eyes='flare', jaw=3, flash=5, ux=3,
                    smoke=[(-6, 58, 3), (-10, 54, 2)])
    return Pose(**dict(CANNON_UP, far_el=(20, 66), far_wr=(9, 65)), jaw=1, ux=1,
                smoke=[(-9, 52, 3), (-13, 47, 2), (-4, 55, 2)])


def hit(i) -> Pose:
    if i == 0:
        return Pose(eyes='squint', white=0.75, ux=3, jaw=2, sparks=True)
    return Pose(eyes='squint', ux=2, uy=1, jaw=1, sparks=True, glow=0.5)


ANIMS = {
    'walk': [walk(i) for i in range(6)],
    'idle': [idle(i) for i in range(4)],
    'attack': [attack(i) for i in range(4)],
    'hit': [hit(i) for i in range(2)],
}


def main():
    root = Path(__file__).resolve().parents[2]
    frames, meta, k = [], {'w': CW, 'h': CH, 'anchorX': ANCHOR_X, 'anims': {}}, 0
    for name, poses in ANIMS.items():
        meta['anims'][name] = {'start': k, 'count': len(poses)}
        for s in poses:
            frames.append(render(s)); k += 1
    sheet = Image.new('RGBA', (CW * len(frames), CH), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * CW, 0))
    out = root / 'assets' / 'sprites' / 'kaostrikken.png'
    sheet.save(out)
    (out.with_suffix('.json')).write_text(json.dumps(meta, indent=1) + '\n')
    print(out, sheet.size, meta)


if __name__ == '__main__':
    main()
