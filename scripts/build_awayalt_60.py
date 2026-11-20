"""Away Alternate (6.0) after the white/gold reference jersey.
helmet  : back bumper EAST CAROLINA -> ECU (the ECU bumper art the front already loads), purple / gold / white like the jersey.
jersey  : gold collar + cuffs, sleeve stripes off, collar patches off, ECU chest wordmark (ECU_AA_WM_* dups),
          purple/white skull & crossbones on both sleeves (ECU_AA_Skull_col dup, Ghost Ship's two sleeve-decal layers).
          Numbers already purple with a gold outline.
usage: build_awayalt_60.py helmet <ECU_HELMET_2021_AWAYOPT.xml in/out>
       build_awayalt_60.py jersey <ECU_JERSEY_2026_AWAYOPT.xml in/out> <Ghost jersey xml> <dup export dir> [skull scale]"""
import re, sys, uuid, xml.etree.ElementTree as ET

T = 'content/characters/player/parts/uniforms/helmets/decals/teams/'
TC = 'content/characters/player/parts/uniforms/team_colors/'
RC = 'ContentShared/characters/player/parts/uniforms/recipe/colors/'
FRONT_ECU = f'ref="{T}ECU_Bumper_Front_ECU_col\\\\d1712d23-f81c-2b1c-d24b-5772dcf9d7ca" partitionGuid="2e5c64a0-48c3-4a96-823f-55d89244f156"'
GOLD   = f'ref="{TC}ECU_Gold\\\\7b0ba81a-2b4a-4470-9dfd-058c0e4d7a90" partitionGuid="a26c629e-6152-4001-9d0b-dd4442f6bc7c"'
PURPLE = f'ref="{TC}ECU_Purple\\\\46d33457-94a7-4c4c-8f0c-d4ddd7113d71" partitionGuid="c76ded6f-7cf2-4520-a156-522e523c721e"'
WHITE_H = f'ref="{RC}global_whiteHelmet\\\\fc247258-b15a-4094-b541-6add49a910ff" partitionGuid="be62a1d8-5761-436e-8486-d6c2be0f7e33"'
WHITE  = f'ref="{RC}global_white\\\\40cdde98-1c5a-460c-b245-6d8d6903e422" partitionGuid="3c4ccc13-726b-4ac6-9fe1-3e25c50c8afd"'
NULL = 'ref="null"'

rd = lambda p: open(p, encoding='utf-8-sig').read()
def wr(p, t): open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p); print('wrote', p)

def layer_span(s, label):
    m = re.search(r'<field name="label">' + re.escape(label) + r'</field>', s); assert m, label
    st = s.rfind('<complex type="LayerCompOverlayInstance">', 0, m.start())
    en = re.search(r'<field name="overlay_transform" ref="[^"]*" />', s[m.end():]).end() + m.end()
    return st, en
def spans(s, label):
    out = []; i = 0
    while True:
        m = re.search(r'<field name="label">' + re.escape(label) + r'</field>', s[i:])
        if not m: return out
        a = s.rfind('<complex type="LayerCompOverlayInstance">', 0, i + m.start())
        e = re.search(r'<field name="overlay_transform" ref="[^"]*" />', s[i + m.end():]).end() + i + m.end()
        out.append((a, e)); i = e
def sub_field(blk, name, newref):
    new, n = re.subn(r'(<field name="' + name + r'" )ref="[^"]*"(?: partitionGuid="[^"]*")?', lambda mm: mm.group(1) + newref, blk, count=1)
    assert n == 1, name; return new
def set_transform(s, blk, vals):
    g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', blk).group(1); assert s.count('ref="%s"' % g) == 1
    m = re.search(r'(<instance guid="' + g + r'"[^>]*>)(.*?)(</instance>)', s, re.S); body = m.group(2)
    su, sv, ou, ov = vals
    for k, v in (('scaleU', su), ('scaleV', sv), ('offsetU', ou), ('offsetV', ov), ('x', su), ('y', sv), ('z', ou), ('w', ov)):
        body = re.sub(r'(<field name="' + k + r'">)[-\d.eE]+(</field>)', lambda mm: f'{mm.group(1)}{v}{mm.group(2)}', body, count=1)
    return s[:m.start(2)] + body + s[m.end(2):]
