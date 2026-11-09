"""Polybius on word lengths: two consecutive word lengths as the row and column of a letter grid.

The Greek Polybius square writes every letter as two digits (row, column). If the scribe hid a
text in the lengths of his words, a pair of lengths would be one letter. The solver assigns a
letter to every pair value (up to 9 x 9 cells, several cells may share a letter) by annealed
hill climbing on the full likelihood: letter trigrams of the language plus the emission cost
-sum n_u log n_u (without it the climber merges many cells into a few frequent letters, the
failure already met in voynich.lab.nomen2).
"""

from __future__ import annotations

import math
import random
import unicodedata
from collections import Counter
from typing import Sequence

import numpy as np

from .. import corpus


def letters(lang: str) -> str:
    """The reference text as one string of letters (Hebrew as is, other languages folded to a-z)."""
    t = "".join(c for w in corpus.load_reference(lang) for c in w.lower() if c.isalpha())
    if lang != "Hebrew":
        t = "".join(c for c in unicodedata.normalize("NFD", t.replace("ß", "ss")) if "a" <= c <= "z")
    return t


class TrigramLM:
    """Letter trigram model (add-0.01), log2 probabilities in an n x n x n array."""

    def __init__(self, text: str):
        self.alphabet = sorted(set(text))
        self.index = {c: i for i, c in enumerate(self.alphabet)}
        n = self.n = len(self.alphabet)
        x = np.array([self.index[c] for c in text])
        c3 = np.zeros((n, n, n))
        np.add.at(c3, (x[:-2], x[1:-1], x[2:]), 1)
        self.lp = np.log2((c3 + 0.01) / (c3.sum(2)[:, :, None] + 0.01 * n))

    def bits(self, text: str) -> float:
        x = np.array([self.index[c] for c in text if c in self.index])
        return float(-self.lp[x[:-2], x[1:-1], x[2:]].mean())


def pairs(seq: Sequence[int], phase: int = 0, cap: int = 9) -> list[int]:
    """Consecutive values (from `phase`) as cell numbers 0..cap*cap-1; values above `cap` count as `cap`."""
    s = [min(cap, max(1, v)) for v in seq][phase:]
    return [(s[i] - 1) * cap + (s[i + 1] - 1) for i in range(0, len(s) - 1, 2)]


def solve(sym: Sequence[int], lm: TrigramLM, iters: int = 20000, restarts: int = 6, seed: int = 0,
          t0: float = 1000.0) -> tuple[np.ndarray, float]:
    """Cell -> letter key by annealing; returns the key and the trigram bits per letter of the decoded text."""
    sym = np.asarray(sym)
    S = int(sym.max()) + 1
    tri = Counter(zip(sym[:-2], sym[1:-1], sym[2:]))
    T = np.array(list(tri.keys()))
    W = np.array(list(tri.values()), float)
    freq = np.bincount(sym, minlength=S).astype(float)
    used = [int(u) for u in np.nonzero(freq)[0]]
    xl = lambda x: np.where(x > 0, x * np.log2(np.maximum(x, 1e-12)), 0.0)

    def score(key):
        load = np.bincount(key[used], weights=freq[used], minlength=lm.n)
        return (W * lm.lp[key[T[:, 0]], key[T[:, 1]], key[T[:, 2]]]).sum() - xl(load).sum()

    rng = random.Random(seed)
    best = None
    for _ in range(restarts):
        key = np.array([rng.randrange(lm.n) for _ in range(S)])
        sc, temp = score(key), t0
        for _ in range(iters):
            s = rng.choice(used)
            old = key[s]
            key[s] = rng.randrange(lm.n)
            new = score(key)
            if new >= sc or rng.random() < math.exp((new - sc) / max(temp, 1e-6)):
                sc = new
            else:
                key[s] = old
            temp *= 0.002 ** (1 / iters)       # t0 down to 0.2% of t0 whatever the length
        if best is None or sc > best[0]:
            best = (sc, key.copy())
    key = best[1]
    return key, float(-(W * lm.lp[key[T[:, 0]], key[T[:, 1]], key[T[:, 2]]]).sum() / W.sum())


def encode(text: str, seed: int) -> tuple[list[int], list[str]]:
    """Positive control: a random 5 x 5 grid of the 25 most frequent letters, coordinates + 1 (look like word lengths 2-6).
    Returns the length sequence and the letter behind every pair."""
    r = random.Random(seed)
    grid = [c for c, _ in Counter(text).most_common(25)]
    r.shuffle(grid)
    pos = {c: i for i, c in enumerate(grid)}
    out, truth = [], []
    for c in text:
        if c in pos:
            out += [pos[c] // 5 + 2, pos[c] % 5 + 2]
            truth.append(c)
    return out, truth


def decode(key: np.ndarray, sym: Sequence[int], lm: TrigramLM) -> str:
    return "".join(lm.alphabet[key[s]] for s in sym)
