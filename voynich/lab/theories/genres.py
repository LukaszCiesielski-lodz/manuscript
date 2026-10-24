"""Theory: a genuine medieval genre without syntax (litany, barbarous names) leaves the manuscript's signature.

Each genre text is measured like the manuscript: long-range dependency split into repeats,
one-glyph variants and unrelated words; word-length dynamics; and the shape measures of the
scorecard. A genre that lands where the manuscript lands, and where languages do not, would
be a candidate for what kind of text this is, meaningful or not.
"""

from __future__ import annotations

import time

from ... import corpus, eva, genres, hoax, lengths, longrange
from ..config import LabConfig
from ..results import TheoryResult


def _lines(words, n: int = 9):
    return [[list(w) for w in words[i:i + n]] for i in range(0, len(words), n)]


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    shuffles = 8 if cfg.quick else 20
    res = TheoryResult(
        theory="genres",
        hypothesis="Rękopis to tekst gatunku, który z natury nie ma składni między słowami: litania (stała rama, "
                   "zmienne imię) albo „imiona barbarzyńskie” ksiąg magicznych (ciągi bez znaczenia z echami i wariantami).",
        method=("Litania do Wszystkich Świętych (la.wikisource) i imiona z Ars Notoria i Liber Iuratus (Esoteric "
                "Archives) mierzone jak rękopis: zależność na odległość rozbita na powtórzenia, warianty i słowa "
                "niespokrewnione; dynamika długości słów (korelacja sąsiadów, DFA); miary kształtu z karty. "
                "Porównanie z rękopisem i łaciną."),
        references=["Ars Notoria (ed. Turner 1657; Esoteric Archives)", "Liber Iuratus Honorii (Esoteric Archives)",
                    "Litaniae Sanctorum"])
    voy = [[eva.glyphs(w) for w in l.words] for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    n = sum(map(len, voy))
    texts = {"rękopis": voy, "łacina (Biblia)": _lines(corpus.load_reference("Latin")[:n])}
    for name in genres.available():
        words = genres.load(name)
        if len(words) >= 600:
            texts[name] = _lines(words)
    if len(texts) == 2:
        res.evidence.append("Brak tekstów gatunkowych: uruchom scripts/fetch_genres.py.")
        res.decide(None)
        res.summary = "Pominięte: brak danych."
        res.seconds = time.time() - t0
        return res
    # Controls: a litany frame planted into the manuscript must raise the unrelated-word z; a litany with its
    # words shuffled must lose it.
    import random as _random
    frame = [[w if i % 3 else ["o", "r", "a"] for i, w in enumerate(l)] for l in voy]
    syn_frame = longrange.split_by_identity(frame, top=60, shuffles=shuffles, seed=cfg.seed)
    res.control("wszczepiona rama litanijna (co trzecie słowo stałe) daje zależność słów niespokrewnionych", "z ≥ 5",
                f"z = {syn_frame['unrelated']['z']:.1f}", syn_frame["unrelated"]["z"] >= 5)
    if "litany" in texts:
        rr = _random.Random(cfg.seed)
        lit = [w for l in texts["litany"] for w in l]
        rr.shuffle(lit)
        syn_sh = longrange.split_by_identity(_lines(lit), top=25, shuffles=shuffles, seed=cfg.seed)
        res.control("litania z przetasowanymi słowami traci zależność", "z < 3", f"z = {syn_sh['unrelated']['z']:.1f}",
                    syn_sh["unrelated"]["z"] < 3)
    stick = hoax.yardstick(voy)
    shape_keys = ["h2", "hapax_ratio", "vocab_density", "adjacent_near", "positional_rigidity", "type_token_ratio"]
    metrics = {}
    for name, lines in texts.items():
        top = 60 if sum(map(len, lines)) > 3000 else 25
        syn = longrange.split_by_identity(lines, top=top, shuffles=shuffles, seed=cfg.seed)
        dyn = lengths.describe(lengths.series([w for l in lines for w in l]), shuffles=shuffles, seed=cfg.seed)
        blocks = hoax.blocks(lines, size=min(hoax.BLOCK, max(600, sum(map(len, lines)) // 2)))
        m = hoax.measure(blocks[0]) if blocks else {}
        zs = {k: (m[k] - stick[k][0]) / stick[k][1] for k in shape_keys if k in m}
        metrics[name] = {"syntax": syn, "lengths": {k: dyn[k] for k in ("ac1", "updown", "dfa")}, "shape_z": zs,
                         "words": sum(map(len, lines))}
        res.evidence.append(f"{name} ({sum(map(len, lines))} słów): powtórzenia z = {syn['same']['z']:.1f}, warianty z = "
                            f"{syn['variants']['z']:.1f}, słowa niespokrewnione z = {syn['unrelated']['z']:.1f}; długości: "
                            f"korelacja sąsiadów {dyn['ac1']['value']:+.3f}, DFA {dyn['dfa']['value']:.3f}; kształt (z wobec "
                            "rękopisu): " + ", ".join(f"{hoax.MEASURES[k]} {z:+.1f}" for k, z in zs.items()) + ".")
    res.metrics = metrics
    v = metrics["rękopis"]
    like = [k for k, m in metrics.items() if k not in ("rękopis", "łacina (Biblia)")
            and m["syntax"]["unrelated"]["z"] < 2.5 and m["syntax"]["same"]["z"] > 3
            and abs(m["lengths"]["ac1"]["value"] - v["lengths"]["ac1"]["value"]) < 0.08]
    res.decide(None)
    res.summary = ("Gatunki o podpisie jak rękopis (brak składni, nadmiar powtórzeń, podobne długości sąsiadów): "
                   + (", ".join(like) if like else "żaden z badanych") + ". "
                   + "; ".join(f"{k}: niespokrewnione z = {m['syntax']['unrelated']['z']:.1f}, powtórzenia z = "
                               f"{m['syntax']['same']['z']:.1f}" for k, m in metrics.items()))
    res.caveats += ["Teksty gatunkowe są krótkie (litania ok. 1,5 tys. słów), więc ich z są z natury mniejsze.",
                    "Imiona wydobyto heurystycznie z wydań angielsko-łacińskich; część to zwykłe słowa.",
                    "Lingua Ignota Hildegardy (1011 słów, sam słownik) nie weszła: nie ma tekstu, tylko listę."]
    res.seconds = time.time() - t0
    return res
