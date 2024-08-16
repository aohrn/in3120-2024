# pylint: disable=missing-module-docstring
# pylint: disable=unnecessary-pass

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class Document(ABC):
    """
    Abstract base class for a document. A document is a simple collection of
    named, typed fields.
    """

    def __getitem__(self, field_name: str) -> Any:
        return self.get_field(field_name, None)

    def __setitem__(self, field_name: str, field_value: Any) -> None:
        self.set_field(field_name, field_value)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return str(self.to_dict())

    @property
    def document_id(self) -> int:
        """
        Convenience function.
        """
        return self.get_document_id()

    def to_dict(self) -> Dict[str, Any]:
        """
        Facilitates JSON serialization.
        """
        fields = dict((name, self.get_field(name, None)) for name in self.get_field_names())
        return {"document_id": self.get_document_id(), "fields": fields}

    @abstractmethod
    def get_document_id(self) -> int:
        """
        Returns the document's unique identifier.
        """
        pass

    @abstractmethod
    def get_field(self, field_name: str, default: Any) -> Any:
        """
        Returns the value of the named field in the document. If the document
        doesn't contain the named field, the provided default field value is
        returned instead.
        """
        pass

    @abstractmethod
    def set_field(self, field_name: str, field_value: Any) -> None:
        """
        Sets the named field in the document to the given value.
        """
        pass

    @abstractmethod
    def get_field_names(self) -> List[str]:
        """
        Returns the names of all the fields that exist in the document.
        """
        pass


class InMemoryDocument(Document):
    """
    A very simple and straightforward in-memory implementation of a document.
    Note that what we index are normalized versions of the raw fields. We keep
    the raw fields here in order to preserve the original presentation.
    """

    def __init__(self, document_id: int, fields: Dict[str, Any]):
        assert document_id is not None
        assert isinstance(fields, dict)
        self.__document_id = document_id
        self.__fields = fields

    def get_document_id(self) -> int:
        return self.__document_id

    def get_field(self, field_name: str, default: Any) -> Any:
        return self.__fields.get(field_name, default)

    def set_field(self, field_name: str, field_value: Any) -> None:
        assert field_name is not None
        self.__fields[field_name] = field_value

    def get_field_names(self) -> List[str]:
        return self.__fields.keys()
