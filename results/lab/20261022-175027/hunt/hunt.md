# Polowanie psów gończych

TABELA (score = przewaga rękopisu nad bełkotem; luka = bity/znak, im mniej tym lepiej):
- [obalony] score +0.04 | luka rękopisu 0.92, bełkot 0.96, kontrola dodatnia 0.03, nadmiar nad językiem +0.66 | Drugi glif rdzeniem, reszta wypełniaczem (kryptolog): {"scope": {"section": "herbal"}, "steps": [{"op": "keep_every", "n": 2, "offset": 1}], "target": "Latin", "target_ops": []}
- [obalony] score -0.01 | luka rękopisu 0.60, bełkot 0.59, kontrola dodatnia 0.00, nadmiar nad językiem -0.11 | Szkielet co 4. z offsetem 1 i abdżad łaciński (dziki pies): {"scope": {"section": "herbal"}, "steps": [{"op": "keep_every", "n": 4, "offset": 1}], "target": "Latin", "target_ops": ["drop_vowels"]}
- [obalony] score -0.02 | luka rękopisu 0.98, bełkot 0.97, kontrola dodatnia 0.03, nadmiar nad językiem +0.82 | Szablonowe wypełnianie (co 3. glif to rdzeń) (dziki pies): {"scope": {"section": "herbal"}, "steps": [{"op": "keep_every", "n": 3, "offset": 0}], "target": "Latin", "target_ops": []}
- [obalony] score -0.05 | luka rękopisu 0.75, bełkot 0.69, kontrola dodatnia -0.15, nadmiar nad językiem +1.81 | Pary glifów jako znaki szyfru rozwlekłego (lingwista): {"scope": {"section": "herbal"}, "steps": [{"op": "group_glyphs", "size": 2}], "target": "Latin", "target_ops": []}
- [obalony] score -0.15 | luka rękopisu 0.53, bełkot 0.38, kontrola dodatnia 0.03, nadmiar nad językiem +0.84 | Akrostych inicjałów, cały tekst (kryptolog): {"scope": {"section": "text"}, "steps": [{"op": "word_initials"}], "target": "Latin", "target_ops": []}
- [obalony] score -0.20 | luka rękopisu 1.29, bełkot 1.08, kontrola dodatnia 0.06, nadmiar nad językiem +0.62 | Odwrócenie glifów w każdym słowie (lingwista): {"scope": {"section": "text"}, "steps": [{"op": "reverse_words"}], "target": "Latin", "target_ops": []}
- [obalony] score -0.26 | luka rękopisu 1.27, bełkot 1.01, kontrola dodatnia 0.06, nadmiar nad językiem +0.65 | q i n jako nulle, pismo od prawej (kryptolog): {"scope": {"section": "text"}, "steps": [{"op": "drop_glyphs", "glyphs": ["q", "n"], "rate": 0.25}, {"op": "reverse_words"}], "target": "Latin", "target_ops": []}
- [obalony] score -0.27 | luka rękopisu 1.18, bełkot 0.91, kontrola dodatnia 0.06, nadmiar nad językiem +0.75 | Nulle q i e, potem rotacja słowa (kryptolog): {"scope": {"section": "text"}, "steps": [{"op": "drop_glyphs", "glyphs": ["q", "e"], "rate": 0.25}, {"op": "rotate", "k": 1}], "target": "Latin", "target_ops": []}
- [obalony] score -0.35 | luka rękopisu 1.28, bełkot 0.93, kontrola dodatnia 0.06, nadmiar nad językiem +0.61 | Odwrócenie kolejności słów w wierszu (lingwista): {"scope": {"section": "text"}, "steps": [{"op": "reverse_lines"}], "target": "Latin", "target_ops": []}
- [obalony] score -0.42 | luka rękopisu 1.36, bełkot 0.95, kontrola dodatnia 0.02, nadmiar nad językiem +0.40 | Hebrajski zapis spółgłoskowy (lingwista): {"scope": {"section": "text"}, "steps": [], "target": "Hebrew", "target_ops": ["drop_vowels"]}
- [obalony] score -0.45 | luka rękopisu 1.29, bełkot 0.84, kontrola dodatnia 0.06, nadmiar nad językiem +0.65 | Usunięcie skrajnych glifów q i n bez odwracania (lingwista): {"scope": {"section": "text"}, "steps": [{"op": "drop_glyphs", "glyphs": ["q", "n"], "rate": 0.25}], "target": "Latin", "target_ops": []}
- [obalony] score -0.45 | luka rękopisu 1.34, bełkot 0.89, kontrola dodatnia 0.06, nadmiar nad językiem +0.68 | co drugie słowo wypełniaczem (kryptolog): {"scope": {"section": "text"}, "steps": [{"op": "take_words", "every": 2, "offset": 0}], "target": "Latin", "target_ops": []}
- [obalony] score -0.69 | luka rękopisu 1.07, bełkot 0.39, kontrola dodatnia -0.40, nadmiar nad językiem +1.62 | Szyfr rozwlekły: pary glifów jako znaki (kryptolog): {"scope": {"section": "text"}, "steps": [{"op": "group_glyphs", "size": 2}], "target": "Latin", "target_ops": []}
- [obalony] score -0.71 | luka rękopisu 0.62, bełkot -0.09, kontrola dodatnia 0.03, nadmiar nad językiem +1.28 | Klucz słowny 'agla' na poziomie słów (kryptolog): {"scope": {"section": "herbal"}, "steps": [{"op": "keystream_shift", "key": "word:agla", "mode": "sub", "unit": "word", "restart": "line"}], "target": "Latin", "target_ops": []}
- [obalony] score -1.73 | luka rękopisu 0.70, bełkot -1.03, kontrola dodatnia -0.66, nadmiar nad językiem +2.86 | Rozwlekły bez fałszywych spacji (kryptolog): {"scope": {"section": "text"}, "steps": [{"op": "join_words"}, {"op": "group_glyphs", "size": 2}], "target": "Latin", "target_ops": []}
- [obalony] score -2.28 | luka rękopisu -0.40, bełkot -2.68, kontrola dodatnia -0.21, nadmiar nad językiem +1.64 | Złoty podział jako strumień klucza Vigenère'a (dziki pies): {"scope": {"section": "cosmological"}, "steps": [{"op": "keystream_shift", "key": "phi", "mode": "sub", "unit": "glyph", "restart": "line"}], "target": "MedievalLatin", "target_ops": []}
Przepisy odrzucone lub z nieudaną kontrolą dodatnią (ostatnie):
- Fibonacci jako klucz stronicowy (reset co stronę): za mało tekstu w zakresie (0 słów)
- sqrt2 jako klucz Vigenère'a z resetem wiersza: za mało tekstu w zakresie (0 słów)
- Grupowanie 2-glifowe z kluczem pierwszym: za mało tekstu w zakresie (279 słów)
- Akrostych inicjałów z korektą e-ulerowską: za mało tekstu w zakresie (0 słów)
- Czyszczenie q/n i przesunięcie e co wiersz: za mało tekstu w zakresie (279 słów)

