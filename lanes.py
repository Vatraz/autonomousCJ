import statistics


class Lanes:
    def __init__(self, window):
        self.lane_l = self.lane_r = None
        self.window = window
        self.point_intersection = [int(window[0]/2), int(window[1]/2)]
        pass

    def split_lines(self, lines):
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

    def find_lanes(self, lines):
        lines_l, lines_r = self.split_lines(lines)
        self.lane_l = Lane(lines_l)
        self.lane_r = Lane(lines_r)
        self.check_if_valid()

    def check_if_valid(self):
        if self.lane_l.exist and self.lane_r.exist and abs(self.lane_r.calculate_intersection_Y(self.window[1])
                                                           - self.lane_l.calculate_intersection_Y(self.window[1])) \
                                                            < self.window[0] / 2:
            self.lane_l.clear()
            self.lane_r.clear()

    def calculate_intersection(self):
        old_y = self.point_intersection[1]
        if not (self.lane_l.exist and self.lane_r.exist):
            return None
        if not self.lane_l.exist:
            return [int((old_y - self.lane_r.b) / self.lane_r.a), old_y]
        if not self.lane_r.exist:
            return [int((old_y - self.lane_l.b) / self.lane_l.a), old_y]

        x = (self.lane_r.b - self.lane_l.b) / (self.lane_l.a - self.lane_r.a)
        y = self.lane_l.a * x + self.lane_l.b
        # print("ok", int(x), int(y))
        self.point_intersection = [int(x), int(y)]
        return [int(x), int(y)]

class Lane:
    def __init__(self, lines):
        if not lines:
            self.a = self.b = None
        else:
            self.a, self.b = self.filter_lines(lines)

    def filter_lines(self, lines):
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

    @property
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

    def calculate_intersection_Y(self, y):
        if not self.a or not self.b:
            return None
        x = (y - self.b) / self.a
        return x
