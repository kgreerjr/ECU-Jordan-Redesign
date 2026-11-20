# 5.1: pants Jumpman resized to Michigan's on-screen size (measured in the Uniform Editor, same camera: MICH 91x109 px vs ECU 131x155 px = 0.70).
# ECU pants have no layout map, so Michigan's numbers (0.069 / 0.085 in Pants_UVSet_front space) can't be copied directly: scale ECU's own 0.05 x 0.1 by 0.70.
# One size AND position on every ECU pants piece (Michigan's), rotate kept (8). Post-processes FINAL/Pants in place; originals in Backups/Before pants resize/
import os, re, glob, xml.etree.ElementTree as ET
R = os.environ.get('ECU_PROJECT_DIR', '.'); P = R + '/FINAL/Pants/'
SU, SV = '0.030', '0.070'
U, V = '0.143', '0.262'   # Michigan's spot: front of the hip (was ECU's Adidas spot 0.16 / 0.245). Tuned in 3 Uniform Editor rounds on Jolly Roger vs MICH_PANTS (3000 px/unit)
for f in sorted(glob.glob(P + '*.xml')):
    t = open(f, encoding='utf-8-sig').read(); done = set()
    for lab in ('Jumpman Logo',):
        for m in re.finditer(r'<field name="label">%s</field>' % lab, t):
            s = t.rfind('<complex type="LayerCompOverlayInstance">', 0, m.start()); g = re.search(r'name="overlay_transform" ref="([0-9a-f-]{36})"', t[s:m.start() + 800]).group(1)
            if g in done: continue
            done.add(g); a = t.index('<instance guid="%s"' % g); b = t.index('</instance>', a); seg = t[a:b]
            seg, c1 = re.subn(r'(<field name="scaleU">)[^<]*', lambda x: x.group(1) + SU, seg, 1); seg, c2 = re.subn(r'(<field name="scaleV">)[^<]*', lambda x: x.group(1) + SV, seg, 1)
            seg, c4 = re.subn(r'(<field name="offsetU">)[^<]*', lambda x: x.group(1) + U, seg, 1); seg, c5 = re.subn(r'(<field name="offsetV">)[^<]*', lambda x: x.group(1) + V, seg, 1); assert c4 == c5 == 1
            seg, c3 = re.subn(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*(</field>\s*<field name="z">)[^<]*(</field>\s*<field name="w">)[^<]*', lambda x: x.group(1) + SU + x.group(2) + SV + x.group(3) + U + x.group(4) + V, seg, 1)
            assert c1 == c2 == c3 == 1, (f, g); t = t[:a] + seg + t[b:]
    # transforms shared with other layers?
    users = {g: len(re.findall(r'overlay_transform" ref="%s"' % g, t)) for g in done}
    open(f, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(f)
    print(os.path.basename(f), 'Jumpman ->', SU, SV, U, V, '| transform used by', users)
