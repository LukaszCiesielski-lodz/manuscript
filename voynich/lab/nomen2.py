"""A two-key nomenclator with miscopying: the last cipher the literature leaves open (Zhang & Sheng 2026).

A nomenclator writes the K most frequent words of the plaintext whole, each as one code word,
and spells every other word letter by letter, each letter again as one code word; frequent
units get several homophones, the two Currier dialects use two keys, and the scribe miscopies
a share of the code words (one glyph changed, added or dropped). Zhang & Sheng exclude it in 14
of 16 languages; it stays open in Arabic and is undecided in Hebrew, where their solver reads
only 46% of the letters even of its own controls.

The solver works one level above a letter cipher: the "glyphs" are Voynich word types, after
rare types are merged into a frequent type one glyph away (undoing miscopying), and prefixed by
dialect (two keys); the "letters" are the plaintext units, scored by a unit bigram model of the
language plus the emission cost of the homophones. Many annealed Gibbs chains run at once, on a
GPU through cupy when there is one, else in numpy with the same code.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from typing import Sequence

Word = tuple[str, ...]
PRIVATE = 0xE000       # unit characters for whole words: one private-use character per code word


# ---------- plaintext units

def top_words(words: Sequence[str], k: int) -> list[str]:
    return [w for w, _ in Counter(words).most_common(k)]


def unit_string(words: Sequence[str], top: Sequence[str]) -> str:
    """A run of words as a string of units: a frequent word is one private character, others are spelled."""
    idx = {w: i for i, w in enumerate(top)}
    return "".join(chr(PRIVATE + idx[w]) if w in idx else w for w in words)


def plaintext_lines(words: Sequence[str], top: Sequence[str], line_len: int = 9) -> list[str]:
    return [unit_string(words[i:i + line_len], top) for i in range(0, len(words), line_len)]


# ---------- enciphering (controls)

def _miscopy(w: Word, alphabet: Sequence[str], r: random.Random) -> Word:
    w = list(w)
    op = r.random()
    if op < 0.5 and w:
        w[r.randrange(len(w))] = r.choice(alphabet)
    elif op < 0.75:
        w.insert(r.randrange(len(w) + 1), r.choice(alphabet))
    elif len(w) > 1:
        del w[r.randrange(len(w))]
    return tuple(w)


def encipher(unit_lines: Sequence[str], code_pool: Sequence[Word], seed: int, keys: int = 2,
             miscopy: float = 0.0) -> tuple[list[list[Word]], list[list[str]], list[str]]:
    """Unit lines under a nomenclator: returns cipher lines (one code word per unit), the true unit of
    every token, and the dialect of every line (the first half of the lines uses key A, the rest key B)."""
    r = random.Random(seed)
    freq = Counter(u for l in unit_lines for u in l)
    units = [u for u, _ in freq.most_common()]
    pool = list(code_pool)
    r.shuffle(pool)
    per_key = len(pool) // keys
    alphabet = sorted({g for w in code_pool for g in w})
    books = []
    for k in range(keys):
        codes = pool[k * per_key:(k + 1) * per_key]
        total = sum(freq.values())
        n = {u: max(1, round(len(codes) * freq[u] / total)) for u in units}
        while sum(n.values()) > len(codes):
            u = max(n, key=n.get)
            if n[u] == 1:
                break
            n[u] -= 1
        book, i = {}, 0
        for u in units:
            book[u] = codes[i:i + n[u]] or [codes[i % len(codes)]]
            i += n[u]
        books.append(book)
    lines, truth, dialects = [], [], []
    for li, l in enumerate(unit_lines):
        k = min(keys - 1, li * keys // max(1, len(unit_lines)))
        toks = []
        for u in l:
            w = r.choice(books[k][u])
            if miscopy and r.random() < miscopy:
                w = _miscopy(w, alphabet, r)
            toks.append(w)
        lines.append(toks)
        truth.append(list(l))
        dialects.append("AB"[k])
    return lines, truth, dialects


# ---------- undoing miscopying: merge rare types into a frequent type one glyph away

def _deletions(w: Word) -> list[tuple[int, Word]]:
    return [(i, w[:i] + w[i + 1:]) for i in range(len(w))]


def cluster_types(lines: Sequence[Sequence[Word]], min_center: int = 4) -> dict[Word, Word]:
    """Type -> its centre: itself if frequent, else the most frequent type at edit distance one, else itself."""
    c = Counter(w for l in lines for w in l)
    centers = {w for w, n in c.items() if n >= min_center}
    by_del: dict[tuple[int, Word], list[Word]] = defaultdict(list)     # substitution: same deletion at same place
    by_any_del: dict[Word, list[Word]] = defaultdict(list)              # insertion in the copy: copy minus one = centre
    for w in centers:
        for d in _deletions(w):
            by_del[d].append(w)
            by_any_del[d[1]].append(w)
    out = {}
    for w in c:
        if w in centers:
            out[w] = w
            continue
        cands = set()
        for d in _deletions(w):
            cands.update(by_del.get(d, ()))           # one glyph substituted
            if d[1] in centers:
                cands.add(d[1])                        # one glyph added by the scribe
        cands.update(by_any_del.get(w, ()))            # one glyph dropped by the scribe
        out[w] = max(cands, key=lambda x: (c[x], x)) if cands else w
    return out


def symbol_lines(lines: Sequence[Sequence[Word]], dialects: Sequence[str], min_center: int = 4) -> list[list[str]]:
    """Cipher lines as sequences of symbols 'dialect|centre' (two keys)."""
    cmap = cluster_types(lines, min_center)
    return [[f"{d}|{'.'.join(cmap[w])}" for w in l] for l, d in zip(lines, dialects)]


def as_glyph_lines(sym_lines: Sequence[Sequence[str]]) -> list[list[Word]]:
    """For GlyphText: each line is one 'word' whose 'glyphs' are the symbols, so the gap marks only line edges."""
    return [[tuple(l)] for l in sym_lines if l]


def inventory(sym_lines: Sequence[Sequence[str]], min_count: int = 3) -> list[str]:
    c = Counter(s for l in sym_lines for s in l)
    return [s for s, n in c.most_common() if n >= min_count]


def token_accuracy(key: dict[str, str], sym_lines: Sequence[Sequence[str]], truth: Sequence[Sequence[str]]) -> float:
    """Share of tokens with a keyed symbol decoded to their true unit."""
    hit = tot = 0
    for ls, lt in zip(sym_lines, truth):
        for s, u in zip(ls, lt):
            if s in key:
                tot += 1
                hit += key[s] == u
    return hit / tot if tot else 0.0


# ---------- the hapax test: where do the rare word forms come from?

def hapax_locality(pages: Sequence[Sequence[Sequence[Word]]], window: int = 5, shuffles: int = 200, seed: int = 0) -> dict:
    """For every hapax with a more frequent neighbour one glyph away: is that neighbour in the preceding lines of
    the same page more often than in the same number of lines of another page? Copying from the neighbourhood
    (self-citation) says yes; miscopied code words of a nomenclator say no more than the neighbour's frequency."""
    r = random.Random(seed)
    lines_all = [l for p in pages for l in p]
    c = Counter(w for l in lines_all for w in l)
    cmap = cluster_types(lines_all, min_center=2)
    events = []      # (page index, line index, neighbour)
    for pi, p in enumerate(pages):
        for li, l in enumerate(p):
            for w in l:
                if c[w] == 1 and cmap.get(w, w) != w:
                    events.append((pi, li, cmap[w]))

    def hit_rate(assign) -> float:
        hits = 0
        for (pi, li, n), qi in zip(events, assign):
            p = pages[qi]
            lo = max(0, li - window) if qi == pi else max(0, min(len(p), li) - window)
            hi = li if qi == pi else min(len(p), li)
            ctx = p[lo:hi] if hi > lo else p[:window]
            hits += any(n in l for l in ctx)
        return hits / max(1, len(events))

    obs = hit_rate([pi for pi, _, _ in events])
    null = []
    for _ in range(shuffles):
        null.append(hit_rate([r.randrange(len(pages)) for _ in events]))
    mean = sum(null) / len(null)
    sd = (sum((x - mean) ** 2 for x in null) / len(null)) ** 0.5
    return {"hapaxes_with_neighbour": len(events), "hapax_share": sum(1 for w, n in c.items() if n == 1) / max(1, len(c)),
            "local_rate": obs, "other_page_rate": mean, "ratio": obs / mean if mean else float("inf"),
            "z": (obs - mean) / sd if sd > 1e-12 else 0.0}


