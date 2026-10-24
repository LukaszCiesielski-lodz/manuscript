"""Theory: the text is a homophonic substitution of a language of the time; a hill climber finds the key.

See voynich.lab.hillclimb. For every lexicon with a running-text sample, a character 4-gram
model of the language is fitted, thousands of climbers on the GPU search the glyph-to-letter
key on the odd lines, and the best key is judged on the even lines. The same attack runs on
meaningless text with the manuscript's statistics (generator v5) and on a real text of the
language enciphered homophonically with as many glyphs as the manuscript has (positive control:
the climber must recover that key). A lead would be a manuscript score clearly better than the
gibberish's and close to natural text of the language.
"""

from __future__ import annotations

import time

from ... import lexicon
from ..brute import paragraph_lines, relabel_lines
from ..config import LabConfig
from ..hillclimb import (Backend, Climb, GlyphText, NgramModel, climb, encipher_homophonic, glyph_inventory,
                         key_accuracy, split_odd_even)
from ..results import TheoryResult
from .brute import QUICK_LANGUAGES
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs


def _attack(lines, lm: NgramModel, s: Climb, xp: Backend, order: int, log=None) -> dict:
    glyphs = glyph_inventory(lines)
    odd, even = split_odd_even(lines)
    fit_text, held = GlyphText.build(odd, glyphs, order), GlyphText.build(even, glyphs, order)
    return climb(fit_text, lm, s, xp, held, log)


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    xp = Backend(prefer_gpu=True)
    names = cfg.attack_languages or (QUICK_LANGUAGES if cfg.quick else lexicon.available())
    names = [n for n in names if n in lexicon.available()]
    s = Climb(population=256 if cfg.quick else cfg.climb_population, steps=300 if cfg.quick else cfg.climb_steps,
              seed=cfg.seed)
    order = cfg.climb_order
    res = TheoryResult(
        theory="hillclimb",
        hypothesis="Tekst to szyfr homofoniczny (kilka glifów na literę) któregoś z języków epoki; klucz da się "
                   "odzyskać wspinaczką z modelem n-gramowym, jak w klasycznych łamaczach (AZdecrypt).",
        method=(f"Dla każdego z {len(names)} leksykonów: model {order}-gramowy znaków z próbki tekstu; {s.population} "
                f"wspinaczy równolegle na {xp.name} przez {s.steps} kroków (wyżarzanie), każdy zmienia literę jednego "
                "glifu; klucz dopasowany na wierszach nieparzystych, oceniany na parzystych (bity na znak). To samo dla "
                "bełkotu v5 o statystyce rękopisu. Kontrola dodatnia: tekst języka zaszyfrowany homofonicznie na tyle "
                "glifów, ile ma rękopis; wspinacz musi odzyskać klucz."),
        references=["Van Eycke, AZdecrypt (2017–2021)", "Nuhn, Schamper & Ney, Beam search for solving substitution "
                    "ciphers, ACL 2013", "Kambhatla, Bigvand & Sarkar, Decipherment of substitution ciphers with "
                    "neural language models, EMNLP 2018"])
    lines = paragraph_lines("glyphs")
    n_glyphs = len(glyph_inventory(lines))
    gen = [[tuple(w) for w in l] for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)
           + generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed + 1)]
    relabelled = relabel_lines(lines, cfg.seed)   # a fresh glyph permutation on every line: no key can exist
    log = (lambda m: print(m, flush=True)) if not cfg.quick else None
    metrics, leads, untestable = {}, [], []
    for name in names:
        try:
            _, _, text = lexicon.load_all(name)
        except Exception as e:
            res.evidence.append(f"{name}: pominięty ({e})")
            continue
        if len(text) < 3000:
            res.evidence.append(f"{name}: pominięty (za mała próbka tekstu)")
            continue
        cut = int(len(text) * 0.7)
        lm = NgramModel.fit(text[:cut], order)
        natural = lm.bits(text[cut:])
        enc, truth = encipher_homophonic(text[cut:], n_glyphs, cfg.seed)
        covered = sum(len(w) for l in enc for w in l) / max(1, sum(len(w) for w in text[cut:]))
        if covered < 0.5:
            res.evidence.append(f"{name}: nietestowalny – {n_glyphs} glifów niesie tylko {covered:.0%} tekstu tego pisma.")
            untestable.append(name)
            continue
        print(f"  {name}: tekst naturalny {natural:.2f} bit/znak", flush=True)
        pos = _attack(enc, lm, s, xp, order)
        acc = key_accuracy(pos["key"], truth, enc)
        ok = acc >= 0.6
        res.control(f"{name}: zaszyfrowany homofonicznie prawdziwy tekst", "klucz odzyskany w ≥ 60% znaków",
                    f"{acc:.0%} (wynik {pos['held_out_bits']:.2f} bit/znak wobec naturalnego {natural:.2f})", ok)
        if not ok:
            untestable.append(name)
        v = _attack(lines, lm, s, xp, order, log)
        g = _attack(gen, lm, s, xp, order)
        rl = _attack(relabelled, lm, s, xp, order)
        gap_gen = g["held_out_bits"] - v["held_out_bits"]          # positive: the manuscript decodes better
        gap_nat = v["held_out_bits"] - natural                    # how far from natural text
        lead = ok and gap_gen >= 0.2 and gap_nat <= 0.8
        metrics[name] = {"natural_bits": natural, "voynich": v, "generator": g, "relabelled": rl, "enciphered": pos,
                         "key_accuracy": acc, "gap_to_generator": gap_gen, "gap_to_natural": gap_nat, "lead": lead}
        if lead:
            leads.append(name)
        sample = " ".join("".join(v["key"].get(g, "?") for g in w) for w in lines[0][:8])
        res.evidence.append(f"{name}: rękopis {v['held_out_bits']:.2f} bit/znak, bełkot v5 {g['held_out_bits']:.2f}, "
                            f"glify przemianowane w każdym wierszu {rl['held_out_bits']:.2f} (bez klucza), "
                            f"tekst naturalny {natural:.2f}; zaszyfrowany tekst odczytany do {pos['held_out_bits']:.2f} "
                            f"z kluczem w {acc:.0%}. " + ("TROP. " if lead else "") + f"Odczyt pierwszego wiersza: „{sample}”.")
        print(f"  {name}: rękopis {v['held_out_bits']:.2f} | bełkot {g['held_out_bits']:.2f} | przemianowane {rl['held_out_bits']:.2f} | naturalny {natural:.2f} | "
              f"klucz {acc:.0%}" + (" TROP" if lead else ""), flush=True)
    res.controls = [c for c in res.controls if c.passed]
    tested = [n for n in metrics if n not in untestable]
    res.metrics = {"languages": metrics, "untestable": untestable, "n_glyphs": n_glyphs, "device": xp.name,
                   "population": s.population, "steps": s.steps}
    if leads:
        res.decide(True)
    elif len(tested) >= max(3, len(metrics) // 2):
        res.decide(False)
    else:
        res.decide(None)
    best = min(tested, key=lambda n: metrics[n]["gap_to_natural"]) if tested else None
    res.summary = (f"Tropy: {', '.join(leads) if leads else 'brak'}; {len(tested)} języków testowalnych, "
                   f"{len(untestable)} nietestowalnych. "
                   + (f"Najbliżej tekstu naturalnego: {best} ({metrics[best]['voynich']['held_out_bits']:.2f} wobec "
                      f"{metrics[best]['natural_bits']:.2f} bit/znak; bełkot {metrics[best]['generator']['held_out_bits']:.2f})."
                      if best else ""))
    res.caveats += ["Model języka z próbki ok. 8 tys. słów; dla szyfru z nullami, skrótami lub zmienną segmentacją "
                    "wspinaczka po samym kluczu glif–litera nie wystarczy.",
                    "Bełkot v5 ma statystykę rękopisu, więc wynik rękopisu musi go wyraźnie przebić, by coś znaczył."]
    res.seconds = time.time() - t0
    return res
