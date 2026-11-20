# 5.4 (ITEM 4): every ECU helmet's back number sits opposite the AAC logo (Jolly Roger layout: x 0.21, y -0.06 in
# backnumberoffset_scale; AAC is at overlay offsetU -0.16 on every ECU helmet) and is colored like its uniform's numbers
# (R = fill, G = outline). Fonts unchanged (each helmet keeps the number texture its bundle loads).
# Run AFTER the per-uniform helmet builders: it post-processes FINAL/Helmets in place (idempotent), adding the
# stock helmets that no build touches. Jolly Roger already has this layout (build_jolly_roger_helmet.py) and is skipped.
import os, re, uuid, xml.etree.ElementTree as ET
R = os.environ.get('ECU_PROJECT_DIR', '.'); FIN = R + '/FINAL/Helmets/'; STOCK = R + '/Backups/ECU helmets/Part items/'
X, Y = '0.246', '-0.081'
NZ, NW = '6.35', '4.12'   # number scale (stock 9.231635 / 6). TEST: assumed divisor (smaller = bigger number), /1.6 to match the AAC logo's height   # v2 (user 'down a tad'): was -0.06
FLAG_U, FLAG_V = '-0.1395', '0.274'   # flag overlay offset (stock 0 / 0.36-0.389 = on the stripe). v2 (user): above the AAC logo (AAC at -0.16 / 0.07); CJ2K sticker mirrors it at +0.16 / 0.30 above the number
lin = lambda c: ((c/255 + 0.055)/1.055)**2.4 if c/255 > 0.04045 else c/255/12.92
PLAN = {   # helmet: (fill, outline, why)  - names = team/global color assets, '#hex' = new ColorValue, None = keep current tint
 'ECU_HELMET_2025_PURPLE_yellowFacemask': ('global_whiteHelmet', 'ECU_Gold',   'Home: Purple Jersey numbers white / gold'),
 'ECU_HELMET_2021_PURPLE_yellowFacemask': ('global_whiteHelmet', 'ECU_Gold',   'Home Option: Purple Jersey numbers'),
 'ECU_HELMET_2021_WHITESCRIPT':           ('ECU_Purple',         'ECU_Gold',   'Away: White Jersey numbers purple / gold'),
 'ECU_HELMET_2021_BLACKOUT':              ('global_whiteHelmet', 'ECU_Purple', 'Black Pirate: Black Jersey numbers white / purple '),
 'ECU_HELMET_2021_AWAYOPT':               ('global_whiteHelmet', 'ECU_Purple', 'Away Option: own copy of the Blackout helmet (6.0)'),
 'ECU_HELMET_2021_WHITE':                 (None, None,                         'Treasure Island: keep gunmetal / gold (gold fill vanishes on the gold shell)'),
 'ECU_HELMET_2026_GHOST':                 (None, None,                         'Ghost Ship: already gray / lavender'),
 'ECU_HELMET_2025_PURPLESCRIPT':          ('global_whiteHelmet', 'ECU_Gold',   'purple helmet: Home style'),
 'ECU_HELMET_2025_PURPLETEXT':            ('global_whiteHelmet', 'ECU_Gold',   'Throwback Purple: Home style (stock gold / white)'),
 'ECU_HELMET_2025_WHITEUSA':              ('ECU_Purple',         'ECU_Gold',   'white helmet: Away style'),
 'ECU_HELMET_2021_WHITE_yellowFacemask':  ('ECU_Purple',         'ECU_Gold',   'white helmet: Away style'),
 'ECU_HELMET_2025_WHITE_blackfacemask':   ('ECU_Purple',         'ECU_Gold',   'white helmet: Away style'),
 'ECU_HELMET_2021_BLACKSCRIPT':           ('global_whiteHelmet', 'ECU_Purple', 'black helmet: Black Pirate style'),
}
HEX = {'ECU_Gold': None, 'ECU_Purple': None, 'global_whiteHelmet': None}
def anyref(name):   # a ref to that color asset as written in any ECU helmet export
    for f in os.listdir(STOCK):
        m = re.search(r'ref="[^"]*/%s\\\\[^"]*" partitionGuid="[^"]*"' % name, open(STOCK + f, encoding='utf-8-sig').read())
        if m: return m.group(0)
    raise SystemExit('no ref for ' + name)
def set_scale(t, g, su, sv):
    a = t.index('<instance guid="%s"' % g); b = t.index('</instance>', a)
    seg, c1 = re.subn(r'(<field name="scaleU">)[^<]*', lambda m: m.group(1) + su, t[a:b], 1); seg, c2 = re.subn(r'(<field name="scaleV">)[^<]*', lambda m: m.group(1) + sv, seg, 1)
    seg, c3 = re.subn(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda m: m.group(1) + su + m.group(2) + sv, seg, 1)
    assert c1 == c2 == c3 == 1; return t[:a] + seg + t[b:]
