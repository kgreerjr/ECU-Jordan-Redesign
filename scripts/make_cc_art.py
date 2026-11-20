"""ITEM 10: City Connect helmet art (v4, final layout like the concept).
Inputs (FINAL/.../City Connect): ECU_CC_Helmet_Left_col.jpg (Cupola), ECU_CC_Helmet_Right_col.jpg (storm sky + small stadium),
ECU_CC_Logo.jpg (Gemini airbrushed ECU logo on solid green).
- Left: zoomed 1.25x (crop x 0.10-0.90, y 0.11-0.91) so the Cupola sits between the two Gemini sizes.
- Both: top 15% darkened to near-black purple so the halves meet cleanly under the gold stripe.
- Right: whole painting fitted into the visible window (see FIT); logo keyed off the green (despilled, Gemini's white outer keyline removed) and placed in the open sky.
- Stripe: gold center stripe + 2 gold pinstripes, clear between (ECU_CC_Helmet_Back_col).
usage: make_cc_art.py <src folder> <out folder> [logo size] [logo cx] [logo cy] [keep_outline 0/1]"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage
SRC, OUT = sys.argv[1], sys.argv[2]
LS = float(sys.argv[3]) if len(sys.argv) > 3 else 0.30
LX = float(sys.argv[4]) if len(sys.argv) > 4 else 0.50
LY = float(sys.argv[5]) if len(sys.argv) > 5 else 0.38
KEEP = len(sys.argv) > 6 and sys.argv[6] == '1'
N = 2048; TOP = np.array([14, 6, 30], float); GOLD = np.array([253, 200, 47], float)
def load(n): return np.asarray(Image.open(f'{SRC}/{n}').convert('RGB')).astype(float)
SEAM = np.array([16, 8, 34], float)   # v5: no stripe - both halves fade to this exact colour at every edge they share
def seam_fade(a, back_right, top=0.22, side=0.18):
    y = np.arange(N) / N; x = np.arange(N) / N
    wt = np.clip(1 - y / top, 0, 1) ** 1.6
    xb = (1 - x) if back_right else x                          # distance from the back edge
    xf = x if back_right else (1 - x)                          # distance from the front edge
    ws = np.maximum(np.clip(1 - xb / side, 0, 1), np.clip(1 - xf / side, 0, 1)) ** 1.6
    w = np.maximum(wt[:, None], ws[None, :])[..., None]
    return a * (1 - w) + SEAM * w
def darken_top(a, h=0.15):
    H = int(h * N)
    for y in range(H):
        t = (y / H) ** 1.4; a[y] = TOP * (1 - t) + a[y] * t
    return a
def fit(img, F, cxf, cyf, top=0.30):
    """shrink a square painting into the helmet's visible window and extend its edges into the hidden margins"""
    k = int(F * N); cx, cy = int(cxf * N), int(cyf * N)
    sm = np.asarray(Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((k, k), Image.LANCZOS)).astype(float)
    x0, y0 = cx - k // 2, cy - k // 2
    yi = np.clip(np.arange(N) - y0, 0, k - 1); xi = np.clip(np.arange(N) - x0, 0, k - 1)
    ext = ndimage.gaussian_filter(sm[yi][:, xi], (40, 40, 0))
    inside = np.zeros((N, N)); inside[max(y0, 0):y0 + k, max(x0, 0):x0 + k] = 1
    inside = ndimage.gaussian_filter(ndimage.binary_erosion(inside, iterations=30).astype(float), 18)
    return darken_top(ext * (1 - inside[..., None]) + sm[yi][:, xi] * inside[..., None], top)
