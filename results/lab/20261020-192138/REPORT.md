# Voynich Lab – przebieg 20261020-192138

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Znaki to liczby | obalona | 5/5 | Dane przemawiają przeciw temu, by cały tekst był zapisany jako jeden z pięciu testowanych systemów liczbowych, oraz słabo przeciw prostemu ciągowi liczb 1–30 w etykietach zodiaku. Automatyczny werdykt „obalona” jest zbyt szeroki: wyniki nie wykluczają wszystkich hipotez, joissa tekst koduje liczby.: 1 |
| Szyfr Naibbe (Greshko 2025) | nierozstrzygnięta | 2/2 | nierozstrzygnięta: 1, Nierozstrzygnięta. Wynik wskazuje na częściowe podobieństwo statystyk, ale istotne różnice i brak wymaganych kontroli nie pozwalają uznać testu za wiarygodne potwierdzenie hipotezy. Test nie wyklucza szyfru Naibbe-podobnego, lecz nie rozstrzyga, czy podobieństwo jest swoiste dla tej klasy. Nie bada też konkretnych oryginalnych tabel ani innych wyjaśnień. Najbardziej zmieniłby ocenę test z kontrolą pozytywną (celowo podłożony efekt) oraz negatywną (dane przetasowane).: 1 |
| Bełkot z kratki Cardana (Rugg 2004) | obalona | 1/1 | Nierozstrzygnięta. Symulowany profil wyraźnie odbiega od profilu rękopisu, ale bez wymaganych kontroli metoda nie uzasadnia rozstrzygającego odrzucenia hipotezy. Najbardziej zmieniłaby ocenę powtórzona symulacja z niezależnie zbudowaną tabelą oraz kontrolą efektu podłożonego i kontrolą na danych przetasowanych.: 1 |
| Hebrajskie anagramy (Hauer i Kondrak 2016) | metoda niewiarygodna | 1/2 | Metoda niewiarygodna jako test tej hipotezy, ponieważ nie przeszła kontroli swoistości. Wynik nie wspiera wiarygodnie hipotezy hebrajskiego tekstu z anagramami. Nie wyklucza jednak, że rękopis jest hebrajski ani nie rozstrzyga innych hipotez; tego test nie bada.: 1, metoda niewiarygodna: 1 |
| Klucz w ilustracjach | nierozstrzygnięta | 2/2 | Nierozstrzygnięta. Dane wspierają jedynie niewielką różnicę długości słów przy przerwach na rysunek; nie rozstrzygają, czy treść tekstu zależy od ilustracji ani czy ilustracje zawierają klucz.: 1, nierozstrzygnięta — test A daje słaby sygnał zależności tekstu od układu strony (p = 0,0033, kontrola podłożonego efektu OK), ale testy B i C nie zostały przeprowadzone (brak skanów), a kontrola na danych przetasowanych dla A nie jest udokumentowana. Hipoteza o kluczu w ilustracjach pozostaje nietestowana w swej istotnej części.: 1 |
| AI generuje brakujące strony | obalona | 2/2 | obalona: 1, Obalona dla badanego transformera i zastosowanego protokołu; nie jest to obalenie możliwości wszystkich modeli generatywnych ani test rekonstrukcji zaginionej treści.: 1 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Znaki to liczby

Cały tekst jako liczby: nie pasuje (najbliższy system: alfabetyczny (grecki/hebrajski), odległość 1.52; dopasowanie wymaga < 0.5, dwie próbki łaciny różnią się o ok. 0,2). Etykiety zodiaku jako kolejne liczby: nie (efekt 2.2% przy p = 0.027; liczby podłożone dają ≥ 16%, zwykły tekst rękopisu 1.3%).

**Synteza rady:**

## Werdykt rady

**Nieuzasadnione jest odrzucenie całej teorii „numbers”.** Wyniki przemawiają przeciwko temu, by cały tekst odpowiadał któremukolwiek z pięciu testowanych systemów liczbowych, oraz przeciwko prostemu ciągowi 1–30 w etykietach zodiaku. Nie wykluczają jednak innych sposobów zapisu liczb.

**Poziom zgody:** brak podstaw do oceny zgody całej rady — opinie A i C są puste. Dostępna opinia B trafnie podkreśla, że automatyczny werdykt jest szerszy niż zakres testu.

## Co test naprawdę pokazuje

Kontrole metody przeszły: testy wykryły podłożone ciągi liczb, a odsetek fałszywych alarmów w próbie losowej mieścił się w przyjętym limicie. Dopasowanie całego tekstu jest słabe: najbliższy system ma odległość 1,52 wobec wymaganego progu poniżej 0,5. W etykietach zodiaku efekt wynosi 2,2% (p = 0,0266) — niewiele więcej niż 1,3% w zwykłym tekście i znacznie mniej niż co najmniej 16% dla podłożonych liczb.

## Główne zastrzeżenia