STICKER_SU, STICKER_SV = '0.15', '0.35'   # one size on every helmet (copied flag scale was 0.4 tall on 2021 helmets -> oval); texture tuned on Jolly Roger at this scale
def set_tr(t, g, u, v):   # overlay transform: scaledTransform.z/w = offsetU/V, mirrored in offsetU/offsetV
    a = t.index('<instance guid="%s"' % g); b = t.index('</instance>', a)
    seg, c1 = re.subn(r'(<field name="offsetU">)[^<]*', lambda m: m.group(1) + u, t[a:b], 1); seg, c2 = re.subn(r'(<field name="offsetV">)[^<]*', lambda m: m.group(1) + v, seg, 1)
    seg, c3 = re.subn(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">[^<]*</field>\s*<field name="y">[^<]*</field>\s*<field name="z">)[^<]*(</field>\s*<field name="w">)[^<]*', lambda m: m.group(1) + u + m.group(2) + v, seg, 1)
    assert c1 == c2 == c3 == 1; return t[:a] + seg + t[b:]
STICKER_SLOT, STICKER_U, STICKER_V = 'overlay_20', '0.142', '0.292'
AAC_U, AAC_V = '-0.146', '0.03'   # v3: AAC and number both ~32 px from the stripe edges; flag centered on AAC, sticker on the number
# scale (Uniform Editor back view): overlay offsetU ~650 px/unit, number x ~357 px/unit   # AAC logo (stock -0.16 / 0.07) moved down with the rest of the back group   # CJ2K ALS sticker (5.4): empty slot on every ECU helmet; mirrors the flag, above the number
STICKER_XML = R + '/Dup IDs/Alt dup IDs/ECU_CJ2K_Sticker_col.xml'   # dup of Standard_Helmet_2022_USAFlag_w_Border_col
def idref(xml):
    x = open(xml, encoding='utf-8-sig').read(); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
    return 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pg.group(2), pg.group(1))
def ov_span(x, slot):
    s = x.index('<field name="%s">' % slot); e = x.index('</field>', x.index('<field name="overlay_blend">', s)); e = x.index('</field>', x.index('</complex>', e)); return s, e
def add_sticker(t):
    if '<field name="label">CJ2K Sticker</field>' in t:   # already added -> just re-place it (idempotent)
        i = t.index('<field name="label">CJ2K Sticker</field>'); g = re.search(r'name="overlay_transform" ref="([0-9a-f-]{36})"', t[i:i + 600]).group(1); return set_scale(set_tr(t, g, STICKER_U, STICKER_V), g, STICKER_SU, STICKER_SV)
    i = t.index('<field name="label">Flag</field>'); fslot = re.findall(r'<field name="(overlay_\d+)">', t[:i])[-1]
    a, b = ov_span(t, fslot); blk = t[a:b].replace('<field name="%s">' % fslot, '<field name="%s">' % STICKER_SLOT, 1)
    blk = re.sub(r'<field name="colorTexture" ref="[^"]*" partitionGuid="[^"]*" />', lambda m: '<field name="colorTexture" %s />' % idref(STICKER_XML), blk, 1)
    blk = re.sub(r'<field name="normalTexture" ref="[^"]*"( partitionGuid="[^"]*")? />', '<field name="normalTexture" ref="null" />', blk, 1)   # flag-shaped emboss -> none
    blk = blk.replace('<field name="label">Flag</field>', '<field name="label">CJ2K Sticker</field>')
    new = []
    for g in set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', blk)):   # local rsm + transform: own copies
        k = t.index('<instance guid="%s"' % g); inst = t[k:t.index('</instance>', k) + len('</instance>')]; ng = str(uuid.uuid4()); new.append((g, ng, inst.replace(g, ng)))
    tg = re.search(r'name="overlay_transform" ref="([0-9a-f-]{36})"', blk).group(1)
    for g, ng, inst in new: blk = blk.replace(g, ng)
    c, d = ov_span(t, STICKER_SLOT); assert 'colorTexture" ref="null"' in t[c:d], 'overlay_20 not empty'
    t = t[:c] + blk + t[d:]; t = t.replace('</partition>', ''.join('\t' + inst + '\n' for _, _, inst in new) + '</partition>')
    ntg = [ng for g, ng, _ in new if g == tg][0]; return set_tr(t, ntg, STICKER_U, STICKER_V)
def move_aac(t):
    i = t.index('<field name="label">AAC  Decal</field>'); return set_tr(t, re.search(r'name="overlay_transform" ref="([0-9a-f-]{36})"', t[i:i + 600]).group(1), AAC_U, AAC_V)
