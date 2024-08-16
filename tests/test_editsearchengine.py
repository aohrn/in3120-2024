# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from context import in3120


class TestEditSearchEngine(unittest.TestCase):

    def setUp(self):
        normalizer = in3120.SimpleNormalizer()
        tokenizer = in3120.SimpleTokenizer()
        trie = in3120.Trie()
        trie.add2([("aleksander", "rednaskela")], normalizer, tokenizer)
        trie.add(["abba", "ørret", "abbor"], normalizer, tokenizer)
        trie.add(["alleksander", "allekander", "aleksanderrrr"], normalizer, tokenizer)
        self._engine = in3120.EditSearchEngine(trie, normalizer, tokenizer)

    def test_exact_match(self):
        options = {"upper_bound": 0}
        results = list(self._engine.evaluate("aleksander", options))
        self.assertEqual(1, len(results))
        self.assertEqual(4, len(results[0]))
        self.assertTrue("score" in results[0])
        self.assertTrue("distance" in results[0])
        self.assertTrue("match" in results[0])
        self.assertTrue("meta" in results[0])
        self.assertEqual("aleksander", results[0]["match"])
        self.assertEqual("rednaskela", results[0]["meta"])
        self.assertEqual(0, results[0]["distance"])
        self.assertAlmostEqual(1.0, results[0]["score"], 5)

    def test_normalization_and_whitespace(self):
        options = {"upper_bound": 0}
        results = list(self._engine.evaluate("  ALEKSANdER ", options))
        self.assertEqual(1, len(results))
        self.assertEqual("aleksander", results[0]["match"])

    def test_scores_are_sorted(self):
        for scoring in ["negated", "normalized", "lopresti"]:
            options = {"upper_bound": 10, "scoring": scoring}
            results = list(self._engine.evaluate("aleksander", options))
            self.assertEqual(7, len(results))
            scores = [r["score"] for r in results]
            self.assertListEqual(scores, sorted(scores, reverse=True))

    def test_invalid_scoring_function(self):
        options = {"scoring": "fgdkjhdfhkjg"}
        with self.assertRaises(AssertionError):
            list(self._engine.evaluate("aleksander", options))

    def test_upper_bound(self):
        expected = [(1, 2), (2, 3), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 6), (9, 7)]
        for (k, hits) in expected:
            options = {"upper_bound": k}
            results = list(self._engine.evaluate("aleksander", options))
            self.assertEqual(hits, len(results))

    def test_hit_count(self):
        expected = [(0, 1), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 7)]
        for (requested, received) in expected:
            options = {"upper_bound": 10, "hit_count": requested}
            results = list(self._engine.evaluate("aleksander", options))
            self.assertEqual(received, len(results))

    def test_candidate_count(self):
        expected = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 7)]
        for (requested, received) in expected:
            options = {"upper_bound": 10, "hit_count": 10, "candidate_count": requested}
            results = list(self._engine.evaluate("aleksander", options))
            self.assertEqual(received, len(results))

    def test_first_n(self):
        expected = {
            "aleksander": [(-1, 7), (0, 7), (1, 6), (2, 4)],
            "øleksander": [(-1, 7), (0, 7), (1, 1), (2, 0)],
            "yleksander": [(-1, 7), (0, 7), (1, 0), (2, 0)],
        }
        for (query, expected2) in expected.items():
            for (n, received) in expected2:
                options = {"upper_bound": 10, "first_n": n}
                results = list(self._engine.evaluate(query, options))
                self.assertEqual(received, len(results))
                for result in results:
                    self.assertTrue(result["match"].startswith(query[:max(0, n)]))

if __name__ == '__main__':
    unittest.main(verbosity=2)
