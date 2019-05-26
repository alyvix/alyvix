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
        self.type = "I"
        self.group = 0
        self.is_main = False
        self.index_in_tree = 0
        self.index_in_group = 0
        self.mouse = {}
        self.keyboard = {}
        self.roi = None

class ImageManager():

    def __init__(self):
        self._template = None


        self._color_screen = None
        self._gray_screen = None
        self._scaling_factor = None

        self._overlapping_factor = 20

    def set_template(self, template, roi=None):
        hist_rgb = cv2.calcHist([template], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist_rgb = cv2.normalize(hist_rgb, None).flatten()

        self._template = (cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), hist_rgb, roi)

    def set_color_screen(self, screen):
        self._color_screen = screen

    def set_gray_screen(self, screen):
        self._gray_screen = screen

    def set_scaling_factor(self, scaling_factor):
        self._scaling_factor = scaling_factor

    def find(self, detection):

        match_colors = detection['colors']
        match_likelihood = detection['likelihood']

        template = self._template[0]
        template_rgb = self._template[1]
        roi = self._template[2]

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

            source_image = self._gray_screen[y1:y2, x1:x2]
        else:
            source_image = self._gray_screen

        objects_found = []
        analyzed_points = []

        template_w, template_h = template.shape[::-1]

        #recalc source image
        source_img_h, source_img_w = source_image.shape

        #cv2.imwrite("d:\\aa_tmpl.png", template)
        #cv2.imwrite("d:\\aa_source.png", source_image)

        if source_img_h <= template_h or source_img_w <= template_w:
            return []

        res = cv2.matchTemplate(source_image, template, cv2.TM_CCOEFF_NORMED)

        loc = np.where(res >= match_likelihood)

        for point in zip(*loc[::-1]):


            x = offset_x + point[0]
            y = offset_y + point[1]

            is_already_found = False

            for point_already_analyzed in analyzed_points:

                tolerance_region_w = (template_w / 2) + (self._overlapping_factor * self._scaling_factor)
                tolerance_region_h = (template_h / 2) + (self._overlapping_factor * self._scaling_factor)

                if (x >= point_already_analyzed[0] - tolerance_region_w and
                    x <= point_already_analyzed[0] + tolerance_region_w) and \
                        (y >= point_already_analyzed[1] - tolerance_region_h and
                         y <= point_already_analyzed[1] + tolerance_region_h):
                    is_already_found = True

            if is_already_found == False:

                hist_rgb = cv2.calcHist([self._color_screen[y:y + template_h, x:x + template_w]], [0, 1, 2], None, [8, 8, 8],
                                        [0, 256, 0, 256, 0, 256])
                hist_rgb = cv2.normalize(hist_rgb, None).flatten()

                comp_rgb = cv2.compareHist(hist_rgb, template_rgb, cv2.HISTCMP_BHATTACHARYYA)

                analyzed_points.append((x, y, template_w, template_h))

                # if (comp_blue > 0.3 or comp_green > 0.3 or comp_red > 0.3) and main_template.match_colors is True:
                if comp_rgb > 0.2 and match_colors is True:
                    continue

                return_value = Result()
                return_value.x = x
                return_value.y = y
                return_value.w = template_w
                return_value.h = template_h

                objects_found.append(return_value)

        return objects_found



