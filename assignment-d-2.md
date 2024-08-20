# Assignment D-2

**Deadline:** 2024-10-25

The purpose of this assignment is to explore a compression algorithm of your choice for compressing posting lists, and to compare this with the `CompressedInMemoryPostingList` implementation in [`postinglist.py`](in3120/postinglist.py).

Your task is to:

- Familiarize yourself with the precode.
- Implement an alternative compression algorithm of your choice, either from scratch or by use of a suitable open-source library.
- Devise and run selected experiments where you quantitatively compare the provided `CompressedInMemoryPostingList` implementation with your alternative implementation.
- Write a short report that summarizes your experiments, observations and findings. You are expected to cover the speed of compression and decompression, as well as differences in space savings.

Your deliverables for this assignment include the source code you write, plus the report.

The `CompressedInMemoryPostingList` class implements variable-byte encoding of gaps between consecutive document identifers. Select another compression algorithm of your choice. Plausible choices include, e.g., Gamma codes, Simple9, PFOR-DELTA, Rice coding, Golomb coding, LZ4, DEFLATE, Snappy, Zstd, or something else. For inspiration see, e.g., [here](slides/compression.pdf) or [here](papers/decoding-billions-of-integers-per-second.pdf) or search the web. You are allowed to make use of open-source libraries, if you don't want to implement the compression algorithm from scratch.

Implementation notes:

- The `InMemoryInvertedIndex` class instantiates `CompressedInMemoryPostingList` objects if the `compressed` constructor argument is set to `True`.
- You can swap out the internals of `CompressedInMemoryPostingList` with your alternative implementation, and/or create a new class.
- Compression can happen per posting list as in `CompressedInMemoryPostingList` or across posting lists. You decide, as long as the interfaces in the precode don't change.
- Make sure you have a sensible test battery as you develop your code as "proof" of working code, and create new unit tests as needed. You may or may not want to extend and tweak the tests in `TestCompressedInMemoryPostingList` and `TestInMemoryInvertedIndexWithCompression`. See example output below for inspiration.

Report notes:

- Strive for clarity: What did you do? Why did you do it? How did you structure and run your experiments? What are your findings and observations? How do your experiments support your conclusions?
- Critique your work: How could you have improved things further? How confident are you in your conclusions? What could you do to make your claims even more scientifically valid? What are possible sources of errors in your experiments?
- Keep it structured: Summarize the important things in the body of your report. Stuff details in an appendix. Consider adhering to the [IMRAD](https://en.wikipedia.org/wiki/IMRAD) structure.
- Be concise: You are not writing a PhD thesis. But the body of your report must be at least 600 words.

Example output, for inspiration:

```
>cd tests
>python3 test_compressedinmemorypostinglist.py
test_append_and_iterate (__main__.TestCompressedInMemoryPostingList.test_append_and_iterate) ... ok
test_invalid_append (__main__.TestCompressedInMemoryPostingList.test_invalid_append) ... ok
test_mesh_corpus (__main__.TestCompressedInMemoryPostingList.test_mesh_corpus) ... ok
test_append_and_iterate (test_inmemorypostinglist.TestInMemoryPostingList.test_append_and_iterate) ... ok
test_invalid_append (test_inmemorypostinglist.TestInMemoryPostingList.test_invalid_append) ... ok
test_empty_lists (test_postingsmerger.TestPostingsMerger.test_empty_lists) ... ok
test_order_independence (test_postingsmerger.TestPostingsMerger.test_order_independence) ... ok
test_uncompressed_mesh_corpus (test_postingsmerger.TestPostingsMerger.test_uncompressed_mesh_corpus) ... ok
test_uses_yield (test_postingsmerger.TestPostingsMerger.test_uses_yield) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.714s

OK
```

```
>python3 test_variablebytecodec.py
test_encode_and_decode (__main__.TestVariableByteCodec.test_encode_and_decode) ... ok
test_illegal_decoding_offsets (__main__.TestVariableByteCodec.test_illegal_decoding_offsets) ... ok
test_missing_buffer (__main__.TestVariableByteCodec.test_missing_buffer) ... ok
test_negative_numbers (__main__.TestVariableByteCodec.test_negative_numbers) ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.002s

OK
```

```
>python3 test_inmemoryinvertedindexwithcompression.py
test_access_postings (__main__.TestInMemoryInvertedIndexWithCompression.test_access_postings) ... ok
test_memory_usage (__main__.TestInMemoryInvertedIndexWithCompression.test_memory_usage) ... ok
test_mesh_corpus (__main__.TestInMemoryInvertedIndexWithCompression.test_mesh_corpus) ... ok
test_multiple_fields (__main__.TestInMemoryInvertedIndexWithCompression.test_multiple_fields) ... ok
test_access_postings (test_inmemoryinvertedindexwithoutcompression.TestInMemoryInvertedIndexWithoutCompression.test_access_postings) ... ok
test_mesh_corpus (test_inmemoryinvertedindexwithoutcompression.TestInMemoryInvertedIndexWithoutCompression.test_mesh_corpus) ... ok
test_multiple_fields (test_inmemoryinvertedindexwithoutcompression.TestInMemoryInvertedIndexWithoutCompression.test_multiple_fields) ... ok

----------------------------------------------------------------------
Ran 7 tests in 5.143s

OK
```
