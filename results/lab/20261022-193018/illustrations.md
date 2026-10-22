# illustrations: metoda niewiarygodna

**Hipoteza.** Klucz do tekstu kryje się w ilustracjach: tekst zależy od rysunków (np. pierwsze słowo strony zielnika to zaszyfrowana nazwa rośliny).

**Metoda.** A: długość słów przy przerwach na rysunek (test permutacyjny). B: test Mantela – podobieństwo obrazów CLIP a podobieństwo słownictwa stron zielnika, permutacje w obrębie skryby i języka Curriera. C: atak z nazwami roślin od modelu wizyjnego jako 'cribami' (wyżarzanie klucza glif→litera) wobec nazw przetasowanych.

Test sprawdza warunek konieczny klucza w ilustracjach: czy tekst w ogóle zależy od rysunku. C (powtórka na 103 nowych stronach, nazwy od qwen/qwen2.5-vl-72b-instruct): dopasowanie 0.29 wobec średnio 0.27 dla nazw przetasowanych, p = 0.260. Wcześniej na 20 stronach f1v–f11r: 0,40 wobec 0,33, p = 0,04. B: 123 stron zielnika. Korelacja podobieństwa obrazów i słownictwa r = 0.084, p = 0.0528 (permutacje w obrębie skryby i języka).

## Kontrole

- ✅ **A: podłożone skrócenie słów przed rysunkiem**: oczekiwano wykryte (p < 0,01); wynik: p = 0.0003
- ✅ **C: nazwy podłożone znanym kluczem**: oczekiwano atak je znajduje (p ≤ 0,05); wynik: wynik 0.47 wobec 0.17 (max dla przetasowanych), p = 0.020
- ✅ **B: połowy tekstu tej samej strony**: oczekiwano zgodne (p < 0,01); wynik: r = 0.30, p = 0.0002
- ❌ **B: losowe podobieństwa obrazów**: oczekiwano brak związku (p > 0,05); wynik: p = 0.025

## Dowody

- A: 613 wierszy przerwanych rysunkiem. Słowo przed rysunkiem różni się długością o -0.24 glifu od słów w środku wiersza, p = 0.0003.
- C (powtórka na 103 nowych stronach, nazwy od qwen/qwen2.5-vl-72b-instruct): dopasowanie 0.29 wobec średnio 0.27 dla nazw przetasowanych, p = 0.260. Wcześniej na 20 stronach f1v–f11r: 0,40 wobec 0,33, p = 0,04.
- B: 123 stron zielnika. Korelacja podobieństwa obrazów i słownictwa r = 0.084, p = 0.0528 (permutacje w obrębie skryby i języka).

## Zastrzeżenia

- Związek tekstu z rysunkiem (B) byłby warunkiem koniecznym, ale nie dowodem klucza: tekst o roślinie też zależy od rośliny.
- Identyfikacje roślin przez model wizyjny są niepewne; botanicy nie zgadzają się co do większości roślin rękopisu.
- Atak C zakłada, że pierwsze słowo strony to nazwa rośliny zapisana szyfrem podstawieniowym od początku słowa.
- CLIP widzi całą stronę razem z pismem; podobny układ tekstu może podbijać podobieństwo obrazów.

## Rada modeli

## Werdykt rady

**Brak wiarygodnego wsparcia dla hipotezy, że ilustracje zawierają klucz do tekstu.** Zgodność opinii jest wysoka: rada zgadza się, że test B nie przechodzi kontroli, a test C nie potwierdził wcześniejszego wyniku. Nie oznacza to jednak, że wszystkie składowe metody są niewiarygodne: kontrole A i C przeszły.

## Co test naprawdę pokazuje

Test A wykrył krótsze słowa przy przerwach na rysunki (różnica −0,24 glifu; p = 0,0003), ale świadczy to o związku z układem strony, nie o zaszyfrowanej treści. Test B uzyskał słabą, graniczną korelację (r = 0,084; p = 0,0528), lecz kontrola z losowymi podobieństwami obrazów dała p = 0,025, mimo oczekiwanego braku związku. Wyniku B nie należy więc traktować jako wiarygodnego dowodu. Test C wykrył celowo podłożony klucz, ale w powtórce na 103 stronach nie wykazał przewagi nad nazwami przetasowanymi (p = 0,260).

Wyniki osłabiają wąską hipotezę testowaną przez C, ale **nie wykluczają** innych form zależności tekstu od ilustracji ani innych typów klucza.

## Główne zastrzeżenia i następny eksperyment

Identyfikacje roślin są niepewne, C opiera się na założeniu dotyczącym pierwszego słowa, a CLIP w B analizował także pismo i układ strony. Najbardziej rozstrzygająca byłaby niezależna powtórka testu B z CLIP analizującym wyłącznie zamaskowane rysunki oraz z kontrolami losowymi, które nie generują fałszywej korelacji.

## Literatura

- Subtle Signs of Scribal Intent in the Voynich Manuscript, arXiv:2404.13069
- Topic Modeling in the Voynich Manuscript, arXiv:2107.02858
- A Generative Grammar Underlying the Voynich Manuscript (pastiche hypothesis), arXiv:2609.20835
- Bax, A proposed partial decoding of the Voynich script (2014)

_Czas: 1283 s · 2026-10-22 19:57_