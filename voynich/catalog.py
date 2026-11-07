"""Zandbergen's page catalogue joined with the text: what the drawings have to do with the words.

data/catalog/pages.json (scripts/fetch_catalog.py) gives every page its section, the drawing
description, the Gheuens/Rapaport drawing-style features of herbal pages (alpha and beta codes),
the Currier language, the LFD hand and cross-references between herbal pages and pharmaceutical
fragments. Three cross-section questions:

1. Drawing style against scribe: do beta-style drawings sit on Currier-B pages (Gheuens and
   Rapaport's claim), and on which hands?
2. Drawing style against text content: do pages that share a drawing feature share vocabulary
   beyond what pages of the same language and hand share anyway? Null: random page groups with
   the same language-and-hand make-up. If drawings and words were about the same plant, pages
   drawn alike should read alike.
3. Section ledger: pages, text items, labels, languages and hands per section, and the drawn
   object counts the catalogue states (nymphs, stars).
"""

from __future__ import annotations

import json
import math
import random
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Sequence

from . import corpus, plantpairs

CATALOG_FILE = corpus.DATA / "catalog" / "pages.json"
Word = tuple[str, ...]


@dataclass
class Entry:
    folio: str
    section: str
    features: list[str]
    currier: str | None
    hand: str | None
    loci: int | None
    text_items: list[str]
    similar: list[dict]
    illustration: str
    words: list[Word] = field(default_factory=list)   # paragraph words of the page
    labels: int = 0                                   # label loci (L*) on the page

    @property
    def stratum(self) -> tuple[str, str]:
        return (self.currier or "-", (self.hand or "?").split()[0])

    @property
    def alpha(self) -> int:
        return sum(1 for f in self.features if f.lstrip("!").startswith("α"))

    @property
    def beta(self) -> int:
        return sum(1 for f in self.features if f.lstrip("!").startswith("β"))


def load(path=CATALOG_FILE, lines: Sequence[corpus.Line] | None = None) -> dict[str, Entry]:
    """Catalogue entries by folio, with the page's paragraph words and label count from the transliteration."""
    raw = json.loads(path.read_text(encoding="utf-8"))["pages"]
    lines = corpus.load_voynich() if lines is None else lines
    pages = plantpairs.load_pages(lines)
    labels = Counter(l.folio for l in lines if l.kind.startswith("L") and l.words)
    out = {}
    for p in raw:
        e = Entry(p["folio"], p["section"], list(p["features"]), p.get("currier"), p.get("hand"), p.get("loci"),
                  list(p.get("text_items") or []), list(p.get("similar_fragments") or []), p.get("illustration", ""))
        page = plantpairs.find(pages, p["folio"])
        if page is not None:
            e.words = list(page.words)
        e.labels = labels.get(p["folio"], 0)
        out[p["folio"]] = e
    return out


def feature_name(code: str) -> str:
    return code.lstrip("!")


# ---------- 1. drawing style against language and hand

def auc(scores_pos: Sequence[float], scores_neg: Sequence[float]) -> float:
    if not scores_pos or not scores_neg:
        return float("nan")
    wins = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a in scores_pos for b in scores_neg)
    return wins / (len(scores_pos) * len(scores_neg))


def style_vs_label(entries: Sequence[Entry], label: str, shuffles: int, seed: int) -> dict:
    """AUC of the beta-minus-alpha score for pages with `label` ('B' for Currier B, or a hand) against the rest."""
    r = random.Random(seed)
    scored = [(e.beta - e.alpha, (e.currier == label) if label in ("A", "B") else ((e.hand or "").split()[0] == label))
              for e in entries if e.features]
    obs = auc([s for s, y in scored if y], [s for s, y in scored if not y])
    ys = [y for _, y in scored]
    null = []
    for _ in range(shuffles):
        r.shuffle(ys)
        null.append(auc([s for (s, _), y in zip(scored, ys) if y], [s for (s, _), y in zip(scored, ys) if not y]))
    sd = statistics.pstdev(null) if len(null) > 1 else 0.0
    return {"label": label, "n": len(scored), "positives": sum(1 for _, y in scored if y), "auc": obs,
            "null_mean": statistics.fmean(null) if null else float("nan"), "z": (obs - statistics.fmean(null)) / sd if sd > 1e-12 else 0.0}


# ---------- 2. drawing features against vocabulary, language and hand held fixed

def _idf_pages(entries: Sequence[Entry]) -> tuple[dict[str, dict[Word, float]], dict[str, float]]:
    df = Counter()
    for e in entries:
        for w in set(e.words):
            df[w] += 1
    n = len(entries)
    idf = {w: math.log((n + 1) / (c + 1)) + 1 for w, c in df.items()}
    weights = {e.folio: {w: idf[w] for w in set(e.words)} for e in entries}
    totals = {f: sum(ws.values()) for f, ws in weights.items()}
    return weights, totals


def group_overlap(folios: Sequence[str], weights: dict[str, dict[Word, float]], totals: dict[str, float]) -> float:
    """Mean over pairs of the share of a page's rarity-weighted vocabulary found on the other page (both directions)."""
    vals = []
    for i in range(len(folios)):
        for j in range(i + 1, len(folios)):
            a, b = weights[folios[i]], weights[folios[j]]
            common = a.keys() & b.keys()
            s = sum(a[w] for w in common)
            vals.append(0.5 * (s / max(totals[folios[i]], 1e-9) + s / max(totals[folios[j]], 1e-9)))
    return statistics.fmean(vals) if vals else 0.0


