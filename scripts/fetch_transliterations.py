"""Fetch the other transliterations of the manuscript (voynich.nu; GitHub cache as fallback).

    python scripts/fetch_transliterations.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_data import fetch  # noqa: E402
from voynich import transliterations as tr  # noqa: E402


def main() -> None:
    tr.DIR.mkdir(parents=True, exist_ok=True)
    for tid, (name, _, urls) in tr.SOURCES.items():
        if tr.path(tid).exists():
            continue
        for url in urls:
            try:
                tr.path(tid).write_bytes(fetch(url))
                print(f"{tid} ({name}) <- {url}")
                break
            except OSError as exc:
                print(f"  {url}: {exc}")
    print("Transliteracje:", ", ".join(tr.available()))


if __name__ == "__main__":
    main()
