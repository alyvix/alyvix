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
import sys
import time
import copy
from threading import Thread

import cv2
import numpy

from alyvix.tools.log import LogManager
from alyvix.tools.screen import ScreenManager
from alyvix.tools.configreader import ConfigReader
from alyvix.finders.cachemanager import CacheManager

#from alyvix.tools.


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


class BaseFinder(object):


    def __init__(self, name=None):
        """
        init the class

        :type name: string
        :param name: the object name
        """

        self._source_image_color = None
        self._source_image_gray = None
        self._objects_found = []
        self._log_manager = None

        #variables for the perfdata
        self._cacheManager = None
        self._min_different_contours = 15
        self._flag_thread_started = False
        self._flag_check_before_exit = False
        self._flag_checked_before_exit = False
        self._flag_thread_have_to_exit = False
        self._screen_capture = None
        #end perfdata section

        self._time_checked_before_exit_start = 0

        self._objects_finders_caller = []
        self._name_with_caller = None

        self._name = name
        self._log_manager = LogManager()
        self._log_manager.set_object_name(self._name)
        self._screen_capture = ScreenManager()
        self._cacheManager = CacheManager()
        self._configReader = ConfigReader()

    def set_name(self, name):
        """
        set the name of the object.

        :type name: string
        :param name: the name of the object
        """
        self._name = name
        self._log_manager.set_object_name(self._name)

    def get_name(self):
        """
        get the name of the object.

        :rtype: string
        :return: the name of the object
        """
        return self._name

    def set_name_with_caller(self):

        tmp_name = self._name

        for object_caller in self._objects_finders_caller:
            tmp_name = object_caller + os.sep + tmp_name

        self._name_with_caller = tmp_name
        self._log_manager.set_object_name(self._name_with_caller)

    def set_source_image_color(self, image_data):
        """
        set the color image on which the find method will search the object.

        :type image_data: numpy.ndarray
        :param image_data: the color image
        """
        self._source_image_color = image_data.copy()
        img_gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        self.set_source_image_gray(img_gray)
        #self._log_manager.set_image(self._source_image)

    def set_source_image_gray(self, image_data):
        """
        set the gray image on which the find method will search the object.

        :type image_data: numpy.ndarray
        :param image_data: the gray image
        """
        self._source_image_gray = image_data.copy()

    def find(self):
        raise NotImplementedError

    def wait(self, timeout=-1):
        """
        wait until the object appears on the screen.
        if timeout value is -1 (default value) then timeout value will be read from config file.
        if configuration file doesn't exist, then timeout value will be 15 sec.

        :param timeout: timeout in seconds
        :type timeout: int
        """

        timeout_value = 15

        if timeout == -1:
            timeout_value = self._configReader.get_finder_wait_timeout()
        else:
            timeout_value = timeout

        self._objects_found = []
        self._flag_thread_started = False
        self._flag_thread_have_to_exit = False

        time_elapsed = 0
        time_of_last_change = 0
        self._time_checked_before_exit_start = None

        #screenCapture = ScreenManager()
        thread_interval = self._configReader.get_finder_thread_interval()
        check_diff_interval = self._configReader.get_finder_diff_interval()

        img1 = self._cacheManager.GetLastObjFoundFullImg()

        if img1 is None:
            img1 = self._screen_capture.grab_desktop(self._screen_capture.get_gray_mat)

        thread_t0 = time.time()
        time_before_loop = time.time()
        while True:
            try:
                if time_elapsed > timeout_value:
                    return -1

                t0 = time.time()

                img2_color = self._screen_capture.grab_desktop(self._screen_capture.get_color_mat)
                img2_gray = cv2.cvtColor(img2_color, cv2.COLOR_BGR2GRAY)

                #cv2.imwrite('img2.png', img2)

                print "te1", time_elapsed
                if time.time() - thread_t0 >= thread_interval:
                    thread_t0 = time.time()
                    #self.__queue.put(False)
                    #print "2 sec. elapsed"
                    if self._flag_thread_started is False:
                        self._flag_thread_started = True
                        #print "Worker Started"
                        self.set_source_image_color(img2_color)
                        self.set_source_image_gray(img2_gray)
                        if self._log_manager.is_log_enable() is True:
                            self._log_manager.delete_all_items(keep_items=20, exclude_item="difference")
                        worker = Thread(target=self.find)
                        worker.setDaemon(True)
                        worker.start()
                print "te2", time_elapsed

                if len(self._objects_found) > 0:
                    if self._time_checked_before_exit_start is not None:
                        print "tttttt", self._time_checked_before_exit_start
                        return self._time_checked_before_exit_start
                    else:
                        print "lc", time_of_last_change
                        return time_of_last_change

                diff_mask = numpy.bitwise_xor(img1, img2_gray)
                #cv2.imwrite("bit.png", diff_mask)

                # find the contours
                contours, hierarchy = cv2.findContours(diff_mask, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                #print "contorus", len(contours)

                for cnt in contours:
                    x,y,w,h = cv2.boundingRect(cnt)
                    #cv2.rectangle(img2,(x,y),(x+w,y+h),(0,0,255),3)

                #is_images_equal = not(diff_mask.any())
                if len(contours) < self._min_different_contours:
                #if True:
                    is_images_equal = True
                else:
                    is_images_equal = False

                if is_images_equal is False:
                    #print "diversi"
                    if self._log_manager.is_log_enable() is True:
                        self._log_manager.save_image("difference", "old.png", img1)
                    img1 = img2_gray.copy()
                    if self._log_manager.is_log_enable() is True:
                        self._log_manager.save_image("difference", "current.png", img2_gray)
                        self._log_manager.save_image("difference", "mask.png", diff_mask)
                        self._log_manager.delete_all_items(sub_dir="difference", keep_items=20)

                    if self._flag_check_before_exit is False:
                        self._flag_check_before_exit = True
                        self._time_checked_before_exit_start = time_of_last_change
                        print "time_c", self._time_checked_before_exit_start
                    elif self._flag_checked_before_exit is True and self._flag_check_before_exit is True:
                        self._flag_check_before_exit = False
                        self._flag_checked_before_exit = False
                        self._flag_thread_have_to_exit = True
                        self._time_checked_before_exit_start = None

                    time_of_last_change = time_elapsed
                    print time_of_last_change
                    print "img false"

                #if len(self._objects_found) > 0:
                #    return time_of_last_change

                t1 = time.time() - t0
                time_sleep = check_diff_interval - t1
                if time_sleep < 0:
                    time_sleep = 0

                #print "time to sleep", time_sleep
                time.sleep(time_sleep)

                time_elapsed = time.time() - time_before_loop
                #print "seconds elapsed", time_elapsed

                #print "minutes elapsed", str(datetime.timedelta(seconds=time_elapsed))
            except Exception, err:
                #print str(err) + " on line " + str(sys.exc_traceback.tb_lineno)
                self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
                return None


    def get_result(self, main_obj_index=0, sub_obj_index = None):
        """
        Return the list that contains coordinates of template(s) found

        :rtype: list[(int, int, int, int)]
        :return: x, y, width, height of template(s) found
        """
        try:
            if len(self._objects_found) == 0:
                #return_val = MatchResult((8000, 8000, 100, 100))
                return None

            if sub_obj_index is None and main_obj_index >= 0:
                return self._objects_found[main_obj_index][0]
            elif main_obj_index >= 0 and sub_obj_index >= 0:
                return self._objects_found[main_obj_index][1][sub_obj_index]
            return self._objects_found
        except Exception, err:
            self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
            return None

    """
    def rebuild_result(self, index_to_keep):
        cnt = 0
        object_to_keep = []
        print self._objects_found
        print index_to_keep
        for object in self._objects_found:
            print cnt
            if cnt == index_to_keep:
                object_to_keep = copy.deepcopy(object)
                print "obj", object
            cnt = cnt + 1

        self._objects_found = []
        self._objects_found.append(copy.deepcopy(object_to_keep))
    """

    def rebuild_result(self, indexes_to_keep):

        objects_to_keep = []
        #self._objects_found = []

        cnt = 0
        for object in self._objects_found:
            print cnt

            for index_to_keep in indexes_to_keep:
                if cnt == index_to_keep:
                    objects_to_keep.append(copy.deepcopy(object))
            cnt = cnt + 1


        self._objects_found = []
        self._objects_found = copy.deepcopy(objects_to_keep)

    def replace_result(self, results):
        self._objects_found = copy.deepcopy(results)

