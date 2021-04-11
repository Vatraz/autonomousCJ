import statistics


class Lanes:
    def __init__(self, window):
        self._lane_l = self._lane_r = Lane(None, None, None)
        self._window = window
        self._point_intersection = [int(window[0]/2), int(window[1]/2)]

    def _split_lines(self, lines):
        """
        Split lines to two subsets. One containing lines that are likely to be the left lane, and second containing
        lines that describe the lane on the right.

        :param lines: list of lines
        :return: left lane lines, right lane lines
        """
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
        """
        Updates both lanes based of the list of detected lines.

        :param lines: list of lines
        """
        lines_l, lines_r = self._split_lines(lines)
        self._lane_l = Lane(lines_l, self._lane_l.a, self._lane_l.b)
        self._lane_r = Lane(lines_r, self._lane_r.a, self._lane_r.b)
        self._clear_invalid()

    def _clear_invalid(self):
        """
        Clears lanes with invalid parameters.
        """
        if self._lane_l.exist() and self._lane_r.exist() and \
               abs(self._lane_r.calculate_intersection_y(self._window[1])
                   - self._lane_l.calculate_intersection_y(self._window[1])) < self._window[0] / 2:
            self._lane_l.clear()
            self._lane_r.clear()

    def calculate_intersection(self):
        """
        Returns an intersection point of lanes. If only one lane was detected, intersection
        is calculated based on old value of the missing lane. If there is no lane, returns None.

        :return: intersection point (x, y)
        """
        old_y = self._point_intersection[1]
        if not (self._lane_l.exist() or self._lane_r.exist()):
            return None
        if not self._lane_l.exist():
            return [int((old_y - self._lane_r.b) / self._lane_r.a), old_y]
        if not self._lane_r.exist():
            return [int((old_y - self._lane_l.b) / self._lane_l.a), old_y]

        x = (self._lane_r.b - self._lane_l.b) / (self._lane_l.a - self._lane_r.a)
        y = self._lane_l.a * x + self._lane_l.b
        self._point_intersection = [int(x), int(y)]
        return [int(x), int(y)]

    def get_lanes(self):
        """
        Returns the tuple containing both lanes.

        :return: (left lane, right lane)
        """
        return self._lane_l, self._lane_r


class Lane:
    def __init__(self, lines, prv_a, prv_b):
        if not lines:
            self.a = self.b = None
        else:
            self.a, self.b = self._filter_lines(lines)

            if prv_a and abs(self.a - prv_a) < 0.1:
                self.a = self.a - (self.a - prv_a)*0.4
            if prv_b and abs(self.b - prv_b) < 10:
                self.b = self.b - (self.b - prv_b)*0.4

    def _filter_lines(self, lines):
        """
        Filters the lines list describing a lane, and returns the values of its a and b parameters
        (slope, interception).

        :param lines: list of lines
        :return: a, b
        """
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
        """
        Assigns None to the lane a and b parameters.
        """
        self.a = self.b = None

    def exist(self):
        """
        Checks if the lane exists, based on its a and b values.

        :return: whether the lane exists
        """
        if self.a and self.b:
            return True
        else:
            return False

    @staticmethod
    def params(x1, y1, x2, y2):
        """
        Calculates slope and intersection of lane described by two points: (x1, y1) and (x2, y2).

        :param x1: position of the first point on the X-axis
        :param y1: position of the first point on the Y-axis
        :param x2: position of the second point on the X-axis
        :param y2: position of the second point on the Y-axis
        :return: slope, interception
        """
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
        """
        Calculate the intersection with the horizontal line crossing the Y-axis at (y, 0).

        :param y: point of the intersection in Y-axis
        :return: point of the intersection in X-axis
        """
        if not self.a or not self.b:
            return None
        x = (y - self.b) / self.a
        return x

    def calculate_intersection_x(self, x):
        """
        Calculate the intersection with the vertical line crossing the Y-axis at (0, x).

        :param x: point of the intersection in X-axis
        :return: point of the intersection in Y-axis
        """
        if not self.a or not self.b:
            return None
        y = self.b + self.a*x
        return y
