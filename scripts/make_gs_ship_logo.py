# Ghost Ship helmet logo v6 (mod author's ship art): cut out of the black JPG background, decomposed into the helmet decal's
# tint-mask channels (R = lavender, G = white, B = gray, remainder = line), fit to the stock skull's footprint.
# Lines are nudged to a dark gray (K x the gray channel) like the skull mask. Stored sRGB-encoded like the stock mask.
import sys, numpy as np
from PIL import Image
from scipy import ndimage
SRC = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else 'ECU_GS_Helmet_Logo_col.png'; K = 0.06
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.75   # share of the stock skull footprint (v1 = 1.0, mod author: 'should be smaller')
DX = int(sys.argv[4]) if len(sys.argv) > 4 else 120; DY = int(sys.argv[5]) if len(sys.argv) > 5 else -95   # px on the 1024 canvas: +x = toward the back of the helmet (facemask covered the bow at 0,0)
lin = lambda c: np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
srgb = lambda l: np.where(l <= 0.0031308, l * 12.92, 1.055 * np.clip(l, 0, None) ** (1 / 2.4) - 0.055)
im = np.asarray(Image.open(SRC).convert('RGB')).astype(float) / 255; lum = im.mean(-1)
# --- cut-out: black connected to the image border = background ---
lab, n = ndimage.label(lum < 0.12); edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
bg = np.isin(lab, list(edge)); near = ndimage.binary_dilation(bg, iterations=3) & ~bg
alpha = (~bg).astype(float); alpha[near] = np.clip((lum[near] - 0.08) / 0.55, 0, 1)        # anti-aliased rim from luminance
col = im.copy(); m = near & (alpha > 0.05); col[m] = np.clip(im[m] / alpha[m, None], 0, 1)     # un-premultiply the black fringe
# --- classify each pixel to the nearest palette color (L lavender, W white, G gray, D line) on a denoised copy, then soften the class edges ---
den = ndimage.median_filter(col, size=(5, 5, 1))
P = np.array([[180, 160, 205], [245, 245, 246], [198, 198, 203], [50, 49, 58], [146, 146, 156], [112, 112, 118]]) / 255   # + shadow grays (kept gray, not lavender)
d = ((den[..., None, :] - P[None, None]) ** 2 * np.array([1, 1.6, 1])).sum(-1); cls = d.argmin(-1)
one = np.stack([(cls == k).astype(float) for k in range(6)], -1); one = ndimage.gaussian_filter(one, sigma=(1.2, 1.2, 0))
L, W, G, D = (one[..., k] for k in range(4)); G = G + 0.5 * one[..., 4] + 0.3 * one[..., 5]; D = D + 0.5 * one[..., 4] + 0.7 * one[..., 5]; G = G + K * D
mask = np.dstack([L, W, G])
# --- crop + fit into the stock skull footprint (512 bbox 38..475 x 22..488 -> x2 on a 1024 canvas) ---
ys, xs = np.where(alpha > 0.05); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
rgba = np.dstack([srgb(mask), alpha])[y0:y1, x0:x1]
bw, bh = (475 - 38) * 2 * SCALE, (488 - 22) * 2 * SCALE; cx, cy = (38 + 475) + DX, (22 + 488) + DY
s = min(bw / rgba.shape[1], bh / rgba.shape[0]); w, h = int(rgba.shape[1] * s), int(rgba.shape[0] * s)
small = np.asarray(Image.fromarray((rgba * 255 + 0.5).astype(np.uint8), 'RGBA').resize((w, h), Image.LANCZOS)).astype(float) / 255
out = np.zeros((1024, 1024, 4)); out[cy - h // 2:cy - h // 2 + h, cx - w // 2:cx - w // 2 + w] = small
# bleed channel values into transparent pixels (clean mips)
idx = ndimage.distance_transform_edt(out[..., 3] < 0.02, return_distances=False, return_indices=True)
out[..., :3] = out[..., :3][idx[0], idx[1]]
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').save(OUT)
# preview with the build's tints on the cool-white shell, full size + "game camera" size
hx = lambda h: lin(np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255)
TL, TW, TG, SHELL = hx('#B9A2DC'), hx('#F2F2F5'), hx('#C6C6CA'), hx('#E9EAF0')
mm = lin(out[..., :3]); rgb = mm[..., 0:1] * TL + mm[..., 1:2] * TW + mm[..., 2:3] * TG; al = out[..., 3:4]
comp = (srgb(rgb * al + SHELL * (1 - al)) * 255 + 0.5).astype(np.uint8)
big = Image.fromarray(comp).resize((512, 512), Image.LANCZOS); tiny = Image.fromarray(comp).resize((64, 64), Image.LANCZOS).resize((256, 256), Image.NEAREST)
pv = Image.new('RGB', (768, 512), (233, 234, 240)); pv.paste(big, (0, 0)); pv.paste(tiny, (512, 128)); pv.save('preview_' + OUT); print('ok', w, h)
