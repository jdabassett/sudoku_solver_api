import copy
import cv2
from keras.models import load_model, Model
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image
import tensorflow as tf
from typing import List, Tuple

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

########################################################################
img_height = 450
img_width = 450
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "solver/model_trained_10_3.keras")
########################################################################


# find biggest contour
def biggest_contour(contours: List[np.ndarray]) -> np.ndarray:
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 50:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest


# convert file into numpy array
def convert_file_to_nparray(file) -> np.ndarray:
    return cv2.imdecode(np.frombuffer(file, np.uint8), cv2.IMREAD_COLOR)


# convert image from numpy array into jpg
def convert_nparray_to_jpg(input: np.ndarray):
    return cv2.imencode(".jpg", input)[1].tobytes()


# display solution on puzzle
def display_numbers(
    puzzle: List[List[int]],
    solution: List[List[int]],
    original_size: Tuple[int],
    color: List[int] = (0, 255, 0),
) -> np.ndarray:
    temp = np.zeros((img_height, img_width, 3), np.uint8)
    width = int(temp.shape[1] / 9)
    height = int(temp.shape[0] / 9)
    for x in range(0, 9):
        for y in range(0, 9):
            prev = puzzle[y][x]
            if prev == 0:
                val = str(solution[y][x])
                cv2.putText(
                    temp,
                    val,
                    (x * width + int(width / 2) - 10, int((y + 0.8) * height)),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL,
                    2,
                    color,
                    2,
                    cv2.LINE_AA,
                )
    temp = cv2.resize(temp, original_size)
    return temp


# find contours
def find_contours(img: np.ndarray) -> List[np.ndarray]:
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


# predict value of each cell
def get_prediction(boxes: List[np.ndarray], model: Model) -> List[int]:
    result_lst = [[] for _ in range(9)]
    cells = []
    tf.get_logger().setLevel('ERROR')
    for idx, image in enumerate(boxes):
        img = np.asarray(image)
        height, width = img.shape[0], img.shape[1]
        h_ten, w_ten = height // 7, width // 7
        img = img[h_ten : height - h_ten, w_ten : width - w_ten]
        img = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 5
        )
        img = cv2.resize(img, (32, 32))
        img = img / 255
        cells.append(img)
        img = img.reshape(1, 32, 32, 1)
        # pred = model.predict(img)
        with tf.device('/cpu:0'): 
            pred = model.predict(img, verbose=0)
        prob_idx = np.argmax(pred, axis=1)
        prob_hgh = pred[0, prob_idx][0]
        row = idx // 9
        if prob_hgh > 0.8:
            result_lst[row].append(int(prob_idx[0] + 1))
        else:
            result_lst[row].append(0)
    return result_lst, cells


# create model
def initialize_prediction_model() -> Model:
    return load_model(model_path)


# overlay solution
def overlay_solution(
    original: np.ndarray,
    mask: np.ndarray,
    border: List[np.ndarray],
    original_size: List[int],
) -> np.ndarray:
    orig_width, orig_height = original_size
    temp_mask = copy.deepcopy(mask)
    temp_orig = copy.deepcopy(original)
    pts2 = np.float32(border)
    pts1 = np.float32(
        [[0, 0], [orig_width, 0], [0, orig_height], [orig_width, orig_height]]
    )
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    temp_mask = cv2.warpPerspective(temp_mask, matrix, (orig_height, orig_width))
    img_ans = cv2.addWeighted(temp_mask, 1, temp_orig, 0.6, 1)
    return img_ans


# apply perspective warp
def perspective_warp(biggest: List[np.ndarray], img: np.ndarray) -> np.ndarray:
    temp = copy.deepcopy(img)
    # make transformation matrix
    pts1 = np.float32(biggest)
    pts2 = np.float32(
        [[0, 0], [img_width, 0], [0, img_height], [img_width, img_height]]
    )
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    # apply perspective shift
    temp = cv2.warpPerspective(temp, matrix, (img_width, img_height))
    temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
    return temp


# plot cells for testing purposes
def plot_cells(cells: List[np.ndarray]) -> None:
    plt.figure(figsize=(12, 12))

    for i in range(0, 81):
        plt.subplot(9, 9, i + 1)
        plt.axis("off")
        plt.imshow(cells[i], cmap="gray")

    plt.show()


# preprocessing image
def preprocess_image(img: np.ndarray) -> np.ndarray:
    # temp = cv2.resize(img, (img_width, img_height))
    temp = copy.deepcopy(img)
    temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
    temp = cv2.GaussianBlur(temp, (5, 5), 1)
    temp = cv2.adaptiveThreshold(temp, 255, 1, 1, 11, 2)
    return temp


# reorder points for Warp Perspective
def reorder(points: List[np.ndarray]) -> List[np.ndarray]:
    points = points.reshape((4, 2))
    points_new = np.zeros((4, 1, 2), dtype=np.int32)
    add = points.sum(1)
    points_new[0] = points[np.argmin(add)]
    points_new[3] = points[np.argmax(add)]
    diff = np.diff(points, axis=1)
    points_new[1] = points[np.argmin(diff)]
    points_new[2] = points[np.argmax(diff)]
    return points_new


# split image into 81 cells
def split_boxes(img: np.ndarray) -> List[np.ndarray]:
    rows = np.vsplit(img, 9)
    boxes = []
    for r in rows:
        cols = np.hsplit(r, 9)
        for box in cols:
            boxes.append(box)
    return boxes


# def main():
#     model = initialize_prediction_model()
#     img = cv2.imread("./data/unsolved/3.jpg")
#     img_proc = preprocess_image(img)
#     # find contours
#     contours = find_contours(img_proc)
#     # find outer border
#     border = biggest_contour(contours)
#     border = reorder(border)
#     # apply perspective shift
#     img_persp = perspective_warp(border, img)
#     # split puzzle into cells
#     cells = split_boxes(img_persp)
#     # extract unsolved puzzle
#     unsolved, cells = get_prediction(cells, model)

#     for row in unsolved:
#       print(row)

#     plot_cells(cells)
