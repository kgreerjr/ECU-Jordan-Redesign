# Jolly Roger helmet: replaces ECU_HELMET_2025_PURPLE_purpleFacemask.
# Phase 1 = colors only (charcoal shell/bumpers/chin, gold facemask); decals unchanged (gold skull) until we see the DDS.
import os, re, xml.etree.ElementTree as ET
R = os.environ.get('ECU_PROJECT_DIR', '.'); SRC = R + '/Backups/ECU helmets/Part items/ECU_HELMET_2025_PURPLE_purpleFacemask.xml'
OUT = R + '/Builds/Jolly Roger/Helmet'; os.makedirs(OUT, exist_ok=True)
t = open(SRC, encoding='utf-8-sig').read()
lin = lambda c: ((c/255 + 0.055)/1.055)**2.4 if c/255 > 0.04045 else c/255/12.92
CHAR = [round(lin(c), 7) for c in (0x40, 0x40, 0x44)]           # same charcoal as the jersey/pants
GOLD = [0.9734453, 0.462077, 0.0]                                  # ECU_Gold (linear)
def setcolor(t, guid, xyz):
    i = t.index('<instance guid="%s" type="ColorValue"' % guid); j = t.index('</instance>', i); seg = t[i:j]
    for k, v in zip('xyz', xyz): seg, c = re.subn(r'(<field name="%s">)[^<]*' % k, lambda m, v=v: m.group(1) + str(v), seg, 1); assert c == 1
    return t[:i] + seg + t[j:]
def label_block(t, label):
    i = t.index('<field name="label">%s</field>' % label); return t.rfind('<complex type="LayerCompMaterialInstance">', 0, i), i
def local_r(t, label):
    s, e = label_block(t, label); return re.search(r'colorR" ref="([0-9a-f-]{36})" />', t[s:e]).group(1)
log = []
shell = local_r(t, 'Helmet Shell')
for lab in ['Helmet Shell', 'Frontplates', 'Backplates']: t = setcolor(t, local_r(t, lab), CHAR); log.append('%-13s -> charcoal' % lab)
for lab in ['Chin Guard', 'Chin Straps']:                          # were ECU_Purple -> point at the shell's charcoal ColorValue
    s, e = label_block(t, lab); seg, c = re.subn(r'<field name="colorR" ref="[^"]*" partitionGuid="[^"]*" />', lambda m: '<field name="colorR" ref="%s" />' % shell, t[s:e], 1); assert c == 1
    t = t[:s] + seg + t[e:]; log.append('%-13s -> charcoal' % lab)
# ---- phase 2: near-black hardware (bumpers, chin) like the concept; BLA skull (purple hat) on the sides; serif "ECU" on the back bumper ----
BLK = [round(lin(c), 7) for c in (0x1C, 0x1C, 0x1E)]
for lab in ['Frontplates', 'Backplates']: t = setcolor(t, local_r(t, lab), BLK); log.append('%-13s -> near-black' % lab)
bg = local_r(t, 'Backplates')
for lab in ['Chin Guard', 'Chin Straps']:
    s, e = label_block(t, lab); seg, c = re.subn(r'<field name="colorR" ref="[^"]*" />', lambda m: '<field name="colorR" ref="%s" />' % bg, t[s:e], 1); assert c == 1; t = t[:s] + seg + t[e:]; log.append('%-13s -> near-black' % lab)
JRD = R + '/Dup IDs/Alt dup IDs/'
def idref(name):
    x = open(JRD + name + '.xml', encoding='utf-8-sig').read(); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
    return 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pg.group(2), pg.group(1))
def teamref(name): return re.search(r'ref="[^"]*/%s\\\\[^"]*" partitionGuid="[^"]*"' % name, t).group(0)
def overlay(t, label):
    i = t.index('<field name="label">%s</field>' % label); return t.rfind('<complex type="LayerCompOverlayInstance">', 0, i), i
def set_field(seg, fld, val):   # val = 'ref=... partitionGuid=...' or 'ref="null"'
    seg, c = re.subn(r'<field name="%s" ref="[^"]*"( partitionGuid="[^"]*")? />' % fld, lambda m: '<field name="%s" %s />' % (fld, val), seg, 1); assert c == 1, fld; return seg
