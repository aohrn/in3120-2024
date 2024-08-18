# pylint: disable=missing-module-docstring
# pylint: disable=line-too-long

class EditTable:
    """
    A simple representation of an edit table with unit edit costs, using Damerau-Levenshtein
    distance. See https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance. See
    also https://www.cs.helsinki.fi/u/tpkarkka/teach/16-17/SPA/lecture06.pdf for additional
    details.

    The edit table is equipped with an interface so that it is easy to use together with the
    trie-based algorithm described in the paper "Tries for Approximate String Matching" by
    Shang and Merrett. That algorithm allows us to not just compute the edit distance between
    two strings, but to efficiently locate all strings in a trie that are "close enough" to
    a given query string.

    The time complexity of computing the edit distance between the query string and the
    candidate string is O(M * N), when M and N are the lengths of the two strings. Less on
    average if Ukkonen's cutoff heuristic is applied and we bound our allowed edit distance.
    Bit-parallelism techniques exist that can bring this down to O(M * N / W), where W is
    the word size of the computer.

    The space complexity of the current implementation is also O(M * N), but this can be reduced
    by noticing that each column of the edit table depends only on the previous column (in the
    case of Levenshtein distance) or previous two columns (in the case of Damerau-Levenshtein
    distance). We do thus not need to store older columns. Such a space optimization does not
    play nice with the needs of the abovementioned algorithm by Shang and Merrett, though.

    """


    def __init__(self, query: str, candidate: str, compute: bool = True):
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def __extend(self, extra: int) -> None:
        """
        Appends a few extra columns to the table. Appending columns implies (a) appending symbols
        to the candidate string, (b) appending cells to the special first padding row, and (c)
        appending cells to all the other rows.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def stringify(self) -> str:
        """
        Creates a readable version of the edit table, for manual inspection and debugging.
        """
        raise NotImplementedError("OPTIONAL: You need to implement this as part of the obligatory assignment.")

    def update(self, j: int) -> int:
        """
        Updates all cells in the given table column, according to the Damerau-Levenshtein rule.
        Assumes unit edit costs for all edit operations, and that all columns to the left have
        already been computed.
        
        Returns the minimum value in the updated table column. This corresponds to returning
        the minimal value of edit-distance(query[0:i], candidate[0:j]) found by varying over
        all the row indices i.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def distance(self, j: int = -1) -> int:
        """
        Returns the edit distance between the query string and the candidate string.
        Defaults to looking at the SE-most cell in the table, i.e., the edit distance
        between the complete strings.
        
        Only a prefix of the candidate string can be considered, if specified. That is,
        the caller is allowed to supply a column index and that way vary the W-E axis.
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")

    def prefix(self, j: int) -> str:
        """
        Returns the prefix of the candidate string, up to the given index. I.e.,
        returns candidate[0:j].
        """
        raise NotImplementedError("You need to implement this as part of the obligatory assignment.")
