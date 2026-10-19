"""Download reference corpora (and the ZL transliteration if missing).

Reference texts come from the multilingual Bible corpus of Christos
Christodoulopoulos (https://github.com/christos-c/bible-corpus): the same
content in every language gives a controlled comparison. Each sample is the
first SAMPLE_WORDS words starting at Genesis, normalized to lowercase letters.

    python scripts/fetch_data.py
"""

from __future__ import annotations

import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from voynich.corpus import REFERENCE_DIR, ZL_FILE, normalize_words  # noqa: E402

BIBLE_URL = "https://raw.githubusercontent.com/christos-c/bible-corpus/master/bibles/{}.xml"
ZL_URLS = [
    "https://www.voynich.nu/data/ZL3b-n.txt",
    "https://raw.githubusercontent.com/noah-chelednik/voynich-data/main/data_sources/cache/ZL3b-n.txt",
]
LANGUAGES = ["Latin", "Italian", "German", "Polish", "Czech", "English", "Hungarian",
             "Finnish", "Turkish", "Hebrew", "Arabic", "Vietnamese"]
SAMPLE_WORDS = 60_000


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read()


def bible_sample(language: str) -> list[str]:
    xml = fetch(BIBLE_URL.format(language)).decode("utf-8")
    # Some files carry stray control characters that break the XML parser.
    xml = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", xml)
    root = ET.fromstring(xml)
    out: list[str] = []
    for seg in root.iter("seg"):
        out.extend(normalize_words("".join(seg.itertext())))
        if len(out) >= SAMPLE_WORDS:
            break
    return out[:SAMPLE_WORDS]


def main() -> None:
    if not ZL_FILE.exists():
        ZL_FILE.parent.mkdir(parents=True, exist_ok=True)
        for url in ZL_URLS:
            try:
                ZL_FILE.write_bytes(fetch(url))
                print(f"ZL transliteration <- {url}")
                break
            except OSError as exc:
                print(f"  {url}: {exc}")
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    for lang in LANGUAGES:
        path = REFERENCE_DIR / f"{lang}.txt"
        if path.exists():
            continue
        words = bible_sample(lang)
        path.write_text(" ".join(words) + "\n", encoding="utf-8")
        print(f"{lang:12s} {len(words):6d} words -> {path.relative_to(REFERENCE_DIR.parent.parent)}")


if __name__ == "__main__":
    main()
