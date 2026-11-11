"""The master card: one table of word pieces from which every scribe could compose the words.

A card has K ordered columns (start ... end of a word); each column holds a few pieces (n-grams
of glyphs, n <= 3). A word can be written from the card when it splits into pieces taken from
strictly increasing columns (a column may be skipped). The size of a card is its number of
entries (a piece in a column). The question: how small a card writes most of the manuscript's
words, against languages, gibberish and the manuscript with glyphs shuffled inside each word.

Parsing is dynamic programming over glyph positions and columns, done for a whole population of
cards and all word types at once; the arrays run on cupy when a GPU is there, else on numpy
(voynich.lab.nomen2.array_module). The search is a (mu + lambda) evolution under a hard budget.
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Sequence

import numpy as np

from .nomen2 import _host, array_module

Word = tuple[str, ...]
MAX_LEN = 15


def chunk_inventory(tokens: Sequence[Word], n_max: int = 3, min_count: int = 20) -> list[Word]:
    """Pieces: every n-gram of units (n <= n_max) seen at least `min_count` times in the tokens, most frequent first."""
    c = Counter()
    for w in tokens:
        for n in range(1, n_max + 1):
            for i in range(len(w) - n + 1):
                c[w[i:i + n]] += 1
    singles = {w[i:i + 1] for w in tokens for i in range(len(w))}
    keep = [g for g, v in c.most_common() if v >= min_count or g in singles]
    return keep


class Encoded:
    """Word types of a corpus as piece ids: ids[w, pos, n-1] = id of type w's piece of length n at pos, or -1."""

    def __init__(self, tokens: Sequence[Word], chunks: Sequence[Word], max_len: int = MAX_LEN):
        index = {g: i for i, g in enumerate(chunks)}
        n_max = max(len(g) for g in chunks)
        counts = Counter(tuple(w) for w in tokens if w)
        self.types = list(counts)
        self.total = sum(counts.values())
        fit = [w for w in self.types if len(w) <= max_len]
        self.fit_types = fit
        self.weights = np.array([counts[w] for w in fit], float)
        self.lengths = np.array([len(w) for w in fit])
        self.ids = -np.ones((len(fit), max_len, n_max), dtype=np.int64)
        for k, w in enumerate(fit):
            for pos in range(len(w)):
                for n in range(1, n_max + 1):
                    if pos + n <= len(w):
                        self.ids[k, pos, n - 1] = index.get(w[pos:pos + n], -1)
        self.max_len, self.n_max, self.n_chunks = max_len, n_max, len(chunks)


def parsed(xp, cards, enc: Encoded, dev=None):
    """Boolean [P, W]: can type w be written from card p? `cards` is a device bool array [P, C, K]."""
    P, C, K = cards.shape
    ids = dev["ids"] if dev else xp.asarray(enc.ids)
    lengths = dev["lengths"] if dev else xp.asarray(enc.lengths)
    W, L = ids.shape[0], enc.max_len
    reach = xp.zeros((P, W, L + 1, K + 1), dtype=bool)
    reach[:, :, 0, 0] = True
    for pos in range(L):
        here = reach[:, :, pos, :]                                    # [P, W, K+1]
        if not bool(here.any()):
            continue
        before = xp.cumsum(here, axis=2) > 0                          # used some column <= j
        for n in range(1, enc.n_max + 1):
            if pos + n > L:
                break
            cid = ids[:, pos, n - 1]
            ok = cid >= 0
            allowed = cards[:, xp.where(ok, cid, 0), :] & ok[None, :, None]   # [P, W, K]
            reach[:, :, pos + n, 1:] |= before[:, :, :K] & allowed    # column j+1 needs a used column <= j
    end = reach[:, xp.arange(W), lengths, :]                          # [P, W, K+1]
    return end[:, :, 1:].any(axis=2)


def coverage(xp, cards, enc: Encoded, dev=None):
    """Share of tokens (all tokens of the corpus, too-long words included) each card can write."""
    w = dev["weights"] if dev else xp.asarray(enc.weights)
    return (parsed(xp, cards, enc, dev) * w[None, :]).sum(1) / enc.total


def positions(tokens: Sequence[Word], chunks: Sequence[Word]) -> np.ndarray:
    """Mean relative position (0 = start, 1 = end) of every piece inside the words where it occurs."""
    index = {g: i for i, g in enumerate(chunks)}
    s, n = np.zeros(len(chunks)), np.zeros(len(chunks))
    for w in tokens:
        for k in range(1, 4):
            for i in range(len(w) - k + 1):
                j = index.get(w[i:i + k])
                if j is not None:
                    s[j] += (i + k / 2) / max(1, len(w))
                    n[j] += 1
    return np.where(n > 0, s / np.maximum(n, 1), 0.5)


