from django.http import HttpResponse
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
            print("View")
            # get image from request
            if "puzzle" not in request.FILES:
                return HttpResponse(
                    {
                        "message": "Puzzle file not supplied",
                        "error": "User must supply image of unsolved sudoku puzzle.",
                    },
                    status=400,
                )

            print("Puzzle")
            # extract unsolved puzzle from request
            puzzle = request.FILES["puzzle"]

            print("Image Type")
            # reject incorrect file types
            if not puzzle.name.lower().endswith((".jpg", ".jpeg", ".png")):
                return HttpResponse(
                    {
                        "message": "Invalid file type, image must be a JPEG or PNG file.",
                        "error": "Only JPEG, PNG, and BMP file types are allowed.",
                    },
                    status=400,
                )

            print("Convert")
            try:
                # convert image into nparray
                img = convert_file_to_nparray(puzzle)
            except Exception as e:
                return HttpResponse(
                    {
                        "message": "Failed to convert file to numpy array",
                        "error": str(e),
                    },
                    status=400,
                )

            print("Process")
            try:
                # preprocess image
                img_proc = preprocess_image(img)
            except Exception as e:
                return HttpResponse(
                    {"message": "Failed to preprocess image.", "error": str(e)},
                    status=400,
                )

            print("Borders")
            try:
                # find contours
                contours = find_contours(img_proc)
                # find outer border
                border = biggest_contour(contours)
                border = reorder(border)
            except Exception as e:
                return HttpResponse(
                    {"message": "Failed to find borders of puzzle.", "error": str(e)},
                    status=400,
                )

            print("Perspective and Spliting")
            try:
                # apply perspective shift
                img_persp = perspective_warp(border, img)
                # split puzzle into cells
                cells = split_boxes(img_persp)
            except Exception as e:
                return HttpResponse(
                    {
                        "message": "Failed to locate each square of the sudoku puzzle.",
                        "error": str(e),
                    },
                    status=400,
                )
            print("Make Predictions")
            try:
                # extract unsolved puzzle
                unsolved, _ = get_prediction(cells, self.model)
            except Exception as e:
                return HttpResponse(
                    {
                        "message": "Failed to make prediction of each square in puzzle.",
                        "error": str(e),
                    },
                    status=400,
                )
            print("Solve Board")
            try:
                # solve board
                solved = solve_board(unsolved)
            except Exception as e:
                return HttpResponse(
                    {
                        "message": "Failed to generate solution to puzzle.",
                        "error": str(e),
                    },
                    status=400,
                )

            print("Overlay Solution")
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

            print("Convert Back")
            try:
                # convert from np.ndarray to jpg
                img_jpg = convert_nparray_to_jpg(img_ans)
            except Exception as e:
                return HttpResponse(
                    {
                        "message": "Failed to convert solved puzzle into JPEG.",
                        "error": str(e),
                    },
                    status=400,
                )

            return HttpResponse(img_jpg, content_type="image/jpeg", status=200)
        except Exception as e:
            return HttpResponse(
                {"message": "An unexpected error occurred", "error": str(e)}, status=500
            )
