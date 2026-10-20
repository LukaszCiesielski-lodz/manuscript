"""Attacking the text as a substitution cipher, with controls that show the attack works.

The attacker knows only a candidate language. It searches for a key (cipher
symbol -> plaintext letter; many-to-one is allowed, so homophonic ciphers are
covered) with simulated annealing.

Objective (noisy channel / minimum description length): the probability of
the *ciphertext*,

    log P(cipher) = log P_lm(plaintext) + log P(cipher | plaintext),

where P_lm is a character trigram model of the language and the channel term
charges for every homophone a letter is split into. Without the channel term
the search cheats: it maps many glyphs onto a few frequent letters and gets a
deceptively probable "plaintext" (an early version of this module produced
"inesi sini ne ninus" from the Voynich text and scored almost like real Latin).

Verdict: compare the best key's bits per symbol with what a trigram model
trained on the cipher text itself achieves (`self_entropy`). If the text is a
substitution cipher of the language, the language explains its structure and
the gap is near zero; the controls in `scripts/run_analysis.py` show that.
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Sequence

SPACE = " "
Word = Sequence[str]
LN2 = math.log(2)


def _stream(words: Sequence[Word]) -> list[str]:
    s = [SPACE]
    for w in words:
        s.extend(w)
        s.append(SPACE)
    return s


def trigram_counts(words: Sequence[Word]) -> Counter:
    s = _stream(words)
    return Counter(zip(s, s[1:], s[2:]))


class _LazyLogP(dict):
    """Trigram log-probabilities computed on first use; unknown symbols get the floor value."""

    def __init__(self, fn, alphabet: set, unknown: float):
        super().__init__()
        self.fn, self.alphabet, self.unknown = fn, alphabet, unknown

    def __missing__(self, key):
        value = self.fn(*key) if all(k in self.alphabet for k in key) else self.unknown
        self[key] = value
        return value

    def get(self, key, default=None):
        return self[key]


class TrigramModel:
    """Interpolated character trigram model over words separated by SPACE."""

    def __init__(self, words: Sequence[Word], weights=(0.6, 0.3, 0.1), floor: float = 1e-6):
        s = _stream(words)
        self.alphabet = sorted(set(s))
        uni, bi, tri = Counter(s), Counter(zip(s, s[1:])), Counter(zip(s, s[1:], s[2:]))
        ctx1 = Counter(a for a, _ in zip(s, s[1:]))
        ctx2 = Counter((a, b) for a, b, _ in zip(s, s[1:], s[2:]))
        n = len(s)
        l3, l2, l1 = weights
        self.unknown = math.log(floor)

        def logp(a: str, b: str, c: str) -> float:
            c2, cb = ctx2.get((a, b), 0), ctx1.get(b, 0)
            p3 = tri.get((a, b, c), 0) / c2 if c2 else 0.0
            p2 = bi.get((b, c), 0) / cb if cb else 0.0
            return math.log(l3 * p3 + l2 * p2 + l1 * uni[c] / n + floor)

        if len(self.alphabet) <= 64:
            self.logp: dict[tuple[str, str, str], float] = {
                (a, b, c): logp(a, b, c) for a in self.alphabet for b in self.alphabet for c in self.alphabet}
        else:  # large symbol sets (grouped glyphs): the full cube would hold millions of entries
            self.logp = _LazyLogP(logp, set(self.alphabet), self.unknown)
        self.letters = [a for a in self.alphabet if a != SPACE]

    def bits_per_symbol(self, words: Sequence[Word]) -> float:
        """Cross-entropy of a text written in this model's own alphabet."""
        counts = trigram_counts(words)
        total = sum(counts.values())
        return -sum(c * self.logp.get(t, self.unknown) for t, c in counts.items()) / total / LN2


def self_entropy(train: Sequence[Word], test: Sequence[Word]) -> float:
    """Bits per symbol of `test` under a trigram model trained on `train` (same script)."""
    return TrigramModel(train).bits_per_symbol(test)


@dataclass
class Solution:
    key: dict[str, str]
    bits: float  # bits per symbol of the cipher text under language model + key

    def decrypt(self, words: Sequence[Word]) -> list[str]:
        return ["".join(self.key.get(g, "?") for g in w) for w in words]


def solve(
    words: Sequence[Word],
    model: TrigramModel,
    restarts: int = 3,
    steps: int = 15000,
    t_start: float = 0.02,
    t_end: float = 0.0005,
    seed: int = 0,
) -> Solution:
    """Simulated annealing over many-to-one keys, maximizing log P(cipher)."""
    rng = random.Random(seed)
    counts = trigram_counts(words)
    total = sum(counts.values())
    symbols = sorted({g for w in words for g in w})
    n_sym = Counter(g for w in words for g in w)
    by_symbol: dict[str, list[tuple[tuple, int]]] = defaultdict(list)
    for t, c in counts.items():
        for g in set(t):
            if g != SPACE:
                by_symbol[g].append((t, c))
    lp = model.logp
    letters = model.letters
    channel_const = sum(n * math.log(n) for n in n_sym.values())

    def xlogx(x: int) -> float:
        return x * math.log(x) if x else 0.0

    def lm_part(entries, key) -> float:
        return sum(c * lp[(key[a], key[b], key[d])] for (a, b, d), c in entries)

    best: Solution | None = None
    for _ in range(restarts):
        key = {SPACE: SPACE}
        for g in symbols:
            key[g] = rng.choice(letters)
        load = Counter()  # occurrences of each plaintext letter under the key
        for g in symbols:
            load[key[g]] += n_sym[g]
        score = lm_part(counts.items(), key) + channel_const - sum(xlogx(v) for v in load.values())
        best_local = (score, dict(key))
        for step in range(steps):
            temp = t_start * (t_end / t_start) ** (step / steps)
            g = rng.choice(symbols)
            old, new = key[g], rng.choice(letters)
            if new == old:
                continue
            entries = by_symbol[g]
            n = n_sym[g]
            before = lm_part(entries, key) - xlogx(load[old]) - xlogx(load[new])
            key[g] = new
            after = lm_part(entries, key) - xlogx(load[old] - n) - xlogx(load[new] + n)
            delta = after - before
            if delta >= 0 or rng.random() < math.exp(delta / (temp * total)):
                score += delta
                load[old] -= n
                load[new] += n
                if score > best_local[0]:
                    best_local = (score, dict(key))
            else:
                key[g] = old
        cand = Solution(best_local[1], -best_local[0] / total / LN2)
        if best is None or cand.bits < best.bits:
            best = cand
    return best


def random_substitution(words: Sequence[Word], seed: int = 0,
                        homophones: int = 1) -> tuple[list[list[str]], dict[str, str]]:
    """Encrypt plaintext with a random key; each letter gets `homophones` cipher symbols."""
    rng = random.Random(seed)
    letters = sorted({c for w in words for c in w})
    symbols = [f"#{i}" for i in range(len(letters) * homophones)]
    rng.shuffle(symbols)
    table = {l: symbols[i * homophones:(i + 1) * homophones] for i, l in enumerate(letters)}
    truth = {s: l for l, ss in table.items() for s in ss}
    return [[rng.choice(table[c]) for c in w] for w in words], truth


def accuracy(solution: Solution, cipher_words: Sequence[Word], truth: dict[str, str]) -> float:
    """Share of cipher symbols (by occurrence) decrypted to the correct letter."""
    n = ok = 0
    for w in cipher_words:
        for g in w:
            n += 1
            ok += solution.key.get(g) == truth[g]
    return ok / n