def feature_groups(entries: Sequence[Entry], min_size: int = 6) -> dict[str, list[Entry]]:
    groups: dict[str, list[Entry]] = defaultdict(list)
    for e in entries:
        for f in e.features:
            groups[feature_name(f)].append(e)
    return {f: g for f, g in groups.items() if len(g) >= min_size}


def feature_scan(entries: Sequence[Entry], shuffles: int = 300, seed: int = 0, min_size: int = 6) -> list[dict]:
    """Vocabulary shared inside every feature group against random groups of the same language-and-hand make-up."""
    r = random.Random(seed)
    pool = [e for e in entries if e.words and e.features]
    weights, totals = _idf_pages(pool)
    by_stratum: dict[tuple[str, str], list[str]] = defaultdict(list)
    for e in pool:
        by_stratum[e.stratum].append(e.folio)
    rows = []
    for f, group in feature_groups(pool, min_size).items():
        folios = [e.folio for e in group]
        obs = group_overlap(folios, weights, totals)
        need = Counter(e.stratum for e in group)
        null = []
        for _ in range(shuffles):
            sample = []
            for stratum, k in need.items():
                sample += r.sample(by_stratum[stratum], min(k, len(by_stratum[stratum])))
            null.append(group_overlap(sample, weights, totals))
        mean, sd = statistics.fmean(null), statistics.pstdev(null)
        z = (obs - mean) / sd if sd > 1e-12 else 0.0
        hits = sum(1 for v in null if v >= obs)
        p = (hits + 1) / (shuffles + 1) if hits else min((hits + 1) / (shuffles + 1), 0.5 * math.erfc(z / math.sqrt(2)))
        rows.append({"feature": f, "n": len(folios), "overlap": obs, "null_mean": mean, "z": z, "p": p,
                     "languages": dict(Counter(e.currier or "-" for e in group))})
    for row in rows:
        row["p_adj"] = min(1.0, row["p"] * max(1, len(rows)))
    return sorted(rows, key=lambda d: -d["z"])


def shuffle_features(entries: Sequence[Entry], seed: int = 0) -> list[Entry]:
    """Negative control: feature lists permuted among pages of the same language and hand."""
    r = random.Random(seed)
    out = [Entry(e.folio, e.section, list(e.features), e.currier, e.hand, e.loci, e.text_items, e.similar, e.illustration,
                 e.words, e.labels) for e in entries]
    groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for i, e in enumerate(out):
        if e.features:
            groups[e.stratum].append(i)
    for idx in groups.values():
        feats = [out[i].features for i in idx]
        r.shuffle(feats)
        for i, fs in zip(idx, feats):
            out[i].features = fs
    return out


def plant_words(entries: Sequence[Entry], feature: str, frac: float = 0.1, seed: int = 0, topic_size: int = 8) -> list[Entry]:
    """Positive control: pages with `feature` get a small shared topic vocabulary.

    `topic_size` word types are drawn from the group's own rarer words and written into a share `frac`
    of every member page's positions: what a group of pages about one thing would look like.
    """
    r = random.Random(seed)
    out = [Entry(e.folio, e.section, list(e.features), e.currier, e.hand, e.loci, e.text_items, e.similar, e.illustration,
                 list(e.words), e.labels) for e in entries]
    members = [e for e in out if feature in {feature_name(f) for f in e.features} and e.words]
    counts = Counter(w for e in members for w in set(e.words))
    rare = [w for w, c in counts.items() if c <= 2]
    topic = r.sample(rare, min(topic_size, len(rare))) if rare else sorted(counts)[:topic_size]
    for e in members:
        k = max(1, int(frac * len(e.words)))
        for pos in r.sample(range(len(e.words)), min(k, len(e.words))):
            e.words[pos] = r.choice(topic)
    return out


# ---------- 3. section ledger

COUNTS = re.compile(r"There are (\d+) in total")


def ledger(entries: Sequence[Entry]) -> list[dict]:
    rows = []
    by_section: dict[str, list[Entry]] = defaultdict(list)
    for e in entries:
        by_section[e.section or "?"].append(e)
    for section, group in sorted(by_section.items(), key=lambda t: -len(t[1])):
        loci = [e.loci for e in group if e.loci is not None]
        figures = [int(m.group(1)) for e in group for m in [COUNTS.search(e.illustration)] if m]
        rows.append({"section": section, "pages": len(group), "loci_mean": statistics.fmean(loci) if loci else None,
                     "labels": sum(e.labels for e in group), "words": sum(len(e.words) for e in group),
                     "currier": dict(Counter(e.currier or "-" for e in group)),
                     "hands": dict(Counter((e.hand or "?").split()[0] for e in group)),
                     "features_pages": sum(1 for e in group if e.features),
                     "figures_stated": sum(figures) if figures else None})
    return rows


def catalogue_pairs(entries: Sequence[Entry]) -> list[tuple[str, str, bool]]:
    """(herbal page, pharmaceutical page, same?) cross-references the catalogue states."""
    out = []
    for e in entries:
        for s in e.similar:
            out.append((e.folio, s["folio"], bool(s.get("same"))))
    return out
