# "Black Helmet 2" (ECU_HELMET_2021_BLACKOUT) -> matte: borrow the Kansas black finish by name (same as Jolly Roger / Troy MATTEBLACK).
# Stock BLACKOUT uses ECU_HELMET_2021_BLACK_preset, whose ES parent is helmet_shell_preset_satin_ES. Colors untouched (global_blackHelmet shell).
import os, re, xml.etree.ElementTree as ET
R = os.environ.get('ECU_PROJECT_DIR', '.'); SRC = R + '/Backups/ECU helmets/Part items/ECU_HELMET_2021_BLACKOUT.xml'
OUT = R + '/Builds/Blackout matte'; os.makedirs(OUT, exist_ok=True)
t = open(SRC, encoding='utf-8-sig').read()
for old, new in (('ECU_HELMET_2021_BLACK_preset', 'KU_HELMET_2021_BLACK_preset'), ('ECU_HELMET_2021_BLACK_preset_ES_appearance', 'KU_HELMET_2021_BLACK_preset_ES_appearance')):
    assert t.count('>%s<' % old) == 1, old; t = t.replace('>%s<' % old, '>%s<' % new)
p = OUT + '/ECU_HELMET_2021_BLACKOUT.xml'; open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p)
print(re.findall(r'AssetName">([^<]+)', t)); print('written', p)
