# White Alt jersey (used by Away + Away Option): jersey palette primary white, secondary ECU purple
# -> TeamColor gloves white with purple; cleats: Away WHISEC (white/purple), Away Option WHIBLA.
import os, re, uuid, xml.etree.ElementTree as ET
R = os.environ.get('ECU_PROJECT_DIR', '.'); SRC = R + '/Backups/ECU part items/ECU Wrappers/U_ECU_JERSEY_2026_WHITEALT.xml'
OUT = R + '/Builds/White Alt palette'; os.makedirs(OUT, exist_ok=True)
WHITE = [0.6375968, 0.6375968, 0.7454042]       # global_white (linear)
PURPLE = [0.0409152, 0.0202885624, 0.122138776]  # ECU_Purple (linear)
t = open(SRC, encoding='utf-8-sig').read()
def cv(g, xyz): return ('\t<instance guid="%s" type="ColorVisuals" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="ColorChannels">\n\t\t\t<complex type="Vec4">\n'
    '\t\t\t\t<field name="x">%s</field>\n\t\t\t\t<field name="y">%s</field>\n\t\t\t\t<field name="z">%s</field>\n\t\t\t\t<field name="w">1</field>\n\t\t\t</complex>\n\t\t</field>\n'
    '\t\t<field name="ColorLookup">ColorLookup_NoLookup</field>\n\t</instance>\n') % (g, *xyz)
pal, p1, p2 = (str(uuid.uuid4()) for _ in range(3))
t, c = re.subn(r'<field name="ItemPalette" ref="null" />', '<field name="ItemPalette" ref="%s" />' % pal, t, count=1); assert c == 1, 'ItemPalette not null'
t = t.replace('</partition>', ('\t<instance guid="%s" type="PaletteVisuals" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="QuaternaryColor" ref="null" />\n'
    '\t\t<field name="PrimaryColor" ref="%s" />\n\t\t<field name="SecondaryColor" ref="%s" />\n\t\t<field name="TertiaryColor" ref="null" />\n\t</instance>\n') % (pal, p1, p2) + cv(p1, WHITE) + cv(p2, PURPLE) + '</partition>')
p = OUT + '/U_ECU_JERSEY_2026_WHITEALT.xml'; open(p, 'w', encoding='utf-8-sig', newline='').write(t); ET.parse(p); print('written', p)
