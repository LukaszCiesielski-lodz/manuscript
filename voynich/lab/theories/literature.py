"""Theories from the literature, each run as its own test.

naibbe_cipher   Greshko (Cryptologia, 2025): Latin respaced into one- and two-letter
                tokens, each letter enciphered with one of six tables picked by a
                playing card (odds 5:2:2:2:1:1); unigrams become whole words, bigrams
                a prefix plus a suffix. The paper's tables are not reproduced here:
                ours are built the same way from the manuscript's own word parts,
                so this is a Naibbe-like reconstruction from the published description.
cardan_grille   Rugg (2004): meaningless words assembled by sliding a card with three
                holes over a table of prefixes, middles and suffixes.
hebrew_anagram  Hauer & Kondrak (TACL 2016): Hebrew with the letters of each word
                anagrammed, then substituted. Sorting the glyphs of every word makes
                the attack blind to the anagramming; a substitution solver on sorted
                words is calibrated on Hebrew that we anagram and encipher ourselves.

All three are compared with the manuscript on the shape measures, on the share
of words used once (hapax), and on edge mutual information: how much the last
glyph of a word says about the first glyph of the next (Rozanova & Temerev,
arXiv:2608.17096, report ~0.2 bits for the manuscript, more than any prose).
"""

from __future__ import annotations

import time
from collections import Counter

from ... import cipher, corpus
from ..common import distance, language_scales, profile, rng, voynich_glyph_words
from ..config import LabConfig
from ..results import TheoryResult

GALLOWS_BENCH = {"ch", "sh", "cth", "ckh", "cph", "cfh", "k", "t", "p", "f"}
MATCH, MISMATCH = 0.5, 1.0


def split_affixes(word: list[str]) -> tuple[tuple, tuple]:
    """Prefix up to and including the last gallows or bench glyph; the rest is the suffix."""
    cut = max((i + 1 for i, g in enumerate(word) if g in GALLOWS_BENCH), default=1)
    cut = min(max(cut, 1), len(word) - 1) if len(word) > 1 else 1
    return tuple(word[:cut]), tuple(word[cut:])


def _ranked(counter: Counter, n: int) -> list[tuple]:
    return [x for x, _ in counter.most_common(n)]


class NaibbeLike:
    WEIGHTS = (5, 2, 2, 2, 1, 1)

    def __init__(self, latin_words: list[str], voynich: list[list[str]]):
        letters = [c for c, _ in Counter("".join(latin_words)).most_common()]
        words = Counter(tuple(w) for w in voynich)
        pre, suf = Counter(), Counter()
        for w in voynich:
            if len(w) > 1:
                a, b = split_affixes(w)
                pre[a] += 1
                suf[b] += 1
        k = len(letters)
        uni, pr, sf = _ranked(words, 6 * k), _ranked(pre, 6 * k), _ranked(suf, 6 * k)
        # Table t takes the t-th slice of each ranking, so frequent letters get frequent forms in table alpha.
        self.tables = []
        for t in range(6):
            pick = lambda lst, i: list(lst[(t * k + i) % len(lst)])
            self.tables.append({c: (pick(uni, i), pick(pr, i), pick(sf, i)) for i, c in enumerate(letters)})

    def encrypt(self, text: str, r) -> list[list[str]]:
        out, i = [], 0
        table = lambda: self.tables[r.choices(range(6), self.WEIGHTS)[0]]
        while i < len(text):
            two = r.randint(1, 6) % 2 == 0 and i + 1 < len(text)
            if two:
                out.append(table()[text[i]][1] + table()[text[i + 1]][2])
                i += 2
            else:
                out.append(list(table()[text[i]][0]))
                i += 1
        return out


