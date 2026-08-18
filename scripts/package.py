"""Package the built fonts together with their license into a release zip.

The OFL requires the license to travel with every copy of the Font Software, so
``OFL.txt`` goes into the archive alongside the ``.ttf`` files. Run ``main.py``
first; this script only collects what is already built.
"""

import json
import tomllib
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

with open(HERE / "config.json") as f:
    CONFIG = json.load(f)

with open(HERE / "pyproject.toml", "rb") as f:
    PYPROJECT = tomllib.load(f)

# CanTone builds several variants; KanaKira builds a single font.
if "variants" in CONFIG:
    fonts = [variant["output"] for variant in CONFIG["variants"]]
else:
    fonts = [CONFIG["fonts"]["output"]]

name = f"{CONFIG['package_name']}-v{PYPROJECT['project']['version']}"
members = [*fonts, "OFL.txt"]

missing = [m for m in members if not (HERE / m).exists()]
if missing:
    raise SystemExit(f"missing {', '.join(missing)} - run `uv run main.py` first")

out = HERE / f"{name}.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
    for member in members:
        archive.write(HERE / member, f"{name}/{Path(member).name}")

print(f"✓ Saved {out.name}")
