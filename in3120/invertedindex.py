# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=unnecessary-pass
# pylint: disable=unused-argument

import itertools
from abc import ABC, abstractmethod
from collections import Counter
from typing import Iterable, Iterator, List, Tuple, Dict
from .dictionary import InMemoryDictionary
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .corpus import Corpus
from .posting import Posting
from .postinglist import CompressedInMemoryPostingList, InMemoryPostingList, PostingList


class InvertedIndex(ABC):
    """
    Abstract base class for a simple inverted index.
    """

    def __getitem__(self, term: str) -> Iterator[Posting]:
        return self.get_postings_iterator(term)

    def __contains__(self, term: str) -> bool:
        return self.get_document_frequency(term) > 0

    @abstractmethod
    def get_terms(self, buffer: str) -> Iterator[str]:
        """
        Processes the given text buffer and returns an iterator that yields normalized
        terms as they are indexed. Useful when both query strings and documents need to
        be identically processed. The terms produced from the given text buffer may or
        may not have been encountered index construction.
        """
        pass

    @abstractmethod
    def get_indexed_terms(self) -> Iterator[str]:
        """
        Returns an iterator over all unique terms that have been encountered during the
        construction of the inverted index, i.e., our term vocabulary or all terms for which
        there exists a posting list. The vocabulary is not listed in any particular order.
        This method might be useful if a client needs to build up some additional data
        structure over the term vocabulary, that is external to the inverted index.
        """
        pass

    @abstractmethod
    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        """
        Returns an iterator that can be used to iterate over the term's associated
        posting list. For out-of-vocabulary terms we associate empty posting lists.
        """
        pass

    @abstractmethod
    def get_document_frequency(self, term: str) -> int:
        """
        Returns the number of documents in the indexed corpus that contain the given term.
        """
        pass

    def get_collection_frequency(self, term: str) -> int:
        """
        Returns the number of times the given term occurs in the indexed corpus, across
        all documents.
        """
        return sum(p.term_frequency for p in self.get_postings_iterator(term))


class InMemoryInvertedIndex(InvertedIndex):
    """
    A simple in-memory implementation of an inverted index, suitable for small corpora.

    In a serious application we'd have configuration to allow for field-specific NLP,
    scale beyond current memory constraints, have a positional index, and so on.

    If index compression is enabled, only the posting lists are compressed. Dictionary
    compression is currently not supported.
    """

    def __init__(self, corpus: Corpus, fields: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer, compressed: bool = False):
        self._corpus = corpus
        self._normalizer = normalizer
        self._tokenizer = tokenizer
        self._posting_lists: List[PostingList] = []
        self._dictionary = InMemoryDictionary()
        self._build_index(fields, compressed)

    def __repr__(self):
        return str({term: self._posting_lists[term_id] for term, term_id in self._dictionary})

    def _build_index(self, fields: Iterable[str], compressed: bool) -> None:
        """
        Kicks off the indexing process. Basically implements a flavor of SPIMI indexing as described in
        https://nlp.stanford.edu/IR-book/html/htmledition/single-pass-in-memory-indexing-1.html but with
        the vastly simplifying assumption that everything fits in memory so we just have a single block
        and thus no need to merge per-block results.

        Note that we currently don't keep track of which field each term occurs in. If we were to allow
        fielded searches (e.g., "find documents that contain 'foo' in the 'title' field") then we would
        have to keep track of that, either as a synthetic term in the dictionary (e.g., 'foo.title') or
        as extra data in the posting. See https://nlp.stanford.edu/IR-book/html/htmledition/parametric-and-zone-indexes-1.html
        for further details.

        Also note that we are building a non-positional index, for simplicity. With a positional index
        we could offer clients the ability to do, e.g., phrase searches and proximity-based filtering and
        ranking. See https://nlp.stanford.edu/IR-book/html/htmledition/positional-indexes-1.html for
        further details.
        """
        for document in self._corpus:
            all_terms = itertools.chain.from_iterable(self.get_terms(document.get_field(f, "")) for f in fields)
            term_frequencies = Counter(all_terms)
            for term, term_frequency in term_frequencies.items():
                term_id = self._add_to_dictionary(term)
                self._append_to_posting_list(term_id, document.document_id, term_frequency, compressed)
        self._finalize_index()

    def _add_to_dictionary(self, term: str) -> int:
        """
        Adds the given term to the dictionary, if it's not already present. If it's already present,
        the dictionary stays unchanged. Returns the term identifier assigned to the term.
        """
        # Assign the term an identifier, if needed. First come, first serve.
        return self._dictionary.add_if_absent(term)

    def _append_to_posting_list(self, term_id: int, document_id: int, term_frequency: int, compressed: bool) -> None:
        """
        Appends a new posting to the right posting list. The posting lists
        must be kept sorted so that we can efficiently traverse and
        merge them when querying the inverted index.
        """
        # Locate the posting list for this term. Create it, if needed.
        assert term_id >= 0
        assert document_id >= 0
        assert term_frequency > 0
        if term_id >= len(self._posting_lists):
            assert term_id == len(self._posting_lists)
            self._posting_lists.append(CompressedInMemoryPostingList() if compressed else InMemoryPostingList())
        posting_list = self._posting_lists[term_id]
        posting_list.append_posting(Posting(document_id, term_frequency))

    def _finalize_index(self):
        """
        Invoked at the very end after all documents have been processed. Provides
        implementations that need it with the chance to tie up any loose ends,
        if needed.
        """
        # For example, if we do compression in chunks or do bit-level compression then there
        # might be outstanding data to be processed.
        for posting_list in self._posting_lists:
            posting_list.finalize_postings()

    def get_terms(self, buffer: str) -> Iterator[str]:
        # In a serious large-scale application there could be field-specific tokenizers.
        # We choose to keep it simple here.
        tokens = self._tokenizer.strings(self._normalizer.canonicalize(buffer))
        return (self._normalizer.normalize(t) for t in tokens)

    def get_indexed_terms(self) -> Iterator[str]:
        # Assume that everything fits in memory. This would not be the case in a serious
        # large-scale application, even with compression.
        return (s for s, _ in self._dictionary)

    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        # Assume that everything fits in memory. This would not be the case in a serious
        # large-scale application, even with compression.
        term_id = self._dictionary.get_term_id(term)
        return iter([]) if term_id is None else iter(self._posting_lists[term_id])

    def get_document_frequency(self, term: str) -> int:
        # In a serious large-scale application we'd store this number explicitly, e.g., as part of the dictionary.
        # That way, we can look up the document frequency without having to access the posting lists
        # themselves. Imagine if the posting lists don't even reside in memory!
        term_id = self._dictionary.get_term_id(term)
        return 0 if term_id is None else self._posting_lists[term_id].get_length()


