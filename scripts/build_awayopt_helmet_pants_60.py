# 6.0 rule (mod author): no uniform shares a helmet, jersey or pants. Away Option gets its own copies of Black Pirate's helmet + pants.
#   ECU_HELMET_2021_AWAYOPT + U_ECU_HELMET_2021_AWAYOPT (Id 91726005), ECU_PANTS_2023_AWAYOPT + U_ECU_PANTS_2023_AWAYOPT (Id 91726006)
#   Content = FINAL BLACKOUT helmet / BLACK pants (identity = the mod author's duplicates). Preset Current2ndAlternate -> new wrappers.
#   Usage: python3 build_awayopt_helmet_pants_60.py [helmet] [pants]
import os, re, sys
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_treasure_island.py'), encoding='utf-8').read()
exec(src[:src.index('# ---------------- jersey (base WHITE)')])
DUP = R + '/Builds/6.0/Dup exports/'
def identity(base_text, dup_xml):
    d = rd(dup_xml); pd = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', d); nd = re.search(r'name="Name">([^<]+)', d).group(1)
    pb = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', base_text); nb = re.search(r'name="Name">([^<]+)', base_text).group(1)
    return base_text.replace(pb.group(1), pd.group(1)).replace(pb.group(2), pd.group(2)).replace('>%s<' % nb, '>%s<' % nd)
def wrapper(name, iid, disp, old_part, new_part):
    W = rd(DUP + name + '.xml')
    W, c1 = re.subn(r'(<field name="Id">\s*<complex type="ItemDataId">\s*<field name="Id">)\d+<', lambda m: m.group(1) + str(iid) + '<', W, 1)
    W, c2 = re.subn(r'(<field name="DisplayName">)[^<]*', lambda m: m.group(1) + disp, W, 1)
    W, c3 = re.subn(r'(<field name="AssetName">)%s(</field>)' % old_part, lambda m: m.group(1) + new_part + m.group(2), W, 1)
    assert c1 == c2 == c3 == 1, name; return W
which = sys.argv[1:] or ['helmet', 'pants']
pre = F + '/Uniform sets/U_UniformType_ECU_Current2ndAlternate.xml'; u = rd(pre)
if 'helmet' in which:
    d = rd(DUP + 'ECU_HELMET_2021_AWAYOPT.xml'); assert 'type="HelmetPartItem"' in d
    wr(F + '/Helmets/ECU_HELMET_2021_AWAYOPT.xml', identity(rd(F + '/Helmets/ECU_HELMET_2021_BLACKOUT.xml'), DUP + 'ECU_HELMET_2021_AWAYOPT.xml'))
    wr(F + '/Wrappers/U_ECU_HELMET_2021_AWAYOPT.xml', wrapper('U_ECU_HELMET_2021_AWAYOPT', 91726005, 'Away Option Helmet', 'ECU_HELMET_2021_BLACKOUT', 'ECU_HELMET_2021_AWAYOPT'))
    if '>U_ECU_HELMET_2021_BLACKOUT<' in u: u = u.replace('>U_ECU_HELMET_2021_BLACKOUT<', '>U_ECU_HELMET_2021_AWAYOPT<')
    print('helmet: ECU_HELMET_2021_AWAYOPT (copy of Blackout) + wrapper 91726005')
if 'pants' in which:
    d = rd(DUP + 'ECU_PANTS_2023_AWAYOPT.xml'); assert 'type="PantsPartItem"' in d, 'ECU_PANTS_2023_AWAYOPT export is not a PantsPartItem (duplicate the part item, not the wrapper)'
    wr(F + '/Pants/ECU_PANTS_2023_AWAYOPT.xml', identity(rd(F + '/Pants/ECU_PANTS_2023_BLACK.xml'), DUP + 'ECU_PANTS_2023_AWAYOPT.xml'))
    wr(F + '/Wrappers/U_ECU_PANTS_2023_AWAYOPT.xml', wrapper('U_ECU_PANTS_2023_AWAYOPT', 91726006, 'Away Option Pants', 'ECU_PANTS_2023_BLACK', 'ECU_PANTS_2023_AWAYOPT'))
    if '>U_ECU_PANTS_2023_BLACK<' in u: u = u.replace('>U_ECU_PANTS_2023_BLACK<', '>U_ECU_PANTS_2023_AWAYOPT<')
    print('pants: ECU_PANTS_2023_AWAYOPT (copy of Black pants) + wrapper 91726006')
wr(pre, u); print('preset Away Option ->', re.findall(r'<field name="ItemAssetName">([^<]*)', u))
