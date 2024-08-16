# pylint: disable=missing-module-docstring

from typing import List, Optional, Callable
from .document import Document


class DocumentPipeline:
    """
    A simple document processing pipeline. Applies a sequence of operations to the document
    that might transform or update the document in some way, e.g., by creating new fields
    that are the result of processing other fields.

    Documents can be dropped, too, if a processing operation returns None instead of the
    transformed document. Processing operations can also be simple identity functions with
    side-effects.
    """

    def __init__(self, processors: List[Callable[[Document], Optional[Document]]]):
        assert processors is not None
        assert all(processors)
        self.__processors = processors

    def __call__(self, document: Document) -> Optional[Document]:
        return self.process_document(document)

    def process_document(self, document: Document) -> Optional[Document]:
        """
        Applies all processors to the document, in the sequence they were provided.
        If a processor returns None, the document is dropped.
        """
        for processor in self.__processors:
            if document is None:
                return None
            document = processor(document)
        return document
