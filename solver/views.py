from django.http import HttpResponse
import json
from rest_framework.views import APIView

from .sudoku_solver import solve_board
from .utilities import (
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


class Sudoku_API(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = initialize_prediction_model()

    def post(self, request):
        try:
            response_data = { 
                'message': "",
                'error': "",
            }
            # print("View")
            # get image from request
            if "puzzle" not in request.FILES:
                response_data['message'] = "Puzzle file not supplied."
                response_data['error'] = 'User must supply image of unsolved sudoku puzzle.'
                return HttpResponse(
                    json.dumps(response_data),
                    status=400,
                )

            # print("Puzzle")
            # extract unsolved puzzle from request
            puzzle = request.FILES["puzzle"]

            # print("Puzzle Type")
            # reject incorrect file types
            if not puzzle.name.lower().endswith((".jpg", ".jpeg", ".png")):
                response_data['message'] = "Invalid file type, image must be a JPEG or PNG file."
                response_data['error'] = 'Only JPEG and PNG file types are allowed.'
                return HttpResponse(
                    json.dumps(response_data),
                    status=400,
                )

            # print("Convert")
            try:
                # convert image into nparray
                puzzle_read = puzzle.read()
                img = convert_file_to_nparray(puzzle_read)
            except Exception as e:
                response_data['message'] = "Failed to convert file to numpy array."
                response_data['error'] = str(e)
                return HttpResponse(
                    json.dumps(response_data),
                    status=400,
                )

            # print("Process")
            try:
                # preprocess image
                img_proc = preprocess_image(img)
            except Exception as e:
                response_data['message'] = "Failed to process image."
                response_data['error'] = str(e)
                return HttpResponse(
                    json.dumps(response_data),
                    status=400,
                )

            # print("Border")
            try:
                # find contours
                contours = find_contours(img_proc)
                # find outer border
                border = biggest_contour(contours)
                border = reorder(border)
            except Exception as e:
                response_data['message'] = "Failed to find borders of sudoku puzzle."
                response_data['error'] = str(e)
                return HttpResponse(
                    json.dumps(response_data),
                    status=400,
                )

            # print("Perspective")
            try:
                # apply perspective shift
                img_persp = perspective_warp(border, img)
                # split puzzle into cells
                cells = split_boxes(img_persp)
            except Exception as e:
                response_data['message'] = "Failed to locate each square of the puzzle."
                response_data['error'] = str(e)
                return HttpResponse(
                    json.dumps(response_data),
                    status=400,
                )
     
            # print("Predict")
            try:
                # extract unsolved puzzle
                unsolved, _ = get_prediction(cells, self.model)
            except Exception as e:
                response_data['message'] = "Failed to predict every square of the puzzle."
                response_data['error'] = str(e)
                return HttpResponse(
                    json.dumps(response_data),
                    status=400,
                )

            # print("Solve")
            try:
                # solve board
                solved = solve_board(unsolved)
                if solved is None:
                    raise ValueError("Puzzle input could not be solved")
            except Exception as e:
                response_data['message'] = "Puzzle unsolvable."
                response_data['error'] = str(e)
                return HttpResponse(
                    json.dumps(response_data),
                    status=400,
                )

            # print("Overlay")
            try:
                # overlay solution to input image
                img_mask = display_numbers(unsolved, solved, img.shape[:-1])
                img_ans = overlay_solution(img, img_mask, border, img.shape[:-1])
            except Exception as e:
                return HttpResponse(
                    {
                        "message": "Failed overlay solution onto puzzle.",
                        "error": str(e),
                    },
                    status=400,
                )

            # print("Convert back")
            try:
                # convert from np.ndarray to jpg
                img_jpg = convert_nparray_to_jpg(img_ans)
            except Exception as e:
                response_data['message'] = "Failed to convert solved puzzle into JPG."
                response_data['error'] = str(e)
                return HttpResponse(
                    json.dumps(response_data),
                    status=400,
                )

            return HttpResponse(img_jpg, content_type="image/jpeg", status=200)
        except Exception as e:
                response_data['message'] = "Unexpected error."
                response_data['error'] = str(e)
                return HttpResponse(
                    json.dumps(response_data),
                    status=500,
                )