L = Image.open(f'{SRC}/ECU_CC_Helmet_Left_col.jpg').convert('RGB')
L = L.crop((int(.10 * L.width), int(.11 * L.height), int(.90 * L.width), int(.91 * L.height))).resize((N, N), Image.LANCZOS)
L = np.asarray(L).astype(float)
# v4.4 (cohesion with the right side): cooler, darker sky like the storm side (less magenta), same dark crown,
# Cupola raised above the ear holes / chin strap and moved back out from behind the facemask clips, sized to match the skull.
L = L * np.array([0.86, 0.93, 1.0]) * 0.94
L = fit(L, 0.62, 0.49, 0.48)   # v5 (user): zoomed out, Cupola smaller and toward the front
# v4.5 (user: the oak fading out at the back looked incomplete): the scene's cut-off oak at the back becomes plain sky and a
# whole airbrushed oak (ECU_CC_Tree.png, transparent PNG) stands on the back quarter, trunk to canopy, ending at the stripe.
import os
TREE = f'{SRC}/ECU_CC_Tree.png'
if os.path.exists(TREE):
    band = L[:, int(0.35 * N):int(0.55 * N)].mean(1); Ssky = np.repeat(band[:, None, :], N, axis=1)
    TW, CXT, BASE = 0.25, 0.71, 0.63   # v5: whole tree inside the visible side (x ~0.33-0.84)
    ramp = np.clip((np.arange(N) - 0.56 * N) / (0.08 * N), 0, 1)[None, :]
    ground = np.clip((np.arange(N) - (BASE - 0.03) * N) / (0.03 * N), 0, 1)[:, None]
    w = (ramp * (1 - ground))[..., None]; L = L * (1 - w) + Ssky * w
    T = Image.open(TREE).convert('RGBA'); T = T.crop(T.getbbox())
    tw = int(TW * N); th = int(T.height * tw / T.width); T = np.asarray(T.resize((tw, th), Image.LANCZOS)).astype(float)
    x0, y0 = int(CXT * N) - tw // 2, int(BASE * N) - th
    xs, xe = max(x0, 0), min(x0 + tw, N)
    a = T[:, xs - x0:xe - x0, 3:4] / 255; L[y0:y0 + th, xs:xe] = L[y0:y0 + th, xs:xe] * (1 - a) + T[:, xs - x0:xe - x0, :3] * a
Image.fromarray(L.clip(0, 255).astype(np.uint8)).save(f'{OUT}/ECU_CC_Helmet_Left_col.png')
R0 = np.asarray(Image.open(f'{SRC}/ECU_CC_Helmet_Right_col.jpg').convert('RGB').resize((N, N), Image.LANCZOS)).astype(float)
# v4.2 (user: "the image blows up a lot more than you thought"): measured on the grid test, a side view only shows the middle
# of each image (x ~0.19-0.81, y ~0.22-0.90), magnified ~1.6x. So the whole Gemini painting is shrunk into that window
# (FIT, centered at x 0.5 / y 0.56) and the hidden margins (crown, back seam, under the facemask/bumper) are filled by
# extending its edges, blurred and darkened toward the crown.
FIT = 0.65; k = int(FIT * N); cx, cy = int(0.44 * N), int(0.43 * N)   # v4.5: cx 0.44 pushes the stadium toward the back (left edge) so the back reads tree | stripe | stadium   # v4.3: measured on the helmet, the side shows y ~0.20-0.83 (chin strap ~0.70-0.77): stadium raised into view
sm = np.asarray(Image.fromarray(R0.astype(np.uint8)).resize((k, k), Image.LANCZOS)).astype(float)
x0, y0 = cx - k // 2, cy - k // 2
yi = np.clip(np.arange(N) - y0, 0, k - 1); xi = np.clip(np.arange(N) - x0, 0, k - 1)
ext = sm[yi][:, xi]                                            # nearest-edge extension
ext = ndimage.gaussian_filter(ext, (40, 40, 0))
inside = np.zeros((N, N)); inside[y0:y0 + k, x0:x0 + k] = 1
inside = ndimage.gaussian_filter(ndimage.binary_erosion(inside, iterations=30).astype(float), 18)
R = ext * (1 - inside[..., None]) + np.pad(sm, ((y0, N - y0 - k), (x0, N - x0 - k), (0, 0)), mode='edge') * inside[..., None]
R = darken_top(R, 0.30)
lg = load('ECU_CC_Logo.jpg')
r, g, b = lg[..., 0], lg[..., 1], lg[..., 2]
green = g - np.maximum(r, b)                                   # ~186 on the background
alpha = np.clip((150 - green) / (150 - 60), 0, 1)
bg = alpha < 0.5
if not KEEP:                                                   # Gemini's white keyline: light, unsaturated pixels touching the background
    light = (np.minimum(np.minimum(r, g), b) > 150) & ((np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b)) < 70)
    lab, n = ndimage.label(light | bg)
    outside = np.isin(lab, np.unique(lab[bg]))
    ring = outside & ~bg
    alpha = np.where(ring, 0, alpha); alpha = ndimage.gaussian_filter(alpha, 1.0)
