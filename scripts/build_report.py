"""Build docs/index.html from docs/template.html and docs/results.json.

    python scripts/build_report.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Glyphs shown in the slot chart, in reading order of their usual slot.
SLOT_GLYPHS = ["q", "o", "ch", "sh", "y", "d", "s", "cth", "ckh", "k", "t", "p", "f", "e", "a",
               "ii", "i", "l", "r", "n", "m", "g"]


def _finite(x):
    """NaN is not valid JSON; the page shows None as a dash."""
    if isinstance(x, float) and math.isnan(x):
        return None
    if isinstance(x, dict):
        return {k: _finite(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_finite(v) for v in x]
    return x


def main() -> None:
    res = json.loads((DOCS / "results.json").read_text(encoding="utf-8"))
    latin_top = [c for c, _ in sorted(
        ((c, sum(p.values())) for c, p in res["positional_profile"]["Latin"].items()), key=lambda t: -t[1])]
    data = {
        "corpus": res["corpus"],
        "n": res["n_compare"],
        "fingerprints": res["fingerprints"],
        "selfcite_sd": res["selfcite_sd"],
        "selfcite_sample": res["selfcite_sample"],
        "currier": res["currier"],
        "permutation": res["permutation"],
        "slots": {
            "Voynich": {g: res["positional_profile"]["Voynich"][g] for g in SLOT_GLYPHS
                        if g in res["positional_profile"]["Voynich"]},
            "Latin": {c: res["positional_profile"]["Latin"][c] for c in sorted(latin_top)},
        },
        "line_position": res["line_position"],
        "length_distribution": res["length_distribution"],
        "rank_frequency": {k: v[:1000] for k, v in res["rank_frequency"].items()},
        "section_keywords": res["section_keywords"],
        "currier_keywords": res["currier_keywords"],
        "labels": res["labels"],
        "cipher": res["cipher"],
        "generated": res["generated"],
        "ext": json.loads((DOCS / "results_ext.json").read_text(encoding="utf-8")),
    }
    blob = json.dumps(_finite(data), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = (DOCS / "template.html").read_text(encoding="utf-8").replace("__DATA__", blob)
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote docs/index.html ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
