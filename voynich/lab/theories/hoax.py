"""Theory: the text is meaningless, produced by rules a 15th-century scribe could follow.

The strongest form of the "hoax" explanation is a recipe that reproduces every
measured property of the manuscript at once. Two generators are judged:

- v4: copy-and-modify (Timm & Schinner 2020) with edits and a word-shape
  grammar learned from the text;
- v5 "scribe's table": the same, but each word is chosen among a few
  candidates by habits a scribe could keep on one sheet (which word start
  follows which word end, what opens and closes a line, word length), with
  some fresh words from the shape table and heavier reuse of favourite words;
- v5 by section: the same, written section by section and dialect by dialect
  (Currier A/B), each with habits learned from that part, new words made of a
  known front and a known ending.

Fair play: every rule, edit and table is learned from the odd-numbered
folios; the yardstick and the line classifier use only the even ones.
"""

from __future__ import annotations

import time

from ... import corpus, eva, hoax, selfcite
from ..config import LabConfig
from ..results import TheoryResult

# Found by a local search on odd folios only (scorecard + classifier); the even folios never took part.
V5_PARAMS = dict(p_new=0.185, p_far=0.775, p_copy=0.047, p_same_column=0.559, gamma=3.364, length_gamma=0.736,
                 p_hot=0.235, hot_power=1.208, p_repeat=0.001, window=4, candidates=3)


def _folio_number(folio: str) -> int:
    digits = "".join(c for c in folio if c.isdigit())
    return int(digits) if digits else 0


def split_lines() -> tuple[list, list]:
    """Paragraph lines as glyph words, split into odd and even folios."""
    odd, even = [], []
    for l in corpus.load_voynich():
        if l.kind.startswith("P") and l.words:
            (odd if _folio_number(l.folio) % 2 else even).append([eva.glyphs(w) for w in l.words])
    return odd, even


def odd_runs() -> list[tuple[tuple, list]]:
    """Odd-folio paragraph lines as contiguous runs of one (section, Currier language), in manuscript order."""
    runs: list[tuple[tuple, list]] = []
    for l in corpus.load_voynich():
        if l.kind.startswith("P") and l.words and _folio_number(l.folio) % 2:
            key = (l.section, l.language)
            if not runs or runs[-1][0] != key:
                runs.append((key, []))
            runs[-1][1].append([eva.glyphs(w) for w in l.words])
    return runs


