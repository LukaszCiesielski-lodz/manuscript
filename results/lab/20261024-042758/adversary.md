# adversary: obalona

**Hipoteza.** Któryś z generatorów bez treści pisze wiersze, których nie odróżni od rękopisu nawet transformer.

**Metoda.** Transformer-klasyfikator (4 warstwy, 192 wymiary) uczony na GPU: prawdziwe wiersze (foliały parzyste) przeciw wierszom każdego generatora (reguły z nieparzystych); AUC na odłożonej połowie, najlepsza epoka. Kontrola: prawdziwe przeciw prawdziwym (nieparzyste) musi dać AUC ≈ 0,5.

Prawdziwe vs prawdziwe: AUC 0.54. Transformer odróżnia każdy generator od rękopisu: v4 (kopiowanie ze zmianami) 0.97, v5 działami (tabela skryby) 0.64, łańcuch słów (pamięć 1) 0.61, tarcza (volvelle) 0.97.

## Kontrole

- ✅ **transformer: prawdziwe vs prawdziwe**: oczekiwano AUC ≤ 0,62; wynik: AUC = 0.539

## Dowody

- v4 (kopiowanie ze zmianami): transformer AUC 0.966 (klasyfikator n-gramowy 0.998).
- v5 działami (tabela skryby): transformer AUC 0.639 (klasyfikator n-gramowy 0.777).
- łańcuch słów (pamięć 1): transformer AUC 0.613 (klasyfikator n-gramowy 0.672).
- tarcza (volvelle): transformer AUC 0.971 (klasyfikator n-gramowy 0.994).

## Zastrzeżenia

- Mały transformer uczony kilka epok na ~8 tys. wierszy; większy model może odróżnić więcej.
- Wiersze jako ciągi znaków EVA; test nie widzi układu strony ani rysunków.

## Rada modeli

## Werdykt rady
**Metoda niewiarygodna w świetle przyjętych kryteriów; hipoteza pozostaje nierozstrzygnięta.** Kontrola prawdziwe–prawdziwe przeszła (AUC 0,539), ale raport nie przedstawia kontroli wykrywającej efekt celowo podłożony ani kontroli na danych przetasowanych.

## Poziom zgody
Opinie początkowe różniły się co do werdyktu. W późniejszej rundzie silniej wybrzmiało, że brak wymaganych kontroli nie pozwala uznać metody za wiarygodną ani automatycznie obalić hipotezy.

## Co test naprawdę pokazuje
Dla czterech przetestowanych generatorów transformer uzyskał AUC od 0,613 do 0,971; wyniki dwóch generatorów były znacznie wyższe. Klasyfikator n-gramowy także odróżniał wszystkie cztery. To przemawia przeciw nieodróżnialności **tych konkretnych generatorów**, ale nie rozstrzyga hipotezy o którymkolwiek generatorze bez treści.

## Główne zastrzeżenia
Brak wymaganych kontroli uniemożliwia ocenę czułości metody i jej zachowania po przetasowaniu. Brak przedziałów niepewności oraz wybór najlepszej epoki mogą zawyżać wyniki; najniższe AUC są bliskie poziomowi losowemu. Test obejmuje tylko cztery generatory i ciągi EVA, nie układ strony ani rysunki.

## Rekomendowany następny eksperyment
Powtórzyć test na niezależnych podziałach danych, z kontrolą dodatnią (celowo podłożony efekt), kontrolą przetasowaną i przedziałami niepewności; szczególną uwagę poświęcić dwóm generatorom z najniższym AUC.

## Literatura

- Vaswani et al., Attention is all you need (2017)
- Gaskell & Bowern (2022)

_Czas: 148 s · 2026-10-24 04:34_