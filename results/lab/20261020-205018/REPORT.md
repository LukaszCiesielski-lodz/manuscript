# Voynich Lab – przebieg 20261020-205018

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Znaki to liczby | obalona | 5/5 | obalona: 3 |
| Szyfr Naibbe (Greshko 2025) | obalona | 2/2 | nierozstrzygnięta: 1, metoda niewiarygodna: 2 |
| Bełkot z kratki Cardana (Rugg 2004) | obalona | 1/1 | test nie uzasadnia obalenia hipotezy; je: 1, metoda niewiarygodna: 2 |
| Hebrajskie anagramy (Hauer i Kondrak 2016) | metoda niewiarygodna | 1/2 | metoda niewiarygodna: 3 |
| Klucz w ilustracjach | nierozstrzygnięta | 2/2 | nierozstrzygnięta: 3 |
| AI generuje brakujące strony | obalona | 2/2 | wykazana konfiguracja transformera nie o: 1, obalona: 2 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Znaki to liczby

Cały tekst jako liczby: nie pasuje (najbliższy system: alfabetyczny (grecki/hebrajski), odległość 1.73; dopasowanie wymaga < 0.5, dwie próbki łaciny różnią się o ok. 0,2). Etykiety zodiaku jako kolejne liczby: nie (efekt 2.1% przy p = 0.051; liczby podłożone dają ≥ 16%, zwykły tekst rękopisu 1.3%).

**Synteza rady:**

## Werdykt rady
**Niepotwierdzona; mocny wynik negatywny dla sprawdzonych wariantów.** Cały tekst słabo pasuje do pięciu badanych systemów liczbowych, a etykiety zodiaku nie wykazują przekonującego podobieństwa do kolejnych liczb 1–30. Nie uzasadnia to jednak obalenia szerokiej hipotezy o dowolnym zapisie liczb.

**Poziom zgody:** Wysoka co do negatywnych wyników testów i ich ograniczonego zakresu; umiarkowana co do werdyktu. Opinie różnią się głównie tym, czy wynik uznać za „obalenie” testowanych wariantów, czy za mocne osłabienie hipotezy ogólnej.

## Co test naprawdę pokazuje
Dla całego tekstu najbliższy system ma odległość **1,73**, daleką od wymaganego dopasowania **<0,5**. Test etykiet daje efekt **2,1%** przy **p = 0,0506**, wobec co najmniej **16%** dla podłożonych ciągów. Kontrole wykryły podłożone liczby we wszystkich trzech sprawdzonych zapisach; kalibracja przetasowań dała **0/20** fałszywych alarmów.

## Główne zastrzeżenia
Test całego tekstu obejmuje pięć systemów i przyjęty rozkład liczb; nie rozstrzyga wariantu ograniczonego do etykiet. Test etykiet sprawdza tylko ciąg 1–30, zakłada poprawną kolejność transliteracji względem układu na stronach, a jego wynik jest graniczny. Kontrola 0/20 ma ograniczoną liczebność. Raport zastrzega też, że kodowanie homofoniczne nie zostało wykluczone.

## Rekomendowany następny eksperyment
Przeprowadzić z góry określony test **homofonicznego kodowania liczb**, z podłożonymi danymi jako kontrolą wykrywalności oraz przetasowanymi etykietami jako kontrolą fałszywych trafień.

Szczegóły: [numbers.md](numbers.md)

## Szyfr Naibbe (Greshko 2025)

Szyfr Naibbe-podobny: odległość 0.83, różnica hapaksów 20%. Literatura: Naibbe odtwarza entropię i rozkład długości, ale nie hapaksy (41% wobec 70%).

**Synteza rady:**

## Werdykt rady
**Test niewiarygodny jako podstawa rozstrzygnięcia; hipoteza pozostaje nierozstrzygnięta.** Nie należy przyjmować automatycznego werdyktu „obalona”.

## Poziom zgody
Wysoki: wszystkie opinie w drugiej rundzie uznają, że rozbieżności liczbowe nie wystarczają do obalenia hipotezy bez właściwej walidacji metody.

## Co test naprawdę pokazuje
W badanej rekonstrukcji szyfru odsetek hapaksów wynosi 49% wobec 70% w rękopisie, MI krawędzi 0,012 wobec 0,168, a H2 jest zbliżone: 2,30 wobec 2,35. Wyniki wskazują więc na różnice między tą rekonstrukcją a profilem rękopisu, ale nie dowodzą, że różnice są rozstrzygające dla całej klasy szyfrów Naibbe.

