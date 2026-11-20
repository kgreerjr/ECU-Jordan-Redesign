# ECU "Ghost Ship": white + lavender fog, lavender PIRATES/numbers/trim, matte white helmet with the black-line skull.
# All pieces are NEW duplicates (no base piece overwritten): ECU_JERSEY_2026_GHOST, ECU_PANTS_2026_GHOST, ECU_HELMET_2026_GHOST (+ U_ wrappers),
# preset CFB/ECU/U_UniformType_ECU_Current9thAlternate. Content is rebuilt from the stock ECU pieces, identity (partition/GUID/Name) from the mod author's duplicate exports.
# usage: python3 build_ghost_ship.py   -> Builds/Ghost Ship/{Jerseys,Pants,Helmet,Wrappers,Uniform sets}
import os, re, uuid
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_treasure_island.py'), encoding='utf-8').read()
exec(src[:src.index('# ---------------- jersey (base WHITE)')])          # helpers: Doc, wr, rd, idref, copy_overlay, teamref, lin
GS = R + '/Builds/Ghost Ship'; DUP = GS + '/Dup exports/'; ST = R + '/Backups/Slot test'
BASE = R + '/Backups/Pre-alternates FINAL'
hexlin = lambda h: [round(lin(int(h[i:i + 2], 16)), 7) for i in (1, 3, 5)]
WHITE = [0.6375968, 0.6375968, 0.7454042]          # global_white
LAV = hexlin('#B9A2DC'); WISP = hexlin('#B5B4BD'); TRIM = hexlin('#A9A8B2'); DARK = hexlin('#5B4386'); GFILL = hexlin('#9A99A4'); LOUT = hexlin('#9479D0');   MASK = hexlin('#9A99A4')   # v3: white/gray primary (gray fog WISP + gray sleeve TRIM), lavender accents only; dark-purple outline; light-gray facemask; v4: GFILL/LOUT = PIRATES/numbers/name gray fill, lavender outline
FOG_SCALE = '0.12'                                  # fog tile size in UV. v1 0.3 = smeared to an even wash (JR notes: 0.2 already 'blurry bands'); 0.11 proven crisp
log = []
def identity(base_text, dup_xml):
    """Content of base_text, identity (partition guid, primary instance guid, Name) of the mod author's duplicate."""
    d = rd(dup_xml); pd = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', d); nd = re.search(r'name="Name">([^<]+)', d).group(1)
    pb = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', base_text); nb = re.search(r'name="Name">([^<]+)', base_text).group(1)
    return base_text.replace(pb.group(1), pd.group(1)).replace(pb.group(2), pd.group(2)).replace('>%s<' % nb, '>%s<' % nd)
def fog(D, label, tex_xml):
    a, b = D.block(label); tail = D.t.index('</complex>\n\t\t</field>', b)
    seg = re.sub(r'<field name="colorTexture" ref="[^"]*" partitionGuid="[^"]*" />', lambda m: '<field name="colorTexture" %s />' % idref(tex_xml), D.t[a:tail], 1)
    m = re.search(r'<field name="material_transform" ref="([0-9a-f-]{36})" />', seg)
    if not m:   # shared transform asset -> local copy so other teams aren't affected
        ext = re.search(r'<field name="material_transform" ref="[^"]*"( partitionGuid="[^"]*")? />', seg); assert ext, label
        tg = str(uuid.uuid4()); D.new.append('\t' + LOCAL_TR.replace(LOCAL_TR_G, tg) + '\n'); seg = seg.replace(ext.group(0), '<field name="material_transform" ref="%s" />' % tg, 1); g = tg
    else: g = m.group(1)
    D.t = D.t[:a] + seg + D.t[tail:]
    D.tint('G', D.color(WISP), label); D.tint('B', D.color(LAV), label)   # fog channels are tint masks: G = gray mist, B = lavender drift
    D.fog_tr.add(g)
