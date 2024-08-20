# Assignment E-1

**Deadline:** 2024-11-08

The purpose of this assignment is to write a simple classifier that, using the multinomial naïve Bayes classification rule, can automatically detect which language a given input buffer is written in. We will train the classifier on a small corpus of Norwegian, Danish, English and German documents. Use add-one smoothing as described in the textbook when computing the probability estimates.

Your solution should only contain edits to the file [`naivebayesclassifier.py`](./in3120/naivebayesclassifier.py). Changes to other files will be ignored.

Implementation notes:

- The `NaiveBayesClassifier` class implements a simple multinomial naïve Bayes text classifier. It can be trained to classify text into any set of categories, but we will use it for language identification. I.e., the set of possible output categories is {_no_, _da_, _en_, _de_}.
- For text normalization and tokenization purposes, you can use the `SimpleNormalizer` and `SimpleTokenizer` classes.
- To debug your implementation and ensure that you get the probability estimates right, take a look at [Example 13.1 in the textbook](https://nlp.stanford.edu/IR-book/pdf/13bayes.pdf). One of the unit tests covers this example specifically.
- There are several plausible approaches for handling out-of-vocabulary terms, i.e., terms that are part of the buffer to classify but that you never saw in the training set. For the purposes of this assignment, you can simply ignore such terms.

Your task is to:

- Familiarize yourself with the precode.
- Implement the missing code in the `NaiveBayesClassifier` class.
- Ensure that the code is correct and passes all tests.

Some optional bonus challenges for the interested student:

- Using the `SimpleNormalizer` and `SimpleTokenizer` classes is kind of backwards and is a simplification when doing language identification. Because normalization and especially tokenization is generally language-specific (e.g., a tokenizer for Japanese is very different from a tokenizer for English) and we are trying to infer the language of the text, our implementation would fall short if we had added, e.g., Japanese as a possible output category. Modify your implementation to use the language-agnostic `ShingleGenerator` class instead, and extend your training set with more languages. Does this make a difference?
- Find some other training data, e.g., try learning how to classify text into different topics such as {_sports_, _politics_, _finance_, ...} or sentiment classes such as {_positive_, _neutral_, _negative_}. For inspiration see, e.g., [here](https://metatext.io/datasets-list/text-classification-task) or [here](https://datasetsearch.research.google.com/) or search the web.
- Select some other text classification algorithms and implement these. For inspiration see, e.g., [here](https://scikit-learn.org/stable/supervised_learning.html) or search the web.
- The assignment addresses multinomial naïve Bayes classification, which works well for text and discrete-valued features and is based on simple counting. But naïve Bayes can be used for real-valued features, too, for example by assuming that a real-valued feature's values for a given category follow a [Gaussian distribution](https://en.wikipedia.org/wiki/Normal_distribution), and then estimating the mean and the standard deviation from the training set. With that in hand, instead of using lookup tables as in the multinomial naïve Bayes classification, we can use the estimated Gaussian to produce our conditional probabilities. Real-valued features can occur in text classification, too, e.g., consider the usage of TF-IDF scores or [cosine similarities in some embedding space](./assignment-e-2.md). Extend your implementation to handle real-valued features.

Example output:

```
>cd tests
>python3 assignments.py e
test_china_example_from_textbook (tests.TestNaiveBayesClassifier) ... ok
test_language_detection_trained_on_some_news_corpora (tests.TestNaiveBayesClassifier) ... ok

----------------------------------------------------------------------
Ran 2 tests in 3.281s

OK
```

```
>python3 repl.py e-1
Initializing naive Bayes classifier from news corpora...
Enter some text and classify it into ['en', 'no', 'da', 'de'].
Returned scores are log-probabilities.
Ctrl-C to exit.
text>norsk er nærmere dansk enn tysk
[{'category': 'no', 'score': -50.90542217389785},
 {'category': 'da', 'score': -57.70586771883279},
 {'category': 'de', 'score': -69.80849082418189},
 {'category': 'en', 'score': -76.06463449054945}]
Evaluation took 0.00020830000000060522 seconds.
text>the bicycle was built for two persons
[{'category': 'en', 'score': -54.30172379503675},
 {'category': 'da', 'score': -75.13534392006915},
 {'category': 'no', 'score': -77.17518464340273},
 {'category': 'de', 'score': -77.69365558296839}]
Evaluation took 0.00021139999999775227 seconds.
text>^C
Bye!
```
