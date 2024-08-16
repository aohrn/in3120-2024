# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from typing import List, Dict, Any
from context import in3120


class TestExtendedBooleanSearchEngine(unittest.TestCase):

    def setUp(self):
        self._normalizer = in3120.SimpleNormalizer()
        self._tokenizer = in3120.SimpleTokenizer()
        self._corpus = in3120.InMemoryCorpus("../data/names.txt")
        self._index = in3120.InMemoryInvertedIndex(self._corpus, ["body"], self._normalizer, self._tokenizer)
        self._synonyms = in3120.Trie.from_strings2([("xxxYYYzzz", ["abcdefg", "brock"])], self._normalizer, self._tokenizer)
        self._engine = in3120.ExtendedBooleanSearchEngine(self._corpus, self._index, self._synonyms)

    def __verify_error(self, engine: in3120.ExtendedBooleanSearchEngine, expression: str, message: str, options: Dict[str, Any]):
        results = list(engine.evaluate(expression, options))
        self.assertEqual(1, len(results))
        self.assertTrue("error" in results[0])
        self.assertEqual(results[0]["error"], message)

    def _verify_error(self, expression: str, message: str, options: Dict[str, Any]):
        self.__verify_error(self._engine, expression, message, options)

    def test_malformed_queries(self):
        for optimize in (True, False):
            options = {"optimize": optimize}
            self._verify_error("LOOKSLIKE('brocck', 'abba')", "Operator LOOKSLIKE expects exactly one argument.", options)
            self._verify_error("LOOKSLIKE('brocck abba')", "Operator LOOKSLIKE expects a single-term argument, got ['brocck', 'abba'].", options)
            self._verify_error("LOOKSLIKE(OR('brocck', 'abba'))", "Operator LOOKSLIKE has an argument of an unexpected type.", options)

    def __verify_matches(self, engine: in3120.ExtendedBooleanSearchEngine, expression: str, expected: List[int], options: Dict[str, Any]):
        results = list(engine.evaluate(expression, options))
        self.assertEqual(len(expected), len(results))
        self.assertTrue(all(map(lambda r: "document" in r, results)))
        self.assertListEqual(expected, [m["document"].document_id for m in results])

    def _verify_matches(self, expression: str, expected: List[int], options: Dict[str, Any]):
        self.__verify_matches(self._engine, expression, expected, options)

    def test_valid_expressions(self):
        for optimize in (True, False):
            options = {"optimize": optimize}
            self._verify_matches("AND('Mary', LOOKSLIKE('Brocck'))", [20], options)
            self._verify_matches("AND('Mary', WILDCARD('bro*k'))", [20], options)
            self._verify_matches("AND('Mary', WILDCARD('brock'))", [20], options)
            self._verify_matches("AND('Mary', SYNONYM('XXXyyyZZZ'))", [20], options)
            self._verify_matches("AND(SYNONYM('Mary'), SYNONYM('XXXyyyZZZ'))", [20], options)
            self._verify_matches("AND(SOUNDSLIKE('Maery'), OR(SOUNDSLIKE('fdsfsdfsdfsdf'), SOUNDSLIKE('brockh')))", [20], options)

    def test_synonym_dictionary_missing_values(self):
        synonyms = in3120.Trie.from_strings(["a"], self._normalizer, self._tokenizer)
        with self.assertRaises(AssertionError) as exc:
            in3120.ExtendedBooleanSearchEngine(self._corpus, self._index, synonyms)
        self.assertEqual(str(exc.exception), "Key 'a' has no values.")

    def test_synonym_dictionary_values_not_list(self):
        synonyms = in3120.Trie.from_strings2([("a", "b")], self._normalizer, self._tokenizer)
        with self.assertRaises(AssertionError) as exc:
            in3120.ExtendedBooleanSearchEngine(self._corpus, self._index, synonyms)
        self.assertEqual(str(exc.exception), "Key 'a' has meta data that is not a list.")

    def test_synonym_dictionary_key_multiterm(self):
        synonyms = in3120.Trie.from_strings2([("a b", ["c"])], self._normalizer, self._tokenizer)
        with self.assertRaises(AssertionError) as exc:
            in3120.ExtendedBooleanSearchEngine(self._corpus, self._index, synonyms)
        self.assertEqual(str(exc.exception), "Key 'a b' maps to a sequence of index terms ['a', 'b'] instead of a single index term.")

    def test_synonym_dictionary_value_multiterm(self):
        synonyms = in3120.Trie.from_strings2([("a", ["c", "d e"])], self._normalizer, self._tokenizer)
        with self.assertRaises(AssertionError) as exc:
            in3120.ExtendedBooleanSearchEngine(self._corpus, self._index, synonyms)
        self.assertEqual(str(exc.exception), "At least one of the values for key 'a' maps to a sequence of index terms instead of a single index term.")

    def test_with_unsupported_tokenizer(self):
        for tokenizer in [in3120.ShingleGenerator(3)]:
            index = in3120.InMemoryInvertedIndex(self._corpus, ["body"], self._normalizer, tokenizer)
            synonyms = in3120.Trie.from_strings2([("xxxYYYzzz", ["abcdefg", "brock"])], self._normalizer, self._tokenizer)
            with self.assertRaises(AssertionError) as exc:
                in3120.ExtendedBooleanSearchEngine(self._corpus, index, synonyms)
            self.assertEqual(str(exc.exception), "Unsupported tokenization detected.")

    def test_with_unsupported_normalizer(self):
        for normalizer in [in3120.PorterNormalizer(), in3120.SoundexNormalizer()]:
            index = in3120.InMemoryInvertedIndex(self._corpus, ["body"], normalizer, self._tokenizer)
            synonyms = in3120.Trie.from_strings2([("xxxYYYzzz", ["abcdefg", "brock"])], self._normalizer, self._tokenizer)
            with self.assertRaises(AssertionError) as exc:
                in3120.ExtendedBooleanSearchEngine(self._corpus, index, synonyms)
            self.assertEqual(str(exc.exception), "Unsupported normalization detected.")


if __name__ == '__main__':
    unittest.main(verbosity=2)
