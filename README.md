# Rękopis Wojnicza w liczbach

Laboratorium do statystycznej analizy rękopisu Wojnicza (Beinecke MS 408).
Czysty Python 3, bez zależności.

**Nie odczytaliśmy rękopisu.** Nikt tego jeszcze wiarygodnie nie zrobił.
Ten projekt robi rzecz skromniejszą, ale sprawdzalną: mierzy tekst tymi samymi
miarami co 12 języków, atakuje go łamaczem szyfrów z obowiązkowymi próbami
kontrolnymi i sprawdza, które hipotezy przetrwają kontakt z danymi.

Raport z wykresami: [`docs/index.html`](docs/index.html) (otwórz w przeglądarce).

## Najważniejsze wyniki

Liczby z `docs/results.json` (35 000 słów na tekst; języki to ten sam fragment
Biblii, rękopis liczony w glifach).

| | rękopis | 12 języków |
|---|---|---|
| entropia warunkowa h₂ (bity/znak) | **2,30** | 2,89–3,65 |
| sztywność kolejności znaków w słowie | **0,88** | 0,66–0,74 (wietnamski 0,90) |
| gęstość słownika (słowa z „sąsiadem” o 1 znak) | **99%** | 43–87% (wietnamski 98%) |
| kolejne słowa różniące się 1 znakiem | **4,4%** | 0,1–1,4% |

1. **Szyfr podstawieniowy (prosty i homofoniczny) wykluczony dla 11 z 12 języków.**
   Łamacz (`voynich/cipher.py`) odzyskuje 93–100% liter szyfrów kontrolnych, a na
   rękopisie najlepszy klucz zostawia lukę 1,07–1,55 bita na znak względem tego,
   co tekst „wie” sam o sobie. Wyjątek: wietnamski (91 liter z tonami), gdzie
   łamacz nie łamie nawet kontroli (46% liter), więc brak werdyktu.
2. **Tekst jest zbyt przewidywalny jak na język** i żadne podstawienie znaków
   tego nie zmienia (test `test_substitution_leaves_fingerprint_unchanged`).
3. **Glify mają stałe miejsca w słowie**: `q` na początku w 99%, `n` na końcu w 98%.
4. **Sąsiednie słowa są do siebie podobne** dwa razy częściej niż po przetasowaniu
   (test permutacyjny); w łacinie i włoskim odwrotnie.
5. **Wiersz jest jednostką**: `m` i `g` ponad 6× częściej w ostatnim słowie wiersza,
   `p` ok. 2,4× częściej w pierwszym.
6. **Zgodne z językiem**: prawo Zipfa i słownictwo zależne od działu.
7. **Hipoteza samocytowania** (Timm i Schinner 2020) częściowo: nasz generator
   odtwarza gęstość słownika i podobieństwo sąsiadów (nawet z nadmiarem), ale nie
   niską entropię: h₂ = 2,65 zamiast 2,30.

### Etap 2: łacina średniowieczna, szyfry sylabiczne, lepszy generator

8. **Łacina średniowieczna wykluczona** (11 tekstów z VII–XV w. plus Kolumella:
   Izydor, Hugo od św. Wiktora, Tomasz z Akwinu, Złota legenda, Kempis i inne).
   Na mapie odcisków palca (`docs/index.html#medieval`) tworzą zwarte skupisko
   z Wulgatą, daleko od rękopisu. Łamacz z modelem łaciny średniowiecznej łamie
   kontrole w 99,7–99,8%, a na rękopisie zostawia lukę 1,15 bita (zielnik) i 1,33 bita (dialekt B).
9. **Skróty skrybów nie pomagają**: łacina ze skrótami (`⁊`, `-ꝰ`, `-ꝝ`, `ꝯ-`, kreska
   zamiast m/n) ma h₂ ≈ 3,5 zamiast 3,3, czyli jest dalej od rękopisu (2,3).
10. **Słowo = sylaba wykluczone**: łacina rozbita na sylaby ma 621–766 różnych sylab na 13 tys.,
    rękopis 3800 różnych słów; sylaby mają 2,3 litery, słowa rękopisu 4,0 glifu.
11. **Szyfr sylabiczny/rozwlekły słowo za słowem mało prawdopodobny**: każdy taki kod
    zachowuje powtórzenia słów, a rękopis powtarza słowo zaraz po sobie w 0,83% par
    (55 różnych słów), najbardziej powtarzalny z 24 tekstów porównawczych w 0,22%.
    Przykładowy kod sylabiczny obniża entropię łaciny (3,3 → 2,9) i usztywnia
    pozycje glifów, ale daje za długie słowa.
12. **Generator**: samo kopiowanie słów ze zmianami, nawet podpatrzonymi u skryby
    (14 663 par), daje h₂ ≈ 3,0. Dopiero dodanie gramatyki kształtu słowa (trigramy
    glifów uczone na liście różnych słów, bez częstości) daje h₂ = 2,30 i przy okazji
    trafia w h₃ (2,04 vs 2,08), sztywność glifów, gęstość słownika i powtórzenia.
    Parametry dobrane tylko pod h₂ i podobnych sąsiadów. Nie odtwarza liczby hapaksów
    (45% vs 69%), długości słów (5,1 vs 4,3), nachylenia Zipfa ani efektów końca wiersza.

Wykluczamy konkretne hipotezy, nie wszystkie. Model trigramowy nie wychwyci
szyfrów przestawieniowych, sylabicznych ani nomenklatorów (kodów całych słów).

## Etap 3: Voynich Lab na Colabie

`colab/Voynich_Lab.ipynb` uruchamia na GPU (Colab Pro, High-RAM) testy hipotez z kontrolami metody,
a każdy wynik omawia rada modeli przez OpenRouter (opinie → wzajemna recenzja → synteza przewodniczącego).
Werdykt testu wynika tylko z liczb i kontroli; rada go komentuje. Przegląd literatury: [`docs/LITERATURA.md`](docs/LITERATURA.md).

