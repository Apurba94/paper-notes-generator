"""Render one Markdown note per reference, never overwriting notes you have written in."""
import os
import re
import string

DEFAULT_TEMPLATE = """---
citekey: $key
title: "$title_yaml"
authors: [$authors_yaml]
year: $year
venue: "$venue_yaml"
doi: $doi
tags: [literature-note$tags_yaml]
status: unread
---

# $title

**Authors:** $authors
**Published:** $venue ($year)
**Links:** $links

## Summary (in my own words)

-

## Research question / problem

-

## Methods and data

-

## Key findings

-

## Strengths

-

## Limitations / open questions

-

## How it relates to my work

-

## Quotes and page numbers

> (p. )

## Related notes

$related
"""

_ENTRY = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,")


def parse_bibtex(text):
    entries = []
    for m in _ENTRY.finditer(text):
        if m.group(1).lower() in ("comment", "string", "preamble"):
            continue
        i, depth = text.index("{", m.start()), 0
        for j in range(i, len(text)):
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            if depth == 0:
                break
        f = {}
        for fm in re.finditer(r"([\w-]+)\s*=\s*(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\"[^\"]*\"|\d+)", text[m.end():j]):
            v = fm.group(2)
            f[fm.group(1).lower()] = " ".join((v[1:-1] if v[0] in "{\"" else v).replace("{", "").replace("}", "").split())
        entries.append({"type": m.group(1).lower(), "key": m.group(2), "fields": f})
    return entries


def _people(field):
    out = []
    for a in re.split(r"\s+and\s+", field or ""):
        a = a.strip()
        if not a:
            continue
        if "," in a:
            last, first = [p.strip() for p in a.split(",", 1)]
            a = (first + " " + last).strip()
        out.append(a)
    return out


def _yaml(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def note_filename(entry, pattern="{key}.md"):
    safe_key = re.sub(r"[^\w.\-]", "_", entry["key"])
    return pattern.format(key=safe_key, year=entry["fields"].get("year", "nd"))


def render_note(entry, template=DEFAULT_TEMPLATE, related=()):
    """Fill the template. `related` is a list of citekeys rendered as [[wikilinks]]."""
    f = entry["fields"]
    authors = _people(f.get("author") or f.get("editor"))
    links = []
    if f.get("doi"):
        links.append("[DOI](https://doi.org/%s)" % f["doi"])
    if f.get("url"):
        links.append("[URL](%s)" % f["url"])
    if f.get("eprint") and "arxiv" in f.get("archiveprefix", "arxiv").lower():
        links.append("[arXiv](https://arxiv.org/abs/%s)" % f["eprint"])
    kw = [k.strip().lower().replace(" ", "-") for k in re.split(r"[;,]", f.get("keywords", "")) if k.strip()]
    values = {
        "key": entry["key"],
        "title": f.get("title", entry["key"]),
        "title_yaml": _yaml(f.get("title", entry["key"])),
        "authors": ", ".join(authors) or "unknown",
        "authors_yaml": ", ".join('"%s"' % _yaml(a) for a in authors),
        "year": f.get("year", ""),
        "venue": f.get("journal") or f.get("booktitle") or f.get("publisher") or entry["type"],
        "venue_yaml": _yaml(f.get("journal") or f.get("booktitle") or f.get("publisher") or ""),
        "doi": f.get("doi", ""),
        "links": " | ".join(links) or "-",
        "tags_yaml": "".join(", " + k for k in kw),
        "abstract": f.get("abstract", ""),
        "related": "\n".join("- [[%s]]" % r for r in related) or "-",
    }
    return string.Template(template).safe_substitute(values)


def _related_by_keywords(entries):
    kws = {e["key"]: {k.strip().lower() for k in re.split(r"[;,]", e["fields"].get("keywords", "")) if k.strip()}
           for e in entries}
    return {k: sorted(o for o, s in kws.items() if o != k and s & v) for k, v in kws.items()}


def generate_notes(entries, outdir, template=DEFAULT_TEMPLATE, pattern="{key}.md", overwrite=False):
    """Write one note per entry. Existing notes are kept unless overwrite=True.

    Returns (created, skipped) lists of file paths. Entries sharing a keyword are cross-linked.
    """
    os.makedirs(outdir, exist_ok=True)
    related = _related_by_keywords(entries)
    created, skipped = [], []
    for e in entries:
        path = os.path.join(outdir, note_filename(e, pattern))
        if os.path.exists(path) and not overwrite:
            skipped.append(path)
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(render_note(e, template, related.get(e["key"], [])))
        created.append(path)
    return created, skipped
