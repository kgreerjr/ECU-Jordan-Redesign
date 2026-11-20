# 6.0: every in-use helmet's back number uses its jersey's font. Fonts follow the bundle rule: a copy of an array the helmet
# already loads, holding the target font's art (method proven on Ghost Ship, technical notes section 23).
#   ECU_Block_NUM_Array_A = dup of ECU_Jersey_2021_NUM_Array + ECU_Jersey_2023 (block) art -> Home, Home Option
#   ECU_Block_NUM_Array_B = dup of CMU_Jersey_2021_NUM_Array + ECU_Jersey_2023 (block) art -> Away, Black Pirate / Away Option
#   ECU_GS_Helmet_NUM_Array = dup of CMU_Jersey_2021_NUM_Array + ECU_Jersey_2021 (serif) art -> Ghost Ship, Treasure Island
#   Jolly Roger keeps ECU_Jersey_2021_NUM_Array (its jersey's font, loaded directly).
# Run BEFORE build_helmet_numbers.py (sizes depend on the font).
import os, re
R = os.environ.get('ECU_PROJECT_DIR', '.'); H = R + '/FINAL/Helmets/'; IDS = R + '/Dup IDs/Alt dup IDs/'
def idref(n):
    x = open(IDS + n + '.xml', encoding='utf-8-sig').read(); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', x)
    return 'ref="%s\\\\%s" partitionGuid="%s"' % (re.search(r'name="Name">([^<]+)', x).group(1), pg.group(2), pg.group(1))
FONT = {'ECU_HELMET_2025_PURPLE_yellowFacemask': 'ECU_Block_NUM_Array_A', 'ECU_HELMET_2021_PURPLE_yellowFacemask': 'ECU_Block_NUM_Array_A',
        'ECU_HELMET_2021_WHITESCRIPT': 'ECU_Block_NUM_Array_B', 'ECU_HELMET_2021_BLACKOUT': 'ECU_Block_NUM_Array_B', 'ECU_HELMET_2021_AWAYOPT': 'ECU_Block_NUM_Array_B',
        'ECU_HELMET_2021_WHITE': 'ECU_GS_Helmet_NUM_Array', 'ECU_HELMET_2026_GHOST': 'ECU_GS_Helmet_NUM_Array'}
for h, n in FONT.items():
    p = H + h + '.xml'; t = open(p, encoding='utf-8-sig').read()
    t, c = re.subn(r'ref="content/characters/player/parts/uniforms/jerseys/numbers/[A-Za-z0-9_]+_NUM_Array\\\\[^"]*" partitionGuid="[^"]*"', lambda m: idref(n), t); assert c == 1, (h, c)
    open(p, 'w', encoding='utf-8-sig', newline='').write(t); print('%-40s -> %s' % (h, n))
