"""Generators v6 and v7: the v5 scribe's habits searched by evolution against the manuscript's scorecard.

v5 by section misses three vocabulary measures (too few distinct words and hapax legomena, too
much weight on the ten most frequent words): its reuse is too concentrated. `freq_gamma` damps a
word the more often it has been written. The eighteen settings below are evolved on the CPU (a
process pool; each evaluation generates ~37k words and scores every measure of the scorecard against the yardstick
of the odd folios); the even folios, never seen by the search, rank the finalists, and the
transformer judge on the GPU gives the last word. v7 adds `neighbour_gamma` (a candidate resembling
the word just written is avoided), `p_edge` (a stock of whole line-opening and line-closing words) and
the 23rd measure, the information between adjacent words, which the edge vocabulary drives.
"""

from __future__ import annotations

import json
import os
import random
import statistics
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence

from .. import hoax
from .theories.hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs, section_models, split_lines

# name: (low, high, integer?)
SPACE: dict[str, tuple[float, float, bool]] = {
    "p_new": (0.2, 0.9, False), "p_far": (0.3, 1.0, False), "p_copy": (0.0, 0.5, False), "p_same_column": (0.0, 0.9, False),
    "gamma": (0.5, 8.0, False), "length_gamma": (0.3, 3.0, False), "p_hot": (0.0, 0.1, False), "hot_power": (0.5, 3.0, False),
    "p_repeat": (0.0, 0.02, False), "window": (3, 30, True), "candidates": (2, 8, True), "p_fav": (0.0, 0.3, False),
    "p_short": (0.0, 0.15, False), "position_gamma": (0.0, 4.0, False), "pair_gamma": (0.0, 4.0, False),
    "mood_gamma": (0.0, 4.0, False), "freq_gamma": (0.0, 2.0, False), "fav_n": (5, 120, True),
    "neighbour_gamma": (0.0, 6.0, False), "p_edge": (0.0, 0.9, False),
}
VOCAB = ("type_token_ratio", "hapax_ratio", "top10_coverage", "vocab_density")
V5_POINT = {**V5_SECTION_PARAMS, "freq_gamma": 0.0, "fav_n": 40, "neighbour_gamma": 0.0, "p_edge": 0.0}


def clip(params: dict) -> dict:
    out = {}
    for k, (lo, hi, integer) in SPACE.items():
        v = min(hi, max(lo, params.get(k, V5_POINT[k])))
        out[k] = int(round(v)) if integer else float(v)
    return out


def mutate(params: dict, sigma: float, rng: random.Random) -> dict:
    """Gaussian step of `sigma` times the range on every setting (each with probability 0.6)."""
    out = dict(params)
    for k, (lo, hi, integer) in SPACE.items():
        if rng.random() < 0.6:
            out[k] = params[k] + rng.gauss(0, sigma * (hi - lo))
    return clip(out)


def crossover(a: dict, b: dict, rng: random.Random) -> dict:
    return clip({k: (a[k] if rng.random() < 0.5 else b[k]) for k in SPACE})


def split_params(params: dict) -> tuple[dict, int]:
    """Settings of generate_v5 and the fav_n of generate_by_section."""
    p = dict(params)
    fav_n = int(p.pop("fav_n"))
    return p, fav_n


def fitness_of(card: dict[str, dict]) -> float:
    """Sum of squared excess over |z| = 1 on all measures, vocabulary measures counted three times more."""
    f = 0.0
    for k, v in card.items():
        z = abs(v["z"])
        f += max(0.0, z - 1.0) ** 2
        if k in VOCAB:
            f += 3.0 * z * z
    return f


@dataclass
class Shared:
    runs: list
    models: dict
    stick: dict
    n_blocks: int | None = None


_SHARED: Shared | None = None


def _init(shared: Shared | None) -> None:
    global _SHARED
    if shared is None:
        runs = odd_runs()
        odd, _ = split_lines()
        shared = Shared(runs, section_models(runs), hoax.yardstick(odd))
    _SHARED = shared


def evaluate(params: dict, seed: int, shared: Shared | None = None) -> dict:
    """Generate with `params` and score against the yardstick: fitness, misses, card."""
    sh = shared or _SHARED
    if sh is None:
        _init(None)
        sh = _SHARED
    p, fav_n = split_params(clip(params))
    gen = generate_by_section(sh.runs, p, seed, fav_n=fav_n, models=sh.models)
    card = hoax.scorecard(gen, sh.stick, sh.n_blocks)
    return {"fitness": fitness_of(card), "misses": hoax.misses(card), "card": card}


def _work(job):
    params, seed = job
    r = evaluate(params, seed)
    return {"fitness": r["fitness"], "misses": r["misses"]}


@dataclass
class Evolution:
    population: int = 32
    generations: int = 25
    elite: int = 4
    sigma_start: float = 0.25
    sigma_end: float = 0.08
    patience: int = 6
    workers: int = 0
    seed: int = 7
    log: Callable[[str], None] | None = None
    history: list = field(default_factory=list)
    finalists: list = field(default_factory=list)   # distinct settings of the last generation, best first

    def run(self, start: dict | None = None, shared: Shared | None = None) -> dict:
        """(μ+λ) evolution from the v5 point; returns the best settings with their fitness and misses."""
        rng = random.Random(self.seed)
        workers = self.workers or max(1, (os.cpu_count() or 2) - 1)
        base = clip(start or V5_POINT)
        pop = [base] + [mutate(base, self.sigma_start, rng) for _ in range(self.population - 1)]
        best, best_fit, stale = base, float("inf"), 0
        with ProcessPoolExecutor(workers, initializer=_init, initargs=(shared,)) as ex:
            for g in range(self.generations):
                sigma = self.sigma_start + (self.sigma_end - self.sigma_start) * g / max(1, self.generations - 1)
                seed = self.seed * 1000 + g                 # one seed per generation: fair comparison inside it
                results = list(ex.map(_work, [(p, seed) for p in pop]))
                ranked = sorted(zip(results, pop), key=lambda t: t[0]["fitness"])
                top_fit, top = ranked[0][0]["fitness"], ranked[0][1]
                self.finalists = []
                for _, p in ranked:
                    if p not in self.finalists:
                        self.finalists.append(p)
                self.history.append({"generation": g, "best": top_fit, "misses": ranked[0][0]["misses"],
                                     "median": statistics.median(r["fitness"] for r in results)})
                if self.log:
                    self.log(f"  pokolenie {g}: najlepszy {top_fit:.2f} (chybienia: {', '.join(ranked[0][0]['misses']) or 'brak'}), "
                             f"mediana {self.history[-1]['median']:.2f}, σ {sigma:.3f}")
                if top_fit < best_fit * 0.98:
                    best, best_fit, stale = top, top_fit, 0
                elif top_fit < best_fit:
                    best, best_fit = top, top_fit
                    stale += 1
                else:
                    stale += 1
                if stale >= self.patience:
                    break
                elites = [p for _, p in ranked[: self.elite]]
                children = []
                while len(children) < self.population - self.elite:
                    a, b = rng.sample(elites, 2) if len(elites) > 1 else (elites[0], elites[0])
                    child = crossover(a, b, rng) if rng.random() < 0.3 else dict(a)
                    children.append(mutate(child, sigma, rng))
                pop = elites + children                     # elites are re-evaluated with the next generation's seed
        return {"params": best, "fitness": best_fit, "generations": len(self.history)}


def save(result: dict, folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "best_params.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    return path
