# Technical reference: CFB 27 apparel swap and custom alternates (ECU, Adidas to Jordan)

The working record kept while building the mod, edited for publication. It covers how the game's
uniform assets fit together, the fixes that worked, exact field names and values, and the dead ends,
so a repeat of the process for another team can skip the troubleshooting. Claude (Anthropic) wrote it
during development as the AI pair-programmer; "the user" means the mod author, who did every Frosty
and in-game step and confirmed each result in game.

Final result of part 1, all verified in game:
- Jumpman on every ECU jersey (5), pants (6) and sock (2) part item, in team colors.
- The Jumpman survives the national championship game (no swap to the Adidas "Shiny" logo).
- ECU is a Jordan school in the roster: apparel = Jordan, all 85 players in Jordan cleats and gloves,
  editor offers Nike and Jordan gear, Play Now preview model and on-field players in Jordan gear.
- Roster-screen headshots show the Jumpman.

---

## 0. Environment and tools

- Game: EA SPORTS College Football 27 on PC. Mods only work on PC.
- Frosty Editor **MMC Edition 1.1.0.8** (from the College Football Modding Community Discord), run
  as administrator. The mod is exported as a `.fbmod` and applied with the MMC mod manager.
- Python scripts (Pillow, numpy, SciPy, OpenCV) edit the exported XML and generate textures. They
  ran outside Frosty; the mod author did every Frosty step (export, import, duplicate, rebuild) by hand.

## 1. How the uniform logo is built

Chain: `TeamVisuals.Uniforms` → `UniformVisuals/CFB/<TEAM>/U_UniformType_*` →
`FootballCharacter/Items/uniform/<piece>/U_<TEAM>_JERSEY_*` (CharacterUniformJerseyItem, a
**wrapper**, ~5 KB, holds `PartItemRef` → `JerseyPartItemReference.AssetName`) →
`content/characters/player/parts/uniforms/{jerseys,pants,socks}/partitems/<TEAM>_JERSEY_*`
(**JerseyPartItem / PantsPartItem / SockPartItem**, 50 to 130 KB: the layer stack, the ones to edit).

Not useful for the logo:
- `.../jerseys/presets/*_preset*.xml` (AppearanceShaderPreset): material settings only.
  ECU and Michigan presets are nearly identical.
- `*_uniform_recipes_brt*` and `*_brt_blueprint` (BundleRefTable): export as empty shells.
- `partitems` folders also hold vendor templates (`ADIDAS_Jersey_2023_01`, `UA_Jersey_*`).
  They aren't team-specific.

### The logo layer inside a part item
One `LayerCompOverlayInstance` (ECU: jerseys `overlay_3`, pants `overlay_2`, socks `overlay_1`;
Michigan jerseys `overlay_4` or `overlay_5`, pants `overlay_2`, socks `overlay_1`):
```
textures  (LayerCompMaps): colorTexture / layoutTexture / rsmTexture / normalTexture refs,
                           assetResolveRuleType, hasAO, isMask
tint      (LayerCompTint): colorR / colorG / colorB refs (ColorValue), TintMode_WithValue
rsm       (LayerCompTextureSurfaceParams): rsmR/G/B
info      (LayerCompInfo): label ("Adidas Logo" / "Jumpman Logo"), slot ref
overlay_transform -> separate LayerCompTransform instance in the same file:
           scaledTransform Vec4 (x=scaleU, y=scaleV, z=offsetU, w=offsetV),
           scaleU, scaleV, offsetU, offsetV, rotate, clampUV, transformRange
overlay_blend (LayerCompBlend): occBlend, colorBlend, normalBlend, rsmBlend
```
Brand decals live in `ContentShared/characters/player/parts/uniforms/decals/vendors/`:
`Adidas_Decal_2023_{col,norm,rsm}`, `Adidas_Decal_2023_WithText_*`, `Adidas_Decal_2023_Shiny_*`
(championship version), `Jumpman_Decal_2022_Cotton_*`, `Jumpman_Decal_2022_Diamond_*`, plus other
Jumpman variants and Nike and UA ones.
Slots: `content/characters/Player/parts/uniforms/adidas_patch_slot`
(`\\ff8693b2-ac83-44fb-8365-3a9a8b6e60f3`, partition `8142d2ed-08c6-43ca-b57f-ef939dfdb73a`),
`Content/characters/Player/parts/uniforms/jordan_patch_slot`
(`\\b722f189-8a45-40f3-a07f-aab7ad32a8e3`, partition `9b45fa53-5f21-4a91-9737-f35506c5a350`).
Socks have slot `null`.

### Texture channel layouts (decoded from the DDS)
- Adidas decal `_col`: R = 255 everywhere, G = B = 0, **A = logo shape**. The tint uses colorR only,
  as the logo color.
- Jumpman `_col` (BC3_UNORM, DXGI 78, 512x512): **A = figure plus a thick outline patch, R =
  everything except the figure, G = the figure**. Tint: **colorR = the uniform's base color**
  (paints the patch, which then blends in), **colorG = the logo color**. Michigan white jersey:
  R = global_white, G = MICH_Blue.
- Jumpman `_norm` and `_rsm` are BC7 (DXGI 98).

### Placement (LayerCompTransform), all values confirmed in game
- Jerseys: Michigan's Jumpman: `scaleU=scaleV=0.03, offsetU=0.069, offsetV=-0.099, rotate=0`,
  scaledTransform (0.03, 0.03, 0.0690000057, -0.09900001). ECU's Adidas was 0.04 to 0.05 scale.
- Pants: **keep the team's own Adidas transform** (ECU: 0.05 / 0.1 / 0.16 / 0.245 / rot 8; PURPLEALT
  0.045 / 0.085 / 0.16 / 0.26 / rot 8), with `layoutTexture` null. Michigan's pants placement
  (0.069 / 0.085 / 0.222 / 0.339 / rot 5) is relative to `uvsets/Pants_UVSet_front`, which ECU's
  pants never load. Copying it would misplace the logo.
- Socks: Michigan's sock transform `0.07 / 0.07 / 0 / 0.315 / rot 0`. Both teams use
  `uvsets/Socks_Outer_UVSet_front`.
