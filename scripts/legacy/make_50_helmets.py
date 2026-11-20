# ITEM 5: the helmets for the 5.0 release = how they looked at 4.2 (every helmet change after 4.2 ships in 6.0; Ghost Ship is the exception).
#   Jolly Roger (2025_PURPLE_purpleFacemask): build_jolly_roger_helmet.py WITHOUT its 5.2 back-number step
#   Treasure Island (2021_WHITE): build_treasure_island.py helmet WITHOUT its two 5.2 lines (back number + AAC gunmetal)
#   Black Pirate / Away Option (2021_BLACKOUT): the 4.0 matte build (Builds/Blackout matte)
#   Away (2021_WHITESCRIPT) + the 8 stock helmets: REVERT in Frosty (they were unmodded at 4.2)
import os, re, shutil, xml.etree.ElementTree as ET
R = os.environ.get('ECU_PROJECT_DIR', '.'); T = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
V = R + '/5.0 helmets'; os.makedirs(V, exist_ok=True)
# Jolly Roger
s = open(T + 'build_jolly_roger_helmet.py', encoding='utf-8').read(); cut = s.index('# 5.2 (user)')
g = {}; exec(s[:cut], g); t = g['t']
p = V + '/ECU_HELMET_2025_PURPLE_purpleFacemask.xml'; open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p); print('Jolly Roger helmet: 4.2 state (no 5.2 number move)')
# Treasure Island (helmet only; nothing else is written)
s = open(T + 'build_treasure_island.py', encoding='utf-8').read()
lines = [l for l in s.split('\n') if not (l.startswith('H.tint(') and '# 5.2' in l)]; assert len(s.split('\n')) - len(lines) == 2
s = '\n'.join(lines)
s = s.replace("wr(OUT + '/Helmet/ECU_HELMET_2021_WHITE.xml'", "WR50(V + '/ECU_HELMET_2021_WHITE.xml'")
s = re.sub(r"\bwr\(OUT \+ '/(Jerseys|Wrapper|Pants)/", "NOWR(OUT + '/", s); assert 'wr(OUT' not in s
def WR50(p, x): open(p, 'w', encoding='utf-8-sig', newline='').write(x); ET.parse(p)
g = {'V': V, 'WR50': WR50, 'NOWR': lambda *a: None, '__file__': T + 'build_treasure_island.py'}; exec(s, g); print('Treasure Island helmet: 4.2 state (no 5.2 number/AAC recolor)')
# Blackout (4.0 matte)
shutil.copy(R + '/Builds/Blackout matte/ECU_HELMET_2021_BLACKOUT.xml', V + '/ECU_HELMET_2021_BLACKOUT.xml'); print('Blackout helmet: 4.0 matte build')
open(V + '/README.txt', 'w').write('''5.0 release helmets (ITEM 5). Import ONLY into the 5.0 project, never the 6.0 copy.
IMPORT (3):  ECU_HELMET_2025_PURPLE_purpleFacemask (Jolly Roger), ECU_HELMET_2021_WHITE (Treasure Island), ECU_HELMET_2021_BLACKOUT (Black Pirate / Away Option)
REVERT in Frosty (9): ECU_HELMET_2021_WHITESCRIPT (Away), 2025_PURPLE_yellowFacemask, 2021_PURPLE_yellowFacemask, 2025_PURPLESCRIPT,
  2025_PURPLETEXT, 2025_WHITEUSA, 2021_WHITE_yellowFacemask, 2025_WHITE_blackfacemask, 2021_BLACKSCRIPT
KEEP: ECU_HELMET_2026_GHOST (Ghost Ship ships with the new back layout + triple stripe as the 6.0 teaser)
Also: CJ2K sticker texture ECU_CJ2K_Sticker_col stays (Ghost Ship uses it).
''')
