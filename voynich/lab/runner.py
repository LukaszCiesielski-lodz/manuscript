"""Run theories, convene the council, write a report and push it to GitHub.

From a notebook:
    lab = Lab(LabConfig(budget_usd=5))
    lab.connect()                 # OpenRouter key from Colab Secrets
    lab.run("numbers")            # or lab.run_all()
    lab.convene()                 # council of models on every result
    lab.report(); lab.push()

From a shell:
    python -m voynich.lab.runner --theories numbers,literature --quick --no-council
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import time
from pathlib import Path

from .. import corpus
from .config import ROOT, LabConfig
from .council import deliberate
from .openrouter import OpenRouter, pick_models
from .registry import THEORIES, expand
from .results import TheoryResult


class Lab:
    def __init__(self, cfg: LabConfig):
        self.stamp = time.strftime("%Y%m%d-%H%M%S")
        self.cfg = dataclasses.replace(cfg, results_dir=cfg.results_dir / self.stamp)
        self.cfg.results_dir.mkdir(parents=True, exist_ok=True)
        self.client: OpenRouter | None = None
        self.members: list[str] = []
        self.chair = ""
        self.vision = ""
        self.results: dict[str, TheoryResult] = {}

    # ---- OpenRouter

    def connect(self) -> None:
        key = self.cfg.secret(self.cfg.openrouter_secret)
        if not key:
            print(f"Brak sekretu {self.cfg.openrouter_secret}: rada modeli i model wizyjny będą pominięte.")
            return
        self.client = OpenRouter(key, budget_usd=self.cfg.budget_usd)
        models = self.client.models()
        members = self.cfg.council_models or pick_models(models, self.cfg.council_vendors, self.cfg.council_size)
        # Probe every model once: OpenRouter lists some (e.g. "decisions" models) that cannot chat at all.
        self.members = [m for m in members if self._probe(m)]
        chair = self.cfg.chair_model or (self.members[0] if self.members else "")
        self.chair = chair if chair in self.members or self._probe(chair) else (self.members[0] if self.members else "")
        vision = self.cfg.vision_model or (pick_models(models, self.cfg.council_vendors, 1, vision=True) or [""])[0]
        self.vision = vision if vision and self._probe(vision) else ""
        if len(self.members) < 2:
            print("UWAGA: mniej niż 2 działające modele w radzie; zmień council_models.")
        price = {m["id"]: m.get("pricing", {}) for m in models}
        print("Rada:", ", ".join(self.members), "| przewodniczący:", self.chair, "| model wizyjny:", self.vision or "brak")
        for m in self.members:
            p = price.get(m, {})
            print(f"  {m}: wejście {float(p.get('prompt') or 0) * 1e6:.2f} USD/M tok., wyjście "
                  f"{float(p.get('completion') or 0) * 1e6:.2f} USD/M tok.")

    def _probe(self, model: str) -> bool:
        """One tiny chat call; a model that refuses it is left out of the run with the reason shown."""
        if not model:
            return False
        try:
            self.client.chat(model, [{"role": "user", "content": "Odpowiedz jednym słowem: OK"}], max_tokens=5)
            return True
        except Exception as e:
            print(f"  pomijam {model}: {str(e)[:200]}")
            return False

    # ---- theories

    def run(self, name: str) -> TheoryResult:
        theory = THEORIES[name]
        problems = corpus.data_problems()
        if problems:
            # Every theory compares against the reference texts; a gap would silently shift all distances.
            raise RuntimeError("Niekompletne dane – uruchom !python scripts/fetch_data.py:\n  " + "\n  ".join(problems))
        print(f"\n=== {theory.title} ({name}) ===", flush=True)
        fn = theory.load()
        res = fn(self.cfg, self.client, self.vision) if "openrouter" in theory.needs else fn(self.cfg)
        res.save(self.cfg.results_dir)
        self.results[name] = res
        print(f"Werdykt: {res.verdict}. {res.summary}")
        for c in res.controls:
            print(f"  {'OK ' if c.passed else 'BŁĄD'} {c.name}: {c.observed}")
        return res

    def run_all(self) -> None:
        for name in expand(self.cfg.theories):
            try:
                self.run(name)
            except Exception as e:  # one broken theory must not stop the others
                print(f"!!! {name}: {type(e).__name__}: {e}")

    # ---- council

    def recover(self, name: str) -> TheoryResult | None:
        """The newest saved result of a theory from an earlier run on this machine (after a kernel restart)."""
        root = self.cfg.results_dir.parent
        found = sorted(root.glob(f"*/{name}.json"), key=lambda p: p.stat().st_mtime)
        if not found:
            return None
        res = TheoryResult.load(found[-1])
        self.results[name] = res
        res.save(self.cfg.results_dir)
        print(f"Wynik {name} wczytany z {found[-1].parent.name}.", flush=True)
        return res

    def convene(self, names: list[str] | None = None) -> None:
        if not self.client or not self.members:
            print("Rada pominięta: brak połączenia z OpenRouter.")
            return
        chat = lambda model, messages, max_tokens: self.client.chat(model, messages, max_tokens)
        for name in names or list(self.results):
            res = self.results.get(name) or self.recover(name)
            if res is None:
                print(f"Rada pomija {name}: brak wyniku w tej sesji i na dysku.")
                continue
            print(f"Rada obraduje: {name} ...", flush=True)
            res.council = deliberate(res, self.members, self.chair, chat, self.cfg.council_language, self.cfg.max_tokens)
            res.save(self.cfg.results_dir)
            print(f"  głosy: {res.council.get('votes')}, wydano dotąd {self.client.spent_usd:.2f} USD")
            if res.council.get("error"):
                print("  przerwano:", res.council["error"])
                break

    # ---- the hunt

    def hunt(self, rounds: int = 4, per_hound: int = 2, workers: int | None = None) -> dict:
        """Council members as hounds: they invent recipes, the lab tests them with controls, repeat."""
        from .hounds import Hunt
        problems = corpus.data_problems()
        if problems:
            raise RuntimeError("Niekompletne dane – uruchom !python scripts/fetch_data.py:\n  " + "\n  ".join(problems))
        self.hunt_result = Hunt(self, rounds, per_hound, workers).run()
        return self.hunt_result

    # ---- report and git

    def report(self) -> Path:
        lines = [f"# Voynich Lab – przebieg {self.stamp}", "",
                 "| teoria | werdykt testów | kontrole | głosy rady |", "|---|---|---|---|"]
        for name, r in self.results.items():
            ok = sum(c.passed for c in r.controls)
            votes = ", ".join(f"{k}: {v}" for k, v in (r.council.get("votes") or {}).items()) or "–"
            lines.append(f"| {THEORIES[name].title} | {r.verdict} | {ok}/{len(r.controls)} | {votes} |")
        lines += ["", "Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.", ""]
        for name, r in self.results.items():
            lines += [f"## {THEORIES[name].title}", "", r.summary, ""]
            if r.council.get("synthesis"):
                lines += ["**Synteza rady:**", "", r.council["synthesis"], ""]
            lines.append(f"Szczegóły: [{name}.md]({name}.md)")
            lines.append("")
        hunt = getattr(self, "hunt_result", None)
        if hunt:
            ranked = sorted((e for e in hunt["entries"] if "score" in e["result"]), key=lambda e: -e["result"]["score"])
            lines += ["## Polowanie psów gończych", "",
                      f"Przetestowano {len(hunt['entries'])} przepisów; tropy (TROP): "
                      f"{sum(e['result']['verdict'] == 'TROP' for e in hunt['entries'])}.", "",
                      "| przepis | pies | werdykt | score | luka rękopisu |", "|---|---|---|---|---|"]
            lines += [f"| {e['recipe'].get('name')} | {e['hound']} | {e['result']['verdict']} | "
                      f"{e['result']['score']:+.2f} | {e['result']['gap_voynich']:.2f} |" for e in ranked[:10]]
            lines += ["", hunt.get("synthesis") or "", "", "Szczegóły: [hunt/hunt.md](hunt/hunt.md)", ""]
        if self.client:
            lines += [f"Koszt OpenRouter: {self.client.spent_usd:.2f} USD w {self.client.calls} wywołaniach. "
                      f"Rada: {', '.join(self.members)}; przewodniczący: {self.chair}."]
        path = self.cfg.results_dir / "REPORT.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        (self.cfg.results_dir / "costs.json").write_text(json.dumps(self.client.log if self.client else [], indent=1))
        return path

    def push(self) -> None:
        """Commit this run's folder to cfg.git_branch and push with the token from Colab Secrets."""
        token = self.cfg.secret(self.cfg.github_secret)
        if not token:
            print(f"Brak sekretu {self.cfg.github_secret}: wyniki zostają tylko lokalnie w {self.cfg.results_dir}")
            return
        out = self.publish(f"https://x-access-token:{token}@github.com/{self.cfg.git_repo}.git")
        print("Wypchnięto na gałąź", self.cfg.git_branch if out.returncode == 0 else f"BŁĄD: {out.stderr.replace(token, '***')}")

    def publish(self, url: str) -> subprocess.CompletedProcess:
        """Commit the results folder on top of the remote branch and push it, in a throw-away worktree.

        The code checkout is never touched: switching the main working tree to the results branch
        (an old copy of the code) once made every theory imported after the first push disappear.
        """
        import shutil
        import tempfile
        branch = self.cfg.git_branch
        git = lambda *a, cwd=ROOT, check=True: subprocess.run(["git", "-C", str(cwd), *a], check=check,
                                                                capture_output=True, text=True)
        author = ["-c", "user.name=Voynich Lab (Colab)", "-c", "user.email=voynich-lab@users.noreply.github.com"]
        wt = Path(tempfile.mkdtemp(prefix="lab-results-"))
        wt.rmdir()
        try:
            remote = git("ls-remote", "--heads", url, branch, check=False).stdout.strip()
            if remote:
                git("fetch", url, f"+{branch}:refs/remotes/lab/{branch}")
                git("worktree", "add", "--detach", str(wt), f"refs/remotes/lab/{branch}")
            else:
                git("worktree", "add", "--detach", str(wt))
                git("switch", "--orphan", f"lab-{self.stamp}", cwd=wt)
            rel = self.cfg.results_dir.relative_to(ROOT)
            shutil.copytree(self.cfg.results_dir, wt / rel, dirs_exist_ok=True)
            git("add", "-f", str(rel), cwd=wt)
            subprocess.run(["git", "-C", str(wt), *author, "commit", "-m", f"Voynich Lab: wyniki przebiegu {self.stamp}"],
                           check=False, capture_output=True, text=True)
            return git("push", url, f"HEAD:refs/heads/{branch}", cwd=wt, check=False)
        finally:
            git("worktree", "remove", "--force", str(wt), check=False)
            git("worktree", "prune", check=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theories", default="all")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--no-council", action="store_true")
    ap.add_argument("--budget", type=float, default=5.0)
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()
    cfg = LabConfig(theories=args.theories.split(","), quick=args.quick, budget_usd=args.budget)
    lab = Lab(cfg)
    if not args.no_council:
        lab.connect()
    lab.run_all()
    if not args.no_council:
        lab.convene()
    print("Raport:", lab.report())
    if args.push:
        lab.push()


if __name__ == "__main__":
    main()
