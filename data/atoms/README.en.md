# Illustration atoms

We take the drawings apart into atoms: one record per one drawn thing, pinned to the label (the words) written next to it.
There are 853 labels (1014 words) on 51 pages. The goal: to check whether some feature of the drawing predicts something in the label (the first glyph, the length, the ending). If a rebus
exists, it sits precisely in the drawing–label pairs: the paragraphs do not quote the labels of their own page, and pages with the same plant
do not share words (the `labels` and `plant_pairs` tests).

## Rules

1. **Only what can be seen.** "flower, 5 petals, blue" yes; "sage" no. Put the interpretation in `uwaga`.
2. **Every atom has a label.** The files are generated from the transliteration: one atom per one label word (loci `L*`),
   with the words already filled in. You fill in only `cechy`, `pozycja.krag`, `zrodlo`, `pewnosc`.
3. **Values only from the vocabulary** `vocab.json` (`true`/`false`, a number or one of the allowed words). `null` = I do not know / not applicable.
4. **`zrodlo` = your first name, `pewnosc`** 1 (I am guessing), 2 (probably yes), 3 (certain). Two people on the same page is not
   a waste: the agreement of two people (kappa) tells whether the feature is objective at all. Features with kappa < 0.6 do not enter the test.
5. **Order: zodiac → pharmaceutical section → herbal section.** The zodiac is the most regular (nymph, star, label; 294 labels on
   12 pages). In the herbal section the atoms are the most a matter of judgement.

## Record

```json
{"id": "f70v2-07", "typ": "nimfa",
 "cechy": {"naga": true, "w_obiekcie": "nic", "korona": false, "wlosy": "rozpuszczone", "trzyma": "gwiazda",
           "kierunek": "lewo", "gwiazda_promienie": 8, "gwiazda_ogon": true, "gwiazda_kolor": "czerwony"},
 "pozycja": {"krag": "zewn", "kolejnosc": 7},
 "etykieta": {"locus": "8", "rodzaj": "Lz", "slowa": ["okala"]},
 "zrodlo": "Marek", "pewnosc": 2, "uwaga": ""}
```

`pozycja.kolejnosc` is the order of the label in the transliteration (ZL), usually in agreement with the order of the nymphs in the ring, but the zodiac has
an outer and an inner ring: fill in `krag` (`zewn`, `srod`, `wewn`). If a label does not fit any nymph or a nymph has no
label, write that in `uwaga`; an atom without a label can be added with `"etykieta": null`.

The default type follows from the kind of locus: `Lz`, `Ln` → nimfa (nymph); `Ls` → gwiazda (star); `Lc` → naczynie (vessel); `Lf` → fragment (fragment); `Lt` → rura (tube);
`L0` → obiekt (object). If it is something else (e.g. in the zodiac the animal in the centre), change `typ` to another one from the vocabulary.

## Where the images come from

Scans: Beinecke (collections.library.yale.edu, MS 408) or archive.org/details/voynich. Page names as in the transliteration:
`f70v2` is the second panel of the foldout leaf 70v. Zodiac: f70v2 Pisces, f70v1 Aries (dark), f71r Aries (light), f71v Taurus (light),
f72r1 Taurus (dark), f72r2 Gemini, f72r3 Cancer, f72v3 Leo, f72v2 Virgo, f72v1 Libra, f73r Scorpio, f73v Sagittarius.

## Draft from a vision model

The notebook `colab/Voynich_Atomy.ipynb` asks a model that sees images for a first, dirty description of the zodiac pages in the same schema
(`zrodlo: "vlm"`, `pewnosc: 1`). The numbers from the model (rays, petals) are uncertain: this is a draft to be corrected, not a result.

## Draft on your own GPU

The notebook `colab/Voynich_Atomy_GPU.ipynb` (A100) does the same without a paid API, with open models from Hugging Face: Molmo2
points at the figures and stars, geometry computes the rings and the clockwise order, Qwen3-VL describes
the crop around each figure. The result is `atoms_vision/<strona>.json` (`zrodlo: "vision"`) and a PNG with the point numbers: before
anyone corrects the features, they should check on the PNG whether number 7 really is the seventh label in the ring. The order from geometry assumes
that the transliteration numbers the labels from the top clockwise; where the number of points does not agree
with the number of labels, the `uwaga` field says so and the matching is a guess.

Merging the draft into `data/atoms`: `python scripts/merge_atoms.py results/lab/<przebieg>/atoms_vision` takes only the pages
on which the number of figures found agrees with the number of nymphs (±1), and does not overwrite pages with entries by people. Status: 6 zodiac
pages (f70v2, f70v1, f71r, f71v, f72r3, f73r) have a `vision` draft; the features in it are sometimes wrong (e.g. `w_obiekcie` for nymphs in tubs),
so when correcting, change `zrodlo` to your first name and raise `pewnosc`.

## Check and test

```
python scripts/make_atoms.py          # adds the missing page templates, does not overwrite filled-in ones
python -m voynich.lab.runner --theories atoms --no-council   # rebus test with controls
```

The test (`atoms`): for each pair (drawing feature, label feature) the mutual information against labels shuffled within
the page, with a correction for the number of pairs. Controls: the first glyph of the label planted according to a feature (must be detected) and features
shuffled between the atoms of a page (must not be). The test starts at ≥ 100 filled-in atoms with a label.
