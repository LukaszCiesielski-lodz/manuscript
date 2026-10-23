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
