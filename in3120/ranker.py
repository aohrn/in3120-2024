# pylint: disable=missing-module-docstring
# pylint: disable=unnecessary-pass

from abc import ABC, abstractmethod
from .posting import Posting


class Ranker(ABC):
    """
    Abstract base class for rankers used together with document-at-a-time traversal.
    """

    @abstractmethod
    def reset(self, document_id: int) -> None:
        """
        Resets the ranker, i.e., prepares it for evaluating another document.
        """
        pass

    @abstractmethod
    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        """
        Tells the ranker to update its internals based on information from one
        query term and the associated posting. This method might be invoked multiple
        times if the query contains multiple unique terms. Since a query term might
        occur multiple times in a query, the query term's multiplicity or occurrence
        count in the query is also provided.
        """
        pass

    @abstractmethod
    def evaluate(self) -> float:
        """
        Returns the current document's relevancy score. I.e., evaluates how relevant
        the current document is, given all the previous update invocations.
        """
        pass


class SimpleRanker(Ranker):
    """
    A dead simple ranker, based on TF alone.
    """

    def __init__(self):
        self.__document_id = None
        self.__score = 0.0

    def reset(self, document_id: int) -> None:
        self.__document_id = document_id
        self.__score = 0.0

    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        assert self.__document_id == posting.document_id
        self.__score += multiplicity * posting.term_frequency

    def evaluate(self) -> float:
        return self.__score
