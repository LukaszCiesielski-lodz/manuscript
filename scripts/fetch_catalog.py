"""Build data/catalog/pages.json from René Zandbergen's page descriptions (voynich.nu, quires 1-20).

    python scripts/fetch_catalog.py [--from DIR]   # DIR holds q01.html ... q20.html already downloaded

Every page of the manuscript gets one record: the section as he classifies it, his description of
the illustration, the Gheuens/Rapaport drawing-style features for herbal pages (alpha/beta codes),
the count and kinds of text items, Currier language, his own language code, the LFD hand, the
tentative plant identifications and cross-references to other folios ("same plant as fragment 204
on f102r1"). The descriptions are his; the file records the source and date.
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "catalog" / "pages.json"
QUIRES = [f"q{n:02d}" for n in range(1, 21)]
SECTIONS = [("herbal page", "herbal"), ("zodiac page", "zodiac"), ("astronomical page", "astronomical"),
            ("cosmological page", "cosmological"), ("biological page", "biological"), ("balneological", "biological"),
            ("pharmaceutical page", "pharmaceutical"), ("text-only page", "text"), ("text only page", "text"),
            ("stars drawn in the margin", "stars"), ("rosettes", "cosmological"), ("so-called biological", "biological")]
FEATURE = re.compile(r"^(!?)\s*(α|β)\s*:\s*(.+?)\s*(\(tentative\))?$")


def fetch(q: str, folder: Path | None) -> str:
    if folder and (folder / f"{q}.html").exists():
        return (folder / f"{q}.html").read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(f"https://www.voynich.nu/{q}/index.html", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def text(fragment: str) -> str:
    t = re.sub(r"<BR\s*/?>", "\n", fragment, flags=re.I)
    t = re.sub(r"</P>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    return "\n".join(line.strip() for line in t.splitlines()).strip()


def links(fragment: str) -> list[str]:
    return sorted({m for m in re.findall(r'HREF="[^"]*#(f\d+[rv]\d?)"', fragment)})


def parse_page(folio: str, block: str, quire: str) -> dict:
    parts = re.split(r"<H4>\s*(.*?)\s*</H4>", block, flags=re.I)
    sections = {}
    for k in range(1, len(parts) - 1, 2):
        sections[parts[k].strip().lower()] = parts[k + 1]
    general = text(sections.get("general description", sections.get("description", "")))
    illus_html = sections.get("illustration(s)", "")
    illus = text(illus_html)
    txt = text(sections.get("text", ""))
    ident = text(sections.get("tentative identifications", ""))
    other = text(sections.get("other information", ""))
    section = next((code for key, code in SECTIONS if key in general.lower()), "")
    if not section and "zodiac" in illus.lower():
        section = "zodiac"
    features, tentative = [], []
    for line in illus.splitlines():
        m = FEATURE.match(line.strip())
        if m:
            (tentative if m.group(4) else features).append(f"{'!' if m.group(1) else ''}{m.group(2)}:{m.group(3).strip()}")
    description = "\n".join(l for l in illus.splitlines() if not FEATURE.match(l.strip())
                            and not l.startswith("Herbal drawing characterisation") and l.strip() != "(none)").strip()
    m = re.search(r"This page has (\d+) text items?", txt)
    loci = int(m.group(1)) if m else None
    kinds = []
    if m:
        after = txt[m.end():]
        after = after[after.find(":") + 1:] if "as follows" in after[:40] else after
        for line in after.split("\n"):
            line = line.strip().rstrip(";.,")
            if not line:
                continue
            if not re.match(r"^\d+ ", line):
                break
            kinds.append(line)
    cur = re.search(r"Currier language:\s*([A-Z\-]+)", txt)
    rz = re.search(r"RZ language:\s*([^\n]+)", txt)
    hand = re.search(r"LFD hand:\s*([^\n]+)", txt)
    ids = {}
    for tag in ("ELV", "ThP", "THP", "ELVA"):
        m2 = re.search(tag + r":\s*([^\n]+?)(?=(?:\s(?:ELV|ThP|THP|ELVA):)|$)", ident, flags=re.M)
        if m2:
            ids[tag.upper()] = m2.group(1).strip()
    frag = [(int(n), f) for n, f in re.findall(r"fragment #?(\d+) on\s*(?:\[)?(f\d+[rv]\d?)", illus_html.replace("\n", " ") and text(illus_html).replace("\n", " "))]
    same = [(int(n), f) for n, f in re.findall(r"same plant as shown in fragment #?(\d+) on\s*(f\d+[rv]\d?)", text(illus_html).replace("\n", " "))]
    other = other.split("\nFolio ")[0].strip()
    description = re.sub(r"\n{2,}", "\n", description)
    return {"folio": folio, "quire": int(quire[1:]), "section": section, "illustration": description,
            "features": features, "features_tentative": tentative, "loci": loci, "text_items": kinds,
            "currier": cur.group(1) if cur else None, "rz_language": rz.group(1).strip() if rz else None,
            "hand": hand.group(1).strip() if hand else None, "identifications": ids,
            "links": [l for l in links(illus_html) if l != folio],
            "similar_fragments": [{"fragment": n, "folio": f, "same": (n, f) in same} for n, f in frag],
            "general": general[:600], "other": other[:600]}


def parse_quire(page_html: str, quire: str) -> list[dict]:
    heads = list(re.finditer(r'<TH CLASS="Ph" ID="(f\d+[rv]\d?)">', page_html))
    out = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(page_html)
        out.append(parse_page(h.group(1), page_html[h.end():end], quire))
    return out


def main(argv: list[str]) -> int:
    folder = Path(argv[argv.index("--from") + 1]) if "--from" in argv else None
    pages = []
    for q in QUIRES:
        try:
            src = fetch(q, folder)
        except Exception as e:  # quires 16 and 18 are lost: the site has no page for them
            print(f"{q}: {e}")
            continue
        got = parse_quire(src, q)
        print(f"{q}: {len(got)} stron")
        pages += got
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"source": "René Zandbergen, voynich.nu, quire pages q01-q20 (descriptions and Gheuens/Rapaport features), fetched 2026-11-07",
                               "pages": pages}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"zapisano {len(pages)} stron do {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
