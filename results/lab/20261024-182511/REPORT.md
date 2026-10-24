# Voynich Lab – przebieg 20261024-182511

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Zysk z tokenów pozycji: czy słowo zależy od miejsca w wierszu (GPT) | metoda niewiarygodna | 1/2 | metoda niewiarygodna: 4 |
| Generator v6: nawyki skryby ewoluowane na karcie, sędzia na GPU | nierozstrzygnięta | 4/4 | obalona: 1, nierozstrzygnięta: 1 |
| Spójność strony: czy sędzia pozna dwa wiersze z tej samej strony | metoda niewiarygodna | 1/2 | metoda niewiarygodna: 4 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Zysk z tokenów pozycji: czy słowo zależy od miejsca w wierszu (GPT)

Zysk z tokenów pozycji (bit/znak): łacina -0.003, bełkot v5 -0.011, rękopis -0.017, apicius -0.030, martyrology -0.048, chorał -0.055. Rękopis wobec bełkotu v5: -0.006 (próg +0,05); kontrola losowa -0.013, rekordy syntetyczne +0.012.

**Synteza rady:**

## Werdykt rady

**Metoda niewiarygodna.** Zgoda jest wysoka: wszystkie opinie wskazują na niezaliczoną kontrolę pozytywną. W danych syntetycznych oczekiwano zysku co najmniej **0,15 bitu/znak**, a uzyskano **0,012 ± 0,008**. Test nie wykazał więc, że potrafi wykryć celowo podłożony efekt.

## Co test naprawdę pokazuje

W tym ustawieniu dodanie jawnych tokenów pozycji nie poprawiło predykcji rękopisu: raportowany zysk wyniósł **−0,017 ± 0,004 bitu/znak**. Kontrola losowych pozycji spełniła podane kryterium, ale nie zastępuje niezaliczonej kontroli pozytywnej. Wynik nie rozstrzyga, czy zależność od miejsca w wierszu istnieje; nie stanowi też wiarygodnego dowodu przeciw hipotezie. Różnica rękopis–bełkot v5 (**−0,006**) nie osiąga progu **+0,05**.

## Główne zastrzeżenia

- Tylko jeden przebieg treningu na korpus; bootstrap po wierszach nie mierzy zmienności między treningami.
- Dodanie tokenów może samo utrudniać uczenie przy ustalonym budżecie; wynik obejmuje też efekty krawędzi wiersza.
- Ujemne wyniki dla wszystkich korpusów nie rozstrzygają, czy przyczyną jest brak mierzonego efektu, czy ograniczenie metody.

## Rekomendowany następny eksperyment

Powtórzyć test po dostrojeniu modelu i budżetu, na syntetycznej kontroli o porównywalnej długości, z wieloma ziarnami. Kontrola pozytywna musi wykryć wymagany efekt, a dane z przetasowanymi pozycjami nie mogą go wykazywać; dopiero potem ponownie ocenić rękopis.

Szczegóły: [fields_lm.md](fields_lm.md)

## Generator v6: nawyki skryby ewoluowane na karcie, sędzia na GPU

Najlepszy v6: AUC sędziego 0.655 (prawdziwe wobec prawdziwych 0.531, v5 0.658), chybienia na parzystych: edge_mi, hapax_ratio, line_last_m, line_mean_spread (v5: hapax_ratio, line_last_m, line_mean_spread, top10_coverage, type_token_ratio, vocab_density). Sędzia nadal odróżnia tekst bez treści od rękopisu.

**Synteza rady:**

## Werdykt rady

**Nierozstrzygnięta.** W badanym wyszukiwaniu v6 nie uzyskano rozwiązania spełniającego hipotezę, ale wynik nie dowodzi, że takie ustawienia nie istnieją.

**Poziom zgody:** umiarkowanie wysoki co do tego, że badani finaliści nie spełnili deklarowanych kryteriów; mniejszy co do tego, czy wolno uznać test za wiarygodny. Brakuje kluczowej kontroli negatywnej.

## Co test naprawdę pokazuje

Najlepszy zgłoszony wynik sędziego dla v6 to AUC **0,655**, wobec **0,531** dla porównania prawdziwe–prawdziwe i **0,658** dla v5. Sędzia nadal odróżniał więc tekst v6 od rękopisu. Finaliści mieli też uchybienia w **1–4 z 22 miar** na foliałach parzystych. To świadczy o niepowodzeniu tej próby strojenia, nie o niemożliwości dostrojenia reguł w ogóle.

Kontrola czułości na celowo zmienione glify przeszła (**AUC 0,854**), podobnie porównanie prawdziwe–prawdziwe. Raport nie podaje jednak wyniku na danych przetasowanych, wymaganego do uznania kontroli metody za zaliczoną.

## Główne zastrzeżenia

Wyszukiwanie było ograniczone do 25 pokoleń i 32 ustawień, a strojenie nie uwzględniało wyniku sędziego. Ocena sędziego dotyczyła pojedynczych wierszy, nie spójności całych stron. Finalistów sprawdzono na trzech ziarnach i niewidzianych foliałach, ale nie usuwa to tych ograniczeń.

## Następny eksperyment

Przeprowadzić wieloziarnowe strojenie z kryterium obejmującym sędziego, oceniając je na nietkniętym zbiorze; równocześnie wykazać, że metoda wykrywa efekt celowo podłożony, a nie znajduje go w danych przetasowanych.

Szczegóły: [v6.md](v6.md)

## Spójność strony: czy sędzia pozna dwa wiersze z tej samej strony

Para wierszy z tej samej strony: AUC rękopisu 0.526 wobec 0.500 po rozdaniu wierszy i 0.500 dla bełkotu v5 (łacina 0.500, z wszczepionym słowem 0.654). Strona rękopisu nie jest spójniejsza niż losowy zbiór wierszy jej działu.

**Synteza rady:**

## Werdykt rady

**Metoda niewiarygodna w tej konfiguracji.** Zgodność jest wysoka: wszystkie oceny wskazują, że kontrola dodatnia nie przeszła, choć kontrola ujemna przeszła.

## Co test naprawdę pokazuje

Kontrola ujemna dała AUC 0,500, a rękopis 0,526 — wynik bliski losowemu, który sam w sobie nie stanowi przekonującego dowodu spójności stron. Jednak kontrola dodatnia osiągnęła tylko 0,654, poniżej wymaganego progu 0,7. Metoda nie wykazała więc, że potrafi niezawodnie wykrywać podłożony sygnał. Wynik rękopisu **nie rozstrzyga hipotezy i nie wyklucza spójności stron**.

## Główne zastrzeżenia

Test mierzy rozpoznawanie par połówek wierszy na podstawie znaków, nie spójność semantyczną ani inne cechy strony. Różnice rąk skrybów w obrębie działu mogą dostarczać dodatkowych wskazówek, a obcinanie i dopełnianie wierszy do 47 znaków może zniekształcać sygnał.

## Rekomendowany następny eksperyment

Powtórzyć test po skalibrowaniu kontroli dodatniej na danych możliwie zbliżonych do badanego materiału i przy sile sygnału odpowiadającej badanemu efektowi. Kontrola powinna osiągnąć ustalony próg AUC ≥ 0,7, zanim wynik rękopisu zostanie zinterpretowany.

Szczegóły: [cohesion.md](cohesion.md)

Koszt OpenRouter: 0.04 USD w 45 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.