"""Theory: a stronger judge. A transformer trained on the GPU to tell real lines from generated ones.

The lab's line classifier (character n-grams, logistic regression) is weak on purpose: it
runs everywhere. Here a small transformer classifier is trained on the GPU for every generator
(copy-and-modify v4, scribe's table v5, the wheel, a one-word chain) and for the control
real-vs-real split. A generator that this judge cannot tell from the manuscript (AUC near the
real-vs-real value) has reproduced what the text has at the level of whole lines.
"""

from __future__ import annotations

import random
import time

from ... import hoax, selfcite
from ..config import LabConfig
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs, split_lines


def train_judge(real: list[str], fake: list[str], cfg: LabConfig, seed: int) -> float:
    """AUC of a character transformer classifier on a held-out half (real vs fake lines)."""
    import torch
    import torch.nn as nn
    from sklearn.metrics import roc_auc_score
    r = random.Random(seed)
    n = min(len(real), len(fake))
    x = r.sample(real, n) + r.sample(fake, n)
    y = [0] * n + [1] * n
    idx = list(range(2 * n))
    r.shuffle(idx)
    cut = len(idx) // 2
    chars = sorted({c for s in x for c in s})
    stoi = {c: i + 2 for i, c in enumerate(chars)}  # 0 pad, 1 cls
    L = 96
    enc = lambda s: [1] + [stoi[c] for c in s[: L - 1]] + [0] * max(0, L - 1 - len(s))
    X = torch.tensor([enc(x[i]) for i in idx])
    Y = torch.tensor([y[i] for i in idx], dtype=torch.float32)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(seed)

    class Judge(nn.Module):
        def __init__(self, v, d=192, heads=6, layers=4):
            super().__init__()
            self.emb = nn.Embedding(v, d)
            self.pos = nn.Parameter(torch.zeros(1, L, d))
            layer = nn.TransformerEncoderLayer(d, heads, 4 * d, dropout=0.1, batch_first=True)
            self.enc = nn.TransformerEncoder(layer, layers)
            self.out = nn.Linear(d, 1)

        def forward(self, t):
            h = self.enc(self.emb(t) + self.pos, src_key_padding_mask=(t == 0))
            return self.out(h[:, 0]).squeeze(-1)

    model = Judge(len(chars) + 2).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.05)
    Xtr, Ytr, Xte, Yte = X[:cut].to(device), Y[:cut].to(device), X[cut:].to(device), Y[cut:]
    epochs = 3 if cfg.quick else cfg.judge_epochs
    best = 0.5
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(len(Xtr), device=device)
        for i in range(0, len(perm), 64):
            b = perm[i:i + 64]
            loss = nn.functional.binary_cross_entropy_with_logits(model(Xtr[b]), Ytr[b])
            opt.zero_grad()
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            scores = torch.cat([model(Xte[i:i + 256]).sigmoid().cpu() for i in range(0, len(Xte), 256)])
        auc = float(roc_auc_score(Yte.numpy(), scores.numpy()))
        best = max(best, auc)  # the judge's best epoch: the strongest case against the generator
    return best


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    res = TheoryResult(
        theory="adversary",
        hypothesis="Któryś z generatorów bez treści pisze wiersze, których nie odróżni od rękopisu nawet transformer.",
        method=("Transformer-klasyfikator (4 warstwy, 192 wymiary) uczony na GPU: prawdziwe wiersze (foliały parzyste) "
                "przeciw wierszom każdego generatora (reguły z nieparzystych); AUC na odłożonej połowie, najlepsza epoka. "
                "Kontrola: prawdziwe przeciw prawdziwym (nieparzyste) musi dać AUC ≈ 0,5."),
        references=["Vaswani et al., Attention is all you need (2017)", "Gaskell & Bowern (2022)"])
    try:
        import torch  # noqa: F401
    except ImportError:
        res.evidence.append("Brak PyTorch: uruchom w Colabie.")
        res.decide(None)
        res.summary = "Pominięte: wymaga PyTorch i GPU."
        res.seconds = time.time() - t0
        return res
    odd, even = split_lines()
    words = [w for l in odd for w in l]
    n = 3 * hoax.BLOCK + 1000
    edits, grammar = selfcite.EditModel(words), selfcite.WordGrammar(words, beta=5)
    gens = {
        "v4 (kopiowanie ze zmianami)": selfcite.generate(odd[:3], n, [len(l) for l in odd], p_copy=0.22, window=8, p_far=0.05,
                                                          seed=cfg.seed, edits=edits, grammar=grammar),
        "v5 działami (tabela skryby)": generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed),
        "łańcuch słów (pamięć 1)": hoax.word_chain(odd, odd, 1, seed=cfg.seed),
    }
    try:
        from ..wheel import Backend, Search, fit, scribe
        pop, gens_n = (64, 30) if cfg.quick else (cfg.wheel_population, max(100, cfg.wheel_generations // 4))
        best, text = fit([[tuple(w) for w in l] for l in odd], Search(cfg.wheel_rings, cfg.wheel_cells, pop, gens_n,
                                                                        seed=cfg.seed), Backend(), None)
        gens["tarcza (volvelle)"] = scribe([[tuple(w) for w in l] for l in odd], best["rings"], text.seg, n, cfg.seed)
    except Exception as e:
        res.evidence.append(f"Tarcza pominięta: {e}")
    real_even, real_odd = hoax.line_strings(even), hoax.line_strings(odd)
    auc0 = train_judge(real_even, real_odd, cfg, cfg.seed)
    res.control("transformer: prawdziwe vs prawdziwe", "AUC ≤ 0,62", f"AUC = {auc0:.3f}", auc0 <= 0.62)
    # Sensitivity: real lines with one glyph in ten replaced at random must be caught.
    r = random.Random(cfg.seed)
    glyph_pool = sorted({g for l in odd for w in l for g in w})
    perturbed = [[[g if r.random() > 0.1 else r.choice(glyph_pool) for g in w] for w in l] for l in odd]
    auc_p = train_judge(real_even, hoax.line_strings(perturbed), cfg, cfg.seed)
    res.control("transformer wykrywa podłożony efekt (10% glifów podmienionych)", "AUC ≥ 0,7", f"AUC = {auc_p:.3f}", auc_p >= 0.7)
    metrics = {"real_vs_real": auc0, "perturbed_real": auc_p}
    for name, g in gens.items():
        if not g:
            continue
        seeds = [cfg.seed] if cfg.quick else [cfg.seed, cfg.seed + 1, cfg.seed + 2]
        aucs = [train_judge(real_even, hoax.line_strings(g), cfg, sd) for sd in seeds]
        auc = sum(aucs) / len(aucs)
        spread = (max(aucs) - min(aucs)) / 2
        weak = hoax.classifier_auc(even, g, cfg.seed)
        metrics[name] = {"transformer": auc, "transformer_runs": aucs, "ngram": weak}
        res.evidence.append(f"{name}: transformer AUC {auc:.3f} ± {spread:.3f} ({len(aucs)} podziały; klasyfikator n-gramowy {weak:.3f}).")
        print(f"  {name}: transformer {auc:.3f}, n-gramy {weak:.3f}", flush=True)
    res.metrics = metrics
    passing = [k for k, v in metrics.items() if isinstance(v, dict) and v["transformer"] <= auc0 + 0.07]
    res.decide(True if passing else False)
    res.summary = (f"Prawdziwe vs prawdziwe: AUC {auc0:.2f}. " + (f"Nieodróżnialne dla transformera: {', '.join(passing)}."
                   if passing else "Transformer odróżnia każdy generator od rękopisu: "
                   + ", ".join(f"{k} {v['transformer']:.2f}" for k, v in metrics.items() if isinstance(v, dict)) + "."))
    res.caveats += ["Mały transformer uczony kilka epok na ~8 tys. wierszy; większy model może odróżnić więcej.",
                    "Wiersze jako ciągi znaków EVA; test nie widzi układu strony ani rysunków."]
    res.seconds = time.time() - t0
    return res
