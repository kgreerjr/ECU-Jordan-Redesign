"""ITEM 6.5 - helmet bumpers (6.0).
Front bumper = "ECU", back bumper = jersey wordmark, bumper color = shell
(TI gunmetal kept, Home Option ECU Purple, Jolly Roger charcoal).
Edits FINAL/Helmets in place. Usage: python build_bumpers_60.py <Helmets dir>"""
import re, sys, os

D = sys.argv[1] if len(sys.argv) > 1 else '.'
T = 'content/characters/player/parts/uniforms/helmets/decals/teams/'
FRONT_ECU = f'ref="{T}ECU_Bumper_Front_ECU_col\\\\d1712d23-f81c-2b1c-d24b-5772dcf9d7ca" partitionGuid="2e5c64a0-48c3-4a96-823f-55d89244f156"'
BACK_EC   = f'ref="{T}ECU_Bumper_Back_EC_col\\\\63a42958-3068-fa30-8915-3bcfcca4d356" partitionGuid="6a625957-cd5b-420a-a3ab-64ea43fe1c1d"'
BACK_ECJR = f'ref="{T}ECU_Bumper_Back_EC_JR_col\\\\380d1621-4821-a53e-85fa-965c56716da7" partitionGuid="30c32230-ec19-4689-9d8a-fadb734adebd"'
PIRATES   = f'ref="{T}ECU_Helmet_2021_WHI_FrontLogo_col\\\\43754f42-7c48-0345-4d32-af2527c5614d" partitionGuid="befcd250-7832-11ed-9d32-9ebf70faa4af"'
PIR_NORM  = f'ref="{T}ECU_Helmet_2021_WHI_FrontLogo_norm\\\\8accbaed-ee21-8509-1994-87592e1f216b" partitionGuid="bf32d6b5-7832-11ed-9d32-9ebf70faa4af"'
TC = 'content/characters/player/parts/uniforms/team_colors/'
RC = 'ContentShared/characters/player/parts/uniforms/recipe/colors/'
GOLD   = f'ref="{TC}ECU_Gold\\\\7b0ba81a-2b4a-4470-9dfd-058c0e4d7a90" partitionGuid="a26c629e-6152-4001-9d0b-dd4442f6bc7c"'
PURPLE = f'ref="{TC}ECU_Purple\\\\46d33457-94a7-4c4c-8f0c-d4ddd7113d71" partitionGuid="c76ded6f-7cf2-4520-a156-522e523c721e"'
WHITE  = f'ref="{RC}global_whiteHelmet\\\\fc247258-b15a-4094-b541-6add49a910ff" partitionGuid="be62a1d8-5761-436e-8486-d6c2be0f7e33"'
BLACK  = f'ref="{RC}global_blackHelmet\\\\49e2220c-3481-490f-9171-772f8c1b4f9d" partitionGuid="183a2cf5-84a3-4c3b-be24-93edaa6bd965"'
OFFWH  = f'ref="{RC}global_offWhiteHelmetShell\\\\634ef185-ddb2-444e-89ac-a731b5d1be9c" partitionGuid="9e9e0912-0a3d-405d-8090-0f76b07d4180"'
SHELL = 'SHELL'   # = whatever the Helmet Shell layer's colorR points at
KEEP = None
NULL = 'ref="null"'

# front ECU transform (TI/Ghost values) and back transforms (Home's EAST CAROLINA values)
TF_FRONT = (0.45, 0.45, 0, 0.03)
TF_X1    = (0.45, 0.7, 0, 0)
TF_BACK  = (0.76, 0.9, 0, -0.03)
# PIRATES art is ~2x taller than EAST CAROLINA for its width, so it runs 70% size on the back
PIR_K = 0.7
TF_X1_PIR   = (round(0.45*PIR_K,4), round(0.7*PIR_K,4), 0, 0)
TF_BACK_PIR = (round(0.76*PIR_K,4), round(0.9*PIR_K,4), 0, -0.03)

# per helmet: front (tex, norm, rsm, tints RGB) | back (tex, norm, tints) | bumper color
PLAN = {
 # Home: purple shell, gold|white|gold stripe
 'ECU_HELMET_2025_PURPLE_yellowFacemask': dict(front=(GOLD, WHITE, PURPLE), back=('PIR', (GOLD, GOLD, GOLD)), bumper=SHELL),
 # Home Option: purple chrome, bumper ECU Purple
 'ECU_HELMET_2021_PURPLE_yellowFacemask': dict(front=(GOLD, WHITE, PURPLE), back=('PIR', (GOLD, GOLD, GOLD)), bumper=PURPLE),
 # Black Pirate: black, gold|purple|gold
 'ECU_HELMET_2021_BLACKOUT':  dict(front=(GOLD, PURPLE, GOLD), back=('PIR', (GOLD, GOLD, GOLD)), bumper=BLACK),
 # Away Option: same helmet look, EAST CAROLINA back
 'ECU_HELMET_2021_AWAYOPT':   dict(front=(GOLD, PURPLE, GOLD), back=('EC', (GOLD, GOLD, NULL)), bumper=BLACK),
 # Away / TI / Ghost: front already ECU; back NO QUARTER -> EAST CAROLINA, text colors kept
 'ECU_HELMET_2021_WHITESCRIPT': dict(front=(PURPLE, GOLD, PURPLE), back=('EC', KEEP), bumper=OFFWH),
 'ECU_HELMET_2021_WHITE':       dict(front=None, back=('EC', KEEP), bumper=KEEP),   # gunmetal stays
 'ECU_HELMET_2026_GHOST':       dict(front=None, back=('EC', KEEP), bumper=SHELL),
 # Jolly Roger: charcoal, gold|white|gold
 'ECU_HELMET_2025_PURPLE_purpleFacemask': dict(front=(GOLD, WHITE, SHELL), back=('ECJR', (GOLD, GOLD, NULL)), bumper=SHELL),
}

