"""Theory: the text was written with a volvelle (a wheel of glyph rings), Llull's device, no language behind it.

See voynich.lab.wheel. The wheel is inferred on the GPU from the text itself (coverage of
the vocabulary, cost of turning between consecutive words), the same search is run on
control texts, and the best wheel then writes text with the scribe's own turning habits,
which goes through the lab's generator battery (scorecard, line classifier, syntax, word
lengths). What would support the theory: the manuscript turns more cheaply than language or
shuffled text, and the wheel's text passes the bars that copy-and-modify generators fail.
"""

from __future__ import annotations

import statistics
import time

from ... import corpus, eva, hoax, lengths, longrange
from ..config import LabConfig
from ..results import TheoryResult
from ..wheel import Backend, Search, fit, random_wheel, scribe, write_random
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs, split_lines


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    xp = Backend(prefer_gpu=True)
    pop, gens = (64, 40) if cfg.quick else (cfg.wheel_population, cfg.wheel_generations)
    s = Search(rings=cfg.wheel_rings, cells=cfg.wheel_cells, population=pop, generations=gens, seed=cfg.seed)
    res = TheoryResult(
        theory="wheel",
        hypothesis="Tekst powstał z tarczy (volvelle) o kilku pierścieniach z ciągami glifów: słowo = komórki pod "
                   "wskaźnikiem, między słowami pierścienie obracają się o ząbek lub dwa; żadnego języka za tym nie ma.",
        method=(f"Tarcza nieznana, więc wnioskowana: populacja {pop} tarcz ({s.rings} pierścienie × {s.cells} komórek, "
                f"komórka = 0–3 glify) oceniana na {xp.name} przez {gens} pokoleń: pokrycie słownictwa i koszt obrotu "
                "między kolejnymi słowami wiersza. To samo dla tekstów kontrolnych: rękopis z przetasowanymi słowami, "
                "bełkot v5, łacina (litery jako glify). Najlepsza tarcza pisze tekst nawykami obrotu odczytanymi z rękopisu; "
                "tekst idzie przez kartę 22 miar, klasyfikator wierszy, test składni i dynamiki długości."),
        references=["Llull, Ars generalis ultima (1305–1308); Bonner, The Art and Logic of Ramon Llull (2007)",
                    "Timm & Schinner, Cryptologia 44 (2020)"])
    odd, even = split_lines()
    lines = [[tuple(w) for w in l] for l in odd + even]
    log = lambda m: print(m, flush=True)
    print("  tarcza dla rękopisu...", flush=True)
    best, text = fit(lines, s, xp, log)
    gen5 = [[tuple(w) for w in l] for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)]
    flat = [w for l in lines for w in l]
    import random
    r = random.Random(cfg.seed)
    r.shuffle(flat)
    shuffled, i = [], 0
    for l in lines:
        shuffled.append(flat[i:i + len(l)])
        i += len(l)
    latin = corpus.load_reference("Latin")[:len(flat)]
    latin_lines = [[tuple(w) for w in latin[i:i + 9]] for i in range(0, len(latin), 9)]
    controls = {}
    for name, txt in (("słowa przetasowane", shuffled), ("bełkot v5", gen5), ("łacina (litery)", latin_lines)):
        print(f"  tarcza dla: {name}...", flush=True)
        controls[name], _ = fit(txt, s, xp, None)
    fmt = lambda b: f"pokrycie {b['coverage']:.1%}, koszt obrotu {b['turn']:.3f}"
    res.evidence.append(f"Rękopis: {fmt(best)} (tarcza z pokolenia {best['generation']}, {best['seconds']:.0f} s).")
    for name, b in controls.items():
        if name != "tekst znanej tarczy":
            res.evidence.append(f"{name}: {fmt(b)}.")
    # Positive control: a text really written with a known wheel (small turns) must be recovered as such.
    known = random_wheel(text.seg, s.rings, s.cells, cfg.seed)
    planted = write_random(known, text.seg, min(len(flat), 12000), cfg.seed)
    print("  tarcza dla: tekst napisany znaną tarczą...", flush=True)
    recovered, _ = fit(planted, s, xp, None)
    overlap = statistics.mean(len(set(known[rr]) & set(recovered["rings"][rr])) / len(set(known[rr]))
                              for rr in range(s.rings))
    res.control("wyszukiwanie odzyskuje znaną tarczę z tekstu nią napisanego", "pokrycie ≥ 0,9 i koszt obrotu ≤ 0,25",
                f"pokrycie {recovered['coverage']:.1%}, koszt {recovered['turn']:.3f}, wspólnych komórek {overlap:.0%}",
                recovered["coverage"] >= 0.9 and recovered["turn"] <= 0.25)
    controls["tekst znanej tarczy"] = {k: v for k, v in recovered.items() if k != "rings"} | {"cell_overlap": overlap}
    cheaper = best["turn"] < controls["słowa przetasowane"]["turn"] - 0.02
    res.control("tarcza rękopisu obraca się taniej niż na słowach przetasowanych", "koszt obrotu niższy o ≥ 0,02",
                f"{best['turn']:.3f} wobec {controls['słowa przetasowane']['turn']:.3f}", cheaper)
    for rr, ring in enumerate(best["cells"]):
        res.evidence.append(f"Pierścień {rr + 1}: " + " ".join("".join(c) or "·" for c in ring))

    # The wheel writes; the text is judged like every generator (rules from odd folios, bar from even ones).
    gen = scribe([[tuple(w) for w in l] for l in odd], best["rings"], text.seg, 3 * hoax.BLOCK + 1000, cfg.seed)
    metrics = {"wheel": {k: v for k, v in best.items() if k != "rings"}, "controls": controls}
    if gen:
        stick = hoax.yardstick(even)
        card = hoax.scorecard(gen, stick)
        miss = hoax.misses(card)
        auc = hoax.classifier_auc(even, gen, cfg.seed)
        split = hoax.split_auc(even, gen, cfg.seed)
        syn = longrange.split_by_identity(gen, top=60, shuffles=8 if cfg.quick else 20, seed=cfg.seed)
        xs = lengths.series([w for l in gen for w in l])
        dyn = lengths.describe(xs, shuffles=8, seed=cfg.seed)
        metrics["text"] = {"card": card, "misses": miss, "auc": auc, "split": split, "syntax": syn, "lengths": dyn,
                           "sample": [".".join("".join(w) for w in l) for l in gen[5:11]]}
        res.evidence.append(f"Tekst z tarczy: {len(hoax.MEASURES) - len(miss)}/{len(hoax.MEASURES)} miar w rozrzucie "
                            f"rękopisu; poza: " + (", ".join(f"{hoax.MEASURES[k]} (z = {card[k]['z']:+.1f})" for k in miss)
                                                   or "żadna") + f". Klasyfikator wierszy: AUC {auc:.3f} (wewnątrz słów "
                            f"{split['inside']:.2f}, na styku {split['across']:.2f}; v5 działami ≈ 0,78, prawdziwe 0,55).")
        res.evidence.append(f"Składnia tekstu z tarczy: powtórzenia z = {syn['same']['z']:.1f}, warianty z = "
                            f"{syn['variants']['z']:.1f}, słowa niespokrewnione z = {syn['unrelated']['z']:.1f} "
                            f"(rękopis ≈ 10, 9, −1). Długości: korelacja sąsiadów {dyn['ac1']['value']:+.3f} "
                            f"(rękopis +0,16), DFA {dyn['dfa']['value']:.3f} (0,60).")
        res.evidence.append("Próbka: " + " | ".join(metrics["text"]["sample"][:3]))
        passed = not miss and auc <= 0.6
        res.decide(True if passed and cheaper else None)
    else:
        res.evidence.append("Tarcza nie składa dość słów, by pisać; brak tekstu do oceny.")
        res.decide(None)
    res.metrics = metrics
    res.summary = (f"Najlepsza tarcza składa {best['coverage']:.0%} słów rękopisu przy koszcie obrotu {best['turn']:.2f} "
                   f"(przetasowane {controls['słowa przetasowane']['turn']:.2f}, łacina "
                   f"{controls['łacina (litery)']['turn']:.2f}, bełkot v5 {controls['bełkot v5']['turn']:.2f}). "
                   + (f"Tekst pisany tarczą: {len(hoax.MEASURES) - len(metrics['text']['misses'])}/{len(hoax.MEASURES)} miar, "
                      f"AUC {metrics['text']['auc']:.2f}." if gen else ""))
    res.caveats += [
        "Tarcza o 3 pierścieniach i komórkach do 3 glifów to jeden z możliwych kształtów urządzenia; inne (więcej pierścieni, "
        "nierówne pierścienie) mogą składać więcej.",
        "Koszt obrotu zależy od ułożenia komórek, które wyszukiwanie dopasowuje do rękopisu; dlatego porównanie z tekstami "
        "kontrolnymi, dla których szukano tak samo długo.",
        "Pokrycie poniżej 100% oznacza słowa, których tarcza nie składa; skryba mógł je dopisywać ręcznie.",
    ]
    res.seconds = time.time() - t0
    return res
