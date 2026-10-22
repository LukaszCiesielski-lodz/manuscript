"""A self-citation text generator after Timm & Schinner (2020).

Torsten Timm and Andreas Schinner, "A possible generating algorithm of the
Voynich manuscript", Cryptologia 44(1), 2020, propose that the scribe produced
each new word by copying a word written shortly before, often from the same
place in a line above, and changing it slightly: swapping a glyph for a
similar-looking one, adding or dropping a prefix, or adding/removing an 'e'.

This is an independent, simplified re-implementation on glyph sequences. It
is a hypothesis to test against the real text, not a reconstruction of their
code: the rule set and probabilities below are this project's choices.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from typing import Sequence

from .stats import is_near

Word = list[str]

# Glyphs that look alike in the manuscript and swap freely under the hypothesis.
SIMILAR = [
    ("o", "a", "y"),
    ("ch", "sh"),
    ("k", "t"),
    ("p", "f"),
    ("cth", "ckh"),
    ("cph", "cfh"),
    ("l", "r"),
    ("d", "s"),
    ("i", "ii", "iii"),
]
_SWAP = {g: [h for h in grp if h != g] for grp in SIMILAR for g in grp}
PREFIXES = (("q", "o"), ("o",), ("y",), ("d",), ("s",), ("ch",))
_E_HOSTS = {"ch", "sh", "k", "t", "cth", "ckh", "e"}


def _swap(w: Word, rng: random.Random) -> Word:
    idx = [i for i, g in enumerate(w) if g in _SWAP]
    if not idx:
        return w
    i = rng.choice(idx)
    return w[:i] + [rng.choice(_SWAP[w[i]])] + w[i + 1:]


def _prefix(w: Word, rng: random.Random) -> Word:
    """Drop the word's prefix if it has one, else add a random prefix."""
    for p in sorted(PREFIXES, key=len, reverse=True):
        if tuple(w[:len(p)]) == p and len(w) > len(p):
            return w[len(p):]
    return list(rng.choice(PREFIXES)) + w


def _e(w: Word, rng: random.Random) -> Word:
    """Insert an 'e' after a bench/gallows glyph, or remove one (equally likely)."""
    es = [i for i, g in enumerate(w) if g == "e"]
    if es and rng.random() < 0.5:
        i = rng.choice(es)
        return w[:i] + w[i + 1:]
    hosts = [i for i, g in enumerate(w) if g in _E_HOSTS and i + 1 < len(w)]
    if not hosts:
        return w
    i = rng.choice(hosts)
    return w[:i + 1] + ["e"] + w[i + 1:]


def _splice(w: Word, other: Word, rng: random.Random) -> Word:
    if len(w) < 2 or len(other) < 2:
        return w
    return w[:rng.randint(1, len(w) - 1)] + other[rng.randint(1, len(other) - 1):]


class EditModel:
    """Single-glyph edits learned from the text itself.

    Collects every pair (earlier word -> later word) at edit distance 1 that
    sits within `window` words of each other, and records the edit with its
    neighbouring glyphs: substitute, insert or delete glyph x between left
    and right context ('^' and '$' mark the word edges). Applying the model
    picks an edit that fits the word's own contexts, weighted by how often the
    scribe made it. This replaces the hand-written similarity rules.
    """

    def __init__(self, glyph_words: Sequence[Word], window: int = 10):
        self.ops: Counter = Counter()
        ws = [tuple(w) for w in glyph_words]
        for i, b in enumerate(ws):
            for a in ws[max(0, i - window):i]:
                if is_near(a, b):
                    self.ops[self._op(a, b)] += 1
        self.pairs = sum(self.ops.values())
        self.kind_counts = Counter()
        # Index by context so applying an edit only looks at edits that fit.
        self._ins: dict[tuple, list] = {}
        self._at: dict[tuple, list] = {}
        for (kind, left, old, new, right), n in self.ops.items():
            self.kind_counts[kind] += n
            if kind == "ins":
                self._ins.setdefault((left, right), []).append((new, n))
            else:
                self._at.setdefault((left, old, right), []).append((kind, new, n))

    @staticmethod
    def _op(a: tuple, b: tuple) -> tuple:
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        left = a[i - 1] if i else "^"
        if len(a) == len(b):
            return ("sub", left, a[i], b[i], a[i + 1] if i + 1 < len(a) else "$")
        if len(b) > len(a):
            return ("ins", left, "", b[i], a[i] if i < len(a) else "$")
        return ("del", left, a[i], "", a[i + 1] if i + 1 < len(a) else "$")

    def apply(self, w: Word, rng: random.Random) -> Word:
        """Pick the edit type with the scribe's own odds, then a fitting edit of that type.

        Choosing the type first keeps word length stationary: insertions fit
        far more places than deletions, so sampling among all fitting edits
        at once makes words grow without bound.
        """
        w = list(w)
        padded = ["^"] + w + ["$"]
        by_kind: dict[str, tuple[list, list]] = {"sub": ([], []), "ins": ([], []), "del": ([], [])}
        for i in range(len(w) + 1):
            # insertion between padded[i] and padded[i + 1]
            for new, n in self._ins.get((padded[i], padded[i + 1]), ()):
                by_kind["ins"][0].append((i, new))
                by_kind["ins"][1].append(n)
            if i < len(w):
                for kind, new, n in self._at.get((padded[i], w[i], padded[i + 2]), ()):
                    by_kind[kind][0].append((i, new))
                    by_kind[kind][1].append(n)
        kinds = [k for k in by_kind if by_kind[k][0]]
        if not kinds:
            return w
        kind = rng.choices(kinds, [self.kind_counts[k] for k in kinds])[0]
        i, new = rng.choices(*by_kind[kind])[0]
        if kind == "sub":
            return w[:i] + [new] + w[i + 1:]
        if kind == "ins":
            return w[:i] + [new] + w[i:]
        return w[:i] + w[i + 1:]


