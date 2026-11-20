# "Unlock more slots" test: an 8th uniform preset ("Slot Test") wearing a DUPLICATED jersey (red-number marker).
# Inputs: Slot test/*.xml (user's Frosty duplicates of ECU_JERSEY_2023_WHITE, U_ECU_JERSEY_2023_WHITE, U_UniformType_ECU_CurrentHome)
# Output: Slot test/IMPORT - *.xml (3 duplicates edited + TeamVisuals with 8 presets). No subfolders: Windows blocks new folders under Program Files.
import os, re
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'build_treasure_island.py'), encoding='utf-8').read()
exec(src[:src.index('# ---------------- jersey (base WHITE)')])          # helpers only (Doc, wr, idref, ...)
PRESET = 'U_UniformType_ECU_Current9thAlternate'   # v2: duplicate made in CFB/ECU (v1 Current8thAlternate landed in CFB/CHAR and sorted 3rd)
S = R + '/Backups/Slot test'; O = S + '/IMPORT these/'
# 1) duplicated part item: red number fill so the duplicate is unmistakable
J = Doc(rd(S + '/ECU_JERSEY_2026_GHOST.xml'))
J.tint('R', J.color([0.8, 0.0, 0.0]), tex='ECU_Jersey_2021_NUM_Array')
wr(O + 'ECU_JERSEY_2026_GHOST.xml', J.done())
# 2) duplicated wrapper: own item Id, own name, points at the duplicated part item
w = rd(S + '/U_ECU_JERSEY_2026_GHOST.xml')
w = re.sub(r'(<field name="Id">\s*<complex type="ItemDataId">\s*<field name="Id">)24172424<', r'\g<1>91726001<', w, 1); assert '91726001' in w
w = w.replace('<field name="DisplayName">Treasure Island</field>', '<field name="DisplayName">Slot Test</field>', 1)
assert w.count('<field name="AssetName">ECU_JERSEY_2023_WHITE</field>') == 1
w = w.replace('<field name="AssetName">ECU_JERSEY_2023_WHITE</field>', '<field name="AssetName">ECU_JERSEY_2026_GHOST</field>')
wr(O + 'U_ECU_JERSEY_2026_GHOST.xml', w)
# 3) 8th preset: Treasure Island pieces, but the duplicated jersey
u = rd(S + '/' + PRESET + '.xml')
u = u.replace('<field name="DisplayName">Home</field>', '<field name="DisplayName">Slot Test</field>', 1)
assert u.count('<field name="CurrentOfficial">true</field>') == 1; u = u.replace('<field name="CurrentOfficial">true</field>', '<field name="CurrentOfficial">false</field>')   # copied from Home: official presets list first (Slot Test sat 3rd) and may auto-select
swap = {'U_ECU_JERSEY_2023_PURPLEALT': 'U_ECU_JERSEY_2026_GHOST', 'U_ECU_HELMET_2025_PURPLE_yellowFacemask': 'U_ECU_HELMET_2021_WHITE',
        'U_ECU_PANTS_2023_YELLOW': 'U_ECU_PANTS_2023_WHITEALT', 'U_GENERIC_SHOESX_WHIPRI': 'U_GENERIC_SHOESX_WHISEC'}
for a, b in swap.items(): assert '>%s<' % a in u, a; u = u.replace('>%s<' % a, '>%s<' % b)
wr(O + PRESET + '.xml', u)
# 4) TeamVisuals: append the 8th preset to Uniforms
tv = rd(F + '/TeamVisuals/ECUXXX_TeamVisuals.xml'); i = tv.index('<array name="Uniforms"'); j = tv.index('</array>', i)
tv = tv[:j] + '\t<item %s />\n\t\t' % idref(S + '/' + PRESET + '.xml') + tv[j:]
wr(O + 'ECUXXX_TeamVisuals.xml', tv)
print('Slot test built ->', O)
