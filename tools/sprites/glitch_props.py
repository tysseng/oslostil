"""Glitch-level props (level 2, «a-a-a-automaten hakker»), drawn into the props sheet by props.py.

Built from the plain ticket machine in assets/sprites/automat.png (column «plain», 24 × 32) so the
clones are exactly the machines from Sandvika, then broken up frame by frame: row slices that slip
sideways, a pink/cyan channel split, static on the screen, «A-A-A» on the screen and missing-texture
blocks. Only solid pixels in the project's colours (no alpha, no blended edges). The base rows never
move and the top row stays at the same height, so the props are safe to stand on.

  glitch_machine        one clone, 8 frames ............................ 32 px (one jump)
  glitch_machine_stack  a clone copy-pasted on top of another, the top
                        copy slips sideways, 8 frames .................. 64 px (double jump)
  glitch_machine_smear  a clone dragging an echo trail to the left,
                        a long low platform, 8 frames .................. 32 px (one jump)

Each entry: (name, draw function → list of frames, fps, top, light function).
"""
import random
from pathlib import Path
from PIL import Image
from props import rgb

PINK, CYAN = rgb('#ff2bd6'), rgb('#2bf0ff')
VOID = rgb('#0f0f31')
SCREEN = [rgb('#2f66e8'), rgb('#7fb0ff'), rgb('#1c2468'), rgb('#cfe0ff'), PINK, CYAN]
SCREEN_BOX = (5, 3, 15, 13)            # x0, y0, x1, y1 (inclusive) of the screen inside the machine
MW, MH = 24, 32
FPS = 8                                 # 8 frames at 8 fps: one loop ≈ two beats at 122 BPM


def plain():
    sheet = Image.open(Path(__file__).resolve().parents[2] / 'assets' / 'sprites' / 'automat.png').convert('RGBA')
    return sheet.crop((6 * MW, 0, 7 * MW, MH))


class Frame:
    """props.py calls .image() on every frame."""

    def __init__(self, im):
        self.im = im

    def image(self):
        return self.im


def silhouette(im, col):
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    px, op = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][3]:
                op[x, y] = col + (255,)
    return out


def shift_rows(im, y0, y1, dx):
    """Cut rows y0..y1 and paste them dx px sideways (the slice slips)."""
    band = im.crop((0, y0, im.width, y1 + 1))
    out = im.copy()
    out.paste((0, 0, 0, 0), (0, y0, im.width, y1 + 1))
    out.alpha_composite(band, (dx, y0)) if dx >= 0 else out.alpha_composite(band.crop((-dx, 0, band.width, band.height)), (0, y0))
    return out


def screen_static(im, rnd, density=1.0):
    out = im.copy()
    px = out.load()
    x0, y0, x1, y1 = SCREEN_BOX
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if rnd.random() < density:
                px[x, y] = rnd.choice(SCREEN) + (255,)
    return out


A_GLYPH = ['010', '101', '111', '101', '101']


def screen_aaa(im, inverse=False):
    """«A-A-A» on the screen: three 3 × 5 A's with dashes."""
    out = im.copy()
    px = out.load()
    x0, y0, x1, y1 = SCREEN_BOX
    bg, fg = (PINK, rgb('#1c2468')) if inverse else (rgb('#1c2468'), CYAN)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px[x, y] = bg + (255,)
    gx, gy = x0, y0 + 3
    for i in range(3):
        for r, row in enumerate(A_GLYPH):
            for c, ch in enumerate(row):
                if ch == '1':
                    px[gx + c, gy + r] = fg + (255,)
        if i < 2:
            px[gx + 3, gy + 2] = fg + (255,)
        gx += 4
    return out


