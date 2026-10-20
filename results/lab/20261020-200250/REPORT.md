# Voynich Lab – przebieg 20261020-200250

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Znaki to liczby | obalona | 5/5 | Niepotwierdzona w wersji ogólnej. Testy przemawiają przeciw zapisowi całego tekstu w którymkolwiek z pięciu badanych systemów oraz przeciw etykietom będącym jawnym ciągiem 1–30 w założonej kolejności. Nie obalają jednak wszystkich hipotez liczbowych.: 1, obalona (w badanym zakresie): tekst rękopisu nie pasuje do żadnego z 5 testowanych systemów liczbowych (najlepsza odległość 1,73 przy progu <0,5), a etykiety zodiaku nie wyglądają jak kolejne liczby 1–30 (efekt 2,1%, p = 0,0506, wobec ≥16% dla podłożonych liczb i 1,3% dla zwykłego tekstu). Kontrole metody przeszły, więc negatywny wynik jest wiarygodny. Test nie wyklucza: innych rozkładów zapisywanych liczb, szyfrów homofonicznych rozmywających podobieństwo etykiet oraz zapisów liczbowych poza 5 systemami.: 1 |
| Szyfr Naibbe (Greshko 2025) | obalona | 2/2 | Nierozstrzygający; słaba przesłanka przeciw badanej rekonstrukcji Naibbe, nie podstawa do uznania hipotezy za obaloną.: 1 |
| Bełkot z kratki Cardana (Rugg 2004) | obalona | 1/1 | Wynik osłabia konkretną symulację kratki Cardana opisaną w raporcie, ale bez wymaganych kontroli nie uzasadnia wiarygodnego, ogólnego obalenia hipotezy. Nie bada też wszystkich możliwych wariantów tej metody. Najbardziej rozstrzygający następny test: z góry określona, niezależnie zbudowana tabela i procedura, sprawdzone na danych z celowo podłożonym efektem oraz danych przetasowanych.: 1 |
| Hebrajskie anagramy (Hauer i Kondrak 2016) | metoda niewiarygodna | 1/2 | Test jest niewiarygodny jako wsparcie hipotezy hebrajskiego tekstu z anagramami, ponieważ nie odróżnia hebrajskiego od tekstów niehebrajskich. Nie wyklucza jednak tej hipotezy; podważa wartość dowodową zastosowanego ataku. Nie rozstrzyga też innych możliwych analiz rękopisu. Najbardziej zmieniłby ocenę ślepy test na niezależnych, historycznie i statystycznie dopasowanych korpusach hebrajskich oraz niehebrajskich, z wcześniej ustalonym progiem swoistości.: 1 |
| Klucz w ilustracjach | nierozstrzygnięta | 2/2 | Nierozstrzygnięta. Test A wykazał różnicę długości słów przy przerwach na rysunek, ale sam nie dowodzi zależności znaczeniowej ani klucza w ilustracjach. Testy B i C, które mogłyby bezpośredniej sprawdzić hipotezę, pominięto z powodu braku skanów.: 1 |
| AI generuje brakujące strony | nierozstrzygnięta | 2/2 | odrzucona dla testowanego modelu: wygenerowane strony są odróżnialne od prawdziwych (AUC 0,715 przy kontroli 0,492; odległość 0,49; 70,9% skopiowanych wierszy; tylko 1,9% nowych słów). Test NIE rozstrzyga, czy inny, lepiej wytrenowany model generatywny mógłby przejść — przeuczenie (val_bits 1,73→5,43) i przyjęcie atrybutów od sąsiadów to realne czynniki zakłócające. Zapis stron jako SYNTETYCZNE jest zasadny.: 1, Kontrole metody przeszły, więc test jest wiarygodny w granicach użytych miar. Badany model nie spełnił kryterium nieodróżnialności; hipoteza nie została potwierdzona dla tego modelu i ustawienia. Raport nie rozstrzyga, czy inny model mógłby ją spełnić, ani nie odtwarza treści zaginionych stron.: 1 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Znaki to liczby

