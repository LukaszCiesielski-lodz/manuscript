# Voynich Lab – przebieg 20261107-155049

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Co widzi sędzia: słownictwo czy szyk | potwierdzona | 3/3 | nierozstrzygnięta: 2, metoda niewiarygodna: 1 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Co widzi sędzia: słownictwo czy szyk

Sędzia AUC 0.690 (prawdziwe–prawdziwe 0.532); po dopasowaniu słownictwa 0.566. Najsilniejsza pojedyncza cecha: hapax (AUC 0.58). Ślad sędziego to słownictwo: na wspólnych słowach nie odróżnia.

**Synteza rady:**

## Werdykt rady
**Metoda niewiarygodna według przyjętych kryteriów; hipoteza nierozstrzygnięta.** Kontrole prawdziwe–prawdziwe (AUC 0,532) i czułość na zmienione glify (0,862) przeszły, ale brak kontroli na danych przetasowanych uniemożliwia uznanie metody za wiarygodną.

## Poziom zgody
Opinie różniły się co do etykiety werdyktu, lecz zgodnie wskazywały, że przypisanie sygnału słownictwu nie jest dowiedzione. Zgodnie z regułą oceny brak wymaganej kontroli przesądza o niewiarygodności metody.

## Co test naprawdę pokazuje
Sędzia odróżniał korpusy (AUC 0,690), a po dopasowaniu słownictwa wynik spadł do 0,566 na 247 wierszach. To **kierunkowo** wspiera rolę słownictwa, ale jej nie rozstrzyga. Żadna z badanych cech pojedynczo nie daje silnego rozróżnienia; hapaksy osiągają AUC 0,58, a „unseen” 0,52.

## Główne zastrzeżenia
Spadek AUC może wynikać z mniejszej próby, a nie z usunięcia sygnału słownikowego; nie podano niepewności wyników. Test nie rozdziela bezpośrednio wpływu słownictwa od szyku ani kształtu słów. Niskie AUC pojedynczych cech nie wyklucza ich kombinacji.

## Rekomendowany następny eksperyment
Powtórzyć cały test na próbach o jednakowej liczebności, z kontrolą na danych przetasowanych oraz kontrolą efektu podłożonego celowo. W tym samym eksperymencie porównać dane z zachowanym słownictwem, lecz przetasowanym szykiem; pozwoli to lepiej oddzielić wpływ słownictwa od kolejności.

Szczegóły: [judge_probe.md](judge_probe.md)

Koszt OpenRouter: 0.01 USD w 18 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.