# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=fixme
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments

import math
from typing import Iterator, Dict, Any, Callable
from .edittable import EditTable
from .normalizer import Normalizer
from .sieve import Sieve
from .tokenizer import Tokenizer
from .trie import Trie


class EditSearchEngine:
    """
    Realizes a simple edit distance lookup engine, that, given a larger set of strings encoded
    in a trie, finds all strings in the trie that are close to a given query string in terms of edit
    distance.
    
    See the paper "Tries for Approximate String Matching" by Shang and Merrett for details. This
    implementation assumes that we set an upper bound on the allowed edit distance (treating anything
    above this bound as infinity and non-retrievable), and that this upper bound is relatively small.
    Imposing a small upper bound allows us to prune the search space and make the search reasonably
    efficient.
    """

    def __init__(self, trie: Trie, normalizer: Normalizer, tokenizer: Tokenizer):
        self.__trie = trie
        self.__normalizer = normalizer  # The same as was used for trie building.
        self.__tokenizer = tokenizer  # The same as was used for trie building.

    def evaluate(self, query: str, options: dict) -> Iterator[Dict[str, Any]]:
        """
        Locates all strings in the trie that are no more than K edit errors away from the query string.

        The matching strings, if any, are scored and only the highest-scoring matches are yielded
        back to the client as dictionaries having the keys "score" (float), "distance" (int) and
        "match" (str).

        The client can supply a dictionary of options that controls the query evaluation process:
        Supported dictionary keys include "upper_bound" (int), "candidate_count" (int),
        "hit_count" (int), "first_n" (int), and "scoring" (str).
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def __dfs(self, node: Trie, level: int, table: EditTable,
              upper_bound: int, callback: Callable[[float, str, Any], bool]) -> bool:
        """
        Does a recursive depth-first search in the trie, pruning away paths that cannot lead
        to matches with a sufficiently low edit cost. See paper by Shang and Merrett for a
        detailed discussion.

        Returns True unless the supplied callback tells us to abort the search.

        As this implementation is recursive, the call stack might blow up if we go really
        many levels deep into the trie. That should not be an issue as the primary use case
        for this search is to consult a simple spellchecking dictionary of strings all having
        reasonable lengths, but could merit a second look if we look to apply this to other
        use cases.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")
