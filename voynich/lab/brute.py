"""Brute force over substitution keys, one triple of words at a time, against many lexicons.

The question: is there a language in which three consecutive manuscript words, under one
letter-for-glyph key, are three real words that make sense together?

Exhaustive search over keys is hopeless (a triple has 8-12 distinct glyphs: ~10^13 keys),
but the search space collapses when the lexicon is used as a filter. A word can only be
read as a lexicon word with the same repeat pattern (daiin -> ABCCD), so each of the three
words has a candidate list; a reading is a choice of one candidate per word such that the
implied key is consistent (same glyph -> same letter) and injective (different glyphs ->
different letters). The set of readings found this way is exactly the set a full key
enumeration would find. The GPU checks all candidate pairs of words 1 and 2 at once, then
all surviving pairs against every candidate of word 3.

What one triple can show is little: with thousands of candidates per word, most triples
read "sensibly" in most languages by chance (the Hebrew anagram attack taught that).
What decides is agreement: if the text is a cipher of language X, the keys found for
different triples agree on one key for the whole text, and that key turns most words of
the manuscript into lexicon words. Controls make the bar explicit:

- glyphs relabelled line by line: same triples, same readings, but no shared key (how
  much agreement chance alone gives);
- words shuffled: same words, unrelated neighbours (how much "sense" between the three
  words chance gives);
- a real text of the same language enciphered with a random key (what the method finds
  when the key exists).
"""

from __future__ import annotations

import math
import random
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

from .. import corpus, eva, lexicon

Word = tuple[str, ...]


# ---------- patterns and structures

def pattern(word: Sequence[str]) -> tuple[int, ...]:
    """Repeat structure of a word: each symbol replaced by the index of its first occurrence."""
    seen: dict = {}
    return tuple(seen.setdefault(g, len(seen)) for g in word)


def structure(triple: Sequence[Word]) -> tuple:
    """Repeat structure across the three words (what the solution set depends on) and the glyph list."""
    seen: dict = {}
    ids = tuple(tuple(seen.setdefault(g, len(seen)) for g in w) for w in triple)
    return ids, list(seen)


# ---------- lexicons on the device

class Device:
    """numpy or torch (CPU or CUDA) behind one small interface."""

    def __init__(self, prefer_gpu: bool = True):
        self.torch = None
        self.device = "cpu"
        if prefer_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    self.torch, self.device = torch, "cuda"
            except ImportError:
                pass

    @property
    def name(self) -> str:
        return "cuda" if self.torch else "numpy"

    def array(self, a: np.ndarray):
        return self.torch.as_tensor(a, device=self.device) if self.torch else a

    def nonzero(self, mask):
        return mask.nonzero(as_tuple=True) if self.torch else np.nonzero(mask)

    def to_np(self, a) -> np.ndarray:
        return a.cpu().numpy() if self.torch else np.asarray(a)

    def topk(self, values, k: int):
        """(values, indices) of the k largest entries of a 1-d array."""
        k = min(k, int(values.shape[0]))
        if self.torch:
            v, i = self.torch.topk(values, k)
            return v, i
        idx = np.argpartition(-values, k - 1)[:k]
        idx = idx[np.argsort(-values[idx])]
        return values[idx], idx


