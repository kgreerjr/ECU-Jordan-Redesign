# Step 2 of the logo work (as run for ECU): bake team colors into the reference logo so the
# logo layer can use AssetResolveRule_UseDefaults (immune to the championship override).
# Inputs: reference logo _col DDS (Jumpman: A = patch, R = background, G = figure),
#         team color ColorValue XMLs (linear floats). Output: one PNG per color pair.
import sys, io, re, os, numpy as np
from PIL import Image
ROOT = os.environ.get('ECU_PROJECT_DIR', '.')
COLS = os.path.join(ROOT, 'Dup IDs/Team colors')
LOGO = os.path.join(ROOT, 'Dup IDs/Jumpman_Decal_2022_Cotton_col.dds')
OUT  = os.path.join(ROOT, 'FINAL/Jumpman textures')
def col(f):
    t = open(f, encoding='utf-8-sig').read()
    return np.array([float(re.search(r'name="%s">([^<]+)' % k, t).group(1)) for k in 'xyz'])
C = {'Purple': col(COLS+'/ECU_Purple.xml'), 'Gold': col(COLS+'/ECU_Gold.xml'),
     'White': col(COLS+'/global_white.xml'), 'Black': col(COLS+'/global_black.xml')}
def to_srgb(l): l = np.clip(l, 0, 1); return np.where(l <= 0.0031308, 12.92*l, 1.055*np.power(l, 1/2.4) - 0.055)
d = open(LOGO, 'rb').read(); h = bytearray(d[:128]); h[84:88] = b'DXT5'          # BC3 (DXGI 78) -> legacy DXT5 header so Pillow reads it
a = np.asarray(Image.open(io.BytesIO(bytes(h) + d[148:])).convert('RGBA')).astype(float) / 255
R, G, A = a[..., 0:1], a[..., 1:2], a[..., 3]
# name: (uniform color, logo color). WT_ prefix = duplicate made from the WithText Adidas decal.
combos = {'PurpleOnWhite': ('White', 'Purple'), 'GoldOnPurple': ('Purple', 'Gold'), 'WhiteOnBlack': ('Black', 'White'),
          'PurpleOnGold': ('Gold', 'Purple'), 'BlackOnWhite': ('White', 'Black')}
os.makedirs(OUT, exist_ok=True)
for name, (base, logo) in combos.items():
    lin = R*C[base] + G*C[logo]                                   # what the game's tint does (linear)
    rgb = (to_srgb(lin)*255 + 0.5).astype(np.uint8)
    rgb[A == 0] = (to_srgb(C[base])*255 + 0.5).astype(np.uint8)  # no dark fringes
    img = Image.fromarray(np.dstack([rgb, (A*255 + 0.5).astype(np.uint8)]), 'RGBA')
    for pre in (['ECU_JM_WT_', 'ECU_JM_'] if name in ('PurpleOnWhite', 'GoldOnPurple') else ['ECU_JM_']):
        img.save('%s/%s%s_col.png' % (OUT, pre, name))
print('done')
