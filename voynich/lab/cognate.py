"""Cognate matching in the manner of NeuroDecipher (Luo, Cao & Barzilay 2019), glyphs to letters.

The lost script's word types are matched to the word types of a known language. A soft key
(softmax over letters for every glyph) turns each manuscript word into a sequence of letter
distributions; letter-bigram and skip-bigram features of those are compared by cosine with the
same features of the known words, and the whole vocabulary is matched to the whole lexicon by
entropic optimal transport (Sinkhorn), the differentiable stand-in for the paper's minimum-cost
flow. Gradient descent on the key lowers the transport cost; several random restarts run in one
batch on the GPU. The hard key (argmax) is judged by the share of word tokens on held-out folios
that it turns into a lexicon word or a word one edit away ("cognate rate"), against the same
procedure on meaningless text, and on a real enciphered text with spelling noise (key accuracy).
"""

from __future__ import annotations

import math
import random
import time
from collections import Counter
from dataclasses import dataclass
from typing import Sequence

import numpy as np

Word = tuple[str, ...]
MAX_LEN = 12


# ---------- vocabularies

@dataclass
class Vocab:
    symbols: list[str]          # glyphs or letters; the boundary symbol is appended last
    words: list[tuple[int, ...]]  # symbol ids, boundary not included
    weights: np.ndarray         # relative frequency of each word type
    strings: list[str]

    @property
    def boundary(self) -> int:
        return len(self.symbols) - 1

    @classmethod
    def from_counts(cls, counts: Counter, symbols: list[str], limit: int) -> "Vocab":
        sid = {s: i for i, s in enumerate(symbols)}
        words, weights, strings = [], [], []
        for w, n in counts.most_common():
            seq = tuple(w) if isinstance(w, tuple) else tuple(w)
            if 1 <= len(seq) <= MAX_LEN and all(s in sid for s in seq):
                words.append(tuple(sid[s] for s in seq))
                weights.append(n)
                strings.append("".join(seq))
                if len(words) >= limit:
                    break
        wt = np.array(weights, dtype=np.float64)
        return cls(list(symbols) + ["#"], words, wt / wt.sum(), strings)

    def onehot(self) -> np.ndarray:
        """[N, MAX_LEN + 2, S] one-hot rows: boundary, symbols, boundary, then zero padding."""
        S = len(self.symbols)
        out = np.zeros((len(self.words), MAX_LEN + 2, S), dtype=np.float32)
        for i, w in enumerate(self.words):
            out[i, 0, self.boundary] = 1
            for j, s in enumerate(w):
                out[i, j + 1, s] = 1
            out[i, len(w) + 1, self.boundary] = 1
        return out


def features(P, xp):
    """Letter-bigram and skip-bigram counts from positional letter distributions P [..., L, A]."""
    f2 = xp.einsum("...la,...lb->...ab", P[..., :-1, :], P[..., 1:, :])
    f3 = xp.einsum("...la,...lb->...ab", P[..., :-2, :], P[..., 2:, :])
    shape = P.shape[:-2]
    A = P.shape[-1]
    f = xp.concatenate([f2.reshape(*shape, A * A), f3.reshape(*shape, A * A)], -1) if xp is np \
        else xp.cat([f2.reshape(*shape, A * A), f3.reshape(*shape, A * A)], -1)
    norm = xp.sqrt((f * f).sum(-1, keepdims=True) + 1e-9) if xp is np else xp.sqrt((f * f).sum(-1, keepdim=True) + 1e-9)
    return f / norm


def sinkhorn(cost, a, b, eps: float, iters: int, xp):
    """Entropic optimal transport plan for cost [..., N, M] with marginals a [N], b [M]."""
    K = xp.exp(-cost / eps)
    u = xp.ones_like(a)
    for _ in range(iters):
        v = b / ((K * u[..., :, None]).sum(-2) + 1e-30)
        u = a / ((K * v[..., None, :]).sum(-1) + 1e-30)
    return u[..., :, None] * K * v[..., None, :]


# ---------- training (torch only)

@dataclass
class Fit:
    restarts: int = 16
    steps: int = 400
    lr: float = 0.1
    eps: float = 0.05
    sinkhorn_iters: int = 20
    seed: int = 1


