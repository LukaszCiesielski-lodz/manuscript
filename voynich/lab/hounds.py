"""The hunt: council members as hounds that invent, test and refine hypotheses.

Each round every hound sees what is known, the recipe language, the leaderboard
so far and its own past recipes, and proposes new recipes. The lab runs each
recipe with its controls (see recipes.py) in parallel processes. After the
last round the best scent trails are re-run on another part of the manuscript,
because with dozens of attempts some will look good by luck. The chair then
writes what the pack found. Ideas the recipe language cannot express are kept
as a wish list for new building blocks.
"""

from __future__ import annotations

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from .. import corpus, eva, selfcite
from .openrouter import BudgetExceeded, parse_json
from .recipes import Settings, Shared, dsl_doc, fingerprint, run_recipe, validate

PERSONAS = [
    ("kryptolog", "Jesteś kryptologiem znającym szyfry XV i XVI wieku (Alberti, Trithemius, nomenklatory, nulle, "
                  "szyfry rozwlekłe). Szukasz mechanizmu, który skryba mógł wykonać ręcznie."),
    ("lingwista", "Jesteś lingwistą historycznym. Myślisz o tym, jaki język i jaka ortografia mogły stać za tekstem "
                  "i jak pismo mogło gubić lub dodawać informację."),
    ("sceptyk", "Jesteś statystykiem-sceptykiem. Projektujesz przepisy, które odróżnią prawdziwy sygnał od artefaktu, "
                "i sprawdzasz najlepsze tropy innych w zmienionych warunkach."),
    ("dziki pies", "Jesteś psem gończym od nieoczywistych tropów: stałe matematyczne, daty, kalendarze, astrologia, "
                   "zabawy literackie epoki. Proponujesz pomysły, na które nikt by nie wpadł, ale zawsze sprawdzalne."),
]

KNOWN = """Co już wiadomo (z testów tego projektu, z kontrolami):
- Entropia warunkowa h2 rękopisu 2,30 bita na glif; 13 języków ma 2,9–3,65. Podstawienie znaków jej nie zmienia.
- Szyfr podstawieniowy (prosty i homofoniczny) łaciny, łaciny średniowiecznej, włoskiego, niemieckiego, polskiego, czeskiego,
  angielskiego, węgierskiego, fińskiego, tureckiego, hebrajskiego, arabskiego i baskijskiego: obalony (luka ~1,0–1,5 bita/znak).
- Glify mają sztywne miejsca w słowie (q na początku 99%, n na końcu 98%); słowa krótkie (4,3 glifu) o wąskim rozkładzie długości.
- 69% różnych słów występuje raz; słowo powtarza się zaraz po sobie w 0,83% par (w językach ≤ 0,22%).
- Sąsiednie słowa są do siebie podobne 2× częściej niż przypadkiem; glify na styku słów są powiązane (0,17 bita).
- Wiersz jest jednostką: m i g ~6× częściej w ostatnim słowie wiersza, p ~2,4× w pierwszym.
- Szyfr Naibbe-podobny odtwarza entropię, ale nie powiązania na styku słów; kratka Cardana obalona; atak anagramowy
  z hebrajskim jest nieswoisty (znajduje 'hebrajski' także w angielskim i wietnamskim).
Każdy przepis przechodzi automatyczne kontrole: musi odzyskać tekst docelowy zaszyfrowany tym samym przepisem (kontrola
dodatnia) i dać rękopisowi wyraźnie lepszy wynik niż bełkotowi o tej samej statystyce (kontrole ujemne). Wynik 'score'
to przewaga rękopisu nad bełkotem w bitach na znak; 'TROP' wymaga luki rękopisu < 0,5, score > 0,3 i odczytu prawie
tak przewidywalnego jak prawdziwy tekst w języku docelowym (nadmiar < 0,6 bita/znak)."""

