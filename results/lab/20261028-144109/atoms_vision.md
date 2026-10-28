# atoms_vision: nierozstrzygnięta

**Hipoteza.** (szkic, nie test) Otwarte modele widzące na własnym GPU opisują atomy ilustracji w schemacie data/atoms, z kolejnością nimf policzoną z geometrii, żeby ludzie poprawiali zamiast zaczynać od zera.

**Metoda.** Molmo2 (allenai/Molmo2-8B) wskazuje punktami środki kół, postaci i gwiazdy; Grounding DINO (IDEA-Research/grounding-dino-base) liczy te same klasy ramkami jako kontrola; postaci przypisane do najbliższego środka, kręgi i kolejność zgodnie z ruchem wskazówek zegara z geometrii (voynich.atoms.ring_layout); Qwen3-VL (Qwen/Qwen3-VL-8B-Instruct) opisuje wycinek wokół każdej postaci według słownika 'nimfa' (wartości spoza słownika odrzucone); znak w środku koła wskazuje stronę ZL. Wynik: pliki stron w atoms_vision/ (zrodlo 'vision', pewnosc 1) i PNG z numerami punktów.

Szkic 0 stron w atoms_vision/ (do sprawdzenia na PNG, poprawienia i scalenia z data/atoms).

## Kontrole


## Dowody

- Strony: 70v (part): koło 'inne' (28 postaci) bez strony; 70v (part): koło 'inne' (15 postaci) bez strony; 71r: koło 'wodnik' (15 postaci) bez strony; 71v and 72r: koło 'inne' (1 postaci) bez strony; 71v and 72r: koło 'inne' (0 postaci) bez strony; 71v and 72r: koło 'inne' (0 postaci) bez strony; 71v and 72r: koło 'inne' (0 postaci) bez strony; 72v (part): koło 'inne' (0 postaci) bez strony; 72v (part): koło 'inne' (1 postaci) bez strony; 72v (part): koło 'inne' (9 postaci) bez strony; 73r: koło 'inne' (12 postaci) bez strony; 73v: koło 'inne' (1 postaci) bez strony.

## Zastrzeżenia

- Kolejność nimf z geometrii zakłada, że loci transliteracji idą zgodnie z ruchem wskazówek zegara od góry w każdym kręgu; PNG z numerami służy do sprawdzenia tego na oko.
- Modele liczą drobne rzeczy (promienie) niepewnie; pewnosc 1 dla wszystkich wartości.
- To nie jest test: werdykt zawsze 'nierozstrzygnięta'.

## Literatura

- Molmo2 (Ai2 2025), Qwen3-VL (Alibaba 2025), Grounding DINO (IDEA 2023), all Apache 2.0 on Hugging Face

_Czas: 321 s · 2026-10-28 14:46_