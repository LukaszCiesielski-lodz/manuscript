# illustrations: nierozstrzygnięta

**Hipoteza.** Klucz do tekstu kryje się w ilustracjach: tekst zależy od rysunków (np. pierwsze słowo strony zielnika to zaszyfrowana nazwa rośliny).

**Metoda.** A: długość słów przy przerwach na rysunek (test permutacyjny). B: test Mantela – podobieństwo obrazów CLIP a podobieństwo słownictwa stron zielnika, permutacje w obrębie skryby i języka Curriera. C: atak z nazwami roślin od modelu wizyjnego jako 'cribami' (wyżarzanie klucza glif→litera) wobec nazw przetasowanych.

Test sprawdza warunek konieczny klucza w ilustracjach: czy tekst w ogóle zależy od rysunku. C: pominięte, brak skanów (nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg). B: pominięte (nie udało się pobrać skanów: nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg).

## Kontrole

- ✅ **A: podłożone skrócenie słów przed rysunkiem**: oczekiwano wykryte (p < 0,01); wynik: p = 0.0003
- ✅ **C: nazwy podłożone znanym kluczem**: oczekiwano atak je znajduje (p ≤ 0,05); wynik: wynik 0.47 wobec 0.17 (max dla przetasowanych), p = 0.020

## Dowody

- A: 613 wierszy przerwanych rysunkiem. Słowo przed rysunkiem różni się długością o -0.24 glifu od słów w środku wiersza, p = 0.0003.
- C: pominięte, brak skanów (nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg).
- B: pominięte (nie udało się pobrać skanów: nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg).

## Zastrzeżenia

- Związek tekstu z rysunkiem (B) byłby warunkiem koniecznym, ale nie dowodem klucza: tekst o roślinie też zależy od rośliny.
- Identyfikacje roślin przez model wizyjny są niepewne; botanicy nie zgadzają się co do większości roślin rękopisu.
- Atak C zakłada, że pierwsze słowo strony to nazwa rośliny zapisana szyfrem podstawieniowym od początku słowa.
- CLIP widzi całą stronę razem z pismem; podobny układ tekstu może podbijać podobieństwo obrazów.

## Rada modeli

## Werdykt rady: nierozstrzygnięta

**Poziom zgody:** wysoki — oceniający zgodnie uznali, że raport nie rozstrzyga, czy ilustracje zawierają klucz do tekstu.

**Co test naprawdę pokazuje:** Test A wykrył, że w 613 wierszach słowa przed przerwą na rysunek były średnio krótsze o 0,24 glifu (p = 0,0003). Kontrola z celowo podłożonym skróceniem zadziałała. To wskazuje na różnicę długości w określonym układzie strony, nie na związek treści słów z konkretnymi ilustracjami. Nie wyklucza więc hipotezy klucza, ale jej też nie potwierdza.

**Główne zastrzeżenia:** Testy B i C na danych rękopisu pominięto z powodu braku skanów. Kontrola C sprawdzała działanie ataku na danych z podłożonym kluczem, a nie sam rękopis; raport nie wyjaśnia tego rozróżnienia. Ponadto A nie ma podanej kontroli na danych przetasowanych, więc pełna wiarygodność metody nie jest wykazana. Mały efekt może wynikać z formatowania lub praktyk skryby. CLIP może też reagować na układ pisma, a identyfikacje roślin i założenia ataku C są niepewne.

**Rekomendowany następny eksperyment:** Wykonać test B na skanach, z permutacjami w obrębie skryby i języka Curriera oraz kontrolami wykrywającymi efekt w danych podłożonych, ale nie w danych przetasowanych. Należy też ograniczyć wpływ widocznego pisma i układu strony na podobieństwo obrazów.

## Literatura

- Subtle Signs of Scribal Intent in the Voynich Manuscript, arXiv:2404.13069
- Topic Modeling in the Voynich Manuscript, arXiv:2107.02858
- A Generative Grammar Underlying the Voynich Manuscript (pastiche hypothesis), arXiv:2609.20835
- Bax, A proposed partial decoding of the Voynich script (2014)

_Czas: 92 s · 2026-10-20 21:19_