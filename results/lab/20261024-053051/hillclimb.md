# hillclimb: obalona

**Hipoteza.** Tekst to szyfr homofoniczny (kilka glifów na literę) któregoś z języków epoki; klucz da się odzyskać wspinaczką z modelem n-gramowym, jak w klasycznych łamaczach (AZdecrypt).

**Metoda.** Dla każdego z 52 leksykonów: model 4-gramowy znaków z próbki tekstu; 8192 wspinaczy równolegle na cuda przez 3000 kroków (wyżarzanie), każdy zmienia literę jednego glifu; klucz dopasowany na wierszach nieparzystych, oceniany na parzystych (bity na znak). To samo dla bełkotu v5 o statystyce rękopisu. Kontrola dodatnia: tekst języka zaszyfrowany homofonicznie na tyle glifów, ile ma rękopis; wspinacz musi odzyskać klucz.

Tropy: brak; 51 języków testowalnych, 1 nietestowalnych. Najbliżej tekstu naturalnego: OldFrench (4.01 wobec 3.85 bit/znak; bełkot 3.96).

## Kontrole

- ✅ **Afrikaans: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.25 bit/znak wobec naturalnego 2.33)
- ✅ **Albanian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.35 bit/znak wobec naturalnego 2.42)
- ✅ **AncientGreek: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.71 bit/znak wobec naturalnego 2.66)
- ✅ **Arabic: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.24 bit/znak wobec naturalnego 2.31)
- ✅ **Basque: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.25 bit/znak wobec naturalnego 2.28)
- ✅ **BasqueNews: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.72 bit/znak wobec naturalnego 2.76)
- ✅ **BiblicalHebrew: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 99% (wynik 3.18 bit/znak wobec naturalnego 3.20)
- ✅ **Bulgarian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.46 bit/znak wobec naturalnego 2.51)
- ✅ **ClassicalArmenian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.70 bit/znak wobec naturalnego 2.77)
- ✅ **Coptic: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 99% (wynik 3.26 bit/znak wobec naturalnego 3.25)
- ✅ **Croatian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.72 bit/znak wobec naturalnego 2.78)
- ✅ **Czech: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.64 bit/znak wobec naturalnego 2.64)
- ✅ **Danish: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.40 bit/znak wobec naturalnego 2.46)
- ✅ **Dutch: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.21 bit/znak wobec naturalnego 2.22)
- ✅ **English: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.39 bit/znak wobec naturalnego 2.40)
- ✅ **Finnish: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.46 bit/znak wobec naturalnego 2.47)
- ✅ **French: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.66 bit/znak wobec naturalnego 2.64)
- ✅ **German: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.24 bit/znak wobec naturalnego 2.24)
- ✅ **Gothic: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.60 bit/znak wobec naturalnego 2.63)
- ✅ **Greek: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.46 bit/znak wobec naturalnego 2.51)
- ✅ **Hebrew: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.43 bit/znak wobec naturalnego 2.42)
- ✅ **Hindi: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 88% (wynik 2.72 bit/znak wobec naturalnego 2.87)
- ✅ **Hungarian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.80 bit/znak wobec naturalnego 2.78)
- ✅ **Icelandic: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.46 bit/znak wobec naturalnego 2.52)
- ✅ **Irish: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.33 bit/znak wobec naturalnego 2.36)
- ✅ **Italian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.26 bit/znak wobec naturalnego 2.31)
- ✅ **Latin: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 3.03 bit/znak wobec naturalnego 2.99)
- ✅ **LatinAquinas: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.29 bit/znak wobec naturalnego 2.29)
- ✅ **Lithuanian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.28 bit/znak wobec naturalnego 2.32)
- ✅ **Maltese: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 3.15 bit/znak wobec naturalnego 3.20)
- ✅ **MedievalLatin: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.45 bit/znak wobec naturalnego 2.47)
- ✅ **MiddleFrench: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 99% (wynik 3.18 bit/znak wobec naturalnego 3.11)
- ✅ **Norwegian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.22 bit/znak wobec naturalnego 2.25)
- ✅ **OldChurchSlavonic: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.93 bit/znak wobec naturalnego 3.00)
- ✅ **OldEastSlavic: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.52 bit/znak wobec naturalnego 2.66)
- ✅ **OldFrench: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 94% (wynik 3.84 bit/znak wobec naturalnego 3.85)
- ✅ **Persian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 98% (wynik 3.43 bit/znak wobec naturalnego 3.54)
- ✅ **Polish: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.61 bit/znak wobec naturalnego 2.64)
- ✅ **Portuguese: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.31 bit/znak wobec naturalnego 2.41)
- ✅ **Romanian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.48 bit/znak wobec naturalnego 2.49)
- ✅ **Russian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.93 bit/znak wobec naturalnego 2.95)
- ✅ **Serbian: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.53 bit/znak wobec naturalnego 2.58)
- ✅ **Slovak: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.88 bit/znak wobec naturalnego 2.91)
- ✅ **Slovene: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.59 bit/znak wobec naturalnego 2.62)
- ✅ **Spanish: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.41 bit/znak wobec naturalnego 2.49)
- ✅ **Swedish: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.16 bit/znak wobec naturalnego 2.24)
- ✅ **Syriac: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 3.12 bit/znak wobec naturalnego 3.13)
- ✅ **Turkish: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 1.92 bit/znak wobec naturalnego 1.96)
- ✅ **Vietnamese: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 1.99 bit/znak wobec naturalnego 2.01)
- ✅ **VulgarLatin: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 1.91 bit/znak wobec naturalnego 1.97)
- ✅ **Welsh: zaszyfrowany homofonicznie prawdziwy tekst**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (wynik 2.91 bit/znak wobec naturalnego 2.93)

