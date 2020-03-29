import cv2

from keyboard_control import hold_key_stop, press_key, hold_key_start, wait_for_space, get_keymap
from process_image.image import ImageProcessor
from process_image.minimap import Minimap
from analyzer import Analyzer

THRESHOLD_X = 20
WINDOW_Y, WINDOW_X = 600, 800
AIM_X, AIM_Y = int(WINDOW_X / 2), int(WINDOW_Y / 2)

if __name__ == '__main__':
    wait_for_space()

    image_processor = ImageProcessor(WINDOW_X, WINDOW_Y)
    minimap = Minimap(image_processor.get_image(), ((20, int(WINDOW_Y * 3 / 4)), (int(WINDOW_X / 4), WINDOW_Y - 20)))
    analyzer = Analyzer(image_processor, minimap, [AIM_X, AIM_Y])
    keys = get_keymap()

    # main loop
    direction = None
    press_time_mul = 1
    direction_prev = None
    while True:
        prt_scr = image_processor.get_image()
        correction = analyzer.get_distance_to_aim(prt_scr, THRESHOLD_X)

        if abs(correction) >= THRESHOLD_X:
            if correction > 0:
                direction = 'right'
            else:
                direction = 'left'
            correction_level = abs(correction) / THRESHOLD_X
            if correction_level >= 8:
                press_time_mul = 4
            elif correction_level >= 5:
                press_time_mul = 3
            elif correction_level >= 3:
                press_time_mul = 2
            else:
                press_time_mul = 1
        else:
            direction = None
            press_time_mul = 1

        if press_time_mul != 4 or direction != direction_prev:
            hold_key_stop()
            direction_prev = None
        if direction and press_time_mul != 4:
            press_key(direction, press_time_mul)
        elif direction and direction_prev != direction and press_time_mul == 4:
            direction_prev = direction
            arrow = keys['L'] if direction == 'left' else keys['R']
            hold_key_start(arrow)

        cv2.imshow("lanes", cv2.cvtColor(analyzer.draw(prt_scr, THRESHOLD_X), cv2.COLOR_BGR2RGB))
        cv2.imshow("map", cv2.cvtColor(minimap.draw(prt_scr), cv2.COLOR_BGR2RGB))

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break