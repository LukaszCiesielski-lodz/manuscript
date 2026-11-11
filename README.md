# The Voynich manuscript in numbers

**English** | [Polski](README.pl.md)

> *"A Pole started it, and a Pole will finish it."*
>
> The manuscript bears the name of Wilfrid Voynich (Michał Wojnicz), the Polish bookseller who brought it to light in 1912.

A laboratory for statistical analysis of the Voynich manuscript (Beinecke MS 408).
Pure Python 3, no dependencies.

**We have not read the manuscript.** Nobody has done so credibly yet.
This project does something more modest but verifiable: it measures the text with the same
measures as 12 languages, attacks it with a cipher solver with mandatory control
tests, and checks which hypotheses survive contact with the data.

Report with charts: [`docs/index.html`](docs/index.html) (open in a browser; the report page is in Polish).

## Key results

Numbers from `docs/results.json` (35 000 words per text; the languages are the same passage
of the Bible, the manuscript is counted in glyphs).

| | manuscript | 12 languages |
|---|---|---|
| conditional entropy h₂ (bits/character) | **2.30** | 2.89–3.65 |
| rigidity of character order within a word | **0.88** | 0.66–0.74 (Vietnamese 0.90) |
| vocabulary density (words with a “neighbour” 1 character away) | **99%** | 43–87% (Vietnamese 98%) |
| consecutive words differing by 1 character | **4.4%** | 0.1–1.4% |

1. **Substitution cipher (simple and homophonic) ruled out for 11 of 12 languages.**
   The solver (`voynich/cipher.py`) recovers 93–100% of the letters of control ciphers, while on
   the manuscript the best key leaves a gap of 1.07–1.55 bits per character relative to what
   the text “knows” about itself. Exception: Vietnamese (91 letters with tones), where
   the solver does not break even the control (46% of letters), so there is no verdict.
2. **The text is too predictable for a language**, and no substitution of characters
   changes that (test `test_substitution_leaves_fingerprint_unchanged`).
3. **Glyphs have fixed positions in the word**: `q` at the start in 99% of cases, `n` at the end in 98%.
4. **Adjacent words are similar to each other** twice as often as after shuffling
   (permutation test); in Latin and Italian it is the other way round.
5. **The line is a unit**: `m` and `g` are more than 6× as frequent in the last word of a line,
   `p` about 2.4× as frequent in the first.
6. **Consistent with language**: Zipf's law and section-dependent vocabulary.
7. **The self-citation hypothesis** (Timm and Schinner 2020) partly: our generator
   reproduces the vocabulary density and the similarity of neighbours (even in excess), but not
   the low entropy: h₂ = 2.65 instead of 2.30.

### Stage 2: medieval Latin, syllabic ciphers, a better generator

8. **Medieval Latin ruled out** (11 texts from the 7th–15th centuries plus Columella:
   Isidore, Hugh of Saint Victor, Thomas Aquinas, the Golden Legend, Kempis and others).
   On the fingerprint map (`docs/index.html#medieval`) they form a tight cluster
   with the Vulgate, far from the manuscript. The solver with a medieval Latin model breaks
   the controls at 99.7–99.8%, while on the manuscript it leaves a gap of 1.15 bits (herbal section) and 1.33 bits (dialect B).
9. **Scribal abbreviations do not help**: Latin with abbreviations (`⁊`, `-ꝰ`, `-ꝝ`, `ꝯ-`, a stroke
   instead of m/n) has h₂ ≈ 3.5 instead of 3.3, so it is further from the manuscript (2.3).
10. **Word = syllable ruled out**: Latin split into syllables has 621–766 distinct syllables per 13 thousand,
    the manuscript 3800 distinct words; syllables have 2.3 letters, the manuscript's words 4.0 glyphs.
11. **A syllabic/verbose word-by-word cipher is unlikely**: every such code
    preserves word repetitions, and the manuscript repeats a word immediately after itself in 0.83% of pairs
    (55 distinct words), while the most repetitive of the 24 comparison texts does so in 0.22%.
    A sample syllabic code lowers the entropy of Latin (3.3 → 2.9) and makes
    glyph positions more rigid, but gives words that are too long.
12. **Generator**: merely copying words with changes, even changes observed in the scribe
    (14 663 pairs), gives h₂ ≈ 3.0. Only adding a grammar of word shape (glyph trigrams
    learned on the list of distinct words, without frequencies) gives h₂ = 2.30 and, along the way,
    hits h₃ (2.04 vs 2.08), glyph rigidity, vocabulary density and repetitions.
    The parameters were tuned only for h₂ and similar neighbours. It does not reproduce the number of hapaxes
    (45% vs 69%), word lengths (5.1 vs 4.3), the Zipf slope or the line-end effects.

We rule out specific hypotheses, not all of them. A trigram model will not catch
transposition ciphers, syllabic ciphers or nomenclators (codes for whole words).

## Stage 3: Voynich Lab on Colab