@dataclass
class Lexicon:
    name: str
    words: list[str]
    logp: np.ndarray                       # log-probability of each word
    bigrams: dict                           # (word, word) -> log-probability
    by_pattern: dict = field(default_factory=dict)   # pattern -> (indices into words)
    letters: list[str] = field(default_factory=list)
    _cache: dict = field(default_factory=dict)

    @classmethod
    def load(cls, name: str, max_candidates: int = 3000) -> "Lexicon":
        counts, bigrams = lexicon.load(name)
        total = sum(counts.values())
        words = [w for w, _ in counts.most_common()]
        logp = np.array([math.log(counts[w] / total) for w in words], dtype=np.float32)
        letters = sorted({c for w in words for c in w})
        by_pattern: dict = defaultdict(list)
        for i, w in enumerate(words):
            by_pattern[pattern(w)].append(i)
        by_pattern = {p: np.array(ix[:max_candidates]) for p, ix in by_pattern.items()}  # most frequent first
        btotal = sum(bigrams.values()) or 1
        lex = cls(name, words, logp, {k: math.log(v / btotal) for k, v in bigrams.items()}, by_pattern, letters)
        lex.letter_id = {c: i for i, c in enumerate(letters)}
        lex.unigram_floor = math.log(1 / total)
        return lex

    def candidates(self, pat: tuple, dev: Device):
        """(letter matrix n x L, log-probabilities n, word indices n) for words with this pattern, on the device."""
        key = (pat, dev.name)
        if key not in self._cache:
            ix = self.by_pattern.get(pat)
            if ix is None or len(ix) == 0:
                self._cache[key] = None
            else:
                m = np.array([[self.letter_id[c] for c in self.words[i]] for i in ix], dtype=np.int16)
                self._cache[key] = (dev.array(m), dev.array(self.logp[ix]), ix)
        return self._cache[key]

    def bigram_logp(self, a: str, b: str) -> float:
        return self.bigrams.get((a, b), self.unigram_floor * 1.5)


# ---------- the solver

@dataclass
class Settings:
    max_pairs: int = 6000        # surviving (word1, word2) pairs kept before word 3
    top: int = 20                # readings kept per triple
    plausible_bonus: float = 0.0  # unused; plausibility is reported separately


def solve_structure(ids: tuple, lex: Lexicon, dev: Device, s: Settings) -> list[tuple[tuple, float]]:
    """All consistent readings of an abstract triple, best `s.top` by frequency and bigram score.

    Returns (letters for abstract glyphs 0..k-1 as a tuple of letter ids, score).
    """
    w1, w2, w3 = ids
    c1, c2, c3 = (lex.candidates(pattern(w), dev) for w in ids)
    if c1 is None or c2 is None or c3 is None:
        return []
    m1, lp1, ix1 = c1
    m2, lp2, ix2 = c2
    m3, lp3, ix3 = c3
    rep = {}  # abstract glyph -> (word, position) of its first occurrence
    for wi, w in enumerate(ids):
        for pos, g in enumerate(w):
            rep.setdefault(g, (wi, pos))
    g1 = {g for g in w1}
    g2 = {g for g in w2}
    g3 = {g for g in w3}

    # Words 1 and 2: shared glyphs must agree, distinct glyphs must differ.
    ok = None
    for g in g2:
        pos2 = w2.index(g)
        if g in g1:
            m = m1[:, w1.index(g)][:, None] == m2[:, pos2][None, :]
        else:
            m = None
            for h in g1:
                mm = m1[:, w1.index(h)][:, None] != m2[:, pos2][None, :]
                m = mm if m is None else (m & mm)
        ok = m if ok is None else (ok & m)
    if ok is None:  # cannot happen (words are non-empty), kept for safety
        return []
    p1, p2 = dev.nonzero(ok)
    if int(p1.shape[0]) == 0:
        return []
    score12 = lp1[p1] + lp2[p2]
    if int(p1.shape[0]) > s.max_pairs:
        _, keep = dev.topk(score12, s.max_pairs)
        p1, p2, score12 = p1[keep], p2[keep], score12[keep]

    # Word 3 against every surviving pair.
    ok3 = None
    letters12 = {g: m1[p1, w1.index(g)] for g in g1}
    letters12.update({g: m2[p2, w2.index(g)] for g in g2 if g not in g1})
    for g in g3:
        pos3 = w3.index(g)
        col = m3[:, pos3][None, :]
        if g in letters12:
            m = letters12[g][:, None] == col
        else:
            m = None
            for h, v in letters12.items():
                mm = v[:, None] != col
                m = mm if m is None else (m & mm)
        ok3 = m if ok3 is None else (ok3 & m)
    q, r3 = dev.nonzero(ok3)
    if int(q.shape[0]) == 0:
        return []
    total = score12[q] + lp3[r3]
    _, keep = dev.topk(total, s.top * 10)
    q, r3 = dev.to_np(q[keep]), dev.to_np(r3[keep])
    p1n, p2n = dev.to_np(p1), dev.to_np(p2)
    out = []
    for qi, ri in zip(q, r3):
        i1, i2, i3 = ix1[p1n[qi]], ix2[p2n[qi]], ix3[ri]
        a, b, c = lex.words[i1], lex.words[i2], lex.words[i3]
        sc = float(lex.logp[i1] + lex.logp[i2] + lex.logp[i3] + lex.bigram_logp(a, b) + lex.bigram_logp(b, c))
        key = {}
        for g, (wi, pos) in rep.items():
            key[g] = (a, b, c)[wi][pos]
        out.append((tuple(key[g] for g in range(len(rep))), sc, (a, b, c)))
    out.sort(key=lambda t: -t[1])
    return out[: s.top]


