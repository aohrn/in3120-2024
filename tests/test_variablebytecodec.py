# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

import unittest
from context import in3120


class TestVariableByteCodec(unittest.TestCase):

    def test_encode_and_decode(self):
        data = bytearray()
        self.assertEqual(in3120.VariableByteCodec.encode(21, data), 1)
        self.assertEqual(in3120.VariableByteCodec.encode(4, data), 1)
        self.assertEqual(in3120.VariableByteCodec.encode(70, data), 1)
        self.assertEqual(in3120.VariableByteCodec.encode(0, data), 1)
        self.assertEqual(in3120.VariableByteCodec.encode(127, data), 1)
        self.assertEqual(in3120.VariableByteCodec.encode(128, data), 2)
        self.assertEqual(in3120.VariableByteCodec.encode(512, data), 2)
        self.assertEqual(in3120.VariableByteCodec.encode(999, data), 2)
        self.assertEqual(in3120.VariableByteCodec.encode(214577, data), 3)
        self.assertEqual(in3120.VariableByteCodec.encode(134217728, data), 4)
        self.assertEqual(len(data), 18)
        self.assertEqual(in3120.VariableByteCodec.decode(data, 0), (21, 1))
        self.assertEqual(in3120.VariableByteCodec.decode(data, 1), (4, 1))
        self.assertEqual(in3120.VariableByteCodec.decode(data, 2), (70, 1))
        self.assertEqual(in3120.VariableByteCodec.decode(data, 3), (0, 1))
        self.assertEqual(in3120.VariableByteCodec.decode(data, 4), (127, 1))
        self.assertEqual(in3120.VariableByteCodec.decode(data, 5), (128, 2))
        self.assertEqual(in3120.VariableByteCodec.decode(data, 7), (512, 2))
        self.assertEqual(in3120.VariableByteCodec.decode(data, 9), (999, 2))
        self.assertEqual(in3120.VariableByteCodec.decode(data, 11), (214577, 3))
        self.assertEqual(in3120.VariableByteCodec.decode(data, 14), (134217728, 4))

    def test_negative_numbers(self):
        for i in range(1, 5):
            with self.assertRaises(AssertionError):
                in3120.VariableByteCodec.encode(-i, bytearray())

    def test_illegal_decoding_offsets(self):
        data = bytearray()
        self.assertEqual(in3120.VariableByteCodec.encode(210470, data), 3)
        self.assertEqual(len(data), 3)
        self.assertEqual(in3120.VariableByteCodec.decode(data, 0), (210470, 3))
        for i in range(1, 3):
            with self.assertRaises(AssertionError):
                in3120.VariableByteCodec.decode(data, i)
        with self.assertRaises(IndexError):
            in3120.VariableByteCodec.decode(data, 4)

    def test_missing_buffer(self):
        with self.assertRaises(AssertionError):
            in3120.VariableByteCodec.encode(210470, None)
        with self.assertRaises(AssertionError):
            in3120.VariableByteCodec.decode(None, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
