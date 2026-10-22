# hebrew_anagram: metoda niewiarygodna

**Hipoteza.** Rękopis to hebrajski z przestawionymi literami w słowach (anagramy), zaszyfrowany podstawieniem (Hauer i Kondrak 2016).

**Metoda.** Atak słownikowy odporny na anagramy: klucz glif→litera dobierany tak, by jak najwięcej słów po posortowaniu liter było anagramem słowa z hebrajskiego słownika. Kontrola dodatnia: hebrajski zanagramowany i zaszyfrowany przez nas. Kontrola swoistości: ten sam atak na tekstach na pewno nie-hebrajskich (łacina, angielski, wietnamski...) i na bełkocie z szyfru Naibbe-podobnego.

Atak anagramowy daje rękopisowi 69.0%, ale NIE jest swoisty: tekst Vietnamese osiąga 90.8% przy 72.2% dla prawdziwego hebrajskiego. Wysokie pokrycie bierze się z powtarzalności krótkich słów, nie z hebrajskiego.

## Kontrole

- ✅ **hebrajski zanagramowany i zaszyfrowany**: oczekiwano pokrycie słownikiem ≥ 50%; wynik: 72.2%
- ❌ **swoistość: teksty na pewno nie-hebrajskie**: oczekiwano pokrycie co najmniej 10 pkt niższe niż hebrajskie; wynik: najwyżej Vietnamese: 90.8% wobec hebrajskiego 72.2%

## Dowody

- Odsetek słów, które po odszyfrowaniu są anagramami słów hebrajskich: hebrajski (kontrola) 72.2%, rękopis 69.0%; teksty nie-hebrajskie: Latin 49.0%, Polish 43.5%, English 73.7%, Finnish 42.1%, Vietnamese 90.8%, szyfr Naibbe-podobny 65.2%.

## Zastrzeżenia

- Hebrajski korpus to Biblia, nie średniowieczny tekst; inna ortografia może zmienić wynik.
- Krótkie słowa łatwo trafiają w słownik przypadkiem; dlatego porównujemy z bełkotem z tych samych glifów.

## Rada modeli

## Werdykt rady
**Metoda niewiarygodna jako swoisty test hipotezy „hebrew_anagram”.** Zgoda jest pełna: wszyscy czterej recenzenci uznali, że kontrola swoistości nie przeszła.

## Co test naprawdę pokazuje
Kontrola dodatnia zadziałała: zaszyfrowany, zanagramowany hebrajski osiągnął 72,2% przy wymaganym minimum 50%. Swoistość jednak zawiodła: wietnamski uzyskał 90,8%, angielski 73,7%, a rękopis 69,0%. Wynik rękopisu jest też bliski wynikowi szyfru Naibbe-podobnego (65,2%). Zatem ta metoda nie odróżnia wiarygodnie hebrajskiego od danych niehebrajskich. **Nie rozstrzyga to, czy rękopis ma hebrajskie podłoże** — podważa wartość dowodową tego testu.

## Główne zastrzeżenia
Kontrolę hebrajską oparto na Biblii, nie na tekście średniowiecznym. Raport wskazuje też na przypadkowe trafienia krótkich słów; dodatkowo klucz przypisuje wiele różnych glifów do tych samych liter. Te ograniczenia mogą wpływać na pokrycie słownikiem.

## Rekomendowany następny eksperyment
Przeprowadzić z góry określony test porównawczy, zachowując w kontrolach rozkład glifów i długości słów rękopisu, ale losowo zmieniając ich przyporządkowanie do słów. Sprawdzić, czy oryginał wyraźnie przewyższa takie kontrole, zachowując kontrolę dodatnią z celowo zaszyfrowanym hebrajskim.

## Literatura

- B. Hauer, G. Kondrak, Decoding Anagrammed Texts Written in an Unknown Language and Script, TACL 4 (2016)

_Czas: 810 s · 2026-10-22 18:48_