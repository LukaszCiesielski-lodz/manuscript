"""Medieval list genres as comparison texts: a calendar of saints, a recipe book, a glossary.

If the manuscript is a record (one line = one entry of a register, a receptary, a calendar of
names) rather than running prose, its statistics should sit nearer such lists than nearer
prose: little dependency between entries, a nomenclature-heavy vocabulary with many names,
a frame repeated with changing content. Sources (public domain, small, committed in
data/lists/ as one entry per line; scripts/fetch_lists.py refreshes them):

- martyrology: Usuard, Martyrologium (9th c.), one entry per day of the year (la.wikisource, Migne);
- apicius: De re coquinaria, one entry per numbered recipe (la.wikisource);
- alphita: the medico-botanical glossary Alphita (ed. Mowat 1887, archive.org OCR); the two-column
  scan interleaves lines, so the glossary entries are noisy and gated by `quality`; the index of
  headwords (plant and drug names in Latin, French and English) is clean.
"""

from __future__ import annotations

import re
import statistics
from pathlib import Path
from typing import Sequence

from . import corpus

DIR = corpus.DATA / "lists"
WIKI_API = "https://la.wikisource.org/w/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&format=json&formatversion=2&titles="
MARTYROLOGY_PAGES = ["Martyrologium_1_(Usuardus_Sangermanensis)", "Martyrologium_2_(Usuardus_Sangermanensis)"]
APICIUS_PAGES = [f"De_re_coquinaria/Liber_{n}" for n in "I II III IV V VI VII VIII IX X".split()]
ALPHITA_URL = "https://archive.org/download/alphitaamedicob00mowagoog/alphitaamedicob00mowagoog_djvu.txt"

Entry = list[str]

_DAY = re.compile(r"^:?\s*(?:Kal|Non|Id|Prid|[IVX]+\.?\s+(?:Kal|Non|Id)|)[a-z.]*\.?.*\bDie\s+\d+\.?\s*$", re.I)
_MONTH = re.compile(r"^:?\s*MENSIS\s", re.I)
_COLUMN = re.compile(r"\b\d{3}\.\d{4}[A-Z]?\|")          # Migne column references, e.g. 123.0601A|
_WIKI = re.compile(r"\{\{[^{}]*\}\}|'''|''|<[^>]+>")
_LINK = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]")


def _clean_wiki(text: str) -> str:
    text = _LINK.sub(r"\1", text)
    text = _WIKI.sub(" ", text)
    text = _COLUMN.sub(" ", text)
    text = re.sub(r"\[[^\]]*\]", " ", text)                 # editorial brackets: [ Bouillart. add. ...]
    text = re.sub(r"\([^)]*\)", " ", text)                  # parenthetical references
    return text


def martyrology_entries(wikitext: str) -> list[Entry]:
    """One entry per calendar day; the prologues and month headings are dropped."""
    entries: list[list[str]] = []
    current: list[str] | None = None
    started = False                                        # prologues precede the first month heading
    for raw in _clean_wiki(wikitext).splitlines():
        line = raw.strip()
        if not line:
            continue
        if _MONTH.match(line):
            started = True
            current = None
            continue
        if started and _DAY.match(line):
            current = []
            entries.append(current)
            continue
        if current is None:
            continue
        current.extend(corpus.normalize_words(line))
    return [e for e in entries if len(e) >= 3]


_RECIPE = re.compile(r"^\s*(?:\d+\\?\.\s+|==\s*[IVXL]+\.?\s)")


def apicius_entries(wikitext: str) -> list[Entry]:
    """One entry per numbered recipe (a chapter heading without numbered recipes counts as one)."""
    entries: list[list[str]] = []
    current: list[str] | None = None
    heading_only = False
    for raw in _WIKI.sub(" ", _LINK.sub(r"\1", wikitext)).splitlines():
        line = raw.strip()
        if not line:
            continue
        if _RECIPE.match(line):
            if heading_only and current is not None:
                entries.pop()                              # a chapter title followed by its numbered recipes
            current = []
            entries.append(current)
            heading_only = line.startswith("==")
            line = re.sub(r"^\s*\d+\\?\.\s+|=+", " ", line)
        elif current is not None:
            heading_only = False
        if current is None:
            continue
        current.extend(corpus.normalize_words(line))
    return [e for e in entries if len(e) >= 3]


