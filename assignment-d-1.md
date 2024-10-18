# Assignment D-1

**Deadline:** 2024-10-25

The purpose of this assignment is threefold:

- Implement a better ranker than the `SimpleRanker` class. For example, inverse document frequency (i.e., considering how frequent the query terms are across the corpus) and static rank (i.e., a query-independent quality score per document) are two factors that you should include.
- Realize a simple search engine that is capable of approximate matching, e.g., where the query _organik kemmistry_ matches documents containing the terms _organic chemistry_. We will do this by using a tokenizer that produces _k_-grams (i.e., overlapping "shingles" of width _k_) and combine this with _n_-of-_m_ matching. For example, for _k_ = 3, the string _banana_ would be tokenized into the shingles {_ban_, _ana_, _nan_, _ana_}.
- Implement basic methods related to sparse document vectors. For example, related to computing dot products, cosine similarities, and centroids.

Your solution should only contain edits to the files [`shinglegenerator.py`](./in3120/shinglegenerator.py), [`sparsedocumentvector.py`](./in3120/sparsedocumentvector.py), and [`betterranker.py`](./in3120/betterranker.py). Changes to other files will be ignored.

Implementation notes:

- The `BetterRanker` class implements a better ranker than the `SimpleRanker` class. You are not required to compute a static rank score _g(d)_ for each document _d_, but can for the sake of simplicity assume that this value is stored in a suitably named document field. If the named field is missing or doesn't have a value, a default static rank score of 0.0 can be assumed.
- The `ShingleGenerator` class implements a tokenizer that produces character-level shingles.
- The `SparseDocumentVector` class provides a representation of a sparse document vector, and is a basic building block used by, e.g., the [`RocchioClassifier`](./in3120/rocchioclassifier.py) class.

Your task is to:

- Familiarize yourself with the precode.
- Implement the missing code in the `BetterRanker` class.
- Implement the missing code in the `ShingleGenerator` class.
- Implement the missing code in the `SparseDocumentVector` class.
- Ensure that the code is correct and passes all tests.

Some optional bonus challenges for the interested student:

- Extend your `ShingleGenerator` implementation to make special provisions for the beginning and/or ending of strings, so that these are given more weight than other parts of the words. For example, _banana_ could be processed as _^banana$_ where the special marker symbols _^_ and _$_ are added as padding. Do you think this makes a difference?
- The `WordShingleGenerator` class does token- or term-level shingling. Experiment with using this to realize a biword index.
- When working with shingles, the Jaccard distance between the set of shingles in the query and the set of shingles in the document is sometimes used as a relevancy measure. Write a ranker that implements this.
- Extend your ranker to additionally post-process all matches so that edit distance influences the ranking.
- Extend your ranker to take document length into account. See [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) for inspiration.
- Extend the `SimpleNormalizer` class to do various linguistically motivated transformations or replace its use with, e.g., `PorterNormalizer` or even `SoundexNormalizer`. Do you think this makes a difference when combined with standard tokenization as performed by the `SimpleTokenizer` class?

Example output:

```
>cd tests
>python3 assignments.py d-1
test_document_id_mismatch (test_betterranker.TestBetterRanker.test_document_id_mismatch) ... ok
test_inverse_document_frequency (test_betterranker.TestBetterRanker.test_inverse_document_frequency) ... ok
test_static_quality_score (test_betterranker.TestBetterRanker.test_static_quality_score) ... ok
test_term_frequency (test_betterranker.TestBetterRanker.test_term_frequency) ... ok
test_ranges (test_shinglegenerator.TestShingleGenerator.test_ranges) ... ok
test_shingled_mesh_corpus (test_shinglegenerator.TestShingleGenerator.test_shingled_mesh_corpus) ... ok
test_strings (test_shinglegenerator.TestShingleGenerator.test_strings) ... ok
test_tokens (test_shinglegenerator.TestShingleGenerator.test_tokens) ... ok
test_uses_yield (test_shinglegenerator.TestShingleGenerator.test_uses_yield) ... ok
test_centroid (test_sparsedocumentvector.TestSparseDocumentVector.test_centroid) ... ok
test_cosine (test_sparsedocumentvector.TestSparseDocumentVector.test_cosine) ... ok
test_dot_product (test_sparsedocumentvector.TestSparseDocumentVector.test_dot_product) ... ok
test_length (test_sparsedocumentvector.TestSparseDocumentVector.test_length) ... ok
test_normalize_empty (test_sparsedocumentvector.TestSparseDocumentVector.test_normalize_empty) ... ok
test_normalize_nonempty (test_sparsedocumentvector.TestSparseDocumentVector.test_normalize_nonempty) ... ok
test_top (test_sparsedocumentvector.TestSparseDocumentVector.test_top) ... ok
test_truncate (test_sparsedocumentvector.TestSparseDocumentVector.test_truncate) ... ok

----------------------------------------------------------------------
Ran 17 tests in 1.266s

OK
```

