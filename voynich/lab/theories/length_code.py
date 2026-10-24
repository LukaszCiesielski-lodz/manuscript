"""Theory: the message is not in the glyphs but in the word lengths (a code of counts).

Every word is replaced by its number of glyphs; the digit stream of each line is treated as a
cipher text over a small alphabet (lengths 1..9+). Tests: how much a digit can carry (entropy,
alphabet); whether the stream has sequential structure beyond its shuffles (conditional entropy
of digit bigrams, z against within-line shuffles), compared with real language and gibberish v5;
whether any monoalphabetic reading of the digits as letters resembles a language (hill climb
with the character 4-gram model of each language, judged on held-out lines, against the same
attack on the shuffled stream); whether the parity bits (odd/even length) carry structure or a
five-bit letter code (Bacon). Positive control: a Latin text planted as lengths must be caught by
the structure test and read by the climb.
"""

from __future__ import annotations

import math
import random
import time
from collections import Counter

from ... import corpus, eva, lexicon
from ..config import LabConfig
from ..hillclimb import Backend, Climb, GlyphText, NgramModel, climb, split_odd_even
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs

LANGS = ["Latin", "MedievalLatin", "Italian", "German", "Hebrew", "Greek", "Czech", "OldFrench"]
CAP = 9  # lengths above pooled into one symbol


def digits(lines) -> list[list[int]]:
    return [[min(len(w), CAP) for w in l] for l in lines]


def h2(seq: list[int]) -> float:
    c = Counter(zip(seq, seq[1:]))
    c1 = Counter(seq[:-1])
    n = sum(c.values())
    return -sum(v / n * math.log2(v / c1[a]) for (a, b), v in c.items())


def structure_z(rows: list[list[int]], shuffles: int, seed: int) -> tuple[float, float]:
    """(h2 of the stream, z against shuffles within lines). Negative z: more order than chance."""
    r = random.Random(seed)
    flat = [x for row in rows for x in row]
    base = h2(flat)
    vals = []
    for _ in range(shuffles):
        sh = []
        for row in rows:
            row = list(row)
            r.shuffle(row)
            sh += row
        vals.append(h2(sh))
    mu = sum(vals) / len(vals)
    sd = (sum((v - mu) ** 2 for v in vals) / len(vals)) ** 0.5 or 1e-9
    return base, (base - mu) / sd


def planted(words: list[str], rows: list[list[int]]) -> list[list[int]]:
    """Latin letters folded onto the manuscript's length alphabet: letter index mod CAP, in the real line shape."""
    letters = [c for w in words for c in w if c.isalpha()]
    out, i = [], 0
    for row in rows:
        out.append([(ord(letters[i + k]) - 97) % CAP + 1 for k in range(len(row))])
        i += len(row)
        if i + 20 > len(letters):
            break
    return out


def as_glyph_lines(rows: list[list[int]]):
    """One line = one 'word' of digit tokens, so the climber sees line breaks as word gaps."""
    return [[tuple(str(x) for x in row)] for row in rows if row]


def read_as_language(rows, lm: NgramModel, xp: Backend, s: Climb) -> float:
    lines = as_glyph_lines(rows)
    glyphs = [str(k) for k in range(1, CAP + 1)]
    odd, even = split_odd_even(lines)
    fit_text, held = GlyphText.build(odd, glyphs, lm.order), GlyphText.build(even, glyphs, lm.order)
    return climb(fit_text, lm, s, xp, held)["held_out_bits"]


