"""Settings for a lab run. Everything a Colab user may want to change lives here."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class LabConfig:
    # Where results go; on Colab point cache_dir at Google Drive to keep images between sessions.
    results_dir: Path = ROOT / "results" / "lab"
    cache_dir: Path = ROOT / "data" / "cache"

    # Colab Secrets names.
    openrouter_secret: str = "OPENROUTER_API_KEY"
    github_secret: str = "GITHUB_TOKEN"

    # Council of models. Leave council_models empty to pick the newest model of each
    # vendor prefix from OpenRouter's live model list.
    council_models: list[str] = field(default_factory=list)
    council_vendors: list[str] = field(default_factory=lambda: [
        "anthropic/claude", "openai/gpt", "google/gemini", "deepseek/deepseek", "x-ai/grok", "qwen/qwen"])
    council_size: int = 4
    chair_model: str = ""          # empty: the first council member chairs
    vision_model: str = ""         # empty: newest image-capable model from council_vendors
    council_language: str = "polski"
    budget_usd: float = 5.0        # hard stop for all OpenRouter calls in one run
    max_tokens: int = 1800

    # Theories to run: names from voynich.lab.registry.THEORIES, or "literature" / "all".
    theories: list[str] = field(default_factory=lambda: ["all"])
    quick: bool = False            # small settings for a smoke test
    seed: int = 7

    # Images (Beinecke IIIF) and GPU work.
    image_width: int = 1024        # pixels; IIIF serves any size
    images_dir: Path | None = None # optional folder of scans named f1r.jpg, f1v.jpg...; used before downloading
    # Atoms of the drawings on our own GPU (theory atoms_vision): which sections, which Hugging Face models.
    atoms_sections: tuple[str, ...] = ("zodiac",)   # add "pharmaceutical" for jars and plant fragments
    atoms_pointer: str = "allenai/Molmo2-8B"
    atoms_describer: str = "Qwen/Qwen3-VL-8B-Instruct"
    atoms_detector: str = "IDEA-Research/grounding-dino-base"
    atoms_image_width: int = 2000
    clip_model: str = "ViT-L-14"   # open_clip architecture
    clip_pretrained: str = "openai"
    vlm_folios_limit: int = 0      # 0 = all herbal folios; set e.g. 20 to save money
    gpt_steps: int = 6000          # character transformer training steps
    gpt_layers: int = 6
    gpt_width: int = 384
    run_image_diffusion: bool = False  # SDXL LoRA "missing pages"; ~1 h on an A100

    # Brute force over keys, triple by triple (theory "brute").
    brute_languages: list[str] = field(default_factory=list)  # empty: every lexicon in data/reference/lexicon
    brute_triples: int = 0         # most frequent distinct triples per text; 0 = 4000 (800 in quick mode)
    brute_tokenize: str = "glyphs" # "glyphs" (ch, sh, cth... as one symbol) or "chars" (raw EVA letters)

    # The wheel (volvelle) search and the transformer judge (theories "wheel", "adversary").
    wheel_rings: int = 3
    wheel_cells: int = 24
    wheel_population: int = 1024   # wheels scored in parallel on the GPU
    wheel_generations: int = 1500
    judge_epochs: int = 12

    # Attacks borrowed from the decipherment literature (theories "cognate", "hillclimb").
    attack_languages: list[str] = field(default_factory=list)  # empty: every lexicon
    cognate_types: int = 1500      # manuscript word types matched
    cognate_words: int = 6000      # lexicon word types matched against
    cognate_restarts: int = 32     # random restarts in one GPU batch
    cognate_steps: int = 600
    climb_population: int = 8192   # climbers in parallel on the GPU
    climb_steps: int = 3000
    climb_order: int = 4           # character n-gram order of the language model

    # The record track (theories "lists", "fields_lm", "v6", "cohesion").
    lists_corpora: list[str] = field(default_factory=list)   # empty: every corpus in data/lists passing the parse gate
    fields_corpora: list[str] = field(default_factory=lambda: [
        "rękopis", "łacina", "chorał", "bełkot v5", "martyrology", "apicius"])
    fields_steps: int = 2500       # GPT steps per training (15 trainings)
    fields_width: int = 256
    fields_layers: int = 4
    v6_population: int = 32        # evolution of the v6 generator on the CPU
    v6_generations: int = 25
    v6_topk: int = 5               # finalists judged by the transformer on the GPU
    v6_workers: int = 0            # 0 = all CPUs but one
    v6_judge_seeds: int = 3
    v6_inner_auc: bool = False     # add the n-gram line classifier to the fitness (16 s per evaluation)

    # Git: results are committed to this branch and pushed with the token.
    git_branch: str = "lab-results"
    git_repo: str = "lukaszciesielski-lodz/manuscript"

    def secret(self, name: str) -> str | None:
        """Colab Secrets first, then environment variables."""
        try:
            from google.colab import userdata  # type: ignore

            value = userdata.get(name)
            if value:
                return value
        except Exception:
            pass
        return os.environ.get(name)
