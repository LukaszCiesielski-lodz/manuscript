"""Theory 2: the key to the text is in the illustrations.

If the drawings hold the key, the text must at least depend on them. Three tests,
from cheapest to most expensive:

A. Layout (CPU). The transliteration marks where a drawing interrupts a line
   (<->). Words right before and after a drawing are compared with words from
   random positions in the same lines (as in "Subtle Signs of Scribal
   Intent", arXiv:2404.13069). A difference shows the scribe wrote around
   finished drawings; it says nothing about what the words mean.

B. Picture-text agreement (GPU). Herbal folios are embedded with CLIP; folio
   texts are compared by word profiles. A Mantel test asks whether folios with
   similar plants carry similar words, with permutations kept inside the same
   scribe and Currier language so the scribe's style cannot fake the effect.

C. Plant names as cribs (OpenRouter vision model). A vision model names the
   plant on each herbal folio without seeing any transcription. A simulated
   annealing search then looks for one glyph->letter key that turns the first
   word of many folios into the beginning of their plant names. The same search
   on names shuffled between folios gives the null distribution; names planted
   with a known key are the positive control.
"""

from __future__ import annotations

import json
import math
import time
import unicodedata

from ... import corpus, eva
from ..common import permutation_p, rng
from ..config import LabConfig
from ..results import TheoryResult

# Medieval herbal plant names, used to build controls when no vision model is available.
HERBAL_NAMES = """absinthium agrimonia allium althaea anethum angelica apium arnica artemisia asarum betonica
borago buglossa calendula camomilla cannabis capparis carduus centaurea chelidonium cichorium coriandrum
crocus cuminum cynoglossum dictamnus elleborus eruca eupatorium faeniculum filix fragaria gentiana
glycyrrhiza hedera helleborus hypericum hyssopus iris iuniperus lactuca lavandula levisticum lilium
malva mandragora marrubium melissa mentha millefolium nasturtium nepeta origanum paeonia papaver
petroselinum plantago portulaca pulegium rosa rosmarinus ruta salvia sambucus satureia scabiosa
serpyllum solanum symphytum tanacetum thymus urtica valeriana verbena viola""".split()


def norm_name(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if c.isalpha() and c.isascii()).replace("j", "i").replace("v", "u")


# ---------- A. words next to drawings

def drawing_gaps() -> list[tuple[list[str], set[int]]]:
    """Paragraph lines interrupted by a drawing: (words, indices of words standing right before a gap)."""
    from ... import ivtff
    out = []
    for page in ivtff.parse(corpus.ZL_FILE):
        for loc in page.loci:
            if not loc.kind.startswith("P") or "<->" not in loc.raw:
                continue
            parts = [eva.words(eva.clean(p)) for p in loc.raw.split("<->")]
            words, before, idx = [], set(), 0
            for k, part in enumerate(parts):
                words += part
                idx += len(part)
                if k < len(parts) - 1 and 0 < idx < len(words) + 1:
                    before.add(idx - 1)
            if len(words) >= 4 and before:
                out.append((words, before))
    return out


def layout_test(cfg: LabConfig, r, res: TheoryResult) -> dict:
    gaps = drawing_gaps()
    glen = lambda w: len(eva.glyphs(w))

    def stat(gs) -> float:
        b = [glen(words[i]) for words, pos in gs for i in pos if 0 < i < len(words) - 1]
        rest = [glen(w) for words, pos in gs for i, w in enumerate(words) if i not in pos and 0 < i < len(words) - 1]
        return sum(b) / max(1, len(b)) - sum(rest) / max(1, len(rest))

    obs = stat(gaps)
    trials = 300 if cfg.quick else 3000
    null = []
    for _ in range(trials):
        fake = [(words, set(r.sample(range(1, len(words) - 1), min(len(pos), len(words) - 2)))) for words, pos in gaps]
        null.append(stat(fake))
    p = permutation_p(abs(obs), [abs(x) for x in null], smaller_is_extreme=False)
    # Positive control: shorten every word before a gap by one glyph and check the test notices.
    planted = [([w[:-1] if i in pos and len(w) > 2 else w for i, w in enumerate(words)], pos) for words, pos in gaps]
    p_planted = permutation_p(abs(stat(planted)), [abs(x) for x in null], smaller_is_extreme=False)
    res.control("A: podłożone skrócenie słów przed rysunkiem", "wykryte (p < 0,01)", f"p = {p_planted:.4f}", p_planted < 0.01)
    res.evidence.append(f"A: {len(gaps)} wierszy przerwanych rysunkiem. Słowo przed rysunkiem różni się długością o "
                        f"{obs:+.2f} glifu od słów w środku wiersza, p = {p:.4f}.")
    return {"lines": len(gaps), "length_difference": obs, "p": p, "p_planted": p_planted}


