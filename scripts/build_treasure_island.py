# ECU "Treasure Island" (ALT3): ND-gold helmet, gunmetal + metallic-gold jersey, ND 2021 gold pants.
# Replaces: ECU_HELMET_2021_WHITE ("White Helmet 2"), ECU_JERSEY_2023_WHITE (+wrapper), ECU_PANTS_2023_WHITEALT. None are used by the other 6 sets.
import os, re, uuid, io, numpy as np, xml.etree.ElementTree as ET
from PIL import Image
R = os.environ.get('ECU_PROJECT_DIR', '.'); F = R + '/FINAL'; B = R + '/Backups'; ND = R + '/Backups/Notre Dame ref'
OUT = R + '/Builds/Treasure Island'; JRD = R + '/Dup IDs/Alt dup IDs/'
rd = lambda p: open(p, encoding='utf-8-sig').read()
def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(p)
    assert not re.search(r'[^\\]\\[0-9a-f]{8}-', s), 'single-backslash ref in ' + p
    locs = set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', s)); miss = [g for g in locs if '<instance guid="%s"' % g not in s]; assert not miss, (p, miss)
def ndval(name): t = rd(ND + '/%s.xml' % name); return [float(v) for v in re.findall(r'name="[xyz]">([^<]*)', t)[:3]]
lin = lambda c: ((c/255 + 0.055)/1.055)**2.4 if c/255 > 0.04045 else c/255/12.92
GUN_SRGB = (0x5B, 0x59, 0x62)   # true gunmetal with a faint violet undertone (ECU); v1 used ND_BlueGray #424E66, which read blue. Lighter than Jolly Roger #4A4A4F so the two don't blur.
GUN = [round(lin(c), 7) for c in GUN_SRGB]; NDGOLD = ndval('ND_MetallicGold')        # #B09257 metallic gold
SHAM_FILL = [0.587016344, 0.3870031, 0.126315072]; SHAM_OUT = [0.7293471, 0.4795215, 0.154916033]   # ND 2024 Shamrock number golds (#C9A764 / #DEB86E)
ND_SHELL = [0.8900054, 0.7095108, 0.244864345]                                         # ND 2021 gold helmet shell (#F2DB88)
log = []
class Doc:
    def __init__(s, t): s.t = t; s.new = []
    def color(s, xyz, kind='ColorValue'):
        g = str(uuid.uuid4())
        if kind == 'ColorValue':
            s.new.append('\t<instance guid="%s" type="ColorValue" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="Color">\n\t\t\t<complex type="Vec3">\n'
                         '\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t</complex>\n\t\t</field>\n\t</instance>\n' % (g, *xyz))
        else:
            s.new.append('\t<instance guid="%s" type="ColorVisuals" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="ColorChannels">\n\t\t\t<complex type="Vec4">\n'
                         '\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t\t<field name="w">1</field>\n\t\t\t</complex>\n\t\t</field>\n'
                         '\t\t<field name="ColorLookup">ColorLookup_NoLookup</field>\n\t</instance>\n' % (g, *xyz))
        return 'ref="%s"' % g
    def block(s, label=None, tex=None):
        if label:
            i = s.t.index('<field name="label">%s</field>' % label)
            st = max(s.t.rfind('<complex type="LayerComp%s">' % k, 0, i) for k in ('OverlayInstance', 'MaterialInstance', 'ArrayOverlayInstance')); return st, i
        i = s.t.index(tex); st = s.t.rfind('<field name="textures">', 0, i); return st, s.t.index('<field name="info">', i)
    def sub(s, pat, rep, label=None, tex=None, count=1):
        a, b = s.block(label, tex); seg, c = re.subn(pat, lambda m: rep, s.t[a:b], count=count); assert c >= 1, (label, tex, pat); s.t = s.t[:a] + seg + s.t[b:]
    def tint(s, ch, val, label=None, tex=None): s.sub(r'<field name="color%s" ref="[^"]*"( partitionGuid="[^"]*")? />' % ch, '<field name="color%s" %s />' % (ch, val), label, tex)
    def field(s, fld, val, label=None, tex=None): s.sub(r'<field name="%s" ref="[^"]*"( partitionGuid="[^"]*")? />' % fld, '<field name="%s" %s />' % (fld, val), label, tex)
    def assetname(s, old, new): assert s.t.count('>%s<' % old) == 1, old; s.t = s.t.replace('>%s<' % old, '>%s<' % new)
    def surface(s, fld, mm, rf, sm):
        g = re.search(r'name="%s" ref="([0-9a-f-]{36})"' % fld, s.t).group(1); i = s.t.index('<instance guid="%s"' % g); j = s.t.index('</instance>', i); seg = s.t[i:j]
        for k, v in (('metal_mask', mm), ('reflectance', rf), ('smoothness', sm)): seg = re.sub(r'(<field name="%s">)[^<]*' % k, lambda m, v=v: m.group(1) + str(v), seg, 1)
        s.t = s.t[:i] + seg + s.t[j:]
    def rule(s, val, label): s.sub(r'<field name="assetResolveRuleType">[^<]*</field>', '<field name="assetResolveRuleType">%s</field>' % val, label)
    def prelogo(s, label, xml):   # pre-colored full-color art: UseDefaults (shown as-is, tint ignored), old logo's norm/rsm dropped
        s.field('colorTexture', idref(xml), label); s.field('normalTexture', 'ref="null"', label); s.field('rsmTexture', 'ref="null"', label); s.rule('AssetResolveRule_UseDefaults', label)
    def done(s): return s.t.replace('</partition>', ''.join(s.new) + '</partition>')
