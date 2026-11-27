"""Contact sheet: logos ×4 nearest on light, girl for scale; then all on the in-game title backdrop ×2."""
import sys
from PIL import Image, ImageDraw
args = sys.argv[1:]
compact = '--compact' in args
args = [a for a in args if a != '--compact']
root, out, *logos = args
girl = Image.open(f'{root}/assets/sprites/victoria.png').convert('RGBA').crop((0, 0, 24, 32))
import os
ims = [Image.open(p).convert('RGBA') for p in logos]
lights = [Image.open(p[:-4] + '-light.png').convert('RGBA') if os.path.exists(p[:-4] + '-light.png') else None for p in logos]
S = 4; LIGHT = (232, 230, 236, 255); M = 16
W = max(i.width for i in ims) * S + 24 * S + 3 * M
rows = []
for im in ims:
    r = Image.new('RGBA', (W, im.height * S + 2 * M), LIGHT)
    r.alpha_composite(im.resize((im.width * S, im.height * S), Image.NEAREST), (M, M))
    r.alpha_composite(girl.resize((24 * S, 32 * S), Image.NEAREST), (W - 24 * S - M, M + im.height * S - 32 * S))
    ImageDraw.Draw(r).text((4, 2), im_name := logos[ims.index(im)].split('/')[-1], fill=(60, 60, 70))
    rows.append(r)
# game backdrop: 320×180 neon sky, logo at (54, 12), ground at 150
def backdrop(im, li=None):
    b = Image.new('RGBA', (320, 180))
    d = ImageDraw.Draw(b)
    for y in range(150):
        t = y / 149; c = tuple(round(a + (bb - a) * t) for a, bb in zip((0x12, 0, 0x2b), (0x5b, 0x0f, 0x6e)))
        d.line([(0, y), (319, y)], fill=c + (255,))
    d.rectangle([0, 150, 319, 179], fill=(0x16, 0, 0x22, 255)); d.line([(0, 150), (319, 150)], fill=(0xff, 0x4f, 0xd8, 255))
    for i in range(12): d.line([(i * 32, 150), (i * 32, 179)], fill=(0xff, 0x4f, 0xd8, 255))
    b.alpha_composite(im, ((320 - im.width) // 2, 12))
    if li is not None: b.alpha_composite(li, ((320 - im.width) // 2 - 16, 12 - 16))
    b.alpha_composite(girl, (140, 150 - 32))
    return b.resize((640, 360), Image.NEAREST)
bds = [backdrop(i, l) for i, l in zip(ims, lights)]
per = 2 if len(ims) > 1 else 1
sc = min(1.0, (W - M * (per + 1)) / (640 * per))
bw, bh = int(640 * sc), int(360 * sc)
nrow = (len(bds) + per - 1) // per
dark = Image.new('RGBA', (W, nrow * (bh + M) + M), (20, 12, 30, 255))
for k, bd in enumerate(bds):
    bd = bd.resize((bw, bh), Image.NEAREST); dark.alpha_composite(bd, (M + (k % per) * (bw + M), M + (k // per) * (bh + M)))
for im, li in zip(ims, lights):
    if li is None or compact: continue
    r = Image.new('RGBA', (W, im.height * S + 2 * M), (0x24, 0x05, 0x40, 255))
    r.alpha_composite(im.resize((im.width * S, im.height * S), Image.NEAREST), (M, M))
    L = li.resize((li.width * S, li.height * S), Image.BILINEAR)
    big = Image.new('RGBA', r.size); big.alpha_composite(L, (M - 16 * S, M - 16 * S)) if False else None
    tmp = Image.new('RGBA', (r.width + 32 * S, r.height + 32 * S)); tmp.alpha_composite(L, (M, M))
    r.alpha_composite(tmp.crop((16 * S, 16 * S, 16 * S + r.width, 16 * S + r.height)))
    r.alpha_composite(girl.resize((24 * S, 32 * S), Image.NEAREST), (W - 24 * S - M, M + im.height * S - 32 * S))
    rows.append(r)
H = sum(r.height for r in rows) + dark.height
sheet = Image.new('RGBA', (W, H)); y = 0
for r in rows + [dark]: sheet.alpha_composite(r, (0, y)); y += r.height
sheet.convert('RGB').save(out)
