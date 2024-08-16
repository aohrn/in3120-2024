# pylint: disable=missing-module-docstring

from typing import Iterator
from .posting import Posting


class PostingsMerger:
    """
    Utility class for merging posting lists.

    It is currently left unspecified what to do with the term frequency field
    in the returned postings when document identifiers overlap. Different
    approaches are possible, e.g., an arbitrary one of the two postings could
    be returned, or the posting having the smallest/largest term frequency, or
    a new one that produces an averaged value, or something else.
    """

    @staticmethod
    def intersection(iter1: Iterator[Posting], iter2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple AND(A, B) of two posting
        lists A and B, given iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    @staticmethod
    def union(iter1: Iterator[Posting], iter2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple OR(A, B) of two posting
        lists A and B, given iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    @staticmethod
    def difference(iter1: Iterator[Posting], iter2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple ANDNOT(A, B) of two posting
        lists A and B, given iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")
