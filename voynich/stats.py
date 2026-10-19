"""Statistical fingerprints of a text given as a list of words.

Every function takes words as sequences of symbols (str for ordinary text, or
lists of glyphs for Voynich via eva.glyphs), so the same code measures the
manuscript and natural-language reference texts.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Sequence

Word = Sequence[str]
SPACE = " "


def _entropy(counts: Counter) -> float:
    n = sum(counts.values())
    return -sum(c / n * math.log2(c / n) for c in counts.values() if c)


def symbol_stream(words: Sequence[Word]) -> list[str]:
    """Symbols of all words with a space symbol between consecutive words."""
    out: list[str] = []
    for w in words:
        out.extend(w)
        out.append(SPACE)
    return out


def char_entropies(words: Sequence[Word]) -> dict[str, float]:
    """h0 = log2(alphabet), h1 = unigram entropy, h2 = H(X_n | X_n-1), h3 = H(X_n | X_n-2 X_n-1)."""
    s = symbol_stream(words)
    uni = Counter(s)
    bi = Counter(zip(s, s[1:]))
    tri = Counter(zip(s, s[1:], s[2:]))
    return {
        "alphabet": len(uni),
        "h0": math.log2(len(uni)),
        "h1": _entropy(uni),
        "h2": _entropy(bi) - _entropy(Counter(a for a, _ in bi.elements())),
        "h3": _entropy(tri) - _entropy(Counter((a, b) for a, b, _ in tri.elements())),
    }


def zipf_slope(words: Sequence[Word], max_rank: int = 1000) -> float:
    """Least-squares slope of log(frequency) vs log(rank); natural language is near -1."""
    freqs = [c for _, c in Counter(map(tuple, words)).most_common(max_rank)]
    xs = [math.log(r) for r in range(1, len(freqs) + 1)]
    ys = [math.log(f) for f in freqs]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def _neighbours_1(word: tuple, alphabet: set) -> set:
    """All sequences at Levenshtein distance exactly 1 from `word`."""
    out = set()
    for i in range(len(word) + 1):
        for a in alphabet:
            out.add(word[:i] + (a,) + word[i:])
        if i < len(word):
            out.add(word[:i] + word[i + 1:])
            for a in alphabet:
                if a != word[i]:
                    out.add(word[:i] + (a,) + word[i + 1:])
    return out


def is_near(a: tuple, b: tuple) -> bool:
    """True when Levenshtein(a, b) == 1."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    if len(a) == len(b):
        return a[i + 1:] == b[i + 1:]
    return a[i:] == b[i + 1:]


def vocabulary_density(words: Sequence[Word], top: int = 2000) -> float:
    """Share of the `top` most frequent types that have another such type at edit distance 1."""
    types = [w for w, _ in Counter(map(tuple, words)).most_common(top)]
    vocab = set(types)
    alphabet = {s for w in types for s in w}
    return sum(1 for w in types if _neighbours_1(w, alphabet) & vocab) / len(types)


def fingerprint(words: Sequence[Word]) -> dict[str, float]:
    """A compact set of measures; compare texts only at equal token counts."""
    ws = [tuple(w) for w in words]
    counts = Counter(ws)
    lengths = [len(w) for w in ws]
    mean_len = sum(lengths) / len(lengths)
    pairs = list(zip(ws, ws[1:]))
    out = {
        "tokens": len(ws),
        "types": len(counts),
        "type_token_ratio": len(counts) / len(ws),
        "hapax_ratio": sum(1 for c in counts.values() if c == 1) / len(counts),
        "mean_word_len": mean_len,
        "sd_word_len": math.sqrt(sum((x - mean_len) ** 2 for x in lengths) / len(lengths)),
        "top10_coverage": sum(c for _, c in counts.most_common(10)) / len(ws),
        "zipf_slope": zipf_slope(ws),
        "adjacent_repeat": sum(a == b for a, b in pairs) / len(pairs),
        "adjacent_near": sum(is_near(a, b) for a, b in pairs) / len(pairs),
        "vocab_density": vocabulary_density(ws),
    }
    out.update(char_entropies(ws))
    return out


def length_distribution(words: Sequence[Word], max_len: int = 15) -> list[float]:
    c = Counter(min(len(w), max_len) for w in words)
    n = len(words)
    return [c.get(i, 0) / n for i in range(1, max_len + 1)]


def rank_frequency(words: Sequence[Word], max_rank: int = 2000) -> list[int]:
    return [c for _, c in Counter(map(tuple, words)).most_common(max_rank)]
