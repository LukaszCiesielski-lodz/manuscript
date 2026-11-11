"""Theory: the scribes wrote sheet by sheet (bifolium by bifolium), not page after page in the bound book.

See voynich.lab.bifolio. card_choice found that the choices from the master card jump between
leaves and hardly between recto and verso of one leaf. Here the scribe's drift is used as a clock:
the two leaves of one sheet are far apart in the bound quire (f1 and f8); if they are alike, more
than other leaves of the quire written by the same hand in the same Currier language, the sheet was
written in one go before the quire was put together. Then: which pages of a sheet are alike (the
two that share a side of the flat sheet, or the two that face each other when it is folded), is
the quire a unit, and which sheet is closest in habit to which.
"""

from __future__ import annotations

import json
import random
import time
from collections import Counter

import numpy as np

from .. import bifolio as B
from .. import card as K
from .. import cardchoice as C
from ..config import LabConfig
from ..nomen2 import array_module
from ..results import TheoryResult
from .card_choice import manuscript_layout


def _majority(values) -> tuple:
    return Counter(values).most_common(1)[0][0]


def sheet_sides(pages: list, S: np.ndarray, permutations: int, seed: int) -> dict | None:
    """Pages of a sheet whose two leaves have one recto and one verso page each: similarity of recto and verso of a
    leaf, of the two pages on the outer side of the folded sheet (first recto, last verso: one side of the flat sheet),
    of the two facing inner pages (the other side), and of the two pairs on different sides and leaves. z of every
    kind against the 'different side and leaf' pairs; null: the four pages exchanged inside the sheet."""
    ix = {p: i for i, p in enumerate(pages)}
    by_leaf: dict = {}
    for n, f in pages:
        by_leaf.setdefault(n, []).append(f)
    quads = []
    for n, fs in by_leaf.items():
        m = B.conjugate(n)
        if n < m and m in by_leaf and len(fs) == 2 and len(by_leaf[m]) == 2:
            (ar, av), (br, bv) = sorted(fs), sorted(by_leaf[m])
            quads.append([ix[(n, ar)], ix[(n, av)], ix[(m, br)], ix[(m, bv)]])
    if len(quads) < 5:
        return None
    Q = np.array(quads)
    kinds = {"ta sama karta": [(0, 1), (2, 3)], "strona zewnętrzna arkusza": [(0, 3)], "strona wewnętrzna arkusza": [(1, 2)],
             "inna strona i karta": [(0, 2), (1, 3)]}

    def means(q: np.ndarray) -> dict:
        return {k: float(np.mean([S[q[:, a], q[:, b]] for a, b in v])) for k, v in kinds.items()}

    obs = means(Q)
    rng = np.random.default_rng(seed)
    null = {k: [] for k in kinds}
    for _ in range(permutations):
        q = np.stack([row[rng.permutation(4)] for row in Q])
        m = means(q)
        for k in kinds:
            null[k].append(m[k] - m["inna strona i karta"])
    out = {"sheets": len(quads), "mean": obs, "z": {}}
    for k in kinds:
        if k != "inna strona i karta":
            d = obs[k] - obs["inna strona i karta"]
            out["z"][k] = (d - float(np.mean(null[k]))) / (float(np.std(null[k])) or 1e-9)
    return out


