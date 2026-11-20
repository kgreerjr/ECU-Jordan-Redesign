"""City Connect jersey: chest PIRATES (layer 'ECU Logo') -> airbrushed ECU_CC_Pirates_col, full colour (UseDefaults +
identity tints), no emboss/shine maps, layer scale x 1/0.92 (letters were shrunk inside the texture to fit the outline).
usage: build_cc_pirates_60.py <CITY jersey xml in> <dup xml> <out xml>"""
import re, sys, uuid, xml.etree.ElementTree as ET
J, P, O = sys.argv[1:4]; K = 1 / 0.92
rd = lambda p: open(p, encoding='utf-8-sig').read()
s = rd(J); x = rd(P)
pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
TEX = 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pg.group(2), pg.group(1))
new = []
def cv(xyz):
    g = str(uuid.uuid4()); new.append('\t<instance guid="%s" type="ColorValue" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="Color">\n\t\t\t<complex type="Vec3">\n\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t</complex>\n\t\t</field>\n\t</instance>\n' % (g, *xyz)); return 'ref="%s"' % g
m = re.search(r'<field name="label">ECU Logo</field>', s); a = s.rfind('<complex type="LayerCompOverlayInstance">', 0, m.start())
e = m.end() + re.search(r'<field name="overlay_transform" ref="[^"]*" />', s[m.end():]).end(); blk = s[a:e]
def sub(name, val):
    global blk; blk, n = re.subn(r'(<field name="%s" )ref="[^"]*"(?: partitionGuid="[^"]*")?' % name, lambda q: q.group(1) + val, blk, count=1); assert n == 1, name
sub('colorTexture', TEX); sub('normalTexture', 'ref="null"'); sub('rsmTexture', 'ref="null"')
blk = re.sub(r'(<field name="assetResolveRuleType">)\w+', r'\1AssetResolveRule_UseDefaults', blk, count=1)
sub('colorR', cv((1, 0, 0))); sub('colorG', cv((0, 1, 0))); sub('colorB', cv((0, 0, 1)))
s = s[:a] + blk + s[e:]
g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', blk).group(1); assert s.count('ref="%s"' % g) == 1
mm = re.search(r'(<instance guid="%s"[^>]*>)(.*?)(</instance>)' % g, s, re.S); b = mm.group(2)
su = round(float(re.search(r'<field name="scaleU">([^<]*)', b).group(1)) * K, 4); sv = round(float(re.search(r'<field name="scaleV">([^<]*)', b).group(1)) * K, 4)
b = re.sub(r'(<field name="scaleU">)[^<]*', lambda q: q.group(1) + str(su), b, count=1); b = re.sub(r'(<field name="scaleV">)[^<]*', lambda q: q.group(1) + str(sv), b, count=1)
b = re.sub(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda q: '%s%s%s%s' % (q.group(1), su, q.group(2), sv), b, count=1)
s = s[:mm.start(2)] + b + s[mm.end(2):]
s = s.replace('</partition>', ''.join(new) + '</partition>')
open(O, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(O); print('PIRATES -> airbrush, scale', su, sv)
