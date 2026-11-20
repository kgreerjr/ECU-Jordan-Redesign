# Ghost Ship art: tileable lavender fog (material colorTexture, multiplied by the white body tint),
# lavender-on-white Jumpmans, and the helmet-side skull (GS_logo_black, already in the BLA decal's exact layout).
# usage: python3 make_ghost_ship_art.py     (writes into Builds/Ghost Ship/ and FINAL Alternate uniform textures/Ghost Ship/)
import os, io, shutil, numpy as np
from PIL import Image
from scipy import ndimage
R = os.environ.get('ECU_PROJECT_DIR', '.'); OUT = R + '/Builds/Ghost Ship'; FIN = R + '/FINAL/Alt textures/Ghost Ship'
for d in (OUT + '/Pattern', OUT + '/Jumpman images', OUT + '/Logo', FIN): os.makedirs(d, exist_ok=True)
lin = lambda c: ((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92
srgb = lambda l: np.where(np.clip(l, 0, 1) <= 0.0031308, 12.92 * np.clip(l, 0, 1), 1.055 * np.power(np.clip(l, 0, 1), 1 / 2.4) - 0.055)
hexlin = lambda h: np.array([lin(int(h[i:i + 2], 16)) for i in (1, 3, 5)])
WHITE = np.array([0.6375968, 0.6375968, 0.7454042])   # global_white (the game's uniform white, linear)
LAV = hexlin('#B9A2DC')                                 # Ghost Ship lavender (numbers, trim, Jumpman)
WISP = hexlin('#B5B4BD')                                # fog wisps: deeper lavender (v1 used LAV at 0.55/0.8 strength - invisible in game)
# ---- fog: periodic fractal noise (FFT, integer frequencies -> seamless tile), domain-warped into wisps ----
N = 1024; rng = np.random.default_rng(2026)
def noise(beta, seed):
    r = np.random.default_rng(seed); f = np.fft.fftfreq(N) * N; fx, fy = np.meshgrid(f, f); k = np.hypot(fx, fy); k[0, 0] = 1
    spec = (r.normal(size=(N, N)) + 1j * r.normal(size=(N, N))) / k ** beta; spec[k < 0.5] = 0; spec[k > 9] = 0   # v3: tile is ~1/4 of the chest at scale 0.12 -> a few big billows per tile   # no 1-2 cycle waves (they read as bands), no fine marble streaks
    n = np.real(np.fft.ifft2(spec)); return (n - n.mean()) / n.std()
base, wx, wy = noise(1.25, 1), noise(1.8, 2), noise(1.8, 3)
yy, xx = np.mgrid[0:N, 0:N].astype(float); W = 70.0                       # warp distance in px: swirly, streaky mist
fog = ndimage.map_coordinates(base, [yy + W * wy, xx + W * wx], order=1, mode='grid-wrap')
fog = (fog - fog.min()) / (fog.max() - fog.min())
LAVMIX = 0.5   # v5: up to this share of the mist drifts lavender (B channel, colorB = LAV in the build); 0 = all gray
lav_region = noise(1.2, 7); lav_region = (lav_region - lav_region.min()) / (lav_region.max() - lav_region.min())
lav_region = np.clip((lav_region - 0.45) / 0.35, 0, 1); lav_region = lav_region * lav_region * (3 - 2 * lav_region)
def fogtex(name, strength, lo=0.30, hi=0.85):
    # material layers read channels as MASKS: out = R*colorR + G*colorG + B*colorB.  R = white body, G = gray mist (WISP), B = lavender mist (LAV)
    m = np.clip((fog - lo) / (hi - lo), 0, 1); m = strength * m * m * (3 - 2 * m); l = LAVMIX * lav_region
    img = np.dstack([(1 - m) * 255 + 0.5, m * (1 - l) * 255 + 0.5, m * l * 255 + 0.5, np.full_like(m, 255)]).astype(np.uint8)
    Image.fromarray(img, 'RGBA').save(OUT + '/Pattern/%s.png' % name)
    mm, ll = np.tile(m, (2, 2))[..., None], np.tile(l, (2, 2))[..., None]
    prev = srgb(((1 - mm) * WHITE + mm * (1 - ll) * WISP + mm * ll * LAV) * 1.35)
    Image.fromarray((prev * 255 + 0.5).astype(np.uint8)).resize((1024, 1024)).save(OUT + '/Pattern/preview_%s.png' % name)
    shutil.copy(OUT + '/Pattern/%s.png' % name, FIN); print(name, 'strength', strength, 'lavender mix', LAVMIX)
fogtex('ECU_GS_Fog_col', 0.65)            # pants
fogtex('ECU_GS_Fog_Jersey_col', 0.9)      # jersey: stronger (mesh/wrinkles drown pants-strength patterns - Jolly Roger lesson)
# ---- Jumpman: lavender figure on the white body (same channel mix as the TI/JR Jumpmans) ----
d = open(R + '/Dup IDs/Jumpman_Decal_2022_Cotton_col.dds', 'rb').read(); h = bytearray(d[:128]); h[84:88] = b'DXT5'
a = np.asarray(Image.open(io.BytesIO(bytes(h) + d[148:])).convert('RGBA')).astype(float) / 255
def jm(bg, fig, name):
    rgb = (srgb(a[..., 0:1] * bg + a[..., 1:2] * fig) * 255 + 0.5).astype(np.uint8); rgb[a[..., 3] == 0] = (srgb(bg) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(np.dstack([rgb, (a[..., 3] * 255 + 0.5).astype(np.uint8)]), 'RGBA').save(OUT + '/Jumpman images/%s.png' % name); shutil.copy(OUT + '/Jumpman images/%s.png' % name, FIN); print(name)
JMC = hexlin('#6E55A8')   # v2: deeper purple - LAV figure was hard to see on the white body
GFILL, LOUT = hexlin('#9A99A4'), hexlin('#9479D0')   # v3 (user): gray figure, lavender outline patch - matches numbers/wordmark
jm(LOUT, GFILL, 'ECU_GS_JM_Jersey_col'); jm(LOUT, GFILL, 'ECU_GS_JM_Pants_col')
# ---- helmet sides: GS_logo_black is the stock BLA decal recolored, so it already matches that decal's size/placement ----
# v2 helmet logo (deeper lavender #9479D0, hat #CDCED5, lines #2B2531) is made by recolor_skull_logo.py from the stock BLA decal -> FINAL/Ghost Ship/ECU_GS_Helmet_Logo_col.png
