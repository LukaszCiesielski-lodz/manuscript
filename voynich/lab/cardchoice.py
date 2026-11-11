"""Which entry of the master card the scribe took, and whether that choice follows the page.

voynich.lab.card found a card of a few hundred pieces in 6 columns that writes every word. If the
text says something, the meaning can only sit in the choices: which piece (or none) was taken from
each column. Here every token is parsed into its column choices (the most likely parse under the
card's own usage) and the information the choices carry about the page is measured beyond what the
section alone carries: I(choice; page) - I(choice; section), against lines shuffled among the
pages of their section (lines kept whole). A scribe drifting through his habits also makes pages
differ, so the same measure on v7 gibberish (drift and self-citation, no meaning) is the yardstick,
and Latin laid out in the same lines and pages shows what a text with topics gives.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from typing import Sequence

import numpy as np

Word = tuple[str, ...]


class Layout:
    """Lines, pages and sections of a text: token i lies in line[i]; line j in page[j]; page p in section[p]."""

    def __init__(self, line_lengths: Sequence[int], line_page: Sequence[int], page_section: Sequence[int]):
        self.line_lengths = list(line_lengths)
        self.line_page = np.asarray(line_page)
        self.page_section = np.asarray(page_section)
        self.token_line = np.repeat(np.arange(len(self.line_lengths)), self.line_lengths)
        self.n_tokens = int(sum(self.line_lengths))

    def fill(self, words: Sequence[Word]) -> list[Word]:
        """The first n_tokens words laid into these lines (words reused from the start if too few)."""
        if not words:
            raise ValueError("no words")
        return [words[i % len(words)] for i in range(self.n_tokens)]

    def subset(self, pages: set[int]) -> tuple["Layout", np.ndarray]:
        """The layout restricted to some pages, and the mask of their tokens."""
        keep_lines = np.array([p in pages for p in self.line_page])
        mask = keep_lines[self.token_line]
        ids = sorted(pages)
        remap = {p: i for i, p in enumerate(ids)}
        lay = Layout([n for n, k in zip(self.line_lengths, keep_lines) if k],
                     [remap[p] for p, k in zip(self.line_page, keep_lines) if k],
                     [self.page_section[p] for p in ids])
        return lay, mask


def parse_tokens(card: np.ndarray, chunks: Sequence[Word], tokens: Sequence[Word]) -> tuple[np.ndarray, list[list[str]]]:
    """Every token as K column choices: codes[i, k] = 1 + index of the piece taken from column k, 0 = column skipped,
    -1 in the whole row = the card cannot write the token. Among several parses the one most probable under the
    card's own usage (two passes: fewest pieces first, then log usage counts). Returns the codes and, per column,
    the piece names behind the codes."""
    K = card.shape[1]
    col_pieces = [[chunks[j] for j in np.nonzero(card[:, k])[0]] for k in range(K)]
    index = [{g: i for i, g in enumerate(ps)} for ps in col_pieces]
    n_max = max(len(g) for g in chunks)
    types = Counter(tuple(t) for t in tokens)

    def best_parse(w: Word, score) -> tuple | None:
        L = len(w)
        memo: dict = {}

        def go(pos: int, k: int):
            if pos == L:
                return 0.0, ()
            if k >= K:
                return None
            key = (pos, k)
            if key in memo:
                return memo[key]
            best = None
            for kk in range(k, K):
                for n in range(1, min(n_max, L - pos) + 1):
                    j = index[kk].get(w[pos:pos + n])
                    if j is None:
                        continue
                    rest = go(pos + n, kk + 1)
                    if rest is None:
                        continue
                    s = score(kk, j) + rest[0]
                    if best is None or s > best[0] + 1e-12:
                        best = (s, ((kk, j),) + rest[1])
            memo[key] = best
            return best

        r = go(0, 0)
        return None if r is None else r[1]

    parses = {w: best_parse(w, lambda k, j: -1.0) for w in types}
    use = [Counter() for _ in range(K)]
    for w, p in parses.items():
        for k, j in p or ():
            use[k][j] += types[w]
    tot = [sum(u.values()) + len(index[k]) for k, u in enumerate(use)]
    parses = {w: best_parse(w, lambda k, j: math.log((use[k][j] + 1) / tot[k])) if p else None for w, p in parses.items()}
    row = {}
    for w, p in parses.items():
        if p is None:
            row[w] = [-1] * K
        else:
            r = [0] * K
            for k, j in p:
                r[k] = j + 1
            row[w] = r
    codes = np.array([row[tuple(t)] for t in tokens], dtype=np.int64).reshape(len(tokens), K)
    names = [["–"] + ["".join(g) for g in ps] for ps in col_pieces]
    return codes, names


def _mi(x: np.ndarray, y: np.ndarray, nx: int, ny: int) -> float:
    """Plug-in mutual information in bits between two code arrays."""
    joint = np.bincount(y * nx + x, minlength=nx * ny).reshape(ny, nx).astype(float)
    n = joint.sum()
    px = joint.sum(0) / n
    py = joint.sum(1) / n
    p = joint / n
    nz = p > 0
    return float((p[nz] * np.log2(p[nz] / (py[:, None] * px[None, :])[nz])).sum())


def _entropy(x: np.ndarray) -> float:
    p = np.bincount(x) / len(x)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def page_information(codes: np.ndarray, lay: Layout, permutations: int = 200, seed: int = 0) -> dict:
    """Per column: information of the choice about the page beyond its section, I(X; page) - I(X; section), observed
    against lines shuffled among the pages of their section (lines whole). Tokens the card cannot write are left out."""
    ok = codes[:, 0] >= 0
    tl = lay.token_line[ok]
    X = codes[ok]
    page_t = lay.line_page[tl]
    n_pages = int(lay.line_page.max()) + 1
    sec_of_line = lay.page_section[lay.line_page]
    rng = np.random.default_rng(seed)
    perms = []
    for _ in range(permutations):
        lp = lay.line_page.copy()
        for s in np.unique(sec_of_line):
            idx = np.nonzero(sec_of_line == s)[0]
            lp[idx] = lp[rng.permutation(idx)]
        perms.append(lp[tl])
    out = []
    for k in range(X.shape[1]):
        x = X[:, k]
        nx = int(x.max()) + 1
        obs = _mi(x, page_t, nx, n_pages)
        null = np.array([_mi(x, pp, nx, n_pages) for pp in perms])
        h = _entropy(x)
        sd = float(null.std()) or 1e-9
        out.append({"column": k + 1, "H": h, "observed": obs, "null": float(null.mean()), "sd": sd,
                    "excess": obs - float(null.mean()), "z": (obs - float(null.mean())) / sd, "_null": null})
    tot_obs = sum(c["observed"] for c in out)
    tot_null = sum(c["_null"] for c in out)
    for c in out:
        del c["_null"]
    H = sum(c["H"] for c in out)
    excess = tot_obs - float(tot_null.mean())
    return {"columns": out, "excess": excess, "ratio": excess / H if H else 0.0, "H": H,
            "z": excess / (float(tot_null.std()) or 1e-9), "tokens": int(ok.sum()), "unwritten": int((~ok).sum())}


def section_information(codes: np.ndarray, lay: Layout, permutations: int = 200, seed: int = 0) -> list[dict]:
    """Per column: information of the choice about the section, against section labels shuffled among pages."""
    ok = codes[:, 0] >= 0
    page_t = lay.line_page[lay.token_line[ok]]
    X = codes[ok]
    secs = lay.page_section
    n_sec = int(secs.max()) + 1
    rng = np.random.default_rng(seed)
    perms = [rng.permutation(secs)[page_t] for _ in range(permutations)]
    out = []
    for k in range(X.shape[1]):
        x = X[:, k]
        nx = int(x.max()) + 1
        obs = _mi(x, secs[page_t], nx, n_sec)
        null = np.array([_mi(x, s, nx, n_sec) for s in perms])
        h = _entropy(x)
        out.append({"column": k + 1, "excess": obs - float(null.mean()), "ratio": (obs - float(null.mean())) / h if h else 0.0,
                    "z": (obs - float(null.mean())) / (float(null.std()) or 1e-9)})
    return out


def synthetic_pages(chunks: Sequence[Word], lay: Layout, seed: int, bias: float = 0.0, column: int = 2,
                    columns: int = 5, per_column: int = 8) -> tuple[list[Word], np.ndarray]:
    """Control text written from a random true card into the given lines; with `bias` > 0, in column `column` every
    page has its own favourite piece taken with that probability (a choice that follows the page). Returns the tokens
    and the true card."""
    r = random.Random(seed)
    pool = list(range(len(chunks)))
    r.shuffle(pool)
    true = np.zeros((len(chunks), columns), dtype=bool)
    cols = []
    for k in range(columns):
        entries = pool[k * per_column:(k + 1) * per_column]
        cols.append(entries)
        true[entries, k] = True
    n_pages = int(lay.line_page.max()) + 1
    fav = [r.randrange(per_column) for _ in range(n_pages)]
    out = []
    for line, n in enumerate(lay.line_lengths):
        page = lay.line_page[line]
        made = 0
        while made < n:
            w = []
            for k, entries in enumerate(cols):
                if r.random() < 0.6:
                    if k == column and r.random() < bias:
                        j = fav[page]
                    else:
                        j = min(int(r.paretovariate(1.2)) - 1, per_column - 1)
                    w += list(chunks[entries[j]])
            if w:
                out.append(tuple(w))
                made += 1
    return out, true
