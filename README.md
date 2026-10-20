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

## Dane i źródła

- `data/raw/ZL3b-n.txt`: transliteracja Zandbergena–Landiniego, wersja 3b z 13.05.2025
  (René Zandbergen, [voynich.nu](https://www.voynich.nu/transcr.html)), SHA-256 `bf5b6d4a…beccafc`.
- Korpusy porównawcze: [christos-c/bible-corpus](https://github.com/christos-c/bible-corpus)
  oraz łacina średniowieczna z The Latin Library ([cltk/lat_text_latin_library](https://github.com/cltk/lat_text_latin_library)),
  pobierane przez `fetch_data.py` (nie są w repozytorium). Uwaga: „bacon” w tym zbiorze
  to Francis Bacon (XVII w.), nie Roger Bacon, więc go pomijamy.
- T. Timm, A. Schinner, *A possible generating algorithm of the Voynich manuscript*, Cryptologia 44 (2020).
- B. L. Monroe, M. P. Colaresi, K. M. Quinn, *Fightin' Words*, Political Analysis 16 (2008), dla słów kluczowych.
