"""Words as numbers: the sequence of word lengths and how it moves.

A text becomes a series of integers (glyphs or letters per word). The series is
described by:

- its distribution (mean, spread, entropy);
- short-range dynamics: mutual information between neighbouring lengths and the
  autocorrelation at lags 1-5, each as an excess over the same lengths shuffled
  inside page-sized chunks (so only the order counts);
- the up/down pattern: how often a long word follows a short one;
- long-range memory: the detrended fluctuation analysis (DFA) exponent; 0.5 means
  no memory, higher means long stretches of long or short words (language tends
  to sit above 0.5: Ebeling & Neiman 1995, Montemurro & Pury 2002).
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter
from typing import Sequence

CHUNK = 300


def series(words: Sequence) -> list[int]:
    return [len(w) for w in words if len(w)]


def entropy(xs: Sequence[int]) -> float:
    c = Counter(xs)
    n = len(xs)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def lag_mi(xs: Sequence[int], lag: int = 1, cap: int = 10) -> float:
    """Mutual information (bits) between lengths `lag` apart (lengths above `cap` pooled)."""
    ys = [min(x, cap) for x in xs]
    pairs = list(zip(ys, ys[lag:]))
    n = len(pairs)
    pa, pb, pab = Counter(a for a, _ in pairs), Counter(b for _, b in pairs), Counter(pairs)
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in pab.items())


def autocorr(xs: Sequence[int], lag: int) -> float:
    m = statistics.mean(xs)
    v = sum((x - m) ** 2 for x in xs)
    return sum((xs[i] - m) * (xs[i + lag] - m) for i in range(len(xs) - lag)) / v


def up_down(xs: Sequence[int]) -> float:
    """Share of sign changes among consecutive non-zero steps (0.5: random walk, high: zigzag short-long)."""
    steps = [b - a for a, b in zip(xs, xs[1:]) if b != a]
    signs = [s > 0 for s in steps]
    return sum(a != b for a, b in zip(signs, signs[1:])) / max(1, len(signs) - 1)


def dfa(xs: Sequence[int], scales: Sequence[int] = (8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256)) -> float:
    """Detrended fluctuation analysis exponent (slope of log F(s) against log s)."""
    m = statistics.mean(xs)
    profile, acc = [], 0.0
    for x in xs:
        acc += x - m
        profile.append(acc)
    logs, logf = [], []
    for s in scales:
        f2 = []
        for start in range(0, len(profile) - s + 1, s):
            seg = profile[start:start + s]
            t = range(s)
            tm, ym = (s - 1) / 2, statistics.mean(seg)
            sxx = sum((i - tm) ** 2 for i in t)
            b = sum((i - tm) * (y - ym) for i, y in zip(t, seg)) / sxx
            f2.append(statistics.mean((y - (ym + b * (i - tm))) ** 2 for i, y in zip(t, seg)))
        if f2:
            logs.append(math.log(s))
            logf.append(0.5 * math.log(statistics.mean(f2)))
    lm, fm = statistics.mean(logs), statistics.mean(logf)
    return sum((a - lm) * (b - fm) for a, b in zip(logs, logf)) / sum((a - lm) ** 2 for a in logs)


def shuffled(xs: Sequence[int], r: random.Random, chunk: int = CHUNK) -> list[int]:
    out = []
    for i in range(0, len(xs), chunk):
        part = list(xs[i:i + chunk])
        r.shuffle(part)
        out.extend(part)
    return out


def describe(xs: Sequence[int], shuffles: int = 20, seed: int = 1) -> dict:
    """All measures, with order-dependent ones also as excess over chunk-shuffled copies (and their z)."""
    r = random.Random(seed)
    nulls = [shuffled(xs, r) for _ in range(shuffles)]
    out = {"n": len(xs), "mean": statistics.mean(xs), "sd": statistics.stdev(xs), "entropy": entropy(xs),
           "dist": {k: v / len(xs) for k, v in sorted(Counter(min(x, 12) for x in xs).items())}}
    fns = {"mi1": lambda s: lag_mi(s, 1), "mi2": lambda s: lag_mi(s, 2),
           **{f"ac{k}": (lambda s, k=k: autocorr(s, k)) for k in (1, 2, 3, 5)},
           "updown": up_down, "dfa": dfa}
    for name, fn in fns.items():
        real = fn(xs)
        null = [fn(s) for s in nulls]
        mean, sd = statistics.mean(null), statistics.stdev(null)
        out[name] = {"value": real, "null": mean, "excess": real - mean, "z": (real - mean) / sd if sd else 0.0}
    return out


def by_position(lines: Sequence[Sequence], max_pos: int = 8) -> dict[str, float]:
    """Mean word length by place in the line (first, 2nd... and last), relative to the line's mean."""
    acc: dict[str, list] = {}
    for l in lines:
        if len(l) < 4:
            continue
        m = statistics.mean(len(w) for w in l)
        for i, w in enumerate(l):
            key = "ostatnie" if i == len(l) - 1 else str(i + 1) if i < max_pos else None
            if key:
                acc.setdefault(key, []).append(len(w) / m)
    return {k: statistics.mean(v) for k, v in acc.items()}
