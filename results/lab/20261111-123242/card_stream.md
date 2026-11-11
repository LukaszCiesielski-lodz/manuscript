# card_stream: obalona

**Hipoteza.** Jedno słowo rękopisu to jedna litera tekstu jawnego: literę niesie wybór z jednej kolumny karty matki (albo para wyborów z dwóch kolumn), reszta słowa to wypełniacz.

**Metoda.** Karta matka 242 wpisów (GPU, składa 100% słów) rozbija każde słowo na wybory w 6 kolumnach; każda kolumna i każda para kolumn daje strumień symboli, jeden na słowo (21 strumieni). Etap 1: ile symbol mówi o następnym symbolu wiersza ponad to samo po przetasowaniu słów w wierszach (100 tasowań). Etap 2: łamacz homofoniczny (64 kluczy, 12 przejść po symbolach: dla symbolu wszystkie litery naraz; model 4-gramowy liter bez spacji, cuda) na 6 strumieniach z największym nadmiarem, w językach: Latin, Italian, German; klucz z co drugiego wiersza, ocena na pozostałych (bity na symbol); rękopis wobec rękopisu ze słowami przetasowanymi w wierszach. Kontrole: litery prawdziwego tekstu ukryte w tych samych strumieniach (te same symbole, częstości i długości wierszy, kilka symboli na częstą literę).

Żaden strumień wyborów z karty nie niesie tekstu litera po literze. Pamięć najlepszego strumienia to 0.049 bitu (k1+k3) wobec 0.40 bitu dla ukrytej łaciny. Łamacz, który czyta ukryty tekst (18 par język–strumień z działającą kontrolą), z rękopisu wyciąga ciąg o co najmniej 2.6 bitu na symbol gorszy niż język; kolejność słów pomaga mu najwyżej o +0.34 bitu, tyle co znany nawyk na styku słów.

## Kontrole

- ✅ **litery łaciny ukryte w kolumnie 3 i w parze kolumn 3+4: pamięć strumienia**: oczekiwano nadmiar ≥ 0,2 bitu i z ≥ 10 w obu; wynik: k3: 0.51 bitu (z = 251); k3+k4: 0.40 bitu (z = 98)
- ✅ **łamacz czyta tekst ukryty w strumieniu (trafność klucza ≥ 50%)**: oczekiwano co najmniej jeden strumień w każdym języku; wynik: Latin: k1+k3 100%, k1+k6 100%, k1+k2 100%, k1 100%, k2+k3 100%, k1+k5 100%; Italian: k1+k3 99%, k1+k6 100%, k1+k2 100%, k1 100%, k2+k3 100%, k1+k5 100%; German: k1+k3 99%, k1+k6 100%, k1+k2 100%, k1 100%, k2+k3 100%, k1+k5 100%

## Dowody

