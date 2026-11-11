"""Draw the master card as it could have looked on a scribe's desk: a parchment leaf, six ruled columns, brown ink.

    python scripts/render_card.py                 # the 132-entry card (99% of the words) -> docs/karta_matka_rekonstrukcja.jpg
    python scripts/render_card.py --entries 242   # the card that writes every word
    python scripts/render_card.py --lang en       # English caption -> docs/karta_matka_rekonstrukcja.en.jpg

The pieces come from docs/karta_matka_100.md (theory master_card_full). The glyphs are Gabriel Landini's EVA
Hand 1 font, downloaded from voynich.nu into data/cache (the font is free for private use, not for commercial
use, and is not kept in the repository). Everything else is a guess at period practice and is drawn, not found:
the leaf, the ruling, the layout. The picture carries a caption saying so.
"""

from __future__ import annotations

import argparse
import math
import random
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_URL = "https://www.voynich.nu/Fonts/EVA2.ttf"
INK = (58, 36, 20)


def load_card(path: Path, entries: int) -> list[list[str]]:
    for part in path.read_text(encoding="utf-8").split("# Karta matka rękopisu: ")[1:]:
        if part.startswith(f"{entries} wpis"):
            rows = [l for l in part.splitlines() if l.startswith("|")][2:]
            cols = zip(*[[c.strip() for c in r.strip("|").split("|")] for r in rows])
            return [[c for c in col if c] for col in cols]
    raise SystemExit(f"no card of {entries} entries in {path}")


def font_file() -> Path:
    path = ROOT / "data" / "cache" / "fonts" / "EVA2.ttf"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(FONT_URL, headers={"User-Agent": "curl/8.5.0", "Accept": "*/*"})   # the site refuses urllib's default agent
        path.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    return path


def noise(size: tuple[int, int], scale: int, rng: np.random.Generator) -> np.ndarray:
    """Smooth noise in 0..1: random values on a coarse grid, enlarged and blurred."""
    w, h = size
    small = (rng.random((h // scale + 2, w // scale + 2)) * 255).astype(np.uint8)
    img = Image.fromarray(small).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(scale / 3))
    a = np.asarray(img, dtype=np.float32)
    return (a - a.min()) / (a.max() - a.min() + 1e-9)


def parchment(w: int, h: int, rng: np.random.Generator) -> Image.Image:
    """A sheet of calfskin: uneven cream, darker towards the edges, follicle speckle, a few stains, an irregular outline."""
    base = np.array([226, 205, 165], dtype=np.float32)
    tone = 0.55 * noise((w, h), 260, rng) + 0.3 * noise((w, h), 70, rng) + 0.15 * noise((w, h), 14, rng)
    img = base[None, None, :] * (0.86 + 0.2 * tone[:, :, None])
    img[:, :, 2] *= 0.94 + 0.08 * noise((w, h), 400, rng)             # warmer and cooler patches
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]).astype(np.float32)
    img *= (0.72 + 0.28 * np.clip(edge / (0.09 * w), 0, 1) ** 0.6)[:, :, None]
    speck = rng.random((h, w)) < 0.004                                # hair follicles
    img[speck] *= 0.9
    for _ in range(5):                                                # damp blotches, irregular, barely there
        cx, cy, r = rng.integers(0, w), rng.integers(0, h), rng.integers(w // 10, w // 4)
        d = np.sqrt(((xx - cx) / 1.3) ** 2 + (yy - cy) ** 2) / r
        img *= (1 - 0.1 * np.clip(1 - d, 0, 1) ** 1.5 * noise((w, h), 60, rng))[:, :, None]
    img += rng.normal(0, 2.2, (h, w, 1))                              # grain
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.5))
    # outline: a rounded rectangle whose edge wavers slowly, as the edge of a trimmed skin does
    mask = Image.new("L", (w, h), 0)
    cx, cy, a, b = w / 2, h / 2, w / 2 - 0.012 * w, h / 2 - 0.012 * w
    ph = rng.random(4) * 6.28
    pts = []
    for i in range(720):
        th = 2 * math.pi * i / 720
        c, s = math.cos(th), math.sin(th)
        wob = 1 - 0.004 * math.sin(5 * th + ph[0]) - 0.003 * math.sin(11 * th + ph[1]) - 0.0015 * math.sin(23 * th + ph[2])
        pts.append((cx + a * wob * math.copysign(abs(c) ** (2 / 14), c), cy + b * wob * math.copysign(abs(s) ** (2 / 14), s)))
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.5))
    return out, mask


def ink_line(layer: Image.Image, p0: tuple[float, float], p1: tuple[float, float], rng: np.random.Generator, width: float, alpha: int):
    """A line ruled by hand: slightly wavering, the ink thinning and thickening."""
    d = ImageDraw.Draw(layer)
    n = 80
    prev = None
    for i in range(n + 1):
        t = i / n
        x = p0[0] + (p1[0] - p0[0]) * t + 2.2 * math.sin(t * 9 + p0[0]) + rng.normal(0, 0.5)
        y = p0[1] + (p1[1] - p0[1]) * t + 2.2 * math.sin(t * 7 + p0[1]) + rng.normal(0, 0.5)
        if prev:
            a = int(alpha * (0.6 + 0.4 * math.sin(t * 23 + p0[0]) ** 2))
            d.line([prev, (x, y)], fill=INK + (a,), width=max(1, int(width + rng.normal(0, 0.4))))
        prev = (x, y)


