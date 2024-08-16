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
