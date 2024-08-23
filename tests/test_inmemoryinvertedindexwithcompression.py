# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=protected-access

import unittest
import tracemalloc
import inspect
from test_inmemoryinvertedindexwithoutcompression import TestInMemoryInvertedIndexWithoutCompression
from context import in3120


class TestInMemoryInvertedIndexWithCompression(unittest.TestCase):

    def setUp(self):
        self._tester = TestInMemoryInvertedIndexWithoutCompression()
        self._tester.setUp()
        self._tester._compressed = True  # Enable compression!

    def test_access_postings(self):
        self._tester.test_access_postings()

    def test_access_vocabulary(self):
        self._tester.test_access_vocabulary()

    def test_mesh_corpus(self):
        self._tester.test_mesh_corpus()

    def test_multiple_fields(self):
        self._tester.test_multiple_fields()

    def test_memory_usage(self):
        corpus = in3120.InMemoryCorpus("../data/cran.xml")
        tracemalloc.start()
        snapshot_baseline = tracemalloc.take_snapshot()
        index_uncompressed = in3120.InMemoryInvertedIndex(corpus, ["body"], self._tester._normalizer, self._tester._tokenizer, False)
        self.assertIsNotNone(index_uncompressed)
        snapshot_uncompressed = tracemalloc.take_snapshot()
        index_compressed = in3120.InMemoryInvertedIndex(corpus, ["body"], self._tester._normalizer, self._tester._tokenizer, True)
        self.assertIsNotNone(index_compressed)
        snapshot_compressed = tracemalloc.take_snapshot()
        tracemalloc.stop()
        for statistic in snapshot_uncompressed.compare_to(snapshot_baseline, "filename"):
            if statistic.traceback[0].filename == inspect.getfile(in3120.InMemoryInvertedIndex):
                size_uncompressed = statistic.size_diff
        for statistic in snapshot_compressed.compare_to(snapshot_uncompressed, "filename"):
            if statistic.traceback[0].filename == inspect.getfile(in3120.InMemoryInvertedIndex):
                size_compressed = statistic.size_diff
        compression_ratio = size_uncompressed / size_compressed
        self.assertGreater(compression_ratio, 13)


if __name__ == '__main__':
    unittest.main(verbosity=2)