`colab/Voynich_Lab.ipynb` runs hypothesis tests with method controls on a GPU (Colab Pro, High-RAM),
and each result is discussed by a council of models via OpenRouter (opinions → mutual review → the chair's synthesis).
The verdict of a test follows only from the numbers and the controls; the council comments on it. Literature review: [`docs/LITERATURA.en.md`](docs/LITERATURA.en.md).

| theory | test | local result (CPU, quick mode) |
|---|---|---|
| `numbers` | 5 number systems from before 1450; zodiac labels as days 1–30 | refuted |
| `illustrations` | words next to drawings; CLIP + Mantel test; plant names from a vision model as cribs | parts B and C on Colab only |
| `generative` | character-level transformer, missing pages, real/generated classifier; optionally SDXL+LoRA | Colab only |
| `naibbe_cipher` | the Naibbe cipher (Greshko 2025), reconstructed from the description | undecided |
| `cardan_grille` | gibberish from a Cardan grille (Rugg 2004) | refuted |
| `hebrew_anagram` | Hebrew anagrams (Hauer and Kondrak 2016) with a specificity control | method unreliable |
| `basque` | Basque under a substitution cipher: Leizarraga 1571 and the modern press | refuted (gap 0.96–0.99 bits) |
| `nomenclator` | word-for-word code book, solver at the word level; the gain from word order decides | refuted for Latin, Italian, German (manuscript ±0.01 bits, encoded text +0.13–0.47) |
| `hoax` | text without content from a scribe's rules (generator v5, “scribe's table”), rules from odd folios, check on even ones | undecided: v5 by section 16/22 measures, line classifier AUC 0.78–0.80 (real vs real 0.55; v4: 0.998); it reproduces the dynamics of word lengths (neighbour correlation +0.156 against +0.159), but not the repetitions within a line |
| `syntax` | dependence between different words 2–7 words apart (mutual information above shuffling within the page and the position in the line), repetitions and variants separately | refuted: frequent words show no dependence (z = −1.2; 5 language texts z ≥ 3.7), but there is an excess of repetitions and variants (z ≈ 9), profile flat with distance |
| `romance` | (proto-)Romance language (Cheshire 2019): Vulgar Latin (Egeria, c. 400), Old French (9th–13th c.), Bibles: Italian, Spanish, Portuguese, French, Romanian | refuted: gap 1.09–1.26 bits with controls at 99–100%; every Romance text has long-range syntax (z ≥ 11), the manuscript does not (z = −1.2) |
| `lengths` | words replaced by their character counts: neighbour autocorrelation, short–long zigzag, DFA exponent, line effect; 20 language texts, generators, a random sequence | refuted: adjacent lengths are positively correlated (+0.16; negatively in 17 of 20 languages), the strongest long-range memory (DFA 0.60 against 0.47–0.58), whole lines “long” or “short” |
| `brute` | brute force: each of the 4000 most frequent triples of consecutive words under one letter-for-glyph key in ~53 languages of the period (Bibles, UD historical corpora, medieval Latin, the Aramaic of Targum Onkelos, the Syriac Peshitta); agreement of keys between triples, a key from half of the lines checked on the other half | refuted (Colab A100, 51 lexicons, 4000 triples, 39 min): in no language does the manuscript beat v5 gibberish – at most 25% of words in the dictionary under a common key (Old French; gibberish 30%), encrypted real text 96–100%; 3 scripts untestable (Amharic, Hindi, Biblical Hebrew); Aramaic and Syriac (local run, 800 triples): manuscript 14% and 25% of words, gibberish 15% and 30%, encrypted text 98–100% |
| `wheel`, `adversary`, `genres` | far-out medieval ideas: a Llull disc (volvelle) evolved on GPU on the manuscript and on control texts, the best disc writes a text that is scored like the generators; a judge transformer trained on GPU against every content-free generator; litany and barbarous names (Ars Notoria, Liber Iuratus) measured like the manuscript | to be run on Colab: `colab/Voynich_Kolo.ipynb` |
| `transcriptions`, `cognate`, `hillclimb` | solvers from the literature: whether the manuscript's signature holds in the Currier, FSG, v101 and Takahashi transliterations; NeuroDecipher (Luo, Cao, Barzilay 2019): a soft glyph–letter key and optimal transport between the manuscript's vocabulary and the dictionary of each language, control on encrypted text with spelling noise; a homophonic attack as in AZdecrypt: thousands of hill climbers on GPU with a 4-gram model, a key from odd lines scored on even ones | to be run on Colab: `colab/Voynich_Lamacze.ipynb` |
| `phonotactics` | whether the words are built like spoken words: Sukhotin's algorithm determines the “vowels” of the manuscript and of each of ~50 languages, words are replaced by consonant–vowel patterns, the distributions are compared by Jensen-Shannon divergence; control: glyphs shuffled within the word | undecided (local run): vowels o, a, e, y; C/V alternation 0.80 as in Latin; pattern distribution at a distance of 0.21 bits from the nearest language (Old French), while languages lie 0.13 (median) to 0.26 from each other; v5 gibberish scores the same |
| `length_code` | content in word lengths: the sequence of glyph counts as a code for letters, digits or parity bits; capacity, structure against shuffles within the line, digit–letter reading by hill climbing with a 4-gram model of 8 languages, Bacon reading; control: Latin implanted as lengths | refuted (local run): 9 values, 2.7 bits/word, three lengths make up 75% of the sequence; the reading as letters does not beat the shuffled sequence in any language (≤ 0.06 bits), parity bits without structure; the control recovers the implanted Latin |
| `chronology` | the arrow of time of copying: whether hapaxes have sources (neighbours one glyph away) on earlier leaves; background shuffling pages only within blocks of section and language, separately inside blocks; controls: synthetic copying (must show the arrow), Latin (must not) | refuted (local run): z = −12 when the whole codex is shuffled, but 0.0 within blocks and from −2.1 to +1.0 inside blocks; the global signal is the arrangement of the sections; controls z = +21 and +12, Latin −0.5 |
| `hands` | whether the words are shaped by the scribe's hand (Davis 2020) or by the content: line classifier with held-out leaves, pairs of hands in the same section and language against a random deal of leaves; the effect of the section within the same hand | refuted (local run): the hands differ in herbal section B (AUC 0.72–0.90, z = +2.3 to +3.5), but the section within the same hand differentiates more strongly (0.73–0.97); the word rules follow the content or the mode of writing, not the scribe |
| `notation` | non-linguistic notation: Gregorian chant from the Cantus database (63 thousand Volpiano melodies; text words, syllables, neumes), basse danse tablature (Brussels 9085), Python code as a contrast, Latin and v5 gibberish through the battery of the manuscript's signature (8 criteria, defining feature: no long-range syntax); separate notebook `colab/Voynich_Notacja.ipynb` | refuted (local run): chant and code have very strong long-range syntax (unrelated units z = 62–166, manuscript −1.3); they share with the manuscript only the length dynamics (positive neighbour correlation, DFA 0.67–0.71 against 0.60 for the manuscript and 0.52 for Latin) |
| `labels`, `records`, `lists` | the “record notation” track (CPU part, `colab/Voynich_Rejestr.ipynb`, no GPU units): labels next to drawings as a sub-vocabulary of names, and their citation by the paragraphs of the page; the line as a record with fields (the position of the word read from the word alone, folios held out; mutual information of word class and position; predicting the field from the neighbours); the manuscript's signature against medieval lists (Usuard's martyrology, Apicius, the Alphita glossary, `data/lists/`) | local run (quick mode): the labels are a separate sub-vocabulary (hapaxes z = +12, o- +27, q- −12, length +11), but the paragraphs do not cite the labels of their page above background (z = +1.4); the rest to be run |
| `fields_lm`, `v6`, `cohesion` | the “record notation” track (GPU part, `colab/Voynich_Rejestr_GPU.ipynb`): the gain of a small GPT from word-position tokens; generator v6 (v5 with damping of words already used, 18 settings evolved on CPU on the scorecard of the odd folios, finalists on the even ones, judge transformer on GPU); page cohesion (a judge of pairs of lines from the same page against pseudo-pages) | `v6` undecided: evolution brings the misses down from 6 (v5) to 4 on the even folios (what remains: hapaxes, m at the line end, the spread of mean length, the link between the end of a word and the start of the next), but the judge still tells them apart (AUC 0.655; v5 0.658; real–real 0.531): what gives the gibberish away does not sit in the 22 measures. `fields_lm` method unreliable: synthetic records gained 0.012 bits instead of ≥ 0.15, because a GPT with a 256-character window knows the word's position in the line anyway (it counts the dots), so the position tokens are redundant; the test was badly conceived, do not repeat. `cohesion` method unreliable: positive control 0.654 < 0.7; manuscript 0.526 against 0.500 after the lines are dealt out, so there is no support for page cohesion |
| `keystream` | spaces as a key written into the text (`colab/Voynich_Klucz.ipynb`, CPU): 31 rules for cutting, shifting and reading the glyph stream according to the sequence of word lengths (in glyphs and in EVA characters) on the manuscript and on v5 gibberish; the segmentation is scored by description length (MDL), the units by long-range syntax and neighbour information; controls: Latin with spaces rewritten by a rule from the family and Latin read by columns are recovered (F1 = 1.0), plain Latin and v5 gibberish gain from no rule | local run (quick mode, 1500 lines): formally undecided (largest advantage of syntax over gibberish +3.6 at a threshold of 2.5, small-sample noise; full run on Colab), but no rule encodes the manuscript more briefly than the EVA spaces (closest 4.707 against 4.709 bit/glyph), and all four controls pass; the EVA spaces are the best segmentation in this family. Two pieces of side evidence: (1) adjacent words of the manuscript carry **less** information about each other than two random words of the same line (z = −24 on the full text, −7 to −32 by section), while v5 has +11, v6 +1.5, Latin +47; diagnosis: a line-edge effect, because with the first and last word held in place the excess is positive (+0.09 bits as in v5): the first and last words of lines are a separate vocabulary as whole words, not only through the glyphs p/m/g, which v5 does not reproduce; added to the scorecard as the 23rd measure; (2) pieces of 3 glyphs encode the manuscript and the gibberish more briefly than their words do (3.32 against 3.90 bit/glyph), and Latin at greater length (3.89 against 3.45): the manuscript's words are not economical units |
| `v6` as v7 | generator v7 (`colab/Voynich_V7.ipynb`, A100 approx. 40 min): v6 plus a stock of whole words that open and close a line (`p_edge`) and “neighbour avoidance” (`neighbour_gamma`), and the 23rd scorecard measure `adjacent_mi_excess` (information of adjacent words above random words of the line: manuscript −0.17 bits, v5 +0.03, languages positive); evolution of 20 settings, finalists on the even folios, judge transformer | 27 Oct (Colab, 25 generations): undecided. The best finalist misses only 2 of 23 measures on the even folios (hapaxes, the spread of mean line length; v6: 4, v5: 7), the stock of edge words came into use (`p_edge` 0.33–0.52), neighbour avoidance was zeroed out by evolution. The judge still tells them apart: AUC 0.642 (v6 0.655, v5 0.660, real–real 0.531). What gives the gibberish away still does not sit in the scorecard; the constant trace is too few hapaxes |
| `lengthkey` | a different cipher alphabet for each word length (`colab/Voynich_Klucz_Dlugosci.ipynb`, A100 approx. 1 h): a glyph in a word of a given length as a separate symbol, homophonic hill climbing searches for nine keys at once; the manuscript's gain from per-length keys against the gain of v5 gibberish and of renamed glyphs; control: Latin encrypted with nine keys recovered | 26 Oct: method unreliable in this configuration: the nine keys were recovered at 18–44% (one key 94–100%), because there are 9× more symbols for the same number of steps; with per-length keys every text reads worse than with one (the hill climbing does not converge). Even so, in none of the 6 languages did the manuscript's gain exceed the gibberish's gain (max 0.01 bits). To be fixed: start from the single-key key, steps ×7 |
| `brute_length` | brute force separately on each set of words of equal length (`colab/Voynich_Brute_Dlugosci.ipynb`, A100 approx. 30–40 min): sets of 2–8 glyphs and 9+, each as a separate cipher with its own key, triple by triple against 6 lexicons; background and control as in `brute`, per set | refuted (27 Oct, 563 s): 34 testable sets (the positive control for lengths 4–8 recovers the key at 97–100%), in none does the manuscript beat the gibberish; words of length 5–8 under their own key read as words of the language in 0–8% of cases (gibberish the same, encrypted text 97–100%); for lengths 2–3 the high shares (up to 94%) are common to the manuscript and the gibberish, because almost every two-letter string is a word; the 9+ sets are too small (209 words) |
| `plant_pairs` | the same plant in two places (`colab/Voynich_Rosliny.ipynb`, CPU): 9 “same plant” pairs and 28 “similar” ones (Zandbergen, Petersen) between the pharmaceutical section and the herbal section; shared vocabulary weighted by rarity against random pages of the same Currier language, rank of the true partner; labels of the fragments in the text of the herbal section; controls: the partner's words implanted (z = 20), pairs switched (z = −0.7) | refuted (local run): “same plant” pairs share FEWER words than random pages (z = −1.8, median rank 0.82), all pairs z = −1.0 (rank 0.61), labels z = −1.0; the closest in vocabulary are neighbours in the same quire (f87–f90), not pairs of the same plant: the text does not talk about what is drawn |
| `judge_probe` | what the judge sees (`colab/Voynich_Sedzia.ipynb`, A100 approx. 10 min): the real-versus-v7 judge probed with line features (hapaxes, words absent from the other corpus, length, position on the page) and AUC after vocabulary matching (shared words only) | confirmed (Colab 7 Nov, 35 s): judge AUC 0.690 (real–real 0.532, sensitivity 0.862); after vocabulary matching 0.566; strongest single feature: hapaxes (AUC 0.58); the correlations of the judge's score with the features within the real lines are close to zero: the judge's trace is vocabulary, not word order. Council: directionally yes, but there is no control on shuffled data and the sample is 247 lines; to be repeated on equal samples |
| `atoms`, `atoms_draft` | ontology of the illustrations (`data/atoms/`, `colab/Voynich_Atomy.ipynb`, CPU): drawings broken down into atoms, one record per label (853 loci on 51 pages), only observable features from a controlled vocabulary (`vocab.json`), entered by people (agreement of two people: kappa); rebus test: mutual information of each pair (drawing feature, label feature: first/second/last glyph, length, gallows, prefix) against labels shuffled within the page, correction for the number of pairs; controls: first glyph planted according to the feature (z = 72), features shuffled (no association); `atoms_draft`: a vision model (OpenRouter) describes the zodiac nymphs in this schema as a draft to be corrected; `atoms_vision` (`colab/Voynich_Atomy_GPU.ipynb`, A100, no API): Molmo2-8B marks with points the centres of the circles, the figures and the stars, geometry counts the rings and the clockwise order, Qwen3-VL-8B describes the crop around each figure, Grounding DINO counts with boxes as a control; PNGs with point numbers for checking the order; first run (28 Oct, 321 s): the models work, Molmo2 found the circle centres, but on whole spreads it pointed to few figures (Pisces 28/29, Aries 15/15, the rest 0–12/30) and the recognition of the sign failed, 0 pages; fix: a crop of each circle separately at full resolution, three counters merged, pages from the table of scan panels (voynich.nu); second run (696 s, 9 pages): the points hit the nymphs, but every other one landed at x ≈ 0 because of a bug in the Molmo2 coordinate parser (format “frame, number, x, y”), which also spoiled the circle centres; parser fixed according to the model card, circle radius from the panel width; third run (30 Oct, 1642 s, 12 pages): Pisces 28/29, Aries 15/15 and 15/15, Taurus 16 and 18/15, Cancer 30/30, but the pages with reclining nymphs are weak (Leo 12, Virgo 2, Scorpio 11, Sagittarius 8 of 30), Gemini and Libra in excess (39, 37); on the PNG the rings and the order of f71r are correct; fix: the circle crop is pointed at in 4 rotations, exclusion of the centre (the figure of the sign), merging of close points; fourth run with rotations (5 Nov, 2917 s): the pages with reclining nymphs recovered (Scorpio 29, Sagittarius 26, Virgo 34, Leo 35 of 30), excess from duplicates between rotations and from one burst of hallucination (60 “figures” in one rotation of Leo); fix: each point has support from 8 sources (2 questions × 4 rotations), as many of the best-supported points are kept as the page has nymphs; fifth run (7 Nov, 2852 s): 10 of 12 circles with the exact number of figures (Sagittarius 26, Scorpio 29 of 30), 11 pages (255 atoms) merged into `data/atoms` as the “vision” source | refuted on the draft (7 Nov): 255 of 857 atoms described (GPU draft on 11 zodiac pages, 10 of 12 circles with the exact number of figures); none of the 54 pairs drawing feature × label feature exceeds the background (best z = +1.9); controls: planted glyph z = 53, shuffled features no association. Caveat: features from the model's draft (confidence 1), verdict to be repeated after human corrections |
| `catalog` | cross-sectional analysis (`data/catalog/pages.json`, `scripts/fetch_catalog.py`, CPU approx. 1 min): Zandbergen's page catalogue (voynich.nu, 226 pages: section, description of the drawing, the plant-drawing style features of Gheuens and Rapaport α/β on 109 pages of the herbal section, Currier language, LFD hand, herbal–pharmacy cross-references); (1) drawing style β−α against language and hand (AUC with permutations); (2) pages with a shared drawing feature against random groups with the same language+hand composition, vocabulary weighted by rarity, correction for 19 features; (3) register of sections; controls: a shared group glossary planted (z = 5.9), features shuffled (z = 1.4) | refuted (local run, 7 Nov): drawing style predicts the scribe almost without exception (language B: AUC 0.99, z = +7.0; hand 2: AUC 0.98), but not the content: none of the 19 drawing features links pages by vocabulary above language and hand (best “two leaf shapes” z = +2.5, corrected p 0.13); pages with a shared style share as many words as random pages by the same scribe |
| `hapax_source` | where the hapaxes come from (`colab/Voynich_Bomba.ipynb`, CPU approx. 1 min): (1) r* = the copyist's error rate (one glyph changed, added or removed) at which a nomenclator of the same size and with the same code words has the same share of hapaxes among tokens as the manuscript (13.7%); (2) locality: how often a frequent neighbour of a hapax stands in the 5 lines above it compared with another page, for the manuscript, v7 gibberish and the nomenclator at r*; controls: copies from 3 lines above planted (z = 126), lines dealt at random to pages (z = 0.4) | undecided (local run, 7 Nov): r* = 0.21 in Hebrew, Arabic and Latin (every fifth code word with an error); locality of the manuscript ×2.07 against ×1.79–1.96 for nomenclator errors (z of the difference −0.4 to −2.4) and ×1.58 for v7 (+2.4): the hapaxes do not rule out a nomenclator, but locality does not distinguish errors from copying from the neighbourhood |
| `cribs` | cribs from the diagrams (`voynich/lab/cribs.py`, CPU approx. 8 min): the 28 radial words of f69v against the 28 lunar mansions (Arabic, and Agrippa's Latin ones), the 12 words of the circles f67r1, f67v1, f67r2 against the signs of the zodiac (Latin, Italian, Arabic, Hebrew) and the months (Latin, French, Occitan, Catalan, Italian, German); every start and direction of the list, glyph → letter key from hard EM; null: the same names in 1000 shuffled orders, Bonferroni over 32 pairs; control: a list written in the manuscript's glyphs with a random key with 10% noise (z ≥ 9.6 for each list) | refuted (local run, 7 Nov): no pair scores above a random order; f69v × mansions z = −0.1 (Arabic) and −0.5 (Latin); best f67v1 × Catalan months z = +3.8, corrected p 0.10 (one exact hit “maig”, the rest “jilill~juliol”, “mamg~marc”), just behind it the same ring with the French months (z = +3.0): something to check, not a discovery |
| `polybius` | Polybius in word lengths (`voynich/lab/polybius.py`, CPU approx. 10 min): two consecutive word lengths of the paragraphs (in glyphs, 9+ = 9) are the row and the column of a letter; both phases (from the first and from the second word); cell → letter key by annealing on letter trigrams + emission cost; Latin, Hebrew, Italian, German; the manuscript against the same lengths shuffled (3×); control: a text in the language written as word lengths with a random 5×5 table | refuted (local run, 9 Nov): the control is read in Latin, Italian and German at 100% (Hebrew 46%, excluded from the assessment); the manuscript reads the same as the shuffled one: Latin 4.70/4.69 and 4.78/4.71, Italian 5.20/5.18 and 5.18/5.18, German 5.12/5.15 and 5.16/5.12 bits per letter (naturally 2.8–3.3) |
| `master_card` | master card (`voynich/lab/card.py`, `colab/Voynich_Karta.ipynb`, A100 or CPU approx. 23 min): whether the words were assembled from one table of pieces in 6 columns from the start to the end of the word (at most one piece from each column, glyph n-grams n ≤ 3); the best card of 40, 80, 120 and 200 entries from evolution; the manuscript against Latin, Italian, v7 gibberish, the manuscript with glyphs shuffled within the word; control: a text written with a known 5 × 8 card with 10% errors (recovered: 0.93 against 0.91 for the true card); Currier A against B | confirmed (local run, 10 Nov): a card of 120 entries assembles 96% of the manuscript's words (40 entries: 77%, 80: 93%), 70% of Latin, 74% of Italian, 74% of the shuffled manuscript, 95% of v7 gibberish; languages A and B fit in one card (card A on B 0.95, B on A 0.93; drop 0.014 as between random halves of the pages, 0.004–0.012). Card table: [`docs/karta_matka.en.md`](docs/karta_matka.en.md). Caveat: this is a description of how the words are built, consistent with a recipe card, not proof that the card physically existed; v7 is assembled from the card just as well |
| `master_card_full` | master card for 100% of the words (`voynich/lab/card.py`: `prune`, `shrink`; `colab/Voynich_Karta.ipynb`, GPU: L4 7.7 h, A100 faster; CPU approx. 66 min with a smaller population): the full card (every piece in each of the 6 columns) assembles everything; 256 cards prune it at once, each in its own order, an entry disappears when 100% (and 99%) of the tokens can still be assembled without it; then evolution under a budget one entry smaller (up to 40 rounds); the same steps for Latin, Italian, v7, the shuffled manuscript; control: a text written with a known card of 40 entries (recovered card: exactly 40 entries, also at 99%) | confirmed (Colab L4, run 20261110-143915): every word of the manuscript can be assembled from a card of 242 entries (99% of the words: 132); Latin needs 639 (562), Italian 556 (422), the manuscript with shuffled glyphs 563 (355), v7 gibberish 211 (125). Locally on CPU (4 pruning cards): manuscript 264 (185), Latin 652, Italian 579, shuffled 567, v7 215. Table: [`docs/karta_matka_100.en.md`](docs/karta_matka_100.en.md). Caveats: hapaxes also add entries; at 99% the shrinking was stopped by the 40-round limit, so these numbers are upper bounds; pruning finds a small card, it does not prove that there is no smaller one |
| `card_choice` | choices from the master card (`voynich/lab/cardchoice.py`, CPU approx. 17 min): each word broken down into choices from the 6 columns of the text's own card (pruned to 100% of the tokens); how much the choices say about the page beyond the section (against shuffling whole lines between the pages of the section) and whether there is a jump at the page boundary (lines of the same page more similar than lines at the same distance on the two sides of the boundary; lines at the page edges omitted, each line trimmed to 8 choices); separately the recto→verso boundary of the same leaf and the boundary between leaves; the manuscript against v7 gibberish and Latin in the same layout; controls: each page's favourite entry planted (z = 80, jump z = 4.3), drift blind to pages (z = 36, jump z = 1.2), clean text (z = −0.1) | undecided (local run, 11 Nov): the choices carry 2.6% of their entropy about the page (herbal section 3.6%), v7 0.7% (1.3%), Latin 2.0% (2.7%); the jump at the manuscript's page boundaries is +0.10 (z = 4.4), v7 and Latin approx. 0. But the jump sits at the boundaries between leaves (+0.15, z = 7.2, 84 boundaries), and between the recto and verso of the same leaf it is weak (+0.06, z = 1.9, 98 boundaries): this looks like leaves written at different times and later sewn together in a different order, not like content that changes with every plant. Caveat: the clean control text gives a jump of z = 2.3, so the z values of the jump are probably inflated; the jump measurement was added after the first run |
| `sheet_order` | order of writing, the scribe's drift as a clock (`voynich/lab/bifolio.py`, CPU approx. 4 min): leaves of one quire, of the same hand and Currier language; whether two leaves of one sheet (bifolium; far apart in the book, e.g. f1 and f8) are more similar in their choices from the master card than other pairs of leaves of the quire, and whether leaves adjacent in the book are more similar; 2000 swaps of leaves within (quire, hand, language); controls on a text written with a known card by a scribe with drift: by sheets in random order (sheet z = 5.7, adjacent z = 0.0), page by page in book order (adjacent z = 6.1, sheet z = −0.3), without drift (0.3 and −0.2) | confirmed (local run, 11 Nov): leaves of one sheet z = 6.4 (34 pairs), leaves adjacent in the book z = 0.5 (45 pairs): the writing was done sheet by sheet, before the quires were put together. Pages of one sheet: same leaf 5.2, outer side 5.5, inner side 5.7, different side and leaf 4.1 (z 1.7–2.0, too weak to say in what order the four pages were written). The quire is not a unit: the nearest sheet lies in the same quire in 37% of cases against 34% at random (z = 0.6); in herbal section A the nearest sheets are usually in other quires. Table: [`docs/arkusze.en.md`](docs/arkusze.en.md). Caveats: shared content of a sheet would leave the same trace as drift; we do not reconstruct the full order of the sheets (on the control ρ 0.1–0.6), only the nearest neighbour is reliable (62% hits on the control against 4% at random) |
| `card_stream` | one word = one letter? (`voynich/lab/cardstream.py`, `colab/Voynich_Strumien.ipynb`, GPU): the master card of 242 entries (`data/card/karta_matka.json`) breaks a word down into choices in 6 columns; each column and each pair of columns is a stream of symbols, one per word (21 streams); stage 1: how much a symbol says about the next one above the shuffling of words within lines; stage 2: a homophonic solver (passes over the symbols, full likelihood: letter 4-grams minus the cost of merging symbols into one letter) on the streams with the most memory, in Latin, Italian and German; the manuscript against the manuscript with words shuffled within lines; controls: the letters of a real text hidden in the same streams | refuted (local CPU run, 11 Nov, reduced version: 4 streams, Latin and Italian; full run on GPU in the notebook): memory of the best stream 0.049 bits (columns 1+3) against 0.40–0.51 bits for hidden Latin; the solver reads the hidden text in 7 of 8 language–stream pairs (96–100% of the key), while from the manuscript it extracts a sequence of 5.6–6.5 bits per symbol against 3.1–3.2 for language; word order helps it by −0.05 to +0.24 bits (a habit at the junction of words). Caveat: only a letter in one column or in a pair of columns was checked; not checked: a letter spread over three or more columns, the Naibbe cipher, filler words between letters |
| `nomenclator2` | a nomenclator with two keys (Currier languages A and B) and copyist's errors, the only cipher family left open after Zhang and Sheng (arXiv:2610.34499), in Hebrew, Arabic and Latin (`voynich/lab/nomen2.py`): rare types merged with a frequent type one glyph away, symbol → unit key (200 whole words, the rest by letters) from Gibbs sampling with many chains at once (cupy on GPU, numpy on CPU) under the full likelihood: unit bigram + emission cost of homophones (the language model alone preferred a wrong key to the true one: 3.36 against 4.19 bits); key on odd lines, bits on even ones; controls of the same size as the manuscript, encrypted with 800 words of the manuscript at r = 0, r* and 0.5; the manuscript against v7 and the manuscript shuffled within the line | refuted (local run on CPU, 16 chains × 200 sweeps, 654 s, 7 Nov): the solver reads the controls (r = 0: Hebrew 0.81, Arabic 0.83, Latin 0.91 of tokens; at r* = 0.21: 0.54 / 0.64 / 0.81, Zhang and Sheng: 46% for Hebrew), while the manuscript read as a nomenclator has 5.62 / 5.64 / 5.64 bits per unit, the same as v7 gibberish (5.60 / 5.69 / 5.61) and 0.6–1.4 bits more than the control with the same error rate (4.90 / 5.02 / 4.25); shuffled 5.8–6.0. The refutation rule (the mirror of the lead rule: neither 0.15 bits better than v7 nor within 0.3 bits of the control) was fixed after the first run, in which the old rule (≥ v7 − 0.05) left Arabic on the 0.05-bit boundary. The run on A100 (256 chains × 600, `colab/Voynich_Bomba.ipynb`) broke off in the night of 7/8 Nov (Colab disconnected) and was not repeated: the CPU result is final |
| closing run | `colab/Voynich_Final.ipynb`: theories with added controls (genres: frame implanted and litany shuffled; judge: sensitivity and three splits; hill climbing and NeuroDecipher: glyphs renamed in every line; disc: the text of a known disc) and `length_code`, `chronology`, `hands` at full settings | to be run |

**Hounds** (`voynich/lab/hounds.py`, `voynich/lab/recipes.py`): the council stops merely judging and goes hunting itself.
Each model gets a role (cryptologist, linguist, sceptic, “wild dog”) and in successive rounds invents reading recipes
from building blocks: keys from π, e, √2, φ, prime numbers, dates and words (like the Vigenère cipher), nulls, every n-th word or glyph,
glyph groups, reversal, acrostics, removal of spaces, 15 target languages, writing without vowels. Each block has
an exact inverse, so each recipe automatically gets a positive control (a text in the target language encrypted
with the same recipe must come back) and negative controls (gibberish from the v4 generator, the manuscript with shuffled words).
A lead counts only when the manuscript clearly beats the gibberish and the reading is almost as predictable as a real
language; the best leads are repeated on another part of the manuscript. Ideas from outside the blocks go onto the wish list.
In the notebook: `lab.hunt(rounds=4, per_hound=2)`.

The lab compares with 17 Bible languages (Basque joined as the 13th; Spanish, Portuguese, French and Romanian as the 14th–17th) and with medieval Latin, Vulgar Latin (Egeria), Old French, and in brute force also with Aramaic (Targum Onkelos) and Syriac (Peshitta); the report `docs/index.html` from stages 1–2 was still computed on 12.
`fetch_data.py` ends with the message “Dane kompletne.”, and the lab refuses to compute on incomplete data.

Colab secrets: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. The results go to the `lab-results` branch.
From the command line: `python -m voynich.lab.runner --theories numbers,literature --quick --no-council`.

## Final summary (11 November 2026)

In a little over three weeks we turned 48 hypotheses about the manuscript into tests with controls: each test first had
to find an effect that we had planted ourselves, and not find it in random data. No hypothesis that the text is a
language, a cipher, a notation of music, dance or a program, or a list of names, passed. The strongest attack, on a
nomenclator with two keys and copyist errors (the only cipher that the literature had not yet ruled out), reads trial
ciphers in Hebrew, Arabic and Latin at 81–91%, and the manuscript as poorly as computer-generated gibberish. The
illustrations gave nothing either: the style of the drawings gives away the scribe, but not the content, and the diagram
wheels are not enciphered names of lunar mansions, signs or months.

After 8 November, when the project was to be closed, two positive results came. First: the words of the manuscript are
assembled from one small table, the "master card": 242 pieces in 6 columns write every word, where Latin needs 639.
Second: the scribe's habits in choosing from that card work as a clock and show that the manuscript was written sheet by
sheet (bifolium by bifolium) before the quires were put together. The card itself does not carry a text letter by letter
(`card_stream`, a preliminary run).

What explains everything best is a text without content, written out of habit from a shared table of pieces and by
reworking words from neighbouring lines; the only thing that our generator does not fully imitate is the number of words
that occur only once. This is a conclusion based on numbers, not a proof; the code, data and results (`lab-results`) are
public and reproducible.

## State of research (11 November 2026)

A little over three weeks, 48 theories turned into tests with controls, 28 runs on Colab (A100, L4 and CPU) on the
`lab-results` branch and local runs of the latest tests, 131 code tests. Each test must find an effect planted on purpose and not find it in random data; without that the verdict
is "method unreliable". The rows in the table above give the numbers; here is a summary.

**Ruled out (controls passed):**
- Substitution cipher, simple and homophonic, for 53 languages and dictionaries of the period. Three solvers (brute force over word triples,
  hill climbing with an n-gram model, NeuroDecipher) recover the key from the control text at 94–100%, and from the manuscript they extract
  as much as from gibberish. This also covers keys that differ for each word length (`brute_length`: words of 5–8 glyphs read
  as words of a language at 0–8%, the same as gibberish; enciphered text 97–100%) and a key written in the spaces (`keystream`:
  no cutting, shifting or reading of the glyph stream encodes the manuscript more briefly than the EVA spaces).
- Non-linguistic notation with syntax: plainchant, dance tablature, a program (`notation`, z = 65–145 against −1 for the manuscript);
  medieval lists: a martyrology, Apicius, the Alphita glossary (`lists`, z = 64–113).
- Long-range syntax: in four transliterations a word says nothing about the word 2–7 places further on (z ≈ −1), which is true of no
  language, cipher that preserves word order, notation or list.
- Text describing the pictures: paragraphs do not quote the labels of their own page (`labels`, z = +1.4), pages with the same plant share
  fewer words than random pages (`plant_pairs`, z = −2), similarity of drawings does not go together with similarity of words
  (Mantel r = 0.08). Cross-sectional analysis of Zandbergen's catalogue (`catalog`, 7 Nov): the drawing style of the plants (the α/β features of Gheuens
  and Rapaport) predicts the scribe almost without exception (language B: AUC 0.99), but pages with a shared style do not share words beyond
  what random pages by the same scribe share (19 features, the best z = +2.5, nothing after correction). Rebus in drawing–
  label pairs (`atoms`, 255 zodiac nymphs from the GPU draft): none of the 54 pairs drawing feature × label feature exceeds the background.