ASK = """{persona}

{known}

JĘZYK PRZEPISÓW:
{doc}

Przykład przepisu:
{{"name": "pi jako klucz Vigenère'a", "idea": "cyfry π przesuwają kolejne glify, licznik od nowa w każdym wierszu",
  "scope": {{"section": "herbal"}}, "steps": [{{"op": "keystream_shift", "key": "pi", "mode": "sub", "unit": "glyph", "restart": "line"}}],
  "target": "Latin", "target_ops": []}}

{board}

{own}

Runda {round} z {rounds}. Zaproponuj {k} NOWE przepisy (nie powtarzaj już sprawdzonych). Część może rozwijać najlepsze tropy,
część powinna iść w zupełnie inną stronę. Pomysły, których nie da się zapisać tymi klockami, opisz w 'poza_klockami'.
Odpowiedz wyłącznie obiektem JSON: {{"recipes": [...], "poza_klockami": ["..."]}}"""

SYNTH = """Jesteś przewodniczącym rady. Sfora modeli przez {rounds} rund wymyślała i testowała przepisy odczytu rękopisu Wojnicza.

{known}

Tabela wyników (najlepsze na górze):
{board}

Powtórka najlepszych tropów na innej części rękopisu:
{confirm}

Pomysły spoza języka przepisów (lista życzeń):
{wishes}

Napisz podsumowanie w Markdown (do 350 słów): co sfora sprawdziła, czy którykolwiek trop przetrwał kontrole i powtórkę,
jakie kierunki są martwe, jakie warto rozwinąć, i które nowe klocki z listy życzeń dodać najpierw. Nie podawaj własnych
odczytań tekstu rękopisu."""


def build_shared(cfg, n_null_words: int = 40000) -> Shared:
    """Manuscript lines and a meaningless null text with the manuscript's statistics (generator v4)."""
    lines = corpus.load_voynich()
    para = [l for l in lines if l.kind.startswith("P")]
    glyph_words = [eva.glyphs(w) for l in lines for w in l.words]
    gen = selfcite.generate([[eva.glyphs(w) for w in l.words] for l in para[:3]], n_null_words,
                            [len(l.words) for l in para], p_copy=0.22, window=8, p_far=0.05, seed=cfg.seed,
                            edits=selfcite.EditModel(glyph_words), grammar=selfcite.WordGrammar(glyph_words, beta=5))
    null_lines = [(f"g{i // 25}", l) for i, l in enumerate(gen)]
    return Shared(voynich_lines=lines, null_lines=null_lines, seed=cfg.seed)


_SHARED: Shared | None = None


def _init(shared: Shared) -> None:
    global _SHARED
    _SHARED = shared


def _work(args):
    recipe, settings = args
    t = time.time()
    res = run_recipe(recipe, _SHARED, settings)
    res["seconds"] = round(time.time() - t, 1)
    return res


def board_text(entries: list[dict], top: int = 15) -> str:
    ranked = sorted((e for e in entries if "score" in e["result"]), key=lambda e: -e["result"]["score"])
    rows = ["TABELA (score = przewaga rękopisu nad bełkotem; luka = bity/znak, im mniej tym lepiej):"]
    for e in ranked[:top]:
        r = e["result"]
        rows.append(f"- [{r['verdict']}] score {r['score']:+.2f} | luka rękopisu {r['gap_voynich']:.2f}, bełkot "
                    f"{min(r['gap_null_generator'], r['gap_null_shuffled']):.2f}, kontrola dodatnia {r['gap_positive']:.2f}, "
                    f"nadmiar nad językiem {r['excess_over_language']:+.2f} "
                    f"| {e['recipe'].get('name')} ({e['hound']}): {json.dumps({k: e['recipe'].get(k) for k in ('scope', 'steps', 'target', 'target_ops')}, ensure_ascii=False)}")
    bad = [e for e in entries if e["result"]["verdict"] in ("błąd przepisu", "metoda niewiarygodna")][-8:]
    if bad:
        rows.append("Przepisy odrzucone lub z nieudaną kontrolą dodatnią (ostatnie):")
        rows += [f"- {e['recipe'].get('name')}: {e['result'].get('error') or 'kontrola dodatnia nie odzyskała tekstu'}" for e in bad]
    return "\n".join(rows) if len(rows) > 1 else "Na razie brak wyników."


