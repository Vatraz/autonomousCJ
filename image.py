import cv2
import numpy as np
from PIL import ImageGrab

class ImageProcessor:
    def __init__(self, windowX, windowY):
        self.windowX = windowX
        self.windowY = windowY

    def get_image(self):
        return np.array(ImageGrab.grab(bbox=(0, 30, self.windowX, self.windowY + 30)))

    @property
    def window_shape(self):
        return self.windowX, self.windowY

    def _region_of_interest(self, edges):
        mask = np.zeros_like(edges)
        windowX, windowY = self.window_shape

        polygon = np.array([[
            (0, windowY),
            (0, windowY * 3 / 4),
            (windowX / 2, int(windowY/2)),
            (windowX, windowY * 3 / 4),
            (windowX, windowY),
        ]], np.int32)

        cv2.fillPoly(mask, polygon, 255)
        cropped_edges = cv2.bitwise_and(edges, mask)
        return cropped_edges

    def get_lines(self, img):
        prt_blur = cv2.GaussianBlur(img, (5, 5), 0)
        prt_edges = cv2.Canny(prt_blur, 50, 100)
        prt_crop = self._region_of_interest(prt_edges)
        return cv2.HoughLinesP(prt_crop, 1, np.pi / 180, 100, minLineLength=150, maxLineGap=70)

