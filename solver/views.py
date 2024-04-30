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

  def post(self, request):
    try:
       
      # get image from request
      if 'puzzle' not in request.FILES:
              return HttpResponse({"message": "Puzzle file not supplied", "error":"User must supply image of unsolved sudoku puzzle."}, status=400)
      
      puzzle = request.FILES['puzzle']
      
      # convert image into nparray
      try:
          img = convert_file_to_nparray(puzzle)
      except Exception as e:
          return HttpResponse({"message": "Failed to convert file to numpy array", "error": str(e)}, status=400)
      
      # preprocess image
      try:
          img_proc = preprocess_image(img)
      except Exception as e:
          return HttpResponse({"message": "Failed to preprocess image", "error": str(e)}, status=400)
            

      # find contours
      contours = find_contours(img_proc)

      # find outer border
      border = biggest_contour(contours)
      border = reorder(border)

      # # apply perspective shift
      img_persp = perspective_warp(border, img)

      # # split puzzle into cells
      cells = split_boxes(img_persp)

      # # extract unsolved puzzle
      # TODO: if predictions cannot be made
      unsolved, _ = get_prediction(cells, self.model)

      # # solve board
      # TODO: if solution cannot be made
      solved = solve_board(test_puzzle)

      # overlay solution to input image
      # TODO: solution cannot be overlayed or converted to return image
      img_mask = display_numbers(unsolved, solved, img.shape[:-1])
      img_ans = overlay_solution(img, img_mask, border, img.shape[:-1])

      # convert from np.ndarray to jpg
      try:
          img_jpg = convert_nparray_to_jpg(img_ans)
      except Exception as e:
          return HttpResponse({"message": "Failed to convert image to JPEG", "error": str(e)}, status=400)
            
      return HttpResponse(img_jpg, content_type="image/jpeg", status=200)
    except Exception as e:
        return HttpResponse({"message": "An unexpected error occurred", "error": str(e)}, status=500)