Cały tekst jako liczby: nie pasuje (najbliższy system: alfabetyczny (grecki/hebrajski), odległość 1.73; dopasowanie wymaga < 0.5, dwie próbki łaciny różnią się o ok. 0,2). Etykiety zodiaku jako kolejne liczby: nie (efekt 2.1% przy p = 0.051; liczby podłożone dają ≥ 16%, zwykły tekst rękopisu 1.3%).

**Synteza rady:**

## Werdykt rady

**Niepotwierdzona w zbadanych wariantach; nie obalona w każdej możliwej postaci.** Zgodność jest umiarkowana: opinie różnią się głównie tym, czy wniosek ograniczyć do testowanych założeń, czy nazwać je obalonymi.

## Co test pokazuje

Kontrole metody przeszły: test wykrył trzy zestawy podłożonych ciągów liczb 1–30 (p = 0,0003), a w 20 zestawach losowych etykiet nie zgłosił fałszywego efektu. W badanych pięciu systemach i przy przyjętym rozkładzie liczb cały tekst nie osiągnął progu dopasowania: najlepsza odległość wynosiła 1,73 wobec wymaganego <0,5. Dla etykiet zodiaku podobieństwo sąsiadów wzrosło tylko o 2,1% (p = 0,0506), wobec co najmniej 16% dla podłożonych liczb i 1,3% dla zwykłego tekstu. Wyniki przemawiają więc przeciw tym konkretnym modelom liczbowym.

## Główne zastrzeżenia

Wniosek zależy od przyjętego rozkładu liczb i od założenia, że kolejność etykiet w transliteracji odpowiada ich kolejności na pierścieniach. Test nie wyklucza zapisu homofonicznego ani innych systemów, rozkładów czy lokalnego użycia liczb. Wynik zodiakalny jest bliski progowi, a kontrola losowa obejmowała tylko 20 zestawów. Raport podaje też 12 języków, lecz prezentuje 13 odległości.

## Następny eksperyment

Przeprowadzić z góry określony test etykiet zodiaku, z niezależnie ustaloną kolejnością i realistycznymi wariantami kodowania, w tym homofonicznymi; wymagać wykrycia danych podłożonych oraz braku efektu w danych przetasowanych.

Szczegóły: [numbers.md](numbers.md)

## Szyfr Naibbe (Greshko 2025)

Szyfr Naibbe-podobny: odległość 0.83, różnica hapaksów 20%. Literatura: Naibbe odtwarza entropię i rozkład długości, ale nie hapaksy (41% wobec 70%).

**Synteza rady:**

## Werdykt rady

**Nierozstrzygający; test nie uzasadnia werdyktu „obalona”.** Zgoda jest częściowa: raport pokazuje różnice między badaną rekonstrukcją a rękopisem, ale nie potwierdza wiarygodności metody w wymaganych kontrolach.

## Co test naprawdę pokazuje

W badanej rekonstrukcji h2 jest zbliżone do wyniku dla rękopisu (2,30 wobec 2,35), natomiast hapaksy wyraźnie się różnią (49% wobec 70%); różnią się też MI krawędzi (0,012 wobec 0,168) i odsetek podobnych sąsiadów (2,4% wobec 5,0%). To przemawia przeciw **tej rekonstrukcji**, nie rozstrzyga jednak całej hipotezy.

## Główne zastrzeżenia

Zgłoszone kontrole sprawdzają rozpoznanie języka i odwracalność szyfru, ale nie wykazują, że metoda wykrywa celowo podłożoną sygnaturę Naibbe ani że nie wykrywa jej w danych przetasowanych. Ponadto użyto rekonstrukcji i tabel zbudowanych z części słów rękopisu, a nie oryginalnych tabel. Raport nie podaje też niepewności ani progów interpretacji różnic.

## Następny eksperyment

Przeprowadzić ślepy test walidacyjny tym samym pipeline’em na znanych, celowo zaszyfrowanych próbkach Naibbe oraz na odpowiednio przetasowanych próbkach kontrolnych.

