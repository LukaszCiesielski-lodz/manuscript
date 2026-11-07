"""Theory: the circle diagrams name what they show (cribs: lunar mansions, signs, months).

f69v has 28 radial words, as many as the 28 lunar mansions (Zandbergen); f67r1, f67v1 and f67r2
have 12 words in a ring, as many as the signs or the months. If the words are those names under a
letter cipher, one glyph-to-letter key aligns the ring with the list for some start and
direction; see voynich.lab.cribs. Null: the same search against the names in shuffled order.
"""

from __future__ import annotations

import time

from .. import cribs as C
from ..config import LabConfig
from ..results import TheoryResult


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 30 if cfg.quick else 200
    res = TheoryResult(
        theory="cribs",
        hypothesis="Słowa w kołach diagramów to nazwy tego, co diagram pokazuje, zapisane szyfrem literowym: 28 słów f69v = 28 stacji "
                   "Księżyca, 12 słów f67r1/f67v1/f67r2 = znaki zodiaku albo miesiące.",
        method=(f"Dla każdego diagramu i każdej listy (stacje po arabsku i łacinie Agryppy; znaki po łacinie, włosku, arabsku, hebrajsku; "
                f"miesiące w 6 językach) każdy początek i kierunek listy, klucz glif → litera dopasowany twardym EM (ścieżka edycyjna, "
                f"większość liter na glif); wynik = średnie podobieństwo odczytu i nazwy. Null: ta sama procedura wobec {shuffles} "
                "przetasowań kolejności nazw, p z poprawką Bonferroniego po parach. Kontrola: lista zapisana losowym kluczem "
                "homofonicznym w glifach rękopisu z 10% szumu musi dać z ≥ 5."),
        references=["Zandbergen, voynich.nu: f69v, 28 radial words and the lunar mansions",
                    "Agrippa, De occulta philosophia II.33 (mansions)", "Wikipedia: Lunar station (Arabic manāzil)"])
    rows, planted = [], {}
    for folio, kinds, expected, lists in C.DIAGRAMS:
        words = C.diagram_words(folio, kinds)
        if abs(len(words) - expected) > 1:
            res.evidence.append(f"{folio}: {len(words)} słów zamiast {expected}; diagram pominięty.")
            continue
        for name in (lists[:1] if cfg.quick else lists):
            names = C.LISTS[name]
            t = C.test(words, names, 0, shuffles, cfg.seed)
            rows.append({"folio": folio, "list": name, "words": len(words), "score": t["score"], "null_mean": t["null_mean"],
                         "z": t["z"], "p": t["p"], "start": t["start"], "direction": t["direction"],
                         "readings": [f"{a}~{b}" for a, b in t["readings"][:6]]})
            if name not in planted:
                fake = C.plant(names, words, cfg.seed)
                planted[name] = C.test(fake, names, 0, shuffles, cfg.seed)["z"]
    for r in rows:
        r["p_adj"] = min(1.0, r["p"] * len(rows))
    rows.sort(key=lambda r: -r["z"])
    res.metrics["pairs"] = rows
    res.metrics["planted_z"] = planted
    worst = min(planted.values()) if planted else 0.0
    res.control("lista zapisana szyfrem w glifach rękopisu odnaleziona", "z ≥ 5 dla każdej listy",
                f"najsłabsza z = {worst:.1f} ({min(planted, key=planted.get) if planted else '-'})", worst >= 5)
    res.evidence.append("Pary diagram–lista (podobieństwo odczytu do nazwy wobec tasowań, z, p popr.): " + "; ".join(
        f"{r['folio']} × {r['list']}: {r['score']:.3f} wobec {r['null_mean']:.3f}, z = {r['z']:+.1f}, p popr. {r['p_adj']:.2f}" for r in rows) + ".")
    if rows:
        b = rows[0]
        res.evidence.append(f"Najlepsza para {b['folio']} × {b['list']}, pierwsze odczyty: " + ", ".join(b["readings"]) + ".")
    sig = [r for r in rows if r["p_adj"] < 0.05 and r["z"] >= 4]
    if sig:
        res.decide(True)
        res.summary = "Koło czyta się jako lista nazw: " + ", ".join(f"{r['folio']} × {r['list']} (z = {r['z']:+.1f})" for r in sig)
    elif rows:
        res.decide(False)
        res.summary = (f"Żadne z {len(rows)} zestawień koła z listą nazw nie wypada lepiej niż te same nazwy w przypadkowej kolejności "
                       f"(najlepsze {rows[0]['folio']} × {rows[0]['list']}, z = {rows[0]['z']:+.1f}, p popr. {rows[0]['p_adj']:.2f}), "
                       f"choć ta sama procedura znajduje listę ukrytą w glifach rękopisu (z ≥ {worst:.0f}).")
    else:
        res.decide(None)
        res.summary = "Brak diagramów o oczekiwanej liczbie słów."
    res.caveats += ["Sprawdzany jest szyfr literowy (glif → litera, z homofonami); nazwy skrócone, zapisane sylabami albo kodem "
                    "całego słowa nie zostałyby znalezione.",
                    "Pisownia nazw z jednego źródła na listę; średniowieczne warianty (Alnath/Alnach, Albotain/Albothaim) różnią się o 1–2 litery.",
                    "Kolejność słów w kole przyjęta z transliteracji (Takahashi/ZL); błąd kierunku czytania pokrywa przeszukanie obu kierunków."]
    res.seconds = time.time() - t0
    return res
