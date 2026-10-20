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
**Test niewiarygodny jako podstawa rozstrzygnięcia; hipoteza pozostaje nierozstrzygnięta.** Nie należy przyjmować automatycznego werdyktu „obalona”.

## Poziom zgody
Wysoki: wszystkie opinie w drugiej rundzie uznają, że rozbieżności liczbowe nie wystarczają do obalenia hipotezy bez właściwej walidacji metody.

## Co test naprawdę pokazuje
W badanej rekonstrukcji szyfru odsetek hapaksów wynosi 49% wobec 70% w rękopisie, MI krawędzi 0,012 wobec 0,168, a H2 jest zbliżone: 2,30 wobec 2,35. Wyniki wskazują więc na różnice między tą rekonstrukcją a profilem rękopisu, ale nie dowodzą, że różnice są rozstrzygające dla całej klasy szyfrów Naibbe.

## Główne zastrzeżenia
Kontrole rozpoznania języka i odwracalności sprawdzają działanie elementów implementacji, nie trafność testu hipotezy. Brakuje wykazania, że metoda wykrywa celowo podłożony efekt Naibbe i nie wykrywa go w danych przetasowanych. Ponadto użyto rekonstrukcji, nie oryginalnych tabel; porównano jeden tekst jawny, a raport nie podaje interpretowalnego progu dla odległości 0,83.

## Rekomendowany następny eksperyment
Przeprowadzić kalibrację na wielu tekstach jawnych: sprawdzić, czy metoda wykrywa efekt w danych zaszyfrowanych Naibbe oraz czy nie znajduje go w danych przetasowanych. W miarę możliwości użyć oryginalnych tabel.

## Literatura

- M. A. Greshko, The Naibbe cipher, Cryptologia (2025), doi:10.1080/01611194.2025.2566408
- Rozanova & Temerev, arXiv:2608.17096

_Czas: 9 s · 2026-10-20 21:14_