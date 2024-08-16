# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=protected-access

import unittest
from test_inmemorypostinglist import TestInMemoryPostingList
from test_postingsmerger import TestPostingsMerger
from context import in3120


class TestCompressedInMemoryPostingList(unittest.TestCase):

    def setUp(self):
        self._tester1 = TestInMemoryPostingList()
        self._tester1.setUp()
        self._tester2 = TestPostingsMerger()
        self._tester2.setUp()

    def test_append_and_iterate(self):
        self._tester1._test_append_and_iterate(in3120.CompressedInMemoryPostingList())

    def test_invalid_append(self):
        self._tester1._test_invalid_append(in3120.CompressedInMemoryPostingList())

    def test_mesh_corpus(self):
        self._tester2._test_mesh_corpus(True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
