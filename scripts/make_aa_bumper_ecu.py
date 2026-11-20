# Away Alternate back bumper: the jersey's chest ECU (Merriweather Black Italic, purple fill / gold outline / thin white
# outer) in the bumper-art layout (square canvas, art box like Bumper_ECU.png: x 146-3950, y 1129-2966 of 4096), as the
# bumper channel mask: R = fill, G = inner ring, B = outer ring (tinted purple / gold / white on this helmet).
# usage: make_aa_bumper_ecu.py <font.ttf> <out.png>
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
FONT, OUT = sys.argv[1:3]; N = 2048; SS = 2; W = N * SS
font = ImageFont.truetype(FONT, 600 * SS)
try: font.set_variation_by_axes([a['maximum'] if a.get('name') in (b'Weight', 'Weight') else a['default'] for a in font.get_variation_axes()])
except Exception: pass
txt = Image.new('L', (W, W), 0); d = ImageDraw.Draw(txt); bb = d.textbbox((0, 0), 'ECU', font=font)
x = W * 0.05; y = (W - (bb[3] - bb[1])) / 2 - bb[1]
for ch in 'ECU':                                    # same letter spacing as the jersey (0.07 x cap height)
    d.text((x, y), ch, font=font, fill=255); x += d.textlength(ch, font=font) + 0.07 * (bb[3] - bb[1])
fill = np.asarray(txt) > 127; cap = bb[3] - bb[1]
dist = ndimage.distance_transform_edt(~fill)
gold = (dist <= 0.05 * cap) & ~fill; white = (dist > 0.05 * cap) & (dist <= 0.072 * cap)
cover = fill | gold | white; ys, xs = np.where(cover)
# fit inside the Bumper_ECU art box (scaled to this canvas), centred on it
bx0, by0, bx1, by1 = [v / 4096 * W for v in (146, 1129, 3950, 2966)]
k = min((bx1 - bx0) / (xs.max() - xs.min()), (by1 - by0) / (ys.max() - ys.min()))
def place(m):
    z = ndimage.zoom(m.astype(float), k, order=1); out = np.zeros((W, W))
    cy, cx = (ys.min() + ys.max()) / 2 * k, (xs.min() + xs.max()) / 2 * k
    oy, ox = int((by0 + by1) / 2 - cy), int((bx0 + bx1) / 2 - cx)
    y0, x0 = max(oy, 0), max(ox, 0); y1, x1 = min(oy + z.shape[0], W), min(ox + z.shape[1], W)
    out[y0:y1, x0:x1] = z[y0 - oy:y1 - oy, x0 - ox:x1 - ox]; return out
F, G, B = (place(m).reshape(N, SS, N, SS).mean((1, 3)) for m in (fill, gold, white))
A = np.clip(F + G + B, 0, 1); s = np.clip(F + G + B, 1e-6, None)
rgb = np.dstack([F / s, G / s, B / s]) * (A[..., None] > 0)
srgb = lambda c: np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
Image.fromarray((np.dstack([srgb(rgb), A]) * 255 + 0.5).clip(0, 255).astype(np.uint8), 'RGBA').save(OUT); print(OUT, 'k', round(k, 3))
