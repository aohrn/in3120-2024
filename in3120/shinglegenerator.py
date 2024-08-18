# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

from typing import Iterator, Tuple, Optional
from collections import deque
from itertools import islice
from .tokenizer import Tokenizer
from .normalizer import Normalizer, DummyNormalizer


class ShingleGenerator(Tokenizer):
    """
    Does character-level shingling: Tokenizes a buffer into overlapping shingles
    having a specified width, as measured by character count. For example, the
    3-shingles for "mouse" are {"mou", "ous", "use"}.

    If the buffer is shorter than the shingle width then this produces a single
    shorter-than-usual shingle.

    The current implementation is simplistic and not whitespace- or punctuation-aware,
    and doesn't treat the beginning or end of the buffer in any special way.

    Character-level shingles are also called "k-grams", and can be used for various
    kinds of tolerant string matching, or near-duplicate detection. For details, see
    https://nlp.stanford.edu/IR-book/html/htmledition/k-gram-indexes-for-wildcard-queries-1.html,
    https://nlp.stanford.edu/IR-book/html/htmledition/k-gram-indexes-for-spelling-correction-1.html,
    or https://nlp.stanford.edu/IR-book/html/htmledition/near-duplicates-and-shingling-1.html.

    Note that 1-shingles reduces to a simple unigram tokenizer.
    """

    def __init__(self, width: int):
        assert width > 0
        self.__width = width

    def spans(self, buffer: str) -> Iterator[Tuple[int, int]]:
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

class WordShingleGenerator(Tokenizer):
    """
    Does token-level shingling: Tokenizes a buffer into overlapping shingles
    having a specified width, as measured by token count. For example, the
    2-shingles for "foo bar baz gog" are {"foo bar", "bar baz", "baz gog"}.

    If the buffer is shorter than the shingle width then this produces a single
    shorter-than-usual shingle.

    We delegate to another tokenizer exactly how to split the buffer into individual
    tokens. Optionally, individual tokens can be normalized.

    For 2-shingles used with a traditional tokenizer, the tokens are also called "biwords".
    For details, see https://nlp.stanford.edu/IR-book/html/htmledition/biword-indexes-1.html.

    Note that 1-shingles is just a roundabout way of invoking the embedded tokenizer, but
    with the added convenience of doing normalization as part of the tokenization process.
    """

    def __init__(self, width: int, tokenizer: Tokenizer, normalizer: Optional[Normalizer]):
        assert width > 0
        self.__width = width
        self.__tokenizer = tokenizer
        self.__normalizer = normalizer or DummyNormalizer()

    def spans(self, buffer: str) -> Iterator[Tuple[int, int]]:
        return (span for _, span in self.tokens(buffer))

    def strings(self, buffer: str) -> Iterator[str]:
        return (string for string, _ in self.tokens(buffer))

    def tokens(self, buffer: str) -> Iterator[Tuple[str, Tuple[int, int]]]:
        tokens = self.__tokenizer.tokens(buffer)
        header = ((self.__normalizer.normalize(string), _) for string, _ in islice(tokens, self.__width))
        window = deque(header, self.__width)
        while True:
            if len(window) > 0:
                oldest_span = window[0][1]
                newest_span = window[-1][1]
                yield (self.join(window), (oldest_span[0], newest_span[1]))
            string, span = next(tokens, (None, None))
            if string is None:
                break
            window.append((self.__normalizer.normalize(string), span))

