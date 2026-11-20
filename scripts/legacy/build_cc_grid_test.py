"""Step 1: grid test on the Home Option helmet (2021_PURPLE_yellowFacemask).
Right/Left Side Logo layers -> ECU_CC_Helmet_Right/Left_col, Warning Label (rear stickers UV) -> ECU_CC_Helmet_Back_col.
Full UV coverage (scale 1, offset 0), full-color (UseDefaults + identity tints), no normal / shine maps.
TEST ONLY - restore the helmet from FINAL afterwards."""
import re, sys, uuid
src, out = sys.argv[1], sys.argv[2]
T = 'content/characters/player/parts/uniforms/helmets/decals/teams/'
TEX = {
 'Right Side Logo': f'ref="{T}ECU_CC_Helmet_Right_col\\\\3163dc39-1b9b-f028-fa3c-ac46f8e91541" partitionGuid="add58c7d-7b66-40b8-a1a8-57d34ff15212"',
 'Left Side Logo':  f'ref="{T}ECU_CC_Helmet_Left_col\\\\1f84d8b5-a8f0-4eb6-79c8-72ab2e5a9a10" partitionGuid="05c31ede-68a6-4e84-8b2f-71ab9bc83892"',
 'Warning Label':   f'ref="{T}ECU_CC_Helmet_Back_col\\\\f8ced802-c350-83e2-1e50-0cf1bd42b302" partitionGuid="2a7ff100-6bce-40da-a37d-05dcbeee01ce"',
}
s = open(src, encoding='utf-8-sig').read(); new = []
def cv(xyz):
    g = str(uuid.uuid4())
    new.append('\t<instance guid="%s" type="ColorValue" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="Color">\n\t\t\t<complex type="Vec3">\n\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t</complex>\n\t\t</field>\n\t</instance>\n' % (g, *xyz))
    return 'ref="%s"' % g
for lab, tex in TEX.items():
    m = re.search(r'<field name="label">' + re.escape(lab) + r'</field>', s); assert m, lab
    a = s.rfind('<complex type="LayerCompOverlayInstance">', 0, m.start())
    b = re.search(r'<field name="overlay_transform" ref="([0-9a-f-]{36})" />', s[m.end():]); tg = b.group(1); b = m.end() + b.end()
    blk = s[a:b]
    def sub(name, val):
        global blk
        blk, n = re.subn(r'(<field name="' + name + r'" )ref="[^"]*"(?: partitionGuid="[^"]*")?', lambda x: x.group(1) + val, blk, count=1); assert n == 1, (lab, name)
    sub('colorTexture', tex); sub('normalTexture', 'ref="null"'); sub('rsmTexture', 'ref="null"')
    blk = re.sub(r'(<field name="assetResolveRuleType">)\w+', r'\1AssetResolveRule_UseDefaults', blk, count=1)
    for ch, xyz in (('R', (1, 0, 0)), ('G', (0, 1, 0)), ('B', (0, 0, 1))): sub('color' + ch, cv(xyz))
    blk = re.sub(r'(<field name="TintMode">)\w+', r'\1LayerCompTintMode_WithValue', blk, count=1)
    s = s[:a] + blk + s[b:]
    assert s.count('ref="' + tg + '"') == 1, lab + ' transform shared'
    mm = re.search(r'(<instance guid="' + tg + r'" type="LayerCompTransform"[^>]*>)(.*?)(</instance>)', s, re.S); body = mm.group(2)
    for k, v in (('scaleU', 1), ('scaleV', 1), ('offsetU', 0), ('offsetV', 0), ('rotate', 0), ('x', 1), ('y', 1), ('z', 0), ('w', 0)):
        body = re.sub(r'(<field name="' + k + r'">)[^<]*', lambda x: x.group(1) + str(v), body, count=1)
    s = s[:mm.start(2)] + body + s[mm.end(2):]
    print('grid on', lab)
s = s.replace('</partition>', ''.join(new) + '</partition>')
open(out, 'w', encoding='utf-8-sig', newline='').write(s)
import xml.etree.ElementTree as ET; ET.parse(out); print('ok')
