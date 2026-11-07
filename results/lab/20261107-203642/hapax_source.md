# hapax_source: nierozstrzygnięta

**Hipoteza.** Słowa jednorazowe (hapaksy) rękopisu to pomyłki kopisty nomenklatora: zniekształcone słowa kodowe, a nie kopie słów z sąsiednich wierszy.

**Metoda.** (1) r* = stopa pomyłek (jeden glif zmieniony, dodany albo usunięty), przy której nomenklator tej samej wielkości i z tych samych słów kodowych ma udział hapaksów w tokenach jak rękopis (Hebrew, Arabic, Latin). (2) Lokalność: jak często częsty sąsiad hapaksu (o jeden glif) stoi w 5 wierszach nad nim, wobec tych samych wierszy innej strony (200 losowań); nadwyżka lokalna rękopisu, bełkotu v7 i nomenklatora przy r*. Kontrole: kopie z 3 wierszy wyżej podłożone w 10% słów nomenklatora muszą dać z ≥ 5; wiersze rękopisu rozdane losowo na strony nie mogą dać z ≥ 3.

Hapaksy nie wykluczają nomenklatora: przy r* ≈ 0.21 pomyłki dają tyle hapaksów co rękopis i podobną lokalność (×2.07 wobec ×1.96, ×1.86, ×1.79), ale bełkot v7 jest prawie tak samo blisko (×1.58, z różnicy +2.4). Lokalność nie odróżnia pomyłek od kopiowania z sąsiedztwa.

## Kontrole

- ✅ **kopie z wierszy powyżej (10% słów nomenklatora) wykryte**: oczekiwano z ≥ 5; wynik: z = 126.2
- ✅ **wiersze rękopisu rozdane losowo na strony bez lokalności**: oczekiwano z < 3; wynik: z = 0.4

## Dowody

- Udział hapaksów w tokenach: rękopis 0.137, v7 0.110; nomenklator osiąga go przy r* = Hebrew 0.21, Arabic 0.21, Latin 0.21 (co piąte słowo kodowe przepisane z błędem).
- Lokalność hapaksów (sąsiad w 5 wierszach nad / w innej stronie, nadwyżka, z): manuscript 0.083/0.040 (×2.07, z = 13.6, n = 3419); v7 0.072/0.046 (×1.58, z = 7.2, n = 2821); Hebrew r* 0.093/0.047 (×1.96, z = 15.8, n = 4787); Arabic r* 0.106/0.057 (×1.86, z = 14.5, n = 4653); Latin r* 0.135/0.075 (×1.79, z = 16.0, n = 4703).
- Nadwyżka lokalna rękopisu wobec modeli (z różnicy): Hebrew r* -0.4, Arabic r* -1.0, Latin r* -2.4, v7 +2.4.

## Zastrzeżenia

- Lokalność nomenklatora zależy od tematu tekstu jawnego: Biblia ma imiona i wątki ciągnące się przez strony, zielnik mógłby mieć ich więcej albo mniej.
- Pomyłka modelowana jako jeden glif; prawdziwy kopista myli też całe słowa i pomija wiersze.

## Literatura

- Rozanova & Temerev, arXiv:2608.17096 (2026)
- Timm & Schinner, Cryptologia 44 (2020)
- Zhang & Sheng, arXiv:2610.34499 (2026)

_Czas: 21 s · 2026-11-07 20:37_