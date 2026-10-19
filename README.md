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

Wykluczamy konkretne hipotezy, nie wszystkie. Model trigramowy nie wychwyci
szyfrów przestawieniowych, sylabicznych ani nomenklatorów (kodów całych słów).

## Uruchomienie

```bash
python scripts/fetch_data.py      # korpusy porównawcze (Biblia w 12 językach)
python scripts/run_analysis.py    # wszystkie eksperymenty -> docs/results.json (~10 min)
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
| `voynich/selfcite.py` | generator tekstu metodą samocytowania |
| `voynich/cipher.py` | łamacz szyfrów podstawieniowych (wyżarzanie, kryterium MDL) |

## Dane i źródła

- `data/raw/ZL3b-n.txt`: transliteracja Zandbergena–Landiniego, wersja 3b z 13.05.2025
  (René Zandbergen, [voynich.nu](https://www.voynich.nu/transcr.html)), SHA-256 `bf5b6d4a…beccafc`.
- Korpusy porównawcze: [christos-c/bible-corpus](https://github.com/christos-c/bible-corpus),
  pobierane przez `fetch_data.py` (nie są w repozytorium).
- T. Timm, A. Schinner, *A possible generating algorithm of the Voynich manuscript*, Cryptologia 44 (2020).
- B. L. Monroe, M. P. Colaresi, K. M. Quinn, *Fightin' Words*, Political Analysis 16 (2008), dla słów kluczowych.