# ---------- the solver: annealed Gibbs sampling of symbol -> unit under a unit bigram model

import math as _math

import numpy as _np


class UnitBigram:
    """Add-beta interpolated bigram over plaintext units with a line boundary unit (index 0)."""

    def __init__(self, lines: Sequence[str], beta: float = 0.5):
        units = sorted({u for l in lines for u in l})
        self.units = ["\n"] + units
        self.index = {u: i for i, u in enumerate(self.units)}
        A = len(self.units)
        uni = _np.ones(A)
        big = _np.zeros((A, A))
        for l in lines:
            seq = [0] + [self.index[u] for u in l] + [0]
            for a, b in zip(seq, seq[1:]):
                big[a, b] += 1
                uni[b] += 1
        uni /= uni.sum()
        self.logp = _np.log((big + beta * uni[None]) / (big.sum(1, keepdims=True) + beta))

    def bits(self, lines: Sequence[str]) -> float:
        tot = n = 0.0
        for l in lines:
            seq = [0] + [self.index[u] for u in l if u in self.index] + [0]
            for a, b in zip(seq, seq[1:]):
                tot += self.logp[a, b]
                n += 1
        return -tot / max(1.0, n) / _math.log(2)


def _encode(sym_lines: Sequence[Sequence[str]], sid: dict[str, int]) -> list[_np.ndarray]:
    """Lines as arrays of symbol ids, unknown symbols dropped (their neighbours join, as in the climber)."""
    return [_np.array([sid[s] for s in l if s in sid], dtype=_np.int64) for l in sym_lines]