def reference_solve(triple: Sequence[Word], lex_words: Sequence[str]) -> set[tuple[str, str, str]]:
    """Plain backtracking over a small word list; the test oracle for the batched solver."""
    by_pat: dict = defaultdict(list)
    for w in lex_words:
        by_pat[pattern(w)].append(w)
    found = set()

    def extend(i: int, key: dict, used: set, chosen: list):
        if i == 3:
            found.add(tuple(chosen))
            return
        for cand in by_pat.get(pattern(triple[i]), []):
            k, u, good = dict(key), set(used), True
            for g, c in zip(triple[i], cand):
                if g in k:
                    if k[g] != c:
                        good = False
                        break
                elif c in u:
                    good = False
                    break
                else:
                    k[g], u = c, u | {c}
            if good:
                extend(i + 1, k, u, chosen + [cand])

    extend(0, {}, set(), [])
    return found


# ---------- texts and controls

def paragraph_lines(tokenize: str = "glyphs") -> list[list[Word]]:
    out = []
    for l in corpus.load_voynich():
        if l.kind.startswith("P") and l.words:
            out.append([tuple(eva.glyphs(w)) if tokenize == "glyphs" else tuple(w) for w in l.words])
    return out


def triples_of(lines: Sequence[Sequence[Word]]) -> Counter:
    c = Counter()
    for l in lines:
        for i in range(len(l) - 2):
            c[(l[i], l[i + 1], l[i + 2])] += 1
    return c


def relabel_lines(lines: Sequence[Sequence[Word]], seed: int) -> list[list[Word]]:
    """A fresh random glyph permutation on every line: structure kept, shared key destroyed."""
    r = random.Random(seed)
    alphabet = sorted({g for l in lines for w in l for g in w})
    out = []
    for l in lines:
        perm = alphabet[:]
        r.shuffle(perm)
        m = dict(zip(alphabet, perm))
        out.append([tuple(m[g] for g in w) for w in l])
    return out


def shuffle_words(lines: Sequence[Sequence[Word]], seed: int) -> list[list[Word]]:
    r = random.Random(seed)
    flat = [w for l in lines for w in l]
    r.shuffle(flat)
    out, i = [], 0
    for l in lines:
        out.append(flat[i:i + len(l)])
        i += len(l)
    return out


def encipher(words: Sequence[str], n_glyphs: int, seed: int, line_len: int = 9) -> tuple[list[list[Word]], dict]:
    """Real text as lines of pseudo-glyph words under a random injective key (positive control).

    Letters beyond the `n_glyphs` most frequent get no glyph: words containing them are dropped,
    as a manuscript alphabet of ~23 glyphs could not carry a 30-letter language in full.
    """
    r = random.Random(seed)
    freq = Counter(c for w in words for c in w)
    letters = [c for c, _ in freq.most_common(n_glyphs)]
    glyphs = [f"g{i:02d}" for i in range(len(letters))]
    r.shuffle(glyphs)
    key = dict(zip(letters, glyphs))
    ws = [tuple(key[c] for c in w) for w in words if all(c in key for c in w)]
    return [ws[i:i + line_len] for i in range(0, len(ws), line_len)], {v: k for k, v in key.items()}


