# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

from typing import Any, Dict, Iterable, Iterator
from .corpus import Corpus
from .sparsedocumentvector import SparseDocumentVector
from .vectorizer import Vectorizer


class RocchioClassifier:
    """
    Defines a simple Rocchio text classifier, that assumes relatively few possible categories
    and therefore resorts to an exhaustive scan against all centroids. For a detailed primer, see
    https://nlp.stanford.edu/IR-book/html/htmledition/rocchio-classification-1.html.
    
    Note that a Rocchio classifier is basically a 1-NN classifier over the set of centroids
    rather than over the full set of individual vectors. A k-NN classifier over the full set
    of individual vectors might produce better results in practive, but is also more
    resource-intensive at classification-time and might require an approximate nearest neighbor
    index to scale. See https://en.wikipedia.org/wiki/Nearest_neighbor_search for details.
    """

    def __init__(self, training_set: Dict[str, Corpus], fields: Iterable[str], vectorizer: Vectorizer):
        """
        Vectorizes all documents in the training set so that we can compare
        query vectors against these and arrive at a classification.

        The supplied vectorizer is assumed created from an inverted index produced
        from the "super-corpus" consisting of the union of all the corpora in the
        training set.
        """
        self._vectorizer = vectorizer
        self._centroids = {c: SparseDocumentVector.centroid(self._vectorizer.from_document(d, fields) for d in training_set[c]) for c in training_set}

    def classify(self, buffer: str) -> Iterator[Dict[str, Any]]:
        """
        Classifies the given buffer according to the Rocchio classification algorithm.

        The results yielded back to the client are dictionaries having the keys "score" (float) and
        "category" (str).
        """
        # Compare the query vector against every centroid.
        query = SparseDocumentVector(self._vectorizer.from_buffers([buffer]))
        scores = [(query.cosine(centroid), _) for _, centroid in self._centroids.items()]

        # Yield results back to the client in sorted order.
        for similarity, category in sorted(scores, reverse=True):
            if similarity > 0.0:
                yield {"score": similarity, "category": category}
