# cognate: obalona

**Hipoteza.** Słowa rękopisu to słowa (lub bliskie formy) któregoś z języków epoki pod jednym kluczem glif–litera; dopasowanie całego słownictwa do słownika języka odsłania klucz.

**Metoda.** Metoda NeuroDecipher: miękki klucz (softmax nad literami dla każdego glifu), cechy bigramów i bigramów z przeskokiem słów, transport optymalny (Sinkhorn) między 1500 typami słów rękopisu a 6000 słowami języka, spadek gradientu po kluczu, 32 startów w jednej paczce na GPU. Klucz twardy z foliów nieparzystych oceniany na parzystych: udział słów w słowniku lub o jedną zmianę od słowa słownika. Tło: bełkot v5. Kontrola dodatnia: tekst języka z 30% słów zmienionych o jedną literę, zaszyfrowany losowym kluczem; metoda musi odzyskać klucz.

Tropy: brak; 50 języków testowalnych, 2 nietestowalnych. Największa przewaga nad bełkotem: Syriac (rękopis 85% słów o najwyżej jedną zmianę od słownika, bełkot 74%).

## Kontrole

- ✅ **Afrikaans: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 76%, o jedną zmianę 99%)
- ✅ **Albanian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 80%, o jedną zmianę 97%)
- ✅ **AncientGreek: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 99% (słowa w słowniku 62%, o jedną zmianę 91%)
- ✅ **Arabic: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 71%, o jedną zmianę 97%)
- ✅ **Basque: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 69%, o jedną zmianę 100%)
- ✅ **BasqueNews: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 99% (słowa w słowniku 61%, o jedną zmianę 89%)
- ✅ **BiblicalHebrew: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 78%, o jedną zmianę 99%)
- ✅ **Bulgarian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 74%, o jedną zmianę 93%)
- ✅ **ClassicalArmenian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 82%, o jedną zmianę 100%)
- ✅ **Coptic: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 77%, o jedną zmianę 96%)
- ✅ **Croatian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 69%, o jedną zmianę 90%)
- ✅ **Czech: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 72%, o jedną zmianę 96%)
- ✅ **Danish: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 77%, o jedną zmianę 98%)
- ✅ **Dutch: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 75%, o jedną zmianę 97%)
- ✅ **English: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 79%, o jedną zmianę 100%)
- ✅ **Finnish: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 67%, o jedną zmianę 93%)
- ✅ **French: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 83%, o jedną zmianę 100%)
- ✅ **German: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 73%, o jedną zmianę 100%)
- ✅ **Gothic: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 74%, o jedną zmianę 100%)
- ✅ **Greek: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 73%, o jedną zmianę 92%)
- ✅ **Hebrew: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 75%, o jedną zmianę 99%)
- ✅ **Hungarian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 74%, o jedną zmianę 94%)
- ✅ **Icelandic: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 68%, o jedną zmianę 95%)
- ✅ **Irish: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 99% (słowa w słowniku 75%, o jedną zmianę 98%)
- ✅ **Italian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 81%, o jedną zmianę 100%)
- ✅ **Latin: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 65%, o jedną zmianę 93%)
- ✅ **LatinAquinas: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 70%, o jedną zmianę 94%)
- ✅ **Lithuanian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 66%, o jedną zmianę 89%)
- ✅ **Maltese: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 77%, o jedną zmianę 100%)
- ✅ **MedievalLatin: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 63%, o jedną zmianę 87%)
- ✅ **MiddleFrench: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 82%, o jedną zmianę 100%)
- ✅ **Norwegian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 77%, o jedną zmianę 99%)
- ✅ **OldChurchSlavonic: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 98% (słowa w słowniku 76%, o jedną zmianę 92%)
- ✅ **OldEastSlavic: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 97% (słowa w słowniku 74%, o jedną zmianę 91%)
- ✅ **OldFrench: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 99% (słowa w słowniku 73%, o jedną zmianę 95%)
- ✅ **Persian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 79%, o jedną zmianę 97%)
- ✅ **Polish: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 77%, o jedną zmianę 96%)
- ✅ **Portuguese: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 72%, o jedną zmianę 100%)
- ✅ **Romanian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 80%, o jedną zmianę 100%)
- ✅ **Russian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 70%, o jedną zmianę 88%)
- ✅ **Serbian: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 71%, o jedną zmianę 93%)
- ✅ **Slovak: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 70%, o jedną zmianę 91%)
- ✅ **Slovene: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 70%, o jedną zmianę 93%)
- ✅ **Spanish: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 98% (słowa w słowniku 72%, o jedną zmianę 100%)
- ✅ **Swedish: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 78%, o jedną zmianę 98%)
- ✅ **Syriac: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 63%, o jedną zmianę 93%)
- ✅ **Turkish: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 66%, o jedną zmianę 96%)
- ✅ **Vietnamese: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 94% (słowa w słowniku 83%, o jedną zmianę 100%)
- ✅ **VulgarLatin: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 73%, o jedną zmianę 100%)
- ✅ **Welsh: zaszyfrowany tekst z szumem pisowni**: oczekiwano klucz odzyskany w ≥ 60% znaków; wynik: 100% (słowa w słowniku 83%, o jedną zmianę 100%)

