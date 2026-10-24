"""Theory: the lines of a page belong together (one entry, one subject), beyond what the section explains.

A character transformer reads two line fragments side by side and says whether they come from the
same page; pages held out. A register has page cohesion (one entry per page, its names and
quantities recurring); gibberish written line by line has none beyond the section's habits.
Controls: the manuscript with its lines dealt into pseudo-pages of the same section and
dialect (must drop to chance), and Latin pseudo-pages with a page-specific word planted
(must be recognised).
"""

from __future__ import annotations

import random
import time
from collections import defaultdict

from ... import corpus
from ..config import LabConfig
from ..results import TheoryResult
from .adversary import fit_judge
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs

HALF = 47


def pairs(pages: dict[str, list[str]], group_of: dict[str, str], n_pairs: int, seed: int):
    """Same-page vs other-page (same group) pairs 'A|B' of line halves; pages split 50/50 into train and test."""
    rng = random.Random(seed)
    names = sorted(p for p, ls in pages.items() if len(ls) >= 2)
    rng.shuffle(names)
    test = set(names[: len(names) // 2])
    by_group: dict[str, list[str]] = defaultdict(list)
    for p in names:
        by_group[group_of[p]].append(p)

    def make(subset: list[str], n: int):
        xs, ys = [], []
        cands = [p for p in subset if len(by_group[group_of[p]]) >= 2 and any(q in subset for q in by_group[group_of[p]] if q != p)]
        if not cands:
            return xs, ys
        while len(xs) < n:
            p = rng.choice(cands)
            a, b = rng.sample(pages[p], 2)
            xs.append(a[:HALF] + "|" + b[:HALF])
            ys.append(1)
            q = rng.choice([q for q in by_group[group_of[p]] if q != p and q in subset])
            xs.append(a[:HALF] + "|" + rng.choice(pages[q])[:HALF])
            ys.append(0)
        return xs, ys

    tr = [p for p in names if p not in test]
    te = [p for p in names if p in test]
    xtr, ytr = make(tr, n_pairs)
    xte, yte = make(te, n_pairs // 2)
    return xtr, ytr, xte, yte


def pseudo_pages(lines: list[str], groups: list[str], per_page: int, seed: int) -> tuple[dict, dict]:
    """Lines dealt into pseudo-pages of `per_page` lines inside each group (section and dialect)."""
    rng = random.Random(seed)
    by = defaultdict(list)
    for l, g in zip(lines, groups):
        by[g].append(l)
    pages, group_of = {}, {}
    for g, ls in by.items():
        rng.shuffle(ls)
        for i in range(0, len(ls) - per_page + 1, per_page):
            name = f"{g}#{i // per_page}"
            pages[name], group_of[name] = ls[i:i + per_page], g
    return pages, group_of


def plant(pages: dict[str, list[str]], frac: float, seed: int) -> dict[str, list[str]]:
    """A page-specific word replaces `frac` of the words of every line: positive control."""
    rng = random.Random(seed)
    out = {}
    for name, ls in pages.items():
        tag = "".join(rng.choice("abcdefghiklmnopqrstuvxy") for _ in range(rng.randint(4, 7)))
        out[name] = [".".join(tag if rng.random() < frac else w for w in l.split(".")) for l in ls]
    return out


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    n_pairs = 600 if cfg.quick else 3000
    res = TheoryResult(
        theory="cohesion",
        hypothesis="Wiersze jednej strony należą do siebie (jeden wpis, jeden przedmiot) ponad to, co wynika z działu i dialektu: "
                   "sędzia pozna dwa wiersze z tej samej strony.",
        method=(f"Transformer znakowy (4 warstwy, 192 wymiary) na parach połówek wierszy „A|B” ({HALF} znaków każda): ta sama strona "
                f"wobec innej strony tego samego działu i dialektu; {n_pairs} par uczących ze stron uczących, {n_pairs // 2} testowych "
                "ze stron odłożonych; AUC. Przebiegi: rękopis; rękopis z wierszami rozdanymi na pseudostrony w dziale i dialekcie "
                "(kontrola ujemna); bełkot v5 na pseudostronach po 15 wierszy; łacina na pseudostronach; łacina z wszczepionym słowem "
                "strony w 20% słów (kontrola dodatnia)."),
        references=["Vaswani et al., Attention is all you need (2017)"])
    try:
        import torch  # noqa: F401
    except ImportError:
        res.evidence.append("Brak PyTorch: uruchom w Colabie.")
        res.decide(None)
        res.summary = "Pominięte: wymaga PyTorch i GPU."
        res.seconds = time.time() - t0
        return res
    L = [l for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    pages, group_of = defaultdict(list), {}
    for l in L:
        pages[l.folio].append(".".join(l.words))
        group_of[l.folio] = f"{l.section}/{l.language}"
    pages = {p: ls for p, ls in pages.items() if len(ls) >= 4}
    runs = {}

    def judge(name, pg, grp, seed):
        xtr, ytr, xte, yte = pairs(pg, grp, n_pairs, seed)
        auc = fit_judge(xtr, ytr, xte, yte, cfg, seed) if xtr and xte else float("nan")
        runs[name] = {"auc": auc, "pages": len(pg), "train_pairs": len(xtr), "test_pairs": len(xte)}
        print(f"  {name}: AUC {auc:.3f} ({len(pg)} stron)", flush=True)
        return auc

    auc_ms = judge("rękopis", pages, group_of, cfg.seed)
    lines = [l for p in pages for l in pages[p]]
    groups = [group_of[p] for p in pages for _ in pages[p]]
    sh_pages, sh_groups = pseudo_pages(lines, groups, 12, cfg.seed)
    auc_sh = judge("rękopis, wiersze rozdane na pseudostrony", sh_pages, sh_groups, cfg.seed)
    res.control("rękopis z wierszami rozdanymi w dziale i dialekcie: sędzia bez oparcia", "AUC ≤ 0,58", f"{auc_sh:.3f}", auc_sh <= 0.58)
    gen = [".".join("".join(w) for w in l) for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)]
    g_pages, g_groups = pseudo_pages(gen, ["v5"] * len(gen), 15, cfg.seed)
    auc_v5 = judge("bełkot v5 na pseudostronach", g_pages, g_groups, cfg.seed)
    lat = corpus.load_reference("Latin")[:9 * len(lines)]
    latl = [".".join(lat[i:i + 9]) for i in range(0, len(lat) - 9, 9)]
    l_pages, l_groups = pseudo_pages(latl, ["la"] * len(latl), 15, cfg.seed)
    auc_lat = judge("łacina na pseudostronach", l_pages, l_groups, cfg.seed)
    auc_pl = judge("łacina ze słowem strony (20%)", plant(l_pages, 0.2, cfg.seed), l_groups, cfg.seed)
    res.control("łacina z wszczepionym słowem strony: sędzia poznaje stronę", "AUC ≥ 0,7", f"{auc_pl:.3f}", auc_pl >= 0.7)
    res.metrics = runs
    for name, r in runs.items():
        res.evidence.append(f"{name}: AUC {r['auc']:.3f} ({r['pages']} stron, {r['train_pairs']} par uczących, {r['test_pairs']} testowych).")
    if auc_ms >= auc_sh + 0.10 and auc_ms >= auc_v5 + 0.05:
        res.decide(True)
    elif auc_ms <= auc_sh + 0.03:
        res.decide(False)
    else:
        res.decide(None)
    res.summary = (f"Para wierszy z tej samej strony: AUC rękopisu {auc_ms:.3f} wobec {auc_sh:.3f} po rozdaniu wierszy i {auc_v5:.3f} dla bełkotu v5 "
                   f"(łacina {auc_lat:.3f}, z wszczepionym słowem {auc_pl:.3f}). "
                   + ("Strony rękopisu są spójne ponad dział i dialekt." if res.verdict == "potwierdzona" else
                      "Strona rękopisu nie jest spójniejsza niż losowy zbiór wierszy jej działu." if auc_ms <= auc_sh + 0.03 else "Wynik niejednoznaczny."))
    res.caveats += ["Ręka skryby i dział są w tle wspólne dla strony i pseudostrony tylko wtedy, gdy grupa rozdania to dział i dialekt; "
                    "różnice rąk w obrębie działu mogą dodać sędziemu oparcia.",
                    "Połówki wierszy po 47 znaków: długie wiersze obcięte, krótkie dopełnione."]
    res.seconds = time.time() - t0
    return res
