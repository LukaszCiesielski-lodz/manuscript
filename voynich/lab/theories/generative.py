"""Theory 3: generative AI can fill in the missing pages.

Fourteen leaves are lost (folios 12, 59-64, 74, 91, 92, 97, 98, 109, 110).
Nothing can recover what was on them; what a model can do is write pages that
are statistically indistinguishable from the real ones. That is a testable
claim, and it doubles as a probe of the text: how much structure beyond
three glyphs does a transformer find?

Text (GPU): a character transformer is trained on the transliteration, page
by page, with tokens for section, Currier language and scribe. Held-out pages
measure bits per character against a trigram baseline. Pages are then
generated for each missing folio with the attributes of its neighbours.

Fidelity checks:
- distance of generated text from the real one on the shape measures;
- a classifier trained to tell real lines from generated ones (AUC 0.5 =
  indistinguishable). Controls: real vs real must give ~0.5, real vs the
  simple self-citation generator must give a high AUC;
- copying: share of generated lines that exist verbatim in the manuscript.

Images (optional, GPU, ~1 h on an A100): SDXL with a LoRA trained on the
folio scans draws pages for the missing folios. These are illustrations of a
style, not reconstructions; files are marked SYNTETYCZNE.
"""

from __future__ import annotations

import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path

from ... import corpus, eva, ivtff, selfcite
from ..common import distance, language_scales, profile, rng
from ..config import LabConfig
from ..images import MISSING_FOLIOS, base_folio, fetch_folios
from ..results import TheoryResult

SPECIAL = ["<pad>", "<page>", "<end>"]


# ---------- data

def page_records() -> list[dict]:
    """Pages in manuscript order with attributes and paragraph lines (EVA, '.' between words)."""
    out = []
    for p in ivtff.parse(corpus.ZL_FILE):
        lines = []
        for loc in p.loci:
            if loc.kind.startswith("P"):
                ws = eva.words(eva.clean(loc.raw))
                if ws:
                    lines.append(".".join(ws))
        if lines:
            out.append({"folio": p.folio, "section": p.section, "language": p.language, "hand": p.hand,
                        "quire": p.quire, "lines": lines})
    return out


def header(rec: dict) -> list[str]:
    return ["<page>", f"<S:{rec['section']}>", f"<L:{rec['language']}>", f"<H:{rec['hand']}>"]


class Vocab:
    def __init__(self, pages: list[dict]):
        heads = sorted({t for p in pages for t in header(p)[1:]})
        chars = sorted({c for p in pages for l in p["lines"] for c in l} | {"\n"})
        self.itos = SPECIAL + heads + chars
        self.stoi = {s: i for i, s in enumerate(self.itos)}

    def encode_page(self, rec: dict) -> list[int]:
        ids = [self.stoi[t] for t in header(rec) if t in self.stoi]
        for line in rec["lines"]:
            ids += [self.stoi[c] for c in line] + [self.stoi["\n"]]
        return ids + [self.stoi["<end>"]]

    def decode_lines(self, ids: list[int]) -> list[str]:
        text = "".join(self.itos[i] for i in ids if len(self.itos[i]) == 1)
        return [l for l in text.split("\n") if l]


POS_TOKENS = [f"<p:{i}>" for i in range(12)] + ["<p:12+>"]


class PosVocab:
    """Characters plus one token per word position in the line: <p:0>, <p:1>, ... <p:12+>.

    A model that reads the position token before each word gains on text whose words depend on
    their slot (records with fields) and nothing on text whose words do not.
    """

    def __init__(self, lines: list[str]):
        chars = sorted({c for l in lines for c in l} | {"\n"})
        self.itos = SPECIAL + POS_TOKENS + chars
        self.stoi = {s: i for i, s in enumerate(self.itos)}
        self.pos_ids = {self.stoi[t] for t in POS_TOKENS}
        self.keep = {self.stoi[c] for c in chars}          # tokens whose prediction is scored

    def encode(self, lines: list[str], mode: str = "none", seed: int = 1) -> list[int]:
        """Lines (words joined by '.') to ids; mode 'none' (plain text), 'pos' (position token before every word)
        or 'random' (a position token drawn at random: the control that must gain nothing)."""
        import random as _random
        rng = _random.Random(seed)
        ids = []
        for line in lines:
            words = line.split(".")
            for i, w in enumerate(words):
                if mode == "pos":
                    ids.append(self.stoi[POS_TOKENS[min(i, 12)]])
                elif mode == "random":
                    ids.append(self.stoi[POS_TOKENS[rng.randrange(13)]])
                ids += [self.stoi[c] for c in w]
                if i < len(words) - 1:
                    ids.append(self.stoi["."])
            ids.append(self.stoi["\n"])
        return ids


