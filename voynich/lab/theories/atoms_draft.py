"""Draft atoms of the zodiac pages from a vision model (OpenRouter), to be corrected by people.

Not a test: the verdict is always undecided. Each zodiac canvas is sent to the vision model,
which lists the roundels it sees (sign, rings, nymphs clockwise from twelve o'clock) in the
schema of data/atoms/vocab.json. Nymphs are matched to the page's label loci by order, the
sign names the ZL folio (Aries and Taurus appear twice; the canvas and the left-to-right order
settle which is which). Values outside the vocabulary are dropped and counted. Output: one
page file per folio under <results>/atoms_draft/, source "vlm", confidence 1.
"""

from __future__ import annotations

import json
import time

from ... import atoms as A
from .. import images
from ..config import LabConfig
from ..results import TheoryResult

SIGN_FOLIOS = {"ryby": ["f70v2"], "baran": ["f70v1", "f71r"], "byk": ["f71v", "f72r1"], "bliznieta": ["f72r2"],
               "rak": ["f72r3"], "lew": ["f72v3"], "panna": ["f72v2"], "waga": ["f72v1"], "skorpion": ["f73r"],
               "strzelec": ["f73v"]}
ZODIAC_BASES = {"f70v", "f71r", "f71v", "f72r", "f72v", "f73r", "f73v"}
PROMPT = """To jest strona rękopisu Wojnicza z działu zodiaku: jedno lub kilka kół z figurą znaku zodiaku w środku i nagimi lub ubranymi
postaciami (nimfami) w kręgach dookoła, z których każda trzyma gwiazdę. Opisz TYLKO to, co widać; nie czytaj tekstu.
Dla każdego koła, od lewej do prawej, podaj znak w środku i nimfy po kręgach (najpierw zewnętrzny), zgodnie z ruchem wskazówek
zegara od godziny 12. Odpowiedz wyłącznie JSON:
{"kola": [{"znak": "baran|byk|bliznieta|rak|lew|panna|waga|skorpion|strzelec|koziorozec|wodnik|ryby|inne",
  "kregi": [{"krag": "zewn|srod|wewn", "nimfy": [{"naga": true, "w_obiekcie": "nic|beczka|kosz|rura|woda|inne",
    "korona": false, "wlosy": "rozpuszczone|upiete|nakrycie|nie_widac", "trzyma": "gwiazda|nic|krzyz|pierscien|inne",
    "kierunek": "lewo|prawo|przod", "gwiazda_promienie": 8, "gwiazda_ogon": true,
    "gwiazda_kolor": "brak|czerwony|zolty|niebieski|zielony|brazowy|czarny|inny"}]}]}]}
Liczbę nimf podaj dokładnie; jeśli jakiejś cechy nie widać, wpisz null."""


def zodiac_canvases() -> list[dict]:
    return [c for c in images.canvases() if any(images.base_folio(f) in ZODIAC_BASES for f in c["folios"])]


def assign_folios(roundels: list[dict], canvas: dict) -> list[str | None]:
    """ZL folio for each roundel the model reported on this canvas (None when the sign does not fit the canvas)."""
    bases = {images.base_folio(f) for f in canvas["folios"]}
    used: set[str] = set()
    out = []
    for r in roundels:
        sign = str(r.get("znak") or "").strip().lower()
        cands = [f for f in SIGN_FOLIOS.get(sign, []) if images.base_folio(f) in bases and f not in used]
        out.append(cands[0] if cands else None)
        if cands:
            used.add(cands[0])
    return out


def fill_page(template: dict, roundel: dict, vocab: dict) -> tuple[dict, int, int]:
    """Nymphs of a roundel (outer ring first) poured into the page's atoms by order; returns (page, nymphs, dropped values)."""
    specs = vocab["typy"]["nimfa"]["cechy"]
    nymphs = []
    for ring in roundel.get("kregi") or []:
        krag = ring.get("krag") if ring.get("krag") in ("zewn", "srod", "wewn") else None
        for n in ring.get("nimfy") or []:
            if isinstance(n, dict):
                nymphs.append((krag, n))
    page = json.loads(json.dumps(template))
    dropped = 0
    for atom, (krag, n) in zip(page["atomy"], nymphs):
        if atom["typ"] != "nimfa":
            continue
        for k, spec in specs.items():
            v = n.get(k)
            if isinstance(v, float) and v.is_integer():
                v = int(v)
            if v is not None and not A._value_ok(v, spec):
                dropped += 1
                v = None
            atom["cechy"][k] = v
        atom["pozycja"]["krag"] = krag
        atom["zrodlo"], atom["pewnosc"], atom["uwaga"] = "vlm", 1, "szkic modelu widzącego; sprawdzić"
    return page, len(nymphs), dropped


