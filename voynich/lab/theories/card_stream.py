"""Theory: one word is one letter; the letter sits in the choice from one column (or two) of the master card.

See voynich.lab.cardstream. The master card (data/card/karta_matka.json, 242 entries, writes every
word) splits every word into its choices in six columns. Each column and each pair of columns
gives a stream of symbols, one a word. Stage 1 (CPU): how much a symbol tells about the next one,
against the words of every line shuffled; a hidden text must show here. Stage 2 (GPU): the
homophonic solver on the streams that show most, in Latin, Italian and German, on the manuscript
and on the manuscript with the words of every line shuffled; if a text is there, the true order
decodes better. Controls: the letters of a real text hidden in the same streams.
"""

from __future__ import annotations

import json
import time

from .. import card as K
from .. import cardchoice as C
from .. import cardstream as CS
from .. import hillclimb as H
from ..config import ROOT, LabConfig
from ..polybius import letters
from ..results import TheoryResult
from .card_choice import manuscript_layout


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    xp = H.Backend(prefer_gpu=True)
    gpu = xp.name == "cuda"
    langs = ["Latin"] if cfg.quick else list(cfg.stream_languages)
    top_n = 2 if cfg.quick else cfg.stream_top
    shuffles = 20 if cfg.quick else 100
    pop = (16 if cfg.quick else cfg.stream_population) if gpu else (4 if cfg.quick else min(8, cfg.stream_population))
    sweeps = (6 if cfg.quick else cfg.stream_sweeps) if gpu else (4 if cfg.quick else min(12, cfg.stream_sweeps))
    res = TheoryResult(
        theory="card_stream",
        hypothesis="Jedno słowo rękopisu to jedna litera tekstu jawnego: literę niesie wybór z jednej kolumny karty matki (albo para "
                   "wyborów z dwóch kolumn), reszta słowa to wypełniacz.",
        method=("Karta matka 242 wpisów (GPU, składa 100% słów) rozbija każde słowo na wybory w 6 kolumnach; każda kolumna i każda para "
                "kolumn daje strumień symboli, jeden na słowo (21 strumieni). Etap 1: ile symbol mówi o następnym symbolu wiersza ponad "
                f"to samo po przetasowaniu słów w wierszach ({shuffles} tasowań). Etap 2: łamacz homofoniczny ({pop} kluczy, {sweeps} przejść po symbolach: "
                f"dla symbolu wszystkie litery naraz; model 4-gramowy liter bez spacji, {xp.name}) na {top_n} strumieniach z największym nadmiarem, w językach: "
                f"{', '.join(langs)}; klucz z co drugiego wiersza, ocena na pozostałych (bity na symbol); rękopis wobec rękopisu ze słowami "
                "przetasowanymi w wierszach. Kontrole: litery prawdziwego tekstu ukryte w tych samych strumieniach (te same symbole, "
                "częstości i długości wierszy, kilka symboli na częstą literę)."),
        references=["Greshko, Cryptologia (2025): the Naibbe cipher", "Nuhn, Schamper & Ney, ACL 2013", "Van Eycke, AZdecrypt"])
    lay, ms, _, _, _ = manuscript_layout(False)
    chunks = K.chunk_inventory(ms)
    card = K.card_from_table(json.loads((ROOT / "data" / "card" / "karta_matka.json").read_text(encoding="utf-8"))["1.0"], chunks)
    codes, _ = C.parse_tokens(card, chunks, ms)
    st = CS.streams(codes, lay)

    # stage 1: does any stream have the memory of a text?
    info = {name: CS.sequence_information(lines, shuffles, cfg.seed) for name, lines in st.items()}
    ranked = sorted(info, key=lambda k: -info[k]["excess"])
    latin = letters("Latin")
    cut = int(len(latin) * 0.7)
    ctl_info = {name: CS.sequence_information(CS.hide(latin[cut:], st[name], cfg.seed)[0], max(10, shuffles // 5), cfg.seed)
                for name in ("k3", "k3+k4")}
    res.control("litery łaciny ukryte w kolumnie 3 i w parze kolumn 3+4: pamięć strumienia", "nadmiar ≥ 0,2 bitu i z ≥ 10 w obu",
                "; ".join(f"{k}: {v['excess']:.2f} bitu (z = {v['z']:.0f})" for k, v in ctl_info.items()),
                all(v["excess"] >= 0.2 and v["z"] >= 10 for v in ctl_info.values()))
    res.evidence.append("Pamięć strumieni rękopisu (bity, które symbol mówi o następnym, ponad tasowanie; od największej): " + "; ".join(
        f"{k} {info[k]['excess']:.3f} (z = {info[k]['z']:.0f}, {info[k]['symbols']} symboli)" for k in ranked[:8])
        + f"; najsłabszy {ranked[-1]} {info[ranked[-1]]['excess']:.3f}. Ukryty tekst łaciński: "
        + ", ".join(f"{k} {v['excess']:.2f}" for k, v in ctl_info.items()) + ".")
    res.metrics["sequence"] = info
    res.metrics["sequence_control"] = ctl_info

    # stage 2: the solver on the streams with most memory
    tested = ranked[:top_n]
    log = (lambda m: print(m, flush=True)) if not cfg.quick else (lambda m: None)
    solved, leads, testable = {}, [], 0
    for lang in langs:
        text = letters(lang)
        cut = int(len(text) * 0.7)
        for name in tested:
            lines = st[name]
            lm = H.NgramModel.fit(CS.pieces(text[:cut], lines), 4)
            natural = lm.bits(CS.pieces(text[cut:cut + 40000], lines))
            hid, truth = CS.hide(text[cut:], lines, cfg.seed)
            c = CS.solve(hid, lm, pop, sweeps, cfg.seed, xp)
            acc = CS.accuracy(c["key"], truth, hid)
            m = CS.solve(lines, lm, pop, sweeps, cfg.seed, xp)
            s = CS.solve(CS.shuffle_lines(lines, cfg.seed), lm, pop, sweeps, cfg.seed, xp)
            gain = s["held_out_bits"] - m["held_out_bits"]
            ok = acc >= 0.5
            testable += ok
            lead = ok and gain >= 0.15 and m["held_out_bits"] <= natural + 1.0
            if lead:
                leads.append((lang, name))
            solved[f"{lang} {name}"] = {"natural": natural, "control_accuracy": acc, "control_bits": c["held_out_bits"],
                                        "manuscript": m["held_out_bits"], "shuffled": s["held_out_bits"], "gain": gain,
                                        "symbols": m["symbols"], "lead": lead}
            log(f"  {lang} {name}: kontrola {acc:.0%} ({c['held_out_bits']:.2f} bitu, naturalny {natural:.2f}); rękopis "
                f"{m['held_out_bits']:.2f}, przetasowany {s['held_out_bits']:.2f}, zysk {gain:+.2f}")
            if lead or (lang == langs[0] and name == tested[0]):
                sample = "".join(m["key"].get(f"s{x}", "?") for l in lines[:12] for x in l)
                res.evidence.append(f"Odczyt strumienia {name} najlepszym kluczem ({lang}), pierwsze wiersze: {sample[:160]}")
    res.metrics["solver"] = solved
    for lang in langs:
        res.evidence.append(f"{lang} (bity na symbol; kontrola = trafność klucza na ukrytym tekście): " + "; ".join(
            f"{name}: kontrola {v['control_accuracy']:.0%}, rękopis {v['manuscript']:.2f}, przetasowany {v['shuffled']:.2f}, "
            f"zysk {v['gain']:+.2f}, naturalny {v['natural']:.2f}"
            for name in tested for v in [solved[f'{lang} {name}']]) + ".")
    res.control("łamacz czyta tekst ukryty w strumieniu (trafność klucza ≥ 50%)", "co najmniej jeden strumień w każdym języku",
                "; ".join(f"{lang}: " + ", ".join(f"{n} {solved[f'{lang} {n}']['control_accuracy']:.0%}" for n in tested) for lang in langs),
                cfg.quick or all(any(solved[f"{lang} {n}"]["control_accuracy"] >= 0.5 for n in tested) for lang in langs))

    best_info = info[ranked[0]]
    ok = [v for v in solved.values() if v["control_accuracy"] >= 0.5]
    hidden = min(v["excess"] for v in ctl_info.values())
    if cfg.quick:
        res.decide(None)
        res.summary = f"Tryb szybki: największa pamięć strumienia {ranked[0]} {best_info['excess']:.3f} bitu."
    elif leads:
        res.decide(True)
        res.summary = "Strumień wyborów czyta się jak tekst i lepiej w prawdziwej kolejności słów niż po przetasowaniu: " + ", ".join(
            f"{name} ({lang}: {solved[f'{lang} {name}']['manuscript']:.2f} bitu wobec naturalnych {solved[f'{lang} {name}']['natural']:.2f}, "
            f"zysk {solved[f'{lang} {name}']['gain']:+.2f})" for lang, name in leads) + "."
    elif ok and min(v["manuscript"] - v["natural"] for v in ok) >= 1.5:
        res.decide(False)
        gap = min(v["manuscript"] - v["natural"] for v in ok)
        res.summary = (f"Żaden strumień wyborów z karty nie niesie tekstu litera po literze. Pamięć najlepszego strumienia to "
                       f"{best_info['excess']:.3f} bitu ({ranked[0]}) wobec {hidden:.2f} bitu dla ukrytej łaciny. Łamacz, który czyta ukryty "
                       f"tekst ({len(ok)} par język–strumień z działającą kontrolą), z rękopisu wyciąga ciąg o co najmniej {gap:.1f} bitu na "
                       f"symbol gorszy niż język; kolejność słów pomaga mu najwyżej o {max(v['gain'] for v in ok):+.2f} bitu, tyle co znany "
                       "nawyk na styku słów.")
    elif ok:
        res.decide(None)
        res.summary = (f"Najlepszy odczyt rękopisu jest o {min(v['manuscript'] - v['natural'] for v in ok):.1f} bitu od języka, zysk z kolejności "
                       f"słów do {max(v['gain'] for v in ok):+.2f} bitu: między progami.")
    else:
        res.decide(None)
        res.summary = "Łamacz nie odczytał żadnej kontroli: strumienie nietestowalne przy tych ustawieniach."
    res.caveats += ["Sprawdzone: litera w jednej kolumnie albo w parze kolumn, jedno słowo = jedna litera. Nie sprawdzone: litera rozłożona "
                    "na trzy i więcej kolumn, litera jako całe słowo z wieloma zamiennikami (szyfr Naibbe), słowa-wypełniacze między literami.",
                    "Pominięcie kolumny liczy się jako symbol; jeśli słowa bez wpisu w danej kolumnie były pustymi znakami, łamacz dostaje "
                    "tekst z wtrąceniami i traci część sygnału.",
                    "Strumienie par kolumn mają po kilkaset symboli; łamacz bierze pod uwagę tylko symbole z co najmniej 10 wystąpieniami."]
    res.seconds = time.time() - t0
    return res
