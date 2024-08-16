# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
# pylint: disable=broad-exception-caught

import json
import os
import pprint
import sys
from timeit import default_timer as timer
from typing import Callable, Any
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote
from context import in3120


# The colorama module is not part of the Python standard library.
# For self-containment reasons, make it optional and have output
# colorization reduce to a NOP if it's not installed.
try:
    from colorama import Fore, Style
except ImportError:
    print("Colorization disabled, 'pip install colorama' to enable.")
    class Fore:
        GREEN = ""
        RED = ""
        LIGHTYELLOW_EX = ""
        LIGHTBLUE_EX = ""
    class Style:
        RESET_ALL = ""


# Define a small helper so that we get a full absolute path to the named file.
def data_path(filename: str) -> str:
    here = os.path.dirname(__file__)
    data = os.path.join(here, "..", "data")
    full = os.path.abspath(os.path.join(data, filename))
    return full


# Define a simple REPL to query from the terminal.
def simple_repl(prompt: str, evaluator: Callable[[str], Any]):
    printer = pprint.PrettyPrinter()
    print(f"{Fore.LIGHTYELLOW_EX}Ctrl-C to exit.{Style.RESET_ALL}")
    try:
        while True:
            print(f"{Fore.GREEN}{prompt}>{Fore.RED}", end="")
            query = input()
            try:
                start = timer()
                matches = evaluator(query)
                end = timer()
                print(Fore.LIGHTBLUE_EX, end="")
                printer.pprint(matches)
                print(f"{Fore.LIGHTYELLOW_EX}Evaluation took {end - start} seconds.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}{e.__class__.__name__}: {e}{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"{Fore.LIGHTYELLOW_EX}\nBye!{Style.RESET_ALL}")


# Define a small REPL to query from localhost:8000 on a per keypress basis.
# Coordinated with index.html.
def simple_ajax(evaluator: Callable[[str], Any]):
    class MyEncoder(json.JSONEncoder):
        """
        Custom JSON encoder, so that we can serialize custom IN3120 objects.
        """
        def default(self, o):
            if hasattr(o, 'to_dict') and callable(getattr(o, 'to_dict')):
                return o.to_dict()
            return json.JSONEncoder.default(self, o)
    class MyHandler(SimpleHTTPRequestHandler):
        """
        Custom HTTP handler. Supports GET only, suppresses all log messages.
        """
        def do_GET(self):
            if self.path.startswith("/query"):
                query = unquote(self.path.split('=')[1])
                start = timer()
                matches = evaluator(query)
                end = timer()
                results = {"duration": end - start, "matches": matches}
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(results, cls=MyEncoder).encode())
            else:
                super().do_GET()
        def log_message(self, format, *args):
            pass
    port = 8000
    with ThreadingHTTPServer(("", port), MyHandler) as httpd:
        print(f"{Fore.GREEN}Server running on localhost:{port}, open your browser.{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}Ctrl-C to exit.{Style.RESET_ALL}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"{Fore.LIGHTYELLOW_EX}Bye!{Style.RESET_ALL}")
            httpd.server_close()


def repl_a_1():
    print("Building inverted index from Cranfield corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("cran.xml"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    print("Enter one or more index terms and inspect their posting lists.")
    simple_repl("terms", lambda ts: {t: list(index.get_postings_iterator(t)) for t in index.get_terms(ts)})


def repl_a_2():
    print("Building inverted index from English name corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("names.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    engine = in3120.BooleanSearchEngine(corpus, index)
    options = {"optimize": True}
    print("Enter a complex Boolean query expression and find matching documents.")
    print(f"Lookup options are {options}.")
    simple_repl("query", lambda e: list(engine.evaluate(e, options)))


def repl_b_1():
    print("Building suffix array from Cranfield corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("cran.xml"))
    engine = in3120.SuffixArray(corpus, ["body"], normalizer, tokenizer)
    options = {"debug": False, "hit_count": 5}
    print("Enter a prefix phrase query and find matching documents.")
    print(f"Lookup options are {options}.")
    print("Returned scores are occurrence counts.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options)))


def repl_b_2():
    print("Building trie from MeSH corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("mesh.txt"))
    dictionary = in3120.Trie()
    dictionary.add((d["body"] for d in corpus), normalizer, tokenizer)
    engine = in3120.StringFinder(dictionary, normalizer, tokenizer)
    print("Enter some text and locate words and phrases that are MeSH terms.")
    simple_repl("text", lambda t: list(engine.scan(t)))


def repl_b_3():
    print("Building suffix array from airport corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    pipeline = in3120.DocumentPipeline([lambda d: d if d.get_field("type", "") != "closed" else None])
    corpus = in3120.InMemoryCorpus(data_path("airports.csv"), pipeline)
    engine = in3120.SuffixArray(corpus, ["id", "type", "name", "iata_code"], normalizer, tokenizer)
    options = {"debug": False, "hit_count": 5}
    print("Enter a prefix phrase query and find matching (non-closed) airports.")
    print(f"Lookup options are {options}.")
    print("Returned scores are occurrence counts.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options)))


def repl_b_4():
    print("Building suffix array from Pantheon corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("pantheon.tsv"))
    engine = in3120.SuffixArray(corpus, ["name"], normalizer, tokenizer)
    options = {"debug": False, "hit_count": 5}
    print("Enter a prefix phrase query and find matching people.")
    print(f"Lookup options are {options}.")
    print("Returned scores are occurrence counts.")
    simple_ajax(lambda q: list(engine.evaluate(q, options)))


def repl_b_5():
    print("Building trie from MeSH corpus...")
    normalizer = in3120.DummyNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("mesh.txt"))
    dictionary = in3120.Trie()
    dictionary.add((d["body"] for d in corpus), normalizer, tokenizer)
    dictionary.add2([("shibboleth", "https://en.wikipedia.org/wiki/Shibboleth")], normalizer, tokenizer)
    engine = in3120.EditSearchEngine(dictionary, normalizer, tokenizer)
    options = {"hit_count": 5, "upper_bound": 2, "first_n": 0, "scoring": "normalized"}
    print("Enter a query and find MeSH terms that are approximate matches.")
    print(f"Lookup options are {options}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options)))


def repl_c_1():
    print("Indexing English news corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.SimpleRanker()
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_c_2():
    print("Building inverted index from English name corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("names.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    equivalences = ["aleksander", "alexander"]
    synonyms = in3120.Trie.from_strings2(((s, equivalences) for s in equivalences), normalizer, tokenizer)
    engine = in3120.ExtendedBooleanSearchEngine(corpus, index, synonyms)
    options = {"optimize": True}
    print("Enter an extended complex Boolean query expression and find matching documents.")
    print(f"Lookup options are {options}.")
    simple_repl("query", lambda e: list(engine.evaluate(e, options)))


def repl_d_1():
    print("Indexing MeSH corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.ShingleGenerator(3)
    corpus = in3120.InMemoryCorpus(data_path("mesh.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.SimpleRanker()
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Normalizer is {normalizer.__class__.__name__}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_2():
    print("Indexing English news corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.BetterRanker(corpus, index)
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Normalizer is {normalizer.__class__.__name__}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_3():
    print("Indexing English news corpus...")
    normalizer = in3120.PorterNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.BetterRanker(corpus, index)
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    print(f"Normalizer is {normalizer.__class__.__name__}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_4():
    print("Indexing randomly generated English names...")
    normalizer = in3120.SoundexNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("names.txt"))
    index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    ranker = in3120.BetterRanker(corpus, index)
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.2}
    print("Enter a name and find phonetically similar names.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_d_5():
    print("Indexing the set of airports in the world...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("airports.csv"))
    index = in3120.InMemoryInvertedIndex(corpus, ["id", "type", "name", "iata_code"], normalizer, tokenizer)
    ranker = in3120.BetterRanker(corpus, index)
    engine = in3120.SimpleSearchEngine(corpus, index)
    options = {"debug": False, "hit_count": 5, "match_threshold": 0.5}
    print("Enter a query and find matching airports.")
    print(f"Lookup options are {options}.")
    print(f"Normalizer is {normalizer.__class__.__name__}.")
    print(f"Tokenizer is {tokenizer.__class__.__name__}.")
    print(f"Ranker is {ranker.__class__.__name__}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options, ranker)))


def repl_e_1():
    print("Initializing naive Bayes classifier from news corpora...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    languages = ["en", "no", "da", "de"]
    training_set = {language: in3120.InMemoryCorpus(data_path(f"{language}.txt")) for language in languages}
    classifier = in3120.NaiveBayesClassifier(training_set, ["body"], normalizer, tokenizer)
    print(f"Enter some text and classify it into {languages}.")
    print("Returned scores are log-probabilities.")
    simple_repl("text", lambda t: list(classifier.classify(t)))


def repl_e_2():
    print("Indexing English news corpus using an ANN index...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    engine = in3120.SimilaritySearchEngine(corpus, ["body"], normalizer, tokenizer)
    options = {"hit_count": 5}
    print("Enter a query and find matching documents.")
    print(f"Lookup options are {options}.")
    simple_repl("query", lambda q: list(engine.evaluate(q, options)))


def repl_e_3():
    print("Initializing k-NN classifier from movie corpus built over an ANN index...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    movies = in3120.InMemoryCorpus(data_path("imdb.csv"))
    fields = ["title", "description"]
    training_set = movies.split("genre", lambda v: v.split(","))
    classifier = in3120.NearestNeighborClassifier(training_set, fields, normalizer, tokenizer)
    options = {"k": 3, "voting": "weighted"}
    print("Enter some text and have it classified as a movie genre.")
    print(f"Classification options are {options}.")
    simple_repl("text", lambda t: list(classifier.classify(t, options)))


def repl_x_1():
    normalizer = in3120.SimpleNormalizer()
    extractor = in3120.ShallowCaseExtractor()
    options = {}
    print("Enter some text and see what gets extracted based on simple case heuristics.")
    simple_repl("text", lambda t: list(extractor.extract(normalizer.canonicalize(t), options)))


def repl_x_2():
    normalizer = in3120.SoundexNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    print("Enter some text and see the Soundex codes.")
    simple_repl("text", lambda t: [normalizer.normalize(token) for token in tokenizer.strings(normalizer.canonicalize(t))])


def repl_x_3():
    normalizer = in3120.PorterNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    print("Enter some text and see the stemmed terms.")
    simple_repl("text", lambda t: [normalizer.normalize(token) for token in tokenizer.strings(normalizer.canonicalize(t))])


def repl_x_4():
    print("Building permuterm index from MeSH corpus...")
    corpus = in3120.InMemoryCorpus(data_path("mesh.txt"))
    expander = in3120.WildcardExpander((d["body"] for d in corpus))
    print("Enter a wildcard query and locate matching MeSH terms.")
    simple_repl("text", lambda t: list(expander.expand(t)))


def repl_x_5():
    print("Indexing English news corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    corpus = in3120.InMemoryCorpus(data_path("en.txt"))
    inverted_index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    stopwords = in3120.Trie.from_strings((d["body"] for d in in3120.InMemoryCorpus(data_path("stopwords-en.txt"))), normalizer, tokenizer)
    vectorizer = in3120.Vectorizer(corpus, inverted_index, stopwords)
    print(f"Enter a document identifier between 0 and {corpus.size()} to inspect its document vector.")
    simple_repl(f"[0, {corpus.size() - 1}]]", lambda i: {"document": corpus[int(i)], "vector": vectorizer.from_document(corpus[int(i)], ["body"]).top(100)})


def repl_x_6():
    print("Initializing Rocchio classifier from movie corpus...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    movies = in3120.InMemoryCorpus(data_path("imdb.csv"))
    fields = ["title", "description"]
    inverted_index = in3120.DummyInMemoryInvertedIndex(movies, fields, normalizer, tokenizer)
    training_set = movies.split("genre", lambda v: v.split(","))
    stopwords = in3120.Trie.from_strings((d["body"] for d in in3120.InMemoryCorpus(data_path("stopwords-en.txt"))), normalizer, tokenizer)
    vectorizer = in3120.Vectorizer(movies, inverted_index, stopwords)
    classifier = in3120.RocchioClassifier(training_set, fields, vectorizer)
    print("Enter some text and have it classified as a movie genre.")
    simple_repl("text", lambda t: list(classifier.classify(t)))


def repl_x_7():
    print("Initializing Rocchio classifier from news corpora...")
    normalizer = in3120.SimpleNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    languages = ["en", "no", "da", "de"]
    filenames = [data_path(f"{language}.txt") for language in languages]
    annotations = [{"lang": language} for language in languages]
    corpus = in3120.InMemoryCorpus(filenames, annotations)
    inverted_index = in3120.DummyInMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer)
    training_set = corpus.split("lang")
    stopwords = in3120.Trie.from_strings((d["body"] for d in in3120.InMemoryCorpus(data_path("stopwords-en.txt"))), normalizer, tokenizer)
    vectorizer = in3120.Vectorizer(corpus, inverted_index, stopwords)
    classifier = in3120.RocchioClassifier(training_set, ["body"], vectorizer)
    print(f"Enter some text and classify it into {languages}.")
    print("Returned scores are cosine similarities.")
    simple_repl("text", lambda t: list(classifier.classify(t)))


def repl_x_8():
    print("Loading Frankenstein...")
    normalizer = in3120.PorterNormalizer()
    tokenizer = in3120.SimpleTokenizer()
    finder = in3120.WindowFinder(normalizer, tokenizer)
    with open(data_path("frankenstein.txt"), "r", encoding="utf-8") as f:
        frankenstein = normalizer.canonicalize(f.read())
    print("Enter some query terms and locate a plausible result snippet.")
    def generate_snippet(query: str) -> str:
        query = normalizer.canonicalize(query)
        result = finder.scan(frankenstein, query)
        if result is None:
            return "Unable to produce a snippet."
        w, b, e = result
        if w > 75:
            return f"Suppressing snippet, window width is {w}."
        padding = 20
        before = frankenstein[max(0, b - padding):b]
        snippet = frankenstein[b:e]
        after = frankenstein[e:min(len(frankenstein), e + padding)]
        return f"[...{before}]{snippet}[{after}...]"
    simple_repl("query", generate_snippet)


def main():
    repls = {
        "a-1": repl_a_1,  # A.
        "a-2": repl_a_2,  # A.
        "b-1": repl_b_1,  # B-1.
        "b-2": repl_b_2,  # B-1.
        "b-3": repl_b_3,  # B-1.
        "b-4": repl_b_4,  # B-1.
        "b-5": repl_b_5,  # B-2.
        "c-1": repl_c_1,  # C-1.
        "c-2": repl_c_2,  # C-2.
        "d-1": repl_d_1,  # D-1.
        "d-2": repl_d_2,  # D-1.
        "d-3": repl_d_3,  # D-1.
        "d-4": repl_d_4,  # D-1.
        "d-5": repl_d_5,  # D-1.
        "e-1": repl_e_1,  # E-1.
        "e-2": repl_e_2,  # E-2.
        "e-3": repl_e_3,  # E-2.
        "x-1": repl_x_1,
        "x-2": repl_x_2,
        "x-3": repl_x_3,
        "x-4": repl_x_4,
        "x-5": repl_x_5,
        "x-6": repl_x_6,
        "x-7": repl_x_7,
        "x-8": repl_x_8,
    }  # The first letter of each key aligns with an obligatory assignment.
    targets = sys.argv[1:]
    if not targets:
        print(f"{sys.argv[0]} [{'|'.join(repls.keys())}]")
    else:
        for target in targets:
            if target in repls:
                repls[target.lower()]()


if __name__ == "__main__":
    main()
