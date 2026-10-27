"""Theory: the paragraphs describe the plant drawn beside them (the same plant twice shares words).

See voynich.plantpairs. Zandbergen and Petersen point to plant fragments of the pharmaceutical
section that are, or resemble, plants of the herbal section. If the text is about the plant,
the two pages share vocabulary beyond random herbal pages of the same Currier language, and the
true partner ranks high among all herbal pages. Controls: words of the partner planted into the
pharma page (must be found), pairs rewired at random (must not).
"""

from __future__ import annotations

import time

from ... import plantpairs as PP
from ..config import LabConfig
from ..results import TheoryResult


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 300 if cfg.quick else 2000
    res = TheoryResult(
        theory="plant_pairs",
        hypothesis="Tekst opisuje roślinę narysowaną obok: strona farmaceutyczna i strona zielnika z tą samą rośliną dzielą "
                   "słowa ponad to, co dzielą losowe strony tego samego języka Curriera.",
        method=(f"Pary stron z data/plant_pairs.txt (Zandbergen, voynich.nu; Petersen): „ta sama roślina” i „podobna”. Miara: udział typów "
                "słów strony farmaceutycznej obecnych w stronie zielnika, ważony rzadkością słowa (idf po stronach); osobno udział etykiet "
                f"fragmentów (Lf) strony farmaceutycznej w tekście zielnika. Null: losowa strona zielnika tego samego języka ({shuffles} losowań), "
                "z i mediana rangi prawdziwego partnera wśród wszystkich stron zielnika tego języka. Kontrole: 10% słów strony farmaceutycznej "
                "zastąpionych słowami partnera (z ≥ 5); pary przełączone losowo (|z| < 2,5)."),
        references=["Zandbergen, voynich.nu: quires 15 and 19, cross-references of plant fragments (2025)",
                    "Petersen, marginal annotations in his transcription (1930s), as reported on voynich.nu"])
    pages = PP.load_pages()
    pairs = PP.load_pairs()
    idf = PP.idf_table(pages)
    planted = PP.evaluate(PP.plant(pages, pairs, 0.1, cfg.seed), pairs, idf, shuffles, cfg.seed)
    res.control("słowa partnera wszczepione (10%) wykryte", "z ≥ 5", f"z = {planted['z']:.1f}, mediana rangi {planted['median_rank']:.2f}", planted["z"] >= 5)
    rewired = PP.evaluate(pages, PP.rewire(pages, pairs, cfg.seed), idf, shuffles, cfg.seed)
    res.control("pary przełączone losowo bez związku", "|z| < 2,5", f"z = {rewired['z']:.1f}", abs(rewired["z"]) < 2.5)
    same = [p for p in pairs if p.strength == "same"]
    r_same = PP.evaluate(pages, same, idf, shuffles, cfg.seed)
    r_all = PP.evaluate(pages, pairs, idf, shuffles, cfg.seed)
    r_lab = PP.evaluate(pages, pairs, idf, shuffles, cfg.seed, measure=PP.label_hits)
    res.metrics = {"same": {k: v for k, v in r_same.items() if k != "ranks"}, "all": {k: v for k, v in r_all.items() if k != "ranks"},
                   "labels": {k: v for k, v in r_lab.items() if k != "ranks"}, "controls": {"planted": planted["z"], "rewired": rewired["z"]}}
    for name, r in (("ta sama roślina", r_same), ("wszystkie pary", r_all)):
        res.evidence.append(f"{name} ({r['pairs']} par): wspólne słownictwo {r['value']:.3f} wobec {r['null_mean']:.3f} dla losowych stron "
                            f"(z = {r['z']:+.1f}); mediana rangi prawdziwego partnera {r['median_rank']:.2f} (0 = najbliższa ze wszystkich stron "
                            "zielnika, 0,5 = przeciętna).")
    res.evidence.append(f"Etykiety fragmentów w tekście zielnika: {r_lab['value']:.1%} wobec {r_lab['null_mean']:.1%} (z = {r_lab['z']:+.1f}).")
    best = sorted(r_all["per_pair"], key=lambda t: t[4])[:5]
    res.evidence.append("Pary o najbliższym słownictwie: " + "; ".join(f"{a}–{b} ({s}, ranga {rk:.2f})" for a, b, s, v, rk in best)
                        + ". Najbliższe pary to sąsiedzi w tym samym zeszycie (f87–f90), nie pary „tej samej rośliny”: bliskość w kodeksie, nie treść.")
    z, rk = r_same["z"], r_same["median_rank"]
    if z >= 3 and rk <= 0.35:
        res.decide(True)
    elif abs(z) < 2 and 0.4 <= r_all["median_rank"] <= 0.75 and r_all["z"] < 2:
        res.decide(False)
    else:
        res.decide(None)
    res.summary = (f"Strony z tą samą rośliną nie dzielą słów ponad losowe strony: z = {z:+.1f}, mediana rangi {rk:.2f} (wszystkie pary: "
                   f"z = {r_all['z']:+.1f}, ranga {r_all['median_rank']:.2f}; etykiety z = {r_lab['z']:+.1f}); kontrola wszczepiona z = {planted['z']:.0f}. "
                   + ("Tekst nie mówi o tym, co jest narysowane." if res.verdict == "obalona" else ""))
    res.caveats += ["Pary z voynich.nu to oceny podobieństwa rysunków na oko; część może być błędna, ale 9 par „ta sama roślina” to "
                    "najpewniejsze z nich i te wypadają najgorzej.",
                    "Strony farmaceutyczne mają kilkanaście fragmentów; tekst o jednym z nich byłby małą częścią strony, stąd ważenie rzadkością."]
    res.seconds = time.time() - t0
    return res
