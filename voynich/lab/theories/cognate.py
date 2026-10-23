"""Theory: the manuscript's words are the words of a known language (or its cognates) under a glyph key.

See voynich.lab.cognate: the NeuroDecipher idea (match the vocabulary of the lost script to the
vocabulary of a candidate language with a soft glyph-to-letter key and optimal transport),
run on the GPU for every lexicon. Judged on held-out folios by the share of word tokens that
the hard key turns into lexicon words or words one edit away, against meaningless text of the
manuscript's statistics, and against a real text with spelling noise enciphered the same way
(the key must be recovered).
"""

from __future__ import annotations

import time

from ... import lexicon
from ..brute import paragraph_lines
from ..cognate import (EditIndex, Fit, Vocab, cognate_rate, fit, glyph_inventory, key_accuracy, noisy_encipher,
                       type_counts)
from ..config import LabConfig
from ..results import TheoryResult
from .brute import QUICK_LANGUAGES
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs


def _split(lines):
    return [l for i, l in enumerate(lines) if i % 2 == 0], [l for i, l in enumerate(lines) if i % 2 == 1]


def _attack(lines, known: Vocab, index: EditIndex, s: Fit, n_types: int, log=None) -> dict:
    odd, even = _split(lines)
    glyphs = glyph_inventory(odd)
    lost = Vocab.from_counts(type_counts(odd), glyphs, n_types)
    out = fit(lost, known, s, log)
    out["exact"], out["near"] = cognate_rate(even, out["key"], index)
    return out


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    names = cfg.attack_languages or (QUICK_LANGUAGES if cfg.quick else lexicon.available())
    names = [n for n in names if n in lexicon.available()]
    s = Fit(restarts=4 if cfg.quick else cfg.cognate_restarts, steps=60 if cfg.quick else cfg.cognate_steps, seed=cfg.seed)
    n_types, n_words = (500, 2000) if cfg.quick else (cfg.cognate_types, cfg.cognate_words)
    res = TheoryResult(
        theory="cognate",
        hypothesis="Słowa rękopisu to słowa (lub bliskie formy) któregoś z języków epoki pod jednym kluczem glif–litera; "
                   "dopasowanie całego słownictwa do słownika języka odsłania klucz.",
        method=(f"Metoda NeuroDecipher: miękki klucz (softmax nad literami dla każdego glifu), cechy bigramów i "
                f"bigramów z przeskokiem słów, transport optymalny (Sinkhorn) między {n_types} typami słów rękopisu a "
                f"{n_words} słowami języka, spadek gradientu po kluczu, {s.restarts} startów w jednej paczce na GPU. "
                "Klucz twardy z foliów nieparzystych oceniany na parzystych: udział słów w słowniku lub o jedną zmianę "
                "od słowa słownika. Tło: bełkot v5. Kontrola dodatnia: tekst języka z 30% słów zmienionych o jedną "
                "literę, zaszyfrowany losowym kluczem; metoda musi odzyskać klucz."),
        references=["Luo, Cao & Barzilay, Neural decipherment via minimum-cost flow: from Ugaritic to Linear B, ACL 2019",
                    "Luo et al., Deciphering undersegmented ancient scripts using phonetic prior, TACL 2021"])
    try:
        import torch  # noqa: F401
    except ImportError:
        res.evidence.append("Brak PyTorch: uruchom w Colabie.")
        res.decide(None)
        res.summary = "Pominięte: wymaga PyTorch."
        res.seconds = time.time() - t0
        return res
    lines = paragraph_lines("glyphs")
    n_glyphs = len(glyph_inventory(lines))
    gen = [[tuple(w) for w in l] for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)
           + generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed + 1)]
    log = (lambda m: print(m, flush=True)) if not cfg.quick else None
    metrics, leads, untestable = {}, [], []
    for name in names:
        try:
            counts, _, text = lexicon.load_all(name)
        except Exception as e:
            res.evidence.append(f"{name}: pominięty ({e})")
            continue
        if len(text) < 3000:
            res.evidence.append(f"{name}: pominięty (za mała próbka tekstu)")
            continue
        letters = sorted({c for w, _ in counts.most_common(n_words) for c in w})
        known = Vocab.from_counts(counts, letters, n_words)
        index = EditIndex(known.strings)
        enc, truth = noisy_encipher(text, n_glyphs, cfg.seed)
        covered = sum(len(w) for l in enc for w in l) / max(1, sum(len(w) for w in text))
        if covered < 0.5:
            res.evidence.append(f"{name}: nietestowalny – {n_glyphs} glifów niesie tylko {covered:.0%} tekstu tego pisma.")
            untestable.append(name)
            continue
        pos = _attack(enc, known, index, s, n_types)
        acc = key_accuracy(pos["key"], truth, enc)
        ok = acc >= 0.6
        res.control(f"{name}: zaszyfrowany tekst z szumem pisowni", "klucz odzyskany w ≥ 60% znaków",
                    f"{acc:.0%} (słowa w słowniku {pos['exact']:.0%}, o jedną zmianę {pos['near']:.0%})", ok)
        if not ok:
            untestable.append(name)
        v = _attack(lines, known, index, s, n_types, log)
        g = _attack(gen, known, index, s, n_types)
        lead = ok and v["near"] >= g["near"] + 0.15 and v["near"] >= 0.3
        metrics[name] = {"voynich": v, "generator": g, "enciphered": pos, "key_accuracy": acc, "lead": lead}
        if lead:
            leads.append(name)
        sample = " ".join("".join(v["key"].get(gl, "?") for gl in w) for w in lines[0][:8])
        res.evidence.append(f"{name}: rękopis – słowa w słowniku {v['exact']:.1%}, o jedną zmianę {v['near']:.1%} "
                            f"(koszt transportu {v['cost']:.3f}); bełkot v5 – {g['exact']:.1%}, {g['near']:.1%}; "
                            f"zaszyfrowany tekst – klucz {acc:.0%}, słowa {pos['near']:.0%}. " + ("TROP. " if lead else "")
                            + f"Odczyt pierwszego wiersza: „{sample}”.")
        print(f"  {name}: rękopis {v['exact']:.1%}/{v['near']:.1%} | bełkot {g['exact']:.1%}/{g['near']:.1%} | "
              f"klucz {acc:.0%}" + (" TROP" if lead else ""), flush=True)
    res.controls = [c for c in res.controls if c.passed]
    tested = [n for n in metrics if n not in untestable]
    res.metrics = {"languages": metrics, "untestable": untestable, "n_glyphs": n_glyphs, "restarts": s.restarts,
                   "steps": s.steps}
    if leads:
        res.decide(True)
    elif len(tested) >= max(3, len(metrics) // 2):
        res.decide(False)
    else:
        res.decide(None)
    best = max(tested, key=lambda n: metrics[n]["voynich"]["near"] - metrics[n]["generator"]["near"]) if tested else None
    res.summary = (f"Tropy: {', '.join(leads) if leads else 'brak'}; {len(tested)} języków testowalnych, "
                   f"{len(untestable)} nietestowalnych. "
                   + (f"Największa przewaga nad bełkotem: {best} (rękopis {metrics[best]['voynich']['near']:.0%} słów "
                      f"o najwyżej jedną zmianę od słownika, bełkot {metrics[best]['generator']['near']:.0%})." if best else ""))
    res.caveats += ["Cechy bigramowe widzą pisownię, nie wymowę: kognaty różniące się bardziej niż o jedną literę "
                    "nie liczą się jako trafienia.",
                    "Klucz glif–litera jeden do jednego; abrewiacje i ligatury wieloliterowe są poza zasięgiem."]
    res.seconds = time.time() - t0
    return res