Test całego tekstu zależy od pięciu badanych systemów i założonego rozkładu liczb. Test etykiet zakłada, że kolejność transliteracji odpowiada kolejności na pierścieniach; bada tylko prosty ciąg i nie wyklucza kodowania rozmywającego podobieństwo. Kalibracja losowa opiera się zaledwie na 10 zestawach.

## Rekomendowany następny eksperyment

Powtórzyć test etykiet z kolejnością ustaloną niezależnie, z góry określonymi wariantami zapisu i większą liczbą losowych zestawów kontrolnych.

Szczegóły: [numbers.md](numbers.md)

## Szyfr Naibbe (Greshko 2025)

Szyfr Naibbe-podobny: odległość 0.63, różnica hapaksów 7%. Literatura: Naibbe odtwarza entropię i rozkład długości, ale nie hapaksy (41% wobec 70%).

**Synteza rady:**

## Werdykt rady
**Nierozstrzygnięta.** Poziom zgody jest wysoki: obie merytoryczne oceny końcowe uznają, że raport nie potwierdza ani nie wyklucza hipotezy.

## Co test naprawdę pokazuje
Uzyskano **mieszane podobieństwo statystyczne**: entropia h2 jest zbliżona (2,30 wobec 2,37), podobnie jak udział hapaksów (62% wobec 69%). Zarazem MI krawędzi jest znacznie niższe (0,023 wobec 0,167), a miary sąsiedztwa również się różnią. Sama odległość 0,63 nie ma podanej skali porównawczej.

## Główne zastrzeżenia
Kontrole rozpoznania łaciny i odwracalności tabel nie sprawdzają, czy pełna procedura wykrywa efekt celowo podłożony ani czy nie wykrywa go w danych przetasowanych. Te kluczowe kontrole nie zostały przedstawione, więc test nie spełnia kryteriów wiarygodności. Ponadto tabele zrekonstruowano z części słów rękopisu, a nie z oryginalnych tabel; wynik nie rozstrzyga zatem konkretnej implementacji. Test nie wyklucza szyfru Naibbe-podobnego, ale nie wykazuje, że obserwowane podobieństwo jest dla niego swoiste.

## Rekomendowany następny eksperyment
Przeprowadzić **zaślepioną walidację pełnej procedury** na syntetycznych danych z celowo podłożonym efektem Naibbe oraz na danych przetasowanych, używając tabel niezależnych od słownictwa rękopisu.

Szczegóły: [naibbe_cipher.md](naibbe_cipher.md)

## Bełkot z kratki Cardana (Rugg 2004)

Kratka Cardana: odległość 2.26, różnica hapaksów 41%.

**Synteza rady:**

## Werdykt rady
**Nierozstrzygnięta; test nie uzasadnia wiarygodnego obalenia hipotezy.** Opinie w rundzie 2 są zgodne co do tego, że automatyczny werdykt „obalona” wykracza poza przedstawione dowody.

## Co test pokazuje
Opisana symulacja kratki odbiega od profilu rękopisu: hapaksy stanowią 27% wobec 69%, MI krawędzi wynosi 0,004 wobec 0,167, a h2 to 1,92 wobec 2,37. Pokazuje to niedopasowanie **tej implementacji** do badanych miar, nie rozstrzyga jednak samo w sobie o hipotezie.

## Główne zastrzeżenia
Brakuje wymaganych kontroli: nie wykazano, że metoda wykrywa efekt celowo podłożony ani że nie wykrywa go w danych przetasowanych. Kontrola rozpoznawania łaciny tego nie sprawdza. Ponadto tabela i częstości fragmentów pochodzą z badanego rękopisu, a raport nie podaje rozrzutu wyników z powtórzeń. Test obejmuje zatem tylko konkretną symulację, nie inne możliwe konstrukcje kratki.

## Rekomendowany następny eksperyment
Powtórzyć symulację z tabelą zbudowaną z niezależnego źródła zgodnie z opisaną hipotezą, uwzględniając wielokrotne przebiegi oraz kontrole: wykrycie efektu podłożonego i brak wykrycia w danych przetasowanych.

Szczegóły: [cardan_grille.md](cardan_grille.md)

## Hebrajskie anagramy (Hauer i Kondrak 2016)

Atak anagramowy daje rękopisowi 70.7%, ale NIE jest swoisty: tekst Vietnamese osiąga 91.3% przy 78.0% dla prawdziwego hebrajskiego. Wysokie pokrycie bierze się z powtarzalności krótkich słów, nie z hebrajskiego.

**Synteza rady:**

## Werdykt rady

**Metoda niewiarygodna jako test hipotezy.** Poziom zgody jest wysoki: obie merytoryczne opinie wskazują na niezaliczoną kontrolę swoistości; trzecia opinia była pusta.

## Co test pokazuje

