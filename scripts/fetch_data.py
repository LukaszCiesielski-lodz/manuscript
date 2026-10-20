"""Download reference corpora (and the ZL transliteration if missing).

Reference texts come from the multilingual Bible corpus of Christos
Christodoulopoulos (https://github.com/christos-c/bible-corpus): the same
content in every language gives a controlled comparison. Each sample is the
first SAMPLE_WORDS words starting at Genesis, normalized to lowercase letters.

    python scripts/fetch_data.py
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from voynich.corpus import (BIBLE_FILES, BIBLE_LANGUAGES, BIBLE_WORDS, EXTRA_DIR, EXTRA_TEXTS,  # noqa: E402
                            MEDIEVAL_DIR, MEDIEVAL_MIN_WORDS, REFERENCE_DIR, ZL_FILE, data_problems,
                            normalize_words, word_count)
from voynich.latin import normalize as normalize_latin  # noqa: E402

BIBLE_URL = "https://raw.githubusercontent.com/christos-c/bible-corpus/master/bibles/{}.xml"
ZL_URLS = [
    "https://www.voynich.nu/data/ZL3b-n.txt",
    "https://raw.githubusercontent.com/noah-chelednik/voynich-data/main/data_sources/cache/ZL3b-n.txt",
]
LANGUAGES = BIBLE_LANGUAGES
SAMPLE_WORDS = BIBLE_WORDS

# Modern Basque news prose (Universal Dependencies Basque BDT treebank, CC BY-NC-SA 3.0; not committed).
EXTRA_URLS = {"basque_news": "https://raw.githubusercontent.com/UniversalDependencies/UD_Basque-BDT/master/eu_bdt-ud-train.conllu"}


def conllu_words(url: str) -> list[str]:
    forms = [l.split("\t")[1] for l in fetch(url).decode("utf-8").splitlines() if l[:1].isdigit() and "\t" in l]
    return normalize_words(" ".join(forms))

# Medieval Latin from The Latin Library, via the CLTK mirror. name -> files.
LATIN_LIBRARY = "https://raw.githubusercontent.com/cltk/lat_text_latin_library/master/{}"
MEDIEVAL = {
    "Isidorus": ["isidore/17.txt", "isidore/4.txt", "isidore/12.txt"],
    "Hugo": [f"hugo/hugo{i}.txt" for i in range(1, 7)] + ["hugo/hugo.solo.txt"],
    "Alfonsi": ["alfonsi.disciplina.txt"],
    "Conches": ["wmconchesdogma.txt", "wmconchesphil.txt"],
    "Aquinas": ["aquinas/ente.txt", "aquinas/princ.txt", "aquinas/prologus.txt"]
               + [f"aquinas/q1.{i}.txt" for i in range(1, 30)],
    "Voragine": [f"voragine/{n}.txt" for n in (
        "alexio ambro anast andrea ant blas chris fran georgio iacob iul jud luc marc mariamag "
        "marina nic paulo seb septem silv thom vin vir").split()],
    "Dante": [f"dante/{n}.txt" for n in ("mon1", "mon2", "mon3", "vulgar", "vulgar2")],
    "Petrarca": ["petrarchmedicus.txt"],
    "Gesta": ["gestarom.txt"],
    "Kempis": [f"kempis/kempis{i}.txt" for i in range(1, 5)],
    "Poggio": ["poggio.txt"],
    "Columella": [f"columella/columella.rr{i}.txt" for i in (2, 3, 5, 6, 8, 9, 11, 12)],
}
_FOOTER = re.compile(r"The Latin Library|The Classics Page|Christian Latin|Medieval Latin|Neo-Latin")
_ROMAN = re.compile(r"^[IVXLCDM]+\.?$")


def latin_library_words(path: str) -> list[str]:
    """Running text of one Latin Library page: no title line, footer, headings or numerals."""
    lines = fetch(LATIN_LIBRARY.format(path)).decode("utf-8", "replace").splitlines()[1:]
    words = []
    for line in lines:
        letters = re.sub(r"[^A-Za-z]", "", line)
        if not letters or _FOOTER.search(line) or letters.isupper():
            continue
        line = re.sub(r"\[\d+\]", " ", line)
        words += [w for w in line.split() if not _ROMAN.match(w)]
    return normalize_latin(words, merge_uv=False)


def fetch(url: str) -> bytes:
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                return resp.read()
        except OSError:
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))
    raise OSError(url)


def bible_sample(language: str) -> list[str]:
    xml = fetch(BIBLE_URL.format(BIBLE_FILES.get(language, language))).decode("utf-8")
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="download everything again")
    force = ap.parse_args().force
    if not ZL_FILE.exists():
        ZL_FILE.parent.mkdir(parents=True, exist_ok=True)
        for url in ZL_URLS:
            try:
                ZL_FILE.write_bytes(fetch(url))
                print(f"ZL transliteration <- {url}")
                break
            except OSError as exc:
                print(f"  {url}: {exc}")
    failed = []
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    for lang in LANGUAGES:
        path = REFERENCE_DIR / f"{lang}.txt"
        if not force and word_count(path) >= SAMPLE_WORDS:
            continue
        try:
            words = bible_sample(lang)
        except Exception as exc:  # keep going: one bad download must not leave the rest missing
            failed.append(f"{lang}: {exc}")
            continue
        if len(words) < SAMPLE_WORDS:
            failed.append(f"{lang}: tylko {len(words)} słów")
            continue
        path.write_text(" ".join(words) + "\n", encoding="utf-8")
        print(f"{lang:12s} {len(words):6d} words -> {path.relative_to(REFERENCE_DIR.parent.parent)}")
    EXTRA_DIR.mkdir(parents=True, exist_ok=True)
    for name, minimum in EXTRA_TEXTS.items():
        path = EXTRA_DIR / f"{name}.txt"
        if not force and word_count(path) >= minimum:
            continue
        try:
            words = conllu_words(EXTRA_URLS[name])
        except Exception as exc:
            failed.append(f"extra/{name}: {exc}")
            continue
        path.write_text(" ".join(words) + "\n", encoding="utf-8")
        print(f"{name:12s} {len(words):6d} words -> {path.relative_to(REFERENCE_DIR.parent.parent)}")
    MEDIEVAL_DIR.mkdir(parents=True, exist_ok=True)
    for name, files in MEDIEVAL.items():
        path = MEDIEVAL_DIR / f"{name}.txt"
        if not force and word_count(path) >= MEDIEVAL_MIN_WORDS:
            continue
        try:
            words = [w for f in files for w in latin_library_words(f)]
        except Exception as exc:
            failed.append(f"medieval/{name}: {exc}")
            continue
        if len(words) < MEDIEVAL_MIN_WORDS:
            failed.append(f"medieval/{name}: tylko {len(words)} słów")
            continue
        path.write_text(" ".join(words) + "\n", encoding="utf-8")
        print(f"{name:12s} {len(words):6d} words -> {path.relative_to(REFERENCE_DIR.parent.parent)}")
    problems = data_problems()
    if failed or problems:
        print("\nNIEKOMPLETNE DANE:")
        for msg in dict.fromkeys(failed + problems):
            print("  -", msg)
        print("Uruchom skrypt ponownie (pobierze tylko brakujące pliki) albo z --force.")
        sys.exit(1)
    print("Dane kompletne.")


if __name__ == "__main__":
    main()
