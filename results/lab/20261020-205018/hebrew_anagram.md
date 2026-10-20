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

**Metoda niewiarygodna jako test identyfikujący hebrajski.** Zgoda opinii jest pełna: wszystkie trzy oceny uznają, że kontrola dodatnia przeszła (72,2%), ale kontrola swoistości nie (wietnamski: 90,8%; angielski: 73,7%; rękopis: 69,0%).

## Co test naprawdę pokazuje

Atak potrafi uzyskać wysokie pokrycie na celowo zanagramowanym i zaszyfrowanym hebrajskim, lecz równie wysokie lub wyższe wyniki uzyskuje dla badanych tekstów niehebrajskich. Wynik rękopisu nie stanowi więc swoistego dowodu na hipotezę. **Nie obala jednak samej hipotezy** — test nie rozstrzyga, czy rękopis ma takie podłoże.

## Główne zastrzeżenia

Korpus hebrajski pochodzi z Biblii, nie ze średniowiecznego tekstu. Krótkie słowa mogą sprzyjać przypadkowym trafieniom; raport nie podaje kontroli przetasowanej, a klucz zawiera liczne przypisania wielu glifów do tej samej litery. Nie wiadomo, jak bardzo wpływają one na wynik.

## Rekomendowany następny eksperyment

Powtórzyć atak z niezależnym, średniowiecznym korpusem hebrajskim oraz dopasowanymi kontrolami niehebrajskimi i przetasowanymi. Klucz dobierać na części treningowej, a wynik oceniać na odłożonej części. Eksperyment powinien wykryć efekt w kontroli dodatniej i nie wykrywać go w kontrolach niehebrajskich ani przetasowanych.

## Literatura

- B. Hauer, G. Kondrak, Decoding Anagrammed Texts Written in an Unknown Language and Script, TACL 4 (2016)

_Czas: 816 s · 2026-10-20 21:17_