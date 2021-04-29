import cv2
import time
from src.controls import Controls
from src.game_window import GameWindow
from src.lane_detector import LaneDetector
from src.minimap import MiniMap
# from src.pilot import Pilot

__DEBUG_CV__ = True


class CJ:
    def __init__(self):
        # Init submodules
        self.game_window = GameWindow()
        self.minimap = MiniMap()
        self.controls = Controls()
        self.lane_detector = LaneDetector()
        # self.pilot = Pilot(self.game_window)

        # Wait for the user to press the space bar in the game menu
        self.controls.wait_for_space()

        # Find game window on screen
        self.game_window.find_game_rect()

        # Exit menu
        self.controls.exit_menu()
        time.sleep(0.3)

        # Init processing objects
        self.game_window.update_game_image()
        # -- minimap
        self.minimap.find_minimap_loc(self.game_window.screen_img_gray)
        self.minimap.update_player_loc(self.game_window.screen_img_gray, True)

        time.sleep(0.2)

        if __DEBUG_CV__:
            # cv2.imshow("ehh", self.gw.get_game_image())
            print('---------', self.minimap.player_loc)
            # cv2.waitKey(-1)

    def run(self):
        while True:
            self.game_window.update_game_image()
            self.minimap.update_player_loc(self.game_window.screen_img_gray)
            self.lane_detector.update_pos(self.game_window.screen_img_gray)

            if __DEBUG_CV__:
                cv2.waitKey(1)


if __name__ == '__main__':
    cj = CJ()
    cj.run()
