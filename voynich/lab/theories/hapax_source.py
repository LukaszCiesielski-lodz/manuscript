"""Theory: the manuscript's hapax legomena are a nomenclator scribe's miscopies.

68% of the manuscript's word types occur once (Rozanova & Temerev: an open, hapax-rich vocabulary
no generator matches). A miscopying scribe makes hapaxes one glyph away from a frequent code
word, wherever that code word happens to be; copying from the neighbourhood (self-citation, Timm
& Schinner) makes them one glyph away from a word in the lines just above. Two measurements:
(1) the miscopy rate r* at which a nomenclator of the manuscript's size and code words has the
manuscript's share of hapax tokens; (2) locality: how often the frequent neighbour of a hapax
stands in the five lines above it, against the same lines of another page, for the manuscript,
v7 gibberish and the nomenclator at r*.
"""

from __future__ import annotations

import math
import random
import time
from collections import Counter, defaultdict

from ... import corpus
from .. import nomen2 as N
from ..config import LabConfig
from ..results import TheoryResult
from .nomenclator2 import all_runs, hapax_token_share, language, match_rate, trim, v7


def chunk(lines, size: int) -> list[list]:
    size = max(1, size)
    return [lines[i:i + size] for i in range(0, len(lines), size)]


def manuscript_pages() -> list[list[list[tuple]]]:
    from ... import eva
    pages: dict[str, list] = defaultdict(list)
    for l in corpus.load_voynich():
        if l.kind.startswith("P") and l.words:
            pages[l.folio].append([tuple(eva.glyphs(w)) for w in l.words])
    return list(pages.values())


def excess(loc: dict) -> tuple[float, float]:
    """Local rate minus other-page rate, and its binomial standard error."""
    p, n = loc["local_rate"], max(1, loc["hapaxes_with_neighbour"])
    return loc["local_rate"] - loc["other_page_rate"], math.sqrt(max(p * (1 - p), 1e-9) / n)


def plant_local(pages, rate: float, seed: int) -> list[list[list[tuple]]]:
    """Positive control: a share of the words replaced by a one-glyph variant of a word in the three lines above."""
    r = random.Random(seed)
    alphabet = sorted({g for p in pages for l in p for w in l for g in w})
    out = []
    for p in pages:
        q = []
        for li, l in enumerate(p):
            above = [w for ll in q[max(0, li - 3):li] for w in ll]
            new = []
            for w in l:
                if above and r.random() < rate:
                    w = N._miscopy(r.choice(above), alphabet, r)
                new.append(w)
            q.append(new)
        out.append(q)
    return out


