# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

import math
from collections import Counter
from typing import Any, Dict, Iterable, Iterator
from .dictionary import InMemoryDictionary
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .corpus import Corpus


class NaiveBayesClassifier:
    """
    Defines a multinomial naive Bayes text classifier. For a detailed primer, see
    https://nlp.stanford.edu/IR-book/html/htmledition/naive-bayes-text-classification-1.html.
    """

    def __init__(self, training_set: Dict[str, Corpus], fields: Iterable[str],
                 normalizer: Normalizer, tokenizer: Tokenizer):
        """
        Trains the classifier from the named fields in the documents in the
        given training set.
        """
        # Used for breaking the text up into discrete classification features.
        self.__normalizer = normalizer
        self.__tokenizer = tokenizer

        # The vocabulary we've seen during training.
        self.__vocabulary = InMemoryDictionary()

        # Maps a category c to the logarithm of its prior probability,
        # i.e., c maps to log(Pr(c)).
        self.__priors: Dict[str, float] = {}

        # Maps a category c and a term t to the logarithm of its category-conditioned
        # posterior probability, i.e., (c, t) maps to log(Pr(t | c)).
        self.__posteriors: Dict[str, Dict[str, float]] = {}

        # Maps a category c to the denominator used when doing Laplace smoothing for
        # the posterior probabilities.
        self.__denominators: Dict[str, int] = {}

        # Train the classifier, i.e., estimate all probabilities.
        self.__compute_priors(training_set)
        self.__compute_vocabulary(training_set, fields)
        self.__compute_posteriors(training_set, fields)

    def __compute_priors(self, training_set) -> None:
        """
        Estimates all prior probabilities (or, rather, log-probabilities) needed for
        the naive Bayes classifier.
        """
        # Maximum likelihood estimate.
        total_count = sum(map(len, training_set.values()))
        self.__priors = {category: math.log(corpus.size() / total_count) for category, corpus in training_set.items()}

    def __compute_vocabulary(self, training_set, fields) -> None:
        """
        Builds up the overall vocabulary as seen in the training set.
        """
        # We're doing simple add-one (Laplace) smoothing when estimating the probabilities, so
        # figure out the size of the overall vocabulary.
        for _, corpus in training_set.items():
            for document in corpus:
                for field in fields:
                    for term in self.__get_terms(document.get_field(field, "")):
                        self.__vocabulary.add_if_absent(term)

    def __compute_posteriors(self, training_set, fields) -> None:
        """
        Estimates all conditional probabilities (or, rather, log-probabilities) needed for
        the naive Bayes classifier.
        """
        # Use smoothed estimates. Remember the denominators we used, so that we later know how
        # to deal with terms we haven't seen for a category.
        for category, corpus in training_set.items():
            term_frequencies = Counter(self.__get_terms(" ".join(d.get_field(f, "") for d in corpus for f in fields)))
            self.__denominators[category] = sum(term_frequencies.values()) + self.__vocabulary.size()
            self.__posteriors[category] = {term: self.__smooth(frequency, category) for term, frequency in term_frequencies.items()}

    def __smooth(self, frequency: int, category: str) -> float:
        """
        Computes a smoothed log-probability, using Lapace add-one smoothing. Assumes that
        we've already computed the correct fraction denominator to use for the given category.
        """
        return math.log((frequency + 1) / self.__denominators[category])

    def __get_terms(self, buffer) -> Iterator[str]:
        """
        Processes the given text buffer and returns the sequence of normalized
        terms as they appear. Both the documents in the training set and the buffers
        we classify need to be identically processed.
        """
        tokens = self.__tokenizer.strings(self.__normalizer.canonicalize(buffer))
        return (self.__normalizer.normalize(t) for t in tokens)

    def get_prior(self, category: str) -> float:
        """
        Given a category c, returns the category's prior log-probability log(Pr(c)).

        This is an internal detail having public visibility to facilitate testing.
        """
        return self.__priors[category]

    def get_posterior(self, category: str, term: str) -> float:
        """
        Given a category c and a term t, returns the posterior log-probability log(Pr(t | c)).
        If the term has not been observed for the current category, use a smoothed estimate.

        This is an internal detail having public visibility to facilitate testing.
        """
        try:
            return self.__posteriors[category][term]
        except KeyError:
            return self.__smooth(0, category)

    def classify(self, buffer: str) -> Iterator[Dict[str, Any]]:
        """
        Classifies the given buffer according to the multinomial naive Bayes rule. The computed (score, category) pairs
        are emitted back to the client via the supplied callback sorted according to the scores. The reported scores
        are log-probabilities, to minimize numerical underflow issues. Logarithms are base e.

        The results yielded back to the client are dictionaries having the keys "score" (float) and
        "category" (str).
        """
        # Only consider terms that occurred in the training set, for any category.
        terms = [term for term in self.__get_terms(buffer) if term in self.__vocabulary]

        # Compute log-probabilities for each category using priors and posteriors.
        scores = {category: prior + sum(self.get_posterior(category, term) for term in terms) for category, prior in self.__priors.items()}

        # Emit categories back to the client in sorted order.
        results = ({"score": score, "category": category} for category, score in sorted(scores.items(), key=lambda pair: pair[1], reverse=True))
        yield from results
