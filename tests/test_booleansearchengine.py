# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from typing import List, Dict, Any
from context import in3120


class TestBooleanSearchEngine(unittest.TestCase):

    def setUp(self):
        normalizer = in3120.SimpleNormalizer()
        tokenizer = in3120.SimpleTokenizer()
        self._corpus = in3120.InMemoryCorpus("../data/names.txt")
        self._index = in3120.InMemoryInvertedIndex(self._corpus, ["body"], normalizer, tokenizer)
        self._engine = in3120.BooleanSearchEngine(self._corpus, self._index)

    def _verify_error(self, expression: str, message: str, options: Dict[str, Any]):
        results = list(self._engine.evaluate(expression, options))
        self.assertEqual(1, len(results))
        self.assertTrue("error" in results[0])
        self.assertEqual(results[0]["error"], message)

    def test_malformed_queries(self):
        for optimize in (True, False):
            options = {"optimize": optimize}
            self._verify_error("AND('foo', OR())", "Operator OR expects at least one argument.", options)
            self._verify_error("OR('foo', AND())", "Operator AND expects at least one argument.", options)
            self._verify_error("ANDNOT('foo')", "Operator ANDNOT expects exactly two arguments.", options)
            self._verify_error("ANDNOT('foo', 'bar', 'baz')", "Operator ANDNOT expects exactly two arguments.", options)
            self._verify_error("OR('foo', 'bar'))", "Syntax error, unmatched ')'.", options)
            self._verify_error("FOO('foo', 'bar')", "Unsupported operator FOO.", options)
            self._verify_error("foo bar", "Syntax error, invalid syntax.", options)
            self._verify_error("", "Syntax error, invalid syntax.", options)
            self._verify_error("''", "Expected '' to contain at least one term.", options)

    def _verify_matches(self, expression: str, expected: List[int], options: Dict[str, Any]):
        results = list(self._engine.evaluate(expression, options))
        self.assertEqual(len(expected), len(results))
        self.assertListEqual(expected, [m["document"].document_id for m in results])

    def test_valid_expressions(self):
        for optimize in (True, False):
            options = {"optimize": optimize}
            self._verify_matches("AND('Mary', OR('brock', 'stewart'))", [7, 20], options)
            self._verify_matches("ANDNOT('mcdaniel', OR('jessica', 'fdsdfqeg'))", [1504, 2669, 3049], options)
            self._verify_matches("ANDNOT('mcdaniel', 'jessica fdsdfqeg')", [1504, 2669, 3049], options)
            self._verify_matches("ANDNOT('robert mcdaniel', 'jessica fdsdfqeg')", [2669], options)
            self._verify_matches("AND('tyler', saunders)", [1291], options)
            self._verify_matches("OR(AND(mary, smith), AND(OR(peter, xzyds), lee))", [849, 1356, 2452, 4543], options)
            self._verify_matches("AND('Ms. Shannon Rubio')", [2784], options)
            self._verify_matches('AND("Ms. Shannon Rubio")', [2784], options)
            self._verify_matches('"barbara barbara henson henson"', [940], options)
            self._verify_matches("Rubio", [2784], options)
            self._verify_matches("rubio", [2784], options)
            self._verify_matches('OR(AND("steven smith"), AND("smith paul"), AND("RUBEN SMITH"))', [4010, 4774, 4847], options)

    def test_optimization(self):
        for expression in ("AND('Ms. Shannon Rubio')", 'AND(OR("Ms. Malik"), OR("Shannon Malik"), OR("Rubio Malik"))'):
            counts = {}
            for optimize in (True, False):
                options = {"optimize": optimize}
                index = in3120.AccessLoggedInvertedIndex(self._index)
                engine = in3120.BooleanSearchEngine(self._corpus, index)
                results = list(engine.evaluate(expression, options))
                counts[optimize] = len(index.get_history())
            self.assertGreater(counts[False], counts[True])


if __name__ == '__main__':
    unittest.main(verbosity=2)
