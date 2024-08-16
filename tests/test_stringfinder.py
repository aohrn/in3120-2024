# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from types import GeneratorType
from timeit import default_timer as timer
from context import in3120


class TestStringFinder(unittest.TestCase):

    def setUp(self):
        self.__normalizer = in3120.SimpleNormalizer()
        self.__tokenizer = in3120.SimpleTokenizer()

    def __simple_verify(self, finder, text, expected):
        matches = list(finder.scan(text))
        self.assertListEqual([(m["surface"], m["match"]) for m in matches], expected)

    def test_scan_matches_and_surface_forms_only(self):
        strings = ["romerike", "apple computer", "norsk", "norsk ørret", "sverige", "ørret", "banan", "a", "a b"]
        trie = in3120.Trie.from_strings(strings, self.__normalizer, self.__tokenizer)
        finder = in3120.StringFinder(trie, self.__normalizer, self.__tokenizer)
        self.__simple_verify(finder, "en Norsk     ØRRET fra romerike likte abba fra Sverige",
                             [("Norsk", "norsk"), ("Norsk ØRRET", "norsk ørret"), ("ØRRET", "ørret"), ("romerike", "romerike"), ("Sverige", "sverige")])
        self.__simple_verify(finder, "the apple is red", [])
        self.__simple_verify(finder, "", [])
        self.__simple_verify(finder, "apple computer banan foo sverige ben reddik fy fasan",
                             [("apple computer", "apple computer"), ("banan", "banan"), ("sverige", "sverige")])
        self.__simple_verify(finder, "a a b", [("a", "a"), ("a", "a"), ("a b", "a b")])

    def test_scan_matches_and_spans(self):
        strings = ["eple", "drue", "appelsin", "drue appelsin rosin banan papaya"]
        trie = in3120.Trie.from_strings(strings, self.__normalizer, self.__tokenizer)
        finder = in3120.StringFinder(trie, self.__normalizer, self.__tokenizer)
        results = list(finder.scan("et EPLE og en drue   appelsin  rosin banan papaya frukt"))
        self.assertListEqual(results, [{'surface': 'EPLE', 'span': (3, 7), 'match': 'eple', 'meta': None},
                                       {'surface': 'drue', 'span': (14, 18), 'match': 'drue', 'meta': None},
                                       {'surface': 'appelsin', 'span': (21, 29), 'match': 'appelsin', 'meta': None},
                                       {'surface': 'drue appelsin rosin banan papaya', 'span': (14, 49),
                                        'match': 'drue appelsin rosin banan papaya', 'meta': None}])

    def test_with_phonetic_normalizer_and_meta(self):
        normalizer = in3120.SoundexNormalizer()
        strings = ["Benedikt Richardson", "Smith"]
        trie = in3120.Trie.from_strings2(((x, x) for x in strings), normalizer, self.__tokenizer)
        finder = in3120.StringFinder(trie, normalizer, self.__tokenizer)
        results = list(finder.scan("The Benedict  Richards and Smithe conjecture was proven false!"))
        self.assertListEqual(results, [{'surface': 'Benedict Richards', 'span': (4, 22), 'match': 'B532 R263', 'meta': 'Benedikt Richardson'},
                                       {'surface': 'Smithe', 'span': (27, 33), 'match': 'S530', 'meta': 'Smith'}])

    def test_uses_yield(self):
        trie = in3120.Trie.from_strings(["foo"], self.__normalizer, self.__tokenizer)
        finder = in3120.StringFinder(trie, self.__normalizer, self.__tokenizer)
        matches = finder.scan("the foo bar")
        self.assertIsInstance(matches, GeneratorType, "Are you using yield?")

    def test_mesh_terms_in_cran_corpus(self):
        mesh = in3120.InMemoryCorpus("../data/mesh.txt")
        cran = in3120.InMemoryCorpus("../data/cran.xml")
        trie = in3120.Trie.from_strings((d["body"] or "" for d in mesh), self.__normalizer, self.__tokenizer)
        finder = in3120.StringFinder(trie, self.__normalizer, self.__tokenizer)
        self.__simple_verify(finder, cran[0]["body"], [("wing", "wing"), ("wing", "wing")])
        self.__simple_verify(finder, cran[3]["body"], [("solutions", "solutions"), ("skin", "skin"), ("friction", "friction")])
        self.__simple_verify(finder, cran[1254]["body"], [("electrons", "electrons"), ("ions", "ions")])

    def test_with_unigram_tokenizer_for_finding_arbitrary_substrings(self):
        tokenizer = in3120.UnigramTokenizer()
        trie = in3120.Trie.from_strings(["needle", "banana"], self.__normalizer, self.__tokenizer)
        finder = in3120.StringFinder(trie, self.__normalizer, tokenizer)
        results = list(finder.scan("thereisaneEdleinthishaystacksomewhereiamsureotherwisebananapineapple"))
        self.assertListEqual(results, [{'surface': 'neEdle', 'span': (8, 14), 'match': 'needle', 'meta': None},
                                       {'surface': 'banana', 'span': (53, 59), 'match': 'banana', 'meta': None}])

    def test_relative_insensitivity_to_dictionary_size(self):
        mesh = in3120.InMemoryCorpus("../data/mesh.txt")  # Contains more than 25K strings, including "medulla oblongata".
        trie1 = in3120.Trie.from_strings(["medulla oblongata"], self.__normalizer, self.__tokenizer)
        trie2 = in3120.Trie.from_strings((d["body"] or "" for d in mesh), self.__normalizer, self.__tokenizer)
        finder1 = in3120.StringFinder(trie1, self.__normalizer, self.__tokenizer)
        finder2 = in3120.StringFinder(trie2, self.__normalizer, self.__tokenizer)
        buffer = "The injury was located close to the medulla oblongata."
        finders = [finder1, finder2]
        times = [9999999, 9999999]
        for _ in range(10):
            for i in range(2):
                start = timer()
                results = list(finders[i].scan(buffer))
                end = timer()
                self.assertEqual(1, len(results))
                times[i] = min(times[i], end - start)
        ratio = times[1] / times[0]
        slack = 0.30  # Allow quite a bit of slack, to avoid spurious test failures.
        self.assertLessEqual(ratio - slack, 1.0)
        self.assertLessEqual(1.0, ratio + slack)


if __name__ == '__main__':
    unittest.main(verbosity=2)
