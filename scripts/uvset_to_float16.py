# UVSet (layout) DDS: R16G16B16A16_UNORM (dxgi 11, Frosty won't import it) -> R16G16B16A16_FLOAT (dxgi 10, imports).
# Same header, every mip converted. usage: python3 uvset_to_float16.py IN.dds OUT.dds
import sys, struct, numpy as np
d = bytearray(open(sys.argv[1], 'rb').read())
assert d[84:88] == b'DX10', 'expected a DX10 header'
fmt = struct.unpack('<I', d[128:132])[0]
assert fmt == 11, 'expected dxgi 11 (R16G16B16A16_UNORM), got %d' % fmt
px = np.frombuffer(bytes(d[148:]), '<u2').astype(np.float32) / 65535.0
d[128:132] = struct.pack('<I', 10)
w = struct.unpack('<I', d[16:20])[0]
d[20:24] = struct.pack('<I', w * 8)                       # row pitch, as in the proven JR file
open(sys.argv[2], 'wb').write(bytes(d[:148]) + px.astype('<f2').tobytes())
print(sys.argv[2], 'written,', len(px) // 4, 'texels')
