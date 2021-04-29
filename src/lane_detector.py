import cv2
import numpy as np


__DEBUG__ = True

class LaneDetector:
    def __init__(self):
        """
        Initializes the lane detector
        """
        self.lanes_positions = []
        self.roi_line_mask = None

    def setup(self, game_image: np.ndarray):
        """
        Setup lane detector

        :param game_image: The game image
        """
        self.initialize_roi(game_image.shape[:2])

    def initialize_roi(self, window_shape: tuple):
        """
        Initializes the region of interest for lane datection

        :param window_shape: Shape of the game window (h, w)
        """
        mask = np.zeros(window_shape, dtype=np.uint8)
        window_y, window_x = window_shape

        polygon = np.array([[
            (0, window_y),
            (0, window_y * 3 / 4),
            (int(window_x * 2/5), int(window_y/2)),
            (int(window_x * 3/5), int(window_y/2)),
            (window_x, window_y * 3 / 4),
            (window_x, window_y),
        ]], np.int32)

        cv2.fillPoly(mask, polygon, 255)
        self.roi_line_mask = mask

    def update_lanes(self, game_image_gray: np.ndarray):
        """
        Search for road lanes on the game image.

        :param game_image_gray: Game window image in gray scale
        """

        prt_blur = cv2.GaussianBlur(game_image_gray, (5, 5), 0)
        prt_edges = cv2.Canny(prt_blur, 50, 100)
        cropped_img = cv2.bitwise_and(prt_edges, self.roi_line_mask)
        lines = cv2.HoughLinesP(cropped_img, 1, np.pi / 180, 100, minLineLength=150, maxLineGap=70)



    # def