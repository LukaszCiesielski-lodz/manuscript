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
        import importlib.util
        import sys
        from pathlib import Path
        importlib.invalidate_caches()   # files pulled into the package after the first import must still be found
        mod, fn = self.runner.split(":")
        name = f"voynich.lab.theories.{mod}"
        try:
            return getattr(importlib.import_module(name), fn)
        except ModuleNotFoundError as exc:
            if exc.name != name:
                raise
            # The importer's directory cache can be stale in a long-lived notebook kernel: load from the file itself.
            path = Path(__file__).with_name("theories") / f"{mod}.py"
            if not path.exists():
                raise ModuleNotFoundError(f"{path} nie istnieje; w katalogu: "
                                          + ", ".join(sorted(p.name for p in path.parent.glob("*.py")))) from exc
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            return getattr(module, fn)


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
    Theory("length_code", "Kod w długościach słów", (), "length_code:run"),
    Theory("chronology", "Strzałka czasu: kolejność kart odczytana z wariantów słów", (), "chronology:run"),
    Theory("hands", "Ręka skryby czy treść: co kształtuje słowa", (), "hands:run"),
    Theory("notation", "Zapis niejęzykowy: chorał, tabulatura tańca, program", (), "notation:run"),
    Theory("labels", "Etykiety przy rysunkach jako nazwy, cytowane przez akapity", (), "labels:run"),
    Theory("records", "Wiersz jako rekord o polach", (), "records:run"),
    Theory("lists", "Podpis rękopisu wobec list średniowiecznych: martyrologium, Apicius, Alphita", (), "lists:run"),
    Theory("fields_lm", "Zysk z tokenów pozycji: czy słowo zależy od miejsca w wierszu (GPT)", ("gpu",), "fields_lm:run"),
    Theory("v6", "Generator v6: nawyki skryby ewoluowane na karcie, sędzia na GPU", ("gpu",), "v6:run"),
    Theory("cohesion", "Spójność strony: czy sędzia pozna dwa wiersze z tej samej strony", ("gpu",), "cohesion:run"),
]}
ALIASES = {"literature": ["naibbe_cipher", "cardan_grille", "hebrew_anagram"], "rejestr": ["labels", "records", "lists"],
           "rejestr_gpu": ["fields_lm", "v6", "cohesion"], "all": list(THEORIES)}


def expand(names: list[str]) -> list[str]:
    out = []
    for n in names:
        for m in ALIASES.get(n, [n]):
            if m not in THEORIES:
                raise KeyError(f"nieznana teoria: {m}; dostępne: {', '.join(THEORIES)}")
            if m not in out:
                out.append(m)
    return out
