import statistics

def lane(lines):
    if not lines:
        return {'a':0, 'b':0}
    slopes = []
    interceptions = []
    for line in lines:
        slope, interception = params(*line[0])
        slopes.append(slope)
        interceptions.append(interception)
    return {'a':statistics.mean(slopes), 'b':statistics.mean(interceptions)}


def calculate_intersection(a_l, b_l, a_r, b_r, old_y):
    if a_l == 0 and a_r == 0:
        return None
    if a_l == 0:
        # print("a_L ZERO", int((old_y - b_r) / a_r), old_y)
        return int((old_y - b_r) / a_r), old_y
    if a_r == 0:
        # print("a_L ZERO", int((old_y - b_l) / a_l), old_y)
        return int((old_y - b_l) / a_l), old_y

    x = (b_r - b_l) / (a_l - a_r)
    y = a_l * x + b_l
    # print("ok", int(x), int(y))
    return int(x), int(y)


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

def select_lines(lines):
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
