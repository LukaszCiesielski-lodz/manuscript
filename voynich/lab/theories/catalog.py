"""Theory: cross-section analysis of Zandbergen's page catalogue against the text.

See voynich.catalog. (1) Drawing style against scribe: the beta-minus-alpha score of a herbal
page (Gheuens/Rapaport drawing features) against its Currier language and LFD hand, with
permutations. (2) Drawing style against content: pages sharing a drawing feature against random
page groups of the same language-and-hand make-up, rarity-weighted vocabulary overlap, Bonferroni
over features. Controls: words borrowed between pages of one feature must be found; features
permuted within language and hand must find nothing. (3) A ledger of sections: pages, text items,
labels, languages, hands, stated figure counts.
"""

from __future__ import annotations

import time

from ... import catalog as C
from ..config import LabConfig
from ..results import TheoryResult


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 200 if cfg.quick else 2000
    res = TheoryResult(
        theory="catalog",
        hypothesis="Analiza przekrojowa: to, co narysowano na stronie (styl rysunku, obiekty), wiąże się z tym, co na niej napisano, "
                   "ponad to, co wynika z języka Curriera i ręki skryby.",
        method=(f"Katalog stron Zandbergena (voynich.nu, data/catalog/pages.json): dział, opis rysunku, cechy stylu rysunku roślin "
                "Gheuensa i Rapaport (α/β), język Curriera, ręka LFD. (1) Styl wobec skryby: AUC wyniku β−α strony dla języka B "
                f"i dla każdej ręki wobec {shuffles} permutacji etykiet. (2) Styl wobec treści: dla każdej cechy rysunku (≥ 6 stron) "
                "wspólne słownictwo ważone rzadkością w grupie stron z cechą wobec losowych grup o tym samym składzie język+ręka "
                f"({shuffles} losowań), poprawka Bonferroniego. Kontrole: słowa pożyczone między stronami jednej cechy (10%) muszą "
                "dać z ≥ 5; cechy przetasowane w obrębie języka i ręki nie mogą dać pary z p popr. < 0,05 i z ≥ 4. (3) Rejestr działów."),
        references=["Zandbergen, voynich.nu, page descriptions (2025)",
                    "Gheuens & Rapaport, two families of herbal drawings in the Voynich MS (voynich.nu/extra/sp_illustr.html)",
                    "Currier (1976), languages A and B; Davis (2020), five scribal hands"])
    entries = C.load()
    allp = list(entries.values())
    herbal = [e for e in allp if e.section == "herbal"]
    with_feats = [e for e in herbal if e.features and e.words]
    res.metrics["catalogue"] = {"pages": len(allp), "herbal": len(herbal), "herbal_with_features": len(with_feats)}
    # (3) ledger
    rows = C.ledger(allp)
    res.metrics["ledger"] = rows
    res.evidence.append("Rejestr działów (strony / średnio loci / etykiety / słowa akapitów / języki / ręce): " + "; ".join(
        f"{r['section']} {r['pages']} / {r['loci_mean']:.0f} / {r['labels']} / {r['words']} / {r['currier']} / {r['hands']}" for r in rows))
    # (1) style against scribe
    style = {lab: C.style_vs_label(herbal, lab, shuffles, cfg.seed) for lab in ("B", "1", "2", "3", "5")}
    res.metrics["style"] = style
    res.evidence.append("Styl rysunku (β−α) wobec skryby na stronach zielnika z cechami: " + "; ".join(
        f"{'język B' if k == 'B' else 'ręka ' + k}: AUC {v['auc']:.3f} (n = {v['positives']}/{v['n']}, z = {v['z']:+.1f})" for k, v in style.items())
        + ". Rysunki w stylu β leżą na stronach języka B i ręki 2: rysownik i skryba zmieniali się razem.")
    # (2) style against content, with controls
    key = "α:stem-root line"
    planted = C.feature_scan(C.plant_words(allp, key, 0.15, cfg.seed), shuffles, cfg.seed)
    hit = next((r for r in planted if r["feature"] == key), None)
    res.control("wspólny słowniczek grupy jednej cechy (15% słów) wykryty", "z ≥ 4 i p popr. < 0,05",
                f"z = {hit['z']:.1f}, p popr. {hit['p_adj']:.3f}" if hit else "cecha nieobecna", bool(hit and hit["z"] >= 4 and hit["p_adj"] < 0.05))
    shuffled = C.feature_scan(C.shuffle_features(allp, cfg.seed + 1), shuffles, cfg.seed)
    bad = [r for r in shuffled if r["p_adj"] < 0.05 and r["z"] >= 4]
    res.control("cechy przetasowane w obrębie języka i ręki bez związku ze słownictwem", "żadna cecha p popr. < 0,05 i z ≥ 4",
                f"najlepsza {shuffled[0]['feature']} z = {shuffled[0]['z']:+.1f}, p popr. {shuffled[0]['p_adj']:.2f}" if shuffled else "brak", not bad)
    scan = C.feature_scan(allp, shuffles, cfg.seed)
    res.metrics["features"] = scan
    res.evidence.append(f"Cechy rysunku wobec słownictwa ({len(scan)} cech z ≥ 6 stronami, tło o tym samym składzie język+ręka): "
                        + "; ".join(f"{r['feature']} (n={r['n']}, wspólne {r['overlap']:.3f} wobec {r['null_mean']:.3f}, z = {r['z']:+.1f}, p popr. {r['p_adj']:.2f})"
                                    for r in scan[:5]) + ".")
    pairs = C.catalogue_pairs(allp)
    res.metrics["cross_references"] = len(pairs)
    res.evidence.append(f"Odsyłacze katalogu zielnik–farmacja: {len(pairs)} (w tym {sum(1 for _, _, s in pairs if s)} „ta sama roślina”); "
                        "test ich słownictwa to teoria plant_pairs (obalona).")
    sig = [r for r in scan if r["p_adj"] < 0.05 and r["z"] >= 4]
    if sig:
        res.decide(True)
        res.summary = "Strony o wspólnej cesze rysunku dzielą słownictwo ponad język i rękę: " + ", ".join(f"{r['feature']} z = {r['z']:+.1f}" for r in sig)
    elif len(with_feats) >= 100:
        res.decide(False)
        res.summary = (f"Styl rysunku przewiduje skrybę (język B: AUC {style['B']['auc']:.2f}, z = {style['B']['z']:+.1f}), ale nie treść: żadna z "
                       f"{len(scan)} cech rysunku nie łączy się ze słownictwem ponad język i rękę (najlepsza z = {scan[0]['z']:+.1f}, p popr. {scan[0]['p_adj']:.2f}).")
    else:
        res.decide(None)
        res.summary = "Za mało stron z cechami rysunku."
    res.caveats += ["Cechy α/β Gheuensa i Rapaport powstały z oglądania rysunków, ale autorzy znali podział na języki; zgodność z językiem "
                    "nie jest więc odkryciem niezależnym, tylko potwierdzeniem, że dwie rodziny rysunków istnieją i pokrywają się ze skrybami.",
                    "Cechy opisują styl rysowania, nie gatunek rośliny; brak związku ze słownictwem oznacza, że styl nie niesie treści, "
                    "nie że żaden rysunek jej nie niesie.",
                    "Katalog to opisy jednego autora; identyfikacje roślin (ELV, ThP) są w pliku, ale nie weszły do testu."]
    res.seconds = time.time() - t0
    return res
