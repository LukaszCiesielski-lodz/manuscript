"""Cribs from the diagrams: circles whose number of words matches a known ordered list of the time.

f69v carries 28 radial words, as many as the 28 lunar mansions (Zandbergen notes their initials
are distributed like the initials of the mansion names); f67r1 has 12 radial words, f67v1 12
perimeter labels and f67r2 12 star labels, as many as the signs or the months. If the words are
those names under a letter cipher, one glyph-to-letter key aligns the circle with the list, for
some starting point and direction. The search: simulated annealing over the key and the
alignment: every start and direction of the list is tried and the key is fitted by hard EM
(edit-path alignment of decoded word and name, majority letter per glyph); score = mean similarity
(1 - normalised edit distance) between the decoded word and its name. Null: the same search against the same names in shuffled order (order is
what a crib adds; a key can always fit a bag of names a little). Positive control: the names
enciphered with a random homophonic key into Voynich-like glyphs, with a little noise.
"""

from __future__ import annotations

import math
import random
import statistics
import unicodedata
from typing import Sequence

from .. import corpus, eva

Word = tuple[str, ...]


def norm(name: str) -> str:
    s = unicodedata.normalize("NFD", name.lower())
    return "".join(ch for ch in s if ch.isalpha() and ch.isascii())


# Ordered lists. Mansions: Arabic forms (Wikipedia, Lunar station) and the Latin forms of Agrippa,
# De occulta philosophia II.33 (first name of each). Signs and months in the languages of the time.
LISTS: dict[str, list[str]] = {
    "mansions_arabic": ["sharatan", "butayn", "thuraya", "dabaran", "haqa", "hana", "dhira", "nathra", "tarf", "jabha",
                        "zubra", "sarfa", "awa", "simak", "ghafr", "zubana", "iklil", "qalb", "shawla", "naaim", "balda",
                        "saddhabih", "sadbula", "sadsuud", "sadakhbiya", "farghawal", "farghthani", "hut"],
    "mansions_latin": ["alnath", "allothaim", "achaomazon", "aldebaram", "alchatay", "alhanna", "aldimiach", "alnaza",
                       "archaam", "algelioche", "azobra", "alzarpha", "alhaire", "achureth", "agrapha", "azubene", "alchil",
                       "alchas", "allatha", "abnahaya", "abeda", "sadahacha", "zabadola", "sadabath", "sadalabra", "alpharg",
                       "alcharya", "albotham"],
    "signs_latin": ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius",
                    "capricornus", "aquarius", "pisces"],
    "signs_italian": ["ariete", "toro", "gemelli", "cancro", "leone", "vergine", "bilancia", "scorpione", "sagittario",
                      "capricorno", "aquario", "pesci"],
    "signs_arabic": ["hamal", "thawr", "jawza", "saratan", "asad", "sunbula", "mizan", "aqrab", "qaws", "jady", "dalw", "hut"],
    "signs_hebrew": ["tale", "shor", "teomim", "sartan", "arye", "betula", "moznayim", "akrav", "keshet", "gedi", "dli", "dagim"],
    "months_latin": ["ianuarius", "februarius", "martius", "aprilis", "maius", "iunius", "iulius", "augustus", "september",
                     "october", "november", "december"],
    "months_french": ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aoust", "septembre", "octobre",
                      "novembre", "decembre"],
    "months_occitan": ["genier", "febrier", "mars", "abril", "mai", "junh", "julhet", "agost", "setembre", "octobre",
                       "novembre", "decembre"],
    "months_catalan": ["gener", "febrer", "marc", "abril", "maig", "juny", "juliol", "agost", "setembre", "octubre",
                       "novembre", "desembre"],
    "months_italian": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre",
                       "ottobre", "novembre", "dicembre"],
    "months_german": ["jenner", "hornung", "merz", "april", "mai", "brachmonat", "heumonat", "augst", "herbstmonat",
                      "weinmonat", "wintermonat", "christmonat"],
}

# (folio, locus kinds, expected count, which lists)
DIAGRAMS = [
    ("f69v", ("Ri",), 28, ["mansions_arabic", "mansions_latin"]),
    ("f67r1", ("Ri",), 12, [k for k in LISTS if k.startswith(("signs", "months"))]),
    ("f67v1", ("L0",), 12, [k for k in LISTS if k.startswith(("signs", "months"))]),
    ("f67r2", ("Ls",), 12, [k for k in LISTS if k.startswith(("signs", "months"))]),
]


def diagram_words(folio: str, kinds: Sequence[str], lines=None) -> list[Word]:
    """The first word of every locus of the given kinds, in transliteration order (one item per locus)."""
    lines = corpus.load_voynich() if lines is None else lines
    return [tuple(eva.glyphs(l.words[0])) for l in lines if l.folio == folio and l.kind in kinds and l.words]


