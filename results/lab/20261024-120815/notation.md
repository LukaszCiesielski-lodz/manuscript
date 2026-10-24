# notation: obalona

**Hipoteza.** Rękopis jest zapisem niejęzykowym (melodia, kroki, procedura): jego statystyka przypomina notacje średniowieczne bardziej niż mowę.

**Metoda.** Chorał gregoriański z bazy Cantus (Volpiano, jednostki: słowa tekstu, sylaby, neumy), tabulatura basse danse (Bruksela 9085), kod Pythona jako kontrast, łacina i bełkot v5; każdy tekst przycięty do liczby słów rękopisu. Zależność na odległość rozbita na powtórzenia, warianty i jednostki niespokrewnione; dynamika długości jednostek; miary kształtu jako z wobec rozrzutu bloków rękopisu. Osiem kryteriów podpisu rękopisu; cecha definiująca: brak zależności między różnymi jednostkami na odległość 2–7.

Kryteria podpisu rękopisu spełnione: chorał: słowa tekstu 6/8, bełkot v5 6/8, chorał: sylaby 5/8, chorał: neumy 5/8, kod Python 4/8, łacina 1/8. Chorał i kod mają silną składnię na odległość (niespokrewnione jednostki z = 65, 132, 145), której rękopis nie ma (z = -1.2); dzielą z nim za to dynamikę długości (dodatnia korelacja sąsiadów, DFA powyżej języków).

## Kontrole


## Dowody

- Basse danse: tylko 146 kroków w dostępnej próbce, za mało na miary; pełne wydanie pobiera scripts/fetch_notation.py, gdy jest dostępne.
- rękopis (34820 jednostek, 33 znaków): powtórzenia z = 9.6, warianty z = 5.1, niespokrewnione z = -1.2; długości: korelacja sąsiadów +0.16, DFA 0.60; kształt wobec rękopisu: entropia warunkowa h₂ +0.8, różne słowa / wszystkie +0.0, słowa użyte raz (hapaksy) +0.4, sąsiednie słowa różne o 1 glif +1.5, sztywne miejsca glifów w słowie -1.1. Kryteria podpisu: 8/8.
- chorał: słowa tekstu (34830 jednostek, 19 znaków): powtórzenia z = 1.4, warianty z = 9.0, niespokrewnione z = 65.3; długości: korelacja sąsiadów +0.17, DFA 0.67; kształt wobec rękopisu: entropia warunkowa h₂ +1.4, różne słowa / wszystkie -0.2, słowa użyte raz (hapaksy) -2.9, sąsiednie słowa różne o 1 glif -0.2, sztywne miejsca glifów w słowie -5.8. Kryteria podpisu: 6/8, w tym BRAK cechy definiującej (składnia na odległość).
- chorał: sylaby (34848 jednostek, 19 znaków): powtórzenia z = 46.7, warianty z = 13.9, niespokrewnione z = 131.5; długości: korelacja sąsiadów +0.12, DFA 0.71; kształt wobec rękopisu: entropia warunkowa h₂ +0.8, różne słowa / wszystkie -4.3, słowa użyte raz (hapaksy) -4.0, sąsiednie słowa różne o 1 glif +36.1, sztywne miejsca glifów w słowie -16.5. Kryteria podpisu: 5/8, w tym BRAK cechy definiującej (składnia na odległość).
- chorał: neumy (34843 jednostek, 19 znaków): powtórzenia z = 46.0, warianty z = 32.5, niespokrewnione z = 144.7; długości: korelacja sąsiadów +0.23, DFA 0.71; kształt wobec rękopisu: entropia warunkowa h₂ +0.5, różne słowa / wszystkie -4.8, słowa użyte raz (hapaksy) -7.4, sąsiednie słowa różne o 1 glif +38.1, sztywne miejsca glifów w słowie -18.2. Kryteria podpisu: 5/8, w tym BRAK cechy definiującej (składnia na odległość).
- kod Python (34826 jednostek, 37 znaków): powtórzenia z = 48.9, warianty z = 1.6, niespokrewnione z = 137.4; długości: korelacja sąsiadów +0.10, DFA 0.68; kształt wobec rękopisu: entropia warunkowa h₂ +7.4, różne słowa / wszystkie -2.5, słowa użyte raz (hapaksy) -10.4, sąsiednie słowa różne o 1 glif +1.6, sztywne miejsca glifów w słowie -7.1. Kryteria podpisu: 4/8, w tym BRAK cechy definiującej (składnia na odległość).
- łacina (34821 jednostek, 23 znaków): powtórzenia z = -0.5, warianty z = 1.4, niespokrewnione z = 12.7; długości: korelacja sąsiadów -0.11, DFA 0.52; kształt wobec rękopisu: entropia warunkowa h₂ +5.9, różne słowa / wszystkie -1.0, słowa użyte raz (hapaksy) -4.7, sąsiednie słowa różne o 1 glif -4.5, sztywne miejsca glifów w słowie -5.0. Kryteria podpisu: 1/8, w tym BRAK cechy definiującej (składnia na odległość).
- bełkot v5 (17460 jednostek, 31 znaków): powtórzenia z = 0.4, warianty z = 1.6, niespokrewnione z = 0.8; długości: korelacja sąsiadów +0.15, DFA 0.57; kształt wobec rękopisu: entropia warunkowa h₂ +0.2, różne słowa / wszystkie -0.7, słowa użyte raz (hapaksy) -1.3, sąsiednie słowa różne o 1 glif -0.0, sztywne miejsca glifów w słowie -0.6. Kryteria podpisu: 6/8.

