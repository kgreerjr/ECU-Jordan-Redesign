"""ITEM 10: Home Option = City Connect helmet (ECU_HELMET_2021_PURPLE_yellowFacemask).
- Left/Right Side Logo layers -> the airbrushed panels (ECU_CC_Helmet_Left/Right_col), full UV coverage (scale 1, offset 0),
  full color (UseDefaults + identity tints), no emboss/shine maps, one satin surface (metal 0, reflectance 0.4, smoothness 0.5).
  Grid test 2026-11-16: these two layers cover the whole shell, one half each.
- Center Stripe layer -> ECU_CC_Helmet_Back_col (gold center stripe + gold pinstripes, clear between), Blackout's stripe width
  (scaleU 0.45), matte like every 6.0 stripe.
- Shell -> ECU Purple. Back stickers (AAC, flag, CJ2K, warning label) + back number -> Black Pirate's values (same 2021 shell,
  same stripe width), so they clear the new stripe.
NOTE: build_helmet_numbers.py would put this helmet back on the no-stripe layout; run this script after it.
Usage: python build_cc_helmet_60.py <Home Option helmet xml> <Blackout helmet xml> <out xml>"""
import re, sys, uuid, xml.etree.ElementTree as ET
src, ref, out = sys.argv[1:4]
s = open(src, encoding='utf-8-sig').read(); b = open(ref, encoding='utf-8-sig').read(); new = []
T = 'content/characters/player/parts/uniforms/helmets/decals/teams/'
TEX = {
 'Right Side Logo': f'ref="{T}ECU_CC_Helmet_Right_col\\\\3163dc39-1b9b-f028-fa3c-ac46f8e91541" partitionGuid="add58c7d-7b66-40b8-a1a8-57d34ff15212"',
 'Left Side Logo':  f'ref="{T}ECU_CC_Helmet_Left_col\\\\1f84d8b5-a8f0-4eb6-79c8-72ab2e5a9a10" partitionGuid="05c31ede-68a6-4e84-8b2f-71ab9bc83892"',
 'Center Stripe':   f'ref="{T}ECU_CC_Helmet_Back_col\\\\f8ced802-c350-83e2-1e50-0cf1bd42b302" partitionGuid="2a7ff100-6bce-40da-a37d-05dcbeee01ce"',
}
PURPLE = 'ref="content/characters/player/parts/uniforms/team_colors/ECU_Purple\\\\46d33457-94a7-4c4c-8f0c-d4ddd7113d71" partitionGuid="c76ded6f-7cf2-4520-a156-522e523c721e"'
def inst(kind, body):
    g = str(uuid.uuid4()); new.append('\t<instance guid="%s" type="%s" exported="true">\n%s\t</instance>\n' % (g, kind, body)); return 'ref="%s"' % g
def cv(x, y, z): return inst('ColorValue', '\t\t<field name="Name"></field>\n\t\t<field name="Color">\n\t\t\t<complex type="Vec3">\n\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t</complex>\n\t\t</field>\n' % (x, y, z))
def surf(metal, refl, smooth): return inst('LayerCompSurfaceParam', '\t\t<field name="Name"></field>\n\t\t<field name="metal_mask">%s</field>\n\t\t<field name="reflectance">%s</field>\n\t\t<field name="smoothness">%s</field>\n' % (metal, refl, smooth))
def span(t, lab):
    m = re.search(r'<field name="label">' + re.escape(lab) + r'</field>', t); assert m, lab
    a = max(t.rfind('<complex type="LayerCompOverlayInstance">', 0, m.start()), t.rfind('<complex type="LayerCompMaterialInstance">', 0, m.start()))
    e = re.search(r'<field name="(?:overlay|material)_transform" ref="[^"]*" />', t[m.end():]); return a, m.end() + e.end()
def sub(blk, name, val):
    blk, n = re.subn(r'(<field name="' + name + r'" )ref="[^"]*"(?: partitionGuid="[^"]*")?', lambda x: x.group(1) + val, blk, count=1); assert n == 1, name; return blk
def set_tf(t, g, vals):
    m = re.search(r'(<instance guid="' + g + r'" type="LayerCompTransform"[^>]*>)(.*?)(</instance>)', t, re.S); body = m.group(2)
    su, sv, ou, ov, rot = vals
    for k, v in (('scaleU', su), ('scaleV', sv), ('offsetU', ou), ('offsetV', ov), ('rotate', rot)):
        body, n = re.subn(r'(<field name="' + k + r'">)[^<]*', lambda x: x.group(1) + str(v), body, count=1); assert n == 1, k
    body, n = re.subn(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*(</field>\s*<field name="z">)[^<]*(</field>\s*<field name="w">)[^<]*',
                      lambda x: f'{x.group(1)}{su}{x.group(2)}{sv}{x.group(3)}{ou}{x.group(4)}{ov}', body, count=1); assert n == 1
    return t[:m.start(2)] + body + t[m.end(2):]
def tf_of(t, lab):
    a, e = span(t, lab); return re.search(r'_transform" ref="([0-9a-f-]{36})"', t[a:e]).group(1)