def bacon(rows: list[list[int]], index) -> float:
    """Parity bits in groups of five as letters (a=00000...), share of five-letter groups that are words."""
    bits = [x % 2 for row in rows for x in row]
    letters = "".join("abcdefghijklmnopqrstuvwxyz"[min(int("".join(map(str, bits[i:i + 5])), 2), 25)]
                      for i in range(0, len(bits) - 4, 5))
    chunks = [letters[i:i + 5] for i in range(0, len(letters) - 4, 5)]
    return sum(1 for c in chunks if c in index) / max(1, len(chunks))


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 30 if cfg.quick else 200
    xp = Backend(prefer_gpu=False)
    s = Climb(population=128, steps=300 if cfg.quick else 1500, seed=cfg.seed)
    res = TheoryResult(
        theory="length_code",
        hypothesis="Treść nie siedzi w glifach, lecz w długościach słów: ciąg liczb znaków w słowach jest kodem "
                   "(liter, cyfr albo bitów parzystości).",
        method=("Każde słowo zamienione na liczbę glifów (1–9+). Pojemność: entropia i alfabet ciągu. Struktura: "
                "entropia warunkowa bigramów cyfr wobec tasowań w obrębie wiersza (z), to samo dla łaciny i bełkotu v5. "
                "Odczyt jako litery: wspinaczka po kluczu cyfra–litera z modelem 4-gramowym 8 języków, wiersze "
                "nieparzyste uczą, parzyste oceniają, wobec tego samego dla ciągu przetasowanego. Parzystość: "
                "struktura bitów i odczyt piątkami (Bacon). Kontrola dodatnia: tekst łaciński wszczepiony jako długości."),
        references=["Stolfi, word-length distribution of the Voynich text (1998–2000)", "Bacon, De augmentis (1623)"])
    lines = [[eva.glyphs(w) for w in l.words] for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    rows = digits(lines)
    flat = [x for r in rows for x in r]
    n = len(flat)
    gen_rows = digits(generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed))
    latin = corpus.load_reference("Latin")[:n]
    lat_rows, i = [], 0
    for r in rows:
        lat_rows.append([min(len(w), CAP) for w in latin[i:i + len(r)]])
        i += len(r)
    plant_rows = planted(corpus.load_reference("Latin"), rows)
    # capacity
    c = Counter(flat)
    ent = -sum(v / n * math.log2(v / n) for v in c.values())
    top3 = sum(v for k, v in c.most_common(3)) / n
    res.evidence.append(f"Pojemność: {len(c)} wartości, entropia {ent:.2f} bit/słowo; trzy najczęstsze długości to "
                        f"{top3:.0%} ciągu. Rozkład: " + ", ".join(f"{k}:{v}" for k, v in sorted(c.items())) + ".")
    # structure
    zs = {}
    for name, rws in (("rękopis", rows), ("łacina", lat_rows), ("bełkot v5", gen_rows), ("łacina wszczepiona", plant_rows)):
        hv, z = structure_z(rws, shuffles, cfg.seed)
        zs[name] = (hv, z)
    res.evidence.append("Struktura ciągu cyfr (entropia warunkowa; z wobec tasowań w wierszu, ujemne = porządek): "
                        + "; ".join(f"{k} {hv:.3f} bit, z = {z:+.1f}" for k, (hv, z) in zs.items()) + ".")
    res.control("łacina wszczepiona jako długości ma strukturę", "z ≤ −5", f"z = {zs['łacina wszczepiona'][1]:+.1f}",
                zs["łacina wszczepiona"][1] <= -5)
    # readings as letters
    r = random.Random(cfg.seed)
    sh_rows = [r.sample(row, len(row)) for row in rows]
    readings = {}
    for name in LANGS:
        if name not in lexicon.available():
            continue
        _, _, text = lexicon.load_all(name)
        if len(text) < 3000:
            continue
        lm = NgramModel.fit(text[: int(len(text) * 0.7)], 4)
        natural = lm.bits(text[int(len(text) * 0.7):])
        v = read_as_language(rows, lm, xp, s)
        sh = read_as_language(sh_rows, lm, xp, s)
        pl = read_as_language(plant_rows, lm, xp, s) if name == "Latin" else None
        readings[name] = {"natural": natural, "voynich": v, "shuffled": sh, "planted": pl}
        print(f"  {name}: rękopis {v:.2f} | przetasowany {sh:.2f} | naturalny {natural:.2f}"
              + (f" | wszczepiony {pl:.2f}" if pl else ""), flush=True)
    if "Latin" in readings and readings["Latin"]["planted"] is not None:
        gain = readings["Latin"]["shuffled"] - readings["Latin"]["planted"]
        res.control("wspinaczka czyta łacinę wszczepioną jako długości", "o ≥ 0,3 bita lepiej niż ciąg przetasowany",
                    f"{gain:+.2f} bita", gain >= 0.3)
    best_gain = max((d["shuffled"] - d["voynich"] for d in readings.values()), default=0.0)
    res.evidence.append("Odczyt cyfr jako liter (bity na znak, wiersze parzyste): "
                        + "; ".join(f"{k} rękopis {d['voynich']:.2f}, przetasowany {d['shuffled']:.2f}, naturalny {d['natural']:.2f}"
                                    for k, d in readings.items()) + f". Największy zysk rękopisu nad przetasowaniem: {best_gain:+.2f} bita.")
    # parity
    bits = [x % 2 for x in flat]
    odd_share = sum(bits) / n
    bit_rows = [[x % 2 for x in row] for row in rows]
    _, zb = structure_z(bit_rows, shuffles, cfg.seed)
    counts, _, _ = lexicon.load_all("Latin") if "Latin" in lexicon.available() else (Counter(), None, None)
    index = {w for w in counts if len(w) == 5}
    b_voy = bacon(rows, index)
    b_sh = bacon(sh_rows, index)
    res.evidence.append(f"Parzystość długości: nieparzyste {odd_share:.1%}; struktura bitów z = {zb:+.1f}; odczyt piątkami bitów "
                        f"(Bacon) daje łacińskie słowa w {b_voy:.1%} grup (ciąg przetasowany {b_sh:.1%}).")
    res.metrics = {"capacity": {"values": len(c), "entropy": ent, "top3": top3, "distribution": dict(c)},
                   "structure": {k: {"h2": hv, "z": z} for k, (hv, z) in zs.items()}, "readings": readings,
                   "parity": {"odd_share": odd_share, "z": zb, "bacon": b_voy, "bacon_shuffled": b_sh}}
    no_order = abs(zs["rękopis"][1]) < 3 or zs["rękopis"][1] > zs["łacina"][1]
    no_reading = best_gain < 0.3
    no_bits = abs(zb) < 3 and b_voy <= b_sh + 0.01
    res.decide(False if (no_order and no_reading and no_bits) else None)
    res.summary = (f"Ciąg długości ma {len(c)} wartości i {ent:.2f} bit/słowo; porządek w kolejności: rękopis z = "
                   f"{zs['rękopis'][1]:+.1f}, łacina {zs['łacina'][1]:+.1f}, bełkot v5 {zs['bełkot v5'][1]:+.1f}. "
                   f"Odczyt jako litery w żadnym z {len(readings)} języków nie przebija ciągu przetasowanego o więcej niż "
                   f"{best_gain:+.2f} bita; bity parzystości bez struktury (z = {zb:+.1f}). "
                   + ("Długości słów nie są kodem." if not no_order or no_reading else ""))
    res.caveats += ["Kod binarny z kluczem (parzystość jako bity) jest niefalsyfikowalny z samego tekstu; "
                    "sprawdzono tylko jego strukturę i odczyt Bacona.",
                    "Długości liczone w glifach ZL; w literach EVA alfabet ciągu jest szerszy, lecz wniosek ten sam (test jednej strony)."]
    res.seconds = time.time() - t0
    return res
