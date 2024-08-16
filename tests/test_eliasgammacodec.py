# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from context import in3120


class TestEliasGammaCodec(unittest.TestCase):

    def setUp(self):
        # Table 5.5 in the textbook.
        self._pairs = {
            1:    '0',
            2:    '100',
            3:    '101',
            4:    '11000',
            9:    '1110001',
            13:   '1110101',
            24:   '111101000',
            511:  '11111111011111111',
            1025: '111111111100000000001',
        }

    def test_encode(self):
        for decoded, encoded in self._pairs.items():
            self.assertEqual(encoded, in3120.EliasGammaCodec.encode(decoded))

    def test_decode(self):
        for decoded, encoded in self._pairs.items():
            self.assertEqual(decoded, in3120.EliasGammaCodec.decode(encoded))

    def test_roundtrip(self):
        for i in range(1, 3000):
            self.assertEqual(i, in3120.EliasGammaCodec.decode(in3120.EliasGammaCodec.encode(i)))

    def test_non_positive_numbers(self):
        for i in range(0, 2):
            with self.assertRaises(AssertionError):
                in3120.EliasGammaCodec.encode(-i)

    def test_missing_buffer(self):
        for bits in ['', None]:
            with self.assertRaises(AssertionError):
                in3120.EliasGammaCodec.decode(bits)

    def test_malformed_buffer(self):
        for bits in ['aleksander']:
            with self.assertRaises(ValueError):
                in3120.EliasGammaCodec.decode(bits)


if __name__ == '__main__':
    unittest.main(verbosity=2)
