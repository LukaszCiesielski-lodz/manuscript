"""Long-range dependency between words: does a word say anything about the word d positions later?

Mutual information between word classes at distance d, minus the same quantity after
shuffling words inside each page-sized chunk. The shuffle keeps each chunk's vocabulary
(topic, section, scribe), so what remains is due to word order alone. Language keeps
some of it at distances well beyond the neighbouring word (syntax, phrases, repeated
formulae); a scribe who remembers only the previous word cannot (a first-order chain
loses it within a few words).

Words are reduced to the `top` most frequent types plus one class for the rest, so texts
of equal size are measured on equal terms and the estimate is not swamped by rare words.
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter
from typing import Sequence

from .stats import is_near

CHUNK = 300  # words per "page" for the shuffle baseline
OTHER = "·"


def classes(words: Sequence, top: int = 60) -> list:
    ws = [tuple(w) if not isinstance(w, str) else w for w in words]
    keep = {w for w, _ in Counter(ws).most_common(top)}
    return [w if w in keep else OTHER for w in ws]


def mutual_information(seq: Sequence, d: int, chunk: int = CHUNK, line_ids: Sequence | None = None) -> float:
    """MI (bits) between items d apart, counting only pairs inside the same chunk (and line, if given)."""
    pairs = [(seq[i], seq[i + d]) for i in range(len(seq) - d) if i // chunk == (i + d) // chunk
             and (line_ids is None or line_ids[i] == line_ids[i + d])]
    n = len(pairs)
    pa, pb, pab = Counter(a for a, _ in pairs), Counter(b for _, b in pairs), Counter(pairs)
    return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in pab.items())


def shuffle_in_chunks(seq: Sequence, r: random.Random, chunk: int = CHUNK, slots: Sequence | None = None) -> list:
    """Shuffle inside each chunk; with `slots` (e.g. line-first / middle / line-last), only among equal slots."""
    out = list(seq)
    for i in range(0, len(seq), chunk):
        idx = list(range(i, min(i + chunk, len(seq))))
        groups: dict = {}
        for j in idx:
            groups.setdefault(slots[j] if slots else 0, []).append(j)
        for js in groups.values():
            vals = [seq[j] for j in js]
            r.shuffle(vals)
            for j, v in zip(js, vals):
                out[j] = v
    return out


def line_slots(lines: Sequence[Sequence]) -> tuple[list, list, list]:
    """Words of a text given as lines, with each word's slot (first / middle / last) and line number."""
    words, slots, ids = [], [], []
    for k, l in enumerate(lines):
        for i, w in enumerate(l):
            words.append(w)
            slots.append("f" if i == 0 else "l" if i == len(l) - 1 else "m")
            ids.append(k)
    return words, slots, ids


def excess_mi(words: Sequence, distances: Sequence[int] = tuple(range(1, 11)), top: int = 60,
              shuffles: int = 20, seed: int = 1, slots: Sequence | None = None,
              line_ids: Sequence | None = None) -> dict[int, dict[str, float]]:
    """For each distance: MI of the text, mean and sd of MI after shuffling within chunks, and the excess.

    slots     shuffle only among words in the same place of their line (keeps line-edge habits)
    line_ids  count only pairs inside one line (no dependency can come from the line above)
    """
    r = random.Random(seed)
    seq = classes(words, top)
    nulls = [shuffle_in_chunks(seq, r, slots=slots) for _ in range(shuffles)]
    out = {}
    for d in distances:
        real = mutual_information(seq, d, line_ids=line_ids)
        null = [mutual_information(s, d, line_ids=line_ids) for s in nulls]
        mean, sd = statistics.mean(null), statistics.stdev(null)
        out[d] = {"mi": real, "null": mean, "sd": sd, "excess": real - mean, "z": (real - mean) / sd if sd else 0.0}
    return out


def summary(curve: dict[int, dict[str, float]]) -> dict[str, float]:
    """Excess MI next door (d = 1), at mid range (d = 2-3) and far (d = 4-10), in millibits."""
    pick = lambda ds: 1000 * sum(curve[d]["excess"] for d in ds if d in curve)
    far = [d for d in range(4, 11) if d in curve]
    return {"d1": pick([1]), "d2_3": pick([2, 3]), "d4_10": pick(far),
            "z_far": sum(curve[d]["excess"] for d in far) / math.sqrt(sum(curve[d]["sd"] ** 2 for d in far) or 1)}


