# atoms_vision: nierozstrzygnięta

**Hipoteza.** (szkic, nie test) Otwarte modele widzące na własnym GPU opisują atomy ilustracji w schemacie data/atoms, z kolejnością nimf policzoną z geometrii, żeby ludzie poprawiali zamiast zaczynać od zera.

**Metoda.** Molmo2 (allenai/Molmo2-8B) wskazuje punktami środki kół, postaci i gwiazdy; Grounding DINO (IDEA-Research/grounding-dino-base) liczy te same klasy ramkami jako kontrola; postaci przypisane do najbliższego środka, kręgi i kolejność zgodnie z ruchem wskazówek zegara z geometrii (voynich.atoms.ring_layout); Qwen3-VL (Qwen/Qwen3-VL-8B-Instruct) opisuje wycinek wokół każdej postaci według słownika 'nimfa' (wartości spoza słownika odrzucone); znak w środku koła wskazuje stronę ZL. Wynik: pliki stron w atoms_vision/ (zrodlo 'vision', pewnosc 1) i PNG z numerami punktów.

Szkic 9 stron w atoms_vision/ (do sprawdzenia na PNG, poprawienia i scalenia z data/atoms).

## Kontrole


## Dowody

- Strony: f70v2 (ryby; model widzi other): postaci 14 po scaleniu (Molmo {'human figure': 15, 'person': 13, 'dino': 5}), oczekiwano 29, etykiet 29, kręgi {'zewn': 14}, gwiazd 13, odrzuconych wartości 0; f70v1 (baran; model widzi other): postaci 11 po scaleniu (Molmo {'human figure': 6, 'person': 6, 'dino': 5}), oczekiwano 15, etykiet 15, kręgi {'wewn': 1, 'srod': 2, 'zewn': 8}, gwiazd 6, odrzuconych wartości 0; f71r (baran; model widzi strzelec): postaci 12 po scaleniu (Molmo {'human figure': 7, 'person': 7, 'dino': 6}), oczekiwano 15, etykiet 15, kręgi {'wewn': 6, 'srod': 5, 'zewn': 1}, gwiazd 10, odrzuconych wartości 0; f71v (byk; model widzi other): postaci 1 po scaleniu (Molmo {'human figure': 0, 'person': 0, 'dino': 1}), oczekiwano 15, etykiet 15, kręgi {'zewn': 1}, gwiazd 0, odrzuconych wartości 0; f72r1: brak postaci (Molmo {'human figure': 0, 'person': 0, 'dino': 0}, oczekiwano 15); strona pominięta; f72r2 (bliznieta; model widzi other): postaci 1 po scaleniu (Molmo {'human figure': 0, 'person': 0, 'dino': 1}), oczekiwano 30, etykiet 29, kręgi {'zewn': 1}, gwiazd 0, odrzuconych wartości 0; f72r3: brak postaci (Molmo {'human figure': 0, 'person': 0, 'dino': 0}, oczekiwano 30); strona pominięta; f72v3: brak postaci (Molmo {'human figure': 0, 'person': 0, 'dino': 0}, oczekiwano 30); strona pominięta; f72v2 (panna; model widzi other): postaci 1 po scaleniu (Molmo {'human figure': 0, 'person': 0, 'dino': 1}), oczekiwano 30, etykiet 30, kręgi {'zewn': 1}, gwiazd 0, odrzuconych wartości 0; f72v1 (waga; model widzi other): postaci 12 po scaleniu (Molmo {'human figure': 12, 'person': 11, 'dino': 2}), oczekiwano 30, etykiet 28, kręgi {'wewn': 6, 'srod': 5, 'zewn': 1}, gwiazd 1, odrzuconych wartości 0; f73r (skorpion; model widzi other): postaci 16 po scaleniu (Molmo {'human figure': 15, 'person': 14, 'dino': 5}), oczekiwano 30, etykiet 30, kręgi {'zewn': 16}, gwiazd 19, odrzuconych wartości 0; f73v (strzelec; model widzi other): postaci 9 po scaleniu (Molmo {'human figure': 10, 'person': 8, 'dino': 1}), oczekiwano 30, etykiet 29, kręgi {'wewn': 3, 'zewn': 6}, gwiazd 7, odrzuconych wartości 0.

## Zastrzeżenia

- Kolejność nimf z geometrii zakłada, że loci transliteracji idą zgodnie z ruchem wskazówek zegara od góry w każdym kręgu; PNG z numerami służy do sprawdzenia tego na oko.
- Modele liczą drobne rzeczy (promienie) niepewnie; pewnosc 1 dla wszystkich wartości.
- To nie jest test: werdykt zawsze 'nierozstrzygnięta'.

## Literatura

- Molmo2 (Ai2 2025), Qwen3-VL (Alibaba 2025), Grounding DINO (IDEA 2023), all Apache 2.0 on Hugging Face

_Czas: 696 s · 2026-10-28 15:12_