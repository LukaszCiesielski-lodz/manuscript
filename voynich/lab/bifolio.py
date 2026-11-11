"""In what order were the leaves written? The scribe's drift as a clock.

voynich.lab.cardchoice showed that the choices from the master card jump between leaves but hardly
between recto and verso of one leaf: leaves were written at different times. A quire is a stack of
folded sheets (bifolia); leaf n of a quire numbered lo..hi is one sheet with leaf lo + hi - n. If
the scribes wrote sheet by sheet before the quire was put together, the two leaves of a sheet
(far apart in the bound book: f1 and f8) are alike, more than other leaves of the quire; if they
wrote the bound book page after page, neighbouring leaves are alike instead. Then the sheets are
put in the order in which the habits drift (spectral seriation of their similarity).

Similarity: every line is cut to the same number of (column, choice) items, items are standardised
inside the section, and two units (pages, leaves, sheets) are compared by the mean product of
their lines' vectors, which does not depend on how many lines a unit has.
"""

from __future__ import annotations

import random
import re
from typing import Sequence

import numpy as np

from .cardchoice import Layout, Word

# Quires of the manuscript by folio number, missing leaves included (the foliation is older than the losses).
QUIRES = {"A": (1, 8), "B": (9, 16), "C": (17, 24), "D": (25, 32), "E": (33, 40), "F": (41, 48), "G": (49, 56),
          "H": (57, 66), "I": (67, 68), "J": (69, 70), "K": (71, 72), "L": (73, 74), "M": (75, 84), "N": (85, 86),
          "O": (87, 90), "P": (91, 92), "Q": (93, 96), "R": (97, 98), "S": (99, 102), "T": (103, 116)}


def leaf_number(folio: str) -> int:
    m = re.match(r"f(\d+)", folio)
    if not m:
        raise ValueError(folio)
    return int(m.group(1))


def quire_of(n: int) -> str:
    for q, (lo, hi) in QUIRES.items():
        if lo <= n <= hi:
            return q
    raise ValueError(n)


def conjugate(n: int) -> int:
    """The other leaf of the same sheet."""
    lo, hi = QUIRES[quire_of(n)]
    return lo + hi - n


def sheet(n: int) -> tuple[str, int]:
    """The sheet (bifolium) of a leaf: its quire and its depth in the quire (0 = outermost)."""
    lo, _ = QUIRES[quire_of(n)]
    return quire_of(n), min(n, conjugate(n)) - lo