class Hunt:
    def __init__(self, lab, rounds: int = 4, per_hound: int = 2, workers: int | None = None):
        self.lab, self.rounds, self.per_hound = lab, rounds, per_hound
        self.workers = workers or max(1, (os.cpu_count() or 2) - 1)
        q = lab.cfg.quick
        self.settings = Settings(n_words=2000 if q else 4000, steps=15000 if q else 25000, restarts=4 if q else 6)
        self.entries: list[dict] = []
        self.wishes: list[dict] = []
        self.seen: set[str] = set()
        self.silent: list[dict] = []   # replies with no parsable recipe, kept to diagnose a model
        self.out_dir: Path = lab.cfg.results_dir / "hunt"
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def _ask(self, hound_i: int, model: str, round_no: int) -> list[dict]:
        name, persona = PERSONAS[hound_i % len(PERSONAS)]
        own = [e for e in self.entries if e["model"] == model][-6:]
        own_txt = ("Twoje dotychczasowe przepisy i wyniki:\n" + "\n".join(
            f"- {e['recipe'].get('name')}: {e['result']['verdict']}"
            + (f", score {e['result']['score']:+.2f}" if "score" in e["result"] else f" ({e['result'].get('error', '')})")
            for e in own)) if own else "To Twoja pierwsza runda."
        prompt = ASK.format(persona=persona, known=KNOWN, doc=dsl_doc(), board=board_text(self.entries), own=own_txt,
                            round=round_no, rounds=self.rounds, k=self.per_hound)
        messages = [{"role": "user", "content": prompt}]
        text = self.lab.client.chat(model, messages, self.lab.cfg.max_tokens)
        data = parse_json(text)
        if not data.get("recipes"):
            # inception/mercury-3 (sceptyk) answered every round without a parsable recipe in Colab; ask once more.
            messages += [{"role": "assistant", "content": text},
                         {"role": "user", "content": 'Nie znalazłem przepisów. Odpowiedz wyłącznie obiektem JSON '
                                                     '{"recipes": [...], "poza_klockami": [...]}, bez komentarza.'}]
            text = self.lab.client.chat(model, messages, self.lab.cfg.max_tokens)
            data = parse_json(text)
            if not data.get("recipes"):
                self.silent.append({"hound": name, "model": model, "round": round_no, "reply": text[:600]})
                print(f"  {model} ({name}): brak przepisu w odpowiedzi: {text[:120]!r}")
        for w in data.get("poza_klockami") or []:
            self.wishes.append({"hound": name, "model": model, "round": round_no, "idea": str(w)[:400]})
        recipes = data.get("recipes") or []
        return [r for r in recipes if isinstance(r, dict)][: self.per_hound + 1]

    def _run(self, batch: list[tuple[dict, Settings]]) -> list[dict]:
        if self.workers == 1:
            _init(self.shared)
            return [_work(b) for b in batch]
        with ProcessPoolExecutor(self.workers, initializer=_init, initargs=(self.shared,)) as ex:
            return list(ex.map(_work, batch))

    def run(self) -> dict:
        lab = self.lab
        if not lab.client or not lab.members:
            raise RuntimeError("Sfora potrzebuje połączenia z OpenRouter (lab.connect()).")
        print("Przygotowuję tekst kontrolny (generator v4)...", flush=True)
        self.shared = build_shared(lab.cfg)
        try:
            for rnd in range(1, self.rounds + 1):
                print(f"\n--- Runda {rnd}/{self.rounds} ---", flush=True)
                batch, meta = [], []
                for i, model in enumerate(lab.members):
                    try:
                        proposals = self._ask(i, model, rnd)
                    except BudgetExceeded:
                        raise
                    except Exception as e:
                        print(f"  {model}: brak propozycji ({str(e)[:150]})")
                        continue
                    for rec in proposals:
                        fp = fingerprint(rec) if not validate(rec) else None
                        if fp and fp in self.seen:
                            continue
                        if fp:
                            self.seen.add(fp)
                        batch.append((rec, self.settings))
                        meta.append((PERSONAS[i % len(PERSONAS)][0], model))
                print(f"  testuję {len(batch)} przepisów na {self.workers} procesach...", flush=True)
                for (rec, _), (hound, model), res in zip(batch, meta, self._run(batch)):
                    self.entries.append({"round": rnd, "hound": hound, "model": model, "recipe": rec, "result": res})
                    tag = f"score {res['score']:+.2f}" if "score" in res else res.get("error", "")[:90]
                    print(f"  [{res['verdict']}] {rec.get('name', '?')} ({hound}) {tag}")
                self._save()
        except BudgetExceeded as e:
            print("Budżet wyczerpany:", e)
        return self.finish()

    def finish(self) -> dict:
        ranked = sorted((e for e in self.entries if "score" in e["result"]), key=lambda e: -e["result"]["score"])
        confirm = []
        top = [e for e in ranked if e["result"]["verdict"] in ("TROP", "niejasny")][:3]
        if top:
            print(f"\nPowtórka {len(top)} najlepszych tropów na innej części rękopisu...", flush=True)
            s2 = Settings(self.settings.n_words, self.settings.steps, self.settings.restarts + 1, slice=1)
            for e, res in zip(top, self._run([(e["recipe"], s2) for e in top])):
                confirm.append({"name": e["recipe"].get("name"), "first": e["result"], "repeat": res})
                print(f"  {e['recipe'].get('name')}: {e['result']['verdict']} → {res['verdict']}")
        synthesis = ""
        if self.lab.client and self.lab.chair:
            try:
                synthesis = self.lab.client.chat(self.lab.chair, [{"role": "user", "content": SYNTH.format(
                    rounds=self.rounds, known=KNOWN, board=board_text(self.entries, 25),
                    confirm=json.dumps([{"name": c["name"], "przed": c["first"]["verdict"], "po": c["repeat"]["verdict"],
                                         "score_po": c["repeat"].get("score")} for c in confirm], ensure_ascii=False),
                    wishes="\n".join(f"- ({w['hound']}) {w['idea']}" for w in self.wishes) or "brak")}],
                    self.lab.cfg.max_tokens)
            except Exception as e:
                synthesis = f"(synteza niedostępna: {e})"
        self.summary = {"entries": self.entries, "confirm": confirm, "wishes": self.wishes, "silent": self.silent, "synthesis": synthesis,
                        "settings": self.settings.__dict__, "spent_usd": self.lab.client.spent_usd if self.lab.client else 0}
        self._save()
        return self.summary

    def _save(self) -> None:
        data = getattr(self, "summary", {"entries": self.entries, "wishes": self.wishes})
        (self.out_dir / "hunt.json").write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        md = ["# Polowanie psów gończych", "", board_text(self.entries, 40), ""]
        if getattr(self, "summary", None):
            md += ["## Powtórka", ""] + ([f"- {c['name']}: {c['first']['verdict']} → {c['repeat']['verdict']}"
                                         for c in self.summary["confirm"]]
                                        or ["Brak kandydatów: żaden przepis nie dostał werdyktu TROP ani „niejasny”."])
            if self.silent:
                md += ["", "## Psy bez przepisów", ""] + [f"- {x['model']} ({x['hound']}, runda {x['round']}): "
                                                          f"{x['reply'][:200]!r}" for x in self.silent]
            md += ["", "## Lista życzeń (nowe klocki)", ""] + [f"- ({w['hound']}) {w['idea']}" for w in self.wishes]
            md += ["", "## Synteza przewodniczącego", "", self.summary["synthesis"]]
        (self.out_dir / "hunt.md").write_text("\n".join(md), encoding="utf-8")
