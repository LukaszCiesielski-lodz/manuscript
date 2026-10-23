"""Build the word lists for the brute-force attack (data/reference/lexicon/<Language>.txt).

    python scripts/fetch_lexicons.py            # everything available
    python scripts/fetch_lexicons.py --local    # only from files fetch_data.py already produced

Downloads the extra Bible languages and the Universal Dependencies historical treebanks.
Optional data: the rest of the lab does not need it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from voynich import lexicon  # noqa: E402
from voynich.corpus import word_count  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_data import BIBLE_URL, bible_sample, conllu_words, fetch  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    done, failed = [], []
    for name in lexicon.LOCAL_SOURCES:
        path = lexicon.LEXICON_DIR / f"{name}.txt"
        if path.exists() and not args.force:
            continue
        try:
            lexicon.build_from_text(name, lexicon.local_words(name))
            done.append(name)
        except Exception as exc:
            failed.append(f"{name}: {exc}")
    if not args.local:
        for lang in lexicon.BIBLE_EXTRA:
            path = lexicon.LEXICON_DIR / f"{lang}.txt"
            if path.exists() and not args.force:
                continue
            try:
                lexicon.build_from_text(lang, bible_sample(lang, limit=None))
                done.append(lang)
            except Exception as exc:
                failed.append(f"{lang}: {exc}")
        for name, rel in lexicon.UD_SOURCES.items():
            path = lexicon.LEXICON_DIR / f"{name}.txt"
            if path.exists() and not args.force:
                continue
            try:
                lexicon.build_from_text(name, conllu_words(lexicon.UD_BASE.format(rel)))
                done.append(name)
            except Exception as exc:
                failed.append(f"{name}: {exc}")
    for name in done:
        words, _ = lexicon.load(name)
        print(f"{name:20s} {sum(words.values()):8d} tokens, {len(words):6d} types")
    print(f"\nLeksykony: {len(lexicon.available())} gotowe" + (f", {len(failed)} nieudane:" if failed else "."))
    for f in failed:
        print("  -", f)


if __name__ == "__main__":
    main()