## Główne zastrzeżenia
Kontrole rozpoznania języka i odwracalności sprawdzają działanie elementów implementacji, nie trafność testu hipotezy. Brakuje wykazania, że metoda wykrywa celowo podłożony efekt Naibbe i nie wykrywa go w danych przetasowanych. Ponadto użyto rekonstrukcji, nie oryginalnych tabel; porównano jeden tekst jawny, a raport nie podaje interpretowalnego progu dla odległości 0,83.

## Rekomendowany następny eksperyment
Przeprowadzić kalibrację na wielu tekstach jawnych: sprawdzić, czy metoda wykrywa efekt w danych zaszyfrowanych Naibbe oraz czy nie znajduje go w danych przetasowanych. W miarę możliwości użyć oryginalnych tabel.

Szczegóły: [naibbe_cipher.md](naibbe_cipher.md)

## Bełkot z kratki Cardana (Rugg 2004)

Kratka Cardana: odległość 2.44, różnica hapaksów 51%.

**Synteza rady:**

## Werdykt rady
**Test niewiarygodny; hipoteza pozostaje nierozstrzygnięta.** Zgodność opinii jest wysoka: wszystkie oceny końcowe wskazują, że brak wymaganych kontroli uniemożliwia uznanie werdyktu „obalona”.

## Co test pokazuje
Opisana symulacja kratki z trzema otworami nie odtwarza kilku cech rękopisu: hapaksy stanowią 19% wobec 70%, a MI krawędzi wynosi 0,001 wobec 0,168. Pokazuje to niedopasowanie **tej konkretnej symulacji**, nie zaś obalenie wszystkich wersji hipotezy.

## Główne zastrzeżenia
Kontrola rozpoznawania języka nie sprawdza, czy metoda wykrywa efekt kratki. Brakuje kontroli pozytywnej na danych celowo wygenerowanych kratką i negatywnej na danych przetasowanych. Ponadto tabela fragmentów i ich częstości pochodzą z samego rękopisu, więc wynik zależy od jej konstrukcji. Test nie rozstrzyga innych wariantów kratki ani kwestii, których nie bada.

## Rekomendowany następny eksperyment
Przeprowadzić ślepy test z **niezależnie ustaloną tabelą**: sprawdzić, czy metoda wykrywa kratkę w tekście wygenerowanym celowo i nie wykrywa jej w danych przetasowanych; dopiero po przejściu obu kontroli zastosować ją do rękopisu.

Szczegóły: [cardan_grille.md](cardan_grille.md)

## Hebrajskie anagramy (Hauer i Kondrak 2016)

Atak anagramowy daje rękopisowi 69.0%, ale NIE jest swoisty: tekst Vietnamese osiąga 90.8% przy 72.2% dla prawdziwego hebrajskiego. Wysokie pokrycie bierze się z powtarzalności krótkich słów, nie z hebrajskiego.

**Synteza rady:**

## Werdykt rady

**Metoda niewiarygodna jako test identyfikujący hebrajski.** Zgoda opinii jest pełna: wszystkie trzy oceny uznają, że kontrola dodatnia przeszła (72,2%), ale kontrola swoistości nie (wietnamski: 90,8%; angielski: 73,7%; rękopis: 69,0%).

## Co test naprawdę pokazuje

Atak potrafi uzyskać wysokie pokrycie na celowo zanagramowanym i zaszyfrowanym hebrajskim, lecz równie wysokie lub wyższe wyniki uzyskuje dla badanych tekstów niehebrajskich. Wynik rękopisu nie stanowi więc swoistego dowodu na hipotezę. **Nie obala jednak samej hipotezy** — test nie rozstrzyga, czy rękopis ma takie podłoże.

## Główne zastrzeżenia

Korpus hebrajski pochodzi z Biblii, nie ze średniowiecznego tekstu. Krótkie słowa mogą sprzyjać przypadkowym trafieniom; raport nie podaje kontroli przetasowanej, a klucz zawiera liczne przypisania wielu glifów do tej samej litery. Nie wiadomo, jak bardzo wpływają one na wynik.

## Rekomendowany następny eksperyment

