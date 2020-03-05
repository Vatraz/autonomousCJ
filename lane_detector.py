import statistics

def lane(lines, prev_a=0, prev_b=0):
    if not lines:
        return {'a':None, 'b':None}
    slopes = []
    interceptions = []
    for line in lines:
        slope, interception = params(*line[0])
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

    return {'a': a, 'b':b}


def calculate_lanes_intersection(a_1, b_1, a_2, b_2, old_y):
    if not any([a_1, a_2]):
        return None
    if not a_1:
        # print("a_L ZERO", int((old_y - b_r) / a_r), old_y)
        return [int((old_y - b_2) / a_2), old_y]
    if not a_2:
        # print("a_L ZERO", int((old_y - b_l) / a_l), old_y)
        return [int((old_y - b_1) / a_1), old_y]

    x = (b_2 - b_1) / (a_1 - a_2)
    y = a_1 * x + b_1
    # print("ok", int(x), int(y))
    return [int(x), int(y)]


def calculate_intersection_Y(a, b, Y):
    if not a or not b:
        return None
    x = (Y - b)/a
    return x


def params(x1, y1, x2, y2):
    y1 = y1
    y2 = y2

    # Slope
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0:
        dx = 1  # 1px

    slope = dy / dx

    # Interception
    interception = y1 - slope * x1

    return slope, interception


def filter_lines(lines):
    slope_min = 0.2
    selected_left = []
    selected_right = []

    for line in lines:
        coords = line[0]
        slope, _ = params(*coords)

        if slope < -slope_min:
            selected_left.append(line)
        elif slope > slope_min:
            # print(slope)
            selected_right.append(line)

    return selected_left, selected_right
