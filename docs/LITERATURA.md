# Przegląd literatury dla Voynich Lab

Wyszukane przez Firecrawl (indeks prac naukowych: arXiv, PubMed/PMC, oraz wyszukiwarka ogólna), październik 2026.
Przy każdej pracy: co z niej bierzemy do testów.

## Lingwistyka i statystyka tekstu

- **Bowern & Lindemann, *The Linguistics of the Voynich Manuscript*, Annual Review of Linguistics 7 (2021).**
  Przegląd: tekst ma cechy języka naturalnego (Zipf, słownictwo zależne od działu), ale niezwykle niską entropię
  warunkową. Punkt odniesienia dla całego projektu.
- **Lindemann & Bowern, *Character Entropy in Modern and Historical Texts*, arXiv:2010.14697.**
  Na 294 językach i 18 tekstach historycznych: żadne przekształcenie zapisu (kompozycja glifów, skróty) nie zrównuje
  entropii z językami. Ograniczone pozycje znaków w słowie mogą oznaczać utratę rozróżnień fonemicznych. Zgodne z naszym etapem 1.
- **Rozanova & Temerev, *A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space*, arXiv:2608.17096 (2026).**
  Struktura siedzi na krawędziach słów: glify na styku sąsiednich słów mają ~0,2 bita informacji wzajemnej, więcej
  niż w każdym tekście kontrolnym; spacje niepewne zachowują się jak granice wewnątrz słowa. Szyfr Naibbe i generator
  samocytowania odtwarzają niską entropię, ale nie to sprzężenie ani 70% hapaksów (41% i 59–60%).
  → miara `edge_mi` w `voynich/lab/common.py`; porównujemy z nią każdy generator.
- **Montemurro & Zanette, *Keywords and Co-Occurrence Patterns in the Voynich Manuscript*, PLoS ONE 8 (2013).**
  Rozkład słów kluczowych między sekcjami jak w tekście z treścią. Zgodne z naszymi słowami kluczowymi działów.
- **Amancio i in., *Probing the statistical properties of unknown texts*, PLoS ONE 8 (2013), arXiv:1303.0347.**
  Miary sieciowe i intermitencji: tekst zgodny z językami naturalnymi, niezgodny z losowym.
- **Timm, *How the Voynich Manuscript was created*, arXiv:1407.6639; *Co-Occurrence Patterns*, arXiv:1601.07435;
  Timm & Schinner, Cryptologia 44 (2020).** Hipoteza samocytowania; nasz generator v1–v4.
- ***A Quantitative Confirmation of the Currier Language Distinction*, arXiv:2604.25979 (2026).**
  Podział A/B potwierdzony bez etykiet (89% trafności); głównym składnikiem jest „przełącznik” samogłoski po `ch`/`sh`
  ustawiany raz na stronę. → w teście B (Mantel) permutujemy w obrębie języka i skryby.
- ***Evidence of Layered Positional and Directional Constraints*, arXiv:2604.19762 (2026).**
  Kratka Cardana i generator slotowy nie odtwarzają naraz czterech sygnatur rękopisu. → teoria `cardan_grille`.
- ***Directionality of the Voynich Script*, arXiv:2509.10573.** Asymetria perpleksji n-gramów w obie strony.
- ***On the Non-Specificity of Statistical Measures Used in Script Decipherment*, arXiv:2608.02999 (2026).**
  Sztuczny system znaków bez fonetyki dostaje te same „językowe” sygnatury co pismo Indusu, a atak słownikowy
  osiąga wysokie pokrycie dla wielu języków naraz. → kontrole swoistości we wszystkich naszych atakach.

## Szyfry i generatory

- **Greshko, *The Naibbe cipher*, Cryptologia (2025), doi:10.1080/01611194.2025.2566408.**
  Łacina pocięta na unigramy i bigramy (rzut kośćmi), każda litera szyfrowana jedną z 6 tabel wybieraną kartą
  (5:2:2:2:1:1); unigram → całe słowo, bigram → przedrostek + przyrostek. Odtwarza entropię (2,00 bita w EVA),
  rozkład długości, Zipfa i Heapsa; nie odtwarza korelacji dalekiego zasięgu, efektów wiersza ani pełnej różnorodności słów.
  → teoria `naibbe_cipher` (rekonstrukcja z opisu, tabele z części słów rękopisu).
- **Rugg, *An elegant hoax?*, Cryptologia 28 (2004); Zandbergen, *The Cardan grille approach... taken to the next level*, arXiv:2104.12548.**
  → teoria `cardan_grille`.
