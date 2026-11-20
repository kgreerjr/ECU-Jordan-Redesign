"""Home Alternate (6.0): purple counterpart of Away Alternate, listed just before it.
Jersey = Away Alternate jersey with the approved purple look (build_purple_aa_preview.py purplehat) + its own Jumpman dup
(ECU_JM_HA_GoldOnPurple_col, dup of ECU_JM_PurpleOnWhite_col which this jersey loads). Helmet/pants = Frosty copies of
Away Alternate's (no edits). Wrappers Ids 91726009-011, preset Current10thAlternate (dark, WHIPRI cleats, white socks).
usage: build_home_alternate.py <project root>"""
import re, sys, os, subprocess, xml.etree.ElementTree as ET
R = sys.argv[1]; FIN = os.path.join(R, 'FINAL'); OUT = os.path.join(R, 'Builds/6.0', 'Home Alternate')
os.makedirs(OUT, exist_ok=True)
rd = lambda p: open(p, encoding='utf-8-sig').read()
def wr(p, t): open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p); print('wrote', os.path.relpath(p, R))
def one(pat, rep, t, n=1):
    t2, k = re.subn(pat, rep, t, count=n); assert k == n, (pat, k); return t2
# jersey
J = os.path.join(OUT, 'ECU_JERSEY_2026_HOMEALT.xml')
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_purple_aa_preview.py'), os.path.join(R, 'ECU_JERSEY_2026_HOMEALT.xml'), J, 'purplehat'], check=True)
x = rd(os.path.join(R, 'ECU_JM_HA_GoldOnPurple_col.xml')); pg, pi = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x).groups()
JM = 'ref="ContentShared/characters/player/parts/uniforms/decals/vendors/ECU_JM_HA_GoldOnPurple_col\\\\%s" partitionGuid="%s"' % (pi, pg)
s = rd(J); s = one(r'ref="[^"]*/ECU_JM_WT_GoldOnPurple_col\\\\[^"]*" partitionGuid="[^"]*"', lambda m: JM, s); wr(J, s)
# wrappers
for piece, part, wid, disp in (('JERSEY_2026', 'ECU_JERSEY_2026_HOMEALT', 91726009, 'Home Alternate Jersey'),
                               ('HELMET_2021', 'ECU_HELMET_2021_HOMEALT', 91726010, 'Home Alternate Helmet'),
                               ('PANTS_2023', 'ECU_PANTS_2023_HOMEALT', 91726011, 'Home Alternate Pants')):
    p = os.path.join(R, 'U_ECU_%s_HOMEALT.xml' % piece); s = rd(p)
    s = one(r'(<field name="Id">\s*<complex type="ItemDataId">\s*<field name="Id">)\d+', lambda m: m.group(1) + str(wid), s)
    s = one(r'(<field name="AssetName">)ECU_[A-Z]+_20\d\d_AWAYOPT', lambda m: m.group(1) + part, s)
    s = one(r'(<field name="DisplayName">)[^<]*', lambda m: m.group(1) + disp, s)
    if piece.startswith('JERSEY'):   # Home's jersey wrapper has no palette (team palette -> purple gloves like Home)
        g = re.search(r'<field name="ItemPalette" ref="([0-9a-f-]{36})"', s).group(1)
        s = one(r'(<field name="ItemPalette" )ref="[0-9a-f-]{36}"', lambda m: m.group(1) + 'ref="null"', s)
        pv = re.search(r'\t<instance guid="%s" type="PaletteVisuals".*?</instance>\n' % g, s, re.S); kids = re.findall(r'ref="([0-9a-f-]{36})"', pv.group(0))
        s = s.replace(pv.group(0), '')
        for k in kids: s = re.sub(r'\t<instance guid="%s" type="ColorVisuals".*?</instance>\n' % k, '', s, flags=re.S)
    wr(os.path.join(OUT, os.path.basename(p)), s)
# preset
p = os.path.join(R, 'U_UniformType_ECU_Current10thAlternate.xml'); s = rd(p)
s = one(r'(<field name="DisplayName">)Away Alternate', lambda m: m.group(1) + 'Home Alternate', s)
for a, b in (('U_ECU_JERSEY_2026_AWAYOPT', 'U_ECU_JERSEY_2026_HOMEALT'), ('U_ECU_PANTS_2023_AWAYOPT', 'U_ECU_PANTS_2023_HOMEALT'), ('U_ECU_HELMET_2021_AWAYOPT', 'U_ECU_HELMET_2021_HOMEALT')):
    s = one('>%s<' % a, '>%s<' % b, s)
s = one('>U_GENERIC_SHOESX_WHIBLA<', '>U_GENERIC_SHOESX_WHIPRI<', s, 2)
s = one(r'LoadoutType_TeamLight', 'LoadoutType_TeamDark', s)
s = one(r'(<field name="DisplayOrder">)\d+', lambda m: m.group(1) + '7', s)
wr(os.path.join(OUT, os.path.basename(p)), s)
pg, pi = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', s).groups()
# Away Alternate preset: DisplayOrder 7 -> 8
p = os.path.join(FIN, 'Uniform sets', 'U_UniformType_ECU_Current2ndAlternate.xml'); s = rd(p)
s = one(r'(<field name="DisplayOrder">)7', lambda m: m.group(1) + '8', s); wr(os.path.join(OUT, os.path.basename(p)), s)
# TeamVisuals: Home Alternate just before Away Alternate
p = os.path.join(FIN, 'TeamVisuals', 'ECUXXX_TeamVisuals.xml'); s = rd(p)
item = '<item ref="content/FootballCharacter/UniformVisuals/CFB/ECU/U_UniformType_ECU_Current10thAlternate\\\\%s" partitionGuid="%s" />' % (pi, pg)
s = one(r'(\t+)(<item ref="content/FootballCharacter/UniformVisuals/CFB/ECU/U_UniformType_ECU_Current2ndAlternate)', lambda m: m.group(1) + item + '\n' + m.group(1) + m.group(2), s)
wr(os.path.join(OUT, os.path.basename(p)), s)
