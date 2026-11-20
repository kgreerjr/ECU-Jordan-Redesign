# Roster headshot jersey (as run for ECU, with OpenCV):
# paint the old logo out of tjer_teamjerseys_<TEAM> and draw the new one in its place.
# Usage: python3 patch_headshot_overlay.py <overlay.png decoded from the DDS> <Jumpman_col.dds> <out.png>
import sys, io, numpy as np, cv2
from PIL import Image
src = np.asarray(Image.open(sys.argv[1]).convert('RGBA')); im = src.astype(np.int32); r, g, b, a = [im[..., i] for i in range(4)]
gold = (r > 140) & (g > 100) & (b < 120) & (a > 200)          # ECU's logo was gold; change the color test for other teams
roi = np.zeros_like(gold); roi[455:505, 335:410] = True          # logo area on the chest, away from the V collar
m = (gold & roi).astype(np.uint8); ys, xs = np.nonzero(m); bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
med = np.median(im[m.astype(bool)][:, :3], axis=0)
mask = cv2.dilate(m*255, np.ones((5, 5), np.uint8), iterations=1); bgr = cv2.cvtColor(src[..., :3], cv2.COLOR_RGB2BGR)
inp = cv2.inpaint(bgr, mask, 6, cv2.INPAINT_TELEA).astype(np.float32)
h, w = by1-by0+12, bx1-bx0+12; oy, ox = by0-6, bx0-6
donor = bgr[oy-h-8:oy-8, ox:ox+w].astype(np.float32); grain = donor - cv2.GaussianBlur(donor, (0, 0), 3)
mk = (cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 1.2)/255.0)[oy:oy+h, ox:ox+w, None]; inp[oy:oy+h, ox:ox+w] += grain*mk
out = np.clip(inp, 0, 255).astype(np.uint8)
d = open(sys.argv[2], 'rb').read(); hd = bytearray(d[:128]); hd[84:88] = b'DXT5'
jm = np.asarray(Image.open(io.BytesIO(bytes(hd)+d[148:])).convert('RGBA'))[..., 1]; yy, xx = np.nonzero(jm > 8); jm = jm[yy.min():yy.max()+1, xx.min():xx.max()+1]
H = int(round((by1-by0+1)*1.25)); W = int(round(jm.shape[1]*H/jm.shape[0])); jmask = np.asarray(Image.fromarray(jm).resize((W, H), Image.LANCZOS)).astype(np.float32)/255
px, py = int(round((bx0+bx1)/2 - W/2)), int(round((by0+by1)/2 - H/2))
base = out[py:py+H, px:px+W].astype(np.float32); lum = base.mean(axis=2, keepdims=True); shade = np.clip(lum/max(lum.mean(), 1), 0.85, 1.15)
out[py:py+H, px:px+W] = np.clip(base*(1-jmask[..., None]) + (np.array([med[2], med[1], med[0]], np.float32)*shade)*jmask[..., None], 0, 255).astype(np.uint8)
Image.fromarray(np.dstack([cv2.cvtColor(out, cv2.COLOR_BGR2RGB), src[..., 3]]), 'RGBA').save(sys.argv[3])