def heuristic_card(chunks, pos: np.ndarray, freq: np.ndarray, budget: int, K: int) -> np.ndarray:
    """Start card: the most frequent pieces, each in the column of its typical place in the word."""
    card = np.zeros((len(chunks), K), dtype=bool)
    for j in np.argsort(-freq)[:budget]:
        card[j, min(K - 1, int(pos[j] * K))] = True
    return card


def mutate(card: np.ndarray, budget: int, r: random.Random, chunk_p: np.ndarray) -> np.ndarray:
    c = card.copy()
    C, K = c.shape
    for _ in range(r.choice((1, 1, 2, 3))):
        on = np.argwhere(c)
        op = r.random()
        if (op < 0.4 or len(on) == 0) and len(on) < budget:
            j = int(np.searchsorted(np.cumsum(chunk_p), r.random()))
            c[min(j, C - 1), r.randrange(K)] = True
        elif op < 0.7 and len(on):
            a, b = on[r.randrange(len(on))]
            c[a, b] = False
        elif len(on):
            a, b = on[r.randrange(len(on))]
            c[a, b] = False
            c[a, max(0, min(K - 1, b + r.choice((-1, 1))))] = True
    while c.sum() > budget:
        on = np.argwhere(c)
        a, b = on[r.randrange(len(on))]
        c[a, b] = False
    return c


