"""Theory: the manuscript is a nomenclator, a codebook in which every word is one code.

The hounds' most frequent wish in the first hunt. Under a word-for-word code the
glyphs inside a word carry no language, so the letter-level attacks cannot see
it; what survives is the order of words. The attack therefore works one level
up: each of the K most frequent manuscript words is one cipher symbol (the rest
share one "rare" symbol), each of the K most frequent words of the target
language is one plaintext symbol, and the substitution solver searches the
codebook with a word trigram model of the language.

What decides is word order. The same solver also reads the text with its words
shuffled; a real codebook text reads clearly better in its own order than
shuffled (the planted controls show by how much), a text whose word order means
nothing in that language does not. Homophones (two codes per word) are covered
by the many-to-one solver and get their own control.
"""

from __future__ import annotations

import random
import time
from collections import Counter

from ... import cipher, corpus
from ..config import LabConfig
from ..recipes import target_words
from ..results import TheoryResult

RARE = "·"
LINE = 9  # words per unit of plaintext; manuscript paragraph lines average about this


def _units(words: list[str], top: set[str], size: int = LINE) -> list[list[str]]:
    t = [w if w in top else RARE for w in words]
    return [t[i:i + size] for i in range(0, len(t), size)]


def _shuffled(units: list[list[str]], r: random.Random) -> list[list[str]]:
    flat = [g for u in units for g in u]
    r.shuffle(flat)
    out, i = [], 0
    for u in units:
        out.append(flat[i:i + len(u)])
        i += len(u)
    return out


def order_gain(units, model, r, restarts: int, steps: int, seed: int) -> tuple[float, cipher.Solution]:
    """Bits per symbol the solver saves by reading the text in its own order rather than shuffled."""
    sol = cipher.solve(units, model, restarts=restarts, steps=steps, seed=seed)
    shuf = cipher.solve(_shuffled(units, r), model, restarts=restarts, steps=steps, seed=seed)
    return shuf.bits - sol.bits, sol


