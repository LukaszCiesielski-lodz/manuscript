# numbers: obalona

**Hipoteza.** Znaki rękopisu zapisują liczby (cały tekst albo przynajmniej etykiety w dziale zodiakalnym).

**Metoda.** A: teksty liczb w 5 systemach liczbowych sprzed 1450 r. porównane z rękopisem i 12 językami na 10 miarach kształtu tekstu (niezależnych od podstawienia znaków). B: test permutacyjny podobieństwa sąsiednich etykiet zodiaku (czy wyglądają jak kolejne liczby 1–30).

Cały tekst jako liczby: nie pasuje (najbliższy system: alfabetyczny (grecki/hebrajski), odległość 1.52; dopasowanie wymaga < 0.5, dwie próbki łaciny różnią się o ok. 0,2). Etykiety zodiaku jako kolejne liczby: nie (efekt 2.2% przy p = 0.027; liczby podłożone dają ≥ 16%, zwykły tekst rękopisu 1.3%).

## Kontrole

- ✅ **rozpoznanie języka**: oczekiwano druga próbka łaciny najbliżej pierwszej; wynik: najbliżej: Latin (odległość 0.21)
- ✅ **podłożone liczby 1–30 (rzymski addytywny (IIII, VIIII))**: oczekiwano test wykrywa ciąg (p < 0,01); wynik: p = 0.0033
- ✅ **podłożone liczby 1–30 (alfabetyczny (grecki/hebrajski))**: oczekiwano test wykrywa ciąg (p < 0,01); wynik: p = 0.0033
- ✅ **podłożone liczby 1–30 (dziesiętny pozycyjny)**: oczekiwano test wykrywa ciąg (p < 0,01); wynik: p = 0.0033
- ✅ **kalibracja na losowych etykietach**: oczekiwano fałszywe alarmy (p < 0,05) w ok. 5% zestawów, najwyżej 20%; wynik: 1/10

## Dowody

- Najbliższy system liczbowy: alfabetyczny (grecki/hebrajski), odległość 1.52; najbliższy język: Vietnamese, 1.84 (jednostka: rozrzut między językami).
- dziesiętny pozycyjny (rozkład counts): odległość 2.87, h2=2.44, sztywność kolejności=0.75, typy=1064, hapaksy=66%, średnia dł.=1.7
- dwudziestkowy pozycyjny (rozkład counts): odległość 2.62, h2=2.71, sztywność kolejności=0.84, typy=1064, hapaksy=67%, średnia dł.=1.4
- rzymski (z odejmowaniem) (rozkład counts): odległość 2.82, h2=1.86, sztywność kolejności=0.91, typy=1064, hapaksy=65%, średnia dł.=3.2
- rzymski addytywny (IIII, VIIII) (rozkład counts): odległość 2.87, h2=1.46, sztywność kolejności=1.00, typy=1079, hapaksy=66%, średnia dł.=3.7
- alfabetyczny (grecki/hebrajski) (rozkład counts): odległość 1.52, h2=2.51, sztywność kolejności=0.90, typy=1086, hapaksy=67%, średnia dł.=1.7
- Rękopis: h2=2.37, sztywność=0.87, typy=2446, hapaksy=69%, średnia dł.=3.9
- Zodiak: 12 stron, 299 etykiet. Niepodobieństwo sąsiadów 0.658 wobec 0.673 po przetasowaniu (efekt 2.2%), p = 0.0266.
- Podłożone liczby 1–30 dają efekt co najmniej 16%; zwykłe wiersze tekstu rękopisu dają 1.3% (ogólny zwyczaj pisania podobnych słów obok siebie).

## Zastrzeżenia

- Rozkład liczb jest założony (dużo małych liczb, ogon do 3999); inny rozkład zmienia liczbę typów i hapaksów.
- Test B zakłada, że kolejność etykiet w transliteracji odpowiada kolejności wokół pierścieni.
- Szyfr homofoniczny zapisujący liczby rozmyłby podobieństwo kolejnych etykiet; test B go nie wykluczy.

## Rada modeli

## Werdykt rady

**Nieuzasadnione jest odrzucenie całej teorii „numbers”.** Wyniki przemawiają przeciwko temu, by cały tekst odpowiadał któremukolwiek z pięciu testowanych systemów liczbowych, oraz przeciwko prostemu ciągowi 1–30 w etykietach zodiaku. Nie wykluczają jednak innych sposobów zapisu liczb.

**Poziom zgody:** brak podstaw do oceny zgody całej rady — opinie A i C są puste. Dostępna opinia B trafnie podkreśla, że automatyczny werdykt jest szerszy niż zakres testu.

## Co test naprawdę pokazuje

Kontrole metody przeszły: testy wykryły podłożone ciągi liczb, a odsetek fałszywych alarmów w próbie losowej mieścił się w przyjętym limicie. Dopasowanie całego tekstu jest słabe: najbliższy system ma odległość 1,52 wobec wymaganego progu poniżej 0,5. W etykietach zodiaku efekt wynosi 2,2% (p = 0,0266) — niewiele więcej niż 1,3% w zwykłym tekście i znacznie mniej niż co najmniej 16% dla podłożonych liczb.

## Główne zastrzeżenia

Test całego tekstu zależy od pięciu badanych systemów i założonego rozkładu liczb. Test etykiet zakłada, że kolejność transliteracji odpowiada kolejności na pierścieniach; bada tylko prosty ciąg i nie wyklucza kodowania rozmywającego podobieństwo. Kalibracja losowa opiera się zaledwie na 10 zestawach.

## Rekomendowany następny eksperyment

Powtórzyć test etykiet z kolejnością ustaloną niezależnie, z góry określonymi wariantami zapisu i większą liczbą losowych zestawów kontrolnych.

## Literatura

- Bowern & Lindemann, The Linguistics of the Voynich Manuscript, Annual Review of Linguistics 7 (2021)
- Wikipedia/Voynich: 'oror or' na f15v przypomina zaszyfrowane cyfry rzymskie

_Czas: 17 s · 2026-10-20 19:26_