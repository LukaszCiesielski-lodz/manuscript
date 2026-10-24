"""Fetch the notation corpora for the 'notation' theory into data/reference/notation/.

    python scripts/fetch_notation.py

Plainchant: CantusCorpus v0.2 (Cornelissen; scraped from the Cantus database), Volpiano strings,
one chant per line. Basse danse: the full tablature edition is fetched when reachable; a small
committed sample (data/notation/basse_danse.txt) is used otherwise.
"""

from __future__ import annotations

import csv
import io
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_data import fetch  # noqa: E402
from voynich import notation  # noqa: E402

DANCE_PDF = "http://virtuabis.free.fr/Les%20Basses%20Danses%20de%20Marguerite.pdf"


def pdf_text(pdf: Path) -> str:
    """Text of a PDF: pypdf when installed (Colab), pdftotext otherwise."""
    try:
        import pypdf
        return "\n".join(page.extract_text() or "" for page in pypdf.PdfReader(str(pdf)).pages)
    except ImportError:
        return subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout


def main() -> None:
    notation.DIR.mkdir(parents=True, exist_ok=True)
    csv.field_size_limit(10 ** 8)
    if not notation.CHANT_FILE.exists():
        data = fetch(notation.CANTUS_URL)
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            name = next(n for n in z.namelist() if n.endswith("chant.csv"))
            rows = csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8", newline=""))
            n = 0
            with open(notation.CHANT_FILE, "w", encoding="utf-8") as out:
                for row in rows:
                    v = (row.get("volpiano") or "").strip()
                    if v and "TEST" not in v:
                        out.write(v.replace("\n", " ") + "\n")
                        n += 1
        print(f"chorał: {n} melodii Volpiano -> {notation.CHANT_FILE}")
    full = notation.DIR / "basse_danse_full.txt"
    if not full.exists():
        try:
            pdf = notation.DIR / "marguerite.pdf"
            if not pdf.exists():
                pdf.write_bytes(fetch(DANCE_PDF))
            txt = pdf_text(pdf)
            dances = notation.extract_dances(txt)
            if len(dances) >= 20:
                full.write_text("\n".join(dances) + "\n", encoding="utf-8")
                print(f"basse danse: {len(dances)} tańców z wydania Marguerite d'Autriche")
            else:
                print("basse danse: wydanie pobrane, ale tabulatury nie dało się wydobyć; zostaje próbka")
        except Exception as exc:
            print(f"basse danse: pełne wydanie niedostępne ({exc}); zostaje próbka {notation.DANCE_FILE}")
    print("Notacje gotowe.")


if __name__ == "__main__":
    main()
