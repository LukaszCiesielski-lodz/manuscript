"""Is a line a record with fields? Position-from-word measures with folio-held-out classifiers.

In a register every line has the same shape: field one is a name, field two a quantity, field
three a place. Then the place of a word in its line can be read from the word alone, the class
of a word (its first glyph, its last glyph, its length) carries information about its slot, and
one field predicts the others. Prose has none of this beyond the line edges; the manuscript's
edges are known (line-initial p/t gallows, line-final m/g), so the claim rests on the interior.
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter, defaultdict
from typing import Sequence

import numpy as np

Word = tuple[str, ...]
Line = list[Word]
EDGE, INTERIOR = "edge", "interior"


def slot(i: int, n: int, scheme: str) -> int | None:
    """Class of position i in a line of n words: edge = first/middle/last; interior = 2nd, 3rd, 4th, 5th+
    (lines of at least five words, edges excluded)."""
    if scheme == EDGE:
        return 0 if i == 0 else (2 if i == n - 1 else 1)
    if n < 5 or i == 0 or i == n - 1:
        return None
    return min(i, 4) - 1


def _items(lines: Sequence[Line], groups: Sequence, scheme: str):
    xs, ys, gs = [], [], []
    for line, g in zip(lines, groups):
        n = len(line)
        for i, w in enumerate(line):
            s = slot(i, n, scheme)
            if s is not None:
                xs.append("^" + ".".join(w) + "$")
                ys.append(s)
                gs.append(g)
    return xs, ys, gs


def slot_auc(lines: Sequence[Line], groups: Sequence, scheme: str = INTERIOR, seed: int = 1, folds: int = 5) -> float:
    """Macro one-vs-rest AUC of a char n-gram classifier predicting a word's slot from the word alone;
    folds by group (folio), so a word type seen in training on one page is judged on other pages."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    xs, ys, gs = _items(lines, groups, scheme)
    if len(set(ys)) < 2:
        return float("nan")
    r = random.Random(seed)
    uniq = sorted(set(gs), key=str)
    r.shuffle(uniq)
    fold_of = {g: i % folds for i, g in enumerate(uniq)}
    aucs = []
    for k in range(folds):
        tr = [i for i, g in enumerate(gs) if fold_of[g] != k]
        te = [i for i, g in enumerate(gs) if fold_of[g] == k]
        ytr, yte = [ys[i] for i in tr], [ys[i] for i in te]
        if len(set(yte)) < 2 or len(set(ytr)) < 2:
            continue
        vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 3), min_df=2)
        X = vec.fit_transform([xs[i] for i in tr])
        clf = LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced")
        clf.fit(X, ytr)
        proba = clf.predict_proba(vec.transform([xs[i] for i in te]))
        classes = list(clf.classes_)
        per = []
        for c in set(yte):
            if c in classes and 0 < sum(1 for y in yte if y == c) < len(yte):
                per.append(roc_auc_score([int(y == c) for y in yte], proba[:, classes.index(c)]))
        if per:
            aucs.append(float(np.mean(per)))
    return float(np.mean(aucs)) if aucs else float("nan")


def word_class(w: Word, kind: str) -> str:
    if kind == "first":
        return w[0] if w else ""
    if kind == "last":
        return w[-1] if w else ""
    return str(min(len(w), 8))


def mutual_information(pairs: Sequence[tuple[str, int]]) -> float:
    n = len(pairs)
    if not n:
        return 0.0
    cxy, cx, cy = Counter(pairs), Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    return sum(c / n * math.log2(c * n / (cx[x] * cy[y])) for (x, y), c in cxy.items())


def shuffle_within_lines(lines: Sequence[Line], rng: random.Random) -> list[Line]:
    out = []
    for l in lines:
        l = list(l)
        rng.shuffle(l)
        out.append(l)
    return out