- `hasAO` set to false (Michigan's value for the Jumpman).

---

## 2. Problem 1: logo blank in game (bundle loading)

Symptom: after pointing ECU's layer at Michigan's `Jumpman_Decal_2022_Cotton_*`, the Adidas logo
disappeared and nothing drew. The import was verified correct by re-exporting the part item.
Even in an ECU vs. Michigan game the Jumpman didn't show.
Cause: asset references resolve when the referencing partition loads. A texture that isn't in
the team's bundles stays null.
Fix: **Duplicate the team's own Adidas decal** (it's in ECU's bundles), import the Jumpman DDS
into the duplicate, and point the layer at the duplicate. That worked on the first test.
- The text logo (`Adidas_Decal_2023_WithText_*`) is used by ECU jerseys PURPLE, PURPLEALT, WHITE
  and pants PURPLEALT. The plain `Adidas_Decal_2023_*` is used by jersey BLACK, jersey 2026
  WHITEALT, the other 5 pants and both socks. Each uniform piece needs a duplicate of the decal
  **it** uses.
- Reference format in XML: `ref="<path>\\<primaryInstance guid>" partitionGuid="<partition guid>"`,
  taken from the duplicate's own exported XML (`<partition guid=… primaryInstance=…>`). The ID
  doesn't change when an image is imported into the duplicate later.
- Pants trap from the same cause: the copied `Pants_UVSet_front` layout map wasn't in ECU's
  bundles, so the final build keeps ECU's own pants placement.

Duplicates now in the Frosty project (all in `decals/vendors`):
| Duplicate | Made from | Holds | Still used by |
|---|---|---|---|
| ECU_Jumpman_Decal_WithText_col | Adidas_Decal_2023_WithText_col | Jumpman col | nothing (superseded) |
| ECU_Jumpman_Decal_WithText_norm / _rsm | WithText norm / rsm | Jumpman norm / rsm | WithText pieces |
| ECU_Jumpman_Decal_col | Adidas_Decal_2023_col | Jumpman col | nothing (superseded) |
| ECU_Jumpman_Decal_norm / _rsm | plain norm / rsm | Jumpman norm / rsm | plain pieces |
| ECU_JM_WT_PurpleOnWhite_col | WithText col | colored PNG | JERSEY_2023_WHITE |
| ECU_JM_WT_GoldOnPurple_col | WithText col | colored PNG | JERSEY PURPLE, PURPLEALT, Pants PURPLEALT |
| ECU_JM_PurpleOnWhite_col | plain col | colored PNG | JERSEY_2026_WHITEALT, PANTS WHITE, WHITEALT |
| ECU_JM_GoldOnPurple_col | plain col | colored PNG | Pants PURPLE |
| ECU_JM_WhiteOnBlack_col | plain col | colored PNG | JERSEY BLACK, PANTS BLACK, SOCKS BLACK |
| ECU_JM_PurpleOnGold_col | plain col | colored PNG | PANTS YELLOW |
| ECU_JM_BlackOnWhite_col | plain col | colored PNG | SOCKS WHITE |

---

## 3. Problem 2: national championship swaps the logo back

Symptom: in a national championship Play Now game, ECU's logo layer (in our placement) showed the
**Adidas Shiny** decal, metallic looking. That's the gold brand logo EA uses for title games.
Michigan's equivalent is presumably `Jumpman_Decal_2022_Diamond`.
Mechanism: `textures.assetResolveRuleType = AssetResolveRule_UseOverrideRuleset` on every layer
(all 1,906 layers in every export). An override ruleset replaces the texture in event contexts.
What it keys on was never found. Ruled out: roster TAPP, teamdb TAPP, the patch slot
(`jordan_patch_slot` changed nothing), TeamVisuals.BrandName, and the duplicate textures
themselves (they carry only Name, Resource, CropInfo, AuthoredWidth/Height).
Enum values (Frosty dropdown): `AssetResolveRule_UseDefaults`, `AssetResolveRule_UseBaseRuleset`,
`AssetResolveRule_UseOverrideRuleset`.
- `UseDefaults` and `UseBaseRuleset`: no swap, but **no tinting either**. The raw channels render,
  so the logo shows as red background plus green figure.
Fix (final): `UseDefaults` on the logo layer's textures, plus **pre-colored col textures** with the
colors baked in (`make_colored_logos.py`):
`linear = R*base_color + G*logo_color` (ColorValue floats are linear), converted to sRGB 8-bit,
alpha = A, fully transparent pixels filled with the base color. The colors matched the tinted
look in game with no adjustment.
Team colors (ColorValue, linear) and sRGB:
| Asset | Linear | sRGB |
|---|---|---|
| team_colors/ECU_Purple | 0.0409152, 0.0202886, 0.1221388 | 57, 39, 98 |
| team_colors/ECU_Gold | 0.9734453, 0.462077, 0 | 252, 181, 0 |
| recipe/colors/global_white | 0.6375968, 0.6375968, 0.7454042 | 209, 209, 224 |
| recipe/colors/global_black | 0.0212190, 0.0212190, 0.0251869 | 40, 40, 44 |
Color pairs (R = uniform, G = logo), matching ECU's original Adidas logo colors except gold pants:
| Part item | Uniform | Logo | Col duplicate |
|---|---|---|---|
| ECU_JERSEY_2023_WHITE | white | purple | ECU_JM_WT_PurpleOnWhite_col |
| ECU_JERSEY_2023_PURPLE | purple | gold | ECU_JM_WT_GoldOnPurple_col |
| ECU_JERSEY_2023_PURPLEALT | purple | gold | ECU_JM_WT_GoldOnPurple_col |
| ECU_JERSEY_2023_BLACK | black | white | ECU_JM_WhiteOnBlack_col |
| ECU_JERSEY_2026_WHITEALT | white | purple | ECU_JM_PurpleOnWhite_col |
| ECU_PANTS_2023_WHITE | white | purple | ECU_JM_PurpleOnWhite_col |
| ECU_PANTS_2023_WHITEALT | white | purple | ECU_JM_PurpleOnWhite_col |
| ECU_PANTS_2023_BLACK | black | white | ECU_JM_WhiteOnBlack_col |
| ECU_PANTS_2023_YELLOW | gold | **purple** (user's choice; Adidas was white) | ECU_JM_PurpleOnGold_col |
| ECU_Pants_2023_PURPLE | purple | gold | ECU_JM_GoldOnPurple_col |
| ECU_Pants_2023_PURPLEALT | purple | gold | ECU_JM_WT_GoldOnPurple_col |
| ECU_SOCKS_2023_BLACK | black | white | ECU_JM_WhiteOnBlack_col |
| ECU_SOCKS_2023_WHITE | white | black | ECU_JM_BlackOnWhite_col |
The tint fields are still set (harmless, ignored under UseDefaults). The slot is kept as ECU's
original `adidas_patch_slot`. The label is "Jumpman Logo".

---

## 4. Team brand: the four places it's stored

| Place | Field | ECU before → after | Effect |
|---|---|---|---|
| Roster file (saves) | team record `TAPP` | 1 → 3 | **The one that matters**: gear options and the editor |
| Roster file | each player's gear blob | Adidas → Jordan models | What players actually wear |
| Legacy `common/database/teams/teamdb_ecu.DB` | TEAM.TAPP | 1 → 3 | Base data, used for fresh rosters |
| Legacy `teamdb_ecu_visuals.JSON` | loadouts LeftShoe/RightShoe/LeftHandWear/RightHandWear | swapped | Base data |
| `content/FootballCharacter/TeamVisuals/ECUXXX_TeamVisuals` | `BrandName` | `Brands/Adidas_ItemTag` → `Brands/JordanBrand_ItemTag` | No visible change found; kept |

TAPP values (match MyDynasty "Team Apparel" order, confirmed against Ohio State = 0, ECU = 1,
Michigan = 3, Florida = 3): 0 Nike, 1 Adidas, 2 Under Armour, 3 Jordan Brand, 4 New Balance,
5 Generic.
`ItemTagAssets/Brands/JordanBrand_ItemTag`: `\\a76fc807-f8df-4404-9fc2-4bf57e9c5f42`, partition
`79914ba6-ff4a-4e18-8ae1-c40c576015cc`. Adidas_ItemTag: `\\750536d4-f0e3-47d7-a7ad-222504b2d8ec`,
partition `bad61cc4-0e7e-47cc-8400-f108fba7685b`.

Importing only the teamdb edits changed **nothing** in game. The roster editor still offered only
Adidas, because the active roster overrides base data. Existing dynasty saves carry their own copy
(MyDynasty edits those).

---

## 5. Team database and roster files (summary)

The brand change in sections 4 and 18 required editing two of EA's binary save and database formats.
That work is described here at a summary level only. The parsers and patchers are not published,
because EA's user agreement prohibits reverse engineering its formats.

- **Team database (TDB):** a bit-packed table format where every table carries its own checksum.
  The change was one field (the team apparel value) plus a recomputed checksum. Importing it alone
  changed nothing in game, because the active roster overrides the base data.
- **Roster file:** a compressed container with a checksum over the uncompressed data, holding tagged
  fields and compressed per-player gear data. The patch swapped 323 Adidas gear items to Jordan
  equivalents across ECU's 85 players and set the team apparel value.
- **The checksum matters.** A roster with a stale checksum is silently ignored: the game loads its
  own roster with no error. This cost a full round of testing.
- **Verification:** every non-ECU player record and gear entry was compared byte for byte against the
  original, and ECU had 0 Adidas items left.
- **Marker test:** rename a player to a same-length name in a test copy. If the game shows the old
  name, it isn't reading the file.
- Always patch a fresh in-game "save as new roster", not the roster file on disk, which can be an
  older release.

### Gear mapping used in the roster patch (only names that exist in Michigan's data)
Cleats (high-tops became mids; no Jordan high-top was confirmed):
| Adidas | Jordan |
|---|---|
| shoe_low_AdizeroElectric3 | shoe_low_AirJordan1VaporEdge |
| shoe_low_AdizeroElectricPlusII | shoe_low_AirJordanRetro1 |
| shoe_low_Adidas_AdizeroElectricPlus | shoe_low_Jordan5_99Club |
| shoe_low_AdidasFreak22 | shoe_low_Jordan7 |
| shoe_low_AdizeroElectric2 | shoe_low_AirJordanRetro1 |
| shoe_low_Adidas_AdizeroElectricSnake | shoe_low_AirJordanXI |
| shoe_low_AdidasAdizero_LTA58 | shoe_low_AirJordan1VaporEdge |
| shoe_mid_AdizeroImpactII | shoe_mid_AirJordanRetro1 |
| shoe_mid_AdizeroImpactPlusII | shoe_mid_AirJordan3Cement |
| shoe_mid_AdidasAdizeroPrimeKnit | shoe_mid_Jordan11TD |
| shoe_mid_AdidasNasty | shoe_mid_AirJordanX |
| shoe_mid_Adidas_AdizeroImpactPlus (EA's name has no GearFootwear_ prefix) | shoe_mid_Jordan7 |
| shoe_high_AdidasAdizeroChaos2 | shoe_mid_AirJordanRetro1 |
| shoe_high_AdidasFreakUltra23 | shoe_mid_Jordan11TD |
| shoe_high_Adidas_AdizeroChaos | shoe_mid_AirJordan3Cement |
(All prefixed `GearFootwear_` except where noted.)
Gloves (`GearHand_glove_` prefix; variant kept):
| Adidas | Jordan |
|---|---|
| AdidasFreak_TeamColor | JordanSuperbad6_TeamColor |
| AdidasFreak_White | JordanSuperbad6_White |
| AdidasFreak_Black | JordanSuperbad6_TeamColor (no Jordan black confirmed) |
| AdidasImpact2_TeamColor | JordanFlyLock_TeamColor |
| AdidasImpact2_White | JordanFlyLock_White |
| Adizero13_White | JordanFlyLock2_White |
| Adizero13MistmatchDSG_TeamColor | JordanFlylock2_TeamColor |
| Adizero15Electric_TeamColor | JordanVaporJet7_TeamColor |
| Adizero15Electric_White | JordanSuperbad6_White |
| Adizero15ElectricExoticDSG_TeamColor | JordanFlylock2_SecondaryColor |
| Adizero15ElectricExoticDSG_White | JordanFlyLock2_White |
323 swaps in both the base visuals JSON and the roster. ECU's Nike arm sleeves, knee and thigh pads
were left as they were. Other Nike-family references for a Nike swap: Ohio State's file
(`teamdb_ohiost_visuals.JSON`) lists Nike cleat names.

---

## 7. Roster headshots

- Per-player portraits: `content/ui/ImageAssetLibraries/global/nil/playerportraits/assets/`
  `nilpp_Unique_<Last><First>_<PGID>` (ImageLibraryTexture, DDS BC7 512x512). The player is shown
  in the **plain black** `PORTRAIT_JERSEY_2026_BLACK`, with no logo. Don't edit these.
- The team jersey shown on the roster card is a **per-team overlay**: `tjer_teamjerseys_ECU`
  (DDS BC7 512x512, jersey in the bottom third, transparent above). It had a gold Adidas logo
  with text at about x 341 to 393, y 461 to 498.
- Fix: inpaint the logo (OpenCV Telea, dilated mask plus fabric grain from the patch above), then
  draw the Jumpman figure (from the Jumpman col G channel) at 1.25× the logo height, centered on
  it, colored with the logo's median gold (235, 201, 96), shaded by the fabric's local brightness.
  2,146 pixels changed; alpha untouched. Imported as PNG; confirmed in game.
- Ruled out: `filesystemcache` (empty), the portrait jersey part item (generic, no vendor layer).

### 7b. Menu helmets (pre-game screens, dynasty story tiles)
- `content/ui/ImageAssetLibraries/global/TeamHelmets/assets/thel_lthelmets_<TEAM>` and `thel_rthelmets_<TEAM>`
  (left- and right-facing 3D renders, BC7 1024x1024). ECU's had a white "adidas" mark on the black front bumper.
- `TeamHelmetsFlat/assets/thf_rthelmets_<TEAM>` (the flat cartoon helmet used in dynasty backgrounds) has **no brand
  logo**, so no edit is needed.
- **Every team's helmet image uses the same render**, so the bumper sits on the same pixels in ECU's and Michigan's
  images. Fix (`patch_helmet.py`): inpaint the adidas mark (bounded box, Telea, smoothed), then take Michigan's Jumpman
  shape from the same pixel position (navy-on-maize contrast → soft mask, largest component, bumper/facemask seam peeled
  off) and draw it in the old logo's white (~214 gray). Boxes used: lt logo x655-703 y428-463, Jumpman x650-705 y430-470;
  rt logo x320-368 y425-463, Jumpman x315-370 y425-470. About 1,100 pixels changed per image; alpha untouched.
- For another team: export the target team's and the reference team's `thel_lt/rt` images; the same boxes should work
  (same render). Pick the logo color to match what the old brand mark used.

---

## 8. Dead ends, in order (so they aren't repeated)

1. Exported `*_preset` files: material settings only, no logo.
2. Exported `U_` CharacterUniform wrappers instead of part items. Tell-tale signs: 4 to 7 KB and a
   `U_` prefix.
3. `_brt` tables: empty shells.
4. Pointing at the reference team's decal: blank (bundles), so duplicate instead.
5. Copying the reference team's pants layout map: not loaded, misplaces the logo.
6. Changing the slot to `jordan_patch_slot`: no effect on anything observed.
7. teamdb TAPP alone: no in-game effect while a roster is active.
8. Patching `ROSTER-Official` without the checksum: ignored silently (and it was the older release anyway).
9. TeamVisuals.BrandName: no effect on the championship swap.
10. `UseDefaults` / `UseBaseRuleset` with the tinted textures: untinted raw channels.
11. Assuming the headshots were per-player baked images: they're generic black; the team overlay is
    what carries the logo.

## 9. Scripts

The published scripts are in `scripts/` (see the README for what each group does). They were written
for ECU: paths and team values are hardcoded, so adapt them rather than run them blind. Each script
reads exported XML or images from a project folder set with the `ECU_PROJECT_DIR` environment
variable (default: the current folder) and writes new files for import. Experiments that didn't ship
are in `scripts/legacy/`.

## 10. Checklist for the next team (streamlined order)

1. Pick a reference team with the target brand. Get its part items (1 jersey, 1 pants, 1 socks),
   teamdb files, TeamVisuals, and the brand's logo `_col/_norm/_rsm` as DDS.
2. Export the target team's part items (all jerseys, pants, socks; no `U_`), team colors plus
   global_white/black, teamdb files, TeamVisuals, and `tjer_teamjerseys_<TEAM>`.
3. Claude: read each part item's logo layer → which source decal it uses (text vs plain), its
   current tint (the logo color) and the uniform base color → list the color pairs → send the
   duplicate list (one col per pair per source decal, plus norm and rsm per source decal).
   Decode the reference logo's channel layout. Swooshes or other logos may use different channels
   than the Jumpman, so check R/G/A before reusing the formula.
4. User: make the duplicates, export their XMLs.
5. Claude: build the colored PNGs and the part items (UseDefaults; reference placement for jerseys
   and socks, the team's own for pants unless the layout map is shared; norm/rsm duplicates),
   the teamdb edits (TAPP plus the gear map, built only from names in the reference team's data),
   TeamVisuals.BrandName, and the headshot overlay.
6. User: import everything, save the project, rebuild, test one jersey first, then the rest.
7. User: in the game, save the current official roster as a new roster. Claude patches it
   (team apparel, gear map, checksum) to a new `ROSTER-<NAME>`. Verify in the editor and with a marker
   test if anything looks wrong.
8. Test the full checklist: uniforms, pants, socks, Play Now, preview model, editor gear lists,
   national championship, roster headshots.

---

# PART 2: custom alternate uniforms, helmets and uniform sets (2026-11-11)

Built on top of the Jordan swap in one long session. Everything below is verified in game unless it
says otherwise. Two new alternates: **Jolly Roger** (charcoal and gold; replaces the base purple pieces)
and **Treasure Island** (Notre Dame gold helmet, gunmetal and gold; replaces the base white pieces),
plus a rebuilt, renamed, reordered uniform-set list.

## 11. Rules learned (read before building any custom uniform)

### 11a. Replace, don't add
- Each custom uniform **reuses an existing ECU part item** (jersey, pants, helmet) and its `U_` wrapper.
  Pick pieces no uniform set needs (section 15 lists which set uses what). Adding brand-new part items
  was never attempted.
- **Check every set that references a piece before replacing it.** Replacing base PURPLE jersey and pants
  also changed "Current Away" (white jersey + purple pants) and two Home Options until the sets were rebuilt.
- Build from the **Jordan-swap version** of the piece (the Jordan-swap-only copy kept from part 1) so the Jumpman and championship fix carry over. Jolly Roger started from
  PURPLEALT's layer stack (stripes, PIRATES wordmark) with base PURPLE's partition, primary instance, name,
  preset names and number array spliced in.

### 11b. Bundles and duplicates (extends section 2)
- A texture a part item doesn't already load draws nothing. Fix: **duplicate a texture that part item
  already loads**, keep the duplicate in the same folder, import the new image into it, point the layer at it.
- **Never duplicate one of our own duplicates.** `ECU_JM_GunmetalOnGold_col` (a duplicate of our
  `ECU_JM_PurpleOnWhite_col` duplicate) never rendered. Only the Jumpman norm/rsm embossing showed: a dark
  figure with a light edge, whatever image was imported. The same image in `ECU_TI_JM_Pants_col` (a
  duplicate of the original `ECU_Decal_2021_02_col`) worked at once. Always duplicate an original game texture.
- A texture used by **only** the piece being replaced can be repainted in place, with no duplicate needed
  (`ECU_JM_WT_PurpleOnWhite_col`, used only by the base WHITE jersey). Grep all FINAL part items first.
- One duplicate of a texture that several pieces load serves all of them (`ECU_TI_Logo_col` works on the
  jersey and the pants).
- Duplicates of the base PURPLE jersey's textures also loaded on the base WHITE jersey (the `ECU_JR_*`
  sleeve stripe textures), so shared common textures are worth trying before making new duplicates.
- **UVSet (layout) textures are R16G16B16A16_UNORM (DXGI 11), which Frosty can't import.** Convert to
  R16G16B16A16_FLOAT (DXGI 10) and that imports (`Jersey_UVSet_sleeveStripesMirrored_FLOAT16.dds`).
- Importing a PNG or DDS of a different size or format into a duplicate works; Frosty takes the new size.
- Duplicate XMLs land wherever Frosty last exported; check the project root (and DDS vs XML) when one is
  "missing".

### 11c. Colors and tints
- ColorValue colors are **linear**; convert from sRGB. Use R = G with B slightly higher for a neutral
  dark gray. `#3C3F43` rendered **olive** (G > R); `#404044` and `#4A4A4F` render neutral charcoal.
- Local colors: append a `ColorValue` instance to the partition and reference it as `ref="<guid>"`
  (no partitionGuid). Local refs can also be shared by several layers (chin guard and straps use the
  bumpers' color).
- **Never regex non-greedily across instances.** An old step meant for an empty `overlay_18`
  searched forward and overwrote the **number** tint's colorR with charcoal. Find the target block
  first (label or texture), then edit inside it.
- `re.sub` with a string replacement collapses `\\` in refs to `\`. Always use a lambda, and assert
  "no single-backslash refs" before writing.
- **ECU 2021 number font** (`ECU_Jersey_2021_NUM_Array`): **R = fill, G/B = outline**. The outline is
  only a pixel or two at game distance, so no color makes it pop. Base PURPLE had all three channels
  gold; PURPLEALT has R global_number_white and G/B gold.
- Number shine is per part item: `frontNumberRSM / backNumberRSM / sleeveNumberRSM / shoulderNumberRSM`
  (plus `nameplateRSM`) → local `LayerCompSurfaceParam` (metal_mask, reflectance, smoothness). Stock
  0.45/0.4/0.25. ND Shamrock **0.9/0.3/0.925** = mirror (reads bronze/orange under locker lights);
  **0.6/0.3/0.6** = satin metal (reads gold). The wrapper's NumberRSM/NameplateRSM Vec3 is a separate
  setting (Jolly Roger uses 0.6/0.8/1).

### 11d. Copying layers between part items
- Empty overlay slots (colorTexture null, tint null) can take a whole overlay block copied from
  another part item. Copy from `<field name="overlay_N">` through the overlay_blend, rename the slot,
  and bring every **local** instance it references (overlay_transform, rsm params) under new GUIDs.
  The Treasure Island sleeve stripes are the Jolly Roger's `Stripe 1`, `Stripe 2`, `Middle Stripe` and
  `Sleeve Cuff Stripe` blocks copied into WHITE's empty `overlay_9/10/13/14`.
- To remove a layer, set its colorTexture (and normal/rsm) to `ref="null"`. Upper-back logo
  (`Back Logo`, stretched on the yoke) and the Treasure Island shoulder logos were removed this way.

### 11e. Fabric patterns (material layers)
- Material layers (`LayerCompMaterialInstance`: "Vapor Untouchable Fabric", "Sleeve Fabric", "Adidas
  Base Fabric") multiply a **tiled** colorTexture by the tint. The base fabric uses `default_mask`
  (plain white). A duplicate of `default_mask` holding a pattern (white = full color, darker lines =
  tonal print) gives a sublimated pattern under the logos and numbers.
- **The tile size is `scaleU` / `scaleV` in the material's LayerCompTransform. `scaledTransform` x/y
  is ignored.** All early tests changed only scaledTransform, so the pattern never changed size.
  scaleU = the tile size in UV: 0.03 (stock) = about 15 tiles across the chest (chain mail);
  **0.11** = 4 or 5 tiles (final); 0.2 = about 2 (blurry bands).
- The pants' material_transform is a **shared** asset (`Fabric_Nike_VaporUntouchable_pants_transform`).
  Give the pants a local copy of the transform, or every team's pants change.
- The same pattern reads much weaker on the jersey (wrinkle shading, mesh, logos), so the jersey gets
  its own duplicate with darker and thicker lines.

### 11f. Helmets
- Part items: `content/characters/player/parts/uniforms/helmets/partitems/<TEAM>_HELMET_*`. Decals:
  `.../helmets/decals/teams/`. Presets: `.../helmets/helmet_presets/`. Wrappers `U_<TEAM>_HELMET_*`.
- Menu names = the wrapper `DisplayName` (Purple Helmet 2 = 2025_PURPLE_purpleFacemask, Black Helmet 2
  = 2021_BLACKOUT, Purple Chrome Helmet = 2021_PURPLE_yellowFacemask, White Helmet 2 = 2021_WHITE,
  White Script Helmet = 2021_WHITESCRIPT, Purple Helmet = 2025_PURPLE_yellowFacemask).
- Materials: `Helmet Shell`, `Frontplates`, `Backplates`, `Chin Guard`, `Chin Straps` (colorR only).
  Overlays: `Right/Left Side Logo` (UVSet sideLogosR/L), `Frontplate` + `Frontplate_Schutt`,
  `Backplate` + `Backplate_X1`, `Center Stripe` (UVSet centerStripe), `AAC Decal`, `Warning Label`,
  `Flag`, `Screws`, plus an unlabeled helmet-number array.
- **Facemask color**: `faceMaskColor` field on the part item. Set it to a local ColorValue; this
  works on 2021 helmets too, where it was null.
- **Shell finish** = `shellMaterialMap` / `shellESMaterialMap` → AppearanceShaderPresetMap with an
  **AssetName string**. A preset's `_ES` has a Parent in `ContentShared/.../helmets/material_presets/`:
  `helmet_shell_preset_chromeMirror_ES` (ECU 2021 purples are the chrome helmets), `_satin_ES` (black),
  `_basicShininess_ES` (white), plus `helmet_preset_basicMatte_ES` and `helmet_preset_matteShinyStickers_ES`.
  **Other teams' presets can be borrowed by name**: Arkansas red (stock on 2025 purple, glossy), Kansas
  black `KU_HELMET_2021_BLACK_preset` (what Troy's MATTEBLACK uses; satin-matte), and Notre Dame gold
  `ND_HELMET_2021_GOLD_preset` (chrome gold; reflects the environment in low-res blocks, as on ND's own helmet).
- Decal channels (decoded from the DDS):
  - `WHI_Decal_01` (purple helmets): R = hat outline/bandana/earring, G = ECU letters, B = skull/bones.
    The hat interior is transparent (shell shows).
  - `BLA_Decal` (black and white helmets): R = outline + ECU letters + bandana, G = skull and bones,
    B = **hat fill**. Tinted R gold, G white, B ECU purple = the full-color skull.
  - `2023_Decal_01` = "PIRATES" script; `Bumper_ECU` = block "ECU" (R fill, G inner outline, B outer);
    `WHI_BackLogo` = "EAST CAROLINA" bumper text; `WHI_FrontLogo` = "PIRATES" bumper text.
  - `FiveStripe_02` (2048x1024, BC1): G = outer bands, B = next bands, R = center band.
- **Center stripe**: copy a whole `Center Stripe` overlay that has a stripe texture (PURPLETEXT's
  overlay_5 with FiveStripe_02 plus its local rsm and transform instances). The copied transform had
  `offsetV -0.28` (and w -0.28), which ended the stripe above the rear sticker; **set both to 0** for full
  length. Width: redraw the stripe texture (same channel layout) instead of guessing the transform:
  1024 px stock, 480 px final.
- Removed side logos: `colorTexture` and `normalTexture` → null. Full-color art on a helmet: section 11h.

### 11g. Jersey palette → gloves and cleats
- The jersey **wrapper**'s `ItemPalette` (null on most jerseys) → a local `PaletteVisuals` with
  `PrimaryColor` / `SecondaryColor` → local `ColorVisuals` (Vec4 linear + `ColorLookup_NoLookup`). The
  BLACK jersey has one (primary #28282C, secondary purple), which is why black-jersey sets get black gloves.
- It drives the **"TeamColor" gloves** (players' `GearHand_glove_*_TeamColor`) and the **PRI/SEC
  cleats**. With no ItemPalette, the team palette `ECUXXX_PaletteVisuals` is used (primary purple,
  secondary gold, tertiary near-black, quaternary light gray).
- Generic cleats `U_GENERIC_SHOESX_<base><accent>`: BLABLA, BLAPRI, BLASEC, BLAWHI, WHIBLA, WHIPRI,
  WHISEC, WHIWHI. **PRI/SEC follow the jersey palette**, not the team colors (Treasure Island WHIPRI came
  out white and gray, WHISEC white and gold).

### 11h. Full-color artwork (custom logo)
- Tinted decals use R/G/B masks. For full-color art: import a pre-colored RGBA image (straight alpha,
  colors bled into transparent pixels so mips don't fringe) into a duplicate, set the layer's
  `assetResolveRuleType` to **`AssetResolveRule_UseDefaults`** (tint ignored) and null the old
  logo's normal/rsm. This also makes it immune to the championship swap.
- `make_ti_logos.py` cleans AI-art halos (largest opaque blob), crops, and fits the art into the footprint
  of the decal it replaces. The helmet side footprint is the BLA_Decal bbox, x 39 to 472, y 26 to 485 of 512;
  the final helmet logo is at 70% of that.

### 11i. Uniform sets (the "Uniform Name" list)
- Files: `content/FootballCharacter/UniformVisuals/CFB/ECU/U_UniformType_ECU_*` (type UniformVisuals),
  each with 6 `ItemLoadoutElement`s (SlotType HeadWear/OuterShirt/OuterPants/InnerSocks/LeftShoe/RightShoe
  + `ItemAssetName` = the **wrapper name**, e.g. `U_ECU_HELMET_2021_WHITE`) and a `Loadout`
  (`LoadoutType_TeamDark/TeamLight`, `DisplayOrder`).
- **`DisplayName` on a set shows in game** (top of the locker room, dynasty uniform pick). Item names
  don't: wrappers carry `Short/Long/MediumNameId` string IDs that win over DisplayName, and blanking
  them didn't help either.
- **Order = the `Uniforms` array in TeamVisuals.** DisplayOrder was set to 1..7 as well. Sets dropped
  from the array disappear cleanly. An active dynasty kept loading, auto-picked "Away" for a road game,
  and used it in news art.
- Set gear follows the set: cleats come from the set, gloves from the selected jersey's palette.

### 11j. Item names (parked)
- Item names live in `RimeFootball/CollegeFB/Generic/Localization/CFB_TextDatabase_English`
  (FsUITextDatabase): a stub pointing at two binary chunks (BinaryChunk 17,845 B, HistogramChunk
  270,608 B, probably Huffman). `localization_common/platform.JSON` (Legacy Explorer) hold only UI
  and online strings (2,764 entries, no item names). CFMC has no text editor, so it's parked. The set names
  cover what matters.

## 12. Jolly Roger (replaces base PURPLE jersey + pants, 2025_PURPLE_purpleFacemask helmet)
- Jersey (`ECU_JERSEY_2023_PURPLE`): PURPLEALT layer stack. Body, sleeves, collar, cuff, vent holes,
  TShirtandPads, collar stripe = charcoal **#4A4A4F**. Sleeve slash stripes: outer purple, middle gold;
  gold cuff stripe. PIRATES wordmark R gold / G purple (duplicate `ECU_JR_Pirates_*`). Numbers R gold fill,
  G/B **#7A4FC0** brighter purple. Nameplate gold. Jumpman `ECU_JM_WT_GoldOnCharcoal_col`. Topo:
  `ECU_JR_Topo_Jersey_col` (line tone 0.08, width 6 px), scaleU/V 0.11.
- Wrapper: NumberRSM/NameplateRSM 0.6/0.8/1; **ItemPalette primary charcoal, secondary ECU gold** →
  charcoal and gold gloves, black and gold BLASEC cleats.
- Pants (`ECU_Pants_2023_PURPLE`): charcoal base and holes, stripe gold core with purple edges, Jumpman
  `ECU_JM_GoldOnCharcoal_col`, topo `ECU_JR_Topo_col` (tone 0.2, width 4.5 px), scale 0.11 on a local
  copy of the transform.
- Helmet (`ECU_HELMET_2025_PURPLE_purpleFacemask`, "Purple Helmet 2"): shell **#404044** (matte lifts
  it), bumpers, chin guard and straps **#1C1C1E**, facemask ECU gold, finish `KU_HELMET_2021_BLACK_preset`,
  sides = BLA skull (gold/white/purple hat) via `ECU_JR_Helmet_Skull_col/_norm`, back bumper serif "ECU"
  (the hat lettering, deskewed -6°) via `ECU_JR_Helmet_BackECU_col` with norm/rsm nulled, center stripe
  gold/purple/gold 480 px via `ECU_JR_Helmet_Stripe_col`, full length.
- Set: `Current6thAlternate` "Jolly Roger", black socks, BLASEC.
- Concept source: a Gemini "Jolly Roger Jordan Alternate" spec and the user's helmet render
  (matte charcoal, full-color skull, gold/purple stripe, black bumpers, gold facemask).

## 13. Treasure Island (replaces base WHITE jersey, PANTS_2023_WHITEALT, 2021_WHITE helmet)
- Idea (Notre Dame reference notes and a Gemini concept photo):
  ND's gold helmet, ND 2024 Shamrock-style gold numbers, true gunmetal, ECU vibe.
- Colors: gunmetal **#5B5962** (neutral with a faint violet undertone; ND_BlueGray #424E66 read blue),
  `ND_MetallicGold` (linear 0.434, 0.287, 0.095), Shamrock number golds (linear 0.587, 0.387, 0.126 /
  0.729, 0.480, 0.155), ND helmet shell (linear 0.890, 0.710, 0.245).
- Jersey (`ECU_JERSEY_2023_WHITE`): gunmetal body, gold collar, cuffs, EAST CAROLINA, nameplate, AAC.
  Numbers Shamrock gold at satin 0.6/0.3/0.6. Back logo and shoulder logos removed. Gold sleeve slash
  and cuff stripes (copied Jolly Roger layers). Jumpman white on gunmetal (repainted
  `ECU_JM_WT_PurpleOnWhite_col` in place). Fabric preset borrowed: `ND_JERSEY_2023_BLUE_preset`.
- Wrapper: ItemPalette primary gunmetal, secondary ND gold → gunmetal gloves; set uses WHISEC
  (white and gold cleats).
- Pants (`ECU_PANTS_2023_WHITEALT`): gunmetal, solid gold side stripe, the user's logo on the hip
  (`ECU_TI_Logo_col`, UseDefaults), Jumpman white on gunmetal (`ECU_TI_JM_Pants_col`), finish
  `ND_PANTS_2021_GOLD_preset`.
- Helmet (`ECU_HELMET_2021_WHITE`, "White Helmet 2"): ND gold shell plus `ND_HELMET_2021_GOLD_preset`,
  gunmetal bumpers, chin and facemask, gold bumper text, the user's alt logo on the sides
  (`ECU_TI_Helmet_Logo_col`, 70%).
- Set: `Current7thAlternate` "Treasure Island", slot 4 (swapped ahead of Jolly Roger 2026-11-12), white socks, WHISEC.
- Iterations that didn't stick: v2 gold pants (looked good, but the user wanted gunmetal); v3 gold jersey
  with gunmetal numbers ("not loving this").

## 14. Duplicate textures (every one, with its source)
| Duplicate | Duplicated from (original game texture) | Image imported | Used by |
|---|---|---|---|
| ECU_JR_Pirates_col / _norm / _rsm | a decal the base PURPLE jersey loads (decals/teams; source not recorded) | ECU_Decal_2021_03 col/norm/rsm DDS | JR jersey PIRATES |
| ECU_JR_SleeveStripe_col | a common stripe texture of base PURPLE (seams_stripes_CID/common) | SleevesSingle_col DDS | JR + TI sleeve stripes |
| ECU_JR_SleeveCuff_col | same | SleeveCuffs_col DDS | JR + TI cuff stripe |
| ECU_JR_UVSet_sleeveStripes | a UVSet base PURPLE loads (uvsets) | sleeveStripesMirrored **FLOAT16** DDS | JR + TI stripes |
| ECU_JR_Topo_col / ECU_JR_Topo_Jersey_col | `recipe/textures/default_mask` | topo PNGs | JR pants / jersey fabric |
| ECU_JM_GoldOnCharcoal_col, ECU_JM_WT_GoldOnCharcoal_col | (colored Jumpman set, vendors) | gold-on-charcoal PNGs | JR pants / jersey |
| ECU_JR_Helmet_Skull_col | ECU_Helmet_2021_WHI_Decal_01_col | ECU_Helmet_2021_BLA_Decal_col.dds | JR helmet sides |
| ECU_JR_Helmet_Skull_norm | ECU_Helmet_2021_WHI_Decal_norm | ECU_Helmet_2021_BLA_Decal_norm.dds | JR helmet sides |
| ECU_JR_Helmet_BackECU_col | ECU_Helmet_2021_WHI_BackLogo_col | serif ECU PNG | JR back bumper |
| ECU_JR_Helmet_Stripe_col | ECU_Helmet_2021_WHI_Decal_01_col | 480 px stripe PNG | JR center stripe |
| ECU_TI_Logo_col | ECU_Decal_2021_02_col | user's alt logo (940 px fit) | TI pants hip |
| ECU_TI_Helmet_Logo_col | ECU_Helmet_2021_BLA_Decal_col | alt logo (70% of BLA footprint) | TI helmet sides |
| ECU_TI_JM_Pants_col | ECU_Decal_2021_02_col | white-on-gunmetal Jumpman | TI pants |
| (in place) ECU_JM_WT_PurpleOnWhite_col | n/a: repainted, only WHITE jersey uses it | white-on-gunmetal Jumpman | TI jersey |
| ECU_JM_GunmetalOnGold_col | our ECU_JM_PurpleOnWhite_col dup (**broken: dup of a dup**) | n/a | nothing (can be deleted) |

## 15. Uniform-set lineup (final, 5.0)
| # | Name | Set file | Type | Helmet | Jersey | Pants | Socks | Cleats |
|---|---|---|---|---|---|---|---|---|
| 1 | Home | CurrentHome | Dark | 2025_PURPLE_yellowFacemask | 2023_PURPLEALT | 2023_YELLOW | white | WHIPRI |
| 2 | Away | CurrentAway | Light | 2021_WHITESCRIPT | 2026_WHITEALT | 2023_WHITE | white | WHISEC |
| 3 | Black Pirate | Current3rdAlternate | Dark | 2021_BLACKOUT (matte) | 2023_BLACK | 2023_BLACK | black | BLABLA |
| 4 | Treasure Island | Current7thAlternate | Dark | 2021_WHITE | 2023_WHITE | 2023_WHITEALT | white | WHISEC |
| 5 | Ghost Ship | Current9thAlternate (CFB/ECU, NEW asset) | Light | 2026_GHOST | 2026_GHOST | 2026_GHOST | white | WHISEC |
| 6 | Jolly Roger | Current6thAlternate | Dark | 2025_PURPLE_purpleFacemask | 2023_PURPLE | 2023_PURPLE | black | BLASEC |
| 7 | Home Option | CurrentAlternate | Dark | 2021_PURPLE_yellowFacemask | 2023_PURPLEALT | 2023_PURPLEALT | white | WHIPRI |
| 8 | Away Option | Current2ndAlternate | Light | 2021_BLACKOUT (matte) | 2026_WHITEALT | 2023_BLACK | white | WHIBLA |
Dropped from the list (files untouched): CurrentThrowback, CurrentAwayAlternate, CurrentAlternateOption,
Current5thAlternate, Current_Alt_4.

## 15b. Matte Blackout helmet (2026-11-11, confirmed in game)
`ECU_HELMET_2021_BLACKOUT` ("Black Helmet 2", used by Black Pirate and Away Option): only the shell finish names changed,
`ECU_HELMET_2021_BLACK_preset(_ES_appearance)` → `KU_HELMET_2021_BLACK_preset(_ES_appearance)`. Script `build_blackout_matte.py`,
file in FINAL `Helmets/`. `2021_BLACK` ("Black Helmet") stays glossy.

## 15c. White Alt glove palette (2026-11-12)
`U_ECU_JERSEY_2026_WHITEALT` (Away + Away Option) got an ItemPalette: primary global_white, secondary ECU_Purple → white/purple
TeamColor gloves for both sets (gloves follow the jersey, so two sets sharing a jersey can't differ). Away cleats WHIPRI → WHISEC
to stay white/purple. Script `build_whitealt_palette.py`.

## 16. Alternate dead ends (so they aren't repeated)
1. `U_` wrapper DisplayName for item names, and blanking the name IDs: no effect in game.
2. Changing only `scaledTransform` for a tiled pattern: no effect (use scaleU/scaleV).
3. Non-greedy regex from an empty overlay: hit the number tint (charcoal numbers).
4. Duplicate of our own duplicate (`ECU_JM_GunmetalOnGold_col`): never loads.
5. ND's `ND_BlueGray` as "gunmetal": reads blue.
6. Full-mirror metallic numbers (0.9/0.925): bronze/orange glare in the locker room.
7. Upper-back logo on the base white jersey: smeared across the yoke.
8. Purple number outline on charcoal (ECU purple, then #7A4FC0): too thin to read; accepted as solid gold.
9. Text-table editing: binary Huffman chunks, no tool.
10. Jolly Roger alt logo (user's charcoal skull + cutlasses art, 2026-11-12): helmet sides (repainted ECU_JR_Helmet_Skull_col,
    UseDefaults; needed overlay scale 0.45 vs stock 0.35 on the 2025 helmet to read) and pants hip (dup ECU_JR_Logo_col).
    Mostly charcoal art on a charcoal helmet; the user removed it everywhere. 
    Size lesson: a side decal's size = overlay_transform scaleU/scaleV; enlarging the image inside the texture barely helps.

## 17. Workflow for the next custom uniform
1. User writes the idea (colors, which existing uniform it replaces). Check section 15 (or the team's
   sets) so nothing in use changes by accident.
2. User exports: the target part items (jersey, pants, helmet) + wrappers, the team's uniform sets and
   TeamVisuals, any reference team's part items, presets and colors, and DDS of any decals to redraw.
3. Claude: list the layers (label, texture, layout, tint), decode decal channels, plan which textures need
   duplicates (only originals the piece loads) and which colors are local ColorValues.
4. Build with a script (pattern: `build_jolly_roger.py`, `build_treasure_island.py`,
   `build_jolly_roger_helmet.py`, `build_uniform_sets.py`). Each writes to `Builds/<name>/`,
   activates duplicate-dependent steps only when the duplicate's XML exists, and asserts no broken refs.
5. User makes duplicates → imports images into them → exports their XMLs (as XML!) into the IDs folder.
6. Rebuild, import XMLs, export the mod, re-import in Mod Manager, clear mod data, test in the locker room
   (Uniform Name list) and in a live game. Iterate one variable at a time.
7. When happy: copy outputs into the import-ready folder and keep the replaced versions as backups.

## 18. Dynasty brand (2026-11-12, CLOSED: not fixable by mod)

New dynasties started from the patched roster still had ECU in Adidas apparel and gear.
- Every candidate source in the game's dynasty database files was tested (league, streamed and
  template databases, with valid checksums). Each loaded fine, and new dynasties were still Adidas.
- A diff of two dynasty saves (before and after changing ECU's apparel with MyDynasty) showed the
  apparel value plus re-rolled gear blocks, so the save itself carries the brand.
- Tests with the official roster file, the active custom roster, and an offline start all came back
  Adidas.
- **Conclusion:** a new dynasty takes team apparel from the official roster data EA serves at startup,
  held in memory. No file on disk feeds it, so there is no mod-only fix. The supported path is
  MyDynasty's Edit Team step (Team Apparel → Jordan Brand), which the mod's instructions include.

- **Master item list:** `global/Logic/Boot/Flow/Character/CollegeFBCharacterPrefab` > `Objects[0]` (ItemRegistrarData) > `ItemInfos` (10,096 entries). Each `ItemInfo` = ItemName, DisplayName, TeamNames, LoadoutSlots, ItemId, LoadoutShade, role/outfit/authenticity, IsGlobal/CanRemix/HiddenInUI.
  An item missing from this list is invisible to the game: not in the picker, and a preset that uses it loads a random combo every time.

**Adding a new piece**
1. Duplicate the part item and its wrapper in Frosty.
2. Wrapper: new unique `Id` (e.g. 91726001), `PartItemRef/AssetName` -> the new part item.
3. Register it in CollegeFBCharacterPrefab: ItemInfos `+` -> `...` -> **Create new** -> ItemInfo (NOT "Assign from self", which points at an existing item). Fill ItemName, DisplayName, ItemId (= the wrapper's Id), TeamNames `ECUXXX`, LoadoutSlots, LoadoutShade, Role Player, Outfit All, Authenticity All, IsGlobal + CanRemix on. The four dropdowns default to `_Invalid`.

**Adding a preset**
- Duplicate an existing one. Check the Duplicate dialog's folder (it defaulted to `CFB/CHAR` once).
- **Set `CurrentOfficial` = false.** Home/Away are `true`, and official presets list first (the copy sat 3rd) and may auto-select.
- Append it to TeamVisuals `Uniforms`. With CurrentOfficial false it lists last, after Away Option.

**Renaming pieces in the gear picker:** change `DisplayName` in that piece's ItemInfo.
- **NEVER** edit `ItemName`: the game looks pieces up by it. A wrong ItemName = default EA gear, which is what broke TI/JR/Black Helmet 2 during the test.
- Renamed (ItemInfos index): [1350] Treasure Island Helmet, [5087] Treasure Island Pants, [6303] Treasure Island Jersey, [8936] Jolly Roger Helmet, [9536] Jolly Roger Pants, [9740] Jolly Roger Jersey, [9893] Matte Black Helmet. [10096] = U_ECU_JERSEY_2026_GHOST "Slot Test Jersey".

**Frosty limitation:** CollegeFBCharacterPrefab can be EXPORTED but not re-imported as XML. One boxed `FrostySdk.Ebx.PointerRef` (Interface field -> Cranium_HeadVisuals) makes the importer fail, and fully-qualified type names fail too. Edit it in the property grid only.

**Test assets (reuse for Ghost Ship):** ECU_JERSEY_2026_GHOST, U_ECU_JERSEY_2026_GHOST, CFB/ECU/U_UniformType_ECU_Current9thAlternate, registry [10096]. The obsolete CFB/CHAR/U_UniformType_ECU_Current8thAlternate is no longer referenced. Script: scripts/build_slot_test.py.

## 20. Ghost Ship build lessons (2026-11-13)
- **Material (fabric) layers read colorTexture channels as TINT MASKS**, like decals: out = R*colorR + G*colorG + B*colorB.
  A colored PNG shows only its R channel, as gray. Fog = R (white body) + G (mist), with the layer's colorG = the mist color.
- **Fog tile size:** scaleU/V 0.3 smeared the fog into an even wash. 0.12 shows it. The texture has a few big billows per tile.
- **The Frosty texture viewer shows a duplicate's AUTHORED size** (default_mask dups say 16x16 even with a 1024 image inside).
  It is NOT proof the import shrank the image. ECU_JR_Topo_col also reads 16x16 and renders fine.
- **Helmet logo:** pre-colored art + UseDefaults on a matte shell read beige/chrome, because the stock rsm (= the BLA mask) is read raw and the hat channel acts as metal.
  Fix = Jolly Roger style: the stock BLA mask in our dup, tinted (R trim/ECU lavender, G skull white, B hat cool gray), stock normal/rsm and resolve rule.
  Softer lines: make_gs_helmet_logo_mask.py adds K x hat channel into the line pixels (K 0.3 = soft gray, the user's pick; 0.12 = charcoal).
- **Wordmark size:** editing the white jersey's EAST CAROLINA overlay transform had no visible effect.
  Copying Jolly Roger's whole PIRATES overlay (copy_overlay, local instances re-GUIDed) into the same slot (overlay_5) gave the right size.
  The same goes for numbers: copy JR's whole `number_offsetScaleSpacing` block.
- **Numbers/name/wordmark:** R = fill, G (+B for numbers) = outline. The outline shows fine in gray/lavender.
- **Stock white 2021 helmet shell = global_offWhiteHelmetShell (cream).** Use a cool white ColorValue for white/gray looks.
- **Helmet center stripe on a 2021 shell:** copy WHITESCRIPT's overlay_5 (2021 layout) + its local instances, texture -> ECU_JR_Helmet_Stripe_col, tint R/G/B.
- **MMC "FB Uniform Editor"** (Editor tab): live 3D preview (use Reset Preview after imports); "Create Uni Set";
  "Duplicate Asset From Library" + "Register for Team" (it says it adds the CharacterPrefab registration). Try it for the next alternate instead of manual ItemInfos.
- Scripts: build_ghost_ship.py, make_ghost_ship_art.py, png_to_dds.py, make_gs_helmet_logo_mask.py, recolor_skull_logo.py.
- **Helmet side decals are NOT mirrored:** both sides read the texture the same way, so +x is toward the back on the
  LEFT side and toward the front on the RIGHT side. A centered logo (the stock skull) is fine. An off-center one needs a
  texture per side: "Right Side Logo" -> ECU_GS_Helmet_Logo_R_col (dup of ECU_Helmet_2021_BLA_Decal_col), shifted -x.
  Ship logo final: 75% of the skull footprint, shifted 120 px back, 95 px up (make_gs_ship_logo.py SRC OUT 0.75 +/-120 -95).
- Helmet decal surfaces: the stock rsm params were metallic (logo R 0.7 / B 0.5; WHITESCRIPT stripe R 0.775 / G 0.45),
  which made everything chrome. Ghost Ship uses its own LayerCompSurfaceParam (metal 0, reflectance 0.4, smoothness 0.35).
- **The Uniform Editor preview loads every texture; the GAME only loads the piece's bundle.** Ghost Ship's stripe on
  ECU_JR_Helmet_Stripe_col (a dup of WHI_Decal_01, fine on JR's 2025 helmet) showed in the editor but not in game on the
  2021 WHITE-based helmet. Fix: ECU_GS_Helmet_Stripe_col = a dup of ECU_Helmet_2021_BLA_Decal_col (which that helmet loads),
  holding one solid 480 px band in the FiveStripe 2048x1024 layout. Rule of thumb: for helmet decals, duplicate a texture
  the BASE helmet itself references, and confirm in game, not just the editor.


## 21. Ghost Ship (5.0, 2026-11-13) - the first alternate that overwrites nothing
- Pieces: ECU_JERSEY_2026_GHOST / ECU_PANTS_2026_GHOST / ECU_HELMET_2026_GHOST (duplicated part items, content rebuilt from the
  stock ECU 2023 WHITE jersey, 2023 WHITEALT pants and 2021 WHITE helmet), wrappers U_ECU_*_2026_GHOST (Ids 91726001-003),
  preset CFB/ECU/U_UniformType_ECU_Current9thAlternate "Ghost Ship" (LoadoutType Light, CurrentOfficial false), master-list
  entries [10096]-[10098]. Build: scripts/build_ghost_ship.py (+ make_ghost_ship_art.py, make_gs_ship_logo.py, png_to_dds.py).
- Colors (sRGB): body = game white (#D1D1E0); fog = R white / G gray #B5B4BD / B lavender #B9A2DC (lavender mix 0.5, jersey 0.9,
  pants 0.65, tile 0.12); sleeve slash stripes lavender #B9A2DC, middle/cuff stripes + collar + cuffs gray #A9A8B2;
  PIRATES/numbers/nameplate/AAC = gray #9A99A4 fill + lavender #9479D0 outline (AAC star #6F6E78); Jumpmans = gray figure on a
  lavender #9479D0 outline patch; pants stripe #B9A2DC.
- Helmet: shell cool white #E9EAF0 with the matte Kansas preset; facemask #9A99A4; center stripe one solid #B9A2DC band (own dup
  ECU_GS_Helmet_Stripe_col), full length; side logo = the user's ghost ship (tint mask: R lavender #B9A2DC, G white #F2F2F5,
  B gray #C6C6CA; lines = 6% of gray), 75% of the skull footprint, a texture per side (L shifted +120 px, R -120 px, both -95 px);
  all helmet decals matte (metal 0, smoothness 0.35); back AAC + number gray/lavender; bumper text lavender.
- Wordmark + number layout copied whole from Jolly Roger (copy_overlay of PIRATES into overlay_5; number_offsetScaleSpacing block).
- Gloves/cleats: jersey palette primary white, secondary lavender -> WHISEC cleats, TeamColor gloves.

## 22. Polish pass (5.2, 2026-11-13)
- Away helmet (stock 2021 WHITESCRIPT): stripe transform w/offsetV -0.28 -> 0 (full length). scripts/build_away_helmet.py.
- Treasure Island helmet: back AAC + CMU_Jersey_2021_NUM_Array tinted gunmetal fill, gold outline (build_treasure_island.py).
- Jolly Roger helmet: back number via helmet `numberMaterialSettings.offsetScaleSpacing.backnumberoffset_scale`
  x 0.005 -> 0.21 (+x = viewer's right of the stripe), y -0.153 -> -0.06 (more negative = lower); tint R ECU_Gold, G global_whiteHelmet.
  The number array layer has no overlay_transform of its own: helmet number placement lives in backnumberoffset_scale.
- 5.4 (ITEM 4): scripts/build_helmet_numbers.py moves every ECU helmet's back number opposite the AAC logo (x 0.21, y -0.06)
  and tints it like its uniform's jersey numbers (R fill, G outline). It post-processes FINAL/Helmets in place, so
  RUN IT AFTER any per-uniform helmet build (away, TI, Ghost Ship, blackout). The 7 stock helmets no build touches
  (2025 PURPLE_yellowFacemask, 2021 PURPLE_yellowFacemask, PURPLESCRIPT, PURPLETEXT, WHITEUSA, 2021 WHITE_yellowFacemask,
  2025 WHITE_blackfacemask, BLACKSCRIPT) now ship in FINAL for this. Fonts unchanged.

- 5.4 final helmet-back layout (build_helmet_numbers.py, tuned in the Uniform Editor on Jolly Roger, back view):
  flag = dup-free Standard_Helmet_2022_USAFlag_w_Border_col at scale 0.1068 x 0.2495 (width = AAC width), offset -0.1395 / 0.274;
  AAC 0.15 x 0.35 at -0.146 / 0.03; number backnumberoffset_scale x 0.246, y -0.081, size z/w 6.35 / 4.12 (SMALLER z/w = BIGGER number);
  CJ2K sticker = overlay_20, copy of the flag layer (same rearStickers layout map, no normal) with ECU_CJ2K_Sticker_col
  (dup of the flag texture), scale 0.15 x 0.35, offset 0.142 / 0.292. Sticker art drawn 0.895 as wide as tall (measured round).
  Block-font (CMU) helmets: number 90% (z/w 7.06 / 4.58, x 0.236, sticker 0.137). Away (WHITESCRIPT, wide purple-gold-purple stripe):
  everything 85% and pushed out (AAC -0.179, flag -0.1725, number x 0.314 z/w 8.30/5.39, sticker 0.180).
  Overlay offsets: ~650 px/unit across, ~300 px/unit up in that view. Measuring editor screenshots with gold/white masks beat eyeballing.

## 23. Ghost Ship 5.0 polish (ITEM 5, 2026-11-14)
- Helmet: Away-style triple stripe = new art in ECU_GS_Helmet_Stripe_col (stock FiveStripe_02 layout, 2048x1024, bands G122|B135|R509|B135|G122
  centered): R center gray #9A99A4, G outer lavender #B9A2DC, B gaps shell #E9EAF0. Back group uses Away's wide-stripe spacing
  (build_helmet_numbers.py OVR GHOST), number NZ 7.47 / NW 4.85 / X 0.322 for the serif ECU font.
- Jersey: EAST CAROLINA = Away's (WHITEALT) whole overlay_5 "ECU Logo" (ECU_Decal_2021_01_col) copied in, gray fill / lavender outline.
- Pants: stripe channels as on Away's pants (ECU_Pants_2023_Stripe_01_col: R center, G outer, B gaps) = gray / lavender / game white.
- Script: scripts/build_ghost_ship_50.py (post-processes the built files in place).
- **Number fonts obey the bundle rule.** Away's ECU_Jersey_2023_NUM_Array on the Ghost jersey: numbers in the editor, NONE in game.
  ECU_Jersey_2021_NUM_Array referenced directly from the Ghost (2021 WHITE-based) helmet: no helmet number in game.
- **Fix that works: duplicate the font array the piece already loads, import the other font into it.** ECU_GS_Helmet_NUM_Array =
  dup of CMU_Jersey_2021_NUM_Array (512x512 BC7_SRGB, 10 slices = digits 0-9), with ECU_Jersey_2021_NUM_Array's art imported.
  Confirmed in game. Import rules: Frosty imports a TextureArrayAsset from ONE DDS holding every slice (DX10 header, arraySize 10);
  the per-slice dialog entries do not take separate files ("Import one DDS file at a time"). Frosty's own export of an array had
  ~2 slices of trailing data; trimmed to exactly 10 slices before import (Builds/Ghost Ship/Font/ECU_2021_NUM_Array_10digits.dds).
- ECU font arrays store the digit shape in ALPHA (R ~255 everywhere); CMU stores R fill / G outline. The number layer renders both.
- 6.0 font work (ITEM 9) = this same method per piece: dup the array each piece loads, import the target font.

## 24. Jumpman polish (5.1, 2026-11-15)
- **Pre-colored (UseDefaults) layers are STILL TINTED**: output = R*colorR + G*colorG + B*colorB. Section 3's "tint fields ignored" was wrong:
  the gold Jumpman rendered copper (R*ECU_Purple + G*ECU_Gold). Fix: identity tints (local ColorValues 1,0,0 / 0,1,0 / 0,0,1). Measured in the
  editor: Jumpman (230,160,0) = PIRATES (230,160,10). Confirmed in game.
- The colored Jumpman PNGs had an opaque patch (fabric color) around the figure: a visible ring on textured fabric. Rebuilt figure-only
  (alpha x figure weight, RGB = logo color). Ghost Ship keeps its lavender outline patch (design).
- Pants Jumpman = Michigan's on-screen size and spot: scale 0.030 x 0.070, offset 0.143 / 0.262, rotate 8 (was 0.05 x 0.1 at 0.16 / 0.245).
  Michigan's numbers can't be copied (its layer uses Pants_UVSet_front, not in ECU's bundles); matched by pixel-measuring Uniform Editor shots
  with the same camera (~3000 px per UV unit at that zoom). Jerseys (0.03, 0.069 / -0.099) and socks (0.07, 0 / 0.315) already used Michigan's values.
- Scripts: build_pants_jumpman_51.py, build_jumpman_51.py. 

## 25. 6.0 helmets (ITEM 6, 2026-11-16)
- Triple stripes: Home (2025 shell) gold|white|gold purple gaps, Black Pirate/Away Option (2021) gold|purple|gold black gaps, Jolly Roger (2025)
  gold|white|gold charcoal gaps. 2021 helmets copy WHITESCRIPT's overlay_5 + ECU_GS_Helmet_Stripe_col (dup of BLA_Decal); 2025 helmets copy JR's
  overlay_5 + ECU_JR_Helmet_Stripe_col (dup of WHI_Decal_01, triple art re-imported). Matte decal params, no stripe rsm. build_helmets_60.py.
- Back-number fonts = each jersey's font, via font-array copies the helmet already loads (build_helmet_fonts_60.py):
  ECU_Block_NUM_Array_A (dup of ECU_Jersey_2021_NUM_Array, 2023 block art) = Home, Home Option; ECU_Block_NUM_Array_B (dup of CMU array,
  2023 block art) = Away, Blackout; ECU_GS_Helmet_NUM_Array (dup of CMU, 2021 serif art) = Ghost Ship, Treasure Island; Jolly Roger = ECU_Jersey_2021 direct.
  The 2023 block array has R fill / G outline (renders an outline on helmets); the 2021 serif array is alpha-only (no outline on helmets).
- **A duplicate made after the 5.0/6.0 project split has a different ID in each project.** Re-export its XML from the 6.0 copy; FINAL follows 6.0.
- Warning label: EA places it at offsetU 0.325 on the 2025 shell vs 0.349 on 2021. Home moved to 0.349 so its back group uses Away's exact values.
  Jolly Roger keeps its own number spacing (smaller number, 0.325 label), approved as is.
- Back group values (all triple stripes except JR): number 0.314/-0.081 size 8.30x5.39; flag -0.1725/0.274 0.0908x0.2121; AAC -0.179/0.03 0.1275x0.2975;
  CJ2K sticker 0.180/0.292 0.1275x0.2975 (Ghost: serif number 0.322, 7.47x4.85).

## 26. Jersey/pants stripes + Away Option jersey (ITEM 8, 2026-11-16)
- Sleeve stripes: Stripe 1 / Stripe 2 = outer bands, Middle Stripe (WHITEALT: "Gold Stripe") = center, R tint only. Pants ECU_Pants_2023_Stripe_01_col: R center, G outer, B gaps.
- Away Option jersey = new pieces ECU_JERSEY_2026_AWAYOPT + U_ECU_JERSEY_2026_AWAYOPT (Id 91726004), preset Current2ndAlternate -> new wrapper.
  WHITEALT (Adidas 2026 template: equal-width bands, smooth upper fabric, patch collar) kept on purpose to match Away.
- **Import traps seen this session:** XML imported onto the wrong asset (jersey part onto its wrapper -> gray default jersey in game;
  jersey tests onto pants). Always check the Type and File Guid in the grid after an import. And copying a master-list entry by editing it
  in place overwrote Ghost Ship's [10096]; new entries go at the END, then fill in.

## Conference logos after realignment (user test, 2026-11-17)
- Dynasty save with ECU moved to the Big Ten: the **jersey** conference layer (AAC_Decal_2022_Metallic_02_col, AssetResolveRule_UseOverrideRuleset) swapped to the Big Ten logo on every jersey. The **helmet** layer (AAC_Helmet_2022_col on rearStickers, same rule) did NOT show the Big Ten logo on any helmet.
- Helmets show NO logo after the move (not AAC). Helmet decals in helmets/decals/conferences: AAC_Helmet_2022_col, AAC_Helmet_2023_Decal_P6_col; BIG10_Helmet_2022_Bumper_col + BIG10_Helmet_2026_col; BIG12_Helmet_2022_col; CUSA_Helmet_2022_col; ACC 2022 Decal_01/02/03, WithBevel, 2023, 2025. Ohio State wears a Big Ten sticker on the helmet back; Michigan uses the bumper.
- Name-swap theory (AAC_ -> BIG10_ in the file name) fits the jersey (BIG10_Decal_2022_Metallic_02_col exists) but NOT the helmet: moved to the Big 12, whose BIG12_Helmet_2022_col exists, the helmet is still blank. So helmet stickers either don't swap at all (per-team, hidden off-conference) or swap to textures ECU's helmets don't load (bundle rule). Next: see how Ohio State's helmet wires its sticker.
- **Answer: EA's own helmets lose the sticker too.** OSU_HELMET_2021_GREY: overlay_8 'Big Decal' = BIG10_Helmet_2022_Bumper_col (despite the name, that's the rear sticker art) on Helmet_UVSet_rearStickers_col, AssetResolveRule_UseOverrideRuleset, same wiring as ECU's 'AAC  Decal'. Ohio State moved to the Big 12: sticker gone. So the helmet sticker never follows a conference change in this game; the override ruleset drops it off-conference. Jersey patches do follow.
- Options: keep EA behavior (blank after a move), or AssetResolveRule_UseDefaults on the helmet sticker layer (tints still apply, per section 24) to keep the AAC sticker always (untested whether that alone stops the drop).

## Visor clip logos in a third-party helmet mod (2026-11-18)

- A popular helmet and visor mod showed Adidas logos on ECU's visor clips and chin sleeves in every
  mode. That mod is encrypted, so its brand logic wasn't inspected. Testing ruled out every brand
  source this mod controls (roster apparel and gear, dynasty apparel, the team logo sheet, the uniform
  patch slot), which pointed to a built-in team-to-brand list inside that mod.
- Resolution: the other mod's author added a check for ECU's `TeamVisuals.BrandName`. With this mod's
  `JordanBrand_ItemTag` value, ECU gets Jordan clips and chin sleeves. This mod must keep shipping
  `ECUXXX_TeamVisuals` with that BrandName for the check to keep working.
- **Championship logo mechanism found along the way (EA's shared Lua):** in national championship and
  playoff games, the layer compositor replaces jersey and pants logo layers by their patch slot
  (`nike_patch_slot`, `jordan_patch_slot`, `adidas_patch_slot`) with that brand's special decal. Section
  3's fix (pre-colored textures with `UseDefaults`) is why the Jumpman survives it.

## Dynasty gear via Lua (2026-11-18) - WORKED, REJECTED BY USER, REVERTED
- Idea: skip the MyDynasty step by swapping gear at draw time. shoePartLoader_es / handGearPartLoader_es build mesh + preset names from initData.CharacterItemData[slot].Model / .Material; the team is initData.TeamVisuals.AssetName ("ECUXXX").
- Item -> Model/Material has no naming pattern (GearFootwear_shoe_low_AdizeroElectric3 = shoe_low_AdidasAdizero_Electric3; GearFootwear_shoe_low_AirJordan1VaporEdge = shoe_low_Jordan1VaporEdgeFLP; GearFootwear_shoe_mid_AirJordanRetro1 = shoe_mid_AirJordanRetro1). Gloves all use Model "glove"; Material = glove_AdidasAdizero15Electric_teamColor / glove_JordanVaporJet7_TeamColor / glove_JordanSuperbad6_White.
- Rule (ECU only, strings containing "adidas"/"adizero"): cleats shoe_low -> shoe_low_Jordan1VaporEdgeFLP, mid/high -> shoe_mid_AirJordanRetro1; gloves white -> glove_JordanSuperbad6_White, else -> glove_JordanVaporJet7_TeamColor. Colors still come from the player's palette.
- Syntax-checked + helper unit-tested (lupa).
- Result: ECU players drawn in Jordan cleats + gloves; the gear menu still shows the Adidas item names (data unchanged, by design).
- Rejected: without MyDynasty the gear menu only offers Adidas items, so customization still needs MyDynasty; the swap only collapsed every Adidas pick to 2 cleats + 2 gloves. Reverted to EA's scripts. MyDynasty step stays required.

## Home Alternate build note (2026-11-18)
- A Frosty XML import with a broken ref (single backslash, e.g. `..._col\317f...` instead of `..._col\\317f...`) is dropped SILENTLY: the asset keeps its old content, no error.
  Cause: re.sub with a plain replacement string turns `\\` into `\`. Always pass refs to re.sub as `lambda m: REF`. Check generated files with:
  grep -E 'ref="[^"]*[^\\]\\[0-9a-f]{8}-'  (must print nothing)
- If an import "does nothing", export the asset again and diff it against the built file before anything else.
- Home Alternate gray jersey (2026-11-18): the jersey PART ITEM xml had been imported onto the WRAPPER (same trap as ITEM 8). Re-importing each file onto its own asset fixed it. Check Type in the grid (CharacterUniformJerseyItem vs JerseyPartItem) after every import.

## Conference patch colors (2026-11-19)
- Jersey conference layer ('AAC Logo', aac_conference_logo_slot, UseOverrideRuleset) keeps its tints when the art swaps to another conference. ACC_Decal art: R = outline, G = letters, B = oval fill. AAC art: B = the star.
- Treasure Island (ECU_JERSEY_2023_WHITE) had B = ECU_Purple, a color TI doesn't use: purple AAC star, purple ACC oval in an ACC dynasty. Fixed: B -> local ColorValue e8ebca57 (the jersey gunmetal).
- Other jerseys checked, B left alone (already one of the uniform's own colors): Home, Jolly Roger, Home Alternate, Greenville Nights = purple; Black Pirate, Away, Away Alternate = gold; Ghost Ship = its own dark gray. On white jerseys B must NOT be white: G (letters) is white, so the ACC letters would vanish.
