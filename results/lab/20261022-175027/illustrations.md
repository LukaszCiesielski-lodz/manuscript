# illustrations: nierozstrzygnięta

**Hipoteza.** Klucz do tekstu kryje się w ilustracjach: tekst zależy od rysunków (np. pierwsze słowo strony zielnika to zaszyfrowana nazwa rośliny).

**Metoda.** A: długość słów przy przerwach na rysunek (test permutacyjny). B: test Mantela – podobieństwo obrazów CLIP a podobieństwo słownictwa stron zielnika, permutacje w obrębie skryby i języka Curriera. C: atak z nazwami roślin od modelu wizyjnego jako 'cribami' (wyżarzanie klucza glif→litera) wobec nazw przetasowanych.

Test sprawdza warunek konieczny klucza w ilustracjach: czy tekst w ogóle zależy od rysunku. C: 20 stron, nazwy od qwen/qwen2.5-vl-72b-instruct. Dopasowanie 0.40 wobec średnio 0.33 dla nazw przetasowanych, p = 0.040. B: 121 stron zielnika. Korelacja podobieństwa obrazów i słownictwa r = 0.083, p = 0.0712 (permutacje w obrębie skryby i języka).

## Kontrole

- ✅ **A: podłożone skrócenie słów przed rysunkiem**: oczekiwano wykryte (p < 0,01); wynik: p = 0.0003
- ✅ **C: nazwy podłożone znanym kluczem**: oczekiwano atak je znajduje (p ≤ 0,05); wynik: wynik 0.47 wobec 0.17 (max dla przetasowanych), p = 0.020
- ✅ **B: połowy tekstu tej samej strony**: oczekiwano zgodne (p < 0,01); wynik: r = 0.30, p = 0.0002
- ✅ **B: losowe podobieństwa obrazów**: oczekiwano brak związku (p > 0,05); wynik: p = 0.561

## Dowody

- A: 613 wierszy przerwanych rysunkiem. Słowo przed rysunkiem różni się długością o -0.24 glifu od słów w środku wiersza, p = 0.0003.
- C: 20 stron, nazwy od qwen/qwen2.5-vl-72b-instruct. Dopasowanie 0.40 wobec średnio 0.33 dla nazw przetasowanych, p = 0.040.
- B: 121 stron zielnika. Korelacja podobieństwa obrazów i słownictwa r = 0.083, p = 0.0712 (permutacje w obrębie skryby i języka).

## Zastrzeżenia

- Związek tekstu z rysunkiem (B) byłby warunkiem koniecznym, ale nie dowodem klucza: tekst o roślinie też zależy od rośliny.
- Identyfikacje roślin przez model wizyjny są niepewne; botanicy nie zgadzają się co do większości roślin rękopisu.
- Atak C zakłada, że pierwsze słowo strony to nazwa rośliny zapisana szyfrem podstawieniowym od początku słowa.
- CLIP widzi całą stronę razem z pismem; podobny układ tekstu może podbijać podobieństwo obrazów.

## Rada modeli

## Werdykt rady: **nierozstrzygnięta**

**Zgodność:** pełna — wszyscy oceniający uznali, że raport nie uzasadnia ani przyjęcia, ani odrzucenia hipotezy.

**Co test naprawdę pokazuje:** opisane kontrole metody przeszły: procedury wykrywały efekty podłożone celowo i nie wykrywały losowych podobieństw. Test A wykazał niewielką różnicę długości słów przy przerwach na rysunki (−0,24 glifu; *p* = 0,0003), ale sam nie dowodzi zależności treści tekstu od ilustracji. W teście B związek podobieństwa obrazów i słownictwa był słaby i nie osiągnął istotności (*r* = 0,083; *p* = 0,0712). Nie oznacza to jednak, że związek nie istnieje. Test C dał słaby dodatni sygnał (*p* = 0,040), lecz dotyczył 20 stron i zależał od niepewnych nazw oraz konkretnego założenia o sposobie zapisu.

**Główne zastrzeżenia:** CLIP analizował strony wraz z pismem, więc wynik B może być zaburzony układem tekstu. Test C jest mały i wąski; zaliczenie jego kontroli potwierdza działanie metody w kontroli, nie poprawność identyfikacji ani hipotezy. Żaden z wyników nie wykazuje, że ilustracje stanowią klucz.

**Następny eksperyment:** powtórzyć test B na większej, z góry ustalonej próbie, używając obrazów po zamaskowaniu tekstu oraz tych samych permutacji uwzględniających skrybę i język Curriera.

## Literatura

- Subtle Signs of Scribal Intent in the Voynich Manuscript, arXiv:2404.13069
- Topic Modeling in the Voynich Manuscript, arXiv:2107.02858
- A Generative Grammar Underlying the Voynich Manuscript (pastiche hypothesis), arXiv:2609.20835
- Bax, A proposed partial decoding of the Voynich script (2014)

_Czas: 1148 s · 2026-10-22 18:55_