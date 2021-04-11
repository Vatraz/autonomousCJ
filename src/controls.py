from src.joypad_emu import JoyPad
from src.keyboard_emu import Keyboard, Key


class Controls:
    """
    Game control interface
    """
    def __init__(self):
        self.keyboard = Keyboard()
        self.joypad = JoyPad()
        pass

    def wait_for_space(self):
        """
        Waits until a space bar is pressed.
        """
        self.keyboard.wait_for_key(Key.space)

    def exit_menu(self):
        """
        Exits the game menu (ESC)
        """
        self.keyboard.press_key(Key.esc)