def ov_span(x, slot):
    s = x.index('<field name="%s">' % slot); e = x.index('</field>', x.index('<field name="overlay_blend">', s)); e = x.index('</field>', x.index('</complex>', e)); return s, e
def copy_overlay(dst, src_text, src_label, dst_slot, color_ref):
    i = src_text.index('<field name="label">%s</field>' % src_label); slot = re.findall(r'<field name="(overlay_\d+)">', src_text[:i])[-1]
    a, b = ov_span(src_text, slot); blk = src_text[a:b].replace('<field name="%s">' % slot, '<field name="%s">' % dst_slot, 1)
    blk = re.sub(r'<field name="colorR" ref="[^"]*"( partitionGuid="[^"]*")? />', lambda m: '<field name="colorR" %s />' % color_ref, blk, 1)
    for g in set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', blk)):
        if g in color_ref: continue
        k = src_text.index('<instance guid="%s"' % g); inst = src_text[k:src_text.index('</instance>', k) + len('</instance>')]; ng = str(uuid.uuid4())
        dst.new.append('\t' + inst.replace(g, ng) + '\n'); blk = blk.replace(g, ng)
    c, d = ov_span(dst.t, dst_slot); assert 'colorTexture" ref="null"' in dst.t[c:d], dst_slot; dst.t = dst.t[:c] + blk + dst.t[d:]
def teamref(t, name): return re.search(r'ref="[^"]*/%s\\\\[^"]*" partitionGuid="[^"]*"' % name, t).group(0)
def idref(xml):
    x = rd(xml); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
    return 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pg.group(2), pg.group(1))
# ---------------- jersey (base WHITE) ----------------
# v3 (user): jersey body = the pants gold, trim + numbers gunmetal; pants gunmetal with a gold stripe. (v1/v2 were gunmetal jersey, gold pants)
# v4 (user): pants stay v3 (gunmetal + gold stripe); jersey back to gunmetal body with gold trim + Shamrock-gold numbers, now satin instead of mirror
J = Doc(rd(R + '/Backups/Pre-alternates FINAL/Jerseys/ECU_JERSEY_2023_WHITE.xml')); body, trim = J.color(GUN), J.color(NDGOLD); fill, outl = J.color(SHAM_FILL), J.color(SHAM_OUT)
for lab in ['Vapor Untouchable Fabric', 'Nike Vent Holes', 'Vent Holes - Nameplate Area', 'Sleeve Fabric', 'TShirtandPads']: J.tint('R', body, lab)
for lab in ['Collar Fabric', 'Sleeve Cuff']: J.tint('R', trim, lab)
J.tint('R', trim, 'ECU Logo'); J.tint('G', trim, 'ECU Logo')                               # EAST CAROLINA wordmark
J.field('colorTexture', 'ref="null"', 'Back Logo'); J.field('normalTexture', 'ref="null"', 'Back Logo')   # upper-back pirate logo looked smeared on the yoke -> removed
for lab in ['Sleeve Decals - Long Sleeves', 'Sleeve Decals - Standard and Tight Sleeves']: J.tint('G', trim, lab)   # pirate logo: purple hat, metallic-gold outline, white skull
J.tint('R', trim, 'AAC Logo'); J.tint('B', teamref(J.t, 'ECU_Purple'), 'AAC Logo')
J.tint('R', fill, tex='ECU_Jersey_2021_NUM_Array'); J.tint('G', outl, tex='ECU_Jersey_2021_NUM_Array'); J.tint('B', outl, tex='ECU_Jersey_2021_NUM_Array')
J.tint('R', trim, tex='Standard_Jersey_2022_Blocky_02_NAME_Array'); J.tint('G', trim, tex='Standard_Jersey_2022_Blocky_02_NAME_Array')
for f in ['frontNumberRSM', 'backNumberRSM', 'sleeveNumberRSM', 'shoulderNumberRSM']: J.surface(f, 0.6, 0.3, 0.6)   # satin-metal gold (Shamrock 0.9/0.925 mirror read bronze in v2)
J.surface('nameplateRSM', 0.5, 0.25, 0.35)
# sleeves: Jolly Roger's gold shoulder slash stripes + cuff stripe, copied into empty slots (reuses the ECU_JR_* stripe dups; test whether the WHITE jersey can load them)
JRJ = rd(R + '/Builds/Jolly Roger/Jerseys/ECU_JERSEY_2023_PURPLE.xml')
for src, dst in (('Stripe 1', 'overlay_9'), ('Stripe 2', 'overlay_10'), ('Middle Stripe', 'overlay_13'), ('Sleeve Cuff Stripe', 'overlay_14')): copy_overlay(J, JRJ, src, dst, trim)
log.append('jersey: gold sleeve slash stripes + cuff stripe (JR layers)')
TI_LOGO = JRD + 'ECU_TI_Logo_col.xml'
for lab in ['Sleeve Decals - Long Sleeves', 'Sleeve Decals - Standard and Tight Sleeves']:   # v6: user removed the shoulder logo (stripes carry the sleeve)
    J.field('colorTexture', 'ref="null"', lab); J.field('normalTexture', 'ref="null"', lab); J.field('rsmTexture', 'ref="null"', lab)
