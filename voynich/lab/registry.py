"""All theories the lab can test. Add a new one by writing run(cfg) -> TheoryResult and listing it here."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Theory:
    name: str
    title: str
    needs: tuple[str, ...]  # "gpu", "images", "openrouter": what makes the full test possible
    runner: str             # "module:function"

    def load(self) -> Callable:
        import importlib
        importlib.invalidate_caches()   # files pulled into the package after the first import must still be found
        mod, fn = self.runner.split(":")
        return getattr(importlib.import_module(f"voynich.lab.theories.{mod}"), fn)


THEORIES = {t.name: t for t in [
    Theory("numbers", "Znaki to liczby", (), "numbers:run"),
    Theory("illustrations", "Klucz w ilustracjach", ("gpu", "images", "openrouter"), "illustrations:run"),
    Theory("generative", "AI generuje brakujące strony", ("gpu",), "generative:run"),
    Theory("naibbe_cipher", "Szyfr Naibbe (Greshko 2025)", (), "literature:run_naibbe"),
    Theory("cardan_grille", "Bełkot z kratki Cardana (Rugg 2004)", (), "literature:run_grille"),
    Theory("hebrew_anagram", "Hebrajskie anagramy (Hauer i Kondrak 2016)", (), "literature:run_hebrew_anagram"),
    Theory("basque", "Baskijski pod szyfrem podstawieniowym", (), "basque:run"),
    Theory("nomenclator", "Nomenklator: słowo = kod z księgi", (), "nomenclator:run"),
    Theory("hoax", "Tekst bez treści z reguł skryby", (), "hoax:run"),
    Theory("syntax", "Daleka składnia: zależności między różnymi słowami", (), "syntax:run"),
    Theory("romance", "Język (proto)romański", (), "romance:run"),
    Theory("lengths", "Słowa jako liczby: dynamika długości słów", (), "lengths:run"),
    Theory("brute", "Brute force: trójki słów pod jednym kluczem w językach epoki", ("gpu",), "brute:run"),
    Theory("wheel", "Tarcza Lullusa (volvelle) jako urządzenie piszące", ("gpu",), "wheel:run"),
    Theory("adversary", "Transformer-sędzia: prawdziwe vs wygenerowane", ("gpu",), "adversary:run"),
    Theory("genres", "Gatunki średniowieczne bez składni: litania, imiona magiczne", (), "genres:run"),
    Theory("transcriptions", "Podpis rękopisu w innych transliteracjach", (), "transcriptions:run"),
    Theory("cognate", "Dopasowanie form słów do języka (NeuroDecipher)", ("gpu",), "cognate:run"),
    Theory("hillclimb", "Atak homofoniczny: wspinaczka z modelem n-gramowym", ("gpu",), "hillclimb:run"),
    Theory("phonotactics", "Budowa słów jak w mowie: samogłoski Suchotina i wzorce C/V", (), "phonotactics:run"),
]}
ALIASES = {"literature": ["naibbe_cipher", "cardan_grille", "hebrew_anagram"], "all": list(THEORIES)}


def expand(names: list[str]) -> list[str]:
    out = []
    for n in names:
        for m in ALIASES.get(n, [n]):
            if m not in THEORIES:
                raise KeyError(f"nieznana teoria: {m}; dostępne: {', '.join(THEORIES)}")
            if m not in out:
                out.append(m)
    return out
