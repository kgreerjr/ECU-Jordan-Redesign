# PNG -> DDS, R8G8B8A8_UNORM (dxgi 28, linear: for normal and rsm maps), DX10 header, full mip chain.
# Normal mips are renormalised. usage: python3 png_to_dds_rgba8.py IN.png OUT.dds [normal]
import sys, struct, numpy as np
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; is_normal = len(sys.argv) > 3 and sys.argv[3] == 'normal'
a = np.asarray(Image.open(src).convert('RGBA')).astype(np.float64) / 255; h, w = a.shape[:2]
mips = [a]
while min(mips[-1].shape[:2]) > 1:
    m = mips[-1]; m = (m[0::2, 0::2] + m[1::2, 0::2] + m[0::2, 1::2] + m[1::2, 1::2]) / 4
    if is_normal:
        v = m[..., :3] * 2 - 1; v /= np.clip(np.linalg.norm(v, axis=2, keepdims=True), 1e-6, None); m[..., :3] = v * 0.5 + 0.5
    mips.append(m)
data = b''.join((np.clip(m, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes() for m in mips)
flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x8                   # caps|height|width|pixelformat|mipmapcount|pitch
pf = struct.pack('<II4sIIIII', 32, 0x4, b'DX10', 0, 0, 0, 0, 0)
hdr = struct.pack('<4sIIIIIII', b'DDS ', 124, flags, h, w, w * 4, 0, len(mips)) + b'\0' * 44 + pf + struct.pack('<IIIII', 0x1000 | 0x400000 | 0x8, 0, 0, 0, 0)
dx10 = struct.pack('<IIIII', 28, 3, 0, 1, 0)                        # R8G8B8A8_UNORM, TEXTURE2D, array 1
open(out, 'wb').write(hdr + dx10 + data); print(out, w, 'x', h, len(mips), 'mips', len(data) // 1024, 'KB')
