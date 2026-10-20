"""Testing syllabic readings of the Voynich text.

Two different claims hide under "it is a syllabic cipher":

1. Each Voynich *word* is one syllable (a syllabary, as in Chinese or
   Vietnamese writing). Then Voynich words must behave like syllables: few
   types, short, with a repetitive inventory. `syllable_stream` turns a Latin
   text into such a stream for comparison.

2. Each Voynich word is one plaintext word, spelled syllable by syllable with
   a code group per syllable (or per letter: a verbose cipher). Any such
   deterministic word-for-word encoding leaves word-level statistics
   untouched: vocabulary size, Zipf curve, how often a word repeats right
   after itself. Those invariants test the whole family at once, whatever the
   codebook. `SyllableCipher` builds one concrete codebook to show what the
   encoding does to glyph-level statistics.
"""

from __future__ import annotations

from collections import Counter
from typing import Sequence

from . import latin

Word = Sequence[str]

# Glyphs that behave like vowels in Voynich words (fill the middle slot).
VOYNICH_VOWELS = {"o", "a", "e", "y", "i", "ii", "iii"}


def syllable_stream(raw_words: Sequence[str]) -> list[str]:
    """Latin words (v/j kept) -> stream of syllables in medieval spelling."""
    out = []
    for w in raw_words:
        for s in latin.syllabify(w):
            out.append(s.replace("j", "i").replace("v", "u"))
    return out


def split_onc(units: Sequence[str], is_vowel) -> tuple[tuple, tuple, tuple]:
    """Split a syllable into onset, nucleus, coda (each a tuple of units)."""
    i = 0
    while i < len(units) and not is_vowel(units[i], i, units):
        i += 1
    j = i
    while j < len(units) and is_vowel(units[j], j, units):
        j += 1
    return tuple(units[:i]), tuple(units[i:j]), tuple(units[j:])


def _latin_vowel(c, i, units) -> bool:
    if c not in latin.VOWELS:
        return False
    # u after q/g before a vowel is a consonant: qua-, gui-
    return not (c == "u" and i > 0 and units[i - 1] in "qg" and i + 1 < len(units) and units[i + 1] in latin.VOWELS)


def _voynich_vowel(g, i, units) -> bool:
    return g in VOYNICH_VOWELS


class SyllableCipher:
    """Encode Latin syllables as Voynich glyph groups, slot by slot.

    Onsets, nuclei and codas of Latin syllables are ranked by frequency and
    matched to Voynich onsets, nuclei and codas of the same rank (Voynich
    words split by the same rule, with o/a/e/y/i as vowels). The most
    frequent Latin onset gets the most frequent Voynich onset, and so on;
    rare parts beyond the Voynich inventory reuse it cyclically. This is one
    reasonable codebook, built to give the hypothesis its best chance of
    looking like the manuscript; it is not a claim about the real one.
    """

    def __init__(self, latin_raw_words: Sequence[str], voynich_glyph_words: Sequence[Word]):
        lat = [split_onc(list(s), _latin_vowel) for s in syllable_stream(latin_raw_words)]
        voy = [split_onc(list(w), _voynich_vowel) for w in voynich_glyph_words]
        self.maps = []
        for part in range(3):
            l_rank = [p for p, _ in Counter(x[part] for x in lat).most_common()]
            v_rank = [p for p, _ in Counter(x[part] for x in voy).most_common()]
            self.maps.append({p: v_rank[k % len(v_rank)] for k, p in enumerate(l_rank)})

    def encode_word(self, raw_word: str) -> list[str]:
        out: list[str] = []
        for s in syllable_stream([raw_word]):
            parts = split_onc(list(s), _latin_vowel)
            for m, p in zip(self.maps, parts):
                out.extend(m.get(p, p))
        return out

    def encode(self, raw_words: Sequence[str]) -> list[list[str]]:
        return [self.encode_word(w) for w in raw_words]


def repeat_profile(words: Sequence[Word]) -> dict[str, float]:
    """Word-level statistics that no deterministic word-for-word cipher can change."""
    ws = [tuple(w) for w in words]
    pairs = list(zip(ws, ws[1:]))
    repeats = Counter(a for a, b in pairs if a == b)
    last: dict[tuple, int] = {}
    within10 = 0
    for i, w in enumerate(ws):
        if w in last and i - last[w] <= 10:
            within10 += 1
        last[w] = i
    counts = Counter(ws)
    return {
        "types": len(counts),
        "hapax_ratio": sum(1 for c in counts.values() if c == 1) / len(counts),
        "adjacent_repeat": sum(repeats.values()) / len(pairs),
        "repeat_types": len(repeats),
        "repeat_within_10": within10 / len(ws),
    }
