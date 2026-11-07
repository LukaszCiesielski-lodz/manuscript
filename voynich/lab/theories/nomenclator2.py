"""Theory: the manuscript is a two-key nomenclator with miscopying, in Hebrew, Arabic or Latin.

Zhang & Sheng (arXiv:2610.34499) leave this one cipher family open: frequent words written as
whole code words, the rest spelled letter by letter, homophones for frequent units, one key per
Currier dialect, and a scribe who miscopies code words. It stays open in Arabic and is undecided
in Hebrew, where their solver reads only 46% of its own Hebrew controls. Here the solver
(voynich.lab.nomen2: rare types merged into a frequent type one glyph away, then many annealed
Gibbs chains under the generative likelihood of a unit bigram model) must first read Hebrew,
Arabic and Latin controls of the manuscript's size, enciphered with the manuscript's own code
words at the manuscript's hapax rate. Then the key is fitted on odd lines of the manuscript, of
the v7 gibberish and of the manuscript with words shuffled in the line, and judged by the bits per
unit of the even lines it never saw. A nomenclator reads better than gibberish; gibberish does not.
"""

from __future__ import annotations

import json
import random
import time
from collections import Counter

from ... import corpus, eva
from .. import nomen2 as N
from ..config import LabConfig
from ..results import TheoryResult
from .hoax import V7_FAV_N, V7_SECTION_PARAMS, generate_by_section, section_models

RATES = (0.0, 0.05, 0.1, 0.2, 0.3, 0.5)
LINE_WORDS = 2         # plaintext words per line: about 9 units, the length of a manuscript line in code words


# ---------- shared material (also used by hapax_source)

def all_runs() -> list[tuple[tuple, list]]:
    """Paragraph lines of the whole manuscript as runs of one (section, Currier language), in order."""
    runs: list[tuple[tuple, list]] = []
    for l in corpus.load_voynich():
        if l.kind.startswith("P") and l.words:
            key = (l.section, l.language)
            if not runs or runs[-1][0] != key:
                runs.append((key, []))
            runs[-1][1].append([tuple(eva.glyphs(w)) for w in l.words])
    return runs


def dialect(key: tuple) -> str:
    return "B" if key[1] == "B" else "A"


def manuscript(runs) -> tuple[list[list[tuple]], list[str]]:
    lines = [l for _, ls in runs for l in ls]
    return lines, [dialect(k) for k, ls in runs for _ in ls]


def v7(runs, seed: int) -> tuple[list[list[tuple]], list[str], list[int]]:
    """v7 gibberish run by run (habits of each section and dialect), with the dialect and run of every line."""
    models = section_models(runs)
    lines, dialects, run_of = [], [], []
    for i, (k, ls) in enumerate(runs):
        gen = generate_by_section([(k, ls)], V7_SECTION_PARAMS, seed + i, fav_n=V7_FAV_N, models=models)
        lines += [[tuple(w) for w in l] for l in gen]
        dialects += [dialect(k)] * len(gen)
        run_of += [i] * len(gen)
    return lines, dialects, run_of


def shuffled_in_line(lines, seed: int):
    r = random.Random(seed)
    out = []
    for l in lines:
        l = list(l)
        r.shuffle(l)
        out.append(l)
    return out


def language(lang: str, units: int) -> tuple[N.UnitBigram, list[str]]:
    """Unit bigram model on the first 67% of the reference text; the rest as plaintext for the controls."""
    words = corpus.load_reference(lang)
    cut = int(len(words) * 0.67)
    top = N.top_words(words[:cut], units)
    return N.UnitBigram(N.plaintext_lines(words[:cut], top, LINE_WORDS)), N.plaintext_lines(words[cut:], top, LINE_WORDS)


def trim(unit_lines, tokens: int) -> list[str]:
    out, n = [], 0
    for l in unit_lines:
        if n >= tokens:
            break
        out.append(l)
        n += len(l)
    return out


def hapax_token_share(lines) -> float:
    c = Counter(w for l in lines for w in l)
    return sum(v for v in c.values() if v == 1) / max(1, sum(c.values()))


def match_rate(held: list[str], pool, target: float, seed: int) -> tuple[float, dict]:
    """Miscopying rate whose cipher has the manuscript's share of hapax tokens (linear between grid points)."""
    table = {r: hapax_token_share(N.encipher(held, pool, seed, miscopy=r)[0]) for r in RATES}
    pts = sorted(table.items())
    for (r0, h0), (r1, h1) in zip(pts, pts[1:]):
        if h0 <= target <= h1:
            return (r0 + (r1 - r0) * (target - h0) / max(1e-12, h1 - h0)), table
    return (pts[-1][0] if target > pts[-1][1] else 0.0), table