def missing_block(im, x0, y0, w, h):
    """A missing-texture patch: 2 × 2 checker of magenta and near-black, only where the machine is."""
    out = im.copy()
    px = out.load()
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if 0 <= x < out.width and 0 <= y < out.height and px[x, y][3]:
                px[x, y] = (PINK if ((x - x0) // 2 + (y - y0) // 2) % 2 == 0 else VOID) + (255,)
    return out


def split(im, d):
    """Pink copy d px to the left, cyan copy d px to the right, the machine on top (no alpha)."""
    out = Image.new('RGBA', (im.width + 2 * d, im.height), (0, 0, 0, 0))
    out.alpha_composite(silhouette(im, PINK), (0, 0))
    out.alpha_composite(silhouette(im, CYAN), (2 * d, 0))
    out.alpha_composite(im, (d, 0))
    return out


def glitched(f, rnd):
    """Frame f (0..7) of one broken machine, returned on a (MW + 4) × MH canvas, machine at x = 2."""
    m = plain()
    d = 0
    if f == 0:
        m = screen_static(m, rnd, 0.35)
    elif f == 1:
        m = shift_rows(m, 4, 9, 3)
        m = screen_static(m, rnd, 0.6)
        d = 1
    elif f == 2:
        m = screen_aaa(m)
        d = 2
    elif f == 3:
        m = screen_aaa(m, inverse=True)
        m = shift_rows(m, 18, 22, -2)
    elif f == 4:
        m = screen_static(m, rnd, 1.0)
        m = missing_block(m, 12, 15, 8, 6)
        d = 1
    elif f == 5:
        m = shift_rows(m, 2, 6, -3)
        m = shift_rows(m, 10, 13, 2)
        m = screen_static(m, rnd, 0.8)
        d = 2
    elif f == 6:
        m = screen_aaa(m)
        m = missing_block(m, 4, 21, 10, 4)
    else:
        m = screen_static(m, rnd, 0.2)
    out = Image.new('RGBA', (MW + 4, MH), (0, 0, 0, 0))
    s = split(m, d) if d else m
    out.alpha_composite(s, (2 - d, 0))
    return out


def padded(im, pad=10):
    """Room round the sprite so the light (same canvas) isn't clipped."""
    out = Image.new('RGBA', (im.width + 2 * pad, im.height + pad), (0, 0, 0, 0))
    out.alpha_composite(im, (pad, pad))
    return out


# --------------------------------------------------------------------------- the props
def glitch_machine():
    rnd = random.Random(26)
    return [Frame(padded(glitched(f, rnd))) for f in range(8)]


STACK_SLIP = [0, 3, 3, -2, 0, 4, -3, 0]


def glitch_machine_stack():
    """A clone copy-pasted onto another: the top copy slips sideways and glitches out of step."""
    rnd = random.Random(27)
    frames = []
    for f in range(8):
        cv = Image.new('RGBA', (MW + 12, 2 * MH), (0, 0, 0, 0))
        cv.alpha_composite(glitched((f + 4) % 8, rnd), (4, MH))          # lower machine, own glitch phase
        cv.alpha_composite(glitched(f, rnd), (4 + STACK_SLIP[f], 0))     # the pasted copy on top
        frames.append(Frame(padded(cv)))
    return frames


def echo(m, col, rim):
    """A flat echo of the machine: solid tone, a bright top row and edge so it reads as a solid block."""
    e = silhouette(m, col)
    px = e.load()
    for x in range(e.width):
        for y in range(e.height):
            if px[x, y][3]:
                px[x, y] = rim + (255,)
                break
    return e


def glitch_machine_smear():
    """A clone dragging a trail of echoes to the left: one long, low platform."""
    rnd = random.Random(28)
    m0 = plain()
    tones = [(rgb('#1c2468'), CYAN), (rgb('#28338f'), PINK), (rgb('#3b48b4'), CYAN)]
    frames = []
    for f in range(8):
        cv = Image.new('RGBA', (MW + 3 * 13 + 6, MH), (0, 0, 0, 0))
        for i in range(3):                                   # far echo first
            col, rim = tones[(i + f) % 3]
            jitter = (0, 1, -1, 0, 2, 0, -1, 1)[(f + i * 3) % 8]
            x = 2 + i * 13 + jitter
            e = echo(m0, col, rim)
            if (f + i) % 3 == 0:
                e = shift_rows(e, 6 + i * 4, 9 + i * 4, 2)
            cv.alpha_composite(e, (x, 0))
        cv.alpha_composite(glitched(f, rnd), (3 * 13 + 2, 0))
        frames.append(Frame(padded(cv)))
    return frames


# --------------------------------------------------------------------------- light: the screens glow
def _screens_light(screens):
    import tokyo_props as tp

    def lf(w, h):
        A = tp.field(w, h)
        for sx, sy, k in screens(w, h):
            tp.radial(A, sx, sy, 12, 0.45 * k, squash=0.8)
        return A, rgb('#b06aff')
    return lf


PAD = 10
glitch_machine_light = _screens_light(lambda w, h: [(PAD + 2 + 10, PAD + 8, 1.0)])
glitch_machine_stack_light = _screens_light(lambda w, h: [(PAD + 6 + 10, PAD + 8, 1.0), (PAD + 6 + 10, PAD + MH + 8, 0.8)])
glitch_machine_smear_light = _screens_light(lambda w, h: [(PAD + 3 * 13 + 4 + 10, PAD + 8, 1.0), (PAD + 20, PAD + 10, 0.4)])

GLITCH = [
    ('glitch_machine', glitch_machine, FPS, 31, glitch_machine_light),
    ('glitch_machine_stack', glitch_machine_stack, FPS, 63, glitch_machine_stack_light),
    ('glitch_machine_smear', glitch_machine_smear, FPS, 31, glitch_machine_smear_light),
]