_INDEX_ENTRY = re.compile(r"^\|?\s*([A-Z][A-Za-z'’\- ]{1,40}?),\s*\d")
_HEADWORD = re.compile(r"^(?:\d{1,2}\s+)?§?\s*\[?([A-Z][a-z]{2,}(?:\s[a-z]{2,})?)(?:[,\"'’*^°!?]|\s+(?:i\.|est|idem|uel|vel|id est|respice|similis|herba|interpretatur))")
_APPARATUS = re.compile(r"^(?:\d+[.,]\s|[!¹²³]\s|\d+\s+(?:Diosc|App|Bart|E\. P\. N|Matth|Sim\.|See|Cf|Plin|Gerarde|Read|Isid))")
_PAGE_HEAD = re.compile(r"MEDICO-BOTANICAL GLOSSARY|^\d+\s*$|^[.,;:'\"\s]*$")


def _greekish(line: str) -> bool:
    letters = [c for c in line if c.isalpha()]
    return bool(letters) and sum(not c.isascii() for c in letters) / len(letters) > 0.12


def alphita_headwords(text: str) -> list[Entry]:
    """Names from the index of the Mowat edition (Latin, French and English plant and drug names)."""
    out: list[Entry] = []
    seen = set()
    at_index = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("INDEX"):
            at_index = True
            continue
        if not at_index:
            continue
        m = _INDEX_ENTRY.match(line)
        if m:
            words = corpus.normalize_words(m.group(1))
            if words and tuple(words) not in seen:
                seen.add(tuple(words))
                out.append(words)
    return out


def alphita_entries(text: str) -> list[Entry]:
    """Glossary entries from the OCR of the two-column edition: a new entry starts at a headword line.

    Lines of the critical apparatus (variant readings, footnotes, Greek) and page headings are
    dropped; a vertical bar marks the column break, the right half of such lines is appended after
    the page's left column. Expect noise: check with `quality` before use.
    """
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip().startswith("A MEDICO-BOTANICAL GLOSSARY.")), 0)
    end = next((i for i, l in enumerate(lines) if l.strip().startswith("INDEX")), len(lines))
    pages: list[list[str]] = [[]]
    right: list[str] = []
    for raw in lines[start + 1:end]:
        line = raw.strip()
        if "MEDICO-BOTANICAL GLOSSARY" in line:
            pages[-1].extend(right)
            right = []
            pages.append([])
            continue
        if not line or _PAGE_HEAD.match(line) or _APPARATUS.match(line) or _greekish(line):
            continue
        if "|" in line:
            left, _, rest = line.partition("|")
            if left.strip():
                pages[-1].append(left.strip())
            if rest.strip():
                right.append(rest.strip())
        else:
            pages[-1].append(line)
    pages[-1].extend(right)
    entries: list[list[str]] = []
    current: list[str] | None = None
    for page in pages:
        for line in page:
            if _HEADWORD.match(line):
                current = []
                entries.append(current)
            if current is not None:
                current.extend(corpus.normalize_words(line))
    return [e for e in entries if 2 <= len(e) <= 400]


def quality(entries: Sequence[Entry]) -> dict:
    """How list-like a parse is: number of entries, median and spread of words per entry."""
    if not entries:
        return {"entries": 0, "median_words": 0.0, "words": 0}
    n = [len(e) for e in entries]
    return {"entries": len(entries), "median_words": float(statistics.median(n)), "words": sum(n),
            "min_words": min(n), "max_words": max(n)}


def passes(q: dict, min_entries: int = 300, median: tuple[float, float] = (3, 60)) -> bool:
    return q["entries"] >= min_entries and median[0] <= q["median_words"] <= median[1]


def save(name: str, entries: Sequence[Entry]) -> Path:
    DIR.mkdir(parents=True, exist_ok=True)
    path = DIR / f"{name}.txt"
    path.write_text("\n".join(" ".join(e) for e in entries) + "\n", encoding="utf-8")
    return path


def load(name: str) -> list[Entry]:
    path = DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - run: python scripts/fetch_lists.py")
    return [l.split() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def available() -> list[str]:
    return sorted(p.stem for p in DIR.glob("*.txt")) if DIR.exists() else []


def as_lines(entries: Sequence[Entry]) -> list[list[tuple[str, ...]]]:
    """Entries as lines of glyph tuples, the shape the lab's measures take."""
    return [[tuple(w) for w in e] for e in entries]