def tf_vals(t, g):
    body = re.search(r'<instance guid="' + g + r'" type="LayerCompTransform"[^>]*>(.*?)</instance>', t, re.S).group(1)
    return [re.search(r'<field name="%s">([^<]*)' % k, body).group(1) for k in ('scaleU', 'scaleV', 'offsetU', 'offsetV', 'rotate')]

# painted panels + stripe
for lab, tex in TEX.items():
    a, e = span(s, lab); blk = s[a:e]
    blk = sub(blk, 'colorTexture', tex); blk = sub(blk, 'normalTexture', 'ref="null"'); blk = sub(blk, 'rsmTexture', 'ref="null"')
    blk = re.sub(r'(<field name="assetResolveRuleType">)\w+', r'\1AssetResolveRule_UseDefaults', blk, count=1)
    blk = re.sub(r'(<field name="TintMode">)\w+', r'\1LayerCompTintMode_WithValue', blk, count=1)
    blk = sub(blk, 'colorR', cv(1, 0, 0)); blk = sub(blk, 'colorG', cv(0, 1, 0)); blk = sub(blk, 'colorB', cv(0, 0, 1))
    srf = surf(0, 0.4, 0.35) if lab == 'Center Stripe' else surf(0, 0.4, 0.5)
    for ch in 'RGB': blk = sub(blk, 'rsm' + ch, srf)
    s = s[:a] + blk + s[e:]
    g = tf_of(s, lab); assert s.count('ref="%s"' % g) == 1, lab + ' transform shared'
    s = set_tf(s, g, (0.45, 1, 0, 0, 0) if lab == 'Center Stripe' else (1, 1, 0, 0, 0))
    print('layer', lab)
# shell ECU Purple
a, e = span(s, 'Helmet Shell'); s = s[:a] + sub(s[a:e], 'colorR', cv(0.03227, 0.01406, 0.05673)) + s[e:]   # v6: shell = the shared sky colour (make_cc_art.py prints it), so any sliver of shell at a seam matches the art
# back stickers + number = Black Pirate's
for lab in ('AAC  Decal', 'Flag', 'CJ2K Sticker', 'Warning Label'):
    g = tf_of(s, lab); assert s.count('ref="%s"' % g) == 1, lab
    v = tf_vals(b, tf_of(b, lab)); s = set_tf(s, g, v); print('sticker', lab, v)
k = b.index('<field name="backnumberoffset_scale">'); nb = re.findall(r'<field name="([xyzw])">([^<]*)', b[k:k + 300])[:4]
k = s.index('<field name="backnumberoffset_scale">'); seg = s[k:k + 300]
for c, v in nb: seg = re.sub(r'(<field name="%s">)[^<]*' % c, lambda x, v=v: x.group(1) + v, seg, count=1)
s = s[:k] + seg + s[k + 300:]; print('number', nb)
# v7 (user, City Connect only): back layout - no flag, number centered, CJ2K sticker where the number was (AAC's height).
a, e = span(s, 'Flag'); s = s[:a] + sub(s[a:e], 'colorTexture', 'ref="null"') + s[e:]
g = tf_of(s, 'CJ2K Sticker'); v = tf_vals(s, g); s = set_tf(s, g, (v[0], v[1], '0.1217', '0.03', v[4]))
# v7.1 (user): AAC and CJ2K closer to the number, equal gaps (~90 px in the zoomed back view; measured ~1554 px per offset unit)
g = tf_of(s, 'AAC  Decal'); v = tf_vals(s, g); s = set_tf(s, g, (v[0], v[1], '-0.1355', '0.03', v[4]))
k = s.index('<field name="backnumberoffset_scale">'); seg = re.sub(r'(<field name="x">)[^<]*', r'\g<1>0', s[k:k + 300], count=1); s = s[:k] + seg + s[k + 300:]
print('back: flag off, number x 0, CJ2K -> 0.180 / 0.03')
# v5 (user): no stripe - the two paintings meet in one shared colour along the crown and both centerlines.
a, e = span(s, 'Center Stripe'); s = s[:a] + sub(s[a:e], 'colorTexture', 'ref="null"') + s[e:]
print('Center Stripe: off')
# draw order: higher overlay number = drawn on top. The panels (8, 9) covered the stripe (5), flag (6) and warning label (7).
# Swap them with the bumper text layers (3, 4: bumper mesh only, no overlap) so the panels sit under everything on the shell.
SWAP = {'overlay_8': 'overlay_3', 'overlay_3': 'overlay_8', 'overlay_9': 'overlay_4', 'overlay_4': 'overlay_9'}
for k in SWAP: assert s.count('<field name="%s">' % k) == 1, k
s = re.sub(r'<field name="(overlay_[3489])">', lambda x: '<field name="%s">' % SWAP[x.group(1)], s)
print('slots: panels -> overlay_3/4 (under the stripe, flag, warning label); bumper text -> overlay_8/9')
s = s.replace('</partition>', ''.join(new) + '</partition>')
open(out, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(out); print('ok')