| teoria | test | wynik lokalny (CPU, tryb szybki) |
|---|---|---|
| `numbers` | 5 systemów liczbowych sprzed 1450 r.; etykiety zodiaku jako dni 1–30 | obalona |
| `illustrations` | słowa przy rysunkach; CLIP + test Mantela; nazwy roślin od modelu wizyjnego jako criby | części B i C tylko na Colabie |
| `generative` | transformer znakowy, brakujące strony, klasyfikator prawdziwe/wygenerowane; opcjonalnie SDXL+LoRA | tylko na Colabie |
| `naibbe_cipher` | szyfr Naibbe (Greshko 2025), rekonstrukcja z opisu | nierozstrzygnięta |
| `cardan_grille` | bełkot z kratki Cardana (Rugg 2004) | obalona |
| `hebrew_anagram` | hebrajskie anagramy (Hauer i Kondrak 2016) z kontrolą swoistości | metoda niewiarygodna |
| `basque` | baskijski pod szyfrem podstawieniowym: Leizarraga 1571 i prasa współczesna | obalona (luka 0,96–0,99 bita) |
| `nomenclator` | księga kodów słowo-za-słowo, łamacz na poziomie słów; rozstrzyga zysk z szyku słów | obalona dla łaciny, włoskiego, niemieckiego (rękopis ±0,01 bita, zakodowany tekst +0,13–0,47) |
| `hoax` | tekst bez treści z reguł skryby (generator v5 „tabela skryby”), reguły z foliów nieparzystych, sprawdzian na parzystych | nierozstrzygnięta: v5 działami 16/22 miar, klasyfikator wierszy AUC 0,78–0,80 (prawdziwe vs prawdziwe 0,55; v4: 0,998); odtwarza dynamikę długości słów (korelacja sąsiadów +0,156 wobec +0,159), ale nie powtórzeń w wierszu |
| `syntax` | zależność między różnymi słowami odległymi o 2–7 słów (informacja wzajemna ponad tasowanie w stronie i miejscu w wierszu), osobno powtórzenia i warianty | obalona: częste słowa bez zależności (z = −1,2; 5 tekstów językowych z ≥ 3,7), za to nadmiar powtórzeń i wariantów (z ≈ 9), profil płaski z odległością |
| `romance` | język (proto)romański (Cheshire 2019): łacina ludowa (Egeria, ok. 400), starofrancuski (IX–XIII w.), Biblie: włoski, hiszpański, portugalski, francuski, rumuński | obalona: luka 1,09–1,26 bita przy kontrolach 99–100%; każdy tekst romański ma daleką składnię (z ≥ 11), rękopis nie (z = −1,2) |
| `lengths` | słowa zamienione na liczby znaków: autokorelacja sąsiadów, zygzak krótkie–długie, wykładnik DFA, efekt wiersza; 20 tekstów językowych, generatory, ciąg losowy | obalona: sąsiednie długości dodatnio skorelowane (+0,16; w 17 z 20 języków ujemnie), najsilniejsza pamięć długozasięgowa (DFA 0,60 wobec 0,47–0,58), całe wiersze „długie” lub „krótkie” |
| `brute` | brute force: każda z 4000 najczęstszych trójek kolejnych słów pod jednym kluczem litera-za-glif w ~53 językach epoki (Biblie, korpusy historyczne UD, łacina średniowieczna, aramejski Targumu Onkelosa, syryjska Peszitta); zgodność kluczy między trójkami, klucz z połowy wierszy sprawdzany na drugiej | obalona (Colab A100, 51 leksykonów, 4000 trójek, 39 min): w żadnym języku rękopis nie wygrywa z bełkotem v5 – najwyżej 25% słów w słowniku pod wspólnym kluczem (starofrancuski; bełkot 30%), zaszyfrowany prawdziwy tekst 96–100%; 3 pisma nietestowalne (amharski, hindi, hebrajski biblijny); aramejski i syryjski (lokalnie, 800 trójek): rękopis 14% i 25% słów, bełkot 15% i 30%, zaszyfrowany tekst 98–100% |
| `wheel`, `adversary`, `genres` | odjechane pomysły średniowieczne: tarcza Llulla (volvelle) ewoluowana na GPU na rękopisie i tekstach kontrolnych, najlepsza tarcza pisze tekst oceniany jak generatory; transformer-sędzia uczony na GPU przeciw każdemu generatorowi bez treści; litania i imiona barbarzyńskie (Ars Notoria, Liber Iuratus) mierzone jak rękopis | do uruchomienia w Colabie: `colab/Voynich_Kolo.ipynb` |
| `transcriptions`, `cognate`, `hillclimb` | łamacze z literatury: czy podpis rękopisu trzyma w transliteracjach Curriera, FSG, v101, Takahashiego; NeuroDecipher (Luo, Cao, Barzilay 2019): miękki klucz glif–litera i transport optymalny między słownictwem rękopisu a słownikiem każdego języka, kontrola na zaszyfrowanym tekście z szumem pisowni; atak homofoniczny jak w AZdecrypt: tysiące wspinaczy na GPU z modelem 4-gramowym, klucz z wierszy nieparzystych oceniany na parzystych | do uruchomienia w Colabie: `colab/Voynich_Lamacze.ipynb` |
| `phonotactics` | czy słowa są zbudowane jak słowa mówione: algorytm Suchotina wyznacza „samogłoski” rękopisu i każdego z ~50 języków, słowa zamienione na wzorce spółgłoska–samogłoska, rozkłady porównane dywergencją Jensena-Shannona; kontrola: glify przetasowane w słowie | nierozstrzygnięta (lokalnie): samogłoski o, a, e, y; naprzemienność C/V 0,80 jak w łacinie; rozkład wzorców w odległości 0,21 bita od najbliższego języka (starofrancuski), gdy języki leżą od siebie 0,13 (mediana) do 0,26; bełkot v5 wypada tak samo |
| `length_code` | treść w długościach słów: ciąg liczb glifów jako kod liter, cyfr lub bitów parzystości; pojemność, struktura wobec tasowań w wierszu, odczyt cyfra–litera wspinaczką z modelem 4-gramowym 8 języków, odczyt Bacona; kontrola: łacina wszczepiona jako długości | obalona (lokalnie): 9 wartości, 2,7 bita/słowo, trzy długości to 75% ciągu; odczyt jako litery nie przebija ciągu przetasowanego w żadnym języku (≤ 0,06 bita), bity parzystości bez struktury; kontrola odzyskuje wszczepioną łacinę |
| `chronology` | strzałka czasu kopiowania: czy hapaksy mają źródła (sąsiadów o jeden glif) na kartach wcześniejszych; tło tasujące strony tylko w obrębie bloków działu i języka, osobno wewnątrz bloków; kontrole: syntetyczne kopiowanie (musi pokazać strzałkę), łacina (nie może) | obalona (lokalnie): z = −12 przy tasowaniu całego kodeksu, ale 0,0 w obrębie bloków i od −2,1 do +1,0 wewnątrz bloków; sygnał globalny to układ działów; kontrole z = +21 i +12, łacina −0,5 |
| `hands` | czy słowa kształtuje ręka skryby (Davis 2020), czy treść: klasyfikator wierszy z odłożonymi kartami, pary rąk w tym samym dziale i języku wobec losowego rozdania kart; efekt działu w tej samej ręce | obalona (lokalnie): ręce różnią się w zielniku B (AUC 0,72–0,90, z = +2,3 do +3,5), ale dział w tej samej ręce różnicuje mocniej (0,73–0,97); reguły słów idą za treścią lub trybem pisania, nie za skrybą |
| `notation` | zapis niejęzykowy: chorał gregoriański z bazy Cantus (63 tys. melodii Volpiano; słowa tekstu, sylaby, neumy), tabulatura basse danse (Bruksela 9085), kod Pythona jako kontrast, łacina i bełkot v5 przez baterię podpisu rękopisu (8 kryteriów, cecha definiująca: brak składni na odległość); osobny notebook `colab/Voynich_Notacja.ipynb` | obalona (lokalnie): chorał i kod mają bardzo silną składnię na odległość (jednostki niespokrewnione z = 62–166, rękopis −1,3); dzielą z rękopisem tylko dynamikę długości (dodatnia korelacja sąsiadów, DFA 0,67–0,71 wobec 0,60 rękopisu i 0,52 łaciny) |
| `labels`, `records`, `lists` | tor „zapis rekordowy” (część CPU, `colab/Voynich_Rejestr.ipynb`, bez jednostek GPU): etykiety przy rysunkach jako podsłownik nazw i ich cytowanie przez akapity strony; wiersz jako rekord o polach (miejsce słowa odczytane z samego słowa, foliały odłożone; informacja wzajemna klasy słowa i miejsca; przewidywanie pola z sąsiadów); podpis rękopisu wobec list średniowiecznych (martyrologium Usuarda, Apicius, glosariusz Alphita, `data/lists/`) | lokalnie (szybki tryb): etykiety są osobnym podsłownikiem (hapaksy z = +12, o- +27, q- −12, długość +11), ale akapity nie cytują etykiet swojej strony ponad tło (z = +1,4); reszta do uruchomienia |
| `fields_lm`, `v6`, `cohesion` | tor „zapis rekordowy” (część GPU, `colab/Voynich_Rejestr_GPU.ipynb`): zysk małego GPT z tokenów pozycji słowa; generator v6 (v5 z tłumieniem słów już użytych, 18 ustawień ewoluowanych na CPU na karcie foliałów nieparzystych, finaliści na parzystych, sędzia-transformer na GPU); spójność strony (sędzia par wierszy z tej samej strony wobec pseudostron) | `v6` nierozstrzygnięta: ewolucja zbija chybienia z 6 (v5) do 4 na parzystych (zostają hapaksy, m na końcu wiersza, rozrzut średniej długości, związek końca słowa z początkiem następnego), ale sędzia nadal odróżnia (AUC 0,655; v5 0,658; prawdziwe–prawdziwe 0,531): to, co zdradza bełkot, nie siedzi w 22 miarach. `fields_lm` metoda niewiarygodna: rekordy syntetyczne zyskały 0,012 bitu zamiast ≥ 0,15, bo GPT z oknem 256 znaków i tak zna miejsce słowa w wierszu (liczy kropki), więc tokeny pozycji są zbędne; test źle pomyślany, nie powtarzać. `cohesion` metoda niewiarygodna: kontrola dodatnia 0,654 < 0,7; rękopis 0,526 wobec 0,500 po rozdaniu wierszy, czyli brak oparcia dla spójności strony |
| `keystream` | odstępy jako klucz zapisany w tekście (`colab/Voynich_Klucz.ipynb`, CPU): 31 reguł cięcia, przesuwania i czytania strumienia glifów według ciągu długości słów (w glifach i w znakach EVA) na rękopisie i bełkocie v5; podział oceniany długością opisu (MDL), jednostki składnią na odległość i informacją sąsiadów; kontrole: łacina z odstępami przepisanymi regułą z rodziny i łacina czytana kolumnami odzyskane (F1 = 1,0), zwykła łacina i bełkot v5 nie zyskują na żadnej regule | lokalnie (szybki tryb, 1500 wierszy): nierozstrzygnięta formalnie (największa przewaga składni nad bełkotem +3,6 przy progu 2,5, szum małej próbki; pełny przebieg na Colabie), ale żadna reguła nie koduje rękopisu krócej niż odstępy EVA (najbliżej 4,707 wobec 4,709 bit/glif), a wszystkie cztery kontrole przechodzą; odstępy EVA są najlepszym podziałem w tej rodzinie. Dwa dowody uboczne: (1) sąsiednie słowa rękopisu niosą o sobie **mniej** informacji niż dwa losowe słowa tej samej linii (z = −24 na pełnym tekście, −7 do −32 działami), gdy v5 ma +11, v6 +1,5, łacina +47; diagnoza: efekt krawędzi wiersza, bo z pierwszym i ostatnim słowem trzymanym na miejscu nadwyżka jest dodatnia (+0,09 bitu jak u v5): pierwsze i ostatnie słowa wierszy są osobnym słownictwem jako całe słowa, nie tylko przez glify p/m/g, czego v5 nie odtwarza; dodane do karty jako 23. miara; (2) kawałki po 3 glify kodują rękopis i bełkot krócej niż ich słowa (3,32 wobec 3,90 bit/glif), łacinę dłużej (3,89 wobec 3,45): słowa rękopisu nie są oszczędnymi jednostkami |
| `v6` jako v7 | generator v7 (`colab/Voynich_V7.ipynb`, A100 ok. 40 min): v6 plus zasób całych słów otwierających i zamykających wiersz (`p_edge`) i „unikanie sąsiada” (`neighbour_gamma`), oraz 23. miara karty `adjacent_mi_excess` (informacja sąsiednich słów ponad losowe słowa linii: rękopis −0,17 bitu, v5 +0,03, języki dodatnie); ewolucja 20 ustawień, finaliści na parzystych, sędzia-transformer | 27.10 (Colab, 25 pokoleń): nierozstrzygnięta. Najlepszy finalista chybia na parzystych tylko 2 z 23 miar (hapaksy, rozrzut średniej długości wiersza; v6: 4, v5: 7), zasób słów krawędzi weszło w użycie (`p_edge` 0,33–0,52), unikanie sąsiada ewolucja wyzerowała. Sędzia nadal odróżnia: AUC 0,642 (v6 0,655, v5 0,660, prawdziwe–prawdziwe 0,531). To, co zdradza bełkot, nadal nie siedzi w karcie; stały ślad to za mało hapaksów |
| `lengthkey` | inny alfabet szyfru dla każdej długości słowa (`colab/Voynich_Klucz_Dlugosci.ipynb`, A100 ok. 1 h): glif w słowie o danej długości jako osobny symbol, wspinaczka homofoniczna szuka dziewięciu kluczy naraz; zysk rękopisu z kluczy po długości wobec zysku bełkotu v5 i glifów przemianowanych; kontrola: łacina zaszyfrowana dziewięcioma kluczami odzyskana | 26.10: metoda niewiarygodna w tej konfiguracji: dziewięć kluczy odzyskane w 18–44% (jeden klucz 94–100%), bo 9× więcej symboli przy tej samej liczbie kroków; z kluczami po długości każdy tekst czyta się gorzej niż z jednym (wspinaczka nie zbiega). Mimo to w żadnym z 6 języków zysk rękopisu nie przebił zysku bełkotu (max 0,01 bitu). Do poprawy: start z klucza jednokluczowego, kroki ×7 |
| `brute_length` | brute force osobno na każdym zbiorze słów jednakowej długości (`colab/Voynich_Brute_Dlugosci.ipynb`, A100 ok. 30–40 min): zbiory 2–8 glifów i 9+, każdy jako osobny szyfr z własnym kluczem, trójka po trójce przeciw 6 leksykonom; tło i kontrola jak w `brute`, per zbiór | obalona (27.10, 563 s): 34 zbiory testowalne (kontrola dodatnia dla długości 4–8 odzyskuje klucz w 97–100%), w żadnym rękopis nie wygrywa z bełkotem; słowa o długości 5–8 pod własnym kluczem czytają się jako słowa języka w 0–8% (bełkot tyle samo, zaszyfrowany tekst 97–100%); dla długości 2–3 wysokie udziały (do 94%) są wspólne rękopisowi i bełkotowi, bo prawie każdy dwuliterowy ciąg jest słowem; zbiory 9+ za małe (209 słów) |
| `plant_pairs` | ta sama roślina w dwóch miejscach (`colab/Voynich_Rosliny.ipynb`, CPU): 9 par „ta sama roślina” i 28 „podobna” (Zandbergen, Petersen) między działem farmaceutycznym a zielnikiem; wspólne słownictwo ważone rzadkością wobec losowych stron tego samego języka Curriera, ranga prawdziwego partnera; etykiety fragmentów w tekście zielnika; kontrole: słowa partnera wszczepione (z = 20), pary przełączone (z = −0,7) | obalona (lokalnie): pary „ta sama roślina” dzielą słów MNIEJ niż losowe strony (z = −1,8, mediana rangi 0,82), wszystkie pary z = −1,0 (ranga 0,61), etykiety z = −1,0; najbliższe słownictwem są sąsiedzi w tym samym zeszycie (f87–f90), nie pary tej samej rośliny: tekst nie mówi o tym, co jest narysowane |
| `judge_probe` | co widzi sędzia (`colab/Voynich_Sedzia.ipynb`, A100 ok. 10 min): sędzia prawdziwe wobec v7 przepytany cechami wiersza (hapaksy, słowa nieobecne w drugim korpusie, długość, miejsce na stronie) i AUC po dopasowaniu słownictwa (same słowa wspólne) | potwierdzona (Colab 7.11, 35 s): sędzia AUC 0,690 (prawdziwe–prawdziwe 0,532, czułość 0,862); po dopasowaniu słownictwa 0,566; najsilniejsza pojedyncza cecha: hapaksy (AUC 0,58); korelacje wyniku sędziego z cechami w obrębie prawdziwych bliskie zera: ślad sędziego to słownictwo, nie szyk. Rada: kierunkowo tak, ale brak kontroli na danych przetasowanych i próba 247 wierszy; do powtórzenia na równych próbach |
| `atoms`, `atoms_draft` | ontologia ilustracji (`data/atoms/`, `colab/Voynich_Atomy.ipynb`, CPU): rysunki rozebrane na atomy, jeden rekord na etykietę (853 loci na 51 stronach), cechy tylko obserwowalne ze słownika kontrolowanego (`vocab.json`), wpisywane przez ludzi (zgodność dwóch osób: kappa); test rebusu: informacja wzajemna każdej pary (cecha rysunku, cecha etykiety: pierwszy/drugi/ostatni glif, długość, gallows, prefiks) wobec etykiet przetasowanych w obrębie strony, poprawka na liczbę par; kontrole: podłożony pierwszy glif według cechy (z = 72), cechy przetasowane (bez związku); `atoms_draft`: model widzący (OpenRouter) opisuje nimfy zodiaku w tym schemacie jako szkic do poprawienia; `atoms_vision` (`colab/Voynich_Atomy_GPU.ipynb`, A100, bez API): Molmo2-8B wskazuje punktami środki kół, postaci i gwiazdy, geometria liczy kręgi i kolejność zgodnie z ruchem wskazówek zegara, Qwen3-VL-8B opisuje wycinek wokół każdej postaci, Grounding DINO liczy ramkami jako kontrola; PNG z numerami punktów do sprawdzenia kolejności; pierwszy przebieg (28.10, 321 s): modele działają, Molmo2 znalazł środki kół, ale na całych rozkładówkach wskazał mało postaci (Ryby 28/29, Baran 15/15, reszta 0–12/30) i rozpoznanie znaku zawiodło, 0 stron; poprawka: wycinek każdego koła osobno w pełnej rozdzielczości, trzy liczniki scalone, strony z tabeli paneli skanów (voynich.nu); drugi przebieg (696 s, 9 stron): punkty trafiają w nimfy, ale co drugi lądował przy x ≈ 0 przez błąd parsera współrzędnych Molmo2 (format „klatka, numer, x, y”), co psuło też środki kół; parser poprawiony według karty modelu, promień koła z szerokości panelu; trzeci przebieg (30.10, 1642 s, 12 stron): Ryby 28/29, Barany 15/15 i 15/15, Byki 16 i 18/15, Rak 30/30, ale strony z nimfami leżącymi słabo (Lew 12, Panna 2, Skorpion 11, Strzelec 8 z 30), Bliźnięta i Waga z nadmiarem (39, 37); na PNG kręgi i kolejność f71r poprawne; poprawka: wycinek koła wskazywany w 4 obrotach, wykluczenie środka (figura znaku), scalanie bliskich punktów; czwarty przebieg z obrotami (5.11, 2917 s): strony z nimfami leżącymi odzyskane (Skorpion 29, Strzelec 26, Panna 34, Lew 35 z 30), nadmiar z dubli między obrotami i jednego wybuchu halucynacji (60 „postaci” w jednym obrocie Lwa); poprawka: każdy punkt ma poparcie z 8 źródeł (2 pytania × 4 obroty), zostaje tyle najlepiej popartych, ile nimf ma strona; piąty przebieg (7.11, 2852 s): 10 z 12 kół z dokładną liczbą postaci (Strzelec 26, Skorpion 29 z 30), 11 stron (255 atomów) scalonych do `data/atoms` jako źródło „vision” | obalona na szkicu (7.11): 255 z 857 atomów opisanych (szkic z GPU na 11 stronach zodiaku, 10 z 12 kół z dokładną liczbą postaci); żadna z 54 par cecha rysunku × cecha etykiety nie przekracza tła (najlepsza z = +1,9); kontrole: podłożony glif z = 53, przetasowane bez związku. Zastrzeżenie: cechy ze szkicu modelu (pewność 1), werdykt do powtórzenia po poprawkach ludzi |
| `catalog` | analiza przekrojowa (`data/catalog/pages.json`, `scripts/fetch_catalog.py`, CPU ok. 1 min): katalog stron Zandbergena (voynich.nu, 226 stron: dział, opis rysunku, cechy stylu rysunku roślin Gheuensa i Rapaport α/β na 109 stronach zielnika, język Curriera, ręka LFD, odsyłacze zielnik–farmacja); (1) styl rysunku β−α wobec języka i ręki (AUC z permutacjami); (2) strony o wspólnej cesze rysunku wobec losowych grup o tym samym składzie język+ręka, słownictwo ważone rzadkością, poprawka na 19 cech; (3) rejestr działów; kontrole: wspólny słowniczek grupy podłożony (z = 5,9), cechy przetasowane (z = 1,4) | obalona (lokalnie, 7.11): styl rysunku przewiduje skrybę niemal bez wyjątku (język B: AUC 0,99, z = +7,0; ręka 2: AUC 0,98), ale nie treść: żadna z 19 cech rysunku nie łączy stron słownictwem ponad język i rękę (najlepsza „dwa kształty liści” z = +2,5, p popr. 0,13); strony o wspólnym stylu dzielą słów tyle co losowe strony tego samego skryby |
| `hapax_source` | skąd hapaksy (`colab/Voynich_Bomba.ipynb`, CPU ok. 1 min): (1) r* = stopa pomyłek kopisty (jeden glif zmieniony, dodany albo usunięty), przy której nomenklator tej samej wielkości i z tych samych słów kodowych ma udział hapaksów w tokenach jak rękopis (13,7%); (2) lokalność: jak często częsty sąsiad hapaksu stoi w 5 wierszach nad nim wobec innej strony, dla rękopisu, bełkotu v7 i nomenklatora przy r*; kontrole: kopie z 3 wierszy wyżej podłożone (z = 126), wiersze rozdane losowo na strony (z = 0,4) | nierozstrzygnięta (lokalnie, 7.11): r* = 0,21 w hebrajskim, arabskim i łacinie (co piąte słowo kodowe z błędem); lokalność rękopisu ×2,07 wobec ×1,79–1,96 dla pomyłek nomenklatora (z różnicy −0,4 do −2,4) i ×1,58 dla v7 (+2,4): hapaksy nie wykluczają nomenklatora, ale lokalność nie odróżnia pomyłek od kopiowania z sąsiedztwa |
| `cribs` | ściągi z diagramów (`voynich/lab/cribs.py`, CPU ok. 8 min): 28 słów promienistych f69v wobec 28 stacji Księżyca (arabskie i łacińskie Agryppy), 12 słów kół f67r1, f67v1, f67r2 wobec znaków zodiaku (łacina, włoski, arabski, hebrajski) i miesięcy (łacina, francuski, oksytański, kataloński, włoski, niemiecki); każdy początek i kierunek listy, klucz glif → litera z twardego EM; null: te same nazwy w 1000 przetasowanych kolejnościach, Bonferroni po 32 parach; kontrola: lista zapisana w glifach rękopisu losowym kluczem z 10% szumu (z ≥ 9,6 dla każdej listy) | obalona (lokalnie, 7.11): żadna para nie wypada ponad przypadkową kolejność; f69v × stacje z = −0,1 (arabskie) i −0,5 (łacińskie); najlepsza f67v1 × miesiące katalońskie z = +3,8, p popr. 0,10 (jedno dokładne trafienie „maig”, reszta „jilill~juliol”, „mamg~marc”), tuż za nią ten sam krąg z miesiącami francuskimi (z = +3,0): do sprawdzenia, nie odkrycie |
| `polybius` | Polibiusz w długościach słów (`voynich/lab/polybius.py`, CPU ok. 10 min): dwie kolejne długości słów akapitów (w glifach, 9+ = 9) to wiersz i kolumna litery; obie fazy (od pierwszego i od drugiego słowa); klucz pole → litera wyżarzaniem na trigramach liter + koszcie emisji; łacina, hebrajski, włoski, niemiecki; rękopis wobec tych samych długości przetasowanych (3×); kontrola: tekst języka zapisany długościami słów losową tablicą 5×5 | obalona (lokalnie, 9.11): kontrola odczytana w łacinie, włoskim i niemieckim w 100% (hebrajski 46%, poza oceną); rękopis czyta się tak samo jak przetasowany: łacina 4,70/4,69 i 4,78/4,71, włoski 5,20/5,18 i 5,18/5,18, niemiecki 5,12/5,15 i 5,16/5,12 bitu na literę (naturalnie 2,8–3,3) |
| `master_card` | karta matka (`voynich/lab/card.py`, `colab/Voynich_Karta.ipynb`, A100 lub CPU ok. 23 min): czy słowa składano z jednej tabeli kawałków w 6 kolumnach od początku do końca słowa (z każdej kolumny co najwyżej jeden kawałek, n-gramy glifów n ≤ 3); najlepsza karta o 40, 80, 120 i 200 wpisach z ewolucji; rękopis wobec łaciny, włoskiego, bełkotu v7, rękopisu z glifami przetasowanymi w słowie; kontrola: tekst pisany znaną kartą 5 × 8 z 10% pomyłek (odtworzony: 0,93 wobec 0,91 prawdziwej karty); A wobec B Curriera | potwierdzona (lokalnie, 10.11): karta 120 wpisów składa 96% słów rękopisu (40 wpisów: 77%, 80: 93%), łaciny 70%, włoskiego 74%, rękopisu przetasowanego 74%, bełkotu v7 95%; języki A i B mieszczą się w jednej karcie (karta A na B 0,95, B na A 0,93; spadek 0,014 jak między losowymi połówkami stron, 0,004–0,012). Tabela karty: [`docs/karta_matka.md`](docs/karta_matka.md). Zastrzeżenie: to opis budowy słów, zgodny z kartą-przepisem, nie dowód, że karta fizycznie istniała; v7 składa się z karty tak samo dobrze |
| `master_card_full` | karta matka na 100% słów (`voynich/lab/card.py`: `prune`, `shrink`; `colab/Voynich_Karta.ipynb`, GPU: L4 7,7 h, A100 szybciej; CPU ok. 66 min z mniejszą populacją): karta pełna (każdy kawałek w każdej z 6 kolumn) składa wszystko; 256 kart przycina ją naraz, każda w swojej kolejności, wpis znika, gdy bez niego nadal składa się 100% (i 99%) tokenów; potem ewolucja pod budżetem o jeden wpis mniejszym (do 40 rund); te same kroki dla łaciny, włoskiego, v7, rękopisu przetasowanego; kontrola: tekst pisany znaną kartą 40 wpisów (odtworzona karta: dokładnie 40 wpisów, także na 99%) | potwierdzona (Colab L4, przebieg 20261110-143915): każde słowo rękopisu składa się z karty 242 wpisów (99% słów: 132); łacina potrzebuje 639 (562), włoski 556 (422), rękopis z przetasowanymi glifami 563 (355), bełkot v7 211 (125). Lokalnie na CPU (4 karty przycinające): rękopis 264 (185), łacina 652, włoski 579, przetasowany 567, v7 215. Tabela: [`docs/karta_matka_100.md`](docs/karta_matka_100.md). Zastrzeżenia: hapaksy też dokładają wpisy; na 99% zmniejszanie zatrzymał limit 40 rund, więc te liczby to górne granice; przycinanie znajduje małą kartę, nie dowodzi, że mniejszej nie ma |
| `card_choice` | wybory z karty matki (`voynich/lab/cardchoice.py`, CPU ok. 17 min): każde słowo rozbite na wybory z 6 kolumn własnej karty tekstu (przycięcie do 100% tokenów); ile wybory mówią o stronie ponad działem (wobec tasowania całych wierszy między strony działu) i czy na granicy strony jest skok (wiersze tej samej strony podobniejsze niż wiersze w tej samej odległości po dwóch stronach granicy; wiersze przy krawędziach stron pominięte, każdy wiersz przycięty do 8 wyborów); osobno granica recto→verso tej samej karty i granica między kartami; rękopis wobec bełkotu v7 i łaciny w tym samym układzie; kontrole: podłożony ulubiony wpis każdej strony (z = 80, skok z = 4,3), dryf ślepy na strony (z = 36, skok z = 1,2), czysty tekst (z = −0,1) | nierozstrzygnięta (lokalnie, 11.11): wybory niosą o stronie 2,6% swojej entropii (zielnik 3,6%), v7 0,7% (1,3%), łacina 2,0% (2,7%); skok na granicy stron rękopisu +0,10 (z = 4,4), v7 i łacina ok. 0. Ale skok siedzi na granicach między kartami (+0,15, z = 7,2, 84 granice), a między recto i verso tej samej karty jest słaby (+0,06, z = 1,9, 98 granic): to wygląda na karty pisane w różnym czasie i przeszyte potem w innej kolejności, nie na treść zmieniającą się z każdą rośliną. Zastrzeżenie: czysty tekst kontrolny daje skok z = 2,3, więc z skoku są raczej zawyżone; pomiar skoku dodany po pierwszym przebiegu |
| `sheet_order` | kolejność pisania, dryf skryby jako zegar (`voynich/lab/bifolio.py`, CPU ok. 4 min): karty jednej składki, tej samej ręki i języka Curriera; czy dwie karty jednego arkusza (bifolium; daleko od siebie w księdze, np. f1 i f8) są podobniejsze w wyborach z karty matki niż inne pary kart składki, i czy podobniejsze są karty sąsiednie w księdze; 2000 zamian kart w obrębie (składka, ręka, język); kontrole na tekście pisanym znaną kartą przez skrybę z dryfem: arkuszami w losowej kolejności (arkusz z = 5,7, sąsiednie z = 0,0), strona po stronie w kolejności księgi (sąsiednie z = 6,1, arkusz z = −0,3), bez dryfu (0,3 i −0,2) | potwierdzona (lokalnie, 11.11): karty jednego arkusza z = 6,4 (34 pary), karty sąsiednie w księdze z = 0,5 (45 par): pisano arkuszami, zanim złożono składki. Strony jednego arkusza: ta sama karta 5,2, strona zewnętrzna 5,5, wewnętrzna 5,7, inna strona i karta 4,1 (z 1,7–2,0, za słabo, by powiedzieć, w jakiej kolejności zapisywano cztery strony). Składka nie jest jednostką: najbliższy arkusz leży w tej samej składce w 37% przypadków wobec 34% losowo (z = 0,6); w zielniku A najbliższe arkusze są zwykle w innych składkach. Tabela: [`docs/arkusze.md`](docs/arkusze.md). Zastrzeżenia: wspólna treść arkusza dałaby ten sam ślad co dryf; pełnej kolejności arkuszy nie odtwarzamy (na kontroli ρ 0,1–0,6), wiarygodny jest tylko najbliższy sąsiad (62% trafień na kontroli wobec 4% losowo) |
| `nomenclator2` | nomenklator z dwoma kluczami (język A i B Curriera) i pomyłkami kopisty, jedyna rodzina szyfrów otwarta po Zhang i Sheng (arXiv:2610.34499), w hebrajskim, arabskim i łacinie (`voynich/lab/nomen2.py`): rzadkie typy scalane z częstym typem o jeden glif dalej, klucz symbol → jednostka (200 słów całych, reszta literami) z próbkowania Gibbsa wieloma łańcuchami naraz (cupy na GPU, numpy na CPU) pod pełną wiarygodnością: bigram jednostek + koszt emisji homofonów (sam model języka wolał zły klucz od prawdziwego: 3,36 wobec 4,19 bitu); klucz na wierszach nieparzystych, bity na parzystych; kontrole tej samej wielkości co rękopis, zaszyfrowane 800 słowami rękopisu przy r = 0, r* i 0,5; rękopis wobec v7 i rękopisu przetasowanego w wierszu | obalona (lokalnie na CPU, 16 łańcuchów × 200 przebiegów, 654 s, 7.11): łamacz czyta kontrole (r = 0: hebrajski 0,81, arabski 0,83, łacina 0,91 tokenów; przy r* = 0,21: 0,54 / 0,64 / 0,81, Zhang i Sheng: 46% hebrajskich), a rękopis odczytany jako nomenklator ma 5,62 / 5,64 / 5,64 bitu na jednostkę, tyle co bełkot v7 (5,60 / 5,69 / 5,61) i 0,6–1,4 bitu więcej niż kontrola z tą samą stopą pomyłek (4,90 / 5,02 / 4,25); przetasowany 5,8–6,0. Reguła obalenia (lustro reguły tropu: ani 0,15 bitu lepiej od v7, ani w granicach 0,3 bitu od kontroli) ustalona po pierwszym przebiegu, w którym stara reguła (≥ v7 − 0,05) zostawiła arabski na granicy 0,05 bitu. Przebieg na A100 (256 łańcuchów × 600, `colab/Voynich_Bomba.ipynb`) zerwał się w nocy 7/8.11 (Colab rozłączony) i nie został powtórzony: wynik z CPU jest ostateczny |
| przebieg zamykający | `colab/Voynich_Final.ipynb`: teorie z dopisanymi kontrolami (gatunki: rama wszczepiona i litania przetasowana; sędzia: czułość i trzy podziały; wspinaczka i NeuroDecipher: glify przemianowane w każdym wierszu; tarcza: tekst znanej tarczy) oraz `length_code`, `chronology`, `hands` na pełnych ustawieniach | do uruchomienia |

