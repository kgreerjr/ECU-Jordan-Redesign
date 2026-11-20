# Away Alternate number font, after the reference jersey (tall condensed numerals, flag-top 1, rounded 8): Antonio (weight 550),
# widened 1.3x to the reference's proportions, plain outline (no drop shadow).
# Same layout as ECU_Jersey_2023_NUM_Array: 10 slices of 512x512, digit box y 34-477 (~444 px tall incl. outline),
# centred at x ~258; R = fill, G = outline, alpha = coverage. Written as a BC7_UNORM_SRGB (dxgi 99) texture array,
# 10 mips, arraySize 10 (Frosty imports an array from one DDS holding every slice).
# usage: make_aa_numbers.py <Antonio.ttf> <out.dds> <preview.png> [digit sheet image]   (v2 = the user's sheet)
import sys, struct, numpy as np, etcpak
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
FONT, OUT, PREV = sys.argv[1:4]
N, SS = 512, 4; TOP, BOT, CX = 34, 477, 258; OUTL = 12; WIDEN = 1.3; WEIGHT = 550   # 550 opens the counters to the reference's (700 filled them in)
font = ImageFont.truetype(FONT, 400 * SS); font.set_variation_by_axes([WEIGHT])
srgb = lambda c: np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
slices = []
SHEET = sys.argv[4] if len(sys.argv) > 4 else None
if SHEET:
    # v2 (user's digit sheet, number_sheet_user.jpg: purple digits with a gold outline on white, 0-4 over 5-9):
    # unmix every pixel into white / purple / gold weights, cut out each digit, one common scale for all ten
    # (tallest digit = the 444 px box), each row's top kept so the digits stay aligned, centred at x 258.
    img = ndimage.gaussian_filter(np.asarray(Image.open(SHEET).convert('RGB')).astype(float), (0.7, 0.7, 0))
    C = np.array([[248, 248, 248], [51, 24, 100], [249, 173, 13]], float).T          # white, purple, gold
    M = np.vstack([C, 400 * np.ones(3)]); rhs = np.concatenate([img.reshape(-1, 3).T, 400 * np.ones((1, img.shape[0] * img.shape[1]))])
    wts = np.linalg.lstsq(M, rhs, rcond=None)[0].T.clip(0, None); wts /= np.clip(wts.sum(1, keepdims=True), 1e-6, None)
    wts = wts.reshape(img.shape[0], img.shape[1], 3); P, Gd = wts[..., 1], wts[..., 2]
    cover = (P + Gd) > 0.5
    lab, n = ndimage.label(ndimage.binary_closing(cover, iterations=2)); objs = ndimage.find_objects(lab)
    sz = ndimage.sum(cover, lab, range(1, n + 1)); digs = [(i + 1, objs[i]) for i in range(n) if sz[i] > 5000]
    rows = sorted(set(sl[0].start // 600 for _, sl in digs))
    digs = sorted(digs, key=lambda t: (t[1][0].start // 600, t[1][1].start)); assert len(digs) == 10, len(digs)
    rowtop = {r: min(sl[0].start for _, sl in digs if sl[0].start // 600 == r) for r in rows}
    k = (BOT - TOP + 1) / max(sl[0].stop - sl[0].start for _, sl in digs)
    for i, sl in digs:
        own = ndimage.binary_dilation(lab[sl] == i, iterations=3)
        pp, gg = P[sl] * own, Gd[sl] * own
        size = (max(1, round(pp.shape[1] * k)), max(1, round(pp.shape[0] * k)))
        rs = lambda m: np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(size, Image.LANCZOS)).astype(float) / 255
        pr, gr = rs(pp), rs(gg)
        Fz, Gz = np.zeros((N, N)), np.zeros((N, N))
        y0 = TOP + round((sl[0].start - rowtop[sl[0].start // 600]) * k); x0 = CX - pr.shape[1] // 2
        Fz[y0:y0 + pr.shape[0], x0:x0 + pr.shape[1]] = pr; Gz[y0:y0 + gr.shape[0], x0:x0 + gr.shape[1]] = gr
        A = np.clip(Fz + Gz, 0, 1); A = np.clip((A - 0.5) * 1.3 + 0.5, 0, 1) * (A > 0.02)   # crisp edge
        s_ = np.clip(Fz + Gz, 1e-6, None)
        px = np.dstack([srgb(Fz / s_) * (A > 0), srgb(Gz / s_) * (A > 0), np.zeros_like(A), A])
        slices.append((px * 255 + 0.5).clip(0, 255).astype(np.uint8))
for dgt in ('' if SHEET else '0123456789'):
    W = N * SS * 2; im = Image.new('L', (W, W), 0); d = ImageDraw.Draw(im); d.text((W // 4, W // 4), dgt, font=font, fill=255)
    g = np.asarray(im) > 127; ys, xs = np.where(g); g = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hgt = (BOT - TOP + 1 - 2 * OUTL) * SS                        # glyph height so glyph + outline fills the box
    k = hgt / g.shape[0]
    z = np.asarray(Image.fromarray(g.astype(np.uint8) * 255).resize((max(1, round(g.shape[1] * k * WIDEN)), hgt), Image.LANCZOS)) > 127
    canvas = np.zeros((N * SS, N * SS), bool)
    y0 = (TOP + OUTL) * SS; x0 = CX * SS - z.shape[1] // 2
    canvas[y0:y0 + z.shape[0], x0:x0 + z.shape[1]] = z
    out = ndimage.distance_transform_edt(~canvas) <= OUTL * SS
    F = canvas.reshape(N, SS, N, SS).mean((1, 3)); A = out.reshape(N, SS, N, SS).mean((1, 3)); G = np.clip(A - F, 0, 1)
    s = np.clip(F + G, 1e-6, None)
    px = np.dstack([srgb(F / s) * (A > 0), srgb(G / s) * (A > 0), np.zeros_like(A), A])
    slices.append((px * 255 + 0.5).clip(0, 255).astype(np.uint8))
# preview: purple fill / gold outline on white, plus "18"
PU, GO = np.array([89, 42, 138]), np.array([253, 200, 47])
def show(p):
    a = p.astype(float) / 255; lin = lambda c: np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    f, g, al = lin(a[..., 0:1]), lin(a[..., 1:2]), a[..., 3:4]
    return (f * PU + g * GO) * al + 240 * (1 - al)
row = np.hstack([show(p) for p in slices]); eighteen = np.hstack([show(slices[1])[:, 120:400], show(slices[8])[:, 110:410]])
pv = np.zeros((N + N, max(row.shape[1], eighteen.shape[1]), 3)) + 240; pv[:N, :row.shape[1]] = row; pv[N:, :eighteen.shape[1]] = eighteen
Image.fromarray(pv.astype(np.uint8)).resize((pv.shape[1] // 2, pv.shape[0] // 2)).save(PREV)
# DDS: DX10 header, BC7_UNORM_SRGB, array of 10, full mip chain per slice
mips = 10; data = b''
for p in slices:
    cur = p.astype(np.float64)
    for m in range(mips):
        w = N >> m; arr = np.ascontiguousarray(cur.clip(0, 255).astype(np.uint8))
        if w < 4:                                                   # BC blocks are 4x4: pad tiny mips
            pad = np.zeros((4, 4, 4), np.uint8); pad[:w, :w] = arr; arr = pad
        data += etcpak.compress_bc7(arr.tobytes(), arr.shape[1], arr.shape[0])
        if m < mips - 1:
            cur = (cur[0::2, 0::2] + cur[1::2, 0::2] + cur[0::2, 1::2] + cur[1::2, 1::2]) / 4
flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000            # same flags as the proven Frosty export
pf = struct.pack('<II4sIIIII', 32, 0x4, b'DX10', 0, 0, 0, 0, 0)
hdr = struct.pack('<4sIIIIIII', b'DDS ', 124, flags, N, N, N * N, 0, mips) + b'\0' * 44 + pf + struct.pack('<IIIII', 0x1000 | 0x400000 | 0x8, 0, 0, 0, 0)
dx10 = struct.pack('<IIIII', 99, 3, 0, 10, 0)
open(OUT, 'wb').write(hdr + dx10 + data); print(OUT, len(hdr + dx10 + data), 'bytes')
