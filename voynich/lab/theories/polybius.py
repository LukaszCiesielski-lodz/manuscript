"""Theory: the text is hidden in the word lengths, two lengths per letter (Polybius square).

See voynich.lab.polybius. For each language the key is fitted to the manuscript's sequence of
word lengths (paragraphs, in glyphs) read in pairs from the first and from the second word, and
to the same lengths shuffled. A hidden text makes the real order read better than the shuffled
one; the control is a text of the language written in word lengths by a Polybius square.
"""

from __future__ import annotations

import random
import statistics
import time

from ... import corpus, eva
from .. import polybius as P
from ..config import LabConfig
from ..results import TheoryResult

LANGUAGES = ["Latin", "Hebrew", "Italian", "German"]


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    langs = LANGUAGES[:2] if cfg.quick else LANGUAGES
    iters, restarts, shuffles = (20000, 2, 1) if cfg.quick else (20000, 6, 3)
    res = TheoryResult(
        theory="polybius",
        hypothesis="Tekst jest ukryty w długościach słów: dwie kolejne długości to wiersz i kolumna litery w tablicy Polibiusza.",
        method=(f"Długości słów akapitów w glifach (9 i więcej = 9), czytane parami od pierwszego i od drugiego słowa (dwie fazy). "
                f"Klucz pole → litera (do 81 pól, kilka pól może mieć tę samą literę) szukany wyżarzaniem ({restarts} restartów × {iters} kroków) "
                f"na pełnej wiarygodności: trigramy liter języka + koszt emisji. Języki: {', '.join(langs)}. Rękopis wobec tych samych długości "
                f"przetasowanych ({shuffles}×). Kontrola: tekst języka zapisany długościami słów losową tablicą 5×5 musi zostać odczytany w ≥ 50%."),
        references=["Polybius, Historiae X.45–47 (kwadrat sygnałowy)", "Zandbergen, voynich.nu: word length distribution"])
    ms = [len(eva.glyphs(w)) for l in corpus.load_voynich() if l.kind.startswith("P") for w in l.words]
    r = random.Random(cfg.seed)
    rows = {}
    for lang in langs:
        txt = P.letters(lang)
        cut = int(len(txt) * 0.6)
        lm = P.TrigramLM(txt[:cut])
        natural = lm.bits(txt[cut:cut + 20000])
        enc, truth = P.encode(txt[cut:cut + len(ms) // 2], cfg.seed)
        sym = P.pairs(enc)
        key, b = P.solve(sym, lm, iters, restarts, cfg.seed)
        acc = sum(lm.alphabet[key[s]] == t for s, t in zip(sym, truth)) / len(truth)
        row = {"natural_bits": natural, "control_accuracy": acc, "control_bits": b, "phases": {}}
        for ph in (0, 1):
            k, bm = P.solve(P.pairs(ms, ph), lm, iters, restarts, cfg.seed)
            null = []
            for i in range(shuffles):
                sh = ms[:]
                r.shuffle(sh)
                null.append(P.solve(P.pairs(sh, ph), lm, iters, restarts, cfg.seed + 1 + i)[1])
            row["phases"][ph] = {"bits": bm, "shuffled": statistics.fmean(null),
                                 "shuffled_sd": statistics.pstdev(null) if len(null) > 1 else 0.0,
                                 "sample": P.decode(k, P.pairs(ms, ph)[:40], lm)}
        rows[lang] = row
        print(f"  {lang}: kontrola {acc:.2f}; rękopis " + ", ".join(
            f"faza {ph} {v['bits']:.2f} wobec {v['shuffled']:.2f}" for ph, v in row["phases"].items()), flush=True)
    res.metrics["languages"] = rows
    ok = [l for l in langs if rows[l]["control_accuracy"] >= 0.5]
    res.control("tekst zapisany długościami słów (tablica 5×5) odczytany", "≥ 0,5 w co najmniej jednym języku",
                ", ".join(f"{l} {rows[l]['control_accuracy']:.2f}" for l in langs), bool(ok))
    res.evidence.append("Bity na literę (rękopis wobec przetasowanego, faza 0 / faza 1; naturalnie): " + "; ".join(
        f"{l}: {rows[l]['phases'][0]['bits']:.2f}/{rows[l]['phases'][0]['shuffled']:.2f}, "
        f"{rows[l]['phases'][1]['bits']:.2f}/{rows[l]['phases'][1]['shuffled']:.2f} ({rows[l]['natural_bits']:.2f}); "
        f"kontrola {rows[l]['control_accuracy']:.2f}" for l in langs) + ".")
    res.evidence.append("Odczyt rękopisu (faza 0): " + "; ".join(f"{l} „{rows[l]['phases'][0]['sample']}”" for l in ok) + ".")
    hits = [(l, ph) for l in ok for ph, v in rows[l]["phases"].items()
            if v["bits"] <= v["shuffled"] - 0.15 and v["bits"] <= rows[l]["natural_bits"] + 1.0]
    flat = all(v["bits"] > v["shuffled"] - 0.05 for l in ok for v in rows[l]["phases"].values())
    if hits:
        res.decide(True)
        res.summary = "Kolejność długości czyta się lepiej niż przetasowana: " + ", ".join(f"{l} faza {ph}" for l, ph in hits)
    elif ok and flat:
        res.decide(False)
        res.summary = (f"Łamacz odczytuje tekst ukryty Polibiuszem w długościach słów ({', '.join(f'{l} {rows[l]['control_accuracy']:.2f}' for l in ok)}), "
                       "ale długości rękopisu w prawdziwej kolejności nie czytają się lepiej niż przetasowane w żadnym języku ani fazie.")
    else:
        res.decide(None)
        res.summary = "Wynik między progami."
    res.caveats += ["Sprawdzana jest tablica z jedną literą na pole (z dopuszczeniem kilku pól na literę); tablica z wierszem i kolumną "
                    "w innej kolejności niż kolejne słowa (np. co drugie słowo w wierszu) nie jest sprawdzona.",
                    "Długości słów zależą od podziału na słowa w transliteracji; wątpliwe odstępy zmieniają pojedyncze pary."]
    res.seconds = time.time() - t0
    return res
