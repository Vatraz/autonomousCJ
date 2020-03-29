import time

from pynput.keyboard import Key, Controller, Listener
from threading import Thread


keyboard = Controller()
key_hold = False


def keypress_thread(key, time):
    """
    Presses the key for time described by 'time' value.

    :param key: key value
    :param time: keypress time in seconds
    """
    keyboard.press(key)
    time.sleep(time)
    keyboard.release(key)


def keyhold_thread(key):
    """
    Holds the key down as long as the global value key_hold is True.

    :param key: key value
    """
    global key_hold
    print('pressed', key, key_hold)
    keyboard.press(key)
    while key_hold:
        time.sleep(0.005)
    keyboard.release(key)
    print('released', key)


def press_key(key, mult):
    """
    Starts a thread that presses passed key for mult*0.1 seconds.

    :param key: key value
    :param mult: time multiplier
    """
    time = 0.1 * mult
    thread = Thread(target=keypress_thread, args=(key, time))
    thread.start()


def hold_key_start(key):
    """
    Starts a thread that holds the key down.

    :param key: key value
    """
    global key_hold
    key_hold = True
    thread = Thread(target=keyhold_thread, args=(key,))
    thread.start()


def hold_key_stop():
    """
    Stops the thread that holds the key down.

    :param key: key value
    """
    global key_hold
    key_hold = False


def wait_for_space():
    """
    Waits until a spacebar is pressed.
    """
    def check(x):
        if x == Key.space:
            return False

    with Listener(
            on_press=lambda x: x,
            on_release=check) as listener:
        listener.join()


def get_keymap():
    """
    Returns a dictionary with keyboard values mapped to possible moves.

    U - up, D - down, L - left, R - right

    :return: dictionary with keys mapped
    """
    return {'L':Key.left, 'R':Key.right, 'U':'u', 'D':'d'}