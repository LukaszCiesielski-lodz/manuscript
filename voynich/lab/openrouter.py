"""Minimal OpenRouter client (OpenAI-compatible chat API) with a spending cap.

Model ids change often, so nothing here hard-codes one: `pick_models` reads
the live model list and takes the newest model for each vendor prefix.
"""

from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

API = "https://openrouter.ai/api/v1"
# Cheap variants are skipped when picking council members automatically.
_SKIP = (":free", "-mini", "-nano", "-flash-lite", "-lite", "-haiku", "-tiny", "-small", "guard", "embed",
         "image", "audio", "tts", "search", "-online")


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class OpenRouter:
    api_key: str
    budget_usd: float = 5.0
    referer: str = "https://github.com/lukaszciesielski-lodz/manuscript"
    title: str = "Voynich Lab"
    spent_usd: float = 0.0
    calls: int = 0
    log: list = field(default_factory=list)

    def _request(self, path: str, payload: dict | None = None, timeout: int = 180) -> dict:
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(API + path, data=data, method="POST" if data else "GET", headers={
            "Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
            "HTTP-Referer": self.referer, "X-Title": self.title})
        delay = 2.0
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return json.loads(resp.read())
            except urllib.error.HTTPError as e:
                body = e.read().decode(errors="replace")[:500]
                if e.code in (429, 500, 502, 503, 504) and attempt < 4:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise RuntimeError(f"OpenRouter {e.code}: {body}") from None
            except (urllib.error.URLError, TimeoutError):
                if attempt < 4:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise
        raise RuntimeError("OpenRouter: no response")

    def models(self) -> list[dict]:
        return self._request("/models")["data"]

    def chat(self, model: str, messages: list[dict], max_tokens: int = 1500, temperature: float = 0.3) -> str:
        if self.spent_usd >= self.budget_usd:
            raise BudgetExceeded(f"budżet {self.budget_usd:.2f} USD wyczerpany")
        out = self._request("/chat/completions", {
            "model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature,
            "usage": {"include": True}})
        usage = out.get("usage") or {}
        cost = float(usage.get("cost") or 0.0)
        self.spent_usd += cost
        self.calls += 1
        self.log.append({"model": model, "cost": cost, "tokens": usage.get("total_tokens")})
        choices = out.get("choices") or []
        if not choices:
            raise RuntimeError(f"OpenRouter: brak odpowiedzi od {model}: {str(out)[:300]}")
        return choices[0]["message"].get("content") or ""


def image_part(jpeg_bytes: bytes) -> dict:
    return {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(jpeg_bytes).decode()}}


def pick_models(models: list[dict], vendors: list[str], n: int, vision: bool = False) -> list[str]:
    """Newest full-size model per vendor prefix, in the order of `vendors`."""
    chosen = []
    for prefix in vendors:
        cands = [m for m in models if m["id"].startswith(prefix) and not any(s in m["id"] for s in _SKIP)]
        if vision:
            cands = [m for m in cands if "image" in (m.get("architecture", {}).get("input_modalities") or [])]
        if cands:
            chosen.append(max(cands, key=lambda m: m.get("created", 0))["id"])
        if len(chosen) == n:
            break
    return chosen


def parse_json(text: str) -> dict:
    """First JSON object in a model reply (models wrap JSON in prose or code fences)."""
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return {}
