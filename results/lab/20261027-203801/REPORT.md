# Voynich Lab – przebieg 20261027-203801

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Generator v6: nawyki skryby ewoluowane na karcie, sędzia na GPU | nierozstrzygnięta | 4/4 | nierozstrzygnięta: 2, obalona: 1 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Generator v6: nawyki skryby ewoluowane na karcie, sędzia na GPU

Najlepszy v6: AUC sędziego 0.642 (prawdziwe wobec prawdziwych 0.531, v5 0.660), chybienia na parzystych: hapax_ratio, line_mean_spread (v5: adjacent_mi_excess, hapax_ratio, line_last_m, line_mean_spread, top10_coverage, type_token_ratio, vocab_density). Sędzia nadal odróżnia tekst bez treści od rękopisu.

**Synteza rady:**

## Werdykt rady
**Nierozstrzygnięta.** Test nie potwierdza hipotezy dla badanego v6, ale nie obala ogólnej możliwości generowania tekstu regułami bez treści. Zgodność opinii jest wysoka co do wyniku negatywnego dla finalistów; różni się ocena, czy uzasadnia on werdykt „obalona”. Rada przyjmuje ostrożniejszy werdykt.

## Co test naprawdę pokazuje
Żaden z pięciu finalistów nie spełnił wszystkich miar na odłożonych foliałach: powtarzały się chybienia `hapax_ratio` i `line_mean_spread`. Sędzia odróżniał v6 od rękopisu (AUC 0,642; odniesienie prawdziwe–prawdziwe: 0,531). Zatem badane ustawienia nie spełniły kryteriów hipotezy.

## Główne zastrzeżenia
Wymienione kontrole przeszły, ale raport nie pokazuje wymaganej walidacji na danych z celowo podłożonym efektem **i** na danych przetasowanych. Nie można więc uznać pełnej wiarygodności metody według tych kryteriów. Ponadto przeszukiwanie było ograniczone (25 pokoleń, populacja 32; pojedyncze ziarno przy ocenie pokoleń), a sędzia badał pojedyncze wiersze, nie spójność całych stron. Wynik nie rozstrzyga też o innych rodzinach generatorów bez treści.

## Następny eksperyment
Przeprowadzić zaślepioną, z góry zaplanowaną walidację całego potoku: sprawdzić odzyskanie efektu celowo podłożonego oraz brak wykrycia efektu w danych przetasowanych, na wielu ziarnach i odłożonych foliałach.

Szczegóły: [v6.md](v6.md)

Koszt OpenRouter: 0.02 USD w 18 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.