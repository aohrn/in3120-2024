# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from context import in3120


class TestBetterRanker(unittest.TestCase):

    def setUp(self):
        normalizer = in3120.SimpleNormalizer()
        tokenizer = in3120.SimpleTokenizer()
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(0, {"title": "the foo", "static_quality_score": 0.9}))
        corpus.add_document(in3120.InMemoryDocument(1, {"title": "the foo", "static_quality_score": 0.2}))
        corpus.add_document(in3120.InMemoryDocument(2, {"title": "the foo foo", "static_quality_score": 0.2}))
        corpus.add_document(in3120.InMemoryDocument(3, {"title": "the bar"}))
        corpus.add_document(in3120.InMemoryDocument(4, {"title": "the bar bar"}))
        corpus.add_document(in3120.InMemoryDocument(5, {"title": "the baz"}))
        corpus.add_document(in3120.InMemoryDocument(6, {"title": "the baz"}))
        corpus.add_document(in3120.InMemoryDocument(7, {"title": "the baz baz"}))
        index = in3120.InMemoryInvertedIndex(corpus, ["title"], normalizer, tokenizer)
        self.__ranker = in3120.BetterRanker(corpus, index)

    def test_term_frequency(self):
        self.__ranker.reset(1)
        self.__ranker.update("foo", 1, in3120.Posting(1, 1))
        score1 = self.__ranker.evaluate()
        self.__ranker.reset(2)
        self.__ranker.update("foo", 1, in3120.Posting(2, 2))
        score2 = self.__ranker.evaluate()
        self.assertGreater(score1, 0.0)
        self.assertGreater(score2, 0.0)
        self.assertGreater(score2, score1)

    def test_document_id_mismatch(self):
        self.__ranker.reset(21)
        with self.assertRaises(AssertionError):
            self.__ranker.update("foo", 1, in3120.Posting(42, 4))

    def test_inverse_document_frequency(self):
        self.__ranker.reset(3)
        self.__ranker.update("the", 1, in3120.Posting(3, 1))
        self.assertAlmostEqual(self.__ranker.evaluate(), 0.0, 8)
        self.__ranker.reset(3)
        self.__ranker.update("bar", 1, in3120.Posting(3, 1))
        score1 = self.__ranker.evaluate()
        self.__ranker.reset(5)
        self.__ranker.update("baz", 1, in3120.Posting(5, 1))
        score2 = self.__ranker.evaluate()
        self.assertGreater(score1, 0.0)
        self.assertGreater(score2, 0.0)
        self.assertGreater(score1, score2)

    def test_static_quality_score(self):
        self.__ranker.reset(0)
        self.__ranker.update("foo", 1, in3120.Posting(0, 1))
        score1 = self.__ranker.evaluate()
        self.__ranker.reset(1)
        self.__ranker.update("foo", 1, in3120.Posting(1, 1))
        score2 = self.__ranker.evaluate()
        self.assertGreater(score1, 0.0)
        self.assertGreater(score2, 0.0)
        self.assertGreater(score1, score2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