def line_vectors(codes: np.ndarray, lay: Layout, items: int = 8, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Every line as a 0/1 vector over (column, choice) items, cut to `items` random items; lines with fewer are
    marked invalid. Returns the vectors [lines, D] and the valid mask."""
    K = codes.shape[1]
    sizes = [int(codes[:, k].max()) + 1 for k in range(K)]
    off = np.concatenate([[0], np.cumsum(sizes)])
    rng = np.random.default_rng(seed)
    n = len(lay.line_lengths)
    lists: list[list[int]] = [[] for _ in range(n)]
    ok = codes[:, 0] >= 0
    for t in np.nonzero(ok)[0]:
        line = lay.token_line[t]
        for k in range(K):
            v = codes[t, k]
            if v > 0:
                lists[line].append(int(off[k] + v))
    X = np.zeros((n, int(off[-1])), dtype=np.float32)
    valid = np.zeros(n, bool)
    for line, its in enumerate(lists):
        if len(its) >= items:
            X[line, [its[i] for i in rng.choice(len(its), items, replace=False)]] = 1
            valid[line] = True
    return X, valid


def standardise(X: np.ndarray, valid: np.ndarray, group: np.ndarray) -> np.ndarray:
    """Items centred and scaled inside every group of lines (a section), so that what is common to the group cancels."""
    Z = np.zeros_like(X)
    for g in np.unique(group):
        m = valid & (group == g)
        if m.sum() < 2:
            continue
        mu = X[m].mean(0)
        Z[m] = (X[m] - mu) / np.sqrt(np.maximum(mu * (1 - mu), 0.02))
    return Z


def unit_similarity(Z: np.ndarray, valid: np.ndarray, unit: Sequence, min_lines: int = 3) -> tuple[list, np.ndarray]:
    """Units (any hashable label per line) with at least `min_lines` valid lines, and the matrix of their similarities:
    mean product of the standardised vectors of a line of one unit and a line of the other."""
    rows: dict = {}
    for i, u in enumerate(unit):
        if valid[i]:
            rows.setdefault(u, []).append(i)
    units = [u for u, r in rows.items() if len(r) >= min_lines]
    M = np.stack([Z[rows[u]].mean(0) for u in units]) if units else np.zeros((0, Z.shape[1]))
    return units, (M @ M.T) / Z.shape[1] * 1000


def leaf_pair_test(leaves: list[int], S: np.ndarray, stratum: dict, permutations: int = 2000, seed: int = 0) -> dict:
    """Leaves of one quire and one stratum (same hand and language): are the two leaves of a sheet alike (sheets not
    at the centre of the quire, whose leaves are far apart in the bound book), and are neighbouring leaves alike?
    Each against the other pairs of leaves of the same quire and stratum; null: leaves exchanged inside
    (quire, stratum)."""
    n = len(leaves)
    kind = np.full((n, n), -1)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = leaves[i], leaves[j]
            if quire_of(a) != quire_of(b) or stratum[a] != stratum[b]:
                continue
            if conjugate(a) == b:
                kind[i, j] = 1 if abs(a - b) > 1 else 2          # sheet away from the centre / central sheet
            elif abs(a - b) == 1:
                kind[i, j] = 3                                    # neighbours in the book, different sheets
            else:
                kind[i, j] = 0

    def stats(order: np.ndarray) -> tuple[float, float]:
        s = S[np.ix_(order, order)]
        other = s[kind == 0]
        if not len(other):
            return 0.0, 0.0
        c, a = s[kind == 1], s[kind == 3]
        return (float(c.mean() - other.mean()) if len(c) else 0.0, float(a.mean() - other.mean()) if len(a) else 0.0)

    groups: dict = {}
    for i, a in enumerate(leaves):
        groups.setdefault((quire_of(a), stratum[a]), []).append(i)
    rng = np.random.default_rng(seed)
    obs = stats(np.arange(n))
    null = []
    for _ in range(permutations):
        order = np.arange(n)
        for idx in groups.values():
            order[idx] = rng.permutation(idx)
        null.append(stats(order))
    null = np.array(null)
    out = {"pairs": {"arkusz": int((kind == 1).sum()), "arkusz środkowy": int((kind == 2).sum()),
                     "sąsiednie karty": int((kind == 3).sum()), "inne": int((kind == 0).sum())}}
    for name, k in (("sheet", 0), ("neighbour", 1)):
        sd = float(null[:, k].std()) or 1e-9
        out[name] = {"excess": obs[k], "z": (obs[k] - float(null[:, k].mean())) / sd}
    return out


def seriate(S: np.ndarray) -> np.ndarray:
    """Order of the units along one line (spectral seriation: the Fiedler vector of the similarity graph). Returns the
    rank of every unit; the direction is arbitrary."""
    n = len(S)
    if n < 3:
        return np.arange(n)
    W = S - S[~np.eye(n, dtype=bool)].min()
    np.fill_diagonal(W, 0)
    L = np.diag(W.sum(1)) - W
    vals, vecs = np.linalg.eigh(L)
    return np.argsort(np.argsort(vecs[:, 1]))


def spearman(a: Sequence[float], b: Sequence[float]) -> float:
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    if len(ra) < 3 or ra.std() == 0 or rb.std() == 0:
        return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


def synthetic_written(chunks: Sequence[Word], lay: Layout, line_order: Sequence[int], seed: int, strength: float = 0.3,
                      drift: float = 0.01, columns: int = 5, per_column: int = 8) -> tuple[list[Word], np.ndarray]:
    """Control text from a random true card, written line by line in `line_order` (indices of the layout's lines) by a
    scribe whose favourite piece of every column changes after a line with probability `drift`; the lines are then put
    in their places in the layout. `strength` = share of choices that take the favourite (0: no drift at all)."""
    r = random.Random(seed)
    pool = list(range(len(chunks)))
    r.shuffle(pool)
    true = np.zeros((len(chunks), columns), dtype=bool)
    cols = []
    for k in range(columns):
        entries = pool[k * per_column:(k + 1) * per_column]
        cols.append(entries)
        true[entries, k] = True
    fav = [r.randrange(per_column) for _ in range(columns)]
    lines: dict[int, list[Word]] = {}
    for line in line_order:
        for k in range(columns):
            if r.random() < drift:
                fav[k] = r.randrange(per_column)
        out = []
        while len(out) < lay.line_lengths[line]:
            w = []
            for k, entries in enumerate(cols):
                if r.random() < 0.6:
                    j = fav[k] if r.random() < strength else min(int(r.paretovariate(1.2)) - 1, per_column - 1)
                    w += list(chunks[entries[j]])
            if w:
                out.append(tuple(w))
        lines[line] = out
    return [w for line in range(len(lay.line_lengths)) for w in lines[line]], true
