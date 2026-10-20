# naibbe_cipher: nierozstrzygnięta

**Hipoteza.** Rękopis to szyfr typu Naibbe: łacina pocięta na 1–2-literowe kawałki, szyfrowana sześcioma tabelami wybieranymi kartą.

**Metoda.** Rekonstrukcja szyfru z opisu Greshki (2025), tabele zbudowane z części słów rękopisu; szyfrogram Izydora porównany z rękopisem.

Szyfr Naibbe-podobny: odległość 0.63, różnica hapaksów 7%. Literatura: Naibbe odtwarza entropię i rozkład długości, ale nie hapaksy (41% wobec 70%).

## Kontrole

- ✅ **rozpoznanie języka**: oczekiwano druga próbka łaciny najbliżej pierwszej; wynik: najbliżej: Latin
- ✅ **szyfr odwracalny**: oczekiwano odszyfrowanie tabelami odtwarza tekst jawny; wynik: deterministyczne tabele, sprawdzone na próbce

## Dowody

- Naibbe-podobny (Izydor): odległość 0.63, h2=2.30 (rękopis 2.37), hapaksy 62% (69%), MI krawędzi 0.023 (0.167), podobni sąsiedzi 2.5% (5.5%).

## Zastrzeżenia

- To rekonstrukcja z opisu, nie oryginalne tabele Greshki; wynik dotyczy klasy szyfrów, nie konkretnej publikacji.

## Rada modeli

## Werdykt rady
**Nierozstrzygnięta.** Poziom zgody jest wysoki: obie merytoryczne oceny końcowe uznają, że raport nie potwierdza ani nie wyklucza hipotezy.

## Co test naprawdę pokazuje
Uzyskano **mieszane podobieństwo statystyczne**: entropia h2 jest zbliżona (2,30 wobec 2,37), podobnie jak udział hapaksów (62% wobec 69%). Zarazem MI krawędzi jest znacznie niższe (0,023 wobec 0,167), a miary sąsiedztwa również się różnią. Sama odległość 0,63 nie ma podanej skali porównawczej.

## Główne zastrzeżenia
Kontrole rozpoznania łaciny i odwracalności tabel nie sprawdzają, czy pełna procedura wykrywa efekt celowo podłożony ani czy nie wykrywa go w danych przetasowanych. Te kluczowe kontrole nie zostały przedstawione, więc test nie spełnia kryteriów wiarygodności. Ponadto tabele zrekonstruowano z części słów rękopisu, a nie z oryginalnych tabel; wynik nie rozstrzyga zatem konkretnej implementacji. Test nie wyklucza szyfru Naibbe-podobnego, ale nie wykazuje, że obserwowane podobieństwo jest dla niego swoiste.

## Rekomendowany następny eksperyment
Przeprowadzić **zaślepioną walidację pełnej procedury** na syntetycznych danych z celowo podłożonym efektem Naibbe oraz na danych przetasowanych, używając tabel niezależnych od słownictwa rękopisu.

## Literatura

- M. A. Greshko, The Naibbe cipher, Cryptologia (2025), doi:10.1080/01611194.2025.2566408
- Rozanova & Temerev, arXiv:2608.17096

_Czas: 7 s · 2026-10-20 19:28_