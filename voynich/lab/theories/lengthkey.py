"""Theory: a different cipher alphabet for every word length (the spaces select the key).

The user's idea, found nowhere in the literature: the scribe used one substitution for words of
length 1, another for length 2, and so on. A homophonic hill climb over the symbols "glyph#length
class" (voynich.lab.hillclimb.by_length) is a climb over nine keys at once. More keys always fit
anything a little better, so the gain from one key to nine is compared with the same gain on
gibberish v5 and on text whose glyphs are relabelled on every line; Latin enciphered with nine
keys is the positive control.
"""

from __future__ import annotations

import time

from ... import lexicon
from ..brute import paragraph_lines, relabel_lines
from ..config import LabConfig
from ..hillclimb import (Backend, Climb, GlyphText, NgramModel, by_length, climb, encipher_by_length, glyph_inventory,
                         key_accuracy, split_odd_even)
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs

LANGUAGES = ["Latin", "Italian", "German", "French", "Spanish", "Czech"]


def _attack(lines, lm: NgramModel, s: Climb, xp: Backend, order: int) -> dict:
    glyphs = glyph_inventory(lines)
    odd, even = split_odd_even(lines)
    return climb(GlyphText.build(odd, glyphs, order), lm, s, xp, GlyphText.build(even, glyphs, order))


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    xp = Backend(prefer_gpu=True)
    names = [n for n in (cfg.attack_languages or LANGUAGES) if n in lexicon.available()]
    if cfg.quick:
        names = names[:2]
    s = Climb(population=256 if cfg.quick else cfg.climb_population, steps=300 if cfg.quick else cfg.climb_steps, seed=cfg.seed)
    order = cfg.climb_order
    res = TheoryResult(
        theory="lengthkey",
        hypothesis="Klucz szyfru zależy od długości słowa: słowa jedno-, dwu-, ..., dziewięcio- i więcej glifowe mają własne "
                   "alfabety podstawieniowe (odstępy wybierają klucz).",
        method=(f"Glif g w słowie o klasie długości c staje się symbolem g#c (klasy 1–8 i 9+); wspinaczka homofoniczna "
                f"({s.population} wspinaczy, {s.steps} kroków, model {order}-gramowy na {xp.name}) nad takimi symbolami to dziewięć "
                "kluczy naraz. Dla każdego języka: bity na znak na wierszach parzystych z jednym kluczem i z kluczami po długości, "
                "dla rękopisu, bełkotu v5 i glifów przemianowanych w każdym wierszu (tło: więcej kluczy zawsze trochę pomaga). "
                "Kontrola dodatnia: tekst języka zaszyfrowany dziewięcioma kluczami, klucze odzyskane w ≥ 60% symboli. Trop: zysk "
                "rękopisu z kluczy po długości ≥ zysk v5 + 0,2 bitu i ≥ zysk przemianowanych + 0,2, przy wyniku ≤ naturalny + 0,8."),
        references=["Van Eycke, AZdecrypt (2017–2021)", "Stolfi, On the VMS word length distribution (2000)"])
    try:
        import torch  # noqa: F401
    except ImportError:
        res.evidence.append("Brak PyTorch: uruchom w Colabie.")
        res.decide(None)
        res.summary = "Pominięte: wymaga PyTorch i GPU."
        res.seconds = time.time() - t0
        return res
    lines = paragraph_lines("glyphs")
    n_glyphs = len(glyph_inventory(lines))
    gen = [[tuple(w) for w in l] for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)
           + generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed + 1)]
    relabelled = relabel_lines(lines, cfg.seed)
    texts = {"rękopis": lines, "bełkot v5": gen, "przemianowane": relabelled}
    metrics, leads, refuted = {}, [], 0
    for name in names:
        try:
            _, _, text = lexicon.load_all(name)
        except Exception as e:
            res.evidence.append(f"{name}: pominięty ({e})")
            continue
        if len(text) < 3000:
            continue
        cut = int(len(text) * 0.7)
        lm = NgramModel.fit(text[:cut], order)
        natural = lm.bits(text[cut:])
        enc, truth = encipher_by_length(text[cut:], n_glyphs, cfg.seed)
        covered = sum(len(w) for l in enc for w in l) / max(1, sum(len(w) for w in text[cut:]))
        if covered < 0.5:
            res.evidence.append(f"{name}: nietestowalny – {n_glyphs} glifów niesie tylko {covered:.0%} tekstu tego pisma.")
            continue
        pos = _attack(enc, lm, s, xp, order)
        acc = key_accuracy(pos["key"], truth, enc)
        ok = acc >= 0.6
        res.control(f"{name}: tekst zaszyfrowany dziewięcioma kluczami po długości", "klucze odzyskane w ≥ 60% symboli",
                    f"{acc:.0%} (wynik {pos['held_out_bits']:.2f} bit/znak wobec naturalnego {natural:.2f})", ok)
        row = {"natural_bits": natural, "key_accuracy": acc}
        for tname, tl in texts.items():
            one = _attack(tl, lm, s, xp, order)
            nine = _attack(by_length(tl), lm, s, xp, order)
            row[tname] = {"one_key": one["held_out_bits"], "length_keys": nine["held_out_bits"],
                          "gain": one["held_out_bits"] - nine["held_out_bits"]}
            print(f"  {name} / {tname}: jeden klucz {one['held_out_bits']:.2f}, klucze po długości {nine['held_out_bits']:.2f}", flush=True)
            if tname == "rękopis":
                row["sample"] = " ".join("".join(nine["key"].get(g, "?") for g in w) for w in by_length(tl)[0][:8])
        g_ms, g_v5, g_rl = row["rękopis"]["gain"], row["bełkot v5"]["gain"], row["przemianowane"]["gain"]
        lead = ok and g_ms >= g_v5 + 0.2 and g_ms >= g_rl + 0.2 and row["rękopis"]["length_keys"] <= natural + 0.8
        if lead:
            leads.append(name)
        if ok and g_ms <= g_v5 + 0.05:
            refuted += 1
        row["lead"] = lead
        metrics[name] = row
        res.evidence.append(f"{name}: rękopis {row['rękopis']['one_key']:.2f} → {row['rękopis']['length_keys']:.2f} bit/znak "
                            f"(zysk {g_ms:+.2f}); bełkot v5 {row['bełkot v5']['one_key']:.2f} → {row['bełkot v5']['length_keys']:.2f} "
                            f"(zysk {g_v5:+.2f}); przemianowane {row['przemianowane']['one_key']:.2f} → {row['przemianowane']['length_keys']:.2f} "
                            f"(zysk {g_rl:+.2f}); naturalny {natural:.2f}; szyfr testowy odzyskany w {acc:.0%}. "
                            + ("TROP. " if lead else "") + f"Odczyt pierwszego wiersza: „{row['sample']}”.")
    res.controls = [c for c in res.controls if c.passed]
    res.metrics = {"languages": metrics, "n_glyphs": n_glyphs, "device": xp.name, "population": s.population, "steps": s.steps}
    if leads:
        res.decide(True)
    elif refuted >= min(4, max(1, len(metrics))):
        res.decide(False)
    else:
        res.decide(None)
    best = max(metrics, key=lambda n: metrics[n]["rękopis"]["gain"] - metrics[n]["bełkot v5"]["gain"]) if metrics else None
    res.summary = (f"Tropy: {', '.join(leads) if leads else 'brak'}; {len(metrics)} języków. "
                   + (f"Największa przewaga zysku rękopisu nad bełkotem: {best} ({metrics[best]['rękopis']['gain']:+.2f} wobec "
                      f"{metrics[best]['bełkot v5']['gain']:+.2f} bitu); rękopis z kluczami po długości {metrics[best]['rękopis']['length_keys']:.2f} "
                      f"bit/znak wobec naturalnego {metrics[best]['natural_bits']:.2f}." if best else ""))
    res.caveats += ["Dziewięć kluczy to dziewięć razy więcej swobody: każdy tekst zyskuje; liczy się tylko nadwyżka zysku nad bełkotem "
                    "i nad glifami przemianowanymi.",
                    "Klasy długości liczone w glifach EVA (ch, sh, cth jako jeden); długości 9+ razem, bo powyżej to 0,2% słów."]
    res.seconds = time.time() - t0
    return res
