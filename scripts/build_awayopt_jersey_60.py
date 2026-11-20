# 6.0: Away Option gets its own white jersey (gold | purple | gold sleeves, matching its Blackout helmet and black pants).
# New pieces (nothing overwritten): ECU_JERSEY_2026_AWAYOPT (content = FINAL WHITEALT, identity = the mod author's duplicate),
# U_ECU_JERSEY_2026_AWAYOPT (Id 91726004, same white/purple glove palette), preset Current2ndAlternate -> the new wrapper.
import os, re
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_treasure_island.py'), encoding='utf-8').read()
exec(src[:src.index('# ---------------- jersey (base WHITE)')])
DUP = R + '/Builds/6.0/Dup exports/'
def identity(base_text, dup_xml):
    d = rd(dup_xml); pd = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', d); nd = re.search(r'name="Name">([^<]+)', d).group(1)
    pb = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', base_text); nb = re.search(r'name="Name">([^<]+)', base_text).group(1)
    return base_text.replace(pb.group(1), pd.group(1)).replace(pb.group(2), pd.group(2)).replace('>%s<' % nb, '>%s<' % nd)
base = rd(F + '/Jerseys/ECU_JERSEY_2026_WHITEALT.xml'); J = Doc(identity(base, DUP + 'ECU_JERSEY_2026_AWAYOPT.xml'))
gold, purple = teamref(J.t, 'ECU_Gold'), teamref(J.t, 'ECU_Purple')
for lab in ('Stripe 1', 'Stripe 2'): J.tint('R', gold, lab)
J.tint('R', purple, 'Gold Stripe')
wr(F + '/Jerseys/ECU_JERSEY_2026_AWAYOPT.xml', J.done()); print('jersey: Away jersey with gold | purple | gold sleeves')
W = rd(DUP + 'U_ECU_JERSEY_2026_AWAYOPT.xml')
W, c1 = re.subn(r'(<field name="Id">\s*<complex type="ItemDataId">\s*<field name="Id">)\d+<', lambda m: m.group(1) + '91726004<', W, 1)
W, c2 = re.subn(r'(<field name="DisplayName">)[^<]*', lambda m: m.group(1) + 'Away Option Jersey', W, 1)
W, c3 = re.subn(r'(<field name="AssetName">)ECU_JERSEY_2026_WHITEALT(</field>)', lambda m: m.group(1) + 'ECU_JERSEY_2026_AWAYOPT' + m.group(2), W, 1)
assert c1 == c2 == c3 == 1; wr(F + '/Wrappers/U_ECU_JERSEY_2026_AWAYOPT.xml', W); print('wrapper: Id 91726004 -> ECU_JERSEY_2026_AWAYOPT')
p = F + '/Uniform sets/U_UniformType_ECU_Current2ndAlternate.xml'; u = rd(p); assert u.count('>U_ECU_JERSEY_2026_WHITEALT<') == 1
wr(p, u.replace('>U_ECU_JERSEY_2026_WHITEALT<', '>U_ECU_JERSEY_2026_AWAYOPT<')); print('preset Away Option -> U_ECU_JERSEY_2026_AWAYOPT')