- **Hauer & Kondrak, *Decoding Anagrammed Texts Written in an Unknown Language and Script*, TACL 4 (2016).**
  Wniosek „hebrajski z anagramami” krytykowany jako nieswoisty. → teoria `hebrew_anagram` z kontrolą swoistości:
  w naszym teście atak „znajduje hebrajski” także w angielskim (75%) i wietnamskim (91%).
- ***Can Evolutionary Computation Help us to Crib the Voynich Manuscript?*, arXiv:2107.05381.**
  Imiona żeńskie jako criby w kalendarzu. Nasz atak z nazwami roślin (teoria `illustrations`, część C) działa
  podobnie, ale z rozkładem zerowym z przetasowanych nazw.

## Ilustracje i układ strony

- ***Subtle Signs of Scribal Intent in the Voynich Manuscript*, arXiv:2404.13069.**
  Słowa tuż przed rysunkiem i na końcu wiersza mają inne długości (testy χ², binomialne). → teoria `illustrations`,
  część A; nasza replikacja: słowo przed rysunkiem krótsze o 0,24 glifu (p ≈ 0,003).
- ***Topic Modeling in the Voynich Manuscript*, arXiv:2107.02858.** Tematy LDA pokrywają się z działami (ilustracjami)
  i skrybami łącznie. → dlatego test Mantela kontroluje skrybę.
- ***A Generative Grammar Underlying the Voynich Manuscript, the Pastiche Hypothesis*, arXiv:2609.20835 (2026).**
  Dopasowanie obrazów do zielników Pseudo-Apulejusza z pomocą dużych modeli; tekst jako uporządkowana imitacja.
- ***A Visual Classification Dataset... for Historical Manuscript Illustrations*, arXiv:2609.33449.**
  Zero-shot CLIP i modele wizyjno-językowe wypadają słabo na ilustracjach rękopisów. → identyfikacje roślin przez
  model wizyjny traktujemy jako niepewne i testujemy permutacyjnie.

## Liczby

- Wikipedia (*Voynich manuscript*): wiersze f15v „oror or”, „or or oro r” przypominają zaszyfrowane cyfry rzymskie;
  numeracja kart i składek jest późniejsza i zapisana zwykłymi cyframi.
- Fora (voynich.ninja, r/voynich) zgłaszają hipotezy liczbowe bez testów statystycznych; żadna nie przeszła recenzji.
  → teoria `numbers`: 5 systemów liczbowych sprzed 1450 r. i test ciągłości etykiet zodiaku z liczbami podłożonymi.

## Budowa słów (tło dla karty matki)

- J. Stolfi, *A grammar for Voynichese words* (2000): rdzeń, płaszcz i skorupa słowa; pierwsza gramatyka słowa oparta na statystyce.
- G. Rugg, *An elegant hoax?*, Cryptologia 28 (2004): tabela przedrostków, środków i końcówek z kratką Cardana.
- ThomasCoon (forum Voynich Ninja, 2016) i M. Zattera, *A New Transliteration Alphabet Brings New Evidence of Word Structure in the Voynich Manuscript*, CEUR Workshop Proceedings 3313 (2022), [paper 10](https://ceur-ws.org/Vol-3313/paper10.pdf): alfabety slotowe, 12 kolejnych miejsc z kilkoma znakami w każdym.
- Przegląd: https://www.voynich.nu/a3_para.html
  → teorie `master_card`, `master_card_full`: ta sama budowa, ale tabela znaleziona przez wyszukiwanie, składająca każde słowo,
  zmierzona tą samą procedurą wobec łaciny, włoskiego, przetasowanych glifów i tekstu pisanego znaną kartą.

## Inne pisma nieodczytane (metody)

- Rao i in., *A Markov model of the Indus script*, PNAS 106 (2009); Yadav i in., PLoS ONE 5 (2010): n-gramy dla pisma Indusu.
- Luo i in., *Neural Decipherment via Minimum-Cost Flow*, arXiv:1906.06718; *Deciphering Undersegmented Ancient Scripts Using Phonetic Prior*, arXiv:2010.11054.
- Prace nad pismem kości wróżebnych (arXiv:2604.09668, 2406.00684): generatywne modele jako źródło hipotez z przejrzystymi dowodami, nie jako odczyt.

## Źródło skanów

Yale University Library, Beinecke MS 408, manifest IIIF: https://collections.library.yale.edu/manifests/2002046
(213 kart; brakujące folio: 12, 59–64, 74, 91, 92, 97, 98, 109, 110). Skany pobierane są w czasie działania i nie są w repozytorium.
