"""Labels beside the drawings as a vocabulary of names, and whether the paragraphs cite them.

A register, herbal or almanac names things in its pictures and refers to those names in its
text. Here: the words written at drawings (loci L*: zodiac figures, stars, plant parts,
containers, nymphs) against the paragraph words of the same pages. Two questions, each with a
null drawn from the manuscript itself: (1) are the labels a sub-vocabulary of their own (more
hapax legomena, other initials, other lengths than paragraph words of the same sections)?
(2) do the paragraphs of a page cite its labels more than the labels of other pages of the
same section would predict?
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Sequence

from . import corpus, eva

Word = tuple[str, ...]
LABEL_KINDS = ("Lz", "Lf", "L0", "Ls", "Ln", "Lt", "Lc")   # La/Lp/Lx: 12 words in all, dropped
STATS = ("hapax", "o_initial", "q_initial", "mean_length", "top10")


@dataclass
class LabelPage:
    folio: str
    section: str
    language: str
    labels: list[Word] = field(default_factory=list)
    kinds: list[str] = field(default_factory=list)
    paragraphs: list[list[Word]] = field(default_factory=list)


def load_label_pages(lines: Sequence[corpus.Line] | None = None) -> list[LabelPage]:
    """Every folio with labels (and its paragraph lines, if any), in manuscript order."""
    lines = corpus.load_voynich() if lines is None else lines
    pages: dict[str, LabelPage] = {}
    for l in lines:
        if not (l.kind in LABEL_KINDS or l.kind.startswith("P")) or not l.words:
            continue
        page = pages.setdefault(l.folio, LabelPage(l.folio, l.section, l.language))
        words = [tuple(eva.glyphs(w)) for w in l.words]
        if l.kind in LABEL_KINDS:
            page.labels.extend(words)
            page.kinds.extend([l.kind] * len(words))
        else:
            page.paragraphs.append(words)
    return [p for p in pages.values() if p.labels]


def paragraph_pool(lines: Sequence[corpus.Line] | None = None) -> dict[str, list[Word]]:
    """Paragraph words of the whole manuscript by section (the background labels are drawn from)."""
    lines = corpus.load_voynich() if lines is None else lines
    pool: dict[str, list[Word]] = defaultdict(list)
    for l in lines:
        if l.kind.startswith("P") and l.words:
            pool[l.section].extend(tuple(eva.glyphs(w)) for w in l.words)
    return pool


def profile(words: Sequence[Word], top10: set[Word]) -> dict[str, float]:
    """Shape of a word list: hapax share, o- and q- initials, mean length, share of the top-ten paragraph words."""
    n = max(1, len(words))
    counts = Counter(words)
    return {"hapax": sum(1 for w in words if counts[w] == 1) / n,
            "o_initial": sum(1 for w in words if w and w[0] == "o") / n,
            "q_initial": sum(1 for w in words if w and w[0] == "q") / n,
            "mean_length": sum(map(len, words)) / n,
            "top10": sum(1 for w in words if w in top10) / n}


def _z(value: float, draws: Sequence[float]) -> float:
    sd = statistics.pstdev(draws) if len(draws) > 1 else 0.0
    return (value - statistics.fmean(draws)) / sd if sd > 1e-12 else (0.0 if abs(value - statistics.fmean(draws)) < 1e-12 else math.copysign(99.0, value - statistics.fmean(draws)))


def subvocabulary(pages: Sequence[LabelPage], pool: dict[str, list[Word]], draws: int = 500, seed: int = 1,
                  match_length: bool = False) -> dict:
    """Label statistics as z against `draws` samples of paragraph words matched by count and section
    (and by word length when `match_length`)."""
    rng = random.Random(seed)
    labels = [w for p in pages for w in p.labels]
    need = Counter(p.section for p in pages for _ in p.labels)
    all_par = [w for ws in pool.values() for w in ws]
    top10 = {w for w, _ in Counter(all_par).most_common(10)}
    by_len: dict[str, dict[int, list[Word]]] = {}
    for s in need:
        src = pool.get(s) or all_par
        by_len[s] = defaultdict(list)
        for w in src:
            by_len[s][len(w)].append(w)
    obs = profile(labels, top10)
    samples: list[dict[str, float]] = []
    for _ in range(draws):
        drawn: list[Word] = []
        if match_length:
            for p in pages:
                for w in p.labels:
                    bucket = by_len[p.section].get(len(w)) or by_len[p.section].get(min(by_len[p.section], key=lambda k: abs(k - len(w))))
                    drawn.append(rng.choice(bucket))
        else:
            for s, k in need.items():
                src = pool.get(s) or all_par
                drawn.extend(rng.sample(src, k) if k <= len(src) else rng.choices(src, k=k))
        samples.append(profile(drawn, top10))
    par_types = set(all_par)
    out = {k: {"value": obs[k], "null_mean": statistics.fmean(s[k] for s in samples), "z": _z(obs[k], [s[k] for s in samples])}
           for k in STATS}
    out["absent_types"] = sum(1 for w in set(labels) if w not in par_types) / max(1, len(set(labels)))
    out["n_labels"] = len(labels)
    return out


def _edit_index(words: Sequence[Word]):
    """Edit-distance-1 membership over glyph tuples (each glyph one character)."""
    from .lab.cognate import EditIndex
    alphabet = sorted({g for w in words for g in w})
    code = {g: chr(0x100 + i) for i, g in enumerate(alphabet)}
    enc = lambda w: "".join(code.get(g, "\x00") for g in w)   # noqa: E731
    return EditIndex([enc(w) for w in words]), enc


def citation_rate(pages: Sequence[LabelPage], near: bool = False) -> float:
    """Share of paragraph tokens equal to (or, with `near`, within one edit of) a label of the same page."""
    hit = tot = 0
    for p in pages:
        if not p.paragraphs:
            continue
        if near:
            index, enc = _edit_index(p.labels)
            member = lambda w: index.within_one(enc(w))     # noqa: E731
        else:
            labels = set(p.labels)
            member = lambda w: w in labels                   # noqa: E731
        for line in p.paragraphs:
            for w in line:
                tot += 1
                hit += member(w)
    return hit / max(1, tot)


def shuffle_labels(pages: Sequence[LabelPage], rng: random.Random, within_section: bool = True) -> list[LabelPage]:
    """Label sets dealt among pages (of the same section): the paragraphs keep their page, the labels move."""
    groups: dict[str, list[int]] = defaultdict(list)
    for i, p in enumerate(pages):
        groups[p.section if within_section else "*"].append(i)
    out = [LabelPage(p.folio, p.section, p.language, list(p.labels), list(p.kinds), p.paragraphs) for p in pages]
    for idx in groups.values():
        perm = idx[:]
        rng.shuffle(perm)
        for i, j in zip(idx, perm):
            out[i].labels, out[i].kinds = list(pages[j].labels), list(pages[j].kinds)
    return out


def citation(pages: Sequence[LabelPage], shuffles: int = 1000, seed: int = 1, near: bool = False) -> dict:
    """Citation rate against label sets permuted among pages of the same section."""
    rng = random.Random(seed)
    both = [p for p in pages if p.paragraphs]
    obs = citation_rate(both, near)
    null = [citation_rate(shuffle_labels(both, rng), near) for _ in range(shuffles)]
    return {"value": obs, "null_mean": statistics.fmean(null), "z": _z(obs, null), "pages": len(both),
            "tokens": sum(len(l) for p in both for l in p.paragraphs)}


def plant_citations(pages: Sequence[LabelPage], frac: float, seed: int = 1) -> list[LabelPage]:
    """Positive control: `frac` of the paragraph tokens of each page replaced by a label of that page."""
    rng = random.Random(seed)
    out = []
    for p in pages:
        pars = [[rng.choice(p.labels) if rng.random() < frac else w for w in line] for line in p.paragraphs]
        out.append(LabelPage(p.folio, p.section, p.language, list(p.labels), list(p.kinds), pars))
    return out


def uniqueness(pages: Sequence[LabelPage], shuffles: int = 500, seed: int = 1) -> dict[str, dict]:
    """Per label kind: share of labels unique on their page, against labels of that kind dealt among pages."""
    rng = random.Random(seed)
    out = {}
    for kind in LABEL_KINDS:
        per_page = [[w for w, k in zip(p.labels, p.kinds) if k == kind] for p in pages]
        per_page = [ws for ws in per_page if len(ws) >= 2]
        if sum(map(len, per_page)) < 30:
            continue

        def share(groups):
            uniq = tot = 0
            for ws in groups:
                c = Counter(ws)
                uniq += sum(1 for w in ws if c[w] == 1)
                tot += len(ws)
            return uniq / max(1, tot)

        obs = share(per_page)
        flat = [w for ws in per_page for w in ws]
        null = []
        for _ in range(shuffles):
            rng.shuffle(flat)
            i, groups = 0, []
            for ws in per_page:
                groups.append(flat[i:i + len(ws)])
                i += len(ws)
            null.append(share(groups))
        out[kind] = {"value": obs, "null_mean": statistics.fmean(null), "z": _z(obs, null), "labels": len(flat), "pages": len(per_page)}
    return out


def synthetic_label_pages(n_pages: int, seed: int, names: bool = True, cite: float = 0.0) -> tuple[list[LabelPage], dict[str, list[Word]]]:
    """Pages whose labels are (or are not) a vocabulary of their own, with optional citation in the paragraphs.

    Paragraph words come from a common pool of 400 types (Zipf-like); labels from a separate pool of
    names starting with 'o' when `names`, otherwise from the same paragraph pool.
    """
    rng = random.Random(seed)
    glyphs = list("aiodeykchlrsn")
    pool = [tuple(rng.choice(glyphs) for _ in range(rng.randint(2, 7))) for _ in range(400)]
    weights = [1 / (i + 1) for i in range(len(pool))]
    name_pool = [("o",) + tuple(rng.choice(glyphs) for _ in range(rng.randint(3, 8))) for _ in range(600)]
    pages, pool_by_section = [], {"syn": []}
    for i in range(n_pages):
        page = LabelPage(f"f{i}", "syn", "A")
        page.labels = rng.sample(name_pool, 10) if names else rng.choices(pool, weights, k=10)
        page.kinds = ["Lz"] * 10
        for _ in range(8):
            line = [rng.choice(page.labels) if rng.random() < cite else rng.choices(pool, weights)[0] for _ in range(rng.randint(5, 10))]
            page.paragraphs.append(line)
            pool_by_section["syn"].extend(line)
        pages.append(page)
    return pages, pool_by_section
