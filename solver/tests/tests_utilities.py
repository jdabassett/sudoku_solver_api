import cv2
from django.test import SimpleTestCase
from django.core.files.base import File
import os
from PIL import Image
from io import BytesIO
import numpy as np
import unittest
import yaml

from ..utilities import (
    biggest_contour,
    convert_file_to_nparray,
    convert_nparray_to_jpg,
    display_numbers,
    find_contours,
    get_prediction,
    initialize_prediction_model,
    overlay_solution,
    perspective_warp,
    preprocess_image,
    reorder,
    split_boxes,
)

#############################################################################
# Global Variables
with open("./data/data/data.yaml", "r") as file:
    data = yaml.safe_load(file)

test_unsolved_img = data["test_unsolved_img"]
test_solved_img = data["test_solved_img"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
unsolved_path = os.path.join(BASE_DIR, "data/puzzles/3.jpg")
solved_mask_path = os.path.join(BASE_DIR, "data/puzzles/3_mask.jpg")
solved_solution_path = os.path.join(BASE_DIR, "data/puzzles/3_solution.jpg")
#############################################################################


# tests must be run sequentially


class UtilitiesTestCase(SimpleTestCase):

    unsolved = test_unsolved_img
    solved = test_solved_img
    border = np.array([[[44, 215]], [[1873, 215]], [[44, 1848]], [[1873, 1847]]], dtype=np.int32)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = initialize_prediction_model()

    def setUp(self):
        with open(unsolved_path, "rb") as file:
            self.img = convert_file_to_nparray(file)
        with open(solved_mask_path, "rb") as file:
            self.mask = convert_file_to_nparray(file)
        with open(solved_solution_path, "rb") as file:
            self.solution = convert_file_to_nparray(file)

    # @unittest.skip("Skipping this test method")
    def test_convert_file_to_nparray(self):
        """Input different types of mock file images and test conversion of each into np.ndarray."""
        image = Image.new("RGB", size=(5, 5), color=(256, 0, 0))

        for file_type in ["TIFF", "WebP", "JPEG", "PNG", "BMP"]:
            with BytesIO() as image_file:
                image.save(image_file, format=file_type)
                image_file.seek(0)
                mock_file = File(image_file, name="mock_image.png")
                result = convert_file_to_nparray(mock_file)
            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(result.shape, (5, 5, 3))
        self.assertEqual(self.img.shape, (1920, 1920, 3))

    # @unittest.skip("Skipping this test method")
    def test_preprocess_image(self):
        """Test processed image to grayscale and apply blur/threshold."""
        processed = preprocess_image(self.img)
        self.assertIsNotNone(processed)
        self.assertEqual(processed.shape, (1920, 1920))
        self.assertFalse(np.array_equal(self.img, processed))

    # @unittest.skip("Skipping this test method")
    def test_find_contours_and_biggest_contour(self):
        """Can find outer border of sudoku?"""
        processed = preprocess_image(self.img)
        contours = find_contours(processed)
        biggest = biggest_contour(contours)
        expected_raw = np.array(
            [[[44, 215]], [[44, 1848]], [[1873, 1847]], [[1873, 215]]], dtype=np.int32
        )
        self.assertTrue(np.array_equal(biggest, expected_raw))
        biggest_reordered = reorder(biggest)
        self.assertTrue(np.array_equal(biggest_reordered, self.border))
        self.border = biggest_reordered

    # @unittest.skip("Skipping this test method")
    def test_perspective_warp(self):
        """Perspective work returns grayscale image of correct dimensions."""
        processed = preprocess_image(self.img)
        contours = find_contours(processed)
        biggest = biggest_contour(contours)
        border = reorder(biggest)
        img_persp = perspective_warp(border, self.img)
        self.assertEqual(img_persp.shape, (450, 450))
        self.assertGreaterEqual(np.mean(img_persp), 200)
        self.assertLessEqual(np.mean(img_persp), 230)

    # @unittest.skip("Skipping this test method")
    def test_split_boxes(self):
        """Is the test image split into 81 cells of correct dimensions."""
        processed = preprocess_image(self.img)
        contours = find_contours(processed)
        biggest = biggest_contour(contours)
        border = reorder(biggest)
        img_persp = perspective_warp(border, self.img)
        cells = split_boxes(img_persp)
        self.assertEqual(len(cells), 81)
        self.assertEqual(cells[0].shape, (50, 50))

    # @unittest.skip("Skipping this test method")
    def test_get_prediction(self):
        """Can model predict value of each cell accurately."""
        processed = preprocess_image(self.img)
        contours = find_contours(processed)
        biggest = biggest_contour(contours)
        border = reorder(biggest)
        img_persp = perspective_warp(border, self.img)
        cells = split_boxes(img_persp)
        unsolved, _ = get_prediction(cells, self.model)
        self.assertTrue(np.array_equal(unsolved, self.unsolved))

    # @unittest.skip("Skipping this test method")
    def test_display_numbers(self):
        """Is valid mask created."""
        img_mask = display_numbers(self.unsolved, self.solved, self.img.shape[:-1])
        np.allclose(img_mask, self.mask)

    # @unittest.skip("Skipping this test method")
    def test_overlay_solution(self):
        """Is valid overlay created"""
        img_solution = overlay_solution(self.img, self.mask, self.border, self.img.shape[:-1])
        np.allclose(img_solution, self.solution)

    # @unittest.skip("Skipping this test method")
    def test_convert_nparray_to_jpg(self):
        """Does conversion from nparray to jpg work as expected"""
        temp = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        jpeg = convert_nparray_to_jpg(temp)
        reconstructed = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
        np.allclose(temp, reconstructed)