def quire_unit(sheets: list, S: np.ndarray, stratum: dict, permutations: int, seed: int) -> dict:
    """Inside a stratum (section, hand, language): are sheets of one quire closer in habit than sheets of different
    quires, and how often is a sheet's nearest sheet in its own quire? Null: quire labels exchanged inside the stratum."""
    n = len(sheets)
    quire = np.array([s[0] for s in sheets])
    st = [stratum[s] for s in sheets]
    same_st = np.array([[st[i] == st[j] and i != j for j in range(n)] for i in range(n)])
    groups: dict = {}
    for i, s in enumerate(st):
        groups.setdefault(s, []).append(i)
    Sm = np.where(same_st, S, -np.inf)
    has = same_st.any(1)
    top = Sm.argmax(1)

    def stats(q: np.ndarray) -> tuple[float, float]:
        sq = q[:, None] == q[None, :]
        a, b = S[same_st & sq], S[same_st & ~sq]
        return (float(a.mean() - b.mean()) if len(a) and len(b) else 0.0, float(np.mean(q[has] == q[top[has]])) if has.any() else 0.0)

    obs = stats(quire)
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(permutations):
        q = quire.copy()
        for idx in groups.values():
            q[idx] = q[rng.permutation(idx)]
        null.append(stats(q))
    null = np.array(null)
    return {"excess": obs[0], "z": (obs[0] - float(null[:, 0].mean())) / (float(null[:, 0].std()) or 1e-9),
            "nearest_in_quire": obs[1], "nearest_expected": float(null[:, 1].mean()),
            "nearest_z": (obs[1] - float(null[:, 1].mean())) / (float(null[:, 1].std()) or 1e-9),
            "nearest": {sheets[i]: (sheets[int(top[i])], float(Sm[i, top[i]])) for i in range(n) if has[i]}}


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    gpu = array_module().__name__ == "cupy"
    pop = (16 if cfg.quick else cfg.card_prune_population) if gpu else (2 if cfg.quick else 4)
    perms = 200 if cfg.quick else 2000
    res = TheoryResult(
        theory="sheet_order",
        hypothesis="Skrybowie pisali arkuszami (bifoliami: dwie złączone karty, cztery strony naraz), zanim złożono składki, "
                   "a nie strona po stronie w oprawionej księdze.",
        method=("Zegarem jest dryf nawyków skryby w wyborach z karty matki (voynich.lab.cardchoice). Każdy wiersz przycięty do 8 "
                "wyborów (kolumna, kawałek), wybory wystandaryzowane w dziale; podobieństwo dwóch jednostek = średni iloczyn wektorów ich "
                "wierszy (nie zależy od liczby wierszy). Karty jednej składki, tej samej ręki i języka Curriera: czy dwie karty jednego "
                "arkusza (daleko od siebie w księdze, np. f1 i f8; bez arkusza środkowego) są podobniejsze niż inne pary kart składki, "
                f"i czy karty sąsiednie w księdze są podobniejsze; {perms} zamian kart w obrębie (składka, ręka, język). Potem: strony "
                "jednego arkusza (ta sama karta, ta sama strona rozłożonego arkusza, strony naprzeciw siebie), składka jako jednostka, "
                "najbliższy arkusz każdego arkusza. Kontrole na tekście pisanym znaną kartą przez skrybę z dryfem: arkuszami w losowej "
                "kolejności, strona po stronie w kolejności księgi, bez dryfu."),
        references=["Davis, Manuscript Studies 5 (2020): How many glyphs and how many scribes?", "Currier, Papers on the Voynich Manuscript (1976)",
                    "Pelling, The Curse of the Voynich (2006): misbound bifolia"])
    lay, ms, sections, lines, _ = manuscript_layout(False)
    leaf_of_line = [B.leaf_number(l.folio) for l in lines]
    sec_of_line = np.array([sections.index(l.section) for l in lines])
    leaves_all = sorted(set(leaf_of_line))
    leaf_stratum = {n: _majority((l.hand, l.language) for l, m in zip(lines, leaf_of_line) if m == n) for n in leaves_all}
    sheet_lines: dict = {}
    for i, n in enumerate(leaf_of_line):
        sheet_lines.setdefault(B.sheet(n), []).append(i)
    sheet_stratum = {s: _majority((lines[i].section, lines[i].hand, lines[i].language) for i in idx) for s, idx in sheet_lines.items()}
    chunks = K.chunk_inventory(ms)

    def measure(codes: np.ndarray) -> dict:
        X, valid = B.line_vectors(codes, lay, 8, cfg.seed)
        Z = B.standardise(X, valid, sec_of_line)
        leaves, S = B.unit_similarity(Z, valid, leaf_of_line)
        out = {"pairs": B.leaf_pair_test(leaves, S, leaf_stratum, perms, cfg.seed)}
        out["sheets"], out["S_sheets"] = B.unit_similarity(Z, valid, [B.sheet(n) for n in leaf_of_line])
        out["pages"], out["S_pages"] = B.unit_similarity(Z, valid, [(n, l.folio) for n, l in zip(leaf_of_line, lines)])
        return out

    # controls: a known card and a drifting scribe, three ways of writing
    r = random.Random(cfg.seed)
    by_quire: dict = {}
    for s in sheet_lines:
        by_quire.setdefault(s[0], []).append(s)
    order, truth = [], {}
    for q in by_quire:
        ss = by_quire[q][:]
        r.shuffle(ss)
        for s in ss:
            truth[s] = len(truth)
            order += sheet_lines[s]
    natural = list(range(len(lines)))
    ctl = {}
    for name, lo, strength in (("arkuszami", order, 0.3), ("strona po stronie", natural, 0.3), ("bez dryfu", natural, 0.0)):
        syn, true = B.synthetic_written(chunks, lay, lo, cfg.seed, strength=strength)
        codes, _ = C.parse_tokens(true, chunks, syn)
        ctl[name] = measure(codes)
    m = ctl["arkuszami"]
    S2 = m["S_sheets"].copy()
    np.fill_diagonal(S2, -np.inf)
    hit = float(np.mean([abs(truth[m["sheets"][i]] - truth[m["sheets"][j]]) == 1 for i, j in enumerate(S2.argmax(1))]))
    chance = 2 / len(m["sheets"])
    p = m["pairs"]
    res.control("tekst pisany arkuszami w losowej kolejności", "arkusz z ≥ 4, sąsiednie karty z < 2,5, najbliższy arkusz = sąsiad w czasie ≥ 30%",
                f"arkusz z = {p['sheet']['z']:.1f}, sąsiednie z = {p['neighbour']['z']:.1f}, najbliższy = sąsiad {hit:.0%} (losowo {chance:.0%})",
                p["sheet"]["z"] >= 4 and p["neighbour"]["z"] < 2.5 and hit >= 0.3)
    p = ctl["strona po stronie"]["pairs"]
    res.control("tekst pisany strona po stronie w kolejności księgi", "sąsiednie karty z ≥ 4, arkusz z < 2,5",
                f"sąsiednie z = {p['neighbour']['z']:.1f}, arkusz z = {p['sheet']['z']:.1f}", p["neighbour"]["z"] >= 4 and p["sheet"]["z"] < 2.5)
    p = ctl["bez dryfu"]["pairs"]
    res.control("tekst bez dryfu", "|z| < 2,5 (arkusz i sąsiednie karty)",
                f"arkusz z = {p['sheet']['z']:.1f}, sąsiednie z = {p['neighbour']['z']:.1f}", abs(p["sheet"]["z"]) < 2.5 and abs(p["neighbour"]["z"]) < 2.5)

    # the manuscript, on its own card
    card_tokens = ms[:6000] if cfg.quick else ms
    enc = K.Encoded(card_tokens, chunks, max_len=18)
    pr = K.prune(enc, chunks, cfg.card_columns, 1.0, pop, cfg.seed, log=(lambda s: print(s, flush=True)) if not cfg.quick else None)
    codes, _ = C.parse_tokens(pr["card"], chunks, ms)
    m = measure(codes)
    p = m["pairs"]
    sides = sheet_sides(m["pages"], m["S_pages"], perms, cfg.seed)
    qu = quire_unit(m["sheets"], m["S_sheets"], sheet_stratum, perms, cfg.seed)
    res.metrics.update({"pairs": p, "sides": sides, "quire": {k: v for k, v in qu.items() if k != "nearest"}, "card": pr["size"],
                        "controls": {k: v["pairs"] for k, v in ctl.items()}, "control_nearest_hit": hit})
    res.evidence.append(
        f"Karty jednej składki, tej samej ręki i języka ({p['pairs']['arkusz']} par kart jednego arkusza poza środkiem składki, "
        f"{p['pairs']['sąsiednie karty']} par kart sąsiednich z różnych arkuszy, {p['pairs']['inne']} innych par): karty jednego arkusza "
        f"podobniejsze od innych par o {p['sheet']['excess']:.2f} (z = {p['sheet']['z']:.1f}); karty sąsiednie w księdze o "
        f"{p['neighbour']['excess']:.2f} (z = {p['neighbour']['z']:.1f}).")
    if sides:
        res.evidence.append(f"Strony jednego arkusza ({sides['sheets']} arkuszy z czterema stronami tekstu), średnie podobieństwo: " + "; ".join(
            f"{k} {v:.2f}" + (f" (z = {sides['z'][k]:.1f})" if k in sides["z"] else "") for k, v in sides["mean"].items())
            + ". Strona zewnętrzna = pierwsza i ostatnia strona złożonego arkusza, czyli jedna strona arkusza rozłożonego na płasko.")
    res.evidence.append(
        f"Składka jako jednostka (arkusze tego samego działu, ręki i języka): arkusze jednej składki podobniejsze od arkuszy różnych "
        f"składek o {qu['excess']:.2f} (z = {qu['z']:.1f}); najbliższy arkusz leży w tej samej składce w {qu['nearest_in_quire']:.0%} "
        f"przypadków (losowo {qu['nearest_expected']:.0%}, z = {qu['nearest_z']:.1f}).")

    # the table of sheets and their nearest sheets
    def name(s) -> str:
        lo, hi = B.QUIRES[s[0]]
        a = lo + s[1]
        return f"f{a}–f{lo + hi - a}"

    out_dir = cfg.results_dir / "sheet_order"
    out_dir.mkdir(parents=True, exist_ok=True)
    md = ["# Arkusze rękopisu i ich najbliższe arkusze (dryf nawyków skryby jako zegar)\n",
          "Najbliższy = najpodobniejszy w wyborach z karty matki wśród arkuszy tego samego działu, ręki i języka Curriera.\n",
          "| arkusz | składka | dział | ręka | język | najbliższy arkusz | jego składka | podobieństwo |", "|---|---|---|---|---|---|---|---|"]
    js = []
    for s in sorted(qu["nearest"], key=lambda s: (B.QUIRES[s[0]][0], s[1])):
        t, v = qu["nearest"][s]
        sec, hand, lang = sheet_stratum[s]
        md.append(f"| {name(s)} | {s[0]} | {sec} | {hand} | {lang} | {name(t)} | {t[0]}{' (ta sama)' if t[0] == s[0] else ''} | {v:.2f} |")
        js.append({"sheet": name(s), "quire": s[0], "section": sec, "hand": hand, "language": lang, "nearest": name(t), "nearest_quire": t[0],
                   "similarity": v})
    (out_dir / "arkusze.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out_dir / "arkusze.json").write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
    res.artifacts += ["sheet_order/arkusze.md", "sheet_order/arkusze.json"]

    sz, nz = p["sheet"]["z"], p["neighbour"]["z"]
    base = f"Karty jednego arkusza: z = {sz:.1f}; karty sąsiednie w księdze: z = {nz:.1f}. "
    if cfg.quick:
        res.decide(None)
        res.summary = "Tryb szybki. " + base
    elif sz >= 4 and nz < 2.5:
        res.decide(True)
        res.summary = base + ("Dwie karty jednego arkusza, odległe w oprawionej księdze, mają te same nawyki skryby, a karty sąsiednie nie: "
                              "pisano arkuszami przed złożeniem składek.")
    elif nz >= 4 and sz < 2.5:
        res.decide(False)
        res.summary = base + "Podobne są karty sąsiednie w księdze, nie karty jednego arkusza: pisano strona po stronie w gotowej księdze."
    else:
        res.decide(None)
        res.summary = base + "Wynik między progami."
    res.caveats += ["Porównujemy tylko karty tej samej ręki i języka Curriera; ręce i języki same układają się arkuszami (Currier, Davis), "
                    "czego ten test celowo nie liczy.",
                    "Podobieństwo arkusza może też wynikać z treści wspólnej dla arkusza; dryf i treść dają tu ten sam ślad.",
                    "Pełnej kolejności pisania arkuszy nie odtwarzamy: na tekście kontrolnym uporządkowanie wzdłuż jednej linii zgadza się "
                    "z prawdą słabo (ρ 0,1–0,6); wiarygodny jest tylko najbliższy sąsiad (ok. 55% trafień na kontroli wobec 4% losowo).",
                    "Składki z rozkładanymi kartami (I, J, N, O, Q, S) mają nietypową budowę; para kart jednego arkusza liczy się tam tak samo."]
    res.seconds = time.time() - t0
    return res
