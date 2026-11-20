"""Away Alternate (6.0) jersey art.
1) ECU chest wordmark: serif italic ECU (Merriweather Black Italic), purple fill / gold outline / thin white outer
   outline, after the reference jersey. Channel mask like the EA jersey decals (alpha = coverage; R fill, G gold ring,
   B white ring -> tinted Purple / Gold / White). Plus a tackle-twill normal map and an rsm (values from ECU_Decal_2021_03).
2) Sleeve skull: ECU's standard skull & crossbones (BLA decal mask) in purple and white only:
   R = white (skull, bones, trim, bandana, hat ECU), G = purple (hat + line work). Tinted White / Purple.
usage: make_awayalt_art.py <font.ttf> <BLA_Decal_col_mask.png> <outdir>"""
import sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

FONT, SKULL, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
N = 1024
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def srgb(c): return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
def save(arr, name, encode_srgb=False):
    a = arr.copy()
    if encode_srgb: a[..., :3] = srgb(a[..., :3])
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').save(os.path.join(OUT, name))

# ---------------- ECU wordmark ----------------
SS = 4                                            # supersample
font = ImageFont.truetype(FONT, 300 * SS)
try:
    font.set_variation_by_axes([a['maximum'] if a.get('name') in (b'Weight', 'Weight') else a['default'] for a in font.get_variation_axes()])
except Exception:
    pass
W = N * SS
txt = Image.new('L', (W, W), 0); d = ImageDraw.Draw(txt)
TRACK = 0.07                                      # extra gap between letters (x cap height) so the outlines don't merge
bb = d.textbbox((0, 0), 'ECU', font=font)
x = W * 0.08; y = (W - (bb[3] - bb[1])) / 2 - bb[1]
for ch in 'ECU':
    d.text((x, y), ch, font=font, fill=255)
    x += d.textlength(ch, font=font) + TRACK * (bb[3] - bb[1])
fill = np.asarray(txt).astype(float) / 255 > 0.5
cap = bb[3] - bb[1]
dist_out = ndimage.distance_transform_edt(~fill)  # distance outside the letters
GOLD_W, WHITE_W = 0.05 * cap, 0.022 * cap
gold = (dist_out <= GOLD_W) & ~fill
white = (dist_out > GOLD_W) & (dist_out <= GOLD_W + WHITE_W)
cover = fill | gold | white
# fit: total height ~30% of the canvas, centred (PIRATES on Home is 20% tall, full width)
ys, xs = np.where(cover)
h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
k = min(0.30 * W / h, 0.94 * W / w)
def fit(m):
    z = ndimage.zoom(m.astype(float), k, order=1)
    cy, cx = ndimage.center_of_mass(cover.astype(float)) if False else ((ys.min() + ys.max()) / 2 * k, (xs.min() + xs.max()) / 2 * k)
    out = np.zeros((W, W)); oy, ox = int(W / 2 - cy), int(W / 2 - cx)
    y0, x0 = max(oy, 0), max(ox, 0); y1, x1 = min(oy + z.shape[0], W), min(ox + z.shape[1], W)
    out[y0:y1, x0:x1] = z[y0 - oy:y1 - oy, x0 - ox:x1 - ox]; return out
F, G, Wh = fit(fill), fit(gold), fit(white)
def down(m): return m.reshape(N, SS, N, SS).mean((1, 3))
F, G, Wh = down(F), down(G), down(Wh)
A = np.clip(F + G + Wh, 0, 1); s = np.clip(F + G + Wh, 1e-6, None)
col = np.dstack([F / s * (A > 0), G / s * (A > 0), Wh / s * (A > 0), A])
save(col, 'ECU_AA_WM_col.png', encode_srgb=True)

# height: fill (raised twill) > gold ring > white ring; soft bevels; diagonal twill weave
def bevel(m, r): return ndimage.gaussian_filter(m, r)
hgt = 1.0 * bevel(F, 1.6) + 0.55 * bevel(F + G, 1.6) + 0.25 * bevel(A, 1.6)
yy, xx = np.mgrid[0:N, 0:N]
twill = 0.5 + 0.5 * np.sin((xx + yy) * 2 * np.pi / 4.0)
hgt = hgt + 0.06 * twill * (F + G)
dy, dx = np.gradient(hgt)
K = 3.5
nx, ny = -dx * K, dy * K
nz = np.ones_like(nx); L = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
norm = np.dstack([nx / L * 0.5 + 0.5, ny / L * 0.5 + 0.5, nz / L, np.ones_like(nx)])
save(norm, 'ECU_AA_WM_norm.png')
cov = np.clip(F + G, 0, 1)
rsm = np.dstack([(66 + (93 - 66) * cov + 10 * (twill - 0.5) * cov) / 255,
                 (79 * cov + 10 * (twill - 0.5) * cov) / 255, np.zeros_like(cov), np.ones_like(cov)])
