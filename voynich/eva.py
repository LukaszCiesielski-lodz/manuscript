"""Cleaning EVA transliteration text and splitting it into words and glyphs.

EVA (Extensible Voynich Alphabet) writes several Voynich glyphs with more than
one Latin letter: the "benched" gallows cth/ckh/cph/cfh, the benches ch/sh and
the minim runs ii/iii. Counting EVA letters instead of glyphs distorts entropy
and word-length figures, so `glyphs()` merges them back into single units.
"""

from __future__ import annotations

import re

# Longest first: greedy matching relies on this order.
MULTI_GLYPHS = ("cth", "ckh", "cph", "cfh", "iii", "ch", "sh", "ii")

_COMMENT = re.compile(r"<[^>]*>")
_ALTERNATIVE = re.compile(r"\[([^:\]]*)(?::[^\]]*)*\]")
_RARE = re.compile(r"@\d+;")
_NOT_EVA = re.compile(r"[^a-z?.]")


def clean(raw: str, uncertain_spaces: bool = True) -> str:
    """Reduce an IVTFF line to plain EVA with '.' as the only separator.

    - inline comments and markers (<%>, <$>, <!...>, <->) are dropped;
      <-> marks a gap for a drawing, so it becomes a word break
    - [a:b] alternative readings keep the first reading
    - {..} ligature groups lose their braces and apostrophes
    - @nnn; rare glyphs become '?' (unknown)
    - ',' (uncertain space) becomes a space when `uncertain_spaces` is true
    """
    text = raw.replace("<->", ".")
    text = _COMMENT.sub("", text)
    text = _ALTERNATIVE.sub(lambda m: m.group(1), text)
    text = _RARE.sub("?", text)
    text = text.replace(",", "." if uncertain_spaces else "")
    text = _NOT_EVA.sub("", text.lower())
    return re.sub(r"\.+", ".", text).strip(".")


def words(text: str, drop_uncertain: bool = True) -> list[str]:
    """Split cleaned EVA into words; optionally drop words containing '?'."""
    out = [w for w in text.split(".") if w]
    if drop_uncertain:
        out = [w for w in out if "?" not in w]
    return out


def glyphs(word: str) -> list[str]:
    """Tokenize one EVA word into Voynich glyphs (cth, ch, ii... count as one)."""
    out: list[str] = []
    i = 0
    while i < len(word):
        for g in MULTI_GLYPHS:
            if word.startswith(g, i):
                out.append(g)
                i += len(g)
                break
        else:
            out.append(word[i])
            i += 1
    return out