- The last attack ("bomba", 7 Nov, `colab/Voynich_Bomba.ipynb`): a nomenclator with two keys and copyist errors, the only
  family of ciphers that Zhang and Sheng did not rule out. The new solver reads manuscript-sized controls in Hebrew (81%),
  Arabic (83%) and Latin (91%), also at the manuscript's error rate (54–81%), and it reads the manuscript as badly as v7 gibberish
  (`nomenclator2`). The hapaxes do not rule out copyist errors (r* = 0.21), but their position does not distinguish errors from
  copying from the neighbourhood (`hapax_source`). The diagram wheels do not read as lunar mansions, signs or months
  (`cribs`, 32 pairs, the best f67v1 × Catalan months z = +3.8, corrected p 0.10). Nor do the word lengths hide
  a text as pairs of coordinates in a Polybius square (`polybius`, 9 Nov): the manuscript reads like a shuffled one.
  Colab (run 20261107-203642 on `lab-results`) repeated `hapax_source` and `cribs` with the same numbers;
  `nomenclator2` broke off on the GPU and stays with the CPU result.
- One word = one letter (`card_stream`, 11 Nov, a preliminary run on CPU; the full one is in `colab/Voynich_Strumien.ipynb`):
  no column of the master card and no pair of columns carries a text letter by letter. The best stream of choices
  remembers 0.049 bits against 0.40–0.51 bits for hidden Latin, and the solver that reads the hidden text gets out of the
  manuscript a sequence of 5.6–6.5 bits per symbol against 3.1–3.2 for a language.