def field_mi_z(lines: Sequence[Line], scheme: str = INTERIOR, shuffles: int = 200, seed: int = 1) -> dict[str, dict]:
    """Mutual information (bits) between a word's class and its slot, as z against words shuffled within lines."""
    rng = random.Random(seed)

    def mi_all(ls):
        out = {}
        for kind in ("first", "last", "length"):
            pairs = []
            for l in ls:
                n = len(l)
                for i, w in enumerate(l):
                    s = slot(i, n, scheme)
                    if s is not None:
                        pairs.append((word_class(w, kind), s))
            out[kind] = mutual_information(pairs)
        return out

    obs = mi_all(lines)
    null = [mi_all(shuffle_within_lines(lines, rng)) for _ in range(shuffles)]
    res = {}
    for kind, v in obs.items():
        draws = [d[kind] for d in null]
        sd = statistics.pstdev(draws)
        res[kind] = {"value": v, "null_mean": statistics.fmean(draws), "z": (v - statistics.fmean(draws)) / sd if sd > 1e-12 else 0.0}
    return res


def template_gain(lines: Sequence[Line], groups: Sequence, seed: int = 1, folds: int = 5, kind: str = "first") -> float:
    """Accuracy of predicting the class of an interior word from the classes of its two neighbours,
    minus the majority-class accuracy; folds by group. A record with fixed fields gives a gain."""
    xs: list[tuple[str, str, int]] = []
    ys: list[str] = []
    gs = []
    for line, g in zip(lines, groups):
        n = len(line)
        for i in range(1, n - 1):
            xs.append((word_class(line[i - 1], kind), word_class(line[i + 1], kind), min(i, 4)))
            ys.append(word_class(line[i], kind))
            gs.append(g)
    if not ys:
        return 0.0
    r = random.Random(seed)
    uniq = sorted(set(gs), key=str)
    r.shuffle(uniq)
    fold_of = {g: i % folds for i, g in enumerate(uniq)}
    gain = []
    for k in range(folds):
        tr = [i for i, g in enumerate(gs) if fold_of[g] != k]
        te = [i for i, g in enumerate(gs) if fold_of[g] == k]
        if not tr or not te:
            continue
        table: dict[tuple, Counter] = defaultdict(Counter)
        back: dict[tuple, Counter] = defaultdict(Counter)
        maj = Counter()
        for i in tr:
            table[xs[i]][ys[i]] += 1
            back[xs[i][:1]][ys[i]] += 1
            maj[ys[i]] += 1
        top = maj.most_common(1)[0][0]
        hit = base = 0
        for i in te:
            c = table.get(xs[i]) or back.get(xs[i][:1])
            pred = c.most_common(1)[0][0] if c else top
            hit += pred == ys[i]
            base += top == ys[i]
        gain.append((hit - base) / len(te))
    return float(np.mean(gain)) if gain else 0.0


def synthetic_records(n_lines: int, seed: int, n_types: int = 6, groups_of: int = 20) -> tuple[list[Line], list[str]]:
    """Records of `n_types` kinds, each a template of 5-8 fields with a sub-vocabulary of its own per field
    (field words share an initial glyph and a length range), pages of `groups_of` lines."""
    rng = random.Random(seed)
    glyphs = list("aiodeykchlrsnt")
    templates = []
    for _ in range(n_types):
        fields = []
        for _ in range(rng.randint(5, 8)):
            init = rng.choice(glyphs)
            lo = rng.randint(2, 5)
            vocab = [(init,) + tuple(rng.choice(glyphs) for _ in range(rng.randint(lo, lo + 2))) for _ in range(rng.randint(5, 40))]
            fields.append(vocab)
        templates.append(fields)
    lines, groups = [], []
    for i in range(n_lines):
        t = rng.choice(templates)
        lines.append([rng.choice(v) for v in t])
        groups.append(f"p{i // groups_of}")
    return lines, groups


def measure(lines: Sequence[Line], groups: Sequence, seed: int = 1, shuffles: int = 200) -> dict:
    """The three record measures for one corpus."""
    return {"edge_auc": slot_auc(lines, groups, EDGE, seed), "interior_auc": slot_auc(lines, groups, INTERIOR, seed),
            "mi": field_mi_z(lines, INTERIOR, shuffles, seed), "template_gain": template_gain(lines, groups, seed),
            "lines": len(lines), "words": sum(map(len, lines))}