class GlyphGrammar:
    """Which glyph may follow which: the set of adjacent pairs (word edges as '^', '$')
    seen at least `min_count` times in the text. Only a yes/no list; no frequencies."""

    def __init__(self, glyph_words: Sequence[Word], min_count: int = 3):
        c = Counter()
        for w in glyph_words:
            p = ["^", *w, "$"]
            c.update(zip(p, p[1:]))
        self.allowed = {pair for pair, n in c.items() if n >= min_count}

    def ok(self, w: Word) -> bool:
        p = ["^", *w, "$"]
        return all(pair in self.allowed for pair in zip(p, p[1:]))


class WordGrammar:
    """Probability of a word's shape: glyph trigram model with word edges.

    Trained on the list of distinct words (each type once), so it learns
    which shapes are well formed but not how often each word is used; word
    frequencies in generated text come from the copying process alone.
    `accept` is a Metropolis-style step on the per-glyph log-probability: a
    modified word is kept with probability min(1, exp(beta * difference)).
    """

    def __init__(self, glyph_words: Sequence[Word], k: float = 0.1, beta: float = 5.0):
        types = {tuple(w) for w in glyph_words}
        self.beta = beta
        self.tri, self.ctx = Counter(), Counter()
        alphabet = set()
        for w in types:
            p = ["^", "^", *w, "$"]
            alphabet.update(p)
            for a, b, c in zip(p, p[1:], p[2:]):
                self.tri[(a, b, c)] += 1
                self.ctx[(a, b)] += 1
        self.k, self.v = k, len(alphabet)

    def logp(self, w: Word) -> float:
        p = ["^", "^", *w, "$"]
        return sum(math.log((self.tri[(a, b, c)] + self.k) / (self.ctx[(a, b)] + self.k * self.v))
                   for a, b, c in zip(p, p[1:], p[2:]))

    def per_glyph(self, w: Word) -> float:
        """Mean log-probability per transition: comparable across word lengths."""
        return self.logp(w) / (len(w) + 1)

    def accept(self, old: Word, new: Word, rng: random.Random) -> bool:
        # Whole-word probability would favour ever shorter words, so compare per glyph.
        d = self.beta * (self.per_glyph(new) - self.per_glyph(old))
        return d >= 0 or rng.random() < math.exp(d)


