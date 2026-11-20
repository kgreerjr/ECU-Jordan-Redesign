"""Phase 2: City Connect sleeve patch (Cupola badge) on ECU_JERSEY_2026_CITY.
Copies Ghost Ship's two stock sleeve-decal layers (standard/tight + long sleeves; EA's sleeveDecalDuplicate UV set puts the
decal on both sleeves) into two empty overlay slots, full colour (UseDefaults + identity tints), texture = ECU_CC_Patch_col.
usage: build_cc_patch_60.py <CITY jersey xml in/out> <Ghost jersey xml> <ECU_CC_Patch_col dup export xml> [scale]"""
import re, sys, uuid, xml.etree.ElementTree as ET
J, G, P = sys.argv[1:4]; SC = sys.argv[4] if len(sys.argv) > 4 else None
rd = lambda p: open(p, encoding='utf-8-sig').read()
s, g = rd(J), rd(G)
x = rd(P); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
TEX = 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pg.group(2), pg.group(1))
def ov_span(t, slot):
    a = t.index('<field name="%s">' % slot); e = t.index('</field>', t.index('<field name="overlay_blend">', a)); e = t.index('</field>', t.index('</complex>', e)); return a, e
def slot_of(t, lab):
    i = t.index('<field name="label">%s' % lab); return re.findall(r'<field name="(overlay_\d+)">', t[:i])[-1]
new = []; mine = set()
def cv(xyz):
    gg = str(uuid.uuid4()); mine.add(gg); new.append('\t<instance guid="%s" type="ColorValue" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="Color">\n\t\t\t<complex type="Vec3">\n\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t</complex>\n\t\t</field>\n\t</instance>\n' % (gg, *xyz)); return 'ref="%s"' % gg
if 'CC Patch' in s: raise SystemExit('patch already added')
free = [m for m in ('overlay_16', 'overlay_17', 'overlay_18', 'overlay_19', 'overlay_20') if 'colorTexture" ref="null"' in s[slice(*ov_span(s, m))] and '<field name="label"></field>' in s[ov_span(s, m)[0]:ov_span(s, m)[0] + 3000][:3000] and not re.search(r'<field name="label">[^<]+</field>', s[slice(*ov_span(s, m))])]
assert len(free) >= 2, free
for lab, dst in (('Sleeve Decals - Standard', free[0]), ('Sleeve Decals - Long', free[1])):
    src = slot_of(g, lab); a, e = ov_span(g, src); blk = g[a:e].replace('<field name="%s">' % src, '<field name="%s">' % dst, 1)
    blk = re.sub(r'<field name="colorTexture" ref="[^"]*"( partitionGuid="[^"]*")? />', lambda m: '<field name="colorTexture" %s />' % TEX, blk, count=1)
    blk = re.sub(r'(<field name="assetResolveRuleType">)\w+', r'\1AssetResolveRule_UseDefaults', blk, 1)
    for ch, xyz in (('R', (1, 0, 0)), ('G', (0, 1, 0)), ('B', (0, 0, 1))):
        blk = re.sub(r'<field name="color%s" ref="[^"]*"( partitionGuid="[^"]*")? />' % ch, lambda m: '<field name="color%s" %s />' % (ch, cv(xyz)), blk, 1)
    blk = re.sub(r'(<field name="label">)Sleeve Decals[^<]*', lambda m: m.group(1) + 'CC Patch ' + ('(standard sleeves)' if 'Standard' in lab else '(long sleeves)'), blk, 1)
    for old in set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', blk)):          # own copies of local instances (transform)
        if old in mine: continue
        k = g.index('<instance guid="%s"' % old); inst = g[k:g.index('</instance>', k) + len('</instance>')]; ng = str(uuid.uuid4())
        if SC and 'LayerCompTransform' in inst:
            for f in ('scaleU', 'scaleV'): inst = re.sub(r'(<field name="%s">)[^<]*' % f, lambda m: m.group(1) + SC, inst, 1)
            inst = re.sub(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda m: m.group(1) + SC + m.group(2) + SC, inst, 1)
        new.append('\t' + inst.replace(old, ng) + '\n'); blk = blk.replace(old, ng)
    c, d = ov_span(s, dst); s = s[:c] + blk + s[d:]; print(lab, '->', dst)
s = s.replace('</partition>', ''.join(new) + '</partition>')
open(J, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(J); print('ok')