log.append('jersey: shoulder/sleeve logos removed')
J.assetname('ECU_JERSEY_2023_WHITE_preset', 'ND_JERSEY_2023_BLUE_preset'); J.assetname('ECU_JERSEY_2023_WHITE_preset_ES_appearance', 'ND_JERSEY_2023_BLUE_preset_ES_appearance')
wr(OUT + '/Jerseys/ECU_JERSEY_2023_WHITE.xml', J.done()); log.append('jersey v4: gunmetal body, gold trim/wordmark/nameplate, satin-metal Shamrock-gold numbers, back logo removed')
# ---------------- jersey wrapper: palette (gloves) ----------------
W = Doc(rd(B + '/ECU part items/ECU Wrappers/U_ECU_JERSEY_2023_WHITE.xml')); pal = str(uuid.uuid4()); p1, p2 = W.color(GUN, 'vis'), W.color(NDGOLD, 'vis')
W.t, c = re.subn(r'<field name="ItemPalette" ref="null" />', '<field name="ItemPalette" ref="%s" />' % pal, W.t, count=1); assert c == 1
W.new.append('\t<instance guid="%s" type="PaletteVisuals" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="QuaternaryColor" ref="null" />\n\t\t<field name="PrimaryColor" %s />\n'
             '\t\t<field name="SecondaryColor" %s />\n\t\t<field name="TertiaryColor" ref="null" />\n\t</instance>\n' % (pal, p1, p2))
W.t = re.sub(r'(<field name="DisplayName">)[^<]*', lambda m: m.group(1) + 'Treasure Island', W.t, 1)
wr(OUT + '/Wrapper/U_ECU_JERSEY_2023_WHITE.xml', W.done()); log.append('jersey wrapper: palette gunmetal / metallic gold (gloves)')
# ---------------- pants (base WHITEALT) ----------------
P = Doc(rd(R + '/Backups/Pre-alternates FINAL/Pants/ECU_PANTS_2023_WHITEALT.xml')); pgold, pgun = P.color(NDGOLD), P.color(GUN)
for lab in ['Adidas Base Fabric', 'AdidasHoles']: P.tint('R', pgun, lab)
for ch in 'RGB': P.tint(ch, pgold, 'Stripe')                                                # solid gold side stripe = the jersey color
P.tint('G', pgold, 'Logo ECU')
JMP = JRD + 'ECU_TI_JM_Pants_col.xml'   # pants Jumpman = dup of ORIGINAL ECU_Decal_2021_02_col. The older ECU_JM_GunmetalOnGold_col (dup of our dup ECU_JM_PurpleOnWhite_col) only ever showed the norm/rsm embossing - suspected: dup-of-dup gets no bundles
if os.path.exists(JMP): P.field('colorTexture', idref(JMP), 'Jumpman Logo'); log.append('pants: Jumpman -> ECU_TI_JM_Pants_col (white on gunmetal)')
if os.path.exists(TI_LOGO): P.prelogo('Logo ECU', TI_LOGO); log.append('pants: hip logo -> Treasure Island alt logo')
P.assetname('ECU_PANTS_2023_PURPLE_preset', 'ND_PANTS_2021_GOLD_preset'); P.assetname('ECU_PANTS_2023_PURPLE_preset_ES_appearance', 'ND_PANTS_2021_GOLD_preset_ES_appearance')
wr(OUT + '/Pants/ECU_PANTS_2023_WHITEALT.xml', P.done()); log.append('pants v3: gunmetal + ND pants finish preset, gold stripe')
# ---------------- helmet (2021 WHITE) ----------------
H = Doc(rd(B + '/ECU helmets/Part items/ECU_HELMET_2021_WHITE.xml')); shell, hgun, hgold = H.color(ND_SHELL), H.color(GUN), H.color(NDGOLD)
H.tint('R', shell, 'Helmet Shell')
for lab in ['Frontplates', 'Backplates', 'Chin Guard', 'Chin Straps']: H.tint('R', hgun, lab)
TI_HLOGO = JRD + 'ECU_TI_Helmet_Logo_col.xml'
for lab in ['Right Side Logo', 'Left Side Logo']:
    if os.path.exists(TI_HLOGO): H.prelogo(lab, TI_HLOGO)                                   # v5: alt logo on the sides
    else: H.field('colorTexture', 'ref="null"', lab); H.field('normalTexture', 'ref="null"', lab)   # v1-4: "gold helmet, straight up"