def generate(
    seed_lines: Sequence[Sequence[Word]],
    n_words: int,
    line_lengths: Sequence[int],
    p_copy: float = 0.22,
    p_same_column: float = 0.55,
    p_far: float = 0.05,
    window: int = 8,
    max_len: int = 8,
    seed: int = 1,
    edits: EditModel | None = None,
    grammar: GlyphGrammar | WordGrammar | None = None,
    retries: int = 10,
) -> list[list[Word]]:
    """Generate lines of glyph-words by repeated copy-and-modify.

    p_copy        probability that a source word is copied unchanged
    p_same_column probability of taking the source from the same position in
                  one of the `window` previous lines (else any word in them)
    p_far         probability of taking the source from anywhere earlier
    max_len       longer results are discarded (the scribe's words stay short)
    line_lengths  empirical words-per-line values to sample from
    edits         learned EditModel; None uses the hand-written rules above
    grammar       if given, a modified word must pass it (GlyphGrammar.ok or
                  WordGrammar.accept); up to `retries` attempts, then the
                  source is copied unchanged
    """
    rng = random.Random(seed)
    lines: list[list[Word]] = [list(map(list, l)) for l in seed_lines]
    history = [w for l in lines for w in l]
    mutations = (_swap, _swap, _swap, _prefix, _e)
    while len(history) < n_words:
        recent = lines[-window:]
        pool = [w for l in recent for w in l]
        line: list[Word] = []
        for col in range(rng.choice(line_lengths)):
            above = [l[col] for l in recent if col < len(l)]
            r = rng.random()
            if r < p_far:
                src = rng.choice(history)
            elif above and r < p_far + p_same_column:
                src = rng.choice(above)
            else:
                src = rng.choice(pool)
            w = list(src)
            if rng.random() >= p_copy:
                for _ in range(retries if grammar else 1):
                    cand = list(src)
                    for _ in range(1 + (rng.random() < 0.35)):
                        if edits is not None:
                            cand = edits.apply(cand, rng)
                        elif rng.random() < 0.05:
                            cand = _splice(cand, rng.choice(pool), rng)
                        else:
                            cand = rng.choice(mutations)(cand, rng)
                    if (grammar is None
                            or (grammar.accept(src, cand, rng) if isinstance(grammar, WordGrammar)
                                else grammar.ok(cand))):
                        w = cand
                        break
            if 1 <= len(w) <= max_len:
                line.append(w)
        if line:
            lines.append(line)
            history.extend(line)
    return lines


class ScribeRules:
    """Rules a scribe could keep on one sheet, learned as ratios from the text.

    edge   after a word ending in glyph a, how much likelier a word starting with b is (vs. its usual rate)
    first  how much likelier a word's first glyph is when the word opens a line
    last   how much likelier a word's last glyph is when the word closes a line
    length the share of words of each length

    These are tendencies, not a cipher: a scribe filling a page with meaningless
    text could follow them by habit ("after -y start with q", "end lines in -m").
    """

    def __init__(self, lines: Sequence[Sequence[Word]]):
        pairs, first_all, first_line, last_all, last_line, lengths = Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
        for l in lines:
            ws = [w for w in l if w]
            for a, b in zip(ws, ws[1:]):
                pairs[(a[-1], b[0])] += 1
            for i, w in enumerate(ws):
                first_all[w[0]] += 1
                last_all[w[-1]] += 1
                lengths[len(w)] += 1
                if i == 0 and len(ws) >= 3:
                    first_line[w[0]] += 1
                if i == len(ws) - 1 and len(ws) >= 3:
                    last_line[w[-1]] += 1
        a_tot, b_tot = Counter(), Counter()
        for (a, b), n in pairs.items():
            a_tot[a] += n
            b_tot[b] += n
        n_pairs = sum(pairs.values())
        self.edge = {(a, b): (n / a_tot[a]) / (b_tot[b] / n_pairs) for (a, b), n in pairs.items() if n >= 5}
        nf, nl, na, nz = sum(first_line.values()), sum(last_line.values()), sum(first_all.values()), sum(last_all.values())
        self.first = {g: (first_line[g] / nf) / (c / na) for g, c in first_all.items() if c >= 20}
        self.last = {g: (last_line[g] / nl) / (c / nz) for g, c in last_all.items() if c >= 20}
        # The other side of the same habit: glyphs that belong at a line edge are rarer elsewhere
        # (without this, words copied from line ends spread 'm' and 'g' into the middle of lines).
        self.first_mid = {g: ((c - first_line[g]) / (na - nf)) / (c / na) for g, c in first_all.items() if c >= 20}
        self.last_mid = {g: ((c - last_line[g]) / (nz - nl)) / (c / nz) for g, c in last_all.items() if c >= 20}
        n_len = sum(lengths.values())
        self.length = {k: v / n_len for k, v in lengths.items()}

    def weight(self, w: Word, prev: Word | None, at_start: bool, at_end: bool) -> float:
        x = 1.0
        if prev:
            x *= self.edge.get((prev[-1], w[0]), 0.3)
        x *= self.first.get(w[0], 0.3) if at_start else self.first_mid.get(w[0], 1.0)
        x *= self.last.get(w[-1], 0.3) if at_end else self.last_mid.get(w[-1], 1.0)
        return x


