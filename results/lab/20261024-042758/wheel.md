# wheel: nierozstrzygnięta

**Hipoteza.** Tekst powstał z tarczy (volvelle) o kilku pierścieniach z ciągami glifów: słowo = komórki pod wskaźnikiem, między słowami pierścienie obracają się o ząbek lub dwa; żadnego języka za tym nie ma.

**Metoda.** Tarcza nieznana, więc wnioskowana: populacja 2048 tarcz (3 pierścienie × 24 komórek, komórka = 0–3 glify) oceniana na cuda przez 2000 pokoleń: pokrycie słownictwa i koszt obrotu między kolejnymi słowami wiersza. To samo dla tekstów kontrolnych: rękopis z przetasowanymi słowami, bełkot v5, łacina (litery jako glify). Najlepsza tarcza pisze tekst nawykami obrotu odczytanymi z rękopisu; tekst idzie przez kartę 22 miar, klasyfikator wierszy, test składni i dynamiki długości.

Najlepsza tarcza składa 84% słów rękopisu przy koszcie obrotu 0.41 (przetasowane 0.44, łacina 0.84, bełkot v5 0.37). Tekst pisany tarczą: 5/22 miar, AUC 0.99.

## Kontrole

- ✅ **tarcza rękopisu obraca się taniej niż na słowach przetasowanych**: oczekiwano koszt obrotu niższy o ≥ 0,02; wynik: 0.409 wobec 0.440

## Dowody

- Rękopis: pokrycie 83.9%, koszt obrotu 0.409 (tarcza z pokolenia 1995, 1161 s).
- słowa przetasowane: pokrycie 83.8%, koszt obrotu 0.440.
- bełkot v5: pokrycie 86.9%, koszt obrotu 0.370.
- łacina (litery): pokrycie 49.9%, koszt obrotu 0.836.
- Pierścień 1: ch qok ok sh qot ol t cph r qol she y o qo p che d yt cho k yk s ot l
- Pierścień 2: e d ckh k t che kee sh pch p or she od ar aii ok ol al cth ai a o ee ch
- Pierścień 3: y edy ain al ody dar am ky eey iin s r l o n d m chy ar dy ey ol or aiin
- Tekst z tarczy: 5/22 miar w rozrzucie rękopisu; poza: entropia warunkowa h₂ (z = +4.3), entropia warunkowa h₃ (z = +3.3), średnia długość słowa (z = +2.3), rozrzut długości słowa (z = -5.8), różne słowa / wszystkie (z = +23.2), słowa użyte raz (hapaksy) (z = +6.5), nachylenie Zipfa (z = +28.2), udział 10 najczęstszych słów (z = -8.5), to samo słowo zaraz po sobie (z = +18.4), sąsiednie słowa różne o 1 glif (z = +4.1), gęstość słownika (z = +5.9), stała kolejność glifów (z = -3.0), związek końca słowa z początkiem następnego (z = -4.4), p w pierwszym słowie wiersza (z = -2.3), m w ostatnim słowie wiersza (z = -2.9), długość pierwszego słowa wiersza / średnia (z = -2.7), korelacja długości sąsiednich słów (z = +7.0). Klasyfikator wierszy: AUC 0.993 (wewnątrz słów 0.99, na styku 0.95; v5 działami ≈ 0,78, prawdziwe 0,55).
- Składnia tekstu z tarczy: powtórzenia z = 4.6, warianty z = 1.1, słowa niespokrewnione z = -0.3 (rękopis ≈ 10, 9, −1). Długości: korelacja sąsiadów +0.371 (rękopis +0,16), DFA 0.629 (0,60).
- Próbka: ycheey.ychiin.ychchy.ychain.ychody.shechody.sheorar.sheoko.lkeey | sair.qokair.qokaiy.qokshody.qokdey.qolpd.qolps.qolarr.qolaram.qolarody.qolaar | pchedar.qocheey.qochy.olcham.karr.kcher.kas.kan

## Zastrzeżenia

- Tarcza o 3 pierścieniach i komórkach do 3 glifów to jeden z możliwych kształtów urządzenia; inne (więcej pierścieni, nierówne pierścienie) mogą składać więcej.
- Koszt obrotu zależy od ułożenia komórek, które wyszukiwanie dopasowuje do rękopisu; dlatego porównanie z tekstami kontrolnymi, dla których szukano tak samo długo.
- Pokrycie poniżej 100% oznacza słowa, których tarcza nie składa; skryba mógł je dopisywać ręcznie.

## Rada modeli

## Werdykt rady
**Test jest metodologicznie niewiarygodny; hipoteza pozostaje nierozstrzygnięta.** Zgodność jest wysoka co do braku podstaw do uznania wyniku za wiarygodny. Nie ma jednak podstaw, by na tej podstawie obalić wszystkie możliwe warianty hipotezy.

## Co test naprawdę pokazuje
Dla badanej konfiguracji tarczy koszt obrotu wyniósł 0,409 wobec 0,440 dla słów przetasowanych, a pokrycie było niemal identyczne: 83,9% i 83,8%. Bełkot v5 uzyskał lepszy wynik niż rękopis: koszt 0,370 i pokrycie 86,9%. Tekst wygenerowany przez tarczę mieścił się w rozrzucie rękopisu tylko dla 5 z 22 miar. Wyniki te nie dowodzą, że rękopis powstał z tarczy.

## Główne zastrzeżenia
Kontrola przetasowania nie zastępuje kontroli dodatniej: raport nie pokazuje, czy metoda odzyskuje efekt z tekstu celowo wygenerowanego znaną tarczą. Lepsze dopasowanie bełkotu i zbliżone pokrycie przetasowanego tekstu podważają swoistość dopasowania. Ponadto test obejmuje tylko jedną, z góry ograniczoną konfigurację, a wyszukiwanie dopasowuje tarczę do badanych danych. Nie wyklucza to innych konfiguracji, ale też ich nie potwierdza.

## Rekomendowany następny eksperyment
Przeprowadzić ślepą walidację całego potoku: sprawdzić, czy odzyskuje znaną tarczę z tekstu celowo nią wygenerowanego, a nie znajduje podobnego efektu w danych przetasowanych, przy tym samym budżecie wyszukiwania. Ocenę dopasowania należy wykonać także na niewykorzystanych wcześniej wierszach.

## Literatura

- Llull, Ars generalis ultima (1305–1308); Bonner, The Art and Logic of Ramon Llull (2007)
- Timm & Schinner, Cryptologia 44 (2020)

_Czas: 4629 s · 2026-10-24 04:32_