def missing_page_attributes(pages: list[dict]) -> dict[int, dict]:
    """Attributes for each lost folio, taken from the nearest surviving page before it."""
    by_num = {}
    for p in pages:
        n = int(base_folio(p["folio"])[1:-1])
        by_num.setdefault(n, p)
    out = {}
    for m in MISSING_FOLIOS:
        prev = max((n for n in by_num if n < m), default=min(by_num))
        nxt = min((n for n in by_num if n > m), default=max(by_num))
        src = by_num[prev]
        out[m] = {"section": src["section"], "language": src["language"], "hand": src["hand"],
                  "neighbours": [by_num[prev]["folio"], by_num[nxt]["folio"]]}
    return out


# ---------- model (PyTorch, imported lazily so the rest runs without it)

def build_model(vocab_size: int, cfg: LabConfig, block: int):
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    class Block(nn.Module):
        def __init__(self, d, h):
            super().__init__()
            self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
            self.qkv, self.proj = nn.Linear(d, 3 * d), nn.Linear(d, d)
            self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
            self.h = h
            self.drop = nn.Dropout(0.1)

        def forward(self, x):
            b, t, d = x.shape
            q, k, v = self.qkv(self.ln1(x)).split(d, dim=2)
            q, k, v = (z.view(b, t, self.h, d // self.h).transpose(1, 2) for z in (q, k, v))
            a = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=0.1 if self.training else 0.0)
            x = x + self.drop(self.proj(a.transpose(1, 2).reshape(b, t, d)))
            return x + self.drop(self.mlp(self.ln2(x)))

    class GPT(nn.Module):
        def __init__(self):
            super().__init__()
            d = cfg.gpt_width
            self.tok, self.pos = nn.Embedding(vocab_size, d), nn.Embedding(block, d)
            self.blocks = nn.ModuleList(Block(d, max(1, d // 64)) for _ in range(cfg.gpt_layers))
            self.ln, self.head = nn.LayerNorm(d), nn.Linear(d, vocab_size, bias=False)

        def forward(self, idx, targets=None):
            t = idx.shape[1]
            x = self.tok(idx) + self.pos(torch.arange(t, device=idx.device))
            for blk in self.blocks:
                x = blk(x)
            logits = self.head(self.ln(x))
            loss = None if targets is None else F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1),
                                                                ignore_index=0)
            return logits, loss

    return GPT()


def train_gpt(train_ids: list[int], val_ids: list[int], vocab, cfg: LabConfig, block: int = 256, keep: set[int] | None = None,
              test_ids: list[int] | None = None):
    """Train the character GPT; checkpoint chosen on one half of `val_ids`, bits reported on the other
    (or on `test_ids` when given, the checkpoint then chosen on all of `val_ids`).
    `keep`: score only these target tokens (characters, not position tokens)."""
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(cfg.seed)
    model = build_model(len(vocab.itos), cfg, block).to(device)
    data = torch.tensor(train_ids, dtype=torch.long)
    val = torch.tensor(val_ids, dtype=torch.long)
    steps = 300 if cfg.quick else cfg.gpt_steps
    # The corpus is small (~200k glyphs), so thousands of steps overfit (Colab: 1.73 -> 5.43 bit/glyph).
    # Choose the checkpoint on one half of the held-out pages and report bits on the other half.
    if test_ids is not None:
        pick, test = val, torch.tensor(test_ids, dtype=torch.long)
    else:
        half = len(val) // 2
        pick, test = val[:half], val[half:]
    every = max(1, steps // 40)
    best, best_state, stale = float("inf"), None, 0
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.1, betas=(0.9, 0.95))
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=6e-4, total_steps=steps, pct_start=0.05)
    amp = torch.autocast(device_type="cuda", dtype=torch.bfloat16) if device == "cuda" else torch.autocast("cpu", enabled=False)
    batch = 64
    log = []
    for step in range(steps):
        ix = torch.randint(len(data) - block - 1, (batch,))
        x = torch.stack([data[i:i + block] for i in ix]).to(device)
        y = torch.stack([data[i + 1:i + block + 1] for i in ix]).to(device)
        model.train()
        with amp:
            _, loss = model(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if step % every == 0 or step == steps - 1:
            vb = evaluate_bits(model, pick, block, device, keep)
            log.append({"step": step, "train_loss": float(loss), "val_bits": vb})
            print(f"  krok {step}: strata {float(loss):.3f}, walidacja {vb:.3f} bit/znak", flush=True)
            if vb < best:
                best, stale = vb, 0
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            else:
                stale += 1
                if stale >= 6:
                    print(f"  wczesne zatrzymanie: walidacja nie poprawia się od {stale * every} kroków", flush=True)
                    break
    if best_state is not None:
        model.load_state_dict(best_state)
    best_step = min(log, key=lambda e: e["val_bits"])["step"]
    test_bits = evaluate_bits(model, test, block, device, keep)
    print(f"  wybrano krok {best_step}; odłożona połowa testowa: {test_bits:.3f} bit/znak", flush=True)
    return model, {"log": log, "best_step": best_step, "test_bits": test_bits}


def token_losses(model, val, block: int, device: str):
    """Natural-log loss of every target token of `val` (the last partial block dropped), on the CPU."""
    import torch
    import torch.nn.functional as F
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(val) - block - 1, block):
            x = val[i:i + block].unsqueeze(0).to(device)
            y = val[i + 1:i + block + 1].to(device)
            logits, _ = model(x)
            out.append(F.cross_entropy(logits[0], y, reduction="none").float().cpu())
    return torch.cat(out) if out else torch.zeros(0)


def evaluate_bits(model, val, block: int, device: str, keep: set[int] | None = None) -> float:
    """Bits per token; with `keep`, bits per kept token (position tokens and padding excluded)."""
    import torch
    losses = token_losses(model, val, block, device)
    if not len(losses):
        return float("nan")
    targets = val[1:1 + len(losses)]
    mask = torch.ones(len(losses), dtype=torch.bool) if keep is None else torch.tensor([int(t) in keep for t in targets])
    return float(losses[mask].sum() / max(1, int(mask.sum()))) / math.log(2)


def line_bits(model, val, block: int, device: str, newline: int, keep: set[int]) -> list[tuple[float, int]]:
    """(summed bits, kept tokens) per line of `val`, lines delimited by the `newline` token; for paired bootstraps
    between encodings of the same lines."""
    import torch
    losses = token_losses(model, val, block, device)
    targets = val[1:1 + len(losses)]
    out, tot, n = [], 0.0, 0
    for loss, t in zip(losses.tolist(), targets.tolist()):
        if t in keep:
            tot += loss / math.log(2)
            n += 1
        if t == newline:
            out.append((tot, n))
            tot, n = 0.0, 0
    return out


def sample_page(model, vocab: Vocab, attrs: dict, n_lines: int, block: int, temperature: float = 0.9) -> list[str]:
    import torch
    device = next(model.parameters()).device
    rec = {"section": attrs["section"], "language": attrs["language"], "hand": attrs["hand"], "lines": []}
    ids = [vocab.stoi[t] for t in header(rec) if t in vocab.stoi]
    nl, end = vocab.stoi["\n"], vocab.stoi["<end>"]
    lines = 0
    model.eval()
    with torch.no_grad():
        while lines < n_lines and len(ids) < 6000:
            x = torch.tensor([ids[-block:]], device=device)
            logits, _ = model(x)
            probs = torch.softmax(logits[0, -1] / temperature, dim=-1)
            nxt = int(torch.multinomial(probs, 1))
            if nxt == end:
                break
            ids.append(nxt)
            lines += nxt == nl
    return vocab.decode_lines(ids)


# ---------- fidelity

def discriminator_auc(real: list[str], fake: list[str], seed: int) -> float:
    """Logistic regression on character n-grams of single lines; AUC on a held-out half."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    r = random.Random(seed)
    n = min(len(real), len(fake))
    real, fake = r.sample(real, n), r.sample(fake, n)
    X = real + fake
    y = [0] * n + [1] * n
    idx = list(range(2 * n))
    r.shuffle(idx)
    cut = len(idx) // 2
    tr, te = idx[:cut], idx[cut:]
    vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 4), min_df=2)
    Xtr = vec.fit_transform([X[i] for i in tr])
    clf = LogisticRegression(max_iter=2000, C=2.0).fit(Xtr, [y[i] for i in tr])
    scores = clf.predict_proba(vec.transform([X[i] for i in te]))[:, 1]
    return float(roc_auc_score([y[i] for i in te], scores))


def selfcite_lines(pages: list[dict], n_words: int, seed: int) -> list[str]:
    para = [l for p in pages for l in p["lines"]]
    seed_lines = [[eva.glyphs(w) for w in l.split(".")] for l in para[:3]]
    gen = selfcite.generate(seed_lines, n_words, [len(l.split(".")) for l in para], seed=seed)
    return [".".join("".join(w) for w in l) for l in gen]


# ---------- optional images

DIFFUSERS_VERSION = "0.31.0"
LORA_SCRIPT = (f"https://raw.githubusercontent.com/huggingface/diffusers/v{DIFFUSERS_VERSION}/examples/"
               "text_to_image/train_text_to_image_lora_sdxl.py")
SDXL = "stabilityai/stable-diffusion-xl-base-1.0"
SDXL_VAE = "madebyollin/sdxl-vae-fp16-fix"
CAPTION = {"herbal": "a page of a 15th-century herbal manuscript with one large hand-drawn plant and paragraphs of unknown script",
           "biological": "a page of a 15th-century manuscript with small nude figures bathing in green-blue pools connected by tubes, unknown script",
           "pharmaceutical": "a page of a 15th-century manuscript with drawings of apothecary jars and small plant parts with labels, unknown script",
           "stars": "a page of a 15th-century manuscript with dense paragraphs of unknown script, each starting with a small star in the margin",
           "astronomical": "a page of a 15th-century manuscript with a circular astronomical diagram, sun and moon faces, unknown script",
           "cosmological": "a page of a 15th-century manuscript with a large circular cosmological diagram with rays, unknown script",
           "zodiac": "a page of a 15th-century manuscript with a zodiac roundel surrounded by small female figures holding stars",
           "text": "a page of a 15th-century manuscript filled with paragraphs of unknown script"}


def train_image_lora(cfg: LabConfig, pages: list[dict], out_dir: Path) -> Path:
    data_dir = out_dir / "lora_data"
    data_dir.mkdir(parents=True, exist_ok=True)
    folios = sorted({base_folio(p["folio"]) for p in pages})
    paths = fetch_folios(folios, 1024, cfg.cache_dir / "folios", cfg.images_dir)
    section = {base_folio(p["folio"]): p["section"] for p in pages}
    with open(data_dir / "metadata.jsonl", "w") as fh:
        for f, path in paths.items():
            target = data_dir / f"{f}.jpg"
            if not target.exists():
                target.write_bytes(path.read_bytes())
            fh.write(json.dumps({"file_name": target.name,
                                 "text": "voynich style, " + CAPTION.get(section.get(f, "text"), CAPTION["text"])}) + "\n")
    script = out_dir / "train_lora_sdxl.py"
    subprocess.run(["wget", "-q", "-O", str(script), LORA_SCRIPT], check=True)
    lora_dir = out_dir / "lora"
    subprocess.run([
        "accelerate", "launch", str(script), f"--pretrained_model_name_or_path={SDXL}",
        f"--pretrained_vae_model_name_or_path={SDXL_VAE}", f"--train_data_dir={data_dir}", "--caption_column=text",
        "--resolution=1024", "--random_flip", "--train_batch_size=1", "--gradient_accumulation_steps=4",
        f"--max_train_steps={200 if cfg.quick else 1500}", "--learning_rate=1e-4", "--lr_scheduler=cosine",
        "--lr_warmup_steps=50", "--mixed_precision=fp16", "--rank=16", f"--seed={cfg.seed}", f"--output_dir={lora_dir}",
        "--checkpointing_steps=100000"], check=True)
    return lora_dir


def generate_page_images(lora_dir: Path, attrs: dict[int, dict], out_dir: Path, seed: int) -> list[str]:
    import torch
    from diffusers import DiffusionPipeline  # type: ignore
    from PIL import ImageDraw  # type: ignore
    pipe = DiffusionPipeline.from_pretrained(SDXL, torch_dtype=torch.float16, variant="fp16").to("cuda")
    pipe.load_lora_weights(str(lora_dir))
    saved = []
    for m, a in attrs.items():
        img = pipe("voynich style, " + CAPTION.get(a["section"], CAPTION["text"]), num_inference_steps=30,
                   generator=torch.Generator("cuda").manual_seed(seed + m), height=1216, width=896).images[0]
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, img.width, 28], fill=(0, 0, 0))
        draw.text((8, 6), f"SYNTETYCZNE - wygenerowane przez AI, folio {m} (zaginione), nie jest rekonstrukcja", fill=(255, 255, 255))
        path = out_dir / f"SYNTETYCZNE_f{m}.png"
        img.save(path)
        saved.append(path.name)
    return saved


# ---------- theory

def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    r = rng(cfg.seed)
    res = TheoryResult(
        theory="generative",
        hypothesis=("Model generatywny potrafi napisać brakujące strony (f12, f59–64, f74, f91–92, f97–98, f109–110) "
                    "nieodróżnialne statystycznie od prawdziwych."),
        method=("Transformer znakowy uczony stronami z tokenami działu, języka Curriera i skryby; walidacja na odłożonych "
                "stronach; strony brakujące generowane z atrybutami sąsiadów; wierność: odległość miar kształtu, "
                "klasyfikator prawdziwe/wygenerowane (AUC), kopiowanie całych wierszy."),
        references=["A Glyph Is Not a Letter... What the Units of Voynichese Are Not, arXiv:2608.17096",
                    "Timm & Schinner, Cryptologia 44 (2020)"],
    )
    out_dir = cfg.results_dir / "generative"
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = page_records()
    vocab = Vocab(pages)
    val_pages = pages[5::10]
    train_pages = [p for p in pages if p not in val_pages]
    train_ids = [i for p in train_pages for i in vocab.encode_page(p)]
    val_ids = [i for p in val_pages for i in vocab.encode_page(p)]
    real_val_lines = [l for p in val_pages for l in p["lines"]]
    real_train_lines = [l for p in train_pages for l in p["lines"]]

    # Trigram baseline on the same characters.
    from ...cipher import self_entropy
    tri_bits = self_entropy([list(l) for l in real_train_lines], [list(l) for l in real_val_lines])

    # Discriminator controls (CPU).
    # Random halves: splitting by position would set dialect A against B and fake a difference.
    mixed = real_train_lines[:]
    r.shuffle(mixed)
    half = len(mixed) // 2
    auc_real = discriminator_auc(mixed[:half], mixed[half:], cfg.seed)
    auc_sc = discriminator_auc(real_val_lines, selfcite_lines(pages, 8000, cfg.seed), cfg.seed)
    res.control("klasyfikator: prawdziwe vs prawdziwe", "AUC ≈ 0,5 (najwyżej 0,6)", f"AUC = {auc_real:.3f}", auc_real <= 0.6)
    res.control("klasyfikator: prawdziwe vs prosty generator samocytowania", "AUC wyraźnie > 0,5 (≥ 0,7)",
                f"AUC = {auc_sc:.3f}", auc_sc >= 0.7)
    metrics = {"trigram_bits": tri_bits, "auc_real_vs_real": auc_real, "auc_real_vs_selfcite_v1": auc_sc}

    try:
        import torch  # noqa: F401
    except ImportError:
        res.evidence.append("Model tekstowy pominięty: brak PyTorch (uruchom w Colabie).")
        res.summary = "Policzono tylko kontrole klasyfikatora; model generatywny wymaga PyTorch i GPU."
        res.metrics = metrics
        res.decide(None)
        res.seconds = time.time() - t0
        return res

    model, training = train_gpt(train_ids, val_ids, vocab, cfg)
    gpt_bits = training["test_bits"]
    metrics.update({"gpt_bits": gpt_bits, "gpt_best_step": training["best_step"], "training": training["log"]})
    res.evidence.append(f"Odłożone strony: transformer {gpt_bits:.3f} bit/znak, model trigramowy {tri_bits:.3f} "
                        f"(różnica {tri_bits - gpt_bits:+.3f}: tyle struktury leży dalej niż 2 znaki wstecz).")

    # Generate a large sample for fidelity, conditioned like the validation pages.
    gen_lines = []
    for p in val_pages:
        gen_lines += sample_page(model, vocab, p, len(p["lines"]), 256)
    gen_words = [eva.glyphs(w) for l in gen_lines for w in l.split(".") if w]
    real_words = [eva.glyphs(w) for l in real_val_lines for w in l.split(".") if w]
    n = min(len(gen_words), len(real_words))
    _, scales = language_scales(max(2000, n))
    d = distance(profile(gen_words[:n]), profile(real_words[:n]), scales)
    auc_gen = discriminator_auc(real_val_lines, gen_lines, cfg.seed)
    all_real = set(l for p in pages for l in p["lines"])
    copied = sum(1 for l in gen_lines if l in all_real) / max(1, len(gen_lines))
    known_words = set(w for l in all_real for w in l.split("."))
    new_words = sum(1 for l in gen_lines for w in l.split(".") if w and w not in known_words)
    total_words = sum(1 for l in gen_lines for w in l.split(".") if w)
    metrics.update({"distance_generated_vs_real": d, "auc_real_vs_generated": auc_gen, "copied_lines": copied,
                    "new_word_share": new_words / max(1, total_words), "generated_words": total_words})
    res.evidence.append(f"Wygenerowane strony: odległość od prawdziwych {d:.2f} (dwie próbki łaciny ~0,2), AUC "
                        f"klasyfikatora {auc_gen:.3f}, skopiowane całe wiersze {copied:.1%}, nowe słowa {new_words / max(1, total_words):.1%}.")

    attrs = missing_page_attributes(pages)
    med = {}
    for p in pages:
        med.setdefault(p["section"], []).append(len(p["lines"]))
    missing = {}
    for m, a in attrs.items():
        lines_n = sorted(med[a["section"]])[len(med[a["section"]]) // 2]
        missing[f"f{m}"] = {"attributes": a, "lines": sample_page(model, vocab, a, lines_n, 256)}
    (out_dir / "SYNTETYCZNE_brakujace_strony.json").write_text(json.dumps(missing, ensure_ascii=False, indent=1))
    with open(out_dir / "SYNTETYCZNE_brakujace_strony.md", "w") as fh:
        fh.write("# Brakujące strony – tekst wygenerowany przez model (SYNTETYCZNY)\n\n"
                 "To nie jest rekonstrukcja zaginionej treści, tylko tekst o statystyce rękopisu.\n\n")
        for f, v in missing.items():
            fh.write(f"## {f} ({v['attributes']['section']}, język {v['attributes']['language']}, skryba {v['attributes']['hand']})\n\n")
            fh.write("\n".join(f"    {l.replace('.', ' ')}" for l in v["lines"]) + "\n\n")
    res.artifacts += ["generative/SYNTETYCZNE_brakujace_strony.md", "generative/SYNTETYCZNE_brakujace_strony.json"]

    if cfg.run_image_diffusion:
        try:
            lora = train_image_lora(cfg, pages, out_dir)
            res.artifacts += [f"generative/{n}" for n in generate_page_images(lora, attrs, out_dir, cfg.seed)]
        except Exception as e:  # images are optional; keep the text results
            res.evidence.append(f"Obrazy pominięte: {e}")

    res.metrics = metrics
    indist = auc_gen <= 0.6 and d < 0.5
    res.decide(True if indist else False if auc_gen >= 0.75 else None)
    res.summary = (f"Transformer: {gpt_bits:.2f} bit/znak wobec {tri_bits:.2f} dla trigramów. Wygenerowane strony "
                   f"{'są' if indist else 'nie są'} nieodróżnialne od prawdziwych (AUC {auc_gen:.2f}, odległość {d:.2f}). "
                   "Brakujące strony zapisano jako SYNTETYCZNE.")
    res.caveats += [
        "Wygenerowana strona nie zawiera zaginionej treści; pokazuje tylko, jak statystycznie wyglądałaby strona tego działu i skryby.",
        "Niskie AUC oznacza, że prosty klasyfikator nie odróżnia wierszy; mocniejszy klasyfikator może odróżnić.",
        "Atrybuty brakujących stron (dział, skryba) przyjęto od poprzedniej zachowanej strony.",
    ]
    res.seconds = time.time() - t0
    return res
