#!/usr/bin/env python3
"""
KanaKira – create a Katakana‑only TrueType font whose glyphs combine
           a small Katakana (from Noto Sans JP) with centred Romaji
           ruby (from Noto Sans Mono).

Output: KanaKira‑Regular.ttf
"""

import json
from pathlib import Path
from copy import deepcopy
from typing import Dict, Tuple

from fontTools.ttLib import TTFont, newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen

# ────────────────────────────────────────────────────────────────
# 1. Load configuration
# ────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
CONFIG_FILE = HERE / "config.json"

# Load configuration from config.json
with open(CONFIG_FILE, 'r') as f:
    CONFIG = json.load(f)

# Font paths
JP_FONT    = HERE / CONFIG["fonts"]["input"]["japanese"]
ROMAJI_FONT  = HERE / CONFIG["fonts"]["input"]["romaji"]
OUT_FONT   = HERE / CONFIG["fonts"]["output"]

# Scaling and positioning parameters
KANA_SCALE   = CONFIG["scaling"]["kana_scale"]      # scale factor for Katakana glyph
ROMAJI_SCALE = CONFIG["scaling"]["romaji_scale"]    # scale factor for Romaji glyphs
GAP          = CONFIG["positioning"]["gap"]          # vertical gap (FUnits) between Katakana and Romaji
REF_HEIGHT   = CONFIG["positioning"]["ref_height"]   # reference Katakana height in Noto Sans JP
VERT_OFFSET  = CONFIG["positioning"]["vertical_offset"]    # vertical offset to move glyphs higher
HORIZ_OFFSET = CONFIG["positioning"]["horizontal_offset"]  # horizontal offset to move glyphs right

# Katakana → Romaji (Hepburn, all caps)
ROMAJI: Dict[str, str] = {
    "ア": "A",   "イ": "I",   "ウ": "U",   "エ": "E",   "オ": "O",
    "カ": "KA",  "キ": "KI",  "ク": "KU",  "ケ": "KE",  "コ": "KO",
    "サ": "SA",  "シ": "SHI", "ス": "SU",  "セ": "SE",  "ソ": "SO",
    "タ": "TA",  "チ": "CHI", "ツ": "TSU", "テ": "TE",  "ト": "TO",
    "ナ": "NA",  "ニ": "NI",  "ヌ": "NU",  "ネ": "NE",  "ノ": "NO",
    "ハ": "HA",  "ヒ": "HI",  "フ": "FU",  "ヘ": "HE",  "ホ": "HO",
    "マ": "MA",  "ミ": "MI",  "ム": "MU",  "メ": "ME",  "モ": "MO",
    "ヤ": "YA",  "ユ": "YU",  "ヨ": "YO",
    "ラ": "RA",  "リ": "RI",  "ル": "RU",  "レ": "RE",  "ロ": "RO",
    "ワ": "WA",  "ヲ": "WO",  "ン": "N",
    "ガ": "GA",  "ギ": "GI",  "グ": "GU",  "ゲ": "GE",  "ゴ": "GO",
    "ザ": "ZA",  "ジ": "JI",  "ズ": "ZU",  "ゼ": "ZE",  "ゾ": "ZO",
    "ダ": "DA",  "ヂ": "JI",  "ヅ": "ZU",  "デ": "DE",  "ド": "DO",
    "バ": "BA",  "ビ": "BI",  "ブ": "BU",  "ベ": "BE",  "ボ": "BO",
    "パ": "PA",  "ピ": "PI",  "プ": "PU",  "ペ": "PE",  "ポ": "PO",
    "ァ": "A",   "ィ": "I",   "ゥ": "U",   "ェ": "E",   "ォ": "O",
    "ャ": "YA",  "ュ": "YU",  "ョ": "YO",
    "ッ": "TSU", "ー": "-",   "ヴ": "VU"
}

# ────────────────────────────────────────────────────────────────
# 2. Helper utilities
# ────────────────────────────────────────────────────────────────
def glyph_metrics(font: TTFont, gname: str) -> Tuple[int, int]:
    """Return (advanceWidth, yMax)."""
    aw, _ = font["hmtx"][gname]
    g = font["glyf"][gname]
    return aw, g.yMax if g.numberOfContours else 0


def draw_scaled(
    pen: TTGlyphPen,
    src_font: TTFont,
    gname: str,
    scale: float,
    dx: int = 0,
    dy: int = 0
) -> None:
    """Draw *gname* from *src_font* into *pen* using an affine transform."""
    TransformPen(pen, (scale, 0, 0, scale, dx, dy))
    src_font["glyf"][gname].draw(TransformPen(pen, (scale, 0, 0, scale, dx, dy)),
                                 src_font["glyf"])