def array_module(prefer_gpu: bool = True):
    """cupy when a CUDA device is there (Colab ships cupy), else numpy: the solver code is the same for both."""
    if prefer_gpu:
        try:
            import cupy
            if cupy.cuda.runtime.getDeviceCount() > 0:
                return cupy
        except Exception:
            pass
    return _np


def _host(a):
    return a.get() if hasattr(a, "get") else _np.asarray(a)


def neighbour_counts(xp, key, nb, A: int):
    """For R chains: counts[r, u] = how many occurrences have neighbour unit u under chain r's key.
    `key` is R x (S+1) (column S = line boundary, always unit 0), `nb` the neighbour symbol ids."""
    R = key.shape[0]
    units = key[:, nb]                                            # R x n
    flat = (units + A * xp.arange(R)[:, None]).ravel()
    return xp.bincount(flat, minlength=R * A).reshape(R, A).astype(xp.float64)


def _xlogx(xp, x):
    return xp.where(x > 0, x * xp.log(xp.maximum(x, 1e-300)), 0.0)


def full_loglik(xp, key, a, b, freq, lp, A: int):
    """Log-likelihood of every chain: unit bigram over all transitions (a -> b, boundary = column S) plus the
    emission term with maximum-likelihood P(symbol | unit) = c_s / n_u, i.e. sum c_s ln c_s - sum n_u ln n_u.
    Without the emission term a key that merges many symbols into a few frequent letters scores better than
    the true key (seen on Latin controls: 3.36 against 4.19 bits per unit)."""
    R, S1 = key.shape
    lm = lp[key[:, a], key[:, b]].sum(1)
    load = xp.zeros((R, A))
    for r in range(R):
        load[r] = xp.bincount(key[r, :-1], weights=freq, minlength=A)
    return lm + _xlogx(xp, freq).sum() - _xlogx(xp, load).sum(1), lm


