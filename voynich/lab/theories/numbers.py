"""Theory 1: the glyphs are numbers.

Two independent tests.

A. Whole text as numerals. Numbers drawn from a realistic distribution are
   written in five numeral systems known before 1450 (positional decimal,
   Roman with and without subtraction, Greek/Hebrew-style alphabetic numerals,
   positional base 20). Each numeral text is profiled like the manuscript and
   compared with it and with 12 languages. Any substitution of symbols leaves
   these measures unchanged, so the result covers every encrypted variant.

B. Zodiac labels as day numbers. Each zodiac page has 30 (or 15 + 15) labels
   next to the figures. If they count days 1..30 in order, labels next to each
   other must look alike, as consecutive numerals do. A permutation test
   compares neighbouring labels with the same labels shuffled. Planted numeral
   sequences are the positive control.
"""

from __future__ import annotations

import time

from ... import eva, ivtff
from ...corpus import ZL_FILE, load_reference, load_voynich
from ..common import (SHAPE_METRICS, distance, language_scales, levenshtein, permutation_p, profile, rng,
                      voynich_glyph_words)
from ..config import LabConfig
from ..results import TheoryResult

ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
         (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
ROMAN_ADDITIVE = [(1000, "M"), (500, "D"), (100, "C"), (50, "L"), (10, "X"), (5, "V"), (1, "I")]


def roman(v: int, subtractive: bool = True) -> list[str]:
    out = []
    for value, sym in (ROMAN if subtractive else ROMAN_ADDITIVE):
        while v >= value:
            out.append(sym)  # "CM" stays one unit: written as two letters, but a fixed pair
            v -= value
    return [c for s in out for c in s]


def positional(v: int, base: int) -> list[str]:
    digits = []
    while True:
        digits.append(f"d{v % base}")
        v //= base
        if v == 0:
            return digits[::-1]


def alphabetic(v: int) -> list[str]:
    """Greek/Hebrew style: one sign for each of 1-9, 10-90, 100-900; thousands get a mark."""
    out = []
    if v >= 1000:
        out += ["#", f"u{v // 1000}"]
        v %= 1000
    for unit, tag in ((100, "h"), (10, "t"), (1, "u")):
        if v >= unit:
            out.append(f"{tag}{v // unit}")
            v %= unit
    return out


SYSTEMS = {
    "dziesiętny pozycyjny": lambda v: positional(v, 10),
    "dwudziestkowy pozycyjny": lambda v: positional(v, 20),
    "rzymski (z odejmowaniem)": lambda v: roman(v, True),
    "rzymski addytywny (IIII, VIIII)": lambda v: roman(v, False),
    "alfabetyczny (grecki/hebrajski)": alphabetic,
}


def number_sample(n: int, r, kind: str = "counts") -> list[int]:
    """Value distributions; each numeral system is tried with all of them and keeps its best."""
    out = []
    for _ in range(n):
        if kind == "counts":  # recipes and tallies: mostly small, Benford-like tail to 3999
            v = int(30 ** r.random()) if r.random() < 0.6 else int(3999 ** r.random())
        elif kind == "log-uniform":  # astronomical tables: magnitudes up to 10^5
            v = int(100000 ** r.random())
        else:  # uniform 1..1000
            v = r.randint(1, 1000)
        out.append(max(1, v))
    return out


DISTRIBUTIONS = ("counts", "log-uniform", "uniform")
MATCH, MISMATCH = 0.5, 1.0  # RMS distance in between-language spreads; two Latin samples differ by ~0.2


def zodiac_label_pages() -> list[list[list[str]]]:
    """Per zodiac page, the first word of each label in transliteration order (around the rings)."""
    pages = []
    for p in ivtff.parse(ZL_FILE):
        if p.section != "zodiac":
            continue
        labels = []
        for loc in p.loci:
            if loc.kind.startswith("L"):
                ws = eva.words(eva.clean(loc.raw), drop_uncertain=False)
                if ws:
                    labels.append(eva.glyphs(ws[0].replace("?", "")))
        if len(labels) >= 10:
            pages.append(labels)
    return pages


def neighbour_dissimilarity(pages: list[list[list[str]]]) -> float:
    """Mean normalised edit distance between labels standing next to each other."""
    total = n = 0
    for labels in pages:
        for a, b in zip(labels, labels[1:]):
            total += levenshtein(a, b) / max(len(a), len(b), 1)
            n += 1
    return total / n


def sequence_test(pages, trials: int, r) -> tuple[float, float, float]:
    obs = neighbour_dissimilarity(pages)
    null = []
    for _ in range(trials):
        shuffled = []
        for labels in pages:
            s = labels[:]
            r.shuffle(s)
            shuffled.append(s)
        null.append(neighbour_dissimilarity(shuffled))
    return obs, sum(null) / len(null), permutation_p(obs, null)


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    r = rng(cfg.seed)
    n = 8000 if cfg.quick else 20000
    trials = 300 if cfg.quick else 3000
    res = TheoryResult(
        theory="numbers",
        hypothesis="Znaki rękopisu zapisują liczby (cały tekst albo przynajmniej etykiety w dziale zodiakalnym).",
        method=("A: teksty liczb w 5 systemach liczbowych sprzed 1450 r. porównane z rękopisem i 12 językami "
                "na 10 miarach kształtu tekstu (niezależnych od podstawienia znaków). "
                "B: test permutacyjny podobieństwa sąsiednich etykiet zodiaku (czy wyglądają jak kolejne liczby 1–30)."),
        references=["Bowern & Lindemann, The Linguistics of the Voynich Manuscript, Annual Review of Linguistics 7 (2021)",
                    "Wikipedia/Voynich: 'oror or' na f15v przypomina zaszyfrowane cyfry rzymskie"],
    )

    # A. numeral systems as whole texts
    langs, scales = language_scales(n)
    voy = profile(voynich_glyph_words()[:n])
    systems, best_dist = {}, {}
    for name, enc in SYSTEMS.items():
        cands = {kind: profile([enc(v) for v in number_sample(n, r, kind)]) for kind in DISTRIBUTIONS}
        best_dist[name] = min(cands, key=lambda k: distance(cands[k], voy, scales))
        systems[name] = cands[best_dist[name]]
    d_sys = {k: distance(p, voy, scales) for k, p in systems.items()}
    d_lang = {k: distance(p, voy, scales) for k, p in langs.items()}
    best_sys, best_lang = min(d_sys, key=d_sys.get), min(d_lang, key=d_lang.get)

    # Control: the same distance must recognise a language from another sample of itself.
    latin_b = profile(load_reference("Latin")[n:2 * n])
    nearest = min(langs, key=lambda k: distance(langs[k], latin_b, scales))
    res.control("rozpoznanie języka", "druga próbka łaciny najbliżej pierwszej",
                f"najbliżej: {nearest} (odległość {distance(langs[nearest], latin_b, scales):.2f})", nearest == "Latin")
    supported_a = d_sys[best_sys] < MATCH
    refuted_a = d_sys[best_sys] > MISMATCH
    res.evidence.append(f"Najbliższy system liczbowy: {best_sys}, odległość {d_sys[best_sys]:.2f}; "
                        f"najbliższy język: {best_lang}, {d_lang[best_lang]:.2f} (jednostka: rozrzut między językami).")
    for k, p in systems.items():
        res.evidence.append(f"{k} (rozkład {best_dist[k]}): odległość {d_sys[k]:.2f}, h2={p['h2']:.2f}, sztywność kolejności={p['order_consistency']:.2f}, "
                            f"typy={p['types']}, hapaksy={p['hapax_ratio']:.0%}, średnia dł.={p['mean_word_len']:.1f}")
    res.evidence.append(f"Rękopis: h2={voy['h2']:.2f}, sztywność={voy['order_consistency']:.2f}, typy={voy['types']}, "
                        f"hapaksy={voy['hapax_ratio']:.0%}, średnia dł.={voy['mean_word_len']:.1f}")

    # B. zodiac labels as consecutive numbers
    pages = zodiac_label_pages()
    obs, null_mean, p = sequence_test(pages, trials, r)
    planted = {}
    for name in ("rzymski addytywny (IIII, VIIII)", "alfabetyczny (grecki/hebrajski)", "dziesiętny pozycyjny"):
        fake = [[SYSTEMS[name](i + 1) for i in range(len(lbl))] for lbl in pages]
        planted[name] = sequence_test(fake, trials, r)
        res.control(f"podłożone liczby 1–30 ({name})", "test wykrywa ciąg (p < 0,01)",
                    f"p = {planted[name][2]:.4f}", planted[name][2] < 0.01)
    words = [w for lbl in pages for w in lbl]
    # Calibration: on random label sets the test must raise false alarms at about its nominal 5% rate.
    reps = 10 if cfg.quick else 20
    false_alarms = 0
    for _ in range(reps):
        fake_random = [[words[r.randrange(len(words))] for _ in lbl] for lbl in pages]
        false_alarms += sequence_test(fake_random, 200, r)[2] < 0.05
    res.control("kalibracja na losowych etykietach", "fałszywe alarmy (p < 0,05) w ok. 5% zestawów, najwyżej 20%",
                f"{false_alarms}/{reps}", false_alarms / reps <= 0.2)
    # Effect size: how much more alike neighbours are than shuffled ones.
    effect = 1 - obs / null_mean
    planted_min = min(1 - v[0] / v[1] for v in planted.values())
    # Alternative explanation: the manuscript's general habit of writing similar words next to each other.
    lines = [[eva.glyphs(w) for w in l.words] for l in load_voynich()
             if l.kind.startswith("P") and len(l.words) >= 6][:600]
    text_obs, text_null, _ = sequence_test(lines, max(50, trials // 20), r)
    text_effect = 1 - text_obs / text_null
    supported_b = p < 0.01 and effect >= planted_min / 2
    refuted_b = p >= 0.01 or effect < planted_min / 4
    res.evidence.append(f"Zodiak: {len(pages)} stron, {sum(len(x) for x in pages)} etykiet. Niepodobieństwo sąsiadów "
                        f"{obs:.3f} wobec {null_mean:.3f} po przetasowaniu (efekt {effect:.1%}), p = {p:.4f}.")
    res.evidence.append(f"Podłożone liczby 1–30 dają efekt co najmniej {planted_min:.0%}; zwykłe wiersze tekstu "
                        f"rękopisu dają {text_effect:.1%} (ogólny zwyczaj pisania podobnych słów obok siebie).")

    res.metrics = {"distance_systems": d_sys, "distance_languages": d_lang, "voynich": voy, "systems": systems,
                   "zodiac": {"observed": obs, "shuffled": null_mean, "p": p, "pages": len(pages), "effect": effect,
                              "planted_min_effect": planted_min, "running_text_effect": text_effect,
                              "planted": {k: {"observed": v[0], "p": v[2]} for k, v in planted.items()}},
                   "metrics_used": SHAPE_METRICS}
    if supported_a or supported_b:
        res.decide(True)
    elif refuted_a and refuted_b:
        res.decide(False)
    else:
        res.decide(None)
    verdict_a = "pasuje" if supported_a else "nie pasuje" if refuted_a else "niejasne"
    res.summary = (f"Cały tekst jako liczby: {verdict_a} (najbliższy system: {best_sys}, odległość {d_sys[best_sys]:.2f}; "
                   f"dopasowanie wymaga < {MATCH}, dwie próbki łaciny różnią się o ok. 0,2). Etykiety zodiaku jako kolejne "
                   f"liczby: {'tak' if supported_b else 'nie'} (efekt {effect:.1%} przy p = {p:.3f}; liczby podłożone dają "
                   f"≥ {planted_min:.0%}, zwykły tekst rękopisu {text_effect:.1%}).")
    res.caveats += [
        "Rozkład liczb jest założony (dużo małych liczb, ogon do 3999); inny rozkład zmienia liczbę typów i hapaksów.",
        "Test B zakłada, że kolejność etykiet w transliteracji odpowiada kolejności wokół pierścieni.",
        "Szyfr homofoniczny zapisujący liczby rozmyłby podobieństwo kolejnych etykiet; test B go nie wykluczy.",
    ]
    res.seconds = time.time() - t0
    return res
