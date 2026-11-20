# Replace the AAC helmet sticker with the "NO QUARTER" flag (ECU_Helmet_NoQuarter_col, dup of AAC_Helmet_2022_col, so
# every ECU helmet already loads it). EA's helmet stickers vanish after a conference change (Ohio State too); this layer
# is set to AssetResolveRule_UseDefaults so no ruleset can drop it (tints still apply, technical notes section 24).
# Same colors as the AAC (R field, G border, B art), same spot; size = the US flag's width (flag art is 92% of its canvas,
# square canvas -> U:V 0.4286 like the AAC and flag layers).
# usage: build_helmet_noquarter.py <helmet xml in/out> <ECU_Helmet_NoQuarter_col.xml> [width scaleU]
import re, sys, xml.etree.ElementTree as ET
H, DX = sys.argv[1:3]
x = open(DX, encoding='utf-8-sig').read(); pg, pi = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x).groups()
nm = re.search(r'name="Name">([^<]+)', x).group(1); REF = 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pi, pg)
s = open(H, encoding='utf-8-sig').read()
i = s.index('<field name="label">AAC  Decal</field>'); a = s.rfind('<complex type="LayerCompOverlayInstance">', 0, i); b = s[a:i]
b, n = re.subn(r'(<field name="colorTexture" )ref="[^"]*"(?: partitionGuid="[^"]*")?', lambda m: m.group(1) + REF, b, count=1); assert n == 1
for f in ('rsmTexture', 'normalTexture'):
    b = re.sub(r'(<field name="%s" )ref="[^"]*"(?: partitionGuid="[^"]*")?' % f, lambda m: m.group(1) + 'ref="null"', b, count=1)
b, n = re.subn(r'(<field name="assetResolveRuleType">)[^<]*', lambda m: m.group(1) + 'AssetResolveRule_UseDefaults', b, count=1); assert n == 1
s = s[:a] + b + s[i:]
# size: US flag width
fi = s.index('<field name="label">Flag</field>'); fg = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', s[fi:]).group(1)
fk = s.index('<instance guid="%s"' % fg); fsu = float(re.search(r'name="scaleU">([^<]+)', s[fk:s.index('</instance>', fk)]).group(1))
su = round(float(sys.argv[3]) if len(sys.argv) > 3 else fsu / 0.92, 4); sv = round(su / 0.4286, 4)
g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', s[i:]).group(1); assert s.count('ref="%s"' % g) == 1
m = re.search(r'(<instance guid="' + g + r'"[^>]*>)(.*?)(</instance>)', s, re.S); body = m.group(2)
for k, v in (('scaleU', su), ('scaleV', sv), ('x', su), ('y', sv)):
    body, n = re.subn(r'(<field name="%s">)[^<]*' % k, lambda mm: mm.group(1) + str(v), body, count=1); assert n == 1
s = s[:m.start(2)] + body + s[m.end(2):]
open(H, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(H); print('No Quarter on', H.split('/')[-1], 'scale', su, sv)
