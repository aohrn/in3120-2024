# Assignment B-2

**Deadline:** 2024-09-27

The purpose of this assignment is to implement the core idea outlined in [the paper by Shang and Merrett](./papers/tries-for-approximate-string-matching.pdf), that shows how to reasonably efficiently compute the bounded edit distance between a query string and a large collection of candidate strings. The collection of candidate strings are represented in a [trie](./slides/strings-galore.pdf). For example, for the query _banana_ I should get back the _n_ strings in my string collection that have the smallest edit distance to _banana_. We can bound the edit distance, so that we only report matches that are less than or equal to _k_ edits away from the query string. Imposing such an upper bound allows us to prune down the search space and evaluate far fewer candidates than otherwise needed.

To achieve this your task is twofold:

- Implement the required edit table logic required to compute [Damerau-Levenshtein distance](https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance), and equip the edit table with an interface suitable to be used together with a trie search as described in the paper by Shang and Merrett. I.e., your implemenation should be able to correctly compute both the edit distance between two arbitrary, known strings of reasonable length, as well as enable a column-by-column computation driven by a search procedure external to the table.
- Implement an efficient search procedure over the trie, that uses your edit table implementation. I.e., branches in your trie that correspond to an edit distance larger than _k_ from the query should not be visited and evaluated.

Your solution should only contain edits to the files [`edittable.py`](./in3120/edittable.py) and [`editsearchengine.py`](./in3120/editsearchengine.py). Changes to other files will be ignored.

Implementation notes:

- It might be a good idea to draw the data structures on a piece of paper before you start coding, to get clarity on how this should work.
- The `EditTable` class implements a simple edit table, that can be updated on a per column basis. Table rows correspond to the symbols in an immutable string we call _query_, and table columns correspond to the symbols in a mutable string we call _candidate_.
- The `EditSearchEngine` class takes a query string and finds all the candidate strings (or "enough" candidate strings, at least) in our collection of strings that are _k_ or fewer edits away from the query string. The collection of strings where we search for candidates is assumed represented by the `Trie` class.
- There might be a lot of candidate matches that are _k_ or fewer edits away from the query string. Only the _n_ best ones of these should be emitted back to the client, in ranked order. The `Sieve` helper class might come in handy for this. A candidate match is scored according to its edit distance to the query string, possibly including string-length normalization.
- For text normalization and tokenization purposes, you can use the `SimpleNormalizer` and `SimpleTokenizer` classes.

Your task is to:

- Familiarize yourself with the precode.
- Implement the missing code in the `EditTable` and `EditSearchEngine` classes.
- Ensure that the code is correct and passes all tests.

Some optional bonus challenges for the interested student:

- Implement Ukkonen's cutoff heuristic, for further efficiency. That way, you do not have to compute a full column but can abort as soon as the edit distance exceeds your upper bound.
- Extend your `EditSearchEngine` implementation with more lookup modes. For example, the assignment considers the case of a complete match between the query string and a candidate string. But what about, say, prefix matches?
- Extend the candidate scoring logic in your `EditSearchEngine` implementation to be aware about word frequencies in, say, English. Some words are rarely used while some are very frequent, so when we score a candidate we could factor in a measure of how frequently used the candidate is. Note that the `Trie` class supports keeping meta data (such as, e.g., some measure of frequency) along with each entry.
- Combine edit distance with phonetics, for added recall. For example, what if the trie we search over contained phonetic hashes of words instead of the original words themselves? Note that the matches we report back to the user should be the original words, not their phonetic hashes.
- How would we best extend our machinery to compute edit distances at the word-level and not at the character-level, or even combine the two? For example, at the word-level we'd have _d("gatsby great", "the great gatsby") = 2_.

Example output:

```
>cd tests
>python3 assignments.py b-2
test_distance (test_edittable.TestEditTable.test_distance) ... ok
test_stringify (test_edittable.TestEditTable.test_stringify) ... ok
test_candidate_count (test_editsearchengine.TestEditSearchEngine.test_candidate_count) ... ok
test_exact_match (test_editsearchengine.TestEditSearchEngine.test_exact_match) ... ok
test_first_n (test_editsearchengine.TestEditSearchEngine.test_first_n) ... ok
test_hit_count (test_editsearchengine.TestEditSearchEngine.test_hit_count) ... ok
test_invalid_scoring_function (test_editsearchengine.TestEditSearchEngine.test_invalid_scoring_function) ... ok
test_scores_are_sorted (test_editsearchengine.TestEditSearchEngine.test_scores_are_sorted) ... ok
test_upper_bound (test_editsearchengine.TestEditSearchEngine.test_upper_bound) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.020s

OK
```

```
>python repl.py b-5
Building trie from MeSH corpus...
Enter a query and find MeSH term that are approximate matches.
Lookup options are {'hit_count': 5, 'upper_bound': 2, 'first_n': 0, 'scoring': 'normalized'}.
Ctrl-C to exit.
query>gorilla
[{'distance': 2, 'match': 'perilla', 'score': 0.7142857142857143}]
Evaluation took 0.05873560003237799 seconds.
query>humans
[{'distance': 0, 'match': 'humans', 'score': 1.0},
 {'distance': 2, 'match': 'humanism', 'score': 0.75},
 {'distance': 2, 'match': 'furans', 'score': 0.6666666666666667}]
Evaluation took 0.0600300999940373 seconds.
query>^C
Bye!
```