def fog_scale(D):
    for g in D.fog_tr:
        s = D.t.find('<instance guid="%s"' % g)
        if s < 0: s = None; nn = [i for i, x in enumerate(D.new) if 'guid="%s"' % g in x]; x = D.new[nn[0]]
        else: x = D.t[s:D.t.index('</instance>', s)]
        y = re.sub(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda m: m.group(1) + FOG_SCALE + m.group(2) + FOG_SCALE, x, 1)
        y, c = re.subn(r'(<field name="scale[UV]">)[^<]*', lambda m: m.group(1) + FOG_SCALE, y); assert c == 2, g
        if s is None: D.new[nn[0]] = y
        else: D.t = D.t[:s] + y + D.t[s + len(x):]
def kill(D, label):
    for f in ('colorTexture', 'normalTexture', 'rsmTexture'):
        try: D.field(f, 'ref="null"', label)
        except AssertionError: pass
DECAL_SURF = (0, 0.4, 0.35)   # metal_mask, reflectance, smoothness (satin-matte)
def matte(D, label):
    g = str(uuid.uuid4()); D.new.append('\t<instance guid="%s" type="LayerCompSurfaceParam" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="metal_mask">%s</field>\n'
        '\t\t<field name="reflectance">%s</field>\n\t\t<field name="smoothness">%s</field>\n\t</instance>\n' % (g, *DECAL_SURF))
    for ch in 'RGB': D.field('rsm' + ch, 'ref="%s"' % g, label)
JRD_ = JRD
# ---------------- jersey: ECU_JERSEY_2026_GHOST (stock ECU white 2023) ----------------
J = Doc(identity(rd(BASE + '/Jerseys/ECU_JERSEY_2023_WHITE.xml'), ST + '/ECU_JERSEY_2026_GHOST.xml')); J.fog_tr = set()
m = re.search(r'<field name="material_transform" ref="([0-9a-f-]{36})" />', J.t[J.block('Vapor Untouchable Fabric')[0]:]); LOCAL_TR_G = m.group(1)
i = J.t.index('<instance guid="%s"' % LOCAL_TR_G); LOCAL_TR = J.t[i:J.t.index('</instance>', i) + len('</instance>')]
lav, dark = J.color(LAV), J.color(DARK)
for lab in ['Vapor Untouchable Fabric', 'Sleeve Fabric']: fog(J, lab, JRD_ + '../Ghost Ship duplicate IDs (xml)/ECU_GS_Fog_Jersey_col.xml' if False else DUP + 'ECU_GS_Fog_Jersey_col.xml')
fog_scale(J); log.append('jersey: fog on torso + sleeves (ECU_GS_Fog_Jersey_col, scale %s)' % FOG_SCALE)
trim = J.color(TRIM)
for lab in ['Collar Fabric', 'Sleeve Cuff']: J.tint('R', trim, lab)
# v5 (mod author): copy Jolly Roger's whole PIRATES layer (texture + transform + norm/rsm, its local instances get new GUIDs) into the ECU Logo slot.
# (v1-4 swapped textures into the white jersey's EAST CAROLINA layer and edited its transform; scale changes had no visible effect.)
JRJ = rd(R + '/Builds/Jolly Roger/Jerseys/ECU_JERSEY_2023_PURPLE.xml')
slot = re.findall(r'<field name="(overlay_\d+)">', J.t[:J.t.index('<field name="label">ECU Logo</field>')])[-1]
c_, d_ = ov_span(J.t, slot); J.t = J.t[:c_] + re.sub(r'<field name="colorTexture" ref="[^"]*"( partitionGuid="[^"]*")? />', '<field name="colorTexture" ref="null" />', J.t[c_:d_], 1) + J.t[d_:]
gfill, lout = J.color(GFILL), J.color(LOUT)
copy_overlay(J, JRJ, 'ECU Logo', slot, gfill); J.tint('G', lout, 'ECU Logo')
log.append('jersey: PIRATES = Jolly Roger layer copied into %s (size/placement as JR)' % slot)
log.append('jersey: PIRATES gray fill / lavender outline')
kill(J, 'Back Logo'); kill(J, 'Sleeve Decals - Long Sleeves'); kill(J, 'Sleeve Decals - Standard and Tight Sleeves'); log.append('jersey: back + shoulder logos removed (clean ghost look)')
J.tint('R', J.color(GFILL), 'AAC Logo'); J.tint('G', J.color(LOUT), 'AAC Logo'); J.tint('B', J.color(hexlin('#6F6E78')), 'AAC Logo'); log.append('jersey: AAC logo gray, lavender outline, dark-gray star')
J.tint('R', gfill, tex='ECU_Jersey_2021_NUM_Array'); J.tint('G', lout, tex='ECU_Jersey_2021_NUM_Array'); J.tint('B', lout, tex='ECU_Jersey_2021_NUM_Array'); log.append('jersey: numbers gray fill, lavender outline (matte)')
J.tint('R', gfill, tex='Standard_Jersey_2022_Blocky_02_NAME_Array'); J.tint('G', lout, tex='Standard_Jersey_2022_Blocky_02_NAME_Array'); log.append('jersey: nameplate gray fill, lavender outline')
JRJ = rd(R + '/Builds/Jolly Roger/Jerseys/ECU_JERSEY_2023_PURPLE.xml')
for s_, d_ in (('Stripe 1', 'overlay_9'), ('Stripe 2', 'overlay_10'), ('Middle Stripe', 'overlay_13'), ('Sleeve Cuff Stripe', 'overlay_14')): copy_overlay(J, JRJ, s_, d_, lav if s_ in ('Stripe 1', 'Stripe 2') else trim)   # v5: the two slash stripes lavender
log.append('jersey: lavender slash stripes; gray middle/cuff stripe, collar, cuffs')
a, b = J.block('Jumpman Logo'); seg, c = re.subn(r'ref="[^"]*/ECU_JM_WT_PurpleOnWhite_col\\\\[^"]*" partitionGuid="[^"]*"', lambda mm: idref(DUP + 'ECU_GS_JM_Jersey_col.xml'), J.t[a:b]); assert c == 1; J.t = J.t[:a] + seg + J.t[b:]
# v5 (mod author): number size/position/spacing = Jolly Roger's (whole number_offsetScaleSpacing block: chest/back/sleeve/shoulder offset+scale, spacing)
def nblock(x):
    st = x.index('<complex type="number_offsetScaleSpacing">'); d = 0
    for m_ in re.finditer(r'<complex type="[^"]*">|</complex>', x[st:]):
        d += 1 if m_.group(0) != '</complex>' else -1
        if d == 0: return st, st + m_.end()
