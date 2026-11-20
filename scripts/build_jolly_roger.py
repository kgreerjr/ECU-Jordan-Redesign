# ECU "Jolly Roger" alternate, phase 1: replaces the BASE PURPLE jersey + pants (and its wrapper).
# Jersey = the purple alternate's layer stack (stripes, PIRATES wordmark, collar) recolored, inside the base purple part item.
import os, re, uuid, io, numpy as np, xml.etree.ElementTree as ET
from PIL import Image
R = os.environ.get('ECU_PROJECT_DIR', '.'); F = R + '/FINAL'
OUT = R + '/Builds/Jolly Roger'; os.makedirs(OUT, exist_ok=True)
rd = lambda p: open(p, encoding='utf-8-sig').read()
def wr(p, s): open(p, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(p)
CHAR_SRGB = (0x4A, 0x4A, 0x4F)   # refined: #404044 read near-black in sunlight; helmet keeps #404044 (matte lifts it)
NUM_OUTLINE_SRGB = (0x7A, 0x4F, 0xC0)   # brighter purple number outline (ECU purple #392762 vanished on charcoal)                                     # neutral charcoal (R = G like ECU's black #28282C, which renders neutral); v1 #3C3F43 rendered olive
lin = lambda c: ((c/255 + 0.055)/1.055)**2.4 if c/255 > 0.04045 else c/255/12.92
CHAR_LIN = [round(lin(c), 7) for c in CHAR_SRGB]
def colorvalue(guid, xyz=None):
    x, y, z = xyz or CHAR_LIN
    return ('\t<instance guid="%s" type="ColorValue" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="Color">\n'
            '\t\t\t<complex type="Vec3">\n\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n'
            '\t\t\t</complex>\n\t\t</field>\n\t</instance>\n') % (guid, x, y, z)
def teamref(t, name): return re.search(r'ref="[^"]*/%s\\\\[^"]*" partitionGuid="[^"]*"' % name, t).group(0)
def dupref(fld, xmlname):
    x = rd(R + '/Dup IDs/Colored dup IDs/' + xmlname); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
    return '<field name="%s" ref="%s\\\\%s" partitionGuid="%s" />' % (fld, nm, pg.group(2), pg.group(1))
def block_for_label(t, label):
    i = t.index('<field name="label">%s</field>' % label)
    start = max(t.rfind('<complex type="LayerCompOverlayInstance">', 0, i), t.rfind('<complex type="LayerCompMaterialInstance">', 0, i), t.rfind('<complex type="LayerCompArrayOverlayInstance">', 0, i))
    return start, i
def set_tint(t, label, **chans):                     # chans: R=..., G=..., B=...  (value = full 'ref="..." partitionGuid="..."' or 'ref="<guid>"')
    s, e = block_for_label(t, label); seg = t[s:e]
    for ch, val in chans.items():
        rep = '<field name="color%s" %s />' % (ch, val)
        seg, c = re.subn(r'<field name="color%s" ref="[^"]*"( partitionGuid="[^"]*")? />' % ch, lambda m: rep, seg, count=1); assert c == 1, (label, ch)   # lambda: keep the \\ in refs literal
    return t[:s] + seg + t[e:]
log = []

# ---- topo pattern (phase 2): fabric material colorTexture -> ECU_JR_Topo_col (duplicate of default_mask), tiled by the material transform ----
def topo_material(t, label, local_tr=None, xml=None):
    s, e = block_for_label(t, label); tail = t.index('</complex>\n\t\t</field>', e)   # through material_transform
    seg = re.sub(r'<field name="colorTexture" ref="[^"]*" partitionGuid="[^"]*" />', lambda m: '<field name="colorTexture" %s />' % idref(xml or TOPO_XML), t[s:tail], 1)
    if local_tr: seg = re.sub(r'<field name="material_transform" ref="[^"]*"( partitionGuid="[^"]*")? />', lambda m: '<field name="material_transform" ref="%s" />' % local_tr, seg, 1)
    tr = re.search(r'<field name="material_transform" ref="([0-9a-f-]{36})" />', seg).group(1)
    t = t[:s] + seg + t[tail:]
    i = t.index('<instance guid="%s"' % tr); j = t.index('</instance>', i)
    inst = re.sub(r'(<field name="scaledTransform">\s*<complex type="Vec4">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*', lambda m: m.group(1) + TOPO_SCALE + m.group(2) + TOPO_SCALE, t[i:j], 1)
    inst, c = re.subn(r'(<field name="scale[UV]">)[^<]*', lambda m: m.group(1) + TOPO_SCALE, inst); assert c == 2
    return t[:i] + inst + t[j:]
# ---------------- jersey ----------------
P = rd(R + '/Backups/Pre-alternates FINAL/Jerseys/ECU_JERSEY_2023_PURPLE.xml'); A = rd(F + '/Jerseys/ECU_JERSEY_2023_PURPLEALT.xml')   # P = Jordan-swap base (FINAL now holds the Jolly Roger build)
pp = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', P); pa = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', A)
J = A.replace(pa.group(1), pp.group(1)).replace(pa.group(2), pp.group(2))
J = J.replace('jerseys/partItems/ECU_JERSEY_2023_PURPLEALT<', 'jerseys/partItems/ECU_JERSEY_2023_PURPLE<')
J = J.replace('ECU_JERSEY_2023_WHITE_preset_ES_appearance', 'ECU_JERSEY_2023_PURPLE_preset_ES_appearance').replace('>ECU_JERSEY_2023_WHITE_preset<', '>ECU_JERSEY_2023_PURPLE_preset<')
# textures the base purple slot doesn't load -> point at duplicates made from textures it does load
JRD = R + '/Dup IDs/Alt dup IDs/'
TOPO_XML = JRD + 'ECU_JR_Topo_col.xml'; TOPO = os.path.exists(TOPO_XML); TOPO_SCALE = '0.11'   # = tile size in UV (0.03 stock = ~15 tiles across the chest). NOTE: earlier tests only changed scaledTransform, which the game ignores - scaleU/scaleV is what counts
def idref(xmlpath):
    x = rd(xmlpath); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x); nm = re.search(r'name="Name">([^<]+)', x).group(1)
    return 'ref="%s\\\\%s" partitionGuid="%s"' % (nm, pg.group(2), pg.group(1))
