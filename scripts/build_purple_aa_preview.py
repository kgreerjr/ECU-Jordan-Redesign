"""Purple Away Alternate (preview, 2026-11-18): the Away Alternate jersey with a purple body.
Fabric purple; numbers + nameplate white (numbers keep the gold outline); chest ECU white / gold / purple;
sleeve skulls white with gold hat + linework; Jumpman gold-on-purple (Home's baked texture); AAC patch Home's colors.
Gold collar + cuffs unchanged. usage: build_purple_aa_preview.py <AWAYOPT jersey xml> <out xml> [purplehat]"""
import re, sys, xml.etree.ElementTree as ET
TC = 'content/characters/player/parts/uniforms/team_colors/'; RC = 'ContentShared/characters/player/parts/uniforms/recipe/colors/'
GOLD   = f'ref="{TC}ECU_Gold\\\\7b0ba81a-2b4a-4470-9dfd-058c0e4d7a90" partitionGuid="a26c629e-6152-4001-9d0b-dd4442f6bc7c"'
PURPLE = f'ref="{TC}ECU_Purple\\\\46d33457-94a7-4c4c-8f0c-d4ddd7113d71" partitionGuid="c76ded6f-7cf2-4520-a156-522e523c721e"'
WHITE  = f'ref="{RC}global_white\\\\40cdde98-1c5a-460c-b245-6d8d6903e422" partitionGuid="3c4ccc13-726b-4ac6-9fe1-3e25c50c8afd"'
JM_GOP = 'ref="ContentShared/characters/player/parts/uniforms/decals/vendors/ECU_JM_WT_GoldOnPurple_col\\\\1a3d6f7c-9c0b-9349-4333-0878e88ee8f1" partitionGuid="ddf625f3-3e63-4a13-8284-00d5b10e491a"'
src, out = sys.argv[1:3]; s = open(src, encoding='utf-8-sig').read()
def blocks(t):
    st = [m.start() for m in re.finditer(r'<complex type="LayerComp(?:MaterialInstance|OverlayInstance|ArrayOverlayInstance)">', t)]
    return [(a, st[i + 1] if i + 1 < len(st) else len(t)) for i, a in enumerate(st)]
def sub(blk, name, ref):
    new, n = re.subn(r'(<field name="' + name + r'" )ref="[^"]*"(?: partitionGuid="[^"]*")?', lambda m: m.group(1) + ref, blk, count=1); assert n == 1, name; return new
def apply(pred, **f):
    global s; hits = 0
    for a, b in reversed(blocks(s)):
        blk = s[a:b]
        if pred(blk):
            for k, v in f.items(): blk = sub(blk, k, v)
            s = s[:a] + blk + s[b:]; hits += 1
    return hits
lab = lambda L: (lambda blk: '<field name="label">%s</field>' % L in blk)
n = apply(lambda b: b.startswith('<complex type="LayerCompMaterialInstance">') and '/global_white\\' in b and re.search(r'colorR" ref="[^"]*global_white', b) is not None, colorR=PURPLE); print('fabric', n)
print('numbers', apply(lambda b: 'ECU_AA_NUM_Array' in b and 'ArrayOverlayInstance' in b[:60], colorR=WHITE))
print('nameplate', apply(lambda b: '_NAME_Array' in b and 'ArrayOverlayInstance' in b[:60], colorR=WHITE, colorG=WHITE))
print('ECU', apply(lab('ECU Logo'), colorR=WHITE, colorG=GOLD, colorB=PURPLE))
SKULL_HAT = PURPLE if (len(sys.argv) > 3 and sys.argv[3] == 'purplehat') else GOLD   # option A test: hat = jersey purple
print('skulls', apply(lambda b: '<field name="label">AA Skull' in b, colorG=SKULL_HAT))
print('jumpman', apply(lab('Jumpman Logo'), colorTexture=JM_GOP))
print('AAC', apply(lab('AAC Logo'), colorR=GOLD, colorG=WHITE, colorB=PURPLE))
open(out, 'w', encoding='utf-8-sig', newline='').write(s); ET.parse(out); print('wrote', out)
