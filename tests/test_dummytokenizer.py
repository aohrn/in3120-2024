# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from context import in3120


class TestDummyTokenizer(unittest.TestCase):

    def setUp(self):
        self.__tokenizer = in3120.DummyTokenizer()

    def test_strings(self):
        result = list(self.__tokenizer.strings(" Dette  er en\nprøve!"))
        self.assertListEqual(result, [" Dette  er en\nprøve!"])

    def test_tokens(self):
        result = list(self.__tokenizer.tokens(" Dette  er en\nprøve!"))
        self.assertListEqual(result, [(" Dette  er en\nprøve!", (0, 20))])

    def test_spans(self):
        result = list(self.__tokenizer.spans(" Dette  er en\nprøve!"))
        self.assertListEqual(result, [(0, 20)])

    def test_empty_input(self):
        self.assertListEqual(list(self.__tokenizer.strings("")), [])
        self.assertListEqual(list(self.__tokenizer.tokens("")), [])
        self.assertListEqual(list(self.__tokenizer.spans("")), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
