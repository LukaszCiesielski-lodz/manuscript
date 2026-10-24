"""Theory: a scribe's habits (v6, v7) can be tuned until no measure and no transformer judge tells the text from the manuscript.

See voynich.lab.v6. Evolution on the CPU (scorecard of the odd folios), finalists ranked on the
even folios the search never saw (three seeds, n-gram line classifier), the best few judged by
the character transformer of the adversary theory against the real text, with the real-vs-real
AUC and the judge's sensitivity as references.
"""

from __future__ import annotations

import json
import statistics
import time

from ... import hoax
from .. import v6
from ..config import LabConfig
from ..results import TheoryResult
from .adversary import train_judge
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs, split_lines


def _perturb(lines, frac: float, seed: int):
    import random
    rng = random.Random(seed)
    glyphs = sorted({g for l in lines for w in l for g in w})
    return [[[rng.choice(glyphs) if rng.random() < frac else g for g in w] for w in l] for l in lines]


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    pop, gens = (6, 3) if cfg.quick else (cfg.v6_population, cfg.v6_generations)
    res = TheoryResult(
        theory="v6",
        hypothesis="Reguły skryby bez treści (v5 z tłumieniem słów już użytych i unikaniem sąsiada: v7) dają się dostroić tak, że "
                   f"tekst przechodzi wszystkie {len(hoax.MEASURES)} miary i nie odróżnia go transformer-sędzia: rękopis jest wtedy "
                   "wytłumaczalny bez treści.",
        method=(f"Ewolucja (μ+λ) {len(v6.SPACE)} ustawień generatora v5 działami z nowym tłumieniem częstości (freq_gamma): populacja "
                f"{pop}, {gens} pokoleń, elita {4}, wspólne ziarno w pokoleniu, przystosowanie = Σ max(0,|z|−1)² po {len(hoax.MEASURES)} miarach "
                "(w tym nowa: informacja sąsiednich słów ponad losowe słowa linii) + "
                "3·Σ z² po miarach słownictwa wobec karty foliałów nieparzystych. Finaliści oceniani na foliałach parzystych "
                f"(3 ziarna, klasyfikator n-gramowy wierszy), {cfg.v6_topk} najlepszych do sędziego-transformera ({cfg.v6_judge_seeds} ziarna) "
                "z odniesieniami: prawdziwe wobec prawdziwych, bełkot v5 działami, czułość (10% glifów zmienionych)."),
        references=["Beyer & Schwefel, Evolution strategies: a comprehensive introduction (2002)",
                    "Timm & Schinner, A possible generating algorithm of the Voynich manuscript (2019)"])
    odd, even = split_lines()
    stick_odd, stick_even = hoax.yardstick(odd), hoax.yardstick(even)
    m_oe, m_eo = hoax.misses(hoax.scorecard(odd, stick_even)), hoax.misses(hoax.scorecard(even, stick_odd))
    res.control("prawdziwe foliały przechodzą kartę drugiej połowy", "≤ 1 chybienie w obie strony",
                f"nieparzyste wobec parzystych: {len(m_oe)} ({', '.join(m_oe) or '–'}); parzyste wobec nieparzystych: {len(m_eo)} ({', '.join(m_eo) or '–'})",
                len(m_oe) <= 1 and len(m_eo) <= 1)
    runs = odd_runs()
    shared = v6.Shared(runs, v6.section_models(runs), stick_odd)
    a, b = v6.evaluate(v6.V5_POINT, cfg.seed, shared), v6.evaluate(v6.V5_POINT, cfg.seed, shared)
    res.control("ocena ustawień jest deterministyczna", "to samo przystosowanie dwa razy", f"{a['fitness']:.3f} i {b['fitness']:.3f}",
                abs(a["fitness"] - b["fitness"]) < 1e-9)
    log = lambda m: print(m, flush=True)  # noqa: E731
    ev = v6.Evolution(population=pop, generations=gens, elite=min(4, max(2, pop // 4)), workers=cfg.v6_workers, seed=cfg.seed, log=log)
    best = ev.run(shared=shared)
    out_dir = cfg.results_dir / "v6"
    res.artifacts.append(str(v6.save({**best, "history": ev.history}, out_dir)))
    # Finalists on the even folios, never seen by the search.
    finalists = ev.finalists[: cfg.v6_topk] or [best["params"]]
    seeds = [cfg.seed + 101, cfg.seed + 202, cfg.seed + 303][: 1 if cfg.quick else 3]
    ranked = []
    for params in finalists:
        p, fav_n = v6.split_params(params)
        cards, aucs, gens_txt = [], [], []
        for s in seeds:
            gen = generate_by_section(runs, p, s, fav_n=fav_n, models=shared.models)
            cards.append(hoax.scorecard(gen, stick_even))
            aucs.append(hoax.classifier_auc(even, gen, s))
            gens_txt.append(gen)
        fit = statistics.fmean(v6.fitness_of(c) for c in cards)
        miss = sorted({k for c in cards for k in hoax.misses(c)})
        ranked.append({"params": params, "fitness_even": fit, "misses_even": miss, "ngram_auc": statistics.fmean(aucs), "text": gens_txt[0]})
    ranked.sort(key=lambda r: (r["fitness_even"], r["ngram_auc"]))
    v5_cards = [hoax.scorecard(generate_by_section(runs, V5_SECTION_PARAMS, s), stick_even) for s in seeds]
    v5_miss = sorted({k for c in v5_cards for k in hoax.misses(c)})
    for r in ranked:
        res.evidence.append(f"Finalista: przystosowanie na parzystych {r['fitness_even']:.2f}, chybienia {', '.join(r['misses_even']) or 'brak'}, "
                            f"AUC n-gramowy {r['ngram_auc']:.3f}; ustawienia {json.dumps({k: round(v, 3) for k, v in r['params'].items()})}.")
    res.evidence.append(f"Odniesienie v5 działami na parzystych: chybienia {', '.join(v5_miss) or 'brak'} "
                        f"(przystosowanie {statistics.fmean(v6.fitness_of(c) for c in v5_cards):.2f}).")
    (out_dir / "best_sample.txt").write_text("\n".join(" ".join("".join(w) for w in l) for l in ranked[0]["text"][:300]), encoding="utf-8")
    res.artifacts.append(str(out_dir / "best_sample.txt"))
    metrics = {"evolution": best, "history": ev.history, "finalists": [{k: v for k, v in r.items() if k != "text"} for r in ranked],
               "v5_misses_even": v5_miss}
    try:
        import torch  # noqa: F401
    except ImportError:
        res.metrics = metrics
        res.decide(None)
        res.summary = (f"Ewolucja bez sędziego (brak PyTorch): najlepszy finalista chybia {len(ranked[0]['misses_even'])} miar na parzystych "
                       f"({', '.join(ranked[0]['misses_even']) or 'brak'}), v5 {len(v5_miss)}.")
        res.seconds = time.time() - t0
        return res
    real_s, odd_s = hoax.line_strings(even), hoax.line_strings(odd)
    jseeds = [cfg.seed + i for i in range(1 if cfg.quick else cfg.v6_judge_seeds)]
    auc_real = statistics.fmean(train_judge(real_s, odd_s, cfg, s) for s in jseeds)
    res.control("sędzia: prawdziwe wobec prawdziwych blisko 0,5", "AUC ≤ 0,62", f"{auc_real:.3f}", auc_real <= 0.62)
    auc_sens = statistics.fmean(train_judge(real_s, hoax.line_strings(_perturb(odd, 0.1, s)), cfg, s) for s in jseeds)
    res.control("sędzia: czułość na 10% zmienionych glifów", "AUC ≥ 0,7", f"{auc_sens:.3f}", auc_sens >= 0.7)
    auc_v5 = statistics.fmean(train_judge(real_s, hoax.line_strings(generate_by_section(runs, V5_SECTION_PARAMS, s)), cfg, s) for s in jseeds)
    judged = []
    for r in ranked[: cfg.v6_topk]:
        p, fav_n = v6.split_params(r["params"])
        auc = statistics.fmean(train_judge(real_s, hoax.line_strings(generate_by_section(runs, p, s, fav_n=fav_n, models=shared.models)), cfg, s)
                               for s in jseeds)
        judged.append({"fitness_even": r["fitness_even"], "misses_even": r["misses_even"], "judge_auc": auc, "params": r["params"]})
        print(f"  sędzia: finalista {r['fitness_even']:.2f} -> AUC {auc:.3f}", flush=True)
    metrics["judge"] = {"real_vs_real": auc_real, "sensitivity": auc_sens, "v5": auc_v5, "finalists": judged}
    res.metrics = metrics
    top = min(judged, key=lambda j: j["judge_auc"])
    ok = len(top["misses_even"]) <= 1 and top["judge_auc"] <= auc_real + 0.07
    res.decide(True if ok else None)
    res.summary = (f"Najlepszy v6: AUC sędziego {top['judge_auc']:.3f} (prawdziwe wobec prawdziwych {auc_real:.3f}, v5 {auc_v5:.3f}), "
                   f"chybienia na parzystych: {', '.join(top['misses_even']) or 'brak'} (v5: {', '.join(v5_miss) or 'brak'}). "
                   + ("Tekst bez treści nieodróżnialny od rękopisu." if ok else "Sędzia nadal odróżnia tekst bez treści od rękopisu."))
    res.caveats += ["Przystosowanie liczone na jednym ziarnie na pokolenie; finaliści na trzech ziarnach i na foliałach, których wyszukiwanie nie widziało.",
                    "Sędzia widzi pojedyncze wiersze; spójność strony sprawdza osobno teoria cohesion."]
    res.seconds = time.time() - t0
    return res