# ---------- C. plant names as cribs

def _first_words(folios: list[str]) -> dict[str, list[str]]:
    lines = corpus.load_voynich()
    out = {}
    for f in folios:
        for l in lines:
            if l.folio == f and l.kind.startswith("P") and l.words:
                out[f] = eva.glyphs(l.words[0])
                break
    return out


def crib_score(key: dict, words: dict, names: dict, k: int = 4) -> float:
    """Sum over folios of the best prefix agreement (0..1) between the decrypted first word and a name."""
    total = 0.0
    for f, w in words.items():
        dec = "".join(key.get(g, "?") for g in w)[:k]
        best = 0
        for n in names.get(f, ()):
            m = 0
            while m < min(len(dec), len(n), k) and dec[m] == n[m]:
                m += 1
            best = max(best, m)
        total += best / k
    return total / max(1, len(words))


def crib_attack(words: dict, names: dict, r, steps: int) -> float:
    letters = sorted({c for ns in names.values() for n in ns for c in n}) or list("abcdefghilmnoprstu")
    glyphs = sorted({g for w in words.values() for g in w})
    key = {g: r.choice(letters) for g in glyphs}
    score = best = crib_score(key, words, names)
    for step in range(steps):
        t = 0.05 * (1 - step / steps) + 1e-4
        g = r.choice(glyphs)
        old = key[g]
        key[g] = r.choice(letters)
        new = crib_score(key, words, names)
        if new >= score or r.random() < math.exp((new - score) / t):
            score = new
            best = max(best, score)
        else:
            key[g] = old
    return best


# Run 20261022-175027 found a weak crib signal (p = 0.04) on these pages; they are left out of the repeat.
CRIB_DISCOVERY = {"f1v", "f2r", "f2v", "f3r", "f3v", "f4r", "f4v", "f5r", "f5v", "f6r", "f6v", "f7r", "f7v",
                  "f8r", "f8v", "f9r", "f9v", "f10r", "f10v", "f11r"}


def crib_test(words: dict, names: dict, cfg: LabConfig, r, shuffles: int | None = None) -> tuple[float, list[float], float]:
    steps = 1200 if cfg.quick else 6000
    shuffles = shuffles or (19 if cfg.quick else 49)  # 19 is the fewest that can reach p < 0.05
    obs = crib_attack(words, names, r, steps)
    folios = list(names)
    null = []
    for _ in range(shuffles):
        perm = folios[:]
        r.shuffle(perm)
        null.append(crib_attack(words, {f: names[g] for f, g in zip(folios, perm)}, r, steps))
    return obs, null, permutation_p(obs, null, smaller_is_extreme=False)


