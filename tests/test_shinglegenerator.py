# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=protected-access

import unittest
import types
from test_simplesearchengine import TestSimpleSearchEngine
from context import in3120


class TestShingleGenerator(unittest.TestCase):

    def setUp(self):
        self.__tokenizer = in3120.ShingleGenerator(3)

    def test_strings(self):
        self.assertListEqual(list(self.__tokenizer.strings("")), [])
        self.assertListEqual(list(self.__tokenizer.strings("b")), ["b"])
        self.assertListEqual(list(self.__tokenizer.strings("ba")), ["ba"])
        self.assertListEqual(list(self.__tokenizer.strings("ban")), ["ban"])
        self.assertListEqual(list(self.__tokenizer.strings("bana")), ["ban", "ana"])
        self.assertListEqual(list(self.__tokenizer.strings("banan")), ["ban", "ana", "nan"])
        self.assertListEqual(list(self.__tokenizer.strings("banana")), ["ban", "ana", "nan", "ana"])

    def test_tokens(self):
        self.assertListEqual(list(self.__tokenizer.tokens("ba")), [("ba", (0, 2))])
        self.assertListEqual(list(self.__tokenizer.tokens("banan")),
                             [("ban", (0, 3)), ("ana", (1, 4)), ("nan", (2, 5))])

    def test_spans(self):
        self.assertListEqual(list(self.__tokenizer.spans("ba")), [(0, 2)])
        self.assertListEqual(list(self.__tokenizer.spans("banan")), [(0, 3), (1, 4), (2, 5)])

    def test_uses_yield(self):
        for i in range(0, 5):
            text = "x" * i
            self.assertIsInstance(self.__tokenizer.spans(text), types.GeneratorType)
            self.assertIsInstance(self.__tokenizer.tokens(text), types.GeneratorType)
            self.assertIsInstance(self.__tokenizer.strings(text), types.GeneratorType)

    def test_shingled_mesh_corpus(self):
        normalizer = in3120.SimpleNormalizer()
        corpus = in3120.InMemoryCorpus("../data/mesh.txt")
        index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, self.__tokenizer)
        engine = in3120.SimpleSearchEngine(corpus, index)
        tester = TestSimpleSearchEngine()
        tester._process_query_verify_matches("orGAnik kEMmistry", engine,
                                             {"match_threshold": 0.1, "hit_count": 10},
                                             (10, 8.0, [4408, 4410, 4411, 16980, 16981]))
        tester._process_query_verify_matches("synndrome", engine,
                                             {"match_threshold": 0.1, "hit_count": 10},
                                             (10, 7.0, [1275]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
