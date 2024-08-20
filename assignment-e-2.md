# Assignment E-2

**Deadline:** 2024-11-08

The purpose of this assignment is to explore alternative embedding methods and/or approximate nearest neighbor (ANN) index structures, and to compare these with the `SimilaritySearchEngine` implementation in [`similaritysearchengine.py`](in3120/similaritysearchengine.py).

Your task is to:

- Familiarize yourself with the precode.
- Implement an alternative embedding generation implementation of your choice and/or an alternative ANN index structure. You can make use of suitable open-source libraries.
- Devise and run selected experiments where you quantitatively compare the provided `SimilaritySearchEngine` implementation with your alternative implementation.
- Write a short report that summarizes your experiments, observations and findings. You are expected to cover speed, scalability, and search quality aspects.

Your deliverables for this assignment include the source code you write, plus the report.

The `SimilaritySearchEngine` class uses [spaCy](https://spacy.io/) to generate the embedding vectors, and [FAISS](https://github.com/facebookresearch/faiss) to realize the ANN index. You can continue to use these libraries, if you want, e.g., by pulling in other spaCy models, or by passing other arguments to the FAISS index factory, or by using the GPU-version of FAISS instead of the CPU-version (if you have a GPU), or by specifying another index type argument to the FAISS index factory. Or, if you want, you can opt to replace one or both of these with alternative open-source libraries.

Implementation notes:

- To facilitate comparisons, it's recommended that you copy `SimilaritySearchEngine` into a new class `AlternativeSimilaritySearchEngine` and work on this.
- In addition to exploring alternative embedding methods and/or approximate ANN index structures, if you want you can also make `AlternativeSimilaritySearchEngine` more scalable by adding support for batching.
- To investigate speed and scalability differences, search the web for a larger corpus if none of the supplied corpora in the [`data`](data/) folder sufficiently push the boundaries.
- Make sure you have a sensible test battery as you develop your code as "proof" of working code, and create new unit tests as needed. You may or may not want to extend and tweak the tests in `TestSimilaritySearchEngine`. See example output below for inspiration.

Report notes:

- Strive for clarity: What did you do? Why did you do it? How did you structure and run your experiments? What are your findings and observations? How do your experiments support your conclusions?
- Critique your work: How could you have improved things further? How confident are you in your conclusions? What could you do to make your claims even more scientifically valid? What are possible sources of errors in your experiments?
- Keep it structured: Summarize the important things in the body of your report. Stuff details in an appendix. Consider adhering to the [IMRAD](https://en.wikipedia.org/wiki/IMRAD) structure.
- Be concise: You are not writing a PhD thesis. But the body of your report must be at least 600 words.

Example output, for inspiration:

```
>cd tests
>python3 test_similaritysearchengine.py
test_client_can_control_number_of_hits (__main__.TestSimilaritySearchEngine.test_client_can_control_number_of_hits) ... ok
test_empty_corpus_barfs (__main__.TestSimilaritySearchEngine.test_empty_corpus_barfs) ... ok
test_empty_query_yields_no_results (__main__.TestSimilaritySearchEngine.test_empty_query_yields_no_results) ... ok
test_querying_with_indexed_document_yields_itself_with_perfect_cosine_score (__main__.TestSimilaritySearchEngine.test_querying_with_indexed_document_yields_itself_with_perfect_cosine_score) ... ok

----------------------------------------------------------------------
Ran 4 tests in 1.011s

OK
```

```
>python3 repl.py x-4
Indexing English news corpus using an ANN index...
Enter a query and find matching documents.
Lookup options are {'hit_count': 5}.
Ctrl-C to exit.
query>horror movie
[{'document': {'document_id': 9731, 'fields': {'body': 'Why is television more diverse than film?'}},
  'score': 0.4408549},
 {'document': {'document_id': 1329, 'fields': {'body': 'But not every audience member approaches sci-fi like that.'}},
  'score': 0.4343021},
 {'document': {'document_id': 168, 'fields': {'body': 'Actress, Drama Series: Viola Davis, "How to Get Away With Murder," ABC.'}},
  'score': 0.41439927},
 {'document': {'document_id': 430, 'fields': {'body': 'Amy Berg, whose "Deliver Us from Evil" (2006) was nominated for an Oscar, premiered her latest film "Prophet\'s Prey" at the Sundance Film Festival this week.'}},
  'score': 0.4072854},
 {'document': {'document_id': 5288, 'fields': {'body': 'NOW: After The Rocky Horror Picture Show, Nell focused on music.'}},
  'score': 0.39200836}]
Evaluation took 0.0036097000120207667 seconds.
query>organic chemistry
[{'document': {'document_id': 972, 'fields': {'body': 'Baby-suitable foods used in the study included smooth peanut butter, peanut soup and finely ground peanuts mixed into yogurt and other foods.'}},
  'score': 0.660955},
 {'document': {'document_id': 1472, 'fields': {'body': 'By integrating the use of different therapies, including botanical medicine, homeopathic medicine, and nutritional therapy, my patients have found great results and increased their quality of life.'}},
  'score': 0.6293555},
 {'document': {'document_id': 912, 'fields': {'body': 'At the farm level, agroecology means developing and using economically viable practices that work with nature rather than against it.'}},
  'score': 0.6253581},
 {'document': {'document_id': 2630, 'fields': {'body': 'Harnessing microbiomes could cure disease, reduce resistance to antibiotics, rejuvenate depleted farmland, moderate fertilizer and pesticide use, and convert sunlight into useful chemicals.'}},
  'score': 0.6243331},
 {'document': {'document_id': 7097, 'fields': {'body': "The attorney general's office for environmental protection said Tuesday the problems involved waste waters from a coffee processing plant and two fish packing plants in Puerto Chiapas."}},
  'score': 0.6212893}]
Evaluation took 0.010923600057139993 seconds.
query>^C
Bye!
```
