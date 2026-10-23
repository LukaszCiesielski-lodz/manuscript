"""A volvelle as the writing device: rings of glyph strings, one word per setting, small turns between words.

Ramon Llull (13th c.) generated terms with turning paper wheels; 15th-century books carry
volvelles for astronomy and the art of memory, and the manuscript's cosmological pages are
wheels of text. The hypothesis: the scribe had a wheel of R concentric rings, each ring K
cells, each cell a short string of glyphs (or nothing). A word is the cells under the pointer,
read outward; between words one or two rings turn by a notch or two. That predicts, with no
language at all, what the text shows: neighbouring words one glyph apart, similar lengths next
to each other, glyphs in fixed places of a word, no syntax between different words.

The wheel is unknown, so it is inferred: a population of wheels is scored on the GPU by how
much of the vocabulary it can set (coverage) and how few notches it takes to move between
consecutive words of a line (turning cost), and evolved. The best wheel then writes text
with the scribe's own turning habits (the distribution of notch steps read off the real
text); that text goes through the lab's full battery like any other generator.

Everything heavy is batched: W wheels x N word types x C compositions x R rings in one
tensor op, and W x P pairs x C x C x R for the turning cost.
"""

from __future__ import annotations

import math
import random
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

Word = tuple[str, ...]
EMPTY = 0  # segment id of the empty cell


class Backend:
    """torch on CUDA when available, else numpy (the same code path)."""

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
    def name(self):
        return "cuda" if self.torch else "numpy"

    def array(self, a, dtype=None):
        if self.torch:
            t = self.torch.as_tensor(np.asarray(a), device=self.device)
            return t.to(dtype) if dtype else t
        return np.asarray(a, dtype=dtype)

    def to_np(self, a):
        return a.cpu().numpy() if self.torch else np.asarray(a)

    def zeros(self, shape, dtype):
        return self.torch.zeros(shape, dtype=dtype, device=self.device) if self.torch else np.zeros(shape, dtype=dtype)

    def full(self, shape, value, dtype):
        return self.torch.full(shape, value, dtype=dtype, device=self.device) if self.torch else np.full(shape, value, dtype=dtype)

    @property
    def int64(self):
        return self.torch.int64 if self.torch else np.int64

    @property
    def bool_(self):
        return self.torch.bool if self.torch else np.bool_

    @property
    def float32(self):
        return self.torch.float32 if self.torch else np.float32

    def where(self, c, a, b):
        return self.torch.where(c, a, b) if self.torch else np.where(c, a, b)

    def all(self, x, axis):
        return x.all(dim=axis) if self.torch else x.all(axis=axis)

    def any(self, x, axis):
        return x.any(dim=axis) if self.torch else x.any(axis=axis)

    def sum(self, x, axis):
        return x.sum(dim=axis) if self.torch else x.sum(axis=axis)

    def amin(self, x, axis):
        return x.amin(dim=axis) if self.torch else x.min(axis=axis)

    def minimum(self, a, b):
        return self.torch.minimum(a, b) if self.torch else np.minimum(a, b)

    def arange(self, n):
        return self.torch.arange(n, device=self.device) if self.torch else np.arange(n)


# ---------- segments and compositions

@dataclass
class Segments:
    """Candidate cell contents: glyph strings of length 1..max_len seen in the words, plus the empty cell."""
    ids: dict                    # tuple -> id (empty tuple -> 0)
    strings: list                # id -> tuple
    freq: np.ndarray             # id -> occurrences as a substring

    @classmethod
    def from_words(cls, words: Sequence[Word], max_len: int = 3, min_count: int = 2, limit: int = 1500) -> "Segments":
        c = Counter()
        for w in words:
            for i in range(len(w)):
                for n in range(1, max_len + 1):
                    if i + n <= len(w):
                        c[tuple(w[i:i + n])] += 1
        keep = [s for s, n in c.most_common(limit) if n >= min_count]
        strings = [()] + keep
        return cls({s: i for i, s in enumerate(strings)}, strings, np.array([0] + [c[s] for s in keep], dtype=np.float64))


