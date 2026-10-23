"""Could a medieval scribe have produced the manuscript's text without any meaning?

A scorecard compares a generated text with the manuscript on every measure
the project uses, at equal size (blocks of `BLOCK` words, whole lines). The
yardstick is the manuscript itself: its blocks differ from each other (other
sections, scribes and dialects), and a generator counts as matching a measure
when it falls inside that spread. A text that matches every measure and that a
classifier cannot tell from the manuscript line by line is what the "hoax"
explanation needs; the generators here are judged against that bar.
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter
from typing import Sequence

from . import stats, structure
from .lab.common import edge_mutual_information

Word = list[str]
Line = list[Word]
BLOCK = 4000

# Measures and what they capture; all are computed on one block of whole lines.
MEASURES = {
    "h1": "entropia znaków",
    "h2": "entropia warunkowa h₂",
    "h3": "entropia warunkowa h₃",
    "mean_word_len": "średnia długość słowa",
    "sd_word_len": "rozrzut długości słowa",
    "type_token_ratio": "różne słowa / wszystkie",
    "hapax_ratio": "słowa użyte raz (hapaksy)",
    "zipf_slope": "nachylenie Zipfa",
    "top10_coverage": "udział 10 najczęstszych słów",
    "adjacent_repeat": "to samo słowo zaraz po sobie",
    "adjacent_near": "sąsiednie słowa różne o 1 glif",
    "vocab_density": "gęstość słownika",
    "positional_rigidity": "sztywne miejsca glifów w słowie",
    "order_consistency": "stała kolejność glifów",
    "edge_mi": "związek końca słowa z początkiem następnego",
    "words_per_line": "słowa w wierszu",
    "line_first_p": "p w pierwszym słowie wiersza",
    "line_last_m": "m w ostatnim słowie wiersza",
    "line_last_g": "g w ostatnim słowie wiersza",
    "line_first_len": "długość pierwszego słowa wiersza / średnia",
    "len_neighbour": "korelacja długości sąsiednich słów",
    "line_mean_spread": "rozrzut średniej długości słowa między wierszami",
}


def blocks(lines: Sequence[Line], size: int = BLOCK) -> list[list[Line]]:
    out, cur, n = [], [], 0
    for l in lines:
        cur.append(l)
        n += len(l)
        if n >= size:
            out.append(cur)
            cur, n = [], 0
    return out


def measure(lines: Sequence[Line]) -> dict[str, float]:
    words = [tuple(w) for l in lines for w in l if w]
    out = {k: v for k, v in stats.fingerprint(words).items() if k in MEASURES}
    out["positional_rigidity"] = structure.positional_rigidity(words)
    out["order_consistency"] = structure.order_consistency(words)
    out["edge_mi"] = edge_mutual_information(words)
    out["words_per_line"] = len(words) / len(lines)
    enr = structure.line_position_enrichment(lines, min_count=10)
    out["line_first_p"] = enr.get("p", {}).get("line_first", 0.0)
    out["line_last_m"] = enr.get("m", {}).get("line_last", 0.0)
    out["line_last_g"] = enr.get("g", {}).get("line_last", 0.0)
    long = [l for l in lines if len(l) >= 3]
    mean_len = statistics.mean(len(w) for l in long for w in l)
    out["line_first_len"] = statistics.mean(len(l[0]) for l in long) / mean_len
    xs = [len(w) for l in lines for w in l if w]
    m, v = statistics.mean(xs), statistics.pvariance(xs)
    pairs = [(len(a), len(b)) for l in lines for a, b in zip(l, l[1:])]
    out["len_neighbour"] = sum((a - m) * (b - m) for a, b in pairs) / len(pairs) / v
    out["line_mean_spread"] = statistics.pstdev([statistics.mean(len(w) for w in l) for l in long])
    return out


def yardstick(real_lines: Sequence[Line]) -> dict[str, tuple[float, float]]:
    """Mean and spread of every measure over the manuscript's own blocks."""
    ms = [measure(b) for b in blocks(real_lines)]
    out = {}
    for k in MEASURES:
        vals = [m[k] for m in ms]
        mean = statistics.mean(vals)
        out[k] = (mean, max(statistics.stdev(vals), 0.02 * abs(mean), 1e-6))
    return out


