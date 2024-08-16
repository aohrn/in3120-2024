# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
import math
import types
from context import in3120


class TestNaiveBayesClassifier(unittest.TestCase):

    def setUp(self):
        self.__normalizer = in3120.SimpleNormalizer()
        self.__tokenizer = in3120.SimpleTokenizer()
        self.__shingler = in3120.ShingleGenerator(3)

    def test_china_example_from_textbook(self):
        # Specifically, see Example 13.1 here: https://nlp.stanford.edu/IR-book/pdf/13bayes.pdf
        china = in3120.InMemoryCorpus()
        china.add_document(in3120.InMemoryDocument(0, {"body": "Chinese Beijing Chinese"}))
        china.add_document(in3120.InMemoryDocument(1, {"body": "Chinese Chinese Shanghai"}))
        china.add_document(in3120.InMemoryDocument(2, {"body": "Chinese Macao"}))
        not_china = in3120.InMemoryCorpus()
        not_china.add_document(in3120.InMemoryDocument(0, {"body": "Tokyo Japan Chinese"}))
        training_set = {"china": china, "not china": not_china}
        classifier = in3120.NaiveBayesClassifier(training_set, ["body"], self.__normalizer, self.__tokenizer)
        self.assertAlmostEqual(classifier.get_prior("china"), math.log(3 / 4), 6)
        self.assertAlmostEqual(classifier.get_prior("not china"), math.log(1 / 4), 6)
        self.assertAlmostEqual(classifier.get_posterior("china", "chinese"), math.log(3 / 7), 6)
        self.assertAlmostEqual(classifier.get_posterior("china", "tokyo"), math.log(1 / 14), 6)
        self.assertAlmostEqual(classifier.get_posterior("china", "japan"), math.log(1 / 14), 6)
        self.assertAlmostEqual(classifier.get_posterior("not china", "chinese"), math.log(2 / 9), 6)
        self.assertAlmostEqual(classifier.get_posterior("not china", "tokyo"), math.log(2 / 9), 6)
        self.assertAlmostEqual(classifier.get_posterior("not china", "japan"), math.log(2 / 9), 6)
        results = list(classifier.classify("Chinese Chinese Chinese Tokyo Japan"))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["category"], "china")
        self.assertAlmostEqual(math.exp(results[0]["score"]), 0.0003, 4)
        self.assertEqual(results[1]["category"], "not china")
        self.assertAlmostEqual(math.exp(results[1]["score"]), 0.0001, 4)

    def __classify_buffer_and_verify_top_categories(self, buffer, classifier, categories):
        results = list(classifier.classify(buffer))
        self.assertListEqual([results[i]["category"] for i in range(len(categories))], categories)

    def test_language_detection_trained_on_some_news_corpora(self):
        training_set = {language: in3120.InMemoryCorpus(f"../data/{language}.txt") for language in ["en", "no", "da", "de"]}
        classifier = in3120.NaiveBayesClassifier(training_set, ["body"], self.__normalizer, self.__tokenizer)
        self.__classify_buffer_and_verify_top_categories("Vil det riktige språket identifiseres? Dette er bokmål.", classifier, ["no"])
        self.__classify_buffer_and_verify_top_categories("I don't believe that the number of tokens exceeds a billion.", classifier, ["en"])
        self.__classify_buffer_and_verify_top_categories("De danske drenge drikker snaps!", classifier, ["da"])
        self.__classify_buffer_and_verify_top_categories("Der Kriminalpolizei! Haben sie angst?", classifier, ["de"])

    def test_predict_movie_genre_from_movie_title(self):
        movies = in3120.InMemoryCorpus("../data/imdb.csv")
        training_set = movies.split("genre", lambda v: v.split(","))
        classifier = in3120.NaiveBayesClassifier(training_set, ["title"], self.__normalizer, self.__shingler)
        self.__classify_buffer_and_verify_top_categories("friday the 13th 1408 crawlspace", classifier, ["Horror"])
        self.__classify_buffer_and_verify_top_categories("kung fu sausage panda university", classifier, ["Animation"])

    def test_predict_name_of_search_engine_from_description(self):
        engines = in3120.InMemoryCorpus("../data/docs.json")
        training_set = engines.split("title")
        classifier = in3120.NaiveBayesClassifier(training_set, ["body"], self.__normalizer, self.__shingler)
        self.__classify_buffer_and_verify_top_categories("duckie duckie privacy", classifier, ["Duck Duck Go"])
        self.__classify_buffer_and_verify_top_categories("jeeeeeves webb", classifier, ["Ask"])

    def test_scores_are_sorted_descending(self):
        engines = in3120.InMemoryCorpus("../data/docs.json")
        training_set = engines.split("title")
        classifier = in3120.NaiveBayesClassifier(training_set, ["body"], self.__normalizer, self.__shingler)
        results = list(classifier.classify("search"))
        scores = [result["score"] for result in results]
        self.assertListEqual(scores, sorted(scores, reverse=True))

    def test_uses_yield(self):
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(0, {"a": "the foo bar"}))
        training_set = {c: corpus for c in ["x", "y"]}
        classifier = in3120.NaiveBayesClassifier(training_set, ["a"], self.__normalizer, self.__tokenizer)
        matches = classifier.classify("urg foo the gog")
        self.assertIsInstance(matches, types.GeneratorType, "Are you using yield?")


if __name__ == '__main__':
    unittest.main(verbosity=2)
