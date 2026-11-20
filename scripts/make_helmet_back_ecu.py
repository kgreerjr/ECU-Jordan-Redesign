# Back-bumper "ECU" (serif, from the hat lettering) placed where "EAST CAROLINA" sits in WHI_BackLogo_col.  R = letters (tinted gold), A = mask.
import io, os, numpy as np
from PIL import Image
D = os.path.join(os.environ.get('ECU_PROJECT_DIR', '.'), 'Backups/ECU helmets/Decals/'); O = os.path.join(os.environ.get('ECU_PROJECT_DIR', '.'), 'Builds/Jolly Roger/Helmet/')
def dds(p):
    b = bytearray(open(p, 'rb').read()); h = b[:128]; h[84:88] = b'DXT5'; im = Image.open(io.BytesIO(bytes(h) + bytes(b[148:]))); im.load(); return np.array(im.convert('RGBA'))
skull = dds(D + 'ECU_Helmet_2021_WHI_Decal_01_col.dds'); back = dds(D + 'ECU_Helmet_2021_WHI_BackLogo_col.dds')
m = (skull[..., 1] > 128) & (skull[..., 3] > 128); ys, xs = np.where(m); L = skull[ys.min()-4:ys.max()+5, xs.min()-4:xs.max()+5, 1]
def tight(a): y, x = np.where(a > 128); return a[y.min():y.max()+1, x.min():x.max()+1]
best = min(np.arange(-15, 15.1, 0.5), key=lambda d: tight(np.array(Image.fromarray(L).rotate(d, Image.BICUBIC, expand=True))).shape[0])   # deskew: hat lettering is tilted
L = tight(np.array(Image.fromarray(L).rotate(best, Image.BICUBIC, expand=True))); print('deskew', best)
by, bx = np.where(back[..., 3] > 128); y0, y1, x0, x1 = by.min(), by.max(), bx.min(), bx.max(); print('EAST CAROLINA box', x0, x1, y0, y1, 'ECU src', L.shape)
H = int((y1 - y0 + 1) * 1.35); W = int(L.shape[1] * H / L.shape[0])
let = np.array(Image.fromarray(L).resize((W, H), Image.LANCZOS)); cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
out = np.zeros((512, 512, 4), np.uint8); ty, tx = cy - H // 2, cx - W // 2
out[ty:ty+H, tx:tx+W, 0] = let; out[ty:ty+H, tx:tx+W, 3] = let
Image.fromarray(out, 'RGBA').save(O + 'ECU_JR_Helmet_BackECU_col.png')
pv = np.zeros((512, 512, 3), np.uint8); pv[:] = (20, 20, 22); a = out[..., 3:4] / 255; pv = (pv * (1 - a) + np.array([253, 200, 47]) * a).astype(np.uint8)
Image.fromarray(pv).crop((0, cy - 60, 512, cy + 60)).save(O + 'decal previews/preview_back_ECU.png'); print('ok', W, H)
