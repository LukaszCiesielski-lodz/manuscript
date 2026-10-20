"""Theory: the manuscript is Basque under a substitution cipher.

Basque is a recurring amateur proposal with no peer-reviewed support. Two Basque
texts are used so the answer does not hinge on one spelling or genre:
- Leizarraga's New Testament (1571), the oldest comparison text in the project,
  in its original spelling (via the multilingual Bible corpus);
- modern news prose (Universal Dependencies Basque BDT treebank).

For each: the substitution attack with its controls (simple and homophonic
encryption of the same Basque must be broken), the shape distance to the
manuscript ranked among all reference languages, and immediate word repeats,
which no word-for-word code can create.
"""

from __future__ import annotations

import time

from ... import cipher, corpus, eva
from ...syllabic import repeat_profile
from ..common import distance, language_scales, profile, rng
from ..config import LabConfig
from ..results import TheoryResult


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    rng(cfg.seed)
    n_cipher = 4000 if cfg.quick else 8000
    n = 20000 if cfg.quick else 35000
    # Modern Basque has a larger alphabet in use than the Bible text; the search needs room to converge.
    restarts, steps = (5, 20000) if cfg.quick else (8, 30000)
    res = TheoryResult(
        theory="basque",
        hypothesis="Rękopis to tekst baskijski zapisany szyfrem podstawieniowym (prostym lub homofonicznym).",
        method=("Dwa teksty baskijskie: Nowy Testament Leizarragi (1571, oryginalna pisownia) i współczesna prasa (UD Basque-BDT). "
                "Dla każdego: łamacz szyfru z kontrolami na zaszyfrowanym baskijskim, odległość odcisku palca od rękopisu "
                "na tle 13 języków, powtórzenia słów."),
        references=["Leizarraga, Iesus Christ gure Iaunaren Testamentu Berria (La Rochelle, 1571), via christos-c/bible-corpus",
                    "Universal Dependencies Basque BDT treebank (Aranzabe i in.)",
                    "Bowern & Lindemann, Annual Review of Linguistics 7 (2021)"])
    voy_words = [eva.glyphs(w) for w in corpus.tokens(corpus.load_voynich(), paragraphs_only=True)]
    vtest, vtrain = voy_words[:n_cipher], voy_words[n_cipher:]
    v_self = cipher.self_entropy(vtrain, vtest)
    voy_all = [eva.glyphs(w) for w in corpus.tokens(corpus.load_voynich())]
    langs, scales = language_scales(n)
    pv = profile(voy_all[:n])
    ranking = sorted(((distance(p, pv, scales), l) for l, p in langs.items()))
    texts = {"Leizarraga 1571": corpus.load_reference("Basque"), "prasa współczesna": corpus.load_extra("basque_news")}
    metrics = {"ranking": [[l, d] for d, l in ranking], "voynich_repeat": repeat_profile(voy_all[:n])["adjacent_repeat"]}
    gaps = []
    for name, words in texts.items():
        model = cipher.TrigramModel(words[20000:])
        row = {}
        for h in (1, 2):
            enc, truth = cipher.random_substitution(words, seed=cfg.seed + h, homophones=h)
            sol = cipher.solve(enc[:n_cipher], model, restarts=restarts, steps=steps)
            s_self = cipher.self_entropy(enc[20000:], enc[:n_cipher])
            acc = cipher.accuracy(sol, enc[:n_cipher], truth)
            row[f"control_h{h}"] = {"gap": sol.bits - s_self, "accuracy": acc}
            res.control(f"{name}: szyfr {'prosty' if h == 1 else 'homofoniczny'}", "łamacz odzyskuje ≥ 90% liter",
                        f"{acc:.1%}, luka {sol.bits - s_self:+.2f}", acc >= 0.9)
        sol = cipher.solve(vtest, model, restarts=restarts, steps=steps)
        gap = sol.bits - v_self
        gaps.append(gap)
        p = profile(words[:n])
        row.update({"voynich_gap": gap, "decrypted": " ".join(sol.decrypt(vtest[:20])), "distance": distance(p, pv, scales),
                    "profile": p, "repeat": repeat_profile(words[:n])["adjacent_repeat"]})
        metrics[name] = row
        res.evidence.append(f"{name}: rękopis zostawia lukę {gap:+.2f} bita/znak (kontrole ~0); odległość od rękopisu "
                            f"{row['distance']:.2f}; h2 {p['h2']:.2f} (rękopis {pv['h2']:.2f}), średnia długość słowa "
                            f"{p['mean_word_len']:.1f} ({pv['mean_word_len']:.1f}), hapaksy {p['hapax_ratio']:.0%} "
                            f"({pv['hapax_ratio']:.0%}), powtórzenia słów {row['repeat']:.2%} ({metrics['voynich_repeat']:.2%}).")
    rank = [l for _, l in ranking].index("Basque") + 1
    res.evidence.append(f"Ranking odległości od rękopisu wśród {len(ranking)} języków: baskijski na miejscu {rank} "
                        f"({', '.join(f'{l} {d:.2f}' for d, l in ranking[:4])}...).")
    res.metrics = metrics
    res.decide(True if max(gaps) < 0.25 else False if min(gaps) > 0.75 else None)
    res.summary = (f"Szyfr podstawieniowy z baskijskiego: luka {min(gaps):.2f}–{max(gaps):.2f} bita/znak przy kontrolach bliskich zera; "
                   f"baskijski {rank}. na {len(ranking)} języków pod względem podobieństwa do rękopisu.")
    res.caveats += [
        "Wyklucza tylko szyfr podstawieniowy litera-za-glif; nie bada szyfrów sylabicznych ani zapisu gubiącego rozróżnienia głosek.",
        "Baskijski z XV wieku nie zachował się w piśmie (pierwsza książka: 1545); Leizarraga 1571 to najbliższe dostępne przybliżenie.",
        "Tekst biblijny baskijski to Nowy Testament, inne języki zaczynają się od Księgi Rodzaju.",
    ]
    res.seconds = time.time() - t0
    return res