class DummyInMemoryInvertedIndex(InMemoryInvertedIndex):
    """
    Creates a fake or dummy inverted index with no posting lists. Useful if the only effect we're
    after is the ability to infer a term's document frequency in the corpus, and we want to allow
    this to happen whether we have a real inverted index available or not: If we have a real inverted
    index at hand then use that, otherwise we can create and use this dummy version.
    """

    def __init__(self, corpus: Corpus, fields: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer):
        self._document_frequencies: Dict[int, int] = {}  # Maps a term identifier to its document frequency.
        super().__init__(corpus, fields, normalizer, tokenizer, False)

    def __repr__(self):
        return str({term: self._document_frequencies[term_id] for term, term_id in self._dictionary})

    def _append_to_posting_list(self, term_id: int, document_id: int, term_frequency: int, compressed: bool) -> None:
        # Actually, don't append to the posting list. Introduce a side-effect instead.
        self._document_frequencies[term_id] = self._document_frequencies.get(term_id, 0) + 1

    def _finalize_index(self):
        # No posting lists!
        pass

    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        # No posting lists!
        return iter([])

    def get_document_frequency(self, term: str) -> int:
        return self._document_frequencies.get(self._dictionary.get_term_id(term), 0)


class AccessLoggedInvertedIndex(InvertedIndex):
    """
    Wraps another inverted index, and keeps an in-memory log of which postings
    that have been accessed. Facilitates testing.
    """

    class AccessLoggedIterator(Iterator[Posting]):
        """
        Wraps another iterator, and updates an in-memory log of which postings
        that have been accessed. Facilitates testing.
        """

        def __init__(self, term: str, accesses: List[Tuple[str, int]], wrapped: Iterator[Posting]):
            self._term = term
            self._accesses = accesses
            self._wrapped = wrapped

        def __next__(self):
            posting = next(self._wrapped)
            self._accesses.append((self._term, posting.document_id))
            return posting

    def __init__(self, wrapped: InvertedIndex):
        self._wrapped = wrapped
        self._accesses = []

    def get_terms(self, buffer: str) -> Iterator[str]:
        return self._wrapped.get_terms(buffer)

    def get_indexed_terms(self) -> Iterator[str]:
        return self._wrapped.get_indexed_terms()

    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        return __class__.AccessLoggedIterator(term, self._accesses, self._wrapped.get_postings_iterator(term))

    def get_document_frequency(self, term: str) -> int:
        return self._wrapped.get_document_frequency(term)

    def get_history(self) -> List[Tuple[str, int]]:
        """
        Returns the list of postings that clients have accessed so far.
        """
        return self._accesses
