# Assignment A

**Deadline:** 2024-09-13

The purpose of this assignment is to build a simple in-memory inverted index and show how to merge posting lists.

Your solution should only contain edits to the files [`invertedindex.py`](./in3120/invertedindex.py) and [`postingsmerger.py`](./in3120/postingsmerger.py). Changes to other files will be ignored.

Implementation notes:

- The `InMemoryInvertedIndex` class implements a simple inverted index. We create an inverted index from a corpus (i.e., a collection of documents) as represented by the `InMemoryCorpus` class.
- After having indexed the corpus (or at least a specified set of fields in the documents) and created an `InMemoryInvertedIndex` object, we will have created a dictionary of indexed terms as represented by the `InMemoryDictionary` class, and a posting list for each term. Each posting in a posting list should keep track of the document identifier and the number of times the term occurs in the identified document. The resulting posting lists must be sorted in ascending order by document identifiers.
- For text normalization and tokenization purposes, you can use the `SimpleNormalizer` and `SimpleTokenizer` classes.
- With _N_ unique terms, you can assume that the `InMemoryDictionary` class assigns identifiers to terms in the range [_0, ..., N - 1_].
- You might find the `Counter` class in the built-in `collections` module useful.
- Your implementations in `PostingsMerger` should be linear in the length of the posting lists, and should not make use of temporary data structures.
- The `BooleanSearchEngine` class uses `PostingsMerger` as a helper for evaluating complex Boolean expressions.

Your task is to:

- Familiarize yourself with the precode.
- Implement the missing indexing code in the `InMemoryInvertedIndex` class.
- Implement the missing code for merging two posting lists in the `PostingsMerger` class.
- Ensure that the code is correct and passes all tests.

Some optional bonus challenges for the interested student:

- The implementations for the `AND` and `OR` operators take two posting lists as arguments. Can you generalize your implementations to be _n_-ary instead of binary, i.e., how would you efficiently traverse _n_ posting lists in "parallel"?
- Implement an `XOR` operator, sometimes called "symmetric difference".
- Extend your posting list implementation to include skip lists, extend your indexing code to build these, and extend your merging code to make good use of this additional data structure.
- Integrate any extensions you make into the `BooleanSearchEngine` class.

Example output:

```
>cd tests
>python3 assignments.py a
test_access_postings (test_inmemoryinvertedindexwithoutcompression.TestInMemoryInvertedIndexWithoutCompression.test_access_postings) ... ok
test_access_vocabulary (test_inmemoryinvertedindexwithoutcompression.TestInMemoryInvertedIndexWithoutCompression.test_access_vocabulary) ... ok
test_mesh_corpus (test_inmemoryinvertedindexwithoutcompression.TestInMemoryInvertedIndexWithoutCompression.test_mesh_corpus) ... ok
test_multiple_fields (test_inmemoryinvertedindexwithoutcompression.TestInMemoryInvertedIndexWithoutCompression.test_multiple_fields) ... ok
test_empty_lists (test_postingsmerger.TestPostingsMerger.test_empty_lists) ... ok
test_ends_with_same_so_tail_is_empty (test_postingsmerger.TestPostingsMerger.test_ends_with_same_so_tail_is_empty) ... ok
test_order_dependence (test_postingsmerger.TestPostingsMerger.test_order_dependence) ... ok
test_order_independence (test_postingsmerger.TestPostingsMerger.test_order_independence) ... ok
test_uncompressed_mesh_corpus (test_postingsmerger.TestPostingsMerger.test_uncompressed_mesh_corpus) ... ok
test_uses_yield (test_postingsmerger.TestPostingsMerger.test_uses_yield) ... ok
test_malformed_queries (test_booleansearchengine.TestBooleanSearchEngine.test_malformed_queries) ... ok
test_optimization (test_booleansearchengine.TestBooleanSearchEngine.test_optimization) ... ok
test_valid_expressions (test_booleansearchengine.TestBooleanSearchEngine.test_valid_expressions) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.437s

OK
```

```
>python3 repl.py a-1
Building inverted index from Cranfield corpus...
Enter one or more index terms and inspect their posting lists.
Ctrl-C to exit.
terms>break stop million
{'break': [{'document_id': 176, 'term_frequency': 1},
           {'document_id': 372, 'term_frequency': 1},
           {'document_id': 520, 'term_frequency': 1},
           {'document_id': 1247, 'term_frequency': 1}],
 'million': [{'document_id': 164, 'term_frequency': 8},
             {'document_id': 204, 'term_frequency': 1},
             {'document_id': 433, 'term_frequency': 1},
             {'document_id': 779, 'term_frequency': 1},
             {'document_id': 795, 'term_frequency': 1},
             {'document_id': 1213, 'term_frequency': 1},
             {'document_id': 1380, 'term_frequency': 1}],
 'stop': []}
Evaluation took 0.0001183999999980756 seconds.
terms>^C
Bye!
```

```
>python3 repl.py a-2
Building inverted index from English name corpus...
Enter a complex Boolean query expression and find matching documents.
Ctrl-C to exit.
query>AND(alexander, OR(davis, pratt))
[{'document': {'document_id': 1968, 'fields': {'body': 'Alexander Davis'}}},
 {'document': {'document_id': 2667, 'fields': {'body': 'Alexander Pratt'}}}]
Evaluation took 0.0003144000002066605 seconds.
query>^C
Bye!
```