- Pamięć strumieni rękopisu (bity, które symbol mówi o następnym, ponad tasowanie; od największej): k1+k3 0.049 (z = 11, 817 symboli); k1+k6 0.045 (z = 12, 530 symboli); k1+k2 0.041 (z = 9, 602 symboli); k1 0.031 (z = 22, 34 symboli); k2+k3 0.022 (z = 4, 707 symboli); k1+k5 0.020 (z = 5, 609 symboli); k3+k6 0.019 (z = 6, 475 symboli); k2 0.017 (z = 10, 43 symboli); najsłabszy k2+k4 -0.006. Ukryty tekst łaciński: k3 0.51, k3+k4 0.40.
- Odczyt strumienia k1+k3 najlepszym kluczem (Latin), pierwsze wiersze: ?isttteieresiieno?ccivsiiec?iciiadeaeianipe?itaeta?teiaaceeiinineaticiins?inma?reeteaa?a
- Latin (bity na symbol; kontrola = trafność klucza na ukrytym tekście): k1+k3: kontrola 100%, rękopis 5.81, przetasowany 5.94, zysk +0.12, naturalny 3.14; k1+k6: kontrola 100%, rękopis 5.74, przetasowany 5.93, zysk +0.19, naturalny 3.14; k1+k2: kontrola 100%, rękopis 5.85, przetasowany 5.97, zysk +0.11, naturalny 3.14; k1: kontrola 100%, rękopis 5.79, przetasowany 5.76, zysk -0.02, naturalny 3.14; k2+k3: kontrola 100%, rękopis 5.81, przetasowany 5.95, zysk +0.15, naturalny 3.14; k1+k5: kontrola 100%, rękopis 5.71, przetasowany 5.87, zysk +0.15, naturalny 3.14.
- Italian (bity na symbol; kontrola = trafność klucza na ukrytym tekście): k1+k3: kontrola 99%, rękopis 6.38, przetasowany 6.64, zysk +0.26, naturalny 3.19; k1+k6: kontrola 100%, rękopis 6.29, przetasowany 6.63, zysk +0.34, naturalny 3.19; k1+k2: kontrola 100%, rękopis 6.41, przetasowany 6.61, zysk +0.20, naturalny 3.19; k1: kontrola 100%, rękopis 6.32, przetasowany 6.54, zysk +0.22, naturalny 3.19; k2+k3: kontrola 100%, rękopis 6.45, przetasowany 6.62, zysk +0.17, naturalny 3.19; k1+k5: kontrola 100%, rękopis 6.34, przetasowany 6.62, zysk +0.28, naturalny 3.19.
- German (bity na symbol; kontrola = trafność klucza na ukrytym tekście): k1+k3: kontrola 99%, rękopis 6.39, przetasowany 6.60, zysk +0.20, naturalny 3.04; k1+k6: kontrola 100%, rękopis 6.35, przetasowany 6.11, zysk -0.24, naturalny 3.04; k1+k2: kontrola 100%, rękopis 6.39, przetasowany 6.43, zysk +0.04, naturalny 3.04; k1: kontrola 100%, rękopis 5.89, przetasowany 5.85, zysk -0.04, naturalny 3.04; k2+k3: kontrola 100%, rękopis 6.16, przetasowany 6.26, zysk +0.11, naturalny 3.04; k1+k5: kontrola 100%, rękopis 6.08, przetasowany 6.26, zysk +0.18, naturalny 3.04.

## Zastrzeżenia

- Sprawdzone: litera w jednej kolumnie albo w parze kolumn, jedno słowo = jedna litera. Nie sprawdzone: litera rozłożona na trzy i więcej kolumn, litera jako całe słowo z wieloma zamiennikami (szyfr Naibbe), słowa-wypełniacze między literami.
- Pominięcie kolumny liczy się jako symbol; jeśli słowa bez wpisu w danej kolumnie były pustymi znakami, łamacz dostaje tekst z wtrąceniami i traci część sygnału.
- Strumienie par kolumn mają po kilkaset symboli; łamacz bierze pod uwagę tylko symbole z co najmniej 10 wystąpieniami.

## Rada modeli

## Werdykt rady

**Obalona w zakresie sprawdzonej hipotezy:** jedna litera na słowo, kodowana wyborem z jednej lub dwóch kolumn. Poziom zgody jest **pełny**; oceny niezależne były zgodne co do werdyktu i głównych ograniczeń.

## Co test naprawdę pokazuje

Kontrole metody przeszły: podłożony tekst dał nadmiar pamięci 0,40–0,51 bitu, a łamacz odzyskiwał go z trafnością bliską 100%. W rękopisie najlepszy strumień osiągnął 0,049 bitu (k1+k3), a wyniki łamacza pozostały o co najmniej 2,6 bitu na symbol gorsze od języka naturalnego. Niewielka poprawa względem danych przetasowanych (do 0,34 bitu) nie stanowi porównywalnego sygnału tekstu.

## Główne zastrzeżenia

Wynik nie rozstrzyga wariantów niebadanych: kodowania przez co najmniej trzy kolumny, szyfru Naibbe ani słów-wypełniaczy. Brak wpisu w kolumnie potraktowano jako symbol, co mogłoby osłabić wykrywalność. Łamacz objął tylko sześć wybranych strumieni; raport nie podaje też korekty niepewności za wybór spośród wielu strumieni.

## Rekomendowany następny eksperyment

Przetestować **wariant Naibbe na całych słowach**, z kontrolnym tekstem ukrytym według tego samego schematu i porównaniem z danymi przetasowanymi.

## Literatura

- Greshko, Cryptologia (2025): the Naibbe cipher
- Nuhn, Schamper & Ney, ACL 2013
- Van Eycke, AZdecrypt

_Czas: 272 s · 2026-11-11 12:41_