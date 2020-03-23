import cv2
import time

from pynput.keyboard import Key, Controller, Listener
from threading import Thread


from process_image.image import ImageProcessor
from process_image.minimap import Minimap
from analyzer import Analyzer


keyboard = Controller()
key_hold = False


def press_thread(key, power):
    keyboard.press(key)
    time.sleep(power*0.1)
    keyboard.release(key)


def hold_thread(key):
    global key_hold
    print('pressed', key, key_hold)
    keyboard.press(key)
    while key_hold:
        time.sleep(0.005)
    keyboard.release(key)
    print('released', key)


def press_key(key, power):
    thread = Thread(target=press_thread, args=(key, power))
    thread.start()
    

def hold_key(key):
    global key_hold
    key_hold = True
    thread = Thread(target=hold_thread, args=(key, ))
    thread.start()


if __name__ == '__main__':
    window_x, window_y = 800, 600
    aimX, aimY = int(window_x / 2), int(window_y / 2)
    threshold_x = 20

    direction = None
    direction_pow = 1

    direction_prev = None

    # wait to start
    with Listener(
            on_press=lambda x: x,
            on_release=lambda x: False) as listener:
        listener.join()

    # TODO: add support for speed keyboard_proc
    image_processor = ImageProcessor(window_x, window_y)
    minimap = Minimap(image_processor.get_image(), ((20, int(window_y * 3 / 4)), (int(window_x / 4), window_y - 20)))
    analyzer = Analyzer(image_processor, minimap, [aimX, aimY])

    while True:
        prt_scr = image_processor.get_image()
        difference = analyzer.get_distance_to_aim(prt_scr, threshold_x)

        if abs(difference) >= threshold_x:
            if difference > 0:
                direction = 'd'
            else:
                direction = 'a'
            power_sw = abs(difference)/threshold_x
            if power_sw >= 8:
                direction_pow = 4
            elif power_sw >= 5:
                direction_pow = 3
            elif power_sw >= 3:
                direction_pow = 2
            else:
                direction_pow = 1
        else:
            direction = None
            direction_pow = 1

        if direction_pow != 4 or direction != direction_prev:
            key_hold = False
            direction_prev = None
        if direction and direction_pow != 4:
            press_key(direction, direction_pow)
        elif direction and direction_prev != direction and direction_pow == 4:
            direction_prev = direction
            arrow = Key.left if direction == 'a' else Key.right
            hold_key(arrow)

        cv2.imshow("lanes", cv2.cvtColor(analyzer.draw(prt_scr, threshold_x), cv2.COLOR_BGR2RGB))
        cv2.imshow("map", cv2.cvtColor(minimap.draw(prt_scr), cv2.COLOR_BGR2RGB))

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            # if p_keyboard_proc.is_alive():
            #     p_keyboard_proc.join()
            # if p_acc.is_alive():
            #     p_acc.join()
            break