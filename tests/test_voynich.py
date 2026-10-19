import random
import unittest

from voynich import cipher, corpus, eva, ivtff, selfcite, stats, structure


class EvaTest(unittest.TestCase):
    def test_clean_markup(self):
        raw = "<%>fachys.ykal.ar.[cth:oto]res,y.{ck}eo.d@194;n<!@254;><$>"
        self.assertEqual(eva.clean(raw), "fachys.ykal.ar.cthres.y.ckeo.d?n")
        self.assertEqual(eva.clean("ab,cd", uncertain_spaces=False), "abcd")
        self.assertEqual(eva.clean("ab<->cd"), "ab.cd")

    def test_words_drop_uncertain(self):
        self.assertEqual(eva.words("daiin.d?n.ol"), ["daiin", "ol"])
        self.assertEqual(eva.words("daiin.d?n", drop_uncertain=False), ["daiin", "d?n"])

    def test_glyphs(self):
        self.assertEqual(eva.glyphs("qokeedy"), ["q", "o", "k", "e", "e", "d", "y"])
        self.assertEqual(eva.glyphs("cthaiin"), ["cth", "a", "ii", "n"])
        self.assertEqual(eva.glyphs("shckhey"), ["sh", "ckh", "e", "y"])
        self.assertEqual(eva.glyphs("daiiin"), ["d", "a", "iii", "n"])


class IvtffTest(unittest.TestCase):
    def test_parse_real_file(self):
        pages = ivtff.parse(corpus.ZL_FILE)
        self.assertGreater(len(pages), 200)
        f1r = pages[0]
        self.assertEqual(f1r.folio, "f1r")
        self.assertEqual(f1r.language, "A")
        self.assertEqual(f1r.section, "text")
        self.assertTrue(f1r.loci[0].raw.startswith("<%>fachys"))


class StatsTest(unittest.TestCase):
    def test_entropy_of_uniform_alternation(self):
        # "ab ab ab ...": after 'a' always 'b', after 'b' always space, after space always 'a'
        h = stats.char_entropies(["ab"] * 100)
        self.assertAlmostEqual(h["h2"], 0.0, places=6)
        self.assertAlmostEqual(h["h1"], 1.585, places=2)

    def test_zipf_slope_of_ideal_zipf(self):
        words = [f"w{r}" for r in range(1, 201) for _ in range(1000 // r)]
        self.assertAlmostEqual(stats.zipf_slope(words), -1.0, delta=0.05)

    def test_is_near(self):
        self.assertTrue(stats.is_near(tuple("chedy"), tuple("shedy")))
        self.assertTrue(stats.is_near(tuple("chedy"), tuple("chdy")))
        self.assertFalse(stats.is_near(tuple("chedy"), tuple("chedy")))
        self.assertFalse(stats.is_near(tuple("chedy"), tuple("shody")))

    def test_substitution_leaves_fingerprint_unchanged(self):
        # The core argument against simple substitution: every measure is key-invariant.
        words = corpus.load_reference("Latin", 5000)
        letters = sorted({c for w in words for c in w})
        shuffled = letters[:]
        random.Random(3).shuffle(shuffled)
        key = dict(zip(letters, shuffled))
        enc = ["".join(key[c] for c in w) for w in words]
        a, b = stats.fingerprint(words), stats.fingerprint(enc)
        for k in ("h1", "h2", "zipf_slope", "vocab_density", "adjacent_near"):
            self.assertAlmostEqual(a[k], b[k], places=9)


class StructureTest(unittest.TestCase):
    def test_order_consistency_extremes(self):
        self.assertEqual(structure.order_consistency(["ab"] * 50), 1.0)
        self.assertAlmostEqual(structure.order_consistency(["ab", "ba"] * 50), 0.5)

    def test_permutation_detects_local_repetition(self):
        ws = []
        rng = random.Random(1)
        for _ in range(500):
            w = rng.choice(["chedy", "qokain", "daiin", "shol", "okar"])
            ws += [w, w]  # every word immediately repeated
        obs, null, p = structure.permutation_test(ws, structure.adjacent_repeat_rate, trials=50)
        self.assertGreater(obs, null)
        self.assertLess(p, 0.05)


class SelfCiteTest(unittest.TestCase):
    def test_generates_requested_size(self):
        seed = [[eva.glyphs(w) for w in "fachys ykal ar ataiin shol shory".split()]]
        lines = selfcite.generate(seed, 2000, [8, 9, 10], seed=4)
        n = sum(len(l) for l in lines)
        self.assertGreaterEqual(n, 2000)
        self.assertTrue(all(1 <= len(w) <= 8 for l in lines[1:] for w in l))


class CipherTest(unittest.TestCase):
    def test_solver_breaks_latin_substitution(self):
        ref = corpus.load_reference("Latin")
        model = cipher.TrigramModel(ref[20000:])
        enc, truth = cipher.random_substitution(ref[:3000], seed=5)
        sol = cipher.solve(enc, model, restarts=2, steps=8000)
        self.assertGreater(cipher.accuracy(sol, enc, truth), 0.95)


if __name__ == "__main__":
    unittest.main()
