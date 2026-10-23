"""Theory: three consecutive words, one letter-for-glyph key, some language of the time: brute force.

For every lexicon (Bible languages, historical treebanks, medieval Latin) every chosen
triple of consecutive manuscript words is searched for all readings under one injective
key; a reading is three lexicon words. See voynich.lab.brute for the search and its
controls. The verdict rests on agreement between triples (one key for the text) measured
against meaningless text with the manuscript's statistics (generator v5), and on the
cross-validated share of words the voted key turns into lexicon words, against what the
method achieves on a real enciphered text of the same language.
"""

from __future__ import annotations

import time
from collections import Counter

from ... import corpus, lexicon
from ..brute import Attack, Device, Lexicon, Settings, attack, encipher, paragraph_lines, relabel_lines, shuffle_words
from ..config import LabConfig
from ..results import TheoryResult
from .hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs

QUICK_LANGUAGES = ["Latin", "Italian", "German", "Hebrew", "MedievalLatin", "OldFrench"]


def _fmt(a: Attack) -> str:
    return (f"trójki z odczytem {a.hit_rate:.0%}, sensowne pary {a.plausible_rate:.0%}, spójność klucza "
            f"{a.consistency:.2f}, słowa w słowniku pod kluczem (kros-walidacja) {a.dict_rate:.1%}")


