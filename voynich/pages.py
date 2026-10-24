"""Pages of the manuscript as units: vocabulary, one-glyph neighbours, and the statistics of writing order.

A scribe who copies and modifies leaves an arrow of time: a fresh variant (a hapax) has its
source on a page written earlier. `ancestor_excess` measures that arrow for a given page order,
with a null that permutes pages only within blocks (runs of pages of one section and Currier
language), so that the layout of sections in the codex cannot pose as an arrow.
"""

from __future__ import annotations

import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

from . import corpus, eva

Word = tuple[str, ...]


@dataclass
class Page:
    folio: str
    section: str
    language: str
    hand: str
    quire: str
    words: list[Word] = field(default_factory=list)

    @property
    def block_key(self) -> tuple[str, str]:
        return (self.section, self.language)


def folio_key(folio: str) -> tuple:
    m = re.match(r"f(\d+)([rv])(\d*)", folio)
    return (int(m.group(1)), 0 if m.group(2) == "r" else 1, int(m.group(3) or 0)) if m else (10 ** 6, 0, 0)


def load_pages(min_words: int = 60) -> list[Page]:
    """Paragraph text per folio, in foliation order; folios with fewer than `min_words` words dropped."""
    by: dict[str, Page] = {}
    for l in corpus.load_voynich():
        if not l.kind.startswith("P") or not l.words:
            continue
        p = by.setdefault(l.folio, Page(l.folio, l.section, l.language, l.hand, l.quire))
        p.words.extend(tuple(eva.glyphs(w)) for w in l.words)
    return [p for p in sorted(by.values(), key=lambda p: folio_key(p.folio)) if len(p.words) >= min_words]


def blocks(pages: Sequence[Page]) -> list[list[int]]:
    """Maximal runs of consecutive pages with the same section and language, as index lists."""
    out, cur = [], []
    for i, p in enumerate(pages):
        if cur and p.block_key != pages[cur[-1]].block_key:
            out.append(cur)
            cur = []
        cur.append(i)
    if cur:
        out.append(cur)
    return out


class Neighbours:
    """Words within edit distance 1 (glyph level), via the symmetric-deletion trick."""

    def __init__(self, pages: Sequence[Page]):
        glyphs = sorted({g for p in pages for w in p.words for g in w})
        self.gid = {g: chr(0x100 + i) for i, g in enumerate(glyphs)}
        self.counts = [Counter(self.enc(w) for w in p.words) for p in pages]
        self.total: Counter = Counter()
        for c in self.counts:
            self.total.update(c)
        dels: dict[str, set[str]] = defaultdict(set)
        for w in self.total:
            for i in range(len(w)):
                dels[w[:i] + w[i + 1:]].add(w)
        self.nb: dict[str, set[str]] = {}
        for w in self.total:
            out: set[str] = set()
            for i in range(len(w)):
                d = w[:i] + w[i + 1:]
                out |= dels[d]
                if d in self.total:
                    out.add(d)
            out |= dels.get(w, set())
            out.discard(w)
            self.nb[w] = out

    def enc(self, w: Word) -> str:
        return "".join(self.gid[g] for g in w)

    def degree(self, page: int) -> float:
        return float(np.mean([len(self.nb[w]) for w in self.counts[page]]))

    def hapax_share(self, page: int) -> float:
        return float(np.mean([self.total[w] == 1 for w in self.counts[page]]))


def ancestor_excess(nbs: Neighbours, order: Sequence[int], positions: dict[int, int] | None = None) -> tuple[float, int]:
    """Mean over hapaxes of (share of neighbour tokens on pages placed earlier) minus (share expected from the
    hapax's own position). Positive: sources precede their variants (an arrow along `order`)."""
    pos = positions or {p: i for i, p in enumerate(order)}
    N = len(order)
    where: dict[str, list[int]] = defaultdict(list)
    for p in order:
        for w, c in nbs.counts[p].items():
            where[w] += [pos[p]] * c
    vals = []
    for p in order:
        q = pos[p]
        for b in nbs.counts[p]:
            if nbs.total[b] != 1:
                continue
            occ = [x for a in nbs.nb[b] for x in where[a]]
            if occ:
                vals.append(sum(1 for x in occ if x < q) / len(occ) - q / max(1, N - 1))
    return (float(np.mean(vals)) if vals else 0.0), len(vals)


def arrow_z(nbs: Neighbours, order: Sequence[int], blks: Sequence[Sequence[int]], shuffles: int, seed: int) -> dict:
    """Ancestor excess against a null that permutes page positions within each block."""
    r = random.Random(seed)
    base, n = ancestor_excess(nbs, order)
    null = []
    for _ in range(shuffles):
        pos = {}
        for blk in blks:
            xs = [order.index(p) for p in blk]
            r.shuffle(xs)
            for p, x in zip(blk, xs):
                pos[p] = x
        null.append(ancestor_excess(nbs, order, pos)[0])
    mu, sd = float(np.mean(null)), float(np.std(null)) or 1e-9
    return {"excess": base, "n_hapax": n, "null_mean": mu, "null_sd": sd, "z": (base - mu) / sd}


def gradient_z(values: Sequence[float], blks: Sequence[Sequence[int]], shuffles: int, seed: int) -> dict:
    """Spearman correlation of a per-page value with position, against within-block permutations."""
    from scipy.stats import spearmanr
    r = random.Random(seed)
    N = len(values)
    base = spearmanr(range(N), values).correlation
    null = []
    for _ in range(shuffles):
        v = list(values)
        for blk in blks:
            xs = [v[i] for i in blk]
            r.shuffle(xs)
            for i, x in zip(blk, xs):
                v[i] = x
        null.append(spearmanr(range(N), v).correlation)
    mu, sd = float(np.mean(null)), float(np.std(null)) or 1e-9
    return {"rho": float(base), "null_mean": mu, "null_sd": sd, "z": (base - mu) / sd}


def synthetic_self_citation(n_pages: int, words_per_page: int, seed: int, near: bool, p_copy_modify: float = 0.7,
                            p_copy: float = 0.2) -> list[Page]:
    """Pages written by copying-with-modification from earlier pages (the previous three, or all of them)."""
    r = random.Random(seed)
    glyphs = list("abcdefghijklmnopqrst")

    def fresh() -> Word:
        return tuple(r.choice(glyphs) for _ in range(r.randint(2, 7)))

    def mutate(w: Word) -> Word:
        w = list(w)
        i = r.randrange(len(w))
        k = r.random()
        if k < 0.4 and len(w) > 2:
            del w[i]
        elif k < 0.7:
            w[i] = r.choice(glyphs)
        else:
            w.insert(i, r.choice(glyphs))
        return tuple(w)

    pages = [Page("s0", "synthetic", "S", "1", "A", [fresh() for _ in range(words_per_page)])]
    for t in range(1, n_pages):
        src = [w for p in (pages[max(0, t - 3):t] if near else pages[:t]) for w in p.words]
        words = []
        for _ in range(words_per_page):
            k = r.random()
            words.append(mutate(r.choice(src)) if k < p_copy_modify else r.choice(src) if k < p_copy_modify + p_copy else fresh())
        pages.append(Page(f"s{t}", "synthetic", "S", "1", "A", words))
    return pages


def pages_from_words(words: Sequence[str], per_page: int, section: str = "ref") -> list[Page]:
    return [Page(f"p{i}", section, "L", "1", "A", [tuple(w) for w in words[i:i + per_page]])
            for i in range(0, len(words) - per_page + 1, per_page)]
