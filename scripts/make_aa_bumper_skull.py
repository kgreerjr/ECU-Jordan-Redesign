# Away Alternate front bumper: the sleeve/hip skull (mod author's clean purple/white logo) in the bumper-art layout
# (square canvas; centred in the Bumper_ECU art box x 146-3950, y 1129-2966 of 4096, height-limited), as the bumper
# channel mask: R = white parts, G = purple parts (tinted white / purple). Edges re-sharpened like the sleeve skull.
# usage: make_aa_bumper_skull.py <ECU_skull_source_user.png> <out.png>
import sys, numpy as np
from PIL import Image
SRC, OUT = sys.argv[1:3]; N = 2048
src = np.asarray(Image.open(SRC).convert('RGBA')).astype(float) / 255
wsrc = np.clip((src[..., :3].mean(2) - 0.29) / (0.98 - 0.29), 0, 1)
ys, xs = np.where(src[..., 3] > 0.5)
bx0, by0, bx1, by1 = [v / 4096 * N for v in (146, 1129, 3950, 2966)]
k = min((bx1 - bx0) / (xs.max() - xs.min()), (by1 - by0) / (ys.max() - ys.min()))
size = (round(src.shape[1] * k), round(src.shape[0] * k))
up = lambda ch: np.asarray(Image.fromarray((np.clip(ch, 0, 1) * 255).astype(np.uint8)).resize(size, Image.LANCZOS)).astype(float) / 255
crisp = lambda m: np.clip((m - 0.5) * 2.2 / 1.5 + 0.5, 0, 1)
Au = up(src[..., 3]); Wu = crisp(up(wsrc * src[..., 3]) / np.clip(Au, 1e-3, None)); Au = crisp(Au)
A = np.zeros((N, N)); Wm = np.zeros((N, N))
ox = int(round((bx0 + bx1) / 2 - (xs.min() + xs.max()) / 2 * k)); oy = int(round((by0 + by1) / 2 - (ys.min() + ys.max()) / 2 * k))
y0, x0 = max(oy, 0), max(ox, 0); y1, x1 = min(oy + Au.shape[0], N), min(ox + Au.shape[1], N)
A[y0:y1, x0:x1] = Au[y0 - oy:y1 - oy, x0 - ox:x1 - ox]; Wm[y0:y1, x0:x1] = Wu[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
on = (A > 0).astype(float)
srgb = lambda c: np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
out = np.dstack([srgb(Wm * on), srgb((1 - Wm) * on), np.zeros_like(A), A])
Image.fromarray((out * 255 + 0.5).clip(0, 255).astype(np.uint8), 'RGBA').save(OUT); print(OUT, 'k', round(k, 3))
