"""Merge a vision draft (results/lab/<run>/atoms_vision/) into data/atoms, page by page, with a quality gate.

    python scripts/merge_atoms.py <draft_dir> [--tolerance 1] [--force]

A page is taken only when the number of figures the models found is within `tolerance` of the known number of
nymphs (atoms_vision.EXPECTED; the label count elsewhere) and nobody has entered anything by hand on that page
(sources other than "", "vision", "vlm", "losowe"); --force overrides the second rule, never the first.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from voynich import atoms  # noqa: E402
from voynich.lab.theories.atoms_vision import EXPECTED  # noqa: E402

MACHINE = {"", "vision", "vlm", "losowe"}


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    draft = Path(argv[0])
    tol = int(argv[argv.index("--tolerance") + 1]) if "--tolerance" in argv else 1
    force = "--force" in argv
    vocab = atoms.load_vocab()
    taken, skipped = [], []
    for path in sorted(draft.glob("f*.json")):
        page = json.loads(path.read_text(encoding="utf-8"))
        folio = page["strona"]
        errors = atoms.validate(page, vocab, path.name)
        if errors:
            skipped.append(f"{folio}: błędy walidacji ({errors[0]})")
            continue
        found = sum(1 for a in page["atomy"] if a.get("zrodlo") == "vision" and a.get("pozycja", {}).get("x") is not None)
        labelled = sum(1 for a in page["atomy"] if a.get("etykieta"))
        expected = EXPECTED.get(folio, labelled)
        if abs(found - expected) > tol:
            skipped.append(f"{folio}: postaci {found}, oczekiwano {expected}")
            continue
        target = atoms.ATOMS_DIR / f"{folio}.json"
        if target.exists():
            current = json.loads(target.read_text(encoding="utf-8"))
            human = [a["id"] for a in current["atomy"] if a.get("zrodlo") not in MACHINE and any(v is not None for v in (a.get("cechy") or {}).values())]
            if human and not force:
                skipped.append(f"{folio}: {len(human)} atomów wpisanych ręcznie (użyj --force, żeby nadpisać)")
                continue
        target.write_text(json.dumps(page, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        taken.append(f"{folio}: {found} postaci (oczekiwano {expected})")
    print("scalone:", *taken, sep="\n  ")
    print("pominięte:", *skipped, sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
