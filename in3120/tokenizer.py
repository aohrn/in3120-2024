# pylint: disable=missing-module-docstring
# pylint: disable=unnecessary-pass

import re
from abc import ABC, abstractmethod
from typing import Iterator, Tuple


class Tokenizer(ABC):
    """
    Simple abstract base class for tokenizers, with some default implementations.
    """

    @abstractmethod
    def spans(self, buffer: str) -> Iterator[Tuple[int, int]]:
        """
        Returns the positional spans (ranges) that indicate where in the buffer the
        tokens begin and end.
        """
        pass

    def strings(self, buffer: str) -> Iterator[str]:
        """
        Returns the strings that make up the tokens in the given buffer.
        """
        return (buffer[r[0]:r[1]] for r in self.spans(buffer))

    def tokens(self, buffer: str) -> Iterator[Tuple[str, Tuple[int, int]]]:
        """
        Returns the (string, span) pairs that make up the tokens in the given buffer.
        """
        return ((buffer[r[0]:r[1]], r) for r in self.spans(buffer))

    @staticmethod
    def join(tokens: Iterator[Tuple[str, Tuple[int, int]]]) -> str:
        """
        General utility method. The inverse of tokens/2, basically: Joins the tokens
        back into a reconstructed buffer, taking care of spaces (or not) between tokens.
        Currently assumes that the provided tokens are sorted in left-to-right order.
        """
        fragments = []
        previous_end = -1
        for token, (begin, end) in tokens:
            is_connected, previous_end = (previous_end > 0) and (begin == previous_end), end
            if fragments and not is_connected:
                fragments.append(" ")
            fragments.append(token)
        return "".join(fragments)


class SimpleTokenizer(Tokenizer):
    """
    A dead simple tokenizer for testing purposes, based on a naive regular expression.
    A real tokenizer wouldn't be implemented this way.
    """

    # Kids, don't do this at home.
    __pattern = re.compile(r"(\w+)", re.UNICODE | re.MULTILINE | re.DOTALL)

    def __init__(self):
        pass

    def spans(self, buffer: str) -> Iterator[Tuple[int, int]]:
        return ((m.start(), m.end()) for m in self.__pattern.finditer(buffer))


class DummyTokenizer(Tokenizer):
    """
    A tokenizer that doesn't tokenize, but just considers the buffer to be a single token.
    Useful if you have to supply a tokenizer but don't really want any tokenization.
    """

    def __init__(self):
        pass

    def strings(self, buffer: str) -> Iterator[str]:
        if buffer:
            yield buffer

    def tokens(self, buffer: str) -> Iterator[Tuple[str, Tuple[int, int]]]:
        if buffer:
            yield (buffer, (0, len(buffer)))

    def spans(self, buffer: str) -> Iterator[Tuple[int, int]]:
        if buffer:
            yield (0, len(buffer))


class UnigramTokenizer(Tokenizer):
    """
    A tokenizer that simply breaks the buffer up into individual Unicode characters.
    """

    def __init__(self):
        pass

    def strings(self, buffer: str) -> Iterator[str]:
        if buffer:
            yield from buffer

    def tokens(self, buffer: str) -> Iterator[Tuple[str, Tuple[int, int]]]:
        if buffer:
            yield from ((buffer[i], (i, i + 1)) for i in range(len(buffer)))

    def spans(self, buffer: str):
        if buffer:
            yield from ((i, i + 1) for i in range(len(buffer)))
