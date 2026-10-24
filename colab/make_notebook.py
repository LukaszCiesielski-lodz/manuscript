"""Write the Colab notebooks (colab/Voynich_*.ipynb). Edit the cells here, then run: python colab/make_notebook.py"""

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
| `nomenclator` | księga kodów: każde słowo to kod jednego słowa języka (łamacz na poziomie słów, rozstrzyga szyk) | CPU |
| `hoax` | tekst bez treści z reguł skryby: generatory v4 i v5 na 20 miarach i klasyfikatorze wierszy | CPU |
| `syntax` | daleka składnia: czy różne słowa zależą od siebie na odległość 2–7 słów, czy tylko powtórzenia i warianty | CPU |
| `romance` | język (proto)romański: łacina ludowa (Egeria), starofrancuski, 5 Biblii romańskich; szyfr i składnia | CPU |
| `lengths` | słowa jako liczby (długości): zależność sąsiadów, naprzemienność krótkie–długie, pamięć długozasięgowa (DFA) | CPU |
| `wheel`, `adversary`, `genres` | tarcza Llulla ewoluowana na GPU, transformer-sędzia generatorów, gatunki bez składni (litania, imiona magiczne); osobny notebook `Voynich_Kolo.ipynb` | GPU |
| `phonotactics`, `transcriptions`, `cognate`, `hillclimb` | samogłoski Suchotina i wzorce C/V wobec języków; podpis w innych transliteracjach; NeuroDecipher (dopasowanie słownictwa z transportem optymalnym); atak homofoniczny wspinaczką z modelem n-gramowym; osobny notebook `Voynich_Lamacze.ipynb` | GPU |
| `brute` | brute force: każda trójka kolejnych słów pod jednym kluczem litera-za-glif w ~45 językach epoki; czy klucze się zgadzają | GPU |

Każdy test ma **kontrole metody**: musi znaleźć efekt podłożony celowo i nie znajdować go w danych losowych. Gdy kontrola nie przejdzie, werdykt brzmi „metoda niewiarygodna”, niezależnie od wyniku. Rada modeli (OpenRouter) dyskutuje wyniki w trzech rundach, ale werdykt testu wynika tylko z liczb.

**Ustawienia Colaba:** Runtime → Change runtime type → GPU (A100 albo L4), High-RAM.
**Sekrety** (ikona klucza po lewej, z dostępem dla notebooka): `GITHUB_TOKEN` (fine-grained, Contents: read and write na tym repozytorium) i `OPENROUTER_API_KEY`."""),
    ("code", """!nvidia-smi --query-gpu=name,memory.total --format=csv
import psutil; print(f"RAM: {psutil.virtual_memory().total / 1e9:.0f} GB")"""),
    ("md", "## 1. Kod i dane"),
    ("code", f"""import os, subprocess
from google.colab import userdata
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"   # mniej fragmentacji pamięci GPU

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
import importlib; importlib.invalidate_caches()
!git log --oneline -3"""),
    ("code", """# PyTorch, numpy, scikit-learn i Pillow są w Colabie; dokładamy CLIP.
!pip install -q open_clip_torch
!python scripts/fetch_data.py   # na końcu musi wypisać „Dane kompletne.”; jeśli nie, uruchom ponownie
!python scripts/fetch_lexicons.py   # słowniki ~45 języków epoki do brute force (opcjonalne, ~2 min)"""),
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
    vlm_folios_limit=0,        # 0 = wszystkie strony zielnika dla modelu wizyjnego (~120 obrazów); 20 = szybka próba
    images_dir=None,           # np. Path("/content/drive/MyDrive/voynich_skany"): pliki f1r.jpg, f1v.jpg...
    gpt_steps=6000,            # kroki uczenia transformera
    run_image_diffusion=False, # True: SDXL + LoRA dla brakujących stron (~1 h na A100)
)
lab = Lab(cfg)
lab.connect()   # pokaże wybraną radę, model wizyjny i ceny"""),
    ("md", "## 3. Testy\nKażdą komórkę można uruchomić osobno. Wyniki zapisują się w `results/lab/<data>/`."),
    ("code", 'lab.run("numbers");'),
    ("code", 'lab.run("naibbe_cipher"); lab.run("cardan_grille"); lab.run("hebrew_anagram"); lab.run("basque"); lab.run("nomenclator"); lab.run("hoax"); lab.run("syntax"); lab.run("romance"); lab.run("lengths"); lab.run("phonotactics"); lab.run("length_code");'),
    ("code", 'lab.run("brute");            # brute force trójek na GPU (~1 h na A100 przy 45 językach)'),
    ("code", """# Próba pobrania jednego skanu. Yale zwykle odrzuca Colaba (403); wtedy kod bierze te same skany
# Beinecke z Internet Archive (archive.org/details/voynich) i sprawdza proporcje każdej strony.
from voynich.lab import images
try:
    print("OK:", images.fetch(images.single_folio_canvases()["f1v"], 512, cfg.cache_dir / "folios", cfg.images_dir))
except OSError as e:
    print("Brak skanów – części B i C testu ilustracji zostaną pominięte.")
    print(e)"""),
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


