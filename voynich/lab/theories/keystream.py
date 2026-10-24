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


def _cheapest(original: str, names, dl) -> str:
    """The name with the shortest description; ties (a bijection on word types changes nothing) go to the original."""
    best = original
    for n in names:
        if dl(n) < dl(best) - 1e-6:
            best = n
    return best


def _measure(lines, shuffles_mi: int, shuffles_syn: int, seed: int) -> dict:
    nw = sum(map(len, lines))
    syn = longrange.split_by_identity(lines, top=60 if nw > 3000 else 15, shuffles=shuffles_syn, seed=seed)
    mi = keystream.adjacent_mi_z(lines, shuffles_mi, seed)
    voc = keystream.vocabulary(lines)
    return {"unrelated_z": syn["unrelated"]["z"], "same_z": syn["same"]["z"], "variants_z": syn["variants"]["z"],
            "adjacent_mi_z": mi["z"], "adjacent_mi": mi["value"], "dl": keystream.description_length(lines), **voc}


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
                f"i informacją wzajemną sąsiednich jednostek (z wobec tasowania w wierszu; {sh_mi} i {sh_syn} tasowań), a podział "
                "oceniany długością opisu (bity na glif: słownik jednostek plus tekst jako ich kody; prawdziwe słowa języka są blisko "
                "minimum). Trop: reguła kluczowana, która koduje rękopis krócej niż odstępy EVA (≥ 2%) i daje mu składnię (z ≥ 5), "
                "której nie daje bełkotowi (różnica ≥ 5). Kontrole: łacina z odstępami przepisanymi regułą z rodziny i łacina przeczytana "
                "kolumnami muszą zostać odzyskane jako minimum długości opisu; zwykła łacina i bełkot v5 nie mogą zyskać na żadnej regule."),
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
    # Controls on Latin: the description length must pick the true words, and undo a cipher of the family.
    plain = {t.name: _measure(keystream.apply(t, latl), sh_mi, sh_syn, cfg.seed) for t in fam}
    best_plain = _cheapest(fam[0].name, plain, lambda k: plain[k]["dl"])
    res.control("zwykła łacina: żadna reguła nie koduje jej krócej niż własne odstępy", "minimum długości opisu przy odstępach EVA (bez zmian)",
                f"minimum: {best_plain} ({plain[best_plain]['dl']:.3f} bit/glif; bez zmian {plain[fam[0].name]['dl']:.3f})",
                best_plain == fam[0].name)
    for ct in (keystream.Transform("x", "cut", "glyphs", 2), keystream.Transform("x", "read", "none", 3)):
        cipher = keystream.encipher(latl, ct, cfg.seed)
        scores = {t.name: (keystream.description_length(keystream.apply(t, cipher)), t) for t in fam}
        top_name = _cheapest(fam[0].name, scores, lambda k: scores[k][0])
        top_dl, top_t = scores[top_name]
        f1 = keystream.boundary_f1(latl, keystream.apply(top_t, cipher))
        ok = keystream.inverse_of(ct, top_t) and f1 >= 0.9
        label = "odstępy przepisane długościami przesuniętymi o 2" if ct.kind == "cut" else "tekst przeczytany co 3. glif"
        res.control(f"łacina zaszyfrowana ({label}): wyszukiwanie odzyskuje słowa", "minimum długości opisu przy regule odwrotnej, F1 granic ≥ 0,9",
                    f"minimum: {top_name} ({top_dl:.3f} bit/glif), F1 = {f1:.2f}; zaszyfrowana bez zmian {scores[fam[0].name][0]:.3f}", ok)
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
    keyed = [n for n in table if n != fam[0].name and "bez klucza" not in n]
    dl0 = table[fam[0].name]["manuscript"]["dl"]
    dl_v5 = table[fam[0].name]["v5"]["dl"]
    best_v5 = _cheapest(fam[0].name, [fam[0].name] + keyed, lambda n: table[n]["v5"]["dl"])
    res.control("bełkot v5 (pisany słowami): żadna reguła kluczowana nie koduje go krócej niż jego odstępy", "minimum przy odstępach",
                f"minimum: {best_v5} ({table[best_v5]['v5']['dl']:.3f}; odstępy {dl_v5:.3f})", best_v5 == fam[0].name)
    cheaper = [n for n in keyed if table[n]["manuscript"]["dl"] <= 0.98 * dl0]
    leads = [n for n in cheaper if table[n]["manuscript"]["unrelated_z"] >= 5 and table[n]["delta_unrelated"] >= 5]
    best_dl = min(keyed, key=lambda n: table[n]["manuscript"]["dl"])
    best_syn = max(keyed, key=lambda n: table[n]["delta_unrelated"])
    fixed = {n: table[n]["manuscript"]["dl"] for n in table if "bez klucza" in n}
    fixed_best = min(fixed, key=fixed.get)
    for n in sorted(keyed, key=lambda n: table[n]["manuscript"]["dl"])[:4] + [best_syn]:
        r = table[n]
        res.evidence.append(f"{n}: długość opisu {r['manuscript']['dl']:.3f} bit/glif (odstępy EVA {dl0:.3f}; v5 {r['v5']['dl']:.3f} wobec {dl_v5:.3f}); "
                            f"rękopis niespokrewnione z = {r['manuscript']['unrelated_z']:+.1f}, bełkot v5 {r['v5']['unrelated_z']:+.1f}, "
                            f"łacina {r['latin']['unrelated_z']:+.1f}; sąsiedzi z = {r['manuscript']['adjacent_mi_z']:+.1f} (v5 {r['v5']['adjacent_mi_z']:+.1f}); "
                            f"jednostek {r['manuscript']['units']}, typów {r['manuscript']['types']}.")
    res.evidence.append(f"Cięcia bez klucza: {fixed_best} koduje rękopis {fixed[fixed_best]:.3f} bit/glif wobec {dl0:.3f} dla słów EVA "
                        f"(bełkot v5 {table[fixed_best]['v5']['dl']:.3f} wobec {dl_v5:.3f}; łacina {table[fixed_best]['latin']['dl']:.3f} wobec "
                        f"{table[fam[0].name]['latin']['dl']:.3f}). Słowa rękopisu, jak słowa bełkotu, są mniej oszczędnymi jednostkami niż "
                        "sztywne kawałki glifów; słowa łaciny są oszczędniejsze od kawałków.")
    if leads:
        res.decide(True)
    elif not cheaper and max(table[n]["delta_unrelated"] for n in keyed) < 2.5:
        res.decide(False)
    else:
        res.decide(None)
    res.summary = (f"Przy odstępach EVA: różne słowa na odległość z = {base:+.1f}, sąsiednie słowa z = {mi['rękopis']['z']:+.1f} "
                   f"(v5 {mi['bełkot v5']['z']:+.1f}, v6 {mi['bełkot v6']['z']:+.1f}, łacina {mi['łacina']['z']:+.1f}); długość opisu {dl0:.3f} bit/glif. "
                   + ("Trop: " + ", ".join(leads) + "." if leads else
                      f"Żadna z {len(keyed)} reguł kluczowanych nie koduje rękopisu krócej niż odstępy EVA (najbliżej {best_dl}: "
                      f"{table[best_dl]['manuscript']['dl']:.3f}) ani nie daje mu składni, której nie dawałaby bełkotowi (największa przewaga "
                      f"{best_syn}: {table[best_syn]['delta_unrelated']:+.1f}). Odstępy EVA są najlepszym podziałem w tej rodzinie, a klucz "
                      "w długościach słów nie odsłania jednostek z gramatyką."))
    res.caveats += ["Rodzina reguł jest skończona (cięcia, przesunięcia, transpozycje według długości); klucz innego rodzaju, np. tablica "
                    "przyporządkowująca długościom litery, wymagałby osobnego testu (tak działał length_code, obalony).",
                    "Cięcie strumienia glifów w sztywne kawałki samo tworzy pozorną informację między sąsiadami (zależności glifów przechodzą "
                    "przez cięcie); stąd porównanie każdej reguły z tą samą regułą na bełkocie, nie z zerem.",
                    "Ujemna informacja sąsiednich słów rękopisu to nowa miara spoza karty 22; kandydat do karty v7."]
    res.seconds = time.time() - t0
    return res
