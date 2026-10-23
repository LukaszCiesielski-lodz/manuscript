"""Is the text shaped like speech? Sukhotin's vowel finder and consonant-vowel word patterns.

Sukhotin (1962) separates vowels from consonants in an unknown alphabet from one observation:
vowels sit next to consonants more often than next to each other. Guy (1991) applied it to the
manuscript. Applied to the manuscript and to every reference language alike, it gives each text
a vowel set and turns every word into a consonant-vowel pattern (CVCV, CVCC...). Comparing the
pattern distributions tells whether the manuscript's words are built like the words of any
language, like an abjad (vowels unwritten), or like nothing that is spoken.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Sequence

import numpy as np

Word = Sequence[str]


def sukhotin(words: Sequence[Word], weights: Sequence[float] | None = None) -> tuple[set[str], list[str]]:
    """(vowel set, symbols in the order they were declared vowels)."""
    symbols = sorted({s for w in words for s in w})
    sid = {s: i for i, s in enumerate(symbols)}
    n = len(symbols)
    F = np.zeros((n, n))
    for k, w in enumerate(words):
        wt = 1.0 if weights is None else weights[k]
        for a, b in zip(w, w[1:]):
            if a != b:
                F[sid[a], sid[b]] += wt
                F[sid[b], sid[a]] += wt
    sums = F.sum(1)
    vowel = np.zeros(n, dtype=bool)
    order = []
    while True:
        cand = np.where(~vowel, sums, -np.inf)
        i = int(cand.argmax())
        if cand[i] <= 0:
            break
        vowel[i] = True
        order.append(symbols[i])
        sums -= 2 * F[i]
    return {symbols[i] for i in range(n) if vowel[i]}, order


def pattern(word: Word, vowels: set[str]) -> str:
    return "".join("V" if s in vowels else "C" for s in word)


def profile(words: Sequence[Word], vowels: set[str], weights: Sequence[float] | None = None) -> dict:
    """Pattern distribution and summary numbers of a text under a vowel set."""
    pats: Counter = Counter()
    alt = pairs = v_count = total = 0.0
    clusters = []
    for k, w in enumerate(words):
        wt = 1.0 if weights is None else weights[k]
        p = pattern(w, vowels)
        pats[p[:10]] += wt
        total += wt * len(p)
        v_count += wt * p.count("V")
        for a, b in zip(p, p[1:]):
            pairs += wt
            alt += wt * (a != b)
        run = max((len(r) for r in p.split("V")), default=0)
        clusters.append((run, wt))
    z = sum(pats.values()) or 1.0
    dist = {p: c / z for p, c in pats.items()}
    cl = sum(r * w for r, w in clusters) / (sum(w for _, w in clusters) or 1.0)
    return {"patterns": dist, "vowel_share": v_count / (total or 1.0), "alternation": alt / (pairs or 1.0),
            "mean_longest_cluster": cl, "no_vowel_share": sum(c for p, c in dist.items() if "V" not in p)}


def js_divergence(p: dict, q: dict) -> float:
    """Jensen-Shannon divergence (bits) between two pattern distributions."""
    keys = set(p) | set(q)
    out = 0.0
    for k in keys:
        a, b = p.get(k, 0.0), q.get(k, 0.0)
        m = (a + b) / 2
        if a > 0:
            out += 0.5 * a * math.log2(a / m)
        if b > 0:
            out += 0.5 * b * math.log2(b / m)
    return out


def shuffle_within_words(words: Sequence[Word], seed: int) -> list[tuple[str, ...]]:
    """Every word's symbols in random order: the word shapes die, the symbol counts stay."""
    r = np.random.default_rng(seed)
    out = []
    for w in words:
        w = list(w)
        r.shuffle(w)
        out.append(tuple(w))
    return out