def edit(s, label, **f):
    a, b = layer_span(s, label); blk = s[a:b]
    for k, v in f.items(): blk = sub_field(blk, k, v)
    return s[:a] + blk + s[b:]
def idref(xml):
    x = rd(xml); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
    return 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pg.group(2), pg.group(1))

mode = sys.argv[1]
if mode == 'helmet':
    p = sys.argv[2]; s = rd(p)
    # ECU art on the back. Front plate runs it at 0.45 x 0.45; the back layers scale by the same ratio
    # EAST CAROLINA needed (X1 0.45 x 0.7 vs Backplate 0.76 x 0.9), offsets kept.
    for lab, tf in (('Backplate_X1', (0.45, 0.45, 0, 0)), ('Backplate', (0.76, 0.5786, 0, -0.03))):
        s = edit(s, lab, colorTexture=FRONT_ECU, rsmTexture=FRONT_ECU, normalTexture=NULL, colorR=PURPLE, colorG=GOLD, colorB=WHITE_H)
        a, b = layer_span(s, lab); s = set_transform(s, s[a:b], tf)
    wr(p, s)

elif mode == 'jersey':
    J, G, DUP = sys.argv[2:5]; SC = sys.argv[5] if len(sys.argv) > 5 else '0.24'
    s, g = rd(J), rd(G)
    if 'AA Skull' in s: raise SystemExit('already built')
    WM_COL, WM_NORM, WM_RSM = (idref(f'{DUP}/ECU_AA_WM_{k}.xml') for k in ('col', 'norm', 'rsm'))
    SKULL = idref(f'{DUP}/ECU_AA_Skull_col.xml')
    # trim: gold collar + cuffs; sleeve stripes and collar patches off
    s = edit(s, 'Collar Stripe', colorR=GOLD)
    s = edit(s, 'Sleeve Cuff Stripe', colorR=GOLD)
    for lab in ('Stripe 1', 'Stripe 2', 'Gold Stripe'):
        s = edit(s, lab, colorTexture=NULL, normalTexture=NULL)
    for a, b in reversed(spans(s, 'Collar Patch')):
        blk = s[a:b]
        for k in ('colorTexture', 'rsmTexture', 'normalTexture'): blk = sub_field(blk, k, NULL)
        s = s[:a] + blk + s[b:]
    # ECU chest wordmark: purple fill, gold outline, white outer outline; Home's PIRATES box
    s = edit(s, 'ECU Logo', colorTexture=WM_COL, normalTexture=WM_NORM, rsmTexture=WM_RSM, colorR=PURPLE, colorG=GOLD, colorB=WHITE)
    a, b = layer_span(s, 'ECU Logo'); s = set_transform(s, s[a:b], (0.16, 0.15, 0, -0.163))
    # sleeve skulls: copy Ghost Ship's two sleeve-decal layers into two empty overlay slots
    def ov_span(t, slot):
        a = t.index('<field name="%s">' % slot); e = t.index('</field>', t.index('<field name="overlay_blend">', a)); e = t.index('</field>', t.index('</complex>', e)); return a, e
    def slot_of(t, lab):
        i = t.index('<field name="label">%s' % lab); return re.findall(r'<field name="(overlay_\d+)">', t[:i])[-1]
    free = [m for m in ('overlay_16', 'overlay_17', 'overlay_18', 'overlay_19', 'overlay_20')
            if 'colorTexture" ref="null"' in s[slice(*ov_span(s, m))] and not re.search(r'<field name="label">[^<]+</field>', s[slice(*ov_span(s, m))])]
    assert len(free) >= 2, free
    new = []
    for lab, dst in (('Sleeve Decals - Standard', free[0]), ('Sleeve Decals - Long', free[1])):
        src = slot_of(g, lab); a, e = ov_span(g, src); blk = g[a:e].replace('<field name="%s">' % src, '<field name="%s">' % dst, 1)
        blk = sub_field(blk, 'colorTexture', SKULL)
        blk = sub_field(blk, 'normalTexture', NULL); blk = sub_field(blk, 'rsmTexture', NULL)
        blk = sub_field(blk, 'colorR', WHITE); blk = sub_field(blk, 'colorG', PURPLE); blk = sub_field(blk, 'colorB', NULL)
        blk = re.sub(r'(<field name="label">)Sleeve Decals[^<]*', lambda m: m.group(1) + 'AA Skull ' + ('(standard sleeves)' if 'Standard' in lab else '(long sleeves)'), blk, count=1)
        for old in set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', blk)):       # own copy of the local transform
            k = g.index('<instance guid="%s"' % old); inst = g[k:g.index('</instance>', k) + len('</instance>')]; ng = str(uuid.uuid4())
            if 'LayerCompTransform' in inst:
                for f in ('scaleU', 'scaleV'): inst = re.sub(r'(<field name="%s">)[^<]*' % f, lambda m: m.group(1) + SC, inst, count=1)
                inst = re.sub(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda m: m.group(1) + SC + m.group(2) + SC, inst, count=1)
            new.append('\t' + inst.replace(old, ng) + '\n'); blk = blk.replace(old, ng)
        c, d = ov_span(s, dst); s = s[:c] + blk + s[d:]; print(lab, '->', dst)
    s = s.replace('</partition>', ''.join(new) + '</partition>')
    wr(J, s)

