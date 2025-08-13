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
import tomllib
import time
from datetime import datetime, timezone, timedelta

from fontTools.ttLib import TTFont, newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.feaLib.builder import addOpenTypeFeatures

# ────────────────────────────────────────────────────────────────
# 1. Load configuration
# ────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
CONFIG_FILE = HERE / "config.json"

# Load configuration from config.json
with open(CONFIG_FILE, 'r') as f:
    CONFIG = json.load(f)

# Load project information from pyproject.toml
PYPROJECT_FILE = HERE / "pyproject.toml"
with open(PYPROJECT_FILE, 'rb') as f:
    PYPROJECT = tomllib.load(f)

# Font paths
JP_FONT = HERE / CONFIG["fonts"]["input"]["japanese"]
ROMAJI_FONT = HERE / CONFIG["fonts"]["input"]["romaji"]
OUT_FONT = HERE / CONFIG["fonts"]["output"]

# Scaling and positioning parameters
KANA_SCALE = CONFIG["scaling"]["kana_scale"]  # scale factor for Katakana glyph
ROMAJI_SCALE = CONFIG["scaling"]["romaji_scale"]  # scale factor for Romaji glyphs
GAP = CONFIG["positioning"]["gap"]  # vertical gap (FUnits) between Katakana and Romaji
REF_HEIGHT = CONFIG["positioning"]["ref_height"]  # reference Katakana height in Noto Sans JP
VERT_OFFSET = CONFIG["positioning"]["vertical_offset"]  # vertical offset to move glyphs higher
HORIZ_OFFSET = CONFIG["positioning"]["horizontal_offset"]  # horizontal offset to move glyphs right

# Katakana → Romaji (Hepburn, all caps)
# Ordered by Unicode codepoint (30A1-30FC)
ROMAJI: Dict[str, str] = {
    "ァ": "A", "ア": "A", "ィ": "I", "イ": "I", "ゥ": "U",
    "ウ": "U", "ェ": "E", "エ": "E", "ォ": "O", "オ": "O",
    "カ": "KA", "ガ": "GA", "キ": "KI", "ギ": "GI", "ク": "KU",
    "グ": "GU", "ケ": "KE", "ゲ": "GE", "コ": "KO", "ゴ": "GO",
    "サ": "SA", "ザ": "ZA", "シ": "SHI", "ジ": "JI", "ス": "SU",
    "ズ": "ZU", "セ": "SE", "ゼ": "ZE", "ソ": "SO", "ゾ": "ZO",
    "タ": "TA", "ダ": "DA", "チ": "CHI", "ヂ": "JI", "ッ": "ʔ",
    "ツ": "TSU", "ヅ": "ZU", "テ": "TE", "デ": "DE", "ト": "TO", "ド": "DO",
    "ナ": "NA", "ニ": "NI", "ヌ": "NU", "ネ": "NE", "ノ": "NO",
    "ハ": "HA", "バ": "BA", "パ": "PA", "ヒ": "HI", "ビ": "BI", "ピ": "PI",
    "フ": "FU", "ブ": "BU", "プ": "PU", "ヘ": "HE", "ベ": "BE", "ペ": "PE",
    "ホ": "HO", "ボ": "BO", "ポ": "PO",
    "マ": "MA", "ミ": "MI", "ム": "MU", "メ": "ME", "モ": "MO",
    "ャ": "YA", "ヤ": "YA", "ュ": "YU", "ユ": "YU", "ョ": "YO", "ヨ": "YO",
    "ラ": "RA", "リ": "RI", "ル": "RU", "レ": "RE", "ロ": "RO",
    "ワ": "WA", "ヲ": "WO", "ン": "N", "ヴ": "VU", "ー": "-"
}

