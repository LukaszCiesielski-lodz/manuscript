"""Theory: the manuscript records something other than speech: a notation (melody, steps, procedure).

Real medieval notations are run through the lab's signature battery beside the manuscript,
languages and gibberish v5: plainchant from the Cantus database (Volpiano; units at the level of
text words, syllables and neumes), the basse danse step tablature of the Brussels manuscript,
and a modern program as the literal contrast. Measures: long-range dependency split into repeats,
variants and unrelated units; word-length dynamics; the shape measures of the scorecard as z
against the manuscript's own spread. A notation that shares the manuscript's defining trait (no
dependency between different units at a distance) and most of the rest would be a candidate for
what kind of record this is.
"""

from __future__ import annotations

import time

from ... import corpus, eva, hoax, lengths, longrange, notation
from ..config import LabConfig
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs

SHAPE = ["h2", "type_token_ratio", "hapax_ratio", "adjacent_near", "positional_rigidity"]


def _trim(lines, n):
    out, tot = [], 0
    for l in lines:
        out.append([list(w) for w in l])
        tot += len(l)
        if tot >= n:
            break
    return out


def _criteria(syn, dyn, zs) -> dict:
    return {"brak składni na odległość": syn["unrelated"]["z"] < 2.5, "nadmiar powtórzeń": syn["same"]["z"] > 3,
            "nadmiar wariantów": syn["variants"]["z"] > 3, "sąsiedzi podobnej długości": dyn["ac1"]["value"] > 0.08,
            "pamięć długości (DFA > 0,55)": dyn["dfa"]["value"] > 0.55,
            "entropia h₂ jak rękopis": abs(zs.get("h2", 9)) < 3, "słownictwo jak rękopis": abs(zs.get("type_token_ratio", 9)) < 3,
            "hapaksy jak rękopis": abs(zs.get("hapax_ratio", 9)) < 3}


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 8 if cfg.quick else 20
    res = TheoryResult(
        theory="notation",
        hypothesis="Rękopis jest zapisem niejęzykowym (melodia, kroki, procedura): jego statystyka przypomina notacje "
                   "średniowieczne bardziej niż mowę.",
        method=("Chorał gregoriański z bazy Cantus (Volpiano, jednostki: słowa tekstu, sylaby, neumy), tabulatura basse "
                "danse (Bruksela 9085), kod Pythona jako kontrast, łacina i bełkot v5; każdy tekst przycięty do liczby "
                "słów rękopisu. Zależność na odległość rozbita na powtórzenia, warianty i jednostki niespokrewnione; dynamika "
                "długości jednostek; miary kształtu jako z wobec rozrzutu bloków rękopisu. Osiem kryteriów podpisu rękopisu; "
                "cecha definiująca: brak zależności między różnymi jednostkami na odległość 2–7."),
        references=["Cornelissen, Zuidema & Burgoyne, Mode classification and natural units in plainchant, ISMIR 2020 "
                    "(CantusCorpus)", "Brussels, KBR ms. 9085, Les basses danses de Marguerite d'Autriche (c. 1470)",
                    "Crane, Materials for the study of the fifteenth century basse danse (1968)"])
    voy = [[eva.glyphs(w) for w in l.words] for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    n = sum(map(len, voy))
    stick = hoax.yardstick(voy)
    texts = {"rękopis": voy}
    try:
        for lvl, label in (("word", "chorał: słowa tekstu"), ("syllable", "chorał: sylaby"), ("neume", "chorał: neumy")):
            texts[label] = _trim(notation.chant_lines(lvl, limit=None), n)
    except FileNotFoundError:
        res.evidence.append("Brak chorału: uruchom scripts/fetch_notation.py.")
    dances = notation.dance_lines()
    full = notation.DIR / "basse_danse_full.txt"
    if full.exists():
        dances = [[tuple(t) for t in notation.STEP.findall(raw)] for raw in full.read_text(encoding="utf-8").splitlines() if raw.strip()]
    if sum(map(len, dances)) >= 300:
        texts["basse danse"] = [[list(w) for w in l] for l in dances]
    else:
        res.evidence.append(f"Basse danse: tylko {sum(map(len, dances))} kroków w dostępnej próbce, za mało na miary; "
                            "pełne wydanie pobiera scripts/fetch_notation.py, gdy jest dostępne.")
    texts["kod Python"] = _trim(notation.code_lines(), n)
    texts["łacina"] = _trim([[tuple(w) for w in corpus.load_reference("Latin")[i:i + 9]] for i in range(0, n, 9)], n)
    texts["bełkot v5"] = [[list(w) for w in l] for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)]
    if len(texts) < 4:
        res.decide(None)
        res.summary = "Pominięte: brak danych notacji."
        res.seconds = time.time() - t0
        return res
    # Controls: the chant with its units shuffled inside each melody must lose the distant dependency; the manuscript
    # with a planted frame (every third unit fixed) must gain one.
    import random as _random
    rr = _random.Random(cfg.seed)
    chant_key = next((k for k in texts if k.startswith("chorał")), None)
    if chant_key:
        within = []
        for l in texts[chant_key]:
            l = list(l)
            rr.shuffle(l)
            within.append(l)
        flat = [w for l in texts[chant_key] for w in l]
        rr.shuffle(flat)
        across, i = [], 0
        for l in texts[chant_key]:
            across.append(flat[i:i + len(l)])
            i += len(l)
        syn_w = longrange.split_by_identity(within, top=60, shuffles=shuffles, seed=cfg.seed)
        syn_a = longrange.split_by_identity(across, top=60, shuffles=shuffles, seed=cfg.seed)
        res.control("chorał z jednostkami przetasowanymi między melodiami traci składnię na odległość", "z < 3",
                    f"z = {syn_a['unrelated']['z']:.1f}", syn_a["unrelated"]["z"] < 3)
        res.evidence.append(f"Chorał przetasowany tylko w obrębie melodii zachowuje część zależności (z = {syn_w['unrelated']['z']:.1f}): "
                            "jednostki jednej melodii dzielą modus i zakres, więc u chorału część „składni” to spójność melodii, "
                            "nie kolejność. Rękopis nie ma ani jednego, ani drugiego.")
    frame = [[w if i % 3 else ["o", "r", "a"] for i, w in enumerate(l)] for l in voy]
    syn_fr = longrange.split_by_identity(frame, top=60, shuffles=shuffles, seed=cfg.seed)
    res.control("rękopis z wszczepioną ramą (co trzecia jednostka stała) zyskuje składnię na odległość", "z ≥ 5",
                f"z = {syn_fr['unrelated']['z']:.1f}", syn_fr["unrelated"]["z"] >= 5)
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
        scores[name] = sum(crit.values())
        metrics[name] = {"words": nw, "glyphs": len({g for l in lines for w in l for g in w}), "syntax": syn,
                         "lengths": {k: dyn[k] for k in ("ac1", "updown", "dfa")}, "shape_z": zs, "criteria": crit}
        res.evidence.append(f"{name} ({nw} jednostek, {metrics[name]['glyphs']} znaków): powtórzenia z = {syn['same']['z']:.1f}, "
                            f"warianty z = {syn['variants']['z']:.1f}, niespokrewnione z = {syn['unrelated']['z']:.1f}; długości: "
                            f"korelacja sąsiadów {dyn['ac1']['value']:+.2f}, DFA {dyn['dfa']['value']:.2f}; kształt wobec rękopisu: "
                            + ", ".join(f"{hoax.MEASURES[k]} {z:+.1f}" for k, z in zs.items())
                            + f". Kryteria podpisu: {scores[name]}/8" + ("" if crit["brak składni na odległość"] else
                                                                      ", w tym BRAK cechy definiującej (składnia na odległość)") + ".")
    res.metrics = metrics
    notations = [k for k in texts if k.startswith("chorał") or k == "basse danse"]
    match = [k for k in notations if metrics[k]["criteria"]["brak składni na odległość"] and scores[k] >= 6]
    strong_syntax = all(metrics[k]["syntax"]["unrelated"]["z"] > 5 for k in notations) if notations else False
    res.decide(True if match else (False if strong_syntax else None))
    like = sorted(((scores[k], k) for k in texts if k != "rękopis"), reverse=True)
    res.summary = ("Kryteria podpisu rękopisu spełnione: " + ", ".join(f"{k} {s}/8" for s, k in like) + ". "
                   + ("Notacja o podpisie rękopisu: " + ", ".join(match) + "." if match else
                      "Chorał i kod mają silną składnię na odległość (niespokrewnione jednostki z = "
                      + ", ".join(f"{metrics[k]['syntax']['unrelated']['z']:.0f}" for k in notations) + "), której rękopis nie ma "
                      f"(z = {metrics['rękopis']['syntax']['unrelated']['z']:.1f}); dzielą z nim za to dynamikę długości "
                      "(dodatnia korelacja sąsiadów, DFA powyżej języków)." if strong_syntax else "Wynik niejednoznaczny."))
    res.caveats += ["Jednostki chorału zależą od poziomu podziału (słowo, sylaba, neuma); policzono wszystkie trzy.",
                    "Tabulatura basse danse w dostępnej próbce jest za krótka; pełne wydanie (59 tańców) wymaga pobrania PDF.",
                    "Melodie w Volpiano to wysokości bezwzględne; zapis interwałowy mógłby dać inny obraz powtórzeń."]
    res.seconds = time.time() - t0
    return res