# A short notebook for one task: the illustration test on all herbal pages, then council and push.
illustrations_cells = [
    ("md", """# Voynich Lab – ilustracje (powtórka testu C na wszystkich stronach zielnika)

Uruchom: Środowisko wykonawcze → Uruchom wszystko. Wymaga GPU (L4 albo A100) i sekretów `GITHUB_TOKEN`, `OPENROUTER_API_KEY`.
Wynik trafia sam na gałąź `lab-results`."""),
    cells[3], cells[4], cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]',
                                 'theories=["illustrations"],')),
    ("code", """lab.run("illustrations")
lab.convene(["illustrations"])
lab.report(); lab.push()
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "illustrations.md").read_text()))"""),
]


brute_cells = [
    ("md", """# Voynich Lab – brute force trójek słów na GPU

Każda trójka kolejnych słów rękopisu jest czytana pod każdym kluczem litera-za-glif w ~45 językach epoki
(Biblie, korpusy historyczne: greka, staro-cerkiewno-słowiański, gocki, ormiański, koptyjski, hebrajski biblijny,
średniofrancuski, łacina Akwinaty, łacina średniowieczna i ludowa, starofrancuski...). Słownik przycina przestrzeń kluczy
do dokładnie tych odczytów, które dałoby pełne wyliczenie; GPU sprawdza wszystkie kombinacje kandydatów naraz.
Liczy się nie to, czy trójka ma odczyt (ma prawie zawsze), lecz czy odczyty różnych trójek zgadzają się co do jednego
klucza, który zamienia większość słów rękopisu w słowa języka – na tle bełkotu o statystyce rękopisu i zaszyfrowanego
prawdziwego tekstu. Uruchom: Środowisko wykonawcze → Uruchom wszystko (GPU A100, sekrety `GITHUB_TOKEN`, `OPENROUTER_API_KEY`)."""),
    cells[3],
    ("code", """!pip install -q open_clip_torch
!python scripts/fetch_data.py
!python scripts/fetch_lexicons.py"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]',
                                 'theories=["brute"],\n    brute_languages=[],        # puste = wszystkie leksykony; np. ["Latin", "Hebrew"]\n'
                                 '    brute_triples=0,           # 0 = 4000 najczęstszych trójek; 35000 = wszystkie (kilka godzin)\n'
                                 '    brute_tokenize="glyphs",   # albo "chars": litery EVA bez łączenia ch, sh, cth...')),
    ("code", """lab.run("brute")
lab.convene(["brute"])
lab.report(); lab.push()
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "brute.md").read_text()))"""),
]


# One task, maximal GPU load: the wheel (volvelle) search, the transformer judge, medieval genres.
wheel_cells = [
    ("md", """# Voynich Lab – odjechane pomysły średniowieczne na GPU

Trzy testy w jednym przebiegu, każdy obciąża GPU do oporu:

| teoria | co sprawdza |
|---|---|
| `wheel` | tarcza Llulla (volvelle): populacja tarcz o 3 pierścieniach ewoluuje na GPU, aż składa słownictwo rękopisu najtańszym obrotem; to samo dla tekstów kontrolnych; najlepsza tarcza pisze tekst, który idzie przez kartę miar, klasyfikator, składnię i długości |
| `adversary` | transformer-sędzia uczony na GPU: czy odróżni wiersze każdego generatora bez treści (v4, v5, łańcuch, tarcza) od prawdziwych; kontrola prawdziwe vs prawdziwe |
| `genres` | gatunki bez składni: litania do Wszystkich Świętych i imiona barbarzyńskie z Ars Notoria i Liber Iuratus mierzone jak rękopis (składnia na odległość, dynamika długości, kształt) |

Uruchom: Środowisko wykonawcze → Uruchom wszystko (GPU A100, High-RAM, sekrety `GITHUB_TOKEN`, `OPENROUTER_API_KEY`).
Po pobraniu poprawki kodu zawsze: Środowisko wykonawcze → Uruchom ponownie sesję, inaczej Python trzyma stare moduły.
Czas: ok. 2–3 h na A100 przy ustawieniach poniżej; `quick=True` daje próbę w kilkanaście minut."""),
    cells[3],
    ("code", """!pip install -q open_clip_torch
