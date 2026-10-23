"""Theory: the manuscript is written in an early Romance language ("proto-Romance").

Cheshire (Romance Studies, 2019) read the manuscript as "proto-Romance"; the reading
was rejected by medievalists, but the language family deserves the same tests as the
others. Proto-Romance itself survives in no text, so its nearest witnesses stand in:

- Vulgar Latin: Egeria's travel diary (Itinerarium Egeriae, c. 400);
- the oldest Romance writing: Old French, 9th-13th c. (UD PROFITEROLE, opening with the
  Chanson de Roland);
- the Romance Bibles: Italian, Spanish, Portuguese, French, Romanian.

For each: the substitution attack with its controls, the shape distance to the
manuscript among all reference languages, and the long-range syntax measure (do
different frequent words depend on each other two to seven places apart?).
"""

from __future__ import annotations

import time

from ... import cipher, corpus, eva, longrange
from ..common import distance, language_scales, profile, rng
from ..config import LabConfig
from ..results import TheoryResult

TEXTS = {
    "łacina ludowa (Egeria, ok. 400)": lambda: corpus.load_extra("egeria"),
    "starofrancuski (IX–XIII w.)": lambda: corpus.load_extra("old_french"),
    **{lang: (lambda l=lang: corpus.load_reference(l)) for lang in corpus.ROMANCE},
}


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    rng(cfg.seed)
    n_cipher = 4000 if cfg.quick else 8000
    n = 17000 if cfg.quick else 35000
    restarts, steps = (4, 15000) if cfg.quick else (6, 25000)
    names = list(TEXTS)[:3] if cfg.quick else list(TEXTS)
    res = TheoryResult(
        theory="romance",
        hypothesis="Rękopis to tekst we wczesnym języku romańskim („protoromańskim”, Cheshire 2019) lub innym "
                   "romańskim, zapisany szyfrem podstawieniowym albo własnym alfabetem.",
        method=("Protoromański nie zachował się w żadnym tekście, więc zastępują go najbliższe świadectwa: łacina ludowa "
                "(Egeria, ok. 400) i starofrancuski (IX–XIII w.), oraz Biblie romańskie. Dla każdego: łamacz szyfru "
                "z kontrolami (szyfr prosty i homofoniczny tego samego tekstu musi zostać złamany), odległość odcisku "
                "palca od rękopisu na tle wszystkich języków, daleka składnia (zależność różnych częstych słów na "
                "odległość 2–7)."),
        references=["Cheshire, The Language and Writing System of MS408 (Voynich) Explained, Romance Studies 37 (2019)",
                    "Itinerarium Egeriae, The Latin Library", "UD Old French PROFITEROLE (CC BY-SA 4.0)",
                    "Bowern & Lindemann, Annual Review of Linguistics 7 (2021)"])
    para = [l for l in corpus.load_voynich() if l.kind.startswith("P")]
    voy_words = [eva.glyphs(w) for l in para for w in l.words]
    vtest, vtrain = voy_words[:n_cipher], voy_words[n_cipher:]
    v_self = cipher.self_entropy(vtrain, vtest)
    langs, scales = language_scales(n)
    pv = profile(voy_words[:n])
    voy_lines = [[eva.glyphs(w) for w in l.words] for l in para if l.words]
    v_syntax = longrange.split_by_identity(voy_lines, top=60, shuffles=8 if cfg.quick else 20, seed=cfg.seed)
    metrics = {"voynich_syntax": v_syntax}
    gaps, syntax_z = [], []
    for name in names:
        words = TEXTS[name]()
        model = cipher.TrigramModel(words[n_cipher * 2:])
        row = {}
        for h in (1, 2):
            enc, truth = cipher.random_substitution(words[:n_cipher], seed=cfg.seed + h, homophones=h)
            sol = cipher.solve(enc, model, restarts=restarts, steps=steps)
            acc = cipher.accuracy(sol, enc, truth)
            row[f"control_h{h}"] = acc
            res.control(f"{name}: szyfr {'prosty' if h == 1 else 'homofoniczny'}", "łamacz odzyskuje ≥ 90% liter",
                        f"{acc:.1%}", acc >= 0.9)
        sol = cipher.solve(vtest, model, restarts=restarts, steps=steps)
        gap = sol.bits - v_self
        gaps.append(gap)
        p = profile(words[:n])
        lines = [[list(w) for w in words[i:i + 9]] for i in range(0, min(len(words), len(voy_words)), 9)]
        syn = longrange.split_by_identity(lines, top=60, shuffles=8 if cfg.quick else 20, seed=cfg.seed)
        syntax_z.append(syn["unrelated"]["z"])
        row.update({"voynich_gap": gap, "decrypted": " ".join(sol.decrypt(vtest[:20])), "distance": distance(p, pv, scales),
                    "syntax": syn})
        metrics[name] = row
        res.evidence.append(f"{name}: rękopis zostawia lukę {gap:+.2f} bita/znak; odległość odcisku palca {row['distance']:.2f}; "
                            f"h2 {p['h2']:.2f} (rękopis {pv['h2']:.2f}), słowo {p['mean_word_len']:.1f} znaku "
                            f"({pv['mean_word_len']:.1f}); daleka składnia z = {syn['unrelated']['z']:.1f} "
                            f"(rękopis {v_syntax['unrelated']['z']:.1f}). Odczyt próbny: {row['decrypted'][:60]}…")
    ranking = sorted((distance(p, pv, scales), l) for l, p in langs.items())
    places = {l: i + 1 for i, (_, l) in enumerate(ranking)}
    res.evidence.append(f"Ranking odległości od rękopisu wśród {len(ranking)} języków Biblii: "
                        + ", ".join(f"{l} {places[l]}." for l in corpus.ROMANCE if l in places)
                        + f" (najbliżej: {', '.join(f'{l} {d:.2f}' for d, l in ranking[:3])}).")
    res.metrics = metrics
    refuted = min(gaps) > 0.75 and min(syntax_z) >= 3 and v_syntax["unrelated"]["z"] < 1.5
    res.decide(True if max(gaps) < 0.25 else False if refuted else None)
    res.summary = (f"Teksty romańskie, od łaciny ludowej po rumuński: łamacz zostawia na rękopisie lukę "
                   f"{min(gaps):.2f}–{max(gaps):.2f} bita/znak przy kontrolach bliskich pełnego odczytu, a każdy z nich ma "
                   f"składnię na odległość (z ≥ {min(syntax_z):.1f}), której rękopis nie ma "
                   f"(z = {v_syntax['unrelated']['z']:.1f}).")
    res.caveats += [
        "Protoromański jest rekonstrukcją bez tekstów; łacina ludowa i starofrancuski to najbliższe zachowane świadectwa.",
        "Łamacz wyklucza szyfr podstawieniowy litera-za-glif; Cheshire zakłada też skróty i ligatury, których test nie modeluje. "
        "Daleka składnia nie zależy od zapisu i dotyczy także tej wersji.",
        "Teksty romańskie to Biblia, pielgrzymka i epika, nie zielnik; gatunek wpływa na słownictwo, mniej na składnię.",
    ]
    res.seconds = time.time() - t0
    return res
