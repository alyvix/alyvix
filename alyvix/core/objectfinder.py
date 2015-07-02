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

#from alyvix.core.basefinder import Roi
from alyvix.core.basefinder import *
#from alyvix.core.basefinder import MatchResult
#from alyvix.core.basefinder import BaseFinder
#from alyvix.core.imagefinder import ImageFinder
#from alyvix.core.textfinder import TextFinder
#from alyvix.core.rectfinder import RectFinder
from alyvix.tools.screenmanager import ScreenManager


class ObjectFinder(BaseFinder):

    #_main_object = None
    #_sub_objects = []
    #name = None

    def __init__(self, name=None):
        """
        init the class

        :type name: string
        :param name: the object name
        """

        self._main_object = None
        self._sub_objects = []

        the_name = "object_finder"

        if name is not None:
            the_name = name

        super(ObjectFinder, self).__init__(the_name)
        #BaseFinder.__init__(self, the_name)

    def set_main_object(self, main_object, roi_dict=None):
        """
        Set the template image that the find method has to find into the source Image.

        :type main_template: numpy.ndarray
        :param main_template: image of the template
        """

        self._main_object = (main_object, roi_dict)
        self.add_name_to_component(main_object, self._name)

    def add_sub_object(self, sub_object, roi_dict):

        self._sub_objects.append((sub_object, roi_dict))
        self.add_name_to_component(sub_object, self._name)

    def add_name_to_component(self, component, name):

        if isinstance(component, ObjectFinder):
            component.add_name_to_component(component._main_object[0], name)

            for component_sub_object_tuple in component._sub_objects:
                component_sub_object = component_sub_object_tuple[0]

                if isinstance(component_sub_object, ObjectFinder):
                    component_sub_object.add_name_to_component(component_sub_object._main_object[0], name)
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

    def find(self):

        self._objects_found = []

        main_object = self._main_object[0]

        if not isinstance(main_object, ObjectFinder):
            #main_object[1] = [1,1]
            if self._main_object[1] is not None:
                roi = Roi(self._main_object[1])
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

        if self._source_image_color is None or self._source_image_gray is None:

            screen_capture = ScreenManager()
            src_img_color = screen_capture.grab_desktop(screen_capture.get_color_mat)
            self.set_source_image_color(src_img_color)
            src_img_gray = cv2.cvtColor(src_img_color, cv2.COLOR_BGR2GRAY)
            self.set_source_image_gray(src_img_gray)
            main_object.set_source_image_color(self._source_image_color)
            main_object.set_source_image_gray(self._source_image_gray)

        objects_found = []

        main_object.find()

        cnt = 0
        for object in main_object._objects_found:

            if self._flag_thread_have_to_exit is True:
                main_object._flag_thread_have_to_exit = False
                main_object._flag_thread_started = False
                self._flag_thread_have_to_exit = False
                self._flag_thread_started = False
                return []

            object_found = []
            object_found.append([])
            object_found.append([])

            x = object[0].x
            y = object[0].y
            w = object[0].width
            h = object[0].height

            sub_objects_len = len(self._sub_objects)

            if sub_objects_len == 0:
                #good_points.append((x, y, w, h))

                main_object_result = MatchResult((x, y, w, h))
                object_found[0] = main_object_result

                object_found[1] = None
                objects_found.append(object_found)
            else:

                total_sub_object_found = 0

                sub_objects_found = []
                for sub_object in self._sub_objects:

                    if self._flag_thread_have_to_exit is True:
                        main_object._flag_thread_have_to_exit = False
                        main_object._flag_thread_started = False
                        self._flag_thread_have_to_exit = False
                        self._flag_thread_started = False
                        return []

                    sub_template_coordinates = self.find_sub_object((x, y), sub_object)

                    if sub_template_coordinates is not None:
                        sub_objects_found.append(sub_template_coordinates)
                        total_sub_object_found = total_sub_object_found + 1

                    if total_sub_object_found == sub_objects_len:
                        #good_points.append((x, y, w, h))

                        main_object_result = MatchResult((x, y, w, h))
                        object_found[0] = main_object_result

                        object_found[1] = sub_objects_found

                        objects_found.append(object_found)

            #self._log_manager.save_object_image("img_" + str(cnt) + ".png")
            cnt = cnt + 1

        if len(objects_found) > 0:
            self._objects_found = copy.deepcopy(objects_found)
            self._cacheManager.SetLastObjFoundFullImg(self._source_image_gray)

        self._flag_thread_started = False
        main_object._flag_thread_started = False

        self._source_image_color = None
        self._source_image_gray = None

        if self._flag_check_before_exit is True:
            self._flag_checked_before_exit = True

        return self._objects_found

    def find_sub_object(self, main_object_xy=None, sub_object=None):

        roi = Roi(sub_object[1])

        roi.x = main_object_xy[0] + roi.x
        roi.y = main_object_xy[1] + roi.y

        new_roi_dict = roi.get_dict()

        object = sub_object[0]

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
            object.set_main_object(object._main_object[0], roi.get_dict())

        object.set_source_image_color(self._source_image_color)
        object.set_source_image_gray(self._source_image_gray)

        object.find()

        return object.get_result(0)