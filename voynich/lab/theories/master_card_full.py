"""Theory: the master card for 100% of the words, and how big it has to be.

voynich.lab.theories.master_card showed that a card of 120 entries writes 96% of the manuscript.
Here the card must write every word (and, as a sturdier figure, 99%): the full card (every piece in
every column) writes everything; a population of cards prunes it, each in its own order, keeping a
removal only when nothing is lost; the smallest card is then shrunk further by evolution under a
budget one entry smaller, as long as it still writes everything. The size of that card is compared
with the same for Latin, Italian, v7 gibberish and the manuscript with glyphs shuffled inside words,
and checked on a text written from a known card of 40 entries.
"""

from __future__ import annotations

import json
import time

from ... import corpus, eva
from .. import card as K
from ..config import LabConfig
from ..nomen2 import array_module
from ..results import TheoryResult
from .nomenclator2 import all_runs, v7


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    gpu = array_module().__name__ == "cupy"
    Kc = cfg.card_columns
    if gpu:
        p_pop, s_pop, s_gens, s_rounds = (16, 16, 20, 2) if cfg.quick else (cfg.card_prune_population, 256, 100, 40)
    else:
        p_pop, s_pop, s_gens, s_rounds = (2, 8, 10, 1) if cfg.quick else (4, 16, 30, 3)
    targets = [1.0] if cfg.quick else [1.0, 0.99]
    res = TheoryResult(
        theory="master_card_full",
        hypothesis="Istnieje mała karta matka, z której da się złożyć każde słowo rękopisu (100%), znacznie mniejsza niż dla języka.",
        method=(f"Karta pełna ({Kc} kolumn, wszystkie kawałki n ≤ 3 we wszystkich kolumnach) składa 100% słów. {p_pop} kart przycina ją "
                "naraz, każda w swojej kolejności (połowa losowo, połowa najpierw rzadkie i długie kawałki): wpis znika, gdy bez niego nadal "
                f"składa się cel (100% i 99% tokenów). Najmniejszą kartę zmniejsza dalej ewolucja (populacja {s_pop}, {s_gens} pokoleń na rundę, "
                f"do {s_rounds} rund) pod budżetem o jeden wpis mniejszym. {'cupy/GPU' if gpu else 'numpy/CPU'}. Te same kroki dla łaciny, "
                "włoskiego, bełkotu v7, rękopisu z glifami przetasowanymi w słowie i tekstu pisanego znaną kartą 40 wpisów (kontrola)."),
        references=["Stolfi, crust–mantle–core paradigm of Voynichese words", "Rugg, Cryptologia 28 (2004)"])
    pages = [tuple(eva.glyphs(w)) for l in corpus.load_voynich() if l.kind.startswith("P") for w in l.words]
    ms = pages[:6000] if cfg.quick else pages
    n = len(ms)
    ms_chunks = K.chunk_inventory(ms)
    syn, true = K.synthetic(ms_chunks, n, cfg.seed, noise=0.0)
    texts = {"rękopis": ms, "syntetyczny (karta 40 wpisów)": syn}
    if not cfg.quick:
        g_lines, _, _ = v7(all_runs(), cfg.seed)
        texts.update({"łacina": [tuple(w) for w in corpus.load_reference("Latin")[:n]],
                      "włoski": [tuple(w) for w in corpus.load_reference("Italian")[:n]],
                      "v7": [tuple(w) for l in g_lines for w in l][:n],
                      "przetasowany w słowie": K.shuffle_within(ms, cfg.seed)})
    log = (lambda m: print(m, flush=True)) if not cfg.quick else None
    sizes, cards = {}, {}
    for name, toks in texts.items():
        chunks = ms_chunks if name in ("rękopis", "syntetyczny (karta 40 wpisów)") else K.chunk_inventory(toks)
        enc = K.Encoded(toks, chunks, max_len=18)
        sizes[name] = {}
        for tg in targets:
            pr = K.prune(enc, chunks, Kc, tg, p_pop, cfg.seed, log=log)
            best = K.shrink(enc, toks, chunks, pr["card"], pr["target"], Kc, s_pop, s_gens, s_rounds, cfg.seed, log=log)
            sizes[name][tg] = {"pruned": pr["size"], "final": int(best.sum()), "target": pr["target"],
                               "pieces": len(chunks), "types": len(enc.types)}
            if name == "rękopis":
                cards[tg] = (best, chunks, K.piece_frequency(enc, chunks))
            print(f"  {name}: cel {tg:.2f} (osiągalne {pr['target']:.4f}) → przycięta {pr['size']}, po ewolucji {int(best.sum())} wpisów", flush=True)
    res.metrics["sizes"] = {k: {str(t): v for t, v in d.items()} for k, d in sizes.items()}

    out_dir = cfg.results_dir / "master_card_full"
    out_dir.mkdir(parents=True, exist_ok=True)
    md, js = [], {}
    for tg, (cd, chunks, fr) in cards.items():
        cols = K.table(cd, chunks, fr)
        js[str(tg)] = cols
        md += [f"# Karta matka rękopisu: {int(cd.sum())} wpisów, składa {tg:.0%} słów\n",
               "| " + " | ".join(f"kolumna {i + 1} ({len(c)})" for i, c in enumerate(cols)) + " |", "|" + "---|" * len(cols)]
        for i in range(max(map(len, cols))):
            md.append("| " + " | ".join(c[i] if i < len(c) else "" for c in cols) + " |")
        md.append("")
    (out_dir / "karta100.md").write_text("\n".join(md), encoding="utf-8")
    (out_dir / "karta100.json").write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
    res.artifacts += ["master_card_full/karta100.md", "master_card_full/karta100.json"]

    syn_size = sizes["syntetyczny (karta 40 wpisów)"][1.0]["final"]
    res.control("tekst pisany kartą 40 wpisów: znaleziona karta na 100%", "≤ 80 wpisów", f"{syn_size} wpisów", syn_size <= 80)
    res.evidence.append("Najmniejsza karta (wpisy; cel 100% / 99% tokenów, w nawiasie osiągalny sufit): " + "; ".join(
        f"{k}: " + " / ".join(f"{v['final']}" + (f" ({v['target']:.3f})" if v["target"] < t - 1e-9 else "") for t, v in d.items())
        for k, d in sizes.items()) + ".")
    ms_size = sizes["rękopis"][1.0]["final"]
    if cfg.quick:
        res.decide(None)
        res.summary = f"Tryb szybki: karta rękopisu na 100% ma {ms_size} wpisów."
    else:
        lang = min(sizes["łacina"][1.0]["final"], sizes["włoski"][1.0]["final"])
        sh = sizes["przetasowany w słowie"][1.0]["final"]
        if ms_size <= 0.5 * lang and ms_size <= 0.7 * sh:
            res.decide(True)
            res.summary = (f"Każde słowo rękopisu da się złożyć z karty {ms_size} wpisów (99% słów: {sizes['rękopis'][0.99]['final']}); "
                           f"łacina potrzebuje {sizes['łacina'][1.0]['final']}, włoski {sizes['włoski'][1.0]['final']}, rękopis z przetasowanymi "
                           f"glifami {sh}, bełkot v7 {sizes['v7'][1.0]['final']}.")
        elif ms_size >= 0.8 * lang:
            res.decide(False)
            res.summary = f"Karta na 100% rękopisu ({ms_size}) nie jest wyraźnie mniejsza niż dla języka ({lang})."
        else:
            res.decide(None)
            res.summary = f"Karta rękopisu {ms_size}, języka {lang}, przetasowanego {sh}: wynik między progami."
    res.caveats += ["Wpisy potrzebne tylko dla jednego słowa (hapaksu) też liczą się do karty; 99% to miara odporniejsza na pojedyncze dziwne słowa.",
                    "Przycinanie i ewolucja znajdują małą kartę, nie dowodzą, że mniejszej nie ma."]
    res.seconds = time.time() - t0
    return res
