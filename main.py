from pynput.keyboard import Key, Controller
from PIL import ImageGrab
import cv2
import numpy as np
import statistics
import time

keyboard = Controller()

windowX = 800
windowY = 600
horizonY = windowY/2

def region_of_interest(edges):
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # only focus bottom half of the screen
    polygon = np.array([[
        (0, windowY),
        (0, windowY * 3 / 4),
        # (width * 1/8, height * 1 / 2),
        (windowX / 2, horizonY),
        (windowX, windowY * 3 / 4),
        (windowX, windowY),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    return cropped_edges

def keypress():
    keyboard.press('a')
    time.sleep(0.01)
    keyboard.release('a')


def params(x1, y1, x2, y2):
    y1 = windowY - y1
    y2 = windowY - y2

    # Slope
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0:
        dx = 1 # 1px

    slope = dy/dx

    # Interception
    interception = y1 - slope*x1

    return slope, interception


def select_lines(lines):
    slope_min = 0.2
    selected_left = []
    selected_right = []

    for line in lines:
        coords = line[0]
        slope, _ = params(*coords)

        if slope > slope_min:
            selected_left.append(line)
        elif slope < -slope_min:
            # print(slope)
            selected_right.append(line)

    return selected_left, selected_right


def calculate_lane(lines):
    if not lines:
        return [0, 0, 0, 0]
    slopes = []
    interceptions = []
    for line in lines:
        slope, interception = params(*line[0])
        slopes.append(slope)
        interceptions.append(interception)
    a = statistics.mean(slopes)
    b = statistics.mean(interceptions)
    y1 = int(windowY - horizonY)
    x1 = int((y1 - b)/a)
    y2 = 0
    x2 = int((y2 - b)/a)

    coords = [x1, windowY-y1, x2, windowY-y2]
    return coords

def draw_lines(image, hough):
    # try:
    #     for line in hough:
    #         print(line)
    #         print(params(*line[0])[0])
    #         coords = line[0]
    #         cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [255,225,3], 3)
    # except:
    #     pass
    if type(hough) is not np.ndarray:
        return
    lines_l, lines_r = select_lines(hough)
    for line in lines_l:
        coords = line[0]
        # cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [0, 225, 0], 3)
        # print("LEFT", coords)
    for line in lines_r:
        coords = line[0]
        # cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [255, 0, 0], 3)
        # print("RIGHT", coords)

    coords = calculate_lane(lines_l)
    cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [0, 225, 0], 3)

    coords = calculate_lane(lines_r)
    cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [255, 0, 0], 3)


time_last = time.time()
while True:
    # keypress()

    prt_scr = np.array(ImageGrab.grab(bbox=(0, 0, 800, 600)))
    # prt_scr = cv2.cvtColor(prt_scr, cv2.COLOR_BGR2GRAY)
    prt_scr = cv2.GaussianBlur(prt_scr, (5, 5), 0)

    # print("took ", time.time() - time_last)
    # time_last = time.time()

    prt_edges = cv2.Canny(prt_scr, 50, 100)

    # CROP
    prt_crop = region_of_interest(prt_edges)

    # HOUGH
    hough = cv2.HoughLinesP(prt_crop, 1, np.pi / 180, 100, minLineLength=200, maxLineGap=50)
    draw_lines(prt_scr, hough)

    cv2.imshow("GTA SA UDA CI SIE CJ", cv2.cvtColor(prt_scr, cv2.COLOR_BGR2RGB))

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

