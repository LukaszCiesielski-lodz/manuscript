# Voynich Lab – przebieg 20261022-193018

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Klucz w ilustracjach | metoda niewiarygodna | 3/4 | metoda niewiarygodna: 3 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Klucz w ilustracjach

Test sprawdza warunek konieczny klucza w ilustracjach: czy tekst w ogóle zależy od rysunku. C (powtórka na 103 nowych stronach, nazwy od qwen/qwen2.5-vl-72b-instruct): dopasowanie 0.29 wobec średnio 0.27 dla nazw przetasowanych, p = 0.260. Wcześniej na 20 stronach f1v–f11r: 0,40 wobec 0,33, p = 0,04. B: 123 stron zielnika. Korelacja podobieństwa obrazów i słownictwa r = 0.084, p = 0.0528 (permutacje w obrębie skryby i języka).

**Synteza rady:**

## Werdykt rady

**Brak wiarygodnego wsparcia dla hipotezy, że ilustracje zawierają klucz do tekstu.** Zgodność opinii jest wysoka: rada zgadza się, że test B nie przechodzi kontroli, a test C nie potwierdził wcześniejszego wyniku. Nie oznacza to jednak, że wszystkie składowe metody są niewiarygodne: kontrole A i C przeszły.

## Co test naprawdę pokazuje

Test A wykrył krótsze słowa przy przerwach na rysunki (różnica −0,24 glifu; p = 0,0003), ale świadczy to o związku z układem strony, nie o zaszyfrowanej treści. Test B uzyskał słabą, graniczną korelację (r = 0,084; p = 0,0528), lecz kontrola z losowymi podobieństwami obrazów dała p = 0,025, mimo oczekiwanego braku związku. Wyniku B nie należy więc traktować jako wiarygodnego dowodu. Test C wykrył celowo podłożony klucz, ale w powtórce na 103 stronach nie wykazał przewagi nad nazwami przetasowanymi (p = 0,260).

Wyniki osłabiają wąską hipotezę testowaną przez C, ale **nie wykluczają** innych form zależności tekstu od ilustracji ani innych typów klucza.

## Główne zastrzeżenia i następny eksperyment

Identyfikacje roślin są niepewne, C opiera się na założeniu dotyczącym pierwszego słowa, a CLIP w B analizował także pismo i układ strony. Najbardziej rozstrzygająca byłaby niezależna powtórka testu B z CLIP analizującym wyłącznie zamaskowane rysunki oraz z kontrolami losowymi, które nie generują fałszywej korelacji.

Szczegóły: [illustrations.md](illustrations.md)

Koszt OpenRouter: 0.22 USD w 143 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.