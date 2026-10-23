"""Theory: the manuscript's statistical signature holds in every scholarly transliteration.

Everything the lab concluded was measured on the Zandbergen-Landini transliteration. Here the
three measures that carry the verdicts (no long-range dependency between different words, an
excess of repeats and one-glyph variants, neighbours of similar length) plus the shape measures
are recomputed on Currier-D'Imperio, FSG, v101, Takahashi and the reference transliteration.
A signature that depends on who transcribed the pages would be a property of a transcription,
not of the manuscript.
"""

from __future__ import annotations

import time

from ... import hoax, lengths, longrange, transliterations as tr
from ..config import LabConfig
from ..results import TheoryResult

SHAPE = ["h2", "type_token_ratio", "hapax_ratio", "adjacent_near", "len_neighbour"]


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 8 if cfg.quick else 20
    res = TheoryResult(
        theory="transcriptions",
        hypothesis="Podpis statystyczny rękopisu (brak dalekiej składni między różnymi słowami, nadmiar powtórzeń "
                   "i wariantów, podobne długości sąsiadów) jest własnością rękopisu, nie transliteracji ZL.",
        method=("Te same miary na każdej dostępnej transliteracji z voynich.nu: Zandbergen-Landini, Takahashi "
                "(dwie wersje), Reference, Currier-D'Imperio, FSG, v101. Alfabety nie-EVA tokenizowane po znaku. "
                "Składnia na odległość rozbita na powtórzenia, warianty i słowa niespokrewnione (z wobec tasowań "
                "w stronie i miejscu w wierszu); dynamika długości (korelacja sąsiadów, DFA); miary kształtu "
                "jako z wobec rozrzutu bloków ZL."),
        references=["Zandbergen, voynich.nu/transcr.html", "Chelednik, voynich-transcription-mismatch (Hugging Face 2026)"])
    ids = tr.available()
    if ids == ["ZL"]:
        res.evidence.append("Brak innych transliteracji: uruchom scripts/fetch_transliterations.py.")
        res.decide(None)
        res.summary = "Pominięte: tylko ZL dostępne."
        res.seconds = time.time() - t0
        return res
    zl = [[list(w) for w in l] for l in tr.load_lines("ZL")]
    stick = hoax.yardstick(zl)
    zl_words = sum(map(len, zl))
    metrics, holds = {}, []
    for tid in ids:
        lines = [[list(w) for w in l] for l in tr.load_lines(tid)]
        n_words = sum(map(len, lines))
        syn = longrange.split_by_identity(lines, top=60, shuffles=shuffles, seed=cfg.seed)
        dyn = lengths.describe(lengths.series([w for l in lines for w in l]), shuffles=shuffles, seed=cfg.seed)
        card = hoax.scorecard(lines, stick)
        zs = {k: card[k]["z"] for k in SHAPE if k in card}
        glyphs = len({g for l in lines for w in l for g in w})
        ok = syn["unrelated"]["z"] < 2.5 and syn["same"]["z"] > 3 and dyn["ac1"]["value"] > 0.05
        complete = n_words >= 0.8 * zl_words        # Currier's transliteration covers under half the text
        if complete:
            holds.append(ok)
        metrics[tid] = {"name": tr.SOURCES[tid][0], "words": n_words, "glyphs": glyphs, "syntax": syn,
                        "lengths": {k: dyn[k] for k in ("ac1", "updown", "dfa")}, "shape_z": zs, "holds": ok,
                        "complete": complete}
        res.evidence.append(
            f"{tid} ({tr.SOURCES[tid][0]}; {n_words} słów, {glyphs} znaków): słowa niespokrewnione z = "
            f"{syn['unrelated']['z']:.1f}, powtórzenia z = {syn['same']['z']:.1f}, warianty z = {syn['variants']['z']:.1f}; "
            f"korelacja długości sąsiadów {dyn['ac1']['value']:+.3f}, DFA {dyn['dfa']['value']:.3f}; kształt wobec ZL: "
            + ", ".join(f"{hoax.MEASURES[k]} {z:+.1f}" for k, z in zs.items()) + f". Podpis {'trzyma' if ok else 'NIE trzyma'}"
            + ("" if complete else " (transliteracja częściowa, poza werdyktem)") + ".")
    res.metrics = metrics
    res.decide(all(holds))
    res.summary = (f"Podpis trzyma w {sum(holds)}/{len(holds)} pełnych transliteracjach: "
                   + ", ".join(f"{t} {'tak' if m['holds'] else 'nie'}" + ("" if m["complete"] else " (częściowa)")
                               for t, m in metrics.items()) + ".")
    res.caveats += ["ZL i Takahashi są w pełni zgodne tylko w ok. 29% wierszy (Chelednik); różnice to głównie "
                    "niepewne glify i podziały słów.",
                    "Alfabety Curriera, FSG i v101 dzielą tekst na inne jednostki niż EVA, więc miary kształtu "
                    "(entropia, długości) nie są z nimi wprost porównywalne; porównywalne są z składni i znak korelacji."]
    res.seconds = time.time() - t0
    return res
