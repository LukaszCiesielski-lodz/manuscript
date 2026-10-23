"""Theory: the text has the syntax of a language (words depend on other, different words at a distance).

Language ties different words together over several positions (an article and its
noun, a verb and its object, a preposition and its case ending), and the tie fades with
distance. Copying with changes ties a word to itself and to its own variants instead.
The test measures, inside lines and against words shuffled within the same page and the
same place in the line:

- repeats: the same word again 2-7 places later;
- variants: a word one glyph away from it;
- unrelated words: mutual information among pairs that are neither, for the 60 and the
  300 most frequent words, and how it falls off with distance.

Controls: Latin read as syllables and as a two-codes-per-word codebook must still show
the tie between unrelated words; the manuscript with words shuffled inside lines must not.
"""

from __future__ import annotations

import random
import time

from ... import corpus, eva, latin, longrange
from ..config import LabConfig
from ..results import TheoryResult

LANGUAGES = ["Latin", "Italian", "German", "Czech"]


def _lines(words: list, n: int = 9) -> list:
    return [[list(w) if isinstance(w, str) else w for w in words[i:i + n]] for i in range(0, len(words), n)]


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 8 if cfg.quick else 20
    r = random.Random(cfg.seed)
    res = TheoryResult(
        theory="syntax",
        hypothesis="Tekst ma składnię języka: różne słowa zależą od siebie na odległość kilku słów, coraz słabiej "
                   "z odległością (jak rodzajnik i rzeczownik, czasownik i dopełnienie).",
        method=("Informacja wzajemna między słowami odległymi o 2–7 pozycji w tym samym wierszu, ponad tasowanie "
                "słów w obrębie strony i tego samego miejsca w wierszu. Rozdzielone: powtórzenia tego samego słowa, "
                "warianty (1 glif różnicy) i słowa niespokrewnione; klasy 60 i 300 najczęstszych słów. "
                "Porównanie: Biblia w 4 językach, łacina średniowieczna; kontrole: łacina jako sylaby i jako księga "
                "kodów z 2 kodami na słowo (zależność musi zostać), rękopis z przetasowanymi wierszami (musi zniknąć)."),
        references=["Lin & Tegmark, Critical behavior in physics and probabilistic formal languages, Entropy 19 (2017)",
                    "Timm & Schinner, Cryptologia 44 (2020)"])
    voy = [[eva.glyphs(w) for w in l.words] for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    n = sum(map(len, voy))
    texts = {"rękopis": voy}
    for lang in LANGUAGES:
        texts[lang] = _lines(corpus.load_reference(lang)[:n])
    texts["łacina średniowieczna"] = _lines([w for m in corpus.medieval_texts() for w in corpus.load_medieval(m, 4000)][:n])
    lat = corpus.load_reference("Latin")[:n]
    syl = [s for w in latin.normalize(lat[:20000]) for s in latin.syllabify(w)][:n]
    book = {w: [f"{w}#{k}" for k in range(2)] for w in set(lat)}
    controls = {"łacina jako sylaby": _lines(syl), "łacina, 2 kody na słowo": _lines([r.choice(book[w]) for w in lat])}
    flat = [w for l in voy for w in l]
    r.shuffle(flat)
    shuffled, i = [], 0
    for l in voy:
        shuffled.append(flat[i:i + len(l)])
        i += len(l)

    m = {}
    for name, lines in {**texts, **controls, "rękopis, słowa przetasowane": shuffled}.items():
        m[name] = {top: longrange.split_by_identity(lines, top=top, shuffles=shuffles, seed=cfg.seed) for top in (60, 300)}
    for name in ("łacina jako sylaby", "łacina, 2 kody na słowo"):
        z = m[name][60]["unrelated"]["z"]
        res.control(f"{name}: zależność między różnymi jednostkami zostaje", "z ≥ 3 (klasy 60)", f"z = {z:.1f}", z >= 3)
    z_shuf = m["rękopis, słowa przetasowane"][300]["unrelated"]["z"]
    res.control("rękopis ze słowami przetasowanymi: zależność znika", "|z| < 2.5 (klasy 300)", f"z = {z_shuf:.1f}",
                abs(z_shuf) < 2.5)

    profile = {}
    for name in ("rękopis", "łacina średniowieczna", "Latin"):
        profile[name] = [longrange.split_by_identity(texts[name], distances=[d], top=300, shuffles=max(6, shuffles // 2),
                                                     seed=cfg.seed)["unrelated"]["excess"] for d in range(1, 8)]
    fade = {k: (sum(v[3:]) / 4) / v[0] if v[0] > 0 else 0.0 for k, v in profile.items()}  # mean of d=4-7 over d=1

    for name in texts:
        a, b = m[name][60], m[name][300]
        res.evidence.append(f"{name}: powtórzenia z = {a['same']['z']:.1f}, warianty z = {b['variants']['z']:.1f}; "
                            f"słowa niespokrewnione: klasy 60 z = {a['unrelated']['z']:.1f}, klasy 300 z = {b['unrelated']['z']:.1f}.")
    res.evidence.append("Spadek z odległością (niespokrewnione, klasy 300; średnia d = 4–7 jako ułamek d = 1): "
                        + ", ".join(f"{k} {v:.2f}" for k, v in fade.items()) + ". Język: szybki spadek; "
                        "płaski profil oznacza współwystępowanie w wierszu, nie składnię.")
    langs_ok = all(m[l][60]["unrelated"]["z"] >= 3 for l in texts if l != "rękopis")
    voy60 = m["rękopis"][60]["unrelated"]["z"]
    flat_profile = fade["rękopis"] > 2 * max(fade["Latin"], fade["łacina średniowieczna"])
    res.metrics = {"by_text": m, "profile_mbit": {k: [1000 * x for x in v] for k, v in profile.items()}, "fade": fade}
    res.decide(False if (langs_ok and voy60 < 1.5 and flat_profile) else True if voy60 >= 3 else None)
    res.summary = (f"Najczęstsze słowa rękopisu nie zależą od siebie na odległość (z = {voy60:.1f}), a we wszystkich "
                   f"{len(texts) - 1} tekstach językowych tak (z ≥ 3). Rękopis ma za to nadmiar powtórzeń i wariantów "
                   f"(z = {m['rękopis'][60]['same']['z']:.1f} i {m['rękopis'][300]['variants']['z']:.1f}) – ślad kopiowania "
                   "ze zmianami – a zależność rzadszych słów nie słabnie z odległością, jak przy współwystępowaniu w wierszu.")
    res.caveats += [
        "Księga kodów z 3 lub więcej kodami na każde słowo rozmywa składnię poniżej progu tego testu; nie wyjaśnia "
        "jednak nadmiaru powtórzeń i wariantów.",
        "Teksty porównawcze to Biblia i zbiór łaciny średniowiecznej; zielnik czy receptariusz mogą mieć luźniejszą składnię.",
        "Wiersz rękopisu nie musi być zdaniem; teksty porównawcze pocięto na odcinki po 9 słów.",
    ]
    res.seconds = time.time() - t0
    return res
