# Voynich Lab – przebieg 20261023-131130

| teoria | werdykt testów | kontrole | głosy rady |
|---|---|---|---|
| Brute force: trójki słów pod jednym kluczem w językach epoki | metoda niewiarygodna | 48/51 | metoda niewiarygodna: 2, wynik jest mocnym argumentem przeciw hip: 1 |

Werdykt testów wynika wyłącznie z liczb i kontroli. Rada modeli komentuje, nie głosuje nad danymi.

## Brute force: trójki słów pod jednym kluczem w językach epoki

51 języków, 4000 trójek. W żadnym języku rękopis nie wygrywa z bełkotem: najwyższy udział słów w słowniku pod wspólnym kluczem 25.4% (OldFrench; bełkot 29.7%, zaszyfrowany tekst 99%). Pojedyncze trójki czytają się „sensownie” w większości języków, ale ich klucze się nie zgadzają.

**Synteza rady:**

## Werdykt rady
**Test niewiarygodny; hipoteza nie została rozstrzygnięta.** Zgodność ocen jest wysoka: wszyscy recenzenci uznali, że niezaliczone kontrole dodatnie uniemożliwiają uznanie metody za wiarygodną. Raport nie podaje też wyników kontroli negatywnych, więc nie można potwierdzić, że metoda nie wykrywa efektu w danych przetasowanych.

## Co test pokazuje
W badanym wariancie — jednym wspólnym kluczu litera-za-glif i 4000 najczęstszych trójek — najlepszy wynik rękopisu to 25,4% słów w słowniku, wobec 29,7% dla bełkotu i 99% dla zaszyfrowanego tekstu. To wynik niekorzystny dla hipotezy, ale nie stanowi jej rozstrzygającego obalenia, ponieważ walidacja metody nie jest kompletna.

## Główne zastrzeżenia
Kontrole dodatnie nie przeszły dla Amharic, BiblicalHebrew i Hindi. Ponadto brak wyników kontroli z przetasowanymi słowami i przemianowanymi glifami. Test nie obejmuje innych schematów szyfrowania, zmiennego klucza ani analizy całego tekstu poza wskazanymi trójkami.

## Rekomendowany następny eksperyment
Powtórzyć test według wcześniej ustalonego protokołu, opublikować wyniki wszystkich kontroli dodatnich i negatywnych oraz poprawić lub wyłączyć języki, dla których kontrola dodatnia nie przechodzi.

Szczegóły: [brute.md](brute.md)

Koszt OpenRouter: 0.02 USD w 19 wywołaniach. Rada: z-ai/glm-5.3-flash, openai/gpt-6-luna, inception/mercury-3, tencent/hy3; przewodniczący: openai/gpt-6-luna.