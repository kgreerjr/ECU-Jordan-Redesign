"""ITEM 10 phase 2 v2 (user: no medallion on the sleeve stripes): City Connect patch at the front collar, in Away's collar-logo
spot (WHITEALT 'Collar Patch' layer: offset 0 / -0.125, just under the V). Full colour (UseDefaults + identity tints), no emboss.
usage: build_cc_collar_patch_60.py <CITY jersey xml in/out> <WHITEALT jersey xml> <ECU_CC_Patch_col dup xml> [scale]"""
import re, sys, uuid, xml.etree.ElementTree as ET
J, W, P = sys.argv[1:4]; SC = sys.argv[4] if len(sys.argv) > 4 else '0.03'
rd = lambda p: open(p, encoding='utf-8-sig').read()
s, w = rd(J), rd(W)
x = rd(P); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
TEX = 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pg.group(2), pg.group(1))
def ov_span(t, slot):
    a = t.index('<field name="%s">' % slot); e = t.index('</field>', t.index('<field name="overlay_blend">', a)); e = t.index('</field>', t.index('</complex>', e)); return a, e
assert 'CC Patch' not in s, 'patch already in this jersey'
free = [m for m in ('overlay_16', 'overlay_17', 'overlay_18', 'overlay_19', 'overlay_20') if not re.search(r'<field name="label">[^<]+</field>', s[slice(*ov_span(s, m))]) and 'colorTexture" ref="null"' in s[slice(*ov_span(s, m))]]
dst = free[0]
src = [m.group(1) for m in re.finditer(r'<field name="(overlay_\d+)">', w) if '<field name="label">Collar Patch</field>' in w[slice(*ov_span(w, m.group(1)))]][-1]   # the logo layer (overlay_12), not the solid backing
a, e = ov_span(w, src); blk = w[a:e].replace('<field name="%s">' % src, '<field name="%s">' % dst, 1)
new = []; mine = set()
def cv(xyz):
    g = str(uuid.uuid4()); mine.add(g)
    new.append('\t<instance guid="%s" type="ColorValue" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="Color">\n\t\t\t<complex type="Vec3">\n\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t</complex>\n\t\t</field>\n\t</instance>\n' % (g, *xyz)); return 'ref="%s"' % g
blk = re.sub(r'<field name="colorTexture" ref="[^"]*"( partitionGuid="[^"]*")? />', lambda m: '<field name="colorTexture" %s />' % TEX, blk, count=1)
blk = re.sub(r'<field name="normalTexture" ref="[^"]*"( partitionGuid="[^"]*")? />', '<field name="normalTexture" ref="null" />', blk, count=1)
blk = re.sub(r'(<field name="assetResolveRuleType">)\w+', r'\1AssetResolveRule_UseDefaults', blk, count=1)
for ch, xyz in (('R', (1, 0, 0)), ('G', (0, 1, 0)), ('B', (0, 0, 1))):
    blk = re.sub(r'<field name="color%s" ref="[^"]*"( partitionGuid="[^"]*")? />' % ch, lambda m: '<field name="color%s" %s />' % (ch, cv(xyz)), blk, count=1)
blk = blk.replace('<field name="label">Collar Patch</field>', '<field name="label">CC Patch (collar)</field>', 1)
for old in set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', blk)) - mine:
    k = w.index('<instance guid="%s"' % old); inst = w[k:w.index('</instance>', k) + len('</instance>')]; ng = str(uuid.uuid4())
    if 'LayerCompTransform' in inst:
        for f in ('scaleU', 'scaleV'): inst = re.sub(r'(<field name="%s">)[^<]*' % f, lambda m: m.group(1) + SC, inst, count=1)
        inst = re.sub(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda m: m.group(1) + SC + m.group(2) + SC, inst, count=1)
    new.append('\t' + inst.replace(old, ng) + '\n'); blk = blk.replace(old, ng)
c, d = ov_span(s, dst); s = s[:c] + blk + s[d:]
s = s.replace('</partition>', ''.join(new) + '</partition>')
open(J, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(J); print('collar patch ->', dst, 'scale', SC)
