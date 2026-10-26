"""Homophonic substitution attack by parallel hill climbing with a character n-gram language model.

The classical solver (AZdecrypt, Van Eycke; Nuhn & Ney 2013): a key assigns every glyph a letter
(several glyphs may share a letter: homophones), the decoded text is scored by a character
4-gram model of the candidate language, and thousands of climbers on the GPU mutate their keys,
keeping improvements. The score is computed from the counts of distinct glyph 4-grams, so a step
costs one gather per climber per distinct 4-gram. Keys are fitted on odd lines and judged on even
lines (held-out bits per symbol), against the same attack on meaningless text with the
manuscript's statistics and on a real text of the language enciphered homophonically.
"""

from __future__ import annotations

import math
import random
import time
from collections import Counter
from dataclasses import dataclass
from typing import Sequence

import numpy as np

Word = tuple[str, ...]
SPACE = " "


class Backend:
    def __init__(self, prefer_gpu: bool = True):
        self.torch, self.device = None, "cpu"
        if prefer_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    self.torch, self.device = torch, "cuda"
            except ImportError:
                pass

    @property
    def name(self) -> str:
        return "cuda" if self.torch else "numpy"

    def array(self, a, dtype=None):
        a = np.asarray(a)
        if self.torch:
            return self.torch.as_tensor(a, device=self.device)
        return a.astype(dtype) if dtype else a

    def to_np(self, a):
        return a.detach().cpu().numpy() if self.torch else np.asarray(a)


# ---------- character n-gram model

@dataclass
class NgramModel:
    symbols: list[str]          # index -> symbol; SPACE included
    order: int
    table: np.ndarray           # log P(c | history) of shape [A]*order

    @property
    def space(self) -> int:
        return self.symbols.index(SPACE)

    @classmethod
    def fit(cls, words: Sequence[str], order: int = 4, beta: float = 1.0) -> "NgramModel":
        """Interpolated add-beta model: P_n(c|h) = (C(hc) + beta P_{n-1}(c|h')) / (C(h) + beta)."""
        symbols = sorted({c for w in words for c in w}) + [SPACE]
        sid = {c: i for i, c in enumerate(symbols)}
        A = len(symbols)
        seq = np.array([sid[c] for w in words for c in w + SPACE], dtype=np.int64)
        prob = (np.bincount(seq, minlength=A) + 1.0) / (len(seq) + A)           # unigram
        for n in range(2, order + 1):
            counts = np.zeros((A,) * n)
            idx = tuple(seq[i:len(seq) - n + 1 + i] for i in range(n))
            np.add.at(counts, idx, 1.0)
            ctx = counts.sum(-1, keepdims=True)
            prob = (counts + beta * prob[None]) / (ctx + beta)                      # prob[None]: history shortened
        return cls(symbols, order, np.log(prob))

    def bits(self, words: Sequence[str]) -> float:
        """Bits per symbol of a text (unknown symbols skipped)."""
        sid = {c: i for i, c in enumerate(self.symbols)}
        seq = [sid[c] for w in words for c in w + SPACE if c in sid]
        n = self.order
        total = sum(self.table[tuple(seq[i - n + 1 + k] for k in range(n))] for i in range(n - 1, len(seq)))
        return -total / max(1, len(seq) - n + 1) / math.log(2)


# ---------- the text as counts of glyph n-grams

@dataclass
class GlyphText:
    glyphs: list[str]           # index -> glyph; last index is the word gap
    grams: np.ndarray           # [U, order] glyph ids of distinct n-grams
    counts: np.ndarray          # [U]

    @property
    def gap(self) -> int:
        return len(self.glyphs) - 1

    @classmethod
    def build(cls, lines: Sequence[Sequence[Word]], glyphs: list[str], order: int) -> "GlyphText":
        gid = {g: i for i, g in enumerate(glyphs)}
        gap = len(glyphs)
        c: Counter = Counter()
        for l in lines:
            seq = [gap]
            for w in l:
                seq += [gid[g] for g in w if g in gid] + [gap]
            for i in range(len(seq) - order + 1):
                c[tuple(seq[i:i + order])] += 1
        grams = np.array(list(c.keys()), dtype=np.int64)
        return cls(list(glyphs) + [SPACE], grams, np.array(list(c.values()), dtype=np.float64))


