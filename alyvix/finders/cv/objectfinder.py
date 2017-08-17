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

import os
import cv2
import numpy
import copy
import datetime
import inspect

#from alyvix.finders.basefinder import Roi
from alyvix.finders.cv.basefinder import *
from alyvix.tools.screen import ScreenManager
from distutils.sysconfig import get_python_lib


class ObjectFinder(BaseFinder):

    #_main_component = None
    #_sub_components = []
    #name = None

    def __init__(self, name=None):
        """
        init the class

        :type name: string
        :param name: the object name
        """

        self.is_textfinder = False

        #self._main_component = None
        #self._sub_components = []
        self._sub_components_scraper = []

        self._main_indexes_to_keep = []
        self._sub_indexes_to_keep = []

        self._scraped_text = ""

        the_name = "object_finder"

        if name is not None:
            the_name = name

        super(ObjectFinder, self).__init__(the_name)
        #BaseFinder.__init__(self, the_name)

        self._is_object_finder = True

    def set_main_object(self, main_object, roi_dict=None):
        """
        Set the template image that the find method has to find into the source Image.

        :type main_template: numpy.ndarray
        :param main_template: image of the template
        """

        main_object._is_object_finder = True

        self._main_component = (main_object, roi_dict)
        self.add_name_to_component(main_object, self._name)

        #self._is_object_finder = True

    def add_sub_object(self, sub_object, roi_dict):

        roi = Roi(roi_dict)

        sub_object._is_object_finder = True

        self._sub_components.append((sub_object, roi))

        suite_source = self._info_manager.get_info('SUITE SOURCE')
        suite_source = suite_source.split("\\")[-1]
        suite_source = suite_source.split(".")[0]

        if suite_source != None:
            extra_path_old = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + \
                         "Alyvix" + suite_source + "Objects_extra"
            scraper_old_path = extra_path_old + os.sep + sub_object.get_name()
            scraper_old_file = scraper_old_path + os.sep + "scraper.txt"

            proxy_file = inspect.stack()
            proxy_file = proxy_file[1]
            proxy_file = proxy_file[1]
            proxy_file = proxy_file.split(os.sep)[-1]
            proxy_file = proxy_file.split('.')[0]
            proxy_file = proxy_file.replace("AlyvixProxy","")

            extra_path = get_python_lib() + os.sep + "alyvix" + os.sep + "robotproxy" + os.sep + \
                         "Alyvix" + proxy_file + "Objects_extra"
            scraper_path = extra_path + os.sep + sub_object.get_name()
            scraper_file = scraper_path + os.sep + "scraper.txt"

        else:
            scraper_old_path = sub_object.get_name()
            scraper_old_file = scraper_old_path + os.sep + "scraper.txt"


        if os.path.exists(scraper_old_file) or os.path.exists(scraper_file):

            self._sub_components_scraper.append(True)
        else:
            self._sub_components_scraper.append(False)

        self.add_name_to_component(sub_object, self._name)

    def add_name_to_component(self, component, name):

        if isinstance(component, ObjectFinder):
            component.add_name_to_component(component._main_component[0], name)

            for component_sub_object_tuple in component._sub_components:
                component_sub_object = component_sub_object_tuple[0]

                if isinstance(component_sub_object, ObjectFinder):
                    component_sub_object.add_name_to_component(component_sub_object._main_component[0], name)
                else:
                    name_already_present = False

                    for object_finder_caller in component_sub_object._objects_finders_caller:
                        if name == object_finder_caller:
                            name_already_present = True

                    if name_already_present is False:
                        component_sub_object._objects_finders_caller.append(name)
                        #object_called.set_name(object_called.get_name())

                        component_sub_object.set_name_with_caller()
        else:

            name_already_present = False

            for object_finder_caller in component._objects_finders_caller:
                if name == object_finder_caller:
                    name_already_present = True

            if name_already_present is False:
                component._objects_finders_caller.append(name)
                #object_called.set_name(object_called.get_name())

                component.set_name_with_caller()

    def get_scraped_text(self):

        sc_collection = self._info_manager.get_info('SCRAPER COLLECTION')
        sc_collection.append((self.get_name(), self.timestamp, self._scraped_text))

        self._info_manager.set_info('SCRAPER COLLECTION', sc_collection)

        return self._scraped_text

    def find(self):

        self._info_manager.set_info('last log image order', 0)
        self._info_manager.set_info('LOG OBJ FINDER COLOR COUNTER', 0)

        time_before_find = time.time()

        for sub_object in self._sub_components:
            sub_object[0]._objects_found_of_sub_object_finder = []

        self._timedout_main_components = []
        self._timedout_sub_components = []

        self._objects_found = []

        main_object = self._main_component[0]

        if not isinstance(main_object, ObjectFinder):
            #main_object[1] = [1,1]
            if self._main_component[1] is not None:
                roi = Roi(self._main_component[1])
            else:
                roi = None

            main_component = main_object._main_component[0]
            main_object._main_component = (main_component, roi)

            """
            if isinstance(main_object, RectFinder):
                main_rect = main_object._main_rect[0]
                main_object._main_rect = (main_rect, roi)

            elif isinstance(main_object, ImageFinder):
                main_template = main_object._main_template[0]
                main_object._main_template = (main_template, roi)

            elif isinstance(main_object, TextFinder):
                main_text = main_object._main_text[0]
                main_object._main_text = (main_text, roi)
            """

        source_img_auto_set = False

        if self._source_image_color is None or self._source_image_gray is None:

            screen_capture = ScreenManager()
            src_img_color = screen_capture.grab_desktop(screen_capture.get_color_mat)
            self.set_source_image_color(src_img_color)
            src_img_gray = cv2.cvtColor(src_img_color, cv2.COLOR_BGR2GRAY)
            self.set_source_image_gray(src_img_gray)
            #main_object.set_source_image_color(self._source_image_color)
            #main_object.set_source_image_gray(self._source_image_gray)
            source_img_auto_set = True

        main_object.set_source_image_color(self._source_image_color)
        main_object.set_source_image_gray(self._source_image_gray)

        objects_found = []

        main_object.find()

        #self._info_manager.set_info(1)

        cnt = 0
        for object in main_object._objects_found:

            self._info_manager.set_info('LOG OBJ FINDER COLOR COUNTER', 1)

            #self._info_manager.set_info('LOG OBJ FINDER COLOR COUNTER', 0)


            """
            if self._flag_thread_have_to_exit is True:
                main_object._flag_thread_have_to_exit = False
                main_object._flag_thread_started = False
                self._flag_thread_have_to_exit = False
                self._flag_thread_started = False
                return []
            """

            object_found = []
            object_found.append([])
            object_found.append([])

            x = object[0].x
            y = object[0].y
            w = object[0].width
            h = object[0].height

            sub_objects_len = len(self._sub_components)

            self._timedout_main_components.append(MatchResult((x, y, w, h)))

            if sub_objects_len == 0:
                #good_points.append((x, y, w, h))

                main_object_result = MatchResult((x, y, w, h))
                object_found[0] = main_object_result

                object_found[1] = None
                objects_found.append(object_found)
                self._main_indexes_to_keep.append(cnt)
            else:

                total_sub_object_found = 0

                sub_objects_found = []
                timed_out_objects = []
                cnt_sub_obj = 0

                for sub_object in self._sub_components:

                    """
                    if self._flag_thread_have_to_exit is True:
                        main_object._flag_thread_have_to_exit = False
                        main_object._flag_thread_started = False
                        self._flag_thread_have_to_exit = False
                        self._flag_thread_started = False
                        return []
                    """

                    #sub_object._objects_found = []

                    if self._sub_components_scraper[cnt_sub_obj] == True:
                        (self._scraped_text,sub_template_coordinates) = self.find_sub_object((x, y), sub_object, scraper=True)

                    else:
                        sub_template_coordinates = copy.deepcopy(self.find_sub_object((x, y), sub_object))

                    self._info_manager.set_info('LOG OBJ FINDER COLOR COUNTER',
                                                self._info_manager.get_info('LOG OBJ FINDER COLOR COUNTER') + 1)

                    if self._info_manager.get_info('LOG OBJ FINDER COLOR COUNTER') >= \
                            len(self._info_manager.get_info('LOG OBJ FINDER FILL COLOR')):
                        self._info_manager.set_info('LOG OBJ FINDER COLOR COUNTER', 0)

                    if sub_template_coordinates is not None:
                        sub_objects_found.append(sub_template_coordinates)
                        timed_out_objects.append((sub_template_coordinates, sub_object[1]))
                        total_sub_object_found = total_sub_object_found + 1
                    else:
                        timed_out_objects.append((None, sub_object[1]))

                    if total_sub_object_found == sub_objects_len:
                        #good_points.append((x, y, w, h))

                        main_object_result = MatchResult((x, y, w, h))
                        object_found[0] = main_object_result

                        object_found[1] = sub_objects_found

                        objects_found.append(object_found)
                        self._main_indexes_to_keep.append(cnt)

                    cnt_sub_obj += 1

                self._timedout_sub_components.append(timed_out_objects)
            #self._log_manager.save_object_image("img_" + str(cnt) + ".png")
            cnt = cnt + 1

        if len(objects_found) > 0:
            self._info_manager.set_info('LOG OBJ IS FOUND', True)
            self._objects_found = copy.deepcopy(objects_found)
            main_object.rebuild_result(self._main_indexes_to_keep)
            self.rebuild_result_for_sub_component(self._main_indexes_to_keep)
            self._cacheManager.SetLastObjFoundFullImg(self._source_image_gray)

        #self._source_image_color = None
        #self._source_image_gray = None

        if source_img_auto_set is True:
            self._source_image_gray = None
            self._source_image_color = None
            source_img_auto_set = False

        """
        if self._flag_check_before_exit is True:
            self._flag_checked_before_exit = True
            #print "self._flag_checked_before_exit = True"
            #print self._time_checked_before_exit_start
        """

        self._flag_thread_started = False
        main_object._flag_thread_started = False

        if self._calc_last_finder_time is True:
            self._last_finder_time = time.time() - time_before_find
            self._calc_last_finder_time = False

        return self._objects_found

    def find_sub_object(self, main_object_xy=None, sub_object=None, scraper=False):

        roi = copy.deepcopy(sub_object[1]) #roi = Roi(sub_object[1])

        roi.x = main_object_xy[0] + roi.x
        roi.y = main_object_xy[1] + roi.y

        new_roi_dict = roi.get_dict()

        object = sub_object[0]

        object._is_object_finder = True

        #object._objects_found = []

        if not isinstance(object, ObjectFinder):

            main_component = object._main_component[0]
            object._main_component = (main_component, roi)

            """
            if isinstance(object, RectFinder):
                main_rect = object._main_rect[0]
                object._main_rect = (main_rect, roi)

            elif isinstance(object, ImageFinder):
                main_template = object._main_template[0]
                object._main_template = (main_template, roi)

            elif isinstance(object, TextFinder):
                main_text = object._main_text[0]
                object._main_text = (main_text, roi)
            """
        else:
            pass
            object.set_main_component(object._main_component[0], roi.get_dict())

        object.set_source_image_color(self._source_image_color)
        object.set_source_image_gray(self._source_image_gray)

        if scraper is True:

            return (object.scraper(), MatchResult((roi.x, roi.y, roi.width, roi.height)))

        object_old_results = copy.deepcopy(object._objects_found)
        object.find()

        #print "sub_obj", object._objects_found
        result = object.get_result(0)

        if result is None:
            object._objects_found = copy.deepcopy(object_old_results)

        return result