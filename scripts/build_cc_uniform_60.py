"""ITEM 10: City Connect "Greenville Nights" jersey + pants (phase 1).
Jersey = the user's copy of Home's jersey (ECU_JERSEY_2026_CITY): midnight-purple star-speckle fabric (body + sleeves),
gold PIRATES, gold numbers / white outline (name too), gold captain C; sleeves already gold|white|gold.
Pants = copy of Jolly Roger's pants (ECU_PANTS_2026_CITY): same star fabric, gold|white|gold stripe with midnight gaps.
Wrappers 91726007 / 91726008; preset CurrentAlternate (Home Option slot) -> new jersey + pants.
usage: build_cc_uniform_60.py <dup export dir> <FINAL dir>"""
import re, sys, uuid, os, xml.etree.ElementTree as ET
DUP, FIN = sys.argv[1], sys.argv[2]
rd = lambda p: open(p, encoding='utf-8-sig').read()
def wr(p, t): open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p); print('wrote', os.path.basename(p))
def lin(c): c = c / 255; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
MID, STAR, HAZE = (44, 24, 78), (235, 230, 250), (88, 52, 140)
def idref(xml):
    x = rd(xml); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
    return 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pg.group(2), pg.group(1))
def anyref(t, name):
    m = re.search(r'ref="[^"]*/%s\\\\[^"]*" partitionGuid="[^"]*"' % name, t); assert m, name; return m.group(0)
class Doc:
    def __init__(s, t): s.t = t; s.new = []
    def cv(s, rgb):
        g = str(uuid.uuid4()); x, y, z = (round(lin(c), 7) for c in rgb)
        s.new.append('\t<instance guid="%s" type="ColorValue" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="Color">\n\t\t\t<complex type="Vec3">\n\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t</complex>\n\t\t</field>\n\t</instance>\n' % (g, x, y, z))
        return 'ref="%s"' % g
    def span(s, lab):
        m = re.search(r'<field name="label">' + re.escape(lab) + r'</field>', s.t); assert m, lab
        a = max(s.t.rfind('<complex type="LayerCompMaterialInstance">', 0, m.start()), s.t.rfind('<complex type="LayerCompOverlayInstance">', 0, m.start()))
        e = re.search(r'<field name="(?:overlay|material)_transform" ref="[^"]*" />', s.t[m.end():]); return a, m.end() + e.end()
    def sub(s, a, e, name, val):
        blk, n = re.subn(r'(<field name="' + name + r'" )ref="[^"]*"(?: partitionGuid="[^"]*")?', lambda x: x.group(1) + val, s.t[a:e], count=1); assert n == 1, name
        s.t = s.t[:a] + blk + s.t[e:]
    def tint(s, lab, R=None, G=None, B=None):
        for ch, v in (('R', R), ('G', G), ('B', B)):
            if v is not None: a, e = s.span(lab); s.sub(a, e, 'color' + ch, v)
    def scale(s, lab, k):
        a, e = s.span(lab); g = re.search(r'_transform" ref="([0-9a-f-]{36})"', s.t[a:e]).group(1); assert s.t.count('ref="%s"' % g) == 1, lab
        m = re.search(r'(<instance guid="' + g + r'"[^>]*>)(.*?)(</instance>)', s.t, re.S); b = m.group(2)
        for f in ('scaleU', 'scaleV'): b = re.sub(r'(<field name="%s">)[^<]*' % f, lambda x: x.group(1) + str(k), b, count=1)
        b = re.sub(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda x: '%s%s%s%s' % (x.group(1), k, x.group(2), k), b, count=1)
        s.t = s.t[:m.start(2)] + b + s.t[m.end(2):]
    def fabric(s, lab, tex, haze=HAZE):
        a, e = s.span(lab); s.sub(a, e, 'colorTexture', tex)
        s.tint(lab, s.cv(MID), s.cv(STAR), s.cv(haze)); s.scale(lab, 0.12)
    def array_tint(s, texname, R=None, G=None, B=None):
        m = re.search(r'colorTexture" ref="[^"]*%s[^"]*"' % texname, s.t); assert m, texname
        a = s.t.rfind('<complex type="LayerCompArrayOverlayInstance">', 0, m.start()); e = s.t.index('<field name="label">', m.end())
        for ch, v in (('R', R), ('G', G), ('B', B)):
            if v is not None: s.sub(a, e, 'color' + ch, v); e = s.t.index('<field name="label">', a)
    def done(s): return s.t.replace('</partition>', ''.join(s.new) + '</partition>')
