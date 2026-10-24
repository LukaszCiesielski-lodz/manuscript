"""Theory: the spaces carry a key (word lengths) and the glyph stream carries the message cut or shifted by it.

See voynich.keystream. Every keyed transform of the family is applied to the manuscript and to
gibberish v5 of its statistics; the units it produces are measured for syntax (dependency between
different units at a distance 2-7, the lab's defining measure) and for information between
adjacent units. A transform that gives the manuscript syntax and gives v5 none would be a lead.
Positive controls: Latin with its spaces rewritten by a rule of the family (and Latin read in
columns) must be recovered by the search; negative control: plain Latin must not gain from any rule.
"""

from __future__ import annotations

import time
from collections import defaultdict

from ... import corpus, eva, keystream, longrange
from ..config import LabConfig
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, V6_FAV_N, V6_SECTION_PARAMS, generate_by_section, odd_runs


def _measure(lines, shuffles_mi: int, shuffles_syn: int, seed: int) -> dict:
    nw = sum(map(len, lines))
    syn = longrange.split_by_identity(lines, top=60 if nw > 3000 else 15, shuffles=shuffles_syn, seed=seed)
    mi = keystream.adjacent_mi_z(lines, shuffles_mi, seed)
    voc = keystream.vocabulary(lines)
    return {"unrelated_z": syn["unrelated"]["z"], "same_z": syn["same"]["z"], "variants_z": syn["variants"]["z"],
            "adjacent_mi_z": mi["z"], "adjacent_mi": mi["value"], **voc}


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    sh_mi, sh_syn = (10, 8) if cfg.quick else (20, 16)
    fam = keystream.family()
    res = TheoryResult(
        theory="keystream",
        hypothesis="Odstępy nie dzielą słów: ciąg długości „słów” (w glifach albo w znakach EVA) jest kluczem zapisanym w tekście, "
                   "a właściwe jednostki powstają po pocięciu, przesunięciu lub przeczytaniu strumienia glifów według tego klucza.",
        method=(f"Rodzina {len(fam)} przekształceń strumienia glifów wiersza: cięcie według długości przesuniętych o 1–3, odwróconych, "
                "z poprzedniego wiersza, pierwszego słowa, posortowanych, różnic; przesunięcie glifów w alfabecie o długość słowa, "
                "poprzedniego słowa, miejsce w słowie; czytanie co n-ty glif; cięcie co n glifów bez klucza. Dla każdego: jednostki "
                "rękopisu i bełkotu v5 mierzone zależnością między różnymi jednostkami na odległość 2–7 (z wobec tasowania w miejscu) "
                f"i informacją wzajemną sąsiednich jednostek (z wobec tasowania w wierszu; {sh_mi} i {sh_syn} tasowań). Trop: przekształcenie, "
                "które daje rękopisowi składnię (z ≥ 5), a bełkotowi nie (różnica ≥ 5). Kontrole: łacina z odstępami przepisanymi regułą "
                "z rodziny i łacina przeczytana kolumnami muszą zostać odzyskane; zwykła łacina nie może zyskać na żadnej regule."),
        references=["Currier (1976); Zandbergen, voynich.nu: word structure and spaces",
                    "Reddy & Knight, What we know about the Voynich manuscript (2011): word-level statistics"])
    L = [l for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    voy = [[eva.glyphs(w) for w in l.words] for l in L]
    gen = [[list(w) for w in l] for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)
           + generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed + 1)]
    gen6 = [[list(w) for w in l] for l in generate_by_section(odd_runs(), V6_SECTION_PARAMS, cfg.seed, fav_n=V6_FAV_N)]
    lat = corpus.load_reference("Latin")[:sum(map(len, voy))]
    latl = [[list(w) for w in lat[i:i + 9]] for i in range(0, len(lat), 9)]
    if cfg.quick:
        voy, gen, gen6, latl = voy[:1500], gen[:1500], gen6[:1500], latl[:1500]
    # The adjacent-word finding, before any transform.
    mi = {"rękopis": keystream.adjacent_mi_z(voy, sh_mi, cfg.seed), "bełkot v5": keystream.adjacent_mi_z(gen, sh_mi, cfg.seed),
          "bełkot v6": keystream.adjacent_mi_z(gen6, sh_mi, cfg.seed), "łacina": keystream.adjacent_mi_z(latl, sh_mi, cfg.seed)}
    by_section = defaultdict(list)
    for l, line in zip(L, [[eva.glyphs(w) for w in l.words] for l in L]):
        by_section[l.section].append(line)
    sec = {s: keystream.adjacent_mi_z(ls, sh_mi, cfg.seed)["z"] for s, ls in by_section.items() if sum(map(len, ls)) > 2000}
    res.evidence.append("Przed przekształceniem, informacja wzajemna sąsiednich słów wobec tasowania w wierszu (z): "
                        + ", ".join(f"{k} {v['z']:+.1f}" for k, v in mi.items()) + "; rękopis działami: "
                        + ", ".join(f"{s} {z:+.1f}" for s, z in sec.items())
                        + ". Sąsiednie słowa rękopisu wiedzą o sobie MNIEJ niż dwa losowe słowa tej samej linii; bełkot v5 i łacina odwrotnie.")
    # Controls on Latin.
    plain = {t.name: _measure(keystream.apply(t, latl), sh_mi, sh_syn, cfg.seed) for t in fam}
    best_plain = max(plain, key=lambda k: plain[k]["unrelated_z"])
    res.control("zwykła łacina: żadna reguła nie przebija jej własnych odstępów", "najwyższa składnia przy odstępach EVA (bez zmian)",
                f"najwyższa: {best_plain} (z = {plain[best_plain]['unrelated_z']:.1f}; bez zmian {plain[fam[0].name]['unrelated_z']:.1f})",
                best_plain == fam[0].name)
    for ct in (keystream.Transform("x", "cut", "glyphs", 2), keystream.Transform("x", "read", "none", 3)):
        cipher = keystream.encipher(latl, ct, cfg.seed)
        scores = {t.name: (_measure(keystream.apply(t, cipher), sh_mi, sh_syn, cfg.seed)["unrelated_z"], t) for t in fam}
        top_name, (top_z, top_t) = max(scores.items(), key=lambda kv: kv[1][0])
        f1 = keystream.boundary_f1(latl, keystream.apply(top_t, cipher))
        ok = keystream.inverse_of(ct, top_t) and f1 >= 0.9
        label = "odstępy przepisane długościami przesuniętymi o 2" if ct.kind == "cut" else "tekst przeczytany co 3. glif"
        res.control(f"łacina zaszyfrowana ({label}): wyszukiwanie odzyskuje słowa", "najwyższa składnia przy regule odwrotnej, F1 granic ≥ 0,9",
                    f"najwyższa: {top_name} (z = {top_z:.1f}), F1 = {f1:.2f}; zaszyfrowana bez zmian z = {scores[fam[0].name][0]:.1f}", ok)
    # The manuscript and v5 under every transform.
    table = {}
    for t in fam:
        m_ms = _measure(keystream.apply(t, voy), sh_mi, sh_syn, cfg.seed)
        m_v5 = _measure(keystream.apply(t, gen), sh_mi, sh_syn, cfg.seed)
        table[t.name] = {"manuscript": m_ms, "v5": m_v5, "latin": plain[t.name],
                         "delta_unrelated": m_ms["unrelated_z"] - m_v5["unrelated_z"], "delta_mi": m_ms["adjacent_mi_z"] - m_v5["adjacent_mi_z"]}
        print(f"  {t.name}: rękopis niespokrewnione z {m_ms['unrelated_z']:+.1f} (v5 {m_v5['unrelated_z']:+.1f}), "
              f"sąsiedzi z {m_ms['adjacent_mi_z']:+.1f} (v5 {m_v5['adjacent_mi_z']:+.1f}), typów/jednostek {m_ms['type_token_ratio']:.2f}", flush=True)
    res.metrics = {"transforms": table, "adjacent_mi": {k: v for k, v in mi.items()}, "adjacent_mi_by_section": sec}
    base = table[fam[0].name]["manuscript"]["unrelated_z"]
    keyed = [n for n in table if n != fam[0].name]
    leads = [n for n in keyed if table[n]["manuscript"]["unrelated_z"] >= 5 and table[n]["delta_unrelated"] >= 5
             and table[n]["manuscript"]["unrelated_z"] >= base + 5 and table[n]["delta_mi"] >= 5]
    best = max(keyed, key=lambda n: table[n]["delta_unrelated"])
    for n in sorted(keyed, key=lambda n: table[n]["delta_unrelated"], reverse=True)[:6]:
        r = table[n]
        res.evidence.append(f"{n}: rękopis niespokrewnione z = {r['manuscript']['unrelated_z']:+.1f}, bełkot v5 {r['v5']['unrelated_z']:+.1f}, "
                            f"łacina {r['latin']['unrelated_z']:+.1f}; sąsiedzi z = {r['manuscript']['adjacent_mi_z']:+.1f} (v5 {r['v5']['adjacent_mi_z']:+.1f}); "
                            f"jednostek {r['manuscript']['units']}, typów {r['manuscript']['types']}.")
    if leads:
        res.decide(True)
    elif max(table[n]["delta_unrelated"] for n in keyed) < 2.5:
        res.decide(False)
    else:
        res.decide(None)
    res.summary = (f"Przy odstępach EVA: różne słowa na odległość z = {base:+.1f}, sąsiednie słowa z = {mi['rękopis']['z']:+.1f} "
                   f"(v5 {mi['bełkot v5']['z']:+.1f}, v6 {mi['bełkot v6']['z']:+.1f}, łacina {mi['łacina']['z']:+.1f}). "
                   + ("Trop: " + ", ".join(leads) + "." if leads else
                      f"Żadna z {len(keyed)} reguł kluczowanych nie daje rękopisowi składni, której nie dawałaby bełkotowi: największa przewaga "
                      f"nad v5 to {best} ({table[best]['delta_unrelated']:+.1f}). Odstępy EVA są najlepszym podziałem, jaki znamy, a klucz "
                      "w długościach słów nie odsłania jednostek z gramatyką."))
    res.caveats += ["Rodzina reguł jest skończona (cięcia, przesunięcia, transpozycje według długości); klucz innego rodzaju, np. tablica "
                    "przyporządkowująca długościom litery, wymagałby osobnego testu (tak działał length_code, obalony).",
                    "Cięcie strumienia glifów w sztywne kawałki samo tworzy pozorną informację między sąsiadami (zależności glifów przechodzą "
                    "przez cięcie); stąd porównanie każdej reguły z tą samą regułą na bełkocie, nie z zerem.",
                    "Ujemna informacja sąsiednich słów rękopisu to nowa miara spoza karty 22; kandydat do karty v7."]
    res.seconds = time.time() - t0
    return res
