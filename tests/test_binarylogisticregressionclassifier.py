# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=using-constant-test

import unittest
from context import in3120


class TestBinaryLogisticRegressionClassifier(unittest.TestCase):

    def setUp(self):
        # See Example 13.1 here: https://nlp.stanford.edu/IR-book/pdf/13bayes.pdf
        normalizer = in3120.SimpleNormalizer()
        tokenizer = in3120.SimpleTokenizer()
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(0, {"body": "Chinese Beijing Chinese", "is_china": "Yes"}))
        corpus.add_document(in3120.InMemoryDocument(1, {"body": "Chinese Chinese Shanghai", "is_china": "Yes"}))
        corpus.add_document(in3120.InMemoryDocument(2, {"body": "Chinese Macao", "is_china": "Yes"}))
        corpus.add_document(in3120.InMemoryDocument(3, {"body": "Tokyo Japan Chinese", "is_china": "No"}))
        self._fields = ["body"]
        inverted_index = in3120.DummyInMemoryInvertedIndex(corpus, self._fields, normalizer, tokenizer)
        self._training_set = corpus.split("is_china", lambda v: ["china"] if "Yes" in v else ["not china"])
        self._vectorizer = in3120.Vectorizer(corpus, inverted_index, in3120.Trie())

    def test_stopping_early_works_and_loss_decreases(self):
        epochs = []
        losses = []
        def monitor(epoch: int, loss: float) -> bool:
            epochs.append(epoch)
            losses.append(loss)
            return len(losses) < 78
        classifier = in3120.BinaryLogisticRegressionClassifier(self._vectorizer)
        classifier.train(self._training_set, self._fields, {"epochs": 314}, monitor)
        self.assertEqual(78, len(losses))
        self.assertTrue(all(epochs[i + 1] > epochs[i] for i in range(len(epochs) - 1)))
        # The loss typically decreases monotonically, but doesn't strictly have to: E.g., it depends
        # on the choice of learning rate, the data (the shape of the error surface), and initial conditions.
        # Testing that loss decreases monotonically will work in almost all cases, but could
        # in theory trigger an occasional spurious test failure. Testing that the last value is smaller
        # than the first value is a much less strict test, but less prone to spurious test failures.
        if False:
            self.assertTrue(all(losses[i + 1] < losses[i] for i in range(len(losses) - 1)))
        else:
            self.assertTrue(losses[-1] < losses[0])

    def _verify_result(self, classifier: in3120.BinaryLogisticRegressionClassifier, buffer: str, china: bool):
        expected = ["china", "not china"] if china else ["not china", "china"]
        results = list(classifier.classify(buffer))
        self.assertEqual(2, len(results))
        self.assertListEqual(expected, [results[0]["category"], results[1]["category"]])
        self.assertTrue(results[0]["score"] > results[1]["score"])
        self.assertAlmostEqual(1.0, results[0]["score"] + results[1]["score"], 6)

    def test_basic_training_and_classification_works(self):
        classifier = in3120.BinaryLogisticRegressionClassifier(self._vectorizer)
        classifier.train(self._training_set, self._fields, {"epochs": 100}, None)
        self._verify_result(classifier, "Beijing Shanghai", True)
        self._verify_result(classifier, "Osaka Tokyo", False)

    def test_training_barfs_on_tasks_with_more_than_two_classes(self):
        corpus = in3120.InMemoryCorpus()
        corpus.add_document(in3120.InMemoryDocument(0, {"body": "foo", "meta": "A"}))
        corpus.add_document(in3120.InMemoryDocument(1, {"body": "foo", "meta": "B"}))
        corpus.add_document(in3120.InMemoryDocument(2, {"body": "foo", "meta": "C"}))
        barf1 = corpus.split("meta", lambda v: ["X"])
        self.assertEqual(1, len(barf1))
        barf3 = corpus.split("meta", lambda v: [v])
        self.assertEqual(3, len(barf3))
        for training_set in (barf1, barf3):
            classifier = in3120.BinaryLogisticRegressionClassifier(self._vectorizer)
            with self.assertRaises(AssertionError):
                classifier.train(training_set, self._fields, {"epochs": 100}, None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
