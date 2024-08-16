# pylint: disable=missing-module-docstring
# pylint: disable=unnecessary-pass

from abc import abstractmethod
import collections.abc
from typing import Optional, Tuple


class Dictionary(collections.abc.Iterable[Tuple[str, int]]):
    """
    Abstract base class for dictionaries that map vocabulary terms to integer codes.
    It's often easier and more efficient to work with integers than strings, e.g., so
    that we can use the integers as direct indexes into arrays and other lookup structures.
    With N strings in total we want to map these to the integer set {0, .., N - 1}, i.e.,
    a minimal perfect hash.
    """

    def __len__(self):
        return self.size()

    def __getitem__(self, term: str) -> int:
        term_id = self.get_term_id(term)
        if term_id is None:
            raise KeyError
        return term_id

    def __contains__(self, term: str) -> bool:
        return self.get_term_id(term) is not None

    @abstractmethod
    def size(self) -> int:
        """
        Returns the size of the dictionary, i.e., the number of unique terms added
        to the dictionary.
        """
        pass

    @abstractmethod
    def add_if_absent(self, term: str) -> int:
        """
        Adds a new term to the dictionary. If the term already exists in the dictionary,
        the dictionary is left unchanged. The associated term identifier is returned.
        """
        pass

    @abstractmethod
    def get_term_id(self, term: str) -> Optional[int]:
        """
        Looks up the given term in the dictionary and returns the term's corresponding
        integer code. If the term is not present in the dictionary, None is returned.
        """
        pass


class InMemoryDictionary(Dictionary):
    """
    A simple in-memory implementation for demonstration purposes, suitable for
    small vocabularies.
    """

    def __init__(self):
        self._terms = {}

    def __iter__(self):
        yield from self._terms.items()

    def __repr__(self):
        return str(self._terms)

    def size(self) -> int:
        return len(self._terms)

    def add_if_absent(self, term: str) -> int:
        term_id = self.get_term_id(term)
        if term_id is None:
            term_id = self.size()
            self._terms[term] = term_id
        return term_id

    def get_term_id(self, term: str) -> Optional[int]:
        return self._terms.get(term, None)
