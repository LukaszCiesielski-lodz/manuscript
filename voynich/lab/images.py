"""Folio images from the Beinecke Library IIIF server.

`data/raw/beinecke_iiif.json` maps each digitised canvas to its folios
(foldouts hold several). Images are fetched at the requested width and
cached, so a second run (or a Drive-backed cache) costs nothing.
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path

from ..corpus import DATA

IIIF_MAP = DATA / "raw" / "beinecke_iiif.json"
# Leaves lost before the manuscript was foliated (gaps in the 15th-c. numbering).
MISSING_FOLIOS = [12, 59, 60, 61, 62, 63, 64, 74, 91, 92, 97, 98, 109, 110]


def canvases() -> list[dict]:
    return json.loads(IIIF_MAP.read_text(encoding="utf-8"))["canvases"]


def base_folio(zl_folio: str) -> str:
    """ZL names foldout panels f67r1, f85r2...; the scans are per leaf side: f67r, f85r."""
    m = re.match(r"(f\d+[rv])", zl_folio)
    return m.group(1) if m else zl_folio


def single_folio_canvases() -> dict[str, dict]:
    """Folio -> canvas, only for canvases that show exactly one folio side."""
    out = {}
    for c in canvases():
        if len(c["folios"]) == 1 and "part" not in c["label"]:
            out[c["folios"][0]] = c
    return out


def image_url(canvas: dict, width: int) -> str:
    doc = json.loads(IIIF_MAP.read_text(encoding="utf-8"))
    return doc["image_url"].format(iiif=canvas["iiif"], width=width)


def fetch(canvas: dict, width: int, cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{canvas['iiif']}_{width}.jpg"
    if path.exists() and path.stat().st_size > 1000:
        return path
    req = urllib.request.Request(image_url(canvas, width), headers={"User-Agent": "voynich-lab/1.0 (research)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                path.write_bytes(resp.read())
            return path
        except OSError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    return path


def fetch_folios(folios: list[str], width: int, cache_dir: Path) -> dict[str, Path]:
    by_folio = single_folio_canvases()
    out = {}
    for f in folios:
        c = by_folio.get(base_folio(f))
        if c:
            out[f] = fetch(c, width, cache_dir)
            time.sleep(0.2)  # be gentle with the library's server
    return out
