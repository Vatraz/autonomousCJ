import cv2
import numpy as np
from PIL import ImageGrab

class ImageProcessor:
    def __init__(self, window_x, window_y):
        self.window_x = window_x
        self.window_y = window_y

    def get_image(self) -> np.ndarray:
        """
        Returns a screen fragment described by `self.window_x` and `self.window_y`.

        :return: Fragment of the screen capture
        """
        return np.array(ImageGrab.grab(bbox=(0, 30, self.window_x, self.window_y + 30)))

    @property
    def window_shape(self) -> tuple:
        return self.window_x, self.window_y

    def _region_of_interest(self, img: np.ndarray) -> np.ndarray:
        """
        Returns the image masked with ROI

        :param img: Input image
        :return: Cropped image
        """
        mask = np.zeros_like(img)
        window_x, window_y = self.window_shape

        polygon = np.array([[
            (0, window_y),
            (0, window_y * 3 / 4),
            (int(window_x * 2/5), int(window_y/2)),
            (int(window_x * 3/5), int(window_y/2)),
            (window_x, window_y * 3 / 4),
            (window_x, window_y),
        ]], np.int32)

        cv2.fillPoly(mask, polygon, 255)
        cropped_img = cv2.bitwise_and(img, mask)
        return cropped_img

    def get_lines(self, img: np.ndarray) -> np.ndarray:
        """
        Returns an array of lines found in the given image.

        :param img: Processed image
        :return: ndarray containing coordinates of found lines
        """
        prt_blur = cv2.GaussianBlur(img, (5, 5), 0)
        prt_edges = cv2.Canny(prt_blur, 50, 100)
        prt_crop = self._region_of_interest(prt_edges)
        return cv2.HoughLinesP(prt_crop, 1, np.pi / 180, 100, minLineLength=150, maxLineGap=70)