Szczegóły: [naibbe_cipher.md](naibbe_cipher.md)

## Bełkot z kratki Cardana (Rugg 2004)

Kratka Cardana: odległość 2.44, różnica hapaksów 51%.

**Synteza rady:**

## Werdykt rady
**Automatyczne „obalona” nie jest uzasadnione.** Raport nie wykazuje wymaganych kontroli metody, więc test należy uznać za niewiarygodny jako rozstrzygający.

## Poziom zgody
Tylko członek B przedstawił opinię merytoryczną; opinie A i C są puste. Nie ma podstaw do stwierdzenia zgodnej oceny całej rady.

## Co test naprawdę pokazuje
W opisanej symulacji profil różni się od profilu rękopisu: hapaksy wynoszą ok. 19% wobec 70%, a MI krawędzi 0,001 wobec 0,168. To osłabia **ten konkretny wariant symulacji**, ale samo nie dowodzi, że test trafnie rozpoznaje hipotezę. Kontrola rozpoznawania łaciny nie sprawdza skuteczności kratki Cardana.

## Główne zastrzeżenia
Nie wykazano, że procedura odzyskuje efekt celowo podłożony ani że nie wykrywa go w danych przetasowanych. Ponadto tabela fragmentów i ich częstości pochodzą z rękopisu, a wynik zależy od budowy tabeli. Raport nie podaje też niepewności ani wyników dla alternatywnych ustawień.

## Rekomendowany następny eksperyment
Przeprowadzić z góry określony test z tabelą i ustawieniami ustalonymi niezależnie od rękopisu; sprawdzić tę samą procedurę zarówno na danych z celowo podłożonym efektem Cardana, jak i na danych przetasowanych.

Szczegóły: [cardan_grille.md](cardan_grille.md)

## Hebrajskie anagramy (Hauer i Kondrak 2016)

Atak anagramowy daje rękopisowi 69.0%, ale NIE jest swoisty: tekst Vietnamese osiąga 90.8% przy 72.2% dla prawdziwego hebrajskiego. Wysokie pokrycie bierze się z powtarzalności krótkich słów, nie z hebrajskiego.

**Synteza rady:**

## Werdykt rady
**Test jest niewiarygodny jako dowód na hipotezę hebrajskiego tekstu z anagramami.** Kontrola dodatnia przeszła (72,2%), ale kontrola swoistości nie: rękopis uzyskał 69,0%, wobec 90,8% dla wietnamskiego i 73,7% dla angielskiego.

## Poziom zgody
Nie da się ocenić pełnej zgodności rundy: tylko opinia B zawiera merytoryczną ocenę; A i C są puste. Werdykt rady wynika z raportu i pokrywa się z oceną B.

## Co test naprawdę pokazuje
Atak potrafi dopasować kontrolny hebrajski, ale podobne lub wyższe pokrycie uzyskuje dla danych niehebrajskich. Wynik rękopisu nie jest więc swoisty dla hebrajskiego. **Nie wyklucza** tej hipotezy, lecz nie stanowi dla niej wiarygodnego potwierdzenia; test nie rozstrzyga też innych wyjaśnień rękopisu.

## Główne zastrzeżenia
Raport wskazuje, że krótkie, powtarzalne słowa mogą dawać przypadkowe dopasowania. Ponadto kontrolny korpus hebrajski pochodzi z Biblii, a nie ze średniowiecznych tekstów. Wynik dla szyfru Naibbe-podobnego również jest wysoki (65,2%). Raport nie wykazuje osobno, że metoda nie znajduje efektu w danych przetasowanych.

## Rekomendowany następny eksperyment
Przeprowadzić **zaślepiony test na niezależnych, porównywalnych średniowiecznych korpusach hebrajskich i niehebrajskich**, z wcześniej ustalonym progiem swoistości, kontrolą dodatnią oraz przetasowanymi danymi. Klucz należy oceniać na danych niewykorzystanych przy jego doborze.

Szczegóły: [hebrew_anagram.md](hebrew_anagram.md)

