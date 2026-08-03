# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a personal academic homepage for Amir Hossein Amanzadi, deployed via GitHub Pages at `amanzadi.github.io`. The site is statically generated: `build.py` reads BibTeX files and produces a single `index.html`.

## Building the Site

```bash
python build.py
```

This regenerates `index.html` from the current BibTeX data and personal info. There are no other build steps, no tests, and no linting setup.

## Architecture

The entire site is generated from three sources:

1. **`build.py`** — the only script. It contains all content and logic:
   - `get_personal_data()` — name, bio HTML, social links, and footer
   - `get_author_dict()` — maps co-author names to their URLs for auto-linking
   - `get_publications_html()` / `get_talks_html()` — parse BibTeX and render HTML cards
   - `get_index_html()` — assembles the full page HTML string (Bootstrap 4, Font Awesome 6)
   - `write_index_html()` — writes the result to `index.html`

2. **`publication_list.bib`** — one `@inproceedings` entry per publication, ordered top-to-bottom (first = shown first). Supported custom fields: `img`, `html`, `pdf`, `supp`, `video`, `poster`, `code`, `award`.

3. **`talk_list.bib`** — one `@InProceedings` entry per talk. Supported custom fields: `img`, `slides`, `video`.

`index.html` is the **committed build artifact** — it is what GitHub Pages serves. Always regenerate and commit it after editing `build.py` or the `.bib` files.

## Adding Content

- **New publication**: add an `@inproceedings` block to `publication_list.bib`. Required fields: `author`, `title`, `booktitle`, `year`, `img`. Optional link fields listed above.
- **New talk**: add an `@InProceedings` block to `talk_list.bib`. Required: `author`, `title`, `booktitle`, `year`, `img`.
- **New co-author link**: add an entry to the dict in `get_author_dict()`.
- **Profile photo**: `assets/img/profile.png`
- **Publication/talk images**: `assets/img/publications/` and `assets/img/talks/`

## BibTeX String Abbreviations

`publication_list.bib` defines `@STRING` macros (e.g., `IJMS`, `UU`, `RSC`) for venue names. Use lowercase when referencing them in entries (e.g., `booktitle = ijms`).