**Found (controls passed):**
- Master card (`master_card`, 10 Nov): a single table of 120 word pieces in 6 columns is enough to assemble 96% of the
  words of the manuscript, against 70–74% for Latin, Italian and the manuscript with shuffled glyphs. Currier languages A
  and B fit in the same card. This is the simplest mechanism that explains how five scribes wrote fluently by shared
  rules: [`docs/karta_matka.en.md`](docs/karta_matka.en.md). The card that assembles every word without exception
  (`master_card_full`) has 242 entries (GPU): 2.6 times fewer than for Latin (639) and 2.3 times fewer than for the
  manuscript with shuffled glyphs (563), but as many as for v7 gibberish (211); for 99% of the words: 132 entries against
  562 for Latin: [`docs/karta_matka_100.en.md`](docs/karta_matka_100.en.md). So the card describes how the words were
  built, not whether they mean anything. What it could have looked like on the scribe's desk:
  [`docs/karta_matka_rekonstrukcja.en.jpg`](docs/karta_matka_rekonstrukcja.en.jpg) (132 pieces, 99% of the words) and
  [`docs/karta_matka_rekonstrukcja_242.en.jpg`](docs/karta_matka_rekonstrukcja_242.en.jpg) (every word); they are drawn by
  `scripts/render_card.py`. This is a computer reconstruction: the pieces come from the test; the parchment, ruling and
  layout are conjecture.