if os.path.exists(TI_HLOGO): log.append('helmet: side logos -> Treasure Island alt logo')
for lab in ['Frontplate', 'Frontplate_Schutt']: H.tint('R', hgold, lab)
for lab in ['Backplate', 'Backplate_X1']: H.tint('R', hgold, lab); H.tint('G', hgold, lab)
H.t, c = re.subn(r'<field name="faceMaskColor" ref="null" />', '<field name="faceMaskColor" %s />' % hgun, H.t, count=1); assert c == 1
H.assetname('ECU_HELMET_2021_WHITE_preset', 'ND_HELMET_2021_GOLD_preset'); H.assetname('ECU_HELMET_2021_WHITE_preset_ES_appearance', 'ND_HELMET_2021_GOLD_preset_ES_appearance')
H.tint('R', hgun, 'AAC  Decal'); H.tint('G', hgold, 'AAC  Decal'); H.tint('B', hgold, 'AAC  Decal')                # 5.2: back AAC was stock ECU purple -> gunmetal A, gold outline + star
H.tint('R', hgun, tex='CMU_Jersey_2021_NUM_Array'); H.tint('G', hgold, tex='CMU_Jersey_2021_NUM_Array')            # 5.2: back number gunmetal fill, gold outline (gold alone vanishes on the gold shell)
log.append('helmet: back number + AAC gunmetal with gold outline')
wr(OUT + '/Helmet/ECU_HELMET_2021_WHITE.xml', H.done()); log.append('helmet: ND gold shell + ND gold finish preset, gunmetal bumpers/chin/facemask, gold bumper text')
# ---------------- Jumpman images ----------------
d = open(R + '/Dup IDs/Jumpman_Decal_2022_Cotton_col.dds', 'rb').read(); h = bytearray(d[:128]); h[84:88] = b'DXT5'
a = np.asarray(Image.open(io.BytesIO(bytes(h) + d[148:])).convert('RGBA')).astype(float) / 255
srgb = lambda l: np.where(np.clip(l, 0, 1) <= 0.0031308, 12.92 * np.clip(l, 0, 1), 1.055 * np.power(np.clip(l, 0, 1), 1 / 2.4) - 0.055)
def jm(bg, fig, name):
    bg, fig = np.array(bg), np.array(fig); rgb = (srgb(a[..., 0:1] * bg + a[..., 1:2] * fig) * 255 + 0.5).astype(np.uint8); rgb[a[..., 3] == 0] = (srgb(bg) * 255 + 0.5).astype(np.uint8)
    os.makedirs(OUT + '/Jumpman images', exist_ok=True); Image.fromarray(np.dstack([rgb, (a[..., 3] * 255 + 0.5).astype(np.uint8)]), 'RGBA').save(OUT + '/Jumpman images/%s.png' % name)
WHITE = [0.6375968, 0.6375968, 0.7454042]   # global_white (the game's uniform white)
jm(GUN, WHITE, 'ECU_JM_WT_PurpleOnWhite_col')   # jersey Jumpman white on gunmetal; only the WHITE jersey uses this texture, so it is repainted in place (name now misleading)
jm(GUN, WHITE, 'ECU_TI_JM_Pants_col')           # pants Jumpman: white on gunmetal
print('\n'.join(log))
