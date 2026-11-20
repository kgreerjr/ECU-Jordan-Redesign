"""Captain patches, Michigan layout.
Every ECU jersey: EA's CAPTAIN_01 "C" (Michigan's style), one color = that jersey's
number fill color (Color1/2/3 all the same ref, like Michigan), Michigan's patch
position/size, and the AAC conference logo moved/sized to Michigan's BIG10 values.
Wrappers: IsCaptainPatchEnabled = true.
Usage: python build_captain_60.py <Jerseys dir> [<Wrappers dir>]"""
import re, sys, os, glob

JD = sys.argv[1]; WD = sys.argv[2] if len(sys.argv) > 2 else None
STYLE = 'CAPTAIN_01_Decal_2022'
CP_TF   = dict(scaleU=0.03,  scaleV=0.0285, offsetU=-0.09,   offsetV=0.07,   rotate=0)   # Michigan size; above the AAC logo (Michigan's 0.1375 sits on PIRATES)
CONF_TF = dict(scaleU=0.045, scaleV=0.045,  offsetU=-0.0745, offsetV=-0.112, rotate=3)   # Michigan BIG10 size/tilt, nudged down + toward center to clear the C (on this layer +V = up)

def inst_span(s, g, typ):
    m = re.search(r'<instance guid="' + g + r'" type="' + typ + r'"[^>]*>(.*?)</instance>', s, re.S)
    assert m, (g, typ); return m

def set_tf(s, g, v):
    m = inst_span(s, g, 'LayerCompTransform'); body = m.group(1)
    vec = dict(x=v['scaleU'], y=v['scaleV'], z=v['offsetU'], w=v['offsetV'])
    for k, val in list(v.items()) + list(vec.items()):
        body, n = re.subn(r'(<field name="' + k + r'">)[^<]*(</field>)', lambda mm: f'{mm.group(1)}{val}{mm.group(2)}', body, count=1)
        assert n == 1, k
    return s[:m.start(1)] + body + s[m.end(1):]

for path in sorted(glob.glob(os.path.join(JD, '*.xml'))):
    s = open(path, encoding='utf-8').read()
    name = os.path.basename(path)[:-4]
    # number fill color = colorR of the jersey number array layer (ECU_Jersey_20xx_NUM_Array)
    num = re.search(r'colorTexture" ref="[^"]*ECU_Jersey_20\d\d_NUM_Array[^"]*"[^>]*/>.*?<field name="colorR" (ref="[^"]*"(?: partitionGuid="[^"]*")?)', s, re.S)
    assert num, name
    C = num.group(1)

    # captain patch block
    m = re.search(r'<complex type="CaptainPatch">(.*?)</complex>', s, re.S)
    cp = m.group(1)
    refs = dict(re.findall(r'name="(captainpatch_\w+)" ref="([0-9a-f-]{36})"', cp))
    for k in ('captainpatch_Color1', 'captainpatch_Color2', 'captainpatch_Color3'):
        cp, n = re.subn(r'(<field name="' + k + r'" )ref="[^"]*"(?: partitionGuid="[^"]*")?', lambda mm: mm.group(1) + C, cp); assert n == 1
    cp = re.sub(r'(<field name="captainPatch">)[^<]*', r'\1E_CPATCH_ON', cp)
    s = s[:m.start(1)] + cp + s[m.end(1):]
    for k, suf in (('captainpatch_texture_map', '_col'), ('captainpatch_Norm', '_norm'), ('captainpatch_RSM', '_rsm')):
        mm = inst_span(s, refs[k], 'TextureMap')
        body = re.sub(r'(<field name="TextureName">)[^<]*', lambda x: x.group(1) + STYLE + suf, mm.group(1))
        s = s[:mm.start(1)] + body + s[mm.end(1):]
    s = set_tf(s, refs['captainpatch_transform'], CP_TF)

    # AAC conference logo
    lm = re.search(r'<field name="label">AAC Logo</field>.{0,400}?<field name="overlay_transform" ref="([0-9a-f-]{36})"', s, re.S)
    assert lm, name + ' AAC'
    g = lm.group(1); assert s.count('ref="' + g + '"') == 1, 'AAC transform shared'
    s = set_tf(s, g, CONF_TF)
    open(path, 'w', encoding='utf-8', newline='').write(s)
    print(f'{name:28} C color = {C.split("/")[-1][:40]}')

if WD:
    for path in sorted(glob.glob(os.path.join(WD, 'U_ECU_JERSEY_*.xml'))):
        w = open(path, encoding='utf-8').read()
        w, n = re.subn(r'<field name="IsCaptainPatchEnabled">\w+</field>', '<field name="IsCaptainPatchEnabled">true</field>', w); assert n == 1
        open(path, 'w', encoding='utf-8', newline='').write(w)
        print('wrapper on:', os.path.basename(path))
