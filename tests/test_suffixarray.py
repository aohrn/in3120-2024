# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
import tracemalloc
import inspect
import types
from context import in3120


class TestSuffixArray(unittest.TestCase):

    def setUp(self):
        self.__normalizer = in3120.SimpleNormalizer()
        self.__tokenizer = in3120.SimpleTokenizer()

    def __process_query_and_verify_winner(self, engine, query, winners, score):
        options = {"debug": False, "hit_count": 5}
        matches = list(engine.evaluate(query, options))
        if winners:
            self.assertGreaterEqual(len(matches), 1)
            self.assertLessEqual(len(matches), 5)
            self.assertIn(matches[0]["document"].document_id, winners)
            if score:
                self.assertEqual(matches[0]["score"], score)
        else:
            self.assertEqual(len(matches), 0)

    def test_canonicalized_corpus(self):
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(corpus.size(), {"a": "Japanese リンク"}))
        corpus.add_document(in3120.InMemoryDocument(corpus.size(), {"a": "Cedilla \u0043\u0327 and \u00C7 foo"}))
        engine = in3120.SuffixArray(corpus, ["a"], self.__normalizer, self.__tokenizer)
        self.__process_query_and_verify_winner(engine, "ﾘﾝｸ", [0], 1)  # Should match "リンク".
        self.__process_query_and_verify_winner(engine, "\u00C7", [1], 2)  # Should match "\u0043\u0327".

    def test_cran_corpus(self):
        corpus = in3120.InMemoryCorpus("../data/cran.xml")
        engine = in3120.SuffixArray(corpus, ["body"], self.__normalizer, self.__tokenizer)
        self.__process_query_and_verify_winner(engine, "visc", [328], 11)
        self.__process_query_and_verify_winner(engine, "Of  A", [946], 10)
        self.__process_query_and_verify_winner(engine, "", [], None)
        self.__process_query_and_verify_winner(engine, "approximate solution", [159, 1374], 3)

    def test_memory_usage(self):
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(0, {"a": "o  o\n\n\no\n\no", "b": "o o\no   \no"}))
        corpus.add_document(in3120.InMemoryDocument(1, {"a": "ba", "b": "b bab"}))
        corpus.add_document(in3120.InMemoryDocument(2, {"a": "o  o O o", "b": "o o"}))
        corpus.add_document(in3120.InMemoryDocument(3, {"a": "oO" * 10000, "b": "o"}))
        corpus.add_document(in3120.InMemoryDocument(4, {"a": "cbab o obab O ", "b": "o o " * 10000}))
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()
        engine = in3120.SuffixArray(corpus, ["a", "b"], self.__normalizer, self.__tokenizer)
        self.assertIsNotNone(engine)
        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()
        for statistic in snapshot2.compare_to(snapshot1, "filename"):
            if statistic.traceback[0].filename == inspect.getfile(in3120.SuffixArray):
                self.assertLessEqual(statistic.size_diff, 2000000, "Memory usage seems excessive.")

    def test_multiple_fields(self):
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(0, {"field1": "a b c", "field2": "b c d"}))
        corpus.add_document(in3120.InMemoryDocument(1, {"field1": "x", "field2": "y"}))
        corpus.add_document(in3120.InMemoryDocument(2, {"field1": "y", "field2": "z"}))
        engine0 = in3120.SuffixArray(corpus, ["field1", "field2"], self.__normalizer, self.__tokenizer)
        engine1 = in3120.SuffixArray(corpus, ["field1"], self.__normalizer, self.__tokenizer)
        engine2 = in3120.SuffixArray(corpus, ["field2"], self.__normalizer, self.__tokenizer)
        self.__process_query_and_verify_winner(engine0, "b c", [0], 2)
        self.__process_query_and_verify_winner(engine0, "y", [1, 2], 1)
        self.__process_query_and_verify_winner(engine1, "x", [1], 1)
        self.__process_query_and_verify_winner(engine1, "y", [2], 1)
        self.__process_query_and_verify_winner(engine1, "z", [], None)
        self.__process_query_and_verify_winner(engine2, "z", [2], 1)

    def test_uses_yield(self):
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(0, {"a": "the foo bar"}))
        engine = in3120.SuffixArray(corpus, ["a"], self.__normalizer, self.__tokenizer)
        matches = engine.evaluate("foo", {})
        self.assertIsInstance(matches, types.GeneratorType, "Are you using yield?")


if __name__ == '__main__':
    unittest.main(verbosity=2)
