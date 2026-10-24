"""Theory: the manuscript's signature is that of a medieval list (calendar of saints, recipe book, glossary).

The list corpora of voynich.lists go through the signature battery of the notation theory (long-range
dependency split into repeats, variants and unrelated words; word-length dynamics; shape measures as
z against the manuscript's spread; eight criteria) beside the manuscript, Latin prose, gibberish v5,
the litany and the barbarous names, plus the record measures of voynich.records. The report shows the
gradient prose -> lists -> manuscript.
"""

from __future__ import annotations

import random
import time

from ... import corpus, eva, genres, hoax, lengths, lists, longrange, records
from ..config import LabConfig
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs
from .notation import SHAPE, _criteria, _trim


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 8 if cfg.quick else 20
    res = TheoryResult(
        theory="lists",
        hypothesis="Rękopis jest listą (rejestr, receptariusz, kalendarz imion, glosariusz): jego podpis statystyczny "
                   "jest podpisem średniowiecznych tekstów listowych, nie prozy.",
        method=("Martyrologium Usuarda (wpis = dzień), De re coquinaria Apicjusza (wpis = przepis) i glosariusz Alphita "
                "(wpis = hasło, OCR dwukolumnowy) obok rękopisu, łaciny, bełkotu v5, litanii i imion magicznych: zależność na "
                "odległość rozbita na powtórzenia, warianty i słowa niespokrewnione; dynamika długości; miary kształtu jako z "
                "wobec rozrzutu bloków rękopisu; osiem kryteriów podpisu (cecha definiująca: brak zależności między różnymi "
                "słowami na odległość 2–7) oraz miary rekordowe (AUC krawędzi i wnętrza, informacja wzajemna pierwszego glifu "
                "z miejscem). Kontrole: rama wszczepiona w rękopis; martyrologium przetasowane między wpisami; bramka parsowania."),
        references=["Usuardus, Martyrologium (Migne, PL 123–124; la.wikisource)", "Apicius, De re coquinaria (la.wikisource)",
                    "Mowat (ed.), Alphita, a medico-botanical glossary (Oxford 1887)"])
    voy = [[eva.glyphs(w) for w in l.words] for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    n = sum(map(len, voy))
    stick = hoax.yardstick(voy)
    texts = {"rękopis": voy}
    quality = {}
    for name in (cfg.lists_corpora or lists.available()):
        entries = lists.load(name)
        quality[name] = q = lists.quality(entries)
        if lists.passes(q):
            texts[name] = _trim([[list(w) for w in e] for e in entries], n)
    passing = [k for k in quality if lists.passes(quality[k])]
    res.control("parsowanie list: co najmniej dwa korpusy po ≥ 300 wpisów o medianie 3–60 słów", "≥ 2",
                "; ".join(f"{k}: {q['entries']} wpisów, mediana {q['median_words']:.0f} słów" for k, q in quality.items()) or "brak plików",
                len(passing) >= 2)
    if len(passing) < 2:
        res.decide(None)
        res.summary = "Pominięte: brak korpusów list (scripts/fetch_lists.py)."
        res.seconds = time.time() - t0
        return res
    texts["łacina"] = _trim([[list(w) for w in corpus.load_reference("Latin")[i:i + 9]] for i in range(0, n, 9)], n)
    texts["bełkot v5"] = [[list(w) for w in l] for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)]
    for name in genres.available():
        words = genres.load(name)
        if len(words) >= 600:
            texts[name] = [[list(w) for w in words[i:i + 9]] for i in range(0, len(words), 9)]
    rr = random.Random(cfg.seed)
    frame = [[w if i % 3 else ["o", "r", "a"] for i, w in enumerate(l)] for l in voy]
    syn_fr = longrange.split_by_identity(frame, top=60, shuffles=shuffles, seed=cfg.seed)
    res.control("rękopis z wszczepioną ramą (co trzecie słowo stałe) zyskuje składnię na odległość", "z ≥ 5",
                f"z = {syn_fr['unrelated']['z']:.1f}", syn_fr["unrelated"]["z"] >= 5)
    if "martyrology" in texts:
        flat = [w for l in texts["martyrology"] for w in l]
        rr.shuffle(flat)
        across, i = [], 0
        for l in texts["martyrology"]:
            across.append(flat[i:i + len(l)])
            i += len(l)
        syn_a = longrange.split_by_identity(across, top=60, shuffles=shuffles, seed=cfg.seed)
        res.control("martyrologium ze słowami przetasowanymi między wpisami traci składnię na odległość", "z < 3",
                    f"z = {syn_a['unrelated']['z']:.1f}", syn_a["unrelated"]["z"] < 3)
    metrics, scores = {}, {}
    for name, lines in texts.items():
        nw = sum(map(len, lines))
        top = 60 if nw > 3000 else 15
        syn = longrange.split_by_identity(lines, top=top, shuffles=shuffles, seed=cfg.seed)
        dyn = lengths.describe(lengths.series([w for l in lines for w in l]), shuffles=shuffles, seed=cfg.seed)
        blocks = hoax.blocks(lines, size=min(hoax.BLOCK, max(300, nw // 2)))
        m = hoax.measure(blocks[0]) if blocks else {}
        zs = {k: (m[k] - stick[k][0]) / stick[k][1] for k in SHAPE if k in m and k in stick}
        crit = _criteria(syn, dyn, zs)
        tl = [[tuple(w) for w in l] for l in lines]
        groups = [f"{name}{i // 10}" for i in range(len(tl))]
        rec = {"edge_auc": records.slot_auc(tl, groups, records.EDGE, cfg.seed),
               "interior_auc": records.slot_auc(tl, groups, records.INTERIOR, cfg.seed),
               "mi_first_z": records.field_mi_z(tl, records.INTERIOR, 50 if cfg.quick else 100, cfg.seed)["first"]["z"]}
        scores[name] = sum(crit.values())
        metrics[name] = {"words": nw, "lines": len(lines), "syntax": syn, "lengths": {k: dyn[k] for k in ("ac1", "updown", "dfa")},
                         "shape_z": zs, "criteria": crit, "records": rec}
        res.evidence.append(f"{name} ({nw} słów, {len(lines)} wierszy): powtórzenia z = {syn['same']['z']:.1f}, warianty z = "
                            f"{syn['variants']['z']:.1f}, niespokrewnione z = {syn['unrelated']['z']:.1f}; długości: korelacja sąsiadów "
                            f"{dyn['ac1']['value']:+.2f}, DFA {dyn['dfa']['value']:.2f}; kształt wobec rękopisu: "
                            + ", ".join(f"{hoax.MEASURES[k]} {z:+.1f}" for k, z in zs.items())
                            + f". Kryteria podpisu: {scores[name]}/8. Rekord: AUC krawędzi {rec['edge_auc']:.2f}, wnętrza "
                            f"{rec['interior_auc']:.2f}, pierwszy glif a miejsce z = {rec['mi_first_z']:+.1f}.")
        print(f"  {name}: niespokrewnione z {syn['unrelated']['z']:+.1f}, kryteria {scores[name]}/8, wnętrze {rec['interior_auc']:.2f}", flush=True)
    res.metrics = {"texts": metrics, "quality": quality}
    match = [k for k in passing if metrics[k]["criteria"]["brak składni na odległość"] and scores[k] >= 6]
    all_prose = all(metrics[k]["syntax"]["unrelated"]["z"] > 5 and scores[k] <= 4 for k in passing)
    res.decide(True if match else (False if all_prose else None))
    order = sorted(((metrics[k]["syntax"]["unrelated"]["z"], k) for k in texts), reverse=True)
    res.summary = ("Gradient składni na odległość (z słów niespokrewnionych): " + " > ".join(f"{k} {z:.0f}" for z, k in order) + ". "
                   "Kryteria podpisu rękopisu: " + ", ".join(f"{k} {scores[k]}/8" for k in texts if k != "rękopis") + ". "
                   + ("Lista o podpisie rękopisu: " + ", ".join(match) + "." if match else
                      "Listy średniowieczne mają składnię na odległość jak proza (wpisy to zdania), której rękopis nie ma; "
                      "z rękopisem dzielą co najwyżej odczytywalność miejsca słowa w wierszu." if all_prose else
                      "Żadna lista nie ma podpisu rękopisu: wszystkie mają składnię na odległość (z = "
                      + ", ".join(f"{metrics[k]['syntax']['unrelated']['z']:.0f}" for k in passing) + f"), rękopis "
                      f"{metrics['rękopis']['syntax']['unrelated']['z']:.1f}; najbliżej kształtem "
                      + max(passing, key=lambda k: scores[k]) + f" ({max(scores[k] for k in passing)}/8), lecz z silną składnią."))
    res.caveats += ["Alphita pochodzi z OCR wydania dwukolumnowego: wpisy są pomieszane między kolumnami, więc jej miary są surowe.",
                    "Wpisy list (25–60 słów) są dłuższe od wierszy rękopisu (ok. 10); zależność na odległość 2–7 słów liczona w obrębie wpisu.",
                    "Lista haseł Alphity (557 nazw, po jednym słowie) nie przechodzi bramki i służy tylko jako przykład nomenklatury."]
    res.seconds = time.time() - t0
    return res
