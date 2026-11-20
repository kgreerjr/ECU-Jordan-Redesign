"""ITEM 9 - matching wordmarks (6.0).
Plan: EC = EAST CAROLINA, P = PIRATES. Jersey chest wordmark and helmet back bumper match.
  Home P, Away EC, Black Pirate P, Treasure Island P, Ghost Ship EC, Jolly Roger P,
  Home Option P, Away Option EC.
Changes:
  Black Pirate jersey      EC -> P  (ECU_Pirates_WM_* dups, Home's size/position, white kept)
  Treasure Island jersey   EC -> P  (same dups, TI gold kept)
  Jolly Roger helmet back  EC -> P  (WHI_FrontLogo_col, the texture it already loads; gold)
  Treasure Island helmet back EC -> P (ECU_Bumper_Back_P_col dup of BackLogo; TI gold)  [needs the dup XML]
Usage: python build_wordmarks_60.py <dir with the FINAL xmls> [ECU_Bumper_Back_P_col.xml]"""
import re, sys, os

D = sys.argv[1]
P_DUP = sys.argv[2] if len(sys.argv) > 2 else None

DEC = 'content/characters/player/parts/uniforms/decals/teams/'
HT = 'content/characters/player/parts/uniforms/helmets/decals/teams/'
TC = 'content/characters/player/parts/uniforms/team_colors/'

def dup_ref(xml):
    s = open(xml, encoding='utf-8-sig').read()
    pg, pi = re.search(r'<partition guid="([^"]+)" primaryInstance="([^"]+)"', s).groups()
    name = re.search(r'<field name="Name">([^<]+)</field>', s).group(1)
    return f'ref="{name}\\\\{pi}" partitionGuid="{pg}"'

DUPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dups')
WM_COL  = dup_ref(os.path.join(DUPS, 'ECU_Pirates_WM_col.xml'))
WM_NORM = dup_ref(os.path.join(DUPS, 'ECU_Pirates_WM_norm.xml'))
WM_RSM  = dup_ref(os.path.join(DUPS, 'ECU_Pirates_WM_rsm.xml'))
PIRATES = f'ref="{HT}ECU_Helmet_2021_WHI_FrontLogo_col\\\\43754f42-7c48-0345-4d32-af2527c5614d" partitionGuid="befcd250-7832-11ed-9d32-9ebf70faa4af"'
GOLD = f'ref="{TC}ECU_Gold\\\\7b0ba81a-2b4a-4470-9dfd-058c0e4d7a90" partitionGuid="a26c629e-6152-4001-9d0b-dd4442f6bc7c"'
NULL = 'ref="null"'

TF_JERSEY = (0.16, 0.15, 0, -0.163)            # Home's PIRATES
PIR_K = 0.7                                     # PIRATES backs run 70% of EAST CAROLINA size
TF_X1_PIR   = (round(0.45*PIR_K, 4), round(0.7*PIR_K, 4), 0, 0)
TF_BACK_PIR = (round(0.76*PIR_K, 4), round(0.9*PIR_K, 4), 0, -0.03)

def layer_span(s, label):
    m = re.search(r'<field name="label">' + re.escape(label) + r'</field>', s)
    assert m, label
    st = s.rfind('<complex type="LayerCompOverlayInstance">', 0, m.start())
    en = re.search(r'<field name="overlay_transform" ref="[^"]*" />', s[m.end():]).end() + m.end()
    return st, en

def sub_field(blk, name, newref):
    new, n = re.subn(r'(<field name="' + name + r'" )ref="[^"]*"(?: partitionGuid="[^"]*")?',
                     lambda mm: mm.group(1) + newref, blk, count=1)
    assert n == 1, name
    return new

def get_field(blk, name):
    return re.search(r'<field name="' + name + r'" (ref="[^"]*"(?: partitionGuid="[^"]*")?)', blk).group(1)

def set_transform(s, blk, vals):
    g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', blk).group(1)
    m = re.search(r'(<instance guid="' + g + r'"[^>]*>)(.*?)(</instance>)', s, re.S)
    body = m.group(2)
    su, sv, ou, ov = vals
    for k, v in (('scaleU', su), ('scaleV', sv), ('offsetU', ou), ('offsetV', ov),
                 ('x', su), ('y', sv), ('z', ou), ('w', ov)):
        body = re.sub(r'(<field name="' + k + r'">)[-\d.eE]+(</field>)', lambda mm: f'{mm.group(1)}{v}{mm.group(2)}', body, count=1)
    return s[:m.start(2)] + body + s[m.end(2):]

def load(n):  return open(os.path.join(D, n + '.xml'), encoding='utf-8').read()
def save(n, s): open(os.path.join(D, n + '.xml'), 'w', encoding='utf-8', newline='').write(s); print('built', n)

# jerseys: swap the "ECU Logo" layer to PIRATES, keep each jersey's own tints
for n in ('ECU_JERSEY_2023_BLACK', 'ECU_JERSEY_2023_WHITE'):
    s = load(n)
    a, b = layer_span(s, 'ECU Logo'); blk = s[a:b]
    blk = sub_field(blk, 'colorTexture', WM_COL)
    blk = sub_field(blk, 'rsmTexture', WM_RSM)
    blk = sub_field(blk, 'normalTexture', WM_NORM)
    s = s[:a] + blk + s[b:]
    s = set_transform(s, blk, TF_JERSEY)
    save(n, s)

# helmet backs -> PIRATES at 70%
def helmet_back(n, tex, tint):
    s = load(n)
    for lab, tf in (('Backplate_X1', TF_X1_PIR), ('Backplate', TF_BACK_PIR)):
        a, b = layer_span(s, lab); blk = s[a:b]
        t = tint or get_field(blk, 'colorR')          # None = keep the layer's own colour
        blk = sub_field(blk, 'colorTexture', tex)
        blk = sub_field(blk, 'normalTexture', NULL)
        blk = sub_field(blk, 'rsmTexture', NULL)
        for c in 'RGB':
            blk = sub_field(blk, 'color' + c, t)
        s = s[:a] + blk + s[b:]
        s = set_transform(s, blk, tf)
    save(n, s)

helmet_back('ECU_HELMET_2025_PURPLE_purpleFacemask', PIRATES, GOLD)     # Jolly Roger
if P_DUP:
    helmet_back('ECU_HELMET_2021_WHITE', dup_ref(P_DUP), None)           # Treasure Island, TI gold kept

# Black Pirate: drop the small pirate-head logo that sat above the old EAST CAROLINA (it overlaps PIRATES)
s = load('ECU_JERSEY_2023_BLACK')
a, b = layer_span(s, 'Logo ECU'); blk = s[a:b]
for f in ('colorTexture', 'rsmTexture', 'normalTexture'):
    blk = sub_field(blk, f, NULL)
s = s[:a] + blk + s[b:]
save('ECU_JERSEY_2023_BLACK', s)