ja, jb = nblock(JRJ); ga, gb = nblock(J.t); assert not re.search(r'ref="[0-9a-f]{8}-', JRJ[ja:jb]); J.t = J.t[:ga] + JRJ[ja:jb] + J.t[gb:]
log.append('jersey: number size/position/spacing copied from Jolly Roger')
wr(GS + '/Jerseys/ECU_JERSEY_2026_GHOST.xml', J.done())
# ---------------- pants: ECU_PANTS_2026_GHOST (stock ECU white-alt) ----------------
P = Doc(identity(rd(BASE + '/Pants/ECU_PANTS_2023_WHITEALT.xml'), DUP + 'ECU_PANTS_2026_GHOST.xml')); P.fog_tr = set()
fog(P, 'Adidas Base Fabric', DUP + 'ECU_GS_Fog_col.xml'); fog_scale(P); log.append('pants: fog (ECU_GS_Fog_col)')
plav = P.color(LAV)
for ch in 'RGB': P.tint(ch, plav, 'Stripe')
kill(P, 'Logo ECU'); log.append('pants: solid lavender stripe, hip logo removed')
a, b = P.block('Jumpman Logo'); seg, c = re.subn(r'ref="[^"]*/ECU_JM_PurpleOnWhite_col\\\\[^"]*" partitionGuid="[^"]*"', lambda mm: idref(DUP + 'ECU_GS_JM_Pants_col.xml'), P.t[a:b]); assert c == 1; P.t = P.t[:a] + seg + P.t[b:]
wr(GS + '/Pants/ECU_PANTS_2026_GHOST.xml', P.done())
# ---------------- helmet: ECU_HELMET_2026_GHOST (stock ECU 2021 white) ----------------
H = Doc(identity(rd(R + '/Backups/ECU helmets/Part items/ECU_HELMET_2021_WHITE.xml'), DUP + 'ECU_HELMET_2026_GHOST.xml'))
hlav, hmask = H.color(LAV), H.color(MASK)
H.tint('R', H.color(hexlin('#E9EAF0')), 'Helmet Shell')   # v3: cool white - stock global_offWhiteHelmetShell read beige under the matte finish
# v5: like the Jolly Roger helmet - ECU's stock BLA skull MASK (in our dup, lines nudged to soft charcoal by make_gs_helmet_logo_mask.py),
# tinted per channel; stock normal/rsm + stock resolve rule. (v1-4 pre-colored + UseDefaults read the stock rsm raw: hat = metal -> beige/chrome)
HELMET_LOGO = 'ship'   # 'ship' = mod author's ghost-ship art (make_gs_ship_logo.py), 'skull' = stock BLA skull (make_gs_helmet_logo_mask.py). Import the matching PNG
if HELMET_LOGO == 'ship':   # mask from the mod author's art: no matching normal/rsm -> null both (Jolly Roger helmet logo style)
    lt, ls, lh = H.color(hexlin('#B9A2DC')), H.color(hexlin('#F2F2F5')), H.color(hexlin('#C6C6CA'))   # lavender, white, gray
    for lab in ['Right Side Logo', 'Left Side Logo']:   # both sides share UV orientation (no mirroring) -> a shifted logo needs its own texture per side
        tex = DUP + ('ECU_GS_Helmet_Logo_R_col.xml' if lab == 'Right Side Logo' and os.path.exists(DUP + 'ECU_GS_Helmet_Logo_R_col.xml') else 'ECU_GS_Helmet_Logo_col.xml')
        H.field('colorTexture', idref(tex), lab); H.field('normalTexture', 'ref="null"', lab); H.field('rsmTexture', 'ref="null"', lab)
        H.tint('R', lt, lab); H.tint('G', ls, lab); H.tint('B', lh, lab)
