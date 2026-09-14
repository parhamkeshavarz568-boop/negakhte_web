#!/bin/sh
# Full rebuild from source. Run from the project root:
#     sh build/all.sh
set -e
cd "$(dirname "$0")/.."
python3 build/make_font.py
python3 build/make_images.py
python3 build/make_icons.py
python3 build/build_catalog.py
python3 build/build.py
python3 build/check_font.py
python3 build/validate.py
