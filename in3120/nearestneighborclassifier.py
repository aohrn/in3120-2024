# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

from typing import Any, Dict, Iterable, Iterator, Set
from .corpus import Corpus, InMemoryCorpus
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .similaritysearchengine import SimilaritySearchEngine

class NearestNeighborClassifier:
    """
    Implements a simple k-NN text classifier. Compared to the reference functionality as described
    in https://nlp.stanford.edu/IR-book/html/htmledition/k-nearest-neighbor-1.html, the implementation
    is slightly generalized to support the case where an example in the training set can belong to
    multiple categories, and where we can do both simple voting and similarity-based voting. 
    """

    def __init__(self, training_set: Dict[str, Corpus], fields: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer):
        """
        Creates a k-NN text classifier. Indexes all the documents in the training set
        so that we can do efficient text classification later on.
        """
        # Create a mapping from document identifiers to their categories. A document
        # can belong to more than one category.
        self._categories : Dict[str, Set] = {}
        for category, corpus in training_set.items():
            for document in corpus:
                if document.document_id not in self._categories:
                    self._categories[document.document_id] = set()
                self._categories[document.document_id].add(category)

        # Create a merged corpus of all the unique documents, which is what we'll index.
        merged = InMemoryCorpus.merge(training_set)

        # This does the heavy lifting and retrieves the most similar training examples.
        self._retriever = SimilaritySearchEngine(merged, fields, normalizer, tokenizer)

    def classify(self, buffer: str, options: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """
        Classifies the given buffer according to the k-NN classification algorithm, using simple
        voting.

        The results yielded back to the client are dictionaries having the keys "score" (float) and
        "category" (str).
        """
        # Retrieve the most similar documents in the set of training examples. The cosine
        # similarity to each matching training example is also returned.
        k = max(1, min(100, options.get("k", 3)))
        matches = list(self._retriever.evaluate(buffer, {"hit_count": k}))

        # How should we tally up the votes? We either do simple voting, or we weight
        # each vote by the similarity to the training example.
        voting = options.get("voting", "simple")
        assert voting in ("simple", "weighted")

        # Score the categories that the matching documents belong to.
        totals = {}
        accumulated = 0.0
        for match in matches:
            for category in self._categories[match["document"].document_id]:
                votes = {
                    "simple":   lambda m: 1,
                    "weighted": lambda m: m["score"],
                }[voting](match)
                accumulated += votes
                totals[category] = votes + totals.get(category, 0.0)

        # Yield results back to the client in sorted order. Normalize the scores.
        for category, score in sorted(totals.items(), key=lambda item: item[1], reverse=True):
            yield {"score": score / accumulated, "category": category}
