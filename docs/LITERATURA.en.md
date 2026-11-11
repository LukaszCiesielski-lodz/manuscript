# Literature review for Voynich Lab

Found with Firecrawl (index of scientific papers: arXiv, PubMed/PMC, and the general search engine), October 2026.
For each paper: what we take from it for the tests.

## Linguistics and text statistics

- **Bowern & Lindemann, *The Linguistics of the Voynich Manuscript*, Annual Review of Linguistics 7 (2021).**
  A review: the text has features of a natural language (Zipf, section-dependent vocabulary), but an unusually low
  conditional entropy. The reference point for the whole project.
- **Lindemann & Bowern, *Character Entropy in Modern and Historical Texts*, arXiv:2010.14697.**
  On 294 languages and 18 historical texts: no transformation of the writing (glyph composition, abbreviations) brings
  the entropy level with languages. Restricted positions of characters in the word may mean a loss of phonemic distinctions. Consistent with our stage 1.
- **Rozanova & Temerev, *A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space*, arXiv:2608.17096 (2026).**
  The structure sits on the word edges: glyphs at the junction of neighbouring words have ~0.2 bits of mutual information, more
  than in any control text; uncertain spaces behave like boundaries inside a word. The Naibbe cipher and the self-citation
  generator reproduce the low entropy, but not this coupling nor the 70% of hapaxes (41% and 59–60%).
  → the `edge_mi` measure in `voynich/lab/common.py`; we compare every generator against it.
- **Montemurro & Zanette, *Keywords and Co-Occurrence Patterns in the Voynich Manuscript*, PLoS ONE 8 (2013).**
  The distribution of keywords across sections is like in a text with content. Consistent with our section keywords.
- **Amancio et al., *Probing the statistical properties of unknown texts*, PLoS ONE 8 (2013), arXiv:1303.0347.**
  Network and intermittency measures: the text is consistent with natural languages, inconsistent with a random one.
- **Timm, *How the Voynich Manuscript was created*, arXiv:1407.6639; *Co-Occurrence Patterns*, arXiv:1601.07435;
  Timm & Schinner, Cryptologia 44 (2020).** The self-citation hypothesis; our generator v1–v4.
- ***A Quantitative Confirmation of the Currier Language Distinction*, arXiv:2604.25979 (2026).**
  The A/B split confirmed without labels (89% accuracy); the main component is a "switch" of the vowel after `ch`/`sh`
  set once per page. → in test B (Mantel) we permute within language and scribe.
- ***Evidence of Layered Positional and Directional Constraints*, arXiv:2604.19762 (2026).**
  The Cardan grille and the slot generator do not reproduce the four signatures of the manuscript at once. → the `cardan_grille` theory.
- ***Directionality of the Voynich Script*, arXiv:2509.10573.** Asymmetry of n-gram perplexity in the two directions.
- ***On the Non-Specificity of Statistical Measures Used in Script Decipherment*, arXiv:2608.02999 (2026).**
  An artificial sign system without phonetics gets the same "linguistic" signatures as the Indus script, and a dictionary attack
  reaches high coverage for many languages at once. → specificity controls in all our attacks.

## Ciphers and generators

- **Greshko, *The Naibbe cipher*, Cryptologia (2025), doi:10.1080/01611194.2025.2566408.**
  Latin cut into unigrams and bigrams (a dice roll), each letter enciphered with one of 6 tables chosen by a playing card
  (5:2:2:2:1:1); unigram → a whole word, bigram → prefix + suffix. It reproduces the entropy (2.00 bits in EVA),
  the length distribution, Zipf and Heaps; it does not reproduce the long-range correlations, the line effects or the full diversity of words.
  → the `naibbe_cipher` theory (a reconstruction from the description, tables made of word parts of the manuscript).
- **Rugg, *An elegant hoax?*, Cryptologia 28 (2004); Zandbergen, *The Cardan grille approach... taken to the next level*, arXiv:2104.12548.**
  → the `cardan_grille` theory.
