"""Draft atoms on our own GPU: pointing model + geometry + describing model (no API).

Not a test: the verdict is always undecided. For every zodiac canvas Molmo2 points at the
centre of each roundel, at every human figure and at every star; Grounding DINO counts the same
classes with boxes as a check. Figures are assigned to the nearest roundel centre, rings and the
clockwise order come from geometry (voynich.atoms.ring_layout), the sign in the centre names the
ZL folio, and Qwen3-VL describes a crop around each figure with the `nimfa` vocabulary. Output:
one page file per folio under <results>/atoms_vision/ (source "vision", confidence 1) and a PNG
with numbered points so a person can check the order against the labels at a glance.
Pharmaceutical pages (jars and plant fragments, reading order) run when cfg.atoms_sections says so.
"""

from __future__ import annotations

import json
import time

from ... import atoms as A
from .. import images, vision
from ..config import LabConfig
from ..results import TheoryResult
from .atoms_draft import ZODIAC_BASES, assign_folios

SIGN_PROMPT = ("W środku tego koła jest figura znaku zodiaku. Odpowiedz wyłącznie JSON: "
               '{"znak": "baran|byk|bliznieta|rak|lew|panna|waga|skorpion|strzelec|koziorozec|wodnik|ryby|inne"}')


def _clean(values: dict, specs: dict) -> tuple[dict, int]:
    out, dropped = {}, 0
    for k, spec in specs.items():
        v = values.get(k)
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        if isinstance(v, str) and spec == "bool":
            v = {"true": True, "false": False, "tak": True, "nie": False}.get(v.lower(), v)
        if v is not None and not A._value_ok(v, spec):
            dropped += 1
            v = None
        out[k] = v
    return out, dropped


def _preview(image, groups: list[tuple[str, list, list]], path) -> None:
    from PIL import ImageDraw
    img = image.copy()
    d = ImageDraw.Draw(img)
    colours = {"zewn": "red", "srod": "blue", "wewn": "green"}
    for folio, pts, layout in groups:
        for (x, y), lay in zip(pts, layout):
            d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=colours[lay["krag"]], width=3)
            d.text((x + 8, y - 8), f"{lay['kolejnosc']}", fill=colours[lay["krag"]])
        if pts:
            d.text((min(p[0] for p in pts), min(p[1] for p in pts) - 20), folio, fill="black")
    img.save(path)


def _fill(template: dict, typ: str, pts: list, layout: list[dict], descs: list[dict], vocab: dict, width: int,
          height: int, note: str) -> tuple[dict, int]:
    """Points poured into a page template in ring order; extra points become atoms without a label."""
    specs = vocab["typy"][typ]["cechy"]
    page = json.loads(json.dumps(template))
    rank = {"zewn": 0, "srod": 1, "wewn": 2}
    order = sorted(range(len(pts)), key=lambda i: (rank[layout[i]["krag"]], layout[i]["kolejnosc"]))
    slots = [a for a in page["atomy"] if a["typ"] == typ]
    dropped = 0
    for n, i in enumerate(order):
        cechy, d = _clean(descs[i], specs)
        dropped += d
        pos = {**layout[i], "x": round(pts[i][0] / width, 4), "y": round(pts[i][1] / height, 4)}
        if n < len(slots):
            atom = slots[n]
            atom["cechy"], atom["pozycja"] = cechy, {**atom["pozycja"], **pos}
            atom["zrodlo"], atom["pewnosc"], atom["uwaga"] = "vision", 1, note
        else:
            page["atomy"].append({"id": f"{page['strona']}-x{n + 1:02d}", "typ": typ, "cechy": cechy, "pozycja": pos,
                                  "etykieta": None, "zrodlo": "vision", "pewnosc": 1, "uwaga": "punkt bez etykiety; " + note})
    return page, dropped


def _nearest(point, centers):
    return min(range(len(centers)), key=lambda k: (point[0] - centers[k][0]) ** 2 + (point[1] - centers[k][1]) ** 2)


# Which ZL panels each Beinecke canvas shows, left to right (voynich.nu, quires 10-12), how many nymphs
# each roundel holds (Zandbergen's counts) and its sign. Pages are assigned from this table and the figure
# counts; the sign the describer sees is only a check printed in the report.
PANELS = {"1006200": ["f70v2"], "1006201": ["f70v1"], "1006202": ["f71r"], "1006203": ["f71v", "f72r1", "f72r2", "f72r3"],
          "1006204": ["f72v3", "f72v2"], "1006205": ["f72v1"], "1006206": ["f73r"], "1006207": ["f73v"]}
EXPECTED = {"f70v2": 29, "f70v1": 15, "f71r": 15, "f71v": 15, "f72r1": 15, "f72r2": 30, "f72r3": 30, "f72v3": 30,
            "f72v2": 30, "f72v1": 30, "f73r": 30, "f73v": 30}
