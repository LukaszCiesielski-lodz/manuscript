"""The record every theory returns, and how it is saved."""

from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

VERDICTS = ("potwierdzona", "obalona", "nierozstrzygnięta", "metoda niewiarygodna")


@dataclass
class Control:
    """A check on the method itself. `passed` means the method behaved as it must."""

    name: str
    expectation: str
    observed: str
    passed: bool


@dataclass
class TheoryResult:
    theory: str
    hypothesis: str
    method: str
    verdict: str = "nierozstrzygnięta"
    summary: str = ""
    metrics: dict = field(default_factory=dict)
    controls: list[Control] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    seconds: float = 0.0
    council: dict = field(default_factory=dict)

    def control(self, name: str, expectation: str, observed: str, passed: bool) -> None:
        self.controls.append(Control(name, expectation, observed, bool(passed)))

    def decide(self, supported: bool | None) -> None:
        """Set the verdict; a failed control overrides any outcome."""
        if any(not c.passed for c in self.controls):
            self.verdict = "metoda niewiarygodna"
        elif supported is None:
            self.verdict = "nierozstrzygnięta"
        else:
            self.verdict = "potwierdzona" if supported else "obalona"

    def brief(self, max_chars: int = 9000) -> str:
        """Plain-text digest for the council: everything they need, nothing else."""
        lines = [f"TEORIA: {self.theory}", f"HIPOTEZA: {self.hypothesis}", f"METODA: {self.method}",
                 f"WERDYKT AUTOMATYCZNY: {self.verdict}", f"PODSUMOWANIE: {self.summary}", "KONTROLE METODY:"]
        for c in self.controls:
            lines.append(f"- {c.name}: oczekiwano {c.expectation}; zaobserwowano {c.observed}; "
                         f"{'OK' if c.passed else 'NIEZALICZONA'}")
        lines.append("DOWODY:")
        lines += [f"- {e}" for e in self.evidence]
        lines.append("MIARY: " + json.dumps(_finite(self.metrics), ensure_ascii=False)[:4000])
        if self.caveats:
            lines.append("ZASTRZEŻENIA:")
            lines += [f"- {c}" for c in self.caveats]
        if self.references:
            lines.append("LITERATURA: " + "; ".join(self.references))
        return "\n".join(lines)[:max_chars]

    def save(self, folder: Path) -> Path:
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{self.theory}.json"
        path.write_text(json.dumps(_finite(asdict(self)), indent=1, ensure_ascii=False), encoding="utf-8")
        (folder / f"{self.theory}.md").write_text(self.markdown(), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> "TheoryResult":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        d["controls"] = [Control(**c) for c in d.get("controls", [])]
        return cls(**d)

    def markdown(self) -> str:
        out = [f"# {self.theory}: {self.verdict}", "", f"**Hipoteza.** {self.hypothesis}", "",
               f"**Metoda.** {self.method}", "", self.summary, "", "## Kontrole", ""]
        out += [f"- {'✅' if c.passed else '❌'} **{c.name}**: oczekiwano {c.expectation}; wynik: {c.observed}"
                for c in self.controls]
        out += ["", "## Dowody", ""] + [f"- {e}" for e in self.evidence]
        if self.caveats:
            out += ["", "## Zastrzeżenia", ""] + [f"- {c}" for c in self.caveats]
        if self.council.get("synthesis"):
            out += ["", "## Rada modeli", "", self.council["synthesis"]]
        if self.references:
            out += ["", "## Literatura", ""] + [f"- {r}" for r in self.references]
        out += ["", f"_Czas: {self.seconds:.0f} s · {time.strftime('%Y-%m-%d %H:%M')}_"]
        return "\n".join(out)


def _finite(x):
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    if isinstance(x, dict):
        return {str(k): _finite(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_finite(v) for v in x]
    if hasattr(x, "item") and not isinstance(x, (str, bytes)):  # numpy scalars
        try:
            return _finite(x.item())
        except Exception:
            return str(x)
    return x
