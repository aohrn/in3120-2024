# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods


class Soundex:
    """
    Soundex is a phonetic algorithm for indexing names by sound, as pronounced in English.
    See, e.g., https://nlp.stanford.edu/IR-book/html/htmledition/phonetic-correction-1.html
    or https://en.wikipedia.org/wiki/Soundex for background. Multiple Soundex variants exist.
    
    The basic idea is that homophones (i.e., words that are phonetically similar) should map
    to the same code, so that they can be matched despite minor differences in spelling. Phonetic
    hashes are especially applicable to searches on proper names, e.g., the names of people.
    For example, there are often very many and equally correct ways to transliterate Russian or
    Arabic names into their Westernized counterparts.
    
    The Soundex code for a word is a simple (1-letter + 3-digit) code, designed for name pronounciation.
    Although the word to code doesn't strictly have to be a name, that's what it was designed for and
    what it works the best for. Imagine searching for a person's name in a directory of some kind.
    
    Note that there are several (also language-specific) alternative algorithms that have been
    designed also for ordinary words and that are generally considered superior to Soundex.
    See, e.g., https://en.wikipedia.org/wiki/Metaphone or https://github.com/oubiwann/metaphone.
    """

    def __init__(self):
        self._mappings = "X123X12XX22455X12623X1X2X2"  # Logically uses A-Z as the lookup index.

    def encode(self, name: str) -> str:
        """
        Computes and returns the Soundex code for the given name. The name is assumed to be a 
        single name only (e.g., "Johnson") and not a full name (e.g., "Adam Johnson").
        """
        if not name:
            raise ValueError
        encoding = [name[0].upper(), "0", "0", "0"]  # Retain the first letter of the name and pre-pad.
        j = 1
        for i in range(1, len(name)):
            codepoint = ord(name[i].upper())
            if 65 <= codepoint <= 90:  # Soundex covers A-Z only.
                mapping = self._mappings[codepoint - 65]
                if mapping != 'X':  # Encode consonants, drop vowels and vowel-like consonants.
                    if mapping != encoding[j - 1]:  # Drop repetitions.
                        encoding[j] = mapping
                        j += 1
                        if j > 3:  # Soundex caps the code length.
                            break
        return "".join(encoding)
