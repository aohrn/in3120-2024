# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from context import in3120


class TestTrie(unittest.TestCase):

    def setUp(self):
        self.__normalizer = in3120.SimpleNormalizer()
        self.__tokenizer = in3120.SimpleTokenizer()
        self.__root = in3120.Trie()
        self.__root.add(["abba", "ØRRET", "abb", "abbab", "abbor"], self.__normalizer, self.__tokenizer)

    def test_consume_and_final(self):
        root = self.__root
        self.assertTrue(not root.is_final())
        self.assertIsNone(root.consume("snegle"))
        node = root["ab"]
        self.assertTrue(not node.is_final())
        node = node.consume("b")
        node = node.consume("")
        self.assertTrue(node.is_final())
        self.assertEqual(node, root.consume("abb"))

    def test_containment(self):
        self.assertTrue("ørret" in self.__root)
        self.assertFalse("ørr" in self.__root)
        self.assertTrue("abbor" in self.__root)
        self.assertFalse("abborrrr" in self.__root)
        child = self.__root.child("a")
        self.assertTrue("bbor" in child)

    def test_dump_strings(self):
        root = in3120.Trie.from_strings(["elle", "eller", "ELLEN", "hurra   FOR deg"], self.__normalizer, self.__tokenizer)
        self.assertListEqual(list(root.strings()), ["elle", "ellen", "eller", "hurra for deg"])
        node = root.consume("el")
        self.assertListEqual(list(node.strings()), ["le", "len", "ler"])
        self.assertListEqual(list(node), ["le", "len", "ler"])

    def test_add_is_idempotent(self):
        root = in3120.Trie.from_strings(["abba", "ABBA", "ABBA", "abBa"], self.__normalizer, self.__tokenizer)
        self.assertListEqual(list(root.strings()), ["abba"])

    def test_transitions(self):
        root = self.__root
        self.assertListEqual(root.transitions(), ["a", "ø"])
        node = root.consume("abb")
        self.assertListEqual(node.transitions(), ["a", "o"])
        node = node.consume("o")
        self.assertListEqual(node.transitions(), ["r"])
        node = node.consume("r")
        self.assertListEqual(node.transitions(), [])

    def test_child(self):
        root = self.__root
        self.assertIsNotNone(root.child("a"))
        self.assertIsNone(root.child("ab"))
        child = root.child("a")
        child = child.child("b")
        child = child.child("b")
        self.assertIsNone(child.child(""))

    def test_with_meta_data(self):
        root = in3120.Trie.from_strings2([("aleksander", 2104), ("julaften", 2412), ("nei", None)], self.__normalizer, self.__tokenizer)
        self.assertFalse(root.has_meta())
        self.assertFalse(root.consume("aleks").is_final())
        self.assertFalse(root.consume("aleks").has_meta())
        self.assertIsNone(root.consume("aleks").get_meta())
        self.assertTrue(root.consume("aleksander").is_final())
        self.assertTrue(root.consume("aleksander").has_meta())
        self.assertEqual(root.consume("aleksander").get_meta(), 2104)
        self.assertTrue(root.consume("julaften").is_final())
        self.assertTrue(root.consume("julaften").has_meta())
        self.assertEqual(root.consume("julaften").get_meta(), 2412)
        self.assertTrue(root.consume("nei").is_final())
        self.assertFalse(root.consume("nei").has_meta())
        self.assertIsNone(root.consume("nei").get_meta())

    def test_add_is_idempotent_unless_meta_data_differs(self):
        root = in3120.Trie.from_strings2([("abba", 74), ("abba", 74)], self.__normalizer, self.__tokenizer)
        self.assertListEqual(list(root.strings()), ["abba"])
        self.assertEqual(root.consume("abba").get_meta(), 74)
        root = in3120.Trie()
        with self.assertRaises(AssertionError):
            root.add2([("abba", 74), ("abba", 99)], self.__normalizer, self.__tokenizer)


if __name__ == '__main__':
    unittest.main(verbosity=2)