def run(cfg: LabConfig, client=None, vision_model: str = "") -> TheoryResult:
    t0 = time.time()
    res = TheoryResult(
        theory="atoms_draft",
        hypothesis="(szkic, nie test) Model widzący obrazy opisuje nimfy zodiaku w schemacie atomów, żeby ludzie poprawiali zamiast zaczynać od zera.",
        method=("Każdy skan stron zodiaku (f70v–f73v) do modelu widzącego; koła od lewej, nimfy po kręgach zgodnie z ruchem wskazówek zegara; "
                "znak zodiaku wskazuje stronę ZL (Baran i Byk podwójne: rozstrzyga skan i kolejność); nimfy dopasowane do loci etykiet po "
                "kolejności; wartości spoza słownika odrzucone. Wynik: pliki stron w atoms_draft/, zrodlo 'vlm', pewnosc 1."),
        references=["Zandbergen, voynich.nu: the zodiac section"])
    vocab = A.load_vocab()
    tmpl = A.templates(vocab=vocab)
    if client is None or not vision_model:
        res.evidence.append("Brak klienta OpenRouter albo modelu widzącego: szkic pominięty.")
        res.decide(None)
        res.summary = "Szkic nie powstał (brak OpenRouter)."
        res.seconds = time.time() - t0
        return res
    from ..openrouter import image_part, parse_json
    out_dir = cfg.results_dir / "atoms_draft"
    out_dir.mkdir(parents=True, exist_ok=True)
    width = max(cfg.image_width, 1600)
    report, written = [], []
    for canvas in zodiac_canvases():
        try:
            path = images.fetch(canvas, width, cfg.cache_dir / "folios", cfg.images_dir)
        except OSError as e:
            report.append(f"{canvas['label']}: brak skanu ({str(e)[:80]})")
            continue
        try:
            text = client.chat(vision_model, [{"role": "user", "content": [{"type": "text", "text": PROMPT},
                                                                           image_part(path.read_bytes())]}], 4000)
        except Exception as e:  # budget or API error: keep what we have
            report.append(f"{canvas['label']}: błąd modelu ({str(e)[:80]})")
            break
        roundels = parse_json(text).get("kola") or []
        for folio, roundel in zip(assign_folios(roundels, canvas), roundels):
            if not folio or folio not in tmpl:
                report.append(f"{canvas['label']}: koło '{roundel.get('znak')}' bez strony")
                continue
            page, n, dropped = fill_page(tmpl[folio], roundel, vocab)
            labels = sum(1 for a in page["atomy"] if a["typ"] == "nimfa")
            (out_dir / f"{folio}.json").write_text(json.dumps(page, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            written.append(folio)
            res.artifacts.append(f"atoms_draft/{folio}.json")
            report.append(f"{folio} ({roundel.get('znak')}): nimf {n} wobec etykiet {labels}, odrzuconych wartości {dropped}")
    res.metrics = {"pages": written, "report": report, "spent_usd": getattr(client, "spent_usd", None)}
    res.evidence.append("Strony: " + ("; ".join(report) if report else "nic nie opisano") + ".")
    res.decide(None)
    res.summary = f"Szkic {len(written)} stron zodiaku w atoms_draft/ (do poprawienia ręcznie i scalenia z data/atoms)."
    res.caveats += ["Model źle liczy drobne rzeczy (promienie gwiazd); dopasowanie nimf do etykiet po kolejności jest zgadywaniem, "
                    "gdy liczby się nie zgadzają.", "To nie jest test: werdykt zawsze 'nierozstrzygnięta'."]
    res.seconds = time.time() - t0
    return res
