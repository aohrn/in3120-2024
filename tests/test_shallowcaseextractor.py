# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from context import in3120


class TestShallowCaseExtractor(unittest.TestCase):

    @classmethod
    def setUp(cls) -> None:
        cls._extractor = in3120.ShallowCaseExtractor()

    def test_weird_input_buffers(self):
        self.assertListEqual(self._extractor.extract("", {}), [])
        self.assertListEqual(self._extractor.extract(None, {}), [])
        self.assertListEqual(self._extractor.extract(21, {}), [])
        self.assertListEqual(self._extractor.extract(3.14159, {}), [])

    def test_very_basic_functionality(self):
        buffer = "So The Lord of the Rings was a movie.  And Windows 2000 was an operating system."
        self.assertListEqual(self._extractor.extract(buffer, {}), ["The Lord of the Rings", "Windows 2000"])

    def test_suppression_when_too_much_is_extracted(self):
        buffer = "So This Could Be The Longest Paragraph in the whole World Where Everything Is Capitalized!"
        self.assertListEqual(self._extractor.extract(buffer, {}), [])
        self.assertListEqual(self._extractor.extract(buffer, {"coverage_threshold": 1.0}),
                             ["This Could Be The Longest Paragraph", "World Where Everything Is Capitalized"])

    def test_avoid_extracting_at_start_of_sentence(self):
        buffer = "Aa Bb. Cc Dd! Ee Ff? Gg Hh: Ii Jj"
        self.assertListEqual(self._extractor.extract(buffer, {}), ["Bb", "Dd", "Ff", "Hh", "Jj"])

    def test_avoid_extracting_at_start_of_sentence_that_opens_with_a_quote(self):
        buffer = "\"Aleksander codes Python!\", he said."
        self.assertListEqual(self._extractor.extract(buffer, {}), ["Python"])

    def test_extraction_of_non_ascii_strings(self):
        buffer = "Inconceivable, Aleksander  Øhrn is nowhere  as tall as  André the  Giant!"
        self.assertListEqual(self._extractor.extract(buffer, {}), ["Aleksander Øhrn", "André the Giant"])

    def test_extraction_of_hyphenated_strings(self):
        buffer = "Was Hewlett-Packard really started in a garage?"
        self.assertListEqual(self._extractor.extract(buffer, {}), ["Hewlett-Packard"])

    def test_extraction_of_intracapitalized_strings(self):
        buffer = "Does Leonardo DiCaprio own an iPhone?"
        self.assertListEqual(self._extractor.extract(buffer, {}), ["Leonardo DiCaprio", "iPhone"])

    def test_avoid_extracting_across_chunks(self):
        buffer = "This is the First Chunk\n  \nAnd this is Second Chunk"
        self.assertListEqual(self._extractor.extract(buffer, {}), ["First Chunk", "Second Chunk"])

    def test_avoid_extracting_known_bad_matches(self):
        buffer = "Today is April 21 and not a Monday in December. What about Apr 21, or Ruby Tuesday?"
        self.assertListEqual(self._extractor.extract(buffer, {}), ["Ruby Tuesday"])

    def test_extraction_of_strings_with_honorifics(self):
        buffer = "Is Dr. No the best James Bond movie?"
        self.assertListEqual(self._extractor.extract(buffer, {}), ["Dr. No", "James Bond"])


if __name__ == '__main__':
    unittest.main(verbosity=2)
