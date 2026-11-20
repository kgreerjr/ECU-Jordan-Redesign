# Ghost Ship helmet logo v5: ECU's STOCK BLA skull mask (R = trim/ECU/bandana, G = skull+bones, B = hat; no channel = line),
# tinted in the helmet XML like the Jolly Roger helmet. Edit: line pixels get K of the hat channel, so lines render as a
# dimmed hat-gray (soft charcoal) instead of pure black. Mask stays in the stock encoding (sRGB-stored values).
import numpy as np, sys
from PIL import Image
K = float(sys.argv[1]) if len(sys.argv) > 1 else 0.3
lin = lambda c: np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
srgb = lambda l: np.where(l <= 0.0031308, l * 12.92, 1.055 * np.clip(l, 0, None) ** (1 / 2.4) - 0.055)
a = np.array(Image.open('bla.png').convert('RGBA')).astype(float) / 255
m = lin(a[..., :3]); resid = np.clip(1 - m.sum(-1), 0, 1); m[..., 2] += K * resid
out = np.dstack([srgb(np.clip(m, 0, 1)), a[..., 3]]); Image.fromarray((out * 255 + 0.5).astype(np.uint8), 'RGBA').save('ECU_GS_Helmet_Logo_col.png')
# preview with the planned tints on a cool-white shell
hx = lambda h: lin(np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255)
T, S, H = hx('#9479D0'), hx('#F2F2F5'), hx('#D3D2DE')
mm = lin(out[..., :3]); rgb = mm[..., 0:1] * T + mm[..., 1:2] * S + mm[..., 2:3] * H
shell = hx('#E9EAF0'); al = a[..., 3:4]; comp = rgb * al + shell * (1 - al)
Image.fromarray((srgb(comp) * 255 + 0.5).astype(np.uint8)).resize((320, 320)).save('logo_v5_prev.png'); print('ok K', K)
