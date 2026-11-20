# Treasure Island alt-logo textures from the mod author's art (ECU_TI_alt_logo_source.png).
# usage: python3 make_ti_logos.py SRC.png OUTDIR [HELMET_SCALE] [PREFIX]   (PREFIX ECU_TI -> ECU_TI_Helmet_Logo_col / ECU_TI_Logo_col; ECU_JR -> Jolly Roger)
# Cleans the halo (keep largest opaque blob), crops, fits into the footprint of the decal it replaces, bleeds edge color into transparent pixels.
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
src, out = sys.argv[1], sys.argv[2]; HELMET_SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.7   # v1 = 1.0 (too big on the helmet)
PREFIX = sys.argv[4] if len(sys.argv) > 4 else 'ECU_TI'
a = np.array(Image.open(src).convert('RGBA'))
core = ndimage.binary_opening(a[..., 3] > 200, iterations=6); lab, n = ndimage.label(core); keep = lab == (np.argmax(ndimage.sum(core, lab, range(1, n + 1))) + 1)
keep = ndimage.binary_dilation(ndimage.binary_fill_holes(keep), iterations=4); a[~keep] = 0
y, x = np.where(a[..., 3] > 40); crop = Image.fromarray(a).crop((x.min(), y.min(), x.max() + 1, y.max() + 1))
def fit(bw, bh, N, name):
    s = min(bw / crop.width, bh / crop.height); w, h = int(crop.width * s), int(crop.height * s)
    o = Image.new('RGBA', (N, N), (0, 0, 0, 0)); o.paste(crop.resize((w, h), Image.LANCZOS), ((N - w) // 2, (N - h) // 2))
    arr = np.array(o); al = arr[..., 3].copy(); rgb = Image.fromarray(arr[..., :3])
    for _ in range(10):
        b2 = np.array(rgb.filter(ImageFilter.MaxFilter(3))); r2 = np.array(rgb); r2[al == 0] = b2[al == 0]; rgb = Image.fromarray(r2)
    Image.fromarray(np.dstack([np.array(rgb), al])).save(out + '/' + name); print(name, (w, h))
fit(868 * HELMET_SCALE, 920 * HELMET_SCALE, 1024, PREFIX + ('_Helmet_Skull_col.png' if PREFIX == 'ECU_JR' else '_Helmet_Logo_col.png'))   # helmet side (BLA decal footprint 868x920 of 1024) x scale
fit(940, 940, 1024, PREFIX + '_Logo_col.png')                                         # jersey sleeves + pants hip
