import threading

from PIL import ImageGrab
import cv2
import numpy as np
import statistics
import time
import keyboard
import functools

from minimap import Minimap
from lanes import Lanes

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


if __name__ == '__main__':
    point = [aimX, horizonY]
    keyboard.wait('g')
    # t_forward = threading.Thread(target=accelerate_thread)
    # t_forward.start()
    #
    # t_control = threading.Thread(target=steering_thread)
    # t_control.start()
    minimap = None
    lanes = Lanes((windowX, windowY))

    while True:

        prt_scr = np.array(ImageGrab.grab(bbox=(0, 30, windowX, windowY+30)))
        if not minimap:
            minimap = Minimap(prt_scr, ((20, int(windowY * 3 / 4)), (int(windowX / 4), windowY - 20)))
            minimap.show_map(prt_scr)
        else:
            minimap.show_map(prt_scr)
            minimap.get_direction(prt_scr)

        # prt_scr = cv2.cvtColor(prt_scr, cv2.COLOR_BGR2GRAY)
        prt_blur = cv2.GaussianBlur(prt_scr, (5, 5), 0)
        prt_edges = cv2.Canny(prt_blur, 50, 100)
        prt_crop = region_of_interest(prt_edges)
        hough = cv2.HoughLinesP(prt_crop, 1, np.pi / 180, 100, minLineLength=150, maxLineGap=70)

        if type(hough) is not np.ndarray:
            continue

        lanes.find_lanes(hough)

        a_l, b_l = lanes.lane_l.a, lanes.lane_l.b
        a_r, b_r = lanes.lane_r.a, lanes.lane_r.b

        point_candidate = lanes.calculate_intersection()

        if point_candidate and point_candidate[1] < horizonY*1.5:
            point = point_candidate

        if lanes.lane_l.exist:
            if a_l < -0.65 or lanes.lane_l.calculate_intersection_Y(windowY) > 100:
                point[0] += 2*thresholdX
        if lanes.lane_r.exist:
            if a_r > 0.65 or lanes.lane_r.calculate_intersection_Y(windowY) < 700:
                point[0] -= 2*thresholdX

        offset = aimX - point[0]

        if offset > 2*thresholdX:
            direction = 'a'
            direction_pow = 2
        elif offset > thresholdX:
            direction = 'a'
            direction_pow = 1
        elif offset < -2*thresholdX:
            direction = 'd'
            direction_pow = 2
        elif offset < -thresholdX:
            direction = 'd'
            direction_pow = 1
        elif -thresholdX < offset < thresholdX:
            direction = None

        # print(offset)
        coords_l = calculate_lane_coords(a_l, b_l)
        coords_r = calculate_lane_coords( a_r, b_r)

        draw_lines(prt_scr, coords_l, coords_r, point)
        cv2.imshow("UDA CI SIE CJ", cv2.cvtColor(prt_scr, cv2.COLOR_BGR2RGB))

        if cv2.waitKey(25) & 0xFF == ord('q') or keyboard.is_pressed('u'):
            cv2.destroyAllWindows()
            break