# ---------- one attack = one text against one lexicon

@dataclass
class Attack:
    hit_rate: float            # distinct triples with at least one reading
    plausible_rate: float      # distinct triples with a reading whose two bigrams occur in the corpus
    consistency: float         # agreement of the readings on one key, one vote per distinct triple (0..1)
    key: dict                  # the voted key, glyph -> letter (from all lines)
    dict_rate: float           # cross-validated: key voted on odd lines applied to even lines and back;
                               # share of words read as lexicon words
    top_dict_rate: float       # same for the 200 most frequent words
    sample: list               # best readings of a few frequent triples
    triples: int
    seconds: float


def _vote_key(votes: dict) -> tuple[dict, float]:
    key, agree, weight = {}, 0.0, 0.0
    for g, c in votes.items():
        tot = sum(c.values())
        letter, v = c.most_common(1)[0]
        key[g] = letter
        agree += v
        weight += tot
    return key, (agree / weight if weight else 0.0)


def attack(lines: Sequence[Sequence[Word]], lex: Lexicon, dev: Device, s: Settings, max_triples: int | None,
           seed: int) -> Attack:
    t0 = time.time()
    counts = triples_of(lines)
    chosen = {t for t, _ in (counts.most_common(max_triples) if max_triples else counts.items())}
    # Where each chosen triple occurs (odd or even line), for the cross-validated key.
    halves: dict = defaultdict(set)
    for k, l in enumerate(lines):
        for i in range(len(l) - 2):
            t = (l[i], l[i + 1], l[i + 2])
            if t in chosen:
                halves[t].add(k % 2)
    cache: dict = {}
    votes = [defaultdict(Counter), defaultdict(Counter)]  # by half
    hits = plaus = 0
    sample = []
    bigram_seen = lambda a, b: (a, b) in lex.bigrams
    for triple in chosen:
        ids, glyphs = structure(triple)
        if ids not in cache:
            cache[ids] = solve_structure(ids, lex, dev, s)
        sols = cache[ids]
        if not sols:
            continue
        hits += 1
        if any(bigram_seen(a, b) and bigram_seen(b, c) for _, _, (a, b, c) in sols):
            plaus += 1
        best = sols[0][1]
        weights = [math.exp(sc - best) for _, sc, _ in sols]
        z = sum(weights)
        for h in halves[triple]:
            for (letters, _, _), w in zip(sols, weights):
                for g, c in zip(glyphs, letters):
                    votes[h][g][c] += w / z
        if len(sample) < 6 and counts[triple] >= 3:
            sample.append({"triple": [".".join(w) for w in triple], "count": counts[triple],
                           "readings": [" ".join(words) for _, _, words in sols[:3]]})
    both = defaultdict(Counter)
    for h in (0, 1):
        for g, c in votes[h].items():
            both[g].update(c)
    key, consistency = _vote_key(both)
    lex_set = set(lex.words)
    rates, top_rates = [], []
    for h in (0, 1):
        k, _ = _vote_key(votes[h])
        other = [w for i, l in enumerate(lines) if i % 2 != h for w in l]
        decode = lambda w: "".join(k.get(g, "?") for g in w)
        rates.append(sum(decode(w) in lex_set for w in other) / max(1, len(other)))
        top = [w for w, _ in Counter(other).most_common(200)]
        top_rates.append(sum(decode(w) in lex_set for w in top) / max(1, len(top)))
    n = max(1, len(chosen))
    return Attack(hits / n, plaus / n, consistency, key, sum(rates) / 2, sum(top_rates) / 2, sample,
                  len(chosen), time.time() - t0)
