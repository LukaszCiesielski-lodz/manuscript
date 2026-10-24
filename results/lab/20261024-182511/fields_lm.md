# fields_lm: metoda niewiarygodna

**Hipoteza.** Słowo rękopisu zależy od swojego miejsca w wierszu jak pole od rubryki rekordu: model języka, który zna numer słowa w wierszu, przewiduje znaki wyraźnie lepiej.

**Metoda.** Mały GPT znakowy (4 warstwy, 256 wymiarów, 2500 kroków) uczony dwa razy na każdym korpusie: tekst goły i tekst z tokenem pozycji przed każdym słowem (<p:0>, <p:1>, ... <p:12+>); bity na znak na odłożonych wierszach (znaki liczone, tokeny pozycji nie), różnica = zysk z pozycji, rozrzut z bootstrapu po wierszach. Korpusy: rękopis, łacina, chorał (słowa), bełkot v5, martyrologium, Apicius (po ok. 200 tys. znaków). Kontrole: tokeny pozycji losowe na rękopisie (zysk ≈ 0); rekordy syntetyczne o polach (duży zysk).

Zysk z tokenów pozycji (bit/znak): łacina -0.003, bełkot v5 -0.011, rękopis -0.017, apicius -0.030, martyrology -0.048, chorał -0.055. Rękopis wobec bełkotu v5: -0.006 (próg +0,05); kontrola losowa -0.013, rekordy syntetyczne +0.012.

## Kontrole

- ❌ **rekordy syntetyczne o polach: tokeny pozycji dają zysk**: oczekiwano Δ ≥ 0,15 bit/znak; wynik: Δ = 0.012 ± 0.008
- ✅ **rękopis z losowymi tokenami pozycji: brak zysku**: oczekiwano Δ ≤ 0,01; wynik: Δ = -0.013 ± 0.004

## Dowody

- rękopis: 1.696 bit/znak bez pozycji, 1.712 z pozycją; zysk Δ = -0.017 ± 0.004 (386 wierszy testowych, 200020 znaków).
- łacina: 1.982 bit/znak bez pozycji, 1.984 z pozycją; zysk Δ = -0.003 ± 0.008 (346 wierszy testowych, 200066 znaków).
- chorał: 2.240 bit/znak bez pozycji, 2.296 z pozycją; zysk Δ = -0.055 ± 0.011 (218 wierszy testowych, 200027 znaków).
- bełkot v5: 1.723 bit/znak bez pozycji, 1.734 z pozycją; zysk Δ = -0.011 ± 0.003 (408 wierszy testowych, 200031 znaków).
- apicius: 1.364 bit/znak bez pozycji, 1.402 z pozycją; zysk Δ = -0.030 ± 0.011 (38 wierszy testowych, 100115 znaków).
- martyrology: 1.330 bit/znak bez pozycji, 1.375 z pozycją; zysk Δ = -0.048 ± 0.008 (39 wierszy testowych, 200540 znaków).

## Zastrzeżenia

- Zysk obejmuje też krawędzie wiersza (znane nawyki p/m/g); bełkot v5 ma te nawyki wbudowane, stąd porównanie z nim.
- Jeden przebieg na korpus (ziarno cfg.seed); rozrzut z bootstrapu po wierszach, nie z wielu treningów.

## Literatura

- Radford et al., Language models are unsupervised multitask learners (2019)
- Karpathy, nanoGPT

_Czas: 577 s · 2026-10-24 18:34_