```
>python3 repl.py d-1
Indexing MeSH corpus...
Enter a query and find matching documents.
Lookup options are {'debug': False, 'hit_count': 5, 'match_threshold': 0.5}.
Tokenizer is ShingleGenerator.
Ranker is SimpleRanker.
Ctrl-C to exit.
query>orgaNik kemmistry
[{'document': {'document_id': 16981, 'fields': {'body': 'organic chemistry processes', 'meta': '27'}},
  'score': 8.0},
 {'document': {'document_id': 16980, 'fields': {'body': 'organic chemistry phenomena', 'meta': '27'}},
  'score': 8.0},
 {'document': {'document_id': 4411, 'fields': {'body': 'chemistry, organic', 'meta': '18'}},
  'score': 8.0},
 {'document': {'document_id': 4410, 'fields': {'body': 'chemistry, inorganic', 'meta': '20'}},
  'score': 8.0},
 {'document': {'document_id': 4408, 'fields': {'body': 'chemistry, bioinorganic', 'meta': '23'}},
  'score': 8.0}]
Evaluation took 0.013234000000000634 seconds.
query>^C
Bye!
```

```
>python3 repl.py d-2
Indexing English news corpus...
Enter a query and find matching documents.
Lookup options are {'debug': False, 'hit_count': 5, 'match_threshold': 0.5}.
Normalizer is SimpleNormalizer.
Tokenizer is SimpleTokenizer.
Ranker is BetterRanker.
Ctrl-C to exit.
query>water in the tank
[{'document': {'document_id': 157, 'fields': {'body': "A Chinese People's Liberation Army cadet sits in a Main Battle Tank during a demonstration at the PLA's Armoured Forces Engineering Academy Base, July 22, 2014."}},
  'score': 4.159666535003645},
 {'document': {'document_id': 2818, 'fields': {'body': 'He noted that 50 percent of his 71 Shark Tank investments have been in female-led companies.'}},
  'score': 3.9779290398903395},
 {'document': {'document_id': 7655, 'fields': {'body': "Their lawyer, Fernando Chavez, said a collision with the Jeep's plastic gas tank behind the rear axle caused it to burst into flames."}},
  'score': 3.758759727635914},
 {'document': {'document_id': 7398, 'fields': {'body': 'The elevated salt levels in the water threatened some of the wildlife in the area that depend on a supply of fresh water.'}},
  'score': 3.746312408070838},
 {'document': {'document_id': 9699, 'fields': {'body': 'While there are not many people in the water during the winter months, there are plenty playing by the shore with their jeans rolled up just enough so that they can feel the cool water lap up against their feet.'}},
  'score': 3.6091585529242174}]
Evaluation took 0.014417600999877322 seconds.
query>^C
Bye!
```

```
>python3 repl.py x-6
Initializing Rocchio classifier from movie corpus...
Enter some text and have it classified as a movie genre.
Ctrl-C to exit.
text>It was a dark and stormy night.
[{'category': 'Horror', 'score': 0.09401124737117747},
 {'category': 'Thriller', 'score': 0.07818261918043858},
 {'category': 'Mystery', 'score': 0.07640408674526705},
 {'category': 'Romance', 'score': 0.062220941484383556},
 {'category': 'Fantasy', 'score': 0.06041547517917066},
 {'category': 'Drama', 'score': 0.05547877862410392},
 {'category': 'Comedy', 'score': 0.04404293794572259},
 {'category': 'Sci-Fi', 'score': 0.03619449355029178},
 {'category': 'Crime', 'score': 0.03318476743126697},
 {'category': 'Family', 'score': 0.031568925471141276},
 {'category': 'Action', 'score': 0.030971438280831806},
 {'category': 'Adventure', 'score': 0.027093731733426146},
 {'category': 'History', 'score': 0.020218785708303797}]
Evaluation took 0.014864500146359205 seconds.
text>^C
Bye!
```
