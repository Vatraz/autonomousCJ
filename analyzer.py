from lanes import Lanes
import numpy as np
import cv2

class Analyzer:
    minimap_control = False
    minimap_dif = 0
    distance = 0

    def __init__(self, image_processor, minimap, aim, thresh_x):
        self.image_processor = image_processor
        self.windowX, self.windowY = image_processor.window_shape
        self.minimap = minimap
        self.aimX, self.aimY = aim
        self.lanes = Lanes((self.windowX, self.windowY))
        self.point_zero = [aim[0], aim[1]]
        self.point = self.point_zero
        self.thresh_x = thresh_x

    def get_distance_to_aim(self, image):
        windowX, windowY = self.windowX, self.windowY
        thresh_x = self.thresh_x
        hough = self.image_processor.get_lines(image)
        if type(hough) is not np.ndarray:
            self.distance = 0
            return self.distance

        self.lanes.update_lanes(hough)
        lane_l, lane_r = self.lanes.get_lanes()
        point_candidate = self.lanes.calculate_intersection()

        if point_candidate and point_candidate[1] < int(self.aimY*1.2) and point_candidate:
            self.point = point_candidate
        else:
            pass

        distance = self.point[0] - self.aimX
        if lane_l.exist():
            if lane_l.a < -0.65 or lane_l.calculate_intersection_y(windowY) > 0:
                # print('-> R', time.time())
                if lane_r.exist():
                    distance += thresh_x
                else:
                    distance = thresh_x
        if lane_r.exist():
            if lane_r.a > 0.65 or lane_r.calculate_intersection_y(windowY) < windowX:
                # print('<- L', time.time())
                if lane_l.exist():
                    distance -= thresh_x
                else:
                    distance = -thresh_x

        if lane_l.exist() and lane_r.exist() and lane_r.calculate_intersection_x(windowX) < int(windowY*7/8):
            # print('L - b too small')
            distance = 0
        if lane_r.exist() and lane_l.exist()and lane_r.calculate_intersection_x(0) < int(windowY*7/8):
            # print('R - b too small')
            distance = 0

        # if T junction
        minimap_direction = self.minimap.get_direction(image)
        if not (lane_l.exist() or lane_r.exist()) and not minimap_direction[1]:
            # print("PROBLEM", time.time()  )
            if not self.minimap_control:
                if not (minimap_direction[0] or minimap_direction[1]):
                    pass
                elif minimap_direction[0]:
                    self.minimap_dif = -1 * thresh_x
                    self.minimap_control = True
                elif minimap_direction[2]:
                    self.minimap_dif = 3 * thresh_x
                    self.minimap_control = True

        if self.minimap_control:
            # print('MAP', time.time())
            if not (lane_l.exist() or lane_r.exist()):
                distance = self.minimap_dif
            elif minimap_direction[2] or (lane_l.exist() and lane_r.exist()):
                distance = 0
                self.minimap_control = False
                self.point = self.point_zero

        self.distance = distance
        return self.distance

    def draw(self, image):
        image = image.copy()
        windowX, windowY = self.windowX, self.windowY
        thresh_x = self.thresh_x
        lane_l, lane_r = self.lanes.get_lanes()
        aimX, aimY = self.point_zero

        cv2.line(image, (int(windowX / 2), 0), (int(aimX), windowY), [255, 125, 0], 2)
        cv2.line(image, (int(aimX + thresh_x), 0), (int(aimX + thresh_x), windowY), [255, 0, 220], 1)
        cv2.line(image, (int(aimX - thresh_x), 0), (int(aimX - thresh_x), windowY), [255, 0, 220], 1)

        coords_l = lane_l.calculate_coords(windowY, aimY)
        coords_r = lane_r.calculate_coords(windowY, aimY)
        cv2.line(image, (coords_l[0], coords_l[1]), (coords_l[2], coords_l[3]), [0, 225, 0], 5)
        cv2.line(image, (coords_r[0], coords_r[1]), (coords_r[2], coords_r[3]), [255, 0, 0], 5)

        cv2.line(image, (aimX, windowY), (aimX + self.distance, windowY), [0, 0, 225], 3)
        return image
