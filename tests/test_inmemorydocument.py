# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from context import in3120


class TestInMemoryDocument(unittest.TestCase):

    def test_invalid_constructor_arguments(self):
        with self.assertRaises(AssertionError):
            in3120.InMemoryDocument(None, {})
        with self.assertRaises(AssertionError):
            in3120.InMemoryDocument(1, None)

    def test_set_field(self):
        document = in3120.InMemoryDocument(21, {"foo": "This is some text.", "bar": 1970, "baz": "Another field."})
        with self.assertRaises(AssertionError):
            document.set_field(None, "This is bananas.")
        document.set_field("wtf", "Bonanza!")
        self.assertEqual(document["wtf"], "Bonanza!")
        document["omg"] = "Foobar?"
        self.assertEqual(document["omg"], "Foobar?")

    def test_get_field(self):
        document = in3120.InMemoryDocument(21, {"foo": "This is some text.", "bar": 1970, "baz": "Another field."})
        self.assertEqual(document.get_document_id(), 21)
        self.assertEqual(document.document_id, 21)
        self.assertEqual(document.get_field("foo", None), "This is some text.")
        self.assertEqual(document["foo"], "This is some text.")
        self.assertEqual(document.get_field("bar", None), 1970)
        self.assertEqual(document["bar"], 1970)
        self.assertEqual(document.get_field("baz", None), "Another field.")
        self.assertEqual(document["baz"], "Another field.")
        self.assertIsNone(document["wtf"])


if __name__ == '__main__':
    unittest.main(verbosity=2)
