"""Generate structured literature notes from BibTeX entries."""
from .core import parse_bibtex, render_note, note_filename, generate_notes, DEFAULT_TEMPLATE

__version__ = "0.1.0"
__all__ = ["parse_bibtex", "render_note", "note_filename", "generate_notes", "DEFAULT_TEMPLATE"]
