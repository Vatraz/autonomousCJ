from pynput.keyboard import Key, Controller
from PIL import ImageGrab
import cv2
import numpy as np
import statistics
import time
import keyboard

from lane_detector import select_lines, lane, params, calculate_intersection

kbrd = Controller()

windowX = 800
windowY = 600
horizonY = int(windowY/2)
aimX = int(windowX/2)
thresholdX = 20
old_y = 0


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



def calculate_lane_coords(a, b):
    if a == 0:
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
    #     # print("LEFT", coords)
    # for line in lines_r:
    #     coords = line[0]
    #     # cv2.line(image, (coords[0], coords[1]), (coords[2], coords[3]), [255, 0, 0], 3)
    #     # print("RIGHT", coords)

    coords_l = lane_l_coords
    cv2.line(image, (coords_l[0], coords_l[1]), (coords_l[2], coords_l[3]), [0, 225, 0], 3)

    coords_r = lane_r_coords
    cv2.line(image, (coords_r[0], coords_r[1]), (coords_r[2], coords_r[3]), [255, 0, 0], 3)


    cv2.line(image, (aimX, point[1]), (point[0], point[1]), [0, 0, 225], 3)




if __name__ == '__main__':
    point = [0, 0]
    keyboard.wait('g')
    while True:
        # keypress()
        # if keyboard.read_key() == 'p':
        #     break
        prt_scr = np.array(ImageGrab.grab(bbox=(0, 0, 800, 600)))
        # prt_scr = cv2.cvtColor(prt_scr, cv2.COLOR_BGR2GRAY)
        prt_blur = cv2.GaussianBlur(prt_scr, (5, 5), 0)

        prt_edges = cv2.Canny(prt_blur, 50, 100)
        # CROP ROI
        prt_crop = region_of_interest(prt_edges)
        # HOUGH
        hough = cv2.HoughLinesP(prt_crop, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=50)

        if type(hough) is not np.ndarray:
            continue

        lines_l, lines_r = select_lines(hough)
        lane_l = lane(lines_l)
        lane_r = lane(lines_r)
        point = calculate_intersection(lane_l['a'], lane_l['b'], lane_r['a'], lane_r['b'], point[1]) or point

        coords_l = calculate_lane_coords(lane_l['a'], lane_l['b'])
        coords_r = calculate_lane_coords( lane_r['a'], lane_r['b'])
        old_y = point[1]

        offset = aimX - point[0] if point[0] != 0 else 0
        kbrd.press('w')
        if offset > thresholdX:
            kbrd.release(Key.right)
            kbrd.press(Key.left)
        if offset < -thresholdX:
            kbrd.release(Key.left)
            kbrd.press(Key.right)
        print(offset)

        draw_lines(prt_scr, coords_l, coords_r, point)

        cv2.imshow("GTA SA UDA CI SIE CJ", cv2.cvtColor(prt_scr, cv2.COLOR_BGR2RGB))

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

