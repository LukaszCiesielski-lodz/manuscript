# brute_length: obalona

**Hipoteza.** Słowa o tej samej długości mają własny klucz litera-za-glif: każdy zbiór słów jednakowej długości jest osobnym szyfrem podstawieniowym któregoś z języków epoki.

**Metoda.** Słowa rękopisu podzielone na zbiory według długości (2, 3, 4, 5, 6, 7, 8 i 9+ glifów), każdy zbiór w kolejności czytania pocięty na pseudowiersze po 9 słów; na każdym zbiorze osobno brute force po kluczach trójka po trójce (do 4000 najczęstszych trójek, 6 leksykonów, cuda): słownik przycina klucze do odczytów o tym samym wzorze powtórzeń, miary: zgodność odczytów co do jednego klucza i udział słów w słowniku pod kluczem z wierszy nieparzystych na parzystych. Tło na każdym zbiorze: bełkot v5 podzielony tak samo, słowa przetasowane, glify przemianowane w każdym pseudowierszu. Kontrola dodatnia: tekst języka zaszyfrowany losowym kluczem i podzielony według długości; klucz każdego zbioru musi zostać odzyskany.

34 zbiorów testowalnych (6 pominiętych), 6 języków. W żadnym zbiorze długości rękopis nie wygrywa z bełkotem: najwyższy udział słów w słowniku pod kluczem zbioru 93.9% (French, długość 2; bełkot 87.6%, zaszyfrowany tekst 77%). Osobny klucz na długość nie pomaga.

## Kontrole

- ✅ **Latin, długość 2: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 98%, klucz 79%
- ✅ **Latin, długość 3: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 70%, klucz 86%
- ✅ **Latin, długość 4: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 97%, klucz 100%
- ✅ **Latin, długość 5: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Latin, długość 6: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Latin, długość 7: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Latin, długość 8: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Italian, długość 4: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 97%, klucz 100%
- ✅ **Italian, długość 5: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Italian, długość 6: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Italian, długość 7: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Italian, długość 8: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **German, długość 3: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 90%, klucz 95%
- ✅ **German, długość 4: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 97%, klucz 99%
- ✅ **German, długość 5: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 98%, klucz 100%
- ✅ **German, długość 6: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **German, długość 7: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **French, długość 2: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 77%, klucz 73%
- ✅ **French, długość 3: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 67%, klucz 72%
- ✅ **French, długość 4: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 95%, klucz 99%
- ✅ **French, długość 5: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 99%, klucz 100%
- ✅ **French, długość 6: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 99%, klucz 100%
- ✅ **French, długość 7: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Spanish, długość 3: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 70%, klucz 77%
- ✅ **Spanish, długość 4: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 97%, klucz 100%
- ✅ **Spanish, długość 5: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 99%, klucz 100%
- ✅ **Spanish, długość 6: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Spanish, długość 7: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Spanish, długość 8: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Czech, długość 4: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 97%, klucz 100%
- ✅ **Czech, długość 5: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 99%, klucz 100%
- ✅ **Czech, długość 6: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Czech, długość 7: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **Czech, długość 8: zaszyfrowany tekst tej długości**: oczekiwano ≥ 60% słów w słowniku, ≥ 70% klucza; wynik: 100%, klucz 100%
- ✅ **zbiory nietestowalne tą metodą (pominięte w werdykcie)**: oczekiwano jak najmniej; wynik: Italian/2, Italian/3, German/2, Spanish/2, Czech/2, Czech/3

## Dowody

