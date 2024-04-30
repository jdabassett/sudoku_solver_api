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
            self.solved = file.read()

    # @unittest.skip("Skipping this test method")
    def test_post_endpoint(self):
        url = reverse("solve")
        client = Client()
        response = client.post(url, {"puzzle": self.unsolved}, format="multipart")
        if response.status_code != 200:
            try:
                content_str = response.content.decode("utf-8")
                content_json = json.loads(content_str)
                print("Error message:", content_json.get("message"))
            except Exception as e:
                print("Failed to parse error message:", e)
        self.assertEqual(response.status_code, 200)