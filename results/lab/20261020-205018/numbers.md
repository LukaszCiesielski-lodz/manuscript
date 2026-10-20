# numbers: obalona

**Hipoteza.** Znaki rękopisu zapisują liczby (cały tekst albo przynajmniej etykiety w dziale zodiakalnym).

**Metoda.** A: teksty liczb w 5 systemach liczbowych sprzed 1450 r. porównane z rękopisem i 12 językami na 10 miarach kształtu tekstu (niezależnych od podstawienia znaków). B: test permutacyjny podobieństwa sąsiednich etykiet zodiaku (czy wyglądają jak kolejne liczby 1–30).

Cały tekst jako liczby: nie pasuje (najbliższy system: alfabetyczny (grecki/hebrajski), odległość 1.73; dopasowanie wymaga < 0.5, dwie próbki łaciny różnią się o ok. 0,2). Etykiety zodiaku jako kolejne liczby: nie (efekt 2.1% przy p = 0.051; liczby podłożone dają ≥ 16%, zwykły tekst rękopisu 1.3%).

## Kontrole

- ✅ **rozpoznanie języka**: oczekiwano druga próbka łaciny najbliżej pierwszej; wynik: najbliżej: Latin (odległość 0.12)
- ✅ **podłożone liczby 1–30 (rzymski addytywny (IIII, VIIII))**: oczekiwano test wykrywa ciąg (p < 0,01); wynik: p = 0.0003
- ✅ **podłożone liczby 1–30 (alfabetyczny (grecki/hebrajski))**: oczekiwano test wykrywa ciąg (p < 0,01); wynik: p = 0.0003
- ✅ **podłożone liczby 1–30 (dziesiętny pozycyjny)**: oczekiwano test wykrywa ciąg (p < 0,01); wynik: p = 0.0003
- ✅ **kalibracja na losowych etykietach**: oczekiwano fałszywe alarmy (p < 0,05) w ok. 5% zestawów, najwyżej 20%; wynik: 0/20

## Dowody

- Najbliższy system liczbowy: alfabetyczny (grecki/hebrajski), odległość 1.73; najbliższy język: Vietnamese, 2.05 (jednostka: rozrzut między językami).
- dziesiętny pozycyjny (rozkład counts): odległość 2.93, h2=2.44, sztywność kolejności=0.76, typy=1881, hapaksy=54%, średnia dł.=1.7
- dwudziestkowy pozycyjny (rozkład counts): odległość 2.77, h2=2.72, sztywność kolejności=0.82, typy=1900, hapaksy=54%, średnia dł.=1.4
- rzymski (z odejmowaniem) (rozkład counts): odległość 2.82, h2=1.85, sztywność kolejności=0.91, typy=1881, hapaksy=56%, średnia dł.=3.2
- rzymski addytywny (IIII, VIIII) (rozkład counts): odległość 2.85, h2=1.46, sztywność kolejności=1.00, typy=1886, hapaksy=54%, średnia dł.=3.8
- alfabetyczny (grecki/hebrajski) (rozkład counts): odległość 1.73, h2=2.52, sztywność kolejności=0.91, typy=1892, hapaksy=55%, średnia dł.=1.7
- Rękopis: h2=2.35, sztywność=0.88, typy=4996, hapaksy=70%, średnia dł.=4.2
- Zodiak: 12 stron, 299 etykiet. Niepodobieństwo sąsiadów 0.658 wobec 0.672 po przetasowaniu (efekt 2.1%), p = 0.0506.
- Podłożone liczby 1–30 dają efekt co najmniej 16%; zwykłe wiersze tekstu rękopisu dają 1.3% (ogólny zwyczaj pisania podobnych słów obok siebie).

## Zastrzeżenia

- Rozkład liczb jest założony (dużo małych liczb, ogon do 3999); inny rozkład zmienia liczbę typów i hapaksów.
- Test B zakłada, że kolejność etykiet w transliteracji odpowiada kolejności wokół pierścieni.
- Szyfr homofoniczny zapisujący liczby rozmyłby podobieństwo kolejnych etykiet; test B go nie wykluczy.

## Rada modeli

## Werdykt rady
**Niepotwierdzona; mocny wynik negatywny dla sprawdzonych wariantów.** Cały tekst słabo pasuje do pięciu badanych systemów liczbowych, a etykiety zodiaku nie wykazują przekonującego podobieństwa do kolejnych liczb 1–30. Nie uzasadnia to jednak obalenia szerokiej hipotezy o dowolnym zapisie liczb.

**Poziom zgody:** Wysoka co do negatywnych wyników testów i ich ograniczonego zakresu; umiarkowana co do werdyktu. Opinie różnią się głównie tym, czy wynik uznać za „obalenie” testowanych wariantów, czy za mocne osłabienie hipotezy ogólnej.

## Co test naprawdę pokazuje
Dla całego tekstu najbliższy system ma odległość **1,73**, daleką od wymaganego dopasowania **<0,5**. Test etykiet daje efekt **2,1%** przy **p = 0,0506**, wobec co najmniej **16%** dla podłożonych ciągów. Kontrole wykryły podłożone liczby we wszystkich trzech sprawdzonych zapisach; kalibracja przetasowań dała **0/20** fałszywych alarmów.

## Główne zastrzeżenia
Test całego tekstu obejmuje pięć systemów i przyjęty rozkład liczb; nie rozstrzyga wariantu ograniczonego do etykiet. Test etykiet sprawdza tylko ciąg 1–30, zakłada poprawną kolejność transliteracji względem układu na stronach, a jego wynik jest graniczny. Kontrola 0/20 ma ograniczoną liczebność. Raport zastrzega też, że kodowanie homofoniczne nie zostało wykluczone.

## Rekomendowany następny eksperyment
Przeprowadzić z góry określony test **homofonicznego kodowania liczb**, z podłożonymi danymi jako kontrolą wykrywalności oraz przetasowanymi etykietami jako kontrolą fałszywych trafień.

## Literatura

- Bowern & Lindemann, The Linguistics of the Voynich Manuscript, Annual Review of Linguistics 7 (2021)
- Wikipedia/Voynich: 'oror or' na f15v przypomina zaszyfrowane cyfry rzymskie

_Czas: 40 s · 2026-10-20 21:12_