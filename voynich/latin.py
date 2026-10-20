"""Latin text helpers: medieval spelling, syllables and scribal abbreviations.

Medieval scribes did not distinguish u/v or i/j, and abbreviated heavily:
a stroke over a vowel for a following m/n, special signs for -us, -rum,
per-, pro-, con-, -que and et. Proposals that the Voynich text is abbreviated
Latin can be tested by applying the same habits to real Latin.
"""

from __future__ import annotations

import re

VOWELS = set("aeiouy")
DIPHTHONGS = ("ae", "oe", "au")
# Consonant pairs that start a syllable together (muta cum liquida, digraphs).
ONSET_CLUSTERS = {"bl", "br", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "tr",
                  "ch", "ph", "th", "qu", "gu", "sc", "st", "sp"}


def normalize(words: list[str], merge_uv: bool = True) -> list[str]:
    """Medieval orthography: lowercase, letters only; j -> i and v -> u when `merge_uv`.

    Syllabify before merging: consonantal v/j are what tells syllables apart.
    """
    out = []
    for w in words:
        w = w.lower()
        if merge_uv:
            w = w.replace("j", "i").replace("v", "u")
        w = re.sub(r"[^a-z]", "", w.replace("æ", "ae").replace("œ", "oe"))
        if w:
            out.append(w)
    return out


def _nuclei(word: str) -> list[tuple[int, int]]:
    """Spans of vowel nuclei; 'qu'/'gu' + vowel treat the u as consonantal."""
    spans = []
    i = 0
    while i < len(word):
        c = word[i]
        if c in VOWELS and not (c == "u" and i > 0 and word[i - 1] in "qg" and i + 1 < len(word) and word[i + 1] in VOWELS):
            if word.startswith(DIPHTHONGS, i):
                spans.append((i, i + 2))
                i += 2
                continue
            spans.append((i, i + 1))
        i += 1
    return spans


def syllabify(word: str) -> list[str]:
    """Split a Latin word into written syllables (V-CV, VC-CV, V-CCV for clusters)."""
    nuclei = _nuclei(word)
    if len(nuclei) <= 1:
        return [word]
    cuts = []
    for (_, end), (start, _) in zip(nuclei, nuclei[1:]):
        cons = word[end:start]
        if len(cons) <= 1:
            cuts.append(end)
        elif cons[-2:] in ONSET_CLUSTERS:
            cuts.append(start - 2)
        else:
            cuts.append(start - 1)
    out, prev = [], 0
    for c in cuts:
        out.append(word[prev:c])
        prev = c
    out.append(word[prev:])
    return [s for s in out if s]


# Scribal abbreviation signs, written as single symbols.
_ABBREV_WORDS = {"et": "⁊", "est": "÷", "quod": "ꝙ", "per": "ꝑ", "pro": "ꝓ"}
_ABBREV_PREFIXES = (("con", "ꝯ"), ("com", "ꝯ"), ("per", "ꝑ"), ("pro", "ꝓ"), ("prae", "ꝑ̄"))
_ABBREV_SUFFIXES = (("rum", "ꝝ"), ("que", "ꝗ"), ("us", "ꝰ"), ("ur", "ᷣ"), ("um", "ū"), ("am", "ā"),
                    ("em", "ē"), ("is", "ꝭ"))
_NASAL = re.compile(r"([aeiou])[mn](?=[bcdfgpqst])")


def abbreviate(word: str) -> str:
    """Apply common late-medieval abbreviations deterministically."""
    if word in _ABBREV_WORDS:
        return _ABBREV_WORDS[word]
    head, tail = "", word
    for pre, sign in _ABBREV_PREFIXES:
        if tail.startswith(pre) and len(tail) > len(pre) + 1:
            head, tail = sign, tail[len(pre):]
            break
    end = ""
    for suf, sign in _ABBREV_SUFFIXES:
        if tail.endswith(suf) and len(tail) > len(suf):
            tail, end = tail[: -len(suf)], sign
            break
    tail = _NASAL.sub(lambda m: {"a": "ā", "e": "ē", "i": "ī", "o": "ō", "u": "ū"}[m.group(1)], tail)
    return head + tail + end
