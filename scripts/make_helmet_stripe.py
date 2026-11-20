# Thin gold/purple pinstripe set in the FiveStripe_02 encoding (2048x1024, band centered at x=1024):
# G = outer bands, B = next bands, R = center band (tinted gold / purple / gold in the helmet build).
import os, numpy as np
from PIL import Image
O = os.path.join(os.environ.get('ECU_PROJECT_DIR', '.'), 'Builds/Jolly Roger/Helmet/'); a = np.zeros((1024, 2048, 4), np.uint8)
WIDTH = 1.5   # v1 = 1.0 (320 px, 'clean but a bit thin'); v2 = 1.5 (480 px). Stock set = 1024 px.
bands = [(int(w * WIDTH), c) for w, c in [(60, (0, 255, 0)), (40, (0, 0, 255)), (120, (255, 0, 0)), (40, (0, 0, 255)), (60, (0, 255, 0))]]   # px; stock = 122/135/509/135/122
x = 1024 - sum(w for w, _ in bands) // 2
for w, c in bands: a[:, x:x+w, :3] = c; a[:, x:x+w, 3] = 255; x += w
Image.fromarray(a, 'RGBA').save(O + 'ECU_JR_Helmet_Stripe_thin_col.png'); print('ok, total width', sum(w for w, _ in bands), 'px (stock 1024)')