- Latin, długość 9+: za mało słów (209); pominięta.
- Latin: długość 2 (2921 słów): rękopis spójność 0.38, słownik 83.9%, trójek 1570; bełkot spójność 0.38, słownik 81.9%, trójek 1591; przemianowane spójność 0.26; zaszyfrowany 98%, klucz 79%; długość 3 (6493 słów): rękopis spójność 0.28, słownik 16.6%, trójek 4000; bełkot spójność 0.27, słownik 6.9%, trójek 4000; przemianowane spójność 0.14; zaszyfrowany 70%, klucz 86%; długość 4 (8784 słów): rękopis spójność 0.19, słownik 14.1%, trójek 4000; bełkot spójność 0.20, słownik 4.9%, trójek 4000; przemianowane spójność 0.11; zaszyfrowany 97%, klucz 100%; długość 5 (7390 słów): rękopis spójność 0.17, słownik 2.2%, trójek 4000; bełkot spójność 0.17, słownik 1.3%, trójek 4000; przemianowane spójność 0.10; zaszyfrowany 100%, klucz 100%; długość 6 (5309 słów): rękopis spójność 0.18, słownik 0.1%, trójek 4000; bełkot spójność 0.18, słownik 0.1%, trójek 3945; przemianowane spójność 0.10; zaszyfrowany 100%, klucz 100%; długość 7 (2041 słów): rękopis spójność 0.23, słownik 0.0%, trójek 1526; bełkot spójność 0.31, słownik 7.8%, trójek 1487; przemianowane spójność 0.20; zaszyfrowany 100%, klucz 100%; długość 8 (537 słów): rękopis spójność 0.00, słownik 0.0%, trójek 417; bełkot spójność 0.00, słownik 0.0%, trójek 434; przemianowane spójność 0.00; zaszyfrowany 100%, klucz 100%.
- Italian, długość 9+: za mało słów (209); pominięta.
- Italian: długość 2 (2921 słów): rękopis spójność 0.24, słownik 61.1%, trójek 1570; bełkot spójność 0.25, słownik 62.5%, trójek 1591; przemianowane spójność 0.20; zaszyfrowany 82%, klucz 59% (nietestowalna); długość 3 (6493 słów): rękopis spójność 0.19, słownik 35.9%, trójek 4000; bełkot spójność 0.19, słownik 20.3%, trójek 4000; przemianowane spójność 0.13; zaszyfrowany 59%, klucz 78% (nietestowalna); długość 4 (8784 słów): rękopis spójność 0.21, słownik 13.8%, trójek 4000; bełkot spójność 0.21, słownik 21.2%, trójek 4000; przemianowane spójność 0.12; zaszyfrowany 97%, klucz 100%; długość 5 (7390 słów): rękopis spójność 0.18, słownik 4.8%, trójek 4000; bełkot spójność 0.17, słownik 2.5%, trójek 4000; przemianowane spójność 0.11; zaszyfrowany 100%, klucz 100%; długość 6 (5309 słów): rękopis spójność 0.22, słownik 8.1%, trójek 4000; bełkot spójność 0.24, słownik 12.3%, trójek 3945; przemianowane spójność 0.11; zaszyfrowany 100%, klucz 100%; długość 7 (2041 słów): rękopis spójność 0.33, słownik 7.8%, trójek 1526; bełkot spójność 0.37, słownik 0.0%, trójek 1487; przemianowane spójność 0.23; zaszyfrowany 100%, klucz 100%; długość 8 (537 słów): rękopis spójność 0.00, słownik 0.0%, trójek 417; bełkot spójność 0.00, słownik 0.0%, trójek 434; przemianowane spójność 0.00; zaszyfrowany 100%, klucz 100%.
- German, długość 8: za mało słów (537); pominięta.
- German, długość 9+: za mało słów (209); pominięta.
- German: długość 2 (2921 słów): rękopis spójność 0.30, słownik 64.8%, trójek 1570; bełkot spójność 0.31, słownik 57.3%, trójek 1591; przemianowane spójność 0.19; zaszyfrowany 76%, klucz 54% (nietestowalna); długość 3 (6493 słów): rękopis spójność 0.25, słownik 53.6%, trójek 4000; bełkot spójność 0.25, słownik 57.3%, trójek 4000; przemianowane spójność 0.14; zaszyfrowany 90%, klucz 95%; długość 4 (8784 słów): rękopis spójność 0.18, słownik 10.2%, trójek 4000; bełkot spójność 0.19, słownik 13.2%, trójek 4000; przemianowane spójność 0.11; zaszyfrowany 97%, klucz 99%; długość 5 (7390 słów): rękopis spójność 0.17, słownik 0.0%, trójek 4000; bełkot spójność 0.17, słownik 1.1%, trójek 4000; przemianowane spójność 0.10; zaszyfrowany 98%, klucz 100%; długość 6 (5309 słów): rękopis spójność 0.18, słownik 0.0%, trójek 4000; bełkot spójność 0.18, słownik 1.6%, trójek 3945; przemianowane spójność 0.11; zaszyfrowany 100%, klucz 100%; długość 7 (2041 słów): rękopis spójność 0.41, słownik 9.5%, trójek 1526; bełkot spójność 0.51, słownik 10.6%, trójek 1487; przemianowane spójność 0.23; zaszyfrowany 100%, klucz 100%.
- French, długość 8: za mało słów (537); pominięta.
- French, długość 9+: za mało słów (209); pominięta.
- French: długość 2 (2921 słów): rękopis spójność 0.29, słownik 93.9%, trójek 1570; bełkot spójność 0.30, słownik 87.6%, trójek 1591; przemianowane spójność 0.23; zaszyfrowany 77%, klucz 73%; długość 3 (6493 słów): rękopis spójność 0.24, słownik 50.7%, trójek 4000; bełkot spójność 0.24, słownik 53.2%, trójek 4000; przemianowane spójność 0.13; zaszyfrowany 67%, klucz 72%; długość 4 (8784 słów): rękopis spójność 0.22, słownik 2.0%, trójek 4000; bełkot spójność 0.23, słownik 19.7%, trójek 4000; przemianowane spójność 0.11; zaszyfrowany 95%, klucz 99%; długość 5 (7390 słów): rękopis spójność 0.17, słownik 0.8%, trójek 4000; bełkot spójność 0.18, słownik 1.0%, trójek 4000; przemianowane spójność 0.10; zaszyfrowany 99%, klucz 100%; długość 6 (5309 słów): rękopis spójność 0.19, słownik 0.2%, trójek 4000; bełkot spójność 0.18, słownik 0.0%, trójek 3945; przemianowane spójność 0.11; zaszyfrowany 99%, klucz 100%; długość 7 (2041 słów): rękopis spójność 0.34, słownik 0.0%, trójek 1526; bełkot spójność 0.36, słownik 0.0%, trójek 1487; przemianowane spójność 0.18; zaszyfrowany 100%, klucz 100%.
- Spanish, długość 9+: za mało słów (209); pominięta.
- Spanish: długość 2 (2921 słów): rękopis spójność 0.29, słownik 81.4%, trójek 1570; bełkot spójność 0.30, słownik 73.0%, trójek 1591; przemianowane spójność 0.23; zaszyfrowany 96%, klucz 62% (nietestowalna); długość 3 (6493 słów): rękopis spójność 0.26, słownik 26.1%, trójek 4000; bełkot spójność 0.26, słownik 25.2%, trójek 4000; przemianowane spójność 0.13; zaszyfrowany 70%, klucz 77%; długość 4 (8784 słów): rękopis spójność 0.23, słownik 22.5%, trójek 4000; bełkot spójność 0.24, słownik 27.9%, trójek 4000; przemianowane spójność 0.12; zaszyfrowany 97%, klucz 100%; długość 5 (7390 słów): rękopis spójność 0.18, słownik 2.0%, trójek 4000; bełkot spójność 0.19, słownik 2.0%, trójek 4000; przemianowane spójność 0.10; zaszyfrowany 99%, klucz 100%; długość 6 (5309 słów): rękopis spójność 0.21, słownik 0.0%, trójek 4000; bełkot spójność 0.23, słownik 0.1%, trójek 3945; przemianowane spójność 0.11; zaszyfrowany 100%, klucz 100%; długość 7 (2041 słów): rękopis spójność 0.35, słownik 7.6%, trójek 1526; bełkot spójność 0.48, słownik 18.5%, trójek 1487; przemianowane spójność 0.25; zaszyfrowany 100%, klucz 100%; długość 8 (537 słów): rękopis spójność 0.00, słownik 0.0%, trójek 417; bełkot spójność 1.00, słownik 0.0%, trójek 434; przemianowane spójność 0.00; zaszyfrowany 100%, klucz 100%.
- Czech, długość 9+: za mało słów (209); pominięta.
- Czech: długość 2 (2921 słów): rękopis spójność 0.31, słownik 82.1%, trójek 1570; bełkot spójność 0.32, słownik 75.8%, trójek 1591; przemianowane spójność 0.19; zaszyfrowany 66%, klucz 48% (nietestowalna); długość 3 (6493 słów): rękopis spójność 0.23, słownik 58.2%, trójek 4000; bełkot spójność 0.24, słownik 56.6%, trójek 4000; przemianowane spójność 0.13; zaszyfrowany 39%, klucz 59% (nietestowalna); długość 4 (8784 słów): rękopis spójność 0.18, słownik 15.0%, trójek 4000; bełkot spójność 0.19, słownik 22.2%, trójek 4000; przemianowane spójność 0.11; zaszyfrowany 97%, klucz 100%; długość 5 (7390 słów): rękopis spójność 0.13, słownik 0.0%, trójek 4000; bełkot spójność 0.14, słownik 0.1%, trójek 4000; przemianowane spójność 0.09; zaszyfrowany 99%, klucz 100%; długość 6 (5309 słów): rękopis spójność 0.13, słownik 0.0%, trójek 4000; bełkot spójność 0.14, słownik 0.0%, trójek 3945; przemianowane spójność 0.09; zaszyfrowany 100%, klucz 100%; długość 7 (2041 słów): rękopis spójność 0.24, słownik 7.7%, trójek 1526; bełkot spójność 0.39, słownik 18.2%, trójek 1487; przemianowane spójność 0.20; zaszyfrowany 100%, klucz 100%; długość 8 (537 słów): rękopis spójność 0.00, słownik 0.0%, trójek 417; bełkot spójność 0.00, słownik 0.0%, trójek 434; przemianowane spójność 0.00; zaszyfrowany 100%, klucz 100%.

## Zastrzeżenia

- W zbiorze jednej długości „trójka” to trzy kolejne słowa tej długości w kolejności czytania, nie sąsiedzi w tekście; sens par jest więc słabszym sygnałem niż w teorii brute, liczy się zgodność klucza i udział słów w słowniku.
- Zbiory krótkich słów (2–3 glify) mają mało wzorów powtórzeń, więc wiele odczytów pasuje z przypadku; tło bełkotu to wyrównuje.

## Literatura

- Hauer & Kondrak, Decoding Anagrammed Texts Written in an Unknown Language and Script, TACL 4 (2016)
- Stolfi, On the VMS word length distribution (2000)

_Czas: 563 s · 2026-10-27 20:26_