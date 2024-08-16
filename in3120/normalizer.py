# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=unnecessary-pass

import unicodedata
from abc import ABC, abstractmethod
from .soundex import Soundex
from .porterstemmer import PorterStemmer


class Normalizer(ABC):
    """
    Simple abstract base class for text normalizers. A normalizer is a tokenizer's
    cousin: Typically, you canonicalize a buffer before tokenizing it, and then you
    normalize the tokens produced by the tokenizer.
    """

    def canonicalize(self, buffer: str) -> str:
        """
        Normalizes a larger text buffer, so that downstream NLP can assume some kind of
        standardized text representation.

        In a serious application we might normalize the encoding and do Unicode canonicalization
        here, and perhaps nothing else.
        """
        # The Unicode standard defines various normalization forms of a Unicode string, based
        # on the definition of canonical equivalence and compatibility equivalence. In Unicode,
        # several characters can be expressed in various way. For example, the character U+00C7
        # (LATIN CAPITAL LETTER C WITH CEDILLA) can also be expressed as the sequence U+0043
        # (LATIN CAPITAL LETTER C) U+0327 (COMBINING CEDILLA).
        #
        # See, e.g., https://unicode.org/reports/tr15/ or https://docs.python.org/3/library/unicodedata.html
        # for more details.
        #
        # Unicode canonicalization is especially important for some languages. E.g., for Chinese,
        # Japanese and Korean we'd want to properly support both full-width and half-width forms.
        return unicodedata.normalize("NFKC", buffer)

    @abstractmethod
    def normalize(self, token: str) -> str:
        """
        Normalizes a token to produce an actual index term.

        In a serious application we might do transliteration, accent removal, lemmatization or
        stemming, or other stuff here, in addition to simple case folding.
        """
        pass


class SimpleNormalizer(Normalizer):
    """
    A dead simple normalizer for simple testing purposes.
    Bumps the token to lowercase.
    """

    def __init__(self):
        pass

    def normalize(self, token: str) -> str:
        return token.casefold()


class DummyNormalizer(Normalizer):
    """
    A normalizer that doesn't normalize, but just implements the identity function.
    Useful if you have to supply a normalizer but don't really want any normalization.
    Unicode canonicalization is optional, and disabled by default.
    """

    def __init__(self, canonicalize: bool = False):
        self.__canonicalize = canonicalize

    def canonicalize(self, buffer: str) -> str:
        return buffer if not self.__canonicalize else super().canonicalize(buffer)

    def normalize(self, token: str) -> str:
        return token


class SoundexNormalizer(Normalizer):
    """
    For simple phonetic name matching purposes. Assumes English.
    """

    def __init__(self):
        self._soundex = Soundex()

    def normalize(self, token: str) -> str:
        return self._soundex.encode(token)


class PorterNormalizer(Normalizer):
    """
    Applies a set of recall-enhancing stemming heuristics. Assumes English.
    """

    def __init__(self):
        self._stemmer = PorterStemmer()

    def normalize(self, token: str) -> str:
        return self._stemmer.stem(token)
