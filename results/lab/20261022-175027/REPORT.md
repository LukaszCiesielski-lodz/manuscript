# Voynich Lab – przebieg 20261022-175027

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Znaki to liczby | obalona | 5/5 | obalona: 1, nierozstrzygnięta: 3 |
| Szyfr Naibbe (Greshko 2025) | obalona | 2/2 | metoda niewiarygodna: 1, obalona: 1, nierozstrzygnięta: 2 |
| Bełkot z kratki Cardana (Rugg 2004) | obalona | 1/1 | metoda niewiarygodna: 1, obalona: 1, nierozstrzygnięta: 1 |
| Hebrajskie anagramy (Hauer i Kondrak 2016) | metoda niewiarygodna | 1/2 | metoda niewiarygodna: 3, metoda nie dostarcza wiarygodnego, swois: 1 |
| Baskijski pod szyfrem podstawieniowym | obalona | 4/4 | obalona: 3 |
| Klucz w ilustracjach | nierozstrzygnięta | 4/4 | nierozstrzygnięta: 4 |
| AI generuje brakujące strony | obalona | 2/2 | obalona: 3 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Znaki to liczby

Cały tekst jako liczby: nie pasuje (najbliższy system: alfabetyczny (grecki/hebrajski), odległość 1.73; dopasowanie wymaga < 0.5, dwie próbki łaciny różnią się o ok. 0,2). Etykiety zodiaku jako kolejne liczby: nie (efekt 2.1% przy p = 0.051; liczby podłożone dają ≥ 16%, zwykły tekst rękopisu 1.3%).

**Synteza rady:**

## Werdykt rady

**Nierozstrzygnięta w szerokim ujęciu; badane warianty nie znajdują wsparcia.** Zgodność jest wysoka co do tego rozróżnienia: trzy z czterech opinii końcowych uznały szeroką hipotezę za nierozstrzygniętą, a wszystkie wskazały brak mocnego wsparcia dla testowanych zapisów.

## Co test pokazuje

Porównanie całego tekstu z pięcioma badanymi systemami liczbowymi nie dało dopasowania: najbliższa odległość wyniosła 1,73, wobec progu <0,5. Dla etykiet zodiaku efekt podobieństwa sąsiadów był mały (2,1%; p=0,0506), zbliżony do tła zwykłego tekstu (1,3%) i znacznie niższy niż w kontrolach z podłożonymi liczbami (co najmniej 16%).

Kontrole wykazały, że metoda wykrywała podłożone ciągi (p=0,0003), a w 20 przetasowanych zestawach nie dawała fałszywych alarmów. Wspierają więc wiarygodność testu **dla sprawdzonych wariantów**, nie zaś dla każdego możliwego zapisu liczb.

## Główne zastrzeżenia

Wynik zależy od założonego rozkładu liczb, a test etykiet — od zgodności kolejności transliteracji z kolejnością przestrzenną. Nie badano szyfru homofonicznego. Kalibracja przetasowań obejmowała tylko 20 zestawów. Wyniki nie wykluczają zatem wszystkich sposobów zapisywania liczb.

## Rekomendowany następny eksperyment

Przeprowadzić prerejestrowany test etykiet w niezależnie zweryfikowanej kolejności przestrzennej, obejmujący wiarygodne warianty zapisu homofonicznego oraz kontrole z podłożonymi i przetasowanymi danymi; metoda powinna wykrywać podłożenia, a nie wykrywać efektu w przetasowaniach.

Szczegóły: [numbers.md](numbers.md)

## Szyfr Naibbe (Greshko 2025)

Szyfr Naibbe-podobny: odległość 0.83, różnica hapaksów 20%. Literatura: Naibbe odtwarza entropię i rozkład długości, ale nie hapaksy (41% wobec 70%).

**Synteza rady:**

## Werdykt rady
**Nierozstrzygnięte.** Automatycznego werdyktu „obalona” nie uznajemy za wiarygodnie wykazanego.

## Poziom zgody
Wysoki: wszystkie oceny po dyskusji uznały, że brak kluczowych kontroli uniemożliwia rozstrzygający wniosek.

## Co test naprawdę pokazuje
W tej rekonstrukcji szyfru Naibbe wyniki różnią się od rękopisu m.in. pod względem hapaksów (49% wobec 70%), MI krawędzi (0,012 wobec 0,168) i podobnych sąsiadów (2,4% wobec 5,0%). Entropia h2 jest natomiast zbliżona. To przemawia przeciw **badanej rekonstrukcji**, ale samo nie obala całej klasy szyfrów Naibbe.

