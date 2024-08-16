# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
import types
from context import in3120


class TestPostingsMerger(unittest.TestCase):

    def setUp(self):
        self._merger = in3120.PostingsMerger()

    def test_empty_lists(self):
        posting = in3120.Posting(123, 4)
        self.assertListEqual(list(self._merger.intersection(iter([]), iter([]))), [])
        self.assertListEqual(list(self._merger.intersection(iter([]), iter([posting]))), [])
        self.assertListEqual(list(self._merger.intersection(iter([posting]), iter([]))), [])
        self.assertListEqual(list(self._merger.union(iter([]), iter([]))), [])
        self.assertListEqual(list(self._merger.difference(iter([]), iter([]))), [])
        self.assertListEqual([p.document_id for p in self._merger.union(iter([]), iter([posting]))],
                             [posting.document_id])
        self.assertListEqual([p.document_id for p in self._merger.union(iter([posting]), iter([]))],
                             [posting.document_id])
        self.assertListEqual([p.document_id for p in self._merger.difference(iter([posting]), iter([]))],
                             [posting.document_id])
        self.assertListEqual([p.document_id for p in self._merger.difference(iter([]), iter([posting]))],
                             [])

    def test_order_independence(self):
        postings1 = [in3120.Posting(1, 0), in3120.Posting(2, 0), in3120.Posting(3, 0)]
        postings2 = [in3120.Posting(2, 0), in3120.Posting(3, 0), in3120.Posting(6, 0)]
        result12 = list(map(lambda p: p.document_id, self._merger.intersection(iter(postings1), iter(postings2))))
        result21 = list(map(lambda p: p.document_id, self._merger.intersection(iter(postings2), iter(postings1))))
        self.assertListEqual(result12, [2, 3])
        self.assertListEqual(result12, result21)
        result12 = list(map(lambda p: p.document_id, self._merger.union(iter(postings1), iter(postings2))))
        result21 = list(map(lambda p: p.document_id, self._merger.union(iter(postings2), iter(postings1))))
        self.assertListEqual(result12, [1, 2, 3, 6])
        self.assertListEqual(result12, result21)

    def test_order_dependence(self):
        postings1 = [in3120.Posting(1, 0), in3120.Posting(2, 0), in3120.Posting(3, 0), in3120.Posting(9, 0)]
        postings2 = [in3120.Posting(2, 0), in3120.Posting(3, 0), in3120.Posting(6, 0), in3120.Posting(8, 0)]
        result12 = list(map(lambda p: p.document_id, self._merger.difference(iter(postings1), iter(postings2))))
        result21 = list(map(lambda p: p.document_id, self._merger.difference(iter(postings2), iter(postings1))))
        self.assertListEqual(result12, [1, 9])
        self.assertListEqual(result21, [6, 8])

    def test_ends_with_same_so_tail_is_empty(self):
        postings1 = [in3120.Posting(1, 0), in3120.Posting(2, 0), in3120.Posting(6, 0)]
        postings2 = [in3120.Posting(2, 0), in3120.Posting(3, 0), in3120.Posting(6, 0)]
        result1 = list(map(lambda p: p.document_id, self._merger.intersection(iter(postings1), iter(postings2))))
        result2 = list(map(lambda p: p.document_id, self._merger.union(iter(postings1), iter(postings2))))
        self.assertListEqual(result1, [2, 6])
        self.assertListEqual(result2, [1, 2, 3, 6])

    def test_uses_yield(self):
        postings1 = [in3120.Posting(1, 0), in3120.Posting(2, 0), in3120.Posting(3, 0)]
        postings2 = [in3120.Posting(2, 0), in3120.Posting(3, 0), in3120.Posting(6, 0)]
        result1 = self._merger.intersection(iter(postings1), iter(postings2))
        result2 = self._merger.union(iter(postings1), iter(postings2))
        result3 = self._merger.difference(iter(postings1), iter(postings2))
        for result in (result1, result2, result3):
            self.assertIsInstance(result, types.GeneratorType, "Are you using yield?")

    def _process_query_with_two_terms(self, corpus, index, query, operator, expected):
        terms = list(index.get_terms(query))
        postings = [index[terms[i]] for i in range(len(terms))]
        self.assertEqual(len(postings), 2)
        merged = operator(postings[0], postings[1])
        documents = [corpus[posting.document_id] for posting in merged]
        self.assertEqual(len(documents), len(expected))
        self.assertListEqual([d.document_id for d in documents], expected)

    def _test_mesh_corpus(self, compressed: bool):
        normalizer = in3120.SimpleNormalizer()
        tokenizer = in3120.SimpleTokenizer()
        corpus = in3120.InMemoryCorpus("../data/mesh.txt")
        index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer, compressed)
        self._process_query_with_two_terms(corpus, index, "HIV  pROtein", self._merger.intersection,
                                           [11316, 11319, 11320, 11321])
        self._process_query_with_two_terms(corpus, index, "water Toxic", self._merger.union,
                                           [3078, 8138, 8635, 9379, 14472, 18572, 23234, 23985] +
                                           list(range(25265, 25282)))

    def test_uncompressed_mesh_corpus(self):
        self._test_mesh_corpus(False)


if __name__ == '__main__':
    unittest.main(verbosity=2)
