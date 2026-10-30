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
| `judge_probe` | co widzi sędzia (`colab/Voynich_Sedzia.ipynb`, A100 ok. 10 min): sędzia prawdziwe wobec v7 przepytany cechami wiersza (hapaksy, słowa nieobecne w drugim korpusie, długość, miejsce na stronie) i AUC po dopasowaniu słownictwa (same słowa wspólne) | do uruchomienia |
| `atoms`, `atoms_draft` | ontologia ilustracji (`data/atoms/`, `colab/Voynich_Atomy.ipynb`, CPU): rysunki rozebrane na atomy, jeden rekord na etykietę (853 loci na 51 stronach), cechy tylko obserwowalne ze słownika kontrolowanego (`vocab.json`), wpisywane przez ludzi (zgodność dwóch osób: kappa); test rebusu: informacja wzajemna każdej pary (cecha rysunku, cecha etykiety: pierwszy/drugi/ostatni glif, długość, gallows, prefiks) wobec etykiet przetasowanych w obrębie strony, poprawka na liczbę par; kontrole: podłożony pierwszy glif według cechy (z = 72), cechy przetasowane (bez związku); `atoms_draft`: model widzący (OpenRouter) opisuje nimfy zodiaku w tym schemacie jako szkic do poprawienia; `atoms_vision` (`colab/Voynich_Atomy_GPU.ipynb`, A100, bez API): Molmo2-8B wskazuje punktami środki kół, postaci i gwiazdy, geometria liczy kręgi i kolejność zgodnie z ruchem wskazówek zegara, Qwen3-VL-8B opisuje wycinek wokół każdej postaci, Grounding DINO liczy ramkami jako kontrola; PNG z numerami punktów do sprawdzenia kolejności; pierwszy przebieg (28.10, 321 s): modele działają, Molmo2 znalazł środki kół, ale na całych rozkładówkach wskazał mało postaci (Ryby 28/29, Baran 15/15, reszta 0–12/30) i rozpoznanie znaku zawiodło, 0 stron; poprawka: wycinek każdego koła osobno w pełnej rozdzielczości, trzy liczniki scalone, strony z tabeli paneli skanów (voynich.nu); drugi przebieg (696 s, 9 stron): punkty trafiają w nimfy, ale co drugi lądował przy x ≈ 0 przez błąd parsera współrzędnych Molmo2 (format „klatka, numer, x, y”), co psuło też środki kół; parser poprawiony według karty modelu, promień koła z szerokości panelu; trzeci przebieg (30.10, 1642 s, 12 stron): Ryby 28/29, Barany 15/15 i 15/15, Byki 16 i 18/15, Rak 30/30, ale strony z nimfami leżącymi słabo (Lew 12, Panna 2, Skorpion 11, Strzelec 8 z 30), Bliźnięta i Waga z nadmiarem (39, 37); na PNG kręgi i kolejność f71r poprawne; poprawka: wycinek koła wskazywany w 4 obrotach, wykluczenie środka (figura znaku), scalanie bliskich punktów; 5 stron (f70v2, f70v1, f71r, f71v, f72r3; 102 atomy) scalone do `data/atoms` jako źródło „vision”, test `atoms` rusza (najlepsza para z = +2,4, bez wyniku; do obalenia ≥ 200 atomów) | 102 z 855 atomów opisanych (szkic z GPU na 5 stronach zodiaku, do poprawienia przez ludzi); test działa: kontrole OK, najlepsza para z = +2,4 (nic po poprawce); do obalenia ≥ 200 atomów |
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
