import cv2
import numpy as np
import time

from src.utils import crop_bounding_box_xywh, rotate_around_center

__DEBUG_CV__ = True


class MiniMap:
    """
    Class for game minimap analysis.
    """

    def __init__(self):
        # load full map image
        full_map = cv2.imread('src/data/sanandreas_map.jpg')
        self.full_map = cv2.cvtColor(full_map, cv2.COLOR_BGR2GRAY)
        self.offset = 70
        self.full_map = cv2.copyMakeBorder(self.full_map, self.offset, self.offset, self.offset, self.offset,
                                           cv2.BORDER_REPLICATE, None, None)

        self.player_loc = None # player location on the map
        self.map_angle = None # rotation angle of the map
        self.map_angle_diff = None # difference between last and current rotation angle

        self.map_rect = None # minimap fragment described by bounding box
        self.map_rect_in = None # inner minimap fragment that can be used for template matching
        self.map_ring_mask = None # map ring mask used for north symbol search

    def find_minimap_loc(self, org_img: np.ndarray) -> None:
        """
        Search for ellipse and bounding box that describe the position of the minimap in the game window image, as well
        bounding box representing the inner fragment of the minimap and mask used in map rotation finding.

        :param org_img: Game window image in gray scale
        """
        # get lower-left quarter of the image
        offset_y, offset_x = org_img.shape[0]//2, org_img.shape[1]//2
        img_cropped = org_img[offset_y:, :offset_x]

        # Find the biggest contour on the thresholded image - minimap location
        _, thresh = cv2.threshold(img_cropped, 1, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour = sorted(contours, key=cv2.contourArea, reverse=True)[0]

        # Update minimap bounding box
        x, y, w, h = cv2.boundingRect(contour)
        self.map_rect = x, offset_y+y, w, h

        # Mask used for minimap North symbol searching
        thresh_org = thresh[y:y+h, x:x+w]
        map_mask = np.zeros(thresh_org.shape, dtype=np.uint8)
        map_mask = cv2.ellipse(map_mask, (w//2, h//2), (w//2, h//2), 0, 0, 360, 255, thickness=7)
        self.map_ring_mask = map_mask

        # Inner minimap fragment that can be used for template matching
        a = int(min(w, h)/np.sqrt(2)*0.9)
        self.map_rect_in = w//2 - a//2, h//2 - a//2, a, a

    def find_map_rotation(self, img: np.ndarray) -> float:
        """
        Find the counter-clockwise rotation of the minimap.

        :param img: Minimap gray scale image
        :return: Rotation angle [radians]
        """
        # TODO: need to find faster and simpler method
        # find North symbol loc by searching for white in map ring mask
        _, mask = cv2.threshold(img, 250, 255, cv2.THRESH_BINARY)
        mask = cv2.bitwise_and(self.map_ring_mask, mask, mask=self.map_ring_mask)

        # Yet another minimap mask, to filter out noise from inaccuracy of ring masking
        mask_minimap = cv2.threshold(img, 2, 255, cv2.THRESH_BINARY_INV)[1]
        mask_minimap = cv2.bitwise_or(mask_minimap, mask, mask=np.ones(mask.shape, dtype=np.uint8))
        contours, _ = cv2.findContours(mask_minimap, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour = sorted(contours, key=cv2.contourArea, reverse=True)[0]
        cv2.drawContours(mask_minimap, [contour], contourIdx=-1, color=255, thickness=-1)
        mask = cv2.bitwise_and(mask_minimap, mask, mask=mask_minimap)

        # Remove single pixel leftovers
        # S L O O W : /
        kernel1 = np.array([[0, 0, 0],[0, 1, 0],[0, 0, 0]], np.uint8)
        kernel2 = np.array([[1, 1, 1],[1, 0, 1],[1, 1, 1]], np.uint8)
        hitormiss1 = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel1)
        hitormiss2 = cv2.morphologyEx(cv2.bitwise_not(mask), cv2.MORPH_ERODE, kernel2)
        hitormiss = cv2.bitwise_and(hitormiss1, hitormiss2)
        mask = cv2.bitwise_and(mask, mask, mask=cv2.bitwise_not(hitormiss))

        # Find the center of the North symbol
        br = cv2.boundingRect(mask)
        bx, by, bw, bh = br
        w, h = self.map_rect[2:]
        if bw < bh:
            diff = bh - bw
            bx = bx - diff if bx > w//2 else bx + diff
            bw += diff
        elif bw > bh:
            diff = bw - bh
            by = by - diff if by > h // 2 else by + diff
            bh += diff
        bx += bw//2
        by += bh//2

        # Calculate rotation angle
        angle = np.arctan2(w//2-bx, h//2-by)

        if __DEBUG_CV__:
            # cv2.imshow('fmr', mask)
            # cv2.imshow('map_ring_mask', self.map_ring_mask)
            pass
        return angle

    def get_minimap_fragment(self, map_image: np.ndarray, angle: float) -> np.ndarray:
        """
        Get the image of the minimap fragment that can be compared with the full map.

        :param map_image: Map image
        :param angle: Rotation angle
        :return: Minimap fragment image
        """
        map_image = rotate_around_center(map_image, np.rad2deg(angle))
        searched_fragment = crop_bounding_box_xywh(map_image, self.map_rect_in)
        return searched_fragment

    def update_player_loc(self, img: np.ndarray, init=False):
        """
        Updates the player's location on the map. If method is called for the first time, or init flag is set as True,
        performs searching on the full map. Otherwise narrows searching area to area near previous player location.

        :param img: Current game window image in gray scale
        :param init: If location should be search on full map
        """
        tic = time.time()

        # Make sure to init if there is no previous player loc
        if self.player_loc is None:
            init = True

        map_image = crop_bounding_box_xywh(img, self.map_rect)
        angle = self.find_map_rotation(map_image)

        # The first search need to be the most accurate one - we are searching for the location in the full map.
        # Assuming that player doesn't move during the process, game minimap zoom is set to 0.
        max_scale = 68 if not init else 45
        solution = (0, 0)
        last_best = 0
        for scale in list(range(35, max_scale)):
            searched_fragment = self.get_minimap_fragment(map_image, angle)
            maxVal, maxLoc = self.find_player_loc_local(searched_fragment, scale, init)
            # print(scale, ': ', maxVal, ' --- ', maxLoc)
            if maxVal > last_best:
                last_best = maxVal
                solution = maxLoc[0] + scale//2, maxLoc[1] + scale//2

        self.player_loc = solution
        self.map_angle_diff = angle - self.map_angle if self.map_angle else 0
        self.map_angle = angle

        # print(1/(time.time() - tic))
        if __DEBUG_CV__:
            print(solution, last_best)
            full_map = self.full_map.copy()
            cv2.circle(full_map, solution, 10, 255, 2, 8, 0)
            cv2.circle(full_map, solution, 1, 255, 3, 8, 0)
            cv2.imshow('full_map', full_map)
            cv2.imshow('searched_fragment', searched_fragment)
            print('+=======+ OK +=======+')

    def get_map_area_near_prev(self, search_area: int):
        """
        Returns an map area close to the previous player location

        :param search_area:
        :return:
        """
        x, y = self.player_loc
        search_range = np.array([y-search_area, y+search_area, x-search_area, x+search_area])
        search_range = np.clip(search_range, 0, self.full_map.shape[1])
        return self.full_map[search_range[0]:search_range[1], search_range[2]:search_range[3]]

    def find_player_loc_local(self, searched_fragment: np.ndarray, scale: int, full_search=False) -> tuple:
        """
        Find possible player location at given minimap scale and its probability.

        :param searched_fragment: Mimimap image fragment searched on the full map
        :param scale: Scale in which to search
        :param full_search: If searching should be performed on the full map image(True)
                            or the map fragment near previous location (False)
        :return: probability, position (X, Y)
        """
        search_area = int(scale/1.5)
        map = self.get_map_area_near_prev(search_area) if not full_search else self.full_map

        # search for scaled fragment in map
        searched_fragment_scaled = cv2.resize(searched_fragment, (scale, scale), interpolation=cv2.INTER_LINEAR)
        result = cv2.matchTemplate(map, searched_fragment_scaled, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result, None)

        if not full_search:
            maxLoc = (
                    maxLoc[0] + self.player_loc[0] - search_area,
                    maxLoc[1] + self.player_loc[1] - search_area,
            )

        if __DEBUG_CV__:
            # import matplotlib.pyplot as plt
            # plt.imshow(result)
            # plt.show()
            # cv2.imshow('get_map_area_near_prev', map)
            # cv2.imshow('searched_fragment_scaled', searched_fragment_scaled)
            pass

        return maxVal, maxLoc


if __name__ == '__main__':
    for i in range(9, 0, -1):
        screen = cv2.imread(f'{1+i}.png')
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        mp = MiniMap()
        mp.find_minimap_loc(screen)
        mp.update_player_loc(screen)
        cv2.waitKey(-1)
    # mp.find_minimap_loc(screen)
    # mp.find_loc()
