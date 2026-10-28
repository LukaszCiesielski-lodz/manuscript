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
    ("code", 'lab.run("naibbe_cipher"); lab.run("cardan_grille"); lab.run("hebrew_anagram"); lab.run("basque"); lab.run("nomenclator"); lab.run("hoax"); lab.run("syntax"); lab.run("romance"); lab.run("lengths"); lab.run("phonotactics"); lab.run("length_code"); lab.run("chronology"); lab.run("hands");'),
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


# The closing run: every theory the council asked controls for, with those controls, plus the three CPU theories
# added last (length code, arrow of time, scribal hands).
final_cells = [
    ("md", """# Voynich Lab – przebieg zamykający

Jeden notebook domyka etap: teorie, którym rada wytknęła brak kontroli, idą ponownie z kontrolami dodatnimi
i ujemnymi, a trzy ostatnie teorie z procesora liczą się po raz pierwszy na pełnych ustawieniach.

| teoria | co nowego |
|---|---|
| `length_code`, `chronology`, `hands` | kod w długościach słów; strzałka czasu kopiowania między kartami (tło w obrębie bloków działu); ręka skryby a treść (karty odłożone, tło z losowego rozdania kart) |
| `genres`, `notation` | + rama wszczepiona w rękopis (musi dać zależność), litania i chorał przetasowane (muszą ją stracić); notacja z pełną tabulaturą basse danse, gdy PDF dostępny |
| `adversary` | + czułość sędziego (10% glifów podmienionych musi wykryć), AUC z trzech podziałów danych |
| `hillclimb` | + glify przemianowane w każdym wierszu (tekst bez klucza) obok bełkotu v5; 51 języków, ok. 40 min |
| `cognate` | + ta sama kontrola; tylko języki, w których coś drgnęło lub które pasują do epoki (lista w ustawieniach) |
| `wheel` | + tekst napisany znaną tarczą: wyszukiwanie musi ją odzyskać; mniejsza populacja, bo wynik już znamy |

Uruchom: Środowisko wykonawcze → Uruchom wszystko (GPU A100, High-RAM, sekrety `GITHUB_TOKEN`, `OPENROUTER_API_KEY`).
Po pobraniu poprawki kodu zawsze: Środowisko wykonawcze → Uruchom ponownie sesję. Czas: ok. 3 h; wyniki wypychają się po każdej teorii."""),
    cells[3],
    ("code", """!pip install -q open_clip_torch pypdf
!python scripts/fetch_data.py
!python scripts/fetch_lexicons.py
!python scripts/fetch_transliterations.py
!python scripts/fetch_notation.py"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]',
                                 'theories=["length_code", "chronology", "hands", "genres", "notation", "adversary", "hillclimb", "cognate", "wheel"],\n'
                                 '    attack_languages=["Syriac", "Aramaic", "Latin", "MedievalLatin", "VulgarLatin", "Italian", "German",\n'
                                 '                      "OldFrench", "Hebrew", "Greek", "Czech", "Lithuanian", "Portuguese"],  # tylko cognate; hillclimb bierze wszystkie\n'
                                 '    cognate_restarts=32,\n'
                                 '    cognate_steps=600,\n'
                                 '    climb_population=8192,\n'
                                 '    climb_steps=3000,\n'
                                 '    wheel_population=1024,\n'
                                 '    wheel_generations=800,\n'
                                 '    judge_epochs=20,')),
    ("code", """cpu = ["length_code", "chronology", "hands", "genres", "notation"]
gpu = ["adversary", "hillclimb", "cognate", "wheel"]
for name in cpu + gpu:
    if name == "hillclimb":
        lab.cfg.attack_languages = []            # wspinaczka: wszystkie leksykony (ok. 40 min)
    elif name == "cognate":
        lab.cfg.attack_languages = cfg.attack_languages
    lab.run(name)
    lab.push()                                   # po każdej teorii na GitHub, gdyby sesja padła
lab.convene(cpu + gpu)
lab.report(); lab.push()
from IPython.display import Markdown, display
for name in cpu + gpu:
    display(Markdown((lab.cfg.results_dir / f"{name}.md").read_text()))"""),
]


# One task on the CPU: is the manuscript a notation rather than speech?
notation_cells = [
    ("md", """# Voynich Lab – zapis niejęzykowy? Chorał, tabulatura tańca, program

Czy rękopis statystycznie przypomina notacje średniowieczne bardziej niż mowę? Chorał gregoriański z bazy Cantus
(63 tys. melodii w Volpiano; jednostki: słowa tekstu, sylaby, neumy), tabulatura kroków basse danse (Bruksela 9085,
ok. 1470), kod Pythona jako kontrast, łacina i bełkot v5 idą przez tę samą baterię: składnia na odległość rozbita na
powtórzenia, warianty i jednostki niespokrewnione; dynamika długości; miary kształtu. Osiem kryteriów podpisu rękopisu,
z cechą definiującą: brak zależności między różnymi jednostkami na odległość.

Bez GPU (wystarczy CPU, High-RAM niepotrzebny). Sekrety: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. Czas: ok. 15 min."""),
    cells[3],
    ("code", """!pip install -q pypdf
!python scripts/fetch_data.py
!python scripts/fetch_notation.py      # CantusCorpus (38 MB) i, gdy dostępne, pełne wydanie basse danse (PDF przez pypdf)"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]', 'theories=["notation"],')),
    ("code", """lab.run("notation"); lab.push()
lab.convene(["notation"])
lab.report(); lab.push()
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "notation.md").read_text()))"""),
]


# The record track, CPU part: labels as names, lines as records, medieval lists. No GPU units spent.
rejestr_cells = [
    ("md", """# Voynich Lab – zapis rekordowy (część CPU): etykiety, rekordy, listy

Hipoteza nietekstowa po wykluczeniu melodii, tańca i programu: tekst to **zapis rekordowy** (wiersz = rekord o polach,
strona = wpis z nagłówkiem, słownictwo = nomenklatura), bez gramatyki między rekordami. Trzy teorie na CPU:

| teoria | co sprawdza | czas |
|---|---|---|
| `labels` | czy słowa przy rysunkach to osobny podsłownik nazw (hapaksy, inicjały o-/q-, długość wobec losowań słów akapitów) i czy akapity strony cytują jej etykiety (wobec etykiet innych stron działu) | 3 min |
| `records` | czy miejsce słowa w wierszu da się odczytać z samego słowa (klasyfikator z odłożonymi kartami, wnętrze wiersza), informacja wzajemna klasy słowa i miejsca, przewidywanie pola z sąsiadów; wobec łaciny, chorału, bełkotu v5 i list | 10 min |
| `lists` | podpis rękopisu (8 kryteriów) wobec martyrologium Usuarda, Apicjusza i glosariusza Alphita; gradient proza → listy → rękopis | 15 min |

**Runtime bez akceleratora** (Runtime → Change runtime type → CPU): zero jednostek GPU. Sekrety: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`.
Część GPU (`Voynich_Rejestr_GPU.ipynb`) uruchamia się potem, osobno."""),
    cells[3],
    ("code", """!python scripts/fetch_data.py
!python scripts/fetch_notation.py 2>/dev/null || true   # chorał do porównania w `records` (opcjonalnie)
!python scripts/fetch_lists.py                           # korpusy list są w repozytorium; skrypt tylko potwierdza"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]', 'theories=["rejestr"],')),
    ("code", """for name in ["labels", "records", "lists"]:
    lab.run(name)
    lab.push()                                   # po każdej teorii na GitHub
lab.convene(["labels", "records", "lists"])
lab.report(); lab.push()
from IPython.display import Markdown, display
for name in ["labels", "records", "lists"]:
    display(Markdown((lab.cfg.results_dir / f"{name}.md").read_text()))"""),
]


# The record track, GPU part: position-token GPT, evolved generator v6 with the transformer judge, page cohesion.
rejestr_gpu_cells = [
    ("md", """# Voynich Lab – zapis rekordowy (część GPU): pola, generator v6, spójność strony

Dalszy ciąg `Voynich_Rejestr.ipynb`. Jednostki GPU idą tylko tam, gdzie liczy się skala (budżet ok. 85 min na A100):

| kolejność | teoria | co sprawdza | min |
|---|---|---|---|
| 1 | `fields_lm` | mały GPT uczony dwa razy na każdym korpusie (tekst goły i z tokenem pozycji przed każdym słowem): zysk w bitach na znak = ile miejsce w wierszu mówi o słowie; rękopis wobec łaciny, chorału, bełkotu v5, martyrologium i Apicjusza; kontrole: pozycje losowe, rekordy syntetyczne | 25–30 |
| 2 | `v6` | ewolucja 18 ustawień generatora v5 z tłumieniem słów już użytych (CPU, pula procesów) na karcie foliałów nieparzystych; finaliści na parzystych; 5 najlepszych do sędziego-transformera z odniesieniami (prawdziwe wobec prawdziwych, czułość, v5) | 8 + 30 |
| 3 | `cohesion` | czy sędzia pozna dwa wiersze z tej samej strony wobec innych stron tego samego działu i dialektu; kontrole: wiersze rozdane na pseudostrony, łacina ze słowem strony | 6–8 |

**Runtime:** A100 (High-RAM). Sekrety: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. Wyniki wypychane po każdej teorii; w razie
braku czasu `cohesion` można pominąć (jest ostatnia)."""),
    cells[1],
    cells[3],
    ("code", """!python scripts/fetch_data.py
!python scripts/fetch_notation.py 2>/dev/null || true   # chorał (słowa) jako korpus porównawczy
!python scripts/fetch_lists.py"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]', 'theories=["rejestr_gpu"],')),
    ("code", """import os
lab.cfg.v6_workers = max(1, (os.cpu_count() or 2) - 1)   # ewolucja na wszystkich vCPU poza jednym
for name in ["fields_lm", "v6", "cohesion"]:
    lab.run(name)
    lab.push()                                   # po każdej teorii na GitHub
lab.convene(["fields_lm", "v6", "cohesion"])
lab.report(); lab.push()
from IPython.display import Markdown, display
for name in ["fields_lm", "v6", "cohesion"]:
    display(Markdown((lab.cfg.results_dir / f"{name}.md").read_text()))"""),
]


# One CPU task: are the spaces a key rather than word boundaries?
keystream_cells = [
    ("md", """# Voynich Lab – odstępy jako klucz zapisany w tekście

Czy „słowa” EVA są jednostkami tekstu, czy ciąg ich długości (w glifach albo w znakach EVA) jest kluczem, według którego
trzeba pociąć, przesunąć albo przeczytać strumień glifów? Teoria `keystream` stosuje rodzinę 31 takich reguł do rękopisu
i do bełkotu v5 o jego statystyce, mierzy jednostki składnią na odległość i informacją między sąsiadami, i ma kontrole:
łacina z odstępami przepisanymi regułą z rodziny musi zostać odzyskana, zwykła łacina nie może zyskać na żadnej regule.
Przy okazji mierzy nową cechę: sąsiednie słowa rękopisu niosą o sobie mniej informacji niż losowe słowa tej samej linii.

**Runtime bez akceleratora** (CPU): zero jednostek GPU. Sekrety: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. Czas: ok. 25 min."""),
    cells[3],
    ("code", """!python scripts/fetch_data.py"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]', 'theories=["keystream"],')),
    ("code", """lab.run("keystream"); lab.push()
lab.convene(["keystream"])
lab.report(); lab.push()
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "keystream.md").read_text()))"""),
]


# Generator v7 on the GPU: v6 plus neighbour avoidance and the 23rd measure; the transformer judge decides.
v7_cells = [
    ("md", """# Voynich Lab – generator v7: czy „unikanie sąsiada” domyka bełkot

Sąsiednie słowa rękopisu niosą o sobie mniej informacji niż dwa losowe słowa tej samej linii (z = −24), czego bełkot v5
(+11) ani v6 (+1,5) nie odtwarzają, a łacina ma +47. Diagnoza: to słownictwo krawędzi wiersza (pierwsze i ostatnie słowa
wierszy to osobny zasób całych słów, nie tylko glify p/m/g). v7 dodaje do generatora zasób słów otwierających i zamykających
wiersz (`p_edge`; przy 0,6–0,9 odtwarza miarę) i „unikanie sąsiada” (`neighbour_gamma`), a do karty 23. miarę (informacja
sąsiednich słów ponad losowe słowa linii). Ewolucja 20 ustawień na CPU (karta foliałów nieparzystych), finaliści na
parzystych, 5 najlepszych do sędziego-transformera na GPU.
Jeśli sędzia przestanie odróżniać (AUC ≤ prawdziwe wobec prawdziwych + 0,07), mechanizm skryby tłumaczy wszystko, co
umiemy zmierzyć; jeśli nie, zostaje coś jeszcze.

**Runtime:** A100 (High-RAM). Sekrety: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. Czas: ok. 40 min (8 CPU + 30 GPU)."""),
    cells[1],
    cells[3],
    ("code", """!python scripts/fetch_data.py"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]', 'theories=["v6"],')),
    ("code", """import os
lab.cfg.v6_workers = max(1, (os.cpu_count() or 2) - 1)
lab.run("v6"); lab.push()
lab.convene(["v6"])
lab.report(); lab.push()
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "v6.md").read_text()))"""),
]