def set_num(t):
    k = t.index('<field name="backnumberoffset_scale">'); seg, c1 = re.subn(r'(<field name="x">)[^<]*', lambda m: m.group(1) + X, t[k:k + 250], 1); seg, c2 = re.subn(r'(<field name="y">)[^<]*', lambda m: m.group(1) + Y, seg, 1)
    seg, c3 = re.subn(r'(<field name="z">)[^<]*', lambda m: m.group(1) + NZ, seg, 1); seg, c4 = re.subn(r'(<field name="w">)[^<]*', lambda m: m.group(1) + NW, seg, 1); assert c3 == c4 == 1
    assert c1 == c2 == 1; return t[:k] + seg + t[k + 250:]
FLAG_SU, FLAG_SV = '0.1068', '0.2495'   # v6 (user): flag width = AAC width (69 px), so centered on the AAC it keeps the AAC's 24 px gap to the stripe; CJ2K sticker = same width   # v5 (user: flag + CJ2K sticker same size): stock 0.15 x 0.35 (2025) / 0.4 (2021) -> ~70 x 45 px, one size on every helmet
def move_flag(t):
    i = t.index('<field name="label">Flag</field>'); g = re.search(r'name="overlay_transform" ref="([0-9a-f-]{36})"', t[i:i + 600]).group(1)
    t = set_tr(t, g, FLAG_U, FLAG_V); a = t.index('<instance guid="%s"' % g); b = t.index('</instance>', a)
    seg, c1 = re.subn(r'(<field name="scaleU">)[^<]*', lambda m: m.group(1) + FLAG_SU, t[a:b], 1); seg, c2 = re.subn(r'(<field name="scaleV">)[^<]*', lambda m: m.group(1) + FLAG_SV, seg, 1)
    seg, c3 = re.subn(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda m: m.group(1) + FLAG_SU + m.group(2) + FLAG_SV, seg, 1)
    assert c1 == c2 == c3 == 1; return t[:a] + seg + t[b:]
BLOCK = ['ECU_HELMET_2021_WHITESCRIPT', 'ECU_HELMET_2021_BLACKOUT', 'ECU_HELMET_2021_WHITE', 'ECU_HELMET_2026_GHOST', 'ECU_HELMET_2025_WHITEUSA',
         'ECU_HELMET_2021_WHITE_yellowFacemask', 'ECU_HELMET_2025_WHITE_blackfacemask', 'ECU_HELMET_2021_BLACKSCRIPT']   # CMU block-number font
DEF = dict(X=X, Y=Y, NZ=NZ, NW=NW, FLAG_U=FLAG_U, FLAG_V=FLAG_V, FLAG_SU=FLAG_SU, FLAG_SV=FLAG_SV, STICKER_U=STICKER_U, STICKER_V=STICKER_V,
           STICKER_SU=STICKER_SU, STICKER_SV=STICKER_SV, AAC_U=AAC_U, AAC_V=AAC_V, AAC_SU='0.15', AAC_SV='0.35')
OVR = {}
for b in BLOCK:   # 5.4 v8 (user): block numbers read bigger than the serif ones at the same box size -> 90%, left edge kept
    OVR[b] = dict(NZ='7.06', NW='4.58', X='0.236', STICKER_U='0.137')
# Away (WHITESCRIPT): its stripe is twice as wide (purple-gold-purple), so the group moves out and shrinks to 85% to clear the warning label
OVR['ECU_HELMET_2021_WHITESCRIPT'] = dict(AAC_U='-0.179', AAC_SU='0.1275', AAC_SV='0.2975', FLAG_U='-0.1725', FLAG_SU='0.0908', FLAG_SV='0.2121',
                                          X='0.314', NZ='8.30', NW='5.39', STICKER_U='0.180', STICKER_SU='0.1275', STICKER_SV='0.2975')
OVR['ECU_HELMET_2026_GHOST'] = dict(OVR['ECU_HELMET_2021_WHITESCRIPT']); OVR['ECU_HELMET_2026_GHOST'].update(NZ='7.47', NW='4.85', X='0.322')   # v2: serif ECU 2021 font reads ~10% bigger than CMU block -> same visual size, left edge kept   # 5.0 (ITEM 5): Ghost Ship gets Away's triple stripe -> Away's back spacing

