# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

from typing import Iterator, Iterable, Dict, Any
import faiss
import spacy
import numpy as np
from .corpus import Corpus
from .normalizer import Normalizer
from .tokenizer import Tokenizer


class SimilaritySearchEngine:
    """
    A search engine based on doing approximate nearest neighbor (ANN) lookups
    over embedding vectors generated from a document corpus.

    This implementation relies on selected open-source libraries. For more on
    ANNs, see, e.g., https://towardsdatascience.com/comprehensive-guide-to-approximate-nearest-neighbors-algorithms-8b94f057d6b6,
    https://wangzwhu.github.io/home/file/acmmm-t-part3-ann.pdf, or https://www.pinecone.io/learn/vector-database/.

    Uses spaCy (https://spacy.io/) to generate the embedding vectors for documents,
    using the precomputed word embeddings that come with the package. Using, e.g.,
    SentenceTransformers (https://www.sbert.net/index.html), transformers (https://github.com/huggingface/transformers),
    or UForm (https://github.com/unum-cloud/uform) would have been plausible alternatives.

    Uses FAISS (https://github.com/facebookresearch/faiss) to realize the ANN index
    over the generated embedding vectors. Using, e.g., Annoy (https://github.com/spotify/annoy),
    FALCONN (https://github.com/falconn-lib/falconn), NMSLIB (https://github.com/nmslib/nmslib),
    Chroma (https://www.trychroma.com/), DiskANN (https://github.com/microsoft/DiskANN/),
    Postgres with the pgvector extension (https://github.com/pgvector/pgvector),
    SQLite with the sqlite-vss extension (https://github.com/asg017/sqlite-vss),
    ScaNN (https://github.com/google-research/google-research/tree/master/scann),
    or USearch (https://github.com/unum-cloud/usearch) would have been plausible alternatives.
    We could also use any search engine based on Lucene (https://lucene.apache.org/), such as
    Elasticsearch (https://www.elastic.co/search-labs/vector-search-elasticsearch-rationale).
    """

    # Shared across instances, initialized on demand below.
    __nlp : spacy.Language = None

    def __init__(self, corpus: Corpus, fields: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer):

        # FAISS barfs on an empty corpus.
        assert len(corpus or []) > 0

        # The documents to index, plus basic helpers.
        self.__corpus = corpus
        self.__normalizer = normalizer
        self.__tokenizer = tokenizer

        # The machinery for generating embedding vectors from text buffers. Assume English.
        if SimilaritySearchEngine.__nlp is None:
            SimilaritySearchEngine.__nlp = self.__load_spacy("en_core_web_md")

        # Place the normalized documents in embedding space. Normalize the embeddings.
        # For large corpora, we could embed/add data in batches.
        buffers = (" \0 ".join(self.__normalize(d.get_field(f, "")) for f in fields) for d in self.__corpus)
        embeddings = np.array([self.__embed(b) for b in buffers], dtype=np.float32, copy=False)
        faiss.normalize_L2(embeddings)

        # Enables us to map from matrix row indices to document identifiers. This gives us some robustness
        # in case document identifiers should become, e.g., arbitrary GUIDs. If the N document identifiers
        # are all integers {0, 1, ..., N - 1} then this is superfluous but benign.
        self.__mappings = [d.document_id for d in self.__corpus]

        # The ANN index. See https://github.com/facebookresearch/faiss/wiki/The-index-factory for options.
        dimensionality = embeddings[0].shape[0]
        self.__index = faiss.index_factory(dimensionality, "Flat", faiss.METRIC_INNER_PRODUCT)
        self.__index.train(embeddings)
        self.__index.add(embeddings)

        # Sanity checks.
        assert self.__index.is_trained
        assert self.__index.ntotal == self.__corpus.size()

    def __load_spacy(self, model: str) -> spacy.Language:
        """
        Loads the spaCy model (i.e, text-processing pipeline) to use. This is loaded once
        per process, usually. See, e.g., https://spacy.io/models and https://github.com/explosion/spacy-models
        for details.

        We're not really interested in the pipeline components here, and hence exclude them
        to speed things up when generating embeddings. Rather, we are interested in using the
        word vector tables that come with the 'md' and 'lg' size models.
        """
        try:
            return spacy.load(model, exclude=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer", "ner"])
        except (OSError, AttributeError) as exception:
            raise IOError(f"Do 'python -m spacy download {model}'.") from exception

    def __embed(self, buffer: str) -> np.ndarray:
        """
        Generates the embedding vector representation of the given buffer. The input buffer is
        assumed normalized already, to avoid having to make assumptions on what spaCy does. 
        The generated embedding is not normalized to unit length.

        The current implementation simply returns the averaged word vector, computed over
        all words in the given buffer. A more elaborate implementation could do a weighted
        average, with the weights being, e.g., the TFIDF scores of each word.
        """
        return SimilaritySearchEngine.__nlp(buffer).vector  # pylint: disable=not-callable

    def __normalize(self, buffer: str) -> str:
        """
        Produces a normalized version of the given string. Both queries and documents need to be
        identically processed for lookups to fully work as expected.
        """
        tokens = self.__tokenizer.strings(self.__normalizer.canonicalize(buffer))
        return " ".join(self.__normalizer.normalize(t) for t in tokens)

    def evaluate(self, query: str, options: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """
        Consults the ANN index to locate the documents that are the closest to the
        given query in embedding space.

        The best-matching documents are yielded back to the client as dictionaries
        having the keys "score" (float) and "document" (Document).

        The client can supply a dictionary of options that controls the query evaluation
        process: The maximum number of documents to return to the client is controlled via
        the "hit_count" (int) option.
        """
        # Empty query?
        query = self.__normalize(query or "")
        if not query:
            return

        # Place the normalized query string in embedding space. Normalize the embedding.
        embedding = np.array([self.__embed(query)], dtype=np.float32, copy=False)
        faiss.normalize_L2(embedding)

        # Lookup! See, e.g., https://github.com/facebookresearch/faiss/wiki/Faster-search for options.
        distances, indices = self.__index.search(embedding, min(100, max(1, int(options.get("hit_count", 5)))))

        # With METRIC_INNER_PRODUCT as our metric and normalized vectors, the emitted scores are cosine
        # similarity scores and are emitted back in descending order. With another metric where scores
        # would be distances and emitted back in ascending order, we might want to negate the scores
        # before emitting them in order to keep to the convention that "<" for scores means "ranks below".
        # See, e.g., https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances for more.
        for i in range(len(indices[0])):
            yield {"score": distances[0][i], "document": self.__corpus[self.__mappings[indices[0][i]]]}
