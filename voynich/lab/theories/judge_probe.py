"""Theory: what the transformer judge sees in the manuscript that the scorecard does not, is the vocabulary.

After v7 the judge still tells content-free text from the manuscript (AUC 0.642) although 21 of 23
measures are met; the lasting miss is too few hapax legomena. Here the judge is trained once and
then interrogated: which per-line features follow its score, and does it still see a difference
when both corpora are restricted to lines made only of words common to both (vocabulary matched)?
If the matched AUC drops to the real-vs-real level, the tell is vocabulary; if it stays, the tell
is in the order and shape of words, and the scorecard misses something structural.
"""

from __future__ import annotations

import random
import statistics
import time
from collections import Counter

from ... import hoax
from ..config import LabConfig
from ..results import TheoryResult
from .hoax import V7_FAV_N, V7_SECTION_PARAMS, generate_by_section, odd_runs, split_lines

FEATURES = ["words", "mean_len", "hapax", "unseen", "top10", "first_line", "last_line"]


def features(lines, counts_own: Counter, vocab_other: set, top10: set, page_of) -> list[dict]:
    out = []
    for i, l in enumerate(lines):
        words = [tuple(w) for w in l]
        n = max(1, len(words))
        out.append({"words": len(words), "mean_len": sum(map(len, words)) / n,
                    "hapax": sum(1 for w in words if counts_own[w] == 1) / n,
                    "unseen": sum(1 for w in words if w not in vocab_other) / n,
                    "top10": sum(1 for w in words if w in top10) / n,
                    "first_line": float(page_of(i) == "first"), "last_line": float(page_of(i) == "last")})
    return out


def auc(scores_pos, scores_neg) -> float:
    from sklearn.metrics import roc_auc_score
    y = [1] * len(scores_pos) + [0] * len(scores_neg)
    return float(roc_auc_score(y, list(scores_pos) + list(scores_neg)))


def spearman(x, y) -> float:
    from scipy.stats import spearmanr
    r = spearmanr(x, y).correlation
    return float(r) if r == r else 0.0


