# pylint: disable=missing-module-docstring

from typing import Dict, Any


class Posting:
    """
    A very simple posting entry in a non-positional inverted index.
    """

    def __init__(self, document_id: int, term_frequency: int):
        self.document_id = document_id
        self.term_frequency = term_frequency

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return str(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """
        Facilitates JSON serialization.
        """
        return {"document_id": self.document_id, "term_frequency": self.term_frequency}
