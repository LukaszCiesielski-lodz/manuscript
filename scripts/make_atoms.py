"""Generate the atom template files (one per page with labels) from the transliteration.

    python scripts/make_atoms.py            # add missing pages, keep existing files
    python scripts/make_atoms.py --check    # only validate data/atoms against vocab.json

Existing files are never overwritten: someone may have filled them.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from voynich import atoms  # noqa: E402


def main(argv: list[str]) -> int:
    if "--check" not in argv:
        written, kept = atoms.write_templates()
        print(f"zapisano {len(written)} nowych stron, zachowano {len(kept)} istniejących")
    try:
        all_atoms = atoms.load()
    except ValueError as e:
        print(e)
        return 1
    s = atoms.summary(all_atoms)
    print(f"atomów {s['atoms']} na {s['pages']} stronach; wypełnionych {s['filled']} na {s['pages_filled']} stronach; "
          f"źródła: {', '.join(s['sources']) or 'brak'}; działy: {s['per_section']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
