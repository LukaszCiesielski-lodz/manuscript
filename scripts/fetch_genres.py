"""Fetch the medieval genre texts for the 'genres' theory into data/reference/genres/.

    python scripts/fetch_genres.py

Litany of the Saints (la.wikisource, public domain) and the barbarous names of the Ars Notoria
and Liber Iuratus (Esoteric Archives editions by Joseph H. Peterson; only the names are kept).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_data import fetch  # noqa: E402
from voynich import genres  # noqa: E402


def main() -> None:
    genres.GENRES_DIR.mkdir(parents=True, exist_ok=True)
    failed = []
    try:
        wikitext = json.loads(fetch(genres.LITANY_URL).decode("utf-8"))["parse"]["wikitext"]
        words = genres.litany_words(wikitext)
        (genres.GENRES_DIR / "litany.txt").write_text(" ".join(words) + "\n", encoding="utf-8")
        print(f"litany       {len(words):6d} words")
    except Exception as exc:
        failed.append(f"litany: {exc}")
    known = genres.known_words()
    names = []
    for url in (genres.NOTORIA_URL, genres.IURATUS_URL):
        try:
            names += genres.barbarous_names(fetch(url).decode("latin-1"), known)
        except Exception as exc:
            failed.append(f"{url}: {exc}")
    if names:
        (genres.GENRES_DIR / "voces_magicae.txt").write_text(" ".join(names) + "\n", encoding="utf-8")
        print(f"voces magicae {len(names):5d} names")
    print("Gatunki:", ", ".join(genres.available()) or "brak", ("; nieudane: " + "; ".join(failed)) if failed else "")


if __name__ == "__main__":
    main()
