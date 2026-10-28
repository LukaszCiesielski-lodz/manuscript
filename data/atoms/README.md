# Atomy ilustracji

Rozbieramy rysunki na atomy: jeden rekord na jedną narysowaną rzecz, przypięty do etykiety (słowa) napisanej obok.
Jest 853 etykiet (1014 słów) na 51 stronach. Cel: sprawdzić, czy jakaś cecha rysunku przewiduje coś w etykiecie (pierwszy glif, długość, końcówkę). Jeśli rebus
istnieje, siedzi właśnie w parach rysunek–etykieta: akapity nie cytują etykiet swojej strony, a strony z tą samą rośliną
nie dzielą słów (testy `labels` i `plant_pairs`).

## Zasady

1. **Tylko to, co widać.** „kwiat, 5 płatków, niebieski” tak; „szałwia” nie. Interpretację wpisz w `uwaga`.
2. **Każdy atom ma etykietę.** Pliki są wygenerowane z transliteracji: jeden atom na jedno słowo-etykietę (loci `L*`),
   słowa już wpisane. Ty wypełniasz tylko `cechy`, `pozycja.krag`, `zrodlo`, `pewnosc`.
3. **Wartości tylko ze słownika** `vocab.json` (`true`/`false`, liczba albo jedno z dozwolonych słów). `null` = nie wiem / nie dotyczy.
4. **`zrodlo` = Twoje imię, `pewnosc`** 1 (zgaduję), 2 (raczej tak), 3 (pewne). Dwie osoby na tej samej stronie to nie
   marnotrawstwo: zgodność dwóch osób (kappa) mówi, czy cecha w ogóle jest obiektywna. Cechy o kappa < 0,6 nie wchodzą do testu.
5. **Kolejność: zodiak → farmacja → zielnik.** Zodiak jest najbardziej regularny (nimfa, gwiazda, etykieta; 294 etykiety na
   12 stronach). W zielniku atomy są najbardziej uznaniowe.

## Rekord

```json
{"id": "f70v2-07", "typ": "nimfa",
 "cechy": {"naga": true, "w_obiekcie": "nic", "korona": false, "wlosy": "rozpuszczone", "trzyma": "gwiazda",
           "kierunek": "lewo", "gwiazda_promienie": 8, "gwiazda_ogon": true, "gwiazda_kolor": "czerwony"},
 "pozycja": {"krag": "zewn", "kolejnosc": 7},
 "etykieta": {"locus": "8", "rodzaj": "Lz", "slowa": ["okala"]},
 "zrodlo": "Marek", "pewnosc": 2, "uwaga": ""}
```

`pozycja.kolejnosc` to kolejność etykiety w transliteracji (ZL), na ogół zgodna z kolejnością nimf w kręgu, ale zodiak ma
krąg zewnętrzny i wewnętrzny: wpisz `krag` (`zewn`, `srod`, `wewn`). Jeśli etykieta nie pasuje do żadnej nimfy albo nimfa nie
ma etykiety, napisz to w `uwaga`; atom bez etykiety można dodać z `"etykieta": null`.

Typ domyślny wynika z rodzaju locus: `Lz`, `Ln` → nimfa; `Ls` → gwiazda; `Lc` → naczynie; `Lf` → fragment; `Lt` → rura;
`L0` → obiekt. Jeśli to coś innego (np. w zodiaku zwierzę w środku), zmień `typ` na inny ze słownika.

## Skąd obrazy

Skany: Beinecke (collections.library.yale.edu, MS 408) albo archive.org/details/voynich. Nazwy stron jak w transliteracji:
`f70v2` to drugi panel rozkładanej karty 70v. Zodiak: f70v1 Ryby, f70v2 Baran (ciemny), f71r Baran (jasny), f71v Byk (jasny),
f72r1 Byk (ciemny), f72r2 Bliźnięta, f72r3 Rak, f72v3 Lew, f72v2 Panna, f72v1 Waga, f73r Skorpion, f73v Strzelec.

## Szkic z modelu widzącego

Notebook `colab/Voynich_Atomy.ipynb` prosi model widzący obrazy o pierwszy, brudny opis stron zodiaku w tym samym schemacie
(`zrodlo: "vlm"`, `pewnosc: 1`). Liczby po modelu (promienie, płatki) są niepewne: to szkic do poprawienia, nie wynik.

## Sprawdzenie i test

```
python scripts/make_atoms.py          # dopisuje brakujące szablony stron, nie nadpisuje wypełnionych
python -m voynich.lab.runner --theories atoms --no-council   # test rebusu z kontrolami
```

Test (`atoms`): dla każdej pary (cecha rysunku, cecha etykiety) informacja wzajemna wobec etykiet przetasowanych w obrębie
strony, z poprawką na liczbę par. Kontrole: pierwszy glif etykiety podłożony według cechy (musi być wykryty) i cechy
przetasowane między atomami strony (nie może być). Test rusza przy ≥ 100 wypełnionych atomach z etykietą.
