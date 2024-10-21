# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
import math
from context import in3120


class TestSparseDocumentVector(unittest.TestCase):

    def setUp(self):
        self._empty = in3120.SparseDocumentVector({})
        self._vector1 = in3120.SparseDocumentVector({"a": 0.4, "c": 1.2, "b": 0.9})
        self._vector2 = in3120.SparseDocumentVector({"c": 0.5, "a": 0.8, "x": 1.0})

    def test_dunderscore_len(self):
        self.assertEqual(0, len(self._empty))
        self.assertEqual(3, len(self._vector1))

    def test_dunderscore_contains(self):
        self.assertEqual(True, "c" in self._vector1)
        self.assertEqual(False, "q" in self._vector1)

    def test_dunderscore_getitem(self):
        self.assertEqual(1.2, self._vector1["c"])
        self.assertEqual(0.0, self._vector1["q"])

    def test_dunderscore_setitem(self):
        values = {"c": 0.5, "a": 0.8, "x": 1.0, "y": 2.0}
        vector = in3120.SparseDocumentVector(values)
        self.assertEqual(1.0, vector["x"])
        self.assertEqual(0.0, vector["q"])
        vector["x"] = 21
        vector["q"] = 70
        self.assertEqual(21, vector["x"])
        self.assertEqual(70, vector["q"])

    def test_dot_product(self):
        self.assertAlmostEqual(0.0, self._empty.dot(self._vector1), 6)
        self.assertAlmostEqual(0.0, self._vector1.dot(self._empty), 6)
        self.assertAlmostEqual(0.4 * 0.8 + 1.2 * 0.5, self._vector1.dot(self._vector2), 6)
        self.assertAlmostEqual(0.4 * 0.8 + 1.2 * 0.5, self._vector2.dot(self._vector1), 6)

    def test_length(self):
        self.assertAlmostEqual(0.0, self._empty.get_length(), 6)
        self.assertAlmostEqual(math.sqrt(0.4**2 + 0.9**2 + 1.2**2), self._vector1.get_length(), 6)
        self.assertAlmostEqual(math.sqrt(0.8**2 + 0.5**2 + 1.0**2), self._vector2.get_length(), 6)

    def test_scale(self):
        values = {"c": 0.5, "a": 0.8, "x": 1.0, "y": 2.0}
        vector = in3120.SparseDocumentVector(values)
        factor = 0.210470
        vector.scale(factor)
        self.assertAlmostEqual(factor * math.sqrt(0.5**2 + 0.8**2 + 1.0**2 + 2.0**2), vector.get_length(), 6)
        self.assertAlmostEqual(factor * 0.5, vector["c"], 6)
        self.assertAlmostEqual(factor * 0.8, vector["a"], 6)
        self.assertAlmostEqual(factor * 1.0, vector["x"], 6)
        self.assertAlmostEqual(factor * 2.0, vector["y"], 6)

    def test_scale_zero(self):
        values = {"c": 0.5, "a": 0.8, "x": 1.0, "y": 2.0}
        vector = in3120.SparseDocumentVector(values)
        vector.scale(0.0)
        self.assertEqual(0, len(vector))
        self.assertEqual(0, vector.get_length())

    def test_cosine(self):
        self.assertAlmostEqual(0.0, self._empty.cosine(self._vector1), 6)
        self.assertAlmostEqual(0.0, self._vector1.cosine(self._empty), 6)
        self.assertAlmostEqual(0.0, self._empty.cosine(self._empty), 6)
        self.assertAlmostEqual(1.0, self._vector1.cosine(self._vector1), 6)
        inner12 = 0.4 * 0.8 + 1.2 * 0.5
        length1 = math.sqrt(0.4**2 + 0.9**2 + 1.2**2)
        length2 = math.sqrt(0.8**2 + 0.5**2 + 1.0**2)
        self.assertAlmostEqual(inner12 / (length1 * length2), self._vector1.cosine(self._vector2), 6)
        self.assertAlmostEqual(inner12 / (length1 * length2), self._vector2.cosine(self._vector1), 6)

    def test_normalize_nonempty(self):
        vector = in3120.SparseDocumentVector({"a": 4.1, "c": 1.2, "b": 8.9})
        self.assertNotAlmostEqual(1.0, vector.get_length(), 6)
        vector.normalize()
        self.assertAlmostEqual(1.0, vector.get_length(), 6)

    def test_normalize_empty(self):
        vector = in3120.SparseDocumentVector({})
        self.assertAlmostEqual(0.0, vector.get_length(), 6)
        vector.normalize()
        self.assertAlmostEqual(0.0, vector.get_length(), 6)

    def test_top(self):
        self.assertListEqual(list(self._vector1.top(0)), [])
        self.assertListEqual(list(self._vector1.top(1)), [("c", 1.2)])
        self.assertListEqual(list(self._vector1.top(2)), [("c", 1.2), ("b", 0.9)])
        self.assertListEqual(list(self._vector1.top(3)), [("c", 1.2), ("b", 0.9), ("a", 0.4)])
        self.assertListEqual(list(self._vector1.top(4)), [("c", 1.2), ("b", 0.9), ("a", 0.4)])
        with self.assertRaises(AssertionError):
            list(self._vector1.top(-1))

    def test_truncate(self):
        vector = in3120.SparseDocumentVector({"c": 0.5, "a": 0.8, "x": 1.0, "y": 2.0})
        length = vector.get_length()
        vector.truncate(100)
        self.assertEqual(length, vector.get_length())
        vector.truncate(2)
        self.assertListEqual(list(vector.top(100)), [("y", 2.0), ("x", 1.0)])
        self.assertTrue(length > vector.get_length())
        with self.assertRaises(AssertionError):
            vector.truncate(-1)

    def test_centroid(self):
        centroid = in3120.SparseDocumentVector.centroid([self._vector1, self._vector2, self._empty])
        expected = {
            "a": (0.4 + 0.8 + 0.0) / 3,
            "b": (0.9 + 0.0 + 0.0) / 3,
            "c": (1.2 + 0.5 + 0.0) / 3,
            "x": (0.0 + 1.0 + 0.0) / 3,
        }
        pairs = list(centroid.top(100))
        self.assertEqual(4, len(pairs))
        for term, weight in pairs:
            self.assertTrue(term in expected)
            self.assertAlmostEqual(weight, expected[term], 6)

    def test_only_non_zero_elements_are_kept(self):
        vector = in3120.SparseDocumentVector({"a": 1.5, "b": 0.0})
        self.assertEqual(1, len(vector))
        vector.scale(0)
        self.assertEqual(0, len(vector))


if __name__ == '__main__':
    unittest.main(verbosity=2)