else:
    lt, ls, lh = H.color(hexlin('#9479D0')), H.color(hexlin('#F2F2F5')), H.color(hexlin('#D3D2DE'))   # trim/ECU/bandana, skull, hat
    for lab in ['Right Side Logo', 'Left Side Logo']:
        H.field('colorTexture', idref(DUP + 'ECU_GS_Helmet_Logo_col.xml'), lab); H.tint('R', lt, lab); H.tint('G', ls, lab); H.tint('B', lh, lab)
log.append('helmet: side logo = ' + HELMET_LOGO)
# v6: MATTE decals. Stock rsm params were metallic (logo R 0.7 / B 0.5 metal = old metallic-gold trim; WHITESCRIPT stripe R 0.775 / G 0.45) -> chrome look.
for lab in ['Right Side Logo', 'Left Side Logo']: matte(H, lab)   # Center Stripe: after its layer is copied in (below)
log.append('helmet: side logos + center stripe MATTE (metal 0, smoothness %s)' % DECAL_SURF[2])
for lab in ['Frontplate', 'Frontplate_Schutt']: H.tint('R', hlav, lab)
for lab in ['Backplate', 'Backplate_X1']: H.tint('R', hlav, lab); H.tint('G', hlav, lab)
# v4: lavender center stripe = WHITESCRIPT's (same 2021 helmet) center-stripe overlay + its local instances (new GUIDs), texture -> Jolly Roger's thin stripe dup
WS = rd(R + '/Backups/ECU helmets/Part items/ECU_HELMET_2021_WHITESCRIPT.xml')
def ov5(x): s_ = x.index('<field name="overlay_5">'); e_ = x.index('</field>', x.index('<field name="overlay_blend">', s_)); e_ = x.index('</field>', x.index('</complex>', e_)); return s_, e_
s1, e1 = ov5(WS); blk = WS[s1:e1]; assert '>Center Stripe<' in blk
STRIPE_TEX = DUP + 'ECU_GS_Helmet_Stripe_col.xml' if os.path.exists(DUP + 'ECU_GS_Helmet_Stripe_col.xml') else JRD + 'ECU_JR_Helmet_Stripe_col.xml'   # v8: own dup of BLA_Decal_col (JR's WHI_Decal_01 dup isn't in this helmet's bundle -> invisible in game)
blk, c = re.subn(r'<field name="(colorTexture|rsmTexture)" ref="[^"]*FiveStripe_02_col[^"]*" partitionGuid="[^"]*" />', lambda m: '<field name="%s" %s />' % (m.group(1), idref(STRIPE_TEX)), blk); assert c >= 1
for g in set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', blk)):
    i = WS.index('<instance guid="%s"' % g); inst = WS[i:WS.index('</instance>', i) + len('</instance>')]; assert not re.search(r'ref="[0-9a-f]{8}-[0-9a-f-]{27}"', inst)
    ng = str(uuid.uuid4()); H.new.append('\t' + inst.replace(g, ng) + '\n'); blk = blk.replace(g, ng)