# A key per word length, on the GPU: six languages, nine keys at once.
lengthkey_cells = [
    ("md", """# Voynich Lab – inny klucz dla każdej długości słowa

Czy skryba używał innego alfabetu podstawieniowego dla słów jedno-, dwu-, ..., dziewięcioglifowych (odstępy wybierają
klucz)? Glif w słowie o danej długości staje się osobnym symbolem, więc wspinaczka homofoniczna na GPU szuka dziewięciu
kluczy naraz. Więcej kluczy zawsze trochę pomaga, dlatego zysk rękopisu porównuje się z zyskiem bełkotu v5 i glifów
przemianowanych w każdym wierszu; łacina zaszyfrowana dziewięcioma kluczami musi zostać odzyskana. Sześć języków:
łacina, włoski, niemiecki, francuski, hiszpański, czeski.

**Runtime:** A100. Sekrety: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. Czas: ok. 1 h."""),
    cells[1],
    cells[3],
    ("code", """!python scripts/fetch_data.py
!python scripts/fetch_lexicons.py"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]', 'theories=["lengthkey"],')),
    ("code", """lab.run("lengthkey"); lab.push()
lab.convene(["lengthkey"])
lab.report(); lab.push()
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "lengthkey.md").read_text()))"""),
]


# Brute force per word-length set, on the GPU.
brute_length_cells = [
    ("md", """# Voynich Lab – brute force osobno na każdym zbiorze słów jednakowej długości

