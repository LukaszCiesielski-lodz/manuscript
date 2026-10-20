# illustrations: nierozstrzygnięta

**Hipoteza.** Klucz do tekstu kryje się w ilustracjach: tekst zależy od rysunków (np. pierwsze słowo strony zielnika to zaszyfrowana nazwa rośliny).

**Metoda.** A: długość słów przy przerwach na rysunek (test permutacyjny). B: test Mantela – podobieństwo obrazów CLIP a podobieństwo słownictwa stron zielnika, permutacje w obrębie skryby i języka Curriera. C: atak z nazwami roślin od modelu wizyjnego jako 'cribami' (wyżarzanie klucza glif→litera) wobec nazw przetasowanych.

Test sprawdza warunek konieczny klucza w ilustracjach: czy tekst w ogóle zależy od rysunku. C: pominięte, brak skanów (nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg). B: pominięte (nie udało się pobrać skanów: nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg).

## Kontrole

- ✅ **A: podłożone skrócenie słów przed rysunkiem**: oczekiwano wykryte (p < 0,01); wynik: p = 0.0033
- ✅ **C: nazwy podłożone znanym kluczem**: oczekiwano atak je znajduje (p ≤ 0,05); wynik: wynik 0.49 wobec 0.18 (max dla przetasowanych), p = 0.050

## Dowody

- A: 613 wierszy przerwanych rysunkiem. Słowo przed rysunkiem różni się długością o -0.24 glifu od słów w środku wiersza, p = 0.0033.
- C: pominięte, brak skanów (nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg).
- B: pominięte (nie udało się pobrać skanów: nie udało się pobrać skanu 1v: 403 https://collections.library.yale.edu/iiif/2/1006077/full/1024,/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/!1024,1024/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/pct:50/0/default.jpg; 403 https://collections.library.yale.edu/iiif/2/1006077/full/full/0/default.jpg. Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg).

## Zastrzeżenia

- Związek tekstu z rysunkiem (B) byłby warunkiem koniecznym, ale nie dowodem klucza: tekst o roślinie też zależy od rośliny.
- Identyfikacje roślin przez model wizyjny są niepewne; botanicy nie zgadzają się co do większości roślin rękopisu.
- Atak C zakłada, że pierwsze słowo strony to nazwa rośliny zapisana szyfrem podstawieniowym od początku słowa.
- CLIP widzi całą stronę razem z pismem; podobny układ tekstu może podbijać podobieństwo obrazów.

## Rada modeli

## Werdykt rady
**Nierozstrzygnięta.** Zgodność opinii A i B jest wysoka; opinia C nie zawiera oceny.

## Co test naprawdę pokazuje
W 613 wierszach słowa przed przerwą na rysunek były średnio krótsze o 0,24 glifu niż słowa w środku wiersza (p = 0,0033). Kontrola A z celowo podłożonym skróceniem wykryła efekt. Wynik wskazuje na różnicę związaną z układem strony, ale nie dowodzi, że treść tekstu zależy od ilustracji ani że ilustracje zawierają klucz.

## Główne zastrzeżenia
Test B — bezpośrednio badający związek obrazów ze słownictwem — oraz test C na rękopisie nie zostały wykonane z powodu braku skanów. Dla A nie udokumentowano kontroli na danych przetasowanych, więc nie wykazano, że metoda nie daje efektu przy braku związku. Kontrola C przeszła na granicy (p = 0,050), ale dotyczyła symulacji, nie rękopisu; ponadto test opiera się na założeniach o identyfikacji roślin i sposobie zapisu nazw. Test B, nawet jeśli wykaże związek, nie będzie sam w sobie dowodem klucza; CLIP może reagować na układ pisma.

## Rekomendowany następny eksperyment
Uzyskać skany i przeprowadzić test B na stronach zielnika, maskując tekst przed analizą obrazów oraz stosując zarówno kontrolę z podłożonym związkiem, jak i przetasowane etykiety — z permutacjami w obrębie skryby i języka Curriera.

## Literatura

- Subtle Signs of Scribal Intent in the Voynich Manuscript, arXiv:2404.13069
- Topic Modeling in the Voynich Manuscript, arXiv:2107.02858
- A Generative Grammar Underlying the Voynich Manuscript (pastiche hypothesis), arXiv:2609.20835
- Bax, A proposed partial decoding of the Voynich script (2014)

_Czas: 24 s · 2026-10-20 19:31_