def compositions(word: Word, rings: int, seg: Segments, max_len: int = 3) -> list[tuple[int, ...]]:
    """All ways to write the word as `rings` consecutive cells (empty allowed), as segment ids."""
    out = []

    def rec(i: int, r: int, acc: list):
        if r == rings:
            if i == len(word):
                out.append(tuple(acc))
            return
        for n in range(0, max_len + 1):
            if i + n > len(word):
                break
            s = seg.ids.get(tuple(word[i:i + n]))
            if s is None:
                continue
            rec(i + n, r + 1, acc + [s])

    rec(0, 0, [])
    return out


@dataclass
class Text:
    """A text prepared for the wheel search: word types, their compositions, pairs of neighbours."""
    words: list                  # word types
    freq: np.ndarray             # [N] occurrences
    comps: np.ndarray            # [N, C, R] segment ids; -1 pads
    pairs: np.ndarray            # [P, 2] indices of consecutive word types inside lines (a sample)
    seg: Segments
    rings: int

    @classmethod
    def build(cls, lines: Sequence[Sequence[Word]], rings: int, seg: Segments | None = None, max_comps: int = 24,
              max_pairs: int = 3000, seed: int = 1) -> "Text":
        words_all = [tuple(w) for l in lines for w in l if w]
        seg = seg or Segments.from_words(words_all)
        counts = Counter(words_all)
        words = [w for w, _ in counts.most_common()]
        index = {w: i for i, w in enumerate(words)}
        comps = np.full((len(words), max_comps, rings), -1, dtype=np.int64)
        for i, w in enumerate(words):
            cs = compositions(w, rings, seg)
            # Prefer compositions with fewer empty cells and frequent segments.
            cs.sort(key=lambda c: (sum(s == EMPTY for s in c), -sum(math.log(seg.freq[s] + 1) for s in c)))
            for j, c in enumerate(cs[:max_comps]):
                comps[i, j] = c
        r = random.Random(seed)
        pairs = [(index[tuple(a)], index[tuple(b)]) for l in lines for a, b in zip(l, l[1:]) if a and b]
        r.shuffle(pairs)
        return cls(words, np.array([counts[w] for w in words], dtype=np.float64), comps,
                   np.array(pairs[:max_pairs], dtype=np.int64), seg, rings)


# ---------- wheels on the device

@dataclass
class Search:
    rings: int = 3
    cells: int = 24
    population: int = 512
    generations: int = 300
    mutations: int = 2
    turn_weight: float = 1.0     # weight of the turning cost against coverage
    seed: int = 1


