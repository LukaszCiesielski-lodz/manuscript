"""Write colab/Voynich_Lab.ipynb. Edit the cells here, then run: python colab/make_notebook.py"""

import json
from pathlib import Path

CODE_BRANCH = "ccr-c7aecff8-6u13ue"

cells = [
    ("md", """# Voynich Lab – testy hipotez na GPU z radą modeli

Notebook uruchamia testy hipotez o rękopisie Wojnicza z repozytorium `lukaszciesielski-lodz/manuscript`:

| teoria | co sprawdza | potrzebuje |
|---|---|---|
| `numbers` | czy znaki to liczby (cały tekst w 5 systemach liczbowych; etykiety zodiaku jako dni 1–30) | CPU |
| `illustrations` | czy tekst zależy od rysunków (układ przy rysunkach, CLIP + test Mantela, nazwy roślin jako „criby”) | GPU, OpenRouter (wizja) |
| `generative` | czy transformer napisze brakujące strony nieodróżnialne od prawdziwych; opcjonalnie obrazy SDXL+LoRA | GPU |
| `naibbe_cipher`, `cardan_grille`, `hebrew_anagram` | teorie z literatury (Greshko 2025, Rugg 2004, Hauer i Kondrak 2016) | CPU |
| `basque` | baskijski pod szyfrem podstawieniowym (Leizarraga 1571 i prasa współczesna) | CPU |

Każdy test ma **kontrole metody**: musi znaleźć efekt podłożony celowo i nie znajdować go w danych losowych. Gdy kontrola nie przejdzie, werdykt brzmi „metoda niewiarygodna”, niezależnie od wyniku. Rada modeli (OpenRouter) dyskutuje wyniki w trzech rundach, ale werdykt testu wynika tylko z liczb.

**Ustawienia Colaba:** Runtime → Change runtime type → GPU (A100 albo L4), High-RAM.
**Sekrety** (ikona klucza po lewej, z dostępem dla notebooka): `GITHUB_TOKEN` (fine-grained, Contents: read and write na tym repozytorium) i `OPENROUTER_API_KEY`."""),
    ("code", """!nvidia-smi --query-gpu=name,memory.total --format=csv
import psutil; print(f"RAM: {psutil.virtual_memory().total / 1e9:.0f} GB")"""),
    ("md", "## 1. Kod i dane"),
    ("code", f"""import os, subprocess
from google.colab import userdata

REPO = "lukaszciesielski-lodz/manuscript"
CODE_BRANCH = "{CODE_BRANCH}"   # gałąź z kodem laboratorium
token = userdata.get("GITHUB_TOKEN")
if not os.path.exists("/content/manuscript"):
    subprocess.run(["git", "clone", "--depth", "50", "--branch", CODE_BRANCH,
                    f"https://x-access-token:{{token}}@github.com/{{REPO}}.git", "/content/manuscript"], check=True)
os.chdir("/content/manuscript")
# Kolejne uruchomienie w tej samej sesji: dociągnij najnowszy kod (wyniki są na osobnej gałęzi).
subprocess.run(["git", "fetch", "origin", CODE_BRANCH], check=True)
subprocess.run(["git", "checkout", "-B", CODE_BRANCH, f"origin/{{CODE_BRANCH}}"], check=True)
!git log --oneline -3"""),
    ("code", """# PyTorch, numpy, scikit-learn i Pillow są w Colabie; dokładamy CLIP.
!pip install -q open_clip_torch
!python scripts/fetch_data.py   # na końcu musi wypisać „Dane kompletne.”; jeśli nie, uruchom ponownie"""),
    ("code", """# Opcjonalnie: pamięć podręczna skanów na Dysku, żeby nie pobierać ich przy każdej sesji.
USE_DRIVE = True
if USE_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")
    CACHE = "/content/drive/MyDrive/voynich_lab_cache"
else:
    CACHE = "/content/manuscript/data/cache\""""),
    ("md", "## 2. Ustawienia"),
    ("code", """from pathlib import Path
from voynich.lab.config import LabConfig
from voynich.lab.runner import Lab

cfg = LabConfig(
    cache_dir=Path(CACHE),
    theories=["all"],          # albo np. ["numbers", "literature"]
    quick=False,               # True: szybki przebieg próbny (~5 min)
    budget_usd=5.0,            # twardy limit wydatków na OpenRouter w tym przebiegu
    council_size=4,            # liczba modeli w radzie (gdy council_models puste)
    council_models=[           # puste = najnowszy model każdego dostawcy z listy council_vendors
        "z-ai/glm-5.3-flash",
        "openai/gpt-6-luna",
        "inception/mercury-3",
        "tencent/hy3",
    ],
    chair_model="openai/gpt-6-luna",           # opcjonalnie; bez tego przewodniczy pierwszy z listy
    vision_model="qwen/qwen2.5-vl-72b-instruct",
    vlm_folios_limit=20,       # 0 = wszystkie strony zielnika dla modelu wizyjnego (~130 obrazów)
    images_dir=None,           # np. Path("/content/drive/MyDrive/voynich_skany"): pliki f1r.jpg, f1v.jpg...
    gpt_steps=6000,            # kroki uczenia transformera
    run_image_diffusion=False, # True: SDXL + LoRA dla brakujących stron (~1 h na A100)
)
lab = Lab(cfg)
lab.connect()   # pokaże wybraną radę, model wizyjny i ceny"""),
    ("md", "## 3. Testy\nKażdą komórkę można uruchomić osobno. Wyniki zapisują się w `results/lab/<data>/`."),
    ("code", 'lab.run("numbers");'),
    ("code", 'lab.run("naibbe_cipher"); lab.run("cardan_grille"); lab.run("hebrew_anagram"); lab.run("basque");'),
    ("code", """# Próba pobrania jednego skanu. Yale zwykle odrzuca Colaba (403); wtedy kod bierze te same skany
# Beinecke z Internet Archive (archive.org/details/voynich) i sprawdza proporcje każdej strony.
from voynich.lab import images
try:
    print("OK:", images.fetch(images.single_folio_canvases()["f1v"], 512, cfg.cache_dir / "folios", cfg.images_dir))
except OSError as e:
    print("Brak skanów – części B i C testu ilustracji zostaną pominięte.\n", e)"""),
    ("code", 'lab.run("illustrations");   # pobiera skany z Beinecke (IIIF), liczy CLIP na GPU, pyta model wizyjny'),
    ("code", 'lab.run("generative");      # uczy transformer znakowy i generuje brakujące strony'),
    ("md", "## 4. Rada modeli\nTrzy rundy na każdy wynik: niezależne opinie, wzajemna recenzja anonimowych opinii, synteza przewodniczącego."),
    ("code", """lab.convene()
print(f"Wydano: {lab.client.spent_usd:.2f} USD" if lab.client else "")"""),
    ("code", """from IPython.display import Markdown, display
display(Markdown(lab.report().read_text()))"""),
    ("md", """## 5. Psy gończe
Rada przestaje tylko oceniać: każdy model dostaje rolę (kryptolog, lingwista, sceptyk, dziki pies), wymyśla przepisy
odczytu z klocków (klucze z π, e, dat; nulle; co n-te słowo; brak spacji; akrostychy; języki docelowe...),
laboratorium testuje je z kontrolami, a modele widzą tabelę wyników i w kolejnych rundach poprawiają tropy.
Najlepsze tropy są na końcu powtarzane na innej części rękopisu. Pomysły spoza klocków trafiają na listę życzeń."""),
    ("code", """hunt = lab.hunt(rounds=4, per_hound=2)   # ok. 4 × 4 × 2 = 32 przepisy; quick=True skraca testy
lab.report(); lab.push()                 # od razu na GitHub, nawet gdy nikt nie pilnuje sesji
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "hunt" / "hunt.md").read_text()))"""),
    ("md", "## 6. Zapis wyników na GitHubie\nWyniki trafiają na gałąź `lab-results` (osobną od kodu)."),
    ("code", "lab.push()"),
]


def cell(kind, text):
    src = text.splitlines(keepends=True)
    if kind == "md":
        return {"cell_type": "markdown", "metadata": {}, "source": src}
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}


nb = {"nbformat": 4, "nbformat_minor": 0,
      "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": "A100", "machine_shape": "hm"},
                   "kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}},
      "cells": [cell(k, t) for k, t in cells]}
out = Path(__file__).with_name("Voynich_Lab.ipynb")
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print("wrote", out)
