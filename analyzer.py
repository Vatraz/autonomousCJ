from process_image.lanes import Lanes
import numpy as np
import cv2

class Analyzer:
    minimap_control = False
    minimap_dif = 0

    def __init__(self, image_processor: object, minimap: object, aim: [int, int]) -> object:
        """
        Finds the lanes on given image, processes them and analyzes how the car should be controlled

        :param image_processor: ImageProcessor
        :param minimap: Minimap
        :param aim: Point whose X value should be the X value of the lane intersection
        """
        self.image_processor = image_processor
        self.window_x, self.window_y = image_processor.window_shape
        self.minimap = minimap
        self.aimX, self.aimY = aim
        self.lanes = Lanes((self.window_x, self.window_y))
        self.point_zero = [aim[0], aim[1]]
        self.point = self.point_zero

    def get_distance_to_aim(self, image: np.ndarray, thresh_x: int) -> int:
        """
        Returns a value that describes how to control the car so that it drives in the right direction.

        :param image: Analyzed image
        :param thresh_x: Threshold below which the distance to the aim point should be interpreted as 0
        :return: Distance to the target point
        """
        window_x, window_y = self.window_x, self.window_y
        hough = self.image_processor.get_lines(image)
        if type(hough) is not np.ndarray:
            return 0

        self.lanes.update_lanes(hough)
        lane_l, lane_r = self.lanes.get_lanes()
        point_candidate = self.lanes.calculate_intersection()

        # update aim point
        if point_candidate and point_candidate[1] < int(self.aimY*1.2) and point_candidate:
            self.point = point_candidate

        # calculate distance to aim point
        distance = self.point[0] - self.aimX

        if lane_l.exist() and lane_r.exist():
            if (lane_r.calculate_intersection_x(window_x) < int(window_y*7/8)) \
                    ^ (lane_l.calculate_intersection_x(0) < int(window_y*7/8)):
                distance = 0

        elif lane_r.exist():
            if lane_r.calculate_intersection_x(window_x) < int(window_y * 7/8):
                distance += thresh_x
            if lane_r.a > 0.65 or lane_r.calculate_intersection_y(window_y) < window_x:
                distance -= thresh_x

        elif lane_l.exist():
            if lane_l.calculate_intersection_x(window_x) < int(window_y * 7/8):
                distance -= thresh_x
            if lane_l.a < -0.65 or lane_l.calculate_intersection_y(window_y) > 0:
                distance += thresh_x

        # if T junction
        minimap_direction = self.minimap.get_direction(image)
        if not (lane_l.exist() or lane_r.exist()) and not minimap_direction[1]:
            if not self.minimap_control:
                if not (minimap_direction[0] or minimap_direction[2]):
                    pass
                elif minimap_direction[0]:
                    self.minimap_dif = -1 * thresh_x
                    self.minimap_control = True
                elif minimap_direction[2]:
                    self.minimap_dif = 3 * thresh_x
                    self.minimap_control = True

        if self.minimap_control:
            if not (lane_l.exist() or lane_r.exist()):
                distance = self.minimap_dif
            elif minimap_direction[2] or (lane_l.exist() and lane_r.exist()):
                distance = 0
                self.minimap_control = False
                self.point = self.point_zero

        return distance

    def draw(self, image: np.ndarray, thresh_x: int) -> np.ndarray:
        """
        Draw lanes and current distance to the aim point on the copy of the input image.

        :param image: Input image
        :param thresh_x: Threshold below which the distance to the aim point should be interpreted as 0
        :return: Output image
        """
        image = image.copy()
        window_x, window_y = self.window_x, self.window_y
        lane_l, lane_r = self.lanes.get_lanes()
        aimX, aimY = self.point_zero

        cv2.line(image, (int(window_x / 2), 0), (int(aimX), window_y), [255, 125, 0], 2)
        cv2.line(image, (int(aimX + thresh_x), 0), (int(aimX + thresh_x), window_y), [255, 0, 220], 1)
        cv2.line(image, (int(aimX - thresh_x), 0), (int(aimX - thresh_x), window_y), [255, 0, 220], 1)

        coords_l = lane_l.calculate_intersection_y(window_y), lane_l.calculate_intersection_y(aimY)
        coords_r = lane_r.calculate_intersection_y(window_y), lane_r.calculate_intersection_y(aimY)
        cv2.line(image, (coords_l[0], coords_l[1]), (coords_l[2], coords_l[3]), [0, 225, 0], 5)
        cv2.line(image, (coords_r[0], coords_r[1]), (coords_r[2], coords_r[3]), [255, 0, 0], 5)

        cv2.line(image, (aimX, aimY), (aimX + self.distance, aimY), [0, 0, 225], 3)
        return image
