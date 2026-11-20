import re, os, xml.etree.ElementTree as ET
R = os.environ.get('ECU_PROJECT_DIR', '.')
ECU = os.path.join(R, 'ECU Uniforms'); MICH = os.path.join(R, 'Michigan Uniform (take logo from this)')
OUT = os.path.join(R, 'FINAL')
rd = lambda p: open(p, encoding='utf-8-sig').read()
def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w', encoding='utf-8-sig', newline='').write(s)
def block(t, ov):
    i = t.index('<field name="%s">' % ov); ls = t.rfind('\n', 0, i) + 1; ind = t[ls:i]
    e = '\n' + ind + '</field>'; return i, t.index(e, i) + len(e)
def vendor_overlay(t):
    m = re.search(r'colorTexture" ref="[^"]*decals/vendors/', t)
    return re.findall(r'<field name="(\w+)">\s*<complex type="LayerCompOverlayInstance">', t[:m.start()])[-1]
def tbody(t, g):
    k = t.index('<instance guid="%s"' % g); s = t.index('\n', k) + 1
    return s, t.rindex('\n', 0, t.index('</instance>', k)) + 1
# duplicate texture refs
DUP = {}
for setname, pre in [('withtext', 'ECU_Jumpman_Decal_WithText_'), ('plain', 'ECU_Jumpman_Decal_')]:
    for k, fld in [('col', 'colorTexture'), ('norm', 'normalTexture'), ('rsm', 'rsmTexture')]:
        x = rd(os.path.join(R, 'ECU_JUMPMAN xml', pre + k + '.xml'))
        pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
        assert nm.endswith(pre + k)
        DUP[(setname, fld)] = '<field name="%s" ref="%s\\\\%s" partitionGuid="%s" />' % (fld, nm, pg.group(2), pg.group(1))
# Michigan placement for jerseys + socks (pants keep ECU's own placement: Michigan's needs a layout map ECU doesn't load)
def mtr(rel, ov):
    t = rd(os.path.join(MICH, rel)); a, b = block(t, ov)
    s, e = tbody(t, re.search(r'overlay_transform" ref="([0-9a-f-]+)"', t[a:b]).group(1)); return t[s:e]
TR = {'J': mtr('MICH Jerseys/MICH_JERSEY_2023_WHITE.xml', 'overlay_5'), 'S': mtr('MICH Socks/MICH_SOCKS_2021_WHITE.xml', 'overlay_1')}
COL = {}
for dp, _, fs in os.walk(ECU):
    for f in fs:
        for m in re.finditer(r'ref="((?:content|ContentShared)/[^"]*/(ECU_Purple|ECU_Gold|global_white|global_black)\\\\[^"]*)" partitionGuid="([^"]*)"', rd(os.path.join(dp, f))):
            COL[m.group(2)] = 'ref="%s" partitionGuid="%s"' % (m.group(1), m.group(3))
PLAN = {  # (uniform base color -> R, logo color -> G)
 'ECU Jerseys/ECU_JERSEY_2023_BLACK.xml': ('global_black', 'global_white'), 'ECU Jerseys/ECU_JERSEY_2023_PURPLE.xml': ('ECU_Purple', 'ECU_Gold'),
 'ECU Jerseys/ECU_JERSEY_2023_PURPLEALT.xml': ('ECU_Purple', 'ECU_Gold'), 'ECU Jerseys/ECU_JERSEY_2023_WHITE.xml': ('global_white', 'ECU_Purple'),
 'ECU Jerseys/ECU_JERSEY_2026_WHITEALT.xml': ('global_white', 'ECU_Purple'),
 'ECU Pants/ECU_PANTS_2023_BLACK.xml': ('global_black', 'global_white'), 'ECU Pants/ECU_PANTS_2023_WHITE.xml': ('global_white', 'ECU_Purple'),
 'ECU Pants/ECU_PANTS_2023_WHITEALT.xml': ('global_white', 'ECU_Purple'), 'ECU Pants/ECU_PANTS_2023_YELLOW.xml': ('ECU_Gold', 'global_white'),
 'ECU Pants/ECU_Pants_2023_PURPLE.xml': ('ECU_Purple', 'ECU_Gold'), 'ECU Pants/ECU_Pants_2023_PURPLEALT.xml': ('ECU_Purple', 'ECU_Gold'),
 'ECU Socks/ECU_SOCKS_2023_BLACK.xml': ('global_black', 'global_white'), 'ECU Socks/ECU_SOCKS_2023_WHITE.xml': ('global_white', 'global_black')}
for rel, (rc, gc) in PLAN.items():
    t = rd(os.path.join(ECU, rel)); kind = 'J' if 'JERSEY' in rel else 'P' if 'Pants' in rel else 'S'
    ov = vendor_overlay(t); a, b = block(t, ov); blk = t[a:b]
    st = 'withtext' if 'Adidas_Decal_2023_WithText_col' in blk else 'plain'
    assert re.search(r'colorR" ref="[^"]*/([A-Za-z_]+)\\\\', blk).group(1) == gc, rel
    for fld in ('colorTexture', 'normalTexture', 'rsmTexture'):
        blk, c = re.subn(r'<field name="%s" ref="(?:null|[^"]*decals/vendors/Adidas[^"]*" partitionGuid="[^"]*)" />' % fld, lambda m: DUP[(st, fld)], blk, count=1); assert c == 1, (rel, fld)
    blk = re.sub(r'(<field name="hasAO">)true(</field>)', r'\1false\2', blk, count=1)
    blk, c = re.subn(r'<field name="colorR" ref="[^"]*"( partitionGuid="[^"]*")? />', lambda m: '<field name="colorR" %s />' % COL[rc], blk, count=1); assert c == 1
    blk, c = re.subn(r'<field name="colorG" ref="[^"]*"( partitionGuid="[^"]*")? />', lambda m: '<field name="colorG" %s />' % COL[gc], blk, count=1); assert c == 1
    blk, c = re.subn(r'(<field name="label">)Adidas Logo(</field>)', r'\1Jumpman Logo\2', blk); assert c == 1
    blk = re.sub(r'<field name="rsmR" ref="[0-9a-f-]+" />', '<field name="rsmR" ref="null" />', blk)
    t = t[:a] + blk + t[b:]
    if kind in TR:
        s, e = tbody(t, re.search(r'overlay_transform" ref="([0-9a-f-]+)"', blk).group(1)); t = t[:s] + TR[kind] + t[e:]
    assert 'decals/vendors/Adidas' not in t and 'Jumpman_Decal_2022' not in t and 'jordan_patch_slot' not in t and 'Pants_UVSet_front' not in t
    p = os.path.join(OUT, rel.split('/')[0].replace('ECU ', ''), os.path.basename(rel)); wr(p, t); ET.parse(p)
    print('%-32s set=%-8s R=%-12s G=%-12s placement=%s' % (os.path.basename(rel), st, rc, gc, {'J': 'Michigan chest', 'P': 'ECU original hip', 'S': 'Michigan sock'}[kind]))
