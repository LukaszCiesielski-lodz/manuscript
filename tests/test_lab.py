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
