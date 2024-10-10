# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

from bisect import bisect_left
from itertools import takewhile
from typing import Dict, Iterator, Iterable, Tuple, List
from collections import Counter
from .document import Document
from .corpus import Corpus
from .normalizer import Normalizer
from .tokenizer import Tokenizer


class SuffixArray:
    """
    A simple suffix array implementation. Allows us to conduct efficient substring searches.
    The prefix of a suffix is an infix!

    In a serious application we'd make use of least common prefixes (LCPs), pay more attention
    to memory usage, and add more lookup/evaluation features.
    """

    def __init__(self, corpus: Corpus, fields: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer):
        self.__corpus = corpus
        self.__normalizer = normalizer
        self.__tokenizer = tokenizer
        self.__haystack: List[Tuple[int, str]] = []  # The (<document identifier>, <searchable content>) pairs.
        self.__suffixes: List[Tuple[int, int]] = []  # The sorted (<haystack index>, <start offset>) pairs.
        self.__build_suffix_array(fields)  # Construct the haystack and the suffix array itself.

    def __build_suffix_array(self, fields: Iterable[str]) -> None:
        """
        Builds a simple suffix array from the set of named fields in the document collection.
        The suffix array allows us to search across all named fields in one go.
        """
        # We allow searching across multiple document fields simultaneously, so join the named fields
        # to produce the haystack that we'll search for needles in. Avoid cross-field matches.
        self.__haystack = [(d.document_id, " \0 ".join(self.__normalize(d.get_field(f, "")) for f in fields)) for d in self.__corpus]

        # We don't actually store all suffixes, instead we store (index, offset) pairs which allows us
        # to generate the suffixes if/when we need them: The index identifies the document, and the
        # offset identifies where in the document the substring starts. A naive suffix array generation
        # is fine for now.
        self.__suffixes = [(index, begin) for index, (_, buffer) in enumerate(self.__haystack) for begin, _ in self.__tokenizer.spans(buffer)]
        self.__suffixes.sort(key=self.__get_suffix)

    def __normalize(self, buffer: str) -> str:
        """
        Produces a normalized version of the given string. Both queries and documents need to be
        identically processed for lookups to succeed.
        """
        # Tokenize and join to be robust to nuances in whitespace and punctuation.
        tokens = self.__tokenizer.tokens(self.__normalizer.canonicalize(buffer))
        tokens = ((self.__normalizer.normalize(t), _) for t, _ in tokens)
        return self.__tokenizer.join(tokens)

    def __get_suffix(self, pair: Tuple[int, int]) -> str:
        """
        Produces the suffix/substring from the normalized document buffer for the given (index, offset) pair.
        """
        index, offset = pair
        return self.__haystack[index][1][offset:]  # Slicing implies copying. This should be possible to avoid.

    def evaluate(self, query: str, options: dict) -> Iterator[Dict[str, int | Document]]:
        """
        Evaluates the given query, doing a "phrase prefix search".  E.g., for a supplied query phrase like
        "to the be", we return documents that contain phrases like "to the bearnaise", "to the best",
        "to the behemoth", and so on. I.e., we require that the query phrase starts on a token boundary in the
        document, but it doesn't necessarily have to end on one.

        The matching documents are ranked according to how many times the query substring occurs in the document,
        and only the "best" matches are yielded back to the client. Ties are resolved arbitrarily.

        The client can supply a dictionary of options that controls this query evaluation process: The maximum
        number of documents to return to the client is controlled via the "hit_count" (int) option.

        The results yielded back to the client are dictionaries having the keys "score" (int) and
        "document" (Document).
        """
        # Search for the needle in the haystack, using binary search. Define that the empty query matches
        # nothing, not everything.
        needle = self.__normalize(query)
        if not needle:
            return
        where_start = bisect_left(self.__suffixes, needle, key=self.__get_suffix)

        # Helper predicate. Checks if the identified suffix starts with the needle. Since slicing implies copying,
        # cap the length of the slice to the length of the needle. The starts-with relation then becomes the same
        # as equality, which is quick to check.
        def _is_match(i: int) -> bool:
            j, offset = self.__suffixes[i]
            return self.__haystack[j][1][offset:(offset + len(needle))] == needle

        # Suffixes sharing a prefix are consecutive in the suffix array. Scan ahead from the located index until
        # we no longer get a match. We expect a low number of matches for typical queries, and we process all the
        # matches below anyway. If we just wanted to count the number of matches without processing them, we
        # could instead of a linear scan do another binary search to locate where the range ends.
        matches = takewhile(_is_match, range(where_start, len(self.__suffixes)))

        # Deduplicate. A document in the haystack might contain multiple occurrences of the needle.
        # Rank according to occurrence count, and emit in ranked order.
        if matches:
            debug = options.get("debug", False)
            pairs = [self.__suffixes[i] for i in matches]
            if debug:
                for pair in pairs:
                    print("*** MATCH", pair, self.__get_suffix(pair))
            counter = Counter([i for i, _ in pairs])
            for index, count in counter.most_common(max(1, min(100, options.get("hit_count", 10)))):
                yield {"score": count, "document": self.__corpus[self.__haystack[index][0]]}
