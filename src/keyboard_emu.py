import time
from pynput.keyboard import Key, Controller, Listener
from threading import Thread


class Keyboard:
    """
    Keyboard emulation
    """

    def __init__(self):
        self.controller = Controller()

    def keypress_thread(self, key, press_time):
        """
        A thread that presses a specific key for a specified amount of time.

        :param key: key value
        :param time: keypress time in seconds
        """
        self.controller.press(key)
        time.sleep(press_time)
        self.controller.release(key)

    def press_key(self, key, press_time=0.1):
        """
        Press and release a key

        :param key: key value
        :param mult: keypress time in seconds
        """
        thread = Thread(target=self.keypress_thread, args=(key, press_time))
        thread.start()

    def wait_for_key(self, key: Key):
        """
        Waits until a space bar is pressed.

        :param key: key value
        """
        def check(x):
            if x == key:
                return False

        with Listener(
                on_press=lambda x: x,
                on_release=check) as listener:
            listener.join()
