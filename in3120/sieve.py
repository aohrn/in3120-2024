# pylint: disable=missing-module-docstring

import heapq
from typing import Iterator, Iterable, Any, Union, Tuple

# Not strictly needed, but left for clarity. PEP 484 explicitly specifies that
# "when an argument is annotated as having type float, an argument of type int
# is acceptable." [https://peps.python.org/pep-0484/#the-numeric-tower]
Number = Union[int, float]


class Sieve:
    """
    Implements a "sieve", i.e., a heap-based data structure through which
    we can "sift" N scored items, and be left with the up to K (item, score)
    pairs having the largest scores. Ties are resolved arbitrarily.

    A sieve is an efficient way of selecting the "best" K items from a set of N
    items, where K << N. An internal heap keeps track of "the worst of the best",
    so that we immediately know if a candidate item makes the cut.

    Candidate items can be of any type, as long as that type has an "<" operator
    defined.
    """

    def __init__(self, size: int):
        assert size > 0
        self.__size = size
        self.__heap = []

    def sift(self, score: Number, item: Any) -> None:
        """
        Sifts a scored item through the sieve.
        """
        if len(self.__heap) < self.__size:
            heapq.heappush(self.__heap, (score, item))
        else:
            root_score = self.__heap[0][0]
            if root_score < score:
                heapq.heapreplace(self.__heap, (score, item))

    def sift2(self, pairs: Iterable[Tuple[Number, Any]]) -> None:
        """
        Sifts a stream of scored items through the sieve.
        """
        for score, item in pairs:
            self.sift(score, item)

    def winners(self) -> Iterator[Tuple[Number, Any]]:
        """
        Returns the highest-scoring items that have been sifted through the sieve, sorted
        in descending order. The returned list iterator yields (score, item) tuples.

        This implementation is currently not idempotent. Invoke only once.
        """
        # Since the internal heap tracks "the worst of the best" and we want the
        # list sorted as "the best of the best", we reverse the internal heap ordering.
        return reversed([heapq.heappop(self.__heap) for _ in range(len(self.__heap))])
