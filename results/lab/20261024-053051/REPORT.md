# Voynich Lab – przebieg 20261024-053051

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Budowa słów jak w mowie: samogłoski Suchotina i wzorce C/V | nierozstrzygnięta | 1/1 | nierozstrzygnięta: 4 |
| Podpis rękopisu w innych transliteracjach | potwierdzona | 0/0 | metoda niewiarygodna: 1, potwierdzona: 1, nierozstrzygnięta: 2 |
| Dopasowanie form słów do języka (NeuroDecipher) | obalona | 50/50 | metoda niewiarygodna: 1, brak przekonującego wsparcia dla hipotez: 1 |
| Atak homofoniczny: wspinaczka z modelem n-gramowym | obalona | 51/51 | metoda niewiarygodna: 1, obalona: 2, potwierdzona: 1 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Budowa słów jak w mowie: samogłoski Suchotina i wzorce C/V

Rękopis (glify): samogłoski o a e y n, naprzemienność 0.80; najbliższy język OldFrench w odległości 0.212 bitów, gdy języki leżą od siebie najdalej 0.294 (mediana 0.109). Rękopis jest tak odosobniony jak najbardziej odosobnione języki (turecki, wietnamski). Bełkot v5 wypada tak samo (najbliżej Lithuanian, 0.222), więc naprzemienność C/V odtwarza także kopiujący skryba.

**Synteza rady:**

## Werdykt rady
**Nierozstrzygnięta, z tendencją negatywną:** test nie dostarcza wiarygodnego dowodu, że wzorce C/V rękopisu odzwierciedlają fonotaktykę mowy. Zgoda jest wysoka co do braku rozstrzygającego wsparcia; różnica dotyczy tego, czy nazwać metodę niewiarygodną, czy wynik nierozstrzygniętym.

## Co test naprawdę pokazuje
Przetasowanie glifów obniżyło naprzemienność C/V z 0,80 do 0,60, więc ta miara reaguje na lokalną strukturę. Jednak według kryterium odległości dane przetasowane nadal mieszczą się w rozrzucie języków (0,142 wobec maksimum 0,294). Rękopis ma odległość 0,212 — powyżej mediany międzyjęzykowej 0,109 — a bełkot v5 daje niemal taki sam wynik: naprzemienność 0,80 i odległość 0,222.

## Główne zastrzeżenia
Kontrole nie spełniają w pełni wymogu wiarygodności: brak kontroli pozytywnej z celowo podłożonym efektem, a przetasowanie nie odrzuca kryterium odległości. Nie wiadomo też, jak wygenerowano bełkot v5. Wyniki zależą od segmentacji: glify i EVA dają różne klasy „samogłosek” i inne najbliższe języki. Wartości naprzemienności nie wspierają wariantu abdżadowego, ale same go rozstrzygająco nie wykluczają. Test nie bada semantyki, morfologii ani sposobu powstania tekstu.

## Następny eksperyment
Przeprowadzić zaślepioną walidację całego, z góry ustalonego kryterium na kontrolach dopasowanych długością i częstością znaków: z celowo podłożoną fonotaktyką oraz z danymi przetasowanymi. Metoda powinna wykryć pierwsze i nie kwalifikować drugich.

Szczegóły: [phonotactics.md](phonotactics.md)

## Podpis rękopisu w innych transliteracjach

Podpis trzyma w 4/4 pełnych transliteracjach: ZL tak, IT tak, CD nie (częściowa), FG tak, GC tak.

**Synteza rady:**

## Werdykt rady

**Hipoteza nie została potwierdzona; metoda nie jest dostatecznie zwalidowana.** Zgoda jest wysoka co do tego, że automatyczny werdykt „potwierdzona” nie wynika z przedstawionych dowodów. To nie oznacza, że hipoteza jest fałszywa.

## Co test naprawdę pokazuje

W czterech pełnych transliteracjach raportuje się nadmiar powtórzeń i wariantów oraz dodatnią korelację długości sąsiednich słów. Są to powtarzające się sygnały opisowe, ale nie dowodzą, że podpis jest własnością rękopisu, a nie sposobu jego transkrypcji.

## Główne zastrzeżenia

- Nie przedstawiono wymaganych kontroli: wykrycia celowo podłożonego efektu ani niewykrywania go w danych przetasowanych. Podane porównania z tasowaniami nie zastępują walidacji całej metody.
- ZL jest punktem odniesienia dla miar kształtu, więc jego wartości *z* = 0 nie są niezależnym potwierdzeniem.
- Transliteracje nie są niezależnymi świadkami: ZL i Takahashi są w pełni zgodne tylko w około 29% wierszy. Część miar dla różnych alfabetów nie jest wprost porównywalna.
- Składnik dotyczący słów niespokrewnionych nie jest spójny między transliteracjami, a częściowe CD wyłączono bez podanego wcześniej kryterium.

