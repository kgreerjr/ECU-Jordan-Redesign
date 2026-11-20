"""Test: turn on EA's captain patch on the Home jersey (PURPLEALT) - visible in the dynasty roster editor.
Patch art = EA's CAPTAIN_04 block "C" (looked up by texture NAME, shared bundle).
Colors are deliberately three different ones so the in-game test shows which
channel each palette color drives:  Color1 = PURPLE, Color2 = GOLD, Color3 = WHITE (Home numbers: white, gold outline).
Expectation from the art: B = fill, G = inner outline, R = outer edge."""
import re, sys
part, wrap = sys.argv[1], sys.argv[2]
STYLE = 'CAPTAIN_04_Decal_2022'
COLORS = {'captainpatch_Color1': (0.0409152, 0.0202886, 0.1221388),            # ECU purple (expected: outer edge)
          'captainpatch_Color2': (0.9734453, 0.462077, 0),            # ECU gold (linear)
          'captainpatch_Color3': (1, 1, 1)}                                   # white (expected: fill)

s = open(part, encoding='utf-8').read()
cp = re.search(r'<complex type="CaptainPatch">(.*?)</complex>', s, re.S).group(1)
refs = dict(re.findall(r'name="(captainpatch_\w+)" ref="([0-9a-f-]{36}|null)"', cp))
def set_texname(g, name):
    global s
    s, n = re.subn(r'(<instance guid="' + g + r'" type="TextureMap"[^>]*>\s*<field name="TextureName">)[^<]*(</field>)',
                   lambda m: m.group(1) + name + m.group(2), s)
    assert n == 1, g
set_texname(refs['captainpatch_texture_map'], STYLE + '_col')
set_texname(refs['captainpatch_Norm'], STYLE + '_norm')
set_texname(refs['captainpatch_RSM'], STYLE + '_rsm')
for k, (x, y, z) in COLORS.items():
    g = refs[k]; assert g != 'null', k
    m = re.search(r'(<instance guid="' + g + r'" type="ColorValue"[^>]*>)(.*?)(</instance>)', s, re.S)
    body = m.group(2)
    for c, v in (('x', x), ('y', y), ('z', z)):
        body = re.sub(r'(<field name="' + c + r'">)[^<]*(</field>)', lambda mm: f'{mm.group(1)}{v}{mm.group(2)}', body, count=1)
    s = s[:m.start(2)] + body + s[m.end(2):]
assert '<field name="captainPatch">E_CPATCH_ON</field>' in s
open(part, 'w', encoding='utf-8', newline='').write(s)

if wrap == '-':
    print('captain patch test built (wrapper: tick IsCaptainPatchEnabled in Frosty)'); sys.exit()
w = open(wrap, encoding='utf-8').read()
w, n = re.subn(r'<field name="IsCaptainPatchEnabled">false</field>', '<field name="IsCaptainPatchEnabled">true</field>', w)
assert n == 1
open(wrap, 'w', encoding='utf-8', newline='').write(w)
print('captain patch test built')