save(rsm, 'ECU_AA_WM_rsm.png')

# ---------------- sleeve skull ----------------
# Source: the user's clean purple/white logo (ECU_skull_source_user.png, transparent background). Upscaled ~2.2x with
# Lanczos, then the edges are re-sharpened with a 1.5 px ramp so they come out crisp (the old 512 mask was grainy).
# Placed in the same box as the first version so the in-editor size/position doesn't change.
USER = os.path.join(os.path.dirname(os.path.abspath(SKULL)), 'ECU_skull_source_user.png') if not os.path.exists('art/ECU_skull_source_user.png') else 'art/ECU_skull_source_user.png'
src = np.asarray(Image.open(USER).convert('RGBA')).astype(float) / 255
lum = src[..., :3].mean(2)
PURPLE_L, WHITE_L = 0.29, 0.98                                      # measured: purple ~(76,37,100), white 255
wsrc = np.clip((lum - PURPLE_L) / (WHITE_L - PURPLE_L), 0, 1)      # 1 = white part of the logo
ys, xs = np.where(src[..., 3] > 0.5)
BOX = (78, 51, 945, 972)                                            # x0, y0, x1, y1 of the first version on the 1024 canvas
k = min((BOX[2] - BOX[0]) / (xs.max() - xs.min()), (BOX[3] - BOX[1]) / (ys.max() - ys.min()))
def up(ch):
    im = Image.fromarray((ch * 65535).astype(np.uint16) if False else (ch * 255).astype(np.uint8))
    im = im.resize((round(src.shape[1] * k), round(src.shape[0] * k)), Image.LANCZOS)
    return np.asarray(im).astype(float) / 255
Au, Wu = up(src[..., 3]), up(wsrc * (src[..., 3] > 0.02))
def crisp(m, ramp=1.5): return np.clip((m - 0.5) * (1 / (ramp / 2.2 * 0.5)) * 0.5 + 0.5, 0, 1) if False else np.clip((m - 0.5) * 2.2 / ramp + 0.5, 0, 1)
Au, Wu = crisp(Au), crisp(Wu / np.clip(up(src[..., 3]), 1e-3, None) * (Au > 0))
canvas_a, canvas_w = np.zeros((N, N)), np.zeros((N, N))
cx, cy = (BOX[0] + BOX[2]) / 2, (BOX[1] + BOX[3]) / 2
sx, sy = (xs.min() + xs.max()) / 2 * k, (ys.min() + ys.max()) / 2 * k
ox, oy = int(round(cx - sx)), int(round(cy - sy))
y0, x0 = max(oy, 0), max(ox, 0); y1, x1 = min(oy + Au.shape[0], N), min(ox + Au.shape[1], N)
canvas_a[y0:y1, x0:x1] = Au[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
canvas_w[y0:y1, x0:x1] = Wu[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
Al = canvas_a; white_m = canvas_w
purple_m = 1 - white_m
sk = np.dstack([white_m * (Al > 0), purple_m * (Al > 0), np.zeros_like(Al), Al])
save(sk, 'ECU_AA_Skull_col.png', encode_srgb=True)

# ---------------- previews on the white jersey ----------------
PU, GO, WH = np.array([89, 42, 138]) / 255, np.array([253, 200, 47]) / 255, np.ones(3)
JERSEY = np.array([0.93, 0.93, 0.93])
def prev(c, cols, name):
    rgb = sum(c[..., i:i + 1] * cols[i] for i in range(len(cols)))
    o = rgb * c[..., 3:4] + JERSEY * (1 - c[..., 3:4])
    Image.fromarray((o * 255).astype(np.uint8)).save(os.path.join(OUT, name))
prev(col, (PU, GO, WH), 'preview_ECU_wordmark.png')
prev(sk, (WH, PU), 'preview_skull.png')
print('done', k)
