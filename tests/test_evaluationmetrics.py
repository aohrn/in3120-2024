# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=too-many-public-methods

import unittest
import random
from context import in3120


class TestEvaluationMetrics(unittest.TestCase):

    def test_precision_at(self):
        ps = in3120.EvaluationMetrics.precision_at([True, False, True, True, False])
        expected = [1 / 1, 1 / 2, 2 / 3, 3 / 4, 3 / 5]
        for p1, p2 in zip(ps, expected):
            self.assertAlmostEqual(p1, p2, 7)

    def test_interpolated_precision_at(self):
        for _ in range(5):
            judgments = [bool(random.getrandbits(1)) for _ in range(20)]
            ips = list(in3120.EvaluationMetrics.interpolated_precision_at(judgments))
            self.assertEqual(ips[0], max(in3120.EvaluationMetrics.precision_at(judgments)))
            self.assertTrue(all(ips[i] >= ips[i + 1] for i in range(len(ips) - 1)))

    def test_recall_at_1(self):
        rs = in3120.EvaluationMetrics.recall_at([True, False, True, True, False], 3)
        expected = [1 / 3, 1 / 3, 2 / 3, 3 / 3, 3 / 3]
        for r1, r2 in zip(rs, expected):
            self.assertAlmostEqual(r1, r2, 7)

    def test_recall_at_2(self):
        for _ in range(5):
            judgments = [bool(random.getrandbits(1)) for _ in range(20)]
            rs = list(in3120.EvaluationMetrics.recall_at(judgments, len(judgments)))
            self.assertTrue(all(rs[i] <= rs[i + 1] for i in range(len(rs) - 1)))

    def test_f_at(self):
        fs = in3120.EvaluationMetrics.f_at([True, False, True, True, False], 3, 1.0)
        ps = in3120.EvaluationMetrics.precision_at([True, False, True, True, False])
        rs = in3120.EvaluationMetrics.recall_at([True, False, True, True, False], 3)
        expected = [(2 * p * r) / (p + r) for p, r in zip(ps, rs)]
        for f1, f2 in zip(fs, expected):
            self.assertAlmostEqual(f1, f2, 7)

    def test_recall_at_barfs(self):
        for total in (-1, 0, 1, 2):
            with self.assertRaises(AssertionError):
                list(in3120.EvaluationMetrics.recall_at([True, False, True, True, False], total))

    def test_f_at_barfs(self):
        with self.assertRaises(AssertionError):
            list(in3120.EvaluationMetrics.f_at([True, False, True, True, False], 3, -0.5))

    def test_average_precision(self):
        ap = in3120.EvaluationMetrics.average_precision([True, False, True, False, True])
        expected = ((1 / 1) + (2 / 3) + (3 / 5)) / 3
        self.assertAlmostEqual(ap, expected, 7)

    def test_average_precision_corner_cases(self):
        self.assertEqual(in3120.EvaluationMetrics.average_precision([]), 0.0)
        self.assertEqual(in3120.EvaluationMetrics.average_precision([False]), 0.0)

    def test_mean_average_precision(self):
        ranking1 = [True, False, True, False, False, True, False, False, True, True]
        ranking2 = [False, True, False, False, True, False, True, False, False, False]
        mapscore = in3120.EvaluationMetrics.mean_average_precision([ranking1, ranking2])
        ap1 = in3120.EvaluationMetrics.average_precision(ranking1)
        ap2 = in3120.EvaluationMetrics.average_precision(ranking2)
        self.assertAlmostEqual(mapscore, (ap1 + ap2) / 2, 7)
        self.assertAlmostEqual(mapscore, 0.5325, 4)

    def test_mean_average_precision_corner_cases(self):
        self.assertEqual(in3120.EvaluationMetrics.mean_average_precision([]), 0.0)
        self.assertEqual(in3120.EvaluationMetrics.mean_average_precision([[], []]), 0.0)
        self.assertEqual(in3120.EvaluationMetrics.mean_average_precision([[False], [False]]), 0.0)

    def test_discounted_cumulative_gain(self):
        gains = [3, 2, 3, 0, 1, 2]
        dcg = in3120.EvaluationMetrics.discounted_cumulative_gain(gains)
        self.assertAlmostEqual(dcg, 6.861, 3)

    def test_discounted_cumulative_gain_corner_cases(self):
        self.assertEqual(in3120.EvaluationMetrics.discounted_cumulative_gain([]), 0.0)

    def test_normalized_discounted_cumulative_gain(self):
        gains = [3, 2, 3, 0, 1, 2]
        perfect = [3, 3, 3, 2, 2, 2, 1, 0]
        ndcg = in3120.EvaluationMetrics.normalized_discounted_cumulative_gain(gains, perfect)
        self.assertAlmostEqual(ndcg, 0.785, 3)

    def test_normalized_discounted_cumulative_gain_corner_cases(self):
        with self.assertRaises(AssertionError):
            in3120.EvaluationMetrics.normalized_discounted_cumulative_gain([1, 2, 3], [0, 0, 0])
        with self.assertRaises(AssertionError):
            in3120.EvaluationMetrics.normalized_discounted_cumulative_gain([], [])
        with self.assertRaises(AssertionError):
            in3120.EvaluationMetrics.normalized_discounted_cumulative_gain([1, 0, 3], [3, 3])
        with self.assertRaises(AssertionError):
            in3120.EvaluationMetrics.normalized_discounted_cumulative_gain([1, 0, 3], [3, 1, 3])

    def test_mean_normalized_discounted_cumulative_gain(self):
        gains1 = [3, 2, 3, 0, 1, 2]
        perfect1 = [3, 3, 3, 2, 2, 2, 1, 0]
        gains2 = [1, 3, 3]
        perfect2 = [3, 3, 3]
        mndcgscore = in3120.EvaluationMetrics.mean_normalized_discounted_cumulative_gain([gains1, gains2], [perfect1, perfect2])
        ndcg1 = in3120.EvaluationMetrics.normalized_discounted_cumulative_gain(gains1, perfect1)
        ndcg2 = in3120.EvaluationMetrics.normalized_discounted_cumulative_gain(gains2, perfect2)
        self.assertAlmostEqual(mndcgscore, (ndcg1 + ndcg2) / 2, 7)
        self.assertAlmostEqual(mndcgscore, 0.736, 3)

    def test_mean_normalized_discounted_cumulative_gain_corner_cases(self):
        with self.assertRaises(AssertionError):
            in3120.EvaluationMetrics.mean_normalized_discounted_cumulative_gain([[1, 2, 3]], [[3, 3, 3], [1, 1, 1]])

    def test_reciprocal_rank(self):
        self.assertEqual(in3120.EvaluationMetrics.reciprocal_rank([]), 0.0)
        self.assertEqual(in3120.EvaluationMetrics.reciprocal_rank([False]), 0.0)
        self.assertEqual(in3120.EvaluationMetrics.reciprocal_rank([True, False]), 1 / 1)
        self.assertEqual(in3120.EvaluationMetrics.reciprocal_rank([False, True]), 1 / 2)
        self.assertAlmostEqual(in3120.EvaluationMetrics.reciprocal_rank([False, False, True, True]), 1 / 3, 7)

    def test_mean_reciprocal_rank(self):
        mrr = in3120.EvaluationMetrics.mean_reciprocal_rank([[False, True], [False, False, True, True]])
        self.assertAlmostEqual(mrr, ((1 / 2) + (1 / 3)) / 2, 7)

    def test_kendall_tau_1(self):
        preferences = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
        ranking = [1, 3, 2, 4]
        tau = in3120.EvaluationMetrics.kendall_tau(preferences, ranking)
        self.assertAlmostEqual(tau, (5 - 1) / (5 + 1), 7)

    def test_kendall_tau_2(self):
        preferences = [(1, 2), (42, 3), (1, 23), (98, 56)]
        ranking = [1, 3, 2, 4]
        tau = in3120.EvaluationMetrics.kendall_tau(preferences, ranking)
        self.assertAlmostEqual(tau, (2 - 1) / (2 + 1), 7)


if __name__ == '__main__':
    unittest.main(verbosity=2)