## Klucz w ilustracjach

Test sprawdza warunek konieczny klucza w ilustracjach: czy tekst w ogóle zależy od rysunku. C: pominięte, brak skanów (nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg). B: pominięte (nie udało się pobrać skanów: nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg).

**Synteza rady:**

## Werdykt rady: **nierozstrzygnięta**

**Poziom zgody:** wysoki — opinie zgodne, że raport nie rozstrzyga, czy ilustracje są kluczem do tekstu.

**Co test naprawdę pokazuje:** W 613 wierszach słowo przed przerwą na rysunek było średnio krótsze o 0,24 glifu niż słowa w środku wiersza (p = 0,0003). To wskazuje na związek długości słów z układem strony, ale samo nie wykazuje zależności znaczeniowej ani szyfrowania. Kontrola A wykryła podłożone skrócenie; raport nie podaje jednak osobnego wyniku kontroli na danych przetasowanych. Kontrola C wykryła podłożony klucz (0,475 wobec maksimum 0,17 dla przetasowań; p = 0,02), lecz nie przeprowadzono ataku na dane rękopisu.

**Główne zastrzeżenia:** Testy B i C na rękopisie pominięto z powodu braku skanów. Wynik A może wynikać z konwencji układu. Kontrola C sprawdza działanie metody w przypadku sztucznie podłożonego klucza, nie potwierdza jego obecności w rękopisie; ponadto jej założenia są mocne, a identyfikacje roślin niepewne. W teście B CLIP mógłby też reagować na układ tekstu na stronie.

**Następny eksperyment:** Uruchomić test B na skanach, z kontrolami potwierdzającymi wykrycie podłożonego związku obraz–słownictwo i jego brak po permutacjach, przy ograniczeniu wpływu pisma na podobieństwo obrazów.

Szczegóły: [illustrations.md](illustrations.md)

## AI generuje brakujące strony

Transformer: 5.43 bit/znak wobec 2.02 dla trigramów. Wygenerowane strony nie są nieodróżnialne od prawdziwych (AUC 0.72, odległość 0.49). Brakujące strony zapisano jako SYNTETYCZNE.

**Synteza rady:**

## Werdykt rady
**Hipoteza nie została potwierdzona dla badanego modelu i ustawienia; ogólna możliwość, że inny model wygeneruje strony nieodróżnialne, pozostaje nierozstrzygnięta.**

## Poziom zgody
Wysoki: zgodnie uznano, że wygenerowane strony różnią się od prawdziwych według zastosowanych miar, ale wynik nie rozstrzyga o wszystkich modelach generatywnych.

## Co test naprawdę pokazuje
Kontrole klasyfikatora przeszły: AUC dla prawdziwe–prawdziwe wyniosło 0,492, a dla prawdziwe–samocytowanie 1,000. Dla wygenerowanych stron AUC wyniosło 0,715, odległość 0,486; skopiowano 70,9% całych wierszy, a udział nowych słów wyniósł 1,9%. To przemawia przeciw nieodróżnialności **w tym teście**. Test nie odtwarza zaginionej treści ani nie wyklucza sukcesu innego modelu.

## Główne zastrzeżenia
Wynik walidacyjny pogorszył się z około 1,73 do 5,43 bit/znak, mimo spadku błędu treningowego — wskazuje to na przeuczenie i osłabia ocenę końcowego modelu. Zbadano jeden model; nie podano też niepewności miar. Atrybuty brakujących stron przypisano na podstawie sąsiadów, bez niezależnej weryfikacji.

## Rekomendowany następny eksperyment
Powtórzyć test z wczesnym zatrzymaniem wybranym wyłącznie na niezależnym zbiorze walidacyjnym, używając wielu ziaren losowych i odłożonych prawdziwych stron. Ocenić odróżnialność oraz kopiowanie na odrębnym zbiorze testowym.

Szczegóły: [generative.md](generative.md)

Koszt OpenRouter: 0.04 USD w 46 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, tencent/hy3; przewodniczący: openai/gpt-6-luna.