# ---- jersey
J = Doc(rd(DUP + '/ECU_JERSEY_2026_CITY.xml')); assert 'type="JerseyPartItem"' in J.t
GOLD = anyref(J.t, 'ECU_Gold'); NW = anyref(J.t, 'global_number_white')
SJ = idref(DUP + '/ECU_CC_Stars_Jersey_col.xml'); SP = idref(DUP + '/ECU_CC_Stars_Pants_col.xml')
J.fabric('Vapor Untouchable Fabric', SJ); J.fabric('Sleeve Fabric', SJ)
J.tint('ECU Logo', GOLD, GOLD)                                     # PIRATES gold
J.array_tint('ECU_Jersey_2023_NUM_Array', GOLD, NW, NW)            # numbers gold, white outline
J.array_tint('Standard_Jersey_2022_Blocky_02', GOLD, GOLD)         # name on back gold
cp = re.search(r'<complex type="CaptainPatch">(.*?)</complex>', J.t, re.S)
blk = cp.group(1)
for k in ('captainpatch_Color1', 'captainpatch_Color2', 'captainpatch_Color3'):
    blk, n = re.subn(r'(<field name="%s" )ref="[^"]*"(?: partitionGuid="[^"]*")?' % k, lambda x: x.group(1) + GOLD, blk); assert n == 1
J.t = J.t[:cp.start(1)] + blk + J.t[cp.end(1):]
wr(FIN + '/Jerseys/ECU_JERSEY_2026_CITY.xml', J.done())
# ---- pants
P = Doc(rd(DUP + '/ECU_PANTS_2026_CITY.xml')); assert 'type="PantsPartItem"' in P.t
P.fabric('Adidas Base Fabric', SP, haze=MID)   # v2 (user preview): pants haze read as big blotches -> haze tinted = base (stars only)
P.tint('Stripe', B=P.cv(MID))                                      # R white center, G gold outers (kept), gaps midnight
wr(FIN + '/Pants/ECU_PANTS_2026_CITY.xml', P.done())
# ---- wrappers
def wrapper(name, iid, disp, old_part, new_part):
    W = rd(DUP + '/' + name + '.xml')
    W, c1 = re.subn(r'(<field name="Id">\s*<complex type="ItemDataId">\s*<field name="Id">)\d+<', lambda m: m.group(1) + str(iid) + '<', W, 1)
    W, c2 = re.subn(r'(<field name="DisplayName">)[^<]*', lambda m: m.group(1) + disp, W, 1)
    W, c3 = re.subn(r'(<field name="AssetName">)%s(</field>)' % old_part, lambda m: m.group(1) + new_part + m.group(2), W, 1)
    assert c1 == c2 == c3 == 1, name; wr(FIN + '/Wrappers/' + name + '.xml', W)
wrapper('U_ECU_JERSEY_2026_CITY', 91726007, 'City Connect Jersey', 'ECU_JERSEY_2023_PURPLEALT', 'ECU_JERSEY_2026_CITY')
wrapper('U_ECU_PANTS_2026_CITY', 91726008, 'City Connect Pants', 'ECU_Pants_2023_PURPLE', 'ECU_PANTS_2026_CITY')
# ---- preset (Home Option slot)
pre = FIN + '/Uniform sets/U_UniformType_ECU_CurrentAlternate.xml'; u = rd(pre)
for a, b in (('U_ECU_JERSEY_2023_PURPLEALT', 'U_ECU_JERSEY_2026_CITY'), ('U_ECU_Pants_2023_PURPLEALT', 'U_ECU_PANTS_2026_CITY')):
    u, n = re.subn(r'(<field name="ItemAssetName">)%s<' % a, lambda m: m.group(1) + b + '<', u); assert n == 1, a
wr(pre, u); print('preset:', re.findall(r'<field name="ItemAssetName">([^<]*)', u))
