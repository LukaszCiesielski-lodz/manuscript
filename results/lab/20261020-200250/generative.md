# generative: nierozstrzygnięta

**Hipoteza.** Model generatywny potrafi napisać brakujące strony (f12, f59–64, f74, f91–92, f97–98, f109–110) nieodróżnialne statystycznie od prawdziwych.

**Metoda.** Transformer znakowy uczony stronami z tokenami działu, języka Curriera i skryby; walidacja na odłożonych stronach; strony brakujące generowane z atrybutami sąsiadów; wierność: odległość miar kształtu, klasyfikator prawdziwe/wygenerowane (AUC), kopiowanie całych wierszy.

Transformer: 5.43 bit/znak wobec 2.02 dla trigramów. Wygenerowane strony nie są nieodróżnialne od prawdziwych (AUC 0.72, odległość 0.49). Brakujące strony zapisano jako SYNTETYCZNE.

## Kontrole

- ✅ **klasyfikator: prawdziwe vs prawdziwe**: oczekiwano AUC ≈ 0,5 (najwyżej 0,6); wynik: AUC = 0.492
- ✅ **klasyfikator: prawdziwe vs prosty generator samocytowania**: oczekiwano AUC wyraźnie > 0,5 (≥ 0,7); wynik: AUC = 1.000

## Dowody

- Odłożone strony: transformer 5.428 bit/znak, model trigramowy 2.016 (różnica -3.412: tyle struktury leży dalej niż 2 znaki wstecz).
- Wygenerowane strony: odległość od prawdziwych 0.49 (dwie próbki łaciny ~0,2), AUC klasyfikatora 0.715, skopiowane całe wiersze 70.9%, nowe słowa 1.9%.

## Zastrzeżenia

- Wygenerowana strona nie zawiera zaginionej treści; pokazuje tylko, jak statystycznie wyglądałaby strona tego działu i skryby.
- Niskie AUC oznacza, że prosty klasyfikator nie odróżnia wierszy; mocniejszy klasyfikator może odróżnić.
- Atrybuty brakujących stron (dział, skryba) przyjęto od poprzedniej zachowanej strony.

## Rada modeli

## Werdykt rady
**Hipoteza nie została potwierdzona dla badanego modelu i ustawienia; ogólna możliwość, że inny model wygeneruje strony nieodróżnialne, pozostaje nierozstrzygnięta.**

## Poziom zgody
Wysoki: zgodnie uznano, że wygenerowane strony różnią się od prawdziwych według zastosowanych miar, ale wynik nie rozstrzyga o wszystkich modelach generatywnych.

## Co test naprawdę pokazuje
Kontrole klasyfikatora przeszły: AUC dla prawdziwe–prawdziwe wyniosło 0,492, a dla prawdziwe–samocytowanie 1,000. Dla wygenerowanych stron AUC wyniosło 0,715, odległość 0,486; skopiowano 70,9% całych wierszy, a udział nowych słów wyniósł 1,9%. To przemawia przeciw nieodróżnialności **w tym teście**. Test nie odtwarza zaginionej treści ani nie wyklucza sukcesu innego modelu.

## Główne zastrzeżenia
Wynik walidacyjny pogorszył się z około 1,73 do 5,43 bit/znak, mimo spadku błędu treningowego — wskazuje to na przeuczenie i osłabia ocenę końcowego modelu. Zbadano jeden model; nie podano też niepewności miar. Atrybuty brakujących stron przypisano na podstawie sąsiadów, bez niezależnej weryfikacji.

## Rekomendowany następny eksperyment
Powtórzyć test z wczesnym zatrzymaniem wybranym wyłącznie na niezależnym zbiorze walidacyjnym, używając wielu ziaren losowych i odłożonych prawdziwych stron. Ocenić odróżnialność oraz kopiowanie na odrębnym zbiorze testowym.

## Literatura

- A Glyph Is Not a Letter... What the Units of Voynichese Are Not, arXiv:2608.17096
- Timm & Schinner, Cryptologia 44 (2020)

_Czas: 482 s · 2026-10-20 20:36_