def vlm_plant_names(folios: dict, cfg: LabConfig, client, model: str) -> dict[str, list[str]]:
    from ..openrouter import image_part, parse_json
    prompt = ("To jest strona średniowiecznego zielnika. Zidentyfikuj roślinę na rysunku (tylko na podstawie rysunku; "
              "nie próbuj czytać tekstu). Podaj do 3 kandydatów. Odpowiedz JSON: "
              '{"kandydaci": [{"łacina": "...", "włoski": "...", "niemiecki": "...", "pewność": 0-1}]}')
    out = {}
    for f, path in folios.items():
        try:
            text = client.chat(model, [{"role": "user", "content": [{"type": "text", "text": prompt},
                                                                     image_part(path.read_bytes())]}], 600)
        except Exception as e:  # budget or API error: keep what we have
            print(f"  VLM {f}: {e}")
            break
        cands = parse_json(text).get("kandydaci") or []
        names = []
        for c in cands:
            for k in ("łacina", "włoski", "niemiecki"):
                v = c.get(k)
                if v:
                    names += [norm_name(x) for x in str(v).replace(",", " ").split()[:1]]
        out[f] = [n for n in dict.fromkeys(names) if len(n) >= 3]
    return out


# ---------- B. picture-text agreement

def mantel(a, b, strata, trials: int, r) -> tuple[float, float]:
    """Spearman-free Pearson Mantel statistic with permutations inside strata."""
    import numpy as np
    n = len(a)
    iu = np.triu_indices(n, 1)
    x = a[iu]

    def corr(order):
        y = b[np.ix_(order, order)][iu]
        return float(np.corrcoef(x, y)[0, 1])

    base = list(range(n))
    obs = corr(base)
    groups: dict = {}
    for i, s in enumerate(strata):
        groups.setdefault(s, []).append(i)
    null = []
    for _ in range(trials):
        order = base[:]
        for idx in groups.values():
            sh = idx[:]
            r.shuffle(sh)
            for i, j in zip(idx, sh):
                order[i] = j
        null.append(corr(order))
    return obs, permutation_p(obs, null, smaller_is_extreme=False)


def text_similarity(folio_words: list[list[str]]):
    import numpy as np
    vocab = {w: i for i, w in enumerate(sorted({w for ws in folio_words for w in ws}))}
    df = np.zeros(len(vocab))
    m = np.zeros((len(folio_words), len(vocab)))
    for i, ws in enumerate(folio_words):
        for w in ws:
            m[i, vocab[w]] += 1
        df[[vocab[w] for w in set(ws)]] += 1
    m = np.log1p(m) * np.log(len(folio_words) / df)
    m /= np.linalg.norm(m, axis=1, keepdims=True) + 1e-9
    return m @ m.T


def clip_similarity(paths, cfg: LabConfig):
    import numpy as np
    import open_clip  # type: ignore
    import torch  # type: ignore
    from PIL import Image  # type: ignore
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, _, preprocess = open_clip.create_model_and_transforms(cfg.clip_model, pretrained=cfg.clip_pretrained, device=device)
    model.eval()
    feats = []
    with torch.no_grad():
        for p in paths:
            img = preprocess(Image.open(p).convert("RGB")).unsqueeze(0).to(device)
            f = model.encode_image(img)
            feats.append((f / f.norm(dim=-1, keepdim=True)).cpu().numpy()[0])
    e = np.stack(feats)
    return e @ e.T


