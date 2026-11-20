# 6.0 ITEM 8: jersey sleeve + pants stripes match each uniform's helmet stripe (canvas stripe plan).
# Sleeves: Stripe 1 / Stripe 2 = outer bands, Middle Stripe = center. Pants (ECU_Pants_2023_Stripe_01_col): R center, G outer, B gaps.
#   Home jersey (PURPLEALT): white|gold|white -> gold|white|gold   (pants YELLOW already purple|white|purple)
#   Jolly Roger jersey (PURPLE): purple|gold|purple -> gold|white|gold;  pants: -> gold|white|gold, charcoal gaps
# Originals: Backups/Before 6.0 stripes/
import os, re
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_treasure_island.py'), encoding='utf-8').read()
exec(src[:src.index('# ---------------- jersey (base WHITE)')])
J_, P_ = F + '/Jerseys/', F + '/Pants/'
def anyref(name):
    for d in (J_, P_):
        for f in os.listdir(d):
            m = re.search(r'ref="[^"]*/%s\\\\[^"]*" partitionGuid="[^"]*"' % name, rd(d + f))
            if m: return m.group(0)
    raise SystemExit(name)
GOLD, WHITE = anyref('ECU_Gold'), anyref('global_white')
def sleeves(p, outer, center):
    D = Doc(rd(p))
    for lab in ('Stripe 1', 'Stripe 2'): D.tint('R', outer, lab)
    D.tint('R', center, 'Middle Stripe'); wr(p, D.done())
sleeves(J_ + 'ECU_JERSEY_2023_PURPLEALT.xml', GOLD, WHITE); print('Home jersey: gold | white | gold')
sleeves(J_ + 'ECU_JERSEY_2023_PURPLE.xml', GOLD, WHITE); print('Jolly Roger jersey: gold | white | gold')
p = P_ + 'ECU_Pants_2023_PURPLE.xml'; D = Doc(rd(p))
D.tint('R', WHITE, 'Stripe'); D.tint('G', GOLD, 'Stripe'); D.tint('B', D.color([round(lin(c), 7) for c in (0x4A, 0x4A, 0x4F)]), 'Stripe')   # charcoal = JR body #4A4A4F
wr(p, D.done()); print('Jolly Roger pants: gold | white | gold, charcoal gaps')
# v2 (user): Treasure Island jersey + pants white | gold | white (TI's own metallic gold #B09257 center, game white outer; pants gaps gunmetal #5B5962)
TIG = [0.434, 0.287, 0.095]   # ND_MetallicGold (#B09257)
p = J_ + 'ECU_JERSEY_2023_WHITE.xml'; D = Doc(rd(p)); g = D.color(TIG)
for lab in ('Stripe 1', 'Stripe 2'): D.tint('R', WHITE, lab)
D.tint('R', g, 'Middle Stripe'); wr(p, D.done()); print('Treasure Island jersey: white | gold | white')
p = P_ + 'ECU_PANTS_2023_WHITEALT.xml'; D = Doc(rd(p))
D.tint('R', D.color(TIG), 'Stripe'); D.tint('G', WHITE, 'Stripe'); D.tint('B', D.color([round(lin(c), 7) for c in (0x5B, 0x59, 0x62)]), 'Stripe')
wr(p, D.done()); print('Treasure Island pants: white | gold | white, gunmetal gaps')
