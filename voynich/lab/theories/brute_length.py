"""Theory: words of one length share a key of their own; brute force over keys, length class by length class.

The user's idea taken literally: the manuscript's words are split into sets of equal length
(2, 3, ..., 8 glyphs and 9+), and every set is attacked separately with the triple brute force of
voynich.lab.brute against six lexicons, as if each set were its own cipher with its own key.
Within a set, a triple is three consecutive words of that length in reading order. The same
controls as in the brute theory, per set: gibberish v5 split the same way, words shuffled,
glyphs relabelled per pseudo-line, and the language's own text enciphered and split by length
(the method must recover each set's key).
"""

from __future__ import annotations

import time
from collections import Counter

from ... import lexicon
from ..brute import (Device, Lexicon, Settings, attack, encipher, paragraph_lines, relabel_lines, shuffle_words)
from ..config import LabConfig
from ..hillclimb import length_class
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs

LANGUAGES = ["Latin", "Italian", "German", "French", "Spanish", "Czech"]
CLASSES = list(range(2, 10))     # 2..8 glyphs and 9+ (one-glyph words cannot be read as anything)


def length_sets(lines, line_len: int = 9) -> dict[int, list[list]]:
    """Words of each length class in reading order, regrouped into pseudo-lines of `line_len`."""
    by: dict[int, list] = {c: [] for c in CLASSES}
    for l in lines:
        for w in l:
            c = length_class(len(w))
            if c in by:
                by[c].append(tuple(w))
    return {c: [ws[i:i + line_len] for i in range(0, len(ws), line_len)] for c, ws in by.items()}


