import os
import tempfile
import unittest

from paper_notes_generator.cli import main
from paper_notes_generator.core import generate_notes, note_filename, parse_bibtex, render_note

BIB = r"""
@article{vaswani2017,
  author = {Vaswani, Ashish and Shazeer, Noam},
  title = {Attention Is All You Need},
  journal = {NeurIPS},
  year = {2017},
  doi = {10.5555/3295222},
  eprint = {1706.03762},
  keywords = {transformers; attention}
}
@article{devlin2019,
  author = {Jacob Devlin},
  title = {{BERT}: Pre-training of "Deep" Transformers},
  journal = {NAACL},
  year = 2019,
  keywords = {Transformers, language models}
}
@misc{lonely, title = {Unrelated}}
"""
ENTRIES = parse_bibtex(BIB)


class RenderTests(unittest.TestCase):
    def test_front_matter_and_links(self):
        note = render_note(ENTRIES[0])
        self.assertIn("citekey: vaswani2017", note)
        self.assertIn('authors: ["Ashish Vaswani", "Noam Shazeer"]', note)
        self.assertIn("tags: [literature-note, transformers, attention]", note)
        self.assertIn("[DOI](https://doi.org/10.5555/3295222) | [arXiv](https://arxiv.org/abs/1706.03762)", note)

    def test_yaml_escaping_and_braces(self):
        note = render_note(ENTRIES[1])
        self.assertIn('title: "BERT: Pre-training of \\"Deep\\" Transformers"', note)
        self.assertIn("# BERT: Pre-training", note)

    def test_custom_template_keeps_unknown_placeholders(self):
        self.assertEqual(render_note(ENTRIES[2], "$key | $title | $unknown"), "lonely | Unrelated | $unknown")

    def test_filename_pattern(self):
        self.assertEqual(note_filename(ENTRIES[0], "{year}-{key}.md"), "2017-vaswani2017.md")
        self.assertEqual(note_filename({"key": "a/b:c", "fields": {}}), "a_b_c.md")


class GenerateTests(unittest.TestCase):
    def test_cross_links_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            created, skipped = generate_notes(ENTRIES, d)
            self.assertEqual((len(created), len(skipped)), (3, 0))
            with open(os.path.join(d, "vaswani2017.md"), encoding="utf-8") as fh:
                self.assertIn("- [[devlin2019]]", fh.read())
            path = os.path.join(d, "lonely.md")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("my precious notes")
            created, skipped = generate_notes(ENTRIES, d)
            self.assertEqual(len(skipped), 3)
            with open(path, encoding="utf-8") as fh:
                self.assertEqual(fh.read(), "my precious notes")

    def test_cli_only(self):
        with tempfile.TemporaryDirectory() as d:
            bib = os.path.join(d, "r.bib")
            with open(bib, "w", encoding="utf-8") as fh:
                fh.write(BIB)
            main([bib, "-o", os.path.join(d, "n"), "--only", "lonely"])
            self.assertEqual(os.listdir(os.path.join(d, "n")), ["lonely.md"])


if __name__ == "__main__":
    unittest.main()
