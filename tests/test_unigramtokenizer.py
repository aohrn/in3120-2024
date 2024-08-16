# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from context import in3120


class TestUnigramTokenizer(unittest.TestCase):

    def setUp(self):
        self.__tokenizer = in3120.UnigramTokenizer()

    def test_strings(self):
        result = list(self.__tokenizer.strings("A🩷E"))
        self.assertListEqual(result, ["A", "🩷", "E"])

    def test_tokens(self):
        result = list(self.__tokenizer.tokens("A🩷E"))
        self.assertListEqual(result, [("A", (0, 1)), ("🩷", (1, 2)), ("E", (2, 3))])

    def test_spans(self):
        result = list(self.__tokenizer.spans("A🩷E"))
        self.assertListEqual(result, [(0, 1), (1, 2), (2, 3)])

    def test_empty_input(self):
        self.assertListEqual(list(self.__tokenizer.strings("")), [])
        self.assertListEqual(list(self.__tokenizer.tokens("")), [])
        self.assertListEqual(list(self.__tokenizer.spans("")), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
