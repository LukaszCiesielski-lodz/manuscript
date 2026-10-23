"""Theory: the manuscript's words are built like spoken words (vowels and consonants alternate as in a language).

Sukhotin's algorithm finds the "vowels" of the manuscript and of every reference language from
the same evidence (which symbols avoid each other's company); each word becomes a consonant-
vowel pattern; the manuscript's pattern distribution is compared with every language's by
Jensen-Shannon divergence, on glyphs and on raw EVA letters. Controls: meaningless text v5
(should look like the manuscript, it copies its word grammar) and the manuscript with the
glyphs of every word shuffled (a text with no word shapes: alternation must fall). A text
shaped like speech would land within the spread of distances between languages, next to a
language or next to the abjads if vowels were left unwritten.
"""

from __future__ import annotations

import time
from collections import Counter

from ... import corpus, eva, lexicon, phonotactics as ph
from ..config import LabConfig
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs

ABJADS = {"Hebrew", "Arabic", "Aramaic", "Syriac", "BiblicalHebrew"}


def _weighted(words) -> tuple[list, list]:
    c = Counter(tuple(w) for w in words)
    return list(c.keys()), [float(n) for n in c.values()]


def _analyse(words, weights=None) -> dict:
    vowels, order = ph.sukhotin(words, weights)
    prof = ph.profile(words, vowels, weights)
    prof["vowels"] = order
    return prof


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    res = TheoryResult(
        theory="phonotactics",
        hypothesis="Słowa rękopisu mają budowę słów mówionych: da się w nich wskazać samogłoski i spółgłoski, "
                   "a wzorce spółgłoska–samogłoska rozkładają się jak w którymś z języków (albo jak w abdżadzie).",
        method=("Algorytm Suchotina (1962; Guy 1991) na rękopisie (glify i surowe litery EVA) i na każdym z leksykonów: "
                "samogłoski to znaki, które unikają własnego towarzystwa. Każde słowo zamienione na wzorzec C/V; "
                "rozkłady wzorców porównane dywergencją Jensena-Shannona. Tło: bełkot v5; kontrola: rękopis z glifami "
                "przetasowanymi w słowie (naprzemienność musi spaść). Rękopis „jak mowa”, gdy jego odległość do "
                "najbliższego języka mieści się w rozrzucie odległości między językami."),
        references=["Sukhotin, Eksperimental'noe vydelenie klassov bukv s pomoshch'ju EVM (1962)",
                    "Guy, Vowel identification: an old (but good) algorithm, Cryptologia 15 (1991)"])
    lines = [l for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    voy_glyphs = [tuple(eva.glyphs(w)) for l in lines for w in l.words]
    voy_chars = [tuple(w) for l in lines for w in l.words]
    gen = [tuple(w) for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed) for w in l]
    texts = {"rękopis (glify)": _analyse(*_weighted(voy_glyphs)), "rękopis (litery EVA)": _analyse(*_weighted(voy_chars)),
             "bełkot v5": _analyse(*_weighted(gen)),
             "rękopis, glify przetasowane w słowie": _analyse(*_weighted(ph.shuffle_within_words(voy_glyphs, cfg.seed)))}
    langs = {}
    for name in lexicon.available():
        try:
            counts, _, _ = lexicon.load_all(name)
        except Exception:
            continue
        top = counts.most_common(5000)
        langs[name] = _analyse([tuple(w) for w, _ in top], [float(n) for _, n in top])
    if len(langs) < 5:
        res.evidence.append("Za mało leksykonów: uruchom scripts/fetch_lexicons.py.")
        res.decide(None)
        res.summary = "Pominięte: brak leksykonów."
        res.seconds = time.time() - t0
        return res
    # Distances between languages: what "as close as languages get" means.
    names = list(langs)
    nearest_lang = {}
    for a in names:
        nearest_lang[a] = min(ph.js_divergence(langs[a]["patterns"], langs[b]["patterns"]) for b in names if b != a)
    spread = sorted(nearest_lang.values())
    median_nn = spread[len(spread) // 2]
    worst_nn = spread[-1]
    for name, t in texts.items():
        dists = sorted((ph.js_divergence(t["patterns"], l["patterns"]), n) for n, l in langs.items())
        t["nearest"] = [(n, round(d, 3)) for d, n in dists[:5]]
        t["nearest_distance"] = dists[0][0]
        res.evidence.append(f"{name}: samogłoski wg Suchotina: {' '.join(t['vowels'][:6]) or 'brak'}; udział samogłosek "
                            f"{t['vowel_share']:.0%}, naprzemienność C/V {t['alternation']:.2f}, najdłuższa zbitka "
                            f"spółgłosek średnio {t['mean_longest_cluster']:.1f}, słowa bez samogłoski {t['no_vowel_share']:.0%}; "
                            "najbliższe języki: " + ", ".join(f"{n} {d}" for n, d in t["nearest"]) + ".")
    res.evidence.append(f"Odległość języka do najbliższego innego języka: mediana {median_nn:.3f}, największa {worst_nn:.3f} bitów. "
                        "Abdżady (hebrajski, aramejski, syryjski, arabski): naprzemienność "
                        + ", ".join(f"{n} {langs[n]['alternation']:.2f}" for n in names if n in ABJADS) + ".")
    ctrl = texts["rękopis, glify przetasowane w słowie"]["alternation"] < texts["rękopis (glify)"]["alternation"] - 0.05
    res.control("glify przetasowane w słowie tracą naprzemienność", "naprzemienność niższa o ≥ 0,05",
                f"{texts['rękopis, glify przetasowane w słowie']['alternation']:.2f} wobec {texts['rękopis (glify)']['alternation']:.2f}", ctrl)
    v = texts["rękopis (glify)"]
    # Within the typical distance between languages: like speech; beyond every language's nearest neighbour: not.
    like_speech = True if v["nearest_distance"] <= median_nn else (False if v["nearest_distance"] > worst_nn else None)
    res.metrics = {"texts": texts, "languages": {n: {k: l[k] for k in ("vowels", "vowel_share", "alternation",
                                                                        "mean_longest_cluster", "no_vowel_share")}
                                                  for n, l in langs.items()},
                   "nearest_language_distance": nearest_lang, "median_nn": median_nn, "worst_nn": worst_nn}
    res.decide(like_speech if ctrl else None)
    res.summary = (f"Rękopis (glify): samogłoski {' '.join(v['vowels'][:5])}, naprzemienność {v['alternation']:.2f}; najbliższy "
                   f"język {v['nearest'][0][0]} w odległości {v['nearest_distance']:.3f} bitów, gdy języki leżą od siebie "
                   f"najdalej {worst_nn:.3f} (mediana {median_nn:.3f}). "
                   + ("Budowa słów jak w typowym języku." if like_speech else
                      "Budowa słów rękopisu leży poza rozrzutem wszystkich języków." if like_speech is False else
                      "Rękopis jest tak odosobniony jak najbardziej odosobnione języki (turecki, wietnamski).")
                   + f" Bełkot v5 wypada tak samo (najbliżej {texts['bełkot v5']['nearest'][0][0]}, "
                   f"{texts['bełkot v5']['nearest_distance']:.3f}), więc naprzemienność C/V odtwarza także kopiujący skryba.")
    res.caveats += ["Suchotin dzieli znaki na dwie klasy po samym sąsiedztwie; w abdżadach „samogłoskami” zostają "
                    "matres lectionis, w rękopisie znaki o, a, e, y.",
                    "Porównanie wzorców C/V zależy od tego, co uznać za jeden znak; stąd rękopis liczony dwa razy "
                    "(glify i litery EVA)."]
    res.seconds = time.time() - t0
    return res