Kontrola dodatnia przeszła: zanagramowany i zaszyfrowany hebrajski uzyskał pokrycie 78,0%, powyżej progu 50%. Jednak kontrola swoistości nie przeszła: wietnamski osiągnął 91,3%, wobec 78,0% dla hebrajskiego i 70,7% dla rękopisu. Wynik nie pozwala więc uznać wysokiego pokrycia za swoisty dowód hebrajskiego podłoża.

Test podważa wiarygodność **tej metody** jako dowodu na hipotezę; sam nie wyklucza, że hipoteza jest prawdziwa.

## Główne zastrzeżenia

Raport wskazuje ryzyko przypadkowych dopasowań krótkich słów oraz ograniczenie korpusu hebrajskiego do Biblii, który może nie odzwierciedlać średniowiecznej ortografii. Dane wykazują nieswoistość, ale nie dowodzą, jaki mechanizm ją powoduje. Nie przedstawiono też testu statystycznego porównującego wyniki.

## Rekomendowany następny eksperyment

Przeprowadzić zaślepiony test na niezależnych, reprezentatywnych korpusach średniowiecznego hebrajskiego i tekstów niehebrajskich. Z góry ustalić kryteria i sposób doboru klucza, a swoistość ocenić na danych niewykorzystanych do jego dopasowania.

Szczegóły: [hebrew_anagram.md](hebrew_anagram.md)

## Klucz w ilustracjach

Test sprawdza warunek konieczny klucza w ilustracjach: czy tekst w ogóle zależy od rysunku. C: pominięte, brak skanów (nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg). B: pominięte (nie udało się pobrać skanów: nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg).

**Synteza rady:**

## Werdykt rady
**Nierozstrzygnięta.** Zgodność opinii A i B jest wysoka; opinia C nie zawiera oceny.

## Co test naprawdę pokazuje
W 613 wierszach słowa przed przerwą na rysunek były średnio krótsze o 0,24 glifu niż słowa w środku wiersza (p = 0,0033). Kontrola A z celowo podłożonym skróceniem wykryła efekt. Wynik wskazuje na różnicę związaną z układem strony, ale nie dowodzi, że treść tekstu zależy od ilustracji ani że ilustracje zawierają klucz.

## Główne zastrzeżenia
Test B — bezpośrednio badający związek obrazów ze słownictwem — oraz test C na rękopisie nie zostały wykonane z powodu braku skanów. Dla A nie udokumentowano kontroli na danych przetasowanych, więc nie wykazano, że metoda nie daje efektu przy braku związku. Kontrola C przeszła na granicy (p = 0,050), ale dotyczyła symulacji, nie rękopisu; ponadto test opiera się na założeniach o identyfikacji roślin i sposobie zapisu nazw. Test B, nawet jeśli wykaże związek, nie będzie sam w sobie dowodem klucza; CLIP może reagować na układ pisma.

## Rekomendowany następny eksperyment
Uzyskać skany i przeprowadzić test B na stronach zielnika, maskując tekst przed analizą obrazów oraz stosując zarówno kontrolę z podłożonym związkiem, jak i przetasowane etykiety — z permutacjami w obrębie skryby i języka Curriera.

Szczegóły: [illustrations.md](illustrations.md)

## AI generuje brakujące strony

Transformer: 1.96 bit/znak wobec 2.02 dla trigramów. Wygenerowane strony nie są nieodróżnialne od prawdziwych (AUC 0.90, odległość 0.76). Brakujące strony zapisano jako SYNTETYCZNE.

**Synteza rady:**

### Werdykt rady
**Obalona dla badanego transformera i zastosowanego protokołu.** Opinie A i B są zgodne; ich pewność jest wysoka, lecz wniosek ma ograniczony zakres.

### Co test naprawdę pokazuje
Obie kontrole klasyfikatora przeszły według kryteriów raportu: AUC 0,492 dla prawdziwych stron i 1,000 dla stron prostego generatora. Mimo to wygenerowane strony odróżniano od prawdziwych z AUC 0,900; raport podaje też odległość 0,765. Wyniki nie wspierają więc statystycznej nieodróżnialności **tego modelu** według użytych miar.

Test nie rozstrzyga, czy inny model mógłby spełnić hipotezę, ani nie odtwarza zaginionej treści.

### Główne zastrzeżenia
Kontrole potwierdzają działanie klasyfikatora tylko dla sprawdzonych przypadków, nie wykluczają artefaktów generacji ani różnic w długości i atrybutach stron. Atrybuty brakujących stron przypisano na podstawie sąsiadów. Brakuje też niepewności wyników i szczegółów podziału walidacyjnego; porównanie odległości z łaciną jest orientacyjne.

### Rekomendowany następny eksperyment
Powtórzyć ocenę na wielu podziałach walidacyjnych, używając silniejszego klasyfikatora oraz stron dopasowanych pod względem działu, skryby i długości, wraz z kontrolami ujemnymi i dodatnimi.

Szczegóły: [generative.md](generative.md)

Koszt OpenRouter: 0.03 USD w 46 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, tencent/hy3; przewodniczący: openai/gpt-6-luna.