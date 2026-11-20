# ECU uniform-set lineup (user's spec). Rewrites 6 U_UniformType_ECU_* sets + the TeamVisuals Uniforms order.
# Unused sets stay in the game files but are dropped from ECU's list; Current7thAlternate = Treasure Island (ALT3).
import os, re, xml.etree.ElementTree as ET
R = os.environ.get('ECU_PROJECT_DIR', '.'); SRC = R + '/Backups/ECU uniform sets/'
TV = R + '/FINAL/TeamVisuals/ECUXXX_TeamVisuals.xml'; OUT = R + '/Builds/Jolly Roger/Uniform sets/'; os.makedirs(OUT, exist_ok=True)
SLOT = {'helmet': 'HeadWear', 'jersey': 'OuterShirt', 'pants': 'OuterPants', 'socks': 'InnerSocks', 'shoeL': 'LeftShoe', 'shoeR': 'RightShoe'}
LINEUP = [   # (set file, display name, loadout type, helmet, jersey, pants, socks, shoes)
    ('CurrentHome',       'Home',         'TeamDark',  'U_ECU_HELMET_2025_PURPLE_yellowFacemask', 'U_ECU_JERSEY_2023_PURPLEALT', 'U_ECU_PANTS_2023_YELLOW',    'U_ECU_SOCKS_2023_WHITE', 'U_GENERIC_SHOESX_WHIPRI'),
    ('CurrentAway',       'Away',         'TeamLight', 'U_ECU_HELMET_2021_WHITESCRIPT',           'U_ECU_JERSEY_2026_WHITEALT',  'U_ECU_PANTS_2023_WHITE',     'U_ECU_SOCKS_2023_WHITE', 'U_GENERIC_SHOESX_WHISEC'),   # WHITEALT palette = white/purple -> SEC = purple
    ('Current3rdAlternate','Black Pirate','TeamDark',  'U_ECU_HELMET_2021_BLACKOUT',              'U_ECU_JERSEY_2023_BLACK',     'U_ECU_PANTS_2023_BLACK',     'U_ECU_SOCKS_2023_BLACK', 'U_GENERIC_SHOESX_BLABLA'),
    ('Current7thAlternate','Treasure Island','TeamDark', 'U_ECU_HELMET_2021_WHITE',             'U_ECU_JERSEY_2023_WHITE',     'U_ECU_PANTS_2023_WHITEALT',  'U_ECU_SOCKS_2023_WHITE', 'U_GENERIC_SHOESX_WHISEC'),   # white + jersey-palette secondary (metallic gold)
    ('Current6thAlternate','Jolly Roger', 'TeamDark',  'U_ECU_HELMET_2025_PURPLE_purpleFacemask', 'U_ECU_JERSEY_2023_PURPLE',    'U_ECU_Pants_2023_PURPLE',    'U_ECU_SOCKS_2023_BLACK', 'U_GENERIC_SHOESX_BLASEC'),
    ('CurrentAlternate',  'Home Option',  'TeamDark',  'U_ECU_HELMET_2021_PURPLE_yellowFacemask', 'U_ECU_JERSEY_2023_PURPLEALT', 'U_ECU_Pants_2023_PURPLEALT', 'U_ECU_SOCKS_2023_WHITE', 'U_GENERIC_SHOESX_WHIPRI'),
    ('Current2ndAlternate','Away Option', 'TeamLight', 'U_ECU_HELMET_2021_BLACKOUT',              'U_ECU_JERSEY_2026_WHITEALT',  'U_ECU_PANTS_2023_BLACK',     'U_ECU_SOCKS_2023_WHITE', 'U_GENERIC_SHOESX_WHIBLA'),
]
refs = []
for order, (f, name, lt, *items) in enumerate(LINEUP, 1):
    t = open(SRC + 'U_UniformType_ECU_%s.xml' % f, encoding='utf-8-sig').read()
    want = dict(zip(['helmet', 'jersey', 'pants', 'socks'], items[:4])); want['shoeL'] = want['shoeR'] = items[4]
    for k, v in want.items():
        pat = r'(<field name="ItemAssetName">)[^<]*(</field>(?:(?!</instance>).)*?<field name="SlotType">LoadoutSlot_%sOverride</field>)' % SLOT[k]
        t, c = re.subn(pat, lambda m, v=v: m.group(1) + v + m.group(2), t, count=1, flags=re.S); assert c == 1, (f, k)
    t = re.sub(r'(<field name="DisplayName">)[^<]*', lambda m: m.group(1) + name, t, 1)
    t = re.sub(r'(<field name="LoadoutType">)[^<]*', lambda m: m.group(1) + 'LoadoutType_' + lt, t, 1)
    t = re.sub(r'(<field name="DisplayOrder">)[^<]*', lambda m: m.group(1) + str(order), t, 1)
    p = OUT + 'U_UniformType_ECU_%s.xml' % f; open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p)
    pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', t)
    refs.append('\t\t\t<item ref="content/FootballCharacter/UniformVisuals/CFB/ECU/U_UniformType_ECU_%s\\\\%s" partitionGuid="%s" />' % (f, pg.group(2), pg.group(1)))
    print('%d. %-13s <- %-20s %s' % (order, name, f, ' / '.join(i.replace('U_ECU_', '').replace('U_GENERIC_', '') for i in items)))
tv = open(TV, encoding='utf-8-sig').read()
tv, c = re.subn(r'(<array name="Uniforms" type="ref\(PointerRef\)">\n).*?(\n\t\t</array>)', lambda m: m.group(1) + '\n'.join(refs) + m.group(2), tv, count=1, flags=re.S); assert c == 1
p = OUT + 'ECUXXX_TeamVisuals.xml'; open(p, 'w', encoding='utf-8-sig', newline='').write(tv); ET.parse(p)
assert 'JordanBrand_ItemTag' in tv and not re.search(r'[^\\]\\[0-9a-f]{8}-', tv); print('TeamVisuals: %d uniforms, Jordan brand kept' % tv.count('U_UniformType_ECU_') , '(incl. 2 practice refs)')