def _fmt(a) -> str:
    return f"spójność {a.consistency:.2f}, słownik {a.dict_rate:.1%}, trójek {a.triples}"


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    dev = Device(prefer_gpu=True)
    names = [n for n in (cfg.brute_languages or LANGUAGES) if n in lexicon.available()]
    classes = CLASSES
    if cfg.quick:
        names, classes = names[:2], [3, 4, 5]
    max_triples = cfg.brute_triples if cfg.brute_triples else (300 if cfg.quick else 4000)
    s = Settings()
    res = TheoryResult(
        theory="brute_length",
        hypothesis="Słowa o tej samej długości mają własny klucz litera-za-glif: każdy zbiór słów jednakowej długości jest "
                   "osobnym szyfrem podstawieniowym któregoś z języków epoki.",
        method=(f"Słowa rękopisu podzielone na zbiory według długości ({', '.join(str(c) for c in classes[:-1])} i 9+ glifów), "
                "każdy zbiór w kolejności czytania pocięty na pseudowiersze po 9 słów; na każdym zbiorze osobno brute force po "
                f"kluczach trójka po trójce (do {max_triples} najczęstszych trójek, {len(names)} leksykonów, {dev.name}): słownik "
                "przycina klucze do odczytów o tym samym wzorze powtórzeń, miary: zgodność odczytów co do jednego klucza i udział "
                "słów w słowniku pod kluczem z wierszy nieparzystych na parzystych. Tło na każdym zbiorze: bełkot v5 podzielony tak "
                "samo, słowa przetasowane, glify przemianowane w każdym pseudowierszu. Kontrola dodatnia: tekst języka zaszyfrowany "
                "losowym kluczem i podzielony według długości; klucz każdego zbioru musi zostać odzyskany."),
        references=["Hauer & Kondrak, Decoding Anagrammed Texts Written in an Unknown Language and Script, TACL 4 (2016)",
                    "Stolfi, On the VMS word length distribution (2000)"])
    lines = paragraph_lines("glyphs")
    n_glyphs = len({g for l in lines for w in l for g in w})
    gen = [[tuple(w) for w in l] for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)
           + generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed + 1)]
    ms_sets, gen_sets = length_sets(lines), length_sets(gen)
    metrics, leads, untestable = {}, [], []
    for name in names:
        try:
            lex = Lexicon.load(name)
            _, _, text = lexicon.load_all(name)
        except Exception as e:
            res.evidence.append(f"{name}: pominięty ({e})")
            continue
        if len(text) < 1000:
            res.evidence.append(f"{name}: pominięty (brak próbki tekstu)")
            continue
        enc, truth = encipher(text, n_glyphs, cfg.seed)
        enc_sets = length_sets(enc)
        metrics[name] = {}
        rows = []
        for c in classes:
            ms = ms_sets[c]
            n_words = sum(map(len, ms))
            if n_words < 300 or sum(map(len, enc_sets[c])) < 300:
                res.evidence.append(f"{name}, długość {c}{'+' if c == 9 else ''}: za mało słów ({n_words}); pominięta.")
                continue
            pos = attack(enc_sets[c], lex, dev, s, min(max_triples, 600), cfg.seed)
            freq = Counter(g for l in enc_sets[c] for w in l for g in w)
            key_acc = sum(freq[gl] for gl, letter in truth.items() if pos.key.get(gl) == letter) / max(1, sum(freq.values()))
            ok = pos.dict_rate >= 0.6 and key_acc >= 0.7
            res.control(f"{name}, długość {c}{'+' if c == 9 else ''}: zaszyfrowany tekst tej długości", "≥ 60% słów w słowniku, ≥ 70% klucza",
                        f"{pos.dict_rate:.0%}, klucz {key_acc:.0%}", ok)
            a = attack(ms, lex, dev, s, max_triples, cfg.seed)
            g = attack(gen_sets[c], lex, dev, s, max_triples, cfg.seed)
            sh = attack(shuffle_words(ms, cfg.seed), lex, dev, s, max_triples, cfg.seed)
            rl = attack(relabel_lines(ms, cfg.seed), lex, dev, s, max_triples, cfg.seed)
            lead = ok and a.consistency >= g.consistency + 0.15 and a.dict_rate >= max(2 * g.dict_rate, 0.25)
            metrics[name][c] = {"words": n_words, "voynich": vars(a), "generator": vars(g), "shuffled": vars(sh), "relabelled": vars(rl),
                                "enciphered": vars(pos), "key_accuracy": key_acc, "testable": ok, "lead": lead}
            if not ok:
                untestable.append(f"{name}/{c}")
            if lead:
                leads.append(f"{name}, długość {c}")
            rows.append(f"długość {c}{'+' if c == 9 else ''} ({n_words} słów): rękopis {_fmt(a)}; bełkot {_fmt(g)}; przemianowane spójność "
                        f"{rl.consistency:.2f}; zaszyfrowany {pos.dict_rate:.0%}, klucz {key_acc:.0%}" + (" TROP" if lead else "")
                        + ("" if ok else " (nietestowalna)"))
            print(f"  {name} dł. {c}: rękopis {a.consistency:.2f}/{a.dict_rate:.1%} | bełkot {g.consistency:.2f}/{g.dict_rate:.1%} | "
                  f"szyfr {pos.dict_rate:.0%} klucz {key_acc:.0%}" + (" TROP" if lead else ""), flush=True)
        res.evidence.append(f"{name}: " + "; ".join(rows) + ".")
    res.controls = [c for c in res.controls if c.passed]
    if untestable:
        res.control("zbiory nietestowalne tą metodą (pominięte w werdykcie)", "jak najmniej", ", ".join(untestable), True)
    tested = [(n, c) for n in metrics for c in metrics[n] if metrics[n][c]["testable"]]
    res.metrics = {"languages": metrics, "untestable": untestable, "n_glyphs": n_glyphs, "device": dev.name, "max_triples": max_triples}
    res.decide(True if leads else False if tested else None)
    if tested:
        bn, bc = max(tested, key=lambda t: metrics[t[0]][t[1]]["voynich"]["dict_rate"])
        b = metrics[bn][bc]
        res.summary = (f"{len(tested)} zbiorów testowalnych ({len(untestable)} pominiętych), {len(names)} języków. "
                       + (f"Tropy: {', '.join(leads)}." if leads else
                          f"W żadnym zbiorze długości rękopis nie wygrywa z bełkotem: najwyższy udział słów w słowniku pod kluczem zbioru "
                          f"{b['voynich']['dict_rate']:.1%} ({bn}, długość {bc}; bełkot {b['generator']['dict_rate']:.1%}, zaszyfrowany tekst "
                          f"{b['enciphered']['dict_rate']:.0%}). Osobny klucz na długość nie pomaga."))
    else:
        res.summary = "Brak testowalnych zbiorów."
    res.caveats += ["W zbiorze jednej długości „trójka” to trzy kolejne słowa tej długości w kolejności czytania, nie sąsiedzi w tekście; "
                    "sens par jest więc słabszym sygnałem niż w teorii brute, liczy się zgodność klucza i udział słów w słowniku.",
                    "Zbiory krótkich słów (2–3 glify) mają mało wzorów powtórzeń, więc wiele odczytów pasuje z przypadku; tło bełkotu to wyrównuje."]
    res.seconds = time.time() - t0
    return res