# ---------- the theory

def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    xp = N.array_module()
    gpu = xp.__name__ == "cupy"
    chains = (4 if cfg.quick else cfg.nomen2_chains) if gpu else min(4 if cfg.quick else 16, cfg.nomen2_chains)
    sweeps = 30 if cfg.quick else (cfg.nomen2_sweeps if gpu else min(200, cfg.nomen2_sweeps))
    langs = cfg.nomen2_languages[:1] if cfg.quick else list(cfg.nomen2_languages)
    if "Hebrew" not in langs:
        langs = ["Hebrew"] + langs
    res = TheoryResult(
        theory="nomenclator2",
        hypothesis="Rękopis to nomenklator z dwoma kluczami (język A i B Curriera) i pomyłkami kopisty: częste słowa jako całe "
                   "słowa kodowe, reszta literami, po hebrajsku, arabsku albo łacinie (jedyna rodzina szyfrów, której Zhang i Sheng nie wykluczyli).",
        method=(f"Łamacz: rzadkie typy scalane z częstym typem o jeden glif dalej (odwrócenie pomyłek), symbol = dialekt|typ; "
                f"klucz symbol → jednostka szukany próbkowaniem Gibbsa z wyżarzaniem, {chains} łańcuchów naraz ({xp.__name__}), "
                f"{sweeps} przebiegów, pełna wiarygodność: bigramy jednostek + koszt emisji homofonów. Języki: {', '.join(langs)}; "
                f"model na 67% Biblii ({cfg.nomen2_units} słów jako jednostki, reszta literami). Kontrole: pozostałe 33% zaszyfrowane "
                f"{cfg.nomen2_pool} najczęstszymi słowami rękopisu, dwa klucze, tyle tokenów co rękopis, stopa pomyłek 0, r* (ta, przy której "
                "udział hapaksów równa się rękopisowi) i 0,5. Klucz na wierszach nieparzystych, ocena: bity na jednostkę wierszy parzystych. "
                "Rękopis wobec bełkotu v7 (te same działy i dialekty) i rękopisu ze słowami przetasowanymi w wierszu."),
        references=["Zhang & Sheng, arXiv:2610.34499 (2026)", "Berg-Kirkpatrick & Klein, Decipherment with a million random restarts (EMNLP 2013)",
                    "Ravi & Knight, Bayesian inference for Zodiac and other homophonic ciphers (ACL 2011)"])
    runs = all_runs()
    ms_lines, ms_d = manuscript(runs)
    if cfg.quick:
        ms_lines, ms_d = ms_lines[:1200], ms_d[:1200]
    g_lines, g_d, _ = v7(runs, cfg.seed)
    g_lines, g_d = g_lines[:len(ms_lines)], g_d[:len(ms_lines)]
    sh_lines = shuffled_in_line(ms_lines, cfg.seed)
    tokens = sum(map(len, ms_lines))
    target = hapax_token_share(ms_lines)
    pool = [w for w, _ in Counter(w for l in ms_lines for w in l).most_common(cfg.nomen2_pool)]
    res.metrics.update({"tokens": tokens, "hapax_token_share": target, "chains": chains, "sweeps": sweeps, "backend": xp.__name__})
    log = (lambda m: print(m, flush=True)) if not cfg.quick else None
    per_lang, readings = {}, {}
    for lang in langs:
        lm, held = language(lang, cfg.nomen2_units)
        held = trim(held, tokens)
        natural = lm.bits(held)
        r_star, table = match_rate(held, pool, target, cfg.seed)
        rates = [0.0, round(r_star, 3)] + ([] if cfg.quick else [0.5])
        row = {"natural_bits": natural, "r_star": r_star, "hapax_by_rate": table, "controls": {}}
        for r in rates:
            lines, truth, dd = N.encipher(held, pool, cfg.seed, miscopy=r)
            a = N.attack(lines, dd, lm, sweeps, chains, cfg.seed, truth=truth, log=log)
            row["controls"][str(r)] = {k: a[k] for k in ("accuracy", "held_out_bits", "fit_bits", "symbols", "coverage", "chain_agreement")}
            row["controls"][str(r)]["sample"] = a["sample"][0][:60]
            print(f"  {lang} kontrola r = {r}: trafność {a['accuracy']:.3f}, bity {a['held_out_bits']:.3f}", flush=True)
        for name, lines, dd in (("manuscript", ms_lines, ms_d), ("v7", g_lines, g_d), ("shuffled", sh_lines, ms_d)):
            a = N.attack(lines, dd, lm, sweeps, chains, cfg.seed, log=log)
            row[name] = {k: a[k] for k in ("held_out_bits", "fit_bits", "symbols", "coverage", "chain_agreement")}
            row[name]["sample"] = [s[:60] for s in a["sample"]]
            if name == "manuscript":
                c = Counter(s for l in N.symbol_lines(lines, dd) for s in l)
                readings[lang] = [(s, a["key"][s], c[s]) for s, _ in c.most_common(40) if s in a["key"]]
            print(f"  {lang} {name}: bity {a['held_out_bits']:.3f}", flush=True)
        per_lang[lang] = row
    res.metrics["languages"] = per_lang
    out_dir = cfg.results_dir / "nomenclator2"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "readings.json").write_text(json.dumps({"languages": per_lang, "manuscript_key_top40": readings},
                                                      ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    res.artifacts.append("nomenclator2/readings.json")

    heb = per_lang["Hebrew"]["controls"]["0.0"]["accuracy"]
    res.control("łamacz czyta hebrajską kontrolę bez pomyłek (Zhang i Sheng: 46%)", "trafność ≥ 0,5", f"{heb:.3f}", heb >= 0.5)
    best_star = max(per_lang[l]["controls"][str(round(per_lang[l]["r_star"], 3))]["accuracy"] for l in langs)
    res.control("łamacz czyta kontrolę przy stopie pomyłek rękopisu r* (choć jeden język)", "trafność ≥ 0,5", f"{best_star:.3f}", best_star >= 0.5)
    ok = [l for l in langs if per_lang[l]["controls"]["0.0"]["accuracy"] >= 0.5]
    for l in langs:
        p = per_lang[l]
        st = p["controls"][str(round(p["r_star"], 3))]
        res.evidence.append(
            f"{l}: naturalnie {p['natural_bits']:.2f} bitu/jedn.; kontrola r=0 trafność {p['controls']['0.0']['accuracy']:.2f}, "
            f"r*={p['r_star']:.2f} trafność {st['accuracy']:.2f} ({st['held_out_bits']:.2f} bitu); rękopis {p['manuscript']['held_out_bits']:.2f}, "
            f"v7 {p['v7']['held_out_bits']:.2f}, przetasowany {p['shuffled']['held_out_bits']:.2f} bitu; odczyt rękopisu: „{p['manuscript']['sample'][0][:40]}”.")
    hits = [l for l in ok if per_lang[l]["manuscript"]["held_out_bits"] <= per_lang[l]["v7"]["held_out_bits"] - 0.15
            and per_lang[l]["manuscript"]["held_out_bits"] <= per_lang[l]["controls"][str(round(per_lang[l]["r_star"], 3))]["held_out_bits"] + 0.3]
    flat = [l for l in ok if per_lang[l]["manuscript"]["held_out_bits"] >= per_lang[l]["v7"]["held_out_bits"] - 0.05]
    if hits:
        res.decide(True)
        res.summary = "Klucz z wierszy nieparzystych czyta parzyste lepiej niż bełkot: " + ", ".join(
            f"{l} {per_lang[l]['manuscript']['held_out_bits']:.2f} wobec v7 {per_lang[l]['v7']['held_out_bits']:.2f} bitu" for l in hits)
    elif ok and len(flat) == len(ok):
        res.decide(False)
        res.summary = (f"Łamacz czyta kontrole ({', '.join(f'{l} {per_lang[l]['controls']['0.0']['accuracy']:.2f}' for l in ok)}), "
                       "ale rękopis odczytany jako nomenklator nie jest bliższy językowi niż bełkot v7: " + "; ".join(
                           f"{l} {per_lang[l]['manuscript']['held_out_bits']:.2f} wobec {per_lang[l]['v7']['held_out_bits']:.2f} bitu (naturalnie {per_lang[l]['natural_bits']:.2f})" for l in ok) + ".")
    else:
        res.decide(None)
        res.summary = "Łamacz nie czyta kontroli albo wynik leży pomiędzy progami."
    res.caveats += ["Model języka to bigram jednostek z Biblii; tekst zielarski albo astrologiczny miałby inne słownictwo. Bigram "
                    "wystarcza jednak, żeby odczytać kontrole tej samej wielkości co rękopis.",
                    "Pomyłki odwracane tylko o jeden glif; kopista, który myli dwa glify w słowie, wytwarza typy, których scalanie nie złapie.",
                    "Perskiego korpusu nie ma w data/reference; perski nie został sprawdzony.",
                    "Dwa klucze = język A i B Curriera; nomenklator z kluczem zmienianym co dział nie jest tu sprawdzony."]
    res.seconds = time.time() - t0
    return res
