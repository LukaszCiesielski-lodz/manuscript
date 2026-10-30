# Voynich Lab – przebieg 20261030-140042

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Szkic atomów na własnym GPU: Molmo2 + geometria + Qwen3-VL (nie test) | nierozstrzygnięta | 0/0 | – |
| Rebus w rysunkach: cechy atomów ilustracji wobec etykiet | nierozstrzygnięta | 2/2 | – |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Szkic atomów na własnym GPU: Molmo2 + geometria + Qwen3-VL (nie test)

Szkic 12 stron w atoms_vision/ (do sprawdzenia na PNG, poprawienia i scalenia z data/atoms).

Szczegóły: [atoms_vision.md](atoms_vision.md)

## Rebus w rysunkach: cechy atomów ilustracji wobec etykiet

Dane niekompletne: opisanych 0 z 853 atomów (próg 100). Metoda sprawdzona na losowym wypełnieniu: podłożony glif z = 68, przetasowane cechy bez związku.

Szczegóły: [atoms.md](atoms.md)

Koszt OpenRouter: 0.00 USD w 5 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.