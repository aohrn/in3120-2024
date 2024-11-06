# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals

from collections import Counter
from typing import Iterator, Dict, Any
from .sieve import Sieve
from .ranker import Ranker
from .corpus import Corpus
from .invertedindex import InvertedIndex


class SimpleSearchEngine:
    """
    Realizes a simple query evaluator that efficiently performs N-of-M matching over an inverted index.
    I.e., if the query contains M unique query terms, each document in the result set should contain at
    least N of these m terms. For example, 2-of-3 matching over the query 'orange apple banana' would be
    logically equivalent to the following predicate:

       (orange AND apple) OR (orange AND banana) OR (apple AND banana)
       
    Note that N-of-M matching can be viewed as a type of "soft AND" evaluation, where the degree of match
    can be smoothly controlled to mimic either an OR evaluation (1-of-M), or an AND evaluation (M-of-M),
    or something in between.

    The evaluator uses the client-supplied ratio T = N/M as a parameter as specified by the client on a
    per query basis. For example, for the query 'john paul george ringo' we have M = 4 and a specified
    threshold of T = 0.75 would imply that at least 3 of the 4 query terms have to be present in a matching
    document.
    """

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex):
        self.__corpus = corpus
        self.__inverted_index = inverted_index

    def evaluate(self, query: str, options: Dict[str, Any], ranker: Ranker) -> Iterator[Dict[str, Any]]:
        """
        Evaluates the given query, doing N-out-of-M ranked retrieval. I.e., for a supplied query having M
        unique terms, a document is considered to be a match if it contains at least N <= M of those terms.

        The matching documents, if any, are ranked by the supplied ranker, and only the "best" matches are yielded
        back to the client as dictionaries having the keys "score" (float) and "document" (Document).

        The client can supply a dictionary of options that controls the query evaluation process: The value of
        N is inferred from the query via the "match_threshold" (float) option, and the maximum number of documents
        to return to the client is controlled via the "hit_count" (int) option.
        """
        # Produce the query terms. We must use the same string processing here as we used when
        # building up the inverted index. Some terms might be duplicated (e.g., as in the query
        # "to be or not to be").
        query_terms = self.__inverted_index.get_terms(query)
        unique_query_terms = list(Counter(query_terms).items())

        # Get the posting lists for the unique query terms.
        posting_lists = [self.__inverted_index[term] for (term, _) in unique_query_terms]

        # We require that at least N of the M query terms are present in the document,
        # for the document to be considered part of the result set. What should the minimum
        # value of N be? (We could take multiplicity into account here, too, and not just uniqueness.)
        match_threshold = max(0.0, min(1.0, options.get("match_threshold", 0.5)))
        required_minimum = max(1, min(len(unique_query_terms), int(match_threshold * len(unique_query_terms))))

        # When traversing the posting lists using document-at-a-time traversal, we need to keep track
        # of where we are in each of the posting lists. Initially, all the cursors "point to" the first entry
        # in each posting list. Keep track of which posting lists that remain to be fully traversed.
        all_cursors = [next(p, None) for p in posting_lists]
        remaining_cursor_ids = [i for i in range(len(all_cursors)) if all_cursors[i]]

        # We're doing ranked retrieval. Assess relevance scores per document as we go along, as we're doing
        # document-at-a-time traversal. Keep track of the K highest-scoring documents.
        sieve = Sieve(max(1, min(100, options.get("hit_count", 10))))

        # We're doing at least N-of-M matching. As we reach the end of the posting lists, we can abort when
        # the number of non-exhausted lists drops below the required minimum N.
        while len(remaining_cursor_ids) >= required_minimum:

            # The posting lists are sorted by the document identifiers in ascending order. Define the
            # "frontier" as the subset of non-exhausted posting lists that mention the lowest document
            # identifier. In a sense, if we imagine scanning the posting lists from left to right, the
            # frontier is the subset that has the "leftmost" cursors.
            document_id = min(all_cursors[i].document_id for i in remaining_cursor_ids)
            frontier_cursor_ids = [i for i in remaining_cursor_ids if all_cursors[i].document_id == document_id]

            # The number of elements on the "frontier" needs to be at least N. Otherwise, these documents
            # don't contain enough of the query terms, and aren't part of the result set.
            if len(frontier_cursor_ids) >= required_minimum:
                ranker.reset(document_id)
                for i in frontier_cursor_ids:
                    ranker.update(unique_query_terms[i][0], unique_query_terms[i][1], all_cursors[i])
                sieve.sift(ranker.evaluate(), document_id)

            # Move along the cursors on the frontier. The cursors not on the frontier remain where they
            # are. We may or may not reach the end of some posting lists when we advance, so the set of
            # remaining non-exhausted lists might shrink.
            for i in frontier_cursor_ids:
                all_cursors[i] = next(posting_lists[i], None)
            remaining_cursor_ids = [i for i in range(len(all_cursors)) if all_cursors[i]]

        # Alert the client about the best-matching documents. Emit documents sorted according to their
        # relevancy scores.
        for score, document_id in sieve.winners():
            yield {"score": score, "document": self.__corpus[document_id]}