spill = g > np.maximum(r, b); lg[..., 1] = np.where(spill & (alpha < 0.98), np.maximum(r, b), g)   # despill edges
s = int(LS * N); logo = Image.fromarray(np.dstack([lg, alpha * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
bbox = logo.getbbox(); logo = logo.crop(bbox); w, h = logo.size; sc = s / max(w, h); logo = logo.resize((int(w * sc), int(h * sc)), Image.LANCZOS)
base = Image.fromarray(R.clip(0, 255).astype(np.uint8)).convert('RGBA')
# soft airbrushed shadow so it sits in the clouds
sh = logo.split()[3].point(lambda v: int(v * 0.45)); from PIL import ImageFilter; sh = sh.filter(ImageFilter.GaussianBlur(s * 0.02))
shadow = Image.new('RGBA', logo.size, (10, 4, 22, 0)); shadow.putalpha(sh)
x0, y0 = int(LX * N - logo.width / 2), int(LY * N - logo.height / 2)
base.alpha_composite(shadow, (x0 + 8, y0 + 12)); base.alpha_composite(logo, (x0, y0))
R = np.asarray(base.convert('RGB')).astype(float)
st = np.zeros((1024, 2048, 4), np.uint8)
def band(a0, a1): st[:, a0:a1, :3] = GOLD; st[:, a0:a1, 3] = 255
c = 1024; band(c - 254, c + 255)
for sg in (-1, 1): x = c + sg * (254 + 230); band(min(x, x + sg * 50), max(x, x + sg * 50))
Image.fromarray(st, 'RGBA').save(f'{OUT}/ECU_CC_Helmet_Back_col (stripe).png')
print('ok', 'logo', logo.size, 'at', (x0, y0))

# v6 (user: blend needs work): ONE shared background sky G(y), the same function on both halves, taken from the paintings'
# own skies (row median over the visible part of both sides, ground rows -> dark purple), smoothed. Every shared edge
# (crown, back centerline, front centerline) eases into G with a wide smoothstep, so the halves meet in identical colour
# and the transition is a soft gradient, not a dark band.
def sstep(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
Lv = L[:, int(0.33 * N):int(0.84 * N)]; Rv = R[:, int(0.16 * N):int(0.67 * N)]
G = np.median(np.concatenate([Lv, Rv], 1), axis=1)
y = np.arange(N) / N
DEEP = np.array([24, 12, 46], float); CROWN = np.array([12, 6, 26], float)
G = np.where((y > 0.52)[:, None], G * (1 - sstep((y - 0.52) / 0.12))[:, None] + DEEP * sstep((y - 0.52) / 0.12)[:, None], G)
G = ndimage.gaussian_filter1d(G, 70, axis=0)
G = G * (1 - sstep(1 - y / 0.22))[:, None] + CROWN * sstep(1 - y / 0.22)[:, None]
G = ndimage.gaussian_filter1d(G, 25, axis=0)
def blend(a, back_right, top=0.24, side=0.24):
    x = np.arange(N) / N
    xb = (1 - x) if back_right else x; xf = x if back_right else (1 - x)
    ws = np.maximum(sstep(1 - xb / side), sstep(1 - xf / side))
    wt = sstep(1 - y / top)
    w = np.maximum(ws[None, :], wt[:, None])[..., None]
    return a * (1 - w) + G[:, None, :] * w
L = blend(L, True); R = blend(R, False)
Image.fromarray(L.clip(0, 255).astype(np.uint8)).save(f'{OUT}/ECU_CC_Helmet_Left_col.png')
Image.fromarray(R.clip(0, 255).astype(np.uint8)).save(f'{OUT}/ECU_CC_Helmet_Right_col.png')
g = G[int(0.55 * N)]; lin = lambda c: ((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92
print('shared sky done; shell colour (linear, back at mid height):', [round(lin(c), 5) for c in g], 'sRGB', g.round())
