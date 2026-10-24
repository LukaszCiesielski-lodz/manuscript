# keystream: nierozstrzygnięta

**Hipoteza.** Odstępy nie dzielą słów: ciąg długości „słów” (w glifach albo w znakach EVA) jest kluczem zapisanym w tekście, a właściwe jednostki powstają po pocięciu, przesunięciu lub przeczytaniu strumienia glifów według tego klucza.

**Metoda.** Rodzina 31 przekształceń strumienia glifów wiersza: cięcie według długości przesuniętych o 1–3, odwróconych, z poprzedniego wiersza, pierwszego słowa, posortowanych, różnic; przesunięcie glifów w alfabecie o długość słowa, poprzedniego słowa, miejsce w słowie; czytanie co n-ty glif; cięcie co n glifów bez klucza. Dla każdego: jednostki rękopisu i bełkotu v5 mierzone zależnością między różnymi jednostkami na odległość 2–7 (z wobec tasowania w miejscu) i informacją wzajemną sąsiednich jednostek (z wobec tasowania w wierszu; 20 i 16 tasowań), a podział oceniany długością opisu (bity na glif: słownik jednostek plus tekst jako ich kody; prawdziwe słowa języka są blisko minimum). Trop: reguła kluczowana, która koduje rękopis krócej niż odstępy EVA (≥ 2%) i daje mu składnię (z ≥ 5), której nie daje bełkotowi (różnica ≥ 5). Kontrole: łacina z odstępami przepisanymi regułą z rodziny i łacina przeczytana kolumnami muszą zostać odzyskane jako minimum długości opisu; zwykła łacina i bełkot v5 nie mogą zyskać na żadnej regule.

Przy odstępach EVA: różne słowa na odległość z = -1.2, sąsiednie słowa z = -24.4 (v5 +10.9, v6 +1.5, łacina +46.6); długość opisu 3.896 bit/glif. Żadna z 25 reguł kluczowanych nie koduje rękopisu krócej niż odstępy EVA (najbliżej przesunięcie glifów o długość słowa (chars): 3.895) ani nie daje mu składni, której nie dawałaby bełkotowi (największa przewaga cięcie: długości posortowane (glyphs): +5.6). Odstępy EVA są najlepszym podziałem w tej rodzinie, a klucz w długościach słów nie odsłania jednostek z gramatyką.

## Kontrole

- ✅ **zwykła łacina: żadna reguła nie koduje jej krócej niż własne odstępy**: oczekiwano minimum długości opisu przy odstępach EVA (bez zmian); wynik: minimum: odstępy EVA (bez zmian) (3.452 bit/glif; bez zmian 3.452)
- ✅ **łacina zaszyfrowana (odstępy przepisane długościami przesuniętymi o 2): wyszukiwanie odzyskuje słowa**: oczekiwano minimum długości opisu przy regule odwrotnej, F1 granic ≥ 0,9; wynik: minimum: cięcie: długości przesunięte o 2 (glyphs) (3.452 bit/glif), F1 = 1.00; zaszyfrowana bez zmian 6.845
- ✅ **łacina zaszyfrowana (tekst przeczytany co 3. glif): wyszukiwanie odzyskuje słowa**: oczekiwano minimum długości opisu przy regule odwrotnej, F1 granic ≥ 0,9; wynik: minimum: czytanie co 3. glif w wierszu (transpozycja) (3.452 bit/glif), F1 = 1.00; zaszyfrowana bez zmian 7.482
- ✅ **bełkot v5 (pisany słowami): żadna reguła kluczowana nie koduje go krócej niż jego odstępy**: oczekiwano minimum przy odstępach; wynik: minimum: odstępy EVA (bez zmian) (3.473; odstępy 3.473)

## Dowody

- Przed przekształceniem, informacja wzajemna sąsiednich słów wobec tasowania w wierszu (z): rękopis -24.4, bełkot v5 +10.9, bełkot v6 +1.5, łacina +46.6; rękopis działami: text -7.0, herbal -10.8, stars -31.8, biological -7.8, pharmaceutical -7.7. Sąsiednie słowa rękopisu wiedzą o sobie MNIEJ niż dwa losowe słowa tej samej linii; bełkot v5 i łacina odwrotnie.
- przesunięcie glifów o długość słowa (chars): długość opisu 3.895 bit/glif (odstępy EVA 3.896; v5 3.473 wobec 3.473); rękopis niespokrewnione z = -1.8, bełkot v5 +2.3, łacina +12.7; sąsiedzi z = -24.4 (v5 +10.8); jednostek 34820, typów 7014.
- przesunięcie glifów o długość słowa (glyphs): długość opisu 3.896 bit/glif (odstępy EVA 3.896; v5 3.473 wobec 3.473); rękopis niespokrewnione z = -1.8, bełkot v5 +2.3, łacina +12.7; sąsiedzi z = -24.4 (v5 +10.9); jednostek 34820, typów 7018.
- przesunięcie glifów o miejsce w słowie: długość opisu 3.896 bit/glif (odstępy EVA 3.896; v5 3.473 wobec 3.473); rękopis niespokrewnione z = -1.8, bełkot v5 +2.2, łacina +12.6; sąsiedzi z = -24.4 (v5 +10.9); jednostek 34820, typów 7018.
- cięcie: różnice długości (glyphs): długość opisu 5.083 bit/glif (odstępy EVA 3.896; v5 4.890 wobec 3.473); rękopis niespokrewnione z = +3.9, bełkot v5 +3.7, łacina -3.3; sąsiedzi z = +140.7 (v5 +175.1); jednostek 62072, typów 7253.
- cięcie: długości posortowane (glyphs): długość opisu 5.943 bit/glif (odstępy EVA 3.896; v5 5.672 wobec 3.473); rękopis niespokrewnione z = -25.6, bełkot v5 -31.2, łacina -11.6; sąsiedzi z = +17.1 (v5 +28.0); jednostek 34820, typów 14388.
- Cięcia bez klucza: cięcie co 3 glifów (bez klucza) koduje rękopis 3.317 bit/glif wobec 3.896 dla słów EVA (bełkot v5 3.199 wobec 3.473; łacina 3.893 wobec 3.452). Słowa rękopisu, jak słowa bełkotu, są mniej oszczędnymi jednostkami niż sztywne kawałki glifów; słowa łaciny są oszczędniejsze od kawałków.

## Zastrzeżenia

- Rodzina reguł jest skończona (cięcia, przesunięcia, transpozycje według długości); klucz innego rodzaju, np. tablica przyporządkowująca długościom litery, wymagałby osobnego testu (tak działał length_code, obalony).
- Cięcie strumienia glifów w sztywne kawałki samo tworzy pozorną informację między sąsiadami (zależności glifów przechodzą przez cięcie); stąd porównanie każdej reguły z tą samą regułą na bełkocie, nie z zerem.
- Ujemna informacja sąsiednich słów rękopisu to nowa miara spoza karty 22; kandydat do karty v7.

## Literatura

- Currier (1976); Zandbergen, voynich.nu: word structure and spaces
- Reddy & Knight, What we know about the Voynich manuscript (2011): word-level statistics

_Czas: 865 s · 2026-10-24 20:39_