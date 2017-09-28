# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2015 Alan Pipitone
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
import numpy
import copy
import time
import datetime
import os
import sys
from threading import Thread

from alyvix.finders.cv.basefinder import BaseFinder
from alyvix.finders.cv.basefinder import Roi
from alyvix.finders.cv.basefinder import MatchResult
from alyvix.tools.screen import ScreenManager


class _Rect():

    width = 0
    height = 0

    min_width = 0
    max_width = 0

    min_height = 0
    max_height = 0

    height_tolerance = 0
    width_tolerance = 0

    debug_folder = None

    def __init__(self, rect_dict):
        self._set_rect_dictionary(rect_dict)

    def _set_rect_dictionary(self, rect_dict):
        """
        converts the dictionary into the rectangles properties

        :type rect_dict: dict
        :param rect_dict: the dictionary that defines the sub rectangle
        """

        if ("height" in rect_dict and "width" in rect_dict and
                "width_tolerance" in rect_dict and "height_tolerance" in rect_dict):
            self.height = rect_dict['height']
            self.width = rect_dict['width']
            self.height_tolerance = rect_dict['height_tolerance']
            self.width_tolerance = rect_dict['width_tolerance']
        elif ("min_height" in rect_dict and "max_height" in rect_dict and
                "min_width" in rect_dict and "max_width" in rect_dict):
            self.min_height = rect_dict['min_height']
            self.max_height = rect_dict['max_height']
            self.min_width = rect_dict['min_width']
            self.max_width = rect_dict['max_width']
        else:
            raise Exception("Rect dictionary has an incorrect format!")


