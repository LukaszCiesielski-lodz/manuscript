# genres: nierozstrzygnięta

**Hipoteza.** Rękopis to tekst gatunku, który z natury nie ma składni między słowami: litania (stała rama, zmienne imię) albo „imiona barbarzyńskie” ksiąg magicznych (ciągi bez znaczenia z echami i wariantami).

**Metoda.** Litania do Wszystkich Świętych (la.wikisource) i imiona z Ars Notoria i Liber Iuratus (Esoteric Archives) mierzone jak rękopis: zależność na odległość rozbita na powtórzenia, warianty i słowa niespokrewnione; dynamika długości słów (korelacja sąsiadów, DFA); miary kształtu z karty. Porównanie z rękopisem i łaciną.

Gatunki o podpisie jak rękopis (brak składni, nadmiar powtórzeń, podobne długości sąsiadów): żaden z badanych. rękopis: niespokrewnione z = -1.2, powtórzenia z = 9.6; łacina (Biblia): niespokrewnione z = 12.7, powtórzenia z = -0.5; litany: niespokrewnione z = 60.3, powtórzenia z = 5.9; voces_magicae: niespokrewnione z = 3.6, powtórzenia z = 4.8

## Kontrole


## Dowody

- rękopis (34820 słów): powtórzenia z = 9.6, warianty z = 5.1, słowa niespokrewnione z = -1.2; długości: korelacja sąsiadów +0.159, DFA 0.598; kształt (z wobec rękopisu): entropia warunkowa h₂ +0.8, słowa użyte raz (hapaksy) +0.4, gęstość słownika +0.5, sąsiednie słowa różne o 1 glif +1.5, sztywne miejsca glifów w słowie -1.1, różne słowa / wszystkie +0.0.
- łacina (Biblia) (34820 słów): powtórzenia z = -0.5, warianty z = 1.3, słowa niespokrewnione z = 12.7; długości: korelacja sąsiadów -0.110, DFA 0.518; kształt (z wobec rękopisu): entropia warunkowa h₂ +5.9, słowa użyte raz (hapaksy) -4.7, gęstość słownika -27.9, sąsiednie słowa różne o 1 glif -4.5, sztywne miejsca glifów w słowie -5.0, różne słowa / wszystkie -1.0.
- litany (1661 słów): powtórzenia z = 5.9, warianty z = -2.2, słowa niespokrewnione z = 60.3; długości: korelacja sąsiadów -0.047, DFA 0.517; kształt (z wobec rękopisu): entropia warunkowa h₂ +3.1, słowa użyte raz (hapaksy) +2.3, gęstość słownika -40.2, sąsiednie słowa różne o 1 glif -4.9, sztywne miejsca glifów w słowie -4.8, różne słowa / wszystkie -1.8.
- voces_magicae (1479 słów): powtórzenia z = 4.8, warianty z = -0.2, słowa niespokrewnione z = 3.6; długości: korelacja sąsiadów +0.225, DFA 0.768; kształt (z wobec rękopisu): entropia warunkowa h₂ +6.2, słowa użyte raz (hapaksy) +9.7, gęstość słownika -41.9, sąsiednie słowa różne o 1 glif -4.1, sztywne miejsca glifów w słowie -2.0, różne słowa / wszystkie +10.4.

## Zastrzeżenia

- Teksty gatunkowe są krótkie (litania ok. 1,5 tys. słów), więc ich z są z natury mniejsze.
- Imiona wydobyto heurystycznie z wydań angielsko-łacińskich; część to zwykłe słowa.
- Lingua Ignota Hildegardy (1011 słów, sam słownik) nie weszła: nie ma tekstu, tylko listę.

## Rada modeli

## Werdykt rady
**Metoda niewiarygodna w obecnym raporcie; hipoteza pozostaje nierozstrzygnięta.** Kontrole wymagane do uznania testu za wiarygodny nie zostały opisane, więc nie można oprzeć rozstrzygnięcia na podanych miarach.

## Zgodność
Wysoka: niezależne oceny różniły się początkowo werdyktem, ale w rundzie 2 zgodnie uznały brak kontroli za kluczowy problem i odrzuciły wniosek, że hipoteza jest obalona.

## Co test naprawdę pokazuje
Opisowo, żaden z badanych korpusów nie odtwarza łącznie profilu rękopisu: np. „słowa niespokrewnione” mają z = −1,2 w rękopisie, 60,3 w litanii i 3,6 w voces_magicae. To wskazuje na różnice między konkretnymi próbkami, ale bez walidacji metody nie stanowi wiarygodnego wykluczenia nawet tych porównań. Test nie rozstrzyga o całej klasie tekstów bez składni.

## Główne zastrzeżenia
Pusta sekcja kontroli metody; krótkie korpusy gatunkowe; heurystyczne wydobycie imion z możliwym zanieczyszczeniem zwykłymi słowami; ograniczenie do niewielu źródeł. Pominięcie listy słownikowej nie jest samo w sobie rozstrzygające, bo nie jest tekstem do porównania tych miar.

## Następny eksperyment
Powtórzyć analizę po ustaleniu protokołu kontroli: wykazać, że miary wykrywają celowo wszczepiony efekt i nie wykrywają go w tych samych danych po przetasowaniu.

## Literatura

- Ars Notoria (ed. Turner 1657; Esoteric Archives)
- Liber Iuratus Honorii (Esoteric Archives)
- Litaniae Sanctorum

_Czas: 78 s · 2026-10-24 04:37_