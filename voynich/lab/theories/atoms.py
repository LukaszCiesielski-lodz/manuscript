"""Theory: a rebus in the drawings; drawn features predict the label written beside them.

See voynich.atoms. People (and a vision model, as a draft) take the drawings apart into atoms
with observable features, each tied to its label. For every pair (drawn feature, label
feature: first, second and last glyph, length, gallows, two-glyph prefix) the mutual
information is compared with labels shuffled among the atoms of the same page, with a
Bonferroni correction over all pairs. Features two annotators disagree on (kappa < 0.6) are
left out. Controls: a first glyph planted according to a feature must be found; features
shuffled among atoms of a page must not be. Until at least 100 atoms are described, the
controls run on randomly filled templates and the verdict stays undecided.
"""

from __future__ import annotations

import time
from collections import defaultdict

from ... import atoms as A
from ..config import LabConfig
from ..results import TheoryResult

MIN_FILLED = 100
MIN_REFUTE = 200
KAPPA_MIN = 0.6


def _kappa_filter(atoms: list[A.Atom], res: TheoryResult) -> tuple[list[A.Atom], dict]:
    """Drop features with low agreement when two sources described the same pages; keep one source per atom."""
    by_source: dict[str, list[A.Atom]] = defaultdict(list)
    for a in atoms:
        by_source[a.zrodlo or "?"].append(a)
    sources = sorted(by_source, key=lambda s: -len(by_source[s]))
    kappas: dict[str, tuple[float, int]] = {}
    for i, s in enumerate(sources):
        for t in sources[i + 1:]:
            for k, (kap, n) in A.agreement(by_source[s], by_source[t]).items():
                if n >= 10 and (k not in kappas or n > kappas[k][1]):
                    kappas[k] = (kap, n)
    bad = {k for k, (kap, n) in kappas.items() if kap < KAPPA_MIN}
    if kappas:
        res.evidence.append("Zgodność dwóch osób (kappa): " + ", ".join(f"{k} {kap:.2f} (n={n})" for k, (kap, n) in sorted(kappas.items()))
                            + (f". Wykluczone (kappa < {KAPPA_MIN}): {', '.join(sorted(bad))}." if bad else "."))
    seen, kept = set(), []
    for s in sources:   # the most prolific source wins where two described the same atom
        for a in by_source[s]:
            if a.id in seen:
                continue
            seen.add(a.id)
            cechy = {k: (None if f"{a.typ}.{k}" in bad else v) for k, v in a.cechy.items()}
            kept.append(A.Atom(a.page, a.section, a.id, a.typ, cechy, a.pozycja, a.etykieta, a.zrodlo, a.pewnosc, a.uwaga))
    return kept, {k: {"kappa": kap, "n": n} for k, (kap, n) in kappas.items()}