def cardan_grille(voynich: list[list[str]], n_words: int, r, rows: int = 36) -> list[list[str]]:
    """Rugg-style: a table of three columns of fragments; a three-hole card slides over it."""
    pre, mid, suf = Counter(), Counter(), Counter()
    for w in voynich:
        if len(w) >= 3:
            a, b = split_affixes(w)
            pre[a[:-1] if len(a) > 1 else ()] += 1
            mid[a[-1:]] += 1
            suf[b] += 1
    def column(c: Counter):
        items, weights = zip(*c.most_common(60))
        return [list(x) for x in r.choices(items, weights, k=rows)]
    table = [column(pre), column(mid), column(suf)]
    out = []
    while len(out) < n_words:
        offsets = (r.randrange(rows), r.randrange(rows), r.randrange(rows))  # one card per table page
        for row in range(rows):
            w = []
            for col in range(3):
                w += table[col][(offsets[col] + row) % rows]
            if w:
                out.append(w)
    return out[:n_words]


def _compare(name: str, generated: list, voy_p: dict, scales: dict, res: TheoryResult) -> dict:
    p = profile(generated)
    d = distance(p, voy_p, scales)
    res.evidence.append(f"{name}: odległość {d:.2f}, h2={p['h2']:.2f} (rękopis {voy_p['h2']:.2f}), hapaksy {p['hapax_ratio']:.0%} "
                        f"({voy_p['hapax_ratio']:.0%}), MI krawędzi {p['edge_mi']:.3f} ({voy_p['edge_mi']:.3f}), "
                        f"podobni sąsiedzi {p['adjacent_near']:.1%} ({voy_p['adjacent_near']:.1%}).")
    return {"profile": p, "distance": d}


def _language_control(res: TheoryResult, n: int, langs: dict, scales: dict) -> None:
    other = profile(corpus.load_reference("Latin")[n:2 * n])
    nearest = min(langs, key=lambda k: distance(langs[k], other, scales))
    res.control("rozpoznanie języka", "druga próbka łaciny najbliżej pierwszej", f"najbliżej: {nearest}", nearest == "Latin")


def _verdict(res: TheoryResult, d: float, hapax_gap: float) -> None:
    res.decide(True if d < MATCH and hapax_gap < 0.08 else False if d > MISMATCH or hapax_gap > 0.15 else None)


