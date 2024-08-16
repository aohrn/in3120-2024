# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from context import in3120


class TestEditTable(unittest.TestCase):

    def test_stringify(self):
        rows = "elephantischer"
        columns = "relevantisher"
        stringified = in3120.EditTable(rows, columns).stringify()
        lines = [line for line in stringified.split("\n") if line]
        self.assertEqual(2 + len(rows), len(lines))
        header = lines[0].replace(" ", "")
        self.assertEqual(header, columns)
        reconstructed = [column for column in lines[1].split(" ") if column]
        self.assertEqual(len(reconstructed), 1 + len(columns))
        labels = []
        for i in range(2, len(lines)):
            reconstructed = [column for column in lines[i].split(" ") if column]
            labels.append(reconstructed[0])
            self.assertEqual(len(reconstructed), 2 + len(columns))
        self.assertEqual("".join(labels), rows)

    def test_distance(self):
        self.assertEqual(3, in3120.EditTable("cat", "dog").distance())
        self.assertEqual(1, in3120.EditTable("elephant", "elephnat").distance())
        self.assertEqual(3, in3120.EditTable("elephant", "relevant").distance())
        self.assertEqual(2, in3120.EditTable("object", "inject").distance())
        self.assertEqual(7, in3120.EditTable("bullfrog", "frogger").distance())
        self.assertEqual(0, in3120.EditTable("same", "same").distance())


if __name__ == '__main__':
    unittest.main(verbosity=2)