## Powtórka


## Lista życzeń (nowe klocki)

- (kryptolog) Nomenklator słowo-za-słowo: każde słowo rękopisu to osobny kod z księgi kodowej (liczba → całe słowo/krótkie wyrażenie). Tłumaczyłoby to niską h2 (słowa-kody nie mają wewnętrznej struktury językowej), sztywne pozycje glifów (kody o podobnych wartościach zaczynają się podobnie), powtórzenia bezpośrednie (powtórzone liczby w kluczu) i podobieństwo sąsiednich słów (sąsiednie liczby w tekście jawnym d
- (kryptolog) Szyfr z licznikiem wiersza: ostatnie słowo wiersza jako wskaźnik/klucz dla następnego wiersza (autokey międzywierszowy) — tłumaczyłoby wiersz jako jednostkę i nadreprezentację m, g, p na końcach. Wymaga operacji 'przesuń wiersz n o klucz z wiersza n-1', której nie ma w klockach.
- (dziki pies) Hipoteza 'logografów matematycznych': glify to nie litery, lecz wskaźniki do tablicy stałych (np. pierwiastki wielomianów Cremony) – pozycja w słowie to argument funkcji, a samogłoski EVA to tylko separatory dziesiętne.
- (dziki pies) Steganografia w kształcie glifów: różnice w minimalnych wariacjach znaków (np. 'o' vs '9') mogą kodować bity niezależnie od szyfru podstawieniowego, co tłumaczyłoby entropię 2,30 bita przy 13 językach.
- (dziki pies) Kalendarz tryleuitny: słowa to nie zdania, lecz pary (dzień, faza) z cyklu Metona; 'm' i 'g' na końcu wiersza to markery przesileń, a 'p' na początku to nowie księżyca.
- (kryptolog) Szyfr z kluczem słownikowym typu nomenklator: częste słowa łacińskie (et, in, quod, dicit) mają własne stałe 'kody-słowa' w rękopisie, a rzadkie są pisane litera po literze prostym podstawieniem. Wyjaśniałoby to 69% hapaks legomena (każde rzadkie słowo szyfrowane osobno daje unikatowy ciąg) oraz powtórzenia sąsiednich słów (to samo słowo jawne w kluczu). Klocki nie mają operacji 'słownik częstych 
- (kryptolog) Szyfr kolumnowy Trithemiusa: kolejne słowa wiersza przesuwane są o rosnącą liczbę pozycji w alfabecie (słowo 1 o 1, słowo 2 o 2...), licznik od nowa w każdym wierszu — wymagałoby keystream_shift z unit: word i rosnącym (nie cyklicznym) kluczem.
- (dziki pies) Hipoteza kalendarza liturgicznego: glify to nie litery, lecz kody dni świąt ruchomych (np. p = Niedziela Wielkanocna, q = początek Adwentu) wymagające mapowania na tabelę świąt zamiast alfabetu.
- (dziki pies) Steganografia w interpunkcji wizualnej: glify EVA to tak naprawdę znaki diakrytyczne nakładane na niewidoczny szkielet słów w języku baskijskim, gdzie 'puste' glify są nośnikami informacji o rodzaju gramatycznym.
- (kryptolog) Szyfr 'dwóch alfabetów' Albertiego z przełączaniem co wiersz: glify z pierwszego słowa wiersza wybierają, który z dwóch alfabetów szyfruje resztę wiersza — klocki nie mają operacji przełączania alfabetu ani warunkowego wyboru.
- (kryptolog) Nulle pozycyjne: glif jest pusty tylko na określonej pozycji w słowie (np. 'o' puste wszędzie poza pozycją 2) — drop_glyphs usuwa glify globalnie, a sztywna pozycja q/n sugeruje, że nullem może być glif tylko w pewnym miejscu.
- (kryptolog) Sylabariusz o zmiennej długości: słowo = jeden znak nomenklatora (4,3 glifu średnio pasuje do sylab łacińskich), ale klocki nie mają operacji 'całe słowo jako jeden symbol' — take_words zostawia co n-te słowo, a nie mapuje słowo na znak.
- (dziki pies) Hipoteza kalendarzowa: glify to nie litery, lecz kody dni w roku (np. q=1 stycznia, n=31 grudnia). Słowa to przedziały czasu, a ich długość (4,3) to średnia liczba tygodni w miesiącu. Wymagałoby to mapowania glifów na liczby porządkowe i odczytu jako listy świąt/planet.
- (dziki pies) Hipoteza 'sztywnych miejsc' jako gramatyki: q i n to markery przypadków (nominativus/accusativus), a m/g na końcu wiersza to enclitiki lub rymy w języku, który nie jest podstawieniem, lecz aglutynacją glifów (np. glif = morfem, nie fonem).
- (kryptolog) Szyfr słowo-w-wierszu: każde słowo wiersza szyfrowane innym alfabetem nomenklatora (klucz = numer słowa w wierszu) — klocki nie mają per-słowa zmiany alfabetu, a to tłumaczyłoby sztywne pozycje q/n przy jednoczesnej wysokiej entropii.
- (kryptolog) Szyfr karteliany 'dwie kratki': słowo dzielone na dwie połówki i przeplatane (glify 1,3,5... potem 2,4,6...) — tłumaczyłoby podobieństwa sąsiednich słów i powiązania na styku; brak operacji przeplatania.
- (kryptolog) Redundancja rytualna: każde prawdziwe słowo zapisane dwukrotnie z drobną wariacją (jak w modlitwach) — wyjaśniałoby 0,83% natychmiastowych powtórzeń; brak klocka 'wstaw kopię poprzedniego słowa'.
- (dziki pies) Hipoteza fraktalna: glify to nie litery, lecz współrzędne wektorów w przestrzeni 2D (np. q=start, n=koniec ścieżki), a słowa to rzuty rzutów na siatkę kalendarza astrologicznego (domyślnie: 28-30 dni).
- (dziki pies) Kodowanie różnicowe: słowo to nie ciąg znaków, lecz delta pozycji gwiazd względem poprzedniego słowa (stąd podobieństwo sąsiedztw 2x wyższe niż losowe).
- (dziki pies) Steganografia w długości: liczba glifów w słowie to kod binarny (4,3 glifu ≈ 2 bity), a same glify to tylko szum maskujący (stąd 69% unikalnych słów).

## Synteza przewodniczącego

## Podsumowanie czterech rund

Sfora sprawdziła podstawienia i liczne proste przekształcenia glifów, słów oraz wierszy, głównie z celem odczytu w językach naturalnych. Wyniki zestawiano z bełkotem o podobnych statystykach i wymagano także przejścia kontroli dodatniej.

**Żaden trop nie przetrwał kontroli jako wiarygodny odczyt.** Najwyższy wynik ma przewagę zaledwie **+0,04 bita/znak** nad bełkotem, lukę 0,92 i nieudany wynik kontroli dodatniej. To daleko od progu TROP. Powtórka najlepszych tropów na innej części rękopisu nie dała żadnych wyników: `[]`.

## Co można uznać za martwe

- Proste i homofoniczne podstawienia badanych języków — obalone przez dużą lukę entropii.
- Testowane warianty: wyciąganie glifów, usuwanie q/n, odwracanie, akrostychy, grupowanie par, klucze strumieniowe i praca na słowach — nie wykazały przewagi nad bełkotem albo nie przeszły kontroli dodatniej.
- Kratka Cardana została obalona; atak anagramowy z hebrajskim okazał się nieswoisty.
- Naibbe-podobny szyfr odtwarza entropię, ale nie wyjaśnia zależności na styku słów.

Nie oznacza to obalenia wszystkich szyfrów ani wszystkich hipotez o niejęzykowym zapisie.

## Co warto rozwijać

Dane wskazują na zjawiska, których dotychczasowe przepisy słabo obejmowały: sztywne pozycje glifów, zależności między sąsiednimi słowami i ich stykami oraz strukturę wiersza. Nowe testy powinny mierzyć te cechy, a nie tylko dopasowywać entropię.

## Klocki do dodania najpierw

1. **Nomenklator słowo-za-słowo** oraz wariant hybrydowy: stałe kody częstych słów, osobny mechanizm dla reszty.
2. **Mapowanie całego słowa na symbol** i operacje warunkowe zależne od pozycji glifu lub jego miejsca w wierszu.
3. **Transformacje międzywierszowe** z kluczem pochodzącym z poprzedniego wiersza; testować szczególnie bezpośrednio zależności końcówek i początków wierszy.

Hipotezy o kształcie glifów wymagają danych obrazowych; kalendarze i logografy warto odłożyć, dopóki nie da się sformułować dla nich testów rozróżniających je od bełkotu.