## Dowody

- Afrikaans: rękopis 3.91 bit/znak, bełkot v5 3.77, tekst naturalny 2.33; zaszyfrowany tekst odczytany do 2.25 z kluczem w 100%. Odczyt pierwszego wiersza: „neget egee ee egeen gee geee geet e”.
- Albanian: rękopis 4.38 bit/znak, bełkot v5 4.26, tekst naturalny 2.42; zaszyfrowany tekst odczytany do 2.35 z kluczem w 100%. Odczyt pierwszego wiersza: „enrte tene ne nende kte ktet eere t”.
- Amharic: nietestowalny – 28 glifów niesie tylko 12% tekstu tego pisma.
- AncientGreek: rękopis 4.45 bit/znak, bełkot v5 4.35, tekst naturalny 2.66; zaszyfrowany tekst odczytany do 2.71 z kluczem w 100%. Odczyt pierwszego wiersza: „νοεαι ανον ον ονους εαν εανα ιννι α”.
- Arabic: rękopis 4.11 bit/znak, bełkot v5 3.99, tekst naturalny 2.31; zaszyfrowany tekst odczytany do 2.24 z kluczem w 100%. Odczyt pierwszego wiersza: „والهل هلاك ان الانه لاك لانه لنيل ه”.
- Basque: rękopis 4.26 bit/znak, bełkot v5 4.20, tekst naturalny 2.28; zaszyfrowany tekst odczytany do 2.25 z kluczem w 100%. Odczyt pierwszego wiersza: „reiac arec en erera iec iena rnrc a”.
- BasqueNews: rękopis 3.99 bit/znak, bełkot v5 3.83, tekst naturalny 2.76; zaszyfrowany tekst odczytany do 2.72 z kluczem w 100%. Odczyt pierwszego wiersza: „teeak aten en etean ean eana tnrk a”.
- BiblicalHebrew: rękopis 4.39 bit/znak, bełkot v5 4.29, tekst naturalny 3.20; zaszyfrowany tekst odczytany do 3.18 z kluczem w 99%. Odczyt pierwszego wiersza: „לבלבל בלבל בל בלבבך לבל לבלב ללבל ב”.
- Bulgarian: rękopis 4.73 bit/znak, bełkot v5 4.56, tekst naturalny 2.51; zaszyfrowany tekst odczytany do 2.46 z kluczem w 100%. Odczyt pierwszego wiersza: „овсие иови ва вовия сти стаи оате и”.
- ClassicalArmenian: rękopis 4.87 bit/znak, bełkot v5 4.79, tekst naturalny 2.77; zaszyfrowany tekst odczytany do 2.70 z kluczem w 100%. Odczyt pierwszego wiersza: „սատաս ասան ան ասանի տան տանա սնես ա”.
- Coptic: rękopis 3.53 bit/znak, bełkot v5 3.46, tekst naturalny 3.25; zaszyfrowany tekst odczytany do 3.26 z kluczem w 99%. Odczyt pierwszego wiersza: „ⲧⲉⲛⲉⲛ ⲉⲧⲉⲛ ⲉⲛ ⲉⲧⲉⲧⲛ ⲛⲉⲛ ⲛⲉⲛⲉ ⲛⲛⲛⲛ ⲉ”.
- Croatian: rękopis 4.90 bit/znak, bełkot v5 4.72, tekst naturalny 2.78; zaszyfrowany tekst odczytany do 2.72 z kluczem w 100%. Odczyt pierwszego wiersza: „bonam abod og oboze nod noga jgam a”.
- Czech: rękopis 4.84 bit/znak, bełkot v5 4.72, tekst naturalny 2.64; zaszyfrowany tekst odczytany do 2.64 z kluczem w 100%. Odczyt pierwszego wiersza: „lazez ezal al azani zal zale nldz e”.
- Danish: rękopis 4.22 bit/znak, bełkot v5 4.11, tekst naturalny 2.46; zaszyfrowany tekst odczytany do 2.40 z kluczem w 100%. Odczyt pierwszego wiersza: „deeed enen en enere een eene dnnd e”.
- Dutch: rękopis 3.76 bit/znak, bełkot v5 3.70, tekst naturalny 2.22; zaszyfrowany tekst odczytany do 2.21 z kluczem w 100%. Odczyt pierwszego wiersza: „eegnn nren en ereen gen genn enen n”.
- English: rękopis 4.67 bit/znak, bełkot v5 4.52, tekst naturalny 2.40; zaszyfrowany tekst odczytany do 2.39 z kluczem w 100%. Odczyt pierwszego wiersza: „evase seve ve veven ase ases iese s”.
- Finnish: rękopis 3.95 bit/znak, bełkot v5 3.87, tekst naturalny 2.47; zaszyfrowany tekst odczytany do 2.46 z kluczem w 100%. Odczyt pierwszego wiersza: „nasat anan an anaan san sana tnat a”.
- French: rękopis 4.03 bit/znak, bełkot v5 3.96, tekst naturalny 2.64; zaszyfrowany tekst odczytany do 2.66 z kluczem w 100%. Odczyt pierwszego wiersza: „ertse sere re reres tre tres eere s”.
- German: rękopis 4.30 bit/znak, bełkot v5 4.23, tekst naturalny 2.24; zaszyfrowany tekst odczytany do 2.24 z kluczem w 100%. Odczyt pierwszego wiersza: „rehrr rher er ehein her herr hrer r”.
- Gothic: rękopis 4.07 bit/znak, bełkot v5 3.96, tekst naturalny 2.63; zaszyfrowany tekst odczytany do 2.60 z kluczem w 100%. Odczyt pierwszego wiersza: „aniia iana na nands ina inai aana i”.
- Greek: rękopis 4.46 bit/znak, bełkot v5 4.37, tekst naturalny 2.51; zaszyfrowany tekst odczytany do 2.46 z kluczem w 100%. Odczyt pierwszego wiersza: „λεθεν ελει εν ελεις θει θενε μνεν ε”.
- Hebrew: rękopis 4.44 bit/znak, bełkot v5 4.27, tekst naturalny 2.42; zaszyfrowany tekst odczytany do 2.43 z kluczem w 100%. Odczyt pierwszego wiersza: „בנותב תבני נו נבניו ולי ולות אושב ת”.
- Hindi: rękopis 4.48 bit/znak, bełkot v5 4.40, tekst naturalny 2.87; zaszyfrowany tekst odczytany do 2.72 z kluczem w 88%. Odczyt pierwszego wiersza: „लललकल कललक लक लललकर ललक ललकक लकलल क”.
- Hungarian: rękopis 4.61 bit/znak, bełkot v5 4.56, tekst naturalny 2.78; zaszyfrowany tekst odczytany do 2.80 z kluczem w 100%. Odczyt pierwszego wiersza: „nantn tnan ak anant nan nakt nkan t”.
- Icelandic: rękopis 4.42 bit/znak, bełkot v5 4.34, tekst naturalny 2.52; zaszyfrowany tekst odczytany do 2.46 z kluczem w 100%. Odczyt pierwszego wiersza: „anura rana na nanna una unar uana r”.
- Irish: rękopis 3.49 bit/znak, bełkot v5 3.49, tekst naturalny 2.36; zaszyfrowany tekst odczytany do 2.33 z kluczem w 100%. Odczyt pierwszego wiersza: „wwwww wwww ww wwwww www wwww wwww w”.
- Italian: rękopis 4.29 bit/znak, bełkot v5 4.11, tekst naturalny 2.31; zaszyfrowany tekst odczytany do 2.26 z kluczem w 100%. Odczyt pierwszego wiersza: „etsia iati to tatto sti stoi aota i”.
- Latin: rękopis 4.24 bit/znak, bełkot v5 4.11, tekst naturalny 2.99; zaszyfrowany tekst odczytany do 3.03 z kluczem w 100%. Odczyt pierwszego wiersza: „rtisi sate te tatis ite ites eeni s”.
- LatinAquinas: rękopis 4.14 bit/znak, bełkot v5 3.94, tekst naturalny 2.29; zaszyfrowany tekst odczytany do 2.29 z kluczem w 100%. Odczyt pierwszego wiersza: „tiuss stis is itius uis uiss usis s”.
- Lithuanian: rękopis 4.32 bit/znak, bełkot v5 4.20, tekst naturalny 2.32; zaszyfrowany tekst odczytany do 2.28 z kluczem w 100%. Odczyt pierwszego wiersza: „satis isas as asaus tis tisi rsas i”.
- Maltese: rękopis 4.23 bit/znak, bełkot v5 4.09, tekst naturalny 3.20; zaszyfrowany tekst odczytany do 3.15 z kluczem w 100%. Odczyt pierwszego wiersza: „nigan anin in inien gin gina nnħn a”.
- MedievalLatin: rękopis 3.86 bit/znak, bełkot v5 3.75, tekst naturalny 2.47; zaszyfrowany tekst odczytany do 2.45 z kluczem w 100%. Odczyt pierwszego wiersza: „iiisi siis is iiiis iis iiss isii s”.
- MiddleFrench: rękopis 4.55 bit/znak, bełkot v5 4.55, tekst naturalny 3.11; zaszyfrowany tekst odczytany do 3.18 z kluczem w 99%. Odczyt pierwszego wiersza: „setes eues es enent ces cese rsrs e”.
- Norwegian: rękopis 4.23 bit/znak, bełkot v5 4.14, tekst naturalny 2.25; zaszyfrowany tekst odczytany do 2.22 z kluczem w 100%. Odczyt pierwszego wiersza: „neset elen en elene sen sene tntt e”.
- OldChurchSlavonic: rękopis 4.62 bit/znak, bełkot v5 4.59, tekst naturalny 3.00; zaszyfrowany tekst odczytany do 2.93 z kluczem w 100%. Odczyt pierwszego wiersza: „аꙁнаа ааꙁа ꙁа ꙁаꙁна нна ннаа нана а”.
- OldEastSlavic: rękopis 4.78 bit/znak, bełkot v5 4.63, tekst naturalny 2.66; zaszyfrowany tekst odczytany do 2.52 z kluczem w 100%. Odczyt pierwszego wiersza: „нидин инии ии инити дии диии ниин и”.
- OldFrench: rękopis 4.01 bit/znak, bełkot v5 3.96, tekst naturalny 3.85; zaszyfrowany tekst odczytany do 3.84 z kluczem w 94%. Odczyt pierwszego wiersza: „seles eles es elent les lese lses e”.
- Persian: rękopis 3.92 bit/znak, bełkot v5 3.83, tekst naturalny 3.54; zaszyfrowany tekst odczytany do 3.43 z kluczem w 98%. Odczyt pierwszego wiersza: „ادبنم نادی دی دادان بری برین اییم ن”.
- Polish: rękopis 4.72 bit/znak, bełkot v5 4.65, tekst naturalny 2.64; zaszyfrowany tekst odczytany do 2.61 z kluczem w 100%. Odczyt pierwszego wiersza: „ensła łana na nanie sza szał aaza ł”.
- Portuguese: rękopis 4.34 bit/znak, bełkot v5 4.22, tekst naturalny 2.41; zaszyfrowany tekst odczytany do 2.31 z kluczem w 100%. Odczyt pierwszego wiersza: „caaam acas as acaos aas aasa csrm a”.
- Romanian: rękopis 3.97 bit/znak, bełkot v5 3.86, tekst naturalny 2.49; zaszyfrowany tekst odczytany do 2.48 z kluczem w 100%. Odczyt pierwszego wiersza: „ratai arau au arati cau caua ruei a”.
- Russian: rękopis 4.64 bit/znak, bełkot v5 4.53, tekst naturalny 2.95; zaszyfrowany tekst odczytany do 2.93 z kluczem w 100%. Odczyt pierwszego wiersza: „товев евот ов оводу вот вове ввов е”.
- Serbian: rękopis 4.90 bit/znak, bełkot v5 4.77, tekst naturalny 2.58; zaszyfrowany tekst odczytany do 2.53 z kluczem w 100%. Odczyt pierwszego wiersza: „nodod onog om onoga kog komo kmad o”.
- Slovak: rękopis 4.95 bit/znak, bełkot v5 4.86, tekst naturalny 2.91; zaszyfrowany tekst odczytany do 2.88 z kluczem w 100%. Odczyt pierwszego wiersza: „alsla lali la lalia sli slal aaka l”.
- Slovene: rękopis 4.92 bit/znak, bełkot v5 4.78, tekst naturalny 2.62; zaszyfrowany tekst odczytany do 2.59 z kluczem w 100%. Odczyt pierwszego wiersza: „gorov obod og obodo kod kogo dgdv o”.
- Spanish: rękopis 4.34 bit/znak, bełkot v5 4.24, tekst naturalny 2.49; zaszyfrowany tekst odczytany do 2.41 z kluczem w 100%. Odczyt pierwszego wiersza: „caear aras as araon eas easa rsrr a”.
- Swedish: rękopis 4.23 bit/znak, bełkot v5 4.13, tekst naturalny 2.24; zaszyfrowany tekst odczytany do 2.16 z kluczem w 100%. Odczyt pierwszego wiersza: „lasan arar at aratt sar sata lttn a”.
- Syriac: rękopis 3.91 bit/znak, bełkot v5 3.71, tekst naturalny 3.13; zaszyfrowany tekst odczytany do 3.12 z kluczem w 100%. Odczyt pierwszego wiersza: „ܡܠܘܐܘ ܐܡܠܐ ܠܐ ܠܡܠܟܐ ܘܠܐ ܘܠܐܐ ܡܐܠܘ ܐ”.
- Turkish: rękopis 4.73 bit/znak, bełkot v5 4.61, tekst naturalny 1.96; zaszyfrowany tekst odczytany do 1.92 z kluczem w 100%. Odczyt pierwszego wiersza: „lasas alan an ararı san sana ynts a”.
- Vietnamese: rękopis 5.51 bit/znak, bełkot v5 5.30, tekst naturalny 2.01; zaszyfrowany tekst odczytany do 1.99 z kluczem w 100%. Odczyt pierwszego wiersza: „chhat achi hi hchoi tai taia tiut a”.
- VulgarLatin: rękopis 4.47 bit/znak, bełkot v5 4.30, tekst naturalny 1.97; zaszyfrowany tekst odczytany do 1.91 z kluczem w 100%. Odczyt pierwszego wiersza: „itesa sati ta tatem ati atas iana s”.
- Welsh: rękopis 3.93 bit/znak, bełkot v5 3.80, tekst naturalny 2.93; zaszyfrowany tekst odczytany do 2.91 z kluczem w 100%. Odczyt pierwszego wiersza: „eddii iedi di deddi ddi ddii eidi i”.

