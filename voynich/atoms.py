"""The drawings taken apart into atoms, each tied to the label written beside it.

A rebus, if there is one, lives in the pair drawing–label: the paragraphs do not cite the
labels of their page (theory `labels`) and pages showing the same plant share no words
(theory `plant_pairs`). So the ontology is built around the 1014 label words (loci L*): one
record per drawn thing, with observable features only (counts, shapes, colours), the label
copied from the transliteration, the annotator's name and their confidence. Interpretation
("this is sage") is kept out of the records.

Files: data/atoms/vocab.json (controlled vocabulary: atom types and their features),
data/atoms/<folio>.json (one page per file, so several people can work without conflicts).
Templates are generated from the transliteration; people fill the `cechy` dicts.
"""

from __future__ import annotations

import json
import re
import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from . import corpus, eva

ATOMS_DIR = corpus.DATA / "atoms"
VOCAB_FILE = ATOMS_DIR / "vocab.json"
LABEL_KINDS = ("Lz", "Lf", "L0", "Ls", "Ln", "Lt", "Lc")
KIND_TYPES = {"Lz": "nimfa", "Ln": "nimfa", "Ls": "gwiazda", "Lc": "naczynie", "Lf": "fragment", "Lt": "rura", "L0": "obiekt"}
GALLOWS = {"t", "k", "p", "f", "cth", "ckh", "cph", "cfh"}
LABEL_FEATURES = ("pierwszy", "drugi", "ostatni", "dlugosc", "gallows", "prefiks2")
CONFIDENCE = (1, 2, 3)   # 1 = guess, 2 = fairly sure, 3 = certain


@dataclass
class Atom:
    page: str
    section: str
    id: str
    typ: str
    cechy: dict = field(default_factory=dict)
    pozycja: dict = field(default_factory=dict)
    etykieta: dict | None = None
    zrodlo: str = ""
    pewnosc: int | None = None
    uwaga: str = ""

    @property
    def words(self) -> list[str]:
        return list(self.etykieta.get("slowa") or []) if self.etykieta else []

    @property
    def filled(self) -> bool:
        return any(v is not None for v in self.cechy.values())

    def record(self) -> dict:
        return {"id": self.id, "typ": self.typ, "cechy": dict(self.cechy), "pozycja": dict(self.pozycja),
                "etykieta": dict(self.etykieta) if self.etykieta else None, "zrodlo": self.zrodlo,
                "pewnosc": self.pewnosc, "uwaga": self.uwaga}


# ---------- vocabulary and validation