## Główne zastrzeżenia
Nie wykazano, że metoda wykrywa celowo podłożony efekt ani że nie znajduje go w danych przetasowanych. Kontrole rozpoznania języka i odwracalności tego nie sprawdzają. Ponadto użyto rekonstrukcji tabel, jednego tekstu jawnego, a odległość 0,83 nie ma podanej kalibracji ani progu decyzyjnego.

## Rekomendowany następny eksperyment
Zastosować tę samą, z góry ustaloną procedurę do wielu szyfrogramów Naibbe utworzonych z różnych tekstów łacińskich oraz do danych przetasowanych. Test powinien wykrywać efekt w próbkach Naibbe i nie wykrywać go w przetasowanych; dopiero wtedy porównanie z rękopisem może wspierać rozstrzygający wniosek.

Szczegóły: [naibbe_cipher.md](naibbe_cipher.md)

## Bełkot z kratki Cardana (Rugg 2004)

Kratka Cardana: odległość 2.44, różnica hapaksów 51%.

**Synteza rady:**

## Werdykt rady
**Hipoteza nieobalona rzetelnie; test jest niewiarygodny jako rozstrzygający.** Automatyczny werdykt „obalona” wykracza poza to, co uzasadnia raport.

## Poziom zgody
Wysoki: w drugiej rundzie wszyscy wskazali brak kluczowych kontroli i ograniczenia wnioskowania, choć opinie różniły się akcentami.

## Co test naprawdę pokazuje
Jedna symulacja kratki z trzema otworami nie odtworzyła kilku cech rękopisu: hapaksy wyniosły 19% wobec 70%, MI krawędzi 0,001 wobec 0,168, a odległość profilu 2,44. To przemawia przeciw **tej konkretnej symulacji**, ale nie rozstrzyga całej hipotezy.

## Główne zastrzeżenia
Kontrola rozpoznawania łaciny nie sprawdza, czy metoda wykrywa efekt kratki ani czy odrzuca dane przetasowane. Nie podano też kalibracji odległości ani rozkładu odniesienia. Tabela fragmentów i ich częstości pochodziły z samego rękopisu, a test nie objął innych konfiguracji kratki. Zatem raport nie pozwala ustalić, czy niezgodność wynika z hipotezy, czy z przyjętej implementacji.

## Rekomendowany następny eksperyment
Przeprowadzić z góry określony, zaślepiony test kalibracyjny: sprawdzić, czy metoda wykrywa kratkę w danych wygenerowanych z celowo podłożonym efektem i nie wykrywa jej w danych przetasowanych, z tabelą fragmentów niezależną od rękopisu.

Szczegóły: [cardan_grille.md](cardan_grille.md)

## Hebrajskie anagramy (Hauer i Kondrak 2016)

Atak anagramowy daje rękopisowi 69.0%, ale NIE jest swoisty: tekst Vietnamese osiąga 90.8% przy 72.2% dla prawdziwego hebrajskiego. Wysokie pokrycie bierze się z powtarzalności krótkich słów, nie z hebrajskiego.

**Synteza rady:**

## Werdykt rady
**Metoda niewiarygodna jako swoisty test hipotezy „hebrew_anagram”.** Zgoda jest pełna: wszyscy czterej recenzenci uznali, że kontrola swoistości nie przeszła.

## Co test naprawdę pokazuje
Kontrola dodatnia zadziałała: zaszyfrowany, zanagramowany hebrajski osiągnął 72,2% przy wymaganym minimum 50%. Swoistość jednak zawiodła: wietnamski uzyskał 90,8%, angielski 73,7%, a rękopis 69,0%. Wynik rękopisu jest też bliski wynikowi szyfru Naibbe-podobnego (65,2%). Zatem ta metoda nie odróżnia wiarygodnie hebrajskiego od danych niehebrajskich. **Nie rozstrzyga to, czy rękopis ma hebrajskie podłoże** — podważa wartość dowodową tego testu.

## Główne zastrzeżenia
Kontrolę hebrajską oparto na Biblii, nie na tekście średniowiecznym. Raport wskazuje też na przypadkowe trafienia krótkich słów; dodatkowo klucz przypisuje wiele różnych glifów do tych samych liter. Te ograniczenia mogą wpływać na pokrycie słownikiem.

