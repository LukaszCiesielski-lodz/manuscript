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


def zodiac(cfg: LabConfig, pointer: vision.Chat, describer: vision.Chat, detector: vision.Detector, vocab: dict,
           tmpl: dict, out_dir, res: TheoryResult) -> list[str]:
    from PIL import Image
    report, written = [], []
    specs = vocab["typy"]["nimfa"]["cechy"]
    prompt = vision.schema_prompt("nimfa", specs, "To wycinek z rękopisu: jedna postać (nimfa) z kręgu zodiaku, zwykle trzymająca gwiazdę.")
    canvases = [c for c in images.canvases() if any(images.base_folio(f) in ZODIAC_BASES for f in c["folios"])]
    for canvas in canvases:
        try:
            path = images.fetch(canvas, cfg.atoms_image_width, cfg.cache_dir / "folios", cfg.images_dir)
        except OSError as e:
            report.append(f"{canvas['label']}: brak skanu ({str(e)[:80]})")
            continue
        image = Image.open(path).convert("RGB")
        w, h = image.size
        figures = pointer.points(image, "human figure")
        stars = pointer.points(image, "star")
        centers = pointer.points(image, "center of each circular diagram")
        if not centers and figures:   # one roundel assumed: its centre is the mean of the figures
            centers = [(sum(p[0] for p in figures) / len(figures), sum(p[1] for p in figures) / len(figures))]
        try:
            dino = detector.boxes(image, ["human figure", "star"])
        except Exception as e:  # the second counter is a check, not a requirement
            dino = {}
            report.append(f"{canvas['label']}: Grounding DINO pominięty ({str(e)[:60]})")
        if not figures or not centers:
            report.append(f"{canvas['label']}: model nie wskazał postaci/środków (postaci {len(figures)}, środków {len(centers)})")
            continue
        centers = sorted(centers, key=lambda p: p[0])
        groups: dict[int, list] = {k: [] for k in range(len(centers))}
        for p in figures:
            groups[_nearest(p, centers)].append(p)
        signs = []
        for k, c in enumerate(centers):
            side = 0.12 * w
            crop = image.crop((int(max(0, c[0] - side)), int(max(0, c[1] - side)), int(min(w, c[0] + side)), int(min(h, c[1] + side))))
            signs.append({"znak": str(describer.json(crop, SIGN_PROMPT).get("znak") or "").lower()})
        folios = assign_folios(signs, canvas)
        preview = []
        for k, folio in enumerate(folios):
            pts = groups[k]
            if not folio or folio not in tmpl or not pts:
                report.append(f"{canvas['label']}: koło '{signs[k]['znak']}' ({len(pts)} postaci) bez strony")
                continue
            layout = A.ring_layout(pts, centers[k])
            descs = [describer.json(image.crop(A.crop_box(p, pts, w, h)), prompt) for p in pts]
            labels = sum(1 for a in tmpl[folio]["atomy"] if a["typ"] == "nimfa")
            note = f"szkic z GPU: punktów {len(pts)}, etykiet {labels}; sprawdzić kolejność na PNG"
            page, dropped = _fill(tmpl[folio], "nimfa", pts, layout, descs, vocab, w, h, note)
            (out_dir / f"{folio}.json").write_text(json.dumps(page, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            res.artifacts.append(f"atoms_vision/{folio}.json")
            written.append(folio)
            preview.append((folio, pts, layout))
            rings = {}
            for lay in layout:
                rings[lay["krag"]] = rings.get(lay["krag"], 0) + 1
            report.append(f"{folio} ({signs[k]['znak']}): postaci {len(pts)} (DINO {len(dino.get('human figure', []))} na kanwie), "
                          f"etykiet {labels}, kręgi {rings}, gwiazd {len([s for s in stars if _nearest(s, centers) == k])}, "
                          f"odrzuconych wartości {dropped}")
        if preview:
            png = out_dir / f"{canvas['label'].replace(' ', '_').replace('(', '').replace(')', '')}.png"
            _preview(image, preview, png)
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
                "liczy te same klasy ramkami jako kontrola; postaci przypisane do najbliższego środka, kręgi i kolejność zgodnie "
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
