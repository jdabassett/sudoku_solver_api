import copy
import heapq
import pandas as pd
import time
from typing import Dict, List, Set, Tuple


class Sudoku:
    full_set = set([i for i in range(0, 10)])
    solved_set = set([i for i in range(1, 10)])

    @staticmethod
    def _is_solved(board: List[List[str]]) -> bool:
        """Returns boolean if board is solved"""
        if not board:
            return False

        temp = copy.deepcopy(board)

        r, c, s, e = Sudoku.generate_rcs_sets(temp)

        # dict board size should be
        if len(r) != 9 and len(c) != 9 and len(s) != 9 and len(e) == 0:
            return False

        # dict board should contain
        for i in range(9):
            if i not in r or i not in c or i not in s:
                return False
            if r[i] != Sudoku.solved_set or c[i] != Sudoku.solved_set or s[i] != Sudoku.solved_set:
                return False
        return True

    @staticmethod
    def check_board_validity(board: List[List[str]]) -> bool:
        """Test if input board is valid."""
        # board is right type and size
        if not isinstance(board, list) or len(board) != 9:
            return False

        # cells are right type, size and value
        for row in board:
            if not isinstance(row, list) or len(row) != 9:
                return False
            for value in row:
                if not isinstance(value, int) or value not in Sudoku.full_set:
                    return False

        return True

    @staticmethod
    def generate_rcs_sets(board: List[List[str]]) -> Tuple[Dict[int, Set[int]], Dict[int, Set[int]], Dict[int, Set[int]], Set[Tuple[int]]]:
        """Generate board representation of rows, cols, squares, and empties."""
        temp = copy.deepcopy(board)
        rows = {i: set() for i in range(0, 9)}
        cols = {i: set() for i in range(0, 9)}
        squares = {i: set() for i in range(0, 9)}
        empties = set()
        for i in range(9):
            for j in range(9):
                n = temp[i][j]
                k = 3 * (i // 3) + j // 3
                if n == 0:
                    empties.add((i, j, k))
                else:
                    rows[i].add(n)
                    cols[j].add(n)
                    squares[k].add(n)

        return rows, cols, squares, empties

    def __init__(self, unsolved: List[List[str]]):
        if not self.check_board_validity(unsolved):
            raise ValueError("Board is invalid.")
        self.unsolved_board = unsolved
        self.solved_board = None
        self.is_solved = False

    def solve_board(self) -> None | List[List[str]]:
        """Takes unsolved_board attribute and generates solved_board and is_solved attributes. Also returns board is solved or None if not."""
        temp = copy.deepcopy(self.unsolved_board)

        rows, cols, squares, empties = self.generate_rcs_sets(temp)

        heap = []
        count = 0
        for i, j, k in empties:
            possibilities = Sudoku.solved_set - (rows[i] | cols[j] | squares[k])
            if len(possibilities) == 1:
                n = possibilities.pop()
                rows[i].add(n)
                cols[j].add(n)
                squares[k].add(n)
                temp[i][j] = n
            else:
                heapq.heappush(heap, (count, len(possibilities), i, j, k))

        solution = []
        count += 1
        bifurcation_length = 1
        while heap:
            item_count, _, i, j, k = heapq.heappop(heap)

            if item_count > count:
                count = item_count
                bifurcation_length += 1
                # print(f'Incrementing bifurcation length to {bifurcation_length}')

            if bifurcation_length > 9:
                return None

            if item_count < count:
                heapq.heappush(heap, (count, len(possibilities), i, j, k))
                continue

            possibilities = Sudoku.solved_set - (rows[i] | cols[j] | squares[k])

            while not possibilities:
                if not solution:
                    # print('Failed to find solution due to empty solution stack')
                    return None
                # backtrack adding attempted squares back minus n
                heapq.heappush(heap, (count + 1, len(possibilities), i, j, k))
                # backtrack until possibilities are not empty
                i, j, k, n, possibilities = solution.pop()
                rows[i].remove(n)
                cols[j].remove(n)
                squares[k].remove(n)

            if len(possibilities) <= bifurcation_length:
                n = possibilities.pop()
                rows[i].add(n)
                cols[j].add(n)
                squares[k].add(n)
                solution.append((i, j, k, n, possibilities))
                bifurcation_length = 1
                continue

            heapq.heappush(heap, (count + 1, len(possibilities), i, j, k))

        while solution:
            i, j, k, n, possibilities = solution.pop()
            temp[i][j] = n

        if self._is_solved(temp):
            self.is_solved = True
            self.solved_board = temp
            return temp
        else:
            self.is_solved = False
            self.solved_board = None
            return None


def convert_board(board: str) -> List[List[int]]:
    """Convert board from string into nested list of integers"""
    ret_board = [[] for _ in range(9)]
    for idx, val in enumerate(board):
        row = idx//9
        ret_board[row].append(int(val))
    return ret_board


def solve_board(board: List[List[str]]) -> List[List[str]]:
    """Create instance and solve board. Return Solved board."""
    sudoku = Sudoku(board)
    sudoku.solve_board()
    return sudoku.solved_board


# if __name__ == "__main__":
#     num = 1000
#     df = pd.read_csv('../data/raw/sudoku.csv')
#     df = df.head(num)
#     df['raw_unsolved'] = df['quizzes'].apply(convert_board)
#     df['raw_solved'] = df['solutions'].apply(convert_board)
#     start_time = time.time()
#     df['solved'] = df['raw_unsolved'].apply(solve_board)
#     end_time = time.time()
#     elapsed = end_time - start_time
#     m_sec_per = round((elapsed/num)*1000, 0)
#     print(elapsed)
#     results = all(df['raw_solved'] == df['solved'])
#     print(results)
    # print(df['quizzes'][0])
    # print(df['raw_unsolved'][0])
    # print(df['raw_solved'][0])