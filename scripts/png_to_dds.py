# PNG -> DDS (DX10 header, R8G8B8A8_UNORM, full mip chain). For duplicates that Frosty shrinks to the source
# texture's size on PNG import (e.g. default_mask dups stayed 16x16). Mips are 2x2 box averages, so tileable art stays seamless.
# usage: python3 png_to_dds.py IN.png [IN2.png ...]   -> writes IN.dds next to each
import sys, struct, numpy as np
from PIL import Image
def dds(png):
    a = np.asarray(Image.open(png).convert('RGBA')).astype(np.float64); h, w = a.shape[:2]; mips = [a]
    while min(mips[-1].shape[:2]) > 1:
        m = mips[-1]; m = (m[0::2, 0::2] + m[1::2, 0::2] + m[0::2, 1::2] + m[1::2, 1::2]) / 4; mips.append(m)
    data = b''.join((np.clip(m, 0, 255) + 0.5).astype(np.uint8).tobytes() for m in mips)
    flags = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000 | 0x20000            # caps|height|width|pitch|pixelformat|mipmapcount
    pf = struct.pack('<II4sIIIII', 32, 0x4, b'DX10', 0, 0, 0, 0, 0)  # FOURCC DX10
    hdr = struct.pack('<4sIIIIIII', b'DDS ', 124, flags, h, w, w * 4, 0, len(mips)) + b'\0' * 44 + pf + struct.pack('<IIIII', 0x1000 | 0x400000 | 0x8, 0, 0, 0, 0)
    dx10 = struct.pack('<IIIII', 28, 3, 0, 1, 0)                   # R8G8B8A8_UNORM, TEXTURE2D, array 1
    out = png[:-4] + '.dds'; open(out, 'wb').write(hdr + dx10 + data); print(out, w, 'x', h, len(mips), 'mips', len(data) // 1024, 'KB')
for p in sys.argv[1:]: dds(p)