Powtórzyć atak z niezależnym, średniowiecznym korpusem hebrajskim oraz dopasowanymi kontrolami niehebrajskimi i przetasowanymi. Klucz dobierać na części treningowej, a wynik oceniać na odłożonej części. Eksperyment powinien wykryć efekt w kontroli dodatniej i nie wykrywać go w kontrolach niehebrajskich ani przetasowanych.

Szczegóły: [hebrew_anagram.md](hebrew_anagram.md)

## Klucz w ilustracjach

Test sprawdza warunek konieczny klucza w ilustracjach: czy tekst w ogóle zależy od rysunku. C: pominięte, brak skanów (nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg). B: pominięte (nie udało się pobrać skanów: nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg).

**Synteza rady:**

## Werdykt rady: nierozstrzygnięta

**Poziom zgody:** wysoki — oceniający zgodnie uznali, że raport nie rozstrzyga, czy ilustracje zawierają klucz do tekstu.

**Co test naprawdę pokazuje:** Test A wykrył, że w 613 wierszach słowa przed przerwą na rysunek były średnio krótsze o 0,24 glifu (p = 0,0003). Kontrola z celowo podłożonym skróceniem zadziałała. To wskazuje na różnicę długości w określonym układzie strony, nie na związek treści słów z konkretnymi ilustracjami. Nie wyklucza więc hipotezy klucza, ale jej też nie potwierdza.

**Główne zastrzeżenia:** Testy B i C na danych rękopisu pominięto z powodu braku skanów. Kontrola C sprawdzała działanie ataku na danych z podłożonym kluczem, a nie sam rękopis; raport nie wyjaśnia tego rozróżnienia. Ponadto A nie ma podanej kontroli na danych przetasowanych, więc pełna wiarygodność metody nie jest wykazana. Mały efekt może wynikać z formatowania lub praktyk skryby. CLIP może też reagować na układ pisma, a identyfikacje roślin i założenia ataku C są niepewne.

**Rekomendowany następny eksperyment:** Wykonać test B na skanach, z permutacjami w obrębie skryby i języka Curriera oraz kontrolami wykrywającymi efekt w danych podłożonych, ale nie w danych przetasowanych. Należy też ograniczyć wpływ widocznego pisma i układu strony na podobieństwo obrazów.

Szczegóły: [illustrations.md](illustrations.md)

## AI generuje brakujące strony

Transformer: 1.70 bit/znak wobec 2.02 dla trigramów. Wygenerowane strony nie są nieodróżnialne od prawdziwych (AUC 0.83, odległość 1.02). Brakujące strony zapisano jako SYNTETYCZNE.

**Synteza rady:**

## Werdykt rady
**Badany transformer nie osiągnął statystycznej nieodróżnialności**: klasyfikator odróżniał jego strony od prawdziwych (AUC 0,834; odległość 1,02). Nie uznajemy jednak testu za rozstrzygające obalenie szerszej hipotezy o możliwościach modeli generatywnych: wymagane kontrole nie są kompletne.

## Poziom zgody
Umiarkowany. Opinie zgodnie uznają, że wynik przemawia przeciw zbadanej konfiguracji. Różnią się co do tego, czy wystarcza to do werdyktu „obalona”; rada ogranicza wniosek do badanego modelu i miar.

## Co test naprawdę pokazuje
Kontrole prawdziwe–prawdziwe (AUC 0,492) i prawdziwe–samocytowanie (AUC 1,000) dały oczekiwane wyniki. Raport pokazuje więc odróżnialność wygenerowanych stron w tym porównaniu, ale nie dowodzi, że każdy model generatywny poniósłby porażkę. Nie ustala też treści zaginionych stron ani trafności przypisanych im atrybutów.

## Główne zastrzeżenia
Brakuje kontroli na danych przetasowanych oraz jednoznacznej kontroli z celowo podłożonym efektem, wymaganych do uznania metody za wiarygodną. Nie podano też liczebności próbek ani przedziałów ufności; atrybuty stron przyjęto na podstawie sąsiadów.

## Następny eksperyment
Przeprowadzić ślepą replikację na wielu odłożonych stronach, z kontrolą wykrywającą celowo podłożony efekt i kontrolą na danych przetasowanych, przy uprzednio ustalonych atrybutach i klasyfikatorze.

Szczegóły: [generative.md](generative.md)

Koszt OpenRouter: 0.05 USD w 60 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, tencent/hy3; przewodniczący: openai/gpt-6-luna.