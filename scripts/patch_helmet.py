# Swap the white adidas mark on ECU's menu helmet bumper for Michigan's Jumpman shape (same render, same pixels), drawn in white.
import sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage
U = sys.argv[1]; OUT = sys.argv[2]
cfg = {'lt': dict(roi=(620,735,405,480), logo=(655,703,428,463), jm=(650,705,430,470)),
       'rt': dict(roi=(290,400,405,480), logo=(320,368,425,463), jm=(315,370,425,470))}
for s, c in cfg.items():
    E = np.asarray(Image.open(U+'thel_%shelmets_ECU.png' % s).convert('RGBA')); M = np.asarray(Image.open(U+'thel_%shelmets_Michigan.png' % s).convert('RGBA'))
    Ef = E.astype(np.float32); Mf = M.astype(np.float32); lum = Ef[..., :3].mean(2); mlum = Mf[..., :3].mean(2)
    lx0, lx1, ly0, ly1 = c['logo']; box = np.zeros(lum.shape, bool); box[ly0:ly1, lx0:lx1] = True
    r, g, b = Ef[..., 0], Ef[..., 1], Ef[..., 2]; gold = (r > 150) & (g > 110) & (b < 110)
    bg = np.median(lum[box & (lum < 60)]); logo = box & (lum > bg+25) & ~gold
    mask = (ndimage.binary_dilation(logo, iterations=2) & box & ~gold).astype(np.uint8)*255
    out = cv2.cvtColor(cv2.inpaint(cv2.cvtColor(E[..., :3], cv2.COLOR_RGB2BGR), mask, 7, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB).astype(np.float32)
    blur = cv2.GaussianBlur(out, (0, 0), 2.0); mk = cv2.GaussianBlur(mask.astype(np.float32)/255, (0, 0), 1.0)[..., None]; out = out*(1-mk) + blur*mk
    jx0, jx1, jy0, jy1 = c['jm']; jb = np.zeros(lum.shape, bool); jb[jy0:jy1, jx0:jx1] = True
    maize = (Mf[..., 0] > 150) & (Mf[..., 1] > 120) & (Mf[..., 2] < 110)
    maize_l = np.median(mlum[jb & maize]); navy_l = np.percentile(mlum[jb & ~maize], 10)
    a = np.clip((maize_l-mlum)/(maize_l-navy_l), 0, 1)*jb*(~gold)
    core = a > 0.5; lab, n = ndimage.label(core); sz = ndimage.sum(core, lab, range(1, n+1)); keep = lab == (1+int(np.argmax(sz)))
    a = a*ndimage.binary_dilation(keep, iterations=2)
    # remove the bumper/facemask seam: bottom rows of the mask with no figure in the 4 rows above
    ys, xs = np.nonzero(a > 0.05); yb = ys.max(); fig = a > 0.5
    for y in range(yb-3, yb+1):
        for x in np.nonzero(a[y] > 0.05)[0]:
            if not fig[max(y-6, 0):y-2, x].any(): a[y, x] = 0
    def ext(y):
        xs = np.nonzero(a[y] > 0.05)[0]; return (xs.min(), xs.max()) if len(xs) else None
    for _ in range(3):                                   # peel bottom rows that stick out past the feet
        ys = np.nonzero((a > 0.05).any(1))[0]; yb = ys.max(); e0, e2 = ext(yb), ext(yb-2)
        if e2 and (e0[0] < e2[0]-1 or e0[1] > e2[1]+1): a[yb] = 0
        else: break
    white = np.median(Ef[logo][:, :3], axis=0)
    out = out*(1-a[..., None]) + white*a[..., None]
    res = np.dstack([np.clip(out, 0, 255).astype(np.uint8), E[..., 3]]); Image.fromarray(res, 'RGBA').save(OUT+'/thel_%shelmets_ECU.png' % s)
    x0, x1, y0, y1 = c['roi']; pad = np.zeros((y1-y0, 6, 4), np.uint8)+255
    both = np.concatenate([E[y0:y1, x0:x1], pad, res[y0:y1, x0:x1], pad, M[y0:y1, x0:x1]], axis=1)
    Image.fromarray(both).resize((both.shape[1]*4, both.shape[0]*4), Image.NEAREST).save(OUT+'/after_%s.png' % s)
    print(s, 'jumpman px', int((a > 0.05).sum()), 'changed', int((res[..., :3] != E[..., :3]).any(2).sum()), 'alpha same', bool((res[..., 3] == E[..., 3]).all()))
