# Step 3 (as run for ECU): point each part item's logo layer at its pre-colored duplicate and
# set that layer's textures to AssetResolveRule_UseDefaults. Runs on the tinted part items
# (output of build_part_items_tinted.py) in the FINAL folder, editing them in place.
import os, re, glob, xml.etree.ElementTree as ET
ROOT = os.environ.get('ECU_PROJECT_DIR', '.'); F = ROOT + '/FINAL'
X = ROOT + '/Dup IDs/Colored dup IDs'
REF = {}
for f in glob.glob(X + '/*.xml'):
    t = open(f, encoding='utf-8-sig').read(); pg = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', t)
    nm = re.search(r'name="Name">([^<]+)', t).group(1)
    REF[nm.split('/')[-1]] = '<field name="colorTexture" ref="%s\\\\%s" partitionGuid="%s" />' % (nm, pg.group(2), pg.group(1))
PLAN = {'ECU_JERSEY_2023_WHITE': 'WT_PurpleOnWhite', 'ECU_JERSEY_2023_PURPLE': 'WT_GoldOnPurple', 'ECU_JERSEY_2023_PURPLEALT': 'WT_GoldOnPurple',
 'ECU_Pants_2023_PURPLEALT': 'WT_GoldOnPurple', 'ECU_JERSEY_2026_WHITEALT': 'PurpleOnWhite', 'ECU_PANTS_2023_WHITE': 'PurpleOnWhite',
 'ECU_PANTS_2023_WHITEALT': 'PurpleOnWhite', 'ECU_Pants_2023_PURPLE': 'GoldOnPurple', 'ECU_JERSEY_2023_BLACK': 'WhiteOnBlack',
 'ECU_PANTS_2023_BLACK': 'WhiteOnBlack', 'ECU_SOCKS_2023_BLACK': 'WhiteOnBlack', 'ECU_PANTS_2023_YELLOW': 'PurpleOnGold', 'ECU_SOCKS_2023_WHITE': 'BlackOnWhite'}
for f in sorted(glob.glob(F + '/*/ECU_*.xml')):
    name = os.path.basename(f)[:-4]; combo = PLAN[name]; t = open(f, encoding='utf-8-sig').read()
    i = t.index('>Jumpman Logo<'); ms = t.rindex('<complex type="LayerCompMaps">', 0, i); me = t.index('</complex>', ms)
    maps = re.sub(r'<field name="colorTexture" ref="[^"]*" partitionGuid="[^"]*" />', lambda m: REF['ECU_JM_%s_col' % combo], t[ms:me])
    maps = maps.replace('AssetResolveRule_UseOverrideRuleset', 'AssetResolveRule_UseDefaults')
    t = t[:ms] + maps + t[me:]; open(f, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(f); print(name, '->', combo)
