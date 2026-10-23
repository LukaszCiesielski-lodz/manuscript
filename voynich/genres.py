"""Medieval genres with little or no syntax, as comparison texts: litany, barbarous names of ritual magic.

The manuscript's signature (no tie between different words at a distance, an excess of repeats
and one-glyph variants inside a line, neighbours of similar length) is what a copying scribe
leaves, but some genuine medieval genres might leave it too: a litany repeats a frame with a
changing name; the "voces magicae" of the Ars Notoria and Liber Iuratus are deliberately
meaningless strings with echoes and variants (Lemogethom, Hegemochom, Hazachay, Hazatha...).
Texts are fetched by scripts/fetch_genres.py into data/reference/genres/ (not committed).
"""

from __future__ import annotations

import re
from pathlib import Path

from . import corpus, lexicon

GENRES_DIR = corpus.REFERENCE_DIR / "genres"
LITANY_URL = "https://la.wikisource.org/w/api.php?action=parse&page=Litaniae_Sanctorum&prop=wikitext&format=json&formatversion=2"
NOTORIA_URL = "http://www.esotericarchives.com/notoria/notoria.htm"
IURATUS_URL = "http://www.esotericarchives.com/juratus/juratus.htm"


def litany_words(wikitext: str) -> list[str]:
    """Words of the litany in reading order; R. / V. markers, headings and templates dropped."""
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", wikitext)  # [[target|shown]] -> shown
    text = re.sub(r"\{\{[^}]*\}\}|<[^>]+>|==+[^=]*==+", " ", text)
    text = re.sub(r"\b[RV]\.\s", " ", text)
    return [w for w in (lexicon.normalize(t) for t in re.findall(r"[A-Za-zÀ-ÿ]+", text)) if w]


def barbarous_names(html_or_markdown: str, known: set[str]) -> list[str]:
    """Capitalized words from runs of names (italic lists in the Esoteric Archives editions) that are
    neither Latin nor English dictionary words, in order of appearance."""
    text = re.sub(r"<[^>]+>", " ", html_or_markdown)
    out = []
    for span in re.findall(r"[_*]([^_*\n]{15,}?)[_*]", text):
        toks = re.findall(r"[A-Za-zÀ-ÿ]+", span)
        caps = [t for t in toks if t[0].isupper() and len(t) >= 4]
        if len(caps) >= 4 and len(caps) >= 0.8 * len(toks):
            out += [n for n in (lexicon.normalize(t) for t in caps) if n and n not in known]
    return out


def known_words() -> set[str]:
    out: set[str] = set()
    for name in ("Latin", "MedievalLatin", "English"):
        try:
            out |= set(lexicon.load(name)[0])
        except FileNotFoundError:
            pass
    return out


def load(name: str) -> list[str]:
    path = GENRES_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - run: python scripts/fetch_genres.py")
    return path.read_text(encoding="utf-8").split()


def available() -> list[str]:
    return sorted(p.stem for p in GENRES_DIR.glob("*.txt")) if GENRES_DIR.exists() else []
