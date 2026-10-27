"""The same plant drawn twice: does the text next to it share words?

Zandbergen (voynich.nu) and Petersen note plant fragments in the pharmaceutical section that are
the same plant as, or resemble, a plant of the herbal section. If the paragraphs describe the plant,
the two pages share vocabulary beyond what two random pages of the same Currier language share.
The pairs live in data/plant_pairs.txt.
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Sequence

from . import corpus, eva

PAIRS_FILE = corpus.DATA / "plant_pairs.txt"
Word = tuple[str, ...]


@dataclass
class Page:
    folio: str
    section: str
    language: str
    words: list[Word]          # paragraph words
    labels: list[Word]         # plant fragment labels (Lf)


@dataclass(frozen=True)
class Pair:
    pharma: str
    herbal: str
    strength: str
    source: str


def load_pairs(path=PAIRS_FILE) -> list[Pair]:
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.split("#", 1)[0].strip() if raw.startswith("#") else raw.strip()
        if not raw:
            continue
        a, b, strength, source = raw.split()[:4]
        out.append(Pair(a, b, strength, source))
    return out


def load_pages(lines: Sequence[corpus.Line] | None = None) -> dict[str, Page]:
    lines = corpus.load_voynich() if lines is None else lines
    pages: dict[str, Page] = {}
    for l in lines:
        if not l.words:
            continue
        p = pages.setdefault(l.folio, Page(l.folio, l.section, l.language, [], []))
        ws = [tuple(eva.glyphs(w)) for w in l.words]
        if l.kind.startswith("P"):
            p.words.extend(ws)
        elif l.kind == "Lf":
            p.labels.extend(ws)
    return {f: p for f, p in pages.items() if p.words}


def find(pages: dict[str, Page], folio: str) -> Page | None:
    """A folio by name, allowing for the panel suffixes of foldouts (f101r -> f101r1)."""
    for cand in (folio, folio + "1", folio + "2"):
        if cand in pages:
            return pages[cand]
    return None


def idf_table(pages: dict[str, Page]) -> dict[Word, float]:
    df = Counter()
    for p in pages.values():
        df.update(set(p.words))
    n = len(pages)
    return {w: math.log(n / c) for w, c in df.items()}


def overlap(a: Sequence[Word], b: Sequence[Word], idf: dict[Word, float]) -> float:
    """Rarity-weighted share of a's word types that also occur in b."""
    ta, tb = set(a), set(b)
    tot = sum(idf.get(w, 0.0) for w in ta)
    return sum(idf.get(w, 0.0) for w in ta & tb) / tot if tot else 0.0


def label_hits(labels: Sequence[Word], text: Sequence[Word]) -> float:
    """Share of the pharma page's fragment labels found among the herbal page's words."""
    if not labels:
        return 0.0
    t = set(text)
    return sum(1 for w in labels if w in t) / len(labels)


def herbal_pool(pages: dict[str, Page], language: str) -> list[Page]:
    return [p for p in pages.values() if p.section == "herbal" and p.language == language and len(p.words) >= 20]


def evaluate(pages: dict[str, Page], pairs: Sequence[Pair], idf: dict[Word, float], shuffles: int = 1000, seed: int = 1,
             measure=overlap) -> dict:
    """Mean pair statistic against random herbal pages of the partner's language; median rank of the true partner."""
    rng = random.Random(seed)
    resolved = []
    for pr in pairs:
        a, b = find(pages, pr.pharma), find(pages, pr.herbal)
        if a and b:
            resolved.append((pr, a, b))
    if not resolved:
        return {"pairs": 0}
    obs_vals, ranks = [], []
    pools = {}
    for pr, a, b in resolved:
        pool = pools.setdefault(b.language, herbal_pool(pages, b.language))
        v = measure(a.words, b.words, idf) if measure is overlap else measure(a.labels, b.words)
        obs_vals.append(v)
        others = [measure(a.words, h.words, idf) if measure is overlap else measure(a.labels, h.words) for h in pool if h.folio != b.folio]
        ranks.append((sum(1 for o in others if o > v) + 0.5 * sum(1 for o in others if o == v)) / max(1, len(others)))
    obs = statistics.fmean(obs_vals)
    null = []
    for _ in range(shuffles):
        vals = []
        for pr, a, b in resolved:
            h = rng.choice(pools[b.language])
            vals.append(measure(a.words, h.words, idf) if measure is overlap else measure(a.labels, h.words))
        null.append(statistics.fmean(vals))
    sd = statistics.pstdev(null) if len(null) > 1 else 0.0
    return {"pairs": len(resolved), "value": obs, "null_mean": statistics.fmean(null), "z": (obs - statistics.fmean(null)) / sd if sd > 1e-12 else 0.0,
            "median_rank": statistics.median(ranks), "ranks": ranks,
            "per_pair": [(pr.pharma, pr.herbal, pr.strength, round(v, 3), round(r, 2)) for (pr, a, b), v, r in zip(resolved, obs_vals, ranks)]}


def plant(pages: dict[str, Page], pairs: Sequence[Pair], frac: float, seed: int = 1) -> dict[str, Page]:
    """Positive control: `frac` of each pharma page's words replaced by words of its herbal partner."""
    rng = random.Random(seed)
    out = {f: Page(p.folio, p.section, p.language, list(p.words), list(p.labels)) for f, p in pages.items()}
    for pr in pairs:
        a, b = find(out, pr.pharma), find(pages, pr.herbal)
        if a and b:
            a.words = [rng.choice(b.words) if rng.random() < frac else w for w in a.words]
    return out


def rewire(pages: dict[str, Page], pairs: Sequence[Pair], seed: int = 1) -> list[Pair]:
    """Negative control: every pair's herbal page replaced by a random herbal page of the same language."""
    rng = random.Random(seed)
    out = []
    for pr in pairs:
        b = find(pages, pr.herbal)
        pool = herbal_pool(pages, b.language) if b else []
        if pool:
            out.append(Pair(pr.pharma, rng.choice(pool).folio, pr.strength, "rewired"))
    return out
