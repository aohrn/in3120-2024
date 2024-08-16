# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from context import in3120


class TestNearestNeighborClassifier(unittest.TestCase):

    def setUp(self):
        normalizer = in3120.SimpleNormalizer()
        tokenizer = in3120.SimpleTokenizer()
        movies = in3120.InMemoryCorpus("../data/imdb.csv")
        fields = ["title", "description"]
        training_set = movies.split("genre", lambda v: v.split(","))
        self._classifier = in3120.NearestNeighborClassifier(training_set, fields, normalizer, tokenizer)

    def test_predict_movie_genre(self):
        results = list(self._classifier.classify("It was a dark and stormy night", {}))
        self.assertEqual("Thriller", results[0]["category"])

    def test_scores_are_sorted_descending(self):
        for voting in ("simple", "weighted"):
            options = {"voting": voting}
            results = list(self._classifier.classify("It was a dark and stormy night", options))
            scores = [result["score"] for result in results]
            self.assertEqual(5, len(scores))
            self.assertListEqual(scores, sorted(scores, reverse=True))

    def test_barfs_on_invalid_options(self):
        with self.assertRaises(AssertionError):
            list(self._classifier.classify("It was a dark and stormy night", {"voting": "dfdsf"}))


if __name__ == '__main__':
    unittest.main(verbosity=2)
