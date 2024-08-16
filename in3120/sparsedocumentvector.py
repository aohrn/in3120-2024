# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

from __future__ import annotations
from typing import Iterable, Iterator, Dict, Tuple, Optional
from math import sqrt
from .sieve import Sieve

class SparseDocumentVector:
    """
    A simple representation of a sparse document vector. The vector space has one dimension
    per vocabulary term, and our representation only lists the dimensions that have non-zero
    values.

    Being able to place text buffers, be they documents or queries, in a vector space and
    thinking of them as point clouds (or, equivalently, as vectors from the origin) enables us
    to numerically assess how similar they are according to some suitable metric. Cosine
    similarity (the inner product of the vectors normalized by their lengths) is a very
    common metric.
    """

    def __init__(self, values: Dict[str, float]):
        # An alternative, effective representation would be as a
        # [(term identifier, weight)] list kept sorted by integer
        # term identifiers. Computing dot products would then be done
        # pretty much in the same way we do posting list AND-scans.
        self._values = values

        # We cache the length. It might get used over and over, e.g., for cosine
        # computations. A value of None triggers lazy computation.
        self._length : Optional[float] = None

    def __iter__(self):
        return iter(self._values.items())

    def __getitem__(self, term: str) -> float:
        return self._values.get(term, 0.0)

    def __setitem__(self, term: str, weight: float) -> None:
        self._values[term] = weight
        self._length = None

    def __contains__(self, term: str) -> bool:
        return term in self._values

    def __len__(self) -> int:
        """
        Enables use of the built-in len/1 function to count the number of non-zero
        dimensions in the vector. It is not for computing the vector's norm.
        """
        return len(self._values)

    def get_length(self) -> float:
        """
        Returns the length (L^2 norm, also called the Euclidian norm) of the vector.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def normalize(self) -> None:
        """
        Divides all weights by the length of the vector, thus rescaling it to
        have unit length.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def top(self, count: int) -> Iterable[Tuple[str, float]]:
        """
        Returns the top weighted terms, i.e., the "most important" terms and their weights.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def truncate(self, count: int) -> None:
        """
        Truncates the vector so that it contains no more than the given number of terms,
        by removing the lowest-weighted terms.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def scale(self, factor: float) -> None:
        """
        Multiplies every vector component by the given factor.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def dot(self, other: SparseDocumentVector) -> float:
        """
        Returns the dot product (inner product, scalar product) between this vector
        and the other vector.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def cosine(self, other: SparseDocumentVector) -> float:
        """
        Returns the cosine of the angle between this vector and the other vector.
        See also https://en.wikipedia.org/wiki/Cosine_similarity.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    @staticmethod
    def centroid(vectors: Iterator[SparseDocumentVector]) -> SparseDocumentVector:
        """
        Computes the centroid of all the vectors, i.e., the average vector.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")
