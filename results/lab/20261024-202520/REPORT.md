# Voynich Lab – przebieg 20261024-202520

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Odstępy jako klucz: długości słów tną, przesuwają lub czytają strumień glifów | nierozstrzygnięta | 4/4 | hipoteza keystream w przetestowanej rodz: 1, obalona: 2, nierozstrzygnięta: 1 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Odstępy jako klucz: długości słów tną, przesuwają lub czytają strumień glifów

Przy odstępach EVA: różne słowa na odległość z = -1.2, sąsiednie słowa z = -24.4 (v5 +10.9, v6 +1.5, łacina +46.6); długość opisu 3.896 bit/glif. Żadna z 25 reguł kluczowanych nie koduje rękopisu krócej niż odstępy EVA (najbliżej przesunięcie glifów o długość słowa (chars): 3.895) ani nie daje mu składni, której nie dawałaby bełkotowi (największa przewaga cięcie: długości posortowane (glyphs): +5.6). Odstępy EVA są najlepszym podziałem w tej rodzinie, a klucz w długościach słów nie odsłania jednostek z gramatyką.

**Synteza rady:**

## Werdykt rady

**Brak poparcia dla keystream w przetestowanej rodzinie reguł; ogólna hipoteza pozostaje nierozstrzygnięta.** Zgoda jest wysoka co do ograniczonego wyniku, mniejsza co do tego, czy nazywać go „obaleniem” — uzasadnione jest ono wyłącznie dla badanych przekształceń.

## Co test naprawdę pokazuje

Kontrole przeszły: metoda odzyskała celowo przekształconą łacinę z F1 = 1,00, a zwykła łacina i bełkot v5 nie zyskały na regułach. Mimo to żadna z badanych reguł kluczowanych nie poprawiła kompresji rękopisu w wymaganym stopniu: najlepszy wynik to 3,895 wobec 3,896 bit/glif dla odstępów EVA, daleko od progu 2%. Raport nie stwierdza też wymaganej przewagi składniowej nad bełkotem.

## Główne zastrzeżenia

Wniosek dotyczy skończonej rodziny cięć, przesunięć i transpozycji, nie wszystkich możliwych kluczy. Ponadto sztywne cięcie co 3 glify daje krótszy opis niż podział EVA (3,317 wobec 3,896 bit/glif) — sama kompresja nie potwierdza więc, że EVA wyznacza właściwe jednostki. Ujemna MI sąsiednich słów rękopisu (z = −24,4) pozostaje niewyjaśniona.

## Następny eksperyment

Przetestować osobno **length_code** na danych niewykorzystanych do dopasowania, z karą za złożoność mapowania oraz kontrolami wymagającymi wykrycia celowo podłożonego efektu i jego braku w danych przetasowanych.

Szczegóły: [keystream.md](keystream.md)

Koszt OpenRouter: 0.02 USD w 18 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.