# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from typing import Optional
from context import in3120


class TestDocumentPipeline(unittest.TestCase):

    def setUp(self) -> None:
        self.__extractor = in3120.ShallowCaseExtractor()
        normalizer = in3120.DummyNormalizer()
        tokenizer = in3120.SimpleTokenizer()
        us_state_capitals = in3120.Trie()
        us_state_capitals.add(["Phoenix", "New York City", "Sacramento", "Little Rock"], normalizer, tokenizer)
        self.__capitalfinder = in3120.StringFinder(us_state_capitals, normalizer, tokenizer)

    def test_missing_processors(self):
        for processors in (None, [None], [None, lambda d: d]):
            with self.assertRaises(AssertionError):
                in3120.DocumentPipeline(processors)

    def _compute_gog_from_foo(self, document: in3120.Document) -> in3120.Document:
        document["gog"] = ", ".join(self.__extractor.extract(document["foo"], {}))
        return document

    def _compute_bib_from_foo(self, document: in3120.Document) -> in3120.Document:
        document["bib"] = ", ".join([m["match"] for m in self.__capitalfinder.scan(document["foo"])])
        return document

    def _lowercase_gog_and_increment_bar(self, document: in3120.Document) -> in3120.Document:
        document["gog"] = document["gog"].lower()
        document["bar"] = document["bar"] + 1
        return document

    def _drop_if_foo_is_1000(self, document: in3120.Document) -> Optional[in3120.Document]:
        return None if document["foo"] == 1000 else document

    def test_basic_processing(self):
        document = in3120.InMemoryDocument(21, {"foo": "I have been to Radio City Music Hall in New York City in the United States.", "bar": 1970, "baz": "Another field."})
        pipeline = in3120.DocumentPipeline([self._compute_gog_from_foo, self._compute_bib_from_foo, self._lowercase_gog_and_increment_bar])
        document = pipeline(document)
        self.assertEqual(document["foo"], "I have been to Radio City Music Hall in New York City in the United States.")
        self.assertEqual(document["bar"], 1971)
        self.assertEqual(document["baz"], "Another field.")
        self.assertEqual(document["gog"], "radio city music hall, new york city, united states")
        self.assertEqual(document["bib"], "New York City")

    def test_dropped_documents(self):
        pipeline = in3120.DocumentPipeline([self._drop_if_foo_is_1000])
        self.assertIsNone(pipeline.process_document(in3120.InMemoryDocument(10, {"foo": 1000})))
        self.assertIsNotNone(pipeline.process_document(in3120.InMemoryDocument(10, {"foo": 999})))


if __name__ == '__main__':
    unittest.main(verbosity=2)
