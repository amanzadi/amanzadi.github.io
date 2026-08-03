# Copilot Instructions for amanzadi.github.io

This repository contains a personal academic homepage deployed via GitHub Pages. It is a **static site generator** that uses Python to convert BibTeX files into HTML.

## Quick Start

- **Build**: `python build.py` — generates `index.html` from BibTeX files and personal data
- **Preview**: Open `index.html` in a browser after building
- **Dependency**: Requires `pybtex` (already present; Python 3.x)
- **No tests or linting**: This project has neither test suite nor linting setup

## Architecture

The site generation is **monolithic**: all logic lives in a single `build.py` file with these key components:

### Data Sources
1. **`build.py`** — Contains all HTML generation logic and personal metadata
2. **`publication_list.bib`** — BibTeX entries for publications (displayed top-to-bottom order)
3. **`talk_list.bib`** — BibTeX entries for talks (displayed top-to-bottom order)

### Build Pipeline
The build process (triggered by running `python build.py`) follows these steps:

1. **Parse BibTeX files** — Uses `pybtex.database.input.bibtex` to parse both `.bib` files
2. **Generate author HTML** — `generate_person_html()` creates author strings with optional links and bold formatting
3. **Render entries** — `get_paper_entry()` and `get_talk_entry()` render individual cards with metadata and artifact links
4. **Assemble page** — `get_index_html()` builds the full Bootstrap 4 page with profile, publications, talks, and footer
5. **Write output** — `write_index_html()` commits the HTML string to disk

### Key Functions

| Function | Purpose |
|----------|---------|
| `get_personal_data()` | Returns name, bio HTML, and footer content |
| `get_author_dict()` | Maps author names to personal website URLs for auto-linking |
| `generate_person_html()` | Converts BibTeX person objects to HTML with optional links/bold formatting |
| `get_paper_entry()` | Renders a publication card (image, title, authors, venue, artifact links, collapsible bibtex) |
| `get_talk_entry()` | Renders a talk card (image, title, venue, optional slides/video links) |
| `get_publications_html()` / `get_talks_html()` | Parse BibTeX and iterate through all entries |
| `get_index_html()` | Assembles the complete HTML page structure |

## Key Conventions

### BibTeX Requirements
- **Publication entries**: `@inproceedings` with required fields: `author`, `title`, `booktitle`, `year`, `img`
- **Talk entries**: `@InProceedings` with required fields: `author`, `title`, `booktitle`, `year`, `img`
- **BibTeX strings**: Both `.bib` files define `@STRING` macros (e.g., `@STRING{IJMS = "..."}`) for venue names. Reference them in entries as lowercase (e.g., `booktitle = ijms`)

### Custom BibTeX Fields
Publications support optional metadata fields for artifact links and rendering:
- `html` — project/paper page URL
- `pdf` — PDF paper URL
- `supp` — supplemental materials
- `video` — video link
- `poster` — poster link
- `code` — code repository URL
- `award` — award text (renders as red label next to title)

Talks support:
- `slides` — slides URL
- `video` — recording/video URL

### Author Linking
- Add author entries to `get_author_dict()` to auto-link their names in paper/talk cards
- The function `generate_person_html()` automatically detects linked names and wraps them in `<a>` tags
- Author highlighting: "Amir Amanzadi" is automatically bolded via `make_bold_name` parameter

### File Organization
- **Assets**: Store all images in `assets/img/` with subdirectories:
  - `assets/img/profile.png` — profile photo
  - `assets/img/publications/` — publication card images
  - `assets/img/talks/` — talk card images
- **Output**: `index.html` is the **committed build artifact** and the file served by GitHub Pages — always regenerate and commit after editing `build.py` or `.bib` files

### Entry Ordering
Entries appear in the order they appear in the BibTeX file (top-to-bottom). No sorting is performed.

### Dependencies and Libraries
- **pybtex** — BibTeX parsing
- **Bootstrap 4** — CSS framework (CDN-linked in HTML output)
- **Font Awesome 6.2.0** — icon library (CDN-linked in HTML output)
- **jQuery 3.2.1 + Popper.js + Bootstrap JS** — for collapsible bibtex and interactive elements

## Workflow

1. **Edit content**: Update personal data in `get_personal_data()`, add/edit entries in `*.bib` files, or modify `get_author_dict()` for new co-authors
2. **Regenerate**: `python build.py`
3. **Preview**: Open `index.html` in a browser to verify rendering
4. **Commit**: Stage and commit both the modified source files (`.py`, `.bib`) and the generated `index.html`

## Common Tasks

- **Add a publication**: Add `@inproceedings` block to `publication_list.bib` with required fields and desired artifact links
- **Add a talk**: Add `@InProceedings` block to `talk_list.bib` with required fields
- **Link a co-author**: Add name → URL mapping to `get_author_dict()`
- **Update profile**: Edit bio/name/links in `get_personal_data()`
- **Change styling**: Modify HTML string in `get_index_html()` or CSS inline styles in entry rendering functions
