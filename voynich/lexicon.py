"""Word lists with frequencies for many languages of the manuscript's time, for the brute-force attack.

Sources (none committed; scripts/fetch_lexicons.py downloads them):
- the multilingual Bible corpus (christos-c/bible-corpus): modern editions, used as proxies
  for the lexical core of languages spoken around 1400;
- Universal Dependencies treebanks of historical languages (Ancient Greek, Old Church
  Slavonic, Old East Slavic, Gothic, Classical Armenian, Coptic, Biblical Hebrew, Middle
  French, Aquinas' Latin) and of a few living ones without a Bible file here;
- what the lab already holds: medieval Latin (Latin Library), Egeria, Old French, Basque.

A lexicon is a Counter of normalized words: lower case, combining marks removed (so
medieval spelling without diacritics, Hebrew without points), letters only.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from pathlib import Path

from . import corpus

LEXICON_DIR = corpus.REFERENCE_DIR / "lexicon"
MAX_LEN = 12

BIBLE_EXTRA = ["Dutch", "Danish", "Swedish", "Norwegian", "Icelandic", "Greek", "Albanian", "Croatian", "Serbian",
               "Slovene", "Slovak", "Bulgarian", "Russian", "Lithuanian", "Afrikaans", "Amharic", "Hindi"]
UD_BASE = "https://raw.githubusercontent.com/UniversalDependencies/{}"
UD_SOURCES = {
    "AncientGreek": "UD_Ancient_Greek-PROIEL/master/grc_proiel-ud-train.conllu",
    "OldChurchSlavonic": "UD_Old_Church_Slavonic-PROIEL/master/cu_proiel-ud-train.conllu",
    "OldEastSlavic": "UD_Old_East_Slavic-TOROT/master/orv_torot-ud-train.conllu",
    "Gothic": "UD_Gothic-PROIEL/master/got_proiel-ud-train.conllu",
    "ClassicalArmenian": "UD_Classical_Armenian-CAVaL/master/xcl_caval-ud-train.conllu",
    "Coptic": "UD_Coptic-Scriptorium/master/cop_scriptorium-ud-train.conllu",
    "BiblicalHebrew": "UD_Ancient_Hebrew-PTNK/master/hbo_ptnk-ud-train.conllu",
    "MiddleFrench": "UD_Middle_French-PROFITEROLE/master/frm_profiterole-ud-train.conllu",
    "LatinAquinas": "UD_Latin-ITTB/master/la_ittb-ud-train.conllu",
    "Persian": "UD_Persian-PerDT/master/fa_perdt-ud-train.conllu",
    "Welsh": "UD_Welsh-CCG/master/cy_ccg-ud-train.conllu",
    "Irish": "UD_Irish-IDT/master/ga_idt-ud-train.conllu",
    "Maltese": "UD_Maltese-MUDT/master/mt_mudt-ud-train.conllu",
}
# Lexicons built from files the lab already has (no download needed).
LOCAL_SOURCES = {
    **{lang: ("bible", lang) for lang in corpus.BIBLE_LANGUAGES},
    "MedievalLatin": ("medieval", None), "VulgarLatin": ("extra", "egeria"),
    "OldFrench": ("extra", "old_french"), "BasqueNews": ("extra", "basque_news"),
}
# Which group a language belongs to, for the report.
GROUPS = {
    "romański": ["Latin", "MedievalLatin", "LatinAquinas", "VulgarLatin", "Italian", "Spanish", "Portuguese", "French",
                 "OldFrench", "MiddleFrench", "Romanian"],
    "germański": ["German", "Dutch", "English", "Danish", "Swedish", "Norwegian", "Icelandic", "Gothic", "Afrikaans"],
    "słowiański i bałtycki": ["Polish", "Czech", "Slovak", "Slovene", "Croatian", "Serbian", "Bulgarian", "Russian",
                              "OldChurchSlavonic", "OldEastSlavic", "Lithuanian"],
    "celtycki": ["Welsh", "Irish"],
    "grecki, ormiański, albański": ["Greek", "AncientGreek", "ClassicalArmenian", "Albanian"],
    "semicki i koptyjski": ["Hebrew", "BiblicalHebrew", "Arabic", "Maltese", "Amharic", "Coptic"],
    "uralski, turecki, baskijski, perski": ["Hungarian", "Finnish", "Turkish", "Basque", "BasqueNews", "Persian"],
    "inne": ["Hindi", "Vietnamese"],
}


def normalize(word: str) -> str:
    w = unicodedata.normalize("NFKD", word.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    return "".join(c for c in w if c.isalpha())


def build(words: list[str]) -> Counter:
    c = Counter()
    for w in words:
        n = normalize(w)
        if 1 <= len(n) <= MAX_LEN:
            c[n] += 1
    return c


def save(name: str, counts: Counter, bigrams: Counter | None = None) -> Path:
    LEXICON_DIR.mkdir(parents=True, exist_ok=True)
    path = LEXICON_DIR / f"{name}.txt"
    lines = [f"{w}\t{n}" for w, n in counts.most_common()]
    if bigrams:
        lines += [f"{a} {b}\t{n}" for (a, b), n in bigrams.most_common(200_000)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load(name: str) -> tuple[Counter, Counter]:
    """(word counts, bigram counts) of a saved lexicon."""
    path = LEXICON_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing - run: python scripts/fetch_lexicons.py")
    words, bigrams = Counter(), Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        key, _, n = line.rpartition("\t")
        if " " in key:
            a, b = key.split(" ", 1)
            bigrams[(a, b)] = int(n)
        elif key:
            words[key] = int(n)
    return words, bigrams


def available() -> list[str]:
    return sorted(p.stem for p in LEXICON_DIR.glob("*.txt")) if LEXICON_DIR.exists() else []


def local_words(name: str) -> list[str]:
    kind, arg = LOCAL_SOURCES[name]
    if kind == "bible":
        return corpus.load_reference(arg)
    if kind == "medieval":
        return [w for m in corpus.medieval_texts() for w in corpus.load_medieval(m)]
    return corpus.load_extra(arg)


def build_from_text(name: str, words: list[str]) -> Path:
    """Save a lexicon with word and bigram counts from running text."""
    norm = [normalize(w) for w in words]
    norm = [w for w in norm if 1 <= len(w) <= MAX_LEN]
    return save(name, Counter(norm), Counter(zip(norm, norm[1:])))
