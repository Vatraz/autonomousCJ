import cv2
import numpy as np


class Minimap:
    def __init__(self, image, rectangle):
        self.rectangle = rectangle
        img = image.copy()
        img = self.img_crop(img)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(img_gray, 5)
        gray_blur = cv2.medianBlur(gray_blur, 5)
        gray_blur = cv2.medianBlur(gray_blur, 5)

        _, thresh_blur = cv2.threshold(gray_blur, 2, 255, cv2.THRESH_BINARY_INV)

        self.top = self.bottom = None
        self.left = rectangle[1][0]
        self.right = 0

        for num, row in enumerate(thresh_blur):
            non_zeros = np.nonzero(row != 0)[0]
            if non_zeros.size == 0:
                continue
            if not self.top:
                self.top = num

            self.bottom = num
            self.left = self.left if self.left < non_zeros[0] else non_zeros[0]
            self.right = self.right if self.right > non_zeros[-1] else non_zeros[-1]

        self.x = self.left + int((self.right - self.left) / 2)
        self.y = self.top + int((self.bottom - self.top) / 2)
        # ret, thresh = cv2.threshold(gray_blur, 2, 255, cv2.THRESH_BINARY_INV)

    def get_direction(self, image):
        img_cropped = self.img_crop(image)
        img_map = self.process_image(img_cropped)

        up = bool(img_map[ self.y - 10, self.x])
        left = bool(np.nonzero(img_map[self.y-5:self.y+5, self.x-10])[0].size)
        right = bool(np.nonzero(img_map[self.y-5:self.y+5, self.x+10])[0].size)

        return (left, up, right)

    @staticmethod
    def process_image(img_cropped):
        img_gray = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(img_gray, 10, 255, cv2.THRESH_BINARY_INV)
        return thresh

    def img_crop(self, image):
        return image[self.rectangle[0][1]:self.rectangle[1][1], self.rectangle[0][0]:self.rectangle[1][0]]

    def show_map(self, img):
        img = self.img_crop(img)
        # img = self.process_image(img)
        x = self.x
        y = self.y
        cv2.line(img, (x - 2, y), (x - 2, self.top), [0, 150, 0], 1)
        cv2.line(img, (x, y), (x, self.top), [0, 225, 0], 1)
        cv2.line(img, (x + 2, y), (x + 2, self.top), [0, 150, 0], 1)

        cv2.line(img, (self.left, y-10), (self.right, y-10), [0, 0, 150], 1)

        cv2.rectangle(img, (x - 2, y - 2), (x + 2, y + 2), (225, 0, 0), -1)
        # cv2.line()
        cv2.imshow("map", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