## Zastrzeżenia

- Jednostki chorału zależą od poziomu podziału (słowo, sylaba, neuma); policzono wszystkie trzy.
- Tabulatura basse danse w dostępnej próbce jest za krótka; pełne wydanie (59 tańców) wymaga pobrania PDF.
- Melodie w Volpiano to wysokości bezwzględne; zapis interwałowy mógłby dać inny obraz powtórzeń.

## Rada modeli

## Werdykt rady
**Hipoteza nierozstrzygnięta; test niewiarygodny w obecnej postaci.** Zgodność rady jest wysoka: wszyscy oceniający w rundzie 2 odrzucają automatyczne „obalona” jako nieuzasadnione bez wymaganych kontroli.

## Co test naprawdę pokazuje
Warunkowo, jeśli metoda działa poprawnie, rękopis różni się od badanego chorału w kluczowej mierze: zależność dla niespokrewnionych jednostek wynosi **z = −1,2**, wobec **z = 65–145** dla chorału zależnie od segmentacji. Jednocześnie część miar długości jest podobna. Podpis rękopisu spełnia też bełkot v5 (**6/8 kryteriów**), co ogranicza swoistość tego zestawu cech.

To są wyniki dotyczące zbadanych danych, nie dowód przeciwko wszystkim rodzajom zapisu niejęzykowego. Test nie rozstrzyga, czym jest rękopis.

## Główne zastrzeżenia
Raport nie podaje wyników kontroli wymaganych do uznania metody za wiarygodną: wykrycia efektu podłożonego celowo oraz braku efektu w danych przetasowanych. Ponadto basse danse nie została miarodajnie zbadana (146 kroków), wyniki chorału zależą od segmentacji, a nie sprawdzono zapisu interwałowego.

## Następny eksperyment
Przeprowadzić walidację tej samej, ustalonej z góry procedury: wykazać, że wykrywa celowo podłożony efekt i nie wykrywa go po przetasowaniu danych.

## Literatura

- Cornelissen, Zuidema & Burgoyne, Mode classification and natural units in plainchant, ISMIR 2020 (CantusCorpus)
- Brussels, KBR ms. 9085, Les basses danses de Marguerite d'Autriche (c. 1470)
- Crane, Materials for the study of the fifteenth century basse danse (1968)

_Czas: 357 s · 2026-10-24 12:17_