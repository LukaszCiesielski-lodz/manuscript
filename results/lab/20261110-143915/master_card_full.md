# master_card_full: potwierdzona

**Hipoteza.** Istnieje mała karta matka, z której da się złożyć każde słowo rękopisu (100%), znacznie mniejsza niż dla języka.

**Metoda.** Karta pełna (6 kolumn, wszystkie kawałki n ≤ 3 we wszystkich kolumnach) składa 100% słów. 256 kart przycina ją naraz, każda w swojej kolejności (połowa losowo, połowa najpierw rzadkie i długie kawałki): wpis znika, gdy bez niego nadal składa się cel (100% i 99% tokenów). Najmniejszą kartę zmniejsza dalej ewolucja (populacja 256, 100 pokoleń na rundę, do 40 rund) pod budżetem o jeden wpis mniejszym. cupy/GPU. Te same kroki dla łaciny, włoskiego, bełkotu v7, rękopisu z glifami przetasowanymi w słowie i tekstu pisanego znaną kartą 40 wpisów (kontrola).

Każde słowo rękopisu da się złożyć z karty 242 wpisów (99% słów: 132); łacina potrzebuje 639, włoski 556, rękopis z przetasowanymi glifami 563, bełkot v7 211.

## Kontrole

- ✅ **tekst pisany kartą 40 wpisów: znaleziona karta na 100%**: oczekiwano ≤ 80 wpisów; wynik: 40 wpisów

## Dowody

- Najmniejsza karta (wpisy; cel 100% / 99% tokenów, w nawiasie osiągalny sufit): rękopis: 242 / 132; syntetyczny (karta 40 wpisów): 40 / 40; łacina: 639 / 562; włoski: 556 (1.000) / 422; v7: 211 / 125; przetasowany w słowie: 563 / 355.

## Zastrzeżenia

- Wpisy potrzebne tylko dla jednego słowa (hapaksu) też liczą się do karty; 99% to miara odporniejsza na pojedyncze dziwne słowa.
- Przycinanie i ewolucja znajdują małą kartę, nie dowodzą, że mniejszej nie ma.

## Literatura

- Stolfi, crust–mantle–core paradigm of Voynichese words
- Rugg, Cryptologia 28 (2004)

_Czas: 27671 s · 2026-11-10 22:20_