"""The other scholarly transliterations of the manuscript (voynich.nu, IVTFF), beside Zandbergen-Landini.

Two EVA transliterations agree fully on only about 29% of lines (Chelednik, voynich-transcription-
mismatch), so any statistical signature should be checked on every transliteration before it is
believed. Files go to data/reference/transliterations/ (not committed; voynich.nu asks not to
re-host them). Non-EVA alphabets (Currier, FSG, v101) are tokenized as single characters, case kept.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import corpus, eva, ivtff

DIR = corpus.REFERENCE_DIR / "transliterations"
CACHE = "https://raw.githubusercontent.com/noah-chelednik/voynich-data/main/data_sources/cache/"
# id -> (name, alphabet family, download URLs in order of preference)
SOURCES = {
    "ZL": ("Zandbergen-Landini", "eva", []),
    "IT": ("Takahashi (interlinear)", "eva", ["https://www.voynich.nu/data/IT2a-n.txt", CACHE + "IT_ivtff_1a.txt"]),
    "VT": ("Takahashi (voynichese.com)", "eva", ["https://www.voynich.nu/data/VT0e-n.txt"]),
    "RF": ("Reference (GC+ZL)", "eva", ["https://www.voynich.nu/data/RF1b-e.txt"]),
    "CD": ("Currier-D'Imperio", "currier", ["https://www.voynich.nu/data/CD2a-n.txt", CACHE + "CD2a-n.txt"]),
    "FG": ("FSG (First Study Group)", "fsg", ["https://www.voynich.nu/data/FG2a-n.txt", CACHE + "FG2a-n.txt"]),
    "GC": ("GC v101", "v101", ["https://www.voynich.nu/data/GC2a-n.txt", CACHE + "GC2a-n.txt"]),
}

_COMMENT = re.compile(r"<[^>]*>")
_ALTERNATIVE = re.compile(r"\[([^:\]]*)(?::[^\]]*)*\]")
_RARE = re.compile(r"@\d+;")


def clean_generic(raw: str) -> str:
    """IVTFF line of any alphabet to words separated by '.', one character per glyph, case kept."""
    text = raw.replace("<->", ".")
    text = _COMMENT.sub("", text)
    text = _ALTERNATIVE.sub(lambda m: m.group(1), text)
    text = _RARE.sub("?", text)
    text = text.replace(",", ".").replace("{", "").replace("}", "").replace("'", "")
    text = re.sub(r"[\s]+", "", text)
    return re.sub(r"\.+", ".", text).strip(".")


def path(tid: str) -> Path:
    return corpus.ZL_FILE if tid == "ZL" else DIR / f"{tid}.txt"


def available() -> list[str]:
    return [t for t in SOURCES if path(t).exists()]


def load_lines(tid: str, paragraphs_only: bool = True) -> list[list[tuple[str, ...]]]:
    """Lines as lists of words; a word is a tuple of glyph tokens. Words with uncertain glyphs dropped."""
    name, family, _ = SOURCES[tid]
    out = []
    for page in ivtff.parse(path(tid)):
        for locus in page.loci:
            if paragraphs_only and not locus.is_paragraph:
                continue
            if family == "eva":
                ws = [tuple(eva.glyphs(w)) for w in eva.words(eva.clean(locus.raw))]
            else:
                ws = [tuple(w) for w in clean_generic(locus.raw).split(".") if w and "?" not in w]
            if ws:
                out.append(ws)
    return out
