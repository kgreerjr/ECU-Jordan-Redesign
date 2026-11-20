# 5.1 Jumpman cleanup (all ECU jerseys, pants, socks). Michigan reference: crisp figure, no visible patch, true team color.
# 1) Tints: the pre-colored (UseDefaults) Jumpman layers were still multiplied by their tints (R*ECU_Purple + G*ECU_Gold ...),
#    which turned gold into copper. Identity tints (R=red, G=green, B=blue) return the image's own colors. Championship-proof rule kept.
# 2) Images: each colored Jumpman had an opaque patch (meant to blend with the fabric) that showed as a ring on textured fabric.
#    Rebuilt figure-only: alpha = original alpha x figure weight, RGB = logo color. Ghost Ship's lavender outline patch is a design choice: kept.
# Originals: Backups/Before 5.1 Jumpman cleanup/
import os, re, glob, uuid, shutil, numpy as np, xml.etree.ElementTree as ET
from PIL import Image
from collections import Counter
R = os.environ.get('ECU_PROJECT_DIR', '.'); F = R + '/FINAL/'; BK = R + '/Backups/Before 5.1 Jumpman cleanup/'
os.makedirs(BK, exist_ok=True)
PNGS = sorted(glob.glob(F + 'Jumpman textures/*.png')) + [F + 'Alt textures/Jolly Roger/' + n for n in ('ECU_JM_GoldOnCharcoal_col.png', 'ECU_JM_WT_GoldOnCharcoal_col.png')] + [F + 'Alt textures/Treasure Island/ECU_TI_JM_Pants_col.png']
for p in PNGS:
    if not os.path.exists(BK + os.path.basename(p)): shutil.copy(p, BK)
    a = np.array(Image.open(BK + os.path.basename(p)).convert('RGBA')).astype(float)
    op = a[:, :, 3] > 200; cols = Counter(map(tuple, a[op][:, :3].astype(int)))
    pad = np.pad(op, 1); edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])   # outer rim of the opaque area = patch
    base = np.array(Counter(map(tuple, a[edge][:, :3].astype(int))).most_common(1)[0][0], float)
    logo = np.array([c for c, _ in cols.most_common(6) if np.abs(np.array(c) - base).sum() > 60][0], float)
    d = logo - base; g = np.clip(((a[:, :, :3] - base) @ d) / (d @ d), 0, 1)
    out = np.zeros_like(a); out[:, :, :3] = logo; out[:, :, 3] = a[:, :, 3] * g
    Image.fromarray(out.round().astype(np.uint8), 'RGBA').save(p)
    print('%-34s patch %s -> transparent, figure %s' % (os.path.basename(p), tuple(base.astype(int)), tuple(logo.astype(int))))
def cv(new, xyz):
    g = str(uuid.uuid4()); new.append('\t<instance guid="%s" type="ColorValue" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="Color">\n\t\t\t<complex type="Vec3">\n\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t</complex>\n\t\t</field>\n\t</instance>\n' % (g, *xyz)); return 'ref="%s"' % g
for f in sorted(glob.glob(F + 'Jerseys/*.xml') + glob.glob(F + 'Pants/*.xml') + glob.glob(F + 'Socks/*.xml')):
    if not os.path.exists(BK + os.path.basename(f)): shutil.copy(f, BK)
    t = open(f, encoding='utf-8-sig').read(); new = []
    i = t.index('<field name="label">Jumpman Logo</field>'); s = t.rfind('<complex type="LayerCompOverlayInstance">', 0, i); seg = t[s:i]
    assert 'AssetResolveRule_UseDefaults' in t[s:i + 1500], f
    for ch, xyz in (('R', (1, 0, 0)), ('G', (0, 1, 0)), ('B', (0, 0, 1))):
        seg, c = re.subn(r'<field name="color%s" ref="[^"]*"( partitionGuid="[^"]*")? />' % ch, lambda m, ch=ch, xyz=xyz: '<field name="color%s" %s />' % (ch, cv(new, xyz)), seg, 1); assert c == 1, (f, ch)
    t = t[:s] + seg + t[i:]; t = t.replace('</partition>', ''.join(new) + '</partition>')
    open(f, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(f); print('identity tints:', os.path.basename(f))
