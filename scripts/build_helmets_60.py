# ITEM 6 (6.0): Away-style triple stripes (FiveStripe layout: R center, G outer, B gaps = shell) on Home, Black Pirate/Away Option, Jolly Roger.
# Matte decals (metal 0 / refl 0.4 / smooth 0.35), no stripe rsm. Post-processes FINAL/Helmets in place; run build_helmet_numbers.py after.
#  Blackout (2021 shell): WHITESCRIPT's 2021 Center Stripe layer, texture ECU_GS_Helmet_Stripe_col (dup of BLA_Decal, in this helmet's bundle) - gold | purple | gold, black gaps
#  Home (2025 shell):     Jolly Roger's 2025 Center Stripe layer, texture ECU_JR_Helmet_Stripe_col (dup of WHI_Decal_01) - gold | white | gold, purple gaps
#  Jolly Roger (2025):    same texture (re-imported with the triple art) - gold | white | gold, charcoal gaps
# Originals: Backups/Before helmet stripes/
import os, re, uuid
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_treasure_island.py'), encoding='utf-8').read()
exec(src[:src.index('# ---------------- jersey (base WHITE)')])          # Doc, rd, wr, ov_span, idref, lin, F
H_ = F + '/Helmets/'; IDS = R + '/Dup IDs/Alt dup IDs/'; STOCK = R + '/Backups/ECU helmets/Part items/'
def anyref(name):
    for f in os.listdir(STOCK) + os.listdir(H_):
        p = (STOCK if os.path.exists(STOCK + f) else H_) + f
        m = re.search(r'ref="[^"]*/%s\\\\[^"]*" partitionGuid="[^"]*"' % name, rd(p))
        if m: return m.group(0)
    raise SystemExit('no ref ' + name)
DECAL_SURF = (0, 0.4, 0.35)
def matte(D, label):
    g = str(uuid.uuid4()); D.new.append('\t<instance guid="%s" type="LayerCompSurfaceParam" exported="true">\n\t\t<field name="Name"></field>\n\t\t<field name="metal_mask">%s</field>\n'
        '\t\t<field name="reflectance">%s</field>\n\t\t<field name="smoothness">%s</field>\n\t</instance>\n' % (g, *DECAL_SURF))
    for ch in 'RGB': D.field('rsm' + ch, 'ref="%s"' % g, label)
def put_stripe(D, src_text, tex_xml):
    a, b = ov_span(src_text, 'overlay_5'); blk = src_text[a:b]; assert '>Center Stripe<' in blk
    for g in set(re.findall(r'ref="([0-9a-f]{8}-[0-9a-f-]{27})"', blk)):
        k = src_text.index('<instance guid="%s"' % g); inst = src_text[k:src_text.index('</instance>', k) + len('</instance>')]; ng = str(uuid.uuid4())
        D.new.append('\t' + inst.replace(g, ng) + '\n'); blk = blk.replace(g, ng)
    blk, c = re.subn(r'<field name="colorTexture" ref="[^"]*" partitionGuid="[^"]*" />', lambda m: '<field name="colorTexture" %s />' % idref(tex_xml), blk, 1); assert c == 1
    c_, d_ = ov_span(D.t, 'overlay_5'); assert '>Center Stripe<' in D.t[c_:d_] and 'colorTexture" ref="null"' in D.t[c_:d_]; D.t = D.t[:c_] + blk + D.t[d_:]
def finish(D, center, outer, gaps):
    D.tint('R', center, 'Center Stripe'); D.tint('G', outer, 'Center Stripe'); D.tint('B', gaps, 'Center Stripe')
    D.field('rsmTexture', 'ref="null"', 'Center Stripe'); matte(D, 'Center Stripe')
GOLD, WHITE, PURPLE, BLACK = anyref('ECU_Gold'), anyref('global_whiteHelmet'), anyref('ECU_Purple'), anyref('global_blackHelmet')
WS = rd(H_ + 'ECU_HELMET_2021_WHITESCRIPT.xml'); JR0 = rd(H_ + 'ECU_HELMET_2025_PURPLE_purpleFacemask.xml')
# Black Pirate / Away Option
p = H_ + 'ECU_HELMET_2021_BLACKOUT.xml'; D = Doc(rd(p)); put_stripe(D, WS, IDS + 'ECU_GS_Helmet_Stripe_col.xml'); finish(D, PURPLE, GOLD, BLACK); wr(p, D.done()); print('Blackout: gold | purple | gold')
# Home
p = H_ + 'ECU_HELMET_2025_PURPLE_yellowFacemask.xml'; D = Doc(rd(p)); put_stripe(D, JR0, IDS + 'ECU_JR_Helmet_Stripe_col.xml')
shell = re.search(r'name="colorR" ref="([0-9a-f-]{36})"', D.t[max(D.t.rfind('<complex type="LayerComp%s">' % k, 0, D.t.index('<field name="label">Helmet Shell</field>')) for k in ('OverlayInstance', 'MaterialInstance')):D.t.index('<field name="label">Helmet Shell</field>')]).group(1)
finish(D, WHITE, GOLD, 'ref="%s"' % shell); wr(p, D.done()); print('Home: gold | white | gold')
# Jolly Roger
p = H_ + 'ECU_HELMET_2025_PURPLE_purpleFacemask.xml'; D = Doc(JR0)
shell = re.search(r'name="colorR" ref="([0-9a-f-]{36})"', D.t[max(D.t.rfind('<complex type="LayerComp%s">' % k, 0, D.t.index('<field name="label">Helmet Shell</field>')) for k in ('OverlayInstance', 'MaterialInstance')):D.t.index('<field name="label">Helmet Shell</field>')]).group(1)
finish(D, WHITE, GOLD, 'ref="%s"' % shell); wr(p, D.done()); print('Jolly Roger: gold | white | gold')
