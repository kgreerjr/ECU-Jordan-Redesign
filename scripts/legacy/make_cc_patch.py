"""City Connect sleeve patch: Gemini badge -> round cutout. The download had a dark landscape fading into the bottom of the
green screen, so the badge is cut with a circle fitted to its clean top half instead of by colour."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert('RGB')).astype(float); H, W = a.shape[:2]
g = a[..., 1] - np.maximum(a[..., 0], a[..., 2]); disc = g < 100
ys = np.arange(H // 2)
# top half: leftmost / rightmost non-green per row -> circle fit (least squares)
pts = []
for y in ys[::4]:
    xs = np.where(disc[y])[0]
    if len(xs) > 20: pts += [(xs[0], y), (xs[-1], y)]
pts = np.array(pts, float); x, y = pts[:, 0], pts[:, 1]
A = np.c_[2 * x, 2 * y, np.ones(len(x))]; cx, cy, c = np.linalg.lstsq(A, x ** 2 + y ** 2, rcond=None)[0]; r = np.sqrt(c + cx ** 2 + cy ** 2)
print('circle', round(cx), round(cy), round(r))
yy, xx = np.mgrid[0:H, 0:W]; d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
alpha = np.clip((r - 1.5 - d) / 2.5, 0, 1)                   # soft 2-3 px edge, just inside the outer purple ring
s = int(np.ceil(r * 1.04)); x0, y0 = int(cx) - s, int(cy) - s
pad = lambda arr: np.pad(arr, ((max(0, -y0), max(0, y0 + 2 * s - H)), (max(0, -x0), max(0, x0 + 2 * s - W))) + ((0, 0),) * (arr.ndim - 2), mode='edge')
rgba = np.dstack([a, alpha * 255])
X0, Y0 = max(x0, 0), max(y0, 0); crop = pad(rgba[Y0:y0 + 2 * s, X0:x0 + 2 * s])
im = Image.fromarray(crop.clip(0, 255).astype(np.uint8), 'RGBA').resize((1024, 1024), Image.LANCZOS)
A = np.asarray(im).astype(float); al = A[..., 3:4] / 255
blur = ndimage.gaussian_filter(A[..., :3] * al, (12, 12, 0)) / np.clip(ndimage.gaussian_filter(al, (12, 12, 0)), 1e-3, None)
A[..., :3] = np.where(al > 0.02, A[..., :3], blur)               # no dark/green halo in the mips
Image.fromarray(A.clip(0, 255).astype(np.uint8), 'RGBA').save(out)