Słowa rękopisu podzielone na zbiory według długości (2, 3, ..., 8 glifów i 9+); każdy zbiór to osobny szyfr z własnym
kluczem, atakowany brute force trójka po trójce przeciw sześciu leksykonom (łacina, włoski, niemiecki, francuski,
hiszpański, czeski). Na każdym zbiorze to samo tło co w `brute`: bełkot v5 podzielony tak samo, słowa przetasowane, glify
przemianowane; kontrola dodatnia: tekst języka zaszyfrowany i podzielony według długości musi oddać klucz każdego zbioru.

**Runtime:** A100. Sekrety: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. Czas: ok. 30–40 min."""),
    cells[1],
    cells[3],
    ("code", """!python scripts/fetch_data.py
!python scripts/fetch_lexicons.py"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]', 'theories=["brute_length"],')),
    ("code", """lab.run("brute_length"); lab.push()
lab.convene(["brute_length"])
lab.report(); lab.push()
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "brute_length.md").read_text()))"""),
]


# What the judge sees (GPU, ~10 min) and the same plant twice (CPU, ~2 min).
judge_cells = [
    ("md", """# Voynich Lab – co widzi sędzia

Po v7 sędzia-transformer wciąż odróżnia bełkot od rękopisu (AUC 0,642), choć 21 z 23 miar jest trafionych. Ten notebook
uczy sędziego raz i go przepytuje: które cechy wiersza idą za jego wynikiem (hapaksy, słowa nieobecne w drugim korpusie,
długość, miejsce na stronie) i czy nadal odróżnia, gdy oba korpusy ograniczyć do wierszy z samych słów wspólnych
(słownictwo dopasowane). Jeśli wtedy AUC spada do poziomu prawdziwe–prawdziwe, ślad to słownictwo; jeśli zostaje, to szyk.

**Runtime:** A100. Sekrety: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. Czas: ok. 10 min."""),
    cells[1],
    cells[3],
    ("code", """!python scripts/fetch_data.py"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]', 'theories=["judge_probe"],')),
    ("code", """lab.run("judge_probe"); lab.push()
lab.convene(["judge_probe"])
lab.report(); lab.push()
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "judge_probe.md").read_text()))"""),
]

plants_cells = [
    ("md", """# Voynich Lab – ta sama roślina w dwóch miejscach

