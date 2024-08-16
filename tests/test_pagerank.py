# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name

import unittest
from context import in3120


class TestPageRank(unittest.TestCase):

    def setUp(self):
        self._exercise_21_6 = [
            [1],        # 0 → 1
            [0, 2],     # 1 → 0, 1 → 2
            [1],        # 2 → 1
        ]
        self._figure_21_4 = [
            [2],        # 0 → 2
            [1, 2],     # 1 → 1, 1 → 2
            [0, 2, 3],  # 2 → 0, 2 → 2, 2 → 3
            [3, 4],     # 3 → 3, 3 → 4
            [6],        # 4 → 6
            [5, 6],     # 5 → 5, 5 → 6
            [3, 4, 6],  # 6 → 3, 6 → 4, 6 → 6
        ]

    def test_example_in_section_21_2_2_in_textbook_transition_matrix(self):
        P = in3120.PageRank(self._exercise_21_6, 0.5).transition_matrix()
        expected = [
            [1 / 6,  2 / 3, 1 / 6 ],
            [5 / 12, 1 / 6, 5 / 12],
            [1 / 6,  2 / 3, 1 / 6 ],
        ]
        self.assertEqual(3, len(P))
        all(self.assertEqual(3, len(P[i])) for i in range(3))
        all(self.assertAlmostEqual(P[i][j], expected[i][j], 6) for i in range(3) for j in range(3))

    def test_example_in_section_21_2_2_in_textbook_single_step(self):
        initial = [1, 0, 0]
        figure_21_3 = [
            [1 / 6,  2 / 3,  1 / 6 ],
            [1 / 3,  1 / 3,  1 / 3 ],
            [1 / 4,  1 / 2,  1 / 4 ],
            [7 / 24, 5 / 12, 7 / 24],
        ]
        computer = in3120.PageRank(self._exercise_21_6, 0.5)
        x = initial
        for row in figure_21_3:
            x = computer.step(x)
            self.assertEqual(3, len(x))
            all(self.assertAlmostEqual(x[i], row[i], 6) for i in range(3))

    def test_example_in_section_21_2_2_in_textbook_pagerank(self):
        pagerank = in3120.PageRank(self._exercise_21_6, 0.5).pagerank()
        expected = [5 / 18, 4 / 9, 5 / 18]
        self.assertEqual(3, len(pagerank))
        all(self.assertAlmostEqual(pagerank[i], expected[i], 6) for i in range(3))

    def test_example_21_1_from_textbook_transition_matrix(self):
        P = in3120.PageRank(self._figure_21_4, 0.14).transition_matrix()
        expected = [
            [0.02, 0.02, 0.88, 0.02, 0.02, 0.02, 0.02],
            [0.02, 0.45, 0.45, 0.02, 0.02, 0.02, 0.02],
            [0.31, 0.02, 0.31, 0.31, 0.02, 0.02, 0.02],
            [0.02, 0.02, 0.02, 0.45, 0.45, 0.02, 0.02],
            [0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.88],
            [0.02, 0.02, 0.02, 0.02, 0.02, 0.45, 0.45],
            [0.02, 0.02, 0.02, 0.31, 0.31, 0.02, 0.31],
        ]
        self.assertEqual(7, len(P))
        all(self.assertEqual(7, len(P[i])) for i in range(7))
        all(self.assertAlmostEqual(P[i][j], expected[i][j], 2) for i in range(7) for j in range(7))

    def test_example_21_1_from_textbook_pagerank(self):
        pagerank = in3120.PageRank(self._figure_21_4, 0.14).pagerank()
        expected = [0.05, 0.04, 0.11, 0.25, 0.21, 0.04, 0.31]
        self.assertEqual(7, len(pagerank))
        all(self.assertAlmostEqual(pagerank[i], expected[i], 2) for i in range(7))

    def test_empty_graph(self):
        computer = in3120.PageRank([], 0.5)
        self.assertEqual([], computer.transition_matrix())
        self.assertEqual([], computer.step([]))
        self.assertEqual([], computer.pagerank())

    def test_invalid_teleportation_probability(self):
        for alpha in [0, 1.5]:
            with self.assertRaises(AssertionError):
                in3120.PageRank([[1], [0, 2], [1]], alpha)

    def test_invalid_adjacency_lists(self):
        with self.assertRaises(AssertionError):
            in3120.PageRank([[1], [0, 5], [1]], 0.5)
        with self.assertRaises(AssertionError):
            in3120.PageRank(None, 0.5)
        with self.assertRaises(AssertionError):
            in3120.PageRank([[1], [0, 5], None], 0.5)

    def test_invalid_probability_vector(self):
        computer = in3120.PageRank(self._exercise_21_6, 0.5)
        with self.assertRaises(AssertionError):
            computer.step(None)
        with self.assertRaises(AssertionError):
            computer.step([0.0, 1.0])


if __name__ == '__main__':
    unittest.main(verbosity=2)