def glyph_inventory(lines: Sequence[Sequence[Word]], min_count: int = 20) -> list[str]:
    c = Counter(g for l in lines for w in l for g in w)
    return [g for g, n in c.most_common() if n >= min_count]


# ---------- the climb

@dataclass
class Climb:
    population: int = 4096
    steps: int = 2000
    temperature: float = 0.02   # annealed to 0: simulated annealing in bits per symbol
    seed: int = 1


def _score(keys, text_grams, counts, table, xp, total):
    """Mean log-probability per symbol of the decoded n-grams for every key. keys [K, G+1] (gap fixed)."""
    dec = [keys[:, text_grams[:, i]] for i in range(text_grams.shape[1])]   # each [K, U]
    lp = table[tuple(dec)]                                                   # [K, U]
    return (lp * counts[None]).sum(1) / total


def climb(text: GlyphText, lm: NgramModel, s: Climb, xp: Backend, held_out: GlyphText | None = None,
          log=None) -> dict:
    """Best key found: glyph -> letter, with fitted and held-out bits per symbol."""
    r = np.random.default_rng(s.seed)
    G, A = text.gap, len(lm.symbols)
    letters = [i for i in range(A) if i != lm.space]
    keys = r.choice(letters, size=(s.population, G + 1))
    keys[:, G] = lm.space
    k = xp.array(keys)
    grams, counts = xp.array(text.grams), xp.array(text.counts, np.float64)
    table = xp.array(lm.table)
    total = float(text.counts.sum())
    ln2 = math.log(2)
    cur = _score(k, grams, counts, table, xp, total)
    best_val, best_key = float(xp.to_np(cur).max()), keys[int(xp.to_np(cur).argmax())].copy()
    t0 = time.time()
    ar = xp.array(np.arange(s.population))
    for step in range(s.steps):
        temp = s.temperature * (1 - step / s.steps) * ln2
        which = xp.array(r.integers(0, G, size=s.population))
        new_letter = xp.array(r.choice(letters, size=s.population))
        old = k[ar, which]
        k[ar, which] = new_letter
        sc = _score(k, grams, counts, table, xp, total)
        delta = sc - cur
        if temp > 0:
            noise = xp.array(np.log(r.random(s.population) + 1e-12) * temp)
            accept = delta > noise
        else:
            accept = delta > 0
        where = xp.torch.where if xp.torch else np.where
        k[ar, which] = where(accept, new_letter, old)
        cur = where(accept, sc, cur)
        if step % 50 == 0 or step == s.steps - 1:
            cur_np = xp.to_np(cur)
            i = int(cur_np.argmax())
            if cur_np[i] > best_val:
                best_val, best_key = float(cur_np[i]), xp.to_np(k[i]).copy()
            if log and step % max(1, s.steps // 10) == 0:
                log(f"    krok {step}: najlepiej {-best_val / ln2:.3f} bit/znak ({time.time() - t0:.0f} s)")
    key = {text.glyphs[g]: lm.symbols[int(best_key[g])] for g in range(G)}
    out = {"bits": -best_val / ln2, "key": key, "seconds": time.time() - t0}
    if held_out is not None:
        kb = xp.array(best_key[None])
        hv = _score(kb, xp.array(held_out.grams), xp.array(held_out.counts, np.float64), table, xp,
                    float(held_out.counts.sum()))
        out["held_out_bits"] = -float(xp.to_np(hv)[0]) / ln2
    return out


# ---------- controls

def encipher_homophonic(words: Sequence[str], n_glyphs: int, seed: int, line_len: int = 9) -> tuple[list[list[Word]], dict]:
    """Real text under a homophonic key: frequent letters get several glyphs, n_glyphs in all.
    Returns lines of pseudo-glyph words and the true key glyph -> letter."""
    r = random.Random(seed)
    freq = Counter(c for w in words for c in w)
    letters = [c for c, _ in freq.most_common()]
    if len(letters) > n_glyphs:                       # a small alphabet of glyphs cannot carry every letter
        letters = letters[:n_glyphs]
    total = sum(freq[c] for c in letters)
    homophones = {c: max(1, round(n_glyphs * freq[c] / total)) for c in letters}
    while sum(homophones.values()) > n_glyphs:
        c = max(homophones, key=lambda x: homophones[x])
        homophones[c] -= 1
    while sum(homophones.values()) < n_glyphs:
        c = max(letters, key=lambda x: freq[x] / homophones[x])
        homophones[c] += 1
    names = [f"g{i:02d}" for i in range(n_glyphs)]
    r.shuffle(names)
    key, pool, i = {}, {}, 0
    for c in letters:
        pool[c] = names[i:i + homophones[c]]
        for g in pool[c]:
            key[g] = c
        i += homophones[c]
    ws = [tuple(r.choice(pool[c]) for c in w) for w in words if all(c in pool for c in w)]
    return [ws[i:i + line_len] for i in range(0, len(ws), line_len)], key


def key_accuracy(found: dict, true: dict, lines: Sequence[Sequence[Word]]) -> float:
    """Share of glyph occurrences whose letter the attack got right."""
    c = Counter(g for l in lines for w in l for g in w)
    tot = sum(c[g] for g in true if g in found)
    return sum(c[g] for g in true if g in found and found[g] == true[g]) / tot if tot else 0.0


def split_odd_even(lines: Sequence[Sequence[Word]]) -> tuple[list, list]:
    return [l for i, l in enumerate(lines) if i % 2 == 0], [l for i, l in enumerate(lines) if i % 2 == 1]


# ---------- a key per word length (the symbol "g#c" is glyph g inside a word of length class c)

CLASSES = 9


def length_class(n: int, classes: int = CLASSES) -> int:
    """Word lengths 1..classes-1 are their own class; longer words share the last one."""
    return min(max(1, n), classes)


def by_length(lines: Sequence[Sequence[Word]], classes: int = CLASSES) -> list[list[Word]]:
    """Glyphs renamed by the length class of their word, so that one homophonic key over the renamed symbols
    is a separate key for every word length."""
    return [[tuple(f"{g}#{length_class(len(w), classes)}" for g in w) for w in l] for l in lines]


def encipher_by_length(words: Sequence[str], n_glyphs: int, seed: int, classes: int = CLASSES, line_len: int = 9) -> tuple[list[list[Word]], dict]:
    """Real text where every word-length class has a homophonic key of its own; lines of pseudo-glyph words whose
    symbols already carry the class (g#c), and the true key symbol -> letter."""
    by_class: dict[int, list[str]] = {}
    for w in words:
        by_class.setdefault(length_class(len(w), classes), []).append(w)
    enc_words: dict[int, list[Word]] = {}
    truth: dict = {}
    for c, ws in by_class.items():
        lines, key = encipher_homophonic(ws, n_glyphs, seed + 97 * c, line_len=10 ** 9)
        enc_words[c] = [tuple(f"{g}#{c}" for g in w) for l in lines for w in l]
        truth.update({f"{g}#{c}": letter for g, letter in key.items()})
    # restore the original word order (the classes were enciphered separately)
    pos = {c: 0 for c in by_class}
    out: list[Word] = []
    for w in words:
        c = length_class(len(w), classes)
        if pos[c] < len(enc_words[c]):
            cand = enc_words[c][pos[c]]
            if len(cand) == len(w):
                out.append(cand)
                pos[c] += 1
    return [out[i:i + line_len] for i in range(0, len(out), line_len)], truth
