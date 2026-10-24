"""Theory: words depend on their slot in the line (fields of a record), measured as a language model's gain.

A small character GPT is trained twice on each corpus: on the plain text and on the text with a
position token before every word (<p:0>, <p:1>, ...). The gain in bits per character on held-out
lines is what the slot tells the model about the word. Records with fields gain a lot; prose and
gibberish that ignore position gain nothing. The manuscript is set beside Latin, plainchant,
gibberish v5 (whose only positional habits are at the line edges) and two medieval lists, with a
random-position control (must gain nothing) and synthetic records (must gain much).
"""

from __future__ import annotations

import dataclasses
import random
import statistics
import time

from ... import corpus, lists, notation, records
from ..config import LabConfig
from ..results import TheoryResult
from .generative import PosVocab, line_bits, page_records, train_gpt
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs

CHARS = 200_000


def corpora(cfg: LabConfig, limit: int = CHARS) -> dict[str, list[str]]:
    """Named corpora as lines of words joined by '.', each cut to about `limit` characters."""
    out: dict[str, list[str]] = {}
    want = set(cfg.fields_corpora)
    if "rękopis" in want:
        out["rękopis"] = [l for p in page_records() for l in p["lines"]]
    if "łacina" in want:
        lat = corpus.load_reference("Latin")
        out["łacina"] = [".".join(lat[i:i + 9]) for i in range(0, len(lat) - 9, 9)]
    if "chorał" in want:
        try:
            out["chorał"] = [".".join("".join(u) for u in l) for l in notation.chant_lines("word", limit=None)]
        except FileNotFoundError:
            pass
    if "bełkot v5" in want:
        out["bełkot v5"] = [".".join("".join(w) for w in l) for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)
                            + generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed + 1)]
    for name in lists.available():
        if name in want and lists.passes(lists.quality(lists.load(name))):
            out[name] = [".".join(e) for e in lists.load(name)]
    for name, ls in out.items():
        cut, n = [], 0
        for l in ls:
            cut.append(l)
            n += len(l) + 1
            if n >= limit:
                break
        out[name] = cut
    return out


