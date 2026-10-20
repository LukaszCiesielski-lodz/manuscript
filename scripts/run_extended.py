"""Follow-up experiments: medieval Latin, syllabic ciphers, and a better generator.

Writes docs/results_ext.json.

    python scripts/run_extended.py            # ~15 min
    python scripts/run_extended.py --quick
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from voynich import cipher, corpus, eva, latin, selfcite, stats, structure, syllabic  # noqa: E402

N_MED = 13_000  # the shortest medieval sample has ~13.9k words
N = 35_000
CIPHER_WORDS = 8_000
# The medieval model is trained on mixed authors; the search needs more room than for the Bible.
SOLVER_RESTARTS, SOLVER_STEPS = 8, 30_000
OUT = ROOT / "docs" / "results_ext.json"
MAP_METRICS = ["h2", "h3", "mean_word_len", "sd_word_len", "vocab_density", "adjacent_near",
               "adjacent_repeat", "order_consistency", "positional_rigidity", "hapax_ratio", "zipf_slope"]
MEDIEVAL_INFO = {
    "Isidorus": ("Izydor z Sewilli, Etymologiae XVII, IV, XII (rośliny, medycyna, zwierzęta)", "VII"),
    "Hugo": ("Hugo od św. Wiktora", "XII"),
    "Alfonsi": ("Piotr Alfonsi, Disciplina clericalis", "XII"),
    "Conches": ("Wilhelm z Conches, Dragmaticon i Philosophia", "XII"),
    "Aquinas": ("Tomasz z Akwinu, Summa (I, q. 1–29) i opuscula", "XIII"),
    "Voragine": ("Jakub de Voragine, Złota legenda", "XIII"),
    "Dante": ("Dante, Monarchia i De vulgari eloquentia", "XIV"),
    "Petrarca": ("Petrarka, Invectiva contra medicum", "XIV"),
    "Gesta": ("Gesta Romanorum", "XIV"),
    "Kempis": ("Tomasz à Kempis, O naśladowaniu Chrystusa", "XV"),
    "Poggio": ("Poggio Bracciolini, Facetiae", "XV"),
    "Columella": ("Kolumella, De re rustica (rolnictwo i ogrody)", "I"),
}


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def profile(words) -> dict:
    out = stats.fingerprint(words)
    out["positional_rigidity"] = structure.positional_rigidity(words)
    out["order_consistency"] = structure.order_consistency(words)
    return out


def pca_2d(rows: dict[str, dict]) -> dict[str, list[float]]:
    """Project texts onto the first two principal components of z-scored metrics."""
    names = list(rows)
    cols = []
    for m in MAP_METRICS:
        v = [rows[n][m] for n in names]
        mu, sd = statistics.mean(v), statistics.pstdev(v) or 1.0
        cols.append([(x - mu) / sd for x in v])
    X = [list(r) for r in zip(*cols)]  # texts x metrics
    d = len(MAP_METRICS)
    cov = [[sum(r[i] * r[j] for r in X) / len(X) for j in range(d)] for i in range(d)]
    comps = []
    for _ in range(2):
        v = [1.0] * d
        for _ in range(500):
            w = [sum(cov[i][j] * v[j] for j in range(d)) for i in range(d)]
            norm = math.sqrt(sum(x * x for x in w))
            v = [x / norm for x in w]
        lam = sum(v[i] * sum(cov[i][j] * v[j] for j in range(d)) for i in range(d))
        comps.append((v, lam))
        cov = [[cov[i][j] - lam * v[i] * v[j] for j in range(d)] for i in range(d)]
    total = sum(statistics.pvariance(c) for c in cols)
    return {
        "points": {n: [sum(a * b for a, b in zip(X[k], comps[0][0])), sum(a * b for a, b in zip(X[k], comps[1][0]))]
                   for k, n in enumerate(names)},
        "loadings": {m: [comps[0][0][i], comps[1][0][i]] for i, m in enumerate(MAP_METRICS)},
        "explained": [comps[0][1] / total, comps[1][1] / total],
    }


def medieval(res: dict, lines, quick: bool) -> None:
    log("medieval Latin: fingerprints")
    V = [eva.glyphs(w) for w in corpus.tokens(lines)]
    rows = {
        "Voynich": V[:N_MED],
        "Voynich: zielnik": [eva.glyphs(w) for w in corpus.tokens(lines, section="herbal")][:N_MED],
        "Voynich: Currier B": [eva.glyphs(w) for w in corpus.tokens(lines, language="B")][:N_MED],
    }
    for name in corpus.medieval_texts():
        rows[name] = corpus.load_medieval(name, N_MED)
    for name in ("Isidorus", "Kempis", "Voragine"):
        rows[f"{name} (skróty)"] = [list(latin.abbreviate(w)) for w in corpus.load_medieval(name, N_MED)]
    rows["Wulgata"] = latin.normalize(corpus.load_reference("Latin", N_MED))
    fps = {n: profile(w) for n, w in rows.items()}
    res["medieval"] = {"n": N_MED, "info": MEDIEVAL_INFO, "fingerprints": fps,
                       "abbrev_sample": " ".join(latin.abbreviate(w) for w in corpus.load_medieval("Isidorus")[60:84])}

    log("medieval Latin: cipher attack")
    train = [w for n in corpus.medieval_texts() if n not in ("Isidorus", "Columella")
             for w in corpus.load_medieval(n, 20_000)]
    model = cipher.TrigramModel(train)
    iso = corpus.load_medieval("Isidorus")
    row = {"plain_bits": model.bits_per_symbol(iso[:CIPHER_WORDS])}
    for h in (1, 2):
        c, truth = cipher.random_substitution(iso, seed=h, homophones=h)
        sol = cipher.solve(c[:CIPHER_WORDS], model, restarts=SOLVER_RESTARTS, steps=SOLVER_STEPS)
        s_self = cipher.self_entropy(c[CIPHER_WORDS:], c[:CIPHER_WORDS])
        row[f"control_h{h}"] = {"key_bits": sol.bits, "self_bits": s_self, "gap": sol.bits - s_self,
                                "accuracy": cipher.accuracy(sol, c[:CIPHER_WORDS], truth)}
    para = [l for l in lines if l.kind.startswith("P")]
    targets = {"zielnik": lambda l: l.section == "herbal", "Currier B": lambda l: l.language == "B"}
    for tname, pick in targets.items():
        test, test_ids = [], set()
        for l in para:
            if pick(l) and len(test) < CIPHER_WORDS:
                test += [eva.glyphs(w) for w in l.words]
                test_ids.add(id(l))
        # Self-model: every other paragraph line of the manuscript.
        rest = [eva.glyphs(w) for l in para if id(l) not in test_ids for w in l.words]
        sol = cipher.solve(test, model, restarts=SOLVER_RESTARTS, steps=SOLVER_STEPS)
        s_self = cipher.self_entropy(rest, test)
        row[tname] = {"key_bits": sol.bits, "self_bits": s_self, "gap": sol.bits - s_self,
                      "decrypted": " ".join(sol.decrypt(test[:20])), "original": " ".join("".join(w) for w in test[:20])}
        log(f"  {tname}: gap {row[tname]['gap']:+.3f}")
    res["medieval"]["cipher"] = row


def syllables(res: dict, lines) -> None:
    log("syllabic hypotheses")
    V = [eva.glyphs(w) for w in corpus.tokens(lines)]
    out = {"n": N_MED}
    a = {"Voynich (słowa)": profile(V[:N_MED])}
    for name in ("Isidorus", "Kempis", "Voragine"):
        a[f"{name} (sylaby)"] = profile(syllabic.syllable_stream(corpus.load_medieval(name, merge_uv=False))[:N_MED])
    a["wietnamski (sylaby)"] = profile(corpus.load_reference("Vietnamese", N_MED))
    out["word_is_syllable"] = a
    b = {"Voynich": profile(V[:N_MED])}
    samples = {}
    for name in ("Isidorus", "Kempis", "Voragine"):
        raw = corpus.load_medieval(name, merge_uv=False)
        code = syllabic.SyllableCipher(raw, V)
        enc = code.encode(raw[:N_MED])
        b[f"{name} → szyfr sylabiczny"] = profile(enc)
        b[f"{name} (jawny)"] = profile(corpus.load_medieval(name, N_MED))
        samples[name] = {"plain": " ".join(raw[100:112]), "cipher": " ".join("".join(w) for w in code.encode(raw[100:112])),
                         "syllables": " ".join("-".join(latin.syllabify(w)) for w in raw[100:112])}
    out["syllable_cipher"] = b
    out["samples"] = samples
    inv = {"Voynich": syllabic.repeat_profile(V[:N_MED])}
    for name in corpus.medieval_texts():
        inv[name] = syllabic.repeat_profile(corpus.load_medieval(name, N_MED))
    for lang in corpus.reference_languages():
        inv[lang] = syllabic.repeat_profile(corpus.load_reference(lang, N_MED))
    out["invariants"] = inv
    ws = ["".join(w) for w in V]
    out["voynich_repeats"] = Counter(x for x, y in zip(ws, ws[1:]) if x == y).most_common(15)
    res["syllabic"] = out


def generator(res: dict, lines, quick: bool) -> None:
    log("generator")
    para = [l for l in lines if l.kind.startswith("P")]
    lens = [len(l.words) for l in para]
    seed_lines = [[eva.glyphs(w) for w in l.words] for l in para[:3]]
    V = [eva.glyphs(w) for w in corpus.tokens(lines)]
    real = profile(V[:N])
    edits = selfcite.EditModel(V)
    pairs = selfcite.GlyphGrammar(V)
    seeds = (1, 2) if quick else (1, 2, 3)

    def run(**kw):
        runs = []
        for s in seeds:
            gen = selfcite.generate(seed_lines, N, lens, seed=s, **kw)
            ws = [w for l in gen for w in l][:N]
            p = profile(ws)
            lp = structure.line_position_enrichment(gen)
            p["m_line_last"] = lp.get("m", {}).get("line_last", math.nan)
            p["g_line_last"] = lp.get("g", {}).get("line_last", math.nan)
            runs.append((p, gen))
        mean = {}
        for k in runs[0][0]:
            vals = [r[0][k] for r in runs if not math.isnan(r[0][k])]
            mean[k] = statistics.mean(vals) if vals else None  # None: glyph too rare to measure
        return mean, runs[0][1]

    lp_real = structure.line_position_enrichment([[eva.glyphs(w) for w in l.words] for l in para])
    real["m_line_last"], real["g_line_last"] = lp_real["m"]["line_last"], lp_real["g"]["line_last"]

    # Grid search on the word-grammar model, scored on h2 and adjacent_near only.
    grid = []
    betas = (4, 5) if quick else (4, 5, 6)
    for beta, p_copy, window, p_far in itertools.product(betas, (0.1, 0.22), (4, 8), (0.05, 0.15)):
        gram = selfcite.WordGrammar(V, beta=beta)
        prof, _ = run(edits=edits, grammar=gram, p_copy=p_copy, window=window, p_far=p_far)
        loss = abs(prof["h2"] - real["h2"]) / 0.1 + abs(prof["adjacent_near"] - real["adjacent_near"]) / 0.005
        grid.append({"beta": beta, "p_copy": p_copy, "window": window, "p_far": p_far, "loss": loss,
                     "h2": prof["h2"], "adjacent_near": prof["adjacent_near"]})
        log(f"  beta={beta} copy={p_copy} win={window} far={p_far}: loss {loss:.2f}")
    best = min(grid, key=lambda g: g["loss"])

    variants = {}
    variants["v1: reguły ręczne"] = run()
    variants["v2: zmiany podpatrzone u skryby"] = run(edits=edits)
    variants["v3: v2 + dozwolone pary glifów"] = run(edits=edits, grammar=pairs)
    variants["v4: v2 + gramatyka słowa"] = run(edits=edits, grammar=selfcite.WordGrammar(V, beta=best["beta"]),
                                               p_copy=best["p_copy"], window=best["window"], p_far=best["p_far"])
    res["generator"] = {
        "real": real,
        "variants": {k: v[0] for k, v in variants.items()},
        "samples": {k: [" ".join("".join(w) for w in l) for l in v[1][300:305]] for k, v in variants.items()},
        "best": best,
        "grid": grid,
        "edit_pairs": edits.pairs,
        "top_edits": [[list(op), n] for op, n in edits.ops.most_common(12)],
        "allowed_pairs": len(pairs.allowed),
        "tuned_on": ["h2", "adjacent_near"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--only", choices=["medieval", "syllabic", "generator"])
    args = ap.parse_args()
    lines = corpus.load_voynich()
    res = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() and args.only else {}
    res["generated"] = time.strftime("%Y-%m-%d")
    if args.only in (None, "medieval"):
        medieval(res, lines, args.quick)
    if args.only in (None, "syllabic"):
        syllables(res, lines)
    if args.only in (None, "generator"):
        generator(res, lines, args.quick)
    if args.only in (None, "medieval", "generator") and "medieval" in res and "generator" in res:
        log("map")
        rows = dict(res["medieval"]["fingerprints"])
        for lang in corpus.reference_languages():
            if lang != "Latin":
                rows[lang] = profile(corpus.load_reference(lang, N_MED))
        para = [l for l in lines if l.kind.startswith("P")]
        V = [eva.glyphs(w) for w in corpus.tokens(lines)]
        b = res["generator"]["best"]
        gen = selfcite.generate([[eva.glyphs(w) for w in l.words] for l in para[:3]], N_MED,
                                [len(l.words) for l in para], seed=1, edits=selfcite.EditModel(V),
                                grammar=selfcite.WordGrammar(V, beta=b["beta"]), p_copy=b["p_copy"],
                                window=b["window"], p_far=b["p_far"])
        rows["Generator v4"] = profile([w for l in gen for w in l][:N_MED])
        res["map"] = pca_2d(rows)
        res["map"]["groups"] = {n: ("voynich" if n.startswith("Voynich") else "generator" if n.startswith("Generator")
                                    else "abbrev" if "skróty" in n
                                    else "medieval" if n in MEDIEVAL_INFO or n == "Wulgata" else "bible")
                                for n in rows}
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    log(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