## Rekomendowany następny eksperyment

Zweryfikować cały pipeline na kontrolach dodatnich i ujemnych: ma wykrywać efekt podłożony celowo i nie wykrywać go w danych przetasowanych, przy tych samych regułach segmentacji i tokenizacji.

Szczegóły: [transcriptions.md](transcriptions.md)

## Dopasowanie form słów do języka (NeuroDecipher)

Tropy: brak; 50 języków testowalnych, 2 nietestowalnych. Największa przewaga nad bełkotem: Syriac (rękopis 85% słów o najwyżej jedną zmianę od słownika, bełkot 74%).

**Synteza rady:**

## Werdykt rady
**Brak przekonującego wsparcia dla hipotezy w badanym zakresie, ale jej obalenie nie jest uzasadnione.** Metoda nie spełnia wymogu wiarygodności, ponieważ raport nie przedstawia kontroli na danych przetasowanych.

## Poziom zgody
Po początkowych różnicach opinie zbiegły się co do kluczowego zastrzeżenia: samych kontroli dodatnich nie wystarcza do uznania testu za wiarygodny. Nie ma podstaw do kategorycznego werdyktu „obalona”.

## Co test naprawdę pokazuje
W 50 językach testowalnych kontrole dodatnie odzyskały klucz w 94–100% znaków, powyżej progu 60%. W wynikach rękopisu nie zgłoszono tropów. Najwyższy podany wynik, dla Syriac, to 85% słów w odległości najwyżej jednej zmiany od słownika wobec 74% dla bełkotu v5. To nie wykazuje przekonującego dopasowania, ale bez rozkładu wyników tła nie wiadomo, czy różnica jest istotna.

Test dotyczy stałego klucza glif–litera dla testowalnych języków. Nie rozstrzyga hipotez spoza tego modelu ani wyników dla dwóch języków nietestowalnych.

## Główne zastrzeżenia
Brak kontroli ujemnej na danych przetasowanych i rozkładu wielu realizacji tła. Ponadto sekcja dowodów jest niepełna, więc nie można ocenić wszystkich porównań językowych. Kryterium „o jedną zmianę” daje wysokie tło.

## Rekomendowany następny eksperyment
Uruchomić niezmieniony pipeline na wielu przetasowanych wersjach danych oraz wielu realizacjach bełkotu, podać rozkład wyników i pozycję wyniku Syriac względem tych rozkładów.

Szczegóły: [cognate.md](cognate.md)

## Atak homofoniczny: wspinaczka z modelem n-gramowym

Tropy: brak; 51 języków testowalnych, 1 nietestowalnych. Najbliżej tekstu naturalnego: OldFrench (4.01 wobec 3.85 bit/znak; bełkot 3.96).

**Synteza rady:**

## Werdykt rady

**Test jest niewiarygodny jako podstawa kategorycznego obalenia hipotezy.** Wynik jest niekorzystny dla badanej wersji prostego szyfru homofonicznego, ale nie spełniono wymogu kontroli ujemnej na danych przetasowanych.

**Poziom zgody:** wysoki co do braku tej kontroli i konieczności odrzucenia automatycznego werdyktu „obalona”; opinie różnią się, jak mocno interpretować niekorzystny wynik.

### Co test pokazuje

Kontrole dodatnie wskazują, że wspinacz odzyskiwał klucz w testowanych zaszyfrowanych tekstach: zwykle w 100% znaków, w najniższych podanych przypadkach w 88–94%. W rękopisie nie uzyskano tropu; najbliższy wynik OldFrench (4,01 bitu/znak) jest bliski bełkotowi v5 (3,96), a gorszy od wartości naturalnego tekstu (3,85). To przemawia przeciw badanej metodzie szyfrowania, ale nie rozstrzyga sprawy bez pełnej walidacji.

### Główne zastrzeżenia

Brak wyników kontroli na danych przetasowanych oznacza, że nie wiadomo, czy pipeline daje fałszywe trafienia. Nie podano też, który leksykon był nietestowalny ani dlaczego. Raport nie wykazuje, że kontrole dodatnie dopasowano długością i strukturą do badanego materiału. Test nie obejmuje innych typów szyfrów ani języków spoza testowanego zestawu.

### Rekomendowany eksperyment

Powtórzyć pełny pipeline na kontrolach dodatnich o długości i strukturze dopasowanej do rękopisu oraz na odpowiadających im danych przetasowanych; z góry ustalić kryterium trafienia i podać wyniki dla wszystkich leksykonów.

Szczegóły: [hillclimb.md](hillclimb.md)

Koszt OpenRouter: 0.07 USD w 59 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.