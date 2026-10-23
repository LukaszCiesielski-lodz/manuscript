"""Theory: as a sequence of numbers (letters per word), the text moves like a language.

Each word becomes its length; the series is compared with the same series of every
reference text. In languages with short function words (et, in, la, der) short and
long words alternate, so neighbouring lengths are negatively correlated and the series
zigzags; whether lengths also drift in long stretches is measured by the DFA exponent.
Generators and a random sequence with the manuscript's own length distribution show
what copying, word memory and pure chance produce.
"""

from __future__ import annotations

import random
import statistics
import time

from ... import corpus, eva, hoax, lengths
from ..config import LabConfig
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 5 if cfg.quick else 10
    res = TheoryResult(
        theory="lengths",
        hypothesis="Ciąg długości słów (słowo → liczba znaków) ma dynamikę języka naturalnego.",
        method=("Każde słowo zamienione na liczbę znaków (w rękopisie glifów EVA). Rozkład; zależność sąsiednich długości "
                "(informacja wzajemna, autokorelacja dla przesunięć 1–5) i naprzemienność krótkie–długie, jako nadwyżka "
                "ponad tasowanie w obrębie 300 słów; pamięć długozasięgowa (wykładnik DFA, 0,5 = brak pamięci). "
                "Porównanie: 17 języków Biblii, łacina średniowieczna i ludowa, starofrancuski, generator v5, łańcuch słów, "
                "ciąg losowy o rozkładzie rękopisu; rozbicie na efekt wiersza i kolejność w wierszu."),
        references=["Ebeling & Neiman, Long-range correlations between letters and sentences in texts, Physica A 215 (1995)",
                    "Montemurro & Pury, Long-range fractal correlations in literary corpora, Fractals 10 (2002)",
                    "Peng et al., Mosaic organization of DNA nucleotides (DFA), Phys. Rev. E 49 (1994)"])
    para = [l for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    lines = [[eva.glyphs(w) for w in l.words] for l in para]
    glyph = [w for l in lines for w in l]
    n = len(glyph)
    langs = corpus.BIBLE_LANGUAGES[:6] if cfg.quick else corpus.BIBLE_LANGUAGES
    texts = {"rękopis (glify)": glyph, "rękopis (znaki EVA)": [w for l in para for w in l.words]}
    texts.update({l: corpus.load_reference(l)[:n] for l in langs})
    texts["łacina średniowieczna"] = [w for m in corpus.medieval_texts() for w in corpus.load_medieval(m, 4000)][:n]
    texts["łacina ludowa (Egeria)"] = corpus.load_extra("egeria")[:n]
    texts["starofrancuski"] = corpus.load_extra("old_french")[:n]
    gen = generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed) + generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed + 1)
    texts["generator v5 (bez treści)"] = [w for l in gen for w in l]
    texts["łańcuch słów, pamięć 1"] = [w for l in hoax.word_chain(lines, lines, 1, seed=cfg.seed) for w in l]
    r = random.Random(cfg.seed)
    xs = lengths.series(glyph)
    texts["losowy ciąg (rozkład rękopisu)"] = [[0] * r.choice(xs) for _ in range(n)]

    m = {name: lengths.describe(lengths.series(ws), shuffles=shuffles, seed=cfg.seed) for name, ws in texts.items()}
    language_names = [k for k in texts if k in langs or k in ("łacina średniowieczna", "łacina ludowa (Egeria)", "starofrancuski")]
    v = m["rękopis (glify)"]
    rnd = m["losowy ciąg (rozkład rękopisu)"]
    res.control("losowy ciąg: brak zależności", "|z| < 3 dla autokorelacji i DFA",
                f"ac1 z = {rnd['ac1']['z']:.1f}, DFA z = {rnd['dfa']['z']:.1f}",
                abs(rnd["ac1"]["z"]) < 3 and abs(rnd["dfa"]["z"]) < 3)
    res.control("łańcuch słów nauczony na rękopisie odtwarza zależność sąsiadów",
                "autokorelacja przesunięcia 1 w granicach ±0,05 od rękopisu",
                f"{m['łańcuch słów, pamięć 1']['ac1']['value']:+.3f} wobec {v['ac1']['value']:+.3f}",
                abs(m["łańcuch słów, pamięć 1"]["ac1"]["value"] - v["ac1"]["value"]) <= 0.05)

    fmt = lambda d: (f"średnio {d['mean']:.2f} (sd {d['sd']:.2f}); sąsiad: autokorelacja {d['ac1']['value']:+.3f} "
                     f"(nadwyżka {d['ac1']['excess']:+.3f}, z = {d['ac1']['z']:.1f}), zygzak {d['updown']['value']:.3f} "
                     f"(z = {d['updown']['z']:.1f}); DFA α = {d['dfa']['value']:.3f} (z = {d['dfa']['z']:.1f})")
    for name in texts:
        res.evidence.append(f"{name}: {fmt(m[name])}.")
    ac_langs = [m[k]["ac1"]["excess"] for k in language_names]
    dfa_langs = [m[k]["dfa"]["value"] for k in language_names]
    neg = sum(x < 0 for x in ac_langs)

    # Where the persistence comes from: words shuffled inside each line keep line composition only.
    inline = []
    for l in lines:
        l2 = list(l)
        r.shuffle(l2)
        inline.append(l2)
    xin = [len(w) for l in inline for w in l]
    flat = [w for l in lines for w in l]
    r.shuffle(flat)
    mixed, i = [], 0
    for l in lines:
        mixed.append(flat[i:i + len(l)])
        i += len(l)
    spread = lambda ls: statistics.pvariance([statistics.mean(len(w) for w in l) for l in ls if len(l) >= 4])
    pos = lengths.by_position(lines)
    res.evidence.append(f"Skąd trwałość: po potasowaniu słów wewnątrz każdego wiersza autokorelacja spada z "
                        f"{lengths.autocorr(xs, 1):+.3f} do {lengths.autocorr(xin, 1):+.3f}, a DFA zostaje "
                        f"({lengths.dfa(xin):.3f}); średnie długości wierszy różnią się bardziej niż losowo "
                        f"(wariancja {spread(lines):.3f} wobec {spread(mixed):.3f}). Całe wiersze bywają „długie” albo „krótkie”.")
    res.evidence.append("Długość słowa według miejsca w wierszu (względem średniej wiersza): "
                        + ", ".join(f"{k}: {x:.2f}" for k, x in pos.items()) + ".")
    res.metrics = {"by_text": m, "by_position": pos}
    outside = v["ac1"]["excess"] > max(ac_langs) and v["dfa"]["value"] > max(dfa_langs)
    res.decide(False if outside else None)
    res.summary = (f"Jako ciąg liczb rękopis zachowuje się inaczej niż każdy z {len(language_names)} tekstów językowych: "
                   f"sąsiednie długości są dodatnio skorelowane ({v['ac1']['value']:+.3f}; w {neg} z {len(language_names)} "
                   f"językach ujemnie, bo krótkie słowa funkcyjne przeplatają się z długimi), ciąg rzadziej skacze "
                   f"krótkie–długie (z = {v['updown']['z']:.1f}) i ma najsilniejszą pamięć długozasięgową "
                   f"(DFA α = {v['dfa']['value']:.3f}, języki {min(dfa_langs):.3f}–{max(dfa_langs):.3f}). "
                   "Najbliżej są języki bez osobnych słów funkcyjnych (arabski, turecki, wietnamski, hebrajski).")
    res.caveats += [
        "Długość w glifach zależy od podziału na glify (EVA); wynik powtórzono w znakach EVA.",
        "Pamięć długozasięgowa rękopisu pochodzi z całych wierszy o podobnej długości słów; tak działa kopiowanie "
        "sąsiednich słów, ale też tekst z powtarzalnymi formułami.",
        "Języki bez słów funkcyjnych (pismo arabskie, hebrajskie, aglutynacja) są bliżej rękopisu niż języki europejskie.",
    ]
    res.seconds = time.time() - t0
    return res