def gibbs_solve(sym_lines: Sequence[Sequence[str]], symbols: Sequence[str], lm: UnitBigram, sweeps: int = 60,
                chains: int = 8, seed: int = 1, t0: float = 1.5, log=None, prefer_gpu: bool = True) -> dict:
    """Key symbol -> unit maximising the generative likelihood of the lines under the unit bigram model.

    `chains` keys are sampled at once (rows of an R x S array; cupy on a GPU, numpy otherwise). Each sweep
    visits every symbol and, in every chain, draws its unit by Gumbel-max from score / T, where
    score(u) = sum over the symbol's occurrences of ln P(u | previous unit) + ln P(next unit | u)
               - [(n_u + c) ln(n_u + c) - n_u ln n_u]   (emission cost of joining unit u, c = count of the symbol)
    and T falls from t0 to ~0. The chain with the best full log-likelihood wins (many random restarts in
    parallel, as in Berg-Kirkpatrick & Klein 2013)."""
    xp = array_module(prefer_gpu)
    sid = {s: i for i, s in enumerate(symbols)}
    lines = [l for l in _encode(sym_lines, sid) if len(l)]
    S, A, R = len(symbols), len(lm.units), max(1, chains)
    prev_l, next_l, a_l, b_l = [], [], [], []
    for l in lines:
        ext = _np.concatenate([[S], l, [S]])
        prev_l.append(ext[:-2])
        next_l.append(ext[2:])
        a_l.append(ext[:-1])
        b_l.append(ext[1:])
    toks = _np.concatenate(lines)
    prv, nxt = _np.concatenate(prev_l), _np.concatenate(next_l)
    order = _np.argsort(toks, kind="stable")
    bounds = _np.searchsorted(toks[order], _np.arange(S + 1))
    occ_prev = [xp.asarray(prv[order[bounds[s]:bounds[s + 1]]]) for s in range(S)]
    occ_next = [xp.asarray(nxt[order[bounds[s]:bounds[s + 1]]]) for s in range(S)]
    freq_h = _np.bincount(toks, minlength=S).astype(float)
    freq = xp.asarray(freq_h)
    lp = xp.asarray(lm.logp)
    lpT = lp.T.copy()
    rng = _np.random.default_rng(seed)
    key = xp.asarray(_np.concatenate([rng.integers(1, A, size=(R, S)), _np.zeros((R, 1), dtype=_np.int64)], 1))
    load = xp.zeros((R, A))
    for r in range(R):
        load[r] = xp.bincount(key[r, :S], weights=freq, minlength=A)
    rows = xp.arange(R)
    g = xp.random.default_rng(seed) if hasattr(xp.random, "default_rng") else None
    for sw in range(sweeps):
        T = t0 * (1 - sw / max(1, sweeps - 1)) + 1e-3
        for s in rng.permutation(S):
            c = freq_h[s]
            if c == 0:
                continue
            cur = key[:, s]
            load[rows, cur] -= c
            score = neighbour_counts(xp, key, occ_prev[s], A) @ lp + neighbour_counts(xp, key, occ_next[s], A) @ lpT
            score -= _xlogx(xp, load + c) - _xlogx(xp, load)
            score[:, 0] = -xp.inf                                   # a symbol is never the line boundary
            u = g.random((R, A)) if g is not None else xp.random.random((R, A))
            gumbel = -xp.log(-xp.log(xp.clip(u, 1e-12, 1 - 1e-12)))
            new = xp.argmax(score / T + gumbel, axis=1)
            key[:, s] = new
            load[rows, new] += c
        if log and (sw + 1) % max(1, sweeps // 4) == 0:
            ll, _ = full_loglik(xp, key, xp.asarray(_np.concatenate(a_l)), xp.asarray(_np.concatenate(b_l)), freq, lp, A)
            log(f"    przebieg {sw + 1}/{sweeps}: najlepszy łańcuch {float(_host(ll).max()):.0f} nat")
    a, b = xp.asarray(_np.concatenate(a_l)), xp.asarray(_np.concatenate(b_l))
    ll, lmll = full_loglik(xp, key, a, b, freq, lp, A)
    ll_h, lm_h, key_h = _host(ll), _host(lmll), _host(key)
    best = int(ll_h.argmax())
    n = len(a_l and _np.concatenate(a_l))
    agree = float((key_h[:, :S] == key_h[best, :S]).mean()) if R > 1 else 1.0
    return {"key": {symbols[i]: lm.units[int(key_h[best, i])] for i in range(S)},
            "fit_bits": -float(lm_h[best]) / max(1, n) / _math.log(2), "loglik": float(ll_h[best]),
            "chain_agreement": agree, "backend": xp.__name__}


def heldout_bits(key: dict[str, str], sym_lines: Sequence[Sequence[str]], lm: UnitBigram) -> float:
    """Bits per unit of the decoded held-out lines (symbols outside the key dropped)."""
    return lm.bits(["".join(key[s] for s in l if s in key) for l in sym_lines])


def attack(lines: Sequence[Sequence[Word]], dialects: Sequence[str], lm: UnitBigram, sweeps: int, chains: int,
           seed: int, min_count: int = 3, log=None, truth: Sequence[Sequence[str]] | None = None,
           prefer_gpu: bool = True) -> dict:
    """Cluster, key on odd lines, judge on even lines; with `truth`, also the token accuracy of the key."""
    sym = symbol_lines(lines, dialects)
    odd, even = sym[0::2], sym[1::2]
    inv = inventory(odd, min_count)
    sol = gibbs_solve(odd, inv, lm, sweeps, chains, seed, log=log, prefer_gpu=prefer_gpu)
    out = {"fit_bits": sol["fit_bits"], "held_out_bits": heldout_bits(sol["key"], even, lm), "symbols": len(inv),
           "coverage": sum(1 for l in sym for s in l if s in sol["key"]) / max(1, sum(len(l) for l in sym)),
           "chain_agreement": sol["chain_agreement"]}
    if truth is not None:
        out["accuracy"] = token_accuracy(sol["key"], sym, truth)
    out["sample"] = ["".join(sol["key"].get(s, "·") for s in l) for l in even[:3]]
    out["key"] = sol["key"]
    out["backend"] = sol["backend"]
    return out