s2, e2 = ov5(H.t); assert '>Center Stripe<' in H.t[s2:e2]; H.t = H.t[:s2] + blk + H.t[e2:]
for ch in 'RGB': H.tint(ch, hlav, 'Center Stripe')
H.field('rsmTexture', 'ref="null"', 'Center Stripe')
matte(H, 'Center Stripe')
i = H.t.index('<field name="label">Center Stripe</field>'); tg = re.search(r'name="overlay_transform" ref="([0-9a-f-]{36})"', H.t[i:i + 600]).group(1)   # the field right AFTER this layer's label   # v7: full length (offset -0.28 stopped it above the flag)
a_ = H.t.find('<instance guid="%s"' % tg); b_ = H.t.index('</instance>', a_) if a_ >= 0 else -1
if a_ >= 0:
    seg = re.sub(r'(<field name="w">)[^<]*', r'\g<1>0', H.t[a_:b_], 1); seg = re.sub(r'(<field name="offsetV">)[^<]*', r'\g<1>0', seg, 1); H.t = H.t[:a_] + seg + H.t[b_:]
else:
    k = [n for n, x in enumerate(H.new) if 'guid="%s"' % tg in x][0]; seg = re.sub(r'(<field name="w">)[^<]*', r'\g<1>0', H.new[k], 1); H.new[k] = re.sub(r'(<field name="offsetV">)[^<]*', r'\g<1>0', seg, 1)
log.append('helmet: center stripe full length (offset 0)')
hg, hl, hd = H.color(GFILL), H.color(LOUT), H.color(hexlin('#6F6E78'))
H.tint('R', hg, 'AAC  Decal'); H.tint('G', hl, 'AAC  Decal'); H.tint('B', hd, 'AAC  Decal')
H.tint('R', hg, tex='CMU_Jersey_2021_NUM_Array'); H.tint('G', hl, tex='CMU_Jersey_2021_NUM_Array')
log.append('helmet: back AAC logo + number gray, lavender outline; facemask gray #9A99A4')   # v5: stripe art doubled as rsm -> center band read dark/shiny; null = one flat lavender band
log.append('helmet: one solid lavender center stripe (all bands lavender, no rsm)')
H.t, c = re.subn(r'<field name="faceMaskColor" ref="null" />', '<field name="faceMaskColor" %s />' % hmask, H.t, count=1); assert c == 1
H.assetname('ECU_HELMET_2021_WHITE_preset', 'KU_HELMET_2021_BLACK_preset'); H.assetname('ECU_HELMET_2021_WHITE_preset_ES_appearance', 'KU_HELMET_2021_BLACK_preset_ES_appearance')
wr(GS + '/Helmet/ECU_HELMET_2026_GHOST.xml', H.done()); log.append('helmet: off-white shell, MATTE finish (KU preset), black-line skull sides, lavender bumper text, light-gray facemask')
# ---------------- wrappers ----------------
def wrapper(x, iid, part, disp):
    x = re.sub(r'(<field name="Id">\s*<complex type="ItemDataId">\s*<field name="Id">)\d+<', lambda m: m.group(1) + str(iid) + '<', x, 1); assert str(iid) in x
    x = re.sub(r'(<field name="DisplayName">)[^<]*', lambda m: m.group(1) + disp, x, 1)
    x, c = re.subn(r'(<field name="AssetName">)ECU_[A-Z]+_20\d\d_[A-Za-z_]+(</field>)', lambda m: m.group(1) + part + m.group(2), x, 1); assert c == 1; return x