def split(lines: list[str], seed: int, chunk: int = 10) -> tuple[list[str], list[str], list[str]]:
    """Train, pick (checkpoint choice) and test lines; chunks of consecutive lines kept together."""
    rng = random.Random(seed)
    chunks = [lines[i:i + chunk] for i in range(0, len(lines), chunk)]
    idx = list(range(len(chunks)))
    rng.shuffle(idx)
    n_val = max(1, len(idx) // 10)
    pick = {i for i in idx[:n_val]}
    test = {i for i in idx[n_val:2 * n_val]}
    tr = [l for i, c in enumerate(chunks) if i not in pick and i not in test for l in c]
    return tr, [l for i in sorted(pick) for l in chunks[i]], [l for i in sorted(test) for l in chunks[i]]


def gain(lines: list[str], cfg: LabConfig, mode: str, seed: int, log=None) -> dict:
    """Bits per character without and with position tokens (`mode` 'pos' or 'random') on the test lines,
    with a paired bootstrap over lines for the spread of the gain."""
    vocab = PosVocab(lines)
    tr, pick, test = split(lines, seed)
    sub = dataclasses.replace(cfg, gpt_width=cfg.fields_width, gpt_layers=cfg.fields_layers, gpt_steps=cfg.fields_steps)
    out = {}
    per_line = {}
    for m in ("none", mode):
        enc = lambda ls, s=seed: vocab.encode(ls, m, s)   # noqa: E731
        model, info = train_gpt(enc(tr), enc(pick), vocab, sub, 256, vocab.keep, enc(test))
        import torch
        device = next(model.parameters()).device
        per_line[m] = line_bits(model, torch.tensor(enc(test), dtype=torch.long), 256, device, vocab.stoi["\n"], vocab.keep)
        out[m] = info["test_bits"]
        if log:
            log(f"    {m}: {info['test_bits']:.3f} bit/znak (krok {info['best_step']})")
        del model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
    a, b = per_line["none"], per_line[mode]
    n = min(len(a), len(b))
    pairs = [(a[i][0] - b[i][0], a[i][1]) for i in range(n) if a[i][1] > 0]
    rng = random.Random(seed)
    boots = []
    for _ in range(300):
        smp = [pairs[rng.randrange(len(pairs))] for _ in range(len(pairs))]
        boots.append(sum(d for d, _ in smp) / max(1, sum(c for _, c in smp)))
    delta = sum(d for d, _ in pairs) / max(1, sum(c for _, c in pairs))
    return {"bits_none": out["none"], f"bits_{mode}": out[mode], "delta": delta, "delta_sd": statistics.pstdev(boots) if len(boots) > 1 else 0.0,
            "lines_test": n, "chars": sum(len(l) + 1 for l in lines)}


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    res = TheoryResult(
        theory="fields_lm",
        hypothesis="Słowo rękopisu zależy od swojego miejsca w wierszu jak pole od rubryki rekordu: model języka, "
                   "który zna numer słowa w wierszu, przewiduje znaki wyraźnie lepiej.",
        method=(f"Mały GPT znakowy ({cfg.fields_layers} warstwy, {cfg.fields_width} wymiarów, {cfg.fields_steps} kroków) uczony "
                "dwa razy na każdym korpusie: tekst goły i tekst z tokenem pozycji przed każdym słowem (<p:0>, <p:1>, ... <p:12+>); "
                "bity na znak na odłożonych wierszach (znaki liczone, tokeny pozycji nie), różnica = zysk z pozycji, rozrzut "
                "z bootstrapu po wierszach. Korpusy: rękopis, łacina, chorał (słowa), bełkot v5, martyrologium, Apicius "
                "(po ok. 200 tys. znaków). Kontrole: tokeny pozycji losowe na rękopisie (zysk ≈ 0); rekordy syntetyczne o polach (duży zysk)."),
        references=["Radford et al., Language models are unsupervised multitask learners (2019)",
                    "Karpathy, nanoGPT"])
    try:
        import torch  # noqa: F401
    except ImportError:
        res.evidence.append("Brak PyTorch: uruchom w Colabie.")
        res.decide(None)
        res.summary = "Pominięte: wymaga PyTorch i GPU."
        res.seconds = time.time() - t0
        return res
    limit = 30_000 if cfg.quick else CHARS
    data = corpora(cfg, limit)
    log = lambda m: print(m, flush=True)  # noqa: E731
    # Controls.
    syn_l, _ = records.synthetic_records(1500 if cfg.quick else 4000, cfg.seed)
    syn = [".".join("".join(w) for w in l) for l in syn_l]
    print("  rekordy syntetyczne", flush=True)
    g_syn = gain(syn, cfg, "pos", cfg.seed, log)
    res.control("rekordy syntetyczne o polach: tokeny pozycji dają zysk", "Δ ≥ 0,15 bit/znak", f"Δ = {g_syn['delta']:.3f} ± {g_syn['delta_sd']:.3f}",
                g_syn["delta"] >= 0.15)
    print("  rękopis, pozycje losowe", flush=True)
    g_rand = gain(data["rękopis"], cfg, "random", cfg.seed, log)
    res.control("rękopis z losowymi tokenami pozycji: brak zysku", "Δ ≤ 0,01", f"Δ = {g_rand['delta']:.3f} ± {g_rand['delta_sd']:.3f}",
                g_rand["delta"] <= 0.01)
    metrics = {"controls": {"synthetic": g_syn, "random_positions": g_rand}, "corpora": {}}
    for name, lines in data.items():
        print(f"  {name} ({sum(len(l) + 1 for l in lines)} znaków, {len(lines)} wierszy)", flush=True)
        g = gain(lines, cfg, "pos", cfg.seed, log)
        metrics["corpora"][name] = g
        res.evidence.append(f"{name}: {g['bits_none']:.3f} bit/znak bez pozycji, {g['bits_pos']:.3f} z pozycją; zysk Δ = {g['delta']:+.3f} "
                            f"± {g['delta_sd']:.3f} ({g['lines_test']} wierszy testowych, {g['chars']} znaków).")
    res.metrics = metrics
    ms, v5 = metrics["corpora"].get("rękopis"), metrics["corpora"].get("bełkot v5")
    list_deltas = [metrics["corpora"][k]["delta"] for k in metrics["corpora"] if k in lists.available()]
    if ms and v5:
        if ms["delta"] - v5["delta"] >= 0.05 and (not list_deltas or ms["delta"] >= min(list_deltas)):
            res.decide(True)
        elif ms["delta"] <= v5["delta"] + 2 * ms["delta_sd"]:
            res.decide(False)
        else:
            res.decide(None)
    else:
        res.decide(None)
    order = sorted(metrics["corpora"], key=lambda k: metrics["corpora"][k]["delta"], reverse=True)
    res.summary = ("Zysk z tokenów pozycji (bit/znak): " + ", ".join(f"{k} {metrics['corpora'][k]['delta']:+.3f}" for k in order)
                   + (f". Rękopis wobec bełkotu v5: {ms['delta'] - v5['delta']:+.3f} (próg +0,05)" if ms and v5 else "")
                   + f"; kontrola losowa {g_rand['delta']:+.3f}, rekordy syntetyczne {g_syn['delta']:+.3f}.")
    res.caveats += ["Zysk obejmuje też krawędzie wiersza (znane nawyki p/m/g); bełkot v5 ma te nawyki wbudowane, stąd porównanie z nim.",
                    "Jeden przebieg na korpus (ziarno cfg.seed); rozrzut z bootstrapu po wierszach, nie z wielu treningów."]
    res.seconds = time.time() - t0
    return res
