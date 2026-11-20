# 5.0 polish for Ghost Ship (ITEM 5). Post-processes the FINAL Ghost files IN PLACE.
# Revert copies: Backups/Ghost Ship pre-polish/
#  helmet: Away-style triple stripe (texture ECU_GS_Helmet_Stripe_col <- ECU_TripleStripe PNG, FiveStripe layout):
#          R center = gray, G outer = lavender, B gaps = shell; back number font = the jersey's (ECU_Jersey_2023_NUM_Array)
#  jersey: EAST CAROLINA = Away's (WHITEALT) whole ECU Logo layer; numbers = Away's font (ECU_Jersey_2023_NUM_Array) + Away's number size/placement block
#          (sleeve stripes were already lavender | gray | lavender)
#  pants:  stripe R center gray, G outer lavender, B gaps game white (same channel layout as Away's purple | gold | purple)
# Run build_helmet_numbers.py afterwards (Ghost gets Away's back spacing there).
import os, re
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_treasure_island.py'), encoding='utf-8').read()
exec(src[:src.index('# ---------------- jersey (base WHITE)')])          # Doc, rd, wr, ov_span, copy_overlay, lin, F
FIN = F + '/'
hexlin = lambda h: [round(lin(int(h[i:i + 2], 16)), 7) for i in (1, 3, 5)]
WHITE = [0.6375968, 0.6375968, 0.7454042]                                # global_white (game white, the Ghost body)
LAV, GRAY, SHELL = hexlin('#B9A2DC'), hexlin('#9A99A4'), hexlin('#E9EAF0')
GFILL, LOUT = 'ref="80c970a5-55f8-4103-935d-b2d8a4e6cfc4"', 'ref="3dfbbe09-59e8-4bff-850c-12013374f37d"'   # Ghost jersey's local gray fill / lavender outline
WA = rd(FIN + 'Jerseys/ECU_JERSEY_2026_WHITEALT.xml')
NUM23 = re.search(r'ref="[^"]*/ECU_Jersey_2023_NUM_Array\\\\[^"]*" partitionGuid="[^"]*"', WA).group(0)
def nblock(x):
    st = x.index('<complex type="number_offsetScaleSpacing">'); d = 0
    for m_ in re.finditer(r'<complex type="[^"]*">|</complex>', x[st:]):
        d += 1 if m_.group(0) != '</complex>' else -1
        if d == 0: return st, st + m_.end()
# ---- jersey ----
p = FIN + 'Jerseys/ECU_JERSEY_2026_GHOST.xml'; J = Doc(rd(p)); assert GFILL[5:-1] in J.t and LOUT[5:-1] in J.t
c_, d_ = ov_span(J.t, 'overlay_5'); assert 'ECU_JR_Pirates_col' in J.t[c_:d_], 'Ghost overlay_5 is not the PIRATES layer (already converted?)'
J.t = J.t[:c_] + re.sub(r'<field name="colorTexture" ref="[^"]*"( partitionGuid="[^"]*")? />', '<field name="colorTexture" ref="null" />', J.t[c_:d_], 1) + J.t[d_:]
copy_overlay(J, WA, 'ECU Logo', 'overlay_5', GFILL); J.tint('G', LOUT, 'ECU Logo')
# v2: numbers stay on the jersey's own ECU_Jersey_2021_NUM_Array + Jolly Roger size block. Away's 2023 array showed in the
# editor but NOT in game (not in this jersey's bundle) -> no numbers at all.
NUM21 = re.search(r'ref="[^"]*/ECU_Jersey_2021_NUM_Array\\\\[^"]*" partitionGuid="[^"]*"', J.t).group(0)
wr(p, J.done()); print('jersey: EAST CAROLINA (Away layer, gray/lavender); numbers unchanged (2021 font, JR size)')
# ---- pants ----
p = FIN + 'Pants/ECU_PANTS_2026_GHOST.xml'; P = Doc(rd(p))
P.tint('R', P.color(GRAY), 'Stripe'); P.tint('G', P.color(LAV), 'Stripe'); P.tint('B', P.color(WHITE), 'Stripe')
wr(p, P.done()); print('pants: stripe lavender | gray | lavender')
# ---- helmet ----
p = FIN + 'Helmets/ECU_HELMET_2026_GHOST.xml'; H = Doc(rd(p))
H.tint('R', H.color(GRAY), 'Center Stripe'); H.tint('G', H.color(LAV), 'Center Stripe'); H.tint('B', H.color(SHELL), 'Center Stripe')
assert H.t.count('CMU_Jersey_2021_NUM_Array') == 1
GSNUM = idref(R + '/Dup IDs/Alt dup IDs/ECU_GS_Helmet_NUM_Array.xml')   # v3: dup of CMU_Jersey_2021_NUM_Array (in the helmet's bundle) holding the ECU 2021 font art; v2 (direct ECU_Jersey_2021 ref) = no number in game
H.t = re.sub(r'ref="[^"]*/CMU_Jersey_2021_NUM_Array\\\\[^"]*" partitionGuid="[^"]*"', lambda m: GSNUM, H.t)   # v2: the jersey's font (2021); TEST IN GAME (bundle)
wr(p, H.done()); print('helmet: triple stripe tints, back number = ECU_GS_Helmet_NUM_Array (dup of CMU array, ECU 2021 font art)')
