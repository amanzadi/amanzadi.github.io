# Amir H. Amanzadi — Personal Website

Source files for [amanzadi.github.io](https://amanzadi.github.io/), a statically generated academic website hosted with GitHub Pages.

## How it works

- `build.py` generates `index.html` and `cv.html`.
- `publication_list.bib` stores the publication metadata and BibTeX records.
- `talk_list.bib` stores talks shown in the Work section.
- Publication images can be added manually under `assets/img/publications/`.
- `sync_publications.py` checks ORCID and DOI metadata while preserving curated links and images.

## Local development

```bash
python -m pip install -r requirements.txt
python build.py
```

The generated pages can be previewed with any local static server, for example:

```bash
python -m http.server
```

## Publication updates

Publication metadata is refreshed automatically once a month through GitHub Actions. It can also be started manually from the **Actions** tab using the **Update publications** workflow. The workflow creates a pull request for review before changes are merged.

To update publications locally:

```bash
python sync_publications.py
python build.py
```

## Deployment

The **Deploy website** GitHub Actions workflow runs on every push to `main`, rebuilds the pages, and publishes them through GitHub Pages. It can also be triggered manually from the **Actions** tab.