# 6.0 ITEM 6: triple stripes -> Away's wide-stripe spacing. Blackout = block font (as Away). Home + Jolly Roger = 2025 shell, serif ECU font: start from Ghost's serif values, TUNE in the editor.
OVR['ECU_HELMET_2021_BLACKOUT'] = dict(OVR['ECU_HELMET_2021_WHITESCRIPT'])
OVR['ECU_HELMET_2021_AWAYOPT'] = dict(OVR['ECU_HELMET_2021_WHITESCRIPT'])
OVR['ECU_HELMET_2025_PURPLE_yellowFacemask'] = dict(OVR['ECU_HELMET_2026_GHOST'])
OVR['ECU_HELMET_2025_PURPLE_purpleFacemask'] = dict(OVR['ECU_HELMET_2026_GHOST'])
for _h in ('ECU_HELMET_2025_PURPLE_yellowFacemask', 'ECU_HELMET_2025_PURPLE_purpleFacemask'):   # v2 (editor): serif number touched the warning label on the 2025 shell -> 10% smaller, ~10 px toward the stripe; sticker follows
    OVR[_h].update(NZ='8.22', NW='5.34', X='0.296', STICKER_U='0.165')
# v3 fonts (build_helmet_fonts_60.py): Home = block (jersey font) -> block reads ~10% bigger: z/w /0.9, left edge kept. Home Option = block, no stripe -> BLOCK sizes.
# Treasure Island = serif (Ghost's font copy) -> serif DEF sizes (drop its BLOCK override). Away + Blackout stay block (font copy B).
OVR['ECU_HELMET_2025_PURPLE_yellowFacemask'].update(NZ='9.13', NW='5.93', X='0.286')
OVR['ECU_HELMET_2021_PURPLE_yellowFacemask'] = dict(NZ='7.06', NW='4.58', X='0.236', STICKER_U='0.137')
OVR.pop('ECU_HELMET_2021_WHITE', None)
OVR['ECU_HELMET_2025_PURPLE_yellowFacemask'] = dict(OVR['ECU_HELMET_2021_WHITESCRIPT'])   # v4 (user): Home's back group = exactly Away / Black Pirate's values (same block font now)
def params(h):
    g = globals(); g.update(DEF); g.update(OVR.get(h, {}))
def move_aac(t):
    i = t.index('<field name="label">AAC  Decal</field>'); gg = re.search(r'name="overlay_transform" ref="([0-9a-f-]{36})"', t[i:i + 600]).group(1)
    return set_scale(set_tr(t, gg, AAC_U, AAC_V), gg, AAC_SU, AAC_SV)
WARN_U = {'ECU_HELMET_2025_PURPLE_yellowFacemask': '0.349'}   # 6.0 (user): EA put the warning label at 0.325 on the 2025 shell (0.349 on 2021) -> crowded the number; Home matches the 2021 triple stripes
def move_warn(t, h):
    if h not in WARN_U: return t
    i = t.index('<field name="label">Warning Label</field>'); g = re.search(r'name="overlay_transform" ref="([0-9a-f-]{36})"', t[i:i + 600]).group(1)
    a = t.index('<instance guid="%s"' % g); b = t.index('</instance>', a); seg = t[a:b]
    seg, c1 = re.subn(r'(<field name="offsetU">)[^<]*', lambda m: m.group(1) + WARN_U[h], seg, 1)
    seg, c2 = re.subn(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">[^<]*</field>\s*<field name="y">[^<]*</field>\s*<field name="z">)[^<]*', lambda m: m.group(1) + WARN_U[h], seg, 1)
    assert c1 == c2 == 1; return t[:a] + seg + t[b:]
for h, (fill, outl, why) in PLAN.items():
    params(h)
    src = FIN + h + '.xml' if os.path.exists(FIN + h + '.xml') else STOCK + h + '.xml'
    t = open(src, encoding='utf-8-sig').read()
    t = set_num(t)
    if fill:
        m = re.search(r'_NUM_Array(_[AB])?\\\\', t); s_ = t.rfind('<field name="textures">', 0, m.start()); e_ = t.index('<field name="info">', m.start()); seg = t[s_:e_]
        for ch, nm in (('R', fill), ('G', outl)):
            seg, c = re.subn(r'<field name="color%s" ref="[^"]*"( partitionGuid="[^"]*")? />' % ch, lambda mm, nm=nm: '<field name="color%s" %s />' % (ch, anyref(nm)), seg, 1); assert c == 1
        t = t[:s_] + seg + t[e_:]
    t = move_warn(move_aac(add_sticker(move_flag(t))), h)
    p = FIN + h + '.xml'; open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p)
    print('%-40s %s  <- %s' % (h, why, 'FINAL' if src.startswith(FIN) else 'stock'))

# Jolly Roger: number already placed by build_jolly_roger_helmet.py -> flag only
params('ECU_HELMET_2025_PURPLE_purpleFacemask')
p = FIN + 'ECU_HELMET_2025_PURPLE_purpleFacemask.xml'; t = set_num(move_aac(add_sticker(move_flag(open(p, encoding='utf-8-sig').read())))); open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p); print('ECU_HELMET_2025_PURPLE_purpleFacemask    Jolly Roger: flag, sticker, AAC, number position')
