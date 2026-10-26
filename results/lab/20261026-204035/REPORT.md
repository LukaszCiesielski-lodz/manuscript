# Voynich Lab – przebieg 20261026-204035

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Inny alfabet szyfru dla każdej długości słowa (wspinaczka z dziewięcioma kluczami) | nierozstrzygnięta | 0/0 | metoda niewiarygodna: 2 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Inny alfabet szyfru dla każdej długości słowa (wspinaczka z dziewięcioma kluczami)

Tropy: brak; 6 języków. Największa przewaga zysku rękopisu nad bełkotem: French (-1.16 wobec -1.17 bitu); rękopis z kluczami po długości 5.19 bit/znak wobec naturalnego 2.64.

**Synteza rady:**

## Werdykt rady
**Metoda w tej konfiguracji jest niewiarygodna jako podstawa rozstrzygnięcia. Hipoteza pozostaje nierozstrzygnięta.**

**Zgodność:** wysoka. Opinie zgodnie wskazują na nieudaną kontrolę dodatnią i brak tropu; różnią się głównie nazwaniem werdyktu. Najtrafniej oddzielić niewiarygodność testu od oceny samej hipotezy.

## Co test naprawdę pokazuje
Kontrola dodatnia odzyskała zaledwie **18–44%** symboli, poniżej wymaganego progu **60%**. Test nie wykazał więc, że potrafi znaleźć celowo podłożony efekt. Żaden z sześciu języków nie spełnił kryterium tropu. Największa przewaga nad bełkotem wyniosła około **0,008 bitu** dla francuskiego, wobec wymaganych **0,2**. To nie potwierdza hipotezy, ale z powodu nieudanej kontroli dodatniej nie stanowi też jej rzetelnego obalenia.

## Główne zastrzeżenia
Raport nie podaje wyników kontroli na danych przetasowanych, więc nie wiadomo, czy metoda nie wykrywa efektu tam, gdzie nie powinno go być. Ponadto wynik francuski z kluczami po długości przekracza poziom naturalny o około **2,56 bitu/znak**, a zatem nie spełnia też limitu **0,8**.

## Rekomendowany następny eksperyment
Skalibrować tę samą procedurę na tekstach z dziewięcioma celowo podłożonymi kluczami **i** danych przetasowanych. Dopiero po odzysku co najmniej 60% w kontroli dodatniej oraz braku efektu w przetasowanych danych powtórzyć test rękopisu.

Szczegóły: [lengthkey.md](lengthkey.md)

Koszt OpenRouter: 0.01 USD w 15 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, tencent/hy3; przewodniczący: openai/gpt-6-luna.