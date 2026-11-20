"""City Connect (Greenville Nights): tileable star-speckle fabric masks (same channel setup as Ghost Ship's fog):
R = base (tinted midnight purple), G = stars (tinted star white), B = soft haze (tinted violet); R+G+B = 1.
Output PNG + DDS (R8G8B8A8_UNORM, full mips; default_mask dups need DDS or Frosty keeps them 16x16)."""
import sys, struct, numpy as np
from PIL import Image
from scipy import ndimage
def make(out, seed, n_small=90, n_big=14, N=1024, haze=True):
    rng = np.random.default_rng(seed)
    st = np.zeros((N, N))
    for n, r0, r1, b0, b1 in ((n_small, 2.0, 3.2, 0.45, 0.85), (n_big, 4.0, 5.5, 0.85, 1.0)):
        ys, xs = rng.integers(0, N, n), rng.integers(0, N, n)
        for y, x in zip(ys, xs):
            r = rng.uniform(r0, r1); b = rng.uniform(b0, b1); R = int(np.ceil(r * 3))
            yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
            g = b * np.exp(-(yy ** 2 + xx ** 2) / (2 * (r / 1.6) ** 2))
            st[(y + yy) % N, (x + xx) % N] = np.maximum(st[(y + yy) % N, (x + xx) % N], g)
    hz = ndimage.gaussian_filter(rng.normal(0, 1, (N, N)), 60, mode='wrap')
    hz = np.clip((hz - hz.mean()) / (hz.std() * 2.5) + 0.15, 0, 1) ** 1.3 * 0.40
    G = np.clip(st, 0, 1); B = hz * (1 - G) * (1 if haze else 0); R = 1 - G - B
    a = np.dstack([R, G, B, np.ones_like(R)]) * 255
    Image.fromarray(a.round().astype(np.uint8), 'RGBA').save(out + '.png')
    mips = [a]
    while min(mips[-1].shape[:2]) > 1:
        m = mips[-1]; mips.append((m[0::2, 0::2] + m[1::2, 0::2] + m[0::2, 1::2] + m[1::2, 1::2]) / 4)
    data = b''.join((np.clip(m, 0, 255) + 0.5).astype(np.uint8).tobytes() for m in mips)
    flags = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000 | 0x20000
    pf = struct.pack('<II4sIIIII', 32, 0x4, b'DX10', 0, 0, 0, 0, 0)
    hdr = struct.pack('<4sIIIIIII', b'DDS ', 124, flags, N, N, N * 4, 0, len(mips)) + b'\0' * 44 + pf + struct.pack('<IIIII', 0x1000 | 0x400000 | 0x8, 0, 0, 0, 0)
    open(out + '.dds', 'wb').write(hdr + struct.pack('<IIIII', 28, 3, 0, 1, 0) + data)
    print(out, 'stars', (G > 0.3).sum(), 'px')
make('ECU_CC_Stars_Jersey_col', 11, haze=False)   # v2 (mod author): stars only, matches the pants
make('ECU_CC_Stars_Pants_col', 23, haze=False)   # v2: the game reads this mask as sRGB, so haze areas rendered as dark blotches on the pants -> stars only
