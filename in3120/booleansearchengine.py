# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=line-too-long
# pylint: disable=superfluous-parens
# pylint: disable=invalid-name

import ast
from typing import Iterator, Dict, Any
from .corpus import Corpus
from .posting import Posting
from .postingsmerger import PostingsMerger
from .invertedindex import InvertedIndex


class BooleanSearchEngine:
    """
    A simple search engine that does unranked Boolean retrieval. I.e., a document
    either matches the query expression or it does not. All matching documents are
    yielded back in document identifier order.

    A query is an arbitrarily complex Boolean expression composed of the operators
    "AND", "OR", and "ANDNOT". Note that all operators must be uppercased. The
    ANDNOT operator must have arity 2. The AND and OR operators can have varying
    arity. String literals can be compound (e.g., "foo bar").

    For simplicity, the current implementation uses Python's built-in support for
    abstract syntax trees (ASTs) and expression parsing. This might cause issues
    if reserved Python keywords are used in the expressions. For example, using
    'and' instead of 'AND' as the operator name will barf, so will using 'class'
    as a naked literal (you would have to quote it.)
    """

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex):

        # We return back matching documents to the client.
        self._corpus = corpus

        # What we search over to efficiently locate the matching documents.
        self._inverted_index = inverted_index

        # The Boolean operators we offer clients to use in their queries.
        self._operators = {
            "AND":    PostingsMerger.intersection,
            "OR":     PostingsMerger.union,
            "ANDNOT": PostingsMerger.difference,
        }

        # How we estimate costs when optimizing evaluation order.
        self._estimators = {
            "AND":    min,
            "OR":     sum,
            "ANDNOT": sum,
        }

    def _validate(self, tree: ast.AST) -> None:
        """
        Recursively validates that the given AST has the expected structure and looks sane.

        Nodes that represents string literals are decorated with the corresponding term(s)
        that we get after tokenizing and normalizing the string literals, so that these can
        be reused (and possibly reordered) downstream.

        Since normalization is generally not an idempotent operation (consider, e.g., phonetic
        normalization techniques) we want to avoid normalizing terms more than once, and the
        decorate-literal-nodes-with-terms functionality achieves this.
        """
        match tree:

            # A top-level expression.
            case ast.Expression(body=(ast.Call() | ast.Constant() | ast.Name())):
                self._validate(tree.body)

            # An AND or OR operator with some arguments.
            case ast.Call(func=ast.Name(id=("AND" | "OR"))):
                if len(tree.args) < 1:
                    raise ValueError(f"Operator {tree.func.id} expects at least one argument.")
                for argument in tree.args:
                    self._validate(argument)

            # A binary ANDNOT operator.
            case ast.Call(func=ast.Name(id="ANDNOT")):
                if len(tree.args) != 2:
                    raise ValueError("Operator ANDNOT expects exactly two arguments.")
                for argument in tree.args:
                    self._validate(argument)

            # An operator not handled above:
            case ast.Call(func=ast.Name(id=_)):
                self._unhandled(tree)

            # A string literal, e.g., 'foo' or 'foo bar baz'. Decorate the node with unique terms.
            case ast.Constant():
                terms = list(self._inverted_index.get_terms(str(tree.value)))
                terms = list(dict.fromkeys(terms))
                if len(terms) == 0:
                    raise ValueError(f"Expected '{tree.value}' to contain at least one term.")
                tree.terms = terms

            # A naked (unquoted) string literal, e.g., foo. Decorate the node with the term.
            case ast.Name():
                terms = list(self._inverted_index.get_terms(str(tree.id)))
                if len(terms) != 1:
                    raise ValueError(f"Expected '{tree.id}' to contain a single term, got {terms}.")
                tree.terms = terms

            # Something unexpected.
            case _:
                raise NotImplementedError(f"Unknown node type {tree.__class__.__name__}.")

    def _unhandled(self, tree: ast.AST) -> None:
        """
        Invoked during initial validation. Can be overloaded if a subclass wants to extend
        the set of supported operators.
        """
        raise ValueError(f"Unsupported operator {tree.func.id}.")

    def _optimize(self, tree: ast.AST) -> ast.AST:
        """
        Optimizes the AST so that expression evaluation becomes more efficient.

        Optimization here consists of two stages: First, we simplify and rewrite the
        tree structure in a semantics-preserving manner. Then, given the simplified
        AST, reorder any terms and clauses.
        """
        tree = self._simplify(tree)
        self._reorder(tree)
        return tree

    def _simplify(self, tree: ast.AST) -> ast.AST:
        """
        For now, no simplifications take place and this is a placeholder.

        Many optimizing and semantics-preserving simplifications are possible. For example,
        in an expression like AND(AND(a, b), AND(c, d)) we could simplify it to a single AND
        so that literals across ANDs could be reordered and we'd end up with something more
        optimized like AND(c, a, b, d). Or, we could use the absorptive law and other laws
        from Boolean algebra to simplify expressions like OR(AND(a, b), a) to just a.
        """
        return tree

    def _reorder(self, tree: ast.AST, operator: str = None) -> int:
        """
        See https://nlp.stanford.edu/IR-book/html/htmledition/processing-boolean-queries-1.html.

        If we rearrange the evaluation order so that we narrow down the result set as quickly as
        possible, to work with as short posting lists as possible, we get smaller intermediate
        results and fewer postings to work with. For conjunctive queries, we'd want to start with
        the least frequent terms, i.e., the terms having the shortest posting lists. The length of
        a posting list equals the term's document frequency, which the inverted index can tell us.

        Modifies the given AST in place. Returns the estimated cost of processing the given AST.
        """
        match tree:

            # A top-level expression.
            case ast.Expression(body=(ast.Call() | ast.Name())):
                return self._reorder(tree.body)

            # A top-level expression with just a string literal.
            case ast.Expression(body=ast.Constant()):
                return self._reorder(tree.body, "AND")

            # An AND or OR operator with some arguments.
            case ast.Call(func=ast.Name(id=("AND" | "OR") as operator)):
                costs = [(argument, self._reorder(argument, operator)) for argument in tree.args]
                if operator == "AND" and len(tree.args) > 2:
                    tree.args = [argument for argument, _ in sorted(costs, key=lambda pair: pair[1])]
                return self._estimators[operator](cost for _, cost in costs)

            # A binary ANDNOT operator.
            case ast.Call(func=ast.Name(id="ANDNOT")):
                cost1 = self._reorder(tree.args[0], "AND")
                cost2 = self._reorder(tree.args[1], "OR")
                return self._estimators["ANDNOT"]([cost1, cost2])

            # A string literal, e.g., 'foo' or 'foo bar baz' in the context of some parent operator.
            case ast.Constant() if operator:
                costs = [(term, self._inverted_index.get_document_frequency(term)) for term in tree.terms]
                if operator == "AND" and len(tree.terms) > 2:
                    tree.terms = [term for term, _ in sorted(costs, key=lambda pair: pair[1])]
                return self._estimators[operator](cost for _, cost in costs)

            # A naked (unquoted) string literal, e.g., foo.
            case ast.Name():
                return self._inverted_index.get_document_frequency(tree.terms[0])

            # Something unexpected.
            case _:
                raise NotImplementedError(f"Unknown node type {tree.__class__.__name__}.")

    def _evaluate(self, tree: ast.AST, operator: str = None) -> Iterator[Posting]:
        """
        Recursively traverses the given query expression's AST and evaluates and
        returns the resulting posting list.
        """
        match tree:

            # A top-level expression.
            case ast.Expression(body=(ast.Call() | ast.Name())):
                return self._evaluate(tree.body)

            # A top-level expression with just a string literal.
            case ast.Expression(body=ast.Constant()):
                return self._evaluate(tree.body, "AND")

            # An AND or OR operator with some arguments.
            case ast.Call(func=ast.Name(id=("AND" | "OR") as operator)):
                lvalue = self._evaluate(tree.args[0], operator)
                for i in range(1, len(tree.args)):
                    rvalue = self._evaluate(tree.args[i], operator)
                    lvalue = self._operators[operator](lvalue, rvalue)
                return lvalue

            # A binary ANDNOT operator.
            case ast.Call(func=ast.Name(id="ANDNOT")):
                lvalue = self._evaluate(tree.args[0], "AND")
                rvalue = self._evaluate(tree.args[1], "OR")
                return self._operators["ANDNOT"](lvalue, rvalue)

            # A string literal, e.g., 'foo' or 'foo bar baz' in the context of some parent operator.
            case ast.Constant() if operator:
                terms = tree.terms
                lvalue = self._inverted_index.get_postings_iterator(terms[0])
                for i in range(1, len(terms)):
                    rvalue = self._inverted_index.get_postings_iterator(terms[i])
                    lvalue = self._operators[operator](lvalue, rvalue)
                return lvalue

            # A naked (unquoted) string literal, e.g., foo.
            case ast.Name():
                return self._inverted_index.get_postings_iterator(tree.terms[0])

            # Something unexpected.
            case _:
                raise NotImplementedError(f"Unknown node type {tree.__class__.__name__}.")

    def evaluate(self, expression: str, options: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """
        Parses and evaluates the given Boolean query expression.

        The matching documents, if any, are unranked and sorted by their document identifiers.
        Results are yielded back to the client as dictionaries having the key "document" (Document).
        If an error occurs the client is yielded back a dictionary having the key "error" (str).

        The client can supply a dictionary of options that controls the query evaluation process:
        Optimizations can be enabled or disabled via the "optimize" (bool) option.
        """
        try:

            # Parse the expression.
            tree = ast.parse(expression, mode="eval")

            # Does the AST look kosher? Decorate the AST in-place with terms.
            self._validate(tree)

            # Optimize the AST for more efficient evaluation?
            if options.get("optimize", True):
                tree = self._optimize(tree)

            # Evaluate and emit matching documents.
            for posting in self._evaluate(tree):
                yield {"document": self._corpus[posting.document_id]}

        except SyntaxError as e:
            yield {"error": f"Syntax error, {e.msg}."}
        except ValueError as e:
            yield {"error": e.args[0] if e.args else "Unknown error."}
