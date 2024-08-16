# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=protected-access

import unittest
import types
from context import in3120


class TestWordShingleGenerator(unittest.TestCase):

    def setUp(self):
        tokenizer = in3120.SimpleTokenizer()
        normalizer = in3120.SimpleNormalizer()
        self.__tokenizer = in3120.WordShingleGenerator(2, tokenizer, normalizer)

    def test_strings(self):
        self.assertListEqual(list(self.__tokenizer.strings("")), [])
        self.assertListEqual(list(self.__tokenizer.strings("Foo")), ["foo"])
        self.assertListEqual(list(self.__tokenizer.strings("Foo  the")), ["foo the"])
        self.assertListEqual(list(self.__tokenizer.strings("Foo the  BAR")), ["foo the", "the bar"])

    def test_tokens(self):
        self.assertListEqual(list(self.__tokenizer.tokens("Foo")), [("foo", (0, 3))])
        self.assertListEqual(list(self.__tokenizer.tokens("Foo  the")), [("foo the", (0, 8))])
        self.assertListEqual(list(self.__tokenizer.tokens("Foo the  BAR")), [("foo the", (0, 7)), ("the bar", (4, 12))])

    def test_spans(self):
        self.assertListEqual(list(self.__tokenizer.spans("foo")), [(0, 3)])
        self.assertListEqual(list(self.__tokenizer.spans("foo the")), [(0, 7)])
        self.assertListEqual(list(self.__tokenizer.spans("foo the bar")), [(0, 7), (4, 11)])

    def test_uses_yield(self):
        for i in range(0, 5):
            text = "foo " * i
            self.assertIsInstance(self.__tokenizer.spans(text), types.GeneratorType)
            self.assertIsInstance(self.__tokenizer.tokens(text), types.GeneratorType)
            self.assertIsInstance(self.__tokenizer.strings(text), types.GeneratorType)

    def test_spans_cover_surface_forms_but_strings_are_normalized(self):
        wrapped = in3120.SimpleTokenizer()
        normalizer = in3120.PorterNormalizer()
        text = "Operationally intriguing  tests"
        expected = {
            1: (["oper", "intrigu", "test"], ["Operationally", "intriguing", "tests"]),
            2: (["oper intrigu", "intrigu test"], ["Operationally intriguing", "intriguing  tests"]),
        }
        for width, strings in expected.items():
            tokenizer = in3120.WordShingleGenerator(width, wrapped, normalizer)
            tokens = list(tokenizer.tokens(text))
            self.assertListEqual([s for s, _ in tokens], strings[0])
            self.assertListEqual([text[s[0]:s[1]] for _, s in tokens], strings[1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
