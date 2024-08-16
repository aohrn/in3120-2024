# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

class EliasGammaCodec:
    """
    A simple encoder/decoder for Elias gamma codes. See Section 5.3.2 in
    https://nlp.stanford.edu/IR-book/pdf/05comp.pdf for details.
    """

    @staticmethod
    def encode(number: int) -> str:
        """
        Given a positive integer, returns a string of bits representing the
        integer's gamma code.

        The current implementation is extremely inefficient, and is only meant for
        educational purposes.
        """
        assert number > 0
        binary = bin(number)                # The number in binary as a string of bits, with a '0b' prefix.
        offset = binary[3:]                 # The number in binary, with the leading 1 removed.
        length = ('1' * len(offset)) + '0'  # The length of the offset, in unary code.
        return length + offset

    @staticmethod
    def decode(bits: str) -> int:
        """
        Given a string of bits representing a gamma-encoded integer,
        transforms this string of bits back into the original integer.

        The current implementation is extremely inefficient, and is only meant for
        educational purposes.
        """
        assert bits
        length = bits.index('0') + 1        # Read the unary code up to the 0 that terminates it.
        offset = bits[length:]              # The remainder, if any, is the offset.
        binary = '1' + offset               # The 1 that was chopped off in encoding is prepended.
        return int(binary, 2)
