# atoms: nierozstrzygnięta

**Hipoteza.** Rebus w rysunkach: jakaś widoczna cecha narysowanej rzeczy (liczba promieni, kolor, kształt, gest) przewiduje coś w etykiecie napisanej obok (pierwszy glif, długość, końcówkę).

**Metoda.** Atomy ilustracji z data/atoms (jeden rekord na etykietę, cechy ze słownika kontrolowanego, wpisane przez ludzi; szkic z modelu widzącego osobno). Dla każdej pary (cecha rysunku, cecha etykiety) informacja wzajemna wobec etykiet przetasowanych w obrębie strony (2000 tasowań), poprawka Bonferroniego na liczbę par. Cechy o zgodności dwóch osób kappa < 0.6 wykluczone. Kontrole: pierwszy glif etykiety podłożony według cechy w 60% atomów (musi wyjść p popr. < 0,05, z ≥ 5); cechy przetasowane między atomami strony (żadna para p popr. < 0,05 i z ≥ 4).

Brak pary po poprawce (najlepsza nimfa.gwiazda_kolor×dlugosc (n=102, MI 0.282 wobec 0.178, z = +2.5, p popr. 0.92)); opisanych atomów 102, do obalenia potrzeba ≥ 200 i najlepszej z < 2.

## Kontrole

- ✅ **podłożony pierwszy glif według nimfa.wlosy wykryty**: oczekiwano p popr. < 0,05 i z ≥ 5; wynik: z = 20.5, p popr. 0.000
- ✅ **cechy przetasowane między atomami strony bez związku**: oczekiwano żadna para p popr. < 0,05 i z ≥ 4; wynik: najlepsza para nimfa.gwiazda_promienie×drugi z = +2.2, p popr. 1.00

## Dowody

- Atomów 855 na 51 stronach; opisanych (≥ 1 cecha i etykieta) 102 na 5 stronach; źródła: vision; działy: {'zodiac': 102}.
- Par (cecha rysunku × cecha etykiety) z ≥ 30 atomami: 54. Najsilniejsze: nimfa.gwiazda_kolor×dlugosc (n=102, MI 0.282 wobec 0.178, z = +2.5, p popr. 0.92); nimfa.naga×ostatni (n=101, MI 0.188 wobec 0.140, z = +1.5, p popr. 1.00); nimfa.korona×drugi (n=101, MI 0.126 wobec 0.079, z = +1.5, p popr. 1.00); nimfa.w_obiekcie×gallows (n=37, MI 0.053 wobec 0.024, z = +1.2, p popr. 1.00); nimfa.kierunek×pierwszy (n=102, MI 0.081 wobec 0.055, z = +1.1, p popr. 1.00).

## Zastrzeżenia

- Cechy wpisane przez ludzi: błędy odczytu i uznaniowość (co jest 'jednym liściem') obniżają moc testu; kappa to mierzy.
- Test szuka zależności cecha-po-cesze; rebus łączący kilka cech naraz w jeden glif wymaga więcej danych.

## Literatura

- Zandbergen, voynich.nu: descriptions of the zodiac and pharmaceutical pages
- Cohen (1960), A coefficient of agreement for nominal scales

_Czas: 21 s · 2026-11-05 08:52_