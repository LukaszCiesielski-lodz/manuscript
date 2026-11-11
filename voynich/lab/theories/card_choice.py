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

import re
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
    return lay, tokens, sections, lines, sorted(pages, key=pages.get)


def leaf(folio: str) -> str:
    """The physical leaf of a page: f1r and f1v (and f67r1, f67v2) are one leaf."""
    m = re.match(r"f(\d+)", folio)
    return m.group(1) if m else folio


def boundary_kinds(page_keys: list) -> dict:
    """For every page followed by a page of the same section: "ta sama karta" (recto to verso of one leaf, written one
    after the other) or "inna karta" (across leaves, whose order in the binding need not be the order of writing)."""
    out = {}
    for p in range(len(page_keys) - 1):
        (s0, f0), (s1, f1) = page_keys[p], page_keys[p + 1]
        if s0 == s1:
            out[p] = "ta sama karta" if leaf(f0) == leaf(f1) else "inna karta"
    return out


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
    lay, ms, sections, _, page_keys = manuscript_layout(cfg.quick)
    kinds = boundary_kinds(page_keys)
    chunks = K.chunk_inventory(ms)

    # controls: a known card, the choice in column 3 follows the page, drifts blind to pages, or neither
    ctl = {}
    for name, kw in (("strona", {"bias": 0.3}), ("dryf", {"bias": 0.3, "drift": 0.15}), ("nic", {"bias": 0.0})):
        syn, true = C.synthetic_pages(chunks, lay, cfg.seed, **kw)
        codes, _ = C.parse_tokens(true, chunks, syn)
        ctl[name] = (C.page_information(codes, lay, perms, cfg.seed), C.boundary_jump(codes, lay, 10, perms, cfg.seed))
    planted, pj = ctl["strona"]
    best_col = max(planted["columns"], key=lambda c: c["z"])["column"]
    res.control("kolumna z ulubionym wpisem każdej strony (30% wyborów) wykryta", "z ≥ 5, najsilniejsza kolumna 3, skok na granicy stron z ≥ 3",
                f"z = {planted['z']:.1f}, najsilniejsza kolumna {best_col}, skok z = {pj['z']:.1f}",
                planted["z"] >= 5 and best_col == 3 and pj["z"] >= 3)
    dz, dj = ctl["dryf"]
    res.control("ulubiony wpis dryfuje co kilka wierszy, ślepy na strony", "informacja o stronie z ≥ 5, skok |z| < 2,5",
                f"z = {dz['z']:.1f}, skok z = {dj['z']:.1f}", dz["z"] >= 5 and abs(dj["z"]) < 2.5)
    res.control("ten sam tekst bez ulubionych wpisów", "|z| < 2,5 (informacja i skok)",
                f"z = {ctl['nic'][0]['z']:.1f}, skok z = {ctl['nic'][1]['z']:.1f}",
                abs(ctl["nic"][0]["z"]) < 2.5 and abs(ctl["nic"][1]["z"]) < 2.5)

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
        bj = C.boundary_jump(codes, lay, 10, perms, cfg.seed, boundary_kind=kinds)
        hj = C.boundary_jump(codes[hmask], hlay, 10, perms, cfg.seed) if hi else None
        out[name] = {"card": pr["size"], "page": pi, "section": si, "herbal": hi, "jump": bj, "herbal_jump": hj}
        cards[name] = (codes, names)
        print(f"  {name}: karta {pr['size']} wpisów; informacja o stronie {pi['excess']:.3f} bitu/token "
              f"({pi['ratio']:.2%} entropii wyborów, z = {pi['z']:.1f})"
              + (f"; zielnik {hi['ratio']:.2%} (z = {hi['z']:.1f})" if hi else "")
              + f"; skok na granicy stron {bj['jump']:+.3f} (z = {bj['z']:.1f})", flush=True)
    res.metrics["texts"] = {k: {"card": v["card"], "page_ratio": v["page"]["ratio"], "page_excess": v["page"]["excess"],
                                "page_z": v["page"]["z"], "columns": v["page"]["columns"],
                                "section_ratio": [c["ratio"] for c in v["section"]],
                                "herbal_ratio": v["herbal"]["ratio"] if v["herbal"] else None,
                                "herbal_z": v["herbal"]["z"] if v["herbal"] else None,
                                "jump": v["jump"], "herbal_jump": v["herbal_jump"]} for k, v in out.items()}
    res.metrics["controls"] = {k: {"page_z": a["z"], "jump_z": b["z"]} for k, (a, b) in ctl.items()}

    def cols(name):
        return ", ".join(f"{c['column']}: {c['excess']:.3f} (z {c['z']:.0f})" for c in out[name]["page"]["columns"])

    res.evidence.append("Informacja wyborów o stronie ponad działem (udział entropii wyborów; z wobec tasowań wierszy): " + "; ".join(
        f"{k} {v['page']['ratio']:.2%} (z = {v['page']['z']:.1f}, karta {v['card']})" for k, v in out.items()) + ".")
    if all(v["herbal"] for v in out.values()):
        res.evidence.append("Sam zielnik (strona = roślina): " + "; ".join(
            f"{k} {v['herbal']['ratio']:.2%} (z = {v['herbal']['z']:.1f})" for k, v in out.items()) + ".")
    res.evidence.append("Skok na granicy stron (o ile wiersze tej samej strony są podobniejsze niż wiersze w tej samej odległości "
                        "po dwóch stronach granicy, względem średniego podobieństwa; z wobec granic przesuniętych): " + "; ".join(
        f"{k} {v['jump']['jump']:+.3f} (z = {v['jump']['z']:.1f})" + (f", zielnik {v['herbal_jump']['jump']:+.3f} (z = {v['herbal_jump']['z']:.1f})"
                                                                     if v["herbal_jump"] else "") for k, v in out.items()) + ".")
    res.evidence.append("Skok według rodzaju granicy (recto→verso tej samej karty, pisane po sobie, wobec granicy między kartami, "
                        "których kolejność w oprawie nie musi być kolejnością pisania): " + "; ".join(
        f"{k} " + ", ".join(f"{kk} {vv['jump']:+.3f} (z = {vv['z']:.1f}, {vv['boundaries']} granic)" for kk, vv in v["jump"].get("by_kind", {}).items())
        for k, v in out.items()) + ".")
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
    mj, vj, lj = (out[k]["jump"] for k in ("rękopis", "v7", "łacina"))
    more = ms_z >= 4 and ms_r >= 1.5 * v7_r and ms_r - v7_r >= 0.005
    unit = mj["z"] >= 4 and mj["jump"] >= max(vj["jump"], lj["jump"]) + 0.03
    base = (f"Wybory z karty niosą o stronie {ms_r:.2%} swojej entropii (v7 {v7_r:.2%}, łacina {lat_r:.2%}); skok na granicy stron: "
            f"rękopis {mj['jump']:+.3f} (z = {mj['z']:.1f}), v7 {vj['jump']:+.3f}, łacina {lj['jump']:+.3f}. ")
    if cfg.quick:
        res.decide(None)
        res.summary = "Tryb szybki. " + base
    elif more and unit and mj.get("by_kind", {}).get("ta sama karta", {}).get("z", 0) >= 3:
        res.decide(True)
        res.summary = base + ("Strony różnią się wyborami ponad dryf skryby, a skok jest także między recto i verso tej samej karty, "
                              "pisanymi po sobie: wybory idą za stroną (rysunkiem), nie tylko za czasem pisania.")
    elif more and unit:
        bk = mj.get("by_kind", {})
        res.decide(None)
        res.summary = base + ("Strony różnią się wyborami ponad dryf skryby i strona jest jednostką, ale skok siedzi głównie na granicach "
                              "między kartami" + (f" ({bk['inna karta']['jump']:+.3f}, z = {bk['inna karta']['z']:.1f}; recto→verso tej samej karty "
                                                  f"{bk['ta sama karta']['jump']:+.3f}, z = {bk['ta sama karta']['z']:.1f})" if len(bk) == 2 else "")
                              + ": to zgodne z kartami pisanymi w różnym czasie i przeszytymi potem w innej kolejności. Treści to nie wykazuje.")
    elif ms_r <= 1.15 * v7_r + 0.001 or mj["z"] < 2:
        res.decide(False)
        res.summary = base + ("Różnice między stronami tłumaczy dryf skryby: " +
                              ("nie są większe niż w v7." if ms_r <= 1.15 * v7_r + 0.001 else "nie ma skoku na granicy stron, wybory zmieniają się płynnie."))
    else:
        res.decide(None)
        res.summary = base + "Wynik między progami."
    res.caveats += ["v7 odtwarza dryf skryby tylko tak dobrze, jak dopasowano jego ustawienia (23 miary); nadmiar ponad v7 może być też "
                    "dryfem, którego v7 nie umie, a nie treścią.",
                    "Rozbiór słowa na kolumny nie zawsze jest jednoznaczny; wybieramy najbardziej prawdopodobny przy użyciu wpisów w tekście.",
                    "Skok na granicy strony pokazuje, że strona jest jednostką; nie odróżnia treści (roślina) od posiedzenia skryby "
                    "(jedna strona pisana naraz, z jednym zestawem nawyków).",
                    "Pomiar skoku dodany po pierwszym przebiegu (rękopis 2,6% wobec v7 0,7% i łaciny 2,0%), żeby oddzielić dryf od strony "
                    "jako jednostki; kontrola z dryfem ślepym na strony go uzasadnia.",
                    "Strona to jednostka, nie rysunek: w zielniku strona = roślina, w innych działach strona może mieć wiele rysunków."]
    res.seconds = time.time() - t0
    return res
