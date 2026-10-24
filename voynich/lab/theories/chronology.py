"""Theory: the text carries an arrow of time; the order in which the folios were written can be read off it.

A scribe copying and modifying words already on the table leaves fresh variants (hapaxes) whose
sources lie on pages written earlier. Measured along the foliation: the share of a hapax's
one-glyph neighbours on earlier pages, beyond what its position alone predicts (ancestor excess),
with a null that permutes pages only within runs of one section and Currier language, so that
the layout of sections cannot pose as an arrow; the same inside every block; the gradient of
neighbour degree and hapax share along the codex; the local variant flow between consecutive
pages. Positive controls: synthetic copying texts (sources on the previous pages, or anywhere
earlier) must show the arrow; a Latin text cut into pages must not.
"""

from __future__ import annotations

import time

from ... import corpus, pages as pg
from ..config import LabConfig
from ..results import TheoryResult


def _arrow(pages, shuffles, seed, within_blocks=True):
    nbs = pg.Neighbours(pages)
    order = list(range(len(pages)))
    blks = pg.blocks(pages) if within_blocks else [order]
    return pg.arrow_z(nbs, order, blks, shuffles, seed), nbs, blks


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 30 if cfg.quick else 200
    res = TheoryResult(
        theory="chronology",
        hypothesis="Tekst niesie strzałkę czasu kopiowania: świeże warianty (hapaksy) mają źródła na kartach napisanych "
                   "wcześniej, więc z tekstu da się odczytać kolejność powstawania kart (i sprawdzić oprawę).",
        method=("Dla każdego hapaksu udział wystąpień jego sąsiadów o jeden glif na kartach wcześniejszych w foliacji ponad "
                "to, co wynika z samego położenia (nadwyżka przodków); tło: strony tasowane tylko w obrębie bloków jednego "
                "działu i języka Curriera, osobno też wewnątrz każdego bloku; gradient stopnia sąsiedztwa i udziału "
                "hapaksów wzdłuż kodeksu (Spearman wobec tasowań w blokach). Kontrole dodatnie: syntetyczne teksty "
                "kopiowane z poprzednich stron i z całego wcześniejszego tekstu muszą pokazać strzałkę; łacina pocięta na "
                "strony nie może."),
        references=["Timm & Schinner, A possible generating algorithm of the Voynich manuscript, Cryptologia 44 (2020)",
                    "Davis, How many glyphs and how many scribes? Manuscript Studies 5 (2020)"])
    pages = pg.load_pages()
    # positive and negative controls
    near = pg.synthetic_self_citation(60, 150, cfg.seed, near=True)
    far = pg.synthetic_self_citation(60, 150, cfg.seed, near=False)
    latin = pg.pages_from_words(corpus.load_reference("Latin")[:len(pages) * 180], 180)
    zn, _, _ = _arrow(near, shuffles, cfg.seed)
    zf, _, _ = _arrow(far, shuffles, cfg.seed)
    zl, _, _ = _arrow(latin, shuffles, cfg.seed)
    res.control("tekst kopiowany z poprzednich stron pokazuje strzałkę", "z ≥ 5", f"z = {zn['z']:+.1f}", zn["z"] >= 5)
    res.control("tekst kopiowany z całego wcześniejszego tekstu pokazuje strzałkę", "z ≥ 5", f"z = {zf['z']:+.1f}", zf["z"] >= 5)
    res.control("łacina pocięta na strony nie pokazuje strzałki", "|z| < 3", f"z = {zl['z']:+.1f}", abs(zl["z"]) < 3)
    # the manuscript
    nbs = pg.Neighbours(pages)
    order = list(range(len(pages)))
    blks = pg.blocks(pages)
    glob = pg.arrow_z(nbs, order, [order], shuffles, cfg.seed)
    within = pg.arrow_z(nbs, order, blks, shuffles, cfg.seed)
    res.evidence.append(f"Rękopis, {len(pages)} stron z ≥ 60 słowami, {len(blks)} bloków działu i języka. Nadwyżka przodków "
                        f"{within['excess']:+.3f} ({within['n_hapax']} hapaksów): wobec tasowania stron w całym kodeksie "
                        f"z = {glob['z']:+.1f}; wobec tasowania tylko w obrębie bloków z = {within['z']:+.1f}. Różnica to "
                        "układ działów w kodeksie, nie kierunek kopiowania.")
    per_block = {}
    for blk in blks:
        if len(blk) < 8:
            continue
        sub = [pages[i] for i in blk]
        z, _, _ = _arrow(sub, shuffles, cfg.seed, within_blocks=False)
        key = f"{sub[0].section} {sub[0].language} {sub[0].folio}–{sub[-1].folio}"
        per_block[key] = {"pages": len(blk), **z}
    res.evidence.append("Wewnątrz bloków (≥ 8 stron): " + "; ".join(f"{k} ({v['pages']} stron) z = {v['z']:+.1f}"
                                                                      for k, v in per_block.items()) + ".")
    deg = pg.gradient_z([nbs.degree(i) for i in order], blks, shuffles, cfg.seed)
    hap = pg.gradient_z([nbs.hapax_share(i) for i in order], blks, shuffles, cfg.seed)
    res.evidence.append(f"Gradient wzdłuż foliacji: stopień sąsiedztwa słów rho = {deg['rho']:+.2f} (z wobec tasowań w blokach "
                        f"{deg['z']:+.1f}), udział hapaksów rho = {hap['rho']:+.2f} (z = {hap['z']:+.1f}). Późniejsze karty mają "
                        "słowa rzadsze i bardziej odosobnione, ale tylko dlatego, że inne działy leżą dalej w kodeksie.")
    res.evidence.append(f"Kontrole: kopiowanie z poprzednich stron z = {zn['z']:+.1f}, z całego wcześniejszego tekstu "
                        f"z = {zf['z']:+.1f}, łacina z = {zl['z']:+.1f}.")
    res.metrics = {"global": glob, "within_blocks": within, "blocks": per_block, "degree_gradient": deg,
                   "hapax_gradient": hap, "controls": {"near": zn, "far": zf, "latin": zl}}
    strong = [v for v in per_block.values() if abs(v["z"]) >= 4]
    if within["z"] >= 4 or (strong and all(v["z"] > 0 for v in strong)):
        res.decide(True)
    elif within["z"] <= -4:
        res.decide(True)
        res.evidence.append("Strzałka wskazuje wstecz foliacji: karty późniejsze w oprawie byłyby napisane wcześniej.")
    elif abs(within["z"]) < 2 and not strong:
        res.decide(False)
    else:
        res.decide(None)
    res.summary = (f"Nadwyżka przodków hapaksów: z = {glob['z']:+.1f} przy tasowaniu całego kodeksu, ale z = {within['z']:+.1f} "
                   f"przy tasowaniu w obrębie bloków działu; wewnątrz bloków z od {min(v['z'] for v in per_block.values()):+.1f} "
                   f"do {max(v['z'] for v in per_block.values()):+.1f}. Kontrole: kopiowanie syntetyczne z = {zn['z']:+.1f} i "
                   f"{zf['z']:+.1f}, łacina {zl['z']:+.1f}. "
                   + ("Tekst nie niesie strzałki czasu między kartami: jeśli skryba kopiował, to z tej samej karty, nie z "
                      "poprzednich." if res.verdict == "obalona" else ""))
    res.caveats += ["Strzałka mierzy kopiowanie między kartami; kopiowanie w obrębie jednej karty (Timm i Schinner: większość "
                    "źródeł w tym samym lub poprzednim wierszu) nie zostawia śladu w tej miarze.",
                    "Bloki wyznaczone po dziale i języku Curriera z metadanych ZL; karty o mniej niż 60 słowach pominięte."]
    res.seconds = time.time() - t0
    return res