elif mode == 'sleeve':
    # in game the sleeve-decal UV layout isn't loaded for this jersey (bundle rule): point both skull layers at
    # ECU_AA_UVSet_sleeveDecal (dup of sleeveStripesMirrored holding the sleeve-decal layout, FLOAT16) and set the size.
    J, UVX = sys.argv[2:4]; SC = float(sys.argv[4]) if len(sys.argv) > 4 else 0.21
    s = rd(J); UV = idref(UVX)
    for lab in ('AA Skull (standard sleeves)', 'AA Skull (long sleeves)'):
        a, b = layer_span(s, lab); blk = sub_field(s[a:b], 'layoutTexture', UV); s = s[:a] + blk + s[b:]
        g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', blk).group(1)
        m = re.search(r'(<instance guid="' + g + r'"[^>]*>)(.*?)(</instance>)', s, re.S); body = m.group(2)
        for k in ('scaleU', 'scaleV'): body = re.sub(r'(<field name="%s">)[^<]*' % k, lambda mm: mm.group(1) + str(SC), body, count=1)
        body = re.sub(r'(<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda mm: mm.group(1) + str(SC) + mm.group(2) + str(SC), body, count=1)
        s = s[:m.start(2)] + body + s[m.end(2):]
    wr(J, s)

elif mode == 'skullpos':
    # nudge both skull layers by a delta (each keeps its own base: standard V -0.012, long V 0.347):
    # build_awayalt_60.py skullpos <jersey xml> <dU> <dV>   (scaledTransform z/w kept in sync)
    J, DU, DV = sys.argv[2], float(sys.argv[3]), float(sys.argv[4]); s = rd(J)
    for lab in ('AA Skull (standard sleeves)', 'AA Skull (long sleeves)'):
        a, b = layer_span(s, lab)
        g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', s[a:b]).group(1)
        m = re.search(r'(<instance guid="' + g + r'"[^>]*>)(.*?)(</instance>)', s, re.S); body = m.group(2)
        ou = round(float(re.search(r'name="offsetU">([^<]+)', body).group(1)) + DU, 4)
        ov = round(float(re.search(r'name="offsetV">([^<]+)', body).group(1)) + DV, 4)
        for k, v in (('offsetU', ou), ('offsetV', ov), ('z', ou), ('w', ov)):
            body = re.sub(r'(<field name="%s">)[^<]*' % k, lambda mm: mm.group(1) + str(v), body, count=1)
        s = s[:m.start(2)] + body + s[m.end(2):]
        print(lab, 'offset', ou, ov)
    wr(J, s)

elif mode == 'goldhelmet':
    # Away Alternate helmet v2 (user, 2026-11-17): satin ECU-gold shell, white facemask / bumpers / chin parts,
    # Away's exact "Pirates" script in purple with a white outline (G = fill, R = outline in that art),
    # narrow purple | white | purple stripe, back number purple / white, ECU bumpers purple / gold / white.
    # build_awayalt_60.py goldhelmet <AWAYOPT helmet xml in/out> <WHITESCRIPT helmet xml> <dup export dir>
    H, WSX, DUP = sys.argv[2:5]; s, ws = rd(H), rd(WSX)
    SCRIPT, SCRIPT_N, STRIPE = (idref(f'{DUP}/{n}.xml') for n in ('ECU_AA_Helmet_Script_col', 'ECU_AA_Helmet_Script_norm', 'ECU_AA_Helmet_Stripe_col'))
    # 1) side logos: Away's two layers (script placement + its surface), then our textures / colours
    def ov_span(t, slot):
        a = t.index('<field name="%s">' % slot); e = t.index('</field>', t.index('<field name="overlay_blend">', a)); e = t.index('</field>', t.index('</complex>', e)); return a, e
    def slot_of(t, lab):
        i = t.index('<field name="label">%s</field>' % lab); return re.findall(r'<field name="(overlay_\d+)">', t[:i])[-1]
    new = []
    for lab in ('Right Side Logo', 'Left Side Logo'):
        src, dst = slot_of(ws, lab), slot_of(s, lab); a, e = ov_span(ws, src); blk = ws[a:e].replace('<field name="%s">' % src, '<field name="%s">' % dst, 1)
        for old in set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', blk)):
            k = ws.index('<instance guid="%s"' % old); inst = ws[k:ws.index('</instance>', k) + len('</instance>')]; ng = str(uuid.uuid4())
            new.append('\t' + inst.replace(old, ng) + '\n'); blk = blk.replace(old, ng)
        blk = sub_field(blk, 'colorTexture', SCRIPT); blk = sub_field(blk, 'normalTexture', SCRIPT_N)
        blk = sub_field(blk, 'colorR', WHITE_H); blk = sub_field(blk, 'colorG', PURPLE); blk = sub_field(blk, 'colorB', PURPLE)
        c, d = ov_span(s, dst); s = s[:c] + blk + s[d:]
    s = s.replace('</partition>', ''.join(new) + '</partition>')
    # 2) stripe
    s = edit(s, 'Center Stripe', colorTexture=STRIPE, colorR=WHITE_H, colorG=PURPLE, colorB=GOLD)
    # 3) bumper ECUs purple / gold / white (front too, until the front gets its own idea)
    for lab in ('Frontplate', 'Frontplate_Schutt', 'Backplate', 'Backplate_X1'):
        s = edit(s, lab, colorR=PURPLE, colorG=GOLD, colorB=WHITE_H)
    # 4) back stickers like Away (made for a light shell)
    s = edit(s, 'AAC  Decal', colorR=PURPLE, colorG=WHITE_H, colorB=GOLD)
    s = edit(s, 'Warning Label', colorR=PURPLE, colorG=PURPLE)
    # 5) materials: gold shell, white bumpers / chin guard / chin straps
    def mat(t, lab, ref):
        i = t.index('<field name="label">%s</field>' % lab); a = t.rfind('<complex type="LayerCompMaterialInstance">', 0, i)
        return t[:a] + sub_field(t[a:i], 'colorR', ref) + t[i:]
    s = mat(s, 'Helmet Shell', GOLD)
    for lab in ('Frontplates', 'Backplates', 'Chin Guard', 'Chin Straps'): s = mat(s, lab, WHITE_H)
    # 6) satin finish: back to the stock ECU black-helmet shell preset (satin ES parent) from Black Pirate's matte KU one
    for old, nw in (('KU_HELMET_2021_BLACK_preset', 'ECU_HELMET_2021_BLACK_preset'), ('KU_HELMET_2021_BLACK_preset_ES_appearance', 'ECU_HELMET_2021_BLACK_preset_ES_appearance')):
        assert s.count('>%s<' % old) == 1, old; s = s.replace('>%s<' % old, '>%s<' % nw)
    # 7) white facemask
    s, n = re.subn(r'(<field name="faceMaskColor" )ref="[^"]*"(?: partitionGuid="[^"]*")?', lambda m: m.group(1) + WHITE_H, s, count=1); assert n == 1
    # 8) back number: purple fill, white outline
    m = re.search(r'(<field name="number" ref=")([0-9a-f-]{36})"', s); g = m.group(2)
    k = s.index('<instance guid="%s"' % g); e = s.index('</instance>', k); seg = s[k:e]
    seg = sub_field(seg, 'colorR', PURPLE); seg = sub_field(seg, 'colorG', WHITE_H); s = s[:k] + seg + s[e:]
    wr(H, s)

elif mode == 'goldpants':
    # Away Alternate pants v2 (user, 2026-11-17): ECU-gold pants (like Home's), narrow purple | white | purple stripe
    # (ECU_AA_Pants_Stripe_col dup), the purple/white sleeve skull on the hip (ECU_AA_Skull_col is a dup of the hip
    # logo's own texture, ECU_Decal_2021_02_col), Home's purple-on-gold Jumpman.
    # build_awayalt_60.py goldpants <AWAYOPT pants xml in/out> <YELLOW (Home) pants xml> <dup export dir>
    P, YX, DUP = sys.argv[2:5]; s, y = rd(P), rd(YX)
    STRIPE, SKULL = idref(f'{DUP}/ECU_AA_Pants_Stripe_col.xml'), idref(f'{DUP}/ECU_AA_Skull_col.xml')
    WHITE_F = re.search(r'ref="[^"]*/global_white\\\\[^"]*" partitionGuid="[^"]*"', y).group(0)
    def mat(t, lab, ref):
        i = t.index('<field name="label">%s</field>' % lab); a = t.rfind('<complex type="LayerCompMaterialInstance">', 0, i)
        return t[:a] + sub_field(t[a:i], 'colorR', ref) + t[i:]
    for lab in ('Adidas Base Fabric', 'AdidasHoles'): s = mat(s, lab, GOLD)
    s = edit(s, 'Stripe', colorTexture=STRIPE, normalTexture=NULL, colorR=WHITE_F, colorG=PURPLE, colorB=GOLD)
    s = edit(s, 'Logo ECU', colorTexture=SKULL, normalTexture=NULL, rsmTexture=NULL, colorR=WHITE_F, colorG=PURPLE, colorB=NULL)
    # Jumpman: Home gold pants' layer (texture + its own colour instances)
    def ov_span(t, slot):
        a = t.index('<field name="%s">' % slot); e = t.index('</field>', t.index('<field name="overlay_blend">', a)); e = t.index('</field>', t.index('</complex>', e)); return a, e
    def slot_of(t, lab):
        i = t.index('<field name="label">%s</field>' % lab); return re.findall(r'<field name="(overlay_\d+)">', t[:i])[-1]
    src, dst = slot_of(y, 'Jumpman Logo'), slot_of(s, 'Jumpman Logo'); a, e = ov_span(y, src); blk = y[a:e].replace('<field name="%s">' % src, '<field name="%s">' % dst, 1)
    new = []
    for old in set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', blk)):
        k = y.index('<instance guid="%s"' % old); inst = y[k:y.index('</instance>', k) + len('</instance>')]; ng = str(uuid.uuid4())
        new.append('\t' + inst.replace(old, ng) + '\n'); blk = blk.replace(old, ng)
    c, d = ov_span(s, dst); s = s[:c] + blk + s[d:]
    s = s.replace('</partition>', ''.join(new) + '</partition>')
    wr(P, s)

elif mode == 'goldtune':
    # v2 tweaks (user): stickers + back number closer to the narrow stripe (same stripe-to-sticker gap as the
    # triple-stripe helmets: measured ~114-119 px on the user's back view at ~1600 px per sticker-offset unit and
    # ~880 px per back-number unit), back-bumper ECU 60% of v1.
    H = sys.argv[2]; s = rd(H); DU = 0.07
    def tf(t, lab):
        i = t.index('<field name="label">%s</field>' % lab); g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', t[i:]).group(1)
        m = re.search(r'(<instance guid="' + g + r'"[^>]*>)(.*?)(</instance>)', t, re.S); return m
    def setf(t, m, vals):
        body = m.group(2)
        for k, v in vals.items(): body = re.sub(r'(<field name="%s">)[^<]*' % k, lambda mm: mm.group(1) + str(v), body, count=1)
        return t[:m.start(2)] + body + t[m.end(2):]
    for lab in ('Flag', 'AAC  Decal', 'CJ2K Sticker', 'Warning Label'):
        m = tf(s, lab); u = float(re.search(r'name="offsetU">([^<]+)', m.group(2)).group(1))
        nu = round(u - DU if u > 0 else u + DU, 4)
        # v3 pixel check against Away's back view: AAC +0.008, CJ2K -0.003, warning label to Away's 7 px from the number
        nu = {'Flag': -0.105, 'AAC  Decal': -0.111, 'CJ2K Sticker': 0.101, 'Warning Label': 0.349}.get(lab, nu)   # v4: every sticker ~44 px from the stripe on the user's back view (was flag 40 / AAC 28 | CJ2K 54 / number 55)   # label: back to stock 0.349 (0.255 overlapped the number)
        s = setf(s, m, {'offsetU': nu, 'z': nu}); print(lab, u, '->', nu)
    s, n = re.subn(r'(<field name="backnumberoffset_scale">\s*<complex type="Vec4">\s*<field name="x">)[^<]*', lambda mm: mm.group(1) + '0.176', s, count=1); assert n == 1
    for lab, (su, sv) in (('Backplate_X1', (0.27, 0.27)), ('Backplate', (0.456, 0.3472))):
        m = tf(s, lab); s = setf(s, m, {'scaleU': su, 'scaleV': sv, 'x': su, 'y': sv})
    wr(H, s)

elif mode == 'goldbumper':
    # back bumper = the jersey's chest ECU (ECU_AA_Bumper_Back_ECU_col, dup of ECU_Helmet_2021_BackLogo = the stock
    # Blackout back-bumper texture; art from make_aa_bumper_ecu.py in the Bumper_ECU art box): R fill purple, G gold, B white
    H, DUP = sys.argv[2:4]; s = rd(H); ECU2 = idref(f'{DUP}/ECU_AA_Bumper_Back_ECU_col.xml')
    for lab in ('Backplate', 'Backplate_X1'):
        s = edit(s, lab, colorTexture=ECU2, rsmTexture=NULL, colorR=PURPLE, colorG=GOLD, colorB=WHITE_H)
    wr(H, s)

elif mode == 'goldfront':
    # front bumper = the sleeve/hip skull, purple + white (ECU_AA_Bumper_Front_Skull_col, dup of
    # ECU_Helmet_2021_WHI_FrontLogo_col = what the front ECU dup came from; art from make_aa_bumper_skull.py): R white, G purple
    H, DUP = sys.argv[2:4]; s = rd(H); SK = idref(f'{DUP}/ECU_AA_Bumper_Front_Skull_col.xml')
    for lab in ('Frontplate', 'Frontplate_Schutt'):
        s = edit(s, lab, colorTexture=SK, rsmTexture=NULL, normalTexture=NULL, colorR=WHITE_H, colorG=PURPLE, colorB=NULL)
    wr(H, s)

elif mode == 'font':
    # reference-jersey number font (make_aa_numbers.py) on the jersey and the helmet back number, each through a dup of
    # the array that piece already loads: ECU_AA_NUM_Array (dup of ECU_Jersey_2023_NUM_Array) on the jersey,
    # ECU_AA_Helmet_NUM_Array (dup of CMU_Jersey_2021_NUM_Array, like ECU_Block_NUM_Array_B) on the helmet.
    # build_awayalt_60.py font <jersey xml> <helmet xml> <dup export dir>
    J, H, DUP = sys.argv[2:5]
    for path, old, new in ((J, 'ECU_Jersey_2023_NUM_Array', 'ECU_AA_NUM_Array'), (H, 'ECU_Block_NUM_Array_B', 'ECU_AA_Helmet_NUM_Array')):
        s = rd(path); NEW = idref(f'{DUP}/{new}.xml')
        s, n = re.subn(r'ref="[^"]*/%s\\\\[^"]*" partitionGuid="[^"]*"' % old, lambda m: NEW, s); assert n >= 1, (path, old)
        print(path.split('/')[-1], old, '->', new, n, 'refs'); wr(path, s)
