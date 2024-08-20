# Assignment C-2

**Deadline:** 2024-10-11

The purpose of this assignment is to extend the [`BooleanSearchEngine`](./in3120/booleansearchengine.py) class with a handful of new linguistic operators. The existing implementation already provides support for the logical operators `AND`, `OR`, and `ANDNOT`. Your task is to add support for the following new operators:

- `WILDCARD`: Support for simple wildcard matching. E.g., the query expression `WILDCARD("fi*er")` would match documents that contain any of the indexed terms {_fishmonger_, _filibuster_, _fisher_, _finder_, ...} that start with _fi_ and end with _er_. The types of wildcards supported should be the same as what you can do with a permuterm index.
- `LOOKSLIKE`: Support for simple approximate matching based on edit distance. E.g., the query expression `LOOKSLIKE("adverb")` would match documents that contain any of the indexed terms {_adverb_, _advert_, _avderb_, _advverb_, ...} that are a single edit away from the given term. Edit distance should be measured according to the Damerau-Levenshtein metric.
- `SOUNDSLIKE`: Support for simple phonetic matching. E.g., the query expression `SOUNDSLIKE("smith")` would match documents that contain any of the indexed terms {_smith_, _smyth_, _smitt_, ...} that have similar pronounciations as the given term. Phonetic similarity should be assessed using the Soundex algorithm.
- `SYNONYM`: Support for simple equivalence-classing of terms using a provided dictionary. E.g., the query expression `SYNONYM("car")` would match documents that contain any of the indexed terms {_car_, _automobile_, ...}, assuming that this mapping is contained in the provided dictionary.

Observe that all of these operators can easily be implemented by preprocessing the parsed abstract syntax tree and replacing the operator with a suitable `OR` expression prior to evaluation. For example:

    WILDCARD("fi*er")   → OR("fishmonger", "filibuster", "fisher", "finder", ...)
    LOOKSLIKE("adverb") → OR("adverb", "advert", "avderb", "advverb", ...)
    SOUNDSLIKE("smith") → OR("smith", "smyth", "smitt", ...)
    SYNONYM("car")      → OR("car", "automobile", ...)

You will not have to implement the term expansion code yourself for each operator, but can rely on supplied precode for this. You will, however, need to integrate the precode into a complete and working system, and should understand the computational processes that lie behind each operator. For the `WILDCARD` operator you can use the supplied [`WildcardExpander`](./in3120/wildcardexpander.py) class, for the `LOOKSLIKE` operator you can use the supplied [`EditSearchEngine`](./in3120/editsearchengine.py) class, for the `SOUNDSLIKE` operator you can use the supplied [`SoundexNormalizer`](./in3120/normalizer.py) class, and for the `SYNONYM` operator you can use the supplied [`Trie`](./in3120/trie.py) class to hold your equivalence-class dictionary.

For simplicity, you can assume that all the new operators are unary and that the argument they take is a single literal. For example, you will not be expected to deal with the complexities and semantics of expressions like `SOUNDEX(OR("foo", "bar"))` or `LOOKSLIKE("foo bar")`. In such cases, your code can barf but it should barf nicely and raise an exception with an understandable message that makes sense to the user.

Your solution should only contain edits to the file [`extendedbooleansearchengine.py`](./in3120/extendedbooleansearchengine.py). Changes to other files will be ignored.

Your task is to:

- Familiarize yourself with the precode.
- Implement the missing query evaluation code in the `ExtendedBooleanSearchEngine` class.
- Ensure that the code is correct and passes all tests.

Some optional bonus challenges for the interested student:

- The `ExtendedBooleanSearchEngine` class does unranked Boolean retrieval. How would you best equip it to rank the documents, when the query is a complex Boolean expression? Consider approaches like [fuzzy logic](https://en.wikipedia.org/wiki/Fuzzy_logic), for example, together with a fuzzy membership function somehow based on TFIDF statistics.
- Extend the arity of some of the new operators to take optional parameters that specify details of the expansion. For example, the `LOOKSLIKE` operator could take a second optional argument that specified the edit distance to use, or the `SOUNDSLIKE` operator could take a second optional argument that specified which phonetic algorithm to use.
- Add an operator like `STEM` that matches documents containing a stemmed version of the given term. Consider how `STEM` would work when you need to mix stemming with non-stemming (as opposed to always stemming everything or never stemming anything), and how `STEM` might interact (or not) with any of the other operators you added in this assignment.
- When the query is a complex Boolean expression and not just a bag of words in an `AND` expression, consider how you might go about adapting the logic in the [`WindowFinder`](./in3120/windowfinder.py) to produce a relevant result snippet.

Example output:

```
>cd tests
>python3 assignments.py c-2
test_malformed_queries (test_extendedbooleansearchengine.TestExtendedBooleanSearchEngine.test_malformed_queries) ... ok
test_synonym_dictionary_key_multiterm (test_extendedbooleansearchengine.TestExtendedBooleanSearchEngine.test_synonym_dictionary_key_multiterm) ... ok
test_synonym_dictionary_missing_values (test_extendedbooleansearchengine.TestExtendedBooleanSearchEngine.test_synonym_dictionary_missing_values) ... ok
test_synonym_dictionary_value_multiterm (test_extendedbooleansearchengine.TestExtendedBooleanSearchEngine.test_synonym_dictionary_value_multiterm) ... ok
test_synonym_dictionary_values_not_list (test_extendedbooleansearchengine.TestExtendedBooleanSearchEngine.test_synonym_dictionary_values_not_list) ... ok
test_valid_expressions (test_extendedbooleansearchengine.TestExtendedBooleanSearchEngine.test_valid_expressions) ... ok
test_with_normalizer_that_is_not_idempotent (test_extendedbooleansearchengine.TestExtendedBooleanSearchEngine.test_with_normalizer_that_is_not_idempotent) ... ok

----------------------------------------------------------------------
Ran 7 tests in 1.724s

OK
```

```
>python3 repl.py c-2
Building inverted index from English name corpus...
Enter an extended complex Boolean query expression and find matching documents.
Lookup options are {'optimize': True}.
Ctrl-C to exit.
query>OR(SYNONYM(aleksander), LOOKSLIKE(grost))
[{'document': {'document_id': 160, 'fields': {'body': 'Alexander Taylor'}}},
 {'document': {'document_id': 187, 'fields': {'body': 'Ethan Alexander MD'}}},
 {'document': {'document_id': 263, 'fields': {'body': 'Alexander Baker'}}},
 {'document': {'document_id': 425, 'fields': {'body': 'Andrew Alexander'}}},
 {'document': {'document_id': 1124, 'fields': {'body': 'Victoria Gross'}}},
 {'document': {'document_id': 1245, 'fields': {'body': 'Mr. Alexander Barton Jr.'}}},
 {'document': {'document_id': 1495, 'fields': {'body': 'Alexander Brown'}}},
 {'document': {'document_id': 1535, 'fields': {'body': 'Alexander Hood'}}},
 {'document': {'document_id': 1673, 'fields': {'body': 'Alexander Jackson'}}},
 {'document': {'document_id': 1904, 'fields': {'body': 'William Gross'}}},
 {'document': {'document_id': 1968, 'fields': {'body': 'Alexander Davis'}}},
 {'document': {'document_id': 2030, 'fields': {'body': 'Amanda Gross'}}},
 {'document': {'document_id': 2135, 'fields': {'body': 'Mr. Connor Alexander'}}},
 {'document': {'document_id': 2667, 'fields': {'body': 'Alexander Pratt'}}},
 {'document': {'document_id': 2883, 'fields': {'body': 'Alexander Diaz'}}},
 {'document': {'document_id': 2907, 'fields': {'body': 'Alexander Lindsey'}}},
 {'document': {'document_id': 3005, 'fields': {'body': 'Alexander Gross'}}},
 {'document': {'document_id': 3174, 'fields': {'body': 'Amber Alexander'}}},
 {'document': {'document_id': 3327, 'fields': {'body': 'Christopher Alexander'}}},
 {'document': {'document_id': 3411, 'fields': {'body': 'Alexander Wright'}}},
 {'document': {'document_id': 3603, 'fields': {'body': 'Amanda Gross'}}},
 {'document': {'document_id': 3608, 'fields': {'body': 'Alexander Adkins'}}},
 {'document': {'document_id': 3972, 'fields': {'body': 'Travis Gross'}}},
 {'document': {'document_id': 4008, 'fields': {'body': 'Alexander Mahoney'}}},
 {'document': {'document_id': 4152, 'fields': {'body': 'Alexander Harris'}}},
 {'document': {'document_id': 4161, 'fields': {'body': 'Alexander Ryan'}}},
 {'document': {'document_id': 4285, 'fields': {'body': 'Alexander Silva'}}},
 {'document': {'document_id': 4311, 'fields': {'body': 'Douglas Alexander'}}},
 {'document': {'document_id': 4364, 'fields': {'body': 'Laura Alexander'}}},
 {'document': {'document_id': 4472, 'fields': {'body': 'Katherine Gross'}}},
 {'document': {'document_id': 4476, 'fields': {'body': 'Jacob Gross'}}},
 {'document': {'document_id': 4609, 'fields': {'body': 'Alexander Thornton'}}},
 {'document': {'document_id': 4792, 'fields': {'body': 'Alexander Allen'}}}]
Evaluation took 0.007021200028248131 seconds.
query>AND(WILDCARD("gr*ss"), SOUNDSLIKE("kathrin"))
[{'document': {'document_id': 4472, 'fields': {'body': 'Katherine Gross'}}}]
Evaluation took 0.000816799933090806 seconds.
query>^C
Bye!
```
