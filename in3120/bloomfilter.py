# pylint: disable=missing-module-docstring

import hashlib
import math
import sys
from typing import Iterable, Iterator, Tuple


class BloomFilter:
    """
    A very basic and not very efficient implementation of a vanilla Bloom filter,
    for educational demonstration purposes.

    See https://en.wikipedia.org/wiki/Bloom_filter for details.
    """

    def __contains__(self, item: str):
        return self.is_member(item)

    def __init__(self, n: int = 1000, p: float = 0.05):

        # Basic filter parameters, given.
        self._n = n  # The number of items we expect to add.
        self._p = p  # The probability of a false positive when we assess membership.
        assert self._n > 0
        assert 0.0 < self._p < 1.0

        # Basic filter parameters, inferred. See https://en.wikipedia.org/wiki/Bloom_filter.
        self._m = max(1, -math.ceil((self._n * math.log(self._p)) / math.pow(math.log(2), 2)))
        self._k = max(1, round((self._m / self._n) * math.log(2)))

        # The backing bits.
        self._bits = bytearray(math.ceil(self._m / 8))

        # The hash functions. These should be independent of each other. Keep it simple for now.
        # See https://www.eecs.harvard.edu/~michaelm/postscripts/tr-02-05.pdf for a trick where
        # we only need two hash functions to simulate additional hash functions.
        self._hash1 = lambda b: int.from_bytes(hashlib.sha1(b).digest(), sys.byteorder) % self._m
        self._hash2 = lambda b: int.from_bytes(hashlib.md5(b).digest(), sys.byteorder) % self._m

    def _set(self, slot: int, value: bool) -> None:
        """
        Sets the bit in the given slot to the given value.
        """
        quotient, remainder = divmod(slot, 8)
        if value:
            self._bits[quotient] |= (1 << remainder)
        else:
            self._bits[quotient] &= ~(1 << remainder)

    def _get(self, slot: int) -> bool:
        """
        Returns the value of the bit in the given slot.
        """
        quotient, remainder = divmod(slot, 8)
        return 1 == ((self._bits[quotient] >> remainder) & 1)

    def _slots(self, item: str) -> Iterator[int]:
        """
        Lazily generates a set of hash values that can be used as indices ("slots") into the buffer
        of backing bits.

        See https://www.eecs.harvard.edu/~michaelm/postscripts/tr-02-05.pdf for a trick where
        we only need two hash functions to simulate additional hash functions.
        """
        assert item is not None
        stuff = item.encode()
        hash1 = self._hash1(stuff)
        hash2 = self._hash2(stuff)
        value = hash1
        for _ in range(self._k):
            yield value % self._m
            value += hash2

    def _add(self, item: str) -> None:
        """
        Adds the given item to the Bloom filter.
        """
        for slot in self._slots(item):
            self._set(slot, True)

    def add(self, items: Iterable[str]) -> None:
        """
        Adds all the given items to the Bloom filter.
        """
        assert items is not None
        for item in items:
            self._add(item)

    def is_member(self, item: str) -> bool:
        """
        Checks if the given item has previously been added to the Bloom filter.
        
        This is a probabilistic data structure where "no" means no, and "yes" means maybe:
        Returns False if the item has definitely not been added, and returns True if the
        item has probably been added. The false positive rate is controlled by the parameters
        supplied when constructing the filter.
        """
        return all(self._get(slot) for slot in self._slots(item))

    def get_parameters(self) -> Tuple[int, float, int, int]:
        """
        Returns the (n, p, m, k) tuple that defines the Bloom filter. Facilitates testing.
        """
        return (self._n, self._p, self._m, self._k)