def lev(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def similarity(a: str, b: str) -> float:
    return 1.0 - lev(a, b) / max(1, len(a), len(b))


def aligned(names: Sequence[str], start: int, direction: int) -> list[str]:
    n = len(names)
    return [names[(start + direction * i) % n] for i in range(n)]


def _pairs(a: Sequence[str], b: str) -> list[tuple[int, int]]:
    """Positions (i in a, j in b) matched or substituted on an optimal edit path between decoded a and name b."""
    n, m = len(a), len(b)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
    out, i, j = [], n, m
    while i > 0 and j > 0:
        if d[i][j] == d[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            out.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif d[i][j] == d[i - 1][j] + 1:
            i -= 1
        else:
            j -= 1
    return out


def fit_key(words: Sequence[Word], targets: Sequence[str], iters: int = 8) -> tuple[float, dict]:
    """Best glyph -> letter key for fixed word/name pairs: start from proportional alignment, then alternate
    edit-path alignment and per-glyph majority letter (hard EM). Returns mean similarity and the key."""
    from collections import Counter, defaultdict
    counts: dict[str, Counter] = defaultdict(Counter)
    for w, x in zip(words, targets):
        for j, g in enumerate(w):
            counts[g][x[min(len(x) - 1, j * len(x) // max(1, len(w)))]] += 1
    glyphs = sorted({g for w in words for g in w})
    common = Counter(c for x in targets for c in x).most_common(1)[0][0]
    key = {g: (counts[g].most_common(1)[0][0] if counts[g] else common) for g in glyphs}
    for _ in range(iters):
        counts = defaultdict(Counter)
        for w, x in zip(words, targets):
            dec = [key[g] for g in w]
            for a, b in _pairs(dec, x):
                counts[w[a]][x[b]] += 1
        new = {g: (counts[g].most_common(1)[0][0] if counts[g] else key[g]) for g in glyphs}
        if new == key:
            break
        key = new
    score = sum(similarity("".join(key[g] for g in w), x) for w, x in zip(words, targets)) / max(1, len(words))
    return score, key


def attack(words: Sequence[Word], names: Sequence[str], steps: int = 0, seed: int = 0) -> dict:
    """Every start and direction of the list against the words, key fitted by hard EM; the best alignment wins."""
    names = [norm(x) for x in names]
    n = min(len(words), len(names))
    words = list(words)[:n]
    best = None
    for d in (1, -1):
        for st in range(len(names)):
            tgt = aligned(names, st, d)[:n]
            sc, key = fit_key(words, tgt)
            if best is None or sc > best[0]:
                best = (sc, key, st, d)
    s, k, st, d = best
    tgt = aligned(names, st, d)
    readings = ["".join(k[g] for g in words[i]) for i in range(n)]
    return {"score": s, "start": st, "direction": d, "key": k, "readings": list(zip(readings, tgt[:n]))}


def test(words: Sequence[Word], names: Sequence[str], steps: int, shuffles: int, seed: int) -> dict:
    """The attack against the true order and against shuffled orders of the same names."""
    obs = attack(words, names, steps, seed)
    r = random.Random(seed + 7)
    null = []
    for k in range(shuffles):
        perm = list(names)
        r.shuffle(perm)
        null.append(attack(words, perm, steps, seed + 100 + k)["score"])
    mean, sd = statistics.fmean(null), statistics.pstdev(null)
    p = (sum(1 for v in null if v >= obs["score"]) + 1) / (shuffles + 1)
    return {**obs, "null_mean": mean, "null_sd": sd, "z": (obs["score"] - mean) / sd if sd > 1e-12 else 0.0, "p": p}


def plant(names: Sequence[str], words_like: Sequence[Word], seed: int, noise: float = 0.1) -> list[Word]:
    """Positive control: the names written in Voynich-like glyphs under a random key (2 homophones for common letters),
    a share `noise` of the glyphs changed, starting at a random point of the list."""
    r = random.Random(seed)
    names = [norm(x) for x in names]
    glyphs = sorted({g for w in words_like for g in w})
    letters = sorted({c for x in names for c in x})
    pool = glyphs[:]
    r.shuffle(pool)
    key = {c: [pool[i % len(pool)]] for i, c in enumerate(letters)}
    for i, c in enumerate(letters[: max(0, len(pool) - len(letters))]):
        key[c].append(pool[len(letters) + i])
    start = r.randrange(len(names))
    out = []
    for x in aligned(names, start, 1):
        w = [r.choice(key[c]) for c in x]
        w = [r.choice(glyphs) if r.random() < noise else g for g in w]
        out.append(tuple(w))
    return out
