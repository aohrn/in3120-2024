# Assignment B-1

**Deadline:** 2024-09-27

The purpose of this assignment is twofold:

- Build a simple [suffix array](./papers/suffix-arrays.pdf) and implement "phrase prefix searches" using this. For example, for a supplied query phrase like _to the be_, we'd return documents that contain phrases like _to the bearnaise_, _to the best_, _to the behemoth_, and so on. I.e., we require that the query phrase starts on a token boundary in the document, but it doesn’t necessarily have to end on one.
- Given a [trie](./slides/strings-galore.pdf) ("dictionary") with a potentially very large number of entries (words and phrases of arbitrary length), implement a simple version of the [Aho-Corasick algorithm](./papers/efficient-string-matching.pdf) that efficiently detects the subset of dictionary entries that also occur within a given text buffer. For example, if the dictionary contains _harry potter_ and _wizard_, we'd efficiently detect the presence of these strings within the buffer _a wizard named harry potter_. Detected entries should start and end on token boundaries. If entries overlap in the document then all matches should be reported.

Your solution should only contain edits to the files [`suffixarray.py`](./in3120/suffixarray.py) and [`stringfinder.py`](./in3120/stringfinder.py). Changes to other files will be ignored.

Implementation notes:

- It might be a good idea to draw the data structures on a piece of paper before you start coding, to get clarity on how this should work.
- The `SuffixArray` class implements a simple suffix array, ignoring LCP information. We create a suffix array from a corpus (i.e., a collection of documents) as represented by the `InMemoryCorpus` class. After having indexed the corpus (or at least a specified set of fields in the documents) and created a `SuffixArray` object, we can query this and locate matching documents.
- Note that a document might match the query in multiple places. The documents should be ranked according to the match count, and emitted back to the client in ranked order. The `Sieve` helper class might come in handy for this.
- For lookups, your implementation of `SuffixArray` must for typical searches be logarithmic in the number of suffixes in the corpus. Its memory usage should also be sane, e.g., to represent a suffix use an integer index into the full string instead of making a new copy of the suffix string itself. When implementing searches across multiple document fields, you can assume that the Unicode character [`NULL`](https://www.fileformat.info/info/unicode/char/0000/index.htm) does not appear in normal text.
- A naïve construction of the suffix array is fine for this assignment. By naïve is meant building up an array that represents the possible suffixes, and then simply sorting this using a built-in sort.
- The `StringFinder` class scans the buffer once and finds all dictionary entries that occur in the given text buffer. The dictionary itself is assumed represented by the `Trie` class.
- For lookups, your implementation of `StringFinder` must for typical searches be linear in the size of the input buffer and almost insensitive to the size of the dictionary. Matches should be yielded back to the caller in the order in which they appear in the input buffer.
- For text normalization and tokenization purposes, you can use the `SimpleNormalizer` and `SimpleTokenizer` classes.

Your task is to:

- Familiarize yourself with the precode.
- Implement the missing indexing and evaluation code in the `SuffixArray` class.
- Implement the missing code in the `StringFinder` class.
- Ensure that the code is correct and passes all tests.

Some optional bonus challenges for the interested student:

- The `SuffixArray` class doesn’t compute or make use of LCP information. Extend your implementation to include this.
- Extend your `SuffixArray` implementation with a lookup mode that requires that matches also end on token boundaries, thus making this a proper phrase search.
- The `StringFinder` implementation finds and reports all matches, even if they overlap or include each other. For example, if the dictionary contains both _manchester united_ and _united nations_ then both entries would be reported within the buffer _manchester united nations_. Extend your `StringFinder` implementation with an option to do leftmost-longest matching, thus possibly suppressing some matches.
- Experiment with alternative normalizers together with `StringFinder`, e.g., to do case-sensitive matching, case-insensitive matching, phonetic matching, stemmed matching, and so on. How can you make sure to report back matches and ranges relative to the original input buffer?

Example output:

```
>cd tests
>python3 assignments.py b-1
test_canonicalized_corpus (test_suffixarray.TestSuffixArray.test_canonicalized_corpus) ... ok
test_cran_corpus (test_suffixarray.TestSuffixArray.test_cran_corpus) ... ok
test_memory_usage (test_suffixarray.TestSuffixArray.test_memory_usage) ... ok
test_multiple_fields (test_suffixarray.TestSuffixArray.test_multiple_fields) ... ok
test_uses_yield (test_suffixarray.TestSuffixArray.test_uses_yield) ... ok
test_add_is_idempotent (test_trie.TestTrie.test_add_is_idempotent) ... ok
test_add_is_idempotent_unless_meta_data_differs (test_trie.TestTrie.test_add_is_idempotent_unless_meta_data_differs) ... ok
test_child (test_trie.TestTrie.test_child) ... ok
test_consume_and_final (test_trie.TestTrie.test_consume_and_final) ... ok
test_containment (test_trie.TestTrie.test_containment) ... ok
test_dump_strings (test_trie.TestTrie.test_dump_strings) ... ok
test_transitions (test_trie.TestTrie.test_transitions) ... ok
test_with_meta_data (test_trie.TestTrie.test_with_meta_data) ... ok
test_mesh_terms_in_cran_corpus (test_stringfinder.TestStringFinder.test_mesh_terms_in_cran_corpus) ... ok
test_relative_insensitivity_to_dictionary_size (test_stringfinder.TestStringFinder.test_relative_insensitivity_to_dictionary_size) ... ok
test_scan_matches_and_spans (test_stringfinder.TestStringFinder.test_scan_matches_and_spans) ... ok
test_scan_matches_and_surface_forms_only (test_stringfinder.TestStringFinder.test_scan_matches_and_surface_forms_only) ... ok
test_uses_yield (test_stringfinder.TestStringFinder.test_uses_yield) ... ok
test_with_phonetic_normalizer_and_meta (test_stringfinder.TestStringFinder.test_with_phonetic_normalizer_and_meta) ... ok
test_with_unigram_tokenizer_for_finding_arbitrary_substrings (test_stringfinder.TestStringFinder.test_with_unigram_tokenizer_for_finding_arbitrary_substrings) ... ok

----------------------------------------------------------------------
Ran 20 tests in 1.271s

OK
```

```
>python3 repl.py b-1
Building suffix array from Cranfield corpus...
Enter a prefix phrase query and find matching documents.
Lookup options are {'debug': False, 'hit_count': 5}.
Returned scores are occurrence counts.
Ctrl-C to exit.
query>molecule  Con
[{'document': {'document_id': 328, 'fields': {'body': '\nthis paper considers the problem of calculating viscous aerodynamic\ncharacteristics of blunt bodies at hypersonic speeds and\nat sufficiently high alt
itudes where the appropriate mean free\npath becomes too large for the use of familiar boundary-layer\ntheory but not so large that free molecule concepts apply .\n  results of an order-of-magnitude analysis
are presented to\ndefine the regimes of rarefied gas flow and the limits of continuum\ntheory .  based on theoretical and experimental evidence,\nthe complete navier-stokes equations are used as a\nmodel, exc
ept /very close/ to the free molecule condition .  this\nmodel may not necessarily give the shock wave structure in\ndetail but satisfies overall conservation laws and should give a\nreasonably accurate pictu
re of all mean aerodynamic quantities .\n  in this /intermediate/ regime there are two fundamental classes\nof problems ..  a /viscous layer/ class and a /merged layer/\nclass, the latter corresponding to a l
arger degree of rarefaction .\nfor the viscous layer class there is a thin shock wave, but the\nshock layer region between the shock and the body is fully viscous,\nalthough the viscous stresses and conductiv
e heat transfer\nare small at the shock wave boundary .  here, the use of the\nnavier-stokes equations with outer boundary conditions given\nby the hugoniot relations is justified .  for the merged layer\ncla
ss, the shock wave is no longer thin, and the navier-stokes\nequations can be used to give a solution which includes the shock\nstructure and has free-stream conditions as outer boundary conditions\n.  a simp
ler procedure is presented for /incipient merged/\nconditions where the shock may no longer be considered an infinitesimally\nthin discontinuity but where it has not thickened\nsufficiently to entail the /ful
ly merged layer/ analysis .  in this\ncase we approximate the shock by a discontinuity obeying conservation\nlaws which include curvature effects, viscous stresses,\nand heat conduction .\n  for a sphere and
cylinder it is shown that the navier-stokes\nequations can be reduced to ordinary differential equations for\nboth the viscous and merged layer class of problems .  solutions\nof these equations, when used in
 connection with hypersonic flow\nproblems, are in general only valid in the stagnation region .  to\nillustrate the viscous layer solutions, numerical calculations\nhave been performed for a sphere and cylin
der with the assumption\nof constant density in the shock layer, which is a useful\napproximation at hypersonic speeds .  to illustrate the merged\nlayer solution, calculations have been carried out for a sph
ere\nusing the incipient merged layer approximation .\n  results are presented for detachment distance, surface shear,\nand heat-transfer rate in the stagnation region of a highly cooled\nsphere flying at hyp
ersonic speed .  with decreasing reynolds\nnumber, the shear and heat transfer are shown to increase above\nthe extrapolated boundary-layer values in the viscous layer\nregime and then to begin falling in the
 incipient merged regime .\nas the reynolds number decreases in the incipient merged\nregime, the density in the shock layer increases, and the static\nand stagnation enthalpy behind the shock decrease .\n  c
alculations performed for an insulated sphere show that, with\ndecreasing reynolds number in the incipient merged regime,\nthe density in the shock layer decreases,. the total enthalpy behind\nthe shock and a
t the stagnation point increase so that they\nare higher than the free-stream total enthalpy,. and the stagnation-point\npressure behaves like the total enthalpy .\n  for the highly cooled cylinder in the vis
cous layer regime, the\nsame quantities are presented as for the sphere .  the increase\nfound in shear and heat transfer above extrapolated boundarylayer\ntheory is small, in agreement with vorticity interac
tion\ntheory .\n  a discussion is given of the behavior of available experimental\ndata for viscous flow quantities in the intermediate regime and\nthe behavior predicted by the results of the present calcula
tions .\nqualitative agreement is indicated .\n'}},
  'score': 2},
 {'document': {'document_id': 1295, 'fields': {'body': '\nanalysis and solutions of the streamtube gas\ndynamics involving coupled chemical rate equations\nare carried out .  results are presented for airflow
s\nalong the surface of blunt bodies and through\nhypersonic nozzles .  speeds and altitudes corresponding\nto re-entry were selected to obtain initial\nconditions for the external flow calculations .  condit
ions\nappropriate to hypersonic tunnel testing\nwere chosen for the nozzle flow calculations .  composition\nhistories are shown for a kinetic mechanism\nincluding 6 species and 14 reactions .  gas-dynamic ef
fects\nof nonequilibrium processes qualitatively\nresemble those reported earlier .  however, the freezing\nprocess is complicated by the coupling of the\nnitric oxide shuffle reactions with the dissociation-
recombination\nreactions .  in many cases of hypersonic\nnozzle flows where the energy in nitrogen dissociation\nis significant, the fast shuffle reactions\nprevent nitrogen-atom freezing which would otherwis
e occur\nif three-body recombination were the only\nprocess operating .  nitric oxide concentrations\nundershoot the equilibrium values if the ratio of\nnitric oxide to oxygen molecule concentrations\nexceeds
 unity in the freezing region .  this depletion\nof nitric oxide leads to nitrogen-atom freezing .\n'}},
  'score': 1}]
Evaluation took 0.0003016999999942982 seconds.
query>of the ber
[]
Evaluation took 0.00018900000000243722 seconds.
query>^C
Bye!
```

```
>python3 repl.py b-2
Building trie from MeSH corpus...
Enter some text and locate words and phrases that are MeSH terms.
Ctrl-C to exit.
text>the ACiD raIN was bad for the skin
[{'surface': 'ACiD raIN', 'range': (4, 13), 'match': 'acid rain'},
 {'surface': 'raIN', 'range': (9, 13), 'match': 'rain'},
 {'surface': 'skin', 'range': (30, 34), 'match': 'skin'}]
Evaluation took 0.00012373899517115206 seconds.
text>hiv
[{'surface': 'hiv', 'range': (0, 3), 'match': 'hiv'}]
Evaluation took 9.199300257023424e-05 seconds.
text>the phrase adult children sounds like an oxymoron
[{'surface': 'adult', 'range': (11, 16), 'match': 'adult'},
 {'surface': 'adult children', 'range': (11, 25), 'match': 'adult children'}]
Evaluation took 0.00021737000497523695 seconds.
text>^C
Bye!
```