SIGNS = {"f70v2": "ryby", "f70v1": "baran", "f71r": "baran", "f71v": "byk", "f72r1": "byk", "f72r2": "bliznieta", "f72r3": "rak",
         "f72v3": "lew", "f72v2": "panna", "f72v1": "waga", "f73r": "skorpion", "f73v": "strzelec"}
SIGN_PL = {"aries": "baran", "taurus": "byk", "gemini": "bliznieta", "cancer": "rak", "leo": "lew", "virgo": "panna", "libra": "waga",
           "scorpio": "skorpion", "sagittarius": "strzelec", "capricorn": "koziorozec", "aquarius": "wodnik", "pisces": "ryby"}
SIGN_PROMPT_EN = ('This is the centre of a medieval zodiac roundel. Which zodiac sign is the animal or figure? Answer only JSON: '
                  '{"sign": "aries|taurus|gemini|cancer|leo|virgo|libra|scorpio|sagittarius|capricorn|aquarius|pisces|other"}')
FIGURE_PROMPTS = ("human figure", "person")
ROTATIONS = (0, 1, 2, 3)          # quarter turns of the roundel crop: nymphs lie feet to the centre, so each stands up in some turn
MERGE_RADIUS = 0.065              # of the crop width: two points closer than this are one figure
CENTRE_EXCLUSION = 0.22           # of the roundel radius: the sign's own figures (Gemini, Virgo, Sagittarius) live here


def rotate_point(p: tuple[float, float], k: int, width: float, height: float) -> tuple[float, float]:
    """Where a point of a (width x height) image lands after k quarter turns counter-clockwise (PIL ROTATE_90 k times)."""
    x, y = p
    for _ in range(k % 4):
        x, y, width, height = y, width - x, height, width
    return (x, y)


def unrotate_point(p: tuple[float, float], k: int, width: float, height: float) -> tuple[float, float]:
    """Inverse of rotate_point: a point seen in the rotated image, back in the original (width x height) image."""
    return rotate_point(p, (-k) % 4, *((height, width) if k % 2 else (width, height)))


def rotated(image, k: int):
    from PIL import Image
    ops = {1: Image.Transpose.ROTATE_90, 2: Image.Transpose.ROTATE_180, 3: Image.Transpose.ROTATE_270}
    return image.transpose(ops[k]) if k % 4 else image


def merge_points(groups: list[list[tuple[float, float]]], min_dist: float) -> list[tuple[float, float]]:
    """Union of point lists from several sources, points closer than min_dist taken as the same thing."""
    out: list[tuple[float, float]] = []
    for pts in groups:
        for p in pts:
            if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= min_dist ** 2 for q in out):
                out.append(p)
    return out


def _shift(points, dx, dy, scale=1.0):
    return [(x * scale + dx, y * scale + dy) for x, y in points]


