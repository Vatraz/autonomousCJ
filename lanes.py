import statistics
import cv2

class Lanes:
    def __init__(self, window):
        self._lane_l = self._lane_r = None
        self._window = window
        self._point_intersection = [int(window[0]/2), int(window[1]/2)]
        pass

    def _split_lines(self, lines):
        slope_min = 0.2
        selected_left = []
        selected_right = []

        for line in lines:
            coords = line[0]
            slope, _ = Lane.params(*coords)
            if slope < -slope_min:
                selected_left.append(line)
            elif slope > slope_min:
                selected_right.append(line)

        return selected_left, selected_right

    def update_lanes(self, lines):
        lines_l, lines_r = self._split_lines(lines)
        self._lane_l = Lane(lines_l)
        self._lane_r = Lane(lines_r)
        self._check_if_valid()

    def _check_if_valid(self):
        if self._lane_l.exist() and self._lane_r.exist() and \
               abs(self._lane_r.calculate_intersection_y(self._window[1])
                   - self._lane_l.calculate_intersection_y(self._window[1])) < self._window[0] / 2:
            self._lane_l.clear()
            self._lane_r.clear()


    def calculate_intersection(self):
        old_y = self._point_intersection[1]
        if not (self._lane_l.exist() or self._lane_r.exist()):
            return None
        if not self._lane_l.exist():
            return [int((old_y - self._lane_r.b) / self._lane_r.a), old_y]
        if not self._lane_r.exist():
            return [int((old_y - self._lane_l.b) / self._lane_l.a), old_y]

        x = (self._lane_r.b - self._lane_l.b) / (self._lane_l.a - self._lane_r.a)
        y = self._lane_l.a * x + self._lane_l.b
        # print("ok", int(x), int(y))
        self._point_intersection = [int(x), int(y)]
        return [int(x), int(y)]

    def get_lanes(self):
        return self._lane_l, self._lane_r


class Lane:
    def __init__(self, lines):
        if not lines:
            self.a = self.b = None
        else:
            self.a, self.b = self._filter_lines(lines)

    def _filter_lines(self, lines):
        slopes = []
        interceptions = []
        for line in lines:
            slope, interception = self.params(*line[0])
            slopes.append(slope)
            interceptions.append(interception)
        a = statistics.mean(slopes)
        b = statistics.mean(interceptions)

        # filter found lanes
        slopes = list(filter(lambda x: abs(x - a) < 0.1, slopes))
        interceptions = list(filter(lambda x: abs(x - b) < 100, interceptions))
        if slopes:
            a = statistics.mean(slopes)
        if interceptions:
            b = statistics.mean(interceptions)

        return a, b

    def clear(self):
        self.a = self.b = None

    def exist(self):
        if self.a and self.b:
            return True
        else:
            return False

    @staticmethod
    def params(x1, y1, x2, y2):
        # Slope
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            dx = 1  # 1px

        slope = dy / dx

        # Interception
        interception = y1 - slope * x1

        return slope, interception

    def calculate_intersection_y(self, y):
        if not self.a or not self.b:
            return None
        x = (y - self.b) / self.a
        return x

    def calculate_intersection_x(self, x):
        if not self.a or not self.b:
            return None
        y = self.b + self.a*x
        return y

    def calculate_coords(self, y_top, y_bottom):
        if not self.exist():
            return [0, 0, 0, 0]
        y1 = int(y_top - y_bottom)
        x1 = int((y1 - self.b) / self.a)
        y2 = y_top
        x2 = int((y2 - self.b) / self.a)

        return [x1, y1, x2, y2]
