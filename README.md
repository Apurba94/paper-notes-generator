# paper-notes-generator

**Create a structured Markdown literature note for every paper in your `.bib` file, ready
for Obsidian, Logseq, Zettlr, Foam or plain Git, without ever overwriting notes you wrote.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

Systematic reading needs systematic notes: what was the question, what methods, what results,
what limitations, and how it relates to *my* work. Creating each note by hand (and copying title,
authors, DOI) is friction that stops people from taking notes at all. This tool generates the
scaffold so you only write the thinking.

## Features

- YAML front matter (citekey, title, authors, year, venue, DOI, tags, status) for Dataview-style queries
- Sections for summary, research question, methods, findings, strengths, limitations, relevance, quotes
- DOI, URL and arXiv links; BibTeX keywords become tags
- Automatic `[[wikilinks]]` between papers sharing a keyword
- Custom templates (`$key`, `$title`, `$authors`, `$year`, `$venue`, `$doi`, `$links`, `$abstract`, `$related`)
- Safe by default: existing notes are never overwritten (use `--overwrite` deliberately)

## Usage

```bash
pip install .
paper-notes-generator library.bib -o vault/literature
paper-notes-generator library.bib -o notes --pattern "{year}-{key}.md" --only vaswani2017
paper-notes-generator library.bib --template my_template.md
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