def fit(lost: Vocab, known: Vocab, s: Fit, log=None) -> dict:
    """Soft keys from several restarts; returns the best hard key (glyph -> letter) and its cost."""
    import torch
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(s.seed)
    G, A = lost.boundary, known.boundary                      # counts without the boundary symbol
    X = torch.as_tensor(lost.onehot(), device=dev)            # [N, L, G+1]
    Fk = features(torch.as_tensor(known.onehot(), device=dev), torch)   # [M, D]
    a = torch.as_tensor(np.sqrt(lost.weights) / np.sqrt(lost.weights).sum(), device=dev, dtype=torch.float32)
    b = torch.full((len(known.words),), 1.0 / len(known.words), device=dev)
    W = torch.randn(s.restarts, G, A, device=dev, requires_grad=True)
    opt = torch.optim.Adam([W], lr=s.lr)
    t0 = time.time()
    best = None
    for step in range(s.steps):
        temp = max(0.2, 1.0 - step / s.steps)
        S = torch.softmax(W / temp, -1)                       # [R, G, A]
        Sx = torch.zeros(s.restarts, G + 1, A + 1, device=dev)
        Sx[:, :G, :A] = S
        Sx[:, G, A] = 1.0                                     # boundary maps to boundary
        P = torch.einsum("nlg,rga->rnla", X, Sx)             # [R, N, L, A+1]
        Fl = features(P, torch)                               # [R, N, D]
        cost = 1 - Fl @ Fk.T                                  # [R, N, M]
        with torch.no_grad():
            plan = sinkhorn(cost, a[None].expand(s.restarts, -1), b[None].expand(s.restarts, -1), s.eps,
                            s.sinkhorn_iters, torch)
        loss_r = (plan * cost).sum((-2, -1))                  # [R]
        loss = loss_r.sum()
        opt.zero_grad()
        loss.backward()
        opt.step()
        with torch.no_grad():
            i = int(loss_r.argmin())
            if best is None or float(loss_r[i]) < best["cost"]:
                best = {"cost": float(loss_r[i]), "W": W[i].detach().cpu().numpy().copy(), "step": step}
        if log and (step % max(1, s.steps // 5) == 0 or step == s.steps - 1):
            log(f"    krok {step}: koszt transportu {float(loss_r.min()):.4f} ({time.time() - t0:.0f} s)")
    hard = best["W"].argmax(-1)
    key = {lost.symbols[g]: known.symbols[int(hard[g])] for g in range(G)}
    return {"key": key, "cost": best["cost"], "seconds": time.time() - t0, "step": best["step"]}


# ---------- evaluation

def deletions(w: str) -> set[str]:
    return {w[:i] + w[i + 1:] for i in range(len(w))}


class EditIndex:
    """Membership within edit distance 1 of a word list (symmetric-deletion trick)."""

    def __init__(self, words: Sequence[str]):
        self.exact = set(words)
        self.by_deletion: dict[str, set[str]] = {}
        for w in self.exact:
            for d in deletions(w):
                self.by_deletion.setdefault(d, set()).add(w)

    def within_one(self, w: str) -> bool:
        if w in self.exact:
            return True
        dels = deletions(w)
        if any(d in self.exact for d in dels):                 # insertion in w
            return True
        if w in self.by_deletion:                                # deletion in w
            return True
        for d in dels:                                           # substitution
            if d in self.by_deletion:
                return True
        return False


def decode(word: Word, key: dict) -> str | None:
    try:
        return "".join(key[g] for g in word)
    except KeyError:
        return None


def cognate_rate(lines: Sequence[Sequence[Word]], key: dict, index: EditIndex) -> tuple[float, float]:
    """(share of tokens that decode to a lexicon word, share within one edit)."""
    exact = near = total = 0
    for l in lines:
        for w in l:
            d = decode(w, key)
            if d is None:
                continue
            total += 1
            if d in index.exact:
                exact += 1
                near += 1
            elif index.within_one(d):
                near += 1
    return (exact / total, near / total) if total else (0.0, 0.0)


def key_accuracy(found: dict, true: dict, lines: Sequence[Sequence[Word]]) -> float:
    c = Counter(g for l in lines for w in l for g in w)
    tot = sum(c[g] for g in true if g in found)
    return sum(c[g] for g in true if g in found and found[g] == true[g]) / tot if tot else 0.0


def noisy_encipher(words: Sequence[str], n_glyphs: int, seed: int, noise: float = 0.3, line_len: int = 9):
    """Real text under a random injective key, with a share of word types altered by one edit
    (the spelling drift between cognates). Returns lines, true key glyph -> letter."""
    r = random.Random(seed)
    freq = Counter(c for w in words for c in w)
    letters = [c for c, _ in freq.most_common(n_glyphs)]
    glyphs = [f"g{i:02d}" for i in range(len(letters))]
    r.shuffle(glyphs)
    key = dict(zip(letters, glyphs))
    altered = {}
    for w in set(words):
        if r.random() < noise and len(w) > 2:
            i = r.randrange(len(w))
            kind = r.random()
            if kind < 0.4:
                altered[w] = w[:i] + w[i + 1:]
            elif kind < 0.7:
                altered[w] = w[:i] + r.choice(letters) + w[i + 1:]
            else:
                altered[w] = w[:i] + r.choice(letters) + w[i:]
    ws = []
    for w in words:
        w2 = altered.get(w, w)
        if all(c in key for c in w2):
            ws.append(tuple(key[c] for c in w2))
    return [ws[i:i + line_len] for i in range(0, len(ws), line_len)], {v: k for k, v in key.items()}


def type_counts(lines: Sequence[Sequence[Word]]) -> Counter:
    return Counter(w for l in lines for w in l)


def glyph_inventory(lines: Sequence[Sequence[Word]], min_count: int = 20) -> list[str]:
    c = Counter(g for l in lines for w in l for g in w)
    return [g for g, n in c.most_common() if n >= min_count]
