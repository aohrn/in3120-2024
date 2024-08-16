# Guide

The following outlines some key classes and code snippets found in this repository, and ties to them to selected chapters in the [textbook](https://nlp.stanford.edu/IR-book/information-retrieval-book.html) and/or to selected [papers](./papers/).

For interactive and ad hoc testing of many of these classes, check out the [REPL zoo](./tests/repl.py). Also take a look at the many [unit tests](./tests/).

## [Chapter 1](https://nlp.stanford.edu/IR-book/pdf/01bool.pdf)

Section 1.1 introduces many of the basic concepts, reflected by interfaces and classes in this repository, e.g.:

* [`Document`](./in3120/document.py), our basic unit of retrieval. Basically a set of named and typed fields, together with a unique document identifier.
* [`Corpus`](./in3120/corpus.py), sometimes also referred to as a collection. Basically the set of [`Document`](./in3120/document.py) objects that comprises the haystack of information we will index and search across.
* [`InvertedIndex`](./in3120/invertedindex.py). An index structure that makes a corpus efficiently searchable using keyword search. Basically a [`Dictionary`](./in3120/dictionary.py) object plus a set of [`PostingList`](./in3120/postinglist.py) objects, one per dictionary term.
* [`Dictionary`](./in3120/dictionary.py), sometimes also referred to as a vocabulary or a lexicon. Keeps track of which terms that are indexed and searchable in an inverted index.
* [`PostingList`](./in3120/postinglist.py). A sequence of [`Posting`](./in3120/posting.py) objects, typically sorted by their document identifiers.
* [`Posting`](./in3120/posting.py). An individual element in a [`PostingList`](./in3120/postinglist.py).

Some simple implementations of these are provided, typically using non-optimized data structures. The main simplification we will often make for the purposes of this introductory course is that we will assume that everything fits in memory on a single machine and doesn't need to be disk-backed, distributed, or split up into smaller chunks. Hence we have [`InMemoryDocument`](./in3120/document.py), [`InMemoryCorpus`](./in3120/corpus.py), [`InMemoryInvertedIndex`](./in3120/invertedindex.py), [`InMemoryDictionary`](./in3120/dictionary.py), and [`InMemoryPostingList`](./in3120/postinglist.py) classes.

How a [`Document`](./in3120/document.py) object gets processed and algorithmically transformed and enriched prior to being indexed can be quite complex, and the overall flow is handled by the [`DocumentPipeline`](./in3120/documentpipeline.py) class. Transformations that can take place in a document processing pipeline include, e.g., classification, sentiment analysis, named entity recognition, and much more.

Section 1.3 discusses how to process Boolean queries using an inverted index. The [`PostingsMerger`](./in3120/postingsmerger.py) utility class implements logical binary AND, OR and ANDNOT operations on posting lists, and the [`BooleanSearchEngine`](./in3120/booleansearchengine.py) class puts these together to form more complex Boolean expressions. The [`BooleanSearchEngine`](./in3120/booleansearchengine.py) class also contains simple logic for query optimization as discussed in Section 1.3, i.e., for optimizing the evaluation order in more complex Boolean expressions that involve more than two terms.

## [Chapter 2](https://nlp.stanford.edu/IR-book/pdf/02voc.pdf)

Section 2.2.1 discusses tokenization. This is handled by the abstract [`Tokenizer`](./in3120/tokenizer.py) class and its various subclasses, e.g., [`SimpleTokenizer`](./in3120/tokenizer.py) or [`ShingleGenerator`](./in3120/shinglegenerator.py). Note that a production-ready tokenizer would not be implemented this way and have many more features, and might often be language-specific in some way. For example, a tokenizer for English might differ from a tokenizer for Japanese. Also note that, although not covered by the textbook, some tokenizers might be more language-agnostic (apart from training data) and produce tokens drawn from a finite vocabulary (see, e.g., [this paper](./papers/fast-wordpiece-tokenization.pdf) or [this tutorial](https://huggingface.co/learn/nlp-course/en/chapter6/5) or [this repository](https://github.com/karpathy/minbpe)), which might be a useful feature for, e.g., LLM-based applications.

Section 2.2.3 discusses normalization with focus on the case of equivalence-classing, i.e., where a token is normalized to a baseform. Like tokenization, normalization can often have language-specific twists. (There is also the case of expanding a token to multiple alternate forms, discussed elsewhere.) This is handled by the abstract [`Normalizer`](./in3120/normalizer.py) class and its various subclasses. For example, [`SimpleNormalizer`](./in3120/normalizer.py) which does case-folding, or [`PorterNormalizer`](./in3120/normalizer.py) which does case-folding and stemming according to Porter's algorithm for English. Stemming and Porter's algorithm is discussed in Section 2.2.4 and handled by the [`PorterStemmer`](./in3120/porterstemmer.py) class. The [`Normalizer`](./in3120/normalizer.py) class also deals with Unicode canonicalization, which can be rather important for some languages.

Section 2.4.1 presents the concept of a biword index. Note that this can be realized simply by using a suitable [`Tokenizer`](./in3120/tokenizer.py) implementation when we build the inverted index, such as the [`WordShingleGenerator`](./in3120/shinglegenerator.py) class. Section 2.4.1 also introduces the concept of a phrase index, usually realized via a positional index as discussed in Section 2.4.2. The [`SuffixArray`](./in3120/suffixarray.py) class implements an alternate way of realizing a simple phrase index, not covered by the textbook but covered in [this paper](./papers/suffix-arrays.pdf). This has the nice property that the last term in the phrase is allowed to be incomplete, which is useful for as-you-type searches.

## [Chapter 3](https://nlp.stanford.edu/IR-book/pdf/03dict.pdf)

In Section 3.2.1 we can read about general wildcard queries and the permuterm index. The [`WildcardExpander`](./in3120/wildcardexpander.py)class demonstrates the use of a permuterm index to expand a wildcard expression into the set of terms that match the expression. The set of expanded results would typically be used to form a large OR-expression that we can evaluate using [`ExtendedBooleanSearchEngine`](./in3120/extendedbooleansearchengine.py).

Section 3.2.2 discusses the concept of a _k_-gram index, albeit in the particular context of wildcard queries. Note that a _k_-gram index can be realized simply by using a suitable [`Tokenizer`](./in3120/tokenizer.py) implementation when we build the inverted index, specifically a [`ShingleGenerator`](./in3120/shinglegenerator.py) having width _k_.

The notion of edit distance and edit tables is introduced in Section 3.3.3. The [`EditTable`](./in3120/edittable.py) class implements this for Levenshtein-Damerau distance, and enables you to compute the edit distance between a query string _q_ and a single candidate string _c_. However, in practial applications such as spellchecking what you often need to do is to efficiently compute the edit distance between a query string _q_ and a large number of possible candidate strings drawn from a dictionary. To this end, the [`EditSearchEngine`](./in3120/editsearchengine.py) class implements a possible solution as proposed in [this paper](./papers/tries-for-approximate-string-matching.pdf).

In many applications we will need to represent large sets of strings in memory in a compact way that supports prefix lookups. Both [`WildcardExpander`](./in3120/wildcardexpander.py) and [`EditSearchEngine`](./in3120/editsearchengine.py) are examples of this. Although not covered in the textbook, [tries](https://en.wikipedia.org/wiki/Trie) are often a good choice, and the [`Trie`](./in3120/trie.py) class provides a naive trie implementation. A production-ready implementation might transform the trie into a finite state automaton as described in [this paper](./papers/how-to-squeeze-a-lexicon.pdf), and pack the resulting finite state automaton into a byte buffer similar to what is described in [this paper](./papers/tightly-packed-tries.pdf).

Section 3.3.4 introduces _k_-gram indexes for spelling correction. Using [`SimpleSearchEngine`](./in3120/simplesearchengine.py) in tandem with [`ShingleGenerator`](./in3120/shinglegenerator.py) can be used to realize this.

In Section 3.4 the concept of phonetic hashing is introduced. The [`SoundexNormalizer`](./in3120/normalizer.py) class equips the Soundex algorithm with a [`Normalizer`](./in3120/normalizer.py) interface, with [`Soundex`](./in3120/soundex.py) providing the actual implementation of the algorithm. Better algorithms than Soundex exist, and phonetic algorithms are not much used beyond specialized applications where one is known to search for names.

The [`ExtendedBooleanSearchEngine`](./in3120/extendedbooleansearchengine.py) class implements an extended version of [`BooleanSearchEngine`](./in3120/booleansearchengine.py), where some new query operators based on the approximate matching techniques from this chapter are demonstrated.

## [Chapter 4](https://nlp.stanford.edu/IR-book/pdf/04const.pdf)

Index construction is only cursorily addressed in this repository, due to the abovementioned simplyfing assumptions. The [`InMemoryInvertedIndex`](./in3120/invertedindex.py) basically implements single-pass in-memory indexing as presented in Section 4.3, but with a single block and thus no merging of per block results.

## [Chapter 5](https://nlp.stanford.edu/IR-book/pdf/05comp.pdf)

Section 5.2 discusses dictionary compression. When Section 5.2.2 introduces the concept of front coding, note how this begins to resemble general string compression and tries as described above. The ideas described in [this paper](./papers/how-to-squeeze-a-lexicon.pdf) go one step further, by also exploiting shared suffixes in addition to shared prefixes.

The [`CompressedInMemoryPostingList`](./in3120/postinglist.py) class demonstrates gap-encoding of posting lists as presented in Section 5.3, combined with variable byte encoding as presented in Section 5.3.1. The variable byte codec itself is implemented by the [`VariableByteCodec`](./in3120/variablebytecodec.py) class.

Gamma coding as described in Section 5.3.2 is demonstrated by the [`EliasGammaCodec`](./in3120/eliasgammacodec.py) class.

## [Chapter 6](https://nlp.stanford.edu/IR-book/pdf/06vect.pdf)

The concepts of fields and zones from Section 6.1 are reflected in arguments passed to the constructors of classes like [`InMemoryInvertedIndex`](./in3120/invertedindex.py) or [`SuffixArray`](./in3120/suffixarray.py): You can build an index over one or more named zones.

TF-IDF scoring as presented in Section 6.2 is a key concept in ranking and used in subclasses that implement the [`Ranker`](./in3120/ranker.py) interface, such as the [`BetterRanker`](./in3120/betterranker.py) class. Use of TF-IDF scoring is also demonstrated in the [`Vectorizer`](./in3120/vectorizer.py) class.

The vector space model from Section 6.3 works equally well both for sparse vectors (as described in the textbook) and dense vectors (such as embedding vectors described in, e.g., [this paper](./papers/distributed-representations-of-words-and-phrases-and-their-compositionality.pdf)), and cosine similarity as defined in Section 6.3.1 is typically used as a distance metric in both cases. For sparse vectors, see the [`SparseDocumentVector`](./in3120/sparsedocumentvector.py) class for basic example code related to dot products and cosine similarity. For dense vectors, the [`SimilaritySearchEngine`](./in3120/similaritysearchengine.py) class implements an approximate nearest neighbour index over a set of embeddings. The latter is not covered by the textbook but presented at a high-level in [these slides](./slides/embedding-techniques.pdf) and [these slides](./slides/approximate-nearest-neighbours.pdf).

## [Chapter 7](https://nlp.stanford.edu/IR-book/pdf/07system.pdf)

Section 7.1 discusses using a heap to pick out the highest-scoring documents. The [`Sieve`](./in3120/sieve.py) utility class does exactly this.

In Section 7.1.4 the concept of a query-independent static quality score _g(d)_ is introduced, and it is discussed how this could be used for ranking. The [`BetterRanker`](./in3120/betterranker.py) class combines _g(d)_ with a query-dependent TF-IDF score, as proposed by the textbook.

Section 7.1.5 (and Section 6.3.3) introduces the distinction betweeen document-at-a-time scoring and term-at-a-time scoring. The [`SimpleSearchEngine`](./in3120/simplesearchengine.py) class implements document-at-a-time scoring, using a client-specified [`Ranker`](./in3120/Ranker) object for the actual scoring.

Cluster pruning as presented in Section 7.1.6 is one of several possible strategies for realizing an approximate nearest neighbor index. See also [`SimilaritySearchEngine`](./in3120/similaritysearchengine.py) and comments therein.

Section 7.2.2 discusses query-term proximity and defines the notion of a minimal window width _ω_, but does not discuss how to actually compute the value _ω_. See [`WindowFinder`](./in3120/windowfinder.py) for a practical and linear algorithm for this.

## [Chapter 8](https://nlp.stanford.edu/IR-book/pdf/08eval.pdf)

See [`EvaluationMetrics`](./in3120/evaluationmetrics.py) for basic implementations of many of the evaluation metrics from Sections 8.3 and 8.4.

In Section 8.7 the concept of a result snippet is introduced. Result snippets are often produced by finding windows in the matching documents that are as short and query-term dense as possible. See the [`WindowFinder`](./in3120/windowfinder.py) class for an example of finding such windows.

## [Chapter 9](https://nlp.stanford.edu/IR-book/pdf/09expand.pdf)

Section 9.2 talks about global methods for query reformulation, e.g., doing synonym expansion using a manual thesaurus. In such cases we have the subproblem of detecting which words or phrases in a string (either a document or a query) that need to be expanded, and to do that efficiently as the size of our expansion dictionary grows. The go-to algorithm for doing this is not described in the textbook but in [this paper](./papers/efficient-string-matching.pdf), and a simplified variant of it is implemented by the [`StringFinder`](./in3120/stringfinder.py) class. The dictionary of known strings is assumed kept in a [`Trie`](./in3120/trie.py)

## [Chapter 13](https://nlp.stanford.edu/IR-book/pdf/13bayes.pdf)

A lot of the examples given in the introduction to Chapter 13 fit into things that happen at document-processing time, and that would hook into [`DocumentPipeline`](./in3120/documentpipeline.py) as individual processors. For example, to be able to narrow your searches to documents that belong to a given category. One could of course have classification logic taking place on queries, too, e.g., to make programmatic decisions on how the query should be processed.

Section 13.2 presents the multinomial Naïve Bayes model for text classification. An implementation of this can be found in [`NaiveBayesClassifier`](./in3120/naivebayesclassifier.py).

Although not covered by the textbook, the concept of efficiently detecting and extracting "interesting" strings is key in many document- and/or query-processing applications. Also sometimes for text classification applications: For example, if a document contains an overwhelming amount of medical jargon, it might make sense to classify the document as belonging to the _medicine_ category, or if a query contains enough unambiguously offensive words or phrases then it might make sense to classify the query as belonging to the _offensive_ category. But what exactly is "medical jargon" or "offensive words or phrases"? Sometimes we might actually already know or require control of this in the way of having access to extensive dictionaries of names of diseases, treatments, drugs, swear words, and so on. The problem then becomes how to detect which dictionary entries that occur in your text to process and that also occur in your dictionary of known strings. And, specifically, how to do this very efficiently when your dictionary of known strings becomes quite large. Again, this is addressed by the [`StringFinder`](./in3120/stringfinder.py) class. Applied to classification scenarios, this could also be thought of as manual or dictionary-controlled feature selection, feature selection being described in Section 13.5.

## [Chapter 14](https://nlp.stanford.edu/IR-book/pdf/14vcat.pdf)

Section 14.2 introduces the notion of a centroid. For example code related to computing the centroid of a set of sparse vectors, see the [`SparseDocumentVector`](./in3120/sparsedocumentvector.py) class. Code that demonstrates the use of these for classification purposes per the Rocchio classification algorithm is found in the [`RocchioClassifier`](./in3120/rocchioclassifier.py) class.

The _k_ nearest neighbour classification algorithm described in Section 14.3 is really composed of two steps: First we do a _k_ nearest neighbour search in our set of training examples, and then we apply some kind of voting logic on the matching examples to arrive at a classification decision. The [`SimilaritySearchEngine`](./in3120/similaritysearchengine.py) class realizes the initial similarity search step, using an approximate nearest neighbor index and dense vectors: With large amounts of data points and many dimensions in our vector space, we might want to be able to do such lookups approximately and sacrifice correctness for efficiency. Code that demonstrates the _k_ nearest neighbour classification algorithm is found in the [`NearestNeighborClassifier`](./in3120/nearestneighborclassifier.py) class.

## [Chapter 15](https://nlp.stanford.edu/IR-book/pdf/15svm.pdf)

Section 15.4.1 gives a simple example of machine-learned scoring. For a practical demonstration of how the feature _ω_ is computed, see the [`WindowFinder`](./in3120/windowfinder.py) class. For a practical demonstration of how the feature _α_ is computed, see the [`SparseDocumentVector`](./in3120/sparsedocumentvector.py) class.

## [Chapter 21](https://nlp.stanford.edu/IR-book/pdf/21link.pdf)

Section 21.2 presents the random surfer model and PageRank, which is one of many ways to assign a static quality score _g(d)_ (cf. Section 7.1.4) to a document _d_ in a graph of interconnected documents or web pages. Code that demonstrates how PageRank scores can be computed is found in the [`PageRank`](./in3120/pagerank.py) class.

## Other

The topics of entity extraction or [named entity recognition](https://en.wikipedia.org/wiki/Named-entity_recognition) are not really covered by the textbook, but can have an important place in many search applications. For example, in a document processing pipeline we might want to have code that recognizes and extracts the names of people, locations, dates, companies, and so on. If we have extensive dictionaries with high coverage at our disposal then the [`StringFinder`](./in3120/stringfinder.py) class might come in handy, but often we don't have any such lexical resources available that have sufficient coverage. There are many tools and techniques available to us in such cases (e.g., large language models, part-of-speech taggers, grammars, regular expressions, and more), and the [`ShallowCaseExtractor`](./in3120/shallowcaseextractor.py) class demonstrates a very simple example of a surface-level approach for doing this. The underlying regular expression that drives the extraction process is machine-generated from a simple grammar by help of the [`ExpressionComposer`](./in3120/expressioncomposer.py) class.

A simple implementation of a [Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter) can be found in the [`BloomFilter`](./in3120/bloomfilter.py) class. Bloom filters are not covered by the textbook. A Bloom filter is a probabilistic data structure for checking set membership that is commonly used in various places in large-scale search systems, e.g., to avoid unnecessary disk accesses. They were first described in [this paper](./papers/space-time-trade-offs-in-hash-coding-with-allowable-errors.pdf).

Many machine learning models, including text classifiers and neural networks, are typically trained using some flavor of [gradient descent](https://en.wikipedia.org/wiki/Gradient_descent) as presented in [these slides](./slides/gradient-descent.pdf). A simple demonstration implementation of how gradient descent works together with the sparse vectors from Chapter 6 can be found in the [`BinaryLogisticRegressionClassifier`](./in3120/binarylogisticregressionclassifier.py) class. Note that gradient descent assumes a smooth and differentiable function to optimize, i.e., the gradient actually has to exist. [Subgradient methods](https://stanford.edu/class/ee364b/lectures/subgrad_method_notes.pdf) can be applied for non-differentiable functions, e.g., as demonstrated [here](https://people.csail.mit.edu/dsontag/courses/ml16/slides/lecture5.pdf) for SVMs. This is beyond the scope of this course, though.
