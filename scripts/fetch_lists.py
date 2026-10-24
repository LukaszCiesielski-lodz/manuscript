"""Fetch and parse the list corpora for the 'lists' and 'records' theories into data/lists/.

    python scripts/fetch_lists.py

The parsed files are committed (small, public domain), so Colab needs no network; run this to refresh.
Martyrology and Apicius come from la.wikisource (MediaWiki API, wikitext), Alphita from the
archive.org OCR of Mowat's 1887 edition.
"""

from __future__ import annotations

import json
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_data import fetch  # noqa: E402
from voynich import lists  # noqa: E402


def wikitext(pages: list[str]) -> str:
    data = json.loads(fetch(lists.WIKI_API + urllib.parse.quote("|".join(pages), safe="")).decode("utf-8"))
    by_title = {p["title"].replace(" ", "_"): p["revisions"][0]["slots"]["main"]["content"] for p in data["query"]["pages"]}
    return "\n".join(by_title[t] for t in pages if t in by_title)


def main() -> None:
    lists.DIR.mkdir(parents=True, exist_ok=True)
    todo = {"martyrology": lambda: lists.martyrology_entries(wikitext(lists.MARTYROLOGY_PAGES)),
            "apicius": lambda: lists.apicius_entries(wikitext(lists.APICIUS_PAGES))}
    alphita = None

    def alphita_text() -> str:
        nonlocal alphita
        if alphita is None:
            alphita = fetch(lists.ALPHITA_URL).decode("utf-8", errors="replace")
        return alphita

    todo["alphita"] = lambda: lists.alphita_entries(alphita_text())
    todo["alphita_headwords"] = lambda: lists.alphita_headwords(alphita_text())
    for name, parse in todo.items():
        path = lists.DIR / f"{name}.txt"
        if path.exists():
            print(f"{name}: już jest ({lists.quality(lists.load(name))})")
            continue
        try:
            entries = parse()
        except Exception as exc:
            print(f"{name}: niedostępne ({exc})")
            continue
        lists.save(name, entries)
        print(f"{name}: {lists.quality(entries)} -> {path}")
    print("Listy gotowe.")


if __name__ == "__main__":
    main()
