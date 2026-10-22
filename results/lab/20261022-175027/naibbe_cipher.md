# naibbe_cipher: obalona

**Hipoteza.** Rękopis to szyfr typu Naibbe: łacina pocięta na 1–2-literowe kawałki, szyfrowana sześcioma tabelami wybieranymi kartą.

**Metoda.** Rekonstrukcja szyfru z opisu Greshki (2025), tabele zbudowane z części słów rękopisu; szyfrogram Izydora porównany z rękopisem.

Szyfr Naibbe-podobny: odległość 0.83, różnica hapaksów 20%. Literatura: Naibbe odtwarza entropię i rozkład długości, ale nie hapaksy (41% wobec 70%).

## Kontrole

- ✅ **rozpoznanie języka**: oczekiwano druga próbka łaciny najbliżej pierwszej; wynik: najbliżej: Latin
- ✅ **szyfr odwracalny**: oczekiwano odszyfrowanie tabelami odtwarza tekst jawny; wynik: deterministyczne tabele, sprawdzone na próbce

## Dowody

- Naibbe-podobny (Izydor): odległość 0.83, h2=2.30 (rękopis 2.35), hapaksy 49% (70%), MI krawędzi 0.012 (0.168), podobni sąsiedzi 2.4% (5.0%).

## Zastrzeżenia

- To rekonstrukcja z opisu, nie oryginalne tabele Greshki; wynik dotyczy klasy szyfrów, nie konkretnej publikacji.

## Rada modeli

## Werdykt rady
**Nierozstrzygnięte.** Automatycznego werdyktu „obalona” nie uznajemy za wiarygodnie wykazanego.

## Poziom zgody
Wysoki: wszystkie oceny po dyskusji uznały, że brak kluczowych kontroli uniemożliwia rozstrzygający wniosek.

## Co test naprawdę pokazuje
W tej rekonstrukcji szyfru Naibbe wyniki różnią się od rękopisu m.in. pod względem hapaksów (49% wobec 70%), MI krawędzi (0,012 wobec 0,168) i podobnych sąsiadów (2,4% wobec 5,0%). Entropia h2 jest natomiast zbliżona. To przemawia przeciw **badanej rekonstrukcji**, ale samo nie obala całej klasy szyfrów Naibbe.

## Główne zastrzeżenia
Nie wykazano, że metoda wykrywa celowo podłożony efekt ani że nie znajduje go w danych przetasowanych. Kontrole rozpoznania języka i odwracalności tego nie sprawdzają. Ponadto użyto rekonstrukcji tabel, jednego tekstu jawnego, a odległość 0,83 nie ma podanej kalibracji ani progu decyzyjnego.

## Rekomendowany następny eksperyment
Zastosować tę samą, z góry ustaloną procedurę do wielu szyfrogramów Naibbe utworzonych z różnych tekstów łacińskich oraz do danych przetasowanych. Test powinien wykrywać efekt w próbkach Naibbe i nie wykrywać go w przetasowanych; dopiero wtedy porównanie z rękopisem może wspierać rozstrzygający wniosek.

## Literatura

- M. A. Greshko, The Naibbe cipher, Cryptologia (2025), doi:10.1080/01611194.2025.2566408
- Rozanova & Temerev, arXiv:2608.17096

_Czas: 9 s · 2026-10-22 18:41_