def render(cols: list[list[str]], out: Path, seed: int = 7, width: int = 2000, lang: str = "pl"):
    rng = np.random.default_rng(seed)
    r = random.Random(seed)
    w, h = width, int(width * 1.38)
    sheet, mask = parchment(w, h, rng)
    ink = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rows = max(map(len, cols))
    left, right, top, bottom = 0.11 * w, 0.89 * w, 0.085 * h, 0.9 * h
    col_w = (right - left) / len(cols)
    row_h = (bottom - top) / rows
    font = ImageFont.truetype(str(font_file()), int(row_h * 0.74))
    for k in range(1, len(cols)):                                      # column rules, drawn by hand
        x = left + k * col_w + rng.normal(0, 3)
        ink_line(ink, (x, top - 0.02 * h + rng.normal(0, 8)), (x + rng.normal(0, 10), bottom + 0.015 * h + rng.normal(0, 12)), rng, 2.2, 120)
    ink_line(ink, (left - 0.02 * w, top - 0.012 * h), (right + 0.02 * w, top - 0.008 * h), rng, 2.4, 130)
    for k, col in enumerate(cols):
        load = 1.0                                                     # ink on the pen: fades until the next dip
        drift = 0.0
        for i, piece in enumerate(col):
            load -= r.uniform(0.03, 0.09)
            if load < 0.55:
                load = 1.0
            drift += r.uniform(-1.2, 1.2)                              # the column wanders a little
            bbox = font.getbbox(piece)
            tile = Image.new("RGBA", (bbox[2] - bbox[0] + 40, int(row_h * 1.9)), (0, 0, 0, 0))
            ImageDraw.Draw(tile).text((20 - bbox[0], int(row_h * 0.3)), piece, font=font, fill=INK + (int(255 * (0.62 + 0.38 * load)),))
            tile = tile.rotate(r.uniform(-2.2, 1.2), resample=Image.BICUBIC, expand=False)
            x = left + k * col_w + col_w * 0.14 + drift + r.uniform(-4, 4)
            y = top + i * row_h - row_h * 0.3 + r.uniform(-3, 3)
            ink.alpha_composite(tile, (int(x), int(y)))
    # ink sinks into the skin: a soft halo under a sharper stroke, broken by the grain of the parchment
    alpha = np.asarray(ink.split()[3], dtype=np.float32) / 255
    halo = np.asarray(ink.split()[3].filter(ImageFilter.GaussianBlur(1.8)), dtype=np.float32) / 255
    grain = 0.72 + 0.28 * noise((w, h), 5, rng)
    a = np.clip((0.82 * alpha + 0.3 * halo) * grain, 0, 1)
    a *= 0.8 + 0.2 * noise((w, h), 220, rng)                            # rubbed patches
    page = np.asarray(sheet, dtype=np.float32)
    page = page * (1 - a[:, :, None]) + np.array(INK, dtype=np.float32)[None, None, :] * a[:, :, None]
    page = Image.fromarray(np.clip(page, 0, 255).astype(np.uint8))
    # the leaf on a dark desk, with a soft shadow, and an honest caption underneath
    pad, cap = int(0.05 * w), int(0.075 * w)
    canvas = Image.new("RGB", (w + 2 * pad, h + 2 * pad + cap), (38, 30, 24))
    shadow = Image.new("L", canvas.size, 0)
    shadow.paste(mask, (pad + 10, pad + 14))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.composite(Image.new("RGB", canvas.size, (12, 9, 7)), canvas, shadow.point(lambda v: int(v * 0.8)))
    canvas.paste(page, (pad, pad), mask)
    d = ImageDraw.Draw(canvas)
    try:
        cf = ImageFont.truetype("DejaVuSans.ttf", int(0.0135 * w))
    except OSError:
        cf = ImageFont.load_default()
    n = sum(map(len, cols))
    if lang == "en":
        line1 = (f"Computer reconstruction (2026), not an artefact. Master card: {n} pieces in {len(cols)} columns that write "
                 f"{'every word' if n > 200 else '99% of the words'} of the Voynich manuscript.")
        line2 = "Pieces: theory master_card_full. Glyphs: EVA Hand 1 font by G. Landini (voynich.nu). Parchment, ruling and layout: conjecture."
    else:
        line1 = (f"Rekonstrukcja komputerowa (2026), nie zabytek. Karta matka: {n} kawałków w {len(cols)} kolumnach, z których składa się "
                 f"{'każde słowo' if n > 200 else '99% słów'} rękopisu Voynicha.")
        line2 = "Kawałki: teoria master_card_full. Glify: krój EVA Hand 1 G. Landiniego (voynich.nu). Pergamin, liniowanie i układ: domysł."
    d.text((pad, h + 2 * pad + int(0.012 * w)), line1, font=cf, fill=(196, 180, 150))
    d.text((pad, h + 2 * pad + int(0.036 * w)), line2, font=cf, fill=(150, 136, 112))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, quality=90) if out.suffix.lower() in (".jpg", ".jpeg") else canvas.save(out, optimize=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", type=Path, default=ROOT / "docs" / "karta_matka_100.md")
    ap.add_argument("--entries", type=int, default=132)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--width", type=int, default=2000)
    ap.add_argument("--lang", choices=("pl", "en"), default="pl", help="language of the caption")
    a = ap.parse_args()
    suffix = ("" if a.entries == 132 else f"_{a.entries}") + (".en" if a.lang == "en" else "") + ".jpg"
    out = a.out or ROOT / "docs" / ("karta_matka_rekonstrukcja" + suffix)
    print(render(load_card(a.card, a.entries), out, a.seed, a.width, a.lang))
