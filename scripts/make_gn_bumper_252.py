# Greenville Nights front bumper: "252" (Greenville's area code) in the style of the ECU front-bumper art
# (Bumper_ECU.png): same canvas, same pennant (copied from that art), same letter box (y 1213-2300 of 4096), same
# slant (0.206), same build: squared heavy glyphs (bars 0.16 H, stems 0.33 H, glyph width ~1.0 H, one rounded outer
# corner like E/C/U), each glyph with its own white ring (44 px) and purple ring (40 px), glyph gap 130 px.
# Channels like the source art: R = fill, G = inner (white) ring, B = outer (purple) ring, alpha = coverage.
# usage: make_gn_bumper_252.py <Bumper_ECU.png> <out.png>
import sys, numpy as np
from PIL import Image
from scipy import ndimage
SRC, OUT = sys.argv[1:3]; N = 4096
src = np.asarray(Image.open(SRC).convert('RGBA')).astype(int)
SR = (src[..., 0] > 128) & (src[..., 3] > 128)
TOP, BOT, SLANT = 1213, 2300, 0.206
H = BOT - TOP + 1; T, V, W, GAP, RAD = 170, 360, 1050, 130, 190
pennant = SR.copy(); pennant[:2380] = False                       # the swoosh pennant under the letters
def glyph(kind):
    m = np.zeros((H, W), bool); mid0, mid1 = (H - T) // 2, (H + T) // 2
    m[:T] = True; m[mid0:mid1] = True; m[H - T:] = True               # three bars
    if kind == '2': m[:mid1, W - V:] = True; m[mid0:, :V] = True; corner = 'tl'
    else:           m[:mid1, :V] = True; m[mid0:, W - V:] = True; corner = 'br'
    yy, xx = np.mgrid[0:H, 0:W]
    if corner == 'tl': cut = (yy < RAD) & (xx < RAD) & ((yy - RAD) ** 2 + (xx - RAD) ** 2 > RAD ** 2)
    else:              cut = (yy > H - RAD) & (xx > W - RAD) & ((yy - (H - RAD)) ** 2 + (xx - (W - RAD)) ** 2 > RAD ** 2)
    m[cut] = False
    if kind == '2':   # also round the 2's top-right like the C, so the top reads as one bar
        cut2 = (yy < RAD) & (xx > W - RAD) & ((yy - RAD) ** 2 + (xx - (W - RAD)) ** 2 > RAD ** 2); m[cut2] = False
    return m
total = 3 * W + 2 * GAP + int(SLANT * H)
ecu_c = (292 + 3823) / 2; x0 = int(ecu_c - total / 2)
fills = []
for i, ch in enumerate('252'):
    g = glyph(ch); canvas = np.zeros((N, N), bool)
    gx = x0 + i * (W + GAP)
    # shear: a row at height y (from the bottom) shifts right by SLANT * (BOT - y)
    for r in range(H):
        sh = int(round(SLANT * (H - 1 - r))); y = TOP + r
        canvas[y, gx + sh:gx + sh + W] = g[r]
    fills.append(canvas)
fills.append(pennant)
F = np.zeros((N, N), bool); WH = np.zeros((N, N), bool); PU = np.zeros((N, N), bool)
for f in fills:
    d = ndimage.distance_transform_edt(~f)   # (chessboard rings stair-stepped on the slanted sides)
    F |= f; WH |= (d <= 44) & ~f; PU |= (d > 44) & (d <= 84)
WH &= ~F; PU &= ~(F | WH)
def down(m): return m.reshape(N // 2, 2, N // 2, 2).mean((1, 3))
Fd, Wd, Pd = down(F.astype(float)), down(WH.astype(float)), down(PU.astype(float))
A = np.clip(Fd + Wd + Pd, 0, 1); s = np.clip(Fd + Wd + Pd, 1e-6, None)
srgb = lambda c: np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
out = np.dstack([srgb(Fd / s), srgb(Wd / s), srgb(Pd / s), A]) * (A[..., None] > 0)
out[..., 3] = A
Image.fromarray((out * 255 + 0.5).clip(0, 255).astype(np.uint8), 'RGBA').save(OUT); print(OUT, '2048 px, letters x', x0, x0 + total)