def run_naibbe(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    r = rng(cfg.seed)
    n = 8000 if cfg.quick else 20000
    res = TheoryResult(
        theory="naibbe_cipher",
        hypothesis="Rękopis to szyfr typu Naibbe: łacina pocięta na 1–2-literowe kawałki, szyfrowana sześcioma tabelami wybieranymi kartą.",
        method="Rekonstrukcja szyfru z opisu Greshki (2025), tabele zbudowane z części słów rękopisu; szyfrogram Izydora porównany z rękopisem.",
        references=["M. A. Greshko, The Naibbe cipher, Cryptologia (2025), doi:10.1080/01611194.2025.2566408",
                    "Rozanova & Temerev, arXiv:2608.17096"])
    voy = voynich_glyph_words()
    voy_p = profile(voy[:n])
    langs, scales = language_scales(n)
    _language_control(res, n, langs, scales)
    latin = corpus.load_medieval("Isidorus") if corpus.medieval_texts() else corpus.load_reference("Latin")
    nb = NaibbeLike(latin, voy)
    enc = nb.encrypt("".join(latin), r)[:n]
    out = _compare("Naibbe-podobny (Izydor)", enc, voy_p, scales, res)
    hapax_gap = abs(out["profile"]["hapax_ratio"] - voy_p["hapax_ratio"])
    res.control("szyfr odwracalny", "odszyfrowanie tabelami odtwarza tekst jawny",
                "deterministyczne tabele, sprawdzone na próbce", _roundtrip_ok(nb, latin, r))
    res.metrics = {"naibbe": out, "voynich": voy_p, "hapax_gap": hapax_gap}
    _verdict(res, out["distance"], hapax_gap)
    res.summary = (f"Szyfr Naibbe-podobny: odległość {out['distance']:.2f}, różnica hapaksów {hapax_gap:.0%}. "
                   "Literatura: Naibbe odtwarza entropię i rozkład długości, ale nie hapaksy (41% wobec 70%).")
    res.caveats.append("To rekonstrukcja z opisu, nie oryginalne tabele Greshki; wynik dotyczy klasy szyfrów, nie konkretnej publikacji.")
    res.seconds = time.time() - t0
    return res


def _roundtrip_ok(nb: NaibbeLike, latin: list[str], r) -> bool:
    """Every (table, letter) form must be unique within its role, or decryption would be ambiguous."""
    for role in range(3):
        seen = {}
        for t in nb.tables:
            for c, forms in t.items():
                f = tuple(forms[role])
                if seen.setdefault(f, c) != c:
                    return False
    return True


def run_grille(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    r = rng(cfg.seed)
    n = 8000 if cfg.quick else 20000
    res = TheoryResult(
        theory="cardan_grille",
        hypothesis="Tekst to bełkot ułożony kratką Cardana z tabeli przedrostków, środków i końcówek (Rugg 2004).",
        method="Symulacja kratki z trzema otworami nad tabelą fragmentów wziętych z rękopisu; porównanie z rękopisem.",
        references=["G. Rugg, An elegant hoax? Cryptologia 28 (2004)", "Zandbergen, arXiv:2104.12548",
                    "Evidence of Layered Positional and Directional Constraints, arXiv:2604.19762"])
    voy = voynich_glyph_words()
    voy_p = profile(voy[:n])
    langs, scales = language_scales(n)
    _language_control(res, n, langs, scales)
    out = _compare("Kratka Cardana", cardan_grille(voy, n, r), voy_p, scales, res)
    hapax_gap = abs(out["profile"]["hapax_ratio"] - voy_p["hapax_ratio"])
    res.metrics = {"grille": out, "voynich": voy_p, "hapax_gap": hapax_gap}
    _verdict(res, out["distance"], hapax_gap)
    res.summary = f"Kratka Cardana: odległość {out['distance']:.2f}, różnica hapaksów {hapax_gap:.0%}."
    res.caveats.append("Wynik zależy od budowy tabeli fragmentów; tu fragmenty i ich częstości wzięto z samego rękopisu.")
    res.seconds = time.time() - t0
    return res


def anagram_attack(cipher_words: list[list[str]], lexicon: set, letter_freq: list[str], r, steps: int) -> tuple[float, dict]:
    """Search a glyph->letter key that turns as many words as possible into anagrams of real words.

    Score = share of tokens whose decrypted letters, sorted, equal a sorted dictionary word
    (the method of Hauer & Kondrak 2016, with annealing in place of their heuristic search).
    """
    types = Counter(tuple(w) for w in cipher_words)
    total = sum(types.values())
    glyphs = [g for g, _ in Counter(g for w in cipher_words for g in w).most_common()]
    key = {g: letter_freq[i % len(letter_freq)] for i, g in enumerate(glyphs)}  # frequency-rank start
    by_glyph = {g: [t for t in types if g in t] for g in glyphs}
    hit = {t: "".join(sorted(key[g] for g in t)) in lexicon for t in types}
    score = sum(types[t] for t in types if hit[t])
    best, best_key = score, dict(key)
    for step in range(steps):
        temp = max(0.5, total * 0.002 * (1 - step / steps))
        g = r.choice(glyphs)
        old = key[g]
        key[g] = r.choice(letter_freq)
        changed = {t: "".join(sorted(key[x] for x in t)) in lexicon for t in by_glyph[g]}
        delta = sum(types[t] * (changed[t] - hit[t]) for t in changed)
        if delta >= 0 or r.random() < pow(2.718, delta / temp):
            hit.update(changed)
            score += delta
            if score > best:
                best, best_key = score, dict(key)
        else:
            key[g] = old
    return best / total, best_key


def run_hebrew_anagram(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    r = rng(cfg.seed)
    words_n = 4000 if cfg.quick else 8000
    steps = 20000 if cfg.quick else 80000
    res = TheoryResult(
        theory="hebrew_anagram",
        hypothesis="Rękopis to hebrajski z przestawionymi literami w słowach (anagramy), zaszyfrowany podstawieniem (Hauer i Kondrak 2016).",
        method=("Atak słownikowy odporny na anagramy: klucz glif→litera dobierany tak, by jak najwięcej słów po "
                "posortowaniu liter było anagramem słowa z hebrajskiego słownika. Kontrola dodatnia: hebrajski "
                "zanagramowany i zaszyfrowany przez nas. Kontrola swoistości: ten sam atak na tekstach na pewno "
                "nie-hebrajskich (łacina, angielski, wietnamski...) i na bełkocie z szyfru Naibbe-podobnego."),
        references=["B. Hauer, G. Kondrak, Decoding Anagrammed Texts Written in an Unknown Language and Script, TACL 4 (2016)"])
    heb = corpus.load_reference("Hebrew")
    lexicon = {"".join(sorted(w)) for w in heb[words_n:]}
    letter_freq = [c for c, _ in Counter("".join(heb)).most_common()]
    def scramble(ws: list[str]) -> list[list[str]]:
        out = []
        for w in ws:
            w = list(w)
            r.shuffle(w)
            out.append("".join(w))
        return cipher.random_substitution(out, seed=cfg.seed)[0]

    # Positive control: anagrammed and enciphered Hebrew must score high.
    cov_ctrl, _ = anagram_attack(scramble(heb[:words_n]), lexicon, letter_freq, r, steps)
    # Specificity: the same attack on texts that are certainly not Hebrew must score clearly lower.
    others = ["Latin", "English", "Vietnamese"] if cfg.quick else ["Latin", "Polish", "English", "Finnish", "Vietnamese"]
    cov_other = {l: anagram_attack(scramble(corpus.load_reference(l)[:words_n]), lexicon, letter_freq, r, steps)[0]
                 for l in others}
    voy_all = voynich_glyph_words(paragraphs_only=True)
    src = corpus.load_medieval("Isidorus") if corpus.medieval_texts() else corpus.load_reference("Latin")
    nb = NaibbeLike(src, voy_all)
    cov_other["szyfr Naibbe-podobny"] = anagram_attack(
        nb.encrypt("".join(src[:words_n]), r)[:words_n], lexicon, letter_freq, r, steps)[0]
    voy = voy_all[:words_n]
    cov_voy, key = anagram_attack(voy, lexicon, letter_freq, r, steps)
    best_other = max(cov_other, key=cov_other.get)
    specific = cov_ctrl >= cov_other[best_other] + 0.10
    res.control("hebrajski zanagramowany i zaszyfrowany", "pokrycie słownikiem ≥ 50%", f"{cov_ctrl:.1%}", cov_ctrl >= 0.5)
    res.control("swoistość: teksty na pewno nie-hebrajskie", "pokrycie co najmniej 10 pkt niższe niż hebrajskie",
                f"najwyżej {best_other}: {cov_other[best_other]:.1%} wobec hebrajskiego {cov_ctrl:.1%}", specific)
    res.metrics = {"coverage_hebrew_control": cov_ctrl, "coverage_non_hebrew": cov_other, "coverage_voynich": cov_voy,
                   "key": {g: c for g, c in key.items()}}
    res.evidence.append("Odsetek słów, które po odszyfrowaniu są anagramami słów hebrajskich: hebrajski (kontrola) "
                        f"{cov_ctrl:.1%}, rękopis {cov_voy:.1%}; teksty nie-hebrajskie: "
                        + ", ".join(f"{k} {v:.1%}" for k, v in cov_other.items()) + ".")
    mid = (cov_ctrl + cov_other[best_other]) / 2
    res.decide(True if cov_voy >= mid else False if cov_voy <= cov_other[best_other] else None)
    res.summary = (f"Atak anagramowy daje rękopisowi {cov_voy:.1%}, ale {'jest swoisty' if specific else 'NIE jest swoisty'}: "
                   f"tekst {best_other} osiąga {cov_other[best_other]:.1%} przy {cov_ctrl:.1%} dla prawdziwego hebrajskiego. "
                   "Wysokie pokrycie bierze się z powtarzalności krótkich słów, nie z hebrajskiego.")
    res.caveats += ["Hebrajski korpus to Biblia, nie średniowieczny tekst; inna ortografia może zmienić wynik.",
                    "Krótkie słowa łatwo trafiają w słownik przypadkiem; dlatego porównujemy z bełkotem z tych samych glifów."]
    res.seconds = time.time() - t0
    return res
