# Master item list = CollegeFBCharacterPrefab > ItemRegistrarData.ItemInfos (one ItemInfo per wearable item: name, DisplayName, team, slot, ItemId).
# 1) register new duplicated items so the game can find them; 2) rename ECU pieces shown in the gear picker.
# usage: python3 build_item_registry.py   (reads Slot test/CollegeFBCharacterPrefab.xml -> Slot test/IMPORT these/CollegeFBCharacterPrefab.xml)
import os, re, uuid
R = os.environ.get('ECU_PROJECT_DIR', '.'); SRC = R + '/Backups/Slot test/CollegeFBCharacterPrefab.xml'; OUT = R + '/Backups/Slot test/IMPORT these/CollegeFBCharacterPrefab.xml'
NEW = [  # (ItemName, DisplayName, copy settings from, ItemId = wrapper's Id)
    ('U_ECU_JERSEY_2026_GHOST', 'Slot Test Jersey', 'U_ECU_JERSEY_2023_WHITE', 91726001),
]
RENAME = {
    'U_ECU_HELMET_2025_PURPLE_purpleFacemask': 'Jolly Roger Helmet', 'U_ECU_JERSEY_2023_PURPLE': 'Jolly Roger Jersey', 'U_ECU_Pants_2023_PURPLE': 'Jolly Roger Pants',
    'U_ECU_HELMET_2021_WHITE': 'Treasure Island Helmet', 'U_ECU_JERSEY_2023_WHITE': 'Treasure Island Jersey', 'U_ECU_PANTS_2023_WHITEALT': 'Treasure Island Pants',
    'U_ECU_HELMET_2021_BLACKOUT': 'Matte Black Helmet',
}
t = open(SRC, encoding='utf-8-sig').read()
def info(name):
    ms = [m for m in re.finditer(r'\t<instance guid="([^"]+)" type="ItemInfo"[^>]*>.*?</instance>\n', t, re.S) if '<field name="ItemName">%s</field>' % name in m.group(0)]
    assert len(ms) == 1, (name, len(ms)); return ms[0]
for name, disp in RENAME.items():
    m = info(name); blk = re.sub(r'(<field name="DisplayName">)[^<]*', lambda x: x.group(1) + disp, m.group(0), 1); t = t[:m.start()] + blk + t[m.end():]
arr = t.index('<array name="ItemInfos" type="ref(PointerRef)">'); end = t.index('\t\t</array>', arr); add_refs = ''; add_inst = ''
for name, disp, base, iid in NEW:
    assert '>%s<' % name not in t, name + ' already registered'; assert '<field name="ItemId">%d</field>' % iid not in t, 'ItemId in use'
    g = str(uuid.uuid4()); b = info(base).group(0)
    b = b.replace(info(base).group(1), g).replace('>%s<' % base, '>%s<' % name)
    b = re.sub(r'(<field name="DisplayName">)[^<]*', lambda x: x.group(1) + disp, b, 1); b = re.sub(r'(<field name="ItemId">)\d+', lambda x: x.group(1) + str(iid), b, 1)
    add_inst += b; add_refs += '\t\t\t<item ref="%s" />\n' % g
t = t[:end] + add_refs + t[end:]; t = t.replace('</partition>', add_inst + '</partition>')
os.makedirs(os.path.dirname(OUT), exist_ok=True); open(OUT, 'w', encoding='utf-8-sig', newline='').write(t)
import xml.etree.ElementTree as ET; ET.parse(OUT); print('registered', [n[0] for n in NEW], '| renamed', len(RENAME))