- Writing sheet by sheet (`sheet_order`, 11 Nov): the drift of the scribe's habits in choosing from the card works as a
  clock. Two leaves of one sheet, far apart in the bound book, have the same habits (z = 6.4); adjacent leaves do not
  (z = 0.5). The manuscript was written sheet by sheet before the quires were assembled, and the sheets of one quire are
  no closer to each other than the sheets of different quires: [`docs/arkusze.en.md`](docs/arkusze.en.md). `card_choice`
  (undecided) agrees: which pieces the scribe took from the card depends on the page more strongly than in v7 gibberish,
  but it changes abruptly between leaves, and not between the recto and verso of one leaf.

**Unexplained:**
- The contentless generator v7 (copy from the neighbourhood and rework) hits 21 of 23 statistical measures, but the transformer judge
  still tells it apart from the manuscript (AUC 0.642 against 0.531 for the manuscript against itself). A lasting trace: the manuscript has more words
  that occur only once than reworking neighbours gives. `judge_probe` (7 Nov) indicates that the judge sees vocabulary, not word order:
  after restricting to words common to both corpora the AUC falls from 0.690 to 0.566, and the strongest single feature is hapaxes.
  The council adds a caveat: no control on shuffled data and a small sample; to be repeated.
- The labels next to the drawings are a separate stock of names: different beginnings, different lengths, and half never occur in the paragraphs.
- Adjacent words carry less information about each other than random words of the same line (z = −24; gibberish +11, Latin +47).
  The line-edge vocabulary explains this, but the feature itself had not been described before.
