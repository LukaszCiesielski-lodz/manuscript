"""Folio images from the Beinecke Library IIIF server.

`data/raw/beinecke_iiif.json` maps each digitised canvas to its folios
(foldouts hold several). Images are fetched at the requested width and
cached, so a second run (or a Drive-backed cache) costs nothing.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
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


# The library's firewall rejects unknown clients (a custom User-Agent got 403 on Colab),
# so requests look like an ordinary browser visit from the collection page.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://collections.library.yale.edu/catalog/2002046",
}


def image_urls(canvas: dict, width: int) -> list[str]:
    """IIIF variants to try in order: exact width, bounded box, a size the server pre-renders, full size."""
    base = f"https://collections.library.yale.edu/iiif/2/{canvas['iiif']}"
    return [f"{base}/full/{width},/0/default.jpg", f"{base}/full/!{width},{width}/0/default.jpg",
            f"{base}/full/pct:50/0/default.jpg", f"{base}/full/full/0/default.jpg"]


def fetch(canvas: dict, width: int, cache_dir: Path, local_dir: Path | None = None) -> Path:
    """Path to the folio image: user-supplied folder first, then cache, then the IIIF server."""
    if local_dir:
        for name in canvas["folios"]:
            for ext in (".jpg", ".jpeg", ".png"):
                if (local_dir / f"{name}{ext}").exists():
                    return local_dir / f"{name}{ext}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{canvas['iiif']}_{width}.jpg"
    if path.exists() and path.stat().st_size > 1000:
        return path
    errors = []
    for url in image_urls(canvas, width):
        for attempt in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as resp:
                    path.write_bytes(resp.read())
                return path
            except urllib.error.HTTPError as e:
                errors.append(f"{e.code} {url}")
                if e.code in (403, 404):
                    break  # a refusal will not change on retry; try the next URL form
                time.sleep(2 ** attempt)
            except OSError as e:
                errors.append(f"{type(e).__name__} {url}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
    raise OSError("nie udało się pobrać skanu " + canvas["label"] + ": " + "; ".join(errors[-4:]))


def fetch_folios(folios: list[str], width: int, cache_dir: Path, local_dir: Path | None = None) -> dict[str, Path]:
    """Fetch what can be fetched; raise only if nothing at all could be obtained."""
    by_folio = single_folio_canvases()
    out, failed = {}, []
    for f in folios:
        c = by_folio.get(base_folio(f))
        if not c:
            continue
        try:
            out[f] = fetch(c, width, cache_dir, local_dir)
        except OSError as e:
            failed.append(str(e))
            if not out and len(failed) >= 3:
                break  # the server refuses us outright; stop instead of trying every folio
        time.sleep(0.2)  # be gentle with the library's server
    if failed:
        print(f"  skany: pobrano {len(out)}, nie udało się {len(failed)}; pierwszy błąd: {failed[0]}")
    if not out and failed:
        raise OSError(failed[0] + ". Wgraj skany do folderu i ustaw LabConfig(images_dir=...), pliki nazwane np. f1r.jpg")
    return out
