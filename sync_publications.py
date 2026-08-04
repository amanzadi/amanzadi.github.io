#!/usr/bin/env python3
"""Refresh publication_list.bib from public ORCID and DOI metadata."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


ORCID = "0000-0002-0243-5900"
BIB_PATH = Path("publication_list.bib")
DEFAULT_IMAGE = "assets/img/publications/default.svg"
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".svg")


@dataclass
class BibEntry:
    kind: str
    key: str
    fields: dict[str, str] = field(default_factory=dict)


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "amanzadi.github.io publication updater"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def balanced_end(text: str, start: int) -> int:
    depth = 0
    quote_open = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            quote_open = not quote_open
        elif not quote_open and char == "{":
            depth += 1
        elif not quote_open and char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError("unclosed BibTeX entry")


def split_top_level(text: str, delimiter: str = ",") -> list[str]:
    parts, start, depth = [], 0, 0
    quote_open = False
    for index, char in enumerate(text):
        if char == '"' and (index == 0 or text[index - 1] != "\\"):
            quote_open = not quote_open
        elif not quote_open and char == "{":
            depth += 1
        elif not quote_open and char == "}":
            depth -= 1
        elif not quote_open and depth == 0 and char == delimiter:
            parts.append(text[start:index].strip())
            start = index + 1
    parts.append(text[start:].strip())
    return [part for part in parts if part]


def clean_value(value: str) -> str:
    value = value.strip().rstrip(",").strip()
    if len(value) >= 2 and value[0] == "{" and value[-1] == "}":
        return value[1:-1].strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def parse_fields(body: str) -> dict[str, str]:
    fields = {}
    for part in split_top_level(body):
        if "=" not in part:
            continue
        name, value = part.split("=", 1)
        fields[name.strip().lower()] = clean_value(value)
    return fields


def parse_bibtex(text: str) -> tuple[str, list[BibEntry]]:
    entries = []
    matches = list(re.finditer(r"@(?!string\b)([A-Za-z]+)\s*[({]", text, re.I))
    prefix = text[:matches[0].start()] if matches else text
    for match in matches:
        start = match.end() - 1
        end = balanced_end(text, start)
        body = text[start + 1:end - 1]
        parts = split_top_level(body)
        if not parts:
            continue
        key = parts[0].strip()
        entries.append(BibEntry(match.group(1), key, parse_fields(",".join(parts[1:]))))
    return prefix, entries


def format_bibtex(prefix: str, entries: list[BibEntry]) -> str:
    chunks = [prefix.rstrip(), ""]
    for entry in entries:
        chunks.append(f"@{entry.kind}{{{entry.key},")
        for name, value in entry.fields.items():
            if re.fullmatch(r"[a-z][a-z0-9_]*", value) and name == "booktitle":
                rendered = value
            else:
                rendered = "{" + value.replace("}", "}").strip() + "}"
            chunks.append(f"  {name:<14} = {rendered},")
        chunks.extend(["}", ""])
    return "\n".join(chunks)


def title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def orcid_work_summaries() -> list[dict]:
    data = fetch_json(f"https://pub.orcid.org/v3.0/{ORCID}/works")
    summaries = []
    for group in data.get("group", []):
        summaries.extend(group.get("work-summary", []))
    return summaries


def external_id(summary: dict, wanted: str) -> str:
    for item in summary.get("external-ids", {}).get("external-id", []):
        if item.get("external-id-type", "").lower() == wanted:
            return item.get("external-id-value", "").strip()
    return ""


def summary_title(summary: dict) -> str:
    return summary.get("title", {}).get("title", {}).get("value", "").strip()


def summary_year(summary: dict) -> str:
    return str(summary.get("publication-date", {}).get("year", {}).get("value", ""))


def crossref_record(doi: str) -> dict:
    return fetch_json(f"https://api.crossref.org/works/{quote(doi, safe='')}").get("message", {})


def normalized_work(summary: dict) -> dict:
    doi = external_id(summary, "doi")
    try:
        record = crossref_record(doi) if doi else {}
    except Exception as error:
        print(f"warning: DOI lookup failed for {doi}: {error}", file=sys.stderr)
        record = {}
    title = (record.get("title") or [summary_title(summary)])[0].strip()
    authors = []
    for author in record.get("author", []):
        name = " ".join(part for part in (author.get("given"), author.get("family")) if part)
        if name:
            authors.append(name)
    if not authors:
        authors = ["Amir Amanzadi"]
    container = (record.get("container-title") or [""])[0]
    year = str((record.get("published", {}).get("date-parts") or [[summary_year(summary)]])[0][0])
    return {
        "doi": doi,
        "title": title,
        "authors": authors,
        "booktitle": container or summary.get("type", "research-output"),
        "year": year,
        "html": record.get("URL") or summary.get("url", {}).get("value") or (f"https://doi.org/{doi}" if doi else ""),
    }


def image_for_key(key: str) -> str:
    for suffix in IMAGE_SUFFIXES:
        candidate = Path("assets/img/publications") / f"{key}{suffix}"
        if candidate.exists():
            return candidate.as_posix()
    return DEFAULT_IMAGE


def update_entries(entries: list[BibEntry], works: list[dict]) -> int:
    by_doi = {entry.fields.get("doi", "").lower(): entry for entry in entries if entry.fields.get("doi")}
    by_title = {title_key(entry.fields.get("title", "")): entry for entry in entries}
    changed = 0
    for work in works:
        entry = by_doi.get(work["doi"].lower()) if work["doi"] else None
        entry = entry or by_title.get(title_key(work["title"]))
        is_new = entry is None
        if entry is None:
            base = re.sub(r"[^A-Za-z0-9]+", "", work["title"].title())[:24] or "Publication"
            key = f"{base}{work['year']}"
            used = {item.key for item in entries}
            suffix = 2
            while key in used:
                key = f"{base}{work['year']}_{suffix}"
                suffix += 1
            entry = BibEntry("inproceedings", key, {"img": image_for_key(key), "html": work["html"]})
            entries.append(entry)
            changed += 1
        before = dict(entry.fields)
        if is_new:
            entry.fields.update({
                "author": " and ".join(work["authors"]),
                "title": work["title"],
                "booktitle": work["booktitle"],
                "year": work["year"],
            })
        if work["doi"] and not entry.fields.get("doi"):
            entry.fields["doi"] = work["doi"]
        if work["html"] and not entry.fields.get("html"):
            entry.fields["html"] = work["html"]
        if entry.fields.get("img") == DEFAULT_IMAGE:
            entry.fields["img"] = image_for_key(entry.key)
        if entry.fields != before:
            changed += 1
    return changed


def check() -> None:
    _, entries = parse_bibtex(BIB_PATH.read_text(encoding="utf-8"))
    assert entries, "no BibTeX entries found"
    assert len({entry.key for entry in entries}) == len(entries), "duplicate BibTeX keys"
    assert all(entry.fields.get("title") and entry.fields.get("author") for entry in entries), "incomplete entry"
    print(f"checked {len(entries)} publication entries")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate the existing BibTeX without network access")
    args = parser.parse_args()
    if args.check:
        check()
        return 0
    prefix, entries = parse_bibtex(BIB_PATH.read_text(encoding="utf-8"))
    works = [normalized_work(summary) for summary in orcid_work_summaries()]
    changed = update_entries(entries, works)
    BIB_PATH.write_text(format_bibtex(prefix, entries), encoding="utf-8")
    print(f"processed {len(works)} ORCID works; changed {changed} BibTeX records")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"publication sync failed: {error}", file=sys.stderr)
        raise
