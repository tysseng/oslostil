#!/usr/bin/env python3
"""Contact sheet of the landmark masters at one common scale (+ silhouettes on a sunset)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HI = Path(__file__).resolve().parents[2] / 'assets' / 'landmarks' / 'hires'
PPM = 4          # sheet px per metre (masters are 20 px/m)
ROWS = [['holmenkollen', 'munch', 'plaza', 'tryvann', 'radhuset'],
        ['opera', 'slottet', 'stortinget', 'nationaltheatret', 'universitetet', 'monolitten']]
if len(sys.argv) > 2:                    # contact.py out.png name,name name,name  (one arg per row)
    ROWS = [r.split(',') for r in sys.argv[2:]]
GAP, M, LAB = 40, 40, 30
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)


def load(n):
    im = Image.open(HI / f'{n}.png').convert('RGBA')
    return im.resize((round(im.width * PPM / 20), round(im.height * PPM / 20)), Image.LANCZOS)


ims = {n: load(n) for r in ROWS for n in r}
rw = [sum(ims[n].width for n in r) + GAP * (len(r) - 1) for r in ROWS]
rh = [max(ims[n].height for n in r) for r in ROWS]
W = max(rw) + 2 * M
sec = sum(rh) + LAB * 2 + GAP + 2 * M
sheet = Image.new('RGBA', (W, sec * 2), (236, 238, 241, 255))
# sunset gradient for the silhouette half
d = ImageDraw.Draw(sheet)
top = [(26, 12, 58), (120, 30, 110), (255, 92, 120), (255, 190, 110)]
for y in range(sec):
    t = y / (sec - 1) * 3
    i = min(int(t), 2)
    a, b = top[i], top[i + 1]
    u = t - i
    d.line([(0, sec + y), (W, sec + y)], fill=tuple(round(a[k] + (b[k] - a[k]) * u) for k in range(3)) + (255,))
for half in (0, 1):
    y = M + half * sec
    for r, h in zip(ROWS, rh):
        x = M + (W - 2 * M - sum(ims[n].width for n in r) - GAP * (len(r) - 1)) // 2
        for n in r:
            im = ims[n]
            if half:
                sil = Image.new('RGBA', im.size, (24, 10, 48, 255))
                sil.putalpha(im.getchannel('A'))
                im = sil
            sheet.alpha_composite(im, (x, y + h - im.height))
            d.text((x + im.width // 2, y + h + 6), n, fill=(60, 60, 70) if not half else (255, 230, 240), font=font, anchor='mt')
            x += ims[n].width + GAP
        y += h + LAB + GAP
    d.rectangle([W - M - 40 * PPM, M + half * sec, W - M, M + half * sec + 6], fill=(60, 60, 70) if not half else (255, 230, 240))
    d.text((W - M - 20 * PPM, M + half * sec + 12), '40 m', fill=(60, 60, 70) if not half else (255, 230, 240), font=font, anchor='mt')
out = Path(sys.argv[1])
sheet.convert('RGB').save(out)
print(out, sheet.size)
