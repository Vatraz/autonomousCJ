import cv2
import time
import keyboard

from multiprocessing import Pipe, Process, connection

from image import ImageProcessor
from minimap import Minimap
from analyzer import Analyzer


def keyboard_ctrl(key, power):
    keyboard.press(key)
    time.sleep(0.01 * power)
    keyboard.release(key)
    time.sleep(0.01 * power)


def keyboard_acc(key, power):
    keyboard.press(key)
    time.sleep(0.02 * power)
    keyboard.release(key)
    time.sleep(0.01)


def keyboard_proc(conn, handler):
    """
    Supports simulation of keystrokes, depending on commands received from the connection object.

    :param conn: Connection objects that receives instruction list [key, power]
    :param handler: Performs keystrokes based on the values of the instruction list
    """
    key = None
    power = 1
    while True:
        if conn.poll():
            rcv = conn.recv()
            if rcv == 'END':
                break
            key = rcv[0]
            power = rcv[1]
        elif key:
            handler(key, power)
        else:
            time.sleep(0.01)


if __name__ == '__main__':
    windowX, windowY = 800, 600
    aimX, aimY = int(windowX / 2), int(windowY / 2)
    thresholdX = 20

    direction = None
    direction_pow = 1
    sent_key = None
    sent_pow = None

    # wait to start
    keyboard.wait('g')

    conn_ctrl_child, conn_ctrl_parent = Pipe(duplex=False)
    p_keyboard_proc = Process(target=keyboard_proc, args=(conn_ctrl_child, keyboard_ctrl))
    p_keyboard_proc.start()

    conn_acc_child, conn_acc_parent = Pipe(duplex=False)
    p_acc = Process(target=keyboard_proc, args=(conn_acc_child, keyboard_acc))
    p_acc.start()
    # TODO: add support for speed keyboard_proc
    conn_acc_parent.send(['w', 1])

    image_processor = ImageProcessor(windowX, windowY)
    minimap = Minimap(image_processor.get_image(), ((20, int(windowY * 3 / 4)), (int(windowX / 4), windowY - 20)))
    analyzer = Analyzer(image_processor, minimap, [aimX, aimY])

    while True:
        prt_scr = image_processor.get_image()
        difference = analyzer.get_distance_to_aim(prt_scr, thresholdX)

        if abs(difference) >= thresholdX:
            if difference > 0:
                direction = 'd'
            else:
                direction = 'a'
            power_sw = abs(difference)/thresholdX
            if power_sw >= 4:
                direction_pow = 2
            else:
                direction_pow = 1
        else:
            direction = None

        if sent_key != direction or sent_pow != direction_pow:
            conn_ctrl_parent.send([direction, direction_pow])
            sent_key, sent_pow = direction, direction_pow

        cv2.imshow("lanes", cv2.cvtColor(analyzer.draw(prt_scr, thresholdX), cv2.COLOR_BGR2RGB))
        cv2.imshow("map", cv2.cvtColor(minimap.draw(prt_scr), cv2.COLOR_BGR2RGB))

        if cv2.waitKey(25) & 0xFF == ord('q') or keyboard.is_pressed('u'):
            cv2.destroyAllWindows()
            conn_ctrl_parent.send('END')
            conn_acc_parent.send('END')
            if p_keyboard_proc.is_alive():
                p_keyboard_proc.join()
            if p_acc.is_alive():
                p_acc.join()
            break
