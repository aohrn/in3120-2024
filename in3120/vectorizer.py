# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

from __future__ import annotations
from typing import Iterable, Iterator, Dict
from collections import Counter
from itertools import chain
from math import log10
from .document import Document
from .corpus import Corpus
from .invertedindex import InvertedIndex
from .sparsedocumentvector import SparseDocumentVector
from .trie import Trie


class Vectorizer:
    """
    Utility class that demonstrates how to create a sparse document vector from a document or
    set of documents. Uses TF-IDF weighting.
    """

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex, stopwords: Trie):
        self._corpus = corpus  # Actually, we just need to know the size of the corpus.
        self._inverted_index = inverted_index  # Actually, we just need a way to look up the document frequency for a term.
        self._stopwords = stopwords  # As an alternative to this, we could use a document frequency cutoff.

    def _tfidf(self, term: str, term_frequency: int) -> float:
        """
        Returns the TF-IDF weight for the given term.
        """
        tf = 1.0 + log10(term_frequency)
        df = self._inverted_index.get_document_frequency(term)
        idf = log10(self._corpus.size() / df)
        return tf * idf

    def get_vocabulary(self) -> Iterator[str]:
        """
        Returns the vocabulary that the vectorizer knows about, i.e., the dimensions of the vector space
        in which a generated sparse document vector is placed.
        """
        return self._inverted_index.get_indexed_terms()

    def from_buffers(self, buffers: Iterator[str]) -> Dict[str, float]:
        """
        Creates a dictionary of (term, weight) pairs from the given buffers. Only terms that are present
        in our reference index and that are not stopwords are included. The weights are TF-IDF scores.
        """
        # We currently don't keep track of which buffers the terms occur in.
        # If we did, then we could easily include field weights, e.g., indicate
        # things like the 'title' field being twice as important as the 'body'
        # field and as eight times as important as the 'footnotes' field.
        all_terms = chain.from_iterable(self._inverted_index.get_terms(buffer or "") for buffer in buffers)
        known_terms = filter(lambda t: self._inverted_index.get_document_frequency(t) > 0 and t not in self._stopwords, all_terms)
        term_frequencies = Counter(known_terms)
        return {term: self._tfidf(term, term_frequency) for term, term_frequency in term_frequencies.items()}

    def from_document(self, document: Document, fields: Iterable[str]) -> SparseDocumentVector:
        """
        Creates a sparse document vector from the named fields in the given document. Only terms that are present
        in our reference index and that are not stopwords are included. The weights are TF-IDF scores.
        """
        return SparseDocumentVector(self.from_buffers(document.get_field(f, "") for f in fields))
