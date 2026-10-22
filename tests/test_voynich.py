import random
import unittest

from voynich import cipher, corpus, eva, ivtff, latin, selfcite, stats, structure, syllabic


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


class LatinTest(unittest.TestCase):
    def test_syllabify(self):
        self.assertEqual(latin.syllabify("principio"), ["prin", "ci", "pi", "o"])
        self.assertEqual(latin.syllabify("consequuntur"), ["con", "se", "quun", "tur"])
        self.assertEqual(latin.syllabify("creavit"), ["cre", "a", "vit"])
        self.assertEqual(latin.syllabify("aquae"), ["a", "quae"])

    def test_normalize_merges_u_v(self):
        self.assertEqual(latin.normalize(["Vivere", "Jesu"]), ["uiuere", "iesu"])
        self.assertEqual(latin.normalize(["Vivere"], merge_uv=False), ["vivere"])

    def test_abbreviate(self):
        self.assertEqual(latin.abbreviate("et"), "⁊")
        self.assertEqual(latin.abbreviate("dominus"), "dominꝰ")
        self.assertEqual(latin.abbreviate("herbarum"), "herbaꝝ")
        self.assertEqual(latin.abbreviate("consequuntur"), "ꝯsequūtᷣ")


class SyllabicTest(unittest.TestCase):
    def test_word_cipher_cannot_hide_repetition(self):
        # A deterministic word-for-word code keeps every repeat and can only merge types.
        raw = corpus.load_medieval("Kempis", 4000, merge_uv=False)
        glyph_words = [eva.glyphs(w) for w in corpus.tokens(corpus.load_voynich())[:5000]]
        enc = syllabic.SyllableCipher(raw, glyph_words).encode(raw)
        plain, coded = syllabic.repeat_profile(raw), syllabic.repeat_profile(enc)
        self.assertLessEqual(coded["types"], plain["types"])
        self.assertGreaterEqual(coded["adjacent_repeat"], plain["adjacent_repeat"])

    def test_split_onset_nucleus_coda(self):
        self.assertEqual(syllabic.split_onc(list("prin"), syllabic._latin_vowel), (("p", "r"), ("i",), ("n",)))
        self.assertEqual(syllabic.split_onc(["q", "o", "k", "e", "e", "d", "y"], syllabic._voynich_vowel),
                         (("q",), ("o",), ("k", "e", "e", "d", "y")))


class GeneratorModelTest(unittest.TestCase):
    def test_edit_extraction(self):
        op = selfcite.EditModel._op(("ch", "e", "d", "y"), ("sh", "e", "d", "y"))
        self.assertEqual(op, ("sub", "^", "ch", "sh", "e"))
        self.assertEqual(selfcite.EditModel._op(("o", "k", "y"), ("q", "o", "k", "y")), ("ins", "^", "", "q", "o"))

    def test_edit_model_makes_single_edits(self):
        words = [eva.glyphs(w) for w in corpus.tokens(corpus.load_voynich())[:6000]]
        model = selfcite.EditModel(words)
        rng = random.Random(2)
        for w in words[:200]:
            out = tuple(model.apply(w, rng))
            self.assertTrue(out == tuple(w) or stats.is_near(tuple(w), out))

    def test_word_grammar_prefers_real_shapes(self):
        words = [eva.glyphs(w) for w in corpus.tokens(corpus.load_voynich())]
        g = selfcite.WordGrammar(words)
        self.assertGreater(g.per_glyph(eva.glyphs("qokedy")), g.per_glyph(eva.glyphs("yqekdo")))


class CipherTest(unittest.TestCase):
    def test_solver_breaks_latin_substitution(self):
        ref = corpus.load_reference("Latin")
        model = cipher.TrigramModel(ref[20000:])
        enc, truth = cipher.random_substitution(ref[:3000], seed=5)
        sol = cipher.solve(enc, model, restarts=2, steps=8000)
        self.assertGreater(cipher.accuracy(sol, enc, truth), 0.95)


if __name__ == "__main__":
    unittest.main()


class HoaxTest(unittest.TestCase):
    def test_scribe_rules_and_v5_generator(self):
        import random
        from voynich import corpus, eva, hoax, selfcite
        lines = [[eva.glyphs(w) for w in l.words] for l in corpus.load_voynich() if l.kind.startswith("P")][:900]
        words = [w for l in lines for w in l]
        rules = selfcite.ScribeRules(lines)
        self.assertLess(rules.last_mid["m"], 0.6)            # 'm' belongs at line ends
        self.assertGreater(rules.last["m"], 2.0)
        grammar = selfcite.WordGrammar(words)
        new = selfcite.sample_word(grammar, random.Random(1))
        self.assertTrue(all(isinstance(g, str) for g in new))
        gen = selfcite.generate_v5(lines[:3], 5000, [len(l) for l in lines], rules, selfcite.EditModel(words),
                                   grammar, seed=2, p_new=0.2, p_hot=0.1)
        self.assertGreaterEqual(sum(len(l) for l in gen), 5000)
        m = hoax.measure(hoax.blocks(gen)[0])
        self.assertEqual(set(m), set(hoax.MEASURES))

