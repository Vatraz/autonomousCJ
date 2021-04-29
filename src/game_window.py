import cv2
import numpy as np
from PIL import ImageGrab
import typing
import wmctrl
import win32gui


class GameWindow:
    """
    Game window image processing
    """
    def __init__(self):
        """
        Constructor. Finds hwnd of the game window.
        """
        self.gta_window = self.find_game_window()

        # Last window image
        self.screen_img = None
        self.screen_img_gray = None

    def win_enum_handler(self, hwnd, ctx: list) -> int:
        """
        Handler for win32gui EnumWindows method. Appends dictionary containing the hwnd and the name of
        window described by hwnd to ctx list.

        :param hwnd: handle to a window
        :param ctx: updated context
        """
        if win32gui.IsWindowVisible(hwnd):
            ctx.append({'hwnd': hwnd, 'name':win32gui.GetWindowText(hwnd)})
        return 1

    def find_game_window(self) -> dict:
        """
        Find params of the window with GTA: San Andreas

        :return: {hwnd: window hwnd, name: window name}
        """
        windows = []
        win32gui.EnumWindows(self.win_enum_handler, windows)

        gta_window = None
        for window in windows:
            if window['name'].startswith('GTA: San Andreas'):
                gta_window = window
                break

        if gta_window is None:
            raise Exception('Could not find GTA: San Andreas window :(')

        return gta_window

    def find_game_rect(self) -> np.ndarray:
        """
        Find and update the rectangle that describes the game window area on the screen.
        To work properly, GTA menu must be active.

        :return: rectangle coords array - [x1, y1, x2, y2]
        """
        screen_image = self.take_screenshot()
        window_rect = np.array(win32gui.GetWindowRect(self.gta_window['hwnd']))

        # crop window area from the full screenshot image
        window_rect = window_rect.clip(min=0)
        cropped = screen_image[window_rect[1]:window_rect[3], window_rect[0]:window_rect[2], :]

        # filter black color of the menu and find final game window coords
        thresh = cv2.inRange(cropped, 0, 10)
        edges = cv2.Canny(thresh, 50, 200, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, maxLineGap=5, minLineLength=200)
        win_range = [window_rect[0] + min(lines[:,0,0]),
                     window_rect[1] + min(lines[:, 0, 1]),
                     window_rect[0] + max(lines[:, 0, 2]),
                     window_rect[1] + max(lines[:, 0, 3])]

        self.game_rect = np.array(win_range)
        return self.game_rect

    @staticmethod
    def take_screenshot() -> np.ndarray:
        """
        Returns full screenshot image

        :return: Screenshot image
        """
        return np.array(ImageGrab.grab())

    def update_game_image(self) -> typing.Tuple[np.ndarray, np.ndarray]:
        """
        Updates and returns an image of the fragment of the screen that contains the game window

        :return: Game window image in RGB and Gray scale
        """
        screen_image = self.take_screenshot()
        self.screen_img = screen_image[self.game_rect[1]:self.game_rect[3], self.game_rect[0]:self.game_rect[2], :]
        self.screen_img_gray = cv2.cvtColor(self.screen_img, cv2.COLOR_RGB2GRAY)
        return self.screen_img, self.screen_img_gray


if __name__ == '__main__':
    gw = GameWindow()
    win_range = gw.find_game_rect()
    screen_image = gw.take_screenshot()
    cropped = screen_image[win_range[1]:win_range[3], win_range[0]:win_range[2], :]
    cv2.imshow('hihi', cropped); cv2.waitKey(-1)
