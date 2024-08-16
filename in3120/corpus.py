# pylint: disable=missing-module-docstring
# pylint: disable=unnecessary-pass
# pylint: disable=line-too-long
# pylint: disable=too-many-branches

from __future__ import annotations
import collections.abc
import csv
from abc import abstractmethod
from json import loads
from typing import Any, List, Dict, Callable, Optional, Set, Iterable, Union
from xml.dom.minidom import parse
from .document import Document, InMemoryDocument
from .documentpipeline import DocumentPipeline


class Corpus(collections.abc.Iterable):
    """
    Abstract base class representing a corpus we can index and search over,
    i.e., a collection of documents. The class facilitates iterating over
    all documents in the corpus.
    """

    def __len__(self):
        return self.size()

    def __getitem__(self, document_id: int) -> Document:
        return self.get_document(document_id)

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def size(self) -> int:
        """
        Returns the size of the corpus, i.e., the number of documents in the
        document collection.
        """
        pass

    @abstractmethod
    def get_document(self, document_id: int) -> Document:
        """
        Returns the document associated with the given document identifier.
        """
        pass


class InMemoryCorpus(Corpus):
    """
    An in-memory implementation of a document store, suitable only for small
    document collections.

    Document identifiers are assigned on a first-come first-serve basis.
    """

    def __init__(self,
                 filenames: Optional[Union[str, Iterable[str]]] = None,
                 annotations: Optional[Union[Dict[str, Any], Iterable[Dict[str, Any]]]] = None,
                 pipeline: Optional[DocumentPipeline] = None):
        """
        The client can, optionally, supply a single filename or a list of filenames.

        For each filename supplied, if any, the client can also supply a dictionary of "annotations"
        that each document from that file gets assigned as additional content. This is useful so that
        it becomes easy to identify the origin of each document, e.g., when splitting the corpus into
        multiple corpora that define a training set for a classifier.

        Optionally, the client can supply a document processing pipeline that is applied to every
        document. The processing pipeline can transform or even drop the document before they get
        added to the corpus.
        """
        self._documents = []
        if filenames is None:
            assert annotations is None
            filenames = []
        if isinstance(filenames, str):
            assert annotations is None or isinstance(annotations, dict)
        if isinstance(annotations, dict):
            assert isinstance(filenames, str)
        if isinstance(filenames, str):
            filenames = [filenames]
        if isinstance(annotations, dict):
            annotations = [annotations]
        if annotations is None:
            annotations = [{} for _ in range(len(filenames))]
        assert len(filenames) == len(annotations)
        pipeline = pipeline or DocumentPipeline([])
        for filename, annotation in zip(filenames, annotations):
            assert filename is not None
            assert annotation is not None
            if filename.endswith(".txt"):
                self.__load_text(filename, annotation, pipeline)
            elif filename.endswith(".xml"):
                self.__load_xml(filename, annotation, pipeline)
            elif filename.endswith(".json"):
                self.__load_json(filename, annotation, pipeline)
            elif filename.endswith(".csv"):
                self.__load_csv_or_tsv(filename, ",", annotation, pipeline)
            elif filename.endswith(".tsv"):
                self.__load_csv_or_tsv(filename, "\t", annotation, pipeline)
            else:
                raise IOError(f"Filename has unsupported extension: {filename}")

    def __iter__(self):
        return iter(self._documents)

    def size(self) -> int:
        return len(self._documents)

    def get_document(self, document_id: int) -> Document:
        assert 0 <= document_id < len(self._documents)
        return self._documents[document_id]

    def add_document(self, document: Document, strict: bool = True) -> InMemoryCorpus:
        """
        Adds the given document to the corpus. Facilitates testing.
        """
        assert document is not None
        assert (not strict) or (document.document_id == len(self._documents))
        self._documents.append(document)
        return self

    def split(self, field_name: str, splitter: Optional[Callable[[Any], List[Any]]] = None) -> Dict[Any, InMemoryCorpus]:
        """
        Divides the corpus up into multiple corpora, according to the value(s) of the
        named field. I.e., splits the corpus up into several smaller corpora.

        The value(s) of the named fields are used as keys for the splits. A custom splitter
        function can optionally be provided, in case the named field is multi-valued and/or the
        value(s) should be filtered or transformed in some way.
        """
        splitter = splitter if splitter else lambda v: [v]
        splits = {}
        for document in self:
            values = splitter(document.get_field(field_name, ""))
            for value in values:
                if value not in splits:
                    splits[value] = InMemoryCorpus()
                splits[value].add_document(document, False)
        return splits

    @staticmethod
    def merge(splits: Dict[Any, Corpus]) -> InMemoryCorpus:
        """
        The inverse of the split method. Merges a bunch of corpora together, deduplicating any shared
        documents.
        """
        unique = set()
        merged = InMemoryCorpus()
        for _, corpus in splits.items():
            for document in corpus:
                if document.document_id not in unique:
                    unique.add(document.document_id)
                    merged.add_document(document, False)
        return merged

    def __load_text(self, filename: str, annotation: Dict[str, Any], pipeline: DocumentPipeline) -> None:
        """
        Loads documents from the given UTF-8 encoded text file. One document per line,
        tab-separated fields. Empty lines are ignored. The first field gets named "body",
        the second field (optional) gets named "meta". All other fields are currently ignored.
        """
        document_id = self.size()
        with open(filename, mode="r", encoding="utf-8") as file:
            for line in file:
                anonymous_fields = line.strip().split("\t")
                if len(anonymous_fields) == 1 and not anonymous_fields[0]:
                    continue
                named_fields = {"body": anonymous_fields[0]}
                if len(anonymous_fields) >= 2:
                    named_fields["meta"] = anonymous_fields[1]
                named_fields.update(annotation)
                document = pipeline(InMemoryDocument(document_id, named_fields))
                if document:
                    self.add_document(document)
                    document_id += 1

    def __load_xml(self, filename: str, annotation: Dict[str, Any], pipeline: DocumentPipeline) -> None:
        """
        Loads documents from the given XML file. The schema is assumed to be
        simple <doc> nodes. Each <doc> node gets mapped to a single document field
        named "body".
        """
        def __get_text(nodes):
            data = []
            for node in nodes:
                if node.nodeType == node.TEXT_NODE:
                    data.append(node.data)
            return " ".join(data)

        dom = parse(filename)
        document_id = self.size()
        for body in (__get_text(n.childNodes) for n in dom.getElementsByTagName("doc")):
            named_fields = {"body": body}
            named_fields.update(annotation)
            document = pipeline(InMemoryDocument(document_id, named_fields))
            if document:
                self.add_document(document)
                document_id += 1

    def __load_csv_or_tsv(self, filename: str, delimiter: str, annotation: Dict[str, Any], pipeline: DocumentPipeline) -> None:
        """
        Loads documents from the given UTF-8 encoded CSV file. One document per line.
        """
        document_id = self.size()
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=delimiter)
            for row in reader:
                named_fields = dict(row)
                named_fields.update(annotation)
                document = pipeline(InMemoryDocument(document_id, named_fields))
                if document:
                    self.add_document(document)
                    document_id += 1

    def __load_json(self, filename: str, annotation: Dict[str, Any], pipeline: DocumentPipeline) -> None:
        """
        Loads documents from the given UTF-8 encoded JSON file. One document per line.
        Lines that do not start with "{" and end with "}" are ignored.
        """
        document_id = self.size()
        with open(filename, mode="r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.startswith("{") and line.endswith("}"):
                    named_fields = loads(line)
                    named_fields.update(annotation)
                    document = pipeline(InMemoryDocument(document_id, named_fields))
                    if document:
                        self.add_document(document)
                        document_id += 1


class AccessLoggedCorpus(Corpus):
    """
    Wraps another corpus, and keeps an in-memory log of which documents
    that have been accessed. Facilitates testing.
    """

    def __init__(self, wrapped: Corpus):
        self.__wrapped = wrapped
        self.__accesses = set()

    def __iter__(self):
        return iter(self.__wrapped)

    def size(self) -> int:
        return self.__wrapped.size()

    def get_document(self, document_id: int) -> Document:
        self.__accesses.add(document_id)
        return self.__wrapped.get_document(document_id)

    def get_history(self) -> Set[int]:
        """
        Returns the set of document identifiers that clients have accessed so far.
        """
        return self.__accesses
