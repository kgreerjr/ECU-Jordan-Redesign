# Away Alternate narrow stripe for the helmet, in the FiveStripe encoding the 6.0 helmets use
# (2048x1024 canvas, band centred at x=1024; R = centre band, G = outer bands, B = gaps -> none here).
# Thin purple | white | thin purple, touching (no gaps): G 50 | R 240 | G 50 = 340 px (the triple stripes are 1024 px).
import sys, numpy as np
from PIL import Image
out = sys.argv[1]
a = np.zeros((1024, 2048, 4), np.uint8); a[..., 1] = 255          # background like the stock art: G, alpha 0
bands = [(50, (0, 255, 0)), (240, (255, 0, 0)), (50, (0, 255, 0))]
x = 1024 - sum(w for w, _ in bands) // 2
for w, c in bands: a[:, x:x + w, :3] = c; a[:, x:x + w, 3] = 255; x += w
Image.fromarray(a, 'RGBA').save(out); print(out, 'total', sum(w for w, _ in bands), 'px')

# Pants: the ECU pants stripe texture is 256 x 2048, opaque, band across x (G 63-85 | R 85-175 | G 175-197 = purple |
# white | purple on Home). Narrow version, same centre (x 130): G 9 | R 40 | G 9 = 58 px (stock 134).
if len(sys.argv) > 2:
    p = np.zeros((2048, 256, 4), np.uint8); p[..., 3] = 255
    x = 130 - 29
    for w, c in ((9, (0, 255, 0)), (40, (255, 0, 0)), (9, (0, 255, 0))): p[:, x:x + w, :3] = c; x += w
    Image.fromarray(p, 'RGBA').save(sys.argv[2]); print(sys.argv[2], 'pants stripe 58 px (stock 134)')
