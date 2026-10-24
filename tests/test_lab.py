import random
import unittest

from voynich.lab import registry
from voynich.lab.council import deliberate
from voynich.lab.images import MISSING_FOLIOS, base_folio, canvases, single_folio_canvases
from voynich.lab.openrouter import parse_json, pick_models
from voynich.lab.results import TheoryResult
from voynich.lab.theories import illustrations, literature, numbers


class ResultTest(unittest.TestCase):
    def test_failed_control_overrides_verdict(self):
        r = TheoryResult("t", "h", "m")
        r.control("ok", "x", "x", True)
        r.decide(True)
        self.assertEqual(r.verdict, "potwierdzona")
        r.control("broken", "x", "y", False)
        r.decide(True)
        self.assertEqual(r.verdict, "metoda niewiarygodna")


class DataTest(unittest.TestCase):
    def test_reference_data_complete(self):
        from voynich import corpus
        self.assertEqual(corpus.data_problems(), [])
        self.assertIn("Basque", corpus.reference_languages())

    def test_truncated_file_is_reported(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        from voynich import corpus
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(corpus, "REFERENCE_DIR", Path(d)):
                (Path(d) / "Latin.txt").write_text("in principio")
                problems = corpus.data_problems()
        self.assertTrue(any(p.startswith("Latin.txt: 2 słów") for p in problems))


class RegistryTest(unittest.TestCase):
    def test_aliases(self):
        self.assertEqual(registry.expand(["literature"]), ["naibbe_cipher", "cardan_grille", "hebrew_anagram"])
        self.assertEqual(len(registry.expand(["all"])), len(registry.THEORIES))
        with self.assertRaises(KeyError):
            registry.expand(["astrology"])

    def test_every_runner_loads(self):
        for t in registry.THEORIES.values():
            self.assertTrue(callable(t.load()))


class OpenRouterTest(unittest.TestCase):
    def test_parse_json_inside_prose(self):
        self.assertEqual(parse_json('Ocena: ```json {"werdykt": "obalona", "x": {"y": 1}}``` koniec'),
                         {"werdykt": "obalona", "x": {"y": 1}})
        self.assertEqual(parse_json("brak"), {})

    def test_pick_newest_full_model_per_vendor(self):
        models = [{"id": "openai/gpt-9", "created": 5, "architecture": {"input_modalities": ["text", "image"]}},
                  {"id": "openai/gpt-9-mini", "created": 6},
                  {"id": "openai/gpt-8", "created": 1},
                  {"id": "anthropic/claude-x", "created": 3, "architecture": {"input_modalities": ["text"]}}]
        self.assertEqual(pick_models(models, ["anthropic/claude", "openai/gpt"], 2), ["anthropic/claude-x", "openai/gpt-9"])
        self.assertEqual(pick_models(models, ["anthropic/claude", "openai/gpt"], 1, vision=True), ["openai/gpt-9"])

    def test_council_runs_three_rounds(self):
        calls = []

        def chat(model, messages, max_tokens):
            calls.append(model)
            if "przewodniczącym" in messages[-1]["content"]:
                return "**Werdykt rady**: obalona"
            return '{"werdykt": "obalona", "pewność": 0.7, "ranking": ["A"]}'

        r = TheoryResult("t", "h", "m")
        out = deliberate(r, ["a", "b", "c"], "a", chat)
        self.assertEqual(len(calls), 7)  # 3 opinions + 3 reviews + synthesis
        self.assertEqual(out["votes"], {"obalona": 3})


    def test_council_survives_a_model_that_cannot_chat(self):
        def chat(model, messages, max_tokens):
            if model == "decisions/model":
                raise RuntimeError("OpenRouter 400: decisions model cannot be used with chat/completions")
            if "przewodniczącym" in messages[-1]["content"]:
                return "synteza"
            return '{"werdykt": "obalona"}'

        out = deliberate(TheoryResult("t", "h", "m"), ["a", "decisions/model", "b"], "decisions/model", chat)
        self.assertEqual(out["votes"], {"obalona": 2})
        self.assertEqual(out["synthesis"], "synteza")
        self.assertIn("decisions/model", out["failed"])


    def test_vote_labels_from_paragraphs(self):
        from voynich.lab.council import _label
        self.assertEqual(_label("Niepotwierdzona w wersji ogólnej."), "nierozstrzygnięta")
        self.assertEqual(_label("Obalona dla badanego transformera"), "obalona")
        self.assertEqual(_label("Test jest niewiarygodny jako wsparcie"), "metoda niewiarygodna")

    def test_empty_answer_is_retried_then_fails(self):
        from voynich.lab.openrouter import OpenRouter
        client = OpenRouter("k")
        replies = iter([{"choices": [{"message": {"content": ""}}]}, {"choices": [{"message": {"content": ""}}]}])
        client._request = lambda path, body: next(replies)
        with self.assertRaises(RuntimeError):
            client.chat("tencent/hy3", [{"role": "user", "content": "x"}], max_tokens=1800)
        self.assertEqual(client.calls, 2)


class ImagesTest(unittest.TestCase):
    def test_folio_map(self):
        self.assertEqual(len(canvases()), 213)
        self.assertIn("f1r", single_folio_canvases())
        self.assertEqual(base_folio("f85r2"), "f85r")
        mapped = {int(f[1:-1]) for c in canvases() for f in c["folios"]}
        self.assertFalse(mapped & set(MISSING_FOLIOS))


    def test_local_scans_come_first(self):
        import tempfile
        from pathlib import Path
        from voynich.lab.images import fetch, image_urls
        c = single_folio_canvases()["f1v"]
        self.assertTrue(image_urls(c, 800)[0].endswith(f"{c['iiif']}/full/800,/0/default.jpg"))
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "f1v.jpg").write_bytes(b"x" * 2000)
            self.assertEqual(fetch(c, 800, Path(d) / "cache", Path(d)), Path(d) / "f1v.jpg")


    def test_mirror_numbering_and_shape_check(self):
        from voynich.lab import images
        cs = images.canvases()
        self.assertEqual(cs[2]["label"], "1r")
        self.assertTrue(images.mirror_urls(cs[2], 800)[1][0].endswith("/voynich/003.jpg"))
        try:
            from io import BytesIO
            from PIL import Image
        except ImportError:
            self.skipTest("brak Pillow")
        c = cs[2]
        def jpeg(w, h):
            b = BytesIO(); Image.new("RGB", (w, h)).save(b, "JPEG"); return b.getvalue()
        ok = images._check_and_size(jpeg(c["width"] // 4, c["height"] // 4), c, 300, resize=True)
        self.assertEqual(Image.open(BytesIO(ok)).width, 300)
        with self.assertRaises(ValueError):
            images._check_and_size(jpeg(c["height"], c["width"]), c, 300, resize=True)  # a foldout-shaped file


class NumbersTest(unittest.TestCase):
    def test_numeral_systems(self):
        self.assertEqual("".join(numbers.roman(1444)), "MCDXLIV")
        self.assertEqual("".join(numbers.roman(9, subtractive=False)), "VIIII")
        self.assertEqual(numbers.alphabetic(345), ["h3", "t4", "u5"])
        self.assertEqual(numbers.positional(26, 20), ["d1", "d6"])

    def test_zodiac_labels(self):
        pages = numbers.zodiac_label_pages()
        self.assertEqual(len(pages), 12)
        self.assertTrue(all(len(p) in (15, 29, 30) for p in pages))

    def test_sequence_test_finds_planted_numbers(self):
        r = random.Random(1)
        pages = [[numbers.roman(i + 1, False) for i in range(30)] for _ in range(6)]
        self.assertLess(numbers.sequence_test(pages, 200, r)[2], 0.01)


class IllustrationsTest(unittest.TestCase):
    def test_drawing_gaps(self):
        gaps = illustrations.drawing_gaps()
        self.assertGreater(len(gaps), 300)
        self.assertTrue(all(max(pos) < len(words) for words, pos in gaps))

    def test_crib_score(self):
        key = {"k": "s", "o": "a", "l": "l"}
        self.assertEqual(illustrations.crib_score(key, {"f1": ["k", "o", "l"]}, {"f1": ["salvia"]}, k=4), 0.75)


class LiteratureTest(unittest.TestCase):
    def test_affix_split(self):
        self.assertEqual(literature.split_affixes(["q", "o", "k", "e", "e", "d", "y"]), (("q", "o", "k"), ("e", "e", "d", "y")))
        self.assertEqual(literature.split_affixes(["d", "a", "ii", "n"]), (("d",), ("a", "ii", "n")))

    def test_anagram_attack_recovers_plain_anagrams(self):
        r = random.Random(3)
        lexicon = {"".join(sorted(w)) for w in ["abc", "bca", "dd", "cab", "ad"]}
        words = [["x", "y", "z"], ["z", "x", "y"], ["w", "w"], ["x", "w"]]
        cov, key = literature.anagram_attack(words, lexicon, list("abcd"), r, 3000)
        self.assertEqual(cov, 1.0)


if __name__ == "__main__":
    unittest.main()


class RecipeTest(unittest.TestCase):
    def test_key_streams(self):
        from voynich.lab.recipes import digits_of, key_stream
        self.assertEqual(digits_of("pi", 10), [3, 1, 4, 1, 5, 9, 2, 6, 5, 3])
        self.assertEqual(digits_of("e", 6), [2, 7, 1, 8, 2, 8])
        self.assertEqual(digits_of("sqrt2", 5), [1, 4, 1, 4, 2])
        self.assertEqual(key_stream("digits:1404", None), [1, 4, 0, 4])
        self.assertEqual(key_stream("word:agla", None), [0, 6, 11, 0])

    def test_validation(self):
        from voynich.lab.recipes import validate
        ok = {"steps": [{"op": "keystream_shift", "key": "pi"}], "target": "Latin"}
        self.assertEqual(validate(ok), [])
        self.assertTrue(validate({"steps": [{"op": "drop_glyphs"}], "target": "Latin"}))   # missing glyphs
        self.assertTrue(validate({"steps": [], "target": "Klingon"}))
        self.assertTrue(validate({"steps": [{"op": "take_words", "every": 1}], "target": "Latin"}))
        # Zodiac pages hold labels and ring text only: no running text for a recipe (Colab hunt wasted 3 recipes).
        self.assertTrue(validate({"steps": [], "target": "Latin", "scope": {"section": "zodiac"}}))
        self.assertEqual(validate({"steps": [], "target": "Latin", "scope": {"section": "herbal"}}), [])

    def test_every_step_is_undone_by_its_plant(self):
        # The positive control rests on this: decoding a planted text must give back the plaintext.
        from voynich.lab.recipes import OPS, Ctx, apply_steps, as_words, plant_steps
        r = random.Random(4)
        symbols = [f"s{i:02d}" for i in range(26)]
        plain = [("p", [[r.choice(symbols) for _ in range(r.randint(1, 7))] for _ in range(9)]) for _ in range(20)]
        params = {"rotate": {"k": 2}, "drop_glyphs": {"glyphs": ["q", "e"]}, "keep_every": {"n": 3, "offset": 1},
                  "take_words": {"every": 2, "offset": 1}, "group_glyphs": {"size": 2},
                  "keystream_shift": {"key": "pi", "restart": "line", "mode": "add"}}
        for name, op in OPS.items():
            if name == "sort_glyphs":
                continue  # anagram hypotheses decode to sorted letters by design
            recipe = {"steps": [{"op": name, **params.get(name, {})}], "target": "Latin"}
            ctx = Ctx(r, alphabet=symbols)
            back = apply_steps(plant_steps(plain, recipe, ctx), recipe, Ctx(r, alphabet=symbols))
            got = as_words(back, op.spaceless)
            if name == "group_glyphs":
                got = [[g.split("+")[0] for g in w] for w in got]
            want = as_words(plain, op.spaceless)
            self.assertEqual(got, want, name)


class NomenclatorTest(unittest.TestCase):
    def test_codebook_text_gains_from_word_order(self):
        # The theory rests on this: a real text under a random codebook reads better in order than shuffled.
        from collections import Counter
        from voynich import cipher, corpus
        from voynich.lab.theories.nomenclator import _units, order_gain, plant
        r = random.Random(5)
        words = corpus.load_reference("Latin")
        top = {w for w, _ in Counter(words[20000:]).most_common(30)}
        model = cipher.TrigramModel(_units(words[20000:], top))
        gain, _ = order_gain(plant(words[:2500], top, 1, r), model, r, restarts=2, steps=20000, seed=1)
        self.assertGreater(gain, 0.05)


class NotebookTest(unittest.TestCase):
    def test_every_code_cell_compiles(self):
        # A syntax error in a cell stops "Run all" in Colab; shell (!) and magic (%) lines are not Python.
        import json
        from pathlib import Path
        for name in ("Voynich_Lab.ipynb", "Voynich_Ilustracje.ipynb", "Voynich_Brute.ipynb", "Voynich_Final.ipynb",
                     "Voynich_Notacja.ipynb", "Voynich_Rejestr.ipynb", "Voynich_Rejestr_GPU.ipynb",
                     "Voynich_Klucz.ipynb"):
            nb = json.loads((Path(__file__).resolve().parent.parent / "colab" / name).read_text(encoding="utf-8"))
            for i, c in enumerate(nb["cells"]):
                if c["cell_type"] == "code":
                    src = "".join(l for l in c["source"] if not l.lstrip().startswith(("!", "%")))
                    compile(src, f"{name} komórka {i}", "exec")


class HuntTest(unittest.TestCase):
    def test_hound_without_recipe_is_asked_again_then_logged(self):
        import tempfile
        from pathlib import Path
        from types import SimpleNamespace
        from voynich.lab.hounds import Hunt
        replies = iter(["Uważam, że to bełkot.", "Nadal sądzę, że to bełkot.",
                        "Za drugim razem nic.", '{"recipes": [{"name": "x", "steps": [], "target": "Latin"}]}'])
        calls = []
        client = SimpleNamespace(chat=lambda m, msgs, t: (calls.append(len(msgs)), next(replies))[1])
        with tempfile.TemporaryDirectory() as d:
            lab = SimpleNamespace(client=client, cfg=SimpleNamespace(quick=True, results_dir=Path(d), max_tokens=100))
            hunt = Hunt(lab, rounds=1, per_hound=1, workers=1)
            self.assertEqual(hunt._ask(0, "m", 1), [])
            self.assertEqual(len(hunt.silent), 1)
            self.assertEqual(calls, [1, 3])  # the retry carries the first answer and a reminder
            self.assertEqual([r["name"] for r in hunt._ask(0, "m", 1)], ["x"])  # the reminder worked
            self.assertEqual(len(hunt.silent), 1)


class BruteTest(unittest.TestCase):
    def test_batched_solver_matches_backtracking_and_finds_planted_key(self):
        from collections import defaultdict
        import numpy as np
        from voynich.lab import brute
        dev = brute.Device(prefer_gpu=False)
        lex = brute.Lexicon.load("Latin")
        small = lex.words[:300]
        bp = defaultdict(list)
        for i, w in enumerate(small):
            bp[brute.pattern(w)].append(i)
        lex.by_pattern = {p: np.array(ix) for p, ix in bp.items()}
        lex._cache = {}
        lines = brute.paragraph_lines()[:40]
        s = brute.Settings(max_pairs=10 ** 6, top=10 ** 6)
        for triple in list(brute.triples_of(lines))[:60]:
            ids, _ = brute.structure(triple)
            got = {words for _, _, words in brute.solve_structure(ids, lex, dev, s)}
            self.assertEqual(got, brute.reference_solve(triple, small), triple)
        # A real Latin text under a random key: the voted key is recovered.
        lex = brute.Lexicon.load("Latin")
        from voynich import corpus
        text = [brute.lexicon.normalize(w) for w in corpus.load_reference("Latin")[30000:36000]]
        enc, truth = brute.encipher(text, 23, 5)
        a = brute.attack(enc, lex, dev, brute.Settings(), 300, 1)
        self.assertGreater(a.dict_rate, 0.8)
        self.assertGreater(sum(a.key.get(g) == c for g, c in truth.items()) / len(truth), 0.8)


class LexiconTest(unittest.TestCase):
    def test_parsers_for_sefaria_and_text_fabric(self):
        import json
        from voynich import lexicon
        payload = json.dumps({"versions": [{"text": [["בְּקַדְמִין בְּרָא <b>יְיָ</b>:", "וְאַרְעָא הֲוַת"], ["יְהֵי נְהוֹרָא"]]}]})
        words = [lexicon.normalize(w) for w in lexicon.sefaria_words(payload)]
        self.assertEqual([w for w in words if w], ["בקדמין", "ברא", "יי", "וארעא", "הות", "יהי", "נהורא"])  # points stripped
        tf = "@node\n@dataset=peshitta\n\nܥܠ\nܐ̈ܦܝ\nܡ̈ܝܐ\n"
        self.assertEqual([lexicon.normalize(w) for w in lexicon.textfabric_words(tf)], ["ܥܠ", "ܐܦܝ", "ܡܝܐ"])



class WheelTest(unittest.TestCase):
    def _lines(self):
        from voynich import corpus, eva
        lines = [[tuple(eva.glyphs(w)) for w in l.words] for l in corpus.load_voynich() if l.kind.startswith("P") and l.words]
        return lines[:120]

    def test_compositions_round_trip(self):
        from voynich.lab import wheel
        lines = self._lines()
        seg = wheel.Segments.from_words({w for l in lines for w in l})
        word = next(w for l in lines for w in l if len(w) >= 4)
        comps = wheel.compositions(word, 3, seg)
        self.assertTrue(comps)
        for comp in comps:
            self.assertEqual(tuple(g for i in comp for g in seg.strings[i]), word)

    def test_fit_and_scribe(self):
        from voynich.lab import wheel
        lines = self._lines()
        s = wheel.Search(rings=3, cells=12, population=16, generations=3, seed=1)
        best, text = wheel.fit(lines, s, wheel.Backend(prefer_gpu=False), None)
        self.assertGreater(best["coverage"], 0.3)
        self.assertEqual(len(best["rings"]), 3)
        self.assertTrue(all(len(r) == 12 for r in best["rings"]))
        gen = wheel.scribe(lines, best["rings"], text.seg, 300, seed=1)
        self.assertGreaterEqual(sum(map(len, gen)), 300)
        self.assertTrue(all(isinstance(w, (list, tuple)) and w for l in gen for w in l))


class GenresTest(unittest.TestCase):
    def test_litany_words_drop_markup(self):
        from voynich import genres
        words = genres.litany_words("{{Titulus|x}}\n:Sancta Maria,\n:R. ora pro nobis.\n:V. Dominus [[a|vobiscum]].")
        self.assertEqual(words, ["sancta", "maria", "ora", "pro", "nobis", "dominus", "vobiscum"])

    def test_barbarous_names_keep_only_name_runs(self):
        from voynich import genres
        text = "He said _this is an ordinary sentence of prose words_ and then _Hazachay Hazatha Lemogethom Hegemochom Gezomay_."
        names = genres.barbarous_names(text, {"hazatha"})
        self.assertEqual(names, ["hazachay", "lemogethom", "hegemochom", "gezomay"])


class TransliterationsTest(unittest.TestCase):
    def test_generic_cleaning_keeps_case_and_digits(self):
        from voynich import transliterations as tr
        self.assertEqual(tr.clean_generic("<%>fa19s.9,hae.ay.Akam<->2oe.!oy9.@253;scs<$>"),
                         "fa19s.9.hae.ay.Akam.2oe.!oy9.?scs")

    def test_zl_matches_corpus(self):
        from voynich import corpus, eva, transliterations as tr
        lines = tr.load_lines("ZL")
        first = [[tuple(eva.glyphs(w)) for w in l.words] for l in corpus.load_voynich() if l.kind.startswith("P")][0]
        self.assertEqual(lines[0], first)


class HillclimbTest(unittest.TestCase):
    def test_ngram_model_prefers_its_language(self):
        from voynich.lab import hillclimb as hc
        latin = ("in principio creavit deus caelum et terram terra autem erat inanis et vacua et tenebrae erant "
                 "super faciem abyssi et spiritus dei ferebatur super aquas dixitque deus fiat lux et facta est lux").split()
        lm = hc.NgramModel.fit(latin * 20, order=3)
        self.assertLess(lm.bits(["et", "terra", "deus"]), lm.bits(["xqz", "tttt", "zzq"]))

    def test_climb_recovers_a_substitution_key(self):
        from voynich import corpus
        from voynich.lab import hillclimb as hc
        words = corpus.load_reference("Latin")[:6000]
        lm = hc.NgramModel.fit(words[:4000], order=3)
        enc, truth = hc.encipher_homophonic(words[4000:], 22, seed=1)
        glyphs = hc.glyph_inventory(enc, min_count=1)
        odd, even = hc.split_odd_even(enc)
        text, held = hc.GlyphText.build(odd, glyphs, 3), hc.GlyphText.build(even, glyphs, 3)
        out = hc.climb(text, lm, hc.Climb(population=64, steps=400, seed=1), hc.Backend(prefer_gpu=False), held)
        self.assertGreater(hc.key_accuracy(out["key"], truth, enc), 0.5)
        self.assertLess(out["held_out_bits"], lm.bits(words[4000:]) + 1.0)


class CognateTest(unittest.TestCase):
    def test_edit_index(self):
        from voynich.lab.cognate import EditIndex
        ix = EditIndex(["terra", "caelum", "deus"])
        for w in ("terra", "tera", "terrra", "tirra", "deux"):
            self.assertTrue(ix.within_one(w), w)
        self.assertFalse(ix.within_one("tirri"))
        self.assertFalse(ix.within_one("xyz"))

    def test_features_and_sinkhorn_numpy(self):
        import numpy as np
        from collections import Counter
        from voynich.lab import cognate as cg
        known = cg.Vocab.from_counts(Counter({"terra": 5, "deus": 3, "caelum": 2}), list("abcdelmrstu"), 10)
        F = cg.features(known.onehot(), np)
        self.assertEqual(F.shape, (3, 2 * 12 * 12))
        self.assertTrue(np.allclose((F * F).sum(1), 1.0))
        cost = 1 - F @ F.T
        a = np.full(3, 1 / 3); b = np.full(3, 1 / 3)
        plan = cg.sinkhorn(cost, a, b, 0.05, 50, np)
        self.assertTrue(np.allclose(plan.sum(1), a, atol=1e-3))
        self.assertGreater(plan[0, 0], plan[0, 1])

    def test_noisy_encipher_truth_key(self):
        from voynich.lab import cognate as cg
        words = ["terra", "caelum", "deus", "et", "aqua"] * 50
        enc, truth = cg.noisy_encipher(words, 10, seed=2, noise=0.0)
        self.assertEqual(cg.key_accuracy(truth, truth, enc), 1.0)
        self.assertEqual(cg.cognate_rate(enc, truth, cg.EditIndex(set(words)))[0], 1.0)


class PhonotacticsTest(unittest.TestCase):
    def test_sukhotin_finds_latin_vowels(self):
        from voynich import corpus, phonotactics as ph
        words = corpus.load_reference("Latin")[:20000]
        vowels, order = ph.sukhotin([tuple(w) for w in words])
        self.assertTrue({"a", "e", "i", "o", "u"} <= vowels, order)
        self.assertFalse({"t", "s", "r", "m"} & vowels, order)

    def test_patterns_and_divergence(self):
        from voynich import phonotactics as ph
        self.assertEqual(ph.pattern("terra", set("aeiou")), "CVCCV")
        p = ph.profile([("t", "e", "r", "r", "a"), ("e", "t")], set("aeiou"))
        self.assertAlmostEqual(p["patterns"]["CVCCV"], 0.5)
        self.assertEqual(ph.js_divergence(p["patterns"], p["patterns"]), 0.0)
        self.assertAlmostEqual(ph.js_divergence({"CV": 1.0}, {"VC": 1.0}), 1.0)


class RecoverTest(unittest.TestCase):
    def test_result_round_trip_and_recover(self):
        import tempfile
        from pathlib import Path
        from voynich.lab.config import LabConfig
        from voynich.lab.runner import Lab
        r = TheoryResult("t", "h", "m")
        r.control("ok", "x", "x", True)
        r.decide(True)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            r.save(root / "20200101-000000")
            back = TheoryResult.load(root / "20200101-000000" / "t.json")
            self.assertEqual(back.verdict, "potwierdzona")
            self.assertEqual(back.controls[0].name, "ok")
            lab = Lab(LabConfig(results_dir=root))
            self.assertIsNotNone(lab.recover("t"))
            self.assertIn("t", lab.results)
            self.assertIsNone(lab.recover("nope"))


class PublishTest(unittest.TestCase):
    def test_publish_does_not_touch_the_code_checkout(self):
        import subprocess, tempfile
        from pathlib import Path
        from voynich.lab.config import LabConfig
        from voynich.lab.runner import Lab, ROOT
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
        with tempfile.TemporaryDirectory() as tmp:
            bare = Path(tmp) / "remote.git"
            subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
            cfg = LabConfig(results_dir=ROOT / "results" / "test-publish", git_branch="test-lab-results")
            lab = Lab(cfg)
            (lab.cfg.results_dir / "t.md").write_text("x", encoding="utf-8")
            try:
                out = lab.publish(str(bare))
                self.assertEqual(out.returncode, 0, out.stderr)
                (lab.cfg.results_dir / "u.md").write_text("y", encoding="utf-8")
                out = lab.publish(str(bare))           # second push on top of the first
                self.assertEqual(out.returncode, 0, out.stderr)
                log = subprocess.run(["git", "-C", str(bare), "log", "--oneline", "test-lab-results"], capture_output=True, text=True).stdout
                self.assertEqual(len(log.strip().splitlines()), 2)
                files = subprocess.run(["git", "-C", str(bare), "ls-tree", "-r", "--name-only", "test-lab-results"], capture_output=True, text=True).stdout
                self.assertIn(f"results/test-publish/{lab.stamp}/t.md", files)
            finally:
                import shutil
                shutil.rmtree(ROOT / "results" / "test-publish", ignore_errors=True)
        after = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.assertEqual(head, after)
        self.assertTrue((ROOT / "voynich" / "lab" / "theories" / "transcriptions.py").exists())


class LengthCodeTest(unittest.TestCase):
    def test_planted_text_shows_order_and_shuffle_does_not(self):
        from voynich import corpus
        from voynich.lab.theories import length_code as lc
        rows = [[4, 5, 3, 4, 6, 2, 5, 4, 3]] * 300
        plant = lc.planted(corpus.load_reference("Latin"), rows)
        _, z = lc.structure_z(plant, shuffles=20, seed=1)
        self.assertLess(z, -5)
        import random
        r = random.Random(1)
        flat = [x for row in plant for x in row]
        r.shuffle(flat)
        rnd = [flat[i:i + 9] for i in range(0, len(flat) - 8, 9)]
        _, z2 = lc.structure_z(rnd, shuffles=20, seed=1)
        self.assertGreater(z2, -3)
        self.assertEqual(lc.digits([[["a", "b"], ["c"] * 12]]), [[2, 9]])


class PagesTest(unittest.TestCase):
    def test_arrow_in_synthetic_copying_and_not_in_shuffled(self):
        from voynich import pages as pg
        near = pg.synthetic_self_citation(30, 120, seed=1, near=True)
        nbs = pg.Neighbours(near)
        order = list(range(len(near)))
        z = pg.arrow_z(nbs, order, [order], shuffles=20, seed=1)
        self.assertGreater(z["z"], 4)
        import random
        r = random.Random(1)
        sh = order[:]; r.shuffle(sh)
        pos = {p: i for i, p in enumerate(sh)}
        e_sh, _ = pg.ancestor_excess(nbs, order, pos)
        self.assertLess(abs(e_sh - z["null_mean"]), 4 * z["null_sd"] + 0.02)

    def test_blocks_and_neighbours(self):
        from voynich import pages as pg
        ps = [pg.Page("f1r", "herbal", "A", "1", "A", [("a", "b"), ("a", "b", "c"), ("x",)]),
              pg.Page("f1v", "herbal", "A", "1", "A", [("a", "c")]), pg.Page("f2r", "stars", "B", "3", "T", [("q",)])]
        self.assertEqual(pg.blocks(ps), [[0, 1], [2]])
        nbs = pg.Neighbours(ps)
        ab, abc, ac = nbs.enc(("a", "b")), nbs.enc(("a", "b", "c")), nbs.enc(("a", "c"))
        self.assertIn(abc, nbs.nb[ab]); self.assertIn(ac, nbs.nb[ab]); self.assertNotIn(nbs.enc(("x",)), nbs.nb[ab])


class WheelControlTest(unittest.TestCase):
    def test_known_wheel_writes_readable_text(self):
        from voynich import corpus, eva
        from voynich.lab import wheel
        lines = [[tuple(eva.glyphs(w)) for w in l.words] for l in corpus.load_voynich() if l.kind.startswith("P") and l.words][:120]
        seg = wheel.Segments.from_words({w for l in lines for w in l})
        rings = wheel.random_wheel(seg, 3, 12, seed=1)
        self.assertEqual(rings.shape, (3, 12))
        text = wheel.write_random(rings, seg, 200, seed=1)
        words = [w for l in text for w in l]
        self.assertGreaterEqual(len(words), 200)
        self.assertTrue(all(wheel.decompose(w, rings, seg) is not None for w in words[:50]))


class NotationTest(unittest.TestCase):
    def test_volpiano_units(self):
        from voynich import notation
        v = "1---k--l--k--h---gfed--d---"
        self.assertEqual(notation.volpiano_units(v, "word"), [("k", "l", "k", "h"), ("g", "f", "e", "d", "d")])
        self.assertEqual(notation.volpiano_units(v, "syllable")[:3], [("k",), ("l",), ("k",)])
        self.assertEqual(notation.volpiano_units("1---f-g--h7---j4", "neume"), [("f",), ("g",), ("h",), ("j",)])

    def test_extract_dances(self):
        from voynich import notation
        text = "Filles a marier. R b ss d r d r b ss ddd ss r b ss d r b. Next: R b ss."
        d = notation.extract_dances(text)
        self.assertEqual(len(d), 1)
        self.assertTrue(d[0].startswith("R b ss d r"))
        self.assertEqual(notation.dance_lines()[0][:3], [("R",), ("b",), ("s", "s")])


class ListsTest(unittest.TestCase):
    MART = """{{titulus2|x=y}}
PROLOGUS AD CAROLUM.
123.0599A| Domino regum piissimo verba prologi hic sunt multa.
:MENSIS JANUARIUS HABET DIES XXXI.
:Kalendis. Die 1.
123.0601|
Circumcisio Domini nostri Jesu Christi. Romae, natalis sancti Almachii martyris [ Bouillart. add. et prunas] (AUG, l. XX).
:IV Nonas. Die 2.
Apud Antiochiam, passio beati Isidori episcopi et trium fratrum.
:XIX Kal. Die 14.
In Africa, natalis sancti Felicis presbyteri.
"""
    APIC = """{{titulus2|x=y}}
== I. Conditum paradoxum. ==
1. CONDITI PARADOXI COMPOSITIO.

Mellis p.XV in aeneum uas mittuntur, praemissis vini sextariis duobus.

2. CONDITUM MELIZOMUM.

Piper tritum cum melle despumato in cupellam mittis.

== X. Ut uncia laseris toto tempore durent. ==
Laser in spatiosum doliolum vitreum mittis et nucleos pineos.
"""
    ALPH = """Google digitised text
A MEDICO-BOTANICAL GLOSSARY.
Absinthium', herba fortis, gal- | Acopum, i. mitigatiuum et dicitur
lice aloine, anglice uuermode. | a quod est sine labor.
Acacia, i. succus desiccatus prunelarum agrestium.
3. aloyne. 5. lineriuue. 6. sotherwod.
1 dvivOov, E. P. N. p. 42, ‘Absinthium, aloigne, wermod.' κακος ακανθα
2 A MEDICO-BOTANICAL GLOSSARY.
Acorus, i. radix gladioli iuxta aquas crescit.
INDEX.
Bistorte, 23.
Botun de rose, 23.
Bourefair, 40, 115.
"""

    def test_martyrology_days(self):
        from voynich import lists
        e = lists.martyrology_entries(self.MART)
        self.assertEqual(len(e), 3)
        self.assertEqual(e[0][:3], ["circumcisio", "domini", "nostri"])
        self.assertNotIn("bouillart", e[0])
        self.assertNotIn("aug", e[0])
        self.assertNotIn("prologi", " ".join(w for x in e for w in x))
        self.assertEqual(e[2][:2], ["in", "africa"])

    def test_apicius_recipes(self):
        from voynich import lists
        e = lists.apicius_entries(self.APIC)
        self.assertEqual(len(e), 3)
        self.assertEqual(e[0][:3], ["conditi", "paradoxi", "compositio"])
        self.assertIn("mellis", e[0])
        self.assertEqual(e[2][:3], ["x", "ut", "uncia"])

    def test_alphita(self):
        from voynich import lists
        e = lists.alphita_entries(self.ALPH)
        self.assertEqual([x[0] for x in e], ["absinthium", "acacia", "acopum", "acorus"])
        self.assertNotIn("aloyne", " ".join(w for x in e for w in x))
        self.assertEqual(lists.alphita_headwords(self.ALPH), [["bistorte"], ["botun", "de", "rose"], ["bourefair"]])
        q = lists.quality(e)
        self.assertEqual(q["entries"], 4)
        self.assertFalse(lists.passes(q))
        self.assertTrue(lists.passes({"entries": 300, "median_words": 20}))

    def test_committed_corpora_pass_gate(self):
        from voynich import lists
        for name in ("martyrology", "apicius", "alphita"):
            self.assertTrue(lists.passes(lists.quality(lists.load(name))), name)


class LabelsTest(unittest.TestCase):
    def test_planted_citation_detected_shuffled_not(self):
        from voynich import labels
        pages, pool = labels.synthetic_label_pages(30, 3, names=True, cite=0.0)
        base = labels.citation(pages, shuffles=100, seed=1)
        planted = labels.citation(labels.plant_citations(pages, 0.1, 1), shuffles=100, seed=1)
        self.assertLess(abs(base["z"]), 3)
        self.assertGreater(planted["z"], 5)
        cited, _ = labels.synthetic_label_pages(30, 3, names=True, cite=0.1)
        dealt = labels.citation(labels.shuffle_labels(cited, random.Random(2)), shuffles=100, seed=1)
        self.assertLess(abs(dealt["z"]), 3)

    def test_names_are_a_subvocabulary(self):
        from voynich import labels
        pages, pool = labels.synthetic_label_pages(30, 4, names=True)
        sv = labels.subvocabulary(pages, pool, draws=100, seed=1)
        self.assertGreater(sv["hapax"]["z"], 4)
        self.assertGreater(sv["o_initial"]["z"], 4)
        plain, pool = labels.synthetic_label_pages(30, 4, names=False)
        sv = labels.subvocabulary(plain, pool, draws=100, seed=1)
        self.assertLess(max(abs(sv[k]["z"]) for k in ("hapax", "o_initial", "mean_length")), 3)

    def test_uniqueness_and_loading(self):
        from voynich import labels
        pages = labels.load_label_pages()
        self.assertGreater(len(pages), 40)
        self.assertTrue(all(p.labels for p in pages))
        u = labels.uniqueness(pages, shuffles=50, seed=1)
        self.assertIn("Lz", u)
        self.assertTrue(0 <= u["Lz"]["value"] <= 1)


class RecordsTest(unittest.TestCase):
    def test_synthetic_records_and_shuffle(self):
        from voynich import records
        lines, groups = records.synthetic_records(800, 1)
        self.assertGreater(records.slot_auc(lines, groups, records.INTERIOR, 1), 0.8)
        mi = records.field_mi_z(lines, records.INTERIOR, shuffles=30, seed=1)
        self.assertGreater(mi["first"]["z"], 5)
        self.assertGreater(records.template_gain(lines, groups, 1), 0.2)
        sh = records.shuffle_within_lines(lines, random.Random(2))
        self.assertLess(records.slot_auc(sh, groups, records.INTERIOR, 1), 0.65)
        self.assertLess(abs(records.field_mi_z(sh, records.INTERIOR, shuffles=30, seed=1)["first"]["z"]), 3)

    def test_slots(self):
        from voynich import records
        self.assertEqual([records.slot(i, 6, records.EDGE) for i in range(6)], [0, 1, 1, 1, 1, 2])
        self.assertEqual([records.slot(i, 6, records.INTERIOR) for i in range(6)], [None, 0, 1, 2, 3, None])
        self.assertEqual([records.slot(i, 4, records.INTERIOR) for i in range(4)], [None] * 4)


class V6Test(unittest.TestCase):
    def test_freq_gamma_zero_reproduces_v5(self):
        from voynich.lab.theories.hoax import V5_SECTION_PARAMS, generate_by_section, odd_runs, section_models
        runs = odd_runs()[:3]
        models = section_models(runs)
        a = generate_by_section(runs, V5_SECTION_PARAMS, 3, models=models)
        b = generate_by_section(runs, {**V5_SECTION_PARAMS, "freq_gamma": 0.0}, 3)
        self.assertEqual(a, b)
        c = generate_by_section(runs, {**V5_SECTION_PARAMS, "freq_gamma": 1.0}, 3, models=models)
        self.assertNotEqual(a, c)
        wa, wc = sum(map(len, a)), sum(map(len, c))
        self.assertLess(abs(wa - wc) / wa, 0.05)      # the word budget is kept, the line count may differ

    def test_v6_space_and_evolution(self):
        from voynich.lab import v6
        rng = random.Random(1)
        for _ in range(50):
            m = v6.mutate(v6.V5_POINT, 0.5, rng)
            for k, (lo, hi, integer) in v6.SPACE.items():
                self.assertTrue(lo <= m[k] <= hi, k)
                if integer:
                    self.assertIsInstance(m[k], int)
        self.assertEqual(v6.clip(v6.V5_POINT), v6.clip(v6.clip(v6.V5_POINT)))
        card = {"h2": {"z": 0.5}, "hapax_ratio": {"z": -2.0}, "words_per_line": {"z": 3.0}}
        self.assertAlmostEqual(v6.fitness_of(card), 1.0 + 12.0 + 4.0)
        from voynich import hoax
        from voynich.lab.theories.hoax import odd_runs, split_lines
        runs, n = [], 0
        for r in odd_runs():                         # enough runs for one 4000-word block
            runs.append(r)
            n += sum(map(len, r[1]))
            if n >= 4500:
                break
        shared = v6.Shared(runs, v6.section_models(runs), hoax.yardstick(split_lines()[0]), n_blocks=1)
        a, b = v6.evaluate(v6.V5_POINT, 3, shared), v6.evaluate(v6.V5_POINT, 3, shared)
        self.assertEqual(a["fitness"], b["fitness"])
        self.assertTrue(a["fitness"] == a["fitness"] and a["fitness"] < float("inf"))
        ev = v6.Evolution(population=4, generations=2, elite=2, workers=2, seed=1)
        best = ev.run(shared=shared)
        self.assertEqual(len(ev.history), 2)
        self.assertLessEqual(best["fitness"], ev.history[0]["best"] + 1e-9)
        self.assertTrue(ev.finalists)


class FieldsTest(unittest.TestCase):
    def test_position_encoding(self):
        from voynich.lab.theories.generative import POS_TOKENS, PosVocab
        v = PosVocab(["daiin.ol.chedy", "qokeey.dal"])
        plain = v.encode(["daiin.ol.chedy"], "none")
        pos = v.encode(["daiin.ol.chedy"], "pos")
        rnd = v.encode(["daiin.ol.chedy"], "random", seed=5)
        self.assertEqual(len(pos), len(plain) + 3)
        self.assertEqual(len(rnd), len(pos))
        self.assertEqual([v.itos[i] for i in pos if i in v.pos_ids], POS_TOKENS[:3])
        self.assertEqual([i for i in plain if i in v.pos_ids], [])
        self.assertTrue(all(i in v.keep for i in plain))
        self.assertFalse(any(i in v.keep for i in v.pos_ids))

    def test_split_keeps_chunks_apart(self):
        from voynich.lab.theories import fields_lm
        lines = [f"w{i}" for i in range(200)]
        tr, pick, test = fields_lm.split(lines, 1)
        self.assertEqual(len(tr) + len(pick) + len(test), 200)
        self.assertFalse(set(pick) & set(test) or set(tr) & set(pick))


class CohesionTest(unittest.TestCase):
    def test_pairs_hold_pages_out(self):
        from voynich.lab.theories import cohesion
        pages = {f"p{i}": [f"p{i}w{j}.x" for j in range(6)] for i in range(8)}
        group = {p: "s" for p in pages}
        xtr, ytr, xte, yte = cohesion.pairs(pages, group, 40, 1)
        self.assertEqual((len(xtr), len(xte)), (40, 20))
        self.assertEqual(sum(ytr), 20)
        train_pages = {x.split("w")[0] for x in xtr}
        test_pages = {x.split("w")[0] for x in xte}
        self.assertFalse(train_pages & test_pages)
        for x, y in zip(xtr, ytr):
            a, b = x.split("|")
            self.assertEqual(a.split("w")[0] == b.split("w")[0], bool(y))
        pg, grp = cohesion.pseudo_pages([f"l{i}" for i in range(50)], ["a"] * 30 + ["b"] * 20, 10, 1)
        self.assertEqual(len(pg), 5)
        self.assertTrue(all(len(ls) == 10 for ls in pg.values()))
        planted = cohesion.plant({"p": ["a.b.c.d.e"] * 3}, 1.0, 1)
        self.assertEqual(len(set(planted["p"][0].split("."))), 1)


class KeystreamTest(unittest.TestCase):
    LAT = [[list(w) for w in "in principio creavit deus caelum et terram".split()],
           [list(w) for w in "terra autem erat inanis et vacua et tenebrae".split()]]

    def test_cut_and_keys(self):
        from voynich import keystream as K
        self.assertEqual(K.cut(list("abcdefg"), [2, 3]), [list("ab"), list("cde"), list("fg")])
        self.assertEqual(K.key_variant([2, 9, 6, 5], "shift", 1, None), [9, 6, 5, 2])
        self.assertEqual(K.key_variant([2, 9, 6, 5], "reverse", 0, None), [5, 6, 9, 2])
        self.assertEqual(K.key_variant([2, 9], "previous", 0, [3, 3]), [3, 3])
        self.assertEqual(K.lengths([["c", "h", "o"], ["d", "a"]], "glyphs"), [3, 2])
        self.assertEqual(K.lengths([["ch", "o"], ["d", "a"]], "chars"), [3, 2])
        self.assertEqual(K.stride_read(list("abcdef"), 2), list("acebdf"))

    def test_every_transform_keeps_the_glyphs(self):
        from voynich import keystream as K
        for t in K.family():
            out = K.apply(t, self.LAT)
            self.assertEqual(len(out), 2, t.name)
            for a, b in zip(self.LAT, out):
                self.assertEqual(sum(map(len, a)), sum(map(len, b)), t.name)
                if t.kind != "shift":
                    self.assertEqual(sorted(g for w in a for g in w), sorted(g for w in b for g in w), t.name)

    def test_cipher_is_undone_by_its_inverse(self):
        from voynich import keystream as K
        for t in (K.Transform("c", "cut", "glyphs", 2), K.Transform("r", "read", "none", 3), K.Transform("s", "shift", "glyphs", 0),
                  K.Transform("p", "shift", "none", 2)):
            cipher = K.encipher(self.LAT, t)
            self.assertEqual(K.apply(t, cipher), [[list(w) for w in l] for l in self.LAT], t.name)
        c = K.encipher(self.LAT, K.Transform("c", "cut", "glyphs", 2))
        self.assertLess(K.boundary_f1(self.LAT, c), 0.6)
        self.assertEqual(K.boundary_f1(self.LAT, self.LAT), 1.0)

    def test_description_length_prefers_true_words(self):
        from voynich import corpus, keystream as K
        lat = corpus.load_reference("Latin")[:9000]
        lines = [[list(w) for w in lat[i:i + 9]] for i in range(0, len(lat), 9)]
        dl0 = K.description_length(lines)
        for t in K.family()[1:]:
            dl = K.description_length(K.apply(t, lines))
            if t.kind == "shift":                        # a bijection on word types keeps the length; keyed by the neighbour it grows
                self.assertGreaterEqual(dl, dl0 - 1e-9, t.name)
            else:
                self.assertGreater(dl, dl0, t.name)
        cipher = K.encipher(lines, K.Transform("c", "cut", "glyphs", 2))
        scores = {t.name: K.description_length(K.apply(t, cipher)) for t in K.family()}
        self.assertIn("przesunięte o 2", min(scores, key=scores.get))

    def test_adjacent_mi_sign(self):
        from voynich import keystream as K
        rng = random.Random(1)
        vocab = [tuple(rng.choice("abcde") for _ in range(3)) for _ in range(40)]
        # lines where word i+1 is determined by word i: positive MI; the same lines shuffled: about zero
        nxt = {w: vocab[(i * 7 + 3) % 40] for i, w in enumerate(vocab)}
        lines = []
        for _ in range(300):
            w = rng.choice(vocab)
            l = [list(w)]
            for _ in range(7):
                w = nxt[w]
                l.append(list(w))
            lines.append(l)
        z = K.adjacent_mi_z(lines, 20, 1)
        self.assertGreater(z["z"], 5)
        # a shift keyed by the word's own length is a bijection on word types: the information is unchanged
        shifted = K.apply(K.Transform("s", "shift", "glyphs", 0), lines)
        self.assertAlmostEqual(K.adjacent_mi_z(shifted, 20, 1)["value"], z["value"])
