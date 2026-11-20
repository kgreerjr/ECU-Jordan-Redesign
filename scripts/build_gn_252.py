# Greenville Nights helmet (ECU_HELMET_2021_PURPLE_yellowFacemask): front bumper ECU -> "252" (Greenville's area code)
# in the same style (ECU_GN_Bumper_Front_252_col, dup of ECU_Helmet_2021_WHI_FrontLogo_col like the ECU front art;
# art from make_gn_bumper_252.py). Same channels as the ECU art, so the tints stay: gold fill, white ring, purple ring.
# usage: build_gn_252.py <helmet xml in/out> <ECU_GN_Bumper_Front_252_col.xml>
import re, sys, xml.etree.ElementTree as ET
H, DX = sys.argv[1:3]
x = open(DX, encoding='utf-8-sig').read()
pg, pi = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x).groups(); nm = re.search(r'name="Name">([^<]+)', x).group(1)
REF = 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pi, pg)
s = open(H, encoding='utf-8-sig').read()
for lab in ('Frontplate', 'Frontplate_Schutt'):
    i = s.index('<field name="label">%s</field>' % lab); a = s.rfind('<complex type="LayerCompOverlayInstance">', 0, i); blk = s[a:i]
    for f in ('colorTexture', 'rsmTexture'):
        blk, n = re.subn(r'(<field name="%s" )ref="[^"]*/ECU_Bumper_Front_ECU_col\\\\[^"]*" partitionGuid="[^"]*"' % f, lambda m: m.group(1) + REF, blk, count=1); assert n == 1, (lab, f)
    s = s[:a] + blk + s[i:]
open(H, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(H); print('wrote', H)
