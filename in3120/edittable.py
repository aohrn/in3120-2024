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

    # The default cell value, when initializing the table. This value does not matter since all
    # relevant cell values will be computed, but a value of -1 stands out visually when printing
    # the table for debugging purposes. That way, if you print the table while the computation is
    # in some intermediate state, you can easily see which cells that have been visited and which
    # ones that have not.
    _default = -1

    # A large internal value used to represent "infinity", for all practical purposes.
    _infinity = 210470

    def __init__(self, query: str, candidate: str, compute: bool = True):

        # Logical row/column labels. The query string is immutable, but we offer clients the
        # capability to mutate the candidate string on a per symbol basis.
        self._query = query
        self._candidate = list(candidate)

        # Initialize table. Pad the table with an extra row and an extra column,
        # representing the empty string that we can imagine prefixes both strings.
        # Note that since we add an extra row and an extra columns, we will elsewhere
        # have to offset accordingly to align between table row/column indices and the
        # indices into the strings that logically correspond to each row/column.
        self._table = [[self._default for j in range(len(self._candidate) + 1)] for i in range(len(self._query) + 1)]

        # Initialize with edit distances to the empty string, i.e., fill the row/column
        # we padded above.
        for i in range(len(self._query) + 1):
            self._table[i][0] = i
        for j in range(len(self._candidate) + 1):
            self._table[0][j] = j

        # Populate the table, unless otherwise instructed. Start at the NW-most (upper left)
        # corner cell, and do column by column. The edit distance will be located in the SE-most
        # (lower right) corner cell.
        if compute:
            for j in range(1, len(self._candidate) + 1):
                self.update(j)

    def __extend(self, extra: int) -> None:
        """
        Appends a few extra columns to the table. Appending columns implies (a) appending symbols
        to the candidate string, (b) appending cells to the special first padding row, and (c)
        appending cells to all the other rows.
        """
        current = len(self._candidate)
        self._candidate.extend("?" for _ in range(extra))
        self._table[0].extend(x for x in range(current + 1, current + 1 + extra))
        for i in range(1, len(self._table)):
            self._table[i].extend(self._default for _ in range(extra))

    def stringify(self) -> str:
        """
        Creates a readable version of the edit table, for manual inspection and debugging.
        """
        width = 3
        header = " " + (" " * width) + "".join(f"{s:>{width}}" for s in self._candidate)
        row0 = " " + "".join(f"{str(v):>{width}}".format(v) for v in self._table[0])
        rows = [f"{self._query[i]}" + "".join(f"{str(v):>{width}}".format(v) for v in self._table[i + 1]) for i in range(len(self._query))]
        return "\n".join(["", header, row0] + rows)

    def update(self, j: int) -> int:
        """
        Updates all cells in the given table column, according to the Damerau-Levenshtein rule.
        Assumes unit edit costs for all edit operations, and that all columns to the left have
        already been computed.
        
        Returns the minimum value in the updated table column. This corresponds to returning
        the minimal value of edit-distance(query[0:i], candidate[0:j]) found by varying over
        all the row indices i, i.e., the minimal edit distance between candidate[0:j] and some
        prefix of the query string.
        """
        symbol = self._candidate[j - 1]
        result = self._infinity
        for i in range(1, len(self._query) + 1):
            if self._query[i - 1] == symbol:
                self._table[i][j] = self._table[i - 1][j - 1]
            else:
                self._table[i][j] = 1 + min(self._table[i - 1][j], self._table[i][j - 1], self._table[i - 1][j - 1])
            if i > 1 and j > 1 and self._query[i - 2] == symbol and self._query[i - 1] == self._candidate[j - 2]:
                self._table[i][j] = min(self._table[i - 2][j - 2] + 1, self._table[i][j])
            result = min(result, self._table[i][j])
        return result

    def update2(self, j: int, symbol: str) -> int:
        """
        Similar to update/1 above, but simultaneously allows you to update a single symbol
        in the candidate string, namely the symbol corresponding to the given column.

        Additionally, this method appends additional columns to the table if the supplied
        column index is just out of range. That way, the table is usable also by clients
        that need to deal with candidate strings longer than what was initially anticipated.
        """
        if j == len(self._candidate) + 1:
            self.__extend(5)
        self._candidate[j - 1] = symbol
        return self.update(j)

    def distance(self, j: int = -1) -> int:
        """
        Returns the edit distance between the query string and the candidate string.
        Defaults to looking at the SE-most cell in the table, i.e., the edit distance
        between the complete strings.
        
        Only a prefix of the candidate string can be considered, if specified. That is,
        the caller is allowed to supply a column index and that way vary the W-E axis.
        """
        return self._table[-1][j]

    def prefix(self, j: int) -> str:
        """
        Returns the prefix of the candidate string, up to the given index. I.e.,
        returns candidate[0:j].
        """
        return "".join(self._candidate[0:j])
