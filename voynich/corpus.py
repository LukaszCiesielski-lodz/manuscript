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
MEDIEVAL_DIR = REFERENCE_DIR / "medieval"

# What scripts/fetch_data.py must produce. Analyses compare against all of these, so a
# missing or truncated file silently changes every distance; data_problems() guards that.
BIBLE_LANGUAGES = ["Latin", "Italian", "German", "Polish", "Czech", "English", "Hungarian",
                   "Finnish", "Turkish", "Hebrew", "Arabic", "Vietnamese", "Basque"]
# Basque exists in the corpus only as the New Testament (Leizarraga, 1571, original spelling).
BIBLE_FILES = {"Basque": "Basque-NT"}
# Modern prose samples kept apart from the Bible set: name -> minimum words.
EXTRA_DIR = REFERENCE_DIR / "extra"
EXTRA_TEXTS = {"basque_news": 60_000}
BIBLE_WORDS = 60_000
MEDIEVAL_NAMES = ["Isidorus", "Hugo", "Alfonsi", "Conches", "Aquinas", "Voragine", "Dante", "Petrarca",
                  "Gesta", "Kempis", "Poggio", "Columella"]
MEDIEVAL_MIN_WORDS = 13_000


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


def medieval_texts() -> list[str]:
    return sorted(p.stem for p in MEDIEVAL_DIR.glob("*.txt"))


def load_medieval(name: str, limit: int | None = None, merge_uv: bool = True) -> list[str]:
    """Medieval Latin sample; stored with v/j kept so it can be syllabified first."""
    path = MEDIEVAL_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - run: python scripts/fetch_data.py")
    ws = path.read_text(encoding="utf-8").split()[:limit] if limit else path.read_text(encoding="utf-8").split()
    return [w.replace("j", "i").replace("v", "u") for w in ws] if merge_uv else ws


def word_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split()) if path.exists() else 0


def data_problems() -> list[str]:
    """Missing or truncated data files, as readable messages; empty when everything is in place."""
    out = []
    if not ZL_FILE.exists():
        out.append(f"brak transliteracji {ZL_FILE.name}")
    for lang in BIBLE_LANGUAGES:
        n = word_count(REFERENCE_DIR / f"{lang}.txt")
        if n < BIBLE_WORDS:
            out.append(f"{lang}.txt: {n} słów zamiast {BIBLE_WORDS}")
    extra = sorted(set(reference_languages()) - set(BIBLE_LANGUAGES))
    if extra:
        out.append("nieoczekiwane pliki w data/reference: " + ", ".join(f"{e}.txt" for e in extra))
    for name, minimum in EXTRA_TEXTS.items():
        n = word_count(EXTRA_DIR / f"{name}.txt")
        if n < minimum:
            out.append(f"extra/{name}.txt: {n} słów (minimum {minimum})")
    for name in MEDIEVAL_NAMES:
        n = word_count(MEDIEVAL_DIR / f"{name}.txt")
        if n < MEDIEVAL_MIN_WORDS:
            out.append(f"medieval/{name}.txt: {n} słów (minimum {MEDIEVAL_MIN_WORDS})")
    return out


def load_extra(name: str, limit: int | None = None) -> list[str]:
    path = EXTRA_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - run: python scripts/fetch_data.py")
    ws = path.read_text(encoding="utf-8").split()
    return ws[:limit] if limit else ws