## Rekomendowany następny eksperyment
Przeprowadzić z góry określony test porównawczy, zachowując w kontrolach rozkład glifów i długości słów rękopisu, ale losowo zmieniając ich przyporządkowanie do słów. Sprawdzić, czy oryginał wyraźnie przewyższa takie kontrole, zachowując kontrolę dodatnią z celowo zaszyfrowanym hebrajskim.

Szczegóły: [hebrew_anagram.md](hebrew_anagram.md)

## Baskijski pod szyfrem podstawieniowym

Szyfr podstawieniowy z baskijskiego: luka 0.95–1.12 bita/znak przy kontrolach bliskich zera; baskijski 3. na 13 języków pod względem podobieństwa do rękopisu.

**Synteza rady:**

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

Szczegóły: [basque.md](basque.md)

## Klucz w ilustracjach

Test sprawdza warunek konieczny klucza w ilustracjach: czy tekst w ogóle zależy od rysunku. C: 20 stron, nazwy od qwen/qwen2.5-vl-72b-instruct. Dopasowanie 0.40 wobec średnio 0.33 dla nazw przetasowanych, p = 0.040. B: 121 stron zielnika. Korelacja podobieństwa obrazów i słownictwa r = 0.083, p = 0.0712 (permutacje w obrębie skryby i języka).

**Synteza rady:**

## Werdykt rady: **nierozstrzygnięta**

**Zgodność:** pełna — wszyscy oceniający uznali, że raport nie uzasadnia ani przyjęcia, ani odrzucenia hipotezy.

**Co test naprawdę pokazuje:** opisane kontrole metody przeszły: procedury wykrywały efekty podłożone celowo i nie wykrywały losowych podobieństw. Test A wykazał niewielką różnicę długości słów przy przerwach na rysunki (−0,24 glifu; *p* = 0,0003), ale sam nie dowodzi zależności treści tekstu od ilustracji. W teście B związek podobieństwa obrazów i słownictwa był słaby i nie osiągnął istotności (*r* = 0,083; *p* = 0,0712). Nie oznacza to jednak, że związek nie istnieje. Test C dał słaby dodatni sygnał (*p* = 0,040), lecz dotyczył 20 stron i zależał od niepewnych nazw oraz konkretnego założenia o sposobie zapisu.

**Główne zastrzeżenia:** CLIP analizował strony wraz z pismem, więc wynik B może być zaburzony układem tekstu. Test C jest mały i wąski; zaliczenie jego kontroli potwierdza działanie metody w kontroli, nie poprawność identyfikacji ani hipotezy. Żaden z wyników nie wykazuje, że ilustracje stanowią klucz.

**Następny eksperyment:** powtórzyć test B na większej, z góry ustalonej próbie, używając obrazów po zamaskowaniu tekstu oraz tych samych permutacji uwzględniających skrybę i język Curriera.

Szczegóły: [illustrations.md](illustrations.md)

## AI generuje brakujące strony

Transformer: 1.70 bit/znak wobec 2.02 dla trigramów. Wygenerowane strony nie są nieodróżnialne od prawdziwych (AUC 0.83, odległość 1.00). Brakujące strony zapisano jako SYNTETYCZNE.

**Synteza rady:**

## Werdykt rady

**Hipoteza obalona w odniesieniu do badanego transformera i przyjętych atrybutów stron.** Wygenerowane strony nie były statystycznie nieodróżnialne od prawdziwych: klasyfikator osiągnął AUC **0,826**, a miara odległości wyniosła **0,995**. Opinie są zgodne co do werdyktu.

## Co test pokazuje

Obie kontrole klasyfikatora przeszły: prawdziwe–prawdziwe dało AUC **0,492**, a prawdziwe–prosty generator samocytowania **1,000**. Wspiera to wiarygodność wyniku dla zastosowanego testu, ale nie dowodzi, że klasyfikator wykrywa każdy rodzaj różnicy. Transformer uzyskał też lepszy wynik predykcji od trigramów (**1,702 wobec 2,016 bitu/znak**), co nie wystarczyło do uzyskania stron nieodróżnialnych.

Test **nie ustala treści ani istnienia zaginionych stron** i nie wyklucza, że inny model generatywny poradziłby sobie lepiej.

## Główne zastrzeżenia