have = lambda n: os.path.exists(JRD + n + '.xml')
JR_ALT_LOGO = False; JR_LOGO_SCALE = '0.45'   # alt logo on helmet tried 2026-11-12 (needed scale 0.45 to read) - user preferred ECU's BLA skull -> off
#  # False = ECU's BLA skull (import ECU_Helmet_2021_BLA_Decal_col.dds into ECU_JR_Helmet_Skull_col instead of the alt-logo PNG)
if have('ECU_JR_Helmet_Skull_col') and have('ECU_JR_Helmet_Skull_norm'):
    GOLD_R, WHITE_R, PUR_R = teamref('ECU_Gold'), teamref('global_whiteHelmet'), teamref('ECU_Purple')
    for lab in ['Right Side Logo', 'Left Side Logo']:
        s, e = overlay(t, lab); seg = set_field(t[s:e], 'colorTexture', idref('ECU_JR_Helmet_Skull_col')); seg = set_field(seg, 'normalTexture', idref('ECU_JR_Helmet_Skull_norm'))
        for ch, v in (('R', GOLD_R), ('G', WHITE_R), ('B', PUR_R)): seg = set_field(seg, 'color' + ch, v)
        if JR_ALT_LOGO:   # v2: the user's full-color Jolly Roger logo, repainted into ECU_JR_Helmet_Skull_col (only this helmet uses it)
            seg = set_field(seg, 'normalTexture', 'ref="null"'); seg = re.sub(r'<field name="assetResolveRuleType">[^<]*', '<field name="assetResolveRuleType">AssetResolveRule_UseDefaults', seg, 1)
        t = t[:s] + seg + t[e:]; log.append('%-15s -> %s' % (lab, 'Jolly Roger alt logo (pre-colored, UseDefaults)' if JR_ALT_LOGO else 'BLA skull: gold outline/ECU, white skull, purple hat'))
        if JR_ALT_LOGO:   # decal size = overlay_transform scaleU/scaleV (+ scaledTransform x/y). Stock 0.35 here (Treasure Island's 2021 helmet: 0.40/0.43)
            g = re.search(r'<field name="overlay_transform" ref="([0-9a-f-]{36})" />', t[s:t.index('</complex>', e)]).group(1)
            k = t.index('<instance guid="%s"' % g); m = t.index('</instance>', k); inst = t[k:m]
            inst = re.sub(r'(<field name="scale[UV]">)[^<]*', lambda mm: mm.group(1) + JR_LOGO_SCALE, inst)
            inst = re.sub(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda mm: mm.group(1) + JR_LOGO_SCALE + mm.group(2) + JR_LOGO_SCALE, inst, 1)
            t = t[:k] + inst + t[m:]
if have('ECU_JR_Helmet_BackECU_col'):
    for lab in ['Backplate', 'Backplate_X1']:
        s, e = overlay(t, lab); seg = set_field(t[s:e], 'colorTexture', idref('ECU_JR_Helmet_BackECU_col'))
        seg = set_field(seg, 'normalTexture', 'ref="null"'); seg = set_field(seg, 'rsmTexture', 'ref="null"')   # old norm/rsm would emboss "EAST CAROLINA"
        t = t[:s] + seg + t[e:]; log.append('%-15s -> gold "ECU"' % lab)