## Dowody

- Afrikaans: rękopis – słowa w słowniku 12.5%, o jedną zmianę 74.9% (koszt transportu 0.667); bełkot v5 – 15.2%, 78.5%; zaszyfrowany tekst – klucz 100%, słowa 99%. Odczyt pierwszego wiersza: „saees erar al aeang ver vele llos e”.
- Albanian: rękopis – słowa w słowniku 8.7%, o jedną zmianę 79.5% (koszt transportu 0.672); bełkot v5 – 11.1%, 80.2%; zaszyfrowany tekst – klucz 100%, słowa 97%. Odczyt pierwszego wiersza: „sihis irit in isite ket keni lnas i”.
- Amharic: nietestowalny – 28 glifów niesie tylko 13% tekstu tego pisma.
- AncientGreek: rękopis – słowa w słowniku 13.5%, o jedną zmianę 83.1% (koszt transportu 0.666); bełkot v5 – 15.1%, 85.4%; zaszyfrowany tekst – klucz 99%, słowa 91%. Odczyt pierwszego wiersza: „μοενς νροι ον οροος εαι εανν τνις ν”.
- Arabic: rękopis – słowa w słowniku 9.2%, o jedną zmianę 76.6% (koszt transportu 0.647); bełkot v5 – 8.9%, 80.3%; zaszyfrowany tekst – klucz 100%, słowa 97%. Odczyt pierwszego wiersza: „وووةت ةلون ور ولوها فان فارة مررت ة”.
- Basque: rękopis – słowa w słowniku 6.9%, o jedną zmianę 73.9% (koszt transportu 0.664); bełkot v5 – 8.3%, 76.9%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „irinu nera ra raric ita itan oaau n”.
- BasqueNews: rękopis – słowa w słowniku 16.8%, o jedną zmianę 81.6% (koszt transportu 0.654); bełkot v5 – 16.0%, 82.4%; zaszyfrowany tekst – klucz 99%, słowa 89%. Odczyt pierwszego wiersza: „teiai aren ek ereko ean eaka ekri a”.
- BiblicalHebrew: rękopis – słowa w słowniku 14.9%, o jedną zmianę 76.2% (koszt transportu 0.633); bełkot v5 – 13.6%, 81.1%; zaszyfrowany tekst – klucz 100%, słowa 99%. Odczyt pierwszego wiersza: „הנשםא םמנה נת נבנתי ליה ליתם כתרא ם”.
- Bulgarian: rękopis – słowa w słowniku 6.8%, o jedną zmianę 77.4% (koszt transportu 0.682); bełkot v5 – 6.5%, 78.4%; zaszyfrowany tekst – klucz 100%, słowa 93%. Odczyt pierwszego wiersza: „оавея еааа аи аоата сра срие ииия е”.
- ClassicalArmenian: rękopis – słowa w słowniku 9.3%, o jedną zmianę 73.4% (koszt transportu 0.665); bełkot v5 – 8.2%, 74.4%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „սոեիլ իրոյ ոց ոնուն մայ մացի տցել ի”.
- Coptic: rękopis – słowa w słowniku 12.6%, o jedną zmianę 72.6% (koszt transportu 0.664); bełkot v5 – 21.1%, 75.6%; zaszyfrowany tekst – klucz 100%, słowa 96%. Odczyt pierwszego wiersza: „ⲡⲟⲉⲉϩ ⲉⲛⲟⲩ ⲟⲥ ⲟⲧⲟⲩⲩ ⲙⲁⲩ ⲙⲁⲥⲉ ⲡⲥⲧϩ ⲉ”.
- Croatian: rękopis – słowa w słowniku 8.8%, o jedną zmianę 73.3% (koszt transportu 0.666); bełkot v5 – 8.1%, 76.6%; zaszyfrowany tekst – klucz 100%, słowa 90%. Odczyt pierwszego wiersza: „anzmo moni ne nanma sri srem ueao m”.
- Czech: rękopis – słowa w słowniku 4.0%, o jedną zmianę 71.8% (koszt transportu 0.693); bełkot v5 – 5.9%, 76.2%; zaszyfrowany tekst – klucz 100%, słowa 96%. Odczyt pierwszego wiersza: „olzlu lale la lelti sre sral oaeu l”.
- Danish: rękopis – słowa w słowniku 19.0%, o jedną zmianę 76.4% (koszt transportu 0.663); bełkot v5 – 19.8%, 81.0%; zaszyfrowany tekst – klucz 100%, słowa 98%. Odczyt pierwszego wiersza: „leseg eren er erens ran rare trrg e”.
- Dutch: rękopis – słowa w słowniku 15.5%, o jedną zmianę 83.9% (koszt transportu 0.666); bełkot v5 – 11.7%, 79.8%; zaszyfrowany tekst – klucz 100%, słowa 97%. Odczyt pierwszego wiersza: „leodt drer en eleen aer aend onat d”.
- English: rękopis – słowa w słowniku 7.2%, o jedną zmianę 72.8% (koszt transportu 0.671); bełkot v5 – 9.4%, 73.2%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „aerdn daee es eoeth rhe rhsd esin d”.
- Finnish: rękopis – słowa w słowniku 6.7%, o jedną zmianę 80.4% (koszt transportu 0.646); bełkot v5 – 5.2%, 84.6%; zaszyfrowany tekst – klucz 100%, słowa 93%. Odczyt pierwszego wiersza: „islnt nasa si sesta kla klin eiat n”.
- French: rękopis – słowa w słowniku 14.6%, o jedną zmianę 79.5% (koszt transportu 0.651); bełkot v5 – 7.0%, 78.9%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „raaes erar as anant aer aese msis e”.
- German: rękopis – słowa w słowniku 3.0%, o jedną zmianę 78.6% (koszt transportu 0.663); bełkot v5 – 1.9%, 78.1%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „etrns nete tt tater rte rttn otes n”.
- Gothic: rękopis – słowa w słowniku 7.2%, o jedną zmianę 78.3% (koszt transportu 0.647); bełkot v5 – 6.4%, 79.5%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „uiasm snii in inida aai aans inam s”.
- Greek: rękopis – słowa w słowniku 4.5%, o jedną zmianę 68.1% (koszt transportu 0.672); bełkot v5 – 6.6%, 70.1%; zaszyfrowany tekst – klucz 100%, słowa 92%. Odczyt pierwszego wiersza: „αιανε νεια ιι ιαιος αια αιιν ειιε ν”.
- Hebrew: rękopis – słowa w słowniku 7.3%, o jedną zmianę 74.2% (koszt transportu 0.634); bełkot v5 – 8.8%, 79.1%; zaszyfrowany tekst – klucz 100%, słowa 99%. Odczyt pierwszego wiersza: „אנבהת האנו ני נשנים מיו מייה הירת ה”.
- Hindi: rękopis – słowa w słowniku 20.7%, o jedną zmianę 52.3% (koszt transportu 0.635); bełkot v5 – 22.2%, 56.6%; zaszyfrowany tekst – klucz 15%, słowa 100%. Odczyt pierwszego wiersza: „सलरलज लपलत लन लकलहर दहत दहनल लनहज ल”.
- Hungarian: rękopis – słowa w słowniku 6.1%, o jedną zmianę 71.7% (koszt transportu 0.675); bełkot v5 – 7.5%, 70.6%; zaszyfrowany tekst – klucz 100%, słowa 94%. Odczyt pierwszego wiersza: „sazan agak at alaol hek heta ttan a”.
- Icelandic: rękopis – słowa w słowniku 4.6%, o jedną zmianę 77.6% (koszt transportu 0.673); bełkot v5 – 3.4%, 79.8%; zaszyfrowany tekst – klucz 100%, słowa 95%. Odczyt pierwszego wiersza: „anrnt nena ni nonir hta htin aint n”.
- Irish: rękopis – słowa w słowniku 16.6%, o jedną zmianę 76.5% (koszt transportu 0.664); bełkot v5 – 16.1%, 78.8%; zaszyfrowany tekst – klucz 99%, słowa 98%. Odczyt pierwszego wiersza: „gicre raia in ioire tha thnr unhe r”.
- Italian: rękopis – słowa w słowniku 11.3%, o jedną zmianę 74.7% (koszt transportu 0.661); bełkot v5 – 8.1%, 76.6%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „annie iano ne ninto sro srei aeee i”.
- Latin: rękopis – słowa w słowniku 5.9%, o jedną zmianę 77.8% (koszt transportu 0.662); bełkot v5 – 5.1%, 78.6%; zaszyfrowany tekst – klucz 100%, słowa 93%. Odczyt pierwszego wiersza: „irnso sera re rorum ara ares aeuo s”.
- LatinAquinas: rękopis – słowa w słowniku 7.9%, o jedną zmianę 74.7% (koszt transportu 0.672); bełkot v5 – 6.1%, 75.0%; zaszyfrowany tekst – klucz 100%, słowa 94%. Odczyt pierwszego wiersza: „itnsa sate tt totum ure urts utua s”.
- Lithuanian: rękopis – słowa w słowniku 10.3%, o jedną zmianę 75.1% (koszt transportu 0.667); bełkot v5 – 5.6%, 69.8%; zaszyfrowany tekst – klucz 100%, słowa 89%. Odczyt pierwszego wiersza: „unssu sena no nanai sia sios aoiu s”.
- Maltese: rękopis – słowa w słowniku 7.4%, o jedną zmianę 66.5% (koszt transportu 0.710); bełkot v5 – 7.1%, 69.9%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „ilntt tali lu lilha sti stut ouat t”.
- MedievalLatin: rękopis – słowa w słowniku 14.7%, o jedną zmianę 84.6% (koszt transportu 0.646); bełkot v5 – 13.7%, 83.9%; zaszyfrowany tekst – klucz 100%, słowa 87%. Odczyt pierwszego wiersza: „itnso sate ta tetum ure uras aauo s”.
- MiddleFrench: rękopis – słowa w słowniku 7.0%, o jedną zmianę 82.5% (koszt transportu 0.664); bełkot v5 – 7.3%, 82.9%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „seoet erer es erent aer aese lsit e”.
- Norwegian: rękopis – słowa w słowniku 13.7%, o jedną zmianę 77.5% (koszt transportu 0.660); bełkot v5 – 15.6%, 76.4%; zaszyfrowany tekst – klucz 100%, słowa 99%. Odczyt pierwszego wiersza: „lelne naet er eiene let lern orre n”.
- OldChurchSlavonic: rękopis – słowa w słowniku 14.4%, o jedną zmianę 66.4% (koszt transportu 0.691); bełkot v5 – 15.1%, 66.4%; zaszyfrowany tekst – klucz 98%, słowa 92%. Odczyt pierwszego wiersza: „утвъь ъоти те татмъ сри среъ деть ъ”.
- OldEastSlavic: rękopis – słowa w słowniku 10.7%, o jedną zmianę 66.6% (koszt transportu 0.697); bełkot v5 – 9.9%, 66.0%; zaszyfrowany tekst – klucz 97%, słowa 91%. Odczyt pierwszego wiersza: „влсьм ьоли ла лолмъ нри нраь таом ь”.
- OldFrench: rękopis – słowa w słowniku 11.7%, o jedną zmianę 80.1% (koszt transportu 0.633); bełkot v5 – 18.2%, 85.0%; zaszyfrowany tekst – klucz 99%, słowa 95%. Odczyt pierwszego wiersza: „eeatr tree es eueie oae oast iser t”.
- Persian: rękopis – słowa w słowniku 17.4%, o jedną zmianę 84.6% (koszt transportu 0.638); bełkot v5 – 23.8%, 81.9%; zaszyfrowany tekst – klucz 100%, słowa 97%. Odczyt pierwszego wiersza: „دنسنت نانه نی نونند مره مرین کییت ن”.
- Polish: rękopis – słowa w słowniku 8.3%, o jedną zmianę 71.1% (koszt transportu 0.701); bełkot v5 – 9.6%, 69.6%; zaszyfrowany tekst – klucz 100%, słowa 96%. Odczyt pierwszego wiersza: „onzmu moni na nanie sri sram aaau m”.
- Portuguese: rękopis – słowa w słowniku 13.1%, o jedną zmianę 80.9% (koszt transportu 0.645); bełkot v5 – 17.3%, 73.3%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „adrsi seda do dedos rra rros eoii s”.
- Romanian: rękopis – słowa w słowniku 11.1%, o jedną zmianę 74.9% (koszt transportu 0.650); bełkot v5 – 6.2%, 71.7%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „itnia iita te totul sra srei ueaa i”.
- Russian: rękopis – słowa w słowniku 5.3%, o jedną zmianę 68.0% (koszt transportu 0.693); bełkot v5 – 6.2%, 69.6%; zaszyfrowany tekst – klucz 100%, słowa 88%. Odczyt pierwszego wiersza: „влсеу еола ли лелил вра врие оиту е”.
- Serbian: rękopis – słowa w słowniku 8.4%, o jedną zmianę 72.3% (koszt transportu 0.669); bełkot v5 – 11.3%, 78.8%; zaszyfrowany tekst – klucz 100%, słowa 93%. Odczyt pierwszego wiersza: „atsmu moti te tatna sri srem oeau m”.
- Slovak: rękopis – słowa w słowniku 7.6%, o jedną zmianę 70.5% (koszt transportu 0.690); bełkot v5 – 7.9%, 70.3%; zaszyfrowany tekst – klucz 100%, słowa 91%. Odczyt pierwszego wiersza: „snvmu mane ni nonia sre srim aiau m”.
- Slovene: rękopis – słowa w słowniku 5.7%, o jedną zmianę 73.6% (koszt transportu 0.677); bełkot v5 – 7.1%, 77.3%; zaszyfrowany tekst – klucz 100%, słowa 93%. Odczyt pierwszego wiersza: „ojzlo loja je jejli sra srel eeao l”.
- Spanish: rękopis – słowa w słowniku 13.0%, o jedną zmianę 82.0% (koszt transportu 0.650); bełkot v5 – 8.3%, 76.7%; zaszyfrowany tekst – klucz 98%, słowa 100%. Odczyt pierwszego wiersza: „ceeos oren es erera can caso dsis o”.
- Swedish: rękopis – słowa w słowniku 15.8%, o jedną zmianę 71.8% (koszt transportu 0.664); bełkot v5 – 18.2%, 85.6%; zaszyfrowany tekst – klucz 100%, słowa 98%. Odczyt pierwszego wiersza: „leoad aten er erede san sara lrod a”.
- Syriac: rękopis – słowa w słowniku 13.9%, o jedną zmianę 85.0% (koszt transportu 0.614); bełkot v5 – 20.3%, 74.0%; zaszyfrowany tekst – klucz 100%, słowa 93%. Odczyt pierwszego wiersza: „ܡܗܕܐܢ ܐܪܗܘ ܗܝ ܗܒܗܘܢ ܠܐܘ ܠܐܝܐ ܡܝܝܢ ܐ”.
- Turkish: rękopis – słowa w słowniku 11.1%, o jedną zmianę 63.0% (koszt transportu 0.693); bełkot v5 – 13.0%, 69.5%; zaszyfrowany tekst – klucz 100%, słowa 96%. Odczyt pierwszego wiersza: „seoık ılen er ereni san sarı yruk ı”.
- Vietnamese: rękopis – słowa w słowniku 15.7%, o jedną zmianę 61.4% (koszt transportu 0.553); bełkot v5 – 18.1%, 61.1%; zaszyfrowany tekst – klucz 94%, słowa 100%. Odczyt pierwszego wiersza: „meugc gieu en eheet gau gang rnoc g”.
- VulgarLatin: rękopis – słowa w słowniku 4.8%, o jedną zmianę 69.5% (koszt transportu 0.662); bełkot v5 – 7.8%, 73.8%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „irnso sera re rorum ira ires ueuo s”.
- Welsh: rękopis – słowa w słowniku 10.7%, o jedną zmianę 64.4% (koszt transportu 0.691); bełkot v5 – 10.6%, 77.0%; zaszyfrowany tekst – klucz 100%, słowa 100%. Odczyt pierwszego wiersza: „cohol oeon ou orodd dan dauo wuel o”.

## Zastrzeżenia

- Cechy bigramowe widzą pisownię, nie wymowę: kognaty różniące się bardziej niż o jedną literę nie liczą się jako trafienia.
- Klucz glif–litera jeden do jednego; abrewiacje i ligatury wieloliterowe są poza zasięgiem.

## Literatura

- Luo, Cao & Barzilay, Neural decipherment via minimum-cost flow: from Ugaritic to Linear B, ACL 2019
- Luo et al., Deciphering undersegmented ancient scripts using phonetic prior, TACL 2021

_Czas: 17637 s · 2026-10-24 10:28_