Atrybuty działu i skryby przypisano na podstawie sąsiednich stron. Raport nie podaje przedziałów ufności dla AUC ani szczegółowej kalibracji miary odległości; porównanie z łaciną opiera się tylko na dwóch próbkach. Kontrole sprawdzają klasyfikator na określonych przypadkach, nie na wszystkich możliwych różnicach.

## Rekomendowany następny eksperyment

Powtórzyć generację z **mocniejszym modelem**, dobierając zatrzymanie na walidacji, przy lepiej uzasadnionych atrybutach stron. Ocenić wyniki z przedziałami ufności i kontrolami klasyfikatora na wielu odłożonych stronach.

Szczegóły: [generative.md](generative.md)

## Polowanie psów gończych

Przetestowano 21 przepisów; tropy (TROP): 0.

| przepis | pies | werdykt | score | luka rękopisu |
|---|---|---|---|---|
| Drugi glif rdzeniem, reszta wypełniaczem | kryptolog | obalony | +0.04 | 0.92 |
| Szkielet co 4. z offsetem 1 i abdżad łaciński | dziki pies | obalony | -0.01 | 0.60 |
| Szablonowe wypełnianie (co 3. glif to rdzeń) | dziki pies | obalony | -0.02 | 0.98 |
| Pary glifów jako znaki szyfru rozwlekłego | lingwista | obalony | -0.05 | 0.75 |
| Akrostych inicjałów, cały tekst | kryptolog | obalony | -0.15 | 0.53 |
| Odwrócenie glifów w każdym słowie | lingwista | obalony | -0.20 | 1.29 |
| q i n jako nulle, pismo od prawej | kryptolog | obalony | -0.26 | 1.27 |
| Nulle q i e, potem rotacja słowa | kryptolog | obalony | -0.27 | 1.18 |
| Odwrócenie kolejności słów w wierszu | lingwista | obalony | -0.35 | 1.28 |
| Hebrajski zapis spółgłoskowy | lingwista | obalony | -0.42 | 1.36 |

## Podsumowanie czterech rund

Sfora sprawdziła podstawienia i liczne proste przekształcenia glifów, słów oraz wierszy, głównie z celem odczytu w językach naturalnych. Wyniki zestawiano z bełkotem o podobnych statystykach i wymagano także przejścia kontroli dodatniej.

**Żaden trop nie przetrwał kontroli jako wiarygodny odczyt.** Najwyższy wynik ma przewagę zaledwie **+0,04 bita/znak** nad bełkotem, lukę 0,92 i nieudany wynik kontroli dodatniej. To daleko od progu TROP. Powtórka najlepszych tropów na innej części rękopisu nie dała żadnych wyników: `[]`.

## Co można uznać za martwe

- Proste i homofoniczne podstawienia badanych języków — obalone przez dużą lukę entropii.
- Testowane warianty: wyciąganie glifów, usuwanie q/n, odwracanie, akrostychy, grupowanie par, klucze strumieniowe i praca na słowach — nie wykazały przewagi nad bełkotem albo nie przeszły kontroli dodatniej.
- Kratka Cardana została obalona; atak anagramowy z hebrajskim okazał się nieswoisty.
- Naibbe-podobny szyfr odtwarza entropię, ale nie wyjaśnia zależności na styku słów.

Nie oznacza to obalenia wszystkich szyfrów ani wszystkich hipotez o niejęzykowym zapisie.

## Co warto rozwijać

Dane wskazują na zjawiska, których dotychczasowe przepisy słabo obejmowały: sztywne pozycje glifów, zależności między sąsiednimi słowami i ich stykami oraz strukturę wiersza. Nowe testy powinny mierzyć te cechy, a nie tylko dopasowywać entropię.

## Klocki do dodania najpierw

1. **Nomenklator słowo-za-słowo** oraz wariant hybrydowy: stałe kody częstych słów, osobny mechanizm dla reszty.
2. **Mapowanie całego słowa na symbol** i operacje warunkowe zależne od pozycji glifu lub jego miejsca w wierszu.
3. **Transformacje międzywierszowe** z kluczem pochodzącym z poprzedniego wiersza; testować szczególnie bezpośrednio zależności końcówek i początków wierszy.

Hipotezy o kształcie glifów wymagają danych obrazowych; kalendarze i logografy warto odłożyć, dopóki nie da się sformułować dla nich testów rozróżniających je od bełkotu.

Szczegóły: [hunt/hunt.md](hunt/hunt.md)

Koszt OpenRouter: 0.15 USD w 146 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.