# KatakanaKira

KatakanaKira is a TrueType font that combines Katakana characters with their Romaji equivalents, displaying the Romaji text above each Katakana character.

## Features

- **Dual-script glyphs**: Katakana with centered Romaji above
- **Complete coverage**: All standard Katakana with Hepburn romanization
- **Quality base fonts**: Built using Noto Sans JP and Noto Sans Mono
- **Optimized spacing**: Calibrated vertical spacing between elements

## Installation

### Requirements
- Python 3.12+
- FontTools 4.59.0+

### Setup
1. Clone this repository:
   ```
   git clone https://github.com/satoi8080/KatakanaKira.git
   cd KatakanaKira
   ```

2. Install dependencies:
   ```
   pip install fonttools>=4.59.0
   ```
   
   Or with uv:
   ```
   uv pip install -e .
   ```

## Usage

### Configuration

The font generation process is controlled by a `config.json` file with the following parameters:

- **version**: Font version number
- **fonts**: Input and output font paths
  - **input.japanese**: Path to the Japanese font (Katakana source)
  - **input.romaji**: Path to the monospace font (Romaji source)
  - **output**: Path for the generated font file
- **scaling**: Size adjustment parameters
  - **kana_scale**: Scale factor for Katakana glyphs
  - **romaji_scale**: Scale factor for Romaji glyphs
- **positioning**: Position adjustment parameters
  - **gap**: Vertical gap between Katakana and Romaji
  - **ref_height**: Reference Katakana height
  - **vertical_offset**: Vertical offset for glyphs
  - **horizontal_offset**: Horizontal offset for glyphs
- **font_info**: Font naming information
  - **family_name**: Font family name
  - **full_name**: Full font name
  - **postscript_name**: PostScript font name

You can modify these parameters to customize the font generation process.

### Building the Font

Run the main script to build the font:
```
python main.py
```

This generates the font file specified in the config.json (default: `KatakanaKiraSans-Regular.ttf`) in the project directory.

After building, you can install the font on your system, use it in applications that support TrueType fonts, or incorporate it into web designs with @font-face CSS rules.

## How It Works

The font creation process:
1. Loads Noto Sans JP and Noto Sans Mono fonts
2. Scales Katakana and Romaji
3. Positions Romaji above Katakana with proper spacing
4. Centers Romaji horizontally above each character
5. Creates a new font with these composite glyphs

## Character Coverage

Includes all standard Katakana with Hepburn romanization:
- Basic Katakana (ア, イ, ウ, etc.)
- Voiced Katakana (ガ, ギ, グ, etc.)
- Small Katakana (ァ, ィ, ゥ, etc.)
- Special characters (ー, ヴ)

## Dependencies

- [FontTools](https://github.com/fonttools/fonttools): Font manipulation library
- [Noto Sans JP](https://fonts.google.com/noto/specimen/Noto+Sans+JP): Katakana glyphs
- [Noto Sans Mono](https://fonts.google.com/noto/specimen/Noto+Sans+Mono): Romaji text

## License

This project is licensed under the MIT License - see the LICENSE file for details.

The Noto fonts are licensed under the SIL Open Font License 1.1. Full license text in `Noto_Sans_JP/OFL.txt` and `Noto_Sans_Mono/OFL.txt`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Created with ❤️ for Japanese language learners and typography enthusiasts.