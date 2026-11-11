"""Theory: the meaning, if any, sits in which entries of the master card the scribe chose.

See voynich.lab.cardchoice. A card of ~240 entries writes every word (master_card_full), so words
are composed; the only place left for content is the choice made in each column. Measured: how
much the choices tell about the page beyond its section (each herbal page is one plant), against
lines shuffled among the pages of their section. The scribe's drift makes pages differ even
without content, so v7 gibberish (drift and self-citation, no meaning) is the yardstick, and Latin
laid into the same lines and pages shows what a text with topics gives. Every text gets its own
card, found the same way (pruning the full card to 100% of the tokens).
"""

from __future__ import annotations

import time

import numpy as np

from ... import corpus, eva
from .. import card as K
from .. import cardchoice as C
from ..config import LabConfig
from ..nomen2 import array_module
from ..results import TheoryResult
from .nomenclator2 import all_runs, v7


def manuscript_layout(quick: bool = False):
    """Paragraph lines of the manuscript, their pages (section, folio) and sections; with quick, the first 40 pages."""
    lines = [l for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    pages: dict = {}
    for l in lines:
        pages.setdefault((l.section, l.folio), len(pages))
    if quick:
        lines = [l for l in lines if pages[(l.section, l.folio)] < 40]
        pages = {k: v for k, v in pages.items() if v < 40}
    sections = sorted({k[0] for k in pages})
    lay = C.Layout([len(l.words) for l in lines], [pages[(l.section, l.folio)] for l in lines],
                   [sections.index(k[0]) for k in sorted(pages, key=pages.get)])
    tokens = [tuple(eva.glyphs(w)) for l in lines for w in l.words]
    return lay, tokens, sections, lines


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    gpu = array_module().__name__ == "cupy"
    pop = (16 if cfg.quick else cfg.card_prune_population) if gpu else (2 if cfg.quick else 4)
    perms = 40 if cfg.quick else cfg.card_choice_permutations
    Kc = cfg.card_columns
    res = TheoryResult(
        theory="card_choice",
        hypothesis="Treść (jeśli jest) siedzi w tym, który wpis karty matki skryba wybrał z każdej kolumny: wybory zależą od strony "
                   "(rysunku) bardziej, niż wynika z samego dryfu skryby.",
        method=(f"Każdy tekst dostaje własną kartę ({Kc} kolumn) z przycinania karty pełnej do 100% tokenów ({pop} kart, "
                f"{'cupy/GPU' if gpu else 'numpy/CPU'}). Każdy token rozbity na wybory w kolumnach (najbardziej prawdopodobny rozbiór "
                "przy użyciu wpisów w tym tekście). Miara: informacja wyboru o stronie ponad działem, I(wybór; strona) − I(wybór; dział), "
                f"wobec {perms} tasowań całych wierszy między strony tego samego działu; suma po kolumnach odniesiona do entropii wyborów. "
                "Teksty w tym samym układzie wierszy, stron i działów: rękopis, bełkot v7 (dryf i samocytowanie bez treści, miara "
                "odniesienia), łacina ułożona w wiersze rękopisu (tekst z tematami). Osobno sam zielnik (jedna strona = jedna roślina). "
                "Kontrole: tekst pisany znaną kartą, w którym jedna kolumna ma ulubiony wpis każdej strony (30% wyborów), i ten sam "
                "tekst bez ulubionych wpisów."),
        references=["Stolfi, crust–mantle–core paradigm of Voynichese words", "Montemurro & Zanette, PLoS ONE 8 (2013): keywords by section",
                    "Timm & Schinner, Cryptologia 44 (2020): self-citation"])
    lay, ms, sections, _ = manuscript_layout(cfg.quick)
    chunks = K.chunk_inventory(ms)

    # controls: a known card, the choice in column 3 follows the page (or not)
    ctl = {}
    for bias in (0.3, 0.0):
        syn, true = C.synthetic_pages(chunks, lay, cfg.seed, bias=bias)
        codes, _ = C.parse_tokens(true, chunks, syn)
        ctl[bias] = C.page_information(codes, lay, perms, cfg.seed)
    planted = ctl[0.3]
    best_col = max(planted["columns"], key=lambda c: c["z"])["column"]
    res.control("kolumna z ulubionym wpisem każdej strony (30% wyborów) wykryta", "z ≥ 5 i najsilniejsza kolumna 3",
                f"z = {planted['z']:.1f}, najsilniejsza kolumna {best_col}", planted["z"] >= 5 and best_col == 3)
    res.control("ten sam tekst bez ulubionych wpisów", "|z| < 2,5", f"z = {ctl[0.0]['z']:.1f}", abs(ctl[0.0]["z"]) < 2.5)

    g_lines, _, _ = v7(all_runs(), cfg.seed)
    texts = {"rękopis": ms,
             "v7": lay.fill([tuple(w) for l in g_lines for w in l]),
             "łacina": lay.fill([tuple(w) for w in corpus.load_reference("Latin")])}
    herbal = {p for p, s in enumerate(lay.page_section) if sections[s] == "herbal"}
    hlay, hmask = lay.subset(herbal) if herbal else (None, None)
    log = (lambda m: print(m, flush=True)) if not cfg.quick else None
    out, cards = {}, {}
    for name, toks in texts.items():
        ch = chunks if name != "łacina" else K.chunk_inventory(toks)
        enc = K.Encoded(toks, ch, max_len=18)
        pr = K.prune(enc, ch, Kc, 1.0, pop, cfg.seed, log=log)
        codes, names = C.parse_tokens(pr["card"], ch, toks)
        pi = C.page_information(codes, lay, perms, cfg.seed)
        si = C.section_information(codes, lay, perms, cfg.seed)
        hi = C.page_information(codes[hmask], hlay, perms, cfg.seed) if hlay is not None and len(herbal) > 3 else None
        out[name] = {"card": pr["size"], "page": pi, "section": si, "herbal": hi}
        cards[name] = (codes, names)
        print(f"  {name}: karta {pr['size']} wpisów; informacja o stronie {pi['excess']:.3f} bitu/token "
              f"({pi['ratio']:.2%} entropii wyborów, z = {pi['z']:.1f})"
              + (f"; zielnik {hi['ratio']:.2%} (z = {hi['z']:.1f})" if hi else ""), flush=True)
    res.metrics["texts"] = {k: {"card": v["card"], "page_ratio": v["page"]["ratio"], "page_excess": v["page"]["excess"],
                                "page_z": v["page"]["z"], "columns": v["page"]["columns"],
                                "section_ratio": [c["ratio"] for c in v["section"]],
                                "herbal_ratio": v["herbal"]["ratio"] if v["herbal"] else None,
                                "herbal_z": v["herbal"]["z"] if v["herbal"] else None} for k, v in out.items()}
    res.metrics["controls"] = {"planted_z": planted["z"], "planted_column": best_col, "clean_z": ctl[0.0]["z"]}

    def cols(name):
        return ", ".join(f"{c['column']}: {c['excess']:.3f} (z {c['z']:.0f})" for c in out[name]["page"]["columns"])

    res.evidence.append("Informacja wyborów o stronie ponad działem (udział entropii wyborów; z wobec tasowań wierszy): " + "; ".join(
        f"{k} {v['page']['ratio']:.2%} (z = {v['page']['z']:.1f}, karta {v['card']})" for k, v in out.items()) + ".")
    if all(v["herbal"] for v in out.values()):
        res.evidence.append("Sam zielnik (strona = roślina): " + "; ".join(
            f"{k} {v['herbal']['ratio']:.2%} (z = {v['herbal']['z']:.1f})" for k, v in out.items()) + ".")
    res.evidence.append("Kolumny rękopisu (bity ponad tasowanie): " + cols("rękopis") + "; v7: " + cols("v7") + "; łacina: " + cols("łacina") + ".")
    res.evidence.append("Informacja o dziale (udział entropii, kolumny 1–6): " + "; ".join(
        f"{k} " + " ".join(f"{c['ratio']:.2f}" for c in v["section"]) for k, v in out.items()) + ".")

    # which pieces follow the page most: top entries by excess concentration in the manuscript (descriptive)
    codes, names = cards["rękopis"]
    ok = codes[:, 0] >= 0
    page_t = lay.line_page[lay.token_line[ok]]
    tops = []
    for k in range(codes.shape[1]):
        x = codes[ok, k]
        for v in np.unique(x):
            if v == 0:
                continue
            sel = x == v
            n = int(sel.sum())
            if n < 50:
                continue
            share = np.bincount(page_t[sel], minlength=int(lay.line_page.max()) + 1) / n
            tops.append((float(np.sort(share)[-3:].sum()), k + 1, names[k][v], n))
    tops.sort(reverse=True)
    res.evidence.append("Wpisy rękopisu najbardziej skupione na kilku stronach (udział 3 stron, kolumna, kawałek, wystąpienia): "
                        + "; ".join(f"{s:.0%} k{k} {g} ({n})" for s, k, g, n in tops[:8]) + ".")

    ms_r, v7_r, lat_r = (out[k]["page"]["ratio"] for k in ("rękopis", "v7", "łacina"))
    ms_z = out["rękopis"]["page"]["z"]
    if cfg.quick:
        res.decide(None)
        res.summary = f"Tryb szybki: wybory rękopisu niosą {ms_r:.2%} entropii o stronie, v7 {v7_r:.2%}, łacina {lat_r:.2%}."
    elif ms_z >= 4 and ms_r >= 1.5 * v7_r and ms_r - v7_r >= 0.005:
        res.decide(True)
        res.summary = (f"Wybory z karty zależą od strony wyraźnie bardziej niż w bełkocie v7 ({ms_r:.2%} wobec {v7_r:.2%} entropii "
                       f"wyborów; łacina {lat_r:.2%}): strony różnią się wyborami ponad dryf skryby, czyli tam może siedzieć treść.")
    elif ms_r <= 1.15 * v7_r + 0.001:
        res.decide(False)
        res.summary = (f"Wybory z karty zależą od strony nie bardziej niż w bełkocie v7 ({ms_r:.2%} wobec {v7_r:.2%} entropii wyborów; "
                       f"łacina {lat_r:.2%}): różnice między stronami tłumaczy sam dryf skryby.")
    else:
        res.decide(None)
        res.summary = f"Wybory rękopisu niosą {ms_r:.2%} entropii o stronie, v7 {v7_r:.2%}, łacina {lat_r:.2%}: między progami."
    res.caveats += ["v7 odtwarza dryf skryby tylko tak dobrze, jak dopasowano jego ustawienia (23 miary); nadmiar ponad v7 może być też "
                    "dryfem, którego v7 nie umie, a nie treścią.",
                    "Rozbiór słowa na kolumny nie zawsze jest jednoznaczny; wybieramy najbardziej prawdopodobny przy użyciu wpisów w tekście.",
                    "Strona to jednostka, nie rysunek: w zielniku strona = roślina, w innych działach strona może mieć wiele rysunków."]
    res.seconds = time.time() - t0
    return res
