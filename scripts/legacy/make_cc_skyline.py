"""City Connect pants hip graphic: flat skyline silhouette (live oak | Cupola | stadium light towers), one colour.
Mask: R = silhouette (tinted gold in the game), alpha = shape. 2048 wide strip centred in a square texture."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
S = 4; N = 2048 * S
im = Image.new('L', (N, N), 0); d = ImageDraw.Draw(im)
def P(x, y): return (x * S, y * S)
G = 1180                                                    # ground line (y, in 2048 px)
d.rectangle([P(150, G), P(1898, G + 22)], fill=255)       # ground strip
# --- live oak (left): short thick trunk, long low sprawling limbs, wide flat canopy
tx = 470
d.polygon([P(tx - 46, G), P(tx - 26, G - 120), P(tx - 34, G - 165), P(tx + 34, G - 165), P(tx + 26, G - 120), P(tx + 46, G)], fill=255)
for (x0, y0, x1, y1, w) in ((tx - 15, G - 150, tx - 250, G - 215, 30), (tx - 240, G - 215, tx - 330, G - 190, 18), (tx + 15, G - 150, tx + 260, G - 225, 30), (tx + 250, G - 225, tx + 340, G - 195, 18),
                            (tx, G - 160, tx - 60, G - 300, 24), (tx, G - 160, tx + 70, G - 310, 24), (tx - 130, G - 185, tx - 180, G - 280, 16), (tx + 140, G - 190, tx + 190, G - 285, 16)):
    d.line([P(x0, y0), P(x1, y1)], fill=255, width=w * S)
rng = np.random.default_rng(4)
for cx, cy, rx, ry in ((tx, G - 350, 190, 70), (tx - 210, G - 300, 160, 60), (tx + 220, G - 305, 160, 60), (tx - 330, G - 245, 80, 40), (tx + 340, G - 250, 80, 40), (tx - 90, G - 390, 120, 55), (tx + 100, G - 395, 120, 55)):
    for _ in range(14):
        ox, oy = rng.uniform(-0.75, 0.75) * rx, rng.uniform(-0.5, 0.5) * ry; rr = rng.uniform(0.25, 0.42) * rx
        d.ellipse([P(cx + ox - rr, cy + oy - rr * 0.6), P(cx + ox + rr, cy + oy + rr * 0.6)], fill=255)
# --- Cupola (centre)
cx = 1024
d.rectangle([P(cx - 175, G - 30), P(cx + 175, G)], fill=255)                     # plinth
d.rectangle([P(cx - 150, G - 290), P(cx + 150, G - 30)], fill=255)               # colonnade block
for ax in (-100, 0, 100):                                                          # arched openings (cut out)
    d.rectangle([P(cx + ax - 34, G - 210), P(cx + ax + 34, G - 30)], fill=0)
    d.ellipse([P(cx + ax - 34, G - 244), P(cx + ax + 34, G - 176)], fill=0)
d.rectangle([P(cx - 185, G - 325), P(cx + 185, G - 290)], fill=255)              # cornice
d.rectangle([P(cx - 160, G - 345), P(cx + 160, G - 325)], fill=255)
d.pieslice([P(cx - 160, G - 345 - 190), P(cx + 160, G - 345 + 190)], 180, 360, fill=255)   # dome
d.rectangle([P(cx - 22, G - 590), P(cx + 22, G - 530)], fill=255)                # lantern
d.polygon([P(cx - 34, G - 590), P(cx + 34, G - 590), P(cx, G - 640)], fill=255)
d.rectangle([P(cx - 5, G - 700), P(cx + 5, G - 630)], fill=255)                  # finial
d.ellipse([P(cx - 14, G - 682), P(cx + 14, G - 654)], fill=255)
# --- stadium (right): stepped stands with a press box, two light towers
sx = 1580
d.polygon([P(sx - 250, G), P(sx - 250, G - 90), P(sx - 150, G - 90), P(sx - 150, G - 150), P(sx + 60, G - 150), P(sx + 60, G - 205), P(sx + 180, G - 205), P(sx + 180, G - 245), P(sx + 310, G - 245), P(sx + 310, G)], fill=255)
for k in range(3): d.line([P(sx - 250, G - 30 - k * 22), P(sx + 310, G - 30 - k * 22)], fill=0, width=4 * S)
for lx, top in ((sx - 190, G - 540), (sx + 250, G - 600)):
    d.polygon([P(lx - 14, G - 80), P(lx - 6, top), P(lx + 6, top), P(lx + 14, G - 80)], fill=255)
    d.rectangle([P(lx - 62, top - 70), P(lx + 62, top)], fill=255)
    for i in range(4):
        for j in range(2): d.rectangle([P(lx - 52 + i * 27, top - 62 + j * 32), P(lx - 32 + i * 27, top - 40 + j * 32)], fill=0)
im = im.resize((2048, 2048), Image.LANCZOS)
al = np.asarray(im).astype(float)
rgba = np.dstack([np.full_like(al, 255), np.zeros_like(al), np.zeros_like(al), al]).astype(np.uint8)
Image.fromarray(rgba, 'RGBA').save('ECU_CC_Skyline_col.png')
# preview on midnight purple, tinted gold
bg = Image.new('RGBA', (2048, 2048), (44, 24, 78, 255)); fg = Image.new('RGBA', (2048, 2048), (253, 200, 47, 0)); fg.putalpha(im)
bg.alpha_composite(fg); bg.convert('RGB').crop((0, 300, 2048, 1300)).resize((1024, 500)).save('skyline_prev.png')
