import threading

from PIL import ImageGrab
import cv2
import numpy as np
import statistics
import time
import keyboard
import functools

from multiprocessing import Pipe, Process

from minimap import Minimap
from lanes import Lanes

windowX = 800
windowY = 600
horizonY = int(windowY/2)
aimX = int(windowX/2)
thresholdX = 20

forward = 'w'



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


def draw_lines(image, lane_l_coords, lane_r_coords, difference, y):
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


    cv2.line(image, (aimX, y), (aimX+difference, y), [0, 0, 225], 3)


def accelerate_thread():
    while True:
        key = forward
        keyboard.press(key)
        time.sleep(0.02)
        keyboard.release(key)
        time.sleep(0.01)


def control_thread():
    t = time.time()
    while True:
        key = direction
        if not key:
            time.sleep(0.01)
            continue
        keyboard.press(key)
        time.sleep(0.01*direction_pow)
        keyboard.release(key)
        time.sleep(0.02)
        print(time.time() - t)
        t = time.time()

def test(conn):
    # time.sleep(1)
    key = None
    pow = 1
    # t = time.time()
    while True:
        if conn.poll():
            rcv = conn.recv()
            key = rcv[0]
            pow = rcv[1]
        elif key:
            keyboard.press(key)
            time.sleep(0.01 * pow)
            keyboard.release(key)
            time.sleep(0.01)
        else:
            time.sleep(0.01)
        # # keyboard.press('a')
        # time.sleep(0.01)
        # # keyboard.release('a')
        # tt = time.time()
        # # print(tt - t)
        # t = time.time()


if __name__ == '__main__':
    point_zero = [aimX, horizonY]
    point = point_zero
    direction = None
    direction_pow = 1

    keyboard.wait('g')
    # t_forward = threading.Thread(target=accelerate_thread)
    # t_forward.start()

    # t_control = threading.Thread(target=control_thread)
    # t_control.start()

    conn_child, conn_parent = Pipe(duplex=False)
    t_control = threading.Thread(target=test, args=(conn_child,))
    t_control.start()


    print('hihi')

    minimap = None
    lanes = Lanes((windowX, windowY))
    minimap_control = False
    minimap_dif = 0

    sent_key = None
    sent_pow = None

    while True:

        prt_scr = np.array(ImageGrab.grab(bbox=(0, 30, windowX, windowY+30)))
        if not minimap:
            minimap = Minimap(prt_scr, ((20, int(windowY * 3 / 4)), (int(windowX / 4), windowY - 20)))
            minimap.draw(prt_scr)
        else:
            minimap.draw(prt_scr)
            minimap.get_direction(prt_scr)

        # prt_scr = cv2.cvtColor(prt_scr, cv2.COLOR_BGR2GRAY)
        prt_blur = cv2.GaussianBlur(prt_scr, (5, 5), 0)
        prt_edges = cv2.Canny(prt_blur, 50, 100)
        prt_crop = region_of_interest(prt_edges)
        hough = cv2.HoughLinesP(prt_crop, 1, np.pi / 180, 100, minLineLength=150, maxLineGap=70)

        if type(hough) is not np.ndarray:
            cv2.imshow("UDA CI SIE CJ", cv2.cvtColor(prt_scr, cv2.COLOR_BGR2RGB))
            continue

        lanes.update_lanes(hough)
        lane_l, lane_r = lanes.get_lanes()

        point_candidate = lanes.calculate_intersection()

        if point_candidate and point_candidate[1] < int(horizonY*1.2) \
                and point_candidate:
            point = point_candidate
        else:
            pass
            # point = point_zero


        minimap_direction = minimap.get_direction(prt_scr)
        difference = point[0] - aimX

        if lane_l.exist():
            if lane_l.a < -0.65 or lane_l.calculate_intersection_y(windowY) > 0:
                print('korekto -> R', time.time())
                if lane_r.exist():
                    difference += thresholdX
                else:
                    difference = thresholdX
        if lane_r.exist():
            if lane_r.a > 0.65 or lane_r.calculate_intersection_y(windowY) < windowX:
                print('korekto <- L', time.time())
                if lane_l.exist():
                    difference -= thresholdX
                else:
                    difference = -thresholdX

        if lane_l.exist() and lane_r.exist() and lane_r.calculate_intersection_x(windowX) < int(windowY*7/8):
            print('L - b too small')
            difference = 0
        if lane_r.exist() and lane_l.exist()and lane_r.calculate_intersection_x(0) < int(windowY*7/8):
            print('R - b too small')
            difference = 0

        # if T junction
        if not (lane_l.exist() or lane_r.exist()) and not minimap_direction[1]:
            # print("PROBLEM", time.time()  )
            if not minimap_control:
                if not (minimap_direction[0] or minimap_direction[1]):
                    pass
                elif minimap_direction[0]:
                    minimap_dif = -1*thresholdX
                    minimap_control = True
                elif minimap_direction[2]:
                    minimap_dif = 3*thresholdX
                    minimap_control = True

        if minimap_control:
            print('MAP', time.time())
            if not (lane_l.exist() or lane_r.exist()):
                difference = minimap_dif
            elif minimap_direction[2] or (lane_l.exist() and lane_r.exist()):
                difference = 0
                minimap_control = False
                point = [aimX, horizonY]

        if abs(difference) >= thresholdX:
            if difference > 0:
                direction = 'd'
            else:
                direction = 'a'
            power_sw = abs(difference)/thresholdX
            if power_sw >= 4:
                direction_pow = 2
            else:
                direction_pow =1
        else:
            direction = None

        if sent_key != direction or sent_pow != direction_pow:
            conn_parent.send([direction, direction_pow])
            sent_key, sent_pow = direction, direction_pow

        # print(difference)
        coords_l = lane_l.calculate_coords(windowY, horizonY)
        coords_r = lane_r.calculate_coords(windowY, horizonY)

        draw_lines(prt_scr, coords_l, coords_r, difference, point[1])
        cv2.imshow("UDA CI SIE CJ", cv2.cvtColor(prt_scr, cv2.COLOR_BGR2RGB))

        if cv2.waitKey(25) & 0xFF == ord('q') or keyboard.is_pressed('u'):
            cv2.destroyAllWindows()
            break

