"""Medieval symbolic notations as comparison texts: plainchant (Volpiano) and basse danse step tablature.

If the manuscript records something other than speech (a melody, a sequence of steps, a
procedure), its statistics should resemble such notations: a small alphabet, strict local
grammar, repeats and variants of short units, no sentence-level syntax. Chant comes from the
Cantus database (CantusCorpus, Volpiano strings); the basse danse letters (R b ss d r) from the
Brussels manuscript 9085 (c. 1470), the oldest "program" for performers in Europe.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

from . import corpus

DIR = corpus.REFERENCE_DIR / "notation"
CANTUS_URL = "https://github.com/bacor/cantuscorpus/releases/download/v0.2/cantuscorpus-v0.2.zip"
CHANT_FILE = DIR / "chant_volpiano.txt"         # one chant per line, Volpiano only (fetched)
DANCE_FILE = corpus.DATA / "notation" / "basse_danse.txt"   # committed: one dance per line, step letters

NOTE = re.compile(r"[a-s9]")                     # Volpiano pitches (lower case); liquescents in upper case folded
STEP = re.compile(r"R|b|ss|s|ddd|dd|d|rrr|rr|r|c|vs")


def volpiano_units(volpiano: str, level: str = "syllable") -> list[tuple[str, ...]]:
    """Notes grouped into units: '---' separates text words, '--' syllables, '-' neumes.
    level: 'word', 'syllable' or 'neume'. Clefs, bar lines and other marks are dropped."""
    v = volpiano.lower()
    v = re.sub(r"^1", "", v)                     # clef
    v = re.sub(r"[34567]", "", v)                # bar lines and section marks
    sep = {"word": "---", "syllable": "--", "neume": "-"}[level]
    units = []
    for chunk in v.split(sep):
        notes = NOTE.findall(chunk.replace("-", ""))
        if notes:
            units.append(tuple(notes))
    return units


def chant_lines(level: str = "syllable", min_notes: int = 20, limit: int | None = 4000) -> list[list[tuple[str, ...]]]:
    """One line per chant (melodies of at least `min_notes` notes), units as words."""
    if not CHANT_FILE.exists():
        raise FileNotFoundError(f"{CHANT_FILE} missing - run: python scripts/fetch_notation.py")
    out = []
    for raw in CHANT_FILE.read_text(encoding="utf-8").splitlines():
        if len(NOTE.findall(raw.lower())) < min_notes:
            continue
        units = volpiano_units(raw, level)
        if len(units) >= 3:
            out.append(units)
        if limit and len(out) >= limit:
            break
    return out


def dance_lines() -> list[list[tuple[str, ...]]]:
    """One line per dance; each step token is a word, its letters the glyphs (ss -> ('s','s'))."""
    if not DANCE_FILE.exists():
        return []
    out = []
    for raw in DANCE_FILE.read_text(encoding="utf-8").splitlines():
        raw = raw.split("#")[0].strip()
        if not raw:
            continue
        steps = [tuple(t) for t in STEP.findall(raw)]
        if steps:
            out.append(steps)
    return out


def code_lines(limit_lines: int = 6000) -> list[list[tuple[str, ...]]]:
    """A modern program as the literal contrast: the lab's own Python, identifiers and literals as words."""
    out = []
    for path in sorted(Path(__file__).resolve().parent.rglob("*.py")):
        for raw in path.read_text(encoding="utf-8").splitlines():
            toks = re.findall(r"[A-Za-z_][A-Za-z_0-9]*|\d+", raw.split("#")[0])
            if len(toks) >= 2:
                out.append([tuple(t.lower()) for t in toks])
            if len(out) >= limit_lines:
                return out
    return out


def extract_dances(text: str) -> list[str]:
    """Step sequences of at least eight tokens found in a transcription (tablature letters separated by spaces)."""
    tok = r"(?:R|b|ss|s|ddd|dd|d|rrr|rr|r|c|vs)"
    return [" ".join(m.split()) for m in re.findall(rf"((?:{tok}\s+){{7,}}{tok})", text)]
