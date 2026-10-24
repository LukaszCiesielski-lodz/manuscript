"""Theory: the rules that shape the words follow the scribe's hand, not the content.

If the text is a cipher of one source, scribes should differ in letter shapes only: within the
same section and Currier language, lines by different hands should be statistically alike.
If the text comes from each scribe's habits, the hand should be visible in the words even when
section and language are held fixed, and more visible than the section is within one hand.
Lines are classified by character n-grams with whole folios held out (the classifier must not
learn page vocabulary); the null relabels folios at random with the same page counts per class.
"""

from __future__ import annotations

import random
import time
from collections import defaultdict

import numpy as np

from ... import corpus
from ..config import LabConfig
from ..results import TheoryResult

MIN_PAGES = 4


def _auc_pages(A, B, seed: int, folds: int = 5) -> float:
    """Lines of class A vs B; folds by folio; mean AUC over folds (NaN when a class has no test folds)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    r = random.Random(seed)
    pa, pb = sorted({l.folio for l in A}), sorted({l.folio for l in B})
    r.shuffle(pa)
    r.shuffle(pb)
    fa, fb = [pa[i::folds] for i in range(folds)], [pb[i::folds] for i in range(folds)]
    aucs = []
    for k in range(folds):
        test = set(fa[k]) | set(fb[k])
        tr = [(".".join(l.words), 0) for l in A if l.folio not in test] + [(".".join(l.words), 1) for l in B if l.folio not in test]
        te = [(".".join(l.words), 0) for l in A if l.folio in test] + [(".".join(l.words), 1) for l in B if l.folio in test]
        if len({y for _, y in te}) < 2 or len({y for _, y in tr}) < 2:
            continue
        vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 4), min_df=2)
        X, y = vec.fit_transform([s for s, _ in tr]), [c for _, c in tr]
        n1 = sum(y)
        clf = LogisticRegression(max_iter=3000, C=2.0, class_weight={0: len(y) / (2 * (len(y) - n1)), 1: len(y) / (2 * n1)})
        clf.fit(X, y)
        aucs.append(roc_auc_score([c for _, c in te], clf.predict_proba(vec.transform([s for s, _ in te]))[:, 1]))
    return float(np.mean(aucs)) if aucs else float("nan")


def _relabel_null(A, B, seed: int, reps: int) -> tuple[float, float]:
    """AUC when the folios of A and B are dealt into two random groups of the same sizes."""
    r = random.Random(seed)
    by = defaultdict(list)
    for l in A + B:
        by[l.folio].append(l)
    pa, pb = sorted({l.folio for l in A}), sorted({l.folio for l in B})
    pool, out = pa + pb, []
    for _ in range(reps):
        r.shuffle(pool)
        ga = set(pool[:len(pa)])
        v = _auc_pages([l for f in ga for l in by[f]], [l for f in pool if f not in ga for l in by[f]], seed)
        if v == v:
            out.append(v)
    return (float(np.mean(out)), float(np.std(out))) if out else (float("nan"), float("nan"))


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    reps = 4 if cfg.quick else 12
    res = TheoryResult(
        theory="hands",
        hypothesis="Statystyka słów idzie za ręką skryby, nie za treścią: ten sam dział i język pisane różnymi rękami "
                   "różnią się bardziej niż różne działy pisane jedną ręką.",
        method=("Ręce wg Davis (2020) z metadanych ZL. Klasyfikator wierszy (n-gramy znaków, regresja logistyczna) z "
                "całymi kartami odłożonymi do testu (5 podziałów), AUC. Pary rąk w tym samym dziale i języku Curriera; "
                "tło: te same karty rozdane losowo na dwie „ręce” o tych samych liczbach kart (z). Dla porównania efekt "
                "działu w obrębie jednej ręki i efekt języka A/B w obrębie jednej ręki."),
        references=["Davis, How many glyphs and how many scribes? Manuscript Studies 5 (2020)",
                    "Currier, Papers on the Voynich manuscript (1976)"])
    lines = [l for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    groups = defaultdict(list)
    for l in lines:
        groups[(l.hand, l.language, l.section)].append(l)
    pages_of = {k: len({l.folio for l in v}) for k, v in groups.items()}
    big = {k: v for k, v in groups.items() if pages_of[k] >= MIN_PAGES and k[0] not in ("?", "@")}
    hand_tests, section_tests, language_tests = [], [], []
    keys = sorted(big)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if a[1:] == b[1:]:                                  # same language and section, different hand
                auc = _auc_pages(big[a], big[b], cfg.seed)
                mu, sd = _relabel_null(big[a], big[b], cfg.seed, reps)
                z = (auc - mu) / sd if sd and sd == sd else float("nan")
                hand_tests.append({"a": a, "b": b, "auc": auc, "null": mu, "null_sd": sd, "z": z,
                                   "pages": (pages_of[a], pages_of[b])})
                res.evidence.append(f"Ręka {a[0]} vs {b[0]}, {a[2]} {a[1]} ({pages_of[a]} i {pages_of[b]} kart): AUC {auc:.3f}, "
                                    f"losowe podziały kart {mu:.3f} ± {sd:.3f}, z = {z:+.1f}.")
                print(f"  ręce {a[0]}/{b[0]} w {a[2]} {a[1]}: AUC {auc:.3f} (tło {mu:.3f}±{sd:.3f})", flush=True)
            elif a[0] == b[0] and a[1] == b[1]:                 # same hand and language, different section
                auc = _auc_pages(big[a], big[b], cfg.seed)
                section_tests.append({"hand": a[0], "sections": (a[2], b[2]), "auc": auc})
                res.evidence.append(f"Ta sama ręka {a[0]}, język {a[1]}: {a[2]} vs {b[2]}: AUC {auc:.3f} (efekt działu).")
            elif a[0] == b[0] and a[2] == b[2]:                 # same hand and section, different language
                auc = _auc_pages(big[a], big[b], cfg.seed)
                language_tests.append({"hand": a[0], "section": a[2], "languages": (a[1], b[1]), "auc": auc})
                res.evidence.append(f"Ta sama ręka {a[0]}, dział {a[2]}: język {a[1]} vs {b[1]}: AUC {auc:.3f} (efekt języka).")
    res.metrics = {"hand": hand_tests, "section": section_tests, "language": language_tests,
                   "groups": {f"{k[0]}|{k[1]}|{k[2]}": {"lines": len(v), "pages": pages_of[k]} for k, v in big.items()}}
    hz = [t["z"] for t in hand_tests if t["z"] == t["z"]]
    ha = [t["auc"] for t in hand_tests if t["auc"] == t["auc"]]
    sa = [t["auc"] for t in section_tests if t["auc"] == t["auc"]]
    la = [t["auc"] for t in language_tests if t["auc"] == t["auc"]]
    hand_seen = bool(hz) and min(hz) >= 2.5
    if not hand_tests:
        res.decide(None)
    elif hand_seen and ha and sa and np.mean(ha) >= np.mean(sa):
        res.decide(True)
    elif ha and sa and np.mean(ha) < np.mean(sa):
        res.decide(False)
    else:
        res.decide(None)
    res.summary = (f"Ręce w tym samym dziale i języku: AUC {', '.join(f'{x:.2f}' for x in ha)} (z wobec losowych podziałów kart "
                   f"{', '.join(f'{x:+.1f}' for x in hz)}); działy w tej samej ręce: AUC {', '.join(f'{x:.2f}' for x in sa) or 'brak'}; "
                   f"języki A/B w tej samej ręce: AUC {', '.join(f'{x:.2f}' for x in la) or 'brak'}. "
                   + ("Ręka zostawia ślad w słowach, ale dział i język różnicują mocniej: reguły słów idą za treścią "
                      "(lub trybem pisania), nie za skrybą." if res.verdict == "obalona" else
                      "Ręka różnicuje słowa co najmniej tak jak dział." if res.verdict == "potwierdzona" else ""))
    res.caveats += ["Przypisanie rąk wg Davis jest w metadanych ZL przybliżone (na poziomie strony); część rąk ma po kilka kart.",
                    "Klasyfikator z odłożonymi kartami widzi też temat strony; stąd tło z losowego rozdania kart, a nie 0,5."]
    res.seconds = time.time() - t0
    return res
