# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from types import GeneratorType
from context import in3120


class TestSimpleTokenizer(unittest.TestCase):

    def setUp(self):
        self.__tokenizer = in3120.SimpleTokenizer()

    def test_strings(self):
        result = list(self.__tokenizer.strings("Dette  er en\nprøve!"))
        self.assertListEqual(result, ["Dette", "er", "en", "prøve"])

    def test_tokens(self):
        result = list(self.__tokenizer.tokens("Dette  er en\nprøve!"))
        self.assertListEqual(result, [("Dette", (0, 5)), ("er", (7, 9)), ("en", (10, 12)), ("prøve", (13, 18))])

    def test_spans(self):
        result = list(self.__tokenizer.spans("Dette  er en\nprøve!"))
        self.assertListEqual(result, [(0, 5), (7, 9), (10, 12), (13, 18)])

    def test_join(self):
        tokens = list(self.__tokenizer.tokens("Dette  er en\nprøve"))
        tokens.extend([("!", (18, 19)), ("?", (19, 20))])
        result = self.__tokenizer.join(tokens)
        self.assertEqual(result, "Dette er en prøve!?")

    def test_empty_input(self):
        self.assertListEqual(list(self.__tokenizer.strings("")), [])
        self.assertListEqual(list(self.__tokenizer.tokens("")), [])
        self.assertListEqual(list(self.__tokenizer.spans("")), [])

    def test_uses_yield(self):
        for i in range(0, 5):
            text = "foo " * i
            self.assertIsInstance(self.__tokenizer.spans(text), GeneratorType)
            self.assertIsInstance(self.__tokenizer.tokens(text), GeneratorType)
            self.assertIsInstance(self.__tokenizer.strings(text), GeneratorType)


if __name__ == '__main__':
    unittest.main(verbosity=2)
