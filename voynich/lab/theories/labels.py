"""Theory: the labels at the drawings are a vocabulary of names, and the paragraphs cite them (a register).

See voynich.labels. Two claims with nulls drawn from the manuscript itself: the label words are a
sub-vocabulary of their own (hapax share, o-/q- initials, length against paragraph words of the same
sections, with and without matching word length), and the paragraphs of a page use the labels of
that page more than the labels of other pages of the same section would predict (exact and
within one edit). Within-page uniqueness per label kind as a side result.
"""

from __future__ import annotations

import random
import time

from ... import labels
from ..config import LabConfig
from ..results import TheoryResult


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    draws, shuffles = (100, 200) if cfg.quick else (500, 1000)
    res = TheoryResult(
        theory="labels",
        hypothesis="Słowa przy rysunkach (etykiety) to osobny podsłownik nazw, a akapity tej samej strony cytują je: "
                   "tekst byłby rejestrem (zielnik, almanach, inwentarz) odwołującym się do nazwanych rzeczy.",
        method=(f"Etykiety z loci L* ({', '.join(labels.LABEL_KINDS)}) wobec słów akapitów tych samych działów: hapaksy, "
                "inicjały o-/q-, długość, udział dziesięciu najczęstszych słów, jako z wobec losowań słów akapitów dopasowanych "
                f"liczbą i działem ({draws} losowań; osobno dopasowanych także długością). Cytowanie: udział słów akapitu równych "
                f"etykiecie tej samej strony (lub o jedną zmianę) wobec {shuffles} rozdań zbiorów etykiet między stronami tego "
                "samego działu. Unikalność etykiet w obrębie strony według rodzaju. Kontrole: cytowanie wszczepione (10% słów "
                "akapitu zastąpionych etykietami strony), etykiety rozdane między strony, próbka słów akapitów udająca etykiety, "
                "strony syntetyczne z nazwami."),
        references=["Zandbergen, voynich.nu: loci i rodzaje etykiet w transliteracji ZL",
                    "Currier, Some important new statistical findings (1976)"])
    pages = labels.load_label_pages()
    pool = labels.paragraph_pool()
    both = [p for p in pages if p.paragraphs]
    rng = random.Random(cfg.seed)
    # Controls.
    planted = labels.citation(labels.plant_citations(pages, 0.1, cfg.seed), shuffles, cfg.seed)
    res.control("cytowanie wszczepione (10% słów akapitu to etykiety strony) wykryte", "z ≥ 5", f"z = {planted['z']:.1f}", planted["z"] >= 5)
    dealt = labels.citation(labels.shuffle_labels(pages, rng), shuffles, cfg.seed)
    res.control("etykiety rozdane między strony działu nie są cytowane", "|z| < 2,5", f"z = {dealt['z']:.1f}", abs(dealt["z"]) < 2.5)
    fake = []
    for p in pages:
        src = pool.get(p.section) or [w for ws in pool.values() for w in ws]
        fake.append(labels.LabelPage(p.folio, p.section, p.language, rng.sample(src, len(p.labels)), list(p.kinds), p.paragraphs))
    fake_sv = labels.subvocabulary(fake, pool, draws, cfg.seed)
    worst = max(abs(fake_sv[k]["z"]) for k in ("hapax", "o_initial", "q_initial", "mean_length"))
    res.control("słowa akapitów udające etykiety nie tworzą podsłownika", "|z| < 2,5 dla hapaksów, o-, q-, długości",
                f"max |z| = {worst:.1f}", worst < 2.5)
    syn, syn_pool = labels.synthetic_label_pages(40, cfg.seed, names=True, cite=0.1)
    syn_sv = labels.subvocabulary(syn, syn_pool, draws, cfg.seed)
    syn_cite = labels.citation(syn, shuffles, cfg.seed)
    res.control("strony syntetyczne z nazwami i cytowaniem: podsłownik i cytowanie wykryte", "hapaksy z ≥ 4, o- z ≥ 4, cytowanie z ≥ 5",
                f"hapaksy {syn_sv['hapax']['z']:.1f}, o- {syn_sv['o_initial']['z']:.1f}, cytowanie {syn_cite['z']:.1f}",
                syn_sv["hapax"]["z"] >= 4 and syn_sv["o_initial"]["z"] >= 4 and syn_cite["z"] >= 5)
    # Measurements.
    sv_a = labels.subvocabulary(pages, pool, draws, cfg.seed)
    sv_b = labels.subvocabulary(pages, pool, draws, cfg.seed, match_length=True)
    cite = labels.citation(pages, shuffles, cfg.seed)
    cite_near = labels.citation(pages, shuffles, cfg.seed, near=True)
    uniq = labels.uniqueness(pages, shuffles // 2, cfg.seed)
    by_section = {}
    for section in sorted({p.section for p in both}):
        sub = [p for p in both if p.section == section]
        if len(sub) >= 4:
            by_section[section] = labels.citation(sub, shuffles, cfg.seed)
    res.metrics = {"pages": len(pages), "pages_with_paragraphs": len(both), "subvocabulary": sv_a,
                   "subvocabulary_length_matched": {k: v for k, v in sv_b.items() if k != "mean_length"},
                   "citation": cite, "citation_near": cite_near, "citation_by_section": by_section, "uniqueness": uniq,
                   "controls": {"planted": planted, "dealt": dealt, "fake_labels": fake_sv}}
    names = {"hapax": "hapaksy", "o_initial": "inicjał o-", "q_initial": "inicjał q-", "mean_length": "długość", "top10": "dziesięć najczęstszych"}
    res.evidence.append(f"{sv_a['n_labels']} etykiet na {len(pages)} stronach; {sv_a['absent_types']:.0%} typów etykiet nie występuje "
                        "w żadnym akapicie. Wobec słów akapitów tych samych działów: "
                        + "; ".join(f"{names[k]} {sv_a[k]['value']:.3f} wobec {sv_a[k]['null_mean']:.3f} (z = {sv_a[k]['z']:+.1f})" for k in labels.STATS) + ".")
    res.evidence.append("Po dopasowaniu także długości słów: " + "; ".join(f"{names[k]} z = {sv_b[k]['z']:+.1f}" for k in ("hapax", "o_initial", "q_initial", "top10")) + ".")
    res.evidence.append(f"Cytowanie: {cite['value']:.2%} słów akapitu równych etykiecie tej samej strony wobec {cite['null_mean']:.2%} "
                        f"przy etykietach rozdanych w dziale (z = {cite['z']:+.1f}; {cite['pages']} stron, {cite['tokens']} słów); "
                        f"o najwyżej jedną zmianę: {cite_near['value']:.1%} wobec {cite_near['null_mean']:.1%} (z = {cite_near['z']:+.1f}).")
    if by_section:
        res.evidence.append("Cytowanie według działów: " + "; ".join(f"{s} {m['value']:.2%} wobec {m['null_mean']:.2%} (z = {m['z']:+.1f}, {m['pages']} stron)" for s, m in by_section.items()) + ".")
    res.evidence.append("Unikalność etykiet na stronie: " + "; ".join(f"{k} {m['value']:.0%} (z = {m['z']:+.1f}, {m['labels']} etykiet)" for k, m in uniq.items()) + ".")
    d1 = sum(abs(sv_a[k]["z"]) >= 4 for k in ("hapax", "o_initial", "q_initial", "mean_length")) >= 3 and \
        (abs(sv_b["o_initial"]["z"]) >= 3 or abs(sv_b["q_initial"]["z"]) >= 3)
    d2 = cite["z"] >= 3
    res.decide(True if (d1 and d2) else (None if d1 else False))
    res.summary = (("Etykiety są osobnym podsłownikiem nazw" if d1 else "Etykiety nie różnią się od słów akapitów")
                   + f" (hapaksy z = {sv_a['hapax']['z']:+.1f}, o- {sv_a['o_initial']['z']:+.1f}, q- {sv_a['q_initial']['z']:+.1f}, "
                   f"długość {sv_a['mean_length']['z']:+.1f}; o- po dopasowaniu długości {sv_b['o_initial']['z']:+.1f})"
                   + (f"; akapity cytują etykiety swojej strony (z = {cite['z']:+.1f})." if d2 else
                      f"; akapity nie cytują etykiet swojej strony ponad to, co dają etykiety innych stron działu "
                      f"(z = {cite['z']:+.1f}, o jedną zmianę {cite_near['z']:+.1f}): nazwy są, tekst się do nich nie odwołuje."))
    res.caveats += ["Etykiety i akapity tej samej strony pisze ta sama ręka w tym samym dziale, więc tło z etykiet innych stron "
                    "działu jest surowe; pozytywna kontrola pokazuje, że 10% cytowań i tak widać.",
                    "Rodzaje etykiet La, Lp, Lx (12 słów) pominięto; etykiety wielowyrazowe liczone słowo po słowie."]
    res.seconds = time.time() - t0
    return res