def split_by_identity(lines: Sequence[Sequence], distances: Sequence[int] = range(2, 8), top: int = 60,
                      shuffles: int = 20, seed: int = 1) -> dict[str, dict[str, float]]:
    """Excess MI inside lines, split into pairs of the same word and pairs of different words.

    The baseline shuffles words within page-sized chunks among the same place in the line
    (counted up to 3 from the start and from the end), so line-edge habits cannot leak in.
    Repeating a word a few places later is what copying does; different words that depend
    on each other at a distance is what syntax does. "same": excess share of pairs that
    repeat a (frequent) word; "different": excess MI (bits) among pairs of different words;
    "variants": excess share of pairs one edit apart; "unrelated": excess MI among pairs that
    are neither equal nor variants (what syntax adds, and copying with changes does not).
    """
    words, slots, ids = [], [], []
    for k, l in enumerate(lines):
        for i, w in enumerate(l):
            words.append(w)
            slots.append((min(i, 3), min(len(l) - 1 - i, 3)))
            ids.append(k)
    seq = classes(words, top)
    r = random.Random(seed)
    nulls = [shuffle_in_chunks(seq, r, slots=slots) for _ in range(shuffles)]

    def part(sq, d, same):
        pairs = [(sq[i], sq[i + d]) for i in range(len(sq) - d)
                 if ids[i] == ids[i + d] and i // CHUNK == (i + d) // CHUNK]
        if same:
            # How much likelier than chance the second word repeats the first (bits, as a log-ratio rate).
            n = len(pairs)
            pa, pb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
            hits = sum(a == b and a != OTHER for a, b in pairs)
            expected = sum(pa[a] * pb[a] for a in pa if a != OTHER) / n
            return (hits - expected) / n
        # Different words only: MI of the pairs with a != b, marginals taken from those pairs, so a text
        # full of repeats cannot push this part below zero by itself.
        pairs = [(a, b) for a, b in pairs if a != b]
        n = len(pairs)
        pa, pb, pab = Counter(a for a, _ in pairs), Counter(b for _, b in pairs), Counter(pairs)
        return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in pab.items())

    def near_rate(sq, d):
        # Excess share of pairs that are variants of each other (one glyph changed, added or dropped).
        pairs = [(sq[i], sq[i + d]) for i in range(len(sq) - d)
                 if ids[i] == ids[i + d] and i // CHUNK == (i + d) // CHUNK and sq[i] != OTHER and sq[i + d] != OTHER]
        return sum(a != b and is_near(tuple(a), tuple(b)) for a, b in pairs) / max(1, len(pairs))

    def far_words(sq, d):
        # MI among pairs of words that are neither equal nor variants: what syntax would add.
        pairs = [(sq[i], sq[i + d]) for i in range(len(sq) - d)
                 if ids[i] == ids[i + d] and i // CHUNK == (i + d) // CHUNK and sq[i] != sq[i + d]
                 and not (sq[i] != OTHER and sq[i + d] != OTHER and is_near(tuple(sq[i]), tuple(sq[i + d])))]
        n = len(pairs)
        pa, pb, pab = Counter(a for a, _ in pairs), Counter(b for _, b in pairs), Counter(pairs)
        return sum(c / n * math.log2(c * n / (pa[a] * pb[b])) for (a, b), c in pab.items())

    out = {}
    for name, fn in (("same", lambda sq, d: part(sq, d, True)), ("different", lambda sq, d: part(sq, d, False)),
                     ("variants", near_rate), ("unrelated", far_words)):
        ex, var = 0.0, 0.0
        for d in distances:
            null = [fn(sq, d) for sq in nulls]
            ex += fn(seq, d) - statistics.mean(null)
            var += statistics.stdev(null) ** 2
        out[name] = {"excess": ex, "z": ex / math.sqrt(var) if var else 0.0}
    return out