# ────────────────────────────────────────────────────────────────
# 3. Build one composite glyph (Katakana + Romaji)
# ────────────────────────────────────────────────────────────────
def make_combined_glyph(
    jp: TTFont,
    romaji: TTFont,
    kana: str,
    romaji_text: str,
    dst_font: TTFont
) -> str:
    cp = ord(kana)
    kana_src = jp.getBestCmap()[cp]
    dst_name = f"kana_{cp:04X}"

    pen = TTGlyphPen(None)

    # ① draw scaled Katakana (with vertical and horizontal offset)
    draw_scaled(pen, jp, kana_src, KANA_SCALE, dx=HORIZ_OFFSET, dy=VERT_OFFSET)

    aw_k, y_k = glyph_metrics(jp, kana_src)
    aw_k_scaled = int(aw_k * KANA_SCALE)

    # ② measure Romaji block
    romaji_width = 0
    for ch in romaji_text:
        aw, _ = glyph_metrics(romaji, romaji.getBestCmap()[ord(ch)])
        romaji_width += int(aw * ROMAJI_SCALE)

    x_start = max((aw_k_scaled - romaji_width) // 2, 0) + HORIZ_OFFSET
    y_start = int(REF_HEIGHT * KANA_SCALE) + GAP + VERT_OFFSET

    # ③ draw Romaji chars
    x_cursor = x_start
    for ch in romaji_text:
        rname = romaji.getBestCmap()[ord(ch)]
        aw, _ = glyph_metrics(romaji, rname)
        draw_scaled(pen, romaji, rname, ROMAJI_SCALE, x_cursor, y_start)
        x_cursor += int(aw * ROMAJI_SCALE)

    # store glyph + metrics
    dst_font["glyf"][dst_name] = pen.glyph()
    dst_font["hmtx"][dst_name] = (aw_k, 0)
    return dst_name


# ────────────────────────────────────────────────────────────────
# 4. Main build routine
# ────────────────────────────────────────────────────────────────
def build_font() -> None:
    print("» Loading source fonts …")
    jp = TTFont(str(JP_FONT))
    romaji = TTFont(str(ROMAJI_FONT))

    print("» Creating blank font …")
    font = TTFont()
    for tag in ("head", "hhea", "maxp", "OS/2", "post", "name"):
        font[tag] = deepcopy(jp[tag])

    font["glyf"] = newTable("glyf"); font["glyf"].glyphs = {}
    font["hmtx"] = newTable("hmtx"); font["hmtx"].metrics = {}
    font["loca"] = newTable("loca")

    # .notdef
    font.setGlyphOrder([".notdef"])
    font["glyf"][".notdef"] = deepcopy(jp["glyf"][".notdef"])
    font["hmtx"][".notdef"] = jp["hmtx"][".notdef"]

    # build glyphs
    print("» Building composite glyphs …")
    cmap_map = {}
    for kana, roma in ROMAJI.items():
        gname = make_combined_glyph(jp, romaji, kana, roma, font)
        font.setGlyphOrder(font.getGlyphOrder() + [gname])
        cmap_map[ord(kana)] = gname

    # ── sync glyf.glyphOrder with the real glyph dict -------------
    glyph_names = list(font["glyf"].glyphs.keys())
    font.setGlyphOrder(glyph_names)          # master list
    font["glyf"].glyphOrder = glyph_names    # glyf table copy

    # ── build cmap by pruning JP cmap -----------------------------
    cmap_tbl = deepcopy(jp["cmap"])
    for sub in cmap_tbl.tables[:]:
        sub.cmap = {cp: cmap_map[cp] for cp in sub.cmap if cp in cmap_map}
        if not sub.cmap:
            cmap_tbl.tables.remove(sub)
    font["cmap"] = cmap_tbl

    # ── recalc bounds (needed by fontTools ≥4.59) -----------------
    glyf = font["glyf"]
    for g in glyf.glyphs.values():
        g.recalcBounds(glyf)

    # ── ascender fix so ruby isn’t clipped ------------------------
    top = max(g.yMax for g in glyf.glyphs.values() if g.numberOfContours)
    hhea, os2 = font["hhea"], font["OS/2"]
    need = top + 20
    if need > hhea.ascent:
        inc = need - hhea.ascent
        hhea.ascent += inc
        os2.sTypoAscender += inc
        os2.usWinAscent += inc

    # ── final counts + maxp stats --------------------------------
    font["hhea"].numberOfHMetrics = len(glyph_names)
    font["maxp"].numGlyphs = len(glyph_names)
    font["maxp"].recalc(font)

    # ── rename family --------------------------------------------
    fam = CONFIG["font_info"]["family_name"]
    full = CONFIG["font_info"]["full_name"]
    ps = CONFIG["font_info"]["postscript_name"]
    name = font["name"]
    for pid, eid, lid in ((3, 1, 0x409), (0, 3, 0)):
        name.setName(fam, 1, pid, eid, lid)
        name.setName(full, 4, pid, eid, lid)
        name.setName(ps, 6, pid, eid, lid)
        name.setName(fam, 16, pid, eid, lid)
        name.setName("Regular", 17, pid, eid, lid)

    print(f"» Saving {OUT_FONT.name} …")
    font.save(str(OUT_FONT))
    print("✓ Done!  →", OUT_FONT.relative_to(HERE))


# ────────────────────────────────────────────────────────────────
# 5. Entrypoint
# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    build_font()
