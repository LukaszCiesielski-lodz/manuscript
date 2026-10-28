"""Open vision models from Hugging Face for drafting atoms on our own GPU (no API, no cost per call).

Three jobs, three models, all Apache 2.0 and ungated (checked 28.10.2026, transformers 4.57):
- pointing and counting: allenai/Molmo2-8B answers "Point to each X" with <points coords="i x y ..."> scaled by 1000;
- describing a crop: Qwen/Qwen3-VL-8B-Instruct answers a JSON question about one cut-out figure;
- boxes by name: IDEA-Research/grounding-dino-base, a second counter to check the first.
torch and transformers are imported inside the classes, so this module imports anywhere.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

POINTER = "allenai/Molmo2-8B"
DESCRIBER = "Qwen/Qwen3-VL-8B-Instruct"
DETECTOR = "IDEA-Research/grounding-dino-base"


def available() -> bool:
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
        return torch.cuda.is_available()
    except ImportError:
        return False


@dataclass
class Chat:
    """An image-text-to-text model (Molmo2, Qwen3-VL) behind one `ask(image, prompt)`."""

    model_id: str
    model: object = None
    processor: object = None

    def load(self) -> "Chat":
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor
        kw = {"trust_remote_code": True, "dtype": torch.bfloat16, "device_map": "auto"}
        self.processor = AutoProcessor.from_pretrained(self.model_id, **kw)
        self.model = AutoModelForImageTextToText.from_pretrained(self.model_id, **kw).eval()
        return self

    def ask(self, image, prompt: str, max_new_tokens: int = 1200) -> str:
        import torch
        if self.model is None:
            self.load()
        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image", "image": image}]}]
        inputs = self.processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                                    return_tensors="pt", return_dict=True)
        inputs = {k: (v.to(self.model.device) if hasattr(v, "to") else v) for k, v in inputs.items()}
        with torch.inference_mode():
            out = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        return self.processor.tokenizer.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    def points(self, image, what: str) -> list[tuple[float, float]]:
        from .. import atoms
        text = self.ask(image, f"Point to each {what}.", 1500)
        return atoms.parse_points(text, image.width, image.height)

    def json(self, image, prompt: str) -> dict:
        from .openrouter import parse_json
        return parse_json(self.ask(image, prompt, 600))


@dataclass
class Detector:
    """Grounding DINO: boxes for free-text labels."""

    model_id: str = DETECTOR
    model: object = None
    processor: object = None

    def load(self) -> "Detector":
        from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(self.model_id).to("cuda").eval()
        return self

    def boxes(self, image, labels: list[str], threshold: float = 0.3) -> dict[str, list[tuple[float, float, float, float]]]:
        import torch
        if self.model is None:
            self.load()
        inputs = self.processor(images=image, text=[labels], return_tensors="pt").to("cuda")
        with torch.no_grad():
            out = self.model(**inputs)
        res = self.processor.post_process_grounded_object_detection(out, threshold=threshold, text_threshold=threshold,
                                                                    target_sizes=[(image.height, image.width)])[0]
        found: dict[str, list] = {l: [] for l in labels}
        for box, label in zip(res["boxes"], res.get("text_labels") or res.get("labels")):
            key = next((l for l in labels if str(label).strip() in l or l in str(label)), str(label))
            found.setdefault(key, []).append(tuple(round(float(v), 1) for v in box.tolist()))
        return found


def schema_prompt(typ: str, specs: dict, intro: str) -> str:
    """A JSON question about one crop, keys and allowed values straight from vocab.json."""
    fields = {k: ("true/false" if v == "bool" else "liczba" if v == "int" else "|".join(v)) for k, v in specs.items()}
    return (f"{intro} Opisz TYLKO to, co widać na wycinku; nie zgaduj. Odpowiedz wyłącznie JSON z kluczami i dozwolonymi "
            f"wartościami: {json.dumps(fields, ensure_ascii=False)}. Jeśli czegoś nie widać, wpisz null.")