- **Hauer & Kondrak, *Decoding Anagrammed Texts Written in an Unknown Language and Script*, TACL 4 (2016).**
  The conclusion "Hebrew with anagrams" is criticised as non-specific. → the `hebrew_anagram` theory with a specificity control:
  in our test the attack "finds Hebrew" also in English (75%) and Vietnamese (91%).
- ***Can Evolutionary Computation Help us to Crib the Voynich Manuscript?*, arXiv:2107.05381.**
  Female names as cribs in the calendar. Our attack with plant names (the `illustrations` theory, part C) works
  similarly, but with a null distribution from shuffled names.

## Illustrations and page layout

- ***Subtle Signs of Scribal Intent in the Voynich Manuscript*, arXiv:2404.13069.**
  Words just before a drawing and at the end of a line have different lengths (χ², binomial tests). → the `illustrations` theory,
  part A; our replication: the word before a drawing is shorter by 0.24 glyphs (p ≈ 0.003).
- ***Topic Modeling in the Voynich Manuscript*, arXiv:2107.02858.** LDA topics coincide with the sections (illustrations)
  and the scribes jointly. → that is why the Mantel test controls for the scribe.
- ***A Generative Grammar Underlying the Voynich Manuscript, the Pastiche Hypothesis*, arXiv:2609.20835 (2026).**
  Matching of the images to the Pseudo-Apuleius herbals with the help of large models; the text as an ordered imitation.
- ***A Visual Classification Dataset... for Historical Manuscript Illustrations*, arXiv:2609.33449.**
  Zero-shot CLIP and vision-language models perform poorly on manuscript illustrations. → we treat plant identifications by
  a vision model as uncertain and test them by permutation.

## Numbers

- Wikipedia (*Voynich manuscript*): the lines of f15v "oror or", "or or oro r" resemble enciphered Roman numerals;
  the numbering of the leaves and quires is later and written in ordinary digits.
- Forums (voynich.ninja, r/voynich) put forward number hypotheses without statistical tests; none has passed peer review.
  → the `numbers` theory: 5 number systems from before 1450 and a continuity test of the zodiac labels with planted numbers.

## Word structure (background for the master card)

- J. Stolfi, *A grammar for Voynichese words* (2000): core, mantle and crust of a word; the first word grammar based on statistics.
- G. Rugg, *An elegant hoax?*, Cryptologia 28 (2004): a table of prefixes, midfixes and suffixes with a Cardan grille.
- ThomasCoon (Voynich Ninja forum, 2016) and M. Zattera, *A New Transliteration Alphabet Brings New Evidence of Word Structure in the Voynich Manuscript*, CEUR Workshop Proceedings 3313 (2022), [paper 10](https://ceur-ws.org/Vol-3313/paper10.pdf): slot alphabets, 12 consecutive slots with a few glyphs in each.
- Overview: https://www.voynich.nu/a3_para.html
  → the `master_card` and `master_card_full` theories: the same structure, but a table found by search, writing every word,
  measured by the same procedure against Latin, Italian, shuffled glyphs and a text written from a known card.

## Other undeciphered scripts (methods)

- Rao et al., *A Markov model of the Indus script*, PNAS 106 (2009); Yadav et al., PLoS ONE 5 (2010): n-grams for the Indus script.
- Luo et al., *Neural Decipherment via Minimum-Cost Flow*, arXiv:1906.06718; *Deciphering Undersegmented Ancient Scripts Using Phonetic Prior*, arXiv:2010.11054.
- Work on the oracle bone script (arXiv:2604.09668, 2406.00684): generative models as a source of hypotheses with transparent evidence, not as a reading.

## Source of the scans

Yale University Library, Beinecke MS 408, IIIF manifest: https://collections.library.yale.edu/manifests/2002046
(213 canvases; missing folios: 12, 59–64, 74, 91, 92, 97, 98, 109, 110). The scans are downloaded at run time and are not in the repository.