Zandbergen i Petersen wskazują fragmenty roślin w dziale farmaceutycznym, które są tą samą rośliną co rośliny zielnika
(9 par „ta sama”, 28 „podobna”). Jeśli tekst opisuje roślinę, obie strony dzielą słowa ponad losowe strony tego samego
języka Curriera. Kontrole: słowa partnera wszczepione w stronę (muszą zostać wykryte), pary przełączone losowo.

**Runtime bez akceleratora** (CPU). Sekrety: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. Czas: ok. 3 min."""),
    cells[3],
    ("code", """!python scripts/fetch_data.py"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]', 'theories=["plant_pairs"],')),
    ("code", """lab.run("plant_pairs"); lab.push()
lab.convene(["plant_pairs"])
lab.report(); lab.push()
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "plant_pairs.md").read_text()))"""),
]


atoms_cells = [
    ("md", """# Voynich Lab – atomy ilustracji (szkic z modelu widzącego + test rebusu)

Ilustracje rozebrane na atomy (jeden rekord na etykietę, cechy ze słownika `data/atoms/vocab.json`, zasady w
`data/atoms/README.md`). Ten notebook robi dwie rzeczy: (1) `atoms_draft`: model widzący obrazy opisuje nimfy
12 stron zodiaku w schemacie atomów i zapisuje szkic na `lab-results` (`atoms_draft/<strona>.json`, do poprawienia ręcznie
i scalenia z `data/atoms/`); (2) `atoms`: test, czy jakaś cecha rysunku przewiduje etykietę, z kontrolami; rusza naprawdę
dopiero przy ≥ 100 opisanych atomach, wcześniej sprawdza tylko metodę.

**Runtime bez akceleratora** (CPU). Sekrety: `GITHUB_TOKEN`, `OPENROUTER_API_KEY`. Czas: ok. 10 min, koszt modelu ok. 0,3 USD."""),
    cells[3],
    ("code", """!python scripts/fetch_data.py"""),
    cells[5],
    ("code", cells[7][1].replace('theories=["all"],          # albo np. ["numbers", "literature"]', 'theories=["atoms_draft", "atoms"],')),
    ("code", """lab.run("atoms_draft"); lab.push()
lab.run("atoms"); lab.push()
lab.report(); lab.push()
from IPython.display import Markdown, display
display(Markdown((lab.cfg.results_dir / "atoms_draft.md").read_text()))
display(Markdown((lab.cfg.results_dir / "atoms.md").read_text()))"""),
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
nb_cpu = {**nb, "metadata": {"colab": {"provenance": []}, "kernelspec": {"name": "python3", "display_name": "Python 3"},
                             "language_info": {"name": "python"}}}   # no accelerator: no GPU units
for name, cs in (("Voynich_Lab.ipynb", cells), ("Voynich_Ilustracje.ipynb", illustrations_cells),
                 ("Voynich_Brute.ipynb", brute_cells), ("Voynich_Kolo.ipynb", wheel_cells),
                 ("Voynich_Lamacze.ipynb", attack_cells),
                 ("Voynich_Final.ipynb", final_cells),
                 ("Voynich_Notacja.ipynb", notation_cells),
                 ("Voynich_Rejestr.ipynb", rejestr_cells), ("Voynich_Rejestr_GPU.ipynb", rejestr_gpu_cells),
                 ("Voynich_Klucz.ipynb", keystream_cells), ("Voynich_V7.ipynb", v7_cells),
                 ("Voynich_Klucz_Dlugosci.ipynb", lengthkey_cells), ("Voynich_Brute_Dlugosci.ipynb", brute_length_cells),
                 ("Voynich_Sedzia.ipynb", judge_cells), ("Voynich_Rosliny.ipynb", plants_cells),
                 ("Voynich_Atomy.ipynb", atoms_cells)):
    base = nb_cpu if name in ("Voynich_Rejestr.ipynb", "Voynich_Klucz.ipynb", "Voynich_Rosliny.ipynb", "Voynich_Atomy.ipynb") else nb
    out = Path(__file__).with_name(name)
    out.write_text(json.dumps({**base, "cells": [cell(k, t) for k, t in cs]}, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", out)
