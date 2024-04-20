from django.http import HttpResponse
from rest_framework.views import APIView

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


###########################################################
test_puzzle = [[2, 1, 0, 0, 6, 0, 9, 0, 0], [0, 0, 0, 0, 0, 9, 1, 0, 0], [4, 0, 9, 3, 1, 0, 0, 5, 8], [0, 0, 1, 0, 0, 5, 0, 4, 0], [9, 0, 4, 0, 3, 0, 8, 0, 5], [0, 5, 0, 2, 0, 0, 6, 0, 0], [3, 8, 0, 0, 4, 0, 5, 0, 6], [0, 0, 6, 7, 0, 0, 0, 0, 2], [0, 0, 7, 0, 8, 0, 3, 0, 9]]
###########################################################


class Sudoku_API(APIView):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.model = initialize_prediction_model()

  # TODO: error handling
  def post(self, request):
    # get image from request
    if 'puzzle' in request.FILES:
      print("loaded image")
      puzzle = request.FILES['puzzle']
    img = convert_file_to_nparray(puzzle)
    
    # validate that image is compatible with downstream
    # preprocess image
    img_proc = preprocess_image(img)

    # find contours
    contours = find_contours(img_proc)

    # find outer border
    border = biggest_contour(contours)
    border = reorder(border)

    # apply perspective shift
    img_persp = perspective_warp(border, img)

    # split puzzle into cells
    cells = split_boxes(img_persp)

    # extract unsolved puzzle
    unsolved, _ = get_prediction(cells, self.model)

    # solve board
    solved = solve_board(test_puzzle)

    # overlay solution to input image
    img_mask = display_numbers(unsolved, solved, img.shape[:-1])
    img_ans = overlay_solution(img, img_mask, border, img.shape[:-1])

    # # convert from np.ndarray to jpg
    img_jpg = convert_nparray_to_jpg(img_ans)

    try:
        return HttpResponse(img_jpg, content_type="image/jpeg", status=200)
    except:
        return HttpResponse({"message":"Failed, unable convert image for response."}, status=400)

