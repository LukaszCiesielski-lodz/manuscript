"""A self-citation text generator after Timm & Schinner (2020).

Torsten Timm and Andreas Schinner, "A possible generating algorithm of the
Voynich manuscript", Cryptologia 44(1), 2020, propose that the scribe produced
each new word by copying a word written shortly before, often from the same
place in a line above, and changing it slightly: swapping a glyph for a
similar-looking one, adding or dropping a prefix, or adding/removing an 'e'.

This is an independent, simplified re-implementation on glyph sequences. It
is a hypothesis to test against the real text, not a reconstruction of their
code: the rule set and probabilities below are this project's choices.
"""

from __future__ import annotations

import random
from typing import Sequence

Word = list[str]

# Glyphs that look alike in the manuscript and swap freely under the hypothesis.
SIMILAR = [
    ("o", "a", "y"),
    ("ch", "sh"),
    ("k", "t"),
    ("p", "f"),
    ("cth", "ckh"),
    ("cph", "cfh"),
    ("l", "r"),
    ("d", "s"),
    ("i", "ii", "iii"),
]
_SWAP = {g: [h for h in grp if h != g] for grp in SIMILAR for g in grp}
PREFIXES = (("q", "o"), ("o",), ("y",), ("d",), ("s",), ("ch",))
_E_HOSTS = {"ch", "sh", "k", "t", "cth", "ckh", "e"}


def _swap(w: Word, rng: random.Random) -> Word:
    idx = [i for i, g in enumerate(w) if g in _SWAP]
    if not idx:
        return w
    i = rng.choice(idx)
    return w[:i] + [rng.choice(_SWAP[w[i]])] + w[i + 1:]


def _prefix(w: Word, rng: random.Random) -> Word:
    """Drop the word's prefix if it has one, else add a random prefix."""
    for p in sorted(PREFIXES, key=len, reverse=True):
        if tuple(w[:len(p)]) == p and len(w) > len(p):
            return w[len(p):]
    return list(rng.choice(PREFIXES)) + w


def _e(w: Word, rng: random.Random) -> Word:
    """Insert an 'e' after a bench/gallows glyph, or remove one (equally likely)."""
    es = [i for i, g in enumerate(w) if g == "e"]
    if es and rng.random() < 0.5:
        i = rng.choice(es)
        return w[:i] + w[i + 1:]
    hosts = [i for i, g in enumerate(w) if g in _E_HOSTS and i + 1 < len(w)]
    if not hosts:
        return w
    i = rng.choice(hosts)
    return w[:i + 1] + ["e"] + w[i + 1:]


def _splice(w: Word, other: Word, rng: random.Random) -> Word:
    if len(w) < 2 or len(other) < 2:
        return w
    return w[:rng.randint(1, len(w) - 1)] + other[rng.randint(1, len(other) - 1):]


def generate(
    seed_lines: Sequence[Sequence[Word]],
    n_words: int,
    line_lengths: Sequence[int],
    p_copy: float = 0.22,
    p_same_column: float = 0.55,
    p_far: float = 0.05,
    window: int = 8,
    max_len: int = 8,
    seed: int = 1,
) -> list[list[Word]]:
    """Generate lines of glyph-words by repeated copy-and-modify.

    p_copy        probability that a source word is copied unchanged
    p_same_column probability of taking the source from the same position in
                  one of the `window` previous lines (else any word in them)
    p_far         probability of taking the source from anywhere earlier
    max_len       longer results are discarded (the scribe's words stay short)
    line_lengths  empirical words-per-line values to sample from
    """
    rng = random.Random(seed)
    lines: list[list[Word]] = [list(map(list, l)) for l in seed_lines]
    history = [w for l in lines for w in l]
    mutations = (_swap, _swap, _swap, _prefix, _e)
    while len(history) < n_words:
        recent = lines[-window:]
        pool = [w for l in recent for w in l]
        line: list[Word] = []
        for col in range(rng.choice(line_lengths)):
            above = [l[col] for l in recent if col < len(l)]
            r = rng.random()
            if r < p_far:
                src = rng.choice(history)
            elif above and r < p_far + p_same_column:
                src = rng.choice(above)
            else:
                src = rng.choice(pool)
            w = list(src)
            if rng.random() >= p_copy:
                for _ in range(1 + (rng.random() < 0.35)):
                    if rng.random() < 0.05:
                        w = _splice(w, rng.choice(pool), rng)
                    else:
                        w = rng.choice(mutations)(w, rng)
            if 1 <= len(w) <= max_len:
                line.append(w)
        if line:
            lines.append(line)
            history.extend(line)
    return lines
