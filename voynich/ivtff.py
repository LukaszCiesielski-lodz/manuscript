"""Parser for IVTFF (Intermediate Voynich Transliteration File Format).

The format is documented by René Zandbergen at https://www.voynich.nu/transcr.html.
A file is a sequence of page headers and locus lines:

    <f1r>      <! $Q=A $P=A $I=T $L=A $H=1>
    <f1r.1,@P0>       <%>fachys.ykal.ar.ataiin.shol.shory

Page variables used here:
    $I  illustration type  (H herbal, A astronomical, C cosmological, Z zodiac,
                            B biological, P pharmaceutical, S stars/recipes, T text)
    $L  Currier language   (A or B)
    $H  scribe hand        (1-5, after Lisa Fagin Davis)
    $Q  quire
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

ILLUSTRATION = {
    "H": "herbal",
    "A": "astronomical",
    "C": "cosmological",
    "Z": "zodiac",
    "B": "biological",
    "P": "pharmaceutical",
    "S": "stars",
    "T": "text",
}

_PAGE_RE = re.compile(r"^<(f\d+[rv]\d*)>\s*(?:<!(.*)>)?\s*$")
_LOCUS_RE = re.compile(r"^<(f\d+[rv]\d*)\.(\d+[a-z]?),(.)(..)>\s*(.*)$")
_VAR_RE = re.compile(r"\$([A-Z])=(\S+)")


@dataclass
class Locus:
    """One line, label or ring of text on a page."""

    page: str
    number: str
    position: str  # @ new unit, + continues, * new paragraph, = last line, & ...
    kind: str  # P paragraph, L label, C circle, R radial; second char is subtype
    raw: str

    @property
    def is_paragraph(self) -> bool:
        return self.kind.startswith("P")

    @property
    def is_label(self) -> bool:
        return self.kind.startswith("L")


@dataclass
class Page:
    folio: str
    variables: dict[str, str] = field(default_factory=dict)
    loci: list[Locus] = field(default_factory=list)

    @property
    def section(self) -> str:
        return ILLUSTRATION.get(self.variables.get("I", ""), "unknown")

    @property
    def language(self) -> str:
        return self.variables.get("L", "?")

    @property
    def hand(self) -> str:
        return self.variables.get("H", "?")

    @property
    def quire(self) -> str:
        return self.variables.get("Q", "?")


def parse(path: str | Path) -> list[Page]:
    pages: list[Page] = []
    by_folio: dict[str, Page] = {}
    with open(path, encoding="latin-1") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            m = _PAGE_RE.match(line)
            if m:
                page = Page(m.group(1), dict(_VAR_RE.findall(m.group(2) or "")))
                pages.append(page)
                by_folio[page.folio] = page
                continue
            m = _LOCUS_RE.match(line)
            if m:
                folio = m.group(1)
                page = by_folio.get(folio)
                if page is None:
                    page = Page(folio)
                    pages.append(page)
                    by_folio[folio] = page
                page.loci.append(Locus(folio, m.group(2), m.group(3), m.group(4), m.group(5)))
    return pages