SWAP = {'ECU_Decal_2021_03_col': idref(JRD + 'ECU_JR_Pirates_col.xml'), 'ECU_Decal_2021_03_norm': idref(JRD + 'ECU_JR_Pirates_norm.xml'),
        'ECU_Decal_2021_03_rsm': idref(JRD + 'ECU_JR_Pirates_rsm.xml'), 'Standard_Jersey_2023_Stripes_SleevesSingle_col': idref(JRD + 'ECU_JR_SleeveStripe_col.xml'),
        'Standard_Jersey_2023_Stripes_SleeveCuffs_col': idref(JRD + 'ECU_JR_SleeveCuff_col.xml'), 'Jersey_UVSet_sleeveStripesMirrored': idref(JRD + 'ECU_JR_UVSet_sleeveStripes.xml'),
        'ECU_Jersey_2023_NUM_Array': re.search(r'ref="[^"]*/ECU_Jersey_2021_NUM_Array\\\\[^"]*" partitionGuid="[^"]*"', P).group(0)}
for k, v in SWAP.items():
    J, c = re.subn(r'ref="[^"]*/%s\\\\[^"]*" partitionGuid="[^"]*"' % k, lambda m, _v=v: _v, J); assert c >= 1, k; log.append('jersey swap %-46s x%d' % (k, c))
PUR, GOLD = teamref(J, 'ECU_Purple'), teamref(J, 'ECU_Gold'); cg = str(uuid.uuid4()); CH = 'ref="%s"' % cg
for lab in ['Vapor Untouchable Fabric', 'Nike Vent Holes', 'Vent Holes - Nameplate Area', 'Sleeve Fabric', 'Collar Fabric', 'Sleeve Cuff', 'TShirtandPads', 'Collar Stripe']:
    J = set_tint(J, lab, R=CH); log.append('jersey %-28s -> charcoal' % lab)
