# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals

from collections import Counter, deque
from typing import Tuple, Optional
from .normalizer import Normalizer
from .tokenizer import Tokenizer


class WindowFinder:
    """
    Finds the smallest window in a text buffer that contains all the query terms, as measured by the number
    of terms in the window. The width of the window can be a useful engineered feature when learning to rank,
    and the window itself (possibly slightly padded for additional context) can be used as a result snippet.
    Result snippets are sometimes also called dynamic summaries, keyword-in-context snippets, or dynamic teasers.

    For details and background, see https://nlp.stanford.edu/IR-book/html/htmledition/query-term-proximity-1.html,
    https://nlp.stanford.edu/IR-book/html/htmledition/a-simple-example-of-machine-learned-scoring-1.html#sec:mls,
    and https://nlp.stanford.edu/IR-book/html/htmledition/results-snippets-1.html.

    Note that finding the smallest window is just one factor that goes into a production-ready snippet algorithm. For
    example, we might not assign equal emphasis to each query term (think TF-IDF statistics), we might not require that
    the window contains all query terms (think "enough" high-value terms), and we might want to reward windows that
    preserve the original ordering of query terms as much as possible (think term-level edit distance). As such,
    the size of the window just becomes one out of several other factors to combine in finding an "optimal" window.
    """

    def __init__(self, normalizer: Normalizer, tokenizer: Tokenizer):
        self.__normalizer = normalizer
        self.__tokenizer = tokenizer

    def scan(self, buffer: str, query: str) -> Optional[Tuple[int, int, int]]:
        """
        Finds the smallest window in a text buffer that contains all the query terms, as measured by the number
        of terms in the window. The number of terms in such a minimal window is denoted as ω in the textbook.

        This demonstration implementation works on the level of strings and text buffers. A much more efficient
        implementation might instead work on the level of the positional postings data in a positional index. That way,
        we would just be working with the positions of the query terms in the buffer instead of the positions of all
        terms in the buffer, and we would not have to re-tokenize and re-normalize the text buffer. The algorithm
        fundamentals would be similar, though.

        The current implementation uses a sliding window approach to solve the "minimum window substring" problem
        that is sometimes used as an online technical interview question (Google it), but generalized to work on
        query terms instead of characters and slightly improved.

        Currently, a single window is returned. We can easily generalize the implementation to return multiple
        windows, e.g., in the case where there are ties or multiple windows that are "almost as small" as the
        smallest one.

        A window is returned as a (<width>, <begin>, <end>) tuple. Here, <width> indicates how many tokens that
        are contained in the window (i.e., the value ω since the window is minimal), and <begin> and <end> are
        character-level indices that can be used by the client to slice the input buffer to yield a plausible
        result snippet. If no minimal window can be found, None is returned.

        The implementation assumes that the query string and the buffer have both been canonicalized beforehand,
        so that the returned <begin> and <end> values are correctly interpreted.
        """
        # The individual normalized query terms, including their counts if they are not distinct.
        query_terms = Counter(self.__normalizer.normalize(t) for t in self.__tokenizer.strings(query))

        # The buffer terms and their surface-form ranges. Generated lazily, scanned once.
        buffer_terms = ((self.__normalizer.normalize(t), _) for t, _ in self.__tokenizer.tokens(buffer))

        # Bookkeeping.
        infinity = 99999999    # Just a really large value.
        window = deque()       # Our sliding window over the buffer.
        counts = {}            # Our current distribution of query terms within the sliding window.
        covered = 0            # How many of the query terms that we have fully covered within the sliding window.
        smallest_w = infinity  # The width of the smallest window seen so far, that covers all query terms.
        smallest_b = 0         # Where the smallest window seen so far begins, if found.
        smallest_e = 0         # Where the smallest window seen so far ends, if found.

        # Scan, keeping a sliding window!
        for buffer_term, span in buffer_terms:

            # If our window is empty and would still continue to be empty, just skip it.
            is_query_term = buffer_term in query_terms
            if covered == 0 and not is_query_term:
                continue

            # Grow our sliding window on the right. Update our window statistics, if needed.
            window.append((buffer_term, span))
            if is_query_term:
                counts[buffer_term] = 1 + counts.get(buffer_term, 0)
                if counts[buffer_term] == query_terms[buffer_term]:
                    covered += 1

            # If our window now contains everything we need, try to shrink it.
            while covered == len(query_terms):

                # Smallest window found so far?
                if len(window) < smallest_w:
                    smallest_w = len(window)
                    _, (smallest_b, _) = window[0]
                    _, (_, smallest_e) = window[-1]

                # Shrink the window from the left. Update our window statistics, if needed.
                term, _ = window.popleft()
                is_query_term = term in query_terms
                if is_query_term:
                    counts[term] -= 1
                    if counts[term] < query_terms[term]:
                        covered -= 1

        # Emit results, if any.
        return None if smallest_w == infinity else (smallest_w, smallest_b, smallest_e)