# Youon combinations mapping
YOUON_COMBINATIONS: Dict[str, str] = {
    # K series
    "キャ": "KYA", "キュ": "KYU", "キョ": "KYO", "キェ": "KYE",
    "ギャ": "GYA", "ギュ": "GYU", "ギョ": "GYO", "ギェ": "GYE",
    "グァ": "GWA", "グィ": "GWI", "グェ": "GWE", "グォ": "GWO",
    # S series
    "シャ": "SHA", "シュ": "SHU", "ショ": "SHO", "シェ": "SHE",
    "ジャ": "JA", "ジュ": "JU", "ジョ": "JO", "ジェ": "JE",
    # T series
    "チャ": "CHA", "チュ": "CHU", "チョ": "CHO", "チェ": "CHE",
    "ヂャ": "JA", "ヂュ": "JU", "ヂョ": "JO", "ヂェ": "JE",
    "ティ": "TI", "トゥ": "TU", "テュ": "TYU",
    "ディ": "DI", "ドゥ": "DU", "デュ": "DYU",
    # N series
    "ニャ": "NYA", "ニュ": "NYU", "ニョ": "NYO", "ニェ": "NYE",
    # H series
    "ヒャ": "HYA", "ヒュ": "HYU", "ヒョ": "HYO", "ヒェ": "HYE",
    "ビャ": "BYA", "ビュ": "BYU", "ビョ": "BYO", "ビェ": "BYE",
    "ピャ": "PYA", "ピュ": "PYU", "ピョ": "PYO", "ピェ": "PYE",
    # F series (foreign sounds)
    "ファ": "FA", "フィ": "FI", "フェ": "FE", "フォ": "FO", "フュ": "FYU",
    # M series
    "ミャ": "MYA", "ミュ": "MYU", "ミョ": "MYO", "ミェ": "MYE",
    # R series
    "リャ": "RYA", "リュ": "RYU", "リョ": "RYO", "リェ": "RYE",
    # W series (foreign sounds)
    "ウィ": "WI", "ウェ": "WE", "ウォ": "WO",
    # V series (foreign sounds)
    "ヴァ": "VA", "ヴィ": "VI", "ヴェ": "VE", "ヴォ": "VO", "ヴュ": "VYU"
}

# Sokuon combinations - ッ + following consonant
SOKUON_COMBINATIONS: Dict[str, str] = {
    # K series
    "ッカ": "KKA", "ッキ": "KKI", "ック": "KKU", "ッケ": "KKE", "ッコ": "KKO",
    "ッガ": "GGA", "ッギ": "GGI", "ッグ": "GGU", "ッゲ": "GGE", "ッゴ": "GGO",
    # S series
    "ッサ": "SSA", "ッシ": "SSHI", "ッス": "SSU", "ッセ": "SSE", "ッソ": "SSO",
    "ッザ": "ZZA", "ッジ": "JJI", "ッズ": "ZZU", "ッゼ": "ZZE", "ッゾ": "ZZO",
    # T series
    "ッタ": "TTA", "ッチ": "CCHI", "ッツ": "TTSU", "ッテ": "TTE", "ット": "TTO",
    "ッダ": "DDA", "ッヂ": "JJI", "ッヅ": "ZZU", "ッデ": "DDE", "ッド": "DDO",
    # P/B series
    "ッパ": "PPA", "ッピ": "PPI", "ップ": "PPU", "ッペ": "PPE", "ッポ": "PPO",
    "ッバ": "BBA", "ッビ": "BBI", "ッブ": "BBU", "ッベ": "BBE", "ッボ": "BBO",
    # F series
    "ッフ": "FFU"
}

