"""City Connect chest wordmark: the game's own PIRATES (ECU_Decal_2021_03_col, alpha = letters) repainted airbrush style:
gold gradient + sprayed edge shading + upper-left highlight + grain, white outline like the numbers.
Letters shrunk to K inside the texture to make room for the outline (layer scale is raised by 1/K to keep the size)."""
import sys, struct, numpy as np, texture2ddecoder
from PIL import Image
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]; K = 0.92; N = 2048
b = open(src, 'rb').read(); w, h = struct.unpack('<II', b[16:20])[::-1] if False else struct.unpack('<II', b[12:20])[::-1]
raw = texture2ddecoder.decode_bc3(b[148:148 + (w // 4) * (h // 4) * 16], w, h)
A = np.asarray(Image.frombytes('RGBA', (w, h), raw, 'raw', 'BGRA'))[..., 3].astype(float) / 255
big = np.asarray(Image.fromarray((A * 255).astype(np.uint8)).resize((N, N), Image.BICUBIC)).astype(float) / 255
big = np.clip((big - 0.5) / 0.12 + 0.5, 0, 1)                                   # re-sharpen the upscaled edges
k = int(N * K); sm = np.asarray(Image.fromarray((big * 255).astype(np.uint8)).resize((k, k), Image.LANCZOS)).astype(float) / 255
L = np.zeros((N, N)); o = (N - k) // 2; L[o:o + k, o:o + k] = sm                # letters, centred
inside = L > 0.5
d_in = ndimage.distance_transform_edt(inside)                                   # px from the letter edge (inside)
yy, xx = np.mgrid[0:N, 0:N] / N
ys = np.where(inside.any(1))[0]; y0, y1 = ys.min() / N, ys.max() / N
t = np.clip((yy - y0) / (y1 - y0), 0, 1)
TOP, BOT = np.array([255, 224, 120.]), np.array([214, 150, 20.])
col = TOP * (1 - t[..., None]) + BOT * t[..., None]
shade = np.clip(d_in / 14, 0, 1) ** 0.6                                         # sprayed darkening toward the letter edges
col = col * (0.72 + 0.28 * shade[..., None])
hl = np.exp(-(((xx - 0.30) / 0.22) ** 2 + ((yy - (y0 + 0.25 * (y1 - y0))) / 0.04) ** 2))   # soft highlight, upper left
col = col + hl[..., None] * np.array([60, 50, 30.]) * shade[..., None]
rng = np.random.default_rng(5); col = col * (1 + 0.035 * rng.normal(0, 1, (N, N))[..., None])
OUT = 12                                                                         # white outline width (px at 2048)
d_out = ndimage.distance_transform_edt(~inside)
ring = np.clip(OUT + 0.5 - d_out, 0, 1)
alpha = np.maximum(L, ring)
WHITE = np.array([246, 244, 250.])
rgb = np.where(L[..., None] > 0, col * L[..., None] + WHITE * (1 - L[..., None]), WHITE)
img = np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8)
Image.fromarray(img, 'RGBA').save(out)
print('ok; raise the layer scale by', round(1 / K, 4))
