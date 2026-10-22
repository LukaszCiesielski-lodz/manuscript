# basque: obalona

**Hipoteza.** Rękopis to tekst baskijski zapisany szyfrem podstawieniowym (prostym lub homofonicznym).

**Metoda.** Dwa teksty baskijskie: Nowy Testament Leizarragi (1571, oryginalna pisownia) i współczesna prasa (UD Basque-BDT). Dla każdego: łamacz szyfru z kontrolami na zaszyfrowanym baskijskim, odległość odcisku palca od rękopisu na tle 13 języków, powtórzenia słów.

Szyfr podstawieniowy z baskijskiego: luka 0.95–1.12 bita/znak przy kontrolach bliskich zera; baskijski 3. na 13 języków pod względem podobieństwa do rękopisu.

## Kontrole

- ✅ **Leizarraga 1571: szyfr prosty**: oczekiwano łamacz odzyskuje ≥ 90% liter; wynik: 100.0%, luka -0.00
- ✅ **Leizarraga 1571: szyfr homofoniczny**: oczekiwano łamacz odzyskuje ≥ 90% liter; wynik: 100.0%, luka -0.03
- ✅ **prasa współczesna: szyfr prosty**: oczekiwano łamacz odzyskuje ≥ 90% liter; wynik: 100.0%, luka +0.00
- ✅ **prasa współczesna: szyfr homofoniczny**: oczekiwano łamacz odzyskuje ≥ 90% liter; wynik: 99.9%, luka -0.02

## Dowody

- Leizarraga 1571: rękopis zostawia lukę +1.12 bita/znak (kontrole ~0); odległość od rękopisu 2.50; h2 3.17 (rękopis 2.30), średnia długość słowa 6.1 (4.3), hapaksy 49% (69%), powtórzenia słów 0.05% (0.83%).
- prasa współczesna: rękopis zostawia lukę +0.95 bita/znak (kontrole ~0); odległość od rękopisu 2.82; h2 3.22 (rękopis 2.30), średnia długość słowa 6.4 (4.3), hapaksy 66% (69%), powtórzenia słów 0.07% (0.83%).
- Ranking odległości od rękopisu wśród 13 języków: baskijski na miejscu 3 (Vietnamese 2.10, German 2.30, Basque 2.50, English 2.53...).

## Zastrzeżenia

- Wyklucza tylko szyfr podstawieniowy litera-za-glif; nie bada szyfrów sylabicznych ani zapisu gubiącego rozróżnienia głosek.
- Baskijski z XV wieku nie zachował się w piśmie (pierwsza książka: 1545); Leizarraga 1571 to najbliższe dostępne przybliżenie.
- Tekst biblijny baskijski to Nowy Testament, inne języki zaczynają się od Księgi Rodzaju.

## Rada modeli

## Werdykt rady
**Wynik nie wystarcza do uznania hipotezy za obaloną**, ponieważ raport nie przedstawia kontroli na danych przetasowanych. Test dostarcza jednak wyraźnych przesłanek przeciw **prostemu lub homofonicznemu szyfrowi podstawieniowemu** z badanych korpusów baskijskich.

## Poziom zgody
Zgoda jest **wysoka co do wyników i ograniczonego zakresu wniosku**, lecz umiarkowana co do werdyktu: część ocen uznaje hipotezę za obaloną w zbadanym zakresie, część podkreśla brak pełnej walidacji metody.

## Co test naprawdę pokazuje
Kontrole pozytywne przeszły we wszystkich czterech wariantach: odzyskano 99,9–100% liter, przy lukach bliskich zeru. Dla rękopisu luka wynosiła 0,95–1,12 bita/znak. To przemawia przeciw badanemu typowi szyfru. Ranking odległości nie stanowi mocnego argumentu za baskijskim: zajmuje on 3. miejsce na 13 języków.

## Główne zastrzeżenia
Brakuje kontroli negatywnej na danych przetasowanych, wymaganej do pełnego potwierdzenia wiarygodności metody. Korpusy są ograniczone: tekst z 1571 r. i współczesna prasa nie zastępują baskijskiego z epoki rękopisu, a porównania mogą być obciążone różnicami gatunkowymi. Test nie obejmuje innych sposobów szyfrowania ani zapisu.

## Następny eksperyment
Powtórzyć **niezmienioną procedurę** z kontrolą negatywną na przetasowanych danych, zachowując kontrolę pozytywną z zaszyfrowanym baskijskim.

## Literatura

- Leizarraga, Iesus Christ gure Iaunaren Testamentu Berria (La Rochelle, 1571), via christos-c/bible-corpus
- Universal Dependencies Basque BDT treebank (Aranzabe i in.)
- Bowern & Lindemann, Annual Review of Linguistics 7 (2021)

_Czas: 280 s · 2026-10-22 18:52_