def generate_by_section(runs, params: dict, seed: int, min_words: int = 1500) -> list:
    """v5 run by run: each section and dialect written with habits learned from that part alone.

    A forger filling a herbal, then a 'stars' section in another hand, would not keep one
    style throughout; the manuscript does not either (Currier A and B). Parts with too
    little text borrow the habits of their dialect, or of the whole text.
    """
    pooled: dict = {}
    for key, lines in runs:
        for k in (key, ("*", key[1]), ("*", "*")):
            pooled.setdefault(k, []).extend(lines)
    models: dict = {}

    def model(key):
        k = next(k for k in (key, ("*", key[1]), ("*", "*")) if sum(map(len, pooled.get(k, []))) >= min_words)
        if k not in models:
            lines = pooled[k]
            words = [w for l in lines for w in l]
            models[k] = (selfcite.ScribeRules(lines), selfcite.EditModel(words), selfcite.WordGrammar(words, beta=5),
                         selfcite.WordMaker(words), [len(l) for l in lines])
        return models[k]

    out = []
    for i, (key, lines) in enumerate(runs):
        rules, edits, grammar, maker, lengths = model(key)
        n = sum(map(len, lines))
        gen = selfcite.generate_v5(lines[:2], n + sum(map(len, lines[:2])), lengths, rules, edits, grammar,
                                   seed=seed + i, maker=maker, **params)
        out.extend(gen[2:])
    return out


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    res = TheoryResult(
        theory="hoax",
        hypothesis="Tekst nie ma treści: wytworzono go regułami, które średniowieczny skryba mógł stosować z pamięci "
                   "albo z jednej kartki (kopiowanie ze zmianami, tabela kształtów słów, nawyki początku i końca wiersza).",
        method=("Dwa generatory (v4: kopiowanie ze zmianami; v5: skryba wybiera słowo spośród kilku kandydatów według "
                f"nawyków). Reguły uczone na nieparzystych foliach, sprawdzian na parzystych: {len(hoax.MEASURES)} miar "
                "w blokach po 4000 słów (zgodność = w granicach rozrzutu między blokami samego rękopisu, |z| ≤ 2) "
                "oraz klasyfikator wierszy (AUC 0,5 = nie odróżnia)."),
        references=["Timm & Schinner, Cryptologia 44 (2020)", "Rugg, Cryptologia 28 (2004)",
                    "Gaskell & Bowern, Gibberish after all? (2022)"])
    odd, even = split_lines()
    stick = hoax.yardstick(even)
    words = [w for l in odd for w in l]
    lengths = [len(l) for l in odd]
    n = 3 * hoax.BLOCK + 1000
    edits, grammar = selfcite.EditModel(words), selfcite.WordGrammar(words, beta=5)
    gens = {
        "v4": selfcite.generate(odd[:3], n, lengths, p_copy=0.22, window=8, p_far=0.05, seed=cfg.seed,
                                edits=edits, grammar=grammar),
        "v5": selfcite.generate_v5(odd[:3], n, lengths, selfcite.ScribeRules(odd), edits, grammar,
                                   seed=cfg.seed, **V5_PARAMS),
        "v5 działami": generate_by_section(odd_runs(), V5_PARAMS, cfg.seed),
    }

    # Controls: the odd folios are real text, so they must pass the bar; Latin must fail it.
    real_card = hoax.scorecard(odd, stick)
    res.control("prawdziwy tekst (foliały nieparzyste) mieści się w rozrzucie",
                "najwyżej 1 miara poza |z| ≤ 2", f"poza: {', '.join(hoax.misses(real_card)) or 'żadna'}",
                len(hoax.misses(real_card)) <= 1)
    auc_real = hoax.classifier_auc(even, odd, cfg.seed)
    res.control("klasyfikator: prawdziwe vs prawdziwe", "AUC ≤ 0,6", f"AUC = {auc_real:.3f}", auc_real <= 0.6)
    latin = corpus.load_reference("Latin")[:n]
    latin_lines = [[list(w) for w in latin[i:i + 9]] for i in range(0, len(latin), 9)]
    latin_misses = hoax.misses(hoax.scorecard(latin_lines, stick))
    res.control("łacina (tekst z treścią, inny alfabet) odpada", "co najmniej 5 miar poza", f"{len(latin_misses)} miar",
                len(latin_misses) >= 5)

    metrics = {"real_control": real_card, "auc_real": auc_real}
    best = None
    for name, gen in gens.items():
        card = hoax.scorecard(gen, stick)
        auc = hoax.classifier_auc(even, gen, cfg.seed)
        miss = hoax.misses(card)
        metrics[name] = {"card": card, "auc": auc, "misses": miss,
                         "sample": [".".join("".join(w) for w in l) for l in gen[10:16]]}
        res.evidence.append(f"Generator {name}: {len(hoax.MEASURES) - len(miss)}/{len(hoax.MEASURES)} miar w rozrzucie "
                            f"rękopisu; poza: " + (", ".join(f"{hoax.MEASURES[k]} (z = {card[k]['z']:+.1f})" for k in miss)
                                                   or "żadna") + f". Klasyfikator wierszy: AUC = {auc:.3f}.")
        if best is None or (len(miss), auc) < (len(metrics[best]["misses"]), metrics[best]["auc"]):
            best = name
    b = metrics[best]
    passed = not b["misses"] and b["auc"] <= 0.6
    res.metrics = metrics
    res.decide(True if passed else None)  # one failed recipe does not refute meaningless text in general
    res.summary = (f"Najlepszy generator ({best}) trafia w {len(hoax.MEASURES) - len(b['misses'])} z {len(hoax.MEASURES)} "
                   f"miar, klasyfikator odróżnia jego wiersze z AUC {b['auc']:.2f}. "
                   + ("Tekst bez treści, wytworzony prostymi regułami, jest nieodróżnialny od rękopisu w tych testach."
                      if passed else "Nie udało się jeszcze wytworzyć tekstu nieodróżnialnego od rękopisu; "
                                     "to nie obala hipotezy, pokazuje, czego prosty przepis nie odtwarza."))
    res.caveats += [
        "Parametry v5 dobrano wyszukiwaniem na tej samej karcie miar; uczciwość zapewnia tylko podział na foliały "
        "nieparzyste (reguły) i parzyste (sprawdzian).",
        "Reguły v5 są wyuczone z rękopisu: pokazują, że takie nawyki wystarczą, nie skąd skryba by je wziął.",
        "Klasyfikator widzi tylko n-gramy znaków w pojedynczych wierszach; mocniejszy model mógłby odróżnić więcej.",
    ]
    res.seconds = time.time() - t0
    return res
