#!/bin/sh
# Full rebuild. Re-imports the spreadsheets, which overwrites hand edits to
# products.source.json — for a price change, run build.py + validate.py only.
set -e
cd "$(dirname "$0")"
python import_lists.py --force
python make_images.py
python make_font.py
python make_icons.py
python review_sheet.py
python build.py
python make_upload.py      # runs validate.py first; writes dist/concept-store-upload.zip