Wj = Doc(wrapper(rd(ST + '/already imported/U_ECU_JERSEY_2026_GHOST.xml'), 91726001, 'ECU_JERSEY_2026_GHOST', 'Ghost Ship'))
pal = re.search(r'<field name="ItemPalette" ref="([0-9a-f-]{36})" />', Wj.t).group(1); pi = Wj.t.index('<instance guid="%s"' % pal); pv = Wj.t[pi:Wj.t.index('</instance>', pi)]
for slot, col in (('PrimaryColor', WHITE), ('SecondaryColor', LAV)):   # gloves (TeamColor) + WHISEC cleats follow this palette
    g = re.search(r'name="%s" ref="([0-9a-f-]{36})"' % slot, pv).group(1); ci = Wj.t.index('<instance guid="%s"' % g); cj = Wj.t.index('</instance>', ci); seg = Wj.t[ci:cj]
    for ax, v in zip('xyz', col): seg = re.sub(r'(<field name="%s">)[^<]*' % ax, lambda m, v=v: m.group(1) + str(v), seg, 1)
    Wj.t = Wj.t[:ci] + seg + Wj.t[cj:]
wr(GS + '/Wrappers/U_ECU_JERSEY_2026_GHOST.xml', Wj.done()); log.append('jersey wrapper: palette white / lavender (gloves, cleats)')
wr(GS + '/Wrappers/U_ECU_PANTS_2026_GHOST.xml', wrapper(rd(DUP + 'U_ECU_PANTS_2026_GHOST.xml'), 91726002, 'ECU_PANTS_2026_GHOST', 'Ghost Ship Pants'))
wr(GS + '/Wrappers/U_ECU_HELMET_2026_GHOST.xml', wrapper(rd(DUP + 'U_ECU_HELMET_2026_GHOST.xml'), 91726003, 'ECU_HELMET_2026_GHOST', 'Ghost Ship Helmet'))
# ---------------- preset: Ghost Ship ----------------
u = rd(ST + '/IMPORT these/U_UniformType_ECU_Current9thAlternate.xml')
u = re.sub(r'(<field name="DisplayName">)[^<]*', lambda m: m.group(1) + 'Ghost Ship', u, 1)
for a_, b_ in (('U_ECU_HELMET_2021_WHITE', 'U_ECU_HELMET_2026_GHOST'), ('U_ECU_PANTS_2023_WHITEALT', 'U_ECU_PANTS_2026_GHOST')): assert '>%s<' % a_ in u; u = u.replace('>%s<' % a_, '>%s<' % b_)
u = u.replace('LoadoutType_TeamDark', 'LoadoutType_TeamLight'); assert 'CurrentOfficial">false' in u
wr(GS + '/Uniform sets/U_UniformType_ECU_Current9thAlternate.xml', u); log.append('preset: "Ghost Ship" (Light), GHOST helmet/jersey/pants, white socks, WHISEC cleats')
print('\n'.join(log))

# ---------------- TeamVisuals: Ghost Ship between Treasure Island and Jolly Roger ----------------
tv = rd(ST + '/IMPORT these/ECUXXX_TeamVisuals.xml'); a_ = tv.index('<array name="Uniforms"'); b_ = tv.index('</array>', a_)
items = re.findall(r'\t*<item ref="[^"]*" partitionGuid="[^"]*" />\n', tv[a_:b_]); gs_ = [x for x in items if 'Current9thAlternate' in x]; assert len(gs_) == 1
rest = [x for x in items if x not in gs_]; k = [i for i, x in enumerate(rest) if 'Current7thAlternate' in x][0]; new_items = rest[:k + 1] + gs_ + rest[k + 1:]
body = tv[a_:b_]; first = body.index(items[0]); last = body.rindex(items[-1]) + len(items[-1])
tv = tv[:a_] + body[:first] + ''.join(new_items) + body[last:] + tv[b_:]
wr(GS + '/TeamVisuals/ECUXXX_TeamVisuals.xml', tv); log.append('TeamVisuals order: ' + ' / '.join(re.search(r'U_UniformType_ECU_(\w+)', x).group(1) for x in new_items))
print(log[-1])
