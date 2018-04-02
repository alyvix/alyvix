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
import time
import datetime

from alyvix.finders.cv.basefinder import BaseFinder
from alyvix.finders.cv.basefinder import Roi
from alyvix.finders.cv.basefinder import MatchResult
from alyvix.tools.screen import ScreenManager
from alyvix.tools.info import InfoManager


class _Template():

    def __init__(self, template_dict):
        self._info_manager = InfoManager()
        self.image_data = None
        self.threshold = 0.7
        self.hist_red = None
        self.hist_green = None
        self.hist_blue = None
        self.match_colors = False
        self._set_template_dictionary(template_dict)


    def _set_template_dictionary(self, template_dict):
        """
        converts the dictionary into the rectangles properties

        :type rect_dict: dict
        :param rect_dict: the dictionary that defines the sub rectangle
        """

        if "path" in template_dict and "threshold" in template_dict:
            self.image_data = cv2.imread(template_dict['path'])

            if str(self._info_manager.get_info('channel')).lower() != 'all':
                img_b, img_g, img_r = cv2.split(self.image_data)

                if str(self._info_manager.get_info('channel')).lower() == 'b':
                    self.image_data = cv2.cvtColor(img_b, cv2.COLOR_GRAY2BGR)
                elif str(self._info_manager.get_info('channel')).lower() == 'g':
                    self.image_data = cv2.cvtColor(img_g, cv2.COLOR_GRAY2BGR)
                elif str(self._info_manager.get_info('channel')).lower() == 'r':
                    self.image_data = cv2.cvtColor(img_r, cv2.COLOR_GRAY2BGR)

            try:
                self.match_colors = template_dict['match_colors']
            except:
                pass

            self.hist_blue = cv2.calcHist([self.image_data],[0],None,[256],[0,256])
            self.hist_green = cv2.calcHist([self.image_data], [1], None, [256], [0, 256])
            self.hist_red = cv2.calcHist([self.image_data], [2], None, [256], [0, 256])
            self.hist_rgb = hist = cv2.calcHist([self.image_data], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            self.hist_rgb = cv2.normalize(self.hist_rgb).flatten()

            self.image_data = cv2.cvtColor(self.image_data, cv2.COLOR_BGR2GRAY)

            self.threshold = template_dict['threshold']
        else:
            raise Exception("Template dictionary has an incorrect format!")


class ImageFinder(BaseFinder):

    def __init__(self, name=None):
        """
        init the class

        :type name: string
        :param name: the object name
        """

        #self._main_component = None
        #self._sub_components = []
        self.is_textfinder = False
        self.__threshold = 0.7
        self.__timed_out_sub_extra_images = []

        self._info_manager = InfoManager()
        self._overlapping_factor = self._info_manager.get_info("OVERLAPPING TOLERANCE FACTOR")

        try:
            self._overlapping_factor = int(self._overlapping_factor)
        except:
            self._overlapping_factor = 10

        the_name = "template_finder"

        if name is not None:
            the_name = name

        super(ImageFinder, self).__init__(the_name)
       # BaseFinder.__init__(self, the_name)

    def set_main_component(self, template_dict, roi_dict=None):
        """
        Set the template image that the find method has to find into the source Image.

        :type main_template: numpy.ndarray
        :param main_template: image of the template
        """
        main_template = _Template(template_dict)

        if roi_dict is not None:
            roi = Roi(roi_dict)
        else:
            roi = None

        self._main_component = (main_template, roi)
        #print "main component:",self._main_component

    def add_sub_component(self, template_dict, roi_dict):
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
        sub_template = _Template(template_dict)
        self._sub_components.append((sub_template, roi))

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

        :rtype: list[(int, int, int, int)]
        :return: x, y, height, width of main template(s)
        """
        #tzero = time.time()
        time_before_find = time.time()
        try:

            #x = 1 / 0

            #print "main comp:",self._main_component

            self._timedout_main_components = []
            self._timedout_sub_components = []

            self._main_extra_img_log = None
            self._sub_extra_imgages_log = []

            source_img_auto_set = False

            self._objects_found = []

            if self._source_image_gray is None or self._source_image_color is None:
                screen_capture = ScreenManager()
                src_img_color = screen_capture.grab_desktop(screen_capture.get_color_mat)
                self.set_source_image_color(src_img_color)
                src_img_gray = cv2.cvtColor(src_img_color, cv2.COLOR_BGR2GRAY)
                self.set_source_image_gray(src_img_gray)
                source_img_auto_set = True

            if str(self._info_manager.get_info('channel')).lower() != 'all':
                img_b, img_g, img_r = cv2.split(self._source_image_color)

                if str(self._info_manager.get_info('channel')).lower() == 'b':
                    self._source_image_color = cv2.cvtColor(img_b, cv2.COLOR_GRAY2BGR)
                elif str(self._info_manager.get_info('channel')).lower() == 'g':
                    self._source_image_color = cv2.cvtColor(img_g, cv2.COLOR_GRAY2BGR)
                elif str(self._info_manager.get_info('channel')).lower() == 'r':
                    self._source_image_color = cv2.cvtColor(img_r, cv2.COLOR_GRAY2BGR)

                self._source_image_gray = cv2.cvtColor(self._source_image_color , cv2.COLOR_BGR2GRAY)

            self.__find_log_folder = datetime.datetime.now().strftime("%H_%M_%S") + "_" + "searching"

            offset_x = 0
            offset_y = 0


            main_template = self._main_component[0]
            #print "main templ:", main_template
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


            if self._log_manager.is_log_enable() is True:
                self._log_manager.save_image(self.__find_log_folder, "source_img.png", source_image)
                self._log_manager.save_image(self.__find_log_folder, "main_template.png", main_template.image_data)

            #self._timed_out_images.append(source_image.copy())

            objects_found = []
            analyzed_points = []
            self._objects_found = []

            w, h = main_template.image_data.shape[::-1]
            src_w, src_h = source_image.shape[::-1]
            tpl_w = w
            tpl_h = h

            if src_h < tpl_h or src_w < tpl_w:
                self._flag_thread_have_to_exit = False
                """
                self._flag_thread_started = False
                self._source_image_gray = None
                self._source_image_color = None
                """
                return []

            result = None

            res = cv2.matchTemplate(source_image, main_template.image_data, cv2.TM_CCOEFF_NORMED)
            #min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resacascascsacas)

            res_norm = (res *255).round().clip(min=0).astype(numpy.uint8) #numpy.array(res * 255, dtype = numpy.float32) #(res * 255) #.round().astype(numpy.int8)
            res_norm = cv2.resize(res_norm,(source_image.shape[1], source_image.shape[0]), interpolation = cv2.INTER_CUBIC)

            #cv2.imwrite("c:\\log\\res_norm.png",res_norm)
            #cv2.imwrite("c:\\log\\res.png",res)

            #res_norm.resize(res_norm.shape[0], res_norm.shape[0], 3L, refcheck=False)

            if roi is not None:
                self._main_extra_img_log = (res_norm, (x1, y1, x2, y2))
            else:
                self._main_extra_img_log = (res_norm, None)

            loc = numpy.where(res >= main_template.threshold)

            cnt = 0
            for point in zip(*loc[::-1]):

                object_found = []
                object_found.append([])
                object_found.append([])
                self.__timed_out_sub_extra_images = []

                """
                if self._flag_thread_have_to_exit is True:
                    self._flag_thread_have_to_exit = False
                    self._flag_thread_started = False
                    self._source_image_gray = None
                    self._source_image_color = None
                    return []
                """

                x = offset_x + point[0]
                y = offset_y + point[1]

                is_already_found = False

                for point_already_analyzed in analyzed_points:

                    #tolerance_region_w = (tpl_w/2)  + (20 * self._scaling_factor)
                    #tolerance_region_h = (tpl_h/2) + (20 * self._scaling_factor)

                    tolerance_region_w = (tpl_w/2)  + (self._overlapping_factor * self._scaling_factor)
                    tolerance_region_h = (tpl_h/2) + (self._overlapping_factor * self._scaling_factor)

                    if (x >= point_already_analyzed[0] - tolerance_region_w and
                                x <= point_already_analyzed[0] + tolerance_region_w) and\
                            (y >= point_already_analyzed[1] - tolerance_region_h and
                                     y <= point_already_analyzed[1] + tolerance_region_h):

                        is_already_found = True
                        #print point[0],point_already_analyzed[0],point[1],point_already_analyzed[1]

                if is_already_found == False:

                    #hist_blue = cv2.calcHist([self._source_image_color[y:y+h, x:x+w]], [0], None, [256], [0, 256])
                    #hist_green = cv2.calcHist([self._source_image_color[y:y+h, x:x+w]], [1], None, [256], [0, 256])
                    #hist_red = cv2.calcHist([self._source_image_color[y:y+h, x:x+w]], [2], None, [256], [0, 256])

                    hist_rgb = cv2.calcHist([self._source_image_color[y:y+h, x:x+w]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    hist_rgb = cv2.normalize(hist_rgb).flatten()

                    #comp_blue = cv2.compareHist(hist_blue,main_template.hist_blue,cv2.cv.CV_COMP_BHATTACHARYYA)
                    #comp_green = cv2.compareHist(hist_green, main_template.hist_green, cv2.cv.CV_COMP_BHATTACHARYYA)
                    #comp_red = cv2.compareHist(hist_red, main_template.hist_red, cv2.cv.CV_COMP_BHATTACHARYYA)
                    comp_rgb = cv2.compareHist(hist_rgb, main_template.hist_rgb, cv2.cv.CV_COMP_BHATTACHARYYA)

                    analyzed_points.append((x, y, w, h))


                    #if (comp_blue > 0.3 or comp_green > 0.3 or comp_red > 0.3) and main_template.match_colors is True:
                    if comp_rgb > 0.2 and main_template.match_colors is True:
                        continue

                    self._timedout_main_components.append(MatchResult((x, y, w, h)))

                    #self._log_manager.set_main_object_points((x, y, w, h))
                    if self._log_manager.is_log_enable() is True:
                        img_copy = source_image.copy()
                        cv2.rectangle(img_copy, ((x-offset_x), (y-offset_y)), ((x-offset_x)+w, (y-offset_y)+h), (0, 0, 255), 2)
                        self._log_manager.save_image(self.__find_log_folder, "object_found.png", img_copy)

                    sub_templates_len = len(self._sub_components)

                    if sub_templates_len == 0:
                        main_object_result = MatchResult((x, y, w, h))
                        object_found[0] = main_object_result
                        object_found[1] = None
                        objects_found.append(object_found)
                    else:
                        #print sub_templates_len
                        total_sub_template_found = 0
                        sub_objects_found = []
                        timed_out_objects = []
                        timed_out_sub_extra_images = []
                        for sub_template in self._sub_components:

                            """
                            if self._flag_thread_have_to_exit is True:
                                self._flag_thread_have_to_exit = False
                                self._flag_thread_started = False
                                self._source_image_gray = None
                                self._source_image_color = None
                                return []
                            """

                            sub_template_coordinates = self._find_sub_template((x, y), sub_template)

                            if sub_template_coordinates is not None:
                                sub_objects_found.append(sub_template_coordinates)
                                total_sub_template_found = total_sub_template_found + 1
                                timed_out_objects.append((sub_template_coordinates, sub_template[1]))
                            else:
                                timed_out_objects.append((None, sub_template[1]))

                            #timed_out_sub_extra_images.append()

                            if total_sub_template_found == sub_templates_len:
                                #good_points.append((x, y, w, h))

                                main_object_result = MatchResult((x, y, w, h))
                                object_found[0] = main_object_result

                                object_found[1] = sub_objects_found

                                objects_found.append(object_found)
                        self._timedout_sub_components.append(timed_out_objects)
                        self._sub_extra_imgages_log.append(self.__timed_out_sub_extra_images)
                    #self._log_manager.save_object_image("img_" + str(cnt) + ".png")
                cnt = cnt + 1

            if len(objects_found) > 0:
                self._objects_found = copy.deepcopy(objects_found)
                if self._is_object_finder is True:
                    self._objects_found_of_sub_object_finder.extend(copy.deepcopy(objects_found))
                    #if wait_disappear is False:

                    #if self._info_manager.get_info('LOG OBJ IS FOUND') is False:
                    if self._info_manager.get_info('LOG OBJ FINDER TYPE') is None:
                        self._info_manager.set_info('LOG OBJ FINDER TYPE', 0)

                    self._log_manager.save_objects_found(self._name, self.get_source_image_gray(),
                                                         self._objects_found, [x[1] for x in self._sub_components],
                                                         self.main_xy_coordinates, self.sub_xy_coordinates, finder_type=0)

                self._cacheManager.SetLastObjFoundFullImg(self._source_image_gray)

            if source_img_auto_set is True:
                self._source_image_gray = None
                self._source_image_color = None
                source_img_auto_set = False

            """
            if self._flag_check_before_exit is True:
                self._flag_checked_before_exit = True
            """

            #time.sleep(40)

            self._flag_thread_started = False

            if  self._calc_last_finder_time is True:
                self._last_finder_time = time.time() - time_before_find
                self._calc_last_finder_time = False

            #print time.time() - tzero

            return self._objects_found

        except Exception, err:
            self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
            self._flag_thread_started = False
            return []


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

            objects_found = []
            analyzed_points = []

            template = sub_template[0]
            roi = sub_template[1]

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
            source_image_cropped_color = self._source_image_color[y1:y2, x1:x2]

            if self._log_manager.is_log_enable() is True:
                self._log_manager.save_image(self.__find_log_folder, "sub_source_img.png", source_image_cropped)
                self._log_manager.save_image(self.__find_log_folder, "sub_template.png", template.image_data)

            img_w, img_h = source_image_cropped.shape[::-1]
            tmpl_w, tmpl_h = template.image_data.shape[::-1]

            if tmpl_h >= img_h or tmpl_w >= img_w:
                return None

            res = cv2.matchTemplate(source_image_cropped, template.image_data, cv2.TM_CCOEFF_NORMED)

            res_norm = (res *255).round().clip(min=0).astype(numpy.uint8) #numpy.array(res * 255, dtype = numpy.float32) #(res * 255) #.round().astype(numpy.int8)
            res_norm = cv2.resize(res_norm,(source_image_cropped.shape[1], source_image_cropped.shape[0]), interpolation = cv2.INTER_CUBIC)


            #res_norm.resize(res_norm.shape[0], res_norm.shape[1], 3L, refcheck=False)

            self.__timed_out_sub_extra_images.append((res_norm, (x1, y1)))

            #min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            loc = numpy.where(res >= template.threshold)

            cnt = 0
            for point in zip(*loc[::-1]):


                #if max_val >= template.threshold:

                x = point[0]
                y = point[1]

                is_already_found = False

                for point_already_analyzed in analyzed_points:

                    # tolerance_region_w = (tpl_w/2)  + (20 * self._scaling_factor)
                    # tolerance_region_h = (tpl_h/2) + (20 * self._scaling_factor)

                    tolerance_region_w = (tmpl_w / 2) + (self._overlapping_factor * self._scaling_factor)
                    tolerance_region_h = (tmpl_h / 2) + (self._overlapping_factor * self._scaling_factor)

                    if (x >= point_already_analyzed[0] - tolerance_region_w and
                                x <= point_already_analyzed[0] + tolerance_region_w) and \
                            (y >= point_already_analyzed[1] - tolerance_region_h and
                                     y <= point_already_analyzed[1] + tolerance_region_h):
                        is_already_found = True
                        # print point[0],point_already_analyzed[0],point[1],point_already_analyzed[1]

                if is_already_found == False:

                    #hist_blue = cv2.calcHist(self._source_image_color[y1 + y:y1 + y + tmpl_h, x1 + x:x1 + x + tmpl_w], [0], None, [256], [0, 256])
                    #hist_green = cv2.calcHist(self._source_image_color[y1 + y:y1 + y + tmpl_h, x1 + x:x1 + x + tmpl_w], [1], None, [256], [0, 256])
                    #hist_red = cv2.calcHist(self._source_image_color[y1 + y:y1 + y + tmpl_h, x1 + x:x1 + x + tmpl_w], [2], None, [256], [0, 256])

                    hist_rgb = cv2.calcHist([self._source_image_color[y1 + y:y1 + y + tmpl_h, x1 + x:x1 + x + tmpl_w]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    hist_rgb = cv2.normalize(hist_rgb).flatten()

                    #comp_blue = cv2.compareHist(hist_blue, template.hist_blue, cv2.cv.CV_COMP_BHATTACHARYYA)
                    #comp_green = cv2.compareHist(hist_green, template.hist_green, cv2.cv.CV_COMP_BHATTACHARYYA)
                    #comp_red = cv2.compareHist(hist_red, template.hist_red, cv2.cv.CV_COMP_BHATTACHARYYA)
                    comp_rgb = cv2.compareHist(hist_rgb, template.hist_rgb, cv2.cv.CV_COMP_BHATTACHARYYA)

                    analyzed_points.append((x, y, img_w, img_h))

                    #if (comp_blue > 0.3 or comp_green > 0.3 or comp_red > 0.3) and template.match_colors is True:
                    if comp_rgb > 0.2  and template.match_colors is True:
                        continue

                    if self._log_manager.is_log_enable() is True:
                        img_copy = source_image_cropped.copy()
                        cv2.rectangle(img_copy, (x, y), (x+tmpl_w, y+tmpl_h), (0, 0, 255), 2)
                        self._log_manager.save_image(self.__find_log_folder, "sub_object_found.png", img_copy)

                    sub_object_result = MatchResult((x1 + x, y1 + y, tmpl_w, tmpl_h))
                    return sub_object_result

            return None
        except Exception, err:
            self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
            return None
