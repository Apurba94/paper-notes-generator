"""Command-line interface for paper-notes-generator."""
import argparse

from .core import DEFAULT_TEMPLATE, generate_notes, parse_bibtex


def main(argv=None):
    ap = argparse.ArgumentParser(prog="paper-notes-generator",
                                 description="Create a Markdown literature note for every BibTeX entry.")
    ap.add_argument("bibfile")
    ap.add_argument("-o", "--outdir", default="notes")
    ap.add_argument("--template", help="custom template file using $key, $title, $authors, $year, $venue, "
                                       "$doi, $links, $abstract, $related ...")
    ap.add_argument("--pattern", default="{key}.md", help="file name pattern, e.g. '{year}-{key}.md'")
    ap.add_argument("--only", action="append", default=[], help="only these citekeys (repeatable)")
    ap.add_argument("--overwrite", action="store_true", help="replace existing notes (default keeps them)")
    args = ap.parse_args(argv)

    template = DEFAULT_TEMPLATE
    if args.template:
        with open(args.template, encoding="utf-8") as fh:
            template = fh.read()
    with open(args.bibfile, encoding="utf-8") as fh:
        entries = parse_bibtex(fh.read())
    if args.only:
        entries = [e for e in entries if e["key"] in args.only]
    created, skipped = generate_notes(entries, args.outdir, template, args.pattern, args.overwrite)
    print("%d note(s) created, %d existing note(s) kept in %s" % (len(created), len(skipped), args.outdir))
    return 0