def zodiac(cfg: LabConfig, pointer: vision.Chat, describer: vision.Chat, detector: vision.Detector, vocab: dict,
           tmpl: dict, out_dir, res: TheoryResult) -> list[str]:
    from PIL import Image
    report, written = [], []
    specs = vocab["typy"]["nimfa"]["cechy"]
    prompt = vision.schema_prompt("nimfa", specs, "To wycinek z rękopisu: jedna postać (nimfa) z kręgu zodiaku, zwykle trzymająca gwiazdę.")
    canvases = [c for c in images.canvases() if any(images.base_folio(f) in ZODIAC_BASES for f in c["folios"])]
    for canvas in canvases:
        panels = PANELS.get(str(canvas["iiif"])) or [f for f in tmpl if images.base_folio(f) in {images.base_folio(x) for x in canvas["folios"]}]
        width = min(int(canvas.get("width") or 10 ** 6), cfg.atoms_image_width * max(1, len(panels)))
        try:
            path = images.fetch(canvas, width, cfg.cache_dir / "folios", cfg.images_dir)
        except OSError as e:
            report.append(f"{canvas['label']}: brak skanu ({str(e)[:80]})")
            continue
        image = Image.open(path).convert("RGB")
        w, h = image.size
        scale = min(1.0, 2000 / w)
        small = image.resize((int(w * scale), int(h * scale))) if scale < 1 else image
        centers = _shift(pointer.points(small, "center of each circular diagram"), 0, 0, 1 / scale)
        centers = sorted((p for p in centers if 0.03 * w < p[0] < 0.97 * w and 0.03 * h < p[1] < 0.97 * h), key=lambda p: p[0])
        if len(centers) != len(panels):
            report.append(f"{canvas['label']}: model wskazał {len(centers)} środków, paneli {len(panels)}; środki ustawione równo")
            centers = [((k + 0.5) / len(panels) * w, h / 2) for k in range(len(panels))]
        radius = 0.47 * min(h, w / len(panels))      # panels of a foldout are of equal width; the centre only shifts the crop
        preview = []
        for k, (folio, c) in enumerate(zip(panels, centers)):
            x0, y0 = int(max(0, c[0] - 1.05 * radius)), int(max(0, c[1] - 1.05 * radius))
            crop = image.crop((x0, y0, int(min(w, c[0] + 1.05 * radius)), int(min(h, c[1] + 1.05 * radius))))
            sources, counts = [], {}
            for what in FIGURE_PROMPTS:
                for k in ROTATIONS:
                    turned = rotated(crop, k)
                    found = [unrotate_point(q, k, crop.width, crop.height) for q in pointer.points(turned, what)]
                    sources.append(_shift(found, x0, y0))
                    counts[f"{what}@{90 * k}"] = len(found)
            try:
                boxes = detector.boxes(crop, ["person", "star"])
                dino = _shift([((b[0] + b[2]) / 2, (b[1] + b[3]) / 2) for b in boxes.get("person", [])], x0, y0)
                counts["dino"] = len(dino)
                sources.append(dino)
            except Exception as e:  # the second counter is a check, not a requirement
                counts["dino"] = None
                report.append(f"{canvas['label']}: Grounding DINO pominięty ({str(e)[:60]})")
            pts = merge_points(sources, MERGE_RADIUS * crop.width)
            pts = [q for q in pts if (q[0] - c[0]) ** 2 + (q[1] - c[1]) ** 2 >= (CENTRE_EXCLUSION * radius) ** 2]
            stars = _shift(pointer.points(crop, "star"), x0, y0)
            side = int(0.35 * radius)
            centre_crop = image.crop((int(max(0, c[0] - side)), int(max(0, c[1] - side)), int(min(w, c[0] + side)), int(min(h, c[1] + side))))
            seen = str(describer.json(centre_crop, SIGN_PROMPT_EN).get("sign") or "").lower()
            seen_pl = SIGN_PL.get(seen, seen or "?")
            if folio not in tmpl or not pts:
                report.append(f"{folio}: brak postaci (Molmo {counts}, oczekiwano {EXPECTED.get(folio)}); strona pominięta")
                continue
            layout = A.ring_layout(pts, c)
            descs = [describer.json(image.crop(A.crop_box(p, pts, w, h)), prompt) for p in pts]
            labels = sum(1 for a in tmpl[folio]["atomy"] if a["typ"] == "nimfa")
            note = (f"szkic z GPU: postaci {len(pts)} (oczekiwano {EXPECTED.get(folio)}), etykiet {labels}; "
                    f"model widzi znak '{seen_pl}', tabela mówi '{SIGNS.get(folio)}'; sprawdzić kolejność na PNG")
            page, dropped = _fill(tmpl[folio], "nimfa", pts, layout, descs, vocab, w, h, note)
            (out_dir / f"{folio}.json").write_text(json.dumps(page, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            res.artifacts.append(f"atoms_vision/{folio}.json")
            written.append(folio)
            preview.append((folio, _shift(pts, 0, 0, scale), layout))
            rings = {}
            for lay in layout:
                rings[lay["krag"]] = rings.get(lay["krag"], 0) + 1
            report.append(f"{folio} ({SIGNS.get(folio)}; model widzi {seen_pl}): postaci {len(pts)} po scaleniu (Molmo {counts}), "
                          f"oczekiwano {EXPECTED.get(folio)}, etykiet {labels}, kręgi {rings}, gwiazd {len(stars)}, odrzuconych wartości {dropped}")
        if preview:
            png = out_dir / f"{canvas['label'].replace(' ', '_').replace('(', '').replace(')', '')}_{canvas['iiif']}.png"
            _preview(small, preview, png)
            res.artifacts.append(f"atoms_vision/{png.name}")
    res.metrics["zodiac"] = {"pages": written, "report": report}
    return report


def pharmaceutical(cfg: LabConfig, pointer: vision.Chat, describer: vision.Chat, vocab: dict, tmpl: dict, out_dir,
                   res: TheoryResult) -> list[str]:
    from PIL import Image
    report, written = [], []
    by_folio = images.single_folio_canvases()
    jobs = {"naczynie": ("jar or container", "To wycinek z rękopisu: jedno naczynie (słój) z działu farmaceutycznego."),
            "fragment": ("plant", "To wycinek z rękopisu: fragment rośliny (korzeń, liść, kwiat) z działu farmaceutycznego.")}
    for folio, template in tmpl.items():
        if template.get("dzial") != "pharmaceutical" or images.base_folio(folio) not in by_folio or folio != images.base_folio(folio):
            continue
        try:
            path = images.fetch(by_folio[folio], cfg.atoms_image_width, cfg.cache_dir / "folios", cfg.images_dir)
        except OSError as e:
            report.append(f"{folio}: brak skanu ({str(e)[:80]})")
            continue
        image = Image.open(path).convert("RGB")
        w, h = image.size
        page = json.loads(json.dumps(template))
        for typ, (what, intro) in jobs.items():
            pts = pointer.points(image, what)
            labels = sum(1 for a in template["atomy"] if a["typ"] == typ)
            if not pts or not labels:
                continue
            order = A.reading_order(pts, 0.04 * h)
            layout = [{"krag": "zewn", "kolejnosc": k, "kat": None, "promien": None} for k in order]
            prompt = vision.schema_prompt(typ, vocab["typy"][typ]["cechy"], intro)
            descs = [describer.json(image.crop(A.crop_box(p, pts, w, h)), prompt) for p in pts]
            page, dropped = _fill(page, typ, pts, layout, descs, vocab, w, h, f"szkic z GPU: punktów {len(pts)}, etykiet {labels}")
            report.append(f"{folio} {typ}: punktów {len(pts)}, etykiet {labels}, odrzuconych wartości {dropped}")
        (out_dir / f"{folio}.json").write_text(json.dumps(page, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        res.artifacts.append(f"atoms_vision/{folio}.json")
        written.append(folio)
    res.metrics["pharmaceutical"] = {"pages": written, "report": report}
    return report


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    res = TheoryResult(
        theory="atoms_vision",
        hypothesis="(szkic, nie test) Otwarte modele widzące na własnym GPU opisują atomy ilustracji w schemacie data/atoms, "
                   "z kolejnością nimf policzoną z geometrii, żeby ludzie poprawiali zamiast zaczynać od zera.",
        method=(f"Molmo2 ({cfg.atoms_pointer}) wskazuje punktami środki kół, postaci i gwiazdy; Grounding DINO ({cfg.atoms_detector}) "
                "liczy te same klasy ramkami jako kontrola; wycinek każdego koła wskazywany w czterech obrotach (nimfy leżą stopami do środka); "
                "postaci przypisane do najbliższego środka, kręgi i kolejność zgodnie "
                f"z ruchem wskazówek zegara z geometrii (voynich.atoms.ring_layout); Qwen3-VL ({cfg.atoms_describer}) opisuje wycinek "
                "wokół każdej postaci według słownika 'nimfa' (wartości spoza słownika odrzucone); znak w środku koła wskazuje "
                "stronę ZL. Wynik: pliki stron w atoms_vision/ (zrodlo 'vision', pewnosc 1) i PNG z numerami punktów."),
        references=["Molmo2 (Ai2 2025), Qwen3-VL (Alibaba 2025), Grounding DINO (IDEA 2023), all Apache 2.0 on Hugging Face"])
    if not vision.available():
        res.evidence.append("Brak torch/transformers z GPU: szkic pominięty (uruchom colab/Voynich_Atomy_GPU.ipynb).")
        res.decide(None)
        res.summary = "Szkic nie powstał (brak GPU)."
        res.seconds = time.time() - t0
        return res
    vocab = A.load_vocab()
    tmpl = A.templates(vocab=vocab)
    out_dir = cfg.results_dir / "atoms_vision"
    out_dir.mkdir(parents=True, exist_ok=True)
    pointer = vision.Chat(cfg.atoms_pointer)
    describer = vision.Chat(cfg.atoms_describer)
    detector = vision.Detector(cfg.atoms_detector)
    report = []
    if "zodiac" in cfg.atoms_sections:
        report += zodiac(cfg, pointer, describer, detector, vocab, tmpl, out_dir, res)
    if "pharmaceutical" in cfg.atoms_sections:
        report += pharmaceutical(cfg, pointer, describer, vocab, tmpl, out_dir, res)
    pages = [a for a in res.artifacts if a.endswith(".json")]
    res.evidence.append("Strony: " + ("; ".join(report) if report else "nic nie opisano") + ".")
    res.decide(None)
    res.summary = f"Szkic {len(pages)} stron w atoms_vision/ (do sprawdzenia na PNG, poprawienia i scalenia z data/atoms)."
    res.caveats += ["Kolejność nimf z geometrii zakłada, że loci transliteracji idą zgodnie z ruchem wskazówek zegara od góry "
                    "w każdym kręgu; PNG z numerami służy do sprawdzenia tego na oko.",
                    "Modele liczą drobne rzeczy (promienie) niepewnie; pewnosc 1 dla wszystkich wartości.",
                    "To nie jest test: werdykt zawsze 'nierozstrzygnięta'."]
    res.seconds = time.time() - t0
    return res
