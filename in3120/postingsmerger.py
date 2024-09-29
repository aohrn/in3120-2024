# pylint: disable=missing-module-docstring

from typing import Iterator
from .posting import Posting


class PostingsMerger:
    """
    Utility class for merging posting lists.

    Note that the result of merging posting lists is itself a posting list.
    Hence the merging methods can be combined to compute the result of more
    complex Boolean operations over posting lists.

    See https://nlp.stanford.edu/IR-book/pdf/01bool.pdf for further background.

    It is currently left unspecified what to do with the term frequency field
    in the returned postings when document identifiers overlap. Different
    approaches are possible, e.g., an arbitrary one of the two postings could
    be returned, or the posting having the smallest/largest term frequency, or
    a new one that produces an averaged value, or something else.

    In Boolean retrieval and for determining if a document is a match/non-match
    for a possibly complex Boolean query expression, the term frequency field is
    irrelevant. But in a ranked retrieval setting we could imagine a scheme that
    generates a ranking signal (one of several) that acts as a feature in a
    relevance model. For example, we could imagine that each posting held a normalized
    term frequency value instead of (or in addition to) the raw term frequency value,
    and then interpret this as a fuzzy set membership function μ(t, d) to be used
    in a simple fuzzy logic scheme. For a possibly complex Boolean query expression
    q we could then compute μ(q, d) while merging, and let this be used as a ranking
    signal:

        TF(t, d)          = p.term_frequency if p.document_id == d else 0
        μ(t, d)           = TF(t, d) / max(TF(t₂, d) for t₂ in d), for term t
        μ(AND(e₁, e₂), d) = min(μ(e₁, d), μ(e₂, d)), for expressions e₁, e₂
        μ(OR(e₁, e₂), d)  = max(μ(e₁, d), μ(e₂, d)), for expressions e₁, e₂
        μ(NOT(e), d)      = 1 - μ(e, d), for expression e

    Other options are possible, this just being an illustrated example idea. The
    final relevance score that we use to rank by is then some scoring function
    net-score(q, d) = f(μ(q, d), ...) over the documents that match the Boolean query
    expression. Typically, the function f is machine-learnt. Unless already baked
    into μ(t, d), the "..." features would include factors like inverse document
    frequency weighting, static quality scores g(d), and much more. For further
    reading, see https://nlp.stanford.edu/IR-book/pdf/07system.pdf.
    """

    @staticmethod
    def intersection(iter1: Iterator[Posting], iter2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple AND(A, B) of two posting
        lists A and B, given iterators over these.

        In set notation, this corresponds to computing the intersection
        D(A) ∩ D(B), where D(A) and D(B) are the sets of documents that
        appear in A and B: A posting appears once in the result if and
        only if the document referenced by the posting appears in both
        D(A) and D(B).

        All posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        # Start at the head.
        current1 = next(iter1, None)
        current2 = next(iter2, None)

        # We can abort as soon as we exhaust one of the posting lists.
        while current1 and current2:

            # Increment the smallest one. Yield if we have a match.
            if current1.document_id == current2.document_id:
                yield current1
                current1 = next(iter1, None)
                current2 = next(iter2, None)
            elif current1.document_id < current2.document_id:
                current1 = next(iter1, None)
            else:
                current2 = next(iter2, None)

    @staticmethod
    def union(iter1: Iterator[Posting], iter2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple OR(A, B) of two posting
        lists A and B, given iterators over these.

        In set notation, this corresponds to computing the union
        D(A) ∪ D(B), where D(A) and D(B) are the sets of documents that
        appear in A and B: A posting appears once in the result if and
        only if the document referenced by the posting appears in either
        D(A) or D(B).

        All posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        # Start at the head.
        current1 = next(iter1, None)
        current2 = next(iter2, None)

        # First handle the case where neither posting list is exhausted.
        while current1 and current2:

            # Yield the smallest one.
            if current1.document_id == current2.document_id:
                yield current1
                current1 = next(iter1, None)
                current2 = next(iter2, None)
            elif current1.document_id < current2.document_id:
                yield current1
                current1 = next(iter1, None)
            else:
                yield current2
                current2 = next(iter2, None)

        # We have exhausted at least one of the lists. Yield the remaining tail, if any.
        current, tail = (current1, iter1) if current1 else (current2, iter2)
        if current:
            yield current
            yield from tail

    @staticmethod
    def difference(iter1: Iterator[Posting], iter2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple ANDNOT(A, B) of two posting
        lists A and B, given iterators over these.

        In set notation, this corresponds to computing the difference
        D(A) - D(B), where D(A) and D(B) are the sets of documents that
        appear in A and B: A posting appears once in the result if and
        only if the document referenced by the posting appears in D(A)
        but not in D(B).

        All posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        # Start at the head.
        current1 = next(iter1, None)
        current2 = next(iter2, None)

        # First handle the case where neither posting list is exhausted.
        while current1 and current2:
            if current1.document_id < current2.document_id:
                yield current1
                current1 = next(iter1, None)
            elif current1.document_id > current2.document_id:
                current2 = next(iter2, None)
            else:
                current1 = next(iter1, None)
                current2 = next(iter2, None)

        # Yield the remaining elements in the first list, if any.
        if current1:
            yield current1
            yield from iter1
