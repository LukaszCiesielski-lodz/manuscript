"""Hypotheses as recipes: a small language the council's hounds write tests in.

A recipe says how to turn the manuscript into a candidate plaintext:

    {"name": "pi-Vigenere", "idea": "...",
     "scope": {"section": "herbal", "language": "A"},
     "steps": [{"op": "drop_glyphs", "glyphs": ["q"]},
               {"op": "keystream_shift", "key": "pi", "mode": "sub", "unit": "glyph", "restart": "line"}],
     "target": "Latin", "target_ops": ["drop_vowels"]}

After the steps, a substitution solver (cipher.solve, many-to-one, MDL score)
looks for the best symbol->letter key against the target language. Every step
also has a planting inverse, so each recipe gets its controls for free:

- positive: real target text is enciphered *through the recipe in reverse*
  (substitution, then each step's inverse); decoding must recover it;
- negative: the same recipe on meaningless text with the manuscript's
  statistics (self-citation generator v4) and on the manuscript with its
  words shuffled. The manuscript must do clearly better than both.

Score = (best negative-control gap) - (manuscript gap), in bits per symbol.
A scent trail (TROP) also needs the decoded text to be nearly as predictable as
genuine target-language text ("excess" < 0.6 bit/symbol), which noise never is.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass, field
from typing import Callable

from .. import cipher, corpus, eva

Word = list[str]
Line = tuple[str, list[Word]]  # (page, words)
FILLERS = [f"·{i}" for i in range(6)]  # symbols used only as padding in planted texts
CHUNK = 40  # pseudo-word length when a recipe removes word spaces (long, so few artificial boundaries)
REQUIRED = object()  # marks a parameter without a default
VOWELS = set("aeiouyáéíóúàèìòùâêîôûäëïöüåæøœąęıīūāēőűə")


# ---------- key streams

def _arctan_inv(x: int, scale: int) -> int:
    total = term = scale // x
    n, sign, x2 = 1, -1, x * x
    while term:
        term //= x2
        n += 2
        total += sign * (term // n)
        sign = -sign
    return total


def digits_of(name: str, n: int = 2000) -> list[int]:
    """Decimal digits (after the leading integer part is included) of a named constant or sequence."""
    scale = 10 ** (n + 10)
    if name == "pi":
        v = 4 * (4 * _arctan_inv(5, scale) - _arctan_inv(239, scale))
    elif name == "e":
        v, term, k = 0, scale, 0
        while term:
            v += term
            k += 1
            term //= k
    elif name == "sqrt2":
        v = math.isqrt(2 * scale * scale)
    elif name == "phi":
        v = (scale + math.isqrt(5 * scale * scale)) // 2
    elif name == "primes":
        s, k = "", 2
        while len(s) < n:
            if all(k % p for p in range(2, math.isqrt(k) + 1)):
                s += str(k)
            k += 1
        return [int(c) for c in s[:n]]
    elif name == "fibonacci":
        a, b, out = 0, 1, []
        for _ in range(n):
            out.append(a % 10)
            a, b = b, a + b
        return out
    else:
        raise ValueError(f"nieznany klucz: {name}")
    return [int(c) for c in str(v)[:n]]


def key_stream(spec: str, length: int | None) -> list[int]:
    """'pi', 'e', 'sqrt2', 'phi', 'primes', 'fibonacci', 'digits:1492', 'word:agla' (a=0..z=25)."""
    if spec.startswith("digits:"):
        key = [int(c) for c in spec[7:] if c.isdigit()]
    elif spec.startswith("word:"):
        key = [ord(c) - 97 for c in spec[5:].lower() if "a" <= c <= "z"]
    else:
        key = digits_of(spec, max(length or 0, 64) if length else 2000)
    key = key[:length] if length else key
    if not key:
        raise ValueError("pusty klucz")
    return key


# ---------- operations: apply (decode direction) and plant (encode direction, a right inverse)

@dataclass
class Ctx:
    rng: random.Random
    alphabet: list[str] | None = None  # fixed symbol order for shifts; None = take from the text
    spaceless: bool = False


@dataclass
class Op:
    name: str
    params: dict  # name -> (type, default, description)
    doc: str
    apply: Callable
    plant: Callable
    spaceless: bool = False


def _map_words(text, fn):
    return [(pg, [fn(w) for w in words]) for pg, words in text]


def _alphabet(text, ctx: Ctx) -> list[str]:
    if ctx.alphabet:
        return ctx.alphabet
    return sorted({g for _, ws in text for w in ws for g in w})


def _shift(text, p, ctx, sign):
    alpha = _alphabet(text, ctx)
    idx = {s: i for i, s in enumerate(alpha)}
    key = key_stream(p["key"], p.get("length"))
    k_mod = len(alpha)
    direction = (-1 if p.get("mode", "sub") == "sub" else 1) * sign
    pos, page_seen, out = 0, None, []
    for pg, words in text:
        if p.get("restart") == "line" or (p.get("restart") == "page" and pg != page_seen):
            pos = 0
        page_seen = pg
        new_words = []
        for w in words:
            if p.get("restart") == "word":
                pos = 0
            nw = []
            for g in w:
                if g in idx:
                    nw.append(alpha[(idx[g] + direction * key[pos % len(key)]) % k_mod])
                    if p.get("unit", "glyph") == "glyph":
                        pos += 1
                else:
                    nw.append(g)
            if p.get("unit", "glyph") == "word":
                pos += 1
            new_words.append(nw)
        out.append((pg, new_words))
    return out


def _drop_apply(text, p, ctx):
    nulls = set(p["glyphs"])
    return [(pg, [x for x in ([g for g in w if g not in nulls] for w in ws) if x]) for pg, ws in text]


def _drop_plant(text, p, ctx):
    nulls = list(p["glyphs"])
    def ins(w):
        out = []
        for g in w:
            while ctx.rng.random() < p.get("rate", 0.25):
                out.append(ctx.rng.choice(nulls))
            out.append(g)
        return out
    return _map_words(text, ins)


def _keep_every_apply(text, p, ctx):
    n, off = int(p["n"]), int(p.get("offset", 0))
    return [(pg, [x for x in ([g for i, g in enumerate(w) if i % n == off] for w in ws) if x]) for pg, ws in text]


def _keep_every_plant(text, p, ctx):
    n, off = int(p["n"]), int(p.get("offset", 0))
    def expand(w):
        out = []
        for g in w:
            block = [ctx.rng.choice(FILLERS) for _ in range(n)]
            block[off] = g
            out += block
        return out
    return _map_words(text, expand)


def _take_words_apply(text, p, ctx):
    n, off, i, out = int(p["every"]), int(p.get("offset", 0)), 0, []
    for pg, ws in text:
        keep = []
        for w in ws:
            if i % n == off:
                keep.append(w)
            i += 1
        out.append((pg, keep))
    return out


def _take_words_plant(text, p, ctx):
    n, off, out = int(p["every"]), int(p.get("offset", 0)), []
    for pg, ws in text:
        new = []
        for w in ws:
            block = [[ctx.rng.choice(FILLERS) for _ in range(ctx.rng.randint(2, 6))] for _ in range(n)]
            block[off] = w
            new += block
        out.append((pg, new))
    return out


def _group_apply(text, p, ctx):
    k = int(p.get("size", 2))
    return _map_words(text, lambda w: ["+".join(w[i:i + k]) for i in range(0, len(w), k)])


def _group_plant(text, p, ctx):
    k = int(p.get("size", 2))
    return _map_words(text, lambda w: [s for g in w for s in [g] + [ctx.rng.choice(FILLERS[:3]) for _ in range(k - 1)]])


def _rotate(text, p, ctx, sign):
    k = int(p.get("k", 1)) * sign
    return _map_words(text, lambda w: w[k % len(w):] + w[:k % len(w)] if w else w)


def _initials_apply(text, p, ctx):
    return [(pg, [[w[0] for w in ws if w]]) for pg, ws in text]


def _stream_plant(text, ctx, make_words):
    out = []
    for pg, ws in text:
        stream = [g for w in ws for g in w]
        out.append((pg, make_words(stream)))
    return out


def _initials_plant(text, p, ctx):
    return _stream_plant(text, ctx, lambda s: [[g] + [ctx.rng.choice(FILLERS) for _ in range(ctx.rng.randint(1, 4))] for g in s])


def _join_apply(text, p, ctx):
    return [(pg, [[g for w in ws for g in w]]) for pg, ws in text]


def _join_plant(text, p, ctx):
    def cut(s):
        out, i = [], 0
        while i < len(s):
            k = ctx.rng.randint(2, 7)
            out.append(s[i:i + k])
            i += k
        return out
    return _stream_plant(text, ctx, cut)


def _sort_plant(text, p, ctx):
    def shuffled(w):
        w = list(w)
        ctx.rng.shuffle(w)
        return w
    return _map_words(text, shuffled)


OPS = {o.name: o for o in [
    Op("reverse_words", {}, "Odwraca kolejność glifów w każdym słowie (pismo czytane od prawej).",
       lambda t, p, c: _map_words(t, lambda w: w[::-1]), lambda t, p, c: _map_words(t, lambda w: w[::-1])),
    Op("reverse_lines", {}, "Odwraca kolejność słów w każdym wierszu.",
       lambda t, p, c: [(pg, ws[::-1]) for pg, ws in t], lambda t, p, c: [(pg, ws[::-1]) for pg, ws in t]),
    Op("rotate", {"k": (int, 1, "o ile pozycji")}, "Przesuwa cyklicznie glify w słowie o k w lewo.",
       lambda t, p, c: _rotate(t, p, c, 1), lambda t, p, c: _rotate(t, p, c, -1)),
    Op("sort_glyphs", {}, "Sortuje glify w słowie (hipoteza anagramów; dodaj target_ops ['sort_letters']).",
       lambda t, p, c: _map_words(t, sorted), _sort_plant),
    Op("drop_glyphs", {"glyphs": (list, REQUIRED, "lista glifów EVA uznanych za puste, np. ['q','e']"),
                       "rate": (float, 0.25, "tylko dla kontroli: gęstość wstawiania")},
       "Usuwa wskazane glify jako znaki puste (nulle).", _drop_apply, _drop_plant),
    Op("keep_every", {"n": (int, REQUIRED, "co który glif"), "offset": (int, 0, "który z n (od 0)")},
       "W każdym słowie zostawia tylko glify na pozycjach i ≡ offset (mod n); reszta to wypełniacz.",
       _keep_every_apply, _keep_every_plant),
    Op("take_words", {"every": (int, REQUIRED, "co które słowo"), "offset": (int, 0, "które z n (od 0)")},
       "Zostawia co n-te słowo całego tekstu; pozostałe słowa to wypełniacz.", _take_words_apply, _take_words_plant),
    Op("group_glyphs", {"size": (int, 2, "ile glifów na jeden znak")},
       "Łączy kolejne grupy glifów w słowie w jeden znak (szyfr rozwlekły).", _group_apply, _group_plant),
    Op("keystream_shift", {"key": (str, REQUIRED, "pi | e | sqrt2 | phi | primes | fibonacci | digits:1492 | word:agla"),
                           "length": (int, None, "długość klucza (cyklicznie); puste = cały strumień"),
                           "mode": (str, "sub", "sub (odejmij cyfrę) | add"),
                           "unit": (str, "glyph", "glyph: cyfra na glif | word: jedna cyfra na słowo"),
                           "restart": (str, "none", "none | line | page | word: od kiedy klucz liczy się od początku")},
       "Przesuwa każdy glif w alfabecie glifów (posortowanym) o kolejną cyfrę klucza, jak szyfr Vigenère'a. "
       "Tak testuje się np. przypisanie cyfr rozwinięcia π do liter.",
       lambda t, p, c: _shift(t, p, c, 1), lambda t, p, c: _shift(t, p, c, -1)),
    Op("word_initials", {}, "Zostawia tylko pierwszy glif każdego słowa (akrostych); tekst bez spacji.",
       _initials_apply, _initials_plant, spaceless=True),
    Op("join_words", {}, "Usuwa spacje w wierszu (hipoteza: odstępy są fałszywe); tekst bez spacji.",
       _join_apply, _join_plant, spaceless=True),
]}

TARGET_OPS = {
    "drop_vowels": "usuwa samogłoski z języka docelowego (pismo spółgłoskowe, abdżad)",
    "sort_letters": "sortuje litery w słowach języka docelowego (do hipotez anagramowych)",
    "reverse_letters": "odwraca litery w słowach języka docelowego",
}
SECTIONS = ["herbal", "astronomical", "cosmological", "zodiac", "biological", "pharmaceutical", "stars", "text"]


def targets() -> list[str]:
    return corpus.reference_languages() + ["MedievalLatin", "BasqueNews"]


def dsl_doc() -> str:
    """Documentation of the language, generated from the code so the hounds always see what exists."""
    lines = ["Kroki (pole 'steps', wykonywane po kolei, każdy to obiekt z polem 'op'):"]
    for o in OPS.values():
        ps = ", ".join(f"{k}: {d[2]}" + (" (wymagane)" if d[1] is REQUIRED else f" (domyślnie {d[1]})" if d[1] is not None else "")
                       for k, d in o.params.items())
        lines.append(f"- {o.name}: {o.doc}" + (f" Parametry: {ps}." if ps else ""))
    lines.append("Operacje na języku docelowym (pole 'target_ops'): "
                 + "; ".join(f"{k}: {v}" for k, v in TARGET_OPS.items()))
    lines.append("Języki docelowe ('target'): " + ", ".join(targets()))
    lines.append("Zakres ('scope', opcjonalny): section ∈ " + ", ".join(SECTIONS)
                 + "; language ∈ A, B (dialekty Curriera).")
    lines.append("Uwaga: łamacz trigramowy nie radzi sobie z posortowanymi literami, więc przepisy z sort_glyphs zwykle "
                 "kończą się werdyktem 'metoda niewiarygodna' (kontrola dodatnia nie przechodzi).")
    lines.append("Na końcu zawsze działa łamacz szyfru podstawieniowego (wiele glifów może dać tę samą literę), "
                 "więc nie opisujesz przypisania glif→litera: łamacz szuka go sam.")
    return "\n".join(lines)


def validate(recipe: dict) -> list[str]:
    errs = []
    if not isinstance(recipe, dict):
        return ["przepis musi być obiektem JSON"]
    if recipe.get("target") not in targets():
        errs.append(f"nieznany target {recipe.get('target')!r}")
    for t in recipe.get("target_ops", []) or []:
        if t not in TARGET_OPS:
            errs.append(f"nieznana operacja target_ops {t!r}")
    sc = recipe.get("scope") or {}
    if sc.get("section") not in (None, *SECTIONS):
        errs.append(f"nieznany dział {sc.get('section')!r}")
    if sc.get("language") not in (None, "A", "B"):
        errs.append(f"nieznany język Curriera {sc.get('language')!r}")
    steps = recipe.get("steps")
    if not isinstance(steps, list) or len(steps) > 8:
        errs.append("'steps' musi być listą (najwyżej 8 kroków)")
        return errs
    for i, st in enumerate(steps):
        op = OPS.get(st.get("op") if isinstance(st, dict) else None)
        if not op:
            errs.append(f"krok {i}: nieznana operacja {st!r}")
            continue
        for k, (typ, default, _) in op.params.items():
            v = st.get(k, None if default is REQUIRED else default)
            if v is None and default is REQUIRED:
                errs.append(f"krok {i} ({op.name}): brak parametru {k}")
            elif v is not None and typ is int and not (isinstance(v, int) and 0 <= v <= 50):
                errs.append(f"krok {i} ({op.name}): {k} musi być liczbą całkowitą 0–50")
            elif v is not None and typ is list and not (isinstance(v, list) and v and all(isinstance(x, str) for x in v)):
                errs.append(f"krok {i} ({op.name}): {k} musi być niepustą listą glifów")
        if op.name in ("keep_every", "take_words") and int(st.get("n", st.get("every", 1)) or 0) < 2:
            errs.append(f"krok {i} ({op.name}): n/every musi być ≥ 2")
        if op.name in ("keep_every",) and int(st.get("offset", 0)) >= int(st.get("n", 1)):
            errs.append(f"krok {i}: offset musi być < n")
        if op.name == "take_words" and int(st.get("offset", 0)) >= int(st.get("every", 1)):
            errs.append(f"krok {i}: offset musi być < every")
        if op.name == "keystream_shift":
            try:
                key_stream(str(st.get("key")), st.get("length"))
            except Exception as e:
                errs.append(f"krok {i}: zły klucz ({e})")
            if st.get("mode", "sub") not in ("sub", "add") or st.get("unit", "glyph") not in ("glyph", "word") \
                    or st.get("restart", "none") not in ("none", "line", "page", "word"):
                errs.append(f"krok {i}: mode/unit/restart spoza dozwolonych wartości")
    return errs


def fingerprint(recipe: dict) -> str:
    core = {k: recipe.get(k) for k in ("scope", "steps", "target", "target_ops")}
    return hashlib.sha1(json.dumps(core, sort_keys=True).encode()).hexdigest()[:10]


# ---------- running a recipe

def apply_steps(text, recipe, ctx) -> list:
    for st in recipe["steps"]:
        text = OPS[st["op"]].apply(text, st, ctx)
        ctx.spaceless |= OPS[st["op"]].spaceless
    return text


def plant_steps(text, recipe, ctx) -> list:
    for st in reversed(recipe["steps"]):
        text = OPS[st["op"]].plant(text, st, ctx)
    return text


def as_words(text, spaceless: bool) -> list[Word]:
    words = [w for _, ws in text for w in ws if w]
    if not spaceless:
        return words
    stream = [g for w in words for g in w]
    return [stream[i:i + CHUNK] for i in range(0, len(stream), CHUNK)]


def target_words(recipe: dict) -> list[str]:
    t = recipe["target"]
    if t == "MedievalLatin":
        words = [w for n in corpus.medieval_texts() if n not in ("Isidorus", "Columella")
                 for w in corpus.load_medieval(n, 15000)]
    elif t == "BasqueNews":
        words = corpus.load_extra("basque_news")
    else:
        words = corpus.load_reference(t)
    for op in recipe.get("target_ops", []) or []:
        if op == "drop_vowels":
            words = ["".join(c for c in w if c not in VOWELS) for w in words]
        elif op == "sort_letters":
            words = ["".join(sorted(w)) for w in words]
        elif op == "reverse_letters":
            words = [w[::-1] for w in words]
    return [w for w in words if w]


def lines_to_text(lines, n_words: int, start: int = 0) -> list[Line]:
    """Take n_words words from `lines` (corpus.Line objects or (page, words) pairs), skipping `start` words."""
    out, seen, taken = [], 0, 0
    for l in lines:
        pg, ws = (l.folio, [eva.glyphs(w) for w in l.words]) if hasattr(l, "folio") else l
        if seen + len(ws) <= start:
            seen += len(ws)
            continue
        out.append((pg, ws))
        taken += len(ws)
        if taken >= n_words:
            break
    return out


@dataclass
class Settings:
    n_words: int = 3000
    steps: int = 15000
    restarts: int = 4
    slice: int = 0  # 0: first part of the scope; 1: the next part (confirmation run)


@dataclass
class Shared:
    """Texts every recipe run needs, built once per hunt."""
    voynich_lines: list
    null_lines: list  # generator v4 output as (page, words)
    seed: int = 7
    lm_cache: dict = field(default_factory=dict)


def _gap(text_test, text_train, ctx_flags: bool, model, s: Settings, seed: int) -> tuple[float, cipher.Solution, list]:
    test = as_words(text_test, ctx_flags)
    train = as_words(text_train, ctx_flags)
    sol = cipher.solve(test, model, restarts=s.restarts, steps=s.steps, seed=seed)
    return sol.bits - cipher.self_entropy(train, test), sol, test


def run_recipe(recipe: dict, shared: Shared, s: Settings) -> dict:
    """Score one recipe with its controls. Never raises: errors come back in the result."""
    out = {"fingerprint": fingerprint(recipe)}
    errs = validate(recipe)
    if errs:
        return {**out, "verdict": "błąd przepisu", "error": "; ".join(errs)}
    try:
        seed = shared.seed + 1000 * s.slice
        r = random.Random(seed)
        tw = target_words(recipe)
        key = (recipe["target"], tuple(recipe.get("target_ops") or []), any(OPS[x["op"]].spaceless for x in recipe["steps"]))
        spaceless = key[2]
        if key not in shared.lm_cache:
            lm_words = tw[20000:]
            if spaceless:
                stream = [c for w in lm_words for c in w]
                lm_words = [stream[i:i + CHUNK] for i in range(0, len(stream), CHUNK)]
            shared.lm_cache[key] = cipher.TrigramModel(lm_words)
        model = shared.lm_cache[key]
        n = s.n_words

        # The manuscript, restricted to the recipe's scope.
        sc = recipe.get("scope") or {}
        scope = [l for l in shared.voynich_lines if l.kind.startswith("P")
                 and (not sc.get("section") or l.section == sc["section"])
                 and (not sc.get("language") or l.language == sc["language"])]
        total = sum(len(l.words) for l in scope)
        if total < 600:
            return {**out, "verdict": "błąd przepisu", "error": f"za mało tekstu w zakresie ({total} słów)"}
        n_v = min(n, total // 2)
        start = s.slice * n_v if (s.slice + 1) * n_v <= total else 0
        v_test = lines_to_text(scope, n_v, start)
        v_train = [(l.folio, [eva.glyphs(w) for w in l.words]) for l in shared.voynich_lines
                   if l.kind.startswith("P")]
        test_pages = {pg for pg, _ in v_test}
        v_train = [x for x in v_train if x[0] not in test_pages]
        ctx = Ctx(r)
        dv_test, dv_train = apply_steps(v_test, recipe, ctx), apply_steps(v_train, recipe, Ctx(r))
        gap_v, sol_v, words_v = _gap(dv_test, dv_train, spaceless, model, s, seed)

        # Negative controls: meaningless text with the manuscript's statistics; manuscript with words shuffled.
        null_test, null_train = lines_to_text(shared.null_lines, n_v), lines_to_text(shared.null_lines, 4 * n_v, n_v)
        gap_null, _, _ = _gap(apply_steps(null_test, recipe, Ctx(r)), apply_steps(null_train, recipe, Ctx(r)),
                              spaceless, model, s, seed)
        flat = [w for _, ws in v_test for w in ws]
        r.shuffle(flat)
        shuf, i = [], 0
        for pg, ws in v_test:
            shuf.append((pg, flat[i:i + len(ws)]))
            i += len(ws)
        gap_shuf, _, _ = _gap(apply_steps(shuf, recipe, Ctx(r)), dv_train, spaceless, model, s, seed)

        # Positive control: real target text pushed through the recipe in reverse.
        letters = sorted({c for w in tw for c in w})
        symbols = [f"s{i:02d}" for i in range(max(len(letters), 26))]
        sub = dict(zip(letters, r.sample(symbols, len(letters))))
        def planted(words):
            text = [("ctl", [[sub[c] for c in w] for w in words[j:j + 9]]) for j in range(0, len(words), 9)]
            pctx = Ctx(r, alphabet=symbols)
            return apply_steps(plant_steps(text, recipe, pctx), recipe, Ctx(r, alphabet=symbols))
        p_test, p_train = planted(tw[:n_v]), planted(tw[n_v:4 * n_v])
        gap_pos, sol_p, words_p = _gap(p_test, p_train, spaceless, model, s, seed)
        truth = {v: k for k, v in sub.items()}
        hits = tot = 0
        for w in words_p:
            for g in w:
                # grouped symbols look like "s03+·1": the planted letter sits in the first known part
                real = next((truth[x] for x in g.split("+") if x in truth), None)
                if real is not None:
                    tot += 1
                    hits += sol_p.key.get(g) == real
        acc = hits / tot if tot else 0.0

        null_best = min(gap_null, gap_shuf)
        score = null_best - gap_v
        # Absolute check: a real decipherment reads about as predictably as genuine text in the target
        # language. A recipe that turns the text into noise can make the relative gap look good; this cannot.
        plain_bits = model.bits_per_symbol(as_words([("t", [list(w) for w in tw[:n_v]])], spaceless))
        excess = sol_v.bits - plain_bits
        if gap_pos > 0.35 or acc < 0.6:
            verdict = "metoda niewiarygodna"
        elif gap_v < 0.5 and score > 0.3 and excess < 0.6:
            verdict = "TROP"
        elif gap_v > 0.75 or score < 0.1:
            verdict = "obalony"
        else:
            verdict = "niejasny"
        return {**out, "verdict": verdict, "score": score, "gap_voynich": gap_v, "bits_voynich": sol_v.bits,
                "bits_plain_target": plain_bits, "excess_over_language": excess, "gap_null_generator": gap_null,
                "gap_null_shuffled": gap_shuf, "gap_positive": gap_pos, "positive_accuracy": acc,
                "words": len(words_v), "decoded": " ".join(sol_v.decrypt(words_v[:18]))}
    except Exception as e:  # a hound's recipe must never stop the hunt
        return {**out, "verdict": "błąd przepisu", "error": f"{type(e).__name__}: {e}"}