def load_vocab(path: Path = VOCAB_FILE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _value_ok(value, spec) -> bool:
    if value is None:
        return True
    if spec == "bool":
        return isinstance(value, bool)
    if spec == "int":
        return isinstance(value, int) and not isinstance(value, bool) and value >= 0
    return isinstance(value, str) and value in spec


def validate(page: dict, vocab: dict, name: str = "") -> list[str]:
    """Problems in one page file, each naming the file and the atom. Empty list = valid."""
    where = name or page.get("strona", "?")
    errors = []
    if not isinstance(page.get("strona"), str) or not isinstance(page.get("atomy"), list):
        return [f"{where}: plik musi mieć pola 'strona' (tekst) i 'atomy' (lista)"]
    types = vocab["typy"]
    seen = set()
    for a in page["atomy"]:
        aid = a.get("id", "?")
        if aid in seen:
            errors.append(f"{where}/{aid}: powtórzony id")
        seen.add(aid)
        typ = a.get("typ")
        if typ not in types:
            errors.append(f"{where}/{aid}: nieznany typ '{typ}' (dozwolone: {', '.join(types)})")
            continue
        specs = types[typ]["cechy"]
        for key, value in (a.get("cechy") or {}).items():
            if key not in specs:
                errors.append(f"{where}/{aid}: nieznana cecha '{key}' typu {typ} (dozwolone: {', '.join(specs)})")
            elif not _value_ok(value, specs[key]):
                errors.append(f"{where}/{aid}: cecha '{key}' ma wartość {value!r}, dozwolone: {specs[key]}")
        p = a.get("pewnosc")
        if p is not None and p not in CONFIDENCE:
            errors.append(f"{where}/{aid}: pewnosc musi być 1, 2 albo 3 (jest {p!r})")
        lab = a.get("etykieta")
        if lab is not None and not (isinstance(lab, dict) and isinstance(lab.get("slowa"), list)):
            errors.append(f"{where}/{aid}: etykieta musi być null albo {{'locus': ..., 'slowa': [...]}}")
    return errors


# ---------- templates from the transliteration

def label_lines(lines: Sequence[corpus.Line] | None = None) -> list[corpus.Line]:
    lines = corpus.load_voynich() if lines is None else lines
    return [l for l in lines if l.kind in LABEL_KINDS and l.words]


def templates(lines: Sequence[corpus.Line] | None = None, vocab: dict | None = None) -> dict[str, dict]:
    """One page dict per folio with labels: one atom per label locus, features empty, in locus order."""
    vocab = vocab or load_vocab()
    pages: dict[str, dict] = {}
    for l in label_lines(lines):
        page = pages.setdefault(l.folio, {"strona": l.folio, "dzial": l.section, "jezyk": l.language, "atomy": []})
        n = len(page["atomy"]) + 1
        typ = KIND_TYPES[l.kind]
        page["atomy"].append({"id": f"{l.folio}-{n:02d}", "typ": typ,
                              "cechy": {k: None for k in vocab["typy"][typ]["cechy"]},
                              "pozycja": {"krag": None, "kolejnosc": n},
                              "etykieta": {"locus": l.locus, "rodzaj": l.kind, "slowa": list(l.words)},
                              "zrodlo": "", "pewnosc": None, "uwaga": ""})
    return pages


def write_templates(out_dir: Path = ATOMS_DIR, lines: Sequence[corpus.Line] | None = None,
                    overwrite: bool = False) -> tuple[list[str], list[str]]:
    """Write page files; an existing file is kept (someone may have filled it) unless overwrite."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written, kept = [], []
    for folio, page in templates(lines).items():
        path = out_dir / f"{folio}.json"
        if path.exists() and not overwrite:
            kept.append(folio)
            continue
        path.write_text(json.dumps(page, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(folio)
    return written, kept


# ---------- loading

def page_files(folder: Path = ATOMS_DIR) -> list[Path]:
    return sorted(p for p in folder.glob("f*.json"))


def load(folder: Path = ATOMS_DIR, section: str | None = None, vocab: dict | None = None,
         strict: bool = True) -> list[Atom]:
    """Every atom of every page file, validated against the vocabulary."""
    vocab = vocab or load_vocab()
    atoms, errors = [], []
    for path in page_files(folder):
        page = json.loads(path.read_text(encoding="utf-8"))
        errors += validate(page, vocab, path.name)
        if section and page.get("dzial") != section:
            continue
        for a in page["atomy"]:
            if a.get("typ") not in vocab["typy"]:
                continue
            atoms.append(Atom(page["strona"], page.get("dzial", ""), a["id"], a["typ"], dict(a.get("cechy") or {}),
                              dict(a.get("pozycja") or {}), a.get("etykieta"), a.get("zrodlo", ""), a.get("pewnosc"),
                              a.get("uwaga", "")))
    if errors and strict:
        raise ValueError("Błędy w data/atoms:\n  " + "\n  ".join(errors[:30]))
    return atoms


def filled(atoms: Sequence[Atom]) -> list[Atom]:
    """Atoms someone has described (at least one feature set) that carry a label."""
    return [a for a in atoms if a.filled and a.words]


# ---------- label features

def features(words: Sequence[str]) -> dict:
    """Observable features of a label (its first word): initial, second and final glyph, length, gallows, prefix."""
    g = eva.glyphs(words[0]) if words else []
    return {"pierwszy": g[0] if g else "", "drugi": g[1] if len(g) > 1 else "", "ostatni": g[-1] if g else "",
            "dlugosc": len(g), "gallows": any(x in GALLOWS for x in g), "prefiks2": "".join(g[:2])}


# ---------- agreement between annotators

def kappa(a: Sequence, b: Sequence) -> float:
    """Cohen's kappa of two categorical annotations of the same items (1 = perfect, 0 = chance)."""
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if not pairs:
        return float("nan")
    n = len(pairs)
    po = sum(1 for x, y in pairs if x == y) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return 1.0 if pe >= 1 - 1e-12 else (po - pe) / (1 - pe)


def agreement(a: Sequence[Atom], b: Sequence[Atom]) -> dict[str, tuple[float, int]]:
    """Per feature (typ.cecha): kappa and the number of atoms both annotators described."""
    by_id = {x.id: x for x in b}
    rows: dict[str, tuple[list, list]] = defaultdict(lambda: ([], []))
    for x in a:
        y = by_id.get(x.id)
        if not y or y.typ != x.typ:
            continue
        for k, v in x.cechy.items():
            w = y.cechy.get(k)
            if v is not None and w is not None:
                rows[f"{x.typ}.{k}"][0].append(v)
                rows[f"{x.typ}.{k}"][1].append(w)
    return {k: (kappa(xs, ys), len(xs)) for k, (xs, ys) in rows.items()}


# ---------- the rebus test: does any drawn feature predict any label feature?

def mutual_information(xs: Sequence, ys: Sequence) -> float:
    """MI in bits between two categorical sequences of equal length."""
    n = len(xs)
    if n == 0:
        return 0.0
    cx, cy, cxy = Counter(xs), Counter(ys), Counter(zip(xs, ys))
    return sum(c / n * math.log2(c * n / (cx[x] * cy[y])) for (x, y), c in cxy.items())


def feature_table(atoms: Sequence[Atom]) -> dict[str, list[tuple[str, object, dict]]]:
    """typ.cecha -> [(page, value, label features)] over atoms where the feature is set."""
    table: dict[str, list] = defaultdict(list)
    for a in atoms:
        if not a.words:
            continue
        lf = features(a.words)
        for k, v in a.cechy.items():
            if v is not None:
                table[f"{a.typ}.{k}"].append((a.page, v, lf))
    return table


def pair_scan(atoms: Sequence[Atom], shuffles: int = 2000, seed: int = 0, min_n: int = 30,
              within_page: bool = True) -> list[dict]:
    """Every (drawn feature, label feature) pair: MI against labels shuffled among atoms of the same page."""
    r = random.Random(seed)
    rows = []
    table = feature_table(atoms)
    for key, items in table.items():
        if len(items) < min_n:
            continue
        pages = [p for p, _, _ in items]
        values = [v for _, v, _ in items]
        groups: dict[str, list[int]] = defaultdict(list)
        for i, p in enumerate(pages):
            groups[p if within_page else "all"].append(i)
        for lf in LABEL_FEATURES:
            labels = [f[lf] for _, _, f in items]
            obs = mutual_information(values, labels)
            null = []
            for _ in range(shuffles):
                perm = labels[:]
                for idx in groups.values():
                    vals = [labels[i] for i in idx]
                    r.shuffle(vals)
                    for i, v in zip(idx, vals):
                        perm[i] = v
                null.append(mutual_information(values, perm))
            mean, sd = statistics.fmean(null), statistics.pstdev(null)
            z = (obs - mean) / sd if sd > 1e-12 else 0.0
            hits = sum(1 for v in null if v >= obs)
            # Beyond the reach of the permutations (no null value as large) the normal tail of z stands in,
            # so a Bonferroni correction over many pairs is not capped at 1/(shuffles+1).
            p = (hits + 1) / (shuffles + 1) if hits else min((hits + 1) / (shuffles + 1), 0.5 * math.erfc(z / math.sqrt(2)))
            rows.append({"cecha": key, "etykieta": lf, "n": len(items), "mi": obs, "null_mean": mean, "z": z, "p": p})
    n_pairs = max(1, len(rows))
    for row in rows:
        row["p_adj"] = min(1.0, row["p"] * n_pairs)
    return sorted(rows, key=lambda d: -d["z"])


def significant(row: dict, z_min: float = 4.0) -> bool:
    """A pair counts only when it survives the correction over all pairs and stands well clear of the null."""
    return row["p_adj"] < 0.05 and row["z"] >= z_min


# ---------- controls

def shuffle_features(atoms: Sequence[Atom], seed: int = 0) -> list[Atom]:
    """Negative control: feature dicts permuted among atoms of the same page and type."""
    r = random.Random(seed)
    out = [Atom(a.page, a.section, a.id, a.typ, dict(a.cechy), dict(a.pozycja), a.etykieta, a.zrodlo, a.pewnosc, a.uwaga)
           for a in atoms]
    groups: dict[tuple, list[int]] = defaultdict(list)
    for i, a in enumerate(out):
        groups[(a.page, a.typ)].append(i)
    for idx in groups.values():
        dicts = [out[i].cechy for i in idx]
        r.shuffle(dicts)
        for i, d in zip(idx, dicts):
            out[i].cechy = d
    return out


def plant(atoms: Sequence[Atom], key: str, frac: float = 0.6, seed: int = 0) -> list[Atom]:
    """Positive control: the label's first glyph set by the value of feature `key` (typ.cecha) in a share of atoms."""
    r = random.Random(seed)
    typ, cecha = key.split(".", 1)
    glyph_of: dict = {}
    pool = ["o", "d", "s", "ch", "y", "k", "t", "q", "a", "l", "r", "sh", "e", "p", "f"]
    out = []
    for a in atoms:
        new = Atom(a.page, a.section, a.id, a.typ, dict(a.cechy), dict(a.pozycja),
                   dict(a.etykieta) if a.etykieta else None, a.zrodlo, a.pewnosc, a.uwaga)
        v = a.cechy.get(cecha) if a.typ == typ else None
        if v is not None and a.words and r.random() < frac:
            g = glyph_of.setdefault(v, pool[len(glyph_of) % len(pool)])
            rest = eva.glyphs(a.words[0])[1:]
            new.etykieta["slowa"] = ["".join([g] + rest)] + a.words[1:]
        out.append(new)
    return out


def random_fill(atoms: Sequence[Atom], vocab: dict, seed: int = 0, frac: float = 1.0) -> list[Atom]:
    """Features drawn at random from the vocabulary (to exercise the method before anyone has annotated)."""
    r = random.Random(seed)
    out = []
    for a in atoms:
        new = Atom(a.page, a.section, a.id, a.typ, dict(a.cechy), dict(a.pozycja), a.etykieta, "losowe", 1, a.uwaga)
        if r.random() < frac:
            for k, spec in vocab["typy"][a.typ]["cechy"].items():
                new.cechy[k] = (r.random() < 0.5 if spec == "bool" else r.randint(0, 8) if spec == "int" else r.choice(spec))
        out.append(new)
    return out


def summary(atoms: Sequence[Atom]) -> dict:
    """How far the annotation has got: atoms, filled atoms, pages, sources, per section."""
    done = filled(atoms)
    per_section = Counter(a.section for a in done)
    return {"atoms": len(atoms), "filled": len(done), "pages": len({a.page for a in atoms}),
            "pages_filled": len({a.page for a in done}), "sources": sorted({a.zrodlo for a in done if a.zrodlo}),
            "per_section": dict(per_section)}


# ---------- geometry for drafts from vision models (pure Python; see lab/vision.py for the models)

POINT_COORDS = re.compile(r'coords="([^"]*)"')
POINT_TRIPLE = re.compile(r"(\d+) (\d{1,4}) (\d{1,4})")
POINT_XY_ATTR = re.compile(r'x\d*="([\d.]+)"\s+y\d*="([\d.]+)"')


def parse_points(text: str, width: float, height: float) -> list[tuple[float, float]]:
    """Pixel points from a pointing model's reply.

    Molmo2 writes <points ... coords="1 123 456, 2 234 567"/> with coordinates scaled by 1000;
    the first Molmo wrote <point x="12.3" y="45.6"> in percent. Both are read; out-of-image points dropped.
    """
    out = []
    for coords in POINT_COORDS.findall(text):
        for _, x, y in POINT_TRIPLE.findall(coords):
            px, py = float(x) / 1000 * width, float(y) / 1000 * height
            if 0 <= px <= width and 0 <= py <= height:
                out.append((px, py))
    if not out:
        for x, y in POINT_XY_ATTR.findall(text):
            px, py = float(x) / 100 * width, float(y) / 100 * height
            if 0 <= px <= width and 0 <= py <= height:
                out.append((px, py))
    return out


def ring_layout(points: Sequence[tuple[float, float]], center: tuple[float, float] | None = None,
                max_rings: int = 3, gap: float = 0.15) -> list[dict]:
    """Rings and clockwise order (from twelve o'clock) of points around a roundel.

    Returns one dict per input point, same order: krag ("zewn", "srod", "wewn"), kolejnosc (1-based within
    the ring), kat (degrees clockwise from the top), promien (relative to the largest radius). Rings are cut
    where sorted radii jump by more than `gap` of the largest radius, at most `max_rings` rings.
    """
    if not points:
        return []
    if center is None:
        xs, ys = sorted(p[0] for p in points), sorted(p[1] for p in points)
        center = (statistics.median(xs), statistics.median(ys))
    cx, cy = center
    radii = [math.hypot(x - cx, y - cy) for x, y in points]
    angles = [(math.degrees(math.atan2(x - cx, -(y - cy))) + 360.0) % 360.0 for x, y in points]
    rmax = max(radii) or 1.0
    order = sorted(range(len(points)), key=lambda i: -radii[i])    # outermost first
    cuts = sorted(((radii[order[k]] - radii[order[k + 1]]) / rmax, k) for k in range(len(order) - 1))
    cuts = [k for g, k in cuts if g >= gap]
    cuts = sorted(cuts, key=lambda k: -(radii[order[k]] - radii[order[k + 1]]))[: max_rings - 1]
    ring_of = {}
    ring = 0
    for pos, i in enumerate(order):
        ring_of[i] = ring
        if pos in cuts:
            ring += 1
    n_rings = ring + 1
    names = {1: ["zewn"], 2: ["zewn", "wewn"], 3: ["zewn", "srod", "wewn"]}[n_rings]
    out = [None] * len(points)
    for r in range(n_rings):
        members = sorted((i for i in ring_of if ring_of[i] == r), key=lambda i: angles[i])
        for k, i in enumerate(members, 1):
            out[i] = {"krag": names[r], "kolejnosc": k, "kat": round(angles[i], 1), "promien": round(radii[i] / rmax, 3)}
    return out


def reading_order(points: Sequence[tuple[float, float]], row_tolerance: float) -> list[int]:
    """1-based reading order (rows top to bottom, left to right) for points on a page without rings."""
    idx = sorted(range(len(points)), key=lambda i: points[i][1])
    rows, current = [], []
    for i in idx:
        if current and points[i][1] - points[current[0]][1] > row_tolerance:
            rows.append(current)
            current = []
        current.append(i)
    if current:
        rows.append(current)
    out = [0] * len(points)
    k = 1
    for row in rows:
        for i in sorted(row, key=lambda i: points[i][0]):
            out[i] = k
            k += 1
    return out


def crop_box(point: tuple[float, float], points: Sequence[tuple[float, float]], width: float, height: float,
             factor: float = 1.6, minimum: float = 64.0) -> tuple[int, int, int, int]:
    """Square crop around a point, sized from the typical distance between neighbouring points, kept inside the image."""
    x, y = point
    nearest = []
    for i, (a, b) in enumerate(points):
        d = [math.hypot(a - c, b - e) for j, (c, e) in enumerate(points) if j != i]
        if d:
            nearest.append(min(d))
    side = max(minimum, factor * statistics.median(nearest)) if nearest else max(minimum, min(width, height) / 4)
    half = side / 2
    return (int(max(0, x - half)), int(max(0, y - half)), int(min(width, x + half)), int(min(height, y + half)))
