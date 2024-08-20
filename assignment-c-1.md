# Assignment C-1

**Deadline:** 2024-10-11

The purpose of this assignment is to implement a simple query evaluator that efficiently performs _n_-of-_m_ matching over a simple memory-based inverted index. I.e., if the query contains _m_ unique query terms, each document in the result set should contain at least _n_ of these _m_ terms. For example, 2-of-3 matching over the query _orange apple banana_ would be logically equivalent to the following predicate:

    (orange AND apple) OR (orange AND banana) OR (apple AND banana)

Note that _n_-of-_m_ matching can be viewed as a type of "soft `AND`" evaluation, where the degree of match can be smoothly controlled to mimic either an `OR` evaluation (1-of-_m_), or an `AND` evaluation (_m_-of-_m_), or something in between.

The evaluator should use the client-supplied ratio _t = n/m_ as a parameter as specified by the client on a per query basis. For example, for the query _john paul george ringo_ we have _m = 4_ and a specified threshold of _t = 0.7_ would imply that at least 3 of the 4 query terms have to be present in a matching document. You can infer _n_ as:

    n = max(1, min(m, int(t * m)))

The results should be ranked and yielded back to the client according to relevancy. For example, continuing the previous example, it is reasonable to expect that a document that contains all of _orange_, _apple_ and _banana_ to be ranked above a document that contains _orange_ and _apple_ but not _banana_. How many documents to be returned should be controlled on a per query basis as specified by the client.

Note that _m_ above is assumed to be the number of unique query terms. For the 3-term query _bye bye baby_, _m = 2_ and we say that the term _bye_ has multiplicity 2 and the term _baby_ has multiplicity 1. The multiplicity can be taken into account by the ranker.

Your solution should only contain edits to the file [`simplesearchengine.py`](./in3120/simplesearchengine.py). Changes to other files will be ignored.

Implementation notes:

- The `SimpleSearchEngine` class implements a simple search engine that evaluates queries as specified. We are given a corpus and an inverted index built over that same corpus.
- Use document-at-a-time traversal to implement the query evaluation. Your implementation must not iterate over the full corpus, but should iterate over multiple posting lists in parallel.
- Relevancy scores are assessed using a ranker object that we pass in to the query evaluation routine. You can use the `SimpleRanker` class for this.
- The `Sieve` class is useful for sifting the relevancy scores so that we are left with only the best-ranking documents.

Your task is to:

- Familiarize yourself with the precode.
- Implement the missing query evaluation code in the `SimpleSearchEngine` class.
- Ensure that the code is correct and passes all tests.

Some optional bonus challenges for the interested student:

- Can you implement a better ranker? Note how `SimpleRanker` gives equal weight to stopwords and more information-carrying terms.
- How would you use your implementation to realize a simple search engine that was capable of approximate matching, e.g., where the query _organik kemmistry_ matched documents containing the terms _organic chemistry_?
- How would you extend and modify your implementation to include ideas described in [this](papers/efficient-query-evaluation.pdf) paper?

Example output:

```
>cd tests
>python3 assignments.py c
test_document_at_a_time_traversal_mesh_corpus (tests.TestSimpleSearchEngine) ... ok
test_mesh_corpus (tests.TestSimpleSearchEngine) ... ok
test_synthetic_corpus (tests.TestSimpleSearchEngine) ... ok
test_uses_yield (tests.TestSimpleSearchEngine) ... ok

----------------------------------------------------------------------
Ran 4 tests in 1.798s

OK
```

```
>python3 repl.py c-1
Indexing English news corpus...
Enter a query and find matching documents.
Lookup options are {'debug': False, 'hit_count': 5, 'match_threshold': 0.5}.
Tokenizer is SimpleTokenizer.
Ranker is SimpleRanker.
Ctrl-C to exit.
query>wATer  pollution
[{'document': {'document_id': 9699, 'fields': {'body': 'While there are not many people in the water during the winter months, there are plenty playing by the shore with their jeans rolled up just enough so t
hat they can feel the cool water lap up against their feet.'}},
  'score': 2.0},
 {'document': {'document_id': 7398, 'fields': {'body': 'The elevated salt levels in the water threatened some of the wildlife in the area that depend on a supply of fresh water.'}},
  'score': 2.0},
 {'document': {'document_id': 5854, 'fields': {'body': 'Polluted air, on the other hand, contains water-soluble particles, leading to clouds with more, yet smaller, water droplets.'}},
  'score': 2.0},
 {'document': {'document_id': 4515, 'fields': {'body': 'Kate Kralman, who shot the video of the MAX going through the water, was helping a friend load equipment nearby when she saw one light rail train go thr
ough the water.'}},
  'score': 2.0},
 {'document': {'document_id': 354, 'fields': {'body': "A lot of people are disputing that climate change is a reality because they don't see everybody going under water."}},
  'score': 1.0}]
Evaluation took 0.0006383000000056427 seconds.
query>^C
Bye!
```
