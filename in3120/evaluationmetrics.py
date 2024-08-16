# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

from math import log2
from statistics import mean
from typing import Iterable, Iterator, Tuple, List


class EvaluationMetrics:
    """
    Utility class for computing various evaluation metrics for ranked retrieval.
    See https://nlp.stanford.edu/IR-book/pdf/08eval.pdf for details.

    Note that some evaluation metrics for unranked retrieval can be assessed by
    pretending that the results are ranked and then to consider the last value in
    the sequence of "@-scores". For example, from a list with 100 unranked elements,
    consider precision@100.
    """

    @staticmethod
    def precision_at(judgments: Iterable[bool]) -> Iterator[float]:
        """
        Given a sequence or ranked list of results, each result being either relevant or not,
        yields another sequence for precision@k for the corresponding values of k.
        """
        relevant = 0
        for position, is_relevant in enumerate(judgments, 1):
            if is_relevant:
                relevant += 1
            yield relevant / position

    @staticmethod
    def interpolated_precision_at(judgments: Iterable[bool]) -> Iterator[float]:
        """
        The interpolated precision value is a "smoothed" value of precision that
        preserves monotonicity of a precision-recall curve. The interpolated precision
        P' at a certain recall level R is defined as the highest precision P found for
        any recall level R' >= R.

        Note that recall does not decrease with increasing rank k, so if k' >= k then
        we also have that R(k') >= R(k).
        """
        precisions = list(EvaluationMetrics.precision_at(judgments))
        for i in range(len(precisions) - 2, -1, -1):
            precisions[i] = max(precisions[i], precisions[i + 1])
        yield from precisions

    @staticmethod
    def recall_at(judgments: Iterable[bool], total: int) -> Iterator[float]:
        """
        Given a sequence or ranked list of results, each result being either relevant or not,
        yields another sequence for recall@k for the corresponding values of k.

        The client needs to tell us how many relevant documents that exist in total, in case
        all relevant results are not present in the ranked list of results.
        """
        assert total > 0
        relevant = 0
        for is_relevant in judgments:
            if is_relevant:
                relevant += 1
            assert relevant <= total
            yield relevant / total

    @staticmethod
    def f_at(judgments: Iterable[bool], total: int, beta: float = 1.0) -> Iterator[float]:
        """
        Given a sequence or ranked list of results, each result being either relevant or not,
        yields another sequence for the F-measure for the corresponding values of k.

        The F-measure is the weighted harmonic mean of precision and recall. The β parameter
        controls the relative weighting, with β = 1 assigning equal weight to precision and
        recall. Values of β < 1 emphasize precision, while values of β > 1 emphasize recall.

        In some cases one might see a parameter α being used instead of β. The two are related
        via β² = (1 - α) / α, or, equivalently, α = 1 / (β² + 1).
        """
        assert beta >= 0
        for precision, recall in zip(EvaluationMetrics.precision_at(judgments), EvaluationMetrics.recall_at(judgments, total)):
            yield ((1 + beta**2) * (precision * recall)) / ((beta**2 * precision) + recall)

    @staticmethod
    def average_precision(judgments: List[bool]) -> float:
        """
        Computes the average precision@k value, constrained to only consider the values of k
        that correspond to the relevant documents. This is a basic building block for computing
        the mean average precision (MAP).
        """
        if len(judgments) == 0 or not any(judgments):
            return 0.0
        return mean(precision for is_relevant, precision in zip(judgments, EvaluationMetrics.precision_at(judgments)) if is_relevant)

    @staticmethod
    def mean_average_precision(judgments: List[List[bool]]) -> float:
        """
        Given a set of ranked lists of results, one result list per query, computes the
        mean average precision (MAP). MAP is basically the mean AP score, averaged over
        a number of queries. This metric could hence just as well have been called the
        average average precision score, but "mean average" arguably rolls off the tongue
        better than "average average".
        """
        if len(judgments) == 0:
            return 0.0
        return mean(EvaluationMetrics.average_precision(judgments2) for judgments2 in judgments)

    @staticmethod
    def discounted_cumulative_gain(gains: List[float]) -> float:
        """
        Computes the discounted cumulative gain (DCG) for a result set, given the gains
        at each position. This is a basic building block for computing the normalized DCG
        score. See https://en.wikipedia.org/wiki/Discounted_cumulative_gain for details.

        Note that a common alternative formulation, which places emphasis on retrieving
        highly relevant documents, can be be obtained if we transform the gains according
        to f(x) = 2ˣ - 1 prior to invoking this method.
        """
        return sum(gain / log2(position + 1) for position, gain in enumerate(gains, 1))

    @staticmethod
    def normalized_discounted_cumulative_gain(gains: List[float], perfect: List[float]) -> float:
        """
        Computes the normalized discounted cumulative gain (NDCG) for a result set, given the
        gains at each position and the gains of the perfect ordering. For more details, see
        https://en.wikipedia.org/wiki/Discounted_cumulative_gain.
        """
        assert 0 < len(gains) <= len(perfect)
        assert all(perfect[i] >= perfect[i + 1] for i in range(len(perfect) - 1))
        ideal = EvaluationMetrics.discounted_cumulative_gain(perfect[:len(gains)])
        assert ideal != 0.0
        return EvaluationMetrics.discounted_cumulative_gain(gains) / ideal

    @staticmethod
    def mean_normalized_discounted_cumulative_gain(gains: List[List[bool]], perfect: List[List[float]]) -> float:
        """
        Given a set of lists of gains and a set of perfect orderings, one result list per query, computes the
        mean NDCG score.
        """
        assert len(gains) == len(perfect)
        if len(gains) == 0:
            return 0.0
        return mean(EvaluationMetrics.normalized_discounted_cumulative_gain(gains2, perfect2) for gains2, perfect2 in zip(gains, perfect))

    @staticmethod
    def reciprocal_rank(judgments: Iterable[bool]) -> float:
        """
        Returns the reciprocal rank (RR). I.e., returns the inverse of the rank position of the
        first relevant document. This could be, e.g., the only clicked document.
        """
        for k, is_relevant in enumerate(judgments, 1):
            if is_relevant:
                return 1 / k
        return 0.0

    @staticmethod
    def mean_reciprocal_rank(judgments: List[Iterable[bool]]) -> float:
        """
        Returns the mean reciprocal rank (MRR), i.e., the RR averaged across multiple queries.
        See https://en.wikipedia.org/wiki/Mean_reciprocal_rank for details.
        """
        if len(judgments) == 0:
            return 0.0
        return mean(EvaluationMetrics.reciprocal_rank(judgments2) for judgments2 in judgments)

    @staticmethod
    def kendall_tau(preferences: List[Tuple[int, int]], ranking: List[int]) -> float:
        """
        Given a set of pairwise preferences, computes how well a given ranking
        adheres to these preferences. A pairwise preference (i, j) is interpreted
        as "document i should come before document j in the ranking".

        A return value of 1.0 indicates perfect agreement (i.e., the ranking
        respects all the preference pairs), whereas a return value of -1.0 indicates
        perfect disagreement (i.e., the ranking does not respect any of the
        preference pairs.) In actual applications values typically fall somewhere
        between these two extremes. For details, see https://en.wikipedia.org/wiki/Kendall_rank_correlation_coefficient.

        The current implementation simply ignores preference pairs that cannot be verified
        by the given ranking.
        """
        if len(preferences) == 0:
            return 0.0
        agreements = 0
        disagreements = 0
        for before, after in preferences:
            assert before != after
            try:
                i = ranking.index(before)
            except ValueError:
                i = -1
            try:
                j = ranking.index(after)
            except ValueError:
                j = -1
            if i == -1 and j == -1:
                continue
            if i == -1:
                disagreements += 1
            elif j == -1:
                agreements += 1
            elif i < j:
                agreements += 1
            else:
                disagreements += 1
        if agreements == 0 and disagreements == 0:
            return 0.0
        return (agreements - disagreements) / (agreements + disagreements)