for lab in ['Stripe 1', 'Stripe 2']: J = set_tint(J, lab, R=PUR); log.append('jersey %-28s -> purple' % lab)
J = set_tint(J, 'ECU Logo', R=GOLD, G=PUR); log.append('jersey PIRATES wordmark          -> gold, purple')
# (removed: old overlay_18 step - that overlay is empty, and the non-greedy regex was hitting the NUMBER tint's R)
# numbers (ECU_Jersey_2023_NUM_Array): fill gold, outline purple ; nameplate gold
i = J.index('ECU_Jersey_2021_NUM_Array'); s = J.index('<complex type="LayerCompTint">', i); e = J.index('</complex>', s)
seg = J[s:e]; seg = re.sub(r'<field name="colorR" ref="[^"]*" partitionGuid="[^"]*" />', lambda mm: '<field name="colorR" %s />' % GOLD, seg, 1)   # R = number fill
ng = str(uuid.uuid4()); NUM_OUT = [round(lin(c), 7) for c in NUM_OUTLINE_SRGB]
seg = re.sub(r'<field name="color([GB])" ref="[^"]*" partitionGuid="[^"]*" />', lambda mm: '<field name="color%s" ref="%s" />' % (mm.group(1), ng), seg); J = J[:s] + seg + J[e:]   # G/B = outline (brighter purple)
i = J.index('Standard_Jersey_2022_Blocky_02_NAME_Array'); s = J.index('<complex type="LayerCompTint">', i); e = J.index('</complex>', s)
seg = re.sub(r'<field name="color([RG])" ref="[^"]*" partitionGuid="[^"]*" />', lambda mm: '<field name="color%s" %s />' % (mm.group(1), GOLD), J[s:e]); J = J[:s] + seg + J[e:]
log.append('jersey numbers (2021 font)        -> R fill gold, G/B outline purple; names gold')
# Jumpman -> gold on charcoal (WithText duplicate)
s, e = block_for_label(J, 'Jumpman Logo'); seg = re.sub(r'<field name="colorTexture" ref="[^"]*" partitionGuid="[^"]*" />', lambda mm, _r=dupref('colorTexture', 'ECU_JM_WT_GoldOnCharcoal_col.xml'): _r, J[s:e], 1); J = J[:s] + seg + J[e:]
J = J.replace('</partition>', colorvalue(cg) + colorvalue(ng, NUM_OUT) + '</partition>')
TOPO_J = JRD + 'ECU_JR_Topo_Jersey_col.xml'   # jersey gets its own, stronger copy (wrinkles/mesh/logos drown the pants-strength one)
if TOPO: J = topo_material(J, 'Vapor Untouchable Fabric', xml=TOPO_J if os.path.exists(TOPO_J) else None); log.append('jersey torso fabric             -> topo pattern, scale ' + TOPO_SCALE)
os.makedirs(OUT + '/Jerseys', exist_ok=True); wr(OUT + '/Jerseys/ECU_JERSEY_2023_PURPLE.xml', J)
# ---------------- pants ----------------
T = rd(R + '/Backups/Pre-alternates FINAL/Pants/ECU_Pants_2023_PURPLE.xml'); PUR2 = teamref(T, 'ECU_Purple'); cg2 = str(uuid.uuid4()); CH2 = 'ref="%s"' % cg2
for lab in ['Adidas Base Fabric', 'AdidasHoles']: T = set_tint(T, lab, R=CH2); log.append('pants  %-28s -> charcoal' % lab)
T = set_tint(T, 'Stripe', G=PUR2); log.append('pants  stripe                    -> gold core, purple edges')
s, e = block_for_label(T, 'Jumpman Logo'); seg = re.sub(r'<field name="colorTexture" ref="[^"]*" partitionGuid="[^"]*" />', lambda mm, _r=dupref('colorTexture', 'ECU_JM_GoldOnCharcoal_col.xml'): _r, T[s:e], 1); T = T[:s] + seg + T[e:]
T = T.replace('</partition>', colorvalue(cg2) + '</partition>')
JR_HIP_ALT_LOGO = False   # tried, mod author removed the Jolly Roger alt logo entirely -> stock ECU hip logo
if JR_HIP_ALT_LOGO and os.path.exists(JRD + 'ECU_JR_Logo_col.xml'):   # hip logo -> the mod author's Jolly Roger alt logo (dup of ECU_Decal_2021_02_col), pre-colored
    s_, e_ = block_for_label(T, 'Logo ECU'); seg = T[s_:e_]
    seg = re.sub(r'<field name="colorTexture" ref="[^"]*" partitionGuid="[^"]*" />', lambda mm: '<field name="colorTexture" %s />' % idref(JRD + 'ECU_JR_Logo_col.xml'), seg, 1)
    seg = re.sub(r'<field name="(normalTexture|rsmTexture)" ref="[^"]*"( partitionGuid="[^"]*")? />', lambda mm: '<field name="%s" ref="null" />' % mm.group(1), seg)
    seg = re.sub(r'<field name="assetResolveRuleType">[^<]*', '<field name="assetResolveRuleType">AssetResolveRule_UseDefaults', seg, 1); T = T[:s_] + seg + T[e_:]
    log.append('pants  hip logo                 -> Jolly Roger alt logo')
