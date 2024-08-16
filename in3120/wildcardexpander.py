# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

from typing import Iterable, Tuple, Set, List
from .trie import Trie
from .normalizer import DummyNormalizer
from .tokenizer import DummyTokenizer


class WildcardExpander:
    """
    Expands a given wildcard pattern. E.g., the wildcard pattern 'fi*er' might
    be expanded to ['fishmonger', 'filibuster', 'fisher', 'finder'].

    Uses a permuterm index to transform the problem into that of doing a prefix lookup.
    See https://nlp.stanford.edu/IR-book/html/htmledition/permuterm-indexes-1.html for
    details.
    """

    def __init__(self, terms: Iterable[str]):
        # We're going to need prefix lookups, so store the permuterm rotations in a trie.
        # We could have used other prefix-friendly data structures here, too, such as a
        # B-tree or even just a simple sorted array with binary search on top.
        self._rotations = Trie()

        # Assume that the provided terms are already properly normalized tokens.
        normalizer = DummyNormalizer()
        tokenizer = DummyTokenizer()

        # Add all rotations. E.g., the term 'hello' would give rise to the rotations
        # ['hello$', 'ello$h', 'llo$he', 'lo$hel', 'o$hell', '$hello'] where '$' is
        # a magic sentinel symbol. Associate each rotation with the original term
        # that gave rise to the rotation.
        for term in terms:
            padded = term + self.get_sentinel()
            rotations = (padded[i:] + padded[:i] for i in range(len(padded)))
            self._rotations.add2(((rotation, term) for rotation in rotations), normalizer, tokenizer)

    def _lookup(self, key: str, is_prefix: bool) -> Set[str]:
        """
        Given a lookup key, does a lookup among the set of permuterm rotations.
        The lookup can be a prefix lookup or an exact lookup, as specified.

        The original term that gave rise to a permuterm rotation is assumed
        associated with the rotation and available as meta data in the trie node.
        """
        node = self._rotations.consume(key)
        if not node:
            return set()
        if not is_prefix:
            return set() if not node.is_final() else {node.get_meta()}
        return set(node.consume(tail).get_meta() for tail in node.strings())

    def get_sentinel(self) -> str:
        """
        Returns the magic sentinel used for rotations. The sentinel should never occur
        in a valid term.

        This is an internal detail having public visibility to facilitate testing.
        """
        return "\0"

    def get_keys(self, pattern: str) -> List[Tuple[str, bool]]:
        """
        Given a wildcard pattern, returns the lookup key(s) to use for lookups
        in the permuterm index. A returned lookup key is associated with a
        Boolean flag indicating whether the lookup key should be used for a
        prefix lookup (True) or an exact lookup (False).

        Raises a KeyError if the wildcard pattern is invalid or otherwise not
        handled.
        
        This is an internal detail having public visibility to facilitate testing.
        """
        # Decompose the wildcard pattern. Ignore leading/trailing whitespace.
        pattern = pattern.strip()
        parts = pattern.split("*")

        # Infer the appropriate lookup key per the permuterm rules.
        match len(parts):
            case 1:
                # X → X$
                if parts[0]:
                    return [(parts[0] + self.get_sentinel(), False)]
            case 2:
                # X*Y → Y$X*
                if parts[0] and parts[1]:
                    return [(parts[1] + self.get_sentinel() + parts[0], True)]
                # X* → $X*
                if parts[0]:
                    return [(self.get_sentinel() + parts[0], True)]
                # *X → X$*
                if parts[1]:
                    return [(parts[1] + self.get_sentinel(), True)]
            case 3:
                # *X* → X*
                if not parts[0] and parts[1] and not parts[2]:
                    return [(parts[1], True)]
                # X*Y*Z → Z$X* and Y*
                if parts[0] and parts[1]:
                    return [(parts[2] + self.get_sentinel() + parts[0], True),
                            (parts[1], True)]

        # Unhandled.
        raise KeyError(pattern)

    def expand(self, pattern: str) -> Set[str]:
        """
        Given a wildcard pattern like 'fi*er', expands this to the set of terms
        that match the pattern. E.g., 'fi*er' might be expanded to {'fishmonger',
        'filibuster', 'fisher', 'finder'}.
        """
        # Some patterns are bogus.
        if pattern is None or pattern.find(self.get_sentinel()) != -1:
            raise KeyError(pattern)

        # Infer the lookup query.
        keys = self.get_keys(pattern)

        # Look up strings in the permuterm index.
        match len(keys):
            case 1:
                return self._lookup(*keys[0])
            case 2:
                # Filtering results from the first lookup may or may not be more efficient
                # than doing two lookups and computing the intersection. For now, just do
                # it with two lookups.
                return self._lookup(*keys[0]).intersection(self._lookup(*keys[1]))

        # Unhandled.
        raise KeyError(pattern)
