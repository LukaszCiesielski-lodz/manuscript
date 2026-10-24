# transcriptions: potwierdzona

**Hipoteza.** Podpis statystyczny rękopisu (brak dalekiej składni między różnymi słowami, nadmiar powtórzeń i wariantów, podobne długości sąsiadów) jest własnością rękopisu, nie transliteracji ZL.

**Metoda.** Te same miary na każdej dostępnej transliteracji z voynich.nu: Zandbergen-Landini, Takahashi (dwie wersje), Reference, Currier-D'Imperio, FSG, v101. Alfabety nie-EVA tokenizowane po znaku. Składnia na odległość rozbita na powtórzenia, warianty i słowa niespokrewnione (z wobec tasowań w stronie i miejscu w wierszu); dynamika długości (korelacja sąsiadów, DFA); miary kształtu jako z wobec rozrzutu bloków ZL.

Podpis trzyma w 4/4 pełnych transliteracjach: ZL tak, IT tak, CD nie (częściowa), FG tak, GC tak.

## Kontrole


## Dowody

- ZL (Zandbergen-Landini; 34820 słów, 33 znaków): słowa niespokrewnione z = -1.2, powtórzenia z = 9.6, warianty z = 5.1; korelacja długości sąsiadów +0.159, DFA 0.598; kształt wobec ZL: entropia warunkowa h₂ +0.0, różne słowa / wszystkie +0.0, słowa użyte raz (hapaksy) +0.0, sąsiednie słowa różne o 1 glif +0.0, korelacja długości sąsiednich słów +0.0. Podpis trzyma.
- IT (Takahashi (interlinear); 34411 słów, 29 znaków): słowa niespokrewnione z = -0.8, powtórzenia z = 8.0, warianty z = 6.3; korelacja długości sąsiadów +0.158, DFA 0.597; kształt wobec ZL: entropia warunkowa h₂ +0.0, różne słowa / wszystkie +0.1, słowa użyte raz (hapaksy) +0.0, sąsiednie słowa różne o 1 glif -0.2, korelacja długości sąsiednich słów -0.0. Podpis trzyma.
- CD (Currier-D'Imperio; 16082 słów, 35 znaków): słowa niespokrewnione z = 2.6, powtórzenia z = 4.3, warianty z = 4.5; korelacja długości sąsiadów +0.177, DFA 0.604; kształt wobec ZL: entropia warunkowa h₂ +0.4, różne słowa / wszystkie -0.2, słowa użyte raz (hapaksy) -0.3, sąsiednie słowa różne o 1 glif +1.1, korelacja długości sąsiednich słów +0.5. Podpis NIE trzyma (transliteracja częściowa, poza werdyktem).
- FG (FSG (First Study Group); 33002 słów, 23 znaków): słowa niespokrewnione z = 2.1, powtórzenia z = 6.1, warianty z = 4.8; korelacja długości sąsiadów +0.148, DFA 0.604; kształt wobec ZL: entropia warunkowa h₂ +0.2, różne słowa / wszystkie +0.1, słowa użyte raz (hapaksy) +0.0, sąsiednie słowa różne o 1 glif -0.0, korelacja długości sąsiednich słów +0.2. Podpis trzyma.
- GC (GC v101; 36347 słów, 70 znaków): słowa niespokrewnione z = -4.7, powtórzenia z = 5.4, warianty z = 4.5; korelacja długości sąsiadów +0.197, DFA 0.610; kształt wobec ZL: entropia warunkowa h₂ +1.3, różne słowa / wszystkie +0.8, słowa użyte raz (hapaksy) +1.3, sąsiednie słowa różne o 1 glif +0.2, korelacja długości sąsiednich słów +2.2. Podpis trzyma.

## Zastrzeżenia

- ZL i Takahashi są w pełni zgodne tylko w ok. 29% wierszy (Chelednik); różnice to głównie niepewne glify i podziały słów.
- Alfabety Curriera, FSG i v101 dzielą tekst na inne jednostki niż EVA, więc miary kształtu (entropia, długości) nie są z nimi wprost porównywalne; porównywalne są z składni i znak korelacji.

## Literatura

- Zandbergen, voynich.nu/transcr.html
- Chelednik, voynich-transcription-mismatch (Hugging Face 2026)

_Czas: 173 s · 2026-10-24 05:34_