if TOPO:   # pants base fabric uses a SHARED transform asset -> give it a local copy so other teams aren't affected
    i = J.index('<instance guid="1b5df4ed'); tg = str(uuid.uuid4()); inst = J[i:J.index('</instance>', i) + len('</instance>')].replace('1b5df4ed-9585-41a3-9ee4-6c82b14507a6', tg)
    T = T.replace('</partition>', '\t' + inst + '\n</partition>'); T = topo_material(T, 'Adidas Base Fabric', local_tr=tg); log.append('pants  base fabric              -> topo pattern, scale ' + TOPO_SCALE)
os.makedirs(OUT + '/Pants', exist_ok=True); wr(OUT + '/Pants/ECU_Pants_2023_PURPLE.xml', T)
# ---------------- wrapper ----------------
U = rd(R + '/Backups/ECU part items/ECU Wrappers/U_ECU_JERSEY_2023_PURPLE.xml')
U = U.replace('<field name="DisplayName">Purple Jersey</field>', '<field name="DisplayName">Jolly Roger</field>')
def rsm(u, fld, x, y, z):
    return re.sub(r'(<field name="%s">\s*<complex type="Vec3">\s*<field name="x">)[^<]*(</field>\s*<field name="y">)[^<]*(</field>\s*<field name="z">)[^<]*' % fld, r'\g<1>%s\g<2>%s\g<3>%s' % (x, y, z), u, 1)
U = rsm(U, 'NumberRSM', 0.6, 0.8, 1); U = rsm(U, 'NameplateRSM', 0.6, 0.8, 1)
# --- jersey palette (drives TeamColor gloves etc.): same mechanism as the BLACK jersey wrapper (primary black, secondary purple) ---
JR_PRIMARY = CHAR_LIN                                   # charcoal
JR_SECONDARY = [0.9734453, 0.462077, 0.0]               # ECU gold (swap to ECU purple 0.0409152, 0.0202885624, 0.122138776 if preferred)
def colorvisuals(g, xyz):
    return ('\t<instance guid="%s" type="ColorVisuals" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="ColorChannels">\n\t\t\t<complex type="Vec4">\n'
            '\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t\t<field name="w">1</field>\n'
            '\t\t\t</complex>\n\t\t</field>\n\t\t<field name="ColorLookup">ColorLookup_NoLookup</field>\n\t</instance>\n') % (g, *xyz)
pal, cp, cs = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
U, c = re.subn(r'<field name="ItemPalette" ref="null" />', '<field name="ItemPalette" ref="%s" />' % pal, U, count=1); assert c == 1
U = U.replace('</partition>', ('\t<instance guid="%s" type="PaletteVisuals" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="QuaternaryColor" ref="null" />\n'
      '\t\t<field name="PrimaryColor" ref="%s" />\n\t\t<field name="SecondaryColor" ref="%s" />\n\t\t<field name="TertiaryColor" ref="null" />\n\t</instance>\n') % (pal, cp, cs)
      + colorvisuals(cp, JR_PRIMARY) + colorvisuals(cs, JR_SECONDARY) + '</partition>')