class RectFinder(BaseFinder):

    def __init__(self, name=None):
        """
        init the class

        :type name: string
        :param name: the object name
        """

        self.is_textfinder = False

        #self._main_component = None
        #self._sub_components = []
        self.__timed_out_sub_extra_images = []

        the_name = "rect_finder"

        if name is not None:
            the_name = name

        super(RectFinder, self).__init__(the_name)
        #BaseFinder.__init__(self, the_name)


    def set_main_component(self, rect_dict, roi_dict=None):
        """
        Set the rectangle that the find method has to find into the source Image.

        :type rect_dict: dict
        :param rect_dict: the dictionary that defines the main rectangle
        :type roi_dict: dict
        :param roi_dict: the dictionary that defines the ROI
        """

        main_rect = _Rect(rect_dict)

        if roi_dict is not None:
            roi = Roi(roi_dict)
        else:
            roi = None

        self._main_component = (main_rect, roi)

    def add_sub_component(self, rect_dict, roi_dict):
        """
        Add a rectangle that the find method has to find if it has also find the main rectangle.
        A ROI (region of interest) will be cropped from the source image according to the roi_dict.
        The find method will search the sub rectangle only inside the roi area.
        roi_x and roi_y are relative to the main rect x,y coordinates.

        :type rect_dict: dict
        :param rect_dict: the dictionary that defines the sub rectangle
        :type roi_dict: dict
        :param roi_dict: the dictionary that defines the ROI
        """

        roi = Roi(roi_dict)
        sub_rect = _Rect(rect_dict)
        self._sub_components.append((sub_rect, roi))

    def find(self):
        """
        find the main rectangle and sub rectangles into the source image.

        :rtype: list[[MatchResult, list[MatchResult]]]
        :return: a list that contains x, y, height, width of rectangle(s) found
        """
        time_before_find = time.time()
        try:
            self._timedout_main_components = []
            self._timedout_sub_components = []

            self._main_extra_img_log = None
            self._sub_extra_imgages_log = []

            self._objects_found = []

            source_img_auto_set = False

            if self._source_image_color is None:
                screen_capture = ScreenManager()
                src_img_color = screen_capture.grab_desktop(screen_capture.get_color_mat)
                self.set_source_image_color(src_img_color)
                src_img_gray = cv2.cvtColor(src_img_color, cv2.COLOR_BGR2GRAY)
                self.set_source_image_gray(src_img_gray)
                source_img_auto_set = True

            self.__find_log_folder = datetime.datetime.now().strftime("%H_%M_%S") + "_" + "searching"

            offset_x = 0
            offset_y = 0

            main_rect = self._main_component[0]
            roi = self._main_component[1]

            if roi is not None:

                y1 = roi.y
                y2 = y1 + roi.height
                x1 = roi.x
                x2 = x1 + roi.width

                res = self._info_manager.get_info("RESOLUTION")

                y1 = roi.y
                y2 = y1 + roi.height

                x1 = roi.x
                x2 = x1 + roi.width

                if roi.unlimited_up is True:
                    y1 = 0
                    y2 = roi.y + roi.height

                if roi.unlimited_down is True:
                    y2 = res[1]

                if roi.unlimited_left is True:
                    x1 = 0
                    x2 = roi.x + roi.width

                if roi.unlimited_right is True:
                    x2 = res[0]

                offset_x = x1
                offset_y = y1

                source_img_height, source_img_width, channels = self._source_image_color.shape

                if y1 < 0:
                    y1 = 0
                elif y1 > source_img_height:
                    y1 = source_img_height

                if y2 < 0:
                    y2 = 0
                elif y2 > source_img_height:
                    y2 = source_img_height

                if x1 < 0:
                    x1 = 0
                elif x1 > source_img_width:
                    x1 = source_img_width

                if x2 < 0:
                    x2 = 0
                elif x2 > source_img_width:
                    x2 = source_img_width

                #print x1,x2,y1,y2
                source_image = self._source_image_color[y1:y2, x1:x2]
            else:
                source_image = self._source_image_color

            objects_found = []
            analyzed_points = []
            self._objects_found = []

            blue, green, red = cv2.split(source_image)
            # Run canny edge detection on each channel
            blue_edges = self.__median_canny(blue, 0.2, 0.3)
            green_edges = self.__median_canny(green, 0.2, 0.3)
            red_edges = self.__median_canny(red, 0.2, 0.3)

            # Join edges back into image
            edges = blue_edges | green_edges | red_edges
            if self._log_manager.is_log_enable() is True:
                self._log_manager.save_image(self.__find_log_folder, "source_img.png", source_image)
                self._log_manager.save_image(self.__find_log_folder, "edges.png", edges)

            #self._rect_extra_timedout_image = edges.copy()
            if roi is not None:
                self._main_extra_img_log = (edges.copy(), (x1, y1, x2, y2))
            else:
                self._main_extra_img_log = (edges.copy(), None)

            #edges = self.__median_canny(self._source_image, 0.2, 0.3)

            #self._timed_out_images.append(source_image.copy())

            # find the contours
            contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            #self._log_manager.save_image(self.__find_log_folder, "canny.png", edges)

            if main_rect.width != 0 and main_rect.height != 0:
                main_rect.min_width = main_rect.max_width = main_rect.width
                main_rect.min_height = main_rect.max_height = main_rect.height

            if main_rect.width_tolerance != 0 and main_rect.width != 0 and main_rect.height != 0:
                main_rect.min_width = main_rect.min_width - main_rect.width_tolerance
                main_rect.max_width = main_rect.max_width + main_rect.width_tolerance

            if main_rect.height_tolerance != 0 and main_rect.width != 0 and main_rect.height != 0:
                main_rect.min_height = main_rect.min_height - main_rect.height_tolerance
                main_rect.max_height = main_rect.max_height + main_rect.height_tolerance

            cnt = 0

            #print main_rect.min_width, main_rect.max_width, main_rect.min_height, main_rect.max_height
            # For each contour, find the bounding rectangle and draw it
            for c in reversed(contours):

                object_found = []
                object_found.append([])
                object_found.append([])
                self.__timed_out_sub_extra_images = []

                x, y, w, h = cv2.boundingRect(c)
                x = offset_x + x
                y = offset_y + y

                #print x, y, w, h

                if(w >= main_rect.min_width and w <= main_rect.max_width and
                        h >= main_rect.min_height and h <= main_rect.max_height):

                    is_already_found = False

                    for point_already_analyzed in analyzed_points:

                        tolerance_region_w = (((main_rect.min_width + main_rect.max_width)/2)/2)  + (20 * self._scaling_factor)
                        tolerance_region_h = (((main_rect.min_height + main_rect.max_height)/2)/2) + (20 * self._scaling_factor)

                        #tolerance_region = 20 * self._scaling_factor

                        if (x >= point_already_analyzed[0] - tolerance_region_w and
                                    x <= point_already_analyzed[0] + tolerance_region_w) and\
                                (y >= point_already_analyzed[1] - tolerance_region_h and
                                    y <= point_already_analyzed[1] + tolerance_region_h):

                            is_already_found = True

                    if is_already_found == False:

                        analyzed_points.append((x, y, w, h))

                        self._timedout_main_components.append(MatchResult((x, y, w, h)))

                        #self._log_manager.set_main_object_points((x, y, w, h))
                        if self._log_manager.is_log_enable() is True:
                            img_copy = source_image.copy()
                            cv2.rectangle(img_copy, ((x-offset_x), (y-offset_y)), ((x-offset_x)+w, (y-offset_y)+h), (0, 0, 255), 2)
                            self._log_manager.save_image(self.__find_log_folder, "object_found.png", img_copy)

                        sub_templates_len = len(self._sub_components)

                        if sub_templates_len == 0:
                            #good_points.append((x, y, w, h))

                            main_object_result = MatchResult((x, y, w, h))
                            object_found[0] = main_object_result

                            object_found[1] = None
                            objects_found.append(object_found)
                        else:

                            total_sub_template_found = 0

                            sub_objects_found = []
                            timed_out_objects = []

                            for sub_rect in self._sub_components:

                                sub_template_coordinates = self._find_sub_rect((x, y), sub_rect)

                                if sub_template_coordinates is not None:
                                    sub_objects_found.append(sub_template_coordinates)
                                    total_sub_template_found = total_sub_template_found + 1
                                    timed_out_objects.append((sub_template_coordinates, sub_rect[1]))
                                else:
                                    timed_out_objects.append((None, sub_rect[1]))

                                if total_sub_template_found == sub_templates_len:


                                    #good_points.append((x, y, w, h))

                                    main_object_result = MatchResult((x, y, w, h))
                                    object_found[0] = main_object_result

                                    object_found[1] = sub_objects_found

                                    objects_found.append(object_found)

                            self._timedout_sub_components.append(timed_out_objects)
                            self._sub_extra_imgages_log.append(self.__timed_out_sub_extra_images)

                        #self._log_manager.save_object_image("img__result" + str(cnt) + ".png")
                cnt = cnt + 1

            if len(objects_found) > 0:
                self._objects_found = copy.deepcopy(objects_found)
                if self._is_object_finder is True:
                    self._objects_found_of_sub_object_finder.extend(copy.deepcopy(objects_found))
                    #gray_source_img = cv2.cvtColor(self._source_image, cv2.COLOR_BGR2GRAY)
                    # if wait_disappear is False:
                    #if self._info_manager.get_info('LOG OBJ IS FOUND') is False:
                    if self._info_manager.get_info('LOG OBJ FINDER TYPE') is None:
                        self._info_manager.set_info('LOG OBJ FINDER TYPE', 1)


                    self._log_manager.save_objects_found(self._name, self.get_source_image_gray(),
                                                         self._objects_found, [x[1] for x in self._sub_components],
                                                         self.main_xy_coordinates, self.sub_xy_coordinates, finder_type=1)

                self._cacheManager.SetLastObjFoundFullImg(self._source_image_gray)

            #time.sleep(40)

            if source_img_auto_set is True:
                self._source_image_color = None
                self._source_image_gray = None
                source_img_auto_set = False

            self._flag_thread_started = False

            if  self._calc_last_finder_time is True:
                self._last_finder_time = time.time() - time_before_find
                self._calc_last_finder_time = False

            return self._objects_found

        except Exception, err:
            self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
            self._flag_thread_started = False
            return None


    def _find_sub_rect(self, main_template_xy=None, sub_rect=None):
        """
        find sub rectangle into the source image.

        :type main_template_xy: (int, int)
        :param main_template_xy: x,y coordinates of current main template
        :type sub_template: (numpy.ndarray, int, int, int, int)
        :param sub_template: the sub template
        :type threshold: float
        :param threshold: the threshold for the template matching algorithm
        :rtype: bool
        :return: returns True if sub template is found, False otherwise
        """
        try:
            rect = sub_rect[0]
            roi = sub_rect[1]

            res = self._info_manager.get_info("RESOLUTION")

            y1 = main_template_xy[1] + roi.y
            y2 = y1 + roi.height

            x1 = main_template_xy[0] + roi.x
            x2 = x1 + roi.width

            if roi.unlimited_up is True:
                y1 = 0
                y2 = main_template_xy[1] + roi.y + roi.height

            if roi.unlimited_down is True:
                y2 = res[1]

            if roi.unlimited_left is True:
                x1 = 0
                x2 = main_template_xy[0] + roi.x + roi.width

            if roi.unlimited_right is True:
                x2 = res[0]

            source_img_height, source_img_width, channels = self._source_image_color.shape

            if y1 < 0:
                y1 = 0
            elif y1 > source_img_height:
                y1 = source_img_height

            if y2 < 0:
                y2 = 0
            elif y2 > source_img_height:
                y2 = source_img_height

            if x1 < 0:
                x1 = 0
            elif x1 > source_img_width:
                x1 = source_img_width

            if x2 < 0:
                x2 = 0
            elif x2 > source_img_width:
                x2 = source_img_width

            #print x1,x2,y1,y2
            source_image_cropped = self._source_image_color[y1:y2, x1:x2]

            try:
                blue, green, red = cv2.split(source_image_cropped)
            except:
                if self._log_manager.is_log_enable() is True:
                    #self._log_manager.save_image(self.__find_log_folder, "error_sub_edges.png", edges)
                    self._log_manager.save_image(self.__find_log_folder, "error_sub_source_img.png", source_image_cropped)
                    #self._log_manager.save_image(self.__find_log_folder, "sub_edges.png", edges)
                    return None
            # Run canny edge detection on each channel
            blue_edges = self.__median_canny(blue, 0.2, 0.3)
            green_edges = self.__median_canny(green, 0.2, 0.3)
            red_edges = self.__median_canny(red, 0.2, 0.3)

            # Join edges back into image
            edges = blue_edges | green_edges | red_edges
            #edges = self.__median_canny(source_image_cropped, 0.2, 0.3)

            if self._log_manager.is_log_enable() is True:
                self._log_manager.save_image(self.__find_log_folder, "sub_source_img.png", source_image_cropped)
                self._log_manager.save_image(self.__find_log_folder, "sub_edges.png", edges)

            #self._sub_extra_imgages_log.append((edges.copy(), x1, y1))
            self.__timed_out_sub_extra_images.append((edges.copy(), (x1, y1)))

            # find the contours
            contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            #self._log_manager.save_image(self.__find_log_folder, "sub_canny.png", edges)

            if rect.width != 0 and rect.height != 0:
                rect.min_width = rect.max_width = rect.width
                rect.min_height = rect.max_height = rect.height

            if rect.width_tolerance != 0 and rect.width != 0 and rect.height != 0:
                rect.min_width = rect.min_width - rect.width_tolerance
                rect.max_width = rect.max_width + rect.width_tolerance

            if rect.height_tolerance != 0 and rect.width != 0 and rect.height != 0:
                rect.min_height = rect.min_height - rect.height_tolerance
                rect.max_height = rect.max_height + rect.height_tolerance

            rect_found = False

            # For each contour, find the bounding rectangle and draw it
            for c in reversed(contours):

                x, y, w, h = cv2.boundingRect(c)

                if(w >= rect.min_width and w <= rect.max_width and
                           h >= rect.min_height and h <= rect.max_height):

                    if self._log_manager.is_log_enable() is True:
                            img_copy = source_image_cropped.copy()
                            cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 0, 255), 2)
                            self._log_manager.save_image(self.__find_log_folder, "sub_object_found.png", img_copy)

                    #self._log_manager.add_sub_objects_points((x1 + x, y1 + y, w, h))

                    rect_found = True

                    sub_object_result = MatchResult((x1 + x, y1 + y, w, h))
                    return sub_object_result

            return None
        except Exception, err:
            self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
            return None


    def __median_canny(self, img, thresh1, thresh2):
        median = numpy.median(img)
        img = cv2.Canny(img, int(thresh1 * median), int(thresh2 * median))
        return img