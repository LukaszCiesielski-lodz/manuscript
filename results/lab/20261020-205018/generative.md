# generative: obalona

**Hipoteza.** Model generatywny potrafi napisać brakujące strony (f12, f59–64, f74, f91–92, f97–98, f109–110) nieodróżnialne statystycznie od prawdziwych.

**Metoda.** Transformer znakowy uczony stronami z tokenami działu, języka Curriera i skryby; walidacja na odłożonych stronach; strony brakujące generowane z atrybutami sąsiadów; wierność: odległość miar kształtu, klasyfikator prawdziwe/wygenerowane (AUC), kopiowanie całych wierszy.

Transformer: 1.70 bit/znak wobec 2.02 dla trigramów. Wygenerowane strony nie są nieodróżnialne od prawdziwych (AUC 0.83, odległość 1.02). Brakujące strony zapisano jako SYNTETYCZNE.

## Kontrole

- ✅ **klasyfikator: prawdziwe vs prawdziwe**: oczekiwano AUC ≈ 0,5 (najwyżej 0,6); wynik: AUC = 0.492
- ✅ **klasyfikator: prawdziwe vs prosty generator samocytowania**: oczekiwano AUC wyraźnie > 0,5 (≥ 0,7); wynik: AUC = 1.000

## Dowody

- Odłożone strony: transformer 1.703 bit/znak, model trigramowy 2.016 (różnica +0.313: tyle struktury leży dalej niż 2 znaki wstecz).
- Wygenerowane strony: odległość od prawdziwych 1.02 (dwie próbki łaciny ~0,2), AUC klasyfikatora 0.834, skopiowane całe wiersze 0.0%, nowe słowa 6.8%.

## Zastrzeżenia

- Wygenerowana strona nie zawiera zaginionej treści; pokazuje tylko, jak statystycznie wyglądałaby strona tego działu i skryby.
- Niskie AUC oznacza, że prosty klasyfikator nie odróżnia wierszy; mocniejszy klasyfikator może odróżnić.
- Atrybuty brakujących stron (dział, skryba) przyjęto od poprzedniej zachowanej strony.

## Rada modeli

## Werdykt rady
**Badany transformer nie osiągnął statystycznej nieodróżnialności**: klasyfikator odróżniał jego strony od prawdziwych (AUC 0,834; odległość 1,02). Nie uznajemy jednak testu za rozstrzygające obalenie szerszej hipotezy o możliwościach modeli generatywnych: wymagane kontrole nie są kompletne.

## Poziom zgody
Umiarkowany. Opinie zgodnie uznają, że wynik przemawia przeciw zbadanej konfiguracji. Różnią się co do tego, czy wystarcza to do werdyktu „obalona”; rada ogranicza wniosek do badanego modelu i miar.

## Co test naprawdę pokazuje
Kontrole prawdziwe–prawdziwe (AUC 0,492) i prawdziwe–samocytowanie (AUC 1,000) dały oczekiwane wyniki. Raport pokazuje więc odróżnialność wygenerowanych stron w tym porównaniu, ale nie dowodzi, że każdy model generatywny poniósłby porażkę. Nie ustala też treści zaginionych stron ani trafności przypisanych im atrybutów.

## Główne zastrzeżenia
Brakuje kontroli na danych przetasowanych oraz jednoznacznej kontroli z celowo podłożonym efektem, wymaganych do uznania metody za wiarygodną. Nie podano też liczebności próbek ani przedziałów ufności; atrybuty stron przyjęto na podstawie sąsiadów.

## Następny eksperyment
Przeprowadzić ślepą replikację na wielu odłożonych stronach, z kontrolą wykrywającą celowo podłożony efekt i kontrolą na danych przetasowanych, przy uprzednio ustalonych atrybutach i klasyfikatorze.

## Literatura

- A Glyph Is Not a Letter... What the Units of Voynichese Are Not, arXiv:2608.17096
- Timm & Schinner, Cryptologia 44 (2020)

_Czas: 244 s · 2026-10-20 21:21_