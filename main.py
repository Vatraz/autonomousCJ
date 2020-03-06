import threading

from PIL import ImageGrab
import cv2
import numpy as np
import statistics
import time
import keyboard
import functools


from lane_detector import filter_lines, lane, params, calculate_lanes_intersection, calculate_intersection_Y

windowX = 800
windowY = 600
horizonY = int(windowY/2)
aimX = int(windowX/2)
thresholdX = 20

forward = 'w'
direction = None
direction_pow = 1

def region_of_interest(edges):
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


def calculate_lane_coords(a, b):
    if not a or not b:
        return [0,0,0,0]
    y1 = int(windowY - horizonY)
    x1 = int((y1 - b)/a)
    y2 = windowY
    x2 = int((y2 - b)/a)

    return [x1, y1, x2, y2]

def draw_lines(image, lane_l_coords, lane_r_coords, point):
    cv2.line(image, (int(windowX/2), 0), (int(aimX), windowY), [255, 125, 0], 2)
    cv2.line(image, (int(aimX + thresholdX), 0), (int(aimX + thresholdX), windowY), [255, 0, 220], 1)
    cv2.line(image, (int(aimX - thresholdX), 0), (int(aimX - thresholdX), windowY), [255, 0, 220], 1)

    # try:
    #     for line in hough:
    #         print(line)
    #         print(params(*line[0])[0])
    #         coords = line[0]
    #         cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [255,225,3], 3)
    # except:
    #     pass


    # for line in lines_l:
    #     coords = line[0]
    #     # cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [0, 225, 0], 3)
    #     # print("LEFT", coords)dwd
    # for line in lines_r:
    #     coords = line[0]
    #     # cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [255, 0, 0], 3)
    #     # print("RIGHT", coords)

    coords_l = lane_l_coords
    cv2.line(image, (coords_l[0], coords_l[1]), (coords_l[2], coords_l[3]), [0, 225, 0], 5)

    coords_r = lane_r_coords
    cv2.line(image, (coords_r[0], coords_r[1]), (coords_r[2], coords_r[3]), [255, 0, 0], 5)


    cv2.line(image, (aimX, point[1]), (point[0], point[1]), [0, 0, 225], 3)


def accelerate_thread():
    while True:
        key = forward
        keyboard.press(key)
        time.sleep(0.02)
        keyboard.release(key)
        time.sleep(0.02)


def control_thread():
    while True:
        key = direction
        if not key:
            time.sleep(0.01)
            continue
        keyboard.press(key)
        time.sleep(0.02)
        keyboard.release(key)
        time.sleep(0.04/direction_pow)


def find_map(image):
    image = image[int(windowY*3/4):windowY-20, 20:int(windowX/4)]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, 5)
    gray_blur = cv2.medianBlur(gray_blur, 5)
    _, thresh_blur = cv2.threshold(gray_blur, 2, 255, cv2.THRESH_BINARY_INV)

    top = bottom = None
    left = windowX
    right = 0

    for num, row in enumerate(thresh_blur):
        non_zeros = np.nonzero(row != 0)
        if non_zeros[0].size == 0:
            continue
        if not top:
            top = num

        bottom = num
        left = left if left < non_zeros[0][0] else non_zeros[0][0]
        right = right if right > non_zeros[0][-1] else non_zeros[0][-1]




    # gray = cv2.medianBlur(gray, 5)
    # gray = cv2.medianBlur(gray, 5)
    # gray = cv2.Canny(gray, 50, 100)


    ret, thresh = cv2.threshold(gray_blur, 2, 255, cv2.THRESH_BINARY_INV)

    # circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT,1,20, param1=50,param2=30,minRadius=20,maxRadius=100)
    #
    # # # ensure at least some circles were found
    # if circles is not None:
    #     # convert the (x, y) coordinates and radius of the circles to integers
    #     circles = np.round(circles[0, :]).astype("int")
    #     # loop over the (x, y) coordinates and radius of the circles
    #     (x, y, r) = functools.reduce(lambda a, b: a if a[2] > b[2] else b, circles)
    #
    #         # corresponding to the center of the circle
    #     cv2.circle(gray, (x, y), r, 100, 4)
    #     cv2.rectangle(gray, (x - 5, y - 5), (x + 5, y + 5), 100, -1)
    x, y = left + int((right - left)/2), top + int((bottom - top)/2)
    print(x, '____', y)
    cv2.rectangle(thresh, (x - 5, y - 5), (x + 5, y + 5), 100, -1)

    return thresh


if __name__ == '__main__':
    point = [aimX, horizonY]
    keyboard.wait('g')
    # t_forward = threading.Thread(target=accelerate_thread)
    # t_forward.start()
    #
    # t_control = threading.Thread(target=steering_thread)
    # t_control.start()
    while True:

        prt_scr = np.array(ImageGrab.grab(bbox=(0, 30, windowX, 30+windowY)))
        # prt_scr = cv2.cvtColor(prt_scr, cv2.COLOR_BGR2GRAY)
        # prt_blur = cv2.GaussianBlur(prt_scr, (5, 5), 0)
        #
        # prt_edges = cv2.Canny(prt_blur, 50, 100)
        # # CROP ROI
        # prt_crop = region_of_interest(prt_edges)
        # # HOUGH
        # hough = cv2.HoughLinesP(prt_crop, 1, np.pi / 180, 100, minLineLength=150, maxLineGap=70)

        # if type(hough) is not np.ndarray:
        #     continue
        #
        # lines_l, lines_r = filter_lines(hough)
        # lane_l = lane(lines_l)
        # lane_r = lane(lines_r)
        # a_l, b_l = lane_l['a'], lane_l['b']
        # a_r, b_r = lane_r['a'], lane_r['b']
        #
        # if a_r and a_l and abs(calculate_intersection_Y(a_r, b_r, windowY)
        #                        - calculate_intersection_Y(a_l, b_l, windowY)) < windowX / 2:
        #     a_r = a_l = b_l = b_r = None
        #
        # point_candidate = calculate_lanes_intersection(a_l, b_l, a_r, b_r, point[1])
        # if point_candidate and point_candidate[1] < horizonY*1.5:
        #     point = point_candidate
        #
        # if a_l:
        #     if a_l < -0.65 or calculate_intersection_Y(a_l, b_l, windowY) > 100:
        #         point[0] += 2*thresholdX
        # if a_r:
        #     if a_r > 0.65 or calculate_intersection_Y(a_r, b_r, windowY) < 700:
        #         point[0] -= 2*thresholdX
        #
        # offset = aimX - point[0]
        #
        # if offset > 2*thresholdX:
        #     direction = 'a'
        #     direction_pow = 2
        # elif offset > thresholdX:
        #     direction = 'a'
        #     direction_pow = 1
        # elif offset < -2*thresholdX:
        #     direction = 'd'
        #     direction_pow = 2
        # elif offset < -thresholdX:
        #     direction = 'd'
        #     direction_pow = 1
        # elif -thresholdX < offset < thresholdX:
        #     direction = None
        #
        # # print(offset)
        # coords_l = calculate_lane_coords(a_l, b_l)
        # coords_r = calculate_lane_coords( a_r, b_r)
        #
        # draw_lines(prt_scr, coords_l, coords_r, point)
        img = find_map(prt_scr)
        cv2.imshow("UDA CI SIE CJ", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        if cv2.waitKey(25) & 0xFF == ord('q') or keyboard.is_pressed('u'):
            cv2.destroyAllWindows()
            break

