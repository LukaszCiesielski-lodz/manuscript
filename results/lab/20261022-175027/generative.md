# generative: obalona

**Hipoteza.** Model generatywny potrafi napisać brakujące strony (f12, f59–64, f74, f91–92, f97–98, f109–110) nieodróżnialne statystycznie od prawdziwych.

**Metoda.** Transformer znakowy uczony stronami z tokenami działu, języka Curriera i skryby; walidacja na odłożonych stronach; strony brakujące generowane z atrybutami sąsiadów; wierność: odległość miar kształtu, klasyfikator prawdziwe/wygenerowane (AUC), kopiowanie całych wierszy.

Transformer: 1.70 bit/znak wobec 2.02 dla trigramów. Wygenerowane strony nie są nieodróżnialne od prawdziwych (AUC 0.83, odległość 1.00). Brakujące strony zapisano jako SYNTETYCZNE.

## Kontrole

- ✅ **klasyfikator: prawdziwe vs prawdziwe**: oczekiwano AUC ≈ 0,5 (najwyżej 0,6); wynik: AUC = 0.492
- ✅ **klasyfikator: prawdziwe vs prosty generator samocytowania**: oczekiwano AUC wyraźnie > 0,5 (≥ 0,7); wynik: AUC = 1.000

## Dowody

- Odłożone strony: transformer 1.702 bit/znak, model trigramowy 2.016 (różnica +0.314: tyle struktury leży dalej niż 2 znaki wstecz).
- Wygenerowane strony: odległość od prawdziwych 1.00 (dwie próbki łaciny ~0,2), AUC klasyfikatora 0.826, skopiowane całe wiersze 0.0%, nowe słowa 7.2%.

## Zastrzeżenia

- Wygenerowana strona nie zawiera zaginionej treści; pokazuje tylko, jak statystycznie wyglądałaby strona tego działu i skryby.
- Niskie AUC oznacza, że prosty klasyfikator nie odróżnia wierszy; mocniejszy klasyfikator może odróżnić.
- Atrybuty brakujących stron (dział, skryba) przyjęto od poprzedniej zachowanej strony.

## Rada modeli

## Werdykt rady

**Hipoteza obalona w odniesieniu do badanego transformera i przyjętych atrybutów stron.** Wygenerowane strony nie były statystycznie nieodróżnialne od prawdziwych: klasyfikator osiągnął AUC **0,826**, a miara odległości wyniosła **0,995**. Opinie są zgodne co do werdyktu.

## Co test pokazuje

Obie kontrole klasyfikatora przeszły: prawdziwe–prawdziwe dało AUC **0,492**, a prawdziwe–prosty generator samocytowania **1,000**. Wspiera to wiarygodność wyniku dla zastosowanego testu, ale nie dowodzi, że klasyfikator wykrywa każdy rodzaj różnicy. Transformer uzyskał też lepszy wynik predykcji od trigramów (**1,702 wobec 2,016 bitu/znak**), co nie wystarczyło do uzyskania stron nieodróżnialnych.

Test **nie ustala treści ani istnienia zaginionych stron** i nie wyklucza, że inny model generatywny poradziłby sobie lepiej.

## Główne zastrzeżenia

Atrybuty działu i skryby przypisano na podstawie sąsiednich stron. Raport nie podaje przedziałów ufności dla AUC ani szczegółowej kalibracji miary odległości; porównanie z łaciną opiera się tylko na dwóch próbkach. Kontrole sprawdzają klasyfikator na określonych przypadkach, nie na wszystkich możliwych różnicach.

## Rekomendowany następny eksperyment

Powtórzyć generację z **mocniejszym modelem**, dobierając zatrzymanie na walidacji, przy lepiej uzasadnionych atrybutach stron. Ocenić wyniki z przedziałami ufności i kontrolami klasyfikatora na wielu odłożonych stronach.

## Literatura

- A Glyph Is Not a Letter... What the Units of Voynichese Are Not, arXiv:2608.17096
- Timm & Schinner, Cryptologia 44 (2020)

_Czas: 244 s · 2026-10-22 18:59_