"""Theory: the scribes wrote from one master card, a table of word pieces in ordered columns.

See voynich.lab.card. A card-key to a real text is already excluded by the solvers; this tests the
other kind of card: a recipe from which words are composed, one piece (or nothing) per column,
start to end. Measured: how much of each text a card of 40, 80, 120 and 200 entries can write,
for the manuscript, Latin, Italian, v7 gibberish, the manuscript with glyphs shuffled inside each
word (order of pieces destroyed) and a text written from a known card (positive control). Then
Currier A and B: a card fitted on one language and applied to the other, against the same between
two random halves of the pages of one language.
"""

from __future__ import annotations

import json
import random
import time

from ... import corpus, eva
from .. import card as K
from ..config import LabConfig
from ..nomen2 import array_module
from ..results import TheoryResult
from .nomenclator2 import all_runs, v7


def _tokens_by_page(kind_filter=lambda l: True):
    pages: dict[str, list] = {}
    for l in corpus.load_voynich():
        if l.kind.startswith("P") and l.words and kind_filter(l):
            pages.setdefault(l.folio, []).extend(tuple(eva.glyphs(w)) for w in l.words)
    return pages


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    gpu = array_module().__name__ == "cupy"
    pop = (8 if cfg.quick else cfg.card_population) if gpu else min(8 if cfg.quick else 32, cfg.card_population)
    gens = (30 if cfg.quick else cfg.card_generations) if gpu else min(30 if cfg.quick else 150, cfg.card_generations)
    budgets = [120] if cfg.quick else list(cfg.card_budgets)
    Kc = cfg.card_columns
    res = TheoryResult(
        theory="master_card",
        hypothesis="Skrybowie pisali z jednej karty-wzornika („karty matki”): tabeli kawałków słów w kolumnach od początku do końca słowa, "
                   "z której słowo składa się, biorąc z każdej kolumny co najwyżej jeden kawałek.",
        method=(f"Kawałki = n-gramy glifów (liter w językach), n ≤ 3, ≥ 20 wystąpień; karta = {Kc} kolumn, rozmiar = liczba wpisów. "
                "Słowo składalne, gdy da się je pociąć na kawałki z rosnących kolumn (programowanie dynamiczne dla wielu kart i wszystkich "
                f"typów naraz, {'cupy/GPU' if gpu else 'numpy/CPU'}). Najlepsza karta przy budżecie {', '.join(map(str, budgets))} wpisów "
                f"z ewolucji (populacja {pop}, {gens} pokoleń). Teksty: rękopis (akapity), łacina, włoski, bełkot v7, rękopis z glifami "
                "przetasowanymi w każdym słowie, tekst z prawdziwej karty 5 × 8 z 10% pomyłek (kontrola dodatnia); wszystkie tej samej "
                "liczby tokenów. A wobec B: karta jednego języka Curriera na drugim, wobec dwóch losowych połówek stron jednego języka."),
        references=["Stolfi, A prefix-midfix-suffix decomposition of Voynichese words (crust–mantle–core paradigm)",
                    "Rugg, Cryptologia 28 (2004): Cardan grille and a table of syllables",
                    "Zattera, CEUR-WS 3313 (2022): the slot alphabet",
                    "Timm & Schinner, Cryptologia 44 (2020)"])
    pages = _tokens_by_page()
    ms = [w for p in pages.values() for w in p]
    if cfg.quick:
        ms = ms[:8000]
    n = len(ms)
    g_lines, _, _ = v7(all_runs(), cfg.seed)
    texts = {"rękopis": ms,
             "łacina": [tuple(w) for w in corpus.load_reference("Latin")[:n]],
             "włoski": [tuple(w) for w in corpus.load_reference("Italian")[:n]],
             "v7": [tuple(w) for l in g_lines for w in l][:n],
             "przetasowany w słowie": K.shuffle_within(ms, cfg.seed)}
    ms_chunks = K.chunk_inventory(ms)
    syn, true = K.synthetic(ms_chunks, n, cfg.seed)
    texts["syntetyczny (prawdziwa karta)"] = syn
    if cfg.quick:
        texts = {k: v for k, v in texts.items() if k in ("rękopis", "łacina", "syntetyczny (prawdziwa karta)")}
    log = (lambda m: print(m, flush=True)) if not cfg.quick else None
    curves, best_ms = {}, {}
    for name, toks in texts.items():
        chunks = ms_chunks if name in ("rękopis", "syntetyczny (prawdziwa karta)") else K.chunk_inventory(toks)
        enc = K.Encoded(toks, chunks)
        curves[name] = {}
        for b in budgets:
            r = K.evolve(enc, toks, chunks, b, Kc, pop, gens, cfg.seed, log=log)
            curves[name][b] = r["coverage"]
            if name == "rękopis":
                best_ms[b] = r["card"]
            print(f"  {name}: budżet {b} → pokrycie {r['coverage']:.3f}", flush=True)
        if name == "syntetyczny (prawdziwa karta)":
            curves[name]["prawdziwa karta"] = K.evaluate(true, enc)
    res.metrics["coverage"] = curves
    ref = 120 if 120 in budgets else budgets[-1]
    c = {k: v[ref] for k, v in curves.items()}
    syn_true = curves["syntetyczny (prawdziwa karta)"]["prawdziwa karta"]
    res.control("karta odtworzona z tekstu pisanego prawdziwą kartą (5 × 8, 10% pomyłek)",
                f"pokrycie przy {ref} ≥ pokrycie prawdziwej karty − 0,05",
                f"{c['syntetyczny (prawdziwa karta)']:.3f} wobec {syn_true:.3f}", c["syntetyczny (prawdziwa karta)"] >= syn_true - 0.05)
    res.evidence.append("Pokrycie tokenów najlepszą kartą (budżet wpisów → udział słów, które da się z niej złożyć): " + "; ".join(
        f"{k}: " + ", ".join(f"{b} → {v:.2f}" for b, v in curves[k].items() if isinstance(b, int)) for k in curves) + ".")

    # Currier A against B, and random halves of one language as the background
    freq = {}
    for w in ms:
        for k in range(1, 4):
            for i in range(len(w) - k + 1):
                freq[w[i:i + k]] = freq.get(w[i:i + k], 0) + 1
    by_lang = {}
    for lang in ("A", "B"):
        pl = _tokens_by_page(lambda l, lang=lang: (l.language or "A") == lang)
        by_lang[lang] = pl
    ab = {}
    if not cfg.quick:
        def cross(p1: dict, p2: dict, label: str) -> dict:
            t1 = [w for p in p1.values() for w in p]
            t2 = [w for p in p2.values() for w in p]
            e1, e2 = K.Encoded(t1, ms_chunks), K.Encoded(t2, ms_chunks)
            k1 = K.evolve(e1, t1, ms_chunks, 120, Kc, pop, gens, cfg.seed)
            k2 = K.evolve(e2, t2, ms_chunks, 120, Kc, pop, gens, cfg.seed + 1)
            out = {"own_1": k1["coverage"], "on_2": K.evaluate(k1["card"], e2), "own_2": k2["coverage"], "on_1": K.evaluate(k2["card"], e1),
                   "shared_entries": int((k1["card"] & k2["card"]).sum()), "cards": (k1["card"], k2["card"])}
            out["drop"] = ((out["own_1"] - out["on_2"]) + (out["own_2"] - out["on_1"])) / 2
            print(f"  {label}: własne {out['own_1']:.3f}/{out['own_2']:.3f}, krzyżowo {out['on_2']:.3f}/{out['on_1']:.3f}, spadek {out['drop']:.3f}", flush=True)
            return out
        ab["A↔B"] = cross(by_lang["A"], by_lang["B"], "A↔B")
        r = random.Random(cfg.seed)
        for lang in ("A", "B"):
            folios = sorted(by_lang[lang])
            r.shuffle(folios)
            half = set(folios[: len(folios) // 2])
            ab[f"połówki {lang}"] = cross({f: by_lang[lang][f] for f in half}, {f: by_lang[lang][f] for f in folios if f not in half}, f"połówki {lang}")
        bg = max(ab["połówki A"]["drop"], ab["połówki B"]["drop"])
        res.metrics["a_b"] = {k: {kk: vv for kk, vv in v.items() if kk != "cards"} for k, v in ab.items()}
        two = ab["A↔B"]["drop"] > 3 * max(bg, 0.005)
        res.evidence.append(
            f"A wobec B (karta 120 wpisów): własne pokrycie A {ab['A↔B']['own_1']:.2f}, B {ab['A↔B']['own_2']:.2f}; karta A na B "
            f"{ab['A↔B']['on_2']:.2f}, karta B na A {ab['A↔B']['on_1']:.2f}; średni spadek {ab['A↔B']['drop']:.3f} wobec {bg:.3f} między "
            f"losowymi połówkami stron jednego języka; wspólne wpisy kart A i B: {ab['A↔B']['shared_entries']} ze 120. "
            + ("Języki A i B wyglądają jak dwie wersje karty." if two else "A i B mieszczą się w jednej karcie."))
        res.metrics["two_versions"] = two

    # the card itself, as a table
    out_dir = cfg.results_dir / "master_card"
    out_dir.mkdir(parents=True, exist_ok=True)
    fr = [freq.get(g, 0) for g in ms_chunks]
    cards = {"rękopis": best_ms.get(ref)}
    if ab:
        cards["język A"], cards["język B"] = ab["A↔B"]["cards"]
    md = ["# Karta matka: najlepsza karta 120 wpisów\n"]
    js = {}
    for name, cd in cards.items():
        if cd is None:
            continue
        cols = K.table(cd, ms_chunks, fr)
        js[name] = cols
        md.append(f"## {name}\n")
        md.append("| " + " | ".join(f"kolumna {i + 1}" for i in range(len(cols))) + " |")
        md.append("|" + "---|" * len(cols))
        for i in range(max(map(len, cols))):
            md.append("| " + " | ".join(col[i] if i < len(col) else "" for col in cols) + " |")
        md.append("")
    (out_dir / "karta.md").write_text("\n".join(md), encoding="utf-8")
    (out_dir / "karta.json").write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
    res.artifacts += ["master_card/karta.md", "master_card/karta.json"]
    if cards["rękopis"] is not None:
        cols = K.table(cards["rękopis"], ms_chunks, fr)
        res.evidence.append("Karta rękopisu, po 6 najczęstszych kawałków z każdej kolumny: " + " | ".join(" ".join(col[:6]) for col in cols) + ".")

    ms_c, lat, sh = c["rękopis"], c["łacina"], c.get("przetasowany w słowie", c["łacina"])
    if ms_c >= 0.85 and ms_c >= lat + 0.15 and ms_c >= sh + 0.15:
        res.decide(True)
        res.summary = (f"Karta 120 wpisów składa {ms_c:.0%} słów rękopisu, a łaciny tylko {lat:.0%}"
                       + (f" i rękopisu z przetasowanymi glifami {sh:.0%}" if "przetasowany w słowie" in c else "")
                       + (f"; bełkot v7 {c['v7']:.0%}" if "v7" in c else "") + ". Słowa rękopisu wyglądają jak złożone z jednej małej tabeli.")
    elif ms_c <= lat + 0.05:
        res.decide(False)
        res.summary = f"Karta nie składa rękopisu lepiej niż łaciny ({ms_c:.0%} wobec {lat:.0%}): słowa nie wyglądają na złożone z tabeli."
    else:
        res.decide(None)
        res.summary = f"Rękopis {ms_c:.0%}, łacina {lat:.0%}, przetasowany {sh:.0%} przy 120 wpisach: wynik między progami."
    res.caveats += ["Karta opisuje, jak słowa są zbudowane, nie skąd się wzięły: ten sam wynik dałby język o bardzo regularnej odmianie "
                    "albo pismo sylabiczne; nasze inne testy wykluczyły jednak, że tekst niesie język.",
                    "Pokrycie zależy od podziału na glify (ch, sh, cth jako jeden znak) i od transliteracji.",
                    "Ewolucja może nie znaleźć najlepszej karty; kontrola dodatnia mierzy, ile jej brakuje do prawdziwej."]
    res.seconds = time.time() - t0
    return res
