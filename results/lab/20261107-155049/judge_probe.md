# judge_probe: potwierdzona

**Hipoteza.** To, co transformer-sędzia widzi w rękopisie, a czego nie ma w karcie 23 miar, to słownictwo (słowa rzadkie i nowe), nie szyk ani kształt słów.

**Metoda.** Sędzia z teorii adversary uczony na połowie wierszy (prawdziwe parzyste wobec v7), oceniany na drugiej połowie. Cechy wiersza: liczba słów, średnia długość słowa, udział hapaksów, udział słów nieobecnych w drugim korpusie, udział dziesięciu najczęstszych słów, pierwszy/ostatni wiersz strony. Miary: AUC sędziego; AUC każdej cechy osobno; korelacja Spearmana wyniku sędziego z cechami w obrębie prawdziwych i w obrębie v7; AUC sędziego po dopasowaniu słownictwa (tylko wiersze z samych słów obecnych w obu korpusach ≥ 2 razy). Kontrole: prawdziwe wobec prawdziwych (AUC ≤ 0,62, cechy w [0,45; 0,55]); czułość na 10% zmienionych glifów (≥ 0,7).

Sędzia AUC 0.690 (prawdziwe–prawdziwe 0.532); po dopasowaniu słownictwa 0.566. Najsilniejsza pojedyncza cecha: hapax (AUC 0.58). Ślad sędziego to słownictwo: na wspólnych słowach nie odróżnia.

## Kontrole

- ✅ **sędzia: prawdziwe wobec prawdziwych blisko 0,5**: oczekiwano AUC ≤ 0,62; wynik: 0.532
- ✅ **sędzia: czułość na 10% zmienionych glifów**: oczekiwano AUC ≥ 0,7; wynik: 0.862
- ✅ **cechy: prawdziwe wobec prawdziwych bez różnic**: oczekiwano AUC każdej cechy w [0,42; 0,58]; wynik: words 0.50, mean_len 0.50, hapax 0.49, unseen 0.50, top10 0.50

## Dowody

- Sędzia: prawdziwe wobec v7 AUC 0.690; prawdziwe wobec prawdziwych 0.532; czułość 0.862.
- AUC pojedynczych cech (prawdziwe wobec v7): words 0.52, mean_len 0.48, hapax 0.58, unseen 0.52, top10 0.51, first_line 0.49, last_line 0.49.
- Korelacja wyniku sędziego z cechami w obrębie prawdziwych: words -0.08, mean_len -0.00, hapax +0.04, unseen +0.08, top10 -0.06, first_line +0.05, last_line +0.09; w obrębie v7: words -0.23, mean_len -0.20, hapax -0.06, unseen -0.06, top10 +0.00, first_line +0.03, last_line +0.01.
- Słownictwo dopasowane (same słowa obecne w obu korpusach ≥ 2 razy; 247 wierszy na stronę): AUC 0.566.
- Wiersze uznane za najprawdziwsze: pchocthy chypchy qotchy chcfhhy sy | sal lcheal lkeeey okar ar ain olcheees ol cheal okaiin ykar al okalam | okar sheey shekealy | qokeeol olcheeey lcheam | psheoky odaiir qoy ofshod chypchey ypchedy ain chofo chephdy. Najfałszywsze: pchey qokair olkaiin sheey ollchedy qokol dain dol dain okeeoly | qokeedy lcholkan chepcheor oeedy qokeey oky chekedy qokedy lsheody qokaiin okain oltshol chor ykam | ysheeo qoeeeo le okaiin dain okeeo lkaiin shey lkol qokchdor al keedy lpcheeo | pol or dalary kchedy qokeey qokain chedy qol chdy qolchy | qotcheos chopchol chokcheod otcho qokol odaiin oeeaiin.

## Zastrzeżenia

- Dopasowanie słownictwa wybiera wiersze z częstych słów; sędzia na nich uczy się mniej (mniej wierszy), więc AUC spada też z braku danych; stąd próg względem prawdziwe–prawdziwe, nie bezwzględny.
- Cechy są korelatami, nie wyjaśnieniem; sędzia może używać kombinacji, której żadna cecha nie oddaje.

## Rada modeli

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

## Literatura

- Vaswani et al., Attention is all you need (2017)
- Timm & Schinner (2019)

_Czas: 35 s · 2026-11-07 15:55_