## Zastrzeżenia

- Model języka z próbki ok. 8 tys. słów; dla szyfru z nullami, skrótami lub zmienną segmentacją wspinaczka po samym kluczu glif–litera nie wystarczy.
- Bełkot v5 ma statystykę rękopisu, więc wynik rękopisu musi go wyraźnie przebić, by coś znaczył.

## Rada modeli

## Werdykt rady

**Test jest niewiarygodny jako podstawa kategorycznego obalenia hipotezy.** Wynik jest niekorzystny dla badanej wersji prostego szyfru homofonicznego, ale nie spełniono wymogu kontroli ujemnej na danych przetasowanych.

**Poziom zgody:** wysoki co do braku tej kontroli i konieczności odrzucenia automatycznego werdyktu „obalona”; opinie różnią się, jak mocno interpretować niekorzystny wynik.

### Co test pokazuje

Kontrole dodatnie wskazują, że wspinacz odzyskiwał klucz w testowanych zaszyfrowanych tekstach: zwykle w 100% znaków, w najniższych podanych przypadkach w 88–94%. W rękopisie nie uzyskano tropu; najbliższy wynik OldFrench (4,01 bitu/znak) jest bliski bełkotowi v5 (3,96), a gorszy od wartości naturalnego tekstu (3,85). To przemawia przeciw badanej metodzie szyfrowania, ale nie rozstrzyga sprawy bez pełnej walidacji.

### Główne zastrzeżenia

Brak wyników kontroli na danych przetasowanych oznacza, że nie wiadomo, czy pipeline daje fałszywe trafienia. Nie podano też, który leksykon był nietestowalny ani dlaczego. Raport nie wykazuje, że kontrole dodatnie dopasowano długością i strukturą do badanego materiału. Test nie obejmuje innych typów szyfrów ani języków spoza testowanego zestawu.

### Rekomendowany eksperyment

Powtórzyć pełny pipeline na kontrolach dodatnich o długości i strukturze dopasowanej do rękopisu oraz na odpowiadających im danych przetasowanych; z góry ustalić kryterium trafienia i podać wyniki dla wszystkich leksykonów.

## Literatura

- Van Eycke, AZdecrypt (2017–2021)
- Nuhn, Schamper & Ney, Beam search for solving substitution ciphers, ACL 2013
- Kambhatla, Bigvand & Sarkar, Decipherment of substitution ciphers with neural language models, EMNLP 2018

_Czas: 1602 s · 2026-10-24 11:07_