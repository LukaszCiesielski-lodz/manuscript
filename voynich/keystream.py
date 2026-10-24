"""Word lengths as a key stream hidden in the text: the spaces carry the key, the glyph stream carries the message.

If the scribe placed spaces not between words but so that the sequence of word lengths (in glyphs
or in EVA characters) would tell the reader how to cut, shift or read the glyph stream, the EVA
"words" are not the units of the message and every word-level test so far measured the wrong
thing. This module enumerates a family of such keyed transforms and measures how word-like the
units they produce are: dependency between different units at a distance (language has it, the
manuscript's words do not), information between adjacent units, and vocabulary shape. A keyed
transform that turns the manuscript into a text with syntax, and does nothing of the kind to
gibberish of the same statistics, would be a lead.
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Sequence

Glyph = str
Line = list[list[Glyph]]          # a line as words of glyphs


@dataclass(frozen=True)
class Transform:
    name: str
    kind: str          # "cut" (new segmentation), "shift" (autokey substitution), "read" (reordering)
    key: str           # "glyphs", "chars", "none"
    param: int = 0


# ---------- key streams

def lengths(line: Line, key: str) -> list[int]:
    """Key stream of a line: word lengths in glyphs, or in EVA characters (ch, sh, cth count 2 and 3)."""
    if key == "chars":
        return [max(1, len("".join(w))) for w in line]
    return [max(1, len(w)) for w in line]


def key_variant(ks: list[int], variant: str, k: int, prev: list[int] | None) -> list[int]:
    if not ks:
        return ks
    if variant == "shift":                      # the length of word i cuts piece i+k (cyclic in the line)
        return ks[k % len(ks):] + ks[: k % len(ks)]
    if variant == "reverse":
        return ks[::-1]
    if variant == "previous":                   # the previous line's lengths cut this line
        return prev if prev else ks
    if variant == "first":                      # the first word's length repeated
        return [ks[0]] * len(ks)
    if variant == "sorted":
        return sorted(ks)
    if variant == "diff":                       # differences between neighbouring lengths (+1 .. )
        return [max(1, abs(a - b) + 1) for a, b in zip(ks, ks[1:] + ks[:1])]
    return ks


# ---------- transforms

def cut(stream: list[Glyph], sizes: Sequence[int]) -> list[list[Glyph]]:
    """Cut a glyph stream into pieces of the given sizes, repeating the sizes if they run short."""
    out, i, j = [], 0, 0
    sizes = [max(1, s) for s in sizes] or [1]
    while i < len(stream):
        n = sizes[j % len(sizes)]
        out.append(stream[i:i + n])
        i += n
        j += 1
    return out


def fixed_cut(stream: list[Glyph], width: int) -> list[list[Glyph]]:
    return cut(stream, [width])


def autokey_shift(line: Line, ks: list[int], order: dict[Glyph, int], alphabet: list[Glyph], where: str) -> Line:
    """Every glyph of word i shifted in the glyph alphabet by the key of word i (`where` = 'same'), of word i-1
    ('previous') or by the glyph's place in the word ('position')."""
    out = []
    n = len(alphabet)
    for i, w in enumerate(line):
        if where == "same":
            s = ks[i] if i < len(ks) else 0
        elif where == "previous":
            s = ks[i - 1] if i > 0 and i - 1 < len(ks) else 0
        else:
            s = None
        out.append([alphabet[(order[g] + (s if s is not None else j)) % n] if g in order else g for j, g in enumerate(w)])
    return out


def stride_read(stream: list[Glyph], step: int) -> list[Glyph]:
    """Read every `step`-th glyph, then the rest (a columnar transposition with `step` columns)."""
    step = max(1, step)
    return [stream[j] for s in range(step) for j in range(s, len(stream), step)]


def family() -> list[Transform]:
    out = [Transform("odstępy EVA (bez zmian)", "none", "none")]
    for key in ("glyphs", "chars"):
        for k in (1, 2, 3):
            out.append(Transform(f"cięcie: długości przesunięte o {k} ({key})", "cut", key, k))
        out += [Transform(f"cięcie: długości odwrócone ({key})", "cut", key, -1),
                Transform(f"cięcie: długości poprzedniego wiersza ({key})", "cut", key, -2),
                Transform(f"cięcie: długość pierwszego słowa ({key})", "cut", key, -3),
                Transform(f"cięcie: długości posortowane ({key})", "cut", key, -4),
                Transform(f"cięcie: różnice długości ({key})", "cut", key, -5),
                Transform(f"przesunięcie glifów o długość słowa ({key})", "shift", key, 0),
                Transform(f"przesunięcie glifów o długość poprzedniego słowa ({key})", "shift", key, 1)]
    out.append(Transform("przesunięcie glifów o miejsce w słowie", "shift", "none", 2))
    for w in (3, 4, 5, 6, 7):
        out.append(Transform(f"cięcie co {w} glifów (bez klucza)", "cut", "none", w))
    for s in (2, 3, 4, 5):
        out.append(Transform(f"czytanie co {s}. glif w wierszu (transpozycja)", "read", "none", s))
    return out


_VARIANT = {1: ("shift", 1), 2: ("shift", 2), 3: ("shift", 3), -1: ("reverse", 0), -2: ("previous", 0), -3: ("first", 0),
            -4: ("sorted", 0), -5: ("diff", 0)}


