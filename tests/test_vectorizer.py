# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
import math
from context import in3120


class TestVectorizer(unittest.TestCase):

    def setUp(self):
        self._normalizer = in3120.SimpleNormalizer()
        self._tokenizer = in3120.SimpleTokenizer()
        self._corpus = in3120.InMemoryCorpus("../data/en.txt")
        self._fields = ["title", "body"]
        self._inverted_index = in3120.DummyInMemoryInvertedIndex(self._corpus, self._fields, self._normalizer, self._tokenizer)
        self._document = self._corpus[171]  # "A date for that hearing has not yet been set."
        self._stopwords = in3120.Trie()
        self._stopwords.add(["the", "of", "in"], self._normalizer, self._tokenizer)
        self._vectorizer = in3120.Vectorizer(self._corpus, self._inverted_index, self._stopwords)

    def test_from_buffers(self):
        buffer1 = "Who played the role of the JUGGERNAUT in Asia?"
        buffer2 = "gfasdsdfsdsdf fdsfwecszaxre"
        result = self._vectorizer.from_buffers([buffer1, buffer2])
        self.assertEqual(5, len(result))
        self.assertTrue("juggernaut" in result)
        self.assertTrue("asia" in result)
        self.assertTrue("fdsfwecszaxre" not in result)
        self.assertTrue("the" not in result)

    def test_from_document(self):
        result = self._vectorizer.from_document(self._document, ["nbfgffsdf", "body"])
        first = result.top(1)[0]
        self.assertEqual("hearing", first[0])
        tf = 1 + math.log10(1)  # The term 'hearing' appears once in this docment.
        idf = math.log10(self._corpus.size() / 23)  # The term 'hearing' appears in 23 documents in the corpus.
        self.assertAlmostEqual(tf * idf, first[1], 6)


if __name__ == '__main__':
    unittest.main(verbosity=2)