def plant(words: list[str], top: set[str], homophones: int, r: random.Random) -> list[list[str]]:
    """Target-language text written with a random codebook (each word gets `homophones` codes)."""
    vocab = sorted(top) + [RARE]
    codes = [f"k{i}" for i in range(len(vocab) * homophones)]
    r.shuffle(codes)
    book = {w: codes[i * homophones:(i + 1) * homophones] for i, w in enumerate(vocab)}
    return [[r.choice(book[w]) for w in u] for u in _units(words, top)]


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    r = random.Random(cfg.seed)
    restarts, steps = (3, 30000) if cfg.quick else (4, 100000)
    n_words = 2500 if cfg.quick else 4000
    targets = ["Latin", "Italian"] if cfg.quick else ["Latin", "MedievalLatin", "Italian", "German"]
    sizes = [30] if cfg.quick else [30, 60]
    res = TheoryResult(
        theory="nomenclator",
        hypothesis="Rękopis to nomenklator: każde słowo jest kodem jednego słowa języka (jak w księgach kodowych "
                   "kancelarii XV w.), także z kilkoma kodami na częste słowa.",
        method=("Łamacz na poziomie słów: K najczęstszych słów rękopisu to symbole szyfru, K najczęstszych słów języka "
                "to symbole tekstu jawnego, model trigramowy słów języka. Rozstrzyga szyk: o ile lepiej łamacz czyta "
                "tekst w jego kolejności niż po przetasowaniu słów. Kontrole: prawdziwy tekst języka zakodowany "
                "losową księgą (1 i 2 kody na słowo) musi zyskać wyraźnie na szyku; dwa tasowania rękopisu dają szum; "
                "bełkot z generatora v4 jako tło."),
        references=["Pelling, The Curse of the Voynich (2006) – nomenklatory w XV-wiecznej kryptografii",
                    "Kahn, The Codebreakers (1967), rozdz. o nomenklatorach włoskich kancelarii"])

    from ..hounds import build_shared
    para = [l for l in corpus.load_voynich() if l.kind.startswith("P")]
    voy_words = [w for l in para for w in l.words]
    null_lines = [l for _, l in build_shared(cfg, n_null_words=n_words * 2).null_lines]
    metrics, rows = {}, []
    any_lead, all_flat, controls_ok = False, True, True
    for k in sizes:
        vtop = {w for w, _ in Counter(voy_words).most_common(k)}
        lines, count = [], 0
        for l in para:
            lines.append([w if w in vtop else RARE for w in l.words])
            count += len(l.words)
            if count >= n_words:
                break
        gen = ["".join(w) for l in null_lines for w in l]
        gtop = {w for w, _ in Counter(gen).most_common(k)}
        gen_units = _units(gen[:n_words], gtop)
        for target in targets:
            tw = target_words({"target": target})
            top = {w for w, _ in Counter(tw[20000:]).most_common(k)}
            model = cipher.TrigramModel(_units(tw[20000:], top))
            seed = cfg.seed + k
            g1, _ = order_gain(plant(tw[:n_words], top, 1, r), model, r, restarts, steps, seed)
            g2, _ = order_gain(plant(tw[:n_words], top, 2, r), model, r, restarts, steps, seed)
            gv, sol = order_gain(lines, model, r, restarts, steps, seed)
            noise = [order_gain(_shuffled(lines, r), model, r, restarts, steps, seed)[0] for _ in range(2)]
            gg, _ = order_gain(gen_units, model, r, restarts, steps, seed)
            floor = max(abs(x) for x in noise) + 0.02
            ok = g1 >= max(0.05, 3 * floor)
            controls_ok &= ok
            lead = ok and gv >= 0.5 * g1 and gv > floor and gv > gg + floor
            flat = ok and gv < max(0.3 * g1, floor)
            any_lead |= lead
            all_flat &= flat
            name = f"{target}, K={k}"
            metrics[name] = {"plant_gain_h1": g1, "plant_gain_h2": g2, "voynich_gain": gv, "noise": noise,
                             "generator_gain": gg, "voynich_bits": sol.bits,
                             "sample": " ".join(sol.key.get(g, "?") for u in lines[:3] for g in u)}
            res.control(f"{name}: tekst jawny zakodowany księgą (1 kod na słowo)",
                        f"zysk z szyku ≥ {max(0.05, 3 * floor):.2f} bita", f"{g1:+.3f} bita (2 kody na słowo: {g2:+.3f})", ok)
            rows.append(f"{name}: rękopis zyskuje na szyku {gv:+.3f} bita (szum ±{floor - 0.02:.3f}, generator {gg:+.3f}); "
                        f"prawdziwy tekst zakodowany księgą {g1:+.3f} (2 kody na słowo {g2:+.3f}).")
            print("  " + rows[-1], flush=True)
    res.evidence += rows
    res.evidence.append("Przykładowy odczyt (Latin, najmniejsze K): " + metrics[f"{targets[0]}, K={sizes[0]}"]["sample"])
    res.metrics = metrics
    res.decide(True if any_lead else False if all_flat and controls_ok else None)
    res.summary = ("Nomenklator słowo-za-słowo: " + ("w co najmniej jednym języku szyk słów rękopisu niesie informację "
                   "jak zakodowany tekst – trop do powtórki." if any_lead else
                   "szyk słów rękopisu nie pomaga łamaczowi w żadnym z badanych języków, choć zakodowany prawdziwy "
                   "tekst zyskuje na szyku wyraźnie." if all_flat else "wynik niejednoznaczny – szczegóły w dowodach."))
    res.caveats += [
        "Bada tylko księgę kodów dla najczęstszych K słów; rzadkie słowa zlewają się w jeden symbol.",
        "Nie bada nomenklatora mieszanego (częste słowa kodami, rzadkie literami); to osobny klocek.",
        "Języki docelowe to Biblia i łacina średniowieczna; inny gatunek tekstu (receptury, zielnik) ma inny szyk.",
    ]
    res.seconds = time.time() - t0
    return res
