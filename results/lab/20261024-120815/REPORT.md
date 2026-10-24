# Voynich Lab – przebieg 20261024-120815

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Zapis niejęzykowy: chorał, tabulatura tańca, program | obalona | 0/0 | nierozstrzygnięta: 1, metoda niewiarygodna: 2, obalona: 1 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Zapis niejęzykowy: chorał, tabulatura tańca, program

Kryteria podpisu rękopisu spełnione: chorał: słowa tekstu 6/8, bełkot v5 6/8, chorał: sylaby 5/8, chorał: neumy 5/8, kod Python 4/8, łacina 1/8. Chorał i kod mają silną składnię na odległość (niespokrewnione jednostki z = 65, 132, 145), której rękopis nie ma (z = -1.2); dzielą z nim za to dynamikę długości (dodatnia korelacja sąsiadów, DFA powyżej języków).

**Synteza rady:**

## Werdykt rady
**Hipoteza nierozstrzygnięta; test niewiarygodny w obecnej postaci.** Zgodność rady jest wysoka: wszyscy oceniający w rundzie 2 odrzucają automatyczne „obalona” jako nieuzasadnione bez wymaganych kontroli.

## Co test naprawdę pokazuje
Warunkowo, jeśli metoda działa poprawnie, rękopis różni się od badanego chorału w kluczowej mierze: zależność dla niespokrewnionych jednostek wynosi **z = −1,2**, wobec **z = 65–145** dla chorału zależnie od segmentacji. Jednocześnie część miar długości jest podobna. Podpis rękopisu spełnia też bełkot v5 (**6/8 kryteriów**), co ogranicza swoistość tego zestawu cech.

To są wyniki dotyczące zbadanych danych, nie dowód przeciwko wszystkim rodzajom zapisu niejęzykowego. Test nie rozstrzyga, czym jest rękopis.

## Główne zastrzeżenia
Raport nie podaje wyników kontroli wymaganych do uznania metody za wiarygodną: wykrycia efektu podłożonego celowo oraz braku efektu w danych przetasowanych. Ponadto basse danse nie została miarodajnie zbadana (146 kroków), wyniki chorału zależą od segmentacji, a nie sprawdzono zapisu interwałowego.

## Następny eksperyment
Przeprowadzić walidację tej samej, ustalonej z góry procedury: wykazać, że wykrywa celowo podłożony efekt i nie wykrywa go po przetasowaniu danych.

Szczegóły: [notation.md](notation.md)

Koszt OpenRouter: 0.02 USD w 18 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.