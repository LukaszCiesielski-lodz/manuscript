"""Theory: a line is a record with fields (register, receptary, calendar), not a sentence.

See voynich.records. Slot-from-word classifiers (folio held out), mutual information between
word class and slot against within-line shuffles, and neighbour-to-field prediction, for the
manuscript beside Latin prose, plainchant, gibberish v5 and real medieval lists. The manuscript's
line edges are known; the claim rests on the interior of the line.
"""

from __future__ import annotations

import random
import time

from ... import corpus, eva, lists, notation, records
from ..config import LabConfig
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs


def corpora(cfg: LabConfig, n_lines: int | None = None) -> dict[str, tuple[list, list]]:
    """Named corpora as (lines of glyph tuples, group ids), each cut to the manuscript's line count."""
    voy_lines = [l for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    voy = [[tuple(eva.glyphs(w)) for w in l.words] for l in voy_lines]
    groups = [l.folio for l in voy_lines]
    n = n_lines or len(voy)
    out = {"rękopis": (voy[:n], groups[:n])}
    lat = corpus.load_reference("Latin")[:9 * n]
    out["łacina"] = ([[tuple(w) for w in lat[i:i + 9]] for i in range(0, len(lat), 9)][:n], [f"l{i // 30}" for i in range(n)])
    try:
        chant = notation.chant_lines("word", limit=n)
        out["chorał (słowa)"] = ([[tuple(u) for u in l] for l in chant], [f"c{i // 10}" for i in range(len(chant))])
    except FileNotFoundError:
        pass
    gen = [[tuple(w) for w in l] for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)][:n]
    out["bełkot v5"] = (gen, [f"g{i // 15}" for i in range(len(gen))])
    for name in (cfg.lists_corpora or lists.available()):
        entries = lists.load(name)
        if lists.passes(lists.quality(entries)):
            e = lists.as_lines(entries)[:n]
            out[name] = (e, [f"{name}{i // 10}" for i in range(len(e))])
    return out


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 50 if cfg.quick else 200
    n_lines = 1200 if cfg.quick else None
    res = TheoryResult(
        theory="records",
        hypothesis="Wiersz rękopisu to rekord o polach (jak wpis rejestru, przepis, dzień kalendarza): miejsce słowa w wierszu "
                   "da się odczytać z samego słowa, a klasa słowa (pierwszy i ostatni glif, długość) zależy od pola.",
        method=("Klasyfikator n-gramowy znaków przewidujący miejsce słowa z samego słowa (AUC, foliały odłożone): schemat "
                "krawędzi (pierwsze/środek/ostatnie) i wnętrza (2., 3., 4., 5.+ słowo w wierszach ≥ 5 słów); informacja wzajemna "
                f"klasy słowa i miejsca jako z wobec {shuffles} tasowań słów w wierszu; przewidywanie klasy słowa z klas sąsiadów "
                "ponad klasę większościową. Te same miary dla łaciny, chorału, bełkotu v5 i średniowiecznych list (martyrologium, "
                "Apicius, Alphita). Kontrole: rekordy syntetyczne o polach z własnymi podsłownikami; rękopis z przetasowanymi "
                "słowami w wierszu."),
        references=["Currier, Some important new statistical findings (1976): zjawiska początku i końca wiersza",
                    "Zandbergen, voynich.nu: line-initial and line-final patterns"])
    rng = random.Random(cfg.seed)
    syn_l, syn_g = records.synthetic_records(1500, cfg.seed)
    syn = records.measure(syn_l, syn_g, cfg.seed, shuffles)
    res.control("rekordy syntetyczne z polami: wnętrze odczytane", "AUC ≥ 0,8; MI (pierwszy glif) z ≥ 5; zysk ≥ 0,2",
                f"AUC {syn['interior_auc']:.2f}, z = {syn['mi']['first']['z']:.1f}, zysk {syn['template_gain']:.2f}",
                syn["interior_auc"] >= 0.8 and syn["mi"]["first"]["z"] >= 5 and syn["template_gain"] >= 0.2)
    data = corpora(cfg, n_lines)
    voy, voy_g = data["rękopis"]
    sh = records.measure(records.shuffle_within_lines(voy, rng), voy_g, cfg.seed, shuffles)
    worst = max(abs(m["z"]) for m in sh["mi"].values())
    res.control("rękopis z przetasowanymi słowami w wierszu: wnętrze nieodczytywalne", "AUC ≤ 0,6; |z| < 3",
                f"AUC {sh['interior_auc']:.2f}, max |z| = {worst:.1f}", sh["interior_auc"] <= 0.6 and worst < 3)
    metrics = {}
    for name, (lines, groups) in data.items():
        m = records.measure(lines, groups, cfg.seed, shuffles)
        metrics[name] = m
        res.evidence.append(f"{name} ({m['lines']} wierszy, {m['words']} słów): AUC krawędzi {m['edge_auc']:.2f}, wnętrza "
                            f"{m['interior_auc']:.2f}; informacja wzajemna z miejscem (z): pierwszy glif {m['mi']['first']['z']:+.1f}, "
                            f"ostatni {m['mi']['last']['z']:+.1f}, długość {m['mi']['length']['z']:+.1f}; zysk z sąsiadów {m['template_gain']:+.3f}.")
        print(f"  {name}: krawędź {m['edge_auc']:.2f} wnętrze {m['interior_auc']:.2f} MI z {m['mi']['first']['z']:+.1f} zysk {m['template_gain']:+.3f}", flush=True)
    res.metrics = {"corpora": metrics, "controls": {"synthetic": syn, "shuffled": sh}}
    v, g = metrics["rękopis"], metrics["bełkot v5"]
    r1 = v["interior_auc"] >= max(g["interior_auc"] + 0.05, 0.6)
    r2 = v["mi"]["first"]["z"] >= 5 and v["mi"]["first"]["z"] >= g["mi"]["first"]["z"]
    r3 = v["template_gain"] - g["template_gain"] >= 0.05
    if r1 and (r2 or r3):
        res.decide(True)
    elif v["interior_auc"] <= g["interior_auc"] + 0.02 and v["template_gain"] - g["template_gain"] < 0.03:
        res.decide(False)
    else:
        res.decide(None)
    order = sorted(metrics, key=lambda k: metrics[k]["interior_auc"], reverse=True)
    res.summary = (f"Wnętrze wiersza: AUC rękopisu {v['interior_auc']:.2f} wobec bełkotu v5 {g['interior_auc']:.2f} "
                   f"(próg {max(g['interior_auc'] + 0.05, 0.6):.2f}); informacja wzajemna pierwszego glifu z miejscem z = {v['mi']['first']['z']:+.1f} "
                   f"wobec {g['mi']['first']['z']:+.1f}; zysk z sąsiadów {v['template_gain']:+.3f} wobec {g['template_gain']:+.3f}. "
                   "Gradient AUC wnętrza: " + " > ".join(f"{k} {metrics[k]['interior_auc']:.2f}" for k in order) + ".")
    res.caveats += ["Krawędzie wiersza (p/t na początku, m/g na końcu) są znane od Curriera; roszczenie rekordowe opiera się na wnętrzu.",
                    "Wpisy list są dłuższe od wierszy rękopisu, więc ich wnętrze liczy więcej pozycji 5+.",
                    "Bełkot v5 ma nawyki pozycyjne wbudowane (position_gamma), więc jest tłem surowym."]
    res.seconds = time.time() - t0
    return res