# Complex combinations - sokuon + youon (3-character combinations)
COMPLEX_COMBINATIONS: Dict[str, str] = {
    # Sokuon + K youon
    "ッキャ": "KKYA", "ッキュ": "KKYU", "ッキョ": "KKYO", "ッキェ": "KKYE",
    "ッギャ": "GGYA", "ッギュ": "GGYU", "ッギョ": "GGYO", "ッギェ": "GGYE",
    # Sokuon + S youon  
    "ッシャ": "SSHA", "ッシュ": "SSHU", "ッショ": "SSHO", "ッシェ": "SSHE",
    "ッジャ": "JJA", "ッジュ": "JJU", "ッジョ": "JJO", "ッジェ": "JJE",
    # Sokuon + T youon
    "ッチャ": "CCHA", "ッチュ": "CCHU", "ッチョ": "CCHO", "ッチェ": "CCHE",
    "ッティ": "TTI", "ットゥ": "TTU", "ッテュ": "TTYU",
    "ッディ": "DDI", "ッドゥ": "DDU", "ッデュ": "DDYU",
    # Sokuon + H youon
    "ッヒャ": "HHYA", "ッヒュ": "HHYU", "ッヒョ": "HHYO", "ッヒェ": "HHYE",
    "ッビャ": "BBYA", "ッビュ": "BBYU", "ッビョ": "BBYO", "ッビェ": "BBYE",
    "ッピャ": "PPYA", "ッピュ": "PPYU", "ッピョ": "PPYO", "ッピェ": "PPYE",
    # Sokuon + F youon (foreign sounds)
    "ッファ": "FFA", "ッフィ": "FFI", "ッフェ": "FFE", "ッフォ": "FFO", "ッフュ": "FFYU",
    # Sokuon + M youon
    "ッミャ": "MMYA", "ッミュ": "MMYU", "ッミョ": "MMYO", "ッミェ": "MMYE",
    # Sokuon + R youon
    "ッリャ": "RRYA", "ッリュ": "RRYU", "ッリョ": "RRYO", "ッリェ": "RRYE",
    # Sokuon + V youon (foreign sounds)
    "ッヴァ": "VVA", "ッヴィ": "VVI", "ッヴェ": "VVE", "ッヴォ": "VVO", "ッヴュ": "VVYU"
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
        dst_font: TTFont,
        glyph_suffix: str = ""
) -> str:
    cp = ord(kana) if len(kana) == 1 else hash(kana) % 0x10000 + 0xE000
    if len(kana) == 1:
        kana_src = jp.getBestCmap()[cp]
        dst_name = f"kana_{cp:04X}{glyph_suffix}"
    else:
        # For youon/sokuon combinations, use first character as base
        base_cp = ord(kana[0])
        kana_src = jp.getBestCmap()[base_cp]
        dst_name = f"youon_{hash(kana):04X}{glyph_suffix}"

    pen = TTGlyphPen(None)

    if len(kana) == 1:
        # ① Draw single scaled Katakana (with vertical and horizontal offset)
        draw_scaled(pen, jp, kana_src, KANA_SCALE, dx=HORIZ_OFFSET, dy=VERT_OFFSET)
        aw_k, y_k = glyph_metrics(jp, kana_src)
        aw_k_scaled = int(aw_k * KANA_SCALE)
    else:
        # ① Draw multiple Katakana characters for combinations
        total_width = 0
        kana_widths = []

        # Calculate total width first
        for char in kana:
            char_cp = ord(char)
            if char_cp in jp.getBestCmap():
                char_src = jp.getBestCmap()[char_cp]
                aw, _ = glyph_metrics(jp, char_src)
                scaled_width = int(aw * KANA_SCALE)
                kana_widths.append((char_src, scaled_width))
                total_width += scaled_width

        # Draw each character
        x_offset = HORIZ_OFFSET
        for char_src, char_width in kana_widths:
            draw_scaled(pen, jp, char_src, KANA_SCALE, dx=x_offset, dy=VERT_OFFSET)
            x_offset += char_width

        aw_k_scaled = total_width

    # ② Measure Romaji block
    romaji_width = 0
    for ch in romaji_text:
        if ord(ch) in romaji.getBestCmap():
            aw, _ = glyph_metrics(romaji, romaji.getBestCmap()[ord(ch)])
            romaji_width += int(aw * ROMAJI_SCALE)

    x_start = max((aw_k_scaled - romaji_width) // 2, 0) + HORIZ_OFFSET
    y_start = int(REF_HEIGHT * KANA_SCALE) + GAP + VERT_OFFSET

    # ③ Draw Romaji chars
    x_cursor = x_start
    for ch in romaji_text:
        if ord(ch) in romaji.getBestCmap():
            rname = romaji.getBestCmap()[ord(ch)]
            aw, _ = glyph_metrics(romaji, rname)
            draw_scaled(pen, romaji, rname, ROMAJI_SCALE, x_cursor, y_start)
            x_cursor += int(aw * ROMAJI_SCALE)

    # store glyph + metrics
    dst_font["glyf"][dst_name] = pen.glyph()
    dst_font["hmtx"][dst_name] = (aw_k_scaled, 0)
    return dst_name


# ────────────────────────────────────────────────────────────────
# 4. OpenType liga feature generation
# ────────────────────────────────────────────────────────────────
def generate_liga_features(cmap_map: Dict[int, str], youon_glyphs: Dict[str, str], sokuon_glyphs: Dict[str, str],
                           complex_glyphs: Dict[str, str]) -> str:
    """Generate OpenType liga feature code"""
    feature_code = []

    # Ligature rules (order matters - longest combinations first)
    feature_code.append("feature liga {")

    # Add complex ligatures first (3 characters) - highest priority
    for complex_combo, glyph_name in complex_glyphs.items():
        char1, char2, char3 = complex_combo[0], complex_combo[1], complex_combo[2]
        cp1, cp2, cp3 = ord(char1), ord(char2), ord(char3)

        if cp1 in cmap_map and cp2 in cmap_map and cp3 in cmap_map:
            glyph1 = cmap_map[cp1]
            glyph2 = cmap_map[cp2]
            glyph3 = cmap_map[cp3]
            feature_code.append(f"  sub {glyph1} {glyph2} {glyph3} by {glyph_name};")

    # Add youon ligatures (2 characters)
    for youon_combo, glyph_name in youon_glyphs.items():
        char1, char2 = youon_combo[0], youon_combo[1]
        cp1, cp2 = ord(char1), ord(char2)

        if cp1 in cmap_map and cp2 in cmap_map:
            glyph1 = cmap_map[cp1]
            glyph2 = cmap_map[cp2]
            feature_code.append(f"  sub {glyph1} {glyph2} by {glyph_name};")

    # Add sokuon ligatures (2 characters)
    for sokuon_combo, glyph_name in sokuon_glyphs.items():
        char1, char2 = sokuon_combo[0], sokuon_combo[1]
        cp1, cp2 = ord(char1), ord(char2)

        if cp1 in cmap_map and cp2 in cmap_map:
            glyph1 = cmap_map[cp1]
            glyph2 = cmap_map[cp2]
            feature_code.append(f"  sub {glyph1} {glyph2} by {glyph_name};")

    feature_code.append("} liga;")

    return "\n".join(feature_code)


# ────────────────────────────────────────────────────────────────
# 5. Main build routine
# ────────────────────────────────────────────────────────────────
def build_font() -> None:
    print("» Loading source fonts …")
    jp = TTFont(str(JP_FONT))
    romaji = TTFont(str(ROMAJI_FONT))

    print("» Creating blank font …")
    font = TTFont()
    for tag in ("head", "hhea", "maxp", "OS/2", "post"):
        font[tag] = deepcopy(jp[tag])
    
    # Create a clean name table instead of copying the original
    font["name"] = newTable("name")
    font["name"].names = []
    
    # Set font timestamps
    # Fixed creation time: 2025/07/25 at 0:06 JST (UTC+9)
    jst = timezone(timedelta(hours=9))
    creation_time = datetime(2025, 7, 25, 0, 6, 0, tzinfo=jst)
    created_timestamp = int(creation_time.timestamp()) + 2082844800  # Convert to font format
    
    # Current time for modification
    current_time = int(time.time()) + 2082844800  # Convert to font format
    
    font["head"].created = created_timestamp
    font["head"].modified = current_time
    
    # Update fontRevision to match project version
    # Convert version string like "0.1.0" to float like "0.1" 
    version_str = PYPROJECT["project"]["version"]
    version_parts = version_str.split('.')
    font_revision = float(f"{version_parts[0]}.{version_parts[1]}")
    font["head"].fontRevision = font_revision

    font["glyf"] = newTable("glyf");
    font["glyf"].glyphs = {}
    font["hmtx"] = newTable("hmtx");
    font["hmtx"].metrics = {}
    font["loca"] = newTable("loca")

    # .notdef
    font.setGlyphOrder([".notdef"])
    font["glyf"][".notdef"] = deepcopy(jp["glyf"][".notdef"])
    font["hmtx"][".notdef"] = jp["hmtx"][".notdef"]

    # Build basic glyphs
    print("» Building composite glyphs …")
    cmap_map = {}
    for kana, roma in ROMAJI.items():
        gname = make_combined_glyph(jp, romaji, kana, roma, font)
        font.setGlyphOrder(font.getGlyphOrder() + [gname])
        cmap_map[ord(kana)] = gname

    # Build youon combination glyphs
    print("» Building youon ligatures …")
    youon_glyphs = {}
    for youon_combo, roma in YOUON_COMBINATIONS.items():
        gname = make_combined_glyph(jp, romaji, youon_combo, roma, font, "_youon")
        font.setGlyphOrder(font.getGlyphOrder() + [gname])
        youon_glyphs[youon_combo] = gname

    # Build sokuon combination glyphs
    print("» Building sokuon ligatures …")
    sokuon_glyphs = {}
    for sokuon_combo, roma in SOKUON_COMBINATIONS.items():
        gname = make_combined_glyph(jp, romaji, sokuon_combo, roma, font, "_sokuon")
        font.setGlyphOrder(font.getGlyphOrder() + [gname])
        sokuon_glyphs[sokuon_combo] = gname

    # Build complex combination glyphs (sokuon + youon)
    print("» Building complex ligatures …")
    complex_glyphs = {}
    for complex_combo, roma in COMPLEX_COMBINATIONS.items():
        gname = make_combined_glyph(jp, romaji, complex_combo, roma, font, "_complex")
        font.setGlyphOrder(font.getGlyphOrder() + [gname])
        complex_glyphs[complex_combo] = gname

    # ── sync glyf.glyphOrder with the real glyph dict -------------
    glyph_names = list(font["glyf"].glyphs.keys())
    font.setGlyphOrder(glyph_names)  # master list
    font["glyf"].glyphOrder = glyph_names  # glyf table copy

    # ── build cmap by pruning JP cmap -----------------------------
    cmap_tbl = deepcopy(jp["cmap"])
    for sub in cmap_tbl.tables[:]:
        sub.cmap = {cp: cmap_map[cp] for cp in sub.cmap if cp in cmap_map}
        if not sub.cmap:
            cmap_tbl.tables.remove(sub)
    font["cmap"] = cmap_tbl

    # ── add OpenType features (liga) ------------------------------
    print("» Adding OpenType features …")
    try:
        from io import StringIO
        feature_code = generate_liga_features(cmap_map, youon_glyphs, sokuon_glyphs, complex_glyphs)
        feature_file = StringIO(feature_code)
        addOpenTypeFeatures(font, feature_file)
        print("✓ Liga features added successfully")
    except Exception as e:
        print(f"Warning: Could not add liga features: {e}")
        print("Font will work without ligatures")

    # ── recalc bounds (needed by fontTools ≥4.59) -----------------
    glyf = font["glyf"]
    for g in glyf.glyphs.values():
        g.recalcBounds(glyf)

    # ── ascender fix so ruby is not clipped ------------------------
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

    # Set basic name records for multiple platforms
    platforms = [
        (3, 1, 0x409),  # Windows Unicode English
        (0, 3, 0),  # Unicode
        (1, 1, 0),  # Mac Unicode (not Roman)
    ]

    # Get version from pyproject.toml
    project_version = PYPROJECT["project"]["version"]
    project_description = PYPROJECT["project"]["description"]

    for pid, eid, lid in platforms:
        # Basic font identification
        name.setName(fam, 1, pid, eid, lid)  # Family name
        name.setName("Regular", 2, pid, eid, lid)  # Subfamily name
        name.setName(f"{ps}-{project_version}", 3, pid, eid, lid)  # Unique ID
        name.setName(full, 4, pid, eid, lid)  # Full name
        name.setName(ps, 6, pid, eid, lid)  # PostScript name
        name.setName(fam, 16, pid, eid, lid)  # Typographic family
        name.setName("Regular", 17, pid, eid, lid)  # Typographic subfamily

        # Copyright and licensing (nameID 0)
        copyright_text = "Copyright (c) 2025 Zhe (satoi8080). This font is licensed under the MIT License."
        name.setName(copyright_text, 0, pid, eid, lid)

        # Version string (nameID 5) 
        version_text = f"Version {project_version}"
        name.setName(version_text, 5, pid, eid, lid)

        # Trademark (nameID 7)
        trademark_text = "KanaKira is a name of repository of Zhe (satoi8080)."
        name.setName(trademark_text, 7, pid, eid, lid)

        # Designer/Manufacturer (nameID 8)
        manufacturer_text = "Zhe (satoi8080)"
        name.setName(manufacturer_text, 8, pid, eid, lid)

        # Designer (nameID 9) 
        designer_text = "Zhe (satoi8080)"
        name.setName(designer_text, 9, pid, eid, lid)

        # Description (nameID 10)
        description_text = project_description + " Built using Noto Sans JP and Noto Sans Mono fonts for enhanced Japanese language learning."
        name.setName(description_text, 10, pid, eid, lid)
        
        # Vendor URL (nameID 11)
        vendor_url = "https://github.com/satoi8080/KanaKira"
        name.setName(vendor_url, 11, pid, eid, lid)

        # License Description (nameID 13)
        license_description = "This Font Software is licensed under the MIT License. Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files."
        name.setName(license_description, 13, pid, eid, lid)

        # License URL (nameID 14)
        license_url = "https://opensource.org/licenses/MIT"
        name.setName(license_url, 14, pid, eid, lid)

        # Sample text for Font Book preview (nameID 19)
        name.setName("アカサタナハマヤラワ", 19, pid, eid, lid)
        
        # Variations PostScript Name Prefix (nameID 25)
        name.setName(fam, 25, pid, eid, lid)

    print(f"» Saving {OUT_FONT.name} …")
    font.save(str(OUT_FONT))
    print("✓ Done!  →", OUT_FONT.relative_to(HERE))


# ────────────────────────────────────────────────────────────────
# 5. Entrypoint
# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    build_font()
