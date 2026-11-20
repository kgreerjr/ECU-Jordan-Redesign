# 6.0: Home helmet shell (and its stripe gaps, which share the same local ColorValue) = exactly ECU_Purple, the jersey's color.
# Was a custom purple (lin 0.0478 / 0.0137 / 0.1193 = sRGB 62,31,97) vs ECU_Purple (lin 0.0409152 / 0.0202886 / 0.1221388 = sRGB 57,39,98).
import os, re, xml.etree.ElementTree as ET
p = os.path.join(os.environ.get('ECU_PROJECT_DIR', '.'), 'FINAL/Helmets/ECU_HELMET_2025_PURPLE_yellowFacemask.xml'); t = open(p, encoding='utf-8-sig').read()
i = t.index('<field name="label">Helmet Shell</field>'); s = max(t.rfind('<complex type="LayerComp%s">' % k, 0, i) for k in ('OverlayInstance', 'MaterialInstance'))
g = re.search(r'name="colorR" ref="([0-9a-f-]{36})"', t[s:i]).group(1); a = t.index('<instance guid="%s"' % g); b = t.index('</instance>', a); seg = t[a:b]
for ax, v in zip('xyz', ('0.0409152', '0.0202886', '0.1221388')): seg, c = re.subn(r'(<field name="%s">)[^<]*' % ax, lambda m, v=v: m.group(1) + v, seg, 1); assert c == 1
t = t[:a] + seg + t[b:]; open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p)
print('Home shell + stripe gaps = ECU_Purple; color used by', len(re.findall(r'ref="%s"' % g, t)), 'layers')