def layer_span(s, label):
    """(start, end) of the Overlay/Material instance complex whose info label == label"""
    m = re.search(r'<field name="label">' + re.escape(label) + r'</field>', s)
    assert m, label
    st = max(s.rfind('<complex type="LayerCompOverlayInstance">', 0, m.start()),
             s.rfind('<complex type="LayerCompMaterialInstance">', 0, m.start()))
    en = re.search(r'<field name="(overlay|material)_transform" ref="[^"]*" />', s[m.end():]).end() + m.end()
    return st, en

def sub_field(blk, name, newref):
    new, n = re.subn(r'(<field name="' + name + r'" )ref="[^"]*"(?: partitionGuid="[^"]*")?', lambda mm: mm.group(1) + newref, blk, count=1)
    assert n == 1, name
    return new

def set_transform(s, blk, vals):
    g = re.search(r'overlay_transform" ref="([0-9a-f-]{36})"', blk)
    assert g, 'transform is external'
    g = g.group(1)
    m = re.search(r'(<instance guid="' + g + r'"[^>]*>)(.*?)(</instance>)', s, re.S)
    body = m.group(2)
    su, sv, ou, ov = vals
    for k, v in (('scaleU', su), ('scaleV', sv), ('offsetU', ou), ('offsetV', ov),
                 ('x', su), ('y', sv), ('z', ou), ('w', ov)):
        body = re.sub(r'(<field name="' + k + r'">)[-\d.eE]+(</field>)', lambda mm: f'{mm.group(1)}{v}{mm.group(2)}', body, count=1)
    return s[:m.start(2)] + body + s[m.end(2):]

def shell_ref(s):
    a, b = layer_span(s, 'Helmet Shell')
    r = re.search(r'name="colorR" (ref="[^"]*"(?: partitionGuid="[^"]*")?)', s[a:b]).group(1)
    return r

for name, p in PLAN.items():
    path = os.path.join(D, name + '.xml')
    s = open(path, encoding='utf-8').read()
    sh = shell_ref(s)
    R = lambda r: sh if r == SHELL else r

    # front
    if p['front']:
        for lab in ('Frontplate', 'Frontplate_Schutt'):
            a, b = layer_span(s, lab); blk = s[a:b]
            blk = sub_field(blk, 'colorTexture', FRONT_ECU)
            blk = sub_field(blk, 'rsmTexture', FRONT_ECU)      # same as Away/TI/Ghost
            blk = sub_field(blk, 'normalTexture', NULL)        # drop PIRATES emboss
            for c, t in zip('RGB', p['front']):
                blk = sub_field(blk, 'color' + c, R(t))
            s = s[:a] + blk + s[b:]
            s = set_transform(s, blk, TF_FRONT)

    # back
    kind, tints = p['back']
    for lab, tf in (('Backplate_X1', TF_X1_PIR if kind == 'PIR' else TF_X1), ('Backplate', TF_BACK_PIR if kind == 'PIR' else TF_BACK)):
        a, b = layer_span(s, lab); blk = s[a:b]
        if kind == 'PIR':
            blk = sub_field(blk, 'colorTexture', PIRATES)
            blk = sub_field(blk, 'normalTexture', PIR_NORM)
        elif kind == 'EC':
            blk = sub_field(blk, 'colorTexture', BACK_EC)       # keeps WHI_BackLogo_norm (EAST CAROLINA emboss)
        else:
            blk = sub_field(blk, 'colorTexture', BACK_ECJR)
            blk = sub_field(blk, 'normalTexture', NULL)
        blk = sub_field(blk, 'rsmTexture', NULL)
        if tints:
            for c, t in zip('RGB', tints):
                blk = sub_field(blk, 'color' + c, R(t))
        s = s[:a] + blk + s[b:]
        s = set_transform(s, blk, tf)

    # bumper color
    if p['bumper'] is not KEEP:
        for lab in ('Frontplates', 'Backplates'):
            a, b = layer_span(s, lab); blk = s[a:b]
            blk = sub_field(blk, 'colorR', R(p['bumper']))
            s = s[:a] + blk + s[b:]

    open(path, 'w', encoding='utf-8', newline='').write(s)
    print('built', name)
