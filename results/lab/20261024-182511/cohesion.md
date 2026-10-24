# cohesion: metoda niewiarygodna

**Hipoteza.** Wiersze jednej strony należą do siebie (jeden wpis, jeden przedmiot) ponad to, co wynika z działu i dialektu: sędzia pozna dwa wiersze z tej samej strony.

**Metoda.** Transformer znakowy (4 warstwy, 192 wymiary) na parach połówek wierszy „A|B” (47 znaków każda): ta sama strona wobec innej strony tego samego działu i dialektu; 3000 par uczących ze stron uczących, 1500 testowych ze stron odłożonych; AUC. Przebiegi: rękopis; rękopis z wierszami rozdanymi na pseudostrony w dziale i dialekcie (kontrola ujemna); bełkot v5 na pseudostronach po 15 wierszy; łacina na pseudostronach; łacina z wszczepionym słowem strony w 20% słów (kontrola dodatnia).

Para wierszy z tej samej strony: AUC rękopisu 0.526 wobec 0.500 po rozdaniu wierszy i 0.500 dla bełkotu v5 (łacina 0.500, z wszczepionym słowem 0.654). Strona rękopisu nie jest spójniejsza niż losowy zbiór wierszy jej działu.

## Kontrole

- ✅ **rękopis z wierszami rozdanymi w dziale i dialekcie: sędzia bez oparcia**: oczekiwano AUC ≤ 0,58; wynik: 0.500
- ❌ **łacina z wszczepionym słowem strony: sędzia poznaje stronę**: oczekiwano AUC ≥ 0,7; wynik: 0.654

## Dowody

- rękopis: AUC 0.526 (206 stron, 3000 par uczących, 1500 testowych).
- rękopis, wiersze rozdane na pseudostrony: AUC 0.500 (338 stron, 3000 par uczących, 1500 testowych).
- bełkot v5 na pseudostronach: AUC 0.500 (139 stron, 3000 par uczących, 1500 testowych).
- łacina na pseudostronach: AUC 0.500 (274 stron, 3000 par uczących, 1500 testowych).
- łacina ze słowem strony (20%): AUC 0.654 (274 stron, 3000 par uczących, 1500 testowych).

## Zastrzeżenia

- Ręka skryby i dział są w tle wspólne dla strony i pseudostrony tylko wtedy, gdy grupa rozdania to dział i dialekt; różnice rąk w obrębie działu mogą dodać sędziemu oparcia.
- Połówki wierszy po 47 znaków: długie wiersze obcięte, krótkie dopełnione.

## Literatura

- Vaswani et al., Attention is all you need (2017)

_Czas: 39 s · 2026-10-24 18:44_