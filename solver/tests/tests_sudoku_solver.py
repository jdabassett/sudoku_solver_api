from django.test import SimpleTestCase
import unittest
import yaml

from ..sudoku_solver import Sudoku, convert_board, solve_board


########################################################################################################################
# Global Variables
with open("./data/data/data.yaml", "r") as file:
    data = yaml.safe_load(file)

test_unsolved_string = data["test_unsolved_string"]
test_unsolvable = data['test_unsolvable']
test_unsolved = data["test_unsolved"]
test_solved = data["test_solved"]
test_incorrect = data["test_incorrect"]
test_unsolved_r = {key: set(value) for key, value in data["test_unsolved_r"].items()}
test_unsolved_c = {key: set(value) for key, value in data["test_unsolved_c"].items()}
test_unsolved_s = {key: set(value) for key, value in data["test_unsolved_s"].items()}
test_unsolved_e = {tuple(each) for each in data["test_unsolved_e"]}
test_invalids = data['test_invalids']
########################################################################################################################


class ConvertBoardTestCase(SimpleTestCase):
    uncoverted = test_unsolved_string
    unsolved = test_unsolved

    # @unittest.skip("Skipping this test method")
    def test_convert_board(self):
        """function converts string to nested list of integers properly."""
        actual = convert_board(self.uncoverted)
        self.assertEqual(self.unsolved, actual)

    # @unittest.skip("Skipping this test method")
    def test_convert_board_fail(self):
        """function doesn't raise an error with improper input"""
        actual = convert_board(self.uncoverted[:-2])
        self.assertNotEqual(self.unsolved, actual)


class SudokuClassTestCase(SimpleTestCase):
    unsolvable = test_unsolvable
    unsolved = test_unsolved
    solved = test_solved
    incorrect = test_incorrect
    sudoku = None
    r = test_unsolved_r
    c = test_unsolved_c
    s = test_unsolved_s
    e = test_unsolved_e

    def setUp(self):
        self.sudoku = Sudoku(self.unsolved)

    # @unittest.skip("Skipping this test method")
    def test_instance_attributes(self):
        """Attributes of sudoku instance are proper."""
        full_set = set([i for i in range(0, 10)])
        solved_set = set([i for i in range(1, 10)])
        self.assertEqual(self.sudoku.unsolved_board, self.unsolved)
        self.assertEqual(self.sudoku.solved_board, None)
        self.assertEqual(self.sudoku.is_solved, False)
        self.assertEqual(self.sudoku.full_set, full_set)
        self.assertEqual(self.sudoku.solved_set, solved_set)

    # @unittest.skip("Skipping this test method")
    def test_instance_fail(self):
        """Error handling if unsolved board used to create sudoku instances is improper."""
        with self.assertRaises(ValueError):
            sudoku = Sudoku(self.unsolved[:-2])
        with self.assertRaises(ValueError):
            sudoku = Sudoku("")

    # @unittest.skip("Skipping this test method")
    def test_staticmethod_check_board_validity(self):
        """Check if board is valid and all the ways it can fail."""
        valid = self.sudoku.check_board_validity(self.unsolved)
        self.assertTrue(valid)
        for item in test_invalids:
            self.assertFalse(self.sudoku.check_board_validity(item))

    # @unittest.skip("Skipping this test method")
    def test_staticmethod_generate_rcs_sets(self):
        """Proper returns"""
        r, c, s, e = self.sudoku.generate_rcs_sets(self.unsolved)
        self.assertEqual(r, self.r)
        self.assertEqual(c, self.c)
        self.assertEqual(s, self.s)
        self.assertEqual(e, self.e)

    # @unittest.skip("Skipping this test method")
    def test_staticmehod_is_solved(self):
        """Proper returns with input of unsolved, solved, and incorrect puzzles."""
        bool_unsolved = self.sudoku._is_solved(self.unsolved)
        bool_solved = self.sudoku._is_solved(self.solved)
        bool_incorrect = self.sudoku._is_solved(self.incorrect)
        self.assertEqual(bool_unsolved, False)
        self.assertEqual(bool_solved, True)
        self.assertEqual(bool_incorrect, False)

    # @unittest.skip("Skipping this test method")
    def test_solve_board(self):
        """Does unsolved puzzle return solved puzzle? Does unsolvable puzzle return None?"""
        solved0 = solve_board(self.unsolved)
        solved1 = solve_board(self.solved)
        failed = solve_board(self.unsolvable)
        self.assertEqual(solved0, self.solved)
        self.assertEqual(solved1, self.solved)
        self.assertIsNone(failed)