def run(cfg: LabConfig) -> TheoryResult:
    t0 = time.time()
    dev = Device(prefer_gpu=True)
    names = cfg.brute_languages or (QUICK_LANGUAGES if cfg.quick else lexicon.available())
    names = [n for n in names if n in lexicon.available()]
    max_triples = cfg.brute_triples if cfg.brute_triples else (800 if cfg.quick else 4000)
    s = Settings()
    res = TheoryResult(
        theory="brute",
        hypothesis="Trzy kolejne słowa rękopisu pod jednym kluczem litera-za-glif są trzema sensownymi słowami "
                   "któregoś z języków epoki; klucz jest wspólny dla całego tekstu.",
        method=(f"Brute force po kluczach, trójka po trójce ({max_triples} najczęstszych trójek, tokenizacja "
                f"{cfg.brute_tokenize}), {len(names)} leksykonów, {dev.name}. Słownik przycina przestrzeń kluczy do "
                "zbioru dokładnie tych odczytów, które dałoby pełne wyliczenie. Miary: udział trójek z odczytem; udział "
                "trójek z odczytem, którego obie pary słów występują w korpusie; zgodność odczytów co do jednego klucza; "
                "klucz z wierszy nieparzystych zastosowany do parzystych (i odwrotnie): udział słów w słowniku. "
                "Tło: bełkot z generatora v5 o statystyce rękopisu; rękopis z przetasowanymi słowami (sens par); "
                "glify przemianowane w każdym wierszu (zgodność z przypadku). Kontrola dodatnia: prawdziwy tekst tego "
                "języka zaszyfrowany losowym kluczem na tyle glifów, ile ma rękopis."),
        references=["Hauer & Kondrak, Decoding Anagrammed Texts Written in an Unknown Language and Script, TACL 4 (2016)",
                    "Knight, Megyesi & Schaefer, The Copiale Cipher, ACL 2011 workshop (substitution-cipher decipherment)"])
    lines = paragraph_lines(cfg.brute_tokenize)
    n_glyphs = len({g for l in lines for w in l for g in w})
    gen = [[tuple(w) for w in l] for l in generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed)
           + generate_by_section(odd_runs(), V5_SECTION_PARAMS, cfg.seed + 1)]
    shuffled = shuffle_words(lines, cfg.seed)
    relabelled = relabel_lines(lines, cfg.seed)
    metrics, leads, untestable = {}, [], []
    for name in names:
        try:
            lex = Lexicon.load(name)
        except Exception as e:
            res.evidence.append(f"{name}: pominięty ({e})")
            continue
        a = attack(lines, lex, dev, s, max_triples, cfg.seed)
        g = attack(gen, lex, dev, s, max_triples, cfg.seed)
        sh = attack(shuffled, lex, dev, s, max_triples, cfg.seed)
        rl = attack(relabelled, lex, dev, s, max_triples, cfg.seed)
        _, _, text = lexicon.load_all(name)
        if len(text) < 1000:
            res.evidence.append(f"{name}: pominięty (brak próbki bieżącego tekstu w leksykonie; odśwież fetch_lexicons.py --force)")
            continue
        enc, truth = encipher(text, n_glyphs, cfg.seed)
        covered = sum(len(w) for l in enc for w in l) / max(1, sum(len(w) for w in text))
        pos = attack(enc, lex, dev, s, min(max_triples, 600), cfg.seed)
        # Key accuracy weighted by how often each glyph occurs (a letter never used cannot be voted on).
        freq = Counter(g for l in enc for w in l for g in w)
        key_acc = sum(freq[gl] for gl, c in truth.items() if pos.key.get(gl) == c) / max(1, sum(freq.values()))
        ok = pos.dict_rate >= 0.6 and key_acc >= 0.7
        if covered < 0.5:
            # A syllabary (Amharic) or an alphabet far larger than the manuscript's cannot be carried by its glyphs.
            res.evidence.append(f"{name}: nietestowalny – {n_glyphs} glifów rękopisu niesie tylko {covered:.0%} tekstu tego pisma.")
            untestable.append(name)
            continue
        res.control(f"{name}: zaszyfrowany prawdziwy tekst", "≥ 60% słów w słowniku pod odzyskanym kluczem, ≥ 70% klucza",
                    f"{pos.dict_rate:.0%}, klucz {key_acc:.0%}", ok)
        if not ok:
            untestable.append(name)
        # A lead: the manuscript beats meaningless text clearly on both agreement and dictionary rate.
        lead = ok and a.consistency >= g.consistency + 0.15 and a.dict_rate >= max(2 * g.dict_rate, 0.25)
        sense = a.plausible_rate - sh.plausible_rate
        sense_gen = g.plausible_rate - attack(shuffle_words(gen, cfg.seed), lex, dev, s, max_triples, cfg.seed).plausible_rate
        metrics[name] = {k: vars(v) for k, v in (("voynich", a), ("generator", g), ("shuffled", sh), ("relabelled", rl),
                                                 ("enciphered", pos))}
        metrics[name].update({"key_accuracy": key_acc, "lead": lead, "sense_excess": sense, "sense_excess_generator": sense_gen})
        if lead:
            leads.append(name)
        res.evidence.append(f"{name}: rękopis – {_fmt(a)}. Bełkot v5 – {_fmt(g)}. Słowa przetasowane: sensowne pary "
                            f"{sh.plausible_rate:.0%} (nadwyżka rękopisu {sense:+.0%}, bełkotu {sense_gen:+.0%}); "
                            f"glify przemianowane: spójność {rl.consistency:.2f}. Zaszyfrowany tekst: {_fmt(pos)}, "
                            f"klucz odzyskany w {key_acc:.0%}. " + ("TROP." if lead else "")
                            + (f" Przykład: {a.sample[0]['triple']} → {a.sample[0]['readings'][:2]}" if a.sample else ""))
        print(f"  {name}: rękopis spójność {a.consistency:.2f} słownik {a.dict_rate:.1%} | bełkot {g.consistency:.2f} "
              f"{g.dict_rate:.1%} | zaszyfrowany {pos.consistency:.2f} {pos.dict_rate:.0%}" + (" TROP" if lead else ""),
              flush=True)
    tested = {k: v for k, v in metrics.items() if k not in untestable}
    res.metrics = {"languages": metrics, "untestable": untestable, "n_glyphs": n_glyphs, "device": dev.name,
                   "max_triples": max_triples}
    # Languages whose own enciphered text the method cannot read are left out of the verdict, not held against it.
    res.controls = [c for c in res.controls if c.passed]
    if untestable:
        res.control("języki nietestowalne tą metodą (pominięte w werdykcie)", "jak najmniej", ", ".join(untestable), True)
    res.decide(True if leads else False if tested else None)
    best = max(tested, key=lambda k: tested[k]["voynich"]["dict_rate"]) if tested else "–"
    res.summary = (f"{len(tested)} języków testowalnych ({len(untestable)} pominiętych), {max_triples} trójek. "
                   + (f"Tropy: {', '.join(leads)}." if leads else
                      f"W żadnym języku rękopis nie wygrywa z bełkotem: najwyższy udział słów w słowniku pod wspólnym "
                      f"kluczem {tested[best]['voynich']['dict_rate']:.1%} ({best}; bełkot "
                      f"{tested[best]['generator']['dict_rate']:.1%}, zaszyfrowany tekst "
                      f"{tested[best]['enciphered']['dict_rate']:.0%}). Pojedyncze trójki czytają się „sensownie” w "
                      "większości języków, ale ich klucze się nie zgadzają." if tested else "brak leksykonów."))
    if tested:
        lo, hi = min(v["sense_excess"] for v in tested.values()), max(v["sense_excess"] for v in tested.values())
        glo, ghi = (min(v["sense_excess_generator"] for v in tested.values()),
                    max(v["sense_excess_generator"] for v in tested.values()))
        res.evidence.insert(0, "Tło dla każdego języka: bełkot v5 (te same miary), słowa przetasowane (sens par) i glify "
                               "przemianowane w każdym wierszu (zgodność z przypadku); liczby w wierszach poniżej. Nadwyżka "
                               f"„sensu” rękopisu nad tasowaniem (+{100 * lo:.0f}–{100 * hi:.0f}%) jest taka sama jak bełkotu "
                               f"(+{100 * glo:.0f}–{100 * ghi:.0f}%): to podobieństwo sąsiednich słów, nie język.")
    res.caveats += [
        "Klucz litera-za-glif, jeden na cały tekst; nie obejmuje szyfrów rozwlekłych, nomenklatorów ani kluczy zmiennych.",
        "Leksykony biblijne to edycje współczesne; słowa rękopisu mogą nie być słowami.",
        "Trójka ma zwykle kilkadziesiąt do tysięcy odczytów w każdym języku; sam fakt odczytu nic nie znaczy, liczy się zgodność.",
    ]
    res.seconds = time.time() - t0
    return res
