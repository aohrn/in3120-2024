# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

import json
import re
from collections.abc import MutableMapping
from typing import Dict, Any, List


class ExpressionComposerDecorator(MutableMapping):
    """
    A dict-like mapping used for composing a larger expression out of smaller ones. The smaller
    expressions can be decorated with unique names so that they, if specified, can be easily
    captured. Intended used together with the ExpressionComposer class as an internal helper.
    """

    def __init__(self, grammar: Dict[str, Any]):
        self._grammar = grammar  # The grammar, defines the properties of individual keys in the mapping.
        self._mapping = {}       # The backing store for the mapping itself.
        self._counts = {}        # For each key in the mapping, keep track of many times it has been accessed.

    def __iter__(self):
        """
        Implements the dict-like interface.
        """
        return iter(self._mapping)

    def __len__(self):
        """
        Implements the dict-like interface.
        """
        return len(self._mapping)

    def __setitem__(self, key, value):
        """
        Implements the dict-like interface.
        """
        self._mapping[key] = value

    def __delitem__(self, key):
        """
        Implements the dict-like interface.
        """
        del self._mapping[key]

    def __getitem__(self, key):
        """
        Returns the value for the given key, but properly decorated.
        """
        self._counts[key] = self._counts.get(key, -1) + 1
        count = self._counts[key]
        value = self._mapping[key]
        node = self._grammar[key]
        capture = isinstance(node, dict) and node.get("capture", False)
        decorate = (not isinstance(node, dict)) or (isinstance(node, dict) and node.get("decorate", True))
        if capture and not decorate:
            raise ValueError(f"Settings for {key} are contradictory")
        if capture:
            if count > 0:
                return f"(?P<{key}_{count}>{value})"
            return f"(?P<{key}>{value})"
        elif decorate:
            return f"(?:{value})"
        else:
            return value


class ExpressionComposer:
    """
    Helps you machine-generate large and hairy regular expressions from simpler grammars, where small
    fragments can be defined and then put together to yield the overall complex expression.
    """

    def __init__(self, grammar: Dict[str, Any]):
        """
        Constructor. The given grammar defines a set of smaller subexpressions that refer to each other
        in various rather complex ways. The composer's job is to resolve all those references and compose
        the final, large expression where all the subexpressions have been expanded and properly decorated.
        """
        self._grammar = grammar
        self._parser = re.compile(r"(?<!{){([a-z0-9]+)}")

    def _resolve(self, root: str, stack: List[str], decorator: ExpressionComposerDecorator) -> str:
        """
        Internal helper function. Resolves and returns the given root pattern by first recursively resolving all the
        root pattern's subexpressions, and then formats the resulting root pattern by putting all the individual
        pieces together. Like macro-expansion known from C preprocessors, sort of. A special dictionary is used to
        decorate the subexpressions in case the grammar specifies that some subexpressions should be captured as
        named groups.
        """
        if root in stack:
            raise KeyError(f"Recursive definition of {root}")
        node = self._grammar.get(root, None)
        if node is None:
            raise KeyError(f"Unable to resolve {root}")
        expression = str(node.get("expression", None) if isinstance(node, dict) else node)
        matches = self._parser.findall(expression)
        decorator.update({name: self._resolve(name, stack + [root], decorator) for name in matches})
        return expression.format_map(decorator)

    def compose(self, root: str) -> str:
        """
        Composes and returns the named root expression as defined in the grammar.
        """
        decorator = ExpressionComposerDecorator(self._grammar)
        decorator.update({root: self._resolve(root, [], decorator)})
        return f"{{{root}}}".format_map(decorator)

    @classmethod
    def from_grammar(cls, grammar: Dict[str, Any], root: str) -> str:
        """
        Composes and returns the named root expression as defined in the given grammar.
        """
        return cls(grammar).compose(root)

    @classmethod
    def from_filename(cls, filename: str, root: str) -> str:
        """
        Composes and returns the named root expression as defined in the contents of the named file.
        For convenience, ignore lines in the named file that look like comments.
        """
        with open(filename, mode="r", encoding="utf-8") as file:
            grammar = json.loads("".join([line for line in file.readlines() if not re.match("^\\s*(?:#|//)", line)]))
            return cls.from_grammar(grammar, root)