def scorecard(gen_lines: Sequence[Line], stick: dict[str, tuple[float, float]], n_blocks: int | None = None) -> dict[str, dict]:
    """z-score of the generated text on every measure (mean over its first `n_blocks` blocks, default all)."""
    ms = [measure(b) for b in blocks(gen_lines)[:n_blocks]]
    out = {}
    for k in MEASURES:
        g = statistics.mean(m[k] for m in ms)
        mean, sd = stick[k]
        out[k] = {"generated": g, "manuscript": mean, "spread": sd, "z": (g - mean) / sd}
    return out


def misses(card: dict[str, dict], limit: float = 2.0) -> list[str]:
    return [k for k, v in card.items() if abs(v["z"]) > limit]


def section_divergence(by_section: dict[str, Sequence[Line]], size: int = BLOCK) -> float:
    """Jensen-Shannon divergence (bits) between word distributions of two sections, at equal size."""
    names = sorted(by_section)[:2]
    dists = []
    for n in names:
        ws = [tuple(w) for l in blocks(by_section[n], size)[0] for w in l]
        c = Counter(ws)
        dists.append({w: x / len(ws) for w, x in c.items()})
    p, q = dists
    m = {w: (p.get(w, 0) + q.get(w, 0)) / 2 for w in set(p) | set(q)}
    kl = lambda a: sum(v * math.log2(v / m[w]) for w, v in a.items() if v)
    return (kl(p) + kl(q)) / 2


def line_strings(lines: Sequence[Line]) -> list[str]:
    return [".".join("".join(w) for w in l) for l in lines if l]


def classifier_auc(real: Sequence[Line], fake: Sequence[Line], seed: int) -> float:
    """Can a line classifier (character n-grams) tell generated lines from real ones? 0.5 = no."""
    from .lab.theories.generative import discriminator_auc
    return discriminator_auc(line_strings(real), line_strings(fake), seed)


def split_auc(real: Sequence[Line], fake: Sequence[Line], seed: int) -> dict[str, float]:
    """Classifier AUC from cues inside words only, from cues across the gap between words only, and from all.

    Separates "the words look wrong" from "the words follow each other wrongly". For
    reference: real Voynich words shuffled within a line's section give 0.56 / 0.82.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    r = random.Random(seed)
    a, b = line_strings(real), line_strings(fake)
    n = min(len(a), len(b))
    x = r.sample(a, n) + r.sample(b, n)
    y = [0] * n + [1] * n
    idx = list(range(2 * n))
    r.shuffle(idx)
    tr, te = idx[:n], idx[n:]
    vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 4), min_df=2)
    xtr, xte = vec.fit_transform([x[i] for i in tr]), vec.transform([x[i] for i in te])
    names = vec.get_feature_names_out()
    out = {}
    for part, keep in (("inside", lambda f: "." not in f.strip(".")), ("across", lambda f: "." in f.strip(".")),
                       ("all", lambda f: True)):
        cols = [j for j, f in enumerate(names) if keep(f)]
        clf = LogisticRegression(max_iter=3000, C=2.0).fit(xtr[:, cols], [y[i] for i in tr])
        out[part] = float(roc_auc_score([y[i] for i in te], clf.predict_proba(xte[:, cols])[:, 1]))
    return out


def word_chain(train: Sequence[Line], like: Sequence[Line], order: int = 1, keep: float = 0.9, seed: int = 1) -> list[Line]:
    """Lines shaped like `like`, each word drawn given the previous `order` words of its line in `train`.

    A reference, not a hoax recipe: it can only reuse words it has seen. With probability
    1 - keep (and when the context is unseen) it backs off to a shorter context.
    """
    r = random.Random(seed)
    tabs: list[dict] = [{} for _ in range(order + 1)]
    for l in train:
        seq = ["<s>"] * order + [tuple(w) for w in l]
        for i in range(order, len(seq)):
            for k in range(order + 1):
                tabs[k].setdefault(tuple(seq[i - k:i]), Counter())[seq[i]] += 1
    out = []
    for l in like:
        ctx, line = ["<s>"] * order, []
        for _ in l:
            for k in range(order, -1, -1):
                c = tabs[k].get(tuple(ctx[len(ctx) - k:]) if k else ())
                if c and (k == 0 or r.random() < keep):
                    break
            w = r.choices(list(c), list(c.values()))[0]
            line.append(list(w))
            ctx.append(w)
        out.append(line)
    return out


def shuffle_lines(lines: Sequence[Line], seed: int) -> list[Line]:
    r = random.Random(seed)
    out = list(lines)
    r.shuffle(out)
    return out