def run(cfg: LabConfig, client=None, vision_model: str = "") -> TheoryResult:
    t0 = time.time()
    r = rng(cfg.seed)
    res = TheoryResult(
        theory="illustrations",
        hypothesis="Klucz do tekstu kryje się w ilustracjach: tekst zależy od rysunków (np. pierwsze słowo strony zielnika to zaszyfrowana nazwa rośliny).",
        method=("A: długość słów przy przerwach na rysunek (test permutacyjny). B: test Mantela – podobieństwo obrazów CLIP "
                "a podobieństwo słownictwa stron zielnika, permutacje w obrębie skryby i języka Curriera. C: atak z "
                "nazwami roślin od modelu wizyjnego jako 'cribami' (wyżarzanie klucza glif→litera) wobec nazw przetasowanych."),
        references=["Subtle Signs of Scribal Intent in the Voynich Manuscript, arXiv:2404.13069",
                    "Topic Modeling in the Voynich Manuscript, arXiv:2107.02858",
                    "A Generative Grammar Underlying the Voynich Manuscript (pastiche hypothesis), arXiv:2609.20835",
                    "Bax, A proposed partial decoding of the Voynich script (2014)"],
    )
    metrics = {"layout": layout_test(cfg, r, res)}

    lines = corpus.load_voynich()
    herbal = []
    for l in lines:
        if l.section == "herbal" and l.kind.startswith("P") and l.folio not in herbal:
            herbal.append(l.folio)
    words = _first_words(herbal)

    # C, positive control: names planted with a known key must be found.
    names_ctrl, words_ctrl = {}, {}
    glyph_alphabet = sorted({g for w in words.values() for g in w})
    true_key = {}
    for f in list(words)[: (40 if cfg.quick else 100)]:
        name = r.choice(HERBAL_NAMES)
        letters = list(name[:4])
        for c in letters:
            true_key.setdefault(c, r.choice(glyph_alphabet))
        words_ctrl[f] = [true_key[c] for c in letters]
        names_ctrl[f] = [name] + r.sample(HERBAL_NAMES, 2)
    obs_c, null_c, p_c = crib_test(words_ctrl, names_ctrl, cfg, r)
    res.control("C: nazwy podłożone znanym kluczem", "atak je znajduje (p ≤ 0,05)",
                f"wynik {obs_c:.2f} wobec {max(null_c):.2f} (max dla przetasowanych), p = {p_c:.3f}", p_c <= 0.05)
    metrics["crib_control"] = {"observed": obs_c, "null": null_c, "p": p_c}

    supported = refuted = False
    paths = {}
    if client is not None and vision_model:
        from ..images import fetch_folios
        target = herbal[: cfg.vlm_folios_limit] if cfg.vlm_folios_limit else herbal
        try:
            paths = fetch_folios(target, cfg.image_width, cfg.cache_dir / "folios", cfg.images_dir)
        except OSError as e:
            paths = {}
            res.evidence.append(f"C: pominięte, brak skanów ({e}).")
        names = vlm_plant_names(paths, cfg, client, vision_model) if paths else {}
        (cfg.results_dir / "plant_names.json").parent.mkdir(parents=True, exist_ok=True)
        (cfg.results_dir / "plant_names.json").write_text(json.dumps(names, ensure_ascii=False, indent=1))
        res.artifacts.append("plant_names.json")
        w = {f: words[f] for f in names if f in words and names[f]}
        fresh = {f: v for f, v in w.items() if f not in CRIB_DISCOVERY}
        if len(fresh) >= 30:
            # Confirmatory test: only pages the earlier run never saw, so the p = 0.04 there cannot carry over.
            obs, null, p = crib_test(fresh, {f: names[f] for f in fresh}, cfg, r, shuffles=99)
            metrics["crib"] = {"folios": len(fresh), "observed": obs, "null": null, "p": p, "model": vision_model,
                               "set": "potwierdzający (bez 20 stron z odkrycia)"}
            res.evidence.append(f"C (powtórka na {len(fresh)} nowych stronach, nazwy od {vision_model}): dopasowanie "
                                f"{obs:.2f} wobec średnio {sum(null) / len(null):.2f} dla nazw przetasowanych, p = {p:.3f}. "
                                f"Wcześniej na 20 stronach f1v–f11r: 0,40 wobec 0,33, p = 0,04.")
            supported |= p <= 0.01
            refuted = p > 0.2
        elif len(w) >= 15:
            obs, null, p = crib_test(w, {f: names[f] for f in w}, cfg, r)
            metrics["crib"] = {"folios": len(w), "observed": obs, "null": null, "p": p, "model": vision_model}
            res.evidence.append(f"C: {len(w)} stron, nazwy od {vision_model}. Dopasowanie {obs:.2f} wobec średnio "
                                f"{sum(null) / len(null):.2f} dla nazw przetasowanych, p = {p:.3f}.")
            supported |= p <= 0.02  # the best this many shuffles can show
            refuted = p > 0.2
    else:
        res.evidence.append("C: pominięte (brak klucza OpenRouter lub modelu wizyjnego).")

    try:
        import numpy as np
        from ..images import fetch_folios
        # All herbal folios for the Mantel test; ones already fetched for part C come from the cache.
        paths = {**paths, **fetch_folios(herbal, cfg.image_width, cfg.cache_dir / "folios", cfg.images_dir)}
        folios = [f for f in herbal if f in paths]
        img = clip_similarity([paths[f] for f in folios], cfg)
        fw = {f: [w for l in lines if l.folio == f and l.kind.startswith("P") for w in l.words] for f in folios}
        txt = text_similarity([fw[f] for f in folios])
        meta = {l.folio: (l.language, l.hand) for l in lines}
        strata = [meta.get(f, ("?", "?")) for f in folios]
        trials = 500 if cfg.quick else 5000
        obs, p = mantel(img, txt, strata, trials, r)
        # Positive control: two halves of each folio's text must agree with each other.
        halves = [(ws[: len(ws) // 2], ws[len(ws) // 2:]) for ws in (fw[f] for f in folios)]
        ta, tb = text_similarity([h[0] for h in halves]), text_similarity([h[1] for h in halves])
        obs_ctrl, p_ctrl = mantel(ta, tb, strata, trials, r)
        res.control("B: połowy tekstu tej samej strony", "zgodne (p < 0,01)", f"r = {obs_ctrl:.2f}, p = {p_ctrl:.4f}",
                    p_ctrl < 0.01)
        # One random matrix reaches p < 0.05 one time in twenty by design (Colab: p = 0.025 once), so calibrate
        # over 20 random matrices: the false-alarm rate should stay near 5%.
        noise_ps = []
        for _ in range(20):
            noise = np.array([[r.random() for _ in folios] for _ in folios])
            noise_ps.append(mantel((noise + noise.T) / 2, txt, strata, 200, r)[1])
        alarms = sum(q < 0.05 for q in noise_ps)
        p_n = alarms / len(noise_ps)
        res.control("B: losowe podobieństwa obrazów", "fałszywe alarmy (p < 0,05) w najwyżej 3 z 20 losowych macierzy",
                    f"{alarms}/20", alarms <= 3)
        metrics["mantel"] = {"folios": len(folios), "r": obs, "p": p, "control_r": obs_ctrl, "noise_false_alarm_rate": p_n}
        res.evidence.append(f"B: {len(folios)} stron zielnika. Korelacja podobieństwa obrazów i słownictwa r = {obs:.3f}, "
                            f"p = {p:.4f} (permutacje w obrębie skryby i języka).")
        supported |= p < 0.01
        refuted = refuted and p > 0.2
    except ImportError as e:
        res.evidence.append(f"B: pominięte (brak biblioteki: {e.name}; uruchom w Colabie z GPU).")
    except OSError as e:
        res.evidence.append(f"B: pominięte (nie udało się pobrać skanów: {e}).")

    res.metrics = metrics
    res.decide(True if supported else False if refuted else None)
    res.summary = ("Test sprawdza warunek konieczny klucza w ilustracjach: czy tekst w ogóle zależy od rysunku. "
                   + " ".join(e for e in res.evidence if e.startswith(("B:", "C:", "C ("))))
    res.caveats += [
        "Związek tekstu z rysunkiem (B) byłby warunkiem koniecznym, ale nie dowodem klucza: tekst o roślinie też zależy od rośliny.",
        "Identyfikacje roślin przez model wizyjny są niepewne; botanicy nie zgadzają się co do większości roślin rękopisu.",
        "Atak C zakłada, że pierwsze słowo strony to nazwa rośliny zapisana szyfrem podstawieniowym od początku słowa.",
        "CLIP widzi całą stronę razem z pismem; podobny układ tekstu może podbijać podobieństwo obrazów.",
    ]
    res.seconds = time.time() - t0
    return res
