# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from context import in3120


class TestPorterNormalizer(unittest.TestCase):

    def setUp(self):
        self.__normalizer = in3120.PorterNormalizer()

    def test_normalize_no_input(self):
        for argument in ["", None]:
            with self.assertRaises(ValueError):
                self.__normalizer.normalize(argument)

    def test_normalize_weird_inputs(self):
        self.assertEqual(self.__normalizer.normalize("!"), "!")
        self.assertEqual(self.__normalizer.normalize("øhRn"), "øhrn")
        self.assertEqual(self.__normalizer.normalize("bæ?"), "bæ?")
        self.assertEqual(self.__normalizer.normalize("ing"), "ing")
        self.assertEqual(self.__normalizer.normalize("eed"), "eed")
        self.assertEqual(self.__normalizer.normalize("oed"), "o")

    def test_normalize_exceptions(self):
        self.assertEqual(self.__normalizer.normalize("inning"), "inning")
        self.assertEqual(self.__normalizer.normalize("innings"), "inning")

    def test_normalize_short_inputs(self):
        self.assertEqual(self.__normalizer.normalize("a"), "a")
        self.assertEqual(self.__normalizer.normalize("aa"), "aa")

    def test_normalize_textbook_example(self):
        buffer = """
        Such an analysis can reveal features that are not easily visible from
        the variations in the individual genes and can lead to a picture of
        expression that is more biologically transparent and accessible to
        interpretation  
        """
        result = " ".join([self.__normalizer.normalize(token) for token in buffer.split()])
        expected = "".join([
            "such an analysi can reveal featur that are not easili visibl from ",
            "the variat in the individu gene and can lead to a pictur of ",
            "express that is more biolog transpar and access to interpret",
        ])
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
