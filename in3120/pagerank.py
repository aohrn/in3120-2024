# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=cell-var-from-loop

from typing import List


class PageRank:
    """
    A simple PageRank computer. See Section 21.2 in https://nlp.stanford.edu/IR-book/pdf/21link.pdf
    for details. This implementation is slow and not optimized, and primarily intended for pedagogical
    purposes and very small graphs.
    """

    def __init__(self, adjacencies: List[List[int]], alpha: float):
        """
        Given a simple adjacency list for each node in a graph and a teleportation probability α,
        constructs the matrix P of transition probabilities in the induced Markov chain.
        """
        # How many nodes are there? Align naming with textbook.
        self._N : int = len(adjacencies or [])

        # The adjacency lists must define a valid N-by-N matrix.
        assert adjacencies is not None
        assert all(adjacencies[i] is not None for i in range(self._N))
        assert all(0 <= adjacencies[i][j] < self._N for i in range(self._N) for j in range(len(adjacencies[i])))

        # The graph might have islands and dead ends. A teleportation probability α that is
        # non-zero will guarantee us that it's possible to get from one node to any
        # other node in finite time. We then say that the Markov chain is ergodic, i.e., it's
        # irreducible and aperiodic. This in turn ensures that we will converge to a steady-state
        # solution when we iterate, i.e., that the PageRank values actually exist and are
        # well-defined.
        assert 0 < alpha <= 1

        # Create a dense representation of the N-by-N transition probability matrix P from the sparse
        # adjacency list representation. Initialize it with zeros here and compute the actual values
        # below. Align naming with textbook.
        self._P : List[List[float]] = [[0] * self._N for _ in range(self._N)]

        # Compute P, row by row. For a given node we can imagine having a "teleportation budget" of α that we
        # smear uniformly out over all nodes (including itself), and an "outlink budget" of (1 - α) that we smear
        # uniformly out over all nodes to which we have outgoing links. We can imagine extensions where the values are
        # not smeared out uniformly but instead follow some non-uniform distribution, e.g., to compute a
        # topic-specific PageRank or a personalized PageRank. The principal left eigenvector of this matrix
        # corresponds to the PageRank values.
        for i in range(self._N):

            # The set of nodes that we can get to directly from this node.
            outgoing = adjacencies[i]

            # Start out with the adjacency matrix. The row is already initialized with 0-values.
            for j in outgoing:
                self._P[i][j] = 1

            # If this node is truly a dead end, we have to teleport. Otherwise, we can teleport with
            # probability α or follow a link with probability (1 - α).
            if len(outgoing) == 0:
                self._P[i] = [1 / self._N] * self._N
            else:
                self._P[i] = [(alpha / self._N) + (1 - alpha) * (self._P[i][j] / len(outgoing)) for j in range(self._N)]

    def transition_matrix(self) -> List[List[float]]:
        """
        Returns the dense N-by-N matrix of transition probabilities in the induced Markov chain.

        This is an internal detail having public visibility to facilitate testing.
        """
        return self._P

    def step(self, x: List[float]) -> List[float]:
        """
        Given a probability vector x, returns an updated probability vector x' per a single step
        according to the transition probability matrix P. I.e., produces x' = xP.

        This is an internal detail having public visibility to facilitate testing.
        """
        # The given probability vector must have the right dimensions.
        assert x is not None
        assert len(x) == self._N

        # Vector-matrix multiplication.
        return [sum(x[j] * self._P[j][i] for j in range(self._N)) for i in range(self._N)]

    def pagerank(self, iterations: int = 20) -> List[float]:
        """
        Uses the power iteration method to compute the PageRank values. See Section 21.2.2 in
        https://nlp.stanford.edu/IR-book/pdf/21link.pdf for details.
        """
        # Obscure corner case.
        if self._N == 0:
            return []

        # The initial values can be whatever, as long as they sum to 1.
        x = [1 / self._N] * self._N

        # Take "enough" steps so that the values converge. We could check for convergence and
        # potentially abort early here, as soon as it seems that we've reached a fixed-point.
        for _ in range(iterations):
            x = self.step(x)
        return x
