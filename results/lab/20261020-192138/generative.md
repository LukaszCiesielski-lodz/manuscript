# generative: obalona

**Hipoteza.** Model generatywny potrafi napisać brakujące strony (f12, f59–64, f74, f91–92, f97–98, f109–110) nieodróżnialne statystycznie od prawdziwych.

**Metoda.** Transformer znakowy uczony stronami z tokenami działu, języka Curriera i skryby; walidacja na odłożonych stronach; strony brakujące generowane z atrybutami sąsiadów; wierność: odległość miar kształtu, klasyfikator prawdziwe/wygenerowane (AUC), kopiowanie całych wierszy.

Transformer: 1.96 bit/znak wobec 2.02 dla trigramów. Wygenerowane strony nie są nieodróżnialne od prawdziwych (AUC 0.90, odległość 0.76). Brakujące strony zapisano jako SYNTETYCZNE.

## Kontrole

- ✅ **klasyfikator: prawdziwe vs prawdziwe**: oczekiwano AUC ≈ 0,5 (najwyżej 0,6); wynik: AUC = 0.492
- ✅ **klasyfikator: prawdziwe vs prosty generator samocytowania**: oczekiwano AUC wyraźnie > 0,5 (≥ 0,7); wynik: AUC = 1.000

## Dowody

- Odłożone strony: transformer 1.964 bit/znak, model trigramowy 2.016 (różnica +0.052: tyle struktury leży dalej niż 2 znaki wstecz).
- Wygenerowane strony: odległość od prawdziwych 0.76 (dwie próbki łaciny ~0,2), AUC klasyfikatora 0.900, skopiowane całe wiersze 0.0%, nowe słowa 23.0%.

## Zastrzeżenia

- Wygenerowana strona nie zawiera zaginionej treści; pokazuje tylko, jak statystycznie wyglądałaby strona tego działu i skryby.
- Niskie AUC oznacza, że prosty klasyfikator nie odróżnia wierszy; mocniejszy klasyfikator może odróżnić.
- Atrybuty brakujących stron (dział, skryba) przyjęto od poprzedniej zachowanej strony.

## Rada modeli

### Werdykt rady
**Obalona dla badanego transformera i zastosowanego protokołu.** Opinie A i B są zgodne; ich pewność jest wysoka, lecz wniosek ma ograniczony zakres.

### Co test naprawdę pokazuje
Obie kontrole klasyfikatora przeszły według kryteriów raportu: AUC 0,492 dla prawdziwych stron i 1,000 dla stron prostego generatora. Mimo to wygenerowane strony odróżniano od prawdziwych z AUC 0,900; raport podaje też odległość 0,765. Wyniki nie wspierają więc statystycznej nieodróżnialności **tego modelu** według użytych miar.

Test nie rozstrzyga, czy inny model mógłby spełnić hipotezę, ani nie odtwarza zaginionej treści.

### Główne zastrzeżenia
Kontrole potwierdzają działanie klasyfikatora tylko dla sprawdzonych przypadków, nie wykluczają artefaktów generacji ani różnic w długości i atrybutach stron. Atrybuty brakujących stron przypisano na podstawie sąsiadów. Brakuje też niepewności wyników i szczegółów podziału walidacyjnego; porównanie odległości z łaciną jest orientacyjne.

### Rekomendowany następny eksperyment
Powtórzyć ocenę na wielu podziałach walidacyjnych, używając silniejszego klasyfikatora oraz stron dopasowanych pod względem działu, skryby i długości, wraz z kontrolami ujemnymi i dodatnimi.

## Literatura

- A Glyph Is Not a Letter... What the Units of Voynichese Are Not, arXiv:2608.17096
- Timm & Schinner, Cryptologia 44 (2020)

_Czas: 109 s · 2026-10-20 19:32_