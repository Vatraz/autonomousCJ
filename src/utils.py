import cv2


def crop_bounding_box_xywh(image, box):
    x, y, w, h = box
    return image[y:y+h, x:x+w]


def find_white_px_center(image):
    M = cv2.moments(image)

    # calculate x,y coordinate of center
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        cX, cY = 0, 0

    return cX, cY


def rotate_around_center(image, angle):
    w, h = image.shape[1], image.shape[0]
    M = cv2.getRotationMatrix2D((w//2, h//2), -angle, 1)
    rotated = cv2.warpAffine(image, M, (w, h))
    return rotated
