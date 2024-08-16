# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from context import in3120


class TestInMemoryPostingList(unittest.TestCase):

    def _test_append_and_iterate(self, postings: in3120.PostingList):
        self.assertEqual(len(postings), 0)
        self.assertEqual(postings.get_length(), 0)
        postings.append_posting(in3120.Posting(21, 2))
        postings.append_posting(in3120.Posting(42, 1))
        postings.append_posting(in3120.Posting(70, 3))
        postings.finalize_postings()
        self.assertEqual(postings.get_length(), 3)
        iterator = iter(postings)
        posting = next(iterator, None)
        self.assertEqual(posting.document_id, 21)
        self.assertEqual(posting.term_frequency, 2)
        posting = next(iterator, None)
        self.assertEqual(posting.document_id, 42)
        self.assertEqual(posting.term_frequency, 1)
        posting = next(iterator, None)
        self.assertEqual(posting.document_id, 70)
        self.assertEqual(posting.term_frequency, 3)
        posting = next(iterator, None)
        self.assertIsNone(posting)
        entries = list(postings.get_iterator())
        self.assertEqual(len(entries), 3)
        self.assertEqual(entries[0].document_id, 21)
        self.assertEqual(entries[1].document_id, 42)
        self.assertEqual(entries[2].document_id, 70)
        self.assertEqual(entries[0].term_frequency, 2)
        self.assertEqual(entries[1].term_frequency, 1)
        self.assertEqual(entries[2].term_frequency, 3)

    def _test_invalid_append(self, postings: in3120.PostingList):
        postings.append_posting(in3120.Posting(21, 2))
        for i in range(0, 2):
            with self.assertRaises(AssertionError):
                postings.append_posting(in3120.Posting(21 - i, 2))

    def test_append_and_iterate(self):
        self._test_append_and_iterate(in3120.InMemoryPostingList())

    def test_invalid_append(self):
        self._test_invalid_append(in3120.InMemoryPostingList())


if __name__ == '__main__':
    unittest.main(verbosity=2)