def evolve(enc: Encoded, tokens: Sequence[Word], chunks: Sequence[Word], budget: int, K: int = 6, population: int = 32,
           generations: int = 300, seed: int = 0, prefer_gpu: bool = True, log=None, init: np.ndarray | None = None) -> dict:
    """Best card of at most `budget` entries for the corpus; returns the card, its coverage and its size."""
    xp = array_module(prefer_gpu)
    dev = {"ids": xp.asarray(enc.ids), "lengths": xp.asarray(enc.lengths), "weights": xp.asarray(enc.weights)}
    r = random.Random(seed)
    freq = np.zeros(len(chunks))
    index = {g: i for i, g in enumerate(chunks)}
    for w, n in zip(enc.fit_types, enc.weights):
        for k in range(1, enc.n_max + 1):
            for i in range(len(w) - k + 1):
                j = index.get(w[i:i + k])
                if j is not None:
                    freq[j] += n
    chunk_p = (freq + 1) / (freq + 1).sum()
    start = heuristic_card(chunks, positions(tokens, chunks), freq, budget, K) if init is None else init.copy()
    while start.sum() > budget:
        on = np.argwhere(start)
        a, b = on[r.randrange(len(on))]
        start[a, b] = False
    pop = [start] + [mutate(start, budget, r, chunk_p) for _ in range(population - 1)]
    keep = max(2, population // 4)
    best = (-1.0, None)
    for g in range(generations):
        cov = _host(coverage(xp, xp.asarray(np.stack(pop)), enc, dev))
        size = np.array([c.sum() for c in pop])
        order = np.lexsort((size, -cov))
        if cov[order[0]] > best[0] or (cov[order[0]] == best[0] and size[order[0]] < best[1].sum()):
            best = (float(cov[order[0]]), pop[order[0]].copy())
        elite = [pop[i] for i in order[:keep]]
        pop = elite + [mutate(elite[min(r.randrange(keep), r.randrange(keep))], budget, r, chunk_p)
                       for _ in range(population - keep)]
        if log and (g + 1) % max(1, generations // 5) == 0:
            log(f"    pokolenie {g + 1}/{generations}: pokrycie {best[0]:.3f}")
    return {"card": best[1], "coverage": best[0], "size": int(best[1].sum()), "backend": xp.__name__}


def evaluate(card: np.ndarray, enc: Encoded, prefer_gpu: bool = True) -> float:
    xp = array_module(prefer_gpu)
    return float(_host(coverage(xp, xp.asarray(card[None]), enc))[0])


def synthetic(chunks: Sequence[Word], n_tokens: int, seed: int, columns: int = 5, per_column: int = 8,
              noise: float = 0.1) -> tuple[list[Word], np.ndarray]:
    """Positive control: words written from a random true card (one piece or nothing per column), a share `noise`
    with one unit changed. Returns the tokens and the true card over `chunks`."""
    r = random.Random(seed)
    pool = list(range(len(chunks)))
    r.shuffle(pool)
    true = np.zeros((len(chunks), columns), dtype=bool)
    cols = []
    for k in range(columns):
        entries = pool[k * per_column:(k + 1) * per_column]
        cols.append(entries)
        true[entries, k] = True
    units = sorted({u for g in chunks for u in g})
    out = []
    while len(out) < n_tokens:
        w = []
        for entries in cols:
            if r.random() < 0.6:
                w += list(chunks[entries[min(int(r.paretovariate(1.2)) - 1, len(entries) - 1)]])
        if not w or len(w) > MAX_LEN:
            continue
        if r.random() < noise:
            w[r.randrange(len(w))] = r.choice(units)
        out.append(tuple(w))
    return out, true


def shuffle_within(tokens: Sequence[Word], seed: int) -> list[Word]:
    """Negative control: the units of every word type in a fixed random order (same type, same shuffle)."""
    memo = {}
    out = []
    for w in tokens:
        if w not in memo:
            u = list(w)
            random.Random(hash((seed, w)) & 0xFFFFFFFF).shuffle(u)
            memo[w] = tuple(u)
        out.append(memo[w])
    return out


def table(card: np.ndarray, chunks: Sequence[Word], freq: Sequence[float] | None = None, sep: str = "") -> list[list[str]]:
    """The card as columns of piece strings (most frequent piece first)."""
    C, K = card.shape
    cols = []
    for k in range(K):
        ids = list(np.nonzero(card[:, k])[0])
        if freq is not None:
            ids.sort(key=lambda j: -freq[j])
        cols.append([sep.join(chunks[j]) for j in ids])
    return cols


def piece_frequency(enc: Encoded, chunks: Sequence[Word]) -> np.ndarray:
    index = {g: i for i, g in enumerate(chunks)}
    freq = np.zeros(len(chunks))
    for w, n in zip(enc.fit_types, enc.weights):
        for k in range(1, enc.n_max + 1):
            for i in range(len(w) - k + 1):
                j = index.get(w[i:i + k])
                if j is not None:
                    freq[j] += n
    return freq


def prune(enc: Encoded, chunks: Sequence[Word], K: int = 6, target: float = 1.0, population: int = 8, seed: int = 0,
          prefer_gpu: bool = True, log=None) -> dict:
    """Smallest card found by pruning the full card: every one of `population` cards removes the entries one at a time,
    each in its own order, and keeps a removal only when the card still writes `target` of the tokens. Orders: half
    random, half rare-and-long pieces first (with noise). All cards are checked at once at every step."""
    xp = array_module(prefer_gpu)
    dev = {"ids": xp.asarray(enc.ids), "lengths": xp.asarray(enc.lengths), "weights": xp.asarray(enc.weights)}
    freq = piece_frequency(enc, chunks)
    full = np.repeat((freq > 0)[:, None], K, 1)                 # pieces absent from this corpus are never needed
    target = min(target, float(_host(coverage(xp, xp.asarray(full[None]), enc, dev))[0]))
    entries = np.argwhere(full)
    E = len(entries)
    rng = np.random.default_rng(seed)
    orders = []
    key = np.array([-len(chunks[a]) * 10.0 + np.log1p(freq[a]) for a, _ in entries])
    for p in range(population):
        if p % 2:
            orders.append(np.argsort(key + rng.normal(0, 1.0, E)))
        else:
            orders.append(rng.permutation(E))
    orders = np.stack(orders)
    cards = xp.asarray(np.repeat(full[None], population, 0))
    rows = xp.arange(population)
    for t in range(E):
        a = xp.asarray(entries[orders[:, t], 0])
        b = xp.asarray(entries[orders[:, t], 1])
        cards[rows, a, b] = False
        bad = coverage(xp, cards, enc, dev) < target - 1e-9
        cards[rows[bad], a[bad], b[bad]] = True
        if log and (t + 1) % max(1, E // 5) == 0:
            log(f"    krok {t + 1}/{E}: najmniejsza karta {int(_host(cards.sum((1, 2))).min())} wpisów")
    cards_h = _host(cards)
    sizes = cards_h.sum((1, 2))
    best = int(sizes.argmin())
    return {"card": cards_h[best], "size": int(sizes[best]), "sizes": sizes.tolist(), "target": target,
            "backend": xp.__name__}


def shrink(enc: Encoded, tokens: Sequence[Word], chunks: Sequence[Word], card: np.ndarray, target: float, K: int = 6,
           population: int = 32, generations: int = 60, rounds: int = 10, seed: int = 0, prefer_gpu: bool = True,
           log=None) -> np.ndarray:
    """Make a card that writes `target` of the tokens smaller: evolution under budget size - 1, as long as it still
    reaches the target."""
    best = card
    for k in range(rounds):
        r = evolve(enc, tokens, chunks, int(best.sum()) - 1, K, population, generations, seed + k, prefer_gpu, init=best)
        if r["coverage"] < target - 1e-9:
            break
        best = r["card"]
        if log:
            log(f"    zmniejszona do {int(best.sum())} wpisów")
    return best


def card_from_table(columns: Sequence[Sequence[str]], chunks: Sequence[Word]) -> np.ndarray:
    """A card stored as columns of piece strings (voynich.lab.card.table) back as the matrix over `chunks`."""
    by_name: dict[str, int] = {}
    for j, g in enumerate(chunks):
        by_name.setdefault("".join(g), j)
    card = np.zeros((len(chunks), len(columns)), dtype=bool)
    for k, col in enumerate(columns):
        for name in col:
            if name not in by_name:
                raise KeyError(f"piece {name!r} of column {k + 1} is not among the chunks")
            card[by_name[name], k] = True
    return card
