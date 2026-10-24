# phonotactics: nierozstrzygnięta

**Hipoteza.** Słowa rękopisu mają budowę słów mówionych: da się w nich wskazać samogłoski i spółgłoski, a wzorce spółgłoska–samogłoska rozkładają się jak w którymś z języków (albo jak w abdżadzie).

**Metoda.** Algorytm Suchotina (1962; Guy 1991) na rękopisie (glify i surowe litery EVA) i na każdym z leksykonów: samogłoski to znaki, które unikają własnego towarzystwa. Każde słowo zamienione na wzorzec C/V; rozkłady wzorców porównane dywergencją Jensena-Shannona. Tło: bełkot v5; kontrola: rękopis z glifami przetasowanymi w słowie (naprzemienność musi spaść). Rękopis „jak mowa”, gdy jego odległość do najbliższego języka mieści się w rozrzucie odległości między językami.

Rękopis (glify): samogłoski o a e y n, naprzemienność 0.80; najbliższy język OldFrench w odległości 0.212 bitów, gdy języki leżą od siebie najdalej 0.294 (mediana 0.109). Rękopis jest tak odosobniony jak najbardziej odosobnione języki (turecki, wietnamski). Bełkot v5 wypada tak samo (najbliżej Lithuanian, 0.222), więc naprzemienność C/V odtwarza także kopiujący skryba.

## Kontrole

- ✅ **glify przetasowane w słowie tracą naprzemienność**: oczekiwano naprzemienność niższa o ≥ 0,05; wynik: 0.60 wobec 0.80

## Dowody

- rękopis (glify): samogłoski wg Suchotina: o a e y n c; udział samogłosek 50%, naprzemienność C/V 0.80, najdłuższa zbitka spółgłosek średnio 1.3, słowa bez samogłoski 3%; najbliższe języki: OldFrench 0.212, Lithuanian 0.221, English 0.224, Polish 0.229, Syriac 0.229.
- rękopis (litery EVA): samogłoski wg Suchotina: o h a y n g; udział samogłosek 42%, naprzemienność C/V 0.72, najdłuższa zbitka spółgłosek średnio 1.8, słowa bez samogłoski 2%; najbliższe języki: Maltese 0.243, Portuguese 0.251, Italian 0.264, BasqueNews 0.272, Icelandic 0.274.
- bełkot v5: samogłoski wg Suchotina: o a e y n c; udział samogłosek 50%, naprzemienność C/V 0.80, najdłuższa zbitka spółgłosek średnio 1.3, słowa bez samogłoski 2%; najbliższe języki: Lithuanian 0.222, OldFrench 0.223, English 0.239, Russian 0.24, Polish 0.244.
- rękopis, glify przetasowane w słowie: samogłoski wg Suchotina: o y a e n c; udział samogłosek 50%, naprzemienność C/V 0.60, najdłuższa zbitka spółgłosek średnio 1.6, słowa bez samogłoski 3%; najbliższe języki: Syriac 0.142, Arabic 0.178, Persian 0.19, Hebrew 0.208, Amharic 0.25.
- Odległość języka do najbliższego innego języka: mediana 0.109, największa 0.294 bitów. Abdżady (hebrajski, aramejski, syryjski, arabski): naprzemienność Arabic 0.61, BiblicalHebrew 0.62, Hebrew 0.62, Syriac 0.64.

## Zastrzeżenia

- Suchotin dzieli znaki na dwie klasy po samym sąsiedztwie; w abdżadach „samogłoskami” zostają matres lectionis, w rękopisie znaki o, a, e, y.
- Porównanie wzorców C/V zależy od tego, co uznać za jeden znak; stąd rękopis liczony dwa razy (glify i litery EVA).

## Rada modeli

## Werdykt rady
**Nierozstrzygnięta, z tendencją negatywną:** test nie dostarcza wiarygodnego dowodu, że wzorce C/V rękopisu odzwierciedlają fonotaktykę mowy. Zgoda jest wysoka co do braku rozstrzygającego wsparcia; różnica dotyczy tego, czy nazwać metodę niewiarygodną, czy wynik nierozstrzygniętym.

## Co test naprawdę pokazuje
Przetasowanie glifów obniżyło naprzemienność C/V z 0,80 do 0,60, więc ta miara reaguje na lokalną strukturę. Jednak według kryterium odległości dane przetasowane nadal mieszczą się w rozrzucie języków (0,142 wobec maksimum 0,294). Rękopis ma odległość 0,212 — powyżej mediany międzyjęzykowej 0,109 — a bełkot v5 daje niemal taki sam wynik: naprzemienność 0,80 i odległość 0,222.

## Główne zastrzeżenia
Kontrole nie spełniają w pełni wymogu wiarygodności: brak kontroli pozytywnej z celowo podłożonym efektem, a przetasowanie nie odrzuca kryterium odległości. Nie wiadomo też, jak wygenerowano bełkot v5. Wyniki zależą od segmentacji: glify i EVA dają różne klasy „samogłosek” i inne najbliższe języki. Wartości naprzemienności nie wspierają wariantu abdżadowego, ale same go rozstrzygająco nie wykluczają. Test nie bada semantyki, morfologii ani sposobu powstania tekstu.

## Następny eksperyment
Przeprowadzić zaślepioną walidację całego, z góry ustalonego kryterium na kontrolach dopasowanych długością i częstością znaków: z celowo podłożoną fonotaktyką oraz z danymi przetasowanymi. Metoda powinna wykryć pierwsze i nie kwalifikować drugich.

## Literatura

- Sukhotin, Eksperimental'noe vydelenie klassov bukv s pomoshch'ju EVM (1962)
- Guy, Vowel identification: an old (but good) algorithm, Cryptologia 15 (1991)

_Czas: 13 s · 2026-10-24 10:58_