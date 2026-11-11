"""One word = one letter? The choices from the master card as a hidden stream of letters.

A scribe with a table could hide a text one letter a word: the piece taken from one column (or
the pair taken from two columns) stands for the letter, the rest of the word is filler. Then the
sequence of that choice over consecutive words is a homophonic cipher of a spaceless text, and
(1) a choice tells something about the same choice in the next word, as a letter does about the
next letter; (2) a homophonic solver reads it, and reads it worse when the words of every line
are shuffled. Streams: each of the K columns and each pair of columns. The solver scores keys as
voynich.lab.hillclimb does (letter n-grams, every line one "word"), but climbs by sweeps: for a
symbol, all letters are tried at once in every key of the population.
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Sequence

import numpy as np

from . import hillclimb as H
from .cardchoice import Layout, _mi

Line = list[int]


def streams(codes: np.ndarray, lay: Layout) -> dict[str, list[Line]]:
    """The symbol of every word in every stream, line by line: "k3" = the choice in column 3 (0 = column skipped),
    "k3+k4" = the pair of choices. Words the card cannot write are left out."""
    K = codes.shape[1]
    sizes = [int(codes[:, k].max()) + 1 for k in range(K)]
    starts = np.r_[0, np.cumsum(lay.line_lengths)]
    ok = codes[:, 0] >= 0
    out: dict[str, list[Line]] = {}

    def lines_of(sym: np.ndarray) -> list[Line]:
        return [[int(s) for s, good in zip(sym[a:b], ok[a:b]) if good] for a, b in zip(starts[:-1], starts[1:])]

    for a in range(K):
        out[f"k{a + 1}"] = lines_of(codes[:, a])
        for b in range(a + 1, K):
            out[f"k{a + 1}+k{b + 1}"] = lines_of(codes[:, a] * sizes[b] + codes[:, b])
    return out


def shuffle_lines(lines: Sequence[Line], seed: int) -> list[Line]:
    r = random.Random(seed)
    out = []
    for l in lines:
        l = list(l)
        r.shuffle(l)
        out.append(l)
    return out


def sequence_information(lines: Sequence[Line], shuffles: int = 100, seed: int = 0) -> dict:
    """Bits a symbol tells about the next symbol of its line, beyond the same with the symbols of every line shuffled."""
    ids: dict[int, int] = {}
    for l in lines:
        for s in l:
            ids.setdefault(s, len(ids))
    n = len(ids)

    def mi(ls: Sequence[Line]) -> float:
        x = np.array([ids[a] for l in ls for a in l[:-1]])
        y = np.array([ids[b] for l in ls for b in l[1:]])
        return _mi(x, y, n, n)

    obs = mi(lines)
    null = np.array([mi(shuffle_lines(lines, seed + i)) for i in range(shuffles)])
    return {"observed": obs, "excess": obs - float(null.mean()), "z": (obs - float(null.mean())) / (float(null.std()) or 1e-9),
            "symbols": n}


def hide(text: str, template: Sequence[Line], seed: int) -> tuple[list[Line], dict[int, str]]:
    """Positive control: the letters of `text` hidden in a stream with the symbols and the line lengths of `template`.
    Every symbol stands for one letter, frequent letters get several symbols (homophones) so that the symbol
    frequencies stay near those of the template. Returns the lines and the true key symbol -> letter."""
    r = random.Random(seed)
    sym = Counter(s for l in template for s in l)
    n = sum(sym.values())
    let = Counter(text[:n])
    letters = [c for c, _ in let.most_common()][:len(sym)]
    need = {c: let[c] / sum(let[c] for c in letters) for c in letters}
    key: dict[int, str] = {}
    pool: dict[str, list[int]] = {c: [] for c in letters}
    order = [s for s, _ in sym.most_common()]
    for c, s in zip(reversed(letters), reversed(order)):               # every letter gets one symbol, rare with rare
        key[s] = c
        pool[c].append(s)
        need[c] -= sym[s] / n
    for s in order:
        if s not in key:
            c = max(letters, key=lambda x: need[x])
            key[s] = c
            pool[c].append(s)
            need[c] -= sym[s] / n
    weights = {c: [sym[s] for s in pool[c]] for c in letters}
    out, i = [], 0
    for l in template:
        row = []
        while len(row) < len(l) and i < len(text):
            c = text[i]
            i += 1
            if c in pool:
                row.append(r.choices(pool[c], weights[c])[0])
        out.append(row)
    return out, key


def pieces(text: str, template: Sequence[Line]) -> list[str]:
    """A spaceless text cut into pieces as long as the lines of the template (what the solver's language model sees)."""
    out, i = [], 0
    lengths = [len(l) for l in template if l] or [9]
    k = 0
    while i < len(text):
        n = lengths[k % len(lengths)]
        out.append(text[i:i + n])
        i += n
        k += 1
    return [p for p in out if p]


def as_words(lines: Sequence[Line]) -> list[list[H.Word]]:
    """A stream in the solver's format: every line one word, every symbol one glyph."""
    return [[tuple(f"s{s}" for s in l)] for l in lines if l]


def _merge_cost(keys, freq, A: int, xp: H.Backend, total: float):
    """sum_u n_u ln n_u / total for every key, n_u = occurrences of the symbols standing for letter u. The language model
    alone rewards keys that pour most symbols into a few frequent letters (the decoded text is then cheap); the full
    likelihood of a homophonic cipher also pays for which symbol of a letter was written, and that cancels the gain
    (the same correction as in voynich.lab.nomen2 and voynich.lab.polybius)."""
    G = freq.shape[0]
    if xp.torch:
        load = xp.torch.zeros((keys.shape[0], A), dtype=xp.torch.float64, device=keys.device)
        load.scatter_add_(1, keys[:, :G], freq[None].expand(keys.shape[0], G))
        return (load * xp.torch.log(load.clamp(min=1.0))).sum(1) / total
    rows = np.repeat(np.arange(keys.shape[0]), G)
    load = np.bincount(rows * A + keys[:, :G].ravel(), weights=np.tile(freq, keys.shape[0]), minlength=keys.shape[0] * A)
    load = load.reshape(keys.shape[0], A)
    return (load * np.log(np.maximum(load, 1.0))).sum(1) / total


def sweep_climb(text: H.GlyphText, lm: H.NgramModel, population: int, sweeps: int, seed: int, xp: H.Backend,
                held_out: H.GlyphText | None = None, temperature: float = 0.02) -> dict:
    """Homophonic key by coordinate ascent: for one symbol at a time, every letter is tried at once in every one of
    `population` keys and the best is kept (with annealed Gumbel noise, so early sweeps explore). A sweep visits every
    symbol once in a random order. The score is the full likelihood: letter n-grams of the decoded text minus the
    cost of merging symbols into one letter (_merge_cost). Far fewer steps than changing one random symbol to one random letter
    (voynich.lab.hillclimb.climb), which matters for streams of hundreds of symbols. Same result format as climb."""
    import math
    r = np.random.default_rng(seed)
    G, A = text.gap, len(lm.symbols)
    letters = np.array([i for i in range(A) if i != lm.space])
    keys = r.choice(letters, size=(population, G + 1))
    keys[:, G] = lm.space
    k = xp.array(keys)
    grams, counts = xp.array(text.grams), xp.array(text.counts, np.float64)
    table = xp.array(lm.table)
    total = float(text.counts.sum())
    f = np.zeros(G)
    np.add.at(f, text.grams[:, -1][text.grams[:, -1] < G], text.counts[text.grams[:, -1] < G])
    freq = xp.array(f, np.float64)
    let = xp.array(letters)
    L = len(letters)
    ar = xp.array(np.arange(population))
    for sweep in range(sweeps):
        temp = temperature * math.log(2) * (1 - sweep / max(1, sweeps - 1))
        for g in r.permutation(G):
            if xp.torch:
                cand = k.repeat_interleave(L, 0)
                cand[:, g] = let.repeat(population)
            else:
                cand = np.repeat(k, L, 0)
                cand[:, g] = np.tile(let, population)
            sc = (H._score(cand, grams, counts, table, xp, total) - _merge_cost(cand, freq, A, xp, total)).reshape(population, L)
            if temp > 0:
                sc = sc + xp.array(r.gumbel(0, temp, size=(population, L)))
            k[ar, g] = let[sc.argmax(1)]
    lm_score = H._score(k, grams, counts, table, xp, total)
    final = xp.to_np(lm_score - _merge_cost(k, freq, A, xp, total))
    best = int(final.argmax())
    best_key = xp.to_np(k[best]).copy()
    out = {"bits": -float(xp.to_np(lm_score)[best]) / math.log(2), "key": {text.glyphs[g]: lm.symbols[int(best_key[g])] for g in range(G)}}
    if held_out is not None:
        hv = H._score(xp.array(best_key[None]), xp.array(held_out.grams), xp.array(held_out.counts, np.float64), table, xp,
                      float(held_out.counts.sum()))
        out["held_out_bits"] = -float(xp.to_np(hv)[0]) / math.log(2)
    return out


def solve(lines: Sequence[Line], lm: H.NgramModel, population: int, sweeps: int, seed: int, xp: H.Backend, min_count: int = 10) -> dict:
    """Key fitted on every other line, judged on the rest (bits per symbol). Symbols seen under `min_count` times are
    left undecoded."""
    words = as_words(lines)
    fit, held = H.split_odd_even(words)
    glyphs = H.glyph_inventory(words, min_count)
    r = sweep_climb(H.GlyphText.build(fit, glyphs, lm.order), lm, population, sweeps, seed, xp, H.GlyphText.build(held, glyphs, lm.order))
    r["symbols"] = len(glyphs)
    return r


def accuracy(found: dict, truth: dict[int, str], lines: Sequence[Line]) -> float:
    return H.key_accuracy(found, {f"s{s}": c for s, c in truth.items()}, as_words(lines))