def _fmt(rows: list[dict], k: int = 5) -> str:
    return "; ".join(f"{r['cecha']}×{r['etykieta']} (n={r['n']}, MI {r['mi']:.3f} wobec {r['null_mean']:.3f}, z = {r['z']:+.1f}, "
                     f"p popr. {r['p_adj']:.2f})" for r in rows[:k])


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 300 if cfg.quick else 2000
    res = TheoryResult(
        theory="atoms",
        hypothesis="Rebus w rysunkach: jakaś widoczna cecha narysowanej rzeczy (liczba promieni, kolor, kształt, gest) "
                   "przewiduje coś w etykiecie napisanej obok (pierwszy glif, długość, końcówkę).",
        method=("Atomy ilustracji z data/atoms (jeden rekord na etykietę, cechy ze słownika kontrolowanego, wpisane przez ludzi; "
                "szkic z modelu widzącego osobno). Dla każdej pary (cecha rysunku, cecha etykiety) informacja wzajemna wobec "
                f"etykiet przetasowanych w obrębie strony ({shuffles} tasowań), poprawka Bonferroniego na liczbę par. Cechy o zgodności "
                f"dwóch osób kappa < {KAPPA_MIN} wykluczone. Kontrole: pierwszy glif etykiety podłożony według cechy w 60% atomów "
                "(musi wyjść p popr. < 0,05, z ≥ 5); cechy przetasowane między atomami strony (żadna para p popr. < 0,05 i z ≥ 4)."),
        references=["Zandbergen, voynich.nu: descriptions of the zodiac and pharmaceutical pages",
                    "Cohen (1960), A coefficient of agreement for nominal scales"])
    vocab = A.load_vocab()
    all_atoms = A.load(vocab=vocab)
    stats = A.summary(all_atoms)
    done = A.filled(all_atoms)
    res.metrics["annotation"] = stats
    res.evidence.append(f"Atomów {stats['atoms']} na {stats['pages']} stronach; opisanych (≥ 1 cecha i etykieta) {stats['filled']} "
                        f"na {stats['pages_filled']} stronach; źródła: {', '.join(stats['sources']) or 'brak'}; "
                        f"działy: {stats['per_section'] or '–'}.")
    demo = len(done) < MIN_FILLED
    if demo:
        done = A.filled(A.random_fill(all_atoms, vocab, seed=cfg.seed))
        res.evidence.append(f"Za mało opisanych atomów (próg {MIN_FILLED}): kontrole metody liczone na szablonach wypełnionych losowo; "
                            "test właściwy czeka na dane.")
        kappas = {}
    else:
        done, kappas = _kappa_filter(done, res)
    res.metrics["kappa"] = kappas
    # Controls on the same material.
    # The planted control needs a feature that actually varies: the most filled one with at least three values.
    values = defaultdict(list)
    for a in done:
        for k, v in a.cechy.items():
            if v is not None:
                values[f"{a.typ}.{k}"].append(v)
    varied = {k: v for k, v in values.items() if len(set(v)) >= 3} or values
    key = max(varied, key=lambda k: len(varied[k])) if varied else "nimfa.trzyma"
    planted = A.pair_scan(A.plant(done, key, 0.6, cfg.seed), shuffles, cfg.seed)
    hit = next((r for r in planted if r["cecha"] == key and r["etykieta"] == "pierwszy"), None)
    res.control(f"podłożony pierwszy glif według {key} wykryty", "p popr. < 0,05 i z ≥ 5",
                f"z = {hit['z']:.1f}, p popr. {hit['p_adj']:.3f}" if hit else "para nieobecna (za mało atomów)",
                bool(hit and A.significant(hit, 5.0)))
    shuffled = A.pair_scan(A.shuffle_features(done, cfg.seed + 1), shuffles, cfg.seed)
    worst = shuffled[0] if shuffled else None
    res.control("cechy przetasowane między atomami strony bez związku", "żadna para p popr. < 0,05 i z ≥ 4",
                f"najlepsza para {worst['cecha']}×{worst['etykieta']} z = {worst['z']:+.1f}, p popr. {worst['p_adj']:.2f}" if worst else "brak par",
                not any(A.significant(r) for r in shuffled))
    res.metrics["controls"] = {"planted_z": hit["z"] if hit else None, "shuffled_best_z": worst["z"] if worst else None}
    if demo:
        res.decide(None)
        res.summary = (f"Dane niekompletne: opisanych {stats['filled']} z {stats['atoms']} atomów (próg {MIN_FILLED}). Metoda sprawdzona na "
                       f"losowym wypełnieniu: podłożony glif z = {hit['z']:.0f}, przetasowane cechy bez związku.")
        res.caveats.append("Szablony leżą w data/atoms (jeden plik na stronę); wypełnienie 'cechy' według data/atoms/README.md uruchamia test.")
        res.seconds = time.time() - t0
        return res
    rows = A.pair_scan(done, shuffles, cfg.seed)
    res.metrics["pairs"] = rows[:40]
    res.metrics["n_pairs"] = len(rows)
    res.evidence.append(f"Par (cecha rysunku × cecha etykiety) z ≥ 30 atomami: {len(rows)}. Najsilniejsze: {_fmt(rows)}.")
    sig = [r for r in rows if A.significant(r)]
    if sig:
        res.decide(True)
        res.summary = f"Cecha rysunku przewiduje etykietę: {_fmt(sig, 3)}."
    elif len(done) >= MIN_REFUTE and (not rows or rows[0]["z"] < 2):
        res.decide(False)
        res.summary = (f"Żadna z {len(rows)} par cecha rysunku × cecha etykiety nie przekracza tła (najlepsza z = {rows[0]['z']:+.1f}) "
                       f"przy {len(done)} opisanych atomach.")
    else:
        res.decide(None)
        res.summary = (f"Brak pary po poprawce (najlepsza {_fmt(rows, 1)}); opisanych atomów {len(done)}"
                       + (f", do obalenia potrzeba ≥ {MIN_REFUTE} i najlepszej z < 2." if len(done) < MIN_REFUTE else "."))
    res.caveats += ["Cechy wpisane przez ludzi: błędy odczytu i uznaniowość (co jest 'jednym liściem') obniżają moc testu; kappa to mierzy.",
                    "Test szuka zależności cecha-po-cesze; rebus łączący kilka cech naraz w jeden glif wymaga więcej danych."]
    res.seconds = time.time() - t0
    return res
