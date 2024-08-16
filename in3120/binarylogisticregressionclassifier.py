# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals
# pylint: disable=invalid-name

import math
import random
from typing import Any, Dict, Iterable, Iterator, List, Callable, Optional
from .corpus import Corpus
from .sparsedocumentvector import SparseDocumentVector
from .vectorizer import Vectorizer

class BinaryLogisticRegressionClassifier:
    """
    Demonstrates gradient descent by training a binary logistic regression classifier that minimizes cross-entropy loss.
    
    See https://en.wikipedia.org/wiki/Gradient_descent and https://en.wikipedia.org/wiki/Cross-entropy#Cross-entropy_minimization
    for details. See also https://medium.com/@IwriteDSblog/gradient-descent-for-logistics-regression-in-python-18e033775082
    for a worked example.
    """

    def __init__(self, vectorizer: Vectorizer):

        # Helpers and placeholders.
        self._vectorizer = vectorizer
        self._bias = "__bias_this_should_not_be_a_valid_term_bias__"
        self._categories = ["category 0", "category 1"]

        # Our model parameters or weights. Use the name θ to align with notation used elsewhere.
        # Start out with random weights, including one for the bias term. Adjust them during training
        # using gradient descent.
        self._theta = SparseDocumentVector({self._bias: random.uniform(-1, 1)} | {term: random.uniform(-1, 1) for term in vectorizer.get_vocabulary()})

    def train(self, training_set: Dict[str, Corpus], fields: Iterable[str],
              options: Dict[str, Any], callback: Optional[Callable[[int, float], bool]]) -> None:
        """
        Trains the model on the given two-class training set, using vanilla gradient descent.
        The implementation is slow and not optimized, and primarily intended for pedagogical purposes.
        """
        # Assume a two-class classification task for now. Multi-class variants exist.
        assert len(training_set) == 2, "Assuming a binary classification problem."

        # Arbitrarily let the index indicate the desired model output for each class.
        self._categories = list(training_set.keys())

        # Vectorize the training set and create a binary target. Use the names X and y to align
        # with notation used elsewhere.
        X : List[SparseDocumentVector] = []
        y : List[int] = []
        for category in self._categories:
            X.extend(self._vectorizer.from_document(d, fields) for d in training_set[category])
            y.extend(1 if category == self._categories[1] else 0 for _ in range(len(training_set[category])))

        # Normalize the vectors. Add in the bias term afterwards, since that weight is fixed to 1.
        for example in X:
            example.normalize()
            example[self._bias] = 1.0

        # For at most how many epochs/iterations should we learn? It should be large enough to
        # allow us to converge. The client can choose to stop early via the callback.
        epochs = range(max(1, int(options.get("epochs", 100))))

        # What should our learning rate be? The bigger the learning rate, the bigger the step size
        # we take and the faster we converge. However, with too big a learning rate we might overshoot
        # our target and make learning erratic and hard. We could make the learning rate adaptive (see
        # below), but keep it constant for now.
        learning_rate = max(0.000000001, options.get("learning_rate", 0.5))

        # Do gradient descent, minimizing cross-entropy loss.
        for epoch in epochs:

            # Include all examples for now. We could instead, e.g., randomly sample a mini-batch, or
            # cycle through the examples and update θ after each example, or...
            batch = range(len(X))

            # Compute ŷ, i.e., the predicted values given the current weights θ.
            predictions = [(i, self._h(X[i])) for i in batch]

            # Compute our total loss J(θ) for the batch, which is what we want to minimize. We don't
            # really have to compute this, but do so to monitor that learning takes place and so that
            # we can check for convergence. The function J(θ) is sometimes called a loss function, or
            # a cost function, or an error function, or an objective function. Sometimes J(θ) might be
            # referred to as, e.g., L(θ) or E(θ).
            loss = sum(self._cost(yhat, y[i]) for i, yhat in predictions) / len(predictions)

            # We have one weight in θ per term, including the bias term. Update θ so that J(θ) decreases.
            for term, weight in self._theta:

                # Compute the gradient for the current term. This is the analytical expression
                # for the first-order partial derivative of the cross-entropy loss function J wrt
                # the parameter in θ for the current term, i.e., ∂J/∂θ. The vector of all such derivatives
                # is sometimes denoted ∇J(θ) and called the Jacobian. Automatic differentiation engines exist
                # that help us to compute gradients from computational graphs that encode J, instead of
                # having to supply an analytical expression directly like here.
                gradient = sum(X[i][term] * (yhat - y[i]) for i, yhat in predictions) / len(predictions)

                # Update the weight for the current term according to the gradient descent update rule.
                # Possible alternatives include decaying the learning rate per epoch, or adding a
                # momentum term, or looking at the second-order partial derivatives (the curvature of the
                # loss surface, sometimes referred to as the Hessian) and making the learning rate adaptive
                # to that, or doing a line search along the direction of the gradient, or...
                self._theta[term] = weight - learning_rate * gradient

            # Abort? The callback can monitor for convergence and/or overfitting, and possibly stop early.
            # Note that the loss we report is the loss J(θ) before the update to θ. We might want to change this.
            if callback and not callback(epoch, loss):
                break

    def _h(self, vector: SparseDocumentVector) -> float:
        """
        Returns the model's response when applied to the given input vector. The
        input vector is assumed appropriately scaled and equipped with a dummy bias
        term. The model's response will be in the range (0, 1) and can be thresholded
        to indicate if the input vector belongs to "category 0" or to "category 1".
        """
        z = self._theta.dot(vector)
        return 1.0 / (1.0 + math.exp(-z))

    def _cost(self, prediction: float, target: int) -> float:
        """
        Computes the cost for a single training example, given the model's
        predicted output and the correct target class.
        """
        return -math.log(prediction) if target == 1 else -math.log1p(-prediction)

    def classify(self, buffer: str) -> Iterator[Dict[str, Any]]:
        """
        Classifies the buffer into one of two categories.
        """
        # Vectorize the buffer similar to how the training examples were
        # vectorized. Add in a dummy dimension for the bias term.
        vector = SparseDocumentVector(self._vectorizer.from_buffers([buffer]))
        vector.normalize()
        vector[self._bias] = 1.0

        # The model triggers for category 1, whatever "1" is.
        score1 = self._h(vector)
        score0 = 1.0 - score1
        result1 = {"category": self._categories[1], "score": score1}
        result0 = {"category": self._categories[0], "score": score0}

        # Emit both/all categories, but list the highest-scoring class first.
        yield from (result1, result0) if score1 > score0 else (result0, result1)