def sample_word(grammar: WordGrammar, rng: random.Random, max_len: int = 10) -> Word:
    """A new word from the word-shape grammar (glyph trigrams of distinct words)."""
    nxt: dict[tuple, list] = getattr(grammar, "_next", None)
    if nxt is None:
        nxt = {}
        for (a, b, c), n in grammar.tri.items():
            nxt.setdefault((a, b), []).append((c, n))
        grammar._next = nxt
    w, ctx = [], ("^", "^")
    while len(w) <= max_len:
        opts = nxt.get(ctx)
        if not opts:
            break
        g = rng.choices([c for c, _ in opts], [n for _, n in opts])[0]
        if g == "$":
            return w
        w.append(g)
        ctx = (ctx[1], g)
    return []


def generate_v5(
    seed_lines: Sequence[Sequence[Word]],
    n_words: int,
    line_lengths: Sequence[int],
    rules: ScribeRules,
    edits: EditModel,
    grammar: WordGrammar,
    p_copy: float = 0.22,
    p_same_column: float = 0.55,
    p_far: float = 0.05,
    p_new: float = 0.1,
    p_hot: float = 0.0,
    hot_power: float = 1.5,
    p_repeat: float = 0.0,
    window: int = 8,
    candidates: int = 6,
    gamma: float = 1.0,
    length_gamma: float = 1.0,
    max_len: int = 9,
    seed: int = 1,
) -> list[list[Word]]:
    """Copy-and-modify like `generate`, but the scribe writes each word by choosing among a few candidates.

    Candidates come from the same sources as before (copied or edited words from
    recent lines, rarely from far back) plus, with probability `p_new` each, a
    fresh word from the shape grammar. The chosen one is drawn with weight
    rules.weight(...)^gamma times a length factor that steers the length
    distribution towards the scribe's habit.
    """
    rng = random.Random(seed)
    lines: list[list[Word]] = [list(map(list, l)) for l in seed_lines]
    history = [w for l in lines for w in l]
    proposed = Counter({k: 1 for k in rules.length})  # running length distribution of candidates

    counts = Counter(tuple(w) for w in history)
    hot: list = []

    def refresh_hot():
        top = counts.most_common(300)
        hot[:] = [[list(w) for w, _ in top], [c ** hot_power for _, c in top]]

    refresh_hot()

    def candidate(pool, above, prev) -> Word:
        x = rng.random()
        if x < p_new:
            return sample_word(grammar, rng, max_len)
        if x < p_new + p_hot and hot[0]:
            return list(rng.choices(hot[0], hot[1])[0])
        if prev and x < p_new + p_hot + p_repeat:
            return list(prev)
        r = rng.random()
        if r < p_far:
            src = rng.choice(history)
        elif above and r < p_far + p_same_column:
            src = rng.choice(above)
        else:
            src = rng.choice(pool)
        if rng.random() < p_copy:
            return list(src)
        for _ in range(10):
            cand = list(src)
            for _ in range(1 + (rng.random() < 0.35)):
                cand = edits.apply(cand, rng)
            if grammar.accept(src, cand, rng):
                return cand
        return list(src)

    while len(history) < n_words:
        recent = lines[-window:]
        pool = [w for l in recent for w in l]
        n = rng.choice(line_lengths)
        line: list[Word] = []
        for col in range(n):
            above = [l[col] for l in recent if col < len(l)]
            prev = line[-1] if line else None
            cands = [c for c in (candidate(pool, above, prev) for _ in range(candidates)) if 1 <= len(c) <= max_len]
            if not cands:
                continue
            total_prop = sum(proposed.values())
            weights = []
            for c in cands:
                proposed[len(c)] += 1
                lw = (rules.length.get(len(c), 1e-4) / (proposed[len(c)] / total_prop)) ** length_gamma
                weights.append(rules.weight(c, line[-1] if line else None, col == 0, col == n - 1) ** gamma * lw)
            line.append(rng.choices(cands, weights)[0])
        if line:
            lines.append(line)
            history.extend(line)
            counts.update(tuple(w) for w in line)
            if len(lines) % 10 == 0:
                refresh_hot()
    return lines
