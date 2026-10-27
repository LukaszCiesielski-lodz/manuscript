# Voynich Lab – przebieg 20261027-201640

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Brute force osobno na każdym zbiorze słów jednakowej długości | obalona | 35/35 | obalona: 2 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Brute force osobno na każdym zbiorze słów jednakowej długości

34 zbiorów testowalnych (6 pominiętych), 6 języków. W żadnym zbiorze długości rękopis nie wygrywa z bełkotem: najwyższy udział słów w słowniku pod kluczem zbioru 93.9% (French, długość 2; bełkot 87.6%, zaszyfrowany tekst 77%). Osobny klucz na długość nie pomaga.

**Synteza rady:**

## Werdykt rady
**Wynik jest sugestywny, ale test nie uzasadnia stanowczego odrzucenia hipotezy.** Zgodność jest umiarkowana: A i D skłaniają się ku obaleniu w badanym zakresie, B kwestionuje wiarygodność metody, a C zajmuje stanowisko ostrożne. Kluczowe jest to, że raport nie dokumentuje pełnej kontroli ujemnej dla głównej miary.

## Co test naprawdę pokazuje
W 34 zbiorach uznanych za testowalne kontrole dodatnie — teksty zaszyfrowane — osiągnęły podane progi. Wyniki rękopisu na ogół nie przewyższają bełkotu, co nie wspiera hipotezy o osobnym kluczu podstawieniowym dla każdej długości. Jest jednak wyjątek: French, długość 2, gdzie wynik rękopisu to 93,9%, a bełkotu 87,6%, wbrew podsumowaniu raportu. Sześć zbiorów pominięto, bo kontrola dodatnia nie spełniła progów; dodatkowo raport pomija małe zbiory długości 8 i 9+.

## Główne zastrzeżenia
Dla danych przetasowanych/przemianowanych podano miarę „spójności”, ale nie porównywalny wynik głównej miary słownikowej ani jasne kryterium zaliczenia. Zatem nie można potwierdzić, że metoda nie wykrywa efektu w kontroli ujemnej — warunku wiarygodności testu. Brakuje też oceny niepewności, a wynik French/2 wymaga wyjaśnienia.

## Rekomendowany następny eksperyment
Powtórzyć test z wieloma kontrolami ujemnymi, stosując do nich tę samą miarę słownikową co do rękopisu; z góry ustalić kryteria i podać rozkład wyników oraz niepewność. Zachować kontrolę dodatnią i osobno oznaczyć zbiory nietestowalne.

Szczegóły: [brute_length.md](brute_length.md)

Koszt OpenRouter: 0.02 USD w 20 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.