"""City Connect pants: hip logo layer ('Logo ECU') -> gold skyline silhouette (ECU_CC_Skyline_col: R = shape, alpha = shape).
Tint R = ECU Gold, no emboss. Layer scale x SCALE_K (the skyline is a wide strip in a square texture).
usage: build_cc_skyline_60.py <CITY pants xml in> <dup xml> <out xml> [scale]"""
import re, sys, xml.etree.ElementTree as ET
J, P, O = sys.argv[1:4]; SC = sys.argv[4] if len(sys.argv) > 4 else '0.09'
rd = lambda p: open(p, encoding='utf-8-sig').read()
s = rd(J); x = rd(P)
pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
TEX = 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pg.group(2), pg.group(1))
GOLD = re.search(r'ref="[^"]*/ECU_Gold\\\\[^"]*" partitionGuid="[^"]*"', s).group(0)
m = re.search(r'<field name="label">Logo ECU</field>', s); a = s.rfind('<complex type="LayerCompOverlayInstance">', 0, m.start())
e = m.end() + re.search(r'<field name="overlay_transform" ref="[^"]*" />', s[m.end():]).end(); blk = s[a:e]
def sub(name, val):
    global blk; blk, n = re.subn(r'(<field name="%s" )ref="[^"]*"(?: partitionGuid="[^"]*")?' % name, lambda q: q.group(1) + val, blk, count=1); assert n == 1, name
sub('colorTexture', TEX); sub('normalTexture', 'ref="null"'); sub('colorR', GOLD)
blk = blk.replace('<field name="label">Logo ECU</field>', '<field name="label">CC Skyline</field>')
s = s[:a] + blk + s[e:]
g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', blk).group(1); assert s.count('ref="%s"' % g) == 1
mm = re.search(r'(<instance guid="%s"[^>]*>)(.*?)(</instance>)' % g, s, re.S); b = mm.group(2)
for f in ('scaleU', 'scaleV'): b = re.sub(r'(<field name="%s">)[^<]*' % f, lambda q: q.group(1) + SC, b, count=1)
b = re.sub(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda q: q.group(1) + SC + q.group(2) + SC, b, count=1)
print('old transform:', re.findall(r'<field name="(offsetU|offsetV|rotate)">([^<]*)', b))
s = s[:mm.start(2)] + b + s[mm.end(2):]
open(O, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(O); print('skyline on the hip, scale', SC)