- Rigid pieces of 3 glyphs encode the manuscript more briefly than its own words (3.32 against 3.90 bits per glyph); in Latin, words
  beat pieces.

**Final conclusion:** the text carries no content in any sense in which a language, a cipher that preserves word order, a notation
or a list carries it. The most probable is writing without content, produced out of the scribe's habit, with a possible admixture of real names
(the labels). The words were assembled from one small table of pieces, and the leaves were written sheet by sheet:
that describes the scribes' workshop, not a content. This is an opinion based on numbers, not a proof: everything is public and reproducible.

**Image–label track (atoms):** drawings broken down into atoms, one record per label (853 loci on 51 pages),
only observable features from a controlled vocabulary; a draft made on our own GPU with open models (Molmo2, Qwen3-VL, Grounding
DINO) with the order of the nymphs computed from geometry. After five runs 10 of the 12 zodiac wheels have the exact number of figures,
255 atoms are merged, and the `atoms` test on this draft comes out "refuted" (the model's features have confidence 1, so the verdict
awaits corrections by people). Instructions for the people filling it in: [`data/atoms/README.en.md`](data/atoms/README.en.md).

## Running

```bash
python scripts/fetch_data.py      # comparison corpora (the Bible in 12 languages, medieval Latin)
python scripts/run_analysis.py    # stage 1 experiments -> docs/results.json (~10 min)
python scripts/run_extended.py    # stage 2 -> docs/results_ext.json (~5 min)
python scripts/build_report.py    # docs/index.html
python -m unittest                # tests
```

