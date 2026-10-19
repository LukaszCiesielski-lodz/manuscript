"""Where glyphs sit inside words and lines, and which words mark sections.

These are the places the Voynich text departs most from natural language:
glyphs occupy near-fixed slots inside a word, and line position changes
which words are used.
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from typing import Callable, Sequence

from . import stats

Word = Sequence[str]


def positional_profile(words: Sequence[Word], min_count: int = 50) -> dict[str, dict[str, float]]:
    """For each symbol: share of its occurrences word-initially, medially, finally, alone."""
    pos: dict[str, Counter] = defaultdict(Counter)
    for w in words:
        if len(w) == 1:
            pos[w[0]]["alone"] += 1
            continue
        pos[w[0]]["initial"] += 1
        pos[w[-1]]["final"] += 1
        for s in w[1:-1]:
            pos[s]["medial"] += 1
    out = {}
    for s, c in pos.items():
        n = sum(c.values())
        if n >= min_count:
            out[s] = {k: c[k] / n for k in ("initial", "medial", "final", "alone")}
    return out


def positional_rigidity(words: Sequence[Word], min_count: int = 50) -> float:
    """Count-weighted mean of each symbol's dominant-position share (1.0 = every symbol has one slot)."""
    prof = positional_profile(words, min_count)
    counts = Counter(s for w in words for s in w)
    total = sum(counts[s] for s in prof)
    return sum(max(p.values()) * counts[s] for s, p in prof.items()) / total


def order_consistency(words: Sequence[Word], min_pairs: int = 30) -> float:
    """How fixed the relative order of two symbols inside a word is.

    For every pair (a, b) of distinct symbols seen together in words, take
    max(P(a before b), P(b before a)) over first occurrences, weighted by the
    number of words holding both. 0.5 = free order, 1.0 = strict slot order.
    """
    before: Counter = Counter()
    for w in words:
        first: dict[str, int] = {}
        for i, s in enumerate(w):
            first.setdefault(s, i)
        syms = sorted(first, key=first.get)
        for i, a in enumerate(syms):
            for b in syms[i + 1:]:
                before[(a, b)] += 1
    num = den = 0.0
    seen = set()
    for (a, b), n_ab in before.items():
        if (a, b) in seen:
            continue
        seen.update({(a, b), (b, a)})
        n_ba = before.get((b, a), 0)
        n = n_ab + n_ba
        if n >= min_pairs:
            num += max(n_ab, n_ba)
            den += n
    return num / den if den else float("nan")


def permutation_test(
    words: Sequence[Word],
    statistic: Callable[[Sequence[Word]], float],
    trials: int = 200,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Observed statistic vs. word order shuffled `trials` times.

    Returns (observed, mean under shuffling, empirical one-sided p-value).
    A small p means the effect depends on word order, not just on vocabulary.
    """
    rng = random.Random(seed)
    observed = statistic(words)
    shuffled = list(words)
    hits = 0
    total = 0.0
    for _ in range(trials):
        rng.shuffle(shuffled)
        v = statistic(shuffled)
        total += v
        hits += v >= observed
    return observed, total / trials, (hits + 1) / (trials + 1)


def adjacent_near_rate(words: Sequence[Word]) -> float:
    ws = [tuple(w) for w in words]
    return sum(stats.is_near(a, b) for a, b in zip(ws, ws[1:])) / (len(ws) - 1)


def adjacent_repeat_rate(words: Sequence[Word]) -> float:
    ws = [tuple(w) for w in words]
    return sum(a == b for a, b in zip(ws, ws[1:])) / (len(ws) - 1)


def keywords(groups: dict[str, Sequence[str]], top: int = 12, min_count: int = 8) -> dict[str, list[tuple[str, float, int]]]:
    """Words most characteristic of each group: log-odds ratio with an informative Dirichlet prior
    (Monroe, Colaresi & Quinn 2008), returned as (word, z-score, count)."""
    total = Counter()
    per = {g: Counter(ws) for g, ws in groups.items()}
    for c in per.values():
        total.update(c)
    a0 = sum(total.values())
    out = {}
    for g, c in per.items():
        n_g = sum(c.values())
        rest_n = a0 - n_g
        scored = []
        for w, y in c.items():
            if y < min_count:
                continue
            alpha = total[w] / a0 * 500  # prior strength
            y_rest = total[w] - y
            l1 = math.log((y + alpha) / (n_g + 500 - y - alpha))
            l2 = math.log((y_rest + alpha) / (rest_n + 500 - y_rest - alpha))
            var = 1 / (y + alpha) + 1 / (y_rest + alpha)
            scored.append((w, (l1 - l2) / math.sqrt(var), y))
        scored.sort(key=lambda t: -t[1])
        out[g] = scored[:top]
    return out


def line_position_enrichment(lines: Sequence[Sequence[Word]], min_count: int = 40) -> dict[str, dict[str, float]]:
    """Ratio of a symbol's frequency in line-first / line-last words to its overall frequency."""
    first, last, every = Counter(), Counter(), Counter()
    for line in lines:
        if len(line) < 3:
            continue
        first.update(line[0])
        last.update(line[-1])
        for w in line:
            every.update(w)
    nf, nl, ne = sum(first.values()), sum(last.values()), sum(every.values())
    out = {}
    for s, c in every.items():
        if c >= min_count:
            out[s] = {
                "line_first": (first[s] / nf) / (c / ne),
                "line_last": (last[s] / nl) / (c / ne),
            }
    return out
