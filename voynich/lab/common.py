"""Shared measurements for the lab theories."""

from __future__ import annotations

import math
import random
import statistics
from typing import Sequence

from .. import corpus, eva, stats, structure

# Measures that describe a text without depending on word order.
SHAPE_METRICS = ["h2", "h3", "mean_word_len", "sd_word_len", "vocab_density", "order_consistency",
                 "positional_rigidity", "hapax_ratio", "zipf_slope", "type_token_ratio"]


def profile(words: Sequence) -> dict:
    out = stats.fingerprint(words)
    out["positional_rigidity"] = structure.positional_rigidity(words)
    out["order_consistency"] = structure.order_consistency(words)
    out["edge_mi"] = edge_mutual_information(words)
    return out


def edge_mutual_information(words: Sequence) -> float:
    """Mutual information (bits) between the last glyph of a word and the first of the next.

    Rozanova & Temerev (2026) report ~0.2 bits for Voynichese, above every prose control.
    """
    pairs = [(a[-1], b[0]) for a, b in zip(words, words[1:]) if len(a) and len(b)]
    n = len(pairs)
    pa, pb, pab = {}, {}, {}
    for a, b in pairs:
        pa[a] = pa.get(a, 0) + 1
        pb[b] = pb.get(b, 0) + 1
        pab[(a, b)] = pab.get((a, b), 0) + 1
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in pab.items())


def voynich_glyph_words(**where) -> list[list[str]]:
    return [eva.glyphs(w) for w in corpus.tokens(corpus.load_voynich(), **where)]


def language_scales(n: int, metrics: Sequence[str] = SHAPE_METRICS) -> tuple[dict, dict]:
    """Profiles of the reference languages and the spread of each metric across them."""
    profiles = {lang: profile(corpus.load_reference(lang, n)) for lang in corpus.reference_languages()}
    scales = {m: statistics.pstdev(p[m] for p in profiles.values()) or 1.0 for m in metrics}
    return profiles, scales


def distance(a: dict, b: dict, scales: dict, metrics: Sequence[str] = SHAPE_METRICS) -> float:
    """Root-mean-square difference in units of the between-language spread."""
    return math.sqrt(sum(((a[m] - b[m]) / scales[m]) ** 2 for m in metrics) / len(metrics))


def levenshtein(a: Sequence, b: Sequence) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def permutation_p(observed: float, null: Sequence[float], smaller_is_extreme: bool = True) -> float:
    hits = sum(1 for v in null if (v <= observed if smaller_is_extreme else v >= observed))
    return (hits + 1) / (len(null) + 1)


def rng(seed: int) -> random.Random:
    return random.Random(seed)