log.append('wrapper: jersey palette primary charcoal, secondary gold (gloves)')
# --- name test: blank the string-table IDs so the menus fall back to DisplayName (works for uniform sets, which have no IDs) ---
def name_test(u, display):
    u, c = re.subn(r'(<field name="(?:Short|Long|Medium)NameId">)[^<]*', r'\g<1>', u); assert c == 3
    return re.sub(r'(<field name="DisplayName">)[^<]*', lambda m: m.group(1) + display, u, 1)
NAME_TEST = False   # tested: blanking the IDs + DisplayName did NOT rename items in game (names come from elsewhere) -> keep stock IDs
if NAME_TEST: U = name_test(U, 'Jolly Roger Jersey')
os.makedirs(OUT + '/Wrapper', exist_ok=True); wr(OUT + '/Wrapper/U_ECU_JERSEY_2023_PURPLE.xml', U)
if NAME_TEST:
    P2 = name_test(rd(R + '/Backups/ECU part items/ECU Wrappers/U_ECU_Pants_2023_PURPLE.xml'), 'Jolly Roger Pants'); wr(OUT + '/Wrapper/U_ECU_Pants_2023_PURPLE.xml', P2)
    H2 = name_test(rd(R + '/Backups/ECU helmets/Wrappers/U_ECU_HELMET_2025_PURPLE_purpleFacemask.xml'), 'Jolly Roger Helmet'); wr(OUT + '/Wrapper/U_ECU_HELMET_2025_PURPLE_purpleFacemask.xml', H2)
log.append('wrapper: metallic numbers and names' + ('; NAME TEST on' if NAME_TEST else ''))
# ---------------- gold-on-charcoal Jumpman images ----------------
def colv(f): t = rd(f); return np.array([float(re.search(r'name="%s">([^<]+)' % k, t).group(1)) for k in 'xyz'])
gold = colv(R + '/Dup IDs/Team colors/ECU_Gold.xml'); char = np.array(CHAR_LIN)
d = open(R + '/Dup IDs/Jumpman_Decal_2022_Cotton_col.dds', 'rb').read(); h = bytearray(d[:128]); h[84:88] = b'DXT5'
a = np.asarray(Image.open(io.BytesIO(bytes(h) + d[148:])).convert('RGBA')).astype(float)/255
srgb = lambda l: np.where(np.clip(l, 0, 1) <= 0.0031308, 12.92*np.clip(l, 0, 1), 1.055*np.power(np.clip(l, 0, 1), 1/2.4) - 0.055)
rgb = (srgb(a[..., 0:1]*char + a[..., 1:2]*gold)*255 + 0.5).astype(np.uint8); rgb[a[..., 3] == 0] = (srgb(char)*255 + 0.5).astype(np.uint8)
img = Image.fromarray(np.dstack([rgb, (a[..., 3]*255 + 0.5).astype(np.uint8)]), 'RGBA')
os.makedirs(OUT + '/Jumpman images', exist_ok=True)
for n in ['ECU_JM_WT_GoldOnCharcoal_col', 'ECU_JM_GoldOnCharcoal_col']: img.save(OUT + '/Jumpman images/%s.png' % n)
print('\n'.join(log)); print('charcoal linear', CHAR_LIN)
for f in [OUT + '/Jerseys/ECU_JERSEY_2023_PURPLE.xml', OUT + '/Pants/ECU_Pants_2023_PURPLE.xml', OUT + '/Wrapper/U_ECU_JERSEY_2023_PURPLE.xml']:
    bad = re.findall(r'ref="[^"\\]+\\(?!\\)[0-9a-f-]{36}"', rd(f)); ok = re.findall(r'ref="[^"]+\\\\[0-9a-f-]{36}"', rd(f))
    assert not bad, (f, bad[:2]); print(os.path.basename(f), 'external refs ok:', len(ok), 'broken:', len(bad))