**Psy gończe** (`voynich/lab/hounds.py`, `voynich/lab/recipes.py`): rada przestaje tylko oceniać i sama poluje.
Każdy model dostaje rolę (kryptolog, lingwista, sceptyk, „dziki pies”) i w kolejnych rundach wymyśla przepisy odczytu
z klocków: klucze z π, e, √2, φ, liczb pierwszych, dat i słów (jak szyfr Vigenère'a), nulle, co n-te słowo lub glif,
grupy glifów, odwracanie, akrostychy, usuwanie spacji, 15 języków docelowych, pismo bez samogłosek. Każdy klocek ma
dokładną odwrotność, więc każdy przepis dostaje automatycznie kontrolę dodatnią (tekst w języku docelowym zaszyfrowany
tym samym przepisem musi wrócić) i kontrole ujemne (bełkot z generatora v4, rękopis z przetasowanymi słowami).
Trop liczy się tylko, gdy rękopis wyraźnie wygrywa z bełkotem, a odczyt jest prawie tak przewidywalny jak prawdziwy
język; najlepsze tropy są powtarzane na innej części rękopisu. Pomysły spoza klocków trafiają na listę życzeń.
W notebooku: `lab.hunt(rounds=4, per_hound=2)`.

Laboratorium porównuje z 17 językami Biblii (baskijski dołączył jako 13., hiszpański, portugalski, francuski i rumuński jako 14.–17.) oraz z łaciną średniowieczną, łaciną ludową (Egeria), starofrancuskim, a w brute force także z aramejskim (Targum Onkelos) i syryjskim (Peszitta); raport `docs/index.html` z etapów 1–2 liczono jeszcze na 12.
`fetch_data.py` kończy się komunikatem „Dane kompletne.”, a laboratorium odmawia liczenia na niepełnych danych.

Sekrety Colaba: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. Wyniki trafiają na gałąź `lab-results`.
Z wiersza poleceń: `python -m voynich.lab.runner --theories numbers,literature --quick --no-council`.

## Podsumowanie końcowe (8 listopada 2026)

Projekt zamykamy. Przez trzy tygodnie zamieniliśmy 44 hipotezy o rękopisie w testy z kontrolami: każdy test musiał
najpierw znaleźć efekt, który sami podłożyliśmy, i nie znaleźć go w danych losowych. Żadna hipoteza, że tekst jest
językiem, szyfrem, zapisem muzyki, tańca, programu albo listą nazw, nie przeszła. Ostatni i najmocniejszy atak, na
nomenklator z dwoma kluczami i pomyłkami kopisty (jedyny szyfr, którego literatura jeszcze nie wykluczyła), czyta próbne
szyfry po hebrajsku, arabsku i łacinie w 81–91%, a rękopis tak samo słabo jak bełkot wygenerowany komputerowo. Ilustracje
też nic nie dały: styl rysunków zdradza skrybę, ale nie treść, a koła diagramów nie są zaszyfrowanymi nazwami stacji
Księżyca, znaków ani miesięcy. Najlepiej wszystko tłumaczy tekst bez treści, pisany z nawyku przez przerabianie słów
z sąsiednich wierszy; jedyna rzecz, której nasz generator nie naśladuje do końca, to liczba słów jednorazowych.
To wniosek oparty na liczbach, nie dowód; kod, dane i wyniki (`lab-results`) są publiczne i powtarzalne.

## Stan badań (8 listopada 2026)

Trzy tygodnie, 47 teorii zamienionych w testy z kontrolami, 27 przebiegów na Colabie (A100 i CPU) na gałęzi `lab-results`
i lokalne przebiegi ostatniego ataku, 128 testów kodu. Każdy test musi znaleźć efekt podłożony celowo i nie znajdować go w danych losowych; bez tego werdykt
brzmi „metoda niewiarygodna”. Wiersze w tabeli wyżej mają liczby; tu streszczenie.

**Wykluczone (kontrole przeszły):**
- Szyfr podstawieniowy, prosty i homofoniczny, dla 53 języków i słowników epoki. Trzy łamacze (brute force trójek słów,
  wspinaczka z modelem n-gramowym, NeuroDecipher) odzyskują klucz z tekstu kontrolnego w 94–100%, a z rękopisu wyciągają
  tyle samo co z bełkotu. Dotyczy też kluczy innych dla każdej długości słowa (`brute_length`: słowa o 5–8 glifach czytane
  jako słowa języka w 0–8%, tyle co bełkot; zaszyfrowany tekst 97–100%) i klucza zapisanego w odstępach (`keystream`:
  żadne cięcie, przesunięcie ani odczyt strumienia glifów nie koduje rękopisu krócej niż odstępy EVA).
- Zapis niejęzykowy ze składnią: chorał, tabulatura tańca, program (`notation`, z = 65–145 wobec −1 rękopisu); listy
  średniowieczne: martyrologium, Apicius, glosariusz Alphita (`lists`, z = 64–113).
- Daleka składnia: w czterech transliteracjach słowo nic nie mówi o słowie 2–7 miejsc dalej (z ≈ −1), czego nie ma żaden
  język, szyfr zachowujący szyk, notacja ani lista.
- Tekst opisujący obrazki: akapity nie cytują etykiet swojej strony (`labels`, z = +1,4), strony z tą samą rośliną dzielą
  słów mniej niż losowe strony (`plant_pairs`, z = −2), podobieństwo rysunków nie idzie w parze z podobieństwem słów
  (Mantel r = 0,08). Analiza przekrojowa katalogu Zandbergena (`catalog`, 7.11): styl rysunku roślin (cechy α/β Gheuensa
  i Rapaport) przewiduje skrybę niemal bez wyjątku (język B: AUC 0,99), ale strony o wspólnym stylu nie dzielą słów ponad
  to, co dzielą losowe strony tego samego skryby (19 cech, najlepsza z = +2,5 po poprawce nic). Rebus w parach rysunek–
  etykieta (`atoms`, 255 nimf zodiaku ze szkicu GPU): żadna z 54 par cecha rysunku × cecha etykiety nie przekracza tła.

- Ostatni atak („bomba”, 7.11, `colab/Voynich_Bomba.ipynb`): nomenklator z dwoma kluczami i pomyłkami kopisty, jedyna
  rodzina szyfrów, której Zhang i Sheng nie wykluczyli. Nowy łamacz czyta kontrole wielkości rękopisu po hebrajsku (81%),
  arabsku (83%) i łacinie (91%), także przy stopie pomyłek rękopisu (54–81%), a rękopis czyta tak samo źle jak bełkot v7
  (`nomenclator2`). Hapaksy nie wykluczają pomyłek kopisty (r* = 0,21), ale ich położenie nie odróżnia pomyłek od
  kopiowania z sąsiedztwa (`hapax_source`). Koła diagramów nie czytają się jako stacje Księżyca, znaki ani miesiące
  (`cribs`, 32 pary, najlepsza f67v1 × miesiące katalońskie z = +3,8, p popr. 0,10). Długości słów nie kryją
  tekstu także jako pary współrzędnych w tablicy Polibiusza (`polybius`, 9.11): rękopis czyta się jak przetasowany.
- Karta matka (`master_card`, 10.11): jedna tabela 120 kawałków słów w 6 kolumnach wystarcza, żeby złożyć 96% słów rękopisu,
  wobec 70–74% dla łaciny, włoskiego i rękopisu z przetasowanymi glifami. Języki A i B Curriera mieszczą się w tej samej
  karcie. To najprostszy mechanizm, który tłumaczy, jak pięciu skrybów pisało płynnie według wspólnych reguł:
  [`docs/karta_matka.md`](docs/karta_matka.md). Karta, która składa każde słowo bez wyjątku (`master_card_full`), ma 242 wpisy (GPU):
  2,6 raza mniej niż dla łaciny (639) i 2,3 raza mniej niż dla rękopisu z przetasowanymi glifami (563), ale tyle co
  dla bełkotu v7 (211); na 99% słów: 132 wpisy wobec 562 dla łaciny. To, które kawałki skryba brał z karty, zależy od strony
  mocniej niż w bełkocie v7, ale zmienia się skokowo głównie między kartami, a nie między recto i verso jednej karty: najprościej to
  wyjaśnić kartami pisanymi w różnym czasie i przeszytymi potem w innej kolejności (`card_choice`, nierozstrzygnięta). Dryf nawyków jako zegar to potwierdza
  (`sheet_order`): dwie karty jednego arkusza, odległe w oprawionej księdze, mają te same nawyki (z = 6,4), karty sąsiednie nie (z = 0,5).
  Rękopis pisano arkuszami przed złożeniem składek, a arkusze jednej składki nie są sobie bliższe niż arkusze różnych składek:
  [`docs/arkusze.md`](docs/arkusze.md): [`docs/karta_matka_100.md`](docs/karta_matka_100.md). Colab (przebieg 20261107-203642
  na `lab-results`) powtórzył `hapax_source` i `cribs` z tymi samymi liczbami; `nomenclator2` na GPU zerwał się
  i został na wyniku z CPU.

**Niewyjaśnione:**
- Generator bez treści v7 (kopiuj z sąsiedztwa i przerabiaj) trafia 21 z 23 miar statystycznych, ale sędzia-transformer
  wciąż odróżnia go od rękopisu (AUC 0,642 wobec 0,531 dla rękopisu z samym sobą). Trwały ślad: rękopis ma więcej słów
  jednorazowych, niż daje przerabianie sąsiadów. `judge_probe` (7.11) wskazuje, że sędzia widzi słownictwo, nie szyk:
  po ograniczeniu do słów wspólnych obu korpusom AUC spada z 0,690 do 0,566, a najsilniejsza pojedyncza cecha to hapaksy.
  Rada zastrzega: brak kontroli na danych przetasowanych i mała próba; do powtórzenia.
- Etykiety przy rysunkach to osobny zasób nazw: inne początki, inne długości, połowa nigdy nie pada w akapitach.
- Sąsiednie słowa niosą o sobie mniej informacji niż losowe słowa tego samego wiersza (z = −24; bełkot +11, łacina +47).
  Tłumaczy to słownictwo krawędzi wiersza, ale sama cecha nie była wcześniej opisana.
- Sztywne kawałki po 3 glify kodują rękopis krócej niż jego własne słowa (3,32 wobec 3,90 bitu na glif); w łacinie słowa
  wygrywają z kawałkami.

**Wniosek końcowy:** tekst nie niesie treści w żadnym sensie, w jakim niosą ją język, szyfr zachowujący szyk, notacja
czy lista. Najbardziej prawdopodobny jest zapis bez treści z nawyku skryby, z możliwą domieszką prawdziwych nazw
(etykiety). To opinia oparta na liczbach, nie dowód: wszystko jest publiczne i powtarzalne.

**Tor obraz–etykieta (atomy):** rysunki rozbierane na atomy, jeden rekord na etykietę (853 loci na 51 stronach),
cechy tylko obserwowalne ze słownika kontrolowanego; szkic na własnym GPU otwartymi modelami (Molmo2, Qwen3-VL, Grounding
DINO) z kolejnością nimf policzoną z geometrii. Po pięciu przebiegach 10 z 12 kół zodiaku ma dokładną liczbę postaci,
255 atomów jest scalonych, a test `atoms` na tym szkicu wypada „obalona” (cechy modelu mają pewność 1, więc werdykt
czeka na poprawki ludzi). Instrukcja dla osób wypełniających: [`data/atoms/README.md`](data/atoms/README.md).

## Uruchomienie

```bash
python scripts/fetch_data.py      # korpusy porównawcze (Biblia w 12 językach, łacina średniowieczna)
python scripts/run_analysis.py    # eksperymenty etapu 1 -> docs/results.json (~10 min)
python scripts/run_extended.py    # etap 2 -> docs/results_ext.json (~5 min)
python scripts/build_report.py    # docs/index.html
python -m unittest                # testy
```

`run_analysis.py --quick` robi szybki przebieg (3 języki, mniej permutacji).

## Struktura

| plik | co robi |
|---|---|
| `voynich/ivtff.py` | parser formatu IVTFF (strony, zmienne `$I $L $H`, loci) |
| `voynich/eva.py` | czyszczenie EVA, podział na słowa i glify (`cth`, `ch`, `ii`… jako jeden znak) |
| `voynich/corpus.py` | ładowanie rękopisu i korpusów porównawczych |
| `voynich/stats.py` | entropie h₁–h₃, Zipf, gęstość słownika, powtórzenia |
| `voynich/structure.py` | pozycje glifów, sztywność kolejności, testy permutacyjne, słowa kluczowe działów |
| `voynich/selfcite.py` | generator samocytowania: reguły ręczne, edycje podpatrzone u skryby, gramatyka słowa |
| `voynich/latin.py` | pisownia średniowieczna, podział na sylaby, skróty skrybów |
| `voynich/syllabic.py` | hipotezy sylabiczne, kod sylabiczny, niezmienniki na poziomie słów |
| `voynich/cipher.py` | łamacz szyfrów podstawieniowych (wyżarzanie, kryterium MDL) |
| `voynich/lab/` | laboratorium: konfiguracja, klient OpenRouter, rada modeli, skany IIIF, teorie, raport i push |
| `voynich/lab/recipes.py`, `hounds.py` | język przepisów (klocki z odwrotnościami, kontrole) i polowanie psów gończych |
| `colab/` | notebook Colab i skrypt, który go generuje |

## Dane i źródła

- `data/raw/ZL3b-n.txt`: transliteracja Zandbergena–Landiniego, wersja 3b z 13.05.2025
  (René Zandbergen, [voynich.nu](https://www.voynich.nu/transcr.html)), SHA-256 `bf5b6d4a…beccafc`.
- Korpusy porównawcze: [christos-c/bible-corpus](https://github.com/christos-c/bible-corpus)
  oraz łacina średniowieczna z The Latin Library ([cltk/lat_text_latin_library](https://github.com/cltk/lat_text_latin_library)),
  pobierane przez `fetch_data.py` (nie są w repozytorium). Uwaga: „bacon” w tym zbiorze
  to Francis Bacon (XVII w.), nie Roger Bacon, więc go pomijamy.
- T. Timm, A. Schinner, *A possible generating algorithm of the Voynich manuscript*, Cryptologia 44 (2020).
- B. L. Monroe, M. P. Colaresi, K. M. Quinn, *Fightin' Words*, Political Analysis 16 (2008), dla słów kluczowych.
