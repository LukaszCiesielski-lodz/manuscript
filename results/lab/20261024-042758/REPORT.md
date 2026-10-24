# Voynich Lab – przebieg 20261024-042758

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Gatunki średniowieczne bez składni: litania, imiona magiczne | nierozstrzygnięta | 0/0 | nierozstrzygnięta: 1, metoda niewiarygodna: 3 |
| Tarcza Lullusa (volvelle) jako urządzenie piszące | nierozstrzygnięta | 1/1 | nierozstrzygnięta: 1, metoda niewiarygodna: 1 |
| Transformer-sędzia: prawdziwe vs wygenerowane | obalona | 1/1 | nierozstrzygnięta: 1, metoda niewiarygodna: 1, obalona: 1 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Gatunki średniowieczne bez składni: litania, imiona magiczne

Gatunki o podpisie jak rękopis (brak składni, nadmiar powtórzeń, podobne długości sąsiadów): żaden z badanych. rękopis: niespokrewnione z = -1.2, powtórzenia z = 9.6; łacina (Biblia): niespokrewnione z = 12.7, powtórzenia z = -0.5; litany: niespokrewnione z = 60.3, powtórzenia z = 5.9; voces_magicae: niespokrewnione z = 3.6, powtórzenia z = 4.8

**Synteza rady:**

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

Szczegóły: [genres.md](genres.md)

## Tarcza Lullusa (volvelle) jako urządzenie piszące

Najlepsza tarcza składa 84% słów rękopisu przy koszcie obrotu 0.41 (przetasowane 0.44, łacina 0.84, bełkot v5 0.37). Tekst pisany tarczą: 5/22 miar, AUC 0.99.

**Synteza rady:**

## Werdykt rady
**Test jest metodologicznie niewiarygodny; hipoteza pozostaje nierozstrzygnięta.** Zgodność jest wysoka co do braku podstaw do uznania wyniku za wiarygodny. Nie ma jednak podstaw, by na tej podstawie obalić wszystkie możliwe warianty hipotezy.

## Co test naprawdę pokazuje
Dla badanej konfiguracji tarczy koszt obrotu wyniósł 0,409 wobec 0,440 dla słów przetasowanych, a pokrycie było niemal identyczne: 83,9% i 83,8%. Bełkot v5 uzyskał lepszy wynik niż rękopis: koszt 0,370 i pokrycie 86,9%. Tekst wygenerowany przez tarczę mieścił się w rozrzucie rękopisu tylko dla 5 z 22 miar. Wyniki te nie dowodzą, że rękopis powstał z tarczy.

## Główne zastrzeżenia
Kontrola przetasowania nie zastępuje kontroli dodatniej: raport nie pokazuje, czy metoda odzyskuje efekt z tekstu celowo wygenerowanego znaną tarczą. Lepsze dopasowanie bełkotu i zbliżone pokrycie przetasowanego tekstu podważają swoistość dopasowania. Ponadto test obejmuje tylko jedną, z góry ograniczoną konfigurację, a wyszukiwanie dopasowuje tarczę do badanych danych. Nie wyklucza to innych konfiguracji, ale też ich nie potwierdza.

## Rekomendowany następny eksperyment
Przeprowadzić ślepą walidację całego potoku: sprawdzić, czy odzyskuje znaną tarczę z tekstu celowo nią wygenerowanego, a nie znajduje podobnego efektu w danych przetasowanych, przy tym samym budżecie wyszukiwania. Ocenę dopasowania należy wykonać także na niewykorzystanych wcześniej wierszach.

Szczegóły: [wheel.md](wheel.md)

## Transformer-sędzia: prawdziwe vs wygenerowane

Prawdziwe vs prawdziwe: AUC 0.54. Transformer odróżnia każdy generator od rękopisu: v4 (kopiowanie ze zmianami) 0.97, v5 działami (tabela skryby) 0.64, łańcuch słów (pamięć 1) 0.61, tarcza (volvelle) 0.97.

**Synteza rady:**

## Werdykt rady
**Metoda niewiarygodna w świetle przyjętych kryteriów; hipoteza pozostaje nierozstrzygnięta.** Kontrola prawdziwe–prawdziwe przeszła (AUC 0,539), ale raport nie przedstawia kontroli wykrywającej efekt celowo podłożony ani kontroli na danych przetasowanych.

## Poziom zgody
Opinie początkowe różniły się co do werdyktu. W późniejszej rundzie silniej wybrzmiało, że brak wymaganych kontroli nie pozwala uznać metody za wiarygodną ani automatycznie obalić hipotezy.

## Co test naprawdę pokazuje
Dla czterech przetestowanych generatorów transformer uzyskał AUC od 0,613 do 0,971; wyniki dwóch generatorów były znacznie wyższe. Klasyfikator n-gramowy także odróżniał wszystkie cztery. To przemawia przeciw nieodróżnialności **tych konkretnych generatorów**, ale nie rozstrzyga hipotezy o którymkolwiek generatorze bez treści.

## Główne zastrzeżenia
Brak wymaganych kontroli uniemożliwia ocenę czułości metody i jej zachowania po przetasowaniu. Brak przedziałów niepewności oraz wybór najlepszej epoki mogą zawyżać wyniki; najniższe AUC są bliskie poziomowi losowemu. Test obejmuje tylko cztery generatory i ciągi EVA, nie układ strony ani rysunki.

## Rekomendowany następny eksperyment
Powtórzyć test na niezależnych podziałach danych, z kontrolą dodatnią (celowo podłożony efekt), kontrolą przetasowaną i przedziałami niepewności; szczególną uwagę poświęcić dwóm generatorom z najniższym AUC.

Szczegóły: [adversary.md](adversary.md)

Koszt OpenRouter: 0.05 USD w 47 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.