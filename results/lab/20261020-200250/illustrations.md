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

## Werdykt rady: **nierozstrzygnięta**

**Poziom zgody:** wysoki — opinie zgodne, że raport nie rozstrzyga, czy ilustracje są kluczem do tekstu.

**Co test naprawdę pokazuje:** W 613 wierszach słowo przed przerwą na rysunek było średnio krótsze o 0,24 glifu niż słowa w środku wiersza (p = 0,0003). To wskazuje na związek długości słów z układem strony, ale samo nie wykazuje zależności znaczeniowej ani szyfrowania. Kontrola A wykryła podłożone skrócenie; raport nie podaje jednak osobnego wyniku kontroli na danych przetasowanych. Kontrola C wykryła podłożony klucz (0,475 wobec maksimum 0,17 dla przetasowań; p = 0,02), lecz nie przeprowadzono ataku na dane rękopisu.

**Główne zastrzeżenia:** Testy B i C na rękopisie pominięto z powodu braku skanów. Wynik A może wynikać z konwencji układu. Kontrola C sprawdza działanie metody w przypadku sztucznie podłożonego klucza, nie potwierdza jego obecności w rękopisie; ponadto jej założenia są mocne, a identyfikacje roślin niepewne. W teście B CLIP mógłby też reagować na układ tekstu na stronie.

**Następny eksperyment:** Uruchomić test B na skanach, z kontrolami potwierdzającymi wykrycie podłożonego związku obraz–słownictwo i jego brak po permutacjach, przy ograniczeniu wpływu pisma na podobieństwo obrazów.

## Literatura

- Subtle Signs of Scribal Intent in the Voynich Manuscript, arXiv:2404.13069
- Topic Modeling in the Voynich Manuscript, arXiv:2107.02858
- A Generative Grammar Underlying the Voynich Manuscript (pastiche hypothesis), arXiv:2609.20835
- Bax, A proposed partial decoding of the Voynich script (2014)

_Czas: 93 s · 2026-10-20 20:33_