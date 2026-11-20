# ITEM 16 rollout: No Quarter flag on the other 7 helmets (Away = the approved reference, done by hand).
# Away moves (orig -> final): Flag -0.1725 -> -0.1747, NQ at the old CJ2K spot -0.001, CJ2K to the old AAC spot +0.0032 inward,
# number x -0.0134. Treasure Island stickers are 1.176x larger, so its moves scale by 1.176.
# Greenville Nights (one row: NQ | number | CJ2K): NQ mirrors CJ2K, 0.0032 farther out (NQ art is that much wider than CJ2K's).
# usage: rollout_noquarter.py <Helmets dir> <ECU_Helmet_NoQuarter_col.xml>
import re, sys, os, subprocess
D, DUP = sys.argv[1:3]
HERE = os.path.dirname(os.path.abspath(__file__))
#        file                                   flag      NQ (u, v)          CJ2K (u, v)         number x
PLAN = {
 'ECU_HELMET_2025_PURPLE_yellowFacemask': (-0.1747, (0.179, 0.274), (-0.1758, 0.03), 0.3006),   # Home
 'ECU_HELMET_2021_BLACKOUT':              (-0.1747, (0.179, 0.274), (-0.1758, 0.03), 0.3006),   # Black Pirate
 'ECU_HELMET_2026_GHOST':                 (-0.1747, (0.179, 0.274), (-0.1758, 0.03), 0.3086),   # Ghost Ship
 'ECU_HELMET_2025_PURPLE_purpleFacemask': (-0.1747, (0.179, 0.274), (-0.1758, 0.03), 0.2826),   # Jolly Roger
 'ECU_HELMET_2021_WHITE':                 (-0.1421, (0.1408, 0.274), (-0.1422, 0.03), 0.2302),  # Treasure Island
 'ECU_HELMET_2021_AWAYOPT':               (-0.1072, (0.100, 0.274), (-0.1078, 0.03), 0.1626),   # White Alternate
 'ECU_HELMET_2021_PURPLE_yellowFacemask': (None,    (-0.1249, 0.03), None,           None),     # Greenville Nights
}
def tf(s, label, u, v):
    i = s.index('<field name="label">%s</field>' % label)
    a = s.rfind('<complex type="LayerCompOverlayInstance">', 0, i)
    g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', s[a:]).group(1)
    m = re.search(r'(<instance guid="' + g + r'"[^>]*>)(.*?)(</instance>)', s, re.S); body = m.group(2)
    for k, val in (('offsetU', u), ('offsetV', v), ('z', u), ('w', v)):
        body, n = re.subn(r'(<field name="%s">)[^<]*' % k, lambda mm: mm.group(1) + str(val), body, count=1); assert n == 1
    return s[:m.start(2)] + body + s[m.end(2):]
for name, (flag, nq, cj, num) in PLAN.items():
    H = os.path.join(D, name + '.xml')
    subprocess.run([sys.executable, os.path.join(HERE, 'build_helmet_noquarter.py'), H, DUP], check=True)
    s = open(H, encoding='utf-8-sig').read()
    if flag is not None: s = tf(s, 'Flag', flag, 0.274)
    s = tf(s, 'AAC  Decal', *nq)
    if cj: s = tf(s, 'CJ2K Sticker', *cj)
    if num is not None:
        i = s.index('name="backnumberoffset_scale"')
        j = s.index('<field name="x">', i); k = s.index('</field>', j)
        s = s[:j] + '<field name="x">%s' % num + s[k:]
    open(H, 'w', encoding='utf-8-sig', newline='').write(s); print('  placed', name)