class Wheels:
    """A population of wheels and their scores, all on the device."""

    def __init__(self, text: Text, s: Search, xp: Backend):
        self.text, self.s, self.xp = text, s, xp
        self.r = np.random.default_rng(s.seed)
        n_seg = len(text.seg.strings)
        self.seg_p = text.seg.freq / text.seg.freq.sum()  # draw cells in proportion to segment frequency
        self.seg_p[EMPTY] = 0.0
        self.seg_p /= self.seg_p.sum()
        # Seeded start: ring r takes the most frequent segments seen at that slot of the words' first compositions.
        slot = [Counter() for _ in range(s.rings)]
        for i, w in enumerate(text.words):
            for rr in range(s.rings):
                sid = text.comps[i, 0, rr]
                if sid > 0:
                    slot[rr][sid] += text.freq[i]
        base = np.zeros((s.rings, s.cells), dtype=np.int64)
        for rr in range(s.rings):
            top = [sid for sid, _ in slot[rr].most_common(s.cells)]
            base[rr, :len(top)] = top
        self.n_seg = n_seg
        self.rings = np.repeat(base[None], s.population, axis=0)
        for w in range(1, s.population):  # the rest start as mutated copies
            self.rings[w] = self.mutate(self.rings[w], max(1, s.cells // 4))
        self.comps = xp.array(text.comps)                  # [N, C, R]
        self.freq = xp.array(text.freq, xp.float32)        # [N]
        self.pairs = xp.array(text.pairs)                  # [P, 2]

    def mutate(self, ring: np.ndarray, n: int) -> np.ndarray:
        ring = ring.copy()
        for _ in range(n):
            rr, k = self.r.integers(self.s.rings), self.r.integers(self.s.cells)
            if self.r.random() < 0.15:
                ring[rr, k] = EMPTY
            elif self.r.random() < 0.3:  # swap two cells: changes the turning cost, not the coverage
                k2 = self.r.integers(self.s.cells)
                ring[rr, k], ring[rr, k2] = ring[rr, k2], ring[rr, k]
            else:
                ring[rr, k] = self.r.choice(self.n_seg, p=self.seg_p)
        return ring

    def tables(self, rings: np.ndarray):
        """member[W, R, S] and position[W, R, S] (first cell holding the segment; -1 if none)."""
        xp = self.xp
        W, R, K = rings.shape
        pos = np.full((W, R, self.n_seg), -1, dtype=np.int32)
        for k in range(K - 1, -1, -1):  # descending so the first occurrence wins
            np.put_along_axis(pos, rings[:, :, k][:, :, None], k, axis=2)
        pos[:, :, EMPTY] = 0  # the empty cell is "anywhere": no turn needed to read nothing
        has_empty = (rings == EMPTY).any(axis=2)
        member = pos >= 0
        member[:, :, EMPTY] = has_empty | True  # a ring with no empty cell still allows an empty read at cost 0
        return xp.array(member), xp.array(pos)

    def chunk_size(self) -> int:
        """How many wheels fit in device memory at once: the pair cost tensor is [W, P, C, C] int64, several copies."""
        P, C = self.text.pairs.shape[0], self.text.comps.shape[1]
        per_wheel = P * C * C * 4 * 6  # int32 cost tensor and its temporaries
        if self.xp.torch:
            free, _ = self.xp.torch.cuda.mem_get_info()
            budget = free * 0.5
        else:
            budget = 2 * 1024 ** 3
        return max(1, min(self.s.population, int(budget // per_wheel)))

    def score(self, rings: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(score, coverage, mean turning cost) per wheel; the population goes through the device in chunks."""
        step = self.chunk_size()
        parts = [self._score(rings[i:i + step]) for i in range(0, rings.shape[0], step)]
        return tuple(np.concatenate([p[k] for p in parts]) for k in range(3))

    def _score(self, rings: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        xp = self.xp
        member, pos = self.tables(rings)
        W = rings.shape[0]
        N, C, R = self.text.comps.shape
        comps = self.comps
        # valid[W, N, C]: every ring of the composition holds its segment.
        valid = None
        for rr in range(R):
            ids = comps[:, :, rr]                                   # [N, C]
            ok = member[:, rr][:, ids]                              # [W, N, C]
            ok = ok & (ids >= 0)[None]
            valid = ok if valid is None else (valid & ok)
        covered = xp.any(valid, 2)                                  # [W, N]
        coverage = xp.sum(covered * self.freq[None], 1) / float(self.text.freq.sum())
        # Turning cost between consecutive words: the cheapest pair of valid compositions.
        a, b = self.pairs[:, 0], self.pairs[:, 1]
        big = 10 ** 6
        cost = None
        half = self.s.cells // 2
        for rr in range(R):
            pa = pos[:, rr][:, comps[a, :, rr]]                     # [W, P, C]
            pb = pos[:, rr][:, comps[b, :, rr]]
            d = (pa[:, :, :, None] - pb[:, :, None, :])             # [W, P, C, C]
            d = xp.where(d < 0, -d, d)
            d = xp.minimum(d, self.s.cells - d)
            cost = d if cost is None else (cost + d)
        va, vb = valid[:, a], valid[:, b]                           # [W, P, C]
        allowed = va[:, :, :, None] & vb[:, :, None, :]
        cost = xp.where(allowed, cost, xp.full(cost.shape, big, cost.dtype))
        best = xp.amin(xp.amin(cost, 3), 2)                         # [W, P]
        found = best < big
        turn = xp.where(found, best, xp.full(best.shape, R * half, best.dtype)).to(xp.float32) if xp.torch \
            else xp.where(found, best, R * half).astype(np.float32)
        mean_turn = xp.sum(turn, 1) / float(self.text.pairs.shape[0]) / (R * half)  # 0..1
        sc = coverage - self.s.turn_weight * mean_turn
        out = xp.to_np(sc), xp.to_np(coverage), xp.to_np(mean_turn)
        del cost, allowed, valid, va, vb, member, pos
        return out

    def evolve(self, log=None) -> dict:
        s = self.s
        best = None
        for g in range(s.generations):
            sc, cov, turn = self.score(self.rings)
            order = np.argsort(-sc)
            if best is None or sc[order[0]] > best["score"]:
                best = {"score": float(sc[order[0]]), "coverage": float(cov[order[0]]), "turn": float(turn[order[0]]),
                        "rings": self.rings[order[0]].copy(), "generation": g}
            if log and (g % max(1, s.generations // 10) == 0 or g == s.generations - 1):
                log(f"  pokolenie {g}: najlepsze pokrycie {cov[order[0]]:.3f}, obrót {turn[order[0]]:.3f}, "
                    f"wynik {sc[order[0]]:.3f}")
            keep = self.rings[order[: max(1, s.population // 4)]]
            children = [keep[i % len(keep)] for i in range(s.population - len(keep))]
            self.rings = np.concatenate([keep, np.stack([self.mutate(c, s.mutations) for c in children])])
        return best


# ---------- the scribe who writes with the wheel

def decompose(word: Word, rings: np.ndarray, seg: Segments) -> list[tuple[int, ...]] | None:
    """Ring positions that set this word on the wheel (one per ring), or None."""
    R, K = rings.shape
    for comp in compositions(word, R, seg):
        posv = []
        for rr, sid in enumerate(comp):
            if sid == EMPTY:
                posv.append(None)
                continue
            hits = np.nonzero(rings[rr] == sid)[0]
            if len(hits) == 0:
                break
            posv.append(int(hits[0]))
        else:
            return posv
    return None


def read_wheel(rings: np.ndarray, posv: Sequence[int], seg: Segments) -> list[str]:
    out = []
    for rr, p in enumerate(posv):
        out.extend(seg.strings[rings[rr, p]])
    return out


def scribe(lines: Sequence[Sequence[Word]], rings: np.ndarray, seg: Segments, n_words: int, seed: int) -> list[list[list[str]]]:
    """Write text with the wheel, turning the rings as the scribe did between consecutive real words.

    Steps (notches per ring) between consecutive words are read off the real text wherever both
    words set on the wheel; a ring that the composition leaves empty keeps its place. Line
    starts take a random setting from the real line starts. Lines have the real lengths.
    """
    r = random.Random(seed)
    R, K = rings.shape
    steps, starts = [], []
    for l in lines:
        prev = None
        for i, w in enumerate(l):
            d = decompose(tuple(w), rings, seg)
            if d is None:
                prev = None
                continue
            if i == 0:
                starts.append(d)
            if prev is not None:
                steps.append(tuple(0 if (p is None or q is None) else (q - p) % K for p, q in zip(prev, d)))
            prev = d
    if not steps or not starts:
        return []
    lengths = [len(l) for l in lines]
    out, total = [], 0
    while total < n_words:
        start = r.choice(starts)
        posv = [p if p is not None else r.randrange(K) for p in start]
        line = []
        for _ in range(r.choice(lengths)):
            w = read_wheel(rings, posv, seg)
            if w:
                line.append(w)
            st = r.choice(steps)
            posv = [(p + d) % K for p, d in zip(posv, st)]
        if line:
            out.append(line)
            total += len(line)
    return out


def fit(lines: Sequence[Sequence[Word]], s: Search, xp: Backend, log=None) -> tuple[dict, Text]:
    text = Text.build(lines, s.rings, seed=s.seed)
    t0 = time.time()
    best = Wheels(text, s, xp).evolve(log)
    best["seconds"] = time.time() - t0
    best["cells"] = [[list(text.seg.strings[sid]) for sid in ring] for ring in best["rings"]]
    return best, text