if have('ECU_JR_Helmet_Stripe_col'):   # center stripe: copy PURPLETEXT's five-stripe overlay (+ its local rsm/transform instances), texture -> our dup
    PT = open(R + '/Backups/ECU helmets/Part items/ECU_HELMET_2025_PURPLETEXT.xml', encoding='utf-8-sig').read()
    def ov5(x): s = x.index('<field name="overlay_5">'); e = x.index('</field>', x.index('<field name="overlay_blend">', s)); e = x.index('</field>', x.index('</complex>', e)) ; return s, e
    s1, e1 = ov5(PT); blk = PT[s1:e1]
    blk = re.sub(r'<field name="(colorTexture|rsmTexture)" ref="[^"]*FiveStripe_02_col[^"]*" partitionGuid="[^"]*" />', lambda m: '<field name="%s" %s />' % (m.group(1), idref('ECU_JR_Helmet_Stripe_col')), blk)
    G2, P2 = teamref('ECU_Gold'), teamref('ECU_Purple')
    for ch, v in (('R', G2), ('G', G2), ('B', P2)): blk = re.sub(r'<field name="color%s" ref="[^"]*"( partitionGuid="[^"]*")? />' % ch, lambda m, ch=ch, v=v: '<field name="color%s" %s />' % (ch, v), blk, 1)
    for g in set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', blk)):          # bring the local instances along
        assert g not in t, g; i = PT.index('<instance guid="%s"' % g); inst = PT[i:PT.index('</instance>', i) + len('</instance>')]
        assert not re.search(r'ref="[0-9a-f]{8}-[0-9a-f-]{27}"', inst), 'nested local ref'; t = t.replace('</partition>', '\t' + inst + '\n</partition>')
    s2, e2 = ov5(t); assert '>Center Stripe<' in t[s2:e2]; t = t[:s2] + blk + t[e2:]; log.append('Center Stripe   -> gold / purple / gold five-stripe')
    i = t.index('<instance guid="0ccb5483-8f45-465c-a070-d44e2944a9c1"'); j = t.index('</instance>', i)   # stripe transform: offsetV -0.28 cut it off above the rear sticker
    seg = re.sub(r'(<field name="w">)[^<]*', r'\g<1>0', t[i:j], 1); seg = re.sub(r'(<field name="offsetV">)[^<]*', r'\g<1>0', seg, 1); t = t[:i] + seg + t[j:]; log.append('Center Stripe   -> full length (offsetV 0)')
# ---- matte shell: borrow the finish Troy's MATTEBLACK helmet uses (Kansas black preset), by name like the Arkansas one it replaces ----
for old, new in (('ARK_HELMET_2021_RED_preset<', 'KU_HELMET_2021_BLACK_preset<'), ('ARK_HELMET_2021_RED_preset_ES_appearance<', 'KU_HELMET_2021_BLACK_preset_ES_appearance<')):
    assert t.count('>' + old) == 1, old; t = t.replace('>' + old, '>' + new); log.append('shell finish    -> ' + new[:-1])
fm = re.search(r'<field name="faceMaskColor" ref="([0-9a-f-]{36})" />', t).group(1); t = setcolor(t, fm, GOLD); log.append('facemask      -> gold')
# 5.2 (user): back number moved beside the stripe (it sat on the gold/purple stripe) and colored like the AAC logo: gold fill, white outline
NUM_X, NUM_Y = '0.246', '-0.081'   # backnumberoffset_scale x/y (stock 0.005 / -0.153 = centered, low on the stripe). 0.16 moved it ~half a number width; target = mirror of the AAC logo (left side, mid-height)
k = t.index('<field name="backnumberoffset_scale">'); seg, c = re.subn(r'(<field name="x">)[^<]*', lambda m: m.group(1) + NUM_X, t[k:k + 250], 1); seg, c2 = re.subn(r'(<field name="y">)[^<]*', lambda m: m.group(1) + NUM_Y, seg, 1); assert c == c2 == 1; t = t[:k] + seg + t[k + 250:]
k = t.index('ECU_Jersey_2021_NUM_Array'); s_ = t.rfind('<field name="textures">', 0, k); e_ = t.index('<field name="info">', k)
seg, c1 = re.subn(r'<field name="colorR" ref="[^"]*"( partitionGuid="[^"]*")? />', lambda m: '<field name="colorR" %s />' % teamref('ECU_Gold'), t[s_:e_], 1)
seg, c2 = re.subn(r'<field name="colorG" ref="[^"]*"( partitionGuid="[^"]*")? />', lambda m: '<field name="colorG" %s />' % teamref('global_whiteHelmet'), seg, 1); assert c1 == c2 == 1; t = t[:s_] + seg + t[e_:]
log.append('back number   -> beside the stripe (x %s, y %s), gold fill + white outline like the AAC logo' % (NUM_X, NUM_Y))
p = OUT + '/ECU_HELMET_2025_PURPLE_purpleFacemask.xml'; open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p)
assert not re.search(r'ref="[^"\\]+\\[0-9a-f]', t.replace('\\\\', '')), 'single-backslash ref'
print('\n'.join(log)); print('written', p)
