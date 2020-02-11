# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2019 Alan Pipitone
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Developer: Alan Pipitone (Violet Atom) - http://www.violetatom.com/
# Supporter: Wuerth Phoenix - http://www.wuerth-phoenix.com/
# Official website: http://www.alyvix.com/

import cv2
import numpy as np
from alyvix.tools.screen import ScreenManager

class Result():
    def __init__(self):
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.type = "R"
        self.group = 0
        self.is_main = False
        self.index_in_tree = 0
        self.index_in_group = 0
        self.mouse = {}
        self.keyboard = {}
        self.roi = None

class RectangleManager():

    def __init__(self):
        self._rect = None
        self._overlapping_factor = 20

        self._color_screen = None
        self._gray_screen = None
        self._scaling_factor = None

    def set_color_screen(self, screen):
        self._color_screen = screen

    def set_gray_screen(self, screen):
        self._gray_screen = screen

    def set_scaling_factor(self, scaling_factor):
        self._scaling_factor = scaling_factor

    def _median_canny(self, img, thresh1, thresh2):
        median = np.median(img)
        img = cv2.Canny(img, int(thresh1 * median), int(thresh2 * median))
        return img

    def find(self, detection, roi=None):

        min_h = detection['height']['min']
        max_h = detection['height']['max']

        min_w = detection['width']['min']
        max_w = detection['width']['max']

        offset_x = 0
        offset_y = 0

        source_img_h, source_img_w = self._gray_screen.shape

        if roi is not None:


            y1 = roi.y
            y2 = y1 + roi.h

            x1 = roi.x
            x2 = x1 + roi.w

            if roi.unlimited_up is True:
                y1 = 0
                y2 = roi.y + roi.h

            if roi.unlimited_down is True:
                y2 = source_img_h

            if roi.unlimited_left is True:
                x1 = 0
                x2 = roi.x + roi.w

            if roi.unlimited_right is True:
                x2 = source_img_w


            if y1 < 0:
                y1 = 0
            elif y1 > source_img_h:
                y1 = source_img_h

            if y2 < 0:
                y2 = 0
            elif y2 > source_img_h:
                y2 = source_img_h

            if x1 < 0:
                x1 = 0
            elif x1 > source_img_w:
                x1 = source_img_w

            if x2 < 0:
                x2 = 0
            elif x2 > source_img_w:
                x2 = source_img_w

            offset_x = x1
            offset_y = y1

            source_image = self._color_screen[y1:y2, x1:x2]
        else:
            source_image = self._color_screen

        objects_found = []
        analyzed_points = []

        blue, green, red = cv2.split(source_image)
        # Run canny edge detection on each channel
        blue_edges = self._median_canny(blue, 0.2, 0.3)
        green_edges = self._median_canny(green, 0.2, 0.3)
        red_edges = self._median_canny(red, 0.2, 0.3)

        # Join edges back into image
        edges = blue_edges | green_edges | red_edges

        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # self._log_manager.save_image(self.__find_log_folder, "canny.png", edges)

        cnt = 0
        # print main_rect.min_width, main_rect.max_width, main_rect.min_height, main_rect.max_height
        # For each contour, find the bounding rectangle and draw it
        for c in reversed(contours):

            x, y, w, h = cv2.boundingRect(c)
            x = offset_x + x
            y = offset_y + y

            # print x, y, w, h

            if (w >= min_w and w <= max_w and h >= min_h and h <= max_h):

                is_already_found = False

                for point_already_analyzed in analyzed_points:

                    tolerance_region_w = (((min_w + max_w) / 2) / 2) + (self._overlapping_factor * self._scaling_factor)
                    tolerance_region_h = (((min_h + max_h) / 2) / 2) + (self._overlapping_factor * self._scaling_factor)

                    if (x >= point_already_analyzed[0] - tolerance_region_w and
                        x <= point_already_analyzed[0] + tolerance_region_w) and \
                            (y >= point_already_analyzed[1] - tolerance_region_h and
                             y <= point_already_analyzed[1] + tolerance_region_h):
                        is_already_found = True

                if is_already_found == False:

                    analyzed_points.append((x, y, w, h))

                    return_value = Result()
                    return_value.x = x
                    return_value.y = y
                    return_value.w = w
                    return_value.h = h

                    objects_found.append(return_value)

        return objects_found