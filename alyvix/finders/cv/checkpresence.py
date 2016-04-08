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
import sys
import numpy
import copy
import datetime
import time

from alyvix.tools.log import LogManager


class Roi():

    def __init__(self, roi_dict=None):

        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0

        if roi_dict is not None:
            self.set_roi_dict(roi_dict)

    def set_roi_dict(self, roi_dict):
        if ("roi_x" in roi_dict and "roi_y" in roi_dict and
                "roi_width" in roi_dict and "roi_height" in roi_dict):
            self.x = roi_dict['roi_x']
            self.y = roi_dict['roi_y']
            self.height = roi_dict['roi_height']
            self.width = roi_dict['roi_width']
        else:
            raise Exception("Roi dictionary has an incorrect format!")

    def get_dict(self):

        return {"roi_x": self.x, "roi_y": self.y, "roi_width": self.width, "roi_height": self.height}


class MatchResult():

    def __init__(self, coordinates_tuple):
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        self.set_coordinates(coordinates_tuple)

    def set_coordinates(self, coordinates_tuple):
        self.x = int(coordinates_tuple[0])
        self.y = int(coordinates_tuple[1])
        self.width = int(coordinates_tuple[2])
        self.height = int(coordinates_tuple[3])


class CheckPresence:

    def __init__(self, name=None):
        """
        init the class

        :type name: string
        :param name: the object name
        """

        self._main_component = None
        self.__sub_components = []
        self.__threshold = 0.8

        self._objects_finders_caller = []
        self._name_with_caller = None

        self._xy = None

        self._offset_x = 0
        self._offset_y = 0

        self._log_manager = None

        self.__enable_debug_calcperf = False

        if self.__enable_debug_calcperf is True:
            self._log_manager = LogManager()

        self._name = "check_presence"

        if name is not None:
            self._name = name

        if self.__enable_debug_calcperf is True:
            self._log_manager.set_object_name(self._name)

    def set_name(self, name):
        """
        set the name of the object.

        :type name: string
        :param name: the name of the object
        """
        self._name = name

        if self.__enable_debug_calcperf is True:
            self._log_manager.set_object_name(self._name)

    def get_name(self):
        """
        get the name of the object.

        :rtype: string
        :return: the name of the object
        """
        return self._name

    def set_xy(self, x, y):
        self._xy = (x, y)

    def set_source_image_color(self, image_data):
        """
        set the color image on which the find method will search the object.

        :type image_data: numpy.ndarray
        :param image_data: the color image
        """
        self._source_image_color = image_data.copy()
        #img_gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        #self.set_source_image_gray(img_gray)
        #self._log_manager.set_image(self._source_image)

    def set_source_image_gray(self, image_data, crop_properties = None):
        """
        set the gray image on which the find method will search the object.

        :type image_data: numpy.ndarray
        :param image_data: the gray image
        """
        if crop_properties is None:
            self._source_image_gray = image_data.copy()
        else:
            x1 = crop_properties[0]
            y1 = crop_properties[1]
            x2 = crop_properties[2]
            y2 = crop_properties[3]
            self._offset_x = crop_properties[0]
            self._offset_y = crop_properties[1]
            self._source_image_gray = image_data[y1:y2, x1:x2].copy()


    def set_main_component(self, image, roi_dict=None):
        """
        Set the template image that the find method has to find into the source Image.

        :type main_template: numpy.ndarray
        :param main_template: image of the template
        """

        if roi_dict is not None:
            roi = Roi(roi_dict)
        else:
            roi = None

        self._main_component = (image, roi)
        #print "main component:",self._main_component

    def add_sub_component(self, image, roi_dict):
        """
        Add a template that the find method has to find if it has also find the main template.
        A roi (region of interest) will be cropped from the source image according to the parameters
        roi_x, roi_y, roi_width and roi_height. roi_x and roi_y are relative to the main template x,y coordinates.
        The find method will search the sub template only inside the roi area.

        :type template_image: numpy.ndarray
        :param template_image: image of the template
        :type roi_x: int
        :param roi_x: x-coordinate of roi
        :type roi_y: int
        :param roi_y: y-coordinate of roi
        :type roi_width: int
        :param roi_width: roi width
        :type roi_height: int
        :param roi_height: roi height
        """
        roi = Roi(roi_dict)
        self.__sub_components.append((image, roi))

    def _SetThreshold(self, threshold):
        """
        Set the threshold of template matching algorithm. Min value is 0.0, max value is 1.0
        threshold=1.0 means that the source image must contain an exact copy of the template image.
        threshold=0.0 means that the source image can even not contain the template (with the risk
        of false positives).
        The default value for the threshold is 0.7

        :type threshold: float
        :param threshold: threshold value for template matching algorithm
        """
        self.__threshold = threshold

    def find(self):
        """
        find the main template and sub templates into the source image.

        :rtype: bool
        :return: return true if object is present into the image
        """
        try:

            #print "main comp:",self._main_component

            source_img_auto_set = False

            self._objects_found = []

            if self.__enable_debug_calcperf is True:
                self.__find_log_folder = datetime.datetime.now().strftime("%H_%M_%S") + "_" + "searching"

            offset_x = 0
            offset_y = 0


            main_template = self._main_component[0]
            #print "main templ:", main_template
            roi = self._main_component[1]

            if roi is not None:

                y1 = roi.y - self._offset_y
                y2 = y1 + roi.height
                x1 = roi.x - self._offset_x
                x2 = x1 + roi.width

                offset_x = x1
                offset_y = y1

                if offset_x < 0:
                    offset_x = 0

                if offset_y < 0:
                    offset_y = 0

                source_img_height, source_img_width = self._source_image_gray.shape

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
                source_image = self._source_image_gray[y1:y2, x1:x2]
            else:
                source_image = self._source_image_gray


            if self.__enable_debug_calcperf is True:
                self._log_manager.save_image(self.__find_log_folder, "source_img.png", source_image)
                self._log_manager.save_image(self.__find_log_folder, "main_template.png", main_template)


            objects_found = []
            analyzed_points = []
            self._objects_found = []

            w, h = main_template.shape[::-1]
            src_w, src_h = source_image.shape[::-1]
            tpl_w = w
            tpl_h = h

            if src_h < tpl_h or src_w < tpl_w:
                self._flag_thread_have_to_exit = False
                self._flag_thread_started = False
                self._source_image_gray = None
                self._source_image_color = None
                return []

            res = cv2.matchTemplate(source_image, main_template, cv2.TM_CCOEFF_NORMED)

            loc = numpy.where(res >= self.__threshold)

            cnt = 0
            for point in zip(*loc[::-1]):

                object_found = []
                object_found.append([])
                object_found.append([])

                x = offset_x + point[0]
                y = offset_y + point[1]

                tolerance_region = 5

                if not ((x >= self._xy[0] - tolerance_region and
                            x <= self._xy[0] + tolerance_region) and \
                        (y >= self._xy[1] - tolerance_region and
                                 y <= self._xy[1] + tolerance_region)):
                        continue

                #self._log_manager.set_main_object_points((x, y, w, h))

                if self.__enable_debug_calcperf is True:
                    img_copy = source_image.copy()
                    cv2.rectangle(img_copy, ((x-offset_x), (y-offset_y)), ((x-offset_x)+w, (y-offset_y)+h), (0, 0, 255), 2)
                    self._log_manager.save_image(self.__find_log_folder, "object_found.png", img_copy)

                sub_templates_len = len(self.__sub_components)

                if sub_templates_len == 0:
                    main_object_result = MatchResult((x, y, w, h))
                    object_found[0] = main_object_result
                    object_found[1] = None
                    return True
                else:
                    #print sub_templates_len
                    total_sub_template_found = 0
                    sub_objects_found = []
                    for sub_template in self.__sub_components:

                        sub_template_coordinates = self._find_sub_template((x, y), sub_template)

                        if sub_template_coordinates is not None:
                            sub_objects_found.append(sub_template_coordinates)
                            total_sub_template_found = total_sub_template_found + 1

                        if total_sub_template_found == sub_templates_len:
                            #good_points.append((x, y, w, h))

                            main_object_result = MatchResult((x, y, w, h))
                            object_found[0] = main_object_result

                            object_found[1] = sub_objects_found

                            #objects_found.append(object_found)
                            return True

                #self._log_manager.save_object_image("img_" + str(cnt) + ".png")
                cnt = cnt + 1

            #if len(objects_found) > 0:
            #    return True

        except Exception, err:
            self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))

        return False


    def _find_sub_template(self, main_template_xy=None, sub_template=None):
        """
        find sub templates into the source image.

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

            template = sub_template[0]
            roi = sub_template[1]

            y1 = main_template_xy[1] + roi.y
            y2 = y1 + roi.height
            x1 = main_template_xy[0] + roi.x
            x2 = x1 + roi.width

            source_img_height, source_img_width = self._source_image_gray.shape

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
            source_image_cropped = self._source_image_gray[y1:y2, x1:x2]

            if self.__enable_debug_calcperf is True:
                self._log_manager.save_image(self.__find_log_folder, "sub_source_img.png", source_image_cropped)
                self._log_manager.save_image(self.__find_log_folder, "sub_template.png", template)


            img_w, img_h = source_image_cropped.shape[::-1]
            tmpl_w, tmpl_h = template.shape[::-1]

            if tmpl_h >= img_h or tmpl_w >= img_w:
                return False

            res = cv2.matchTemplate(source_image_cropped, template, cv2.TM_CCOEFF_NORMED)

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if max_val >= self.__threshold:
                point = max_loc

                x = point[0]
                y = point[1]

                if self.__enable_debug_calcperf is True:
                    img_copy = source_image_cropped.copy()
                    cv2.rectangle(img_copy, (x, y), (x+tmpl_w, y+tmpl_h), (0, 0, 255), 2)
                    self._log_manager.save_image(self.__find_log_folder, "sub_object_found.png", img_copy)

                sub_object_result = MatchResult((x1 + x, y1 + y, tmpl_w, tmpl_h))
                return sub_object_result

            return None
        except Exception, err:
            self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
            return None
