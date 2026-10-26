# lengthkey: nierozstrzygnięta

**Hipoteza.** Klucz szyfru zależy od długości słowa: słowa jedno-, dwu-, ..., dziewięcio- i więcej glifowe mają własne alfabety podstawieniowe (odstępy wybierają klucz).

**Metoda.** Glif g w słowie o klasie długości c staje się symbolem g#c (klasy 1–8 i 9+); wspinaczka homofoniczna (8192 wspinaczy, 3000 kroków, model 4-gramowy na cuda) nad takimi symbolami to dziewięć kluczy naraz. Dla każdego języka: bity na znak na wierszach parzystych z jednym kluczem i z kluczami po długości, dla rękopisu, bełkotu v5 i glifów przemianowanych w każdym wierszu (tło: więcej kluczy zawsze trochę pomaga). Kontrola dodatnia: tekst języka zaszyfrowany dziewięcioma kluczami, klucze odzyskane w ≥ 60% symboli. Trop: zysk rękopisu z kluczy po długości ≥ zysk v5 + 0,2 bitu i ≥ zysk przemianowanych + 0,2, przy wyniku ≤ naturalny + 0,8.

Tropy: brak; 6 języków. Największa przewaga zysku rękopisu nad bełkotem: French (-1.16 wobec -1.17 bitu); rękopis z kluczami po długości 5.19 bit/znak wobec naturalnego 2.64.

## Kontrole


## Dowody

- Latin: rękopis 4.24 → 5.01 bit/znak (zysk -0.77); bełkot v5 4.11 → 4.79 (zysk -0.68); przemianowane 6.71 → 7.43 (zysk -0.73); naturalny 2.99; szyfr testowy odzyskany w 38%. Odczyt pierwszego wiersza: „ritas edem et inite eis meme rman i”.
- Italian: rękopis 4.29 → 5.09 bit/znak (zysk -0.81); bełkot v5 4.11 → 4.81 (zysk -0.69); przemianowane 6.77 → 7.88 (zysk -1.10); naturalny 2.31; szyfr testowy odzyskany w 27%. Odczyt pierwszego wiersza: „seeeo iseo un ebere sei aioi rori a”.
- German: rękopis 4.30 → 5.23 bit/znak (zysk -0.93); bełkot v5 4.23 → 5.07 (zysk -0.83); przemianowane 7.20 → 7.88 (zysk -0.68); naturalny 2.24; szyfr testowy odzyskany w 44%. Odczyt pierwszego wiersza: „zsenb esen de sisen hen aere grss s”.
- French: rękopis 4.03 → 5.19 bit/znak (zysk -1.16); bełkot v5 3.96 → 5.13 (zysk -1.17); przemianowane 6.94 → 7.73 (zysk -0.79); naturalny 2.64; szyfr testowy odzyskany w 36%. Odczyt pierwszego wiersza: „ertse eret ns reras ain aese csrc c”.
- Spanish: rękopis 4.34 → 5.21 bit/znak (zysk -0.87); bełkot v5 4.24 → 5.03 (zysk -0.79); przemianowane 7.08 → 8.07 (zysk -1.00); naturalny 2.49; szyfr testowy odzyskany w 27%. Odczyt pierwszego wiersza: „ciper ocen al icido les roso rses q”.
- Czech: rękopis 4.84 → 5.62 bit/znak (zysk -0.78); bełkot v5 4.72 → 5.35 (zysk -0.63); przemianowane 7.85 → 8.30 (zysk -0.45); naturalny 2.64; szyfr testowy odzyskany w 18%. Odczyt pierwszego wiersza: „jeeen enam ta elest sem zame nmim a”.

## Zastrzeżenia

- Dziewięć kluczy to dziewięć razy więcej swobody: każdy tekst zyskuje; liczy się tylko nadwyżka zysku nad bełkotem i nad glifami przemianowanymi.
- Klasy długości liczone w glifach EVA (ch, sh, cth jako jeden); długości 9+ razem, bo powyżej to 0,2% słów.

## Literatura

- Van Eycke, AZdecrypt (2017–2021)
- Stolfi, On the VMS word length distribution (2000)

_Czas: 2265 s · 2026-10-26 21:18_