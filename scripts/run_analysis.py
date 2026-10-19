"""Run every experiment and write docs/results.json.

    python scripts/run_analysis.py            # full run (~10 min, cipher attacks dominate)
    python scripts/run_analysis.py --quick    # fewer languages, fewer trials
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from voynich import cipher, corpus, eva, ivtff, selfcite, stats, structure  # noqa: E402

N = 35_000  # tokens per text in comparisons; the Voynich has ~38k usable words
N_SMALL = 10_000  # for Currier A vs B, which are smaller
CIPHER_WORDS = 8_000
OUT = ROOT / "docs" / "results.json"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def full_profile(words) -> dict:
    out = stats.fingerprint(words)
    out["positional_rigidity"] = structure.positional_rigidity(words)
    out["order_consistency"] = structure.order_consistency(words)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    trials = 30 if args.quick else 200
    languages = corpus.reference_languages()
    cipher_langs = ["Latin", "Italian", "German"] if args.quick else languages

    pages = ivtff.parse(corpus.ZL_FILE)
    lines = corpus.load_voynich()
    words = corpus.tokens(lines)
    glyph_words = [eva.glyphs(w) for w in words]
    para_lines = [l for l in lines if l.kind.startswith("P")]
    res: dict = {"generated": time.strftime("%Y-%m-%d"), "n_compare": N}

    res["corpus"] = {
        "pages": len(pages),
        "lines": len(lines),
        "tokens": len(words),
        "types": len(set(words)),
        "glyph_inventory": len({g for w in glyph_words for g in w}),
        "by_section": Counter(l.section for l in lines for _ in l.words),
        "by_language": Counter(l.language for l in lines for _ in l.words),
        "by_hand": Counter(l.hand for l in lines for _ in l.words),
        "top_words": Counter(words).most_common(40),
    }

    log("fingerprints")
    fp = {"Voynich": full_profile(glyph_words[:N]), "Voynich (EVA letters)": full_profile(words[:N])}
    seed_lines = [[eva.glyphs(w) for w in l.words] for l in para_lines[:3]]
    line_lengths = [len(l.words) for l in para_lines]
    sc_runs = []
    for s in range(5 if not args.quick else 2):
        gen = selfcite.generate(seed_lines, N, line_lengths, seed=s + 1)
        sc_runs.append(full_profile([w for l in gen for w in l][:N]))
        if s == 0:
            sc_sample = [" ".join("".join(w) for w in l) for l in gen[200:206]]
    fp["Self-citation model"] = {k: statistics.mean(r[k] for r in sc_runs) for k in sc_runs[0]}
    res["selfcite_sd"] = {k: statistics.pstdev(r[k] for r in sc_runs) for k in sc_runs[0]}
    res["selfcite_sample"] = sc_sample
    ref_words = {}
    for lang in languages:
        ref_words[lang] = corpus.load_reference(lang)
        fp[lang] = full_profile(ref_words[lang][:N])
    shuffled = list(glyph_words[:N])
    random.Random(0).shuffle(shuffled)
    fp["Voynich, words shuffled"] = full_profile(shuffled)
    res["fingerprints"] = fp

    log("Currier A vs B")
    ab = {}
    for lang in ("A", "B"):
        ws = [eva.glyphs(w) for w in corpus.tokens(lines, language=lang)]
        ab[f"Currier {lang}"] = {"available": len(ws), **full_profile(ws[:N_SMALL])}
    ab["Latin"] = full_profile(ref_words["Latin"][:N_SMALL])
    res["currier"] = ab

    log("permutation tests")
    perm = {}
    for name, ws in (("Voynich", glyph_words[:N]), ("Latin", ref_words["Latin"][:N]),
                     ("Italian", ref_words["Italian"][:N])):
        for stat_name, fn in (("adjacent_near", structure.adjacent_near_rate),
                              ("adjacent_repeat", structure.adjacent_repeat_rate)):
            obs, null, p = structure.permutation_test(ws, fn, trials=trials)
            perm.setdefault(name, {})[stat_name] = {"observed": obs, "shuffled_mean": null, "p": p,
                                                    "trials": trials}
    res["permutation"] = perm

    log("positions")
    res["positional_profile"] = {
        "Voynich": structure.positional_profile(glyph_words),
        "Latin": structure.positional_profile(ref_words["Latin"][:N]),
    }
    glyph_counts = Counter(g for w in glyph_words for g in w)
    res["glyph_counts"] = glyph_counts.most_common()
    res["line_position"] = structure.line_position_enrichment(
        [[eva.glyphs(w) for w in l.words] for l in para_lines])
    res["length_distribution"] = {"Voynich": stats.length_distribution(glyph_words[:N])}
    for lang in ("Latin", "Italian", "German", "Polish", "Hebrew"):
        res["length_distribution"][lang] = stats.length_distribution(ref_words[lang][:N])
    res["rank_frequency"] = {"Voynich": stats.rank_frequency(glyph_words[:N])}
    for lang in ("Latin", "English", "Polish"):
        res["rank_frequency"][lang] = stats.rank_frequency(ref_words[lang][:N])

    log("keywords")
    by_section: dict[str, list[str]] = {}
    for l in lines:
        by_section.setdefault(l.section, []).extend(l.words)
    res["section_keywords"] = structure.keywords(by_section)
    res["currier_keywords"] = structure.keywords(
        {lang: corpus.tokens(lines, language=lang) for lang in ("A", "B")}, top=15)
    labels = [w for l in lines if l.kind.startswith("L") for w in l.words]
    res["labels"] = {"tokens": len(labels), "types": len(set(labels)),
                     "in_running_text": sum(1 for w in set(labels) if w in set(corpus.tokens(lines, paragraphs_only=True))) / max(1, len(set(labels))),
                     "top": Counter(labels).most_common(15)}

    log("cipher attacks")
    allv = [eva.glyphs(w) for w in corpus.tokens(lines, paragraphs_only=True)]
    vtest, vtrain = allv[:CIPHER_WORDS], allv[CIPHER_WORDS:]
    v_self = cipher.self_entropy(vtrain, vtest)
    attacks = {"voynich_self_bits": v_self, "languages": {}}
    for lang in cipher_langs:
        t = time.time()
        ref = ref_words[lang]
        model = cipher.TrigramModel(ref[20_000:])
        row = {"plain_bits": model.bits_per_symbol(ref[:CIPHER_WORDS])}
        for h in (1, 2):
            c, truth = cipher.random_substitution(ref, seed=h, homophones=h)
            sol = cipher.solve(c[:CIPHER_WORDS], model)
            s_self = cipher.self_entropy(c[20_000:], c[:CIPHER_WORDS])
            row[f"control_h{h}"] = {"key_bits": sol.bits, "self_bits": s_self, "gap": sol.bits - s_self,
                                    "accuracy": cipher.accuracy(sol, c[:CIPHER_WORDS], truth)}
        sol = cipher.solve(vtest, model)
        row["voynich"] = {"key_bits": sol.bits, "self_bits": v_self, "gap": sol.bits - v_self,
                          "decrypted": " ".join(sol.decrypt(vtest[:24])),
                          "key": {g: p for g, p in sorted(sol.key.items()) if g != " "}}
        attacks["languages"][lang] = row
        log(f"  {lang}: gap {row['voynich']['gap']:+.3f} bits ({time.time() - t:.0f}s)")
    attacks["original"] = " ".join("".join(w) for w in vtest[:24])
    res["cipher"] = attacks

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    log(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