`run_analysis.py --quick` does a quick run (3 languages, fewer permutations).

## Structure

| file | what it does |
|---|---|
| `voynich/ivtff.py` | parser of the IVTFF format (pages, the variables `$I $L $H`, loci) |
| `voynich/eva.py` | EVA cleaning, splitting into words and glyphs (`cth`, `ch`, `ii`… as one character) |
| `voynich/corpus.py` | loading the manuscript and the comparison corpora |
| `voynich/stats.py` | entropies h₁–h₃, Zipf, vocabulary density, repetitions |
| `voynich/structure.py` | glyph positions, rigidity of order, permutation tests, section keywords |
| `voynich/selfcite.py` | self-citation generator: hand-written rules, edits observed in the scribe, word grammar |
| `voynich/latin.py` | medieval spelling, splitting into syllables, scribal abbreviations |
| `voynich/syllabic.py` | syllabic hypotheses, syllabic code, word-level invariants |
| `voynich/cipher.py` | solver for substitution ciphers (annealing, MDL criterion) |
| `voynich/lab/` | the lab: configuration, OpenRouter client, council of models, IIIF scans, theories, report and push |
| `voynich/lab/recipes.py`, `hounds.py` | recipe language (blocks with inverses, controls) and the hunt of the hounds |
| `colab/` | the Colab notebook and the script that generates it |

