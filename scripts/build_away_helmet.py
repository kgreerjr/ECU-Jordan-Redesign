# 5.2: Away helmet (ECU_HELMET_2021_WHITESCRIPT, stock otherwise) - center stripe full length.
# Stock stripe transform has w/offsetV -0.28, which stops the stripe above the back flag (same fix as Jolly Roger and Ghost Ship).
import os, re, xml.etree.ElementTree as ET
R = os.environ.get('ECU_PROJECT_DIR', '.'); SRC = R + '/Backups/ECU helmets/Part items/ECU_HELMET_2021_WHITESCRIPT.xml'
OUT = R + '/Builds/Away helmet'; os.makedirs(OUT, exist_ok=True)
t = open(SRC, encoding='utf-8-sig').read()
i = t.index('<field name="label">Center Stripe</field>'); tg = re.search(r'name="overlay_transform" ref="([0-9a-f-]{36})"', t[i:i + 600]).group(1)
a = t.index('<instance guid="%s"' % tg); b = t.index('</instance>', a)
seg, c1 = re.subn(r'(<field name="w">)[^<]*', r'\g<1>0', t[a:b], 1); seg, c2 = re.subn(r'(<field name="offsetV">)[^<]*', r'\g<1>0', seg, 1); assert c1 == c2 == 1
t = t[:a] + seg + t[b:]
p = OUT + '/ECU_HELMET_2021_WHITESCRIPT.xml'; open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p); print('written', p)
