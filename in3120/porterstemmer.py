# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods


class PorterStemmer:
    """
    Implements Porter's stemming algorithm for English. The algorithm is a heuristic process for
    removing common morphological and inflexional endings from words in English. Its main use is
    as part of a term normalization process that is usually done when setting up information retrieval
    systems. See, e.g., https://nlp.stanford.edu/IR-book/html/htmledition/stemming-and-lemmatization-1.html
    or https://tartarus.org/martin/PorterStemmer/ for background and details.

    Several Python implementations of Porter's algorithm are available online, e.g., as part of NLTK. See,
    e.g., https://tedboy.github.io/nlps/_modules/nltk/stem/porter.html. Adapted and replicated here to make
    things self-contained.

    See also https://snowballstem.org/ for a selection of stemming algorithms, including Porter's
    algorithm, and for other languages than English, including Norwegian. These stemming algorithms are
    expressed in a small domain-specific language called Snowball, that can be compiled into source code
    in many different programming languages, including Python.
    """

    def __init__(self):
        # A table of irregular forms, to be handled as exceptions. It is quite short,
        # but still reflects the errors actually drawn to Martin Porter's attention over
        # a 20 year period.
        self._exceptions = {
            "sky": "sky",
            "skies": "sky",
            "dying": "die",
            "lying": "lie",
            "tying": "tie",
            "news": "news",
            "inning": "inning",
            "innings": "inning",
            "outing": "outing",
            "outings": "outing",
            "canning": "canning",
            "cannings": "canning",
            "howe": "howe",
            "proceed": "proceed",
            "exceed": "exceed",
            "succeed": "succeed",
        }

        # Frequently consulted.
        self._vowels = frozenset(['a', 'e', 'i', 'o', 'u'])

    def _cons(self, word: str, i: int) -> bool:
        """
        Returns True iff word[i] is a consonant or behaves like one.
        """
        if word[i] in self._vowels:
            return False
        if word[i] == 'y':
            return True if (i == 0) else (not self._cons(word, i - 1))
        return True

    def _m(self, word: str, j: int) -> int:
        """
        Measures the number of consonant sequences in the word up until the given index.
        If c is a consonant sequence and v a vowel sequence, and <..> indicates arbitrary
        presence, then:

            <c><v>         -> 0
            <c>vc<v>       -> 1
            <c>vcvc<v>     -> 2
            <c>vcvcvc<v>   -> 3
            <c>vcvcvcvc<v> -> 4
        """
        n = 0
        i = 0
        while True:
            if i > j:
                return n
            if not self._cons(word, i):
                break
            i = i + 1
        i = i + 1
        while True:
            while True:
                if i > j:
                    return n
                if self._cons(word, i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while True:
                if i > j:
                    return n
                if not self._cons(word, i):
                    break
                i = i + 1
            i = i + 1

    def _vowelinstem(self, stem: str) -> bool:
        """
        Returns True iff the given stem contains a vowel.
        """
        for i in range(len(stem)):
            if not self._cons(stem, i):
                return True
        return False

    def _doublec(self, word: str) -> bool:
        """
        Returns True iff the given word ends with a double consonant.
        """
        if len(word) < 2:
            return False
        if word[-1] != word[-2]:
            return False
        return self._cons(word, len(word) - 1)

    def _cvc(self, word: str, i: int) -> bool:
        """
        Returns True iff either:

        (a) We have (i == 1) and word[0:2] is a v-c pair.
            Departure from published algorithm.

        (b) We have that word[(i - 2):(i + 1)] is a c-v-c triple,
            and also if the second c is not 'w', 'x', or 'y'. This
            is used when trying to restore an 'e' at the end of a short
            word. E.g., "cav(e)", "lov(e)", "hop(e)", "crim(e)", but
            "snow", "box", "tray".
        """
        if i == 0:
            return False
        if i == 1:
            return (not self._cons(word, 0) and self._cons(word, 1))
        if not self._cons(word, i) or self._cons(word, i - 1) or not self._cons(word, i - 2):
            return False
        if word[i] in ('w', 'x', 'y'):
            return False
        return True

    def _step1ab(self, word: str) -> str:
        """
        Gets rid of plurals and trims "-ed" or "-ing". For example:

            caresses  ->  caress
            ponies    ->  poni
            sties     ->  sti
            tie       ->  tie
            caress    ->  caress
            cats      ->  cat

            feed      ->  feed
            agreed    ->  agree
            disabled  ->  disable

            matting   ->  mat
            mating    ->  mate
            meeting   ->  meet
            milling   ->  mill
            messing   ->  mess

            meetings  ->  meet
        """
        # Plurals.
        if word[-1] == 's':
            if word.endswith("sses"):
                word = word[:-2]
            elif word.endswith("ies"):
                if len(word) == 4:  # Departure from published algorithm.
                    word = word[:-1]
                else:
                    word = word[:-2]
            elif word[-2] != 's':
                word = word[:-1]

        # Did we trim "-ed" or "-ing"? Requires fix-up.
        ed_or_ing_trimmed = False

        # Trimming.
        if word.endswith("ied"):
            if len(word) == 4:  # Departure from published algorithm.
                word = word[:-1]
            else:
                word = word[:-2]
        elif word.endswith("eed"):
            if self._m(word, len(word) - 4) > 0:
                word = word[:-1]
        elif word.endswith("ed") and self._vowelinstem(word[:-2]):
            word = word[:-2]
            ed_or_ing_trimmed = True
        elif word.endswith("ing") and self._vowelinstem(word[:-3]):
            word = word[:-3]
            ed_or_ing_trimmed = True

        # Trimming fix-up?
        if ed_or_ing_trimmed:
            if word.endswith("at") or word.endswith("bl") or word.endswith("iz"):
                word += 'e'
            elif self._doublec(word):
                if word[-1] not in ('l', 's', 'z'):
                    word = word[:-1]
            elif (self._m(word, len(word)-1) == 1 and self._cvc(word, len(word) - 1)):
                word += 'e'

        return word

    def _step1c(self, word: str) -> str:
        """
        Turns terminal 'y' to 'i' when there is another vowel in the stem.

        Departs from the published algorithm in that 'y' -> 'i' is only done
        when 'y' is preceded by a consonant, but not if the stem
        is only a single consonant. So "happy" -> "happi" but "enjoy" -> "enjoy".
        Formerly "enjoy" -> "enjoi" and "enjoyment" -> "enjoy". This step is
        arguably done too soon, but with this modification that no longer really
        matters.

        Also, the removal of the vowel-in-stem condition means that {"spy", "fly"
        "try", ...} stem to {"spi", "fli", "tri", ...} and conflate with {"spied",
        "tried", "flies", ...}.
        """
        if word[-1] == 'y' and len(word) > 2 and self._cons(word, len(word) - 2):
            return word[:-1] + 'i'
        else:
            return word

    def _step2(self, word: str) -> str:
        """
        Maps double suffixes to single ones. E.g., so that "-ization" ("-ize" plus "-ation")
        maps to "-ize". Note that the string before the suffix must give m() > 0.
        """
        # Could happen with unusual inputs, e.g., "oed".
        if len(word) <= 1:
            return word

        # Dispatch on penultimate letter.
        c = word[-2]

        # Collapse?
        if c == 'a':
            if word.endswith("ational"):
                return word[:-7] + "ate" if self._m(word, len(word) - 8) > 0 else word
            elif word.endswith("tional"):
                return word[:-2] if self._m(word, len(word) - 7) > 0 else word
            else:
                return word
        elif c == 'c':
            if word.endswith("enci"):
                return word[:-4] + "ence" if self._m(word, len(word) - 5) > 0 else word
            elif word.endswith("anci"):
                return word[:-4] + "ance" if self._m(word, len(word) - 5) > 0 else word
            else:
                return word
        elif c == 'e':
            if word.endswith("izer"):
                return word[:-1] if self._m(word, len(word) - 5) > 0 else word
            else:
                return word
        elif c == 'l':
            if word.endswith("bli"):
                return word[:-3] + "ble" if self._m(word, len(word) - 4) > 0 else word  # Departure from published algorithm.
            elif word.endswith("alli"):
                if self._m(word, len(word) - 5) > 0:  # Departure from published algorithm.
                    word = word[:-2]
                    return self._step2(word)
                else:
                    return word
            elif word.endswith("fulli"):
                return word[:-2] if self._m(word, len(word) - 6) else word  # Departure from published algorithm.
            elif word.endswith("entli"):
                return word[:-2] if self._m(word, len(word) - 6) else word
            elif word.endswith("eli"):
                return word[:-2] if self._m(word, len(word) - 4) else word
            elif word.endswith("ousli"):
                return word[:-2] if self._m(word, len(word) - 6) else word
            else:
                return word
        elif c == 'o':
            if word.endswith("ization"):
                return word[:-7] + "ize" if self._m(word, len(word) - 8) else word
            elif word.endswith("ation"):
                return word[:-5] + "ate" if self._m(word, len(word) - 6) else word
            elif word.endswith("ator"):
                return word[:-4] + "ate" if self._m(word, len(word) - 5) else word
            else:
                return word
        elif c == 's':
            if word.endswith("alism"):
                return word[:-3] if self._m(word, len(word) - 6) else word
            elif word.endswith("ness"):
                if word.endswith("iveness"):
                    return word[:-4] if self._m(word, len(word) - 8) else word
                elif word.endswith("fulness"):
                    return word[:-4] if self._m(word, len(word) - 8) else word
                elif word.endswith("ousness"):
                    return word[:-4] if self._m(word, len(word) - 8) else word
                else:
                    return word
            else:
                return word
        elif c == 't':
            if word.endswith("aliti"):
                return word[:-3] if self._m(word, len(word) - 6) else word
            elif word.endswith("iviti"):
                return word[:-5] + "ive" if self._m(word, len(word) - 6) else word
            elif word.endswith("biliti"):
                return word[:-6] + "ble" if self._m(word, len(word) - 7) else word
            else:
                return word
        elif c == 'g':  # Departure from published algorithm.
            if word.endswith("logi"):
                return word[:-1] if self._m(word, len(word) - 4) else word
            else:
                return word
        else:
            return word

    def _step3(self, word: str) -> str:
        """
        Deals with "-ic-", "-full", "-ness", and more. Similar strategy to previous step.
        """
        # Dispatch on last letter.
        c = word[-1]

        # Trim?
        if c == 'e':
            if word.endswith("icate"):
                return word[:-3] if self._m(word, len(word) - 6) else word
            elif word.endswith("ative"):
                return word[:-5] if self._m(word, len(word) - 6) else word
            elif word.endswith("alize"):
                return word[:-3] if self._m(word, len(word) - 6) else word
            else:
                return word
        elif c == 'i':
            if word.endswith("iciti"):
                return word[:-3] if self._m(word, len(word) - 6) else word
            else:
                return word
        elif c == 'l':
            if word.endswith("ical"):
                return word[:-2] if self._m(word, len(word) - 5) else word
            elif word.endswith("ful"):
                return word[:-3] if self._m(word, len(word) - 4) else word
            else:
                return word
        elif c == 's':
            if word.endswith("ness"):
                return word[:-4] if self._m(word, len(word) - 5) else word
            else:
                return word
        else:
            return word

    def _step4(self, word: str) -> str:
        """
        Trims "-ant", "-ence", and more, in context <c>vcvc<v>.
        """
        # Could happen with unusual inputs, e.g., "oed".
        if len(word) <= 1:
            return word

        # Dispatch on penultimate letter.
        c = word[-2]

        # Trim?
        if c == 'a':
            if word.endswith("al"):
                return word[:-2] if self._m(word, len(word) - 3) > 1 else word
            else:
                return word
        elif c == 'c':
            if word.endswith("ance"):
                return word[:-4] if self._m(word, len(word) - 5) > 1 else word
            elif word.endswith("ence"):
                return word[:-4] if self._m(word, len(word) - 5) > 1 else word
            else:
                return word
        elif c == 'e':
            if word.endswith("er"):
                return word[:-2] if self._m(word, len(word) - 3) > 1 else word
            else:
                return word
        elif c == 'i':
            if word.endswith("ic"):
                return word[:-2] if self._m(word, len(word) - 3) > 1 else word
            else:
                return word
        elif c == 'l':
            if word.endswith("able"):
                return word[:-4] if self._m(word, len(word) - 5) > 1 else word
            elif word.endswith("ible"):
                return word[:-4] if self._m(word, len(word) - 5) > 1 else word
            else:
                return word
        elif c == 'n':
            if word.endswith("ant"):
                return word[:-3] if self._m(word, len(word) - 4) > 1 else word
            elif word.endswith("ement"):
                return word[:-5] if self._m(word, len(word) - 6) > 1 else word
            elif word.endswith("ment"):
                return word[:-4] if self._m(word, len(word) - 5) > 1 else word
            elif word.endswith("ent"):
                return word[:-3] if self._m(word, len(word) - 4) > 1 else word
            else:
                return word
        elif c == 'o':
            if word.endswith("sion") or word.endswith("tion"):  # Slightly different logic to all the other cases.
                return word[:-3] if self._m(word, len(word) - 4) > 1 else word
            elif word.endswith("ou"):
                return word[:-2] if self._m(word, len(word) - 3) > 1 else word
            else:
                return word
        elif c == 's':
            if word.endswith("ism"):
                return word[:-3] if self._m(word, len(word) - 4) > 1 else word
            else:
                return word
        elif c == 't':
            if word.endswith("ate"):
                return word[:-3] if self._m(word, len(word) - 4) > 1 else word
            elif word.endswith("iti"):
                return word[:-3] if self._m(word, len(word) - 4) > 1 else word
            else:
                return word
        elif c == 'u':
            if word.endswith("ous"):
                return word[:-3] if self._m(word, len(word) - 4) > 1 else word
            else:
                return word
        elif c == 'v':
            if word.endswith("ive"):
                return word[:-3] if self._m(word, len(word) - 4) > 1 else word
            else:
                return word
        elif c == 'z':
            if word.endswith("ize"):
                return word[:-3] if self._m(word, len(word) - 4) > 1 else word
            else:
                return word
        else:
            return word

    def _step5(self, word: str) -> str:
        """
        Removes a final "-e" if m() > 1, and changes "-ll" to "-l" if m() > 1.
        """
        if word[-1] == 'e':
            a = self._m(word, len(word) - 1)
            if a > 1 or (a == 1 and not self._cvc(word, len(word) - 2)):
                word = word[:-1]
        if word.endswith("ll") and self._m(word, len(word) - 1) > 1:
            word = word[:-1]

        return word

    def stem(self, word: str) -> str:
        """
        Computes and returns the stem of the given word, per Porter's heuristics
        for English. The input is assumed to be a single word (e.g., "automatic")
        and not a full text buffer (e.g., "an automatic differentiation engine".)

        The output is lowercased. The input can be lowercased, uppercased, or in
        mixed case.
        """
        # Stemmable input?
        word = str(word or "").strip().lower()
        if not word:
            raise ValueError

        # Departure from published algorithm.
        if word in self._exceptions:
            return self._exceptions[word]

        # Departure from published algorithm.
        if len(word) <= 2:
            return word

        # Apply rules!
        word = self._step1ab(word)
        word = self._step1c(word)
        word = self._step2(word)
        word = self._step3(word)
        word = self._step4(word)
        word = self._step5(word)

        return word
