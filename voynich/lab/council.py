"""A council of models discusses each result in three rounds.

1. Opinions: every member judges the evidence alone and answers in JSON.
2. Review: every member sees the others' opinions, anonymised as A, B, C...,
   ranks them and may change its verdict.
3. Synthesis: the chair writes the final assessment from both rounds.

The members only judge the numbers the pipeline produced. They are told not
to propose readings of the manuscript, because language models readily invent
"decipherments" that no test supports.
"""

from __future__ import annotations

import json
import string
from typing import Callable

from .openrouter import BudgetExceeded, parse_json
from .results import TheoryResult

Chat = Callable[[str, list[dict], int], str]

SYSTEM = """Jesteś członkiem rady naukowej oceniającej testy hipotez o rękopisie Wojnicza (Beinecke MS 408).
Zasady:
- Oceniasz WYŁĄCZNIE dowody z raportu: liczby, kontrole metody, zastrzeżenia. Nie dodawaj własnych odczytań rękopisu i nie podawaj tłumaczeń jego tekstu.
- Test jest wiarygodny tylko wtedy, gdy jego kontrole przeszły: metoda musi znaleźć efekt podłożony celowo i nie znajdować go w danych przetasowanych.
- Oddziel to, co test wyklucza, od tego, czego nie bada. Wskaż konkretne słabości i jeden następny test, który najbardziej zmieniłby ocenę.
- Pisz po {lang}, rzeczowo i krótko."""

ROUND1 = """Raport z testu:

{brief}

Odpowiedz obiektem JSON:
{{"werdykt": "potwierdzona" | "obalona" | "nierozstrzygnięta" | "metoda niewiarygodna",
  "pewność": liczba 0-1,
  "najmocniejszy_dowód": "...",
  "słabości": ["...", "..."],
  "inne_wyjaśnienia": ["..."],
  "następny_test": "..."}}"""

ROUND2 = """Raport z testu:

{brief}

Opinie innych członków rady (anonimowe):

{others}

Oceń je: która jest najlepiej uzasadniona danymi i dlaczego, gdzie ktoś się myli. Potem podaj swój ostateczny werdykt.
Odpowiedz obiektem JSON:
{{"ranking": ["A", "B", ...], "uwagi": "...", "werdykt": "...", "pewność": liczba 0-1, "zmiana_zdania": "tak/nie i dlaczego"}}"""

SYNTH = """Jesteś przewodniczącym rady. Raport z testu:

{brief}

Runda 1 (opinie niezależne):
{r1}

Runda 2 (po przeczytaniu innych):
{r2}

Napisz syntezę w Markdown (do 250 słów): **Werdykt rady**, poziom zgody, co test naprawdę pokazuje, główne zastrzeżenia, jeden rekomendowany następny eksperyment. Nie podawaj żadnych odczytań tekstu rękopisu."""


def _ask(chat: Chat, model: str, system: str, user: str, max_tokens: int) -> str:
    return chat(model, [{"role": "system", "content": system}, {"role": "user", "content": user}], max_tokens)


def deliberate(result: TheoryResult, members: list[str], chair: str, chat: Chat,
               language: str = "polski", max_tokens: int = 1800) -> dict:
    system = SYSTEM.format(lang=language)
    brief = result.brief()
    out: dict = {"members": members, "chair": chair, "round1": {}, "round2": {}, "synthesis": ""}
    try:
        for m in members:
            text = _ask(chat, m, system, ROUND1.format(brief=brief), max_tokens)
            out["round1"][m] = {"raw": text, "json": parse_json(text)}
        labels = dict(zip(members, string.ascii_uppercase))
        for m in members:
            others = "\n\n".join(f"Opinia {labels[o]}:\n{json.dumps(r['json'] or r['raw'], ensure_ascii=False)[:2500]}"
                                 for o, r in out["round1"].items() if o != m)
            text = _ask(chat, m, system, ROUND2.format(brief=brief, others=others), max_tokens)
            out["round2"][m] = {"raw": text, "json": parse_json(text)}
        fmt = lambda rnd: "\n".join(f"- {labels[m]}: {json.dumps(r['json'] or r['raw'], ensure_ascii=False)[:1500]}"
                                    for m, r in rnd.items())
        out["synthesis"] = _ask(chat, chair, system, SYNTH.format(brief=brief, r1=fmt(out["round1"]),
                                                                  r2=fmt(out["round2"])), max_tokens)
    except BudgetExceeded as e:
        out["error"] = str(e)
    verdicts = [r["json"].get("werdykt") for r in out["round2"].values() if r.get("json")]
    out["votes"] = {v: verdicts.count(v) for v in set(verdicts) if v}
    return out
