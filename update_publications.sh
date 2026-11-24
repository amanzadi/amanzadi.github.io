#!/bin/bash
# Local publication refresh: ORCID + Google Scholar -> build -> commit -> push (Pages deploy runs on push).
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || { python3 -m venv .venv; .venv/bin/pip install -q -r requirements.txt -r requirements-local.txt; }
.venv/bin/python sync_publications.py
.venv/bin/python build.py
git add publication_list.bib index.html cv.html
git diff --cached --quiet && { echo "No publication changes."; exit 0; }
git commit -m "Update publications from Google Scholar/ORCID"
git push
