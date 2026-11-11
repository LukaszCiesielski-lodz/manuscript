# Voynich Lab – przebieg 20261111-123242

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Jedno słowo = jedna litera? Wybory z karty matki jako ukryty strumień liter | obalona | 2/2 | obalona: 2 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Jedno słowo = jedna litera? Wybory z karty matki jako ukryty strumień liter

Żaden strumień wyborów z karty nie niesie tekstu litera po literze. Pamięć najlepszego strumienia to 0.049 bitu (k1+k3) wobec 0.40 bitu dla ukrytej łaciny. Łamacz, który czyta ukryty tekst (18 par język–strumień z działającą kontrolą), z rękopisu wyciąga ciąg o co najmniej 2.6 bitu na symbol gorszy niż język; kolejność słów pomaga mu najwyżej o +0.34 bitu, tyle co znany nawyk na styku słów.

**Synteza rady:**

## Werdykt rady

**Obalona w zakresie sprawdzonej hipotezy:** jedna litera na słowo, kodowana wyborem z jednej lub dwóch kolumn. Poziom zgody jest **pełny**; oceny niezależne były zgodne co do werdyktu i głównych ograniczeń.

## Co test naprawdę pokazuje

Kontrole metody przeszły: podłożony tekst dał nadmiar pamięci 0,40–0,51 bitu, a łamacz odzyskiwał go z trafnością bliską 100%. W rękopisie najlepszy strumień osiągnął 0,049 bitu (k1+k3), a wyniki łamacza pozostały o co najmniej 2,6 bitu na symbol gorsze od języka naturalnego. Niewielka poprawa względem danych przetasowanych (do 0,34 bitu) nie stanowi porównywalnego sygnału tekstu.

## Główne zastrzeżenia

Wynik nie rozstrzyga wariantów niebadanych: kodowania przez co najmniej trzy kolumny, szyfru Naibbe ani słów-wypełniaczy. Brak wpisu w kolumnie potraktowano jako symbol, co mogłoby osłabić wykrywalność. Łamacz objął tylko sześć wybranych strumieni; raport nie podaje też korekty niepewności za wybór spośród wielu strumieni.

## Rekomendowany następny eksperyment

Przetestować **wariant Naibbe na całych słowach**, z kontrolnym tekstem ukrytym według tego samego schematu i porównaniem z danymi przetasowanymi.

Szczegóły: [card_stream.md](card_stream.md)

Koszt OpenRouter: 0.02 USD w 15 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, tencent/hy3; przewodniczący: openai/gpt-6-luna.