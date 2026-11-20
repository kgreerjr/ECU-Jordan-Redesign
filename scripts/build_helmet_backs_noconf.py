# 6.0 helmet backs without the conference sticker. EA's helmet stickers never follow a conference change
# (Ohio State loses its Big Ten sticker in the Big 12 too), and ECU usually leaves the AAC in dynasty, so the AAC sticker
# is removed and the back re-laid out, one helmet at a time.
# Layout v1 (mod author, Away first): everything on the AAC's level; AAC gone; number centered on the stripe;
# CJ2K where the number was (same U, AAC's V); flag where the AAC was (AAC's U and V). Warning label unchanged.
# usage: build_helmet_backs_noconf.py <helmet xml in/out>
import re, sys, xml.etree.ElementTree as ET
H = sys.argv[1]; s = open(H, encoding='utf-8-sig').read()
def blk_span(t, lab):
    i = t.index('<field name="label">%s</field>' % lab); a = t.rfind('<complex type="LayerCompOverlayInstance">', 0, i); return a, i
def tf(t, lab):
    i = t.index('<field name="label">%s</field>' % lab); g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', t[i:]).group(1)
    assert t.count('ref="%s"' % g) == 1, lab
    return re.search(r'(<instance guid="' + g + r'"[^>]*>)(.*?)(</instance>)', t, re.S)
def get(m, k): return float(re.search(r'name="%s">([^<]+)' % k, m.group(2)).group(1))
def setpos(t, lab, u, v):
    m = tf(t, lab); b = m.group(2)
    for k, val in (('offsetU', u), ('offsetV', v), ('z', u), ('w', v)):
        b, n = re.subn(r'(<field name="%s">)[^<]*' % k, lambda mm: mm.group(1) + str(val), b, count=1); assert n == 1
    return t[:m.start(2)] + b + t[m.end(2):]
aac = tf(s, 'AAC  Decal'); AU, AV = get(aac, 'offsetU'), get(aac, 'offsetV')
cj = tf(s, 'CJ2K Sticker'); CU = get(cj, 'offsetU')
# 1) AAC sticker off (layer kept, textures null)
a, i = blk_span(s, 'AAC  Decal'); b = s[a:i]
for f in ('colorTexture', 'rsmTexture', 'normalTexture'):
    b = re.sub(r'(<field name="%s" )ref="[^"]*"(?: partitionGuid="[^"]*")?' % f, lambda mm: mm.group(1) + 'ref="null"', b, count=1)
s = s[:a] + b + s[i:]
# 2) flag -> the AAC's spot; 3) CJ2K -> the number's spot (its own U, the AAC's V)
s = setpos(s, 'Flag', AU, AV); s = setpos(s, 'CJ2K Sticker', CU, AV)
# 4) number centered on the stripe, same height
s, n = re.subn(r'(<field name="backnumberoffset_scale">\s*<complex type="Vec4">\s*<field name="x">)[^<]*', lambda mm: mm.group(1) + '0', s, count=1); assert n == 1
open(H, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(H)
print('AAC off; flag ->', AU, AV, '; CJ2K ->', CU, AV, '; number x -> 0')