## Data and sources

- `data/raw/ZL3b-n.txt`: the Zandbergen–Landini transliteration, version 3b of 13 May 2025
  (René Zandbergen, [voynich.nu](https://www.voynich.nu/transcr.html)), SHA-256 `bf5b6d4a…beccafc`.
- Comparison corpora: [christos-c/bible-corpus](https://github.com/christos-c/bible-corpus)
  and medieval Latin from The Latin Library ([cltk/lat_text_latin_library](https://github.com/cltk/lat_text_latin_library)),
  downloaded by `fetch_data.py` (they are not in the repository). Note: "bacon" in this collection
  is Francis Bacon (17th century), not Roger Bacon, so we skip it.
- T. Timm, A. Schinner, *A possible generating algorithm of the Voynich manuscript*, Cryptologia 44 (2020).
- B. L. Monroe, M. P. Colaresi, K. M. Quinn, *Fightin' Words*, Political Analysis 16 (2008), for the keywords.

## License

The code, the tests and the documentation of this repository are released under the [MIT License](LICENSE).
Third-party material keeps its own terms: the Zandbergen–Landini transliteration in `data/raw` (voynich.nu), the reference
corpora fetched by `fetch_data.py`, and Gabriel Landini's EVA Hand 1 font, which `scripts/render_card.py` downloads for
drawing the master card and which is not part of the repository (free for private, non-commercial use).