def _positions(n_lines: int, per_page: int = 15, real_pages=None):
    if real_pages is not None:
        return lambda i: real_pages[i]
    return lambda i: "first" if i % per_page == 0 else ("last" if i % per_page == per_page - 1 else "middle")


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    res = TheoryResult(
        theory="judge_probe",
        hypothesis="To, co transformer-sędzia widzi w rękopisie, a czego nie ma w karcie 23 miar, to słownictwo (słowa rzadkie "
                   "i nowe), nie szyk ani kształt słów.",
        method=("Sędzia z teorii adversary uczony na połowie wierszy (prawdziwe parzyste wobec v7), oceniany na drugiej połowie. "
                "Cechy wiersza: liczba słów, średnia długość słowa, udział hapaksów, udział słów nieobecnych w drugim korpusie, udział "
                "dziesięciu najczęstszych słów, pierwszy/ostatni wiersz strony. Miary: AUC sędziego; AUC każdej cechy osobno; korelacja "
                "Spearmana wyniku sędziego z cechami w obrębie prawdziwych i w obrębie v7; AUC sędziego po dopasowaniu słownictwa "
                "(tylko wiersze z samych słów obecnych w obu korpusach ≥ 2 razy). Kontrole: prawdziwe wobec prawdziwych (AUC ≤ 0,62, cechy "
                "w [0,45; 0,55]); czułość na 10% zmienionych glifów (≥ 0,7)."),
        references=["Vaswani et al., Attention is all you need (2017)", "Timm & Schinner (2019)"])
    try:
        import torch  # noqa: F401
    except ImportError:
        res.evidence.append("Brak PyTorch: uruchom w Colabie.")
        res.decide(None)
        res.summary = "Pominięte: wymaga PyTorch i GPU."
        res.seconds = time.time() - t0
        return res
    from ... import corpus
    odd, even = split_lines()
    L = [l for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
    even_meta = [l for l in L if int("".join(c for c in l.folio[1:] if c.isdigit()) or 0) % 2 == 0]
    page_pos = []
    for i, l in enumerate(even_meta):
        prev_same = i > 0 and even_meta[i - 1].folio == l.folio
        next_same = i + 1 < len(even_meta) and even_meta[i + 1].folio == l.folio
        page_pos.append("first" if not prev_same else ("last" if not next_same else "middle"))
    if len(page_pos) != len(even):
        page_pos = ["middle"] * len(even)
    gen = generate_by_section(odd_runs(), V7_SECTION_PARAMS, cfg.seed, fav_n=V7_FAV_N)
    rng = random.Random(cfg.seed)

    def judge_run(real, fake, name):
        """Train on half the lines of each, score the other half; returns held-out scores and strings."""
        ri, fi = list(range(len(real))), list(range(len(fake)))
        rng.shuffle(ri)
        rng.shuffle(fi)
        n = min(len(ri), len(fi))
        ri, fi = ri[:n], fi[:n]
        cut = n // 2
        rs, fs = hoax.line_strings(real), hoax.line_strings(fake)
        xtr = [rs[i] for i in ri[:cut]] + [fs[i] for i in fi[:cut]]
        ytr = [1] * cut + [0] * cut
        xte = [rs[i] for i in ri[cut:]] + [fs[i] for i in fi[cut:]]
        yte = [1] * (n - cut) + [0] * (n - cut)
        a, scores = _fit_with_scores(xtr, ytr, xte, yte, cfg, cfg.seed)
        print(f"  sędzia {name}: AUC {a:.3f}", flush=True)
        return a, scores[: n - cut], scores[n - cut:], ri[cut:], fi[cut:]

    auc_main, s_real, s_fake, idx_real, idx_fake = judge_run(even, gen, "prawdziwe wobec v7")
    auc_rr, s_r1, s_r2, _, _ = judge_run(even, odd, "prawdziwe wobec prawdziwych")
    res.control("sędzia: prawdziwe wobec prawdziwych blisko 0,5", "AUC ≤ 0,62", f"{auc_rr:.3f}", auc_rr <= 0.62)
    glyphs = sorted({g for l in odd for w in l for g in w})
    perturbed = [[[rng.choice(glyphs) if rng.random() < 0.1 else g for g in w] for w in l] for l in odd]
    auc_sens, *_ = judge_run(even, perturbed, "czułość 10% glifów")
    res.control("sędzia: czułość na 10% zmienionych glifów", "AUC ≥ 0,7", f"{auc_sens:.3f}", auc_sens >= 0.7)
    # Features of the held-out lines.
    c_real, c_gen = Counter(tuple(w) for l in even for w in l), Counter(tuple(w) for l in gen for w in l)
    top10 = {w for w, _ in c_real.most_common(10)}
    f_real = features([even[i] for i in idx_real], c_real, set(c_gen), top10, lambda k: page_pos[idx_real[k]])
    f_fake = features([gen[i] for i in idx_fake], c_gen, set(c_real), top10, _positions(len(gen)))
    feat_auc = {f: auc([d[f] for d in f_real], [d[f] for d in f_fake]) for f in FEATURES}
    corr_real = {f: spearman([d[f] for d in f_real], s_real) for f in FEATURES}
    corr_fake = {f: spearman([d[f] for d in f_fake], s_fake) for f in FEATURES}
    # Real vs real feature AUCs (should be ~0.5): a control on the features themselves.
    f_r2 = features(odd, Counter(tuple(w) for l in odd for w in l), set(c_real), top10, _positions(len(odd)))
    f_r1 = features(even, c_real, set(Counter(tuple(w) for l in odd for w in l)), top10, lambda k: page_pos[k])
    feat_rr = {f: auc([d[f] for d in f_r1], [d[f] for d in f_r2]) for f in FEATURES if f not in ("first_line", "last_line")}
    bad = [f for f, a in feat_rr.items() if not 0.42 <= a <= 0.58]
    res.control("cechy: prawdziwe wobec prawdziwych bez różnic", "AUC każdej cechy w [0,42; 0,58]",
                ", ".join(f"{f} {a:.2f}" for f, a in feat_rr.items()), not bad)
    # Vocabulary-matched judge: only lines whose every word occurs at least twice in both corpora.
    common = {w for w in c_real if c_real[w] >= 2 and c_gen.get(w, 0) >= 2}
    even_m = [l for l in even if all(tuple(w) in common for w in l) and len(l) >= 3]
    gen_m = [l for l in gen if all(tuple(w) in common for w in l) and len(l) >= 3]
    n_m = min(len(even_m), len(gen_m))
    if n_m >= 200:
        auc_matched, *_ = judge_run(even_m, gen_m, f"słownictwo dopasowane ({n_m} wierszy na stronę)")
    else:
        auc_matched = float("nan")
    # Samples.
    order_r = sorted(range(len(s_real)), key=lambda k: -s_real[k])
    order_f = sorted(range(len(s_fake)), key=lambda k: s_fake[k])
    most_real = [" ".join("".join(w) for w in even[idx_real[k]]) for k in order_r[:8]]
    most_fake = [" ".join("".join(w) for w in gen[idx_fake[k]]) for k in order_f[:8]]
    res.metrics = {"judge_auc": auc_main, "real_vs_real": auc_rr, "sensitivity": auc_sens, "feature_auc": feat_auc,
                   "feature_auc_real_vs_real": feat_rr, "spearman_real": corr_real, "spearman_v7": corr_fake,
                   "matched_auc": auc_matched, "matched_lines": n_m, "most_real": most_real, "most_fake": most_fake}
    res.evidence.append(f"Sędzia: prawdziwe wobec v7 AUC {auc_main:.3f}; prawdziwe wobec prawdziwych {auc_rr:.3f}; czułość {auc_sens:.3f}.")
    res.evidence.append("AUC pojedynczych cech (prawdziwe wobec v7): " + ", ".join(f"{f} {a:.2f}" for f, a in feat_auc.items()) + ".")
    res.evidence.append("Korelacja wyniku sędziego z cechami w obrębie prawdziwych: " + ", ".join(f"{f} {r:+.2f}" for f, r in corr_real.items())
                        + "; w obrębie v7: " + ", ".join(f"{f} {r:+.2f}" for f, r in corr_fake.items()) + ".")
    res.evidence.append(f"Słownictwo dopasowane (same słowa obecne w obu korpusach ≥ 2 razy; {n_m} wierszy na stronę): AUC {auc_matched:.3f}."
                        if n_m >= 200 else f"Słownictwo dopasowane: za mało wierszy ({n_m}).")
    res.evidence.append("Wiersze uznane za najprawdziwsze: " + " | ".join(most_real[:5]) + ". Najfałszywsze: " + " | ".join(most_fake[:5]) + ".")
    if n_m >= 200 and auc_matched <= auc_rr + 0.05:
        res.decide(True)
    elif n_m >= 200 and auc_matched >= 0.60:
        res.decide(False)
    else:
        res.decide(None)
    strongest = max(feat_auc, key=lambda f: abs(feat_auc[f] - 0.5))
    res.summary = (f"Sędzia AUC {auc_main:.3f} (prawdziwe–prawdziwe {auc_rr:.3f}); po dopasowaniu słownictwa "
                   + (f"{auc_matched:.3f}" if n_m >= 200 else "brak danych") + f". Najsilniejsza pojedyncza cecha: {strongest} "
                   f"(AUC {feat_auc[strongest]:.2f}). "
                   + ("Ślad sędziego to słownictwo: na wspólnych słowach nie odróżnia." if res.verdict == "potwierdzona" else
                      "Ślad sędziego zostaje na wspólnych słowach: to szyk lub kształt, nie słownictwo." if res.verdict == "obalona" else
                      "Wynik niejednoznaczny."))
    res.caveats += ["Dopasowanie słownictwa wybiera wiersze z częstych słów; sędzia na nich uczy się mniej (mniej wierszy), więc AUC "
                    "spada też z braku danych; stąd próg względem prawdziwe–prawdziwe, nie bezwzględny.",
                    "Cechy są korelatami, nie wyjaśnieniem; sędzia może używać kombinacji, której żadna cecha nie oddaje."]
    res.seconds = time.time() - t0
    return res


def _fit_with_scores(x_train, y_train, x_test, y_test, cfg: LabConfig, seed: int, length: int = 96):
    """The adversary judge, returning (best-epoch AUC, scores of x_test at that epoch)."""
    import torch
    import torch.nn as nn
    from sklearn.metrics import roc_auc_score
    chars = sorted({c for s in x_train + x_test for c in s})
    stoi = {c: i + 2 for i, c in enumerate(chars)}
    L = length
    enc = lambda s: [1] + [stoi[c] for c in s[: L - 1]] + [0] * max(0, L - 1 - len(s))  # noqa: E731
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
    Xtr = torch.tensor([enc(s) for s in x_train]).to(device)
    Ytr = torch.tensor(y_train, dtype=torch.float32).to(device)
    Xte = torch.tensor([enc(s) for s in x_test]).to(device)
    epochs = 3 if cfg.quick else cfg.judge_epochs
    best, best_scores = 0.5, [0.5] * len(x_test)
    for _ in range(epochs):
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
            scores = torch.cat([model(Xte[i:i + 256]).sigmoid().cpu() for i in range(0, len(Xte), 256)]).tolist()
        a = float(roc_auc_score(y_test, scores))
        if a > best:
            best, best_scores = a, scores
    return best, best_scores
