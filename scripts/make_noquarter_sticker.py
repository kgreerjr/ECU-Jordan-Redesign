# "NO QUARTER" helmet sticker (replaces the AAC sticker, 2026-11-17). Source: the user's Gemini flag on green
# (ECU_NoQuarter_source.jpg: purple field, gold skull/cutlasses/lettering, white die-cut border).
# Unmix every pixel into green / purple / gold / white, cut out, centre on a square canvas (flag 92% of the width), and
# store as the AAC sticker's channels so each helmet's existing AAC tints color it:
#   R = flag field (AAC main color), G = border (AAC outline), B = artwork + lettering (AAC accent).
# usage: make_noquarter_sticker.py <source.jpg> <out.png> [canvas px]
import sys, numpy as np
from PIL import Image
from scipy import ndimage
SRC, OUT = sys.argv[1:3]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
img = ndimage.gaussian_filter(np.asarray(Image.open(SRC).convert('RGB')).astype(float), (0.8, 0.8, 0))
C = np.array([[20, 245, 20], [67, 28, 107], [246, 194, 53], [253, 254, 253]], float).T     # green, purple, gold, white
M = np.vstack([C, 400 * np.ones(4)]); px = img.reshape(-1, 3).T
w = np.linalg.lstsq(M, np.vstack([px, 400 * np.ones((1, px.shape[1]))]), rcond=None)[0].T.clip(0, None)
w /= np.clip(w.sum(1, keepdims=True), 1e-6, None); w = w.reshape(img.shape[0], img.shape[1], 4)
A = 1 - w[..., 0]; P, Gd, Wh = w[..., 1], w[..., 2], w[..., 3]
lab, n = ndimage.label(A > 0.5); keep = lab == (1 + int(np.argmax(ndimage.sum(A > 0.5, lab, range(1, n + 1)))))
keep = ndimage.binary_fill_holes(keep); keep = ndimage.binary_dilation(keep, iterations=2)
A = A * keep; ys, xs = np.where(A > 0.5)
sl = (slice(ys.min() - 4, ys.max() + 5), slice(xs.min() - 4, xs.max() + 5))
k = 0.92 * N / (xs.max() - xs.min())
size = (round((sl[1].stop - sl[1].start) * k), round((sl[0].stop - sl[0].start) * k))
rs = lambda m: np.asarray(Image.fromarray((np.clip(m[sl], 0, 1) * 255).astype(np.uint8)).resize(size, Image.LANCZOS)).astype(float) / 255
Ar, Pr, Gr, Wr = rs(A), rs(P * keep), rs(Gd * keep), rs(Wh * keep)
canvas = np.zeros((N, N, 4)); oy, ox = (N - size[1]) // 2, (N - size[0]) // 2
s = np.clip(Pr + Gr + Wr, 1e-6, None)
srgb = lambda c: np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
on = (Ar > 0.02)
canvas[oy:oy + size[1], ox:ox + size[0]] = np.dstack([srgb(Pr / s) * on, srgb(Wr / s) * on, srgb(Gr / s) * on, Ar * on])
Image.fromarray((canvas * 255 + 0.5).clip(0, 255).astype(np.uint8), 'RGBA').save(OUT); print(OUT, N, 'px, flag', size)