def shuffle_pages(pages, seed: int):
    """Negative control: lines dealt to pages at random, page sizes kept."""
    r = random.Random(seed)
    lines = [l for p in pages for l in p]
    r.shuffle(lines)
    out, i = [], 0
    for p in pages:
        out.append(lines[i:i + len(p)])
        i += len(p)
    return out


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 40 if cfg.quick else 200
    langs = cfg.nomen2_languages[:1] if cfg.quick else list(cfg.nomen2_languages)
    res = TheoryResult(
        theory="hapax_source",
        hypothesis="Słowa jednorazowe (hapaksy) rękopisu to pomyłki kopisty nomenklatora: zniekształcone słowa kodowe, a nie kopie "
                   "słów z sąsiednich wierszy.",
        method=(f"(1) r* = stopa pomyłek (jeden glif zmieniony, dodany albo usunięty), przy której nomenklator tej samej wielkości "
                f"i z tych samych słów kodowych ma udział hapaksów w tokenach jak rękopis ({', '.join(langs)}). (2) Lokalność: jak często "
                f"częsty sąsiad hapaksu (o jeden glif) stoi w 5 wierszach nad nim, wobec tych samych wierszy innej strony ({shuffles} losowań); "
                "nadwyżka lokalna rękopisu, bełkotu v7 i nomenklatora przy r*. Kontrole: kopie z 3 wierszy wyżej podłożone w 10% słów "
                "nomenklatora muszą dać z ≥ 5; wiersze rękopisu rozdane losowo na strony nie mogą dać z ≥ 3."),
        references=["Rozanova & Temerev, arXiv:2608.17096 (2026)", "Timm & Schinner, Cryptologia 44 (2020)",
                    "Zhang & Sheng, arXiv:2610.34499 (2026)"])
    pages = manuscript_pages()
    ms_lines = [l for p in pages for l in p]
    per_page = round(len(ms_lines) / len(pages))
    target = hapax_token_share(ms_lines)
    pool = [w for w, _ in Counter(w for l in ms_lines for w in l).most_common(cfg.nomen2_pool)]
    tokens = sum(map(len, ms_lines))
    types = Counter(w for l in ms_lines for w in l)
    res.metrics.update({"tokens": tokens, "hapax_token_share": target,
                        "hapax_type_share": sum(1 for v in types.values() if v == 1) / len(types), "lines_per_page": per_page})
    loc = {"manuscript": N.hapax_locality(pages, shuffles=shuffles, seed=cfg.seed)}
    runs = all_runs()
    g_lines, _, run_of = v7(runs, cfg.seed)
    g_pages = []
    for i in sorted(set(run_of)):
        g_pages += chunk([l for l, k in zip(g_lines, run_of) if k == i], per_page)
    loc["v7"] = N.hapax_locality(g_pages, shuffles=shuffles, seed=cfg.seed)
    res.metrics["v7_hapax_token_share"] = hapax_token_share(g_lines)
    stars = {}
    for lang in langs:
        _, held = language(lang, cfg.nomen2_units)
        held = trim(held, tokens)
        r_star, table = match_rate(held, pool, target, cfg.seed)
        stars[lang] = {"r_star": r_star, "hapax_by_rate": table}
        lines, _, _ = N.encipher(held, pool, cfg.seed, miscopy=r_star)
        loc[f"{lang} r*"] = N.hapax_locality(chunk(lines, per_page), shuffles=shuffles, seed=cfg.seed)
        if lang == langs[0]:
            clean, _, _ = N.encipher(held, pool, cfg.seed, miscopy=0.0)
            planted = N.hapax_locality(plant_local(chunk(clean, per_page), 0.1, cfg.seed), shuffles=shuffles, seed=cfg.seed)
    res.metrics["rates"] = stars
    res.metrics["locality"] = loc
    neg = N.hapax_locality(shuffle_pages(pages, cfg.seed), shuffles=shuffles, seed=cfg.seed)
    res.control("kopie z wierszy powyżej (10% słów nomenklatora) wykryte", "z ≥ 5", f"z = {planted['z']:.1f}", planted["z"] >= 5)
    res.control("wiersze rękopisu rozdane losowo na strony bez lokalności", "z < 3", f"z = {neg['z']:.1f}", neg["z"] < 3)
    r_mean = sum(s["r_star"] for s in stars.values()) / len(stars)
    res.evidence.append(f"Udział hapaksów w tokenach: rękopis {target:.3f}, v7 {res.metrics['v7_hapax_token_share']:.3f}; nomenklator osiąga "
                        "go przy r* = " + ", ".join(f"{l} {s['r_star']:.2f}" for l, s in stars.items()) + " (co piąte słowo kodowe przepisane z błędem).")
    res.evidence.append("Lokalność hapaksów (sąsiad w 5 wierszach nad / w innej stronie, nadwyżka, z): " + "; ".join(
        f"{k} {v['local_rate']:.3f}/{v['other_page_rate']:.3f} (×{v['ratio']:.2f}, z = {v['z']:.1f}, n = {v['hapaxes_with_neighbour']})" for k, v in loc.items()) + ".")
    e_ms, s_ms = excess(loc["manuscript"])
    diffs = {}
    for k, v in loc.items():
        if k.endswith("r*"):
            e, s = excess(v)
            diffs[k] = (e_ms - e) / math.sqrt(s_ms ** 2 + s ** 2)
    e_g, s_g = excess(loc["v7"])
    diffs["v7"] = (e_ms - e_g) / math.sqrt(s_ms ** 2 + s_g ** 2)
    res.metrics["excess_z"] = diffs
    res.evidence.append("Nadwyżka lokalna rękopisu wobec modeli (z różnicy): " + ", ".join(f"{k} {z:+.1f}" for k, z in diffs.items()) + ".")
    ctl = [z for k, z in diffs.items() if k.endswith("r*")]
    if r_mean > 0.5:
        res.decide(False)
        res.summary = f"Nomenklator potrzebowałby {r_mean:.0%} pomyłek, żeby mieć tyle hapaksów, co rękopis; takiego tekstu nikt by nie odczytał."
    elif all(abs(z) < 2 for z in ctl) and diffs["v7"] >= 3:
        res.decide(True)
        res.summary = f"Hapaksy rękopisu pasują do pomyłek kopisty: r* ≈ {r_mean:.2f}, a lokalność jak w nomenklatorze (z różnicy " + ", ".join(f"{z:+.1f}" for z in ctl) + f") i inna niż w bełkocie v7 (z = {diffs['v7']:+.1f})."
    elif any(abs(z) < 2 for z in ctl):
        res.decide(None)
        res.summary = (f"Hapaksy nie wykluczają nomenklatora: przy r* ≈ {r_mean:.2f} pomyłki dają tyle hapaksów co rękopis i podobną lokalność "
                       f"(×{loc['manuscript']['ratio']:.2f} wobec " + ", ".join(f"×{loc[k]['ratio']:.2f}" for k in loc if k.endswith("r*")) +
                       f"), ale bełkot v7 jest prawie tak samo blisko (×{loc['v7']['ratio']:.2f}, z różnicy {diffs['v7']:+.1f}). "
                       "Lokalność nie odróżnia pomyłek od kopiowania z sąsiedztwa.")
    elif all(z >= 3 for z in ctl):
        res.decide(False)
        res.summary = (f"Liczbę hapaksów nomenklator daje przy r* ≈ {r_mean:.2f}, ale ich miejsca nie: wariant rękopisu stoi przy swoim "
                       f"częstym sąsiedzie w wierszach powyżej {loc['manuscript']['ratio']:.2f} razy częściej niż w innej stronie, "
                       "pomyłki nomenklatora " + ", ".join(f"{loc[k]['ratio']:.2f}" for k in loc if k.endswith("r*")) +
                       f" (z różnicy " + ", ".join(f"{z:+.1f}" for z in ctl) + "). Hapaksy powstają przez przepisywanie z sąsiedztwa, nie przez pomyłki.")
    else:
        res.decide(None)
        res.summary = "Lokalność hapaksów rękopisu leży między nomenklatorem a kopiowaniem z sąsiedztwa."
    res.caveats += ["Lokalność nomenklatora zależy od tematu tekstu jawnego: Biblia ma imiona i wątki ciągnące się przez strony, "
                    "zielnik mógłby mieć ich więcej albo mniej.",
                    "Pomyłka modelowana jako jeden glif; prawdziwy kopista myli też całe słowa i pomija wiersze."]
    res.seconds = time.time() - t0
    return res
