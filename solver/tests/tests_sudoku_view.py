import cv2
from django.test import SimpleTestCase, Client
from django.core.files.base import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from io import BytesIO
from PIL import Image
import numpy as np
import json
import os
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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
unsolved_path = os.path.join(BASE_DIR, "data/puzzles/3.jpg")
solved_solution_path = os.path.join(BASE_DIR, "data/puzzles/3_solution.jpg")
#############################################################################

class SudokuAPITestCase(SimpleTestCase):
    
    def setUp(self):
        with open(unsolved_path, "rb") as file:
            self.unsolved = SimpleUploadedFile("unsolved.jpg", file.read(), content_type="image/jpeg")
        with open(solved_solution_path, "rb") as file:
            self.solved = SimpleUploadedFile("solved.jpg", file.read(), content_type="image/jpeg")

    @unittest.skip("Skipping this test method")
    def test_post_failed_puzzle_key(self):
        """Post request should raise status code 400 if puzzle keyword not in form."""
        url = reverse("solve")
        client = Client()
        response = client.post(url, {"banana": self.unsolved}, format="multipart")
        self.assertEqual(response.status_code, 400)
        content = response.content.decode('utf-8')
        response_data = json.loads(content)
        self.assertEqual(response_data.get("image"),None)
        self.assertEqual(response_data.get("message"),"Puzzle file not supplied.")
        self.assertEqual(response_data.get("error"), "User must supply image of unsolved sudoku puzzle.")


    @unittest.skip("Skipping this test method")
    def test_post_failed_puzzle_extension(self):
        """Post request should raise status code 400 if image extension is not jpeg, jpg, or png."""
        url = reverse("solve")
        client = Client()
        for extension in ["bmp","tiff","gif","pdf","svg","webp"]:
          mock_image = self.create_mock_image(5,5)
          mock_file = SimpleUploadedFile(f"test_image.{extension}", mock_image, content_type=f"image/{extension}")
          response = client.post(url, {"puzzle": mock_file}, format="multipart")
          self.assertEqual(response.status_code, 400)
          content = response.content.decode('utf-8')
          response_data = json.loads(content)
          self.assertEqual(response_data.get("image"),None)
          self.assertEqual(response_data.get("message"),"Invalid file type, image must be a JPEG or PNG file.")
          self.assertEqual(response_data.get("error"), "Only JPEG and PNG file types are allowed.")

        

    @unittest.skip("Skipping this test method")
    def test_post_pass(self):
        """Post request should pass"""
        url = reverse("solve")
        client = Client()
        response = client.post(url, {"puzzle": self.unsolved}, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'image/jpeg')
        response_img = convert_file_to_nparray(response.content)
        actual_img = convert_file_to_nparray(self.solved.read())
        self.assertTrue(np.mean((response_img - actual_img) ** 2)<1)

    def create_mock_image(self, width, height):
        color = (255, 255, 255)  
        image = Image.new("RGB", (width, height), color)
        image_bytes = BytesIO()
        image.save(image_bytes, format="JPEG")
        return image_bytes.getvalue()

    

