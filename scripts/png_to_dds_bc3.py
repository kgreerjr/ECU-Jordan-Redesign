# PNG -> DDS, BC3_UNORM_SRGB (dxgi 78, same format as the ECU helmet decal textures), DX10 header, full mip chain.
# For texture duplicates Frosty shrinks to the source size on PNG import (ECU_CC_Helmet_*_col dups were 512x512).
# usage: python3 png_to_dds_bc3.py IN.png OUT.dds
import sys, struct, numpy as np
from PIL import Image
from quicktex.s3tc.bc3 import BC3Encoder
from quicktex import RawTexture
def srgb2lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lin2srgb(c): return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
src, out = sys.argv[1], sys.argv[2]
img = Image.open(src).convert('RGBA'); w, h = img.size
a = np.asarray(img).astype(np.float64) / 255
lin = a.copy(); lin[..., :3] = srgb2lin(a[..., :3])               # average mips in linear light (correct for sRGB)
mips = [lin]
while min(mips[-1].shape[:2]) > 1:
    m = mips[-1]; mips.append((m[0::2, 0::2] + m[1::2, 0::2] + m[0::2, 1::2] + m[1::2, 1::2]) / 4)
enc = BC3Encoder(18); data = b''
for m in mips:
    s = m.copy(); s[..., :3] = lin2srgb(m[..., :3])
    px = (np.clip(s, 0, 1) * 255 + 0.5).astype(np.uint8); mh, mw = px.shape[:2]
    if mw < 4 or mh < 4:                                          # BC blocks are 4x4: pad tiny mips
        p = np.zeros((max(4, mh), max(4, mw), 4), np.uint8); p[:mh, :mw] = px; px = p
    data += bytes(enc.encode(RawTexture.frombytes(px.tobytes(), px.shape[1], px.shape[0])))
flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000              # caps|height|width|pixelformat|mipmapcount|linearsize
pf = struct.pack('<II4sIIIII', 32, 0x4, b'DX10', 0, 0, 0, 0, 0)
hdr = struct.pack('<4sIIIIIII', b'DDS ', 124, flags, h, w, (w // 4) * (h // 4) * 16, 0, len(mips)) + b'\0' * 44 + pf + struct.pack('<IIIII', 0x1000 | 0x400000 | 0x8, 0, 0, 0, 0)
dx10 = struct.pack('<IIIII', 78, 3, 0, 1, 0)                        # BC3_UNORM_SRGB, TEXTURE2D, array 1
open(out, 'wb').write(hdr + dx10 + data); print(out, w, 'x', h, len(mips), 'mips', len(data) // 1024, 'KB')
