from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .sudoku_solver import (
    solve_board)
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
    split_boxes)


class Sudoku_API(APIView):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.model = initialize_prediction_model()

  # TODO: error handling
  def post(self, request):
    # get image from request
    # if 'puzzle' in request.FILES:
    print("loaded image")
    puzzle = request.FILES['puzzle']
    img = convert_file_to_nparray(puzzle)
    # validate that image is compatible with downstream
    # preprocess image
    print("processed image")
    img_proc = preprocess_image(img)
    # find contours
    print("found contours")
    contours = find_contours(img_proc)
    # find outer border
    print("found largest contour")
    border = biggest_contour(contours)
    border = reorder(border)
    # apply perspective shift
    print("attempted perspective warp")
    img_persp = perspective_warp(border, img_proc)
    # split puzzle into cells
    print("split into cells")
    cells = split_boxes(img_persp)
    # extract unsolved puzzle
    print("attempt predict")
    unsolved = get_prediction(cells, self.model)
    test_puzzle = [[2, 1, 0, 0, 6, 0, 9, 0, 0], [0, 0, 0, 0, 0, 9, 1, 0, 0], [4, 0, 9, 3, 1, 0, 0, 5, 8], [0, 0, 1, 0, 0, 5, 0, 4, 0], [9, 0, 4, 0, 3, 0, 8, 0, 5], [0, 5, 0, 2, 0, 0, 6, 0, 0], [3, 8, 0, 0, 4, 0, 5, 0, 6], [0, 0, 6, 7, 0, 0, 0, 0, 2], [0, 0, 7, 0, 8, 0, 3, 0, 9]]
    # solve board
    print("attempt solve")
    solved = solve_board(test_puzzle)
    # overlay solution to input image
    print("overlay solution")
    img_mask = display_numbers(unsolved, solved)
    img_ans = overlay_solution(img, img_mask, border)
    # # convert from np.ndarray to jpg
    # print("convert to jpg")
    # img_jpg = convert_nparray_to_jpg(img_ans)
    # print("attempt response")
    # return Response(img_jpg, content_type="image/jpeg")
    return Response({"message": "Success!"}, status=status.HTTP_200_OK)