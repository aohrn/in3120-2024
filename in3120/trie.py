# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=protected-access

from __future__ import annotations
from itertools import repeat
from typing import Dict, List, Any, Tuple, Optional, Iterable, Iterator
from .normalizer import Normalizer
from .tokenizer import Tokenizer


class Trie:
    """
    A very simple and straightforward implementation of a trie for demonstration purposes
    and tiny dictionaries. A node in the trie is also itself a trie in this implementation.

    A serious real-world implementation of a trie or an automaton would not be implemented
    this way. The trie/automaton would then instead be encoded into a single contiguous buffer
    and there'd be significant attention on memory consumption and scalability with respect to
    dictionary size. Both keys and values (meta data) would be compressed.

    Using, e.g., Marisa (https://github.com/pytries/marisa-trie), or DAWG (https://dawg.readthedocs.io/en/latest/),
    or datrie (https://pypi.org/project/datrie/), or hat-trie (https://github.com/pytries/hat-trie)
    would have plausible open source alternatives.

    We can, optionally, associate a meta data value of some kind with each final/terminal state
    the trie/automaton. Some applications might benefit from this, if we need to keep rich meta data
    associated with each string. In such cases, these associated values could be other strings, or
    values that can be used as lookup keys into, e.g., some external database. If a string to add
    has no meta data associated with it, we associate the value None.
    """

    def __init__(self):
        self.__children: Dict[str, Optional[Trie]] = {}

    def __repr__(self):
        return repr(self.__children)

    def __contains__(self, string: str):
        descendant = self.consume(string)
        return descendant and descendant.is_final()

    def __iter__(self):
        return self.strings()

    def __getitem__(self, prefix: str):
        return self.consume(prefix)

    @staticmethod
    def from_strings(strings: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer) -> Trie:
        """
        Constructor-like convenience method. Creates and returns a new trie containing
        all the given strings.
        """
        return Trie.from_strings2(zip(strings, repeat(None)), normalizer, tokenizer)

    @staticmethod
    def from_strings2(strings: Iterable[Tuple[str, Optional[Any]]], normalizer: Normalizer, tokenizer: Tokenizer) -> Trie:
        """
        Constructor-like convenience method. Creates and returns a new trie containing
        all the given (string, meta) pairs.
        """
        trie = Trie()
        trie.add2(strings, normalizer, tokenizer)
        return trie

    def __add(self, string: str, meta: Optional[Any]) -> None:
        """
        Internal helper method, adds the given non-empty string and its optional
        associated meta data to the trie with this node as the root. The string is
        assumed already properly normalized at this point.

        The special transition symbol "" is used as a marker to indicate that a node
        is final/terminal. The meta data, if any, is associated with this special
        transition symbol.
        """
        assert 0 < len(string)
        trie = self
        for symbol in string:
            if symbol not in trie.__children:
                trie.__children[symbol] = Trie()
            trie = trie.__children[symbol]
        if "" in trie.__children:
            assert trie.__children[""] == meta
        else:
            trie.__children[""] = meta

    def add(self, strings: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer) -> None:
        """
        Adds all the strings to the trie, after normalizing them. The tokenizer is used so
        that we're robust to nuances in whitespace and punctuation.

        Adding the same string more than once is benign and idempotent. Note that "same" here
        means after normalization.
        """
        self.add2(zip(strings, repeat(None)), normalizer, tokenizer)

    def add2(self, strings: Iterable[Tuple[str, Optional[Any]]], normalizer: Normalizer, tokenizer: Tokenizer) -> None:
        """
        Adds all the strings and their associated meta data values to the trie,
        after normalizing them. The tokenizer is used so that we're robust to nuances
        in whitespace and punctuation.

        If a string has no meta data associated with it, None is assumed passed as the
        meta data value.

        Adding the same string more than once is benign and idempotent, as long as their
        associated meta data values do not differ. Note that "same" here means after
        normalization.
        """
        for string, meta in strings:
            tokens = tokenizer.tokens(normalizer.canonicalize(string))
            self.__add(tokenizer.join((normalizer.normalize(t), _) for t, _ in tokens), meta)

    def consume(self, prefix: str) -> Optional[Trie]:
        """
        Consumes the given prefix verbatim and returns the resulting descendant node,
        if any. I.e., if strings that have this prefix have been added to the trie, then
        the trie node corresponding to traversing the prefix is returned. Otherwise, None
        is returned.

        Assumes that the prefix is already normalized.
        """
        node = self
        for symbol in prefix:
            node = node.__children.get(symbol, None)
            if not node:
                return None
        return node

    def child(self, transition: str) -> Optional[Trie]:
        """
        Returns the immediate child node, given a transition symbol. Returns None if the transition
        symbol is invalid. Functionally equivalent to consume(transition), but simpler and for the
        special of a single transition symbol and not a longer string.

        Assumes that the transition symbol is already normalized.
        """
        return self.__children.get(transition, None)

    def strings(self) -> Iterator[str]:
        """
        Yields all strings that are found in or below this node. For simple testing and debugging purposes.
        The returned strings are emitted back in lexicographical order.
        """
        stack = [(self, "")]
        while stack:
            node, prefix = stack.pop()
            if node.is_final():
                yield prefix
            for symbol, child in sorted(node.__children.items(), reverse=True):
                if symbol and child:
                    stack.append((child, prefix + symbol))

    def transitions(self) -> List[str]:
        """
        Returns the set of symbols that are valid outgoing transitions, i.e., the set of symbols that
        when consumed by this node would lead to a valid child node. The returned transitions are
        emitted back in lexicographical order.
        """
        return sorted(s for s in self.__children if s)

    def is_final(self) -> bool:
        """
        Returns True iff the current node is a final/terminal state in the trie/automaton, i.e.,
        if a string has been added to the trie where the end of the string ends up in this node.
        """
        return "" in self.__children

    def has_meta(self) -> bool:
        """
        Returns True iff the current node is a final/terminal state that has meta data associated
        with it.
        """
        return self.get_meta() is not None

    def get_meta(self) -> Optional[Any]:
        """
        Returns the meta data associated with the final/terminal state, or None if no such meta
        data exists.
        """
        return self.__children[""] if self.is_final() else None
