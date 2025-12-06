# KanaKira

**A unique Japanese learning font that displays Romaji above Katakana characters**

Perfect for Japanese language students, educators, and anyone learning to read Katakana! KanaKira Sans shows you both
the Katakana character and its pronunciation in one beautiful, easy-to-read font.

*Example: When you type アリガトウ, you'll see "A", "RI", "GA", "TO", "U" displayed above each character*

![KanaKira Sans Preview](assets/KanaKira_Sans_Preview.png)

## ✨ What makes KanaKira special?

- **Learn faster**: See pronunciation while reading Katakana
- **Beautiful design**: Clean, readable typography based on Google's Noto fonts
- **Complete coverage**: All Katakana characters including combinations (キャ, ッチ, etc.)
- **Ready to use**: Works in any app that supports TrueType fonts

## 🚀 Quick Start

### Step 1: Get the Font

**Option A: Download Pre-built Font (Recommended)**

Download the latest `KanaKiraSans-Regular.ttf` from
the [Releases Page](https://github.com/satoi8080/KanaKira/releases) - no build required!

**Option B: Build from Source**

Build the font from source (it's easier than it sounds!):

**Requirements:**

- Python 3.12+
- FontTools library

**Build Steps:**

1. Clone and setup:
   ```bash
   git clone https://github.com/satoi8080/KanaKira.git
   cd KanaKira
   pip install fonttools>=4.59.0
   ```

2. Build the font:
   ```bash
   python main.py
   ```

3. Find your font: `KanaKiraSans-Regular.ttf` will be created in the project folder

### Step 2: Install the Font

Once you have `KanaKiraSans-Regular.ttf`:

- **Windows**: Right-click → "Install"
- **Mac**: Double-click → "Install Font"
- **Linux**: Copy to `~/.fonts/` or `/usr/share/fonts/`

## 🎯 How to Use

Once installed, KanaKira Sans works like any other font:

- **In Word processors**: Type Katakana and see Romaji appear above automatically
- **In learning apps**: Perfect for flashcards and study materials
- **On websites**: Use with CSS `font-family: 'KanaKira Sans'`
- **In presentations**: Great for teaching materials

**Example text to try:** アリガトウゴザイマス (Thank you very much!)

## ⚙️ Customization

Want to adjust the font? Edit `config.json` to change:

- Romaji size and positioning
- Katakana scaling
- Vertical spacing between characters
- Font naming

Then rebuild with `python main.py`

## 📚 What's Included

KanaKira Sans covers all Katakana characters you need:

**Basic Characters**: ア イ ウ エ オ カ キ ク...  
**Voiced Sounds**: ガ ギ グ ゲ ゴ ザ ジ ズ...  
**Small Characters**: ァ ィ ゥ ェ ォ ッ ャ ュ ョ  
**Combinations**: キャ シュ チョ ニャ...  
**Double Consonants**: ッカ ッキ ック...  
**Special Characters**: ー ヴ ン

## 🛠️ Technical Details

Built with love using:

- **Base fonts**: Google's Noto Sans JP + Noto Sans Mono
- **Technology**: Python + FontTools library
- **Format**: TrueType (.ttf) with OpenType ligature features
- **Encoding**: Full Unicode support

## 📄 License

This repository is licensed in two parts:

- **The font** (KanaKira Sans): [SIL Open Font License 1.1](OFL.txt). It is built from
  Noto Sans JP and Noto Sans Mono, also under OFL 1.1; the OFL requires derivative
  fonts to stay under the OFL. Free to use in any project, including commercially —
  just keep the license notice with the font and don't sell the font by itself.
- **Source code and build tooling**: [MIT](LICENSE).

## 🤝 Contributing & Support

- **Found a bug?** [Open an issue](https://github.com/satoi8080/KanaKira/issues)
- **Have ideas?** [Start a discussion](https://github.com/satoi8080/KanaKira/discussions)
- **Want to contribute?** Pull requests welcome!

---

**Made with ❤️ for Japanese learners worldwide**  
*Perfect for students, teachers, and typography enthusiasts*