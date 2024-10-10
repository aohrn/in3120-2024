# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods

from typing import Iterator, Dict, Any, List, Tuple
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .trie import Trie


class StringFinder:
    """
    Given a trie encoding a dictionary of strings, efficiently finds the subset of strings in the dictionary
    that are also present in a given text buffer. I.e., in a sense computes the "intersection" or "overlap"
    between the dictionary and the text buffer.

    Uses a trie-walk algorithm similar to the Aho-Corasick algorithm with some simplifications (we ignore the
    part about failure transitions) and some minor NLP extensions. The running time of this algorithm is virtually
    independent of the size of the dictionary, and linear in the length of the buffer we are searching in.

    The tokenizer we use when scanning the input buffer is assumed to be the same as the one that was used
    when adding strings to the trie.
    """

    def __init__(self, trie: Trie, normalizer: Normalizer, tokenizer: Tokenizer):
        self.__trie = trie
        self.__normalizer = normalizer  # The same as was used for trie building.
        self.__tokenizer = tokenizer  # The same as was used for trie building.

    def scan(self, buffer: str) -> Iterator[Dict[str, Any]]:
        """
        Scans the given buffer and finds all dictionary entries in the trie that are also present in the
        buffer. We only consider matches that begin and end on token boundaries.

        The matches, if any, are yielded back to the client as dictionaries having the keys "match" (str),
        "surface" (str), "meta" (Optional[Any]), and "span" (Tuple[int, int]). Note that "match" refers to
        the matching dictionary entry, "surface" refers to the content of the input buffer that triggered the
        match (the surface form), and "span" refers to the exact location in the input buffer where the surface
        form is found. Depending on the normalizer that is used, "match" and "surface" may or may not differ.

        A space-normalized version of the surface form is emitted as "surface", for convenience. Clients
        that require an exact surface form that is not space-normalized can easily reconstruct the desired
        string using the emitted "span" value.

        In a serious application we'd add more lookup/evaluation features, e.g., support for prefix matching,
        support for leftmost-longest matching (instead of reporting all matches), and more.
        """
        # The set of currently explored states. We represent a state as a triple consisting
        # of (a) a node in the trie (that represents where in the trie we are after having
        # consumed zero or more characters), (b) an index (that represents the position into
        # the original buffer where the state was "born"), and (c) a string (that represents
        # the symbols consumed so far to get to the current state.) Item (a) is what we advance
        # along the way, item (b) is needed so that we know where we first started if/when a
        # match is found, and item (c) is needed so that we can differentiate between the surface
        # form of the match and the (possibly heavily normalized) base form of the match.
        live_states: List[Tuple[Trie, int, str]] = []

        # Where did the previous token end? Assume that tokens are produced sorted in left-to-right
        # order.
        previous_end = -1

        # Only consider matches that start on token boundaries.
        for string, (begin, end) in self.__tokenizer.tokens(buffer):

            # Mirror how the trie was built, ensuring we compare apples to apples.
            # Canonicalize on a per token basis instead of doing the whole buffer upfront,
            # to ensure that offsets are retained and the ranges we report back make
            # sense to the client.
            string = self.__normalizer.normalize(self.__normalizer.canonicalize(string))

            # Is this token "connected to" the previous token, in the sense of the two being
            # crammed together with nothing separating them? Some languages, e.g., Japanese or
            # Chinese, don't use whitespace between tokens.
            is_connected, previous_end = (previous_end > 0) and (begin == previous_end), end

            # Inject a space for the currently live states, if needed. Prune away states that
            # don't survive.
            if not is_connected:
                live_states = [(child, _, m + " ") for s, _, m in live_states if (child := s.consume(" "))]

            # Consider this token a potential start for a match.
            live_states.append((self.__trie, begin, ""))

            # Advance all currently live states with the current (normalized) token. Prune away
            # states that don't survive.
            live_states = [(child, _, m + string) for s, _, m in live_states if (child := s.consume(string))]

            # Report matches, if any, that end on the token we just consumed. Use the
            # tokenizer to possibly space-normalize the surface form we emit. If the client
            # requires the exact surface form and its location in the input buffer, they can
            # do that using the returned span.
            for s, b, m in filter(lambda triple: triple[0].is_final(), live_states):
                yield {"match": m,
                       "meta": s.get_meta(),
                       "surface": self.__tokenizer.join(self.__tokenizer.tokens(buffer[b:end])),
                       "span": (b, end)}
