# Remove a baked-in "fake transparency" checkerboard (JPG) from logo art: flood-fill from the image border through
# near-neutral light pixels (the checker squares), keep everything else; soften the edge. usage: SRC OUT.png
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
a = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int)
mx, mn = a.max(2), a.min(2)
checker = (mn > 180) & ((mx - mn) < 14)                       # light, neutral (squares ~205 and ~253)
lab, n = ndimage.label(checker); border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
sizes0 = ndimage.sum(checker, lab, range(1, n + 1))
big = {i + 1 for i, v in enumerate(sizes0) if v > 1500}          # enclosed checker too (inside the sword hand-guards)
bg = np.isin(lab, list(border | big))
bg = ndimage.binary_closing(bg, iterations=2)                  # swallow JPEG specks between squares
fg = ~bg; fg = ndimage.binary_opening(fg, iterations=2)
lab2, n2 = ndimage.label(fg); sizes = ndimage.sum(fg, lab2, range(1, n2 + 1)); fg = lab2 == (np.argmax(sizes) + 1)   # the logo only
alpha = np.array(Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)))
alpha = np.clip((alpha.astype(int) - 40) * 255 // 175, 0, 255).astype(np.uint8)
Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), 'RGBA').save(sys.argv[2]); print('components', n2, 'logo px', fg.sum())