def apply(t: Transform, lines: Sequence[Line]) -> list[Line]:
    """The transform applied line by line (keys never cross a line except 'previous line')."""
    if t.kind == "none":
        return [list(map(list, l)) for l in lines]
    alphabet = sorted({g for l in lines for w in l for g in w})     # fixed order: a shift and its inverse agree
    order = {g: i for i, g in enumerate(alphabet)}
    out, prev = [], None
    for line in lines:
        ks = lengths(line, t.key) if t.key != "none" else []
        stream = [g for w in line for g in w]
        if t.kind == "cut":
            if t.key == "none":
                new = fixed_cut(stream, t.param)
            else:
                variant, k = _VARIANT[t.param]
                new = cut(stream, key_variant(ks, variant, k, prev))
        elif t.kind == "shift":
            new = autokey_shift(line, ks, order, alphabet, {0: "same", 1: "previous", 2: "position"}[t.param])
        else:
            new = cut(stride_read(stream, t.param), [len(w) for w in line])
        out.append(new)
        prev = ks
    return out


# ---------- measures of word-likeness

def adjacent_mi(lines: Sequence[Line]) -> float:
    """Mutual information (bits) between a unit and the next one in the line."""
    pairs = [(tuple(a), tuple(b)) for l in lines for a, b in zip(l, l[1:])]
    if not pairs:
        return 0.0
    n = len(pairs)
    cxy, cx, cy = Counter(pairs), Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    return sum(c / n * math.log2(c * n / (cx[a] * cy[b])) for (a, b), c in cxy.items())


def adjacent_mi_z(lines: Sequence[Line], shuffles: int = 20, seed: int = 1) -> dict:
    """Adjacent-unit MI as z against units shuffled within lines (removes vocabulary effects, keeps the line)."""
    rng = random.Random(seed)
    obs = adjacent_mi(lines)
    null = []
    for _ in range(shuffles):
        sh = []
        for l in lines:
            l = list(l)
            rng.shuffle(l)
            sh.append(l)
        null.append(adjacent_mi(sh))
    sd = statistics.pstdev(null) if len(null) > 1 else 0.0
    return {"value": obs, "null_mean": statistics.fmean(null), "z": (obs - statistics.fmean(null)) / sd if sd > 1e-12 else 0.0}


def vocabulary(lines: Sequence[Line]) -> dict:
    words = [tuple(w) for l in lines for w in l]
    c = Counter(words)
    n = max(1, len(words))
    return {"units": len(words), "types": len(c), "type_token_ratio": len(c) / n,
            "hapax_ratio": sum(1 for v in c.values() if v == 1) / n, "mean_length": sum(map(len, words)) / n}


def boundaries(lines: Sequence[Line]) -> list[set[int]]:
    """Per line: positions in the glyph stream after which a unit ends (the last one excluded)."""
    out = []
    for l in lines:
        b, i = set(), 0
        for w in l:
            i += len(w)
            b.add(i)
        b.discard(i)
        out.append(b)
    return out


def boundary_f1(a: Sequence[Line], b: Sequence[Line]) -> float:
    """Agreement of two segmentations of the same glyph streams."""
    tp = fp = fn = 0
    for x, y in zip(boundaries(a), boundaries(b)):
        tp += len(x & y)
        fp += len(y - x)
        fn += len(x - y)
    p = tp / max(1, tp + fp)
    r = tp / max(1, tp + fn)
    return 2 * p * r / max(1e-9, p + r)


def inverse_of(t: Transform, candidate: Transform) -> bool:
    """Does `candidate` undo the cipher made for `t` by `encipher`? (chars and glyphs coincide for plain letters)"""
    if t.kind == "cut":
        return candidate.kind == "cut" and candidate.param == t.param
    return candidate.kind == t.kind and candidate.param == t.param


def encipher(lines: Sequence[Line], t: Transform, seed: int = 1) -> list[Line]:
    """Positive control: a text whose spaces carry a key of this family. For a 'cut' transform with shifted
    lengths, the plain words' lengths are written into the spaces shifted the other way, so that applying
    `t` recovers the words; for a 'shift' transform the inverse shift is applied; for 'read' the inverse reading."""
    alphabet = sorted({g for l in lines for w in l for g in w})
    order = {g: i for i, g in enumerate(alphabet)}
    n = len(alphabet)
    out = []
    for line in lines:
        stream = [g for w in line for g in w]
        ks = [len(w) for w in line]
        if t.kind == "cut" and t.key == "glyphs" and t.param in (1, 2, 3):
            k = t.param
            cipher_ks = ks[-k % len(ks):] + ks[: -k % len(ks)] if ks else ks   # applying `shift k` to this restores ks
            out.append(cut(stream, cipher_ks))
        elif t.kind == "shift" and t.param == 0:
            # the cipher word i is shifted by -len(word i); lengths survive, so `shift same` undoes it
            out.append([[alphabet[(order[g] - len(w)) % n] for g in w] for w in line])
        elif t.kind == "shift" and t.param == 2:
            out.append([[alphabet[(order[g] - j) % n] for j, g in enumerate(w)] for w in line])
        elif t.kind == "read":
            step = t.param
            # inverse of stride_read: place the read-out back
            idx = [j for s in range(step) for j in range(s, len(stream), step)]
            inv = [None] * len(stream)
            for pos, j in enumerate(idx):
                inv[j] = stream[pos]
            out.append(cut(inv, ks))
        else:
            out.append([list(w) for w in line])
    return out
