# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=bare-except

import json
import os
import re
import tempfile
import unittest
from context import in3120


class TestExpressionComposer(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._grammar = {

            # A simple, little grammar.
            "top": {
                "expression": "{baz} tea {foo} {bar} coffee",
                "capture": True
            },
            "foo": "chocolate",
            "bar": "{baz} strawberry {baz}",
            "baz": {
                "expression": "bread|scones|buns",
                "capture": True
            },

            # An expression that should not be decorated, but left as-is.
            "undecorated": {
                "expression": "a-z",
                "decorate": False
            },

            # An expression that has contradictory settings: Capture implies decoration.
            "contradictory": {
                "expression": "a-z",
                "capture": True,
                "decorate": False
            },

            # An expression with a reference that should not get expanded.
            "unexpandable": "This is an expression with {{top}} doubly curly braces",

            # An unresolvable expression. For testing detection of dangling references.
            "unresolvable": "This is a {dangling} reference.",

            # Some recursively defined patterns. For testing loop detection.
            "recursive0": "{recursive0}",
            "recursive1a": "{recursive1b}",
            "recursive1b": "{recursive1a}",

            # A fancy, complex grammar. Detects sequences of capitalized words, except if they start a new sentence.
            "whitespace": "[\\s\\n\\r\\t]",
            "uppercase": "[A-ZÆØÅ]",
            "lowercase": "[a-zæøå]",
            "digit": "[0-9]",
            "break": "[.:;!?]",
            "spaces": "{whitespace}{{1,3}}",
            "capitalized": "\\b{uppercase}{lowercase}+\\b",
            "integer": "\\b[0-9]+\\b",
            "fluff": "\\bof|the|and|von|der|de\\b",
            "csequence1": "{capitalized}{csequence2}",
            "csequence2": "(?:{spaces}{capitalized})*",
            "fsequence": "(?:{spaces}{fluff}){{0,2}}",
            "forbidden": "(?<!\\A)(?<!{break}{whitespace})",
            "interesting1": "{csequence1}{fsequence}{csequence2}(?:{spaces}{integer})?",
            "interesting2": "{forbidden}{interesting1}"

        }
        cls._composer = in3120.ExpressionComposer(cls._grammar)

    def test_recursive_patterns(self):
        with self.assertRaises(KeyError):
            self._composer.compose("recursive0")
        with self.assertRaises(KeyError):
            self._composer.compose("recursive1a")

    def test_unresolvable_patterns(self):
        with self.assertRaises(KeyError):
            self._composer.compose("missing")
        with self.assertRaises(KeyError):
            self._composer.compose("unresolvable")

    def test_unexpandable_reference(self):
        self.assertEqual(self._composer.compose("unexpandable"),
                         "(?:This is an expression with {top} doubly curly braces)")

    def test_undecorated_reference(self):
        self.assertEqual(self._composer.compose("undecorated"), "a-z")

    def test_contradictory_reference(self):
        with self.assertRaises(ValueError):
            self._composer.compose("contradictory")

    def test_simple_expansion_with_named_groups(self):
        expression = self._composer.compose("top")
        self.assertEqual(expression,
                         "(?P<top>(?P<baz_2>bread|scones|buns) tea (?:chocolate) (?:(?P<baz>bread|scones|buns) " +
                         "strawberry (?P<baz_1>bread|scones|buns)) coffee)")
        pattern = re.compile(expression)
        buffer = "the great bread tea chocolate scones strawberry buns coffee disaster"
        groups = pattern.search(buffer).groupdict()
        self.assertEqual(4, len(groups))
        self.assertTrue("top" in groups)
        self.assertTrue("baz" in groups)
        self.assertTrue("baz_1" in groups)
        self.assertTrue("baz_2" in groups)
        self.assertEqual(groups["top"], "bread tea chocolate scones strawberry buns coffee")
        self.assertTrue(groups["baz"] in ("scones", "bread", "buns"))
        self.assertTrue(groups["baz_1"] in ("scones", "bread", "buns"))
        self.assertTrue(groups["baz_2"] in ("scones", "bread", "buns"))
        self.assertNotEqual(groups["baz"], groups["baz_1"])
        self.assertNotEqual(groups["baz"], groups["baz_2"])
        self.assertNotEqual(groups["baz_1"], groups["baz_2"])

    def test_validity_of_generated_expressions(self):
        for root in ("top", "foo", "bar", "baz", "interesting2"):
            expression = self._composer.compose(root)
            try:
                re.compile(expression)
            except:
                self.fail(expression)

    def test_complex_expansion(self):
        expression = self._composer.compose("interesting2")
        pattern = re.compile(expression)
        buffer = "So The Lord of the Rings was a movie. And Windows 2000 was an operating system."
        self.assertListEqual(pattern.findall(buffer), ["The Lord of the Rings", "Windows 2000"])

    def test_compose_from_named_file_with_comments(self):
        file = tempfile.NamedTemporaryFile(mode="w+t", encoding="utf-8", delete=False)
        try:
            file.write("# This is a comment line.\n")
            file.write("  // This is another, alternate-syntax comment line, with some leading whitespace.\n")
            file.write(json.dumps(self._grammar))
            file.write("\n# Another comment line, at the end this time.\n")
            file.flush()
            file.close()
            expression = in3120.ExpressionComposer.from_filename(file.name, "interesting2")
            self.assertTrue(expression)
        finally:
            os.unlink(file.name)  # Done manually instead of using 'with' because Windows.

    def test_compose_from_grammar(self):
        expression = in3120.ExpressionComposer.from_grammar(self._grammar, "interesting2")
        self.assertTrue(expression)


if __name__ == '__main__':
    unittest.main(verbosity=2)
