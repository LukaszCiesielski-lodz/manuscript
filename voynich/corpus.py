"""High-level access to the Voynich text and to reference corpora."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from . import eva, ivtff

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ZL_FILE = DATA / "raw" / "ZL3b-n.txt"
REFERENCE_DIR = DATA / "reference"


@dataclass
class Line:
    folio: str
    locus: str
    kind: str
    section: str
    language: str
    hand: str
    quire: str
    words: list[str]


def load_voynich(path: str | Path = ZL_FILE, drop_uncertain: bool = True) -> list[Line]:
    lines = []
    for page in ivtff.parse(path):
        for locus in page.loci:
            ws = eva.words(eva.clean(locus.raw), drop_uncertain=drop_uncertain)
            if ws:
                lines.append(Line(page.folio, locus.number, locus.kind, page.section,
                                  page.language, page.hand, page.quire, ws))
    return lines


def tokens(lines: list[Line], paragraphs_only: bool = False, **where: str) -> list[str]:
    """Flatten lines to a word list, filtered by Line attributes, e.g. language="B"."""
    out: list[str] = []
    for line in lines:
        if paragraphs_only and not line.kind.startswith("P"):
            continue
        if all(getattr(line, k) == v for k, v in where.items()):
            out.extend(line.words)
    return out


# Hebrew points/cantillation and Arabic harakat: optional vowel marks, not letters.
_SEMITIC_MARKS = re.compile("[֑-ׇً-ٰٟ]")


def normalize_words(text: str) -> list[str]:
    """Lowercase and keep runs of letters (precomposed letters like 'ą' stay whole)."""
    text = _SEMITIC_MARKS.sub("", unicodedata.normalize("NFC", text.lower()))
    return re.findall(r"[^\W\d_]+", text)


def reference_languages() -> list[str]:
    return sorted(p.stem for p in REFERENCE_DIR.glob("*.txt"))


def load_reference(language: str, limit: int | None = None) -> list[str]:
    path = REFERENCE_DIR / f"{language}.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - run: python scripts/fetch_data.py")
    ws = path.read_text(encoding="utf-8").split()
    return ws[:limit] if limit else ws
