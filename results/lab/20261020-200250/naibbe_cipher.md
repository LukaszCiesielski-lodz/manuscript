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

**Nierozstrzygający; test nie uzasadnia werdyktu „obalona”.** Zgoda jest częściowa: raport pokazuje różnice między badaną rekonstrukcją a rękopisem, ale nie potwierdza wiarygodności metody w wymaganych kontrolach.

## Co test naprawdę pokazuje

W badanej rekonstrukcji h2 jest zbliżone do wyniku dla rękopisu (2,30 wobec 2,35), natomiast hapaksy wyraźnie się różnią (49% wobec 70%); różnią się też MI krawędzi (0,012 wobec 0,168) i odsetek podobnych sąsiadów (2,4% wobec 5,0%). To przemawia przeciw **tej rekonstrukcji**, nie rozstrzyga jednak całej hipotezy.

## Główne zastrzeżenia

Zgłoszone kontrole sprawdzają rozpoznanie języka i odwracalność szyfru, ale nie wykazują, że metoda wykrywa celowo podłożoną sygnaturę Naibbe ani że nie wykrywa jej w danych przetasowanych. Ponadto użyto rekonstrukcji i tabel zbudowanych z części słów rękopisu, a nie oryginalnych tabel. Raport nie podaje też niepewności ani progów interpretacji różnic.

## Następny eksperyment

Przeprowadzić ślepy test walidacyjny tym samym pipeline’em na znanych, celowo zaszyfrowanych próbkach Naibbe oraz na odpowiednio przetasowanych próbkach kontrolnych.

## Literatura

- M. A. Greshko, The Naibbe cipher, Cryptologia (2025), doi:10.1080/01611194.2025.2566408
- Rozanova & Temerev, arXiv:2608.17096

_Czas: 9 s · 2026-10-20 20:30_