!python scripts/fetch_data.py
!python scripts/fetch_lexicons.py --local   # łacina i angielski do odsiewu zwykłych słów z imion
!python scripts/fetch_genres.py            # litania (la.wikisource) i imiona (Esoteric Archives)"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]',
                                 'theories=["wheel", "adversary", "genres"],\n'
                                 '    wheel_rings=3,             # pierścienie tarczy\n'
                                 '    wheel_cells=24,            # komórek na pierścień (0–3 glify każda)\n'
                                 '    wheel_population=2048,     # tarcz w populacji (A100: 2048; L4: 512)\n'
                                 '    wheel_generations=2000,    # pokoleń ewolucji (4 teksty × pokolenia)\n'
                                 '    judge_epochs=20,           # epoki transformera-sędziego na każdy generator')),
    ("code", """for name in ("wheel", "adversary", "genres"):
    lab.run(name)
    lab.push()                     # po każdym teście na GitHub, gdyby sesja padła
lab.convene(["wheel", "adversary", "genres"])
lab.report(); lab.push()
from IPython.display import Markdown, display
for name in ("wheel", "adversary", "genres"):
    display(Markdown((lab.cfg.results_dir / f"{name}.md").read_text()))"""),
]


# One task: the attacks borrowed from the decipherment literature, plus the transliteration check.
attack_cells = [
    ("md", """# Voynich Lab – łamacze z literatury na GPU

| teoria | co sprawdza |
|---|---|
| `phonotactics` | czy słowa mają budowę mowy: samogłoski Suchotina, wzorce spółgłoska–samogłoska rękopisu wobec ~50 języków i abdżadów |
| `transcriptions` | czy podpis rękopisu (brak dalekiej składni, nadmiar powtórzeń, podobne długości sąsiadów) trzyma w transliteracjach Curriera, FSG, v101, Takahashiego i Reference, nie tylko w ZL |
| `cognate` | NeuroDecipher (MIT): miękki klucz glif–litera, transport optymalny między słownictwem rękopisu a słownikiem każdego z ~50 języków, spadek gradientu, 32 starty w jednej paczce na GPU; kontrola na zaszyfrowanym tekście z szumem pisowni |
| `hillclimb` | atak homofoniczny jak w AZdecrypt: model 4-gramowy znaków, 8192 wspinaczy równolegle na GPU, klucz z wierszy nieparzystych oceniany na parzystych; kontrola na tekście zaszyfrowanym homofonicznie |

Uruchom: Środowisko wykonawcze → Uruchom wszystko (GPU A100, High-RAM, sekrety `GITHUB_TOKEN`, `OPENROUTER_API_KEY`).
Po pobraniu poprawki kodu zawsze: Środowisko wykonawcze → Uruchom ponownie sesję. Czas: ok. 2–4 h na A100."""),
    cells[3],
    ("code", """!pip install -q open_clip_torch
!python scripts/fetch_data.py
!python scripts/fetch_lexicons.py             # słowniki ~50 języków epoki (~2 min)
!python scripts/fetch_transliterations.py     # inne transliteracje z voynich.nu"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]',
                                 'theories=["phonotactics", "transcriptions", "cognate", "hillclimb"],\n'
                                 '    attack_languages=[],       # puste = wszystkie leksykony; np. ["Latin", "Italian"]\n'
                                 '    cognate_restarts=32,       # starty w jednej paczce na GPU\n'
                                 '    cognate_steps=600,\n'
                                 '    climb_population=8192,     # wspinaczy równolegle\n'
                                 '    climb_steps=3000,')),
    ("code", """for name in ("phonotactics", "transcriptions", "cognate", "hillclimb"):
    lab.run(name)
    lab.push()                     # po każdym teście na GitHub, gdyby sesja padła
lab.convene(["phonotactics", "transcriptions", "cognate", "hillclimb"])
lab.report(); lab.push()
from IPython.display import Markdown, display
for name in ("phonotactics", "transcriptions", "cognate", "hillclimb"):
    display(Markdown((lab.cfg.results_dir / f"{name}.md").read_text()))"""),
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
for name, cs in (("Voynich_Lab.ipynb", cells), ("Voynich_Ilustracje.ipynb", illustrations_cells),
                 ("Voynich_Brute.ipynb", brute_cells), ("Voynich_Kolo.ipynb", wheel_cells),
                 ("Voynich_Lamacze.ipynb", attack_cells)):
    out = Path(__file__).with_name(name)
    out.write_text(json.dumps({**nb, "cells": [cell(k, t) for k, t in cs]}, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", out)
