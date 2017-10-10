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
from alyvix.bridge.robot import RobotManager
from alyvix.tools.info import InfoManager
from alyvix.tools.perfdata import PerfManager
from .checkpresence import CheckPresence


class Roi():

    def __init__(self, roi_dict=None):

        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        self.unlimited_up = False
        self.unlimited_down = False
        self.unlimited_left = False
        self.unlimited_right = False

        if roi_dict is not None:
            self.set_roi_dict(roi_dict)

    def set_roi_dict(self, roi_dict):
        if ("roi_x" in roi_dict and "roi_y" in roi_dict and
                "roi_width" in roi_dict and "roi_height" in roi_dict):
            self.x = roi_dict['roi_x']
            self.y = roi_dict['roi_y']
            self.height = roi_dict['roi_height']
            self.width = roi_dict['roi_width']

            if "roi_unlimited_up" in roi_dict and\
                    (roi_dict['roi_unlimited_up'] is True or roi_dict['roi_unlimited_up'] is False):
                self.unlimited_up = roi_dict['roi_unlimited_up']
            if "roi_unlimited_down" in roi_dict and \
                    (roi_dict['roi_unlimited_down'] is True or roi_dict['roi_unlimited_down'] is False):
                self.unlimited_down = roi_dict['roi_unlimited_down']
            if "roi_unlimited_left" in roi_dict and \
                    (roi_dict['roi_unlimited_left'] is True or roi_dict['roi_unlimited_left'] is False):
                self.unlimited_left = roi_dict['roi_unlimited_left']
            if "roi_unlimited_right" in roi_dict and \
                    (roi_dict['roi_unlimited_right'] is True or roi_dict['roi_unlimited_right'] is False):
                self.unlimited_right = roi_dict['roi_unlimited_right']
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

        keyword_timestamp_value = int(time.time() * 1000)

        self.timestamp = keyword_timestamp_value

        self._main_component = None
        self._sub_components = []

        self._timedout_main_components = []
        self._timedout_sub_components = []

        self._main_extra_img_log = None
        self._sub_extra_imgages_log = []

        self.main_xy_coordinates = None
        self.main_xy_coordinates_release = None
        self.sub_xy_coordinates = []
        self.sub_xy_coordinates_release = []

        self._rect_extra_timedout_image = None

        self._robot_manager = RobotManager()

        self._rf_is_set = self._robot_manager.context_is_set()


        self._source_image_color = None
        self._source_image_gray = None
        self._objects_found = []
        self._log_manager = None

        self._timed_out_images = []

        self._find_thread_images = []
        self._find_thread_images_disappear = []
        #self._find_thread_images_copy = []
        self._last_thread_image = None
        self._last_thread_image_copy = None
        self._heartbeat_images = []
        self._heartbeat_images_copy = []

        #variables for the perfdata
        self._cacheManager = None
        self._min_different_contours = 15
        self._flag_thread_started = False
        self._flag_check_before_exit = False
        self._flag_checked_before_exit = False
        self._flag_thread_have_to_exit = False
        self._screen_capture = None
        #end perfdata section

        self._info_manager = InfoManager()

        self._info_manager.set_info("DISABLE REPORTS", False)

        self._scaling_factor = self._info_manager.get_info("SCALING FACTOR INT")

        self._time_checked_before_exit_start = 0

        self._objects_finders_caller = []
        self._name_with_caller = None

        self._name = name

        self._perf_manager = PerfManager()

        self._log_manager = LogManager()
        self._log_manager.set_object_name(self._name)
        self._screen_capture = ScreenManager()
        if self._info_manager.get_info("CHECK BG") == True:
            if self._screen_capture.is_resolution_ok() is False:
                raise Exception(
                    "The screen resolution does not match with the Alyvix Background Service settings")

        self._cacheManager = CacheManager()
        self._configReader = ConfigReader()

        self._calc_last_finder_time = False
        self._last_finder_time = None

        self.__enable_debug_calcperf = False

        #self._timer_for_disappear = 0

        self._object_is_found_flag = False

        self._is_object_finder = False
        self._objects_found_of_sub_object_finder = []

        current_keyword_timestamp_array = self._info_manager.get_info('KEYWORD TIMESTAMP')

        #current_keyword_timestamp_array_copy = copy.deepcopy(current_keyword_timestamp_array)

        timestamp_modified = False
        for cnt_kts in xrange(len(current_keyword_timestamp_array)):
            if current_keyword_timestamp_array[cnt_kts][0] == self._name:
                timestamp_modified = True
                current_keyword_timestamp_array[cnt_kts] = (self._name, keyword_timestamp_value)
                break

        if timestamp_modified is False:
            current_keyword_timestamp_array.append((self._name, keyword_timestamp_value))

        self._info_manager.set_info('KEYWORD TIMESTAMP',
                                    current_keyword_timestamp_array)

    def _compress_image(self, img):
        return cv2.imencode('.png', img)[1]

    def _uncompress_image(self, compressed_img):
        return cv2.imdecode(compressed_img, cv2.CV_LOAD_IMAGE_GRAYSCALE)

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

    def get_source_image_color(self):
        """
        get the color image on which the find method will search the object.

        :rtype: numpy.ndarray
        :return: the source color image
        """
        return self._source_image_color

    def get_source_image_gray(self):
        """
        get the gray image on which the find method will search the object.

        :rtype: numpy.ndarray
        :return: the source gray image
        """
        return self._source_image_gray

    def find(self):
        raise NotImplementedError

    def wait(self, timeout=-1, wait_disappear=False):
        """
        wait until the object appears on the screen.
        if timeout value is -1 (default value) then timeout value will be read from config file.
        if configuration file doesn't exist, then timeout value will be 15 sec.

        :param timeout: timeout in seconds
        :type timeout: int
        """



        if self._is_object_finder is False and self.is_textfinder == True:
            raise Exception("A Text Finder is out of an Object Finder")

        #cv2.imwrite()

        #self._robot_manager.write_log_message("wait method: " + self.get_name(), "ERROR", False)
        #self._robot_manager.write_log_message("wait method: " + self.get_name(), "ERROR", False)
        #sss = self._robot_manager.get_suite_name()
        #ttt = self._robot_manager.get_testcase_name()

        #self._robot_manager.method1().method2()

        timeout_value = 15

        self._calc_last_finder_time = True

        if timeout == -1:
            timeout_value = self._configReader.get_finder_wait_timeout()
        else:
            timeout_value = timeout
            #self._perf_manager.set_last_timeout_value(self._name, timeout_value)
            current_keyword_timeout_array = self._info_manager.get_info('KEYWORD TIMEOUT')

            # current_keyword_timestamp_array_copy = copy.deepcopy(current_keyword_timestamp_array)

            timeout_modified = False
            for cnt_kts in xrange(len(current_keyword_timeout_array)):
                if current_keyword_timeout_array[cnt_kts][0] == self._name:
                    timeout_modified = True
                    current_keyword_timeout_array[cnt_kts] = (self._name, timeout_value)
                    break

            if timeout_modified is False:
                current_keyword_timeout_array.append((self._name, timeout_value))

            self._info_manager.set_info('KEYWORD TIMEOUT',
                                        current_keyword_timeout_array)

        self._objects_found = []

        self._heartbeat_images = []
        self._find_thread_images = []

        self._flag_thread_started = False
        self._flag_thread_have_to_exit = False

        self._heartbeat_images_copy = []

        time_elapsed = 0.0
        #time_of_last_change = 0.0
        self._time_checked_before_exit_start = None

        self._object_is_found_flag = False

        #screenCapture = ScreenManager()
        thread_interval = self._info_manager.get_info("FINDER THREAD INTERVAL") #self._configReader.get_finder_thread_interval()
        #thread_interval = 0.5
        check_diff_interval = self._info_manager.get_info("CHECK DIFF INTERVAL")

        img1 = self._cacheManager.GetLastObjFoundFullImg()

        if img1 is None:
            img1 = self._screen_capture.grab_desktop(self._screen_capture.get_gray_mat)

        thread_t0 = time.time()
        time_before_loop = time.time()
        while True:
            #txx = time.time()
            try:

                if len(self._objects_found) > 0 and self._flag_thread_started is False:
                    #do analysis cjecl_time()
                    self._info_manager.set_info('WAIT FINISH', time.time())
                    """
                    print "len main:", len(self._objects_found)

                    print "main x, y, w, h:", self._objects_found[0][0].x, self._objects_found[0][0].y, self._objects_found[0][0].width, self._objects_found[0][0].height


                    if self._objects_found[0][1] is not None:
                        print "len secodn:", len(self._objects_found[0][1])
                        for sub_obj in self._objects_found[0][1]:
                            print "sub x, y, w, h:", sub_obj.x, sub_obj.y, sub_obj.width, sub_obj.height
                    """

                    self._last_thread_image = self._uncompress_image(self._find_thread_images[-1][1])

                    #time.sleep(3600)

                    if wait_disappear is False:
                        from alyvix.finders.cv.objectfinder import ObjectFinder

                        if isinstance(self, ObjectFinder):
                            self._log_manager.save_objects_found(self._name, self.get_source_image_gray(), self._objects_found, [x[1] for x in self._sub_components], self.main_xy_coordinates, self.sub_xy_coordinates, finder_type=3)
                        else:
                            self._log_manager.save_objects_found(self._name, self.get_source_image_gray(),
                                                                 self._objects_found,
                                                                 [x[1] for x in self._sub_components],
                                                                 self.main_xy_coordinates, self.sub_xy_coordinates, finder_type=None)

                    if wait_disappear is True:
                        self._heartbeat_images_copy = copy.deepcopy(self._heartbeat_images)
                        self._last_thread_image_copy = copy.deepcopy(self._last_thread_image)
                        #self._timer_for_disappear = self._heartbeat_images[-1][0]
                        #self._find_thread_images_copy = copy.deepcopy(self._find_thread_images)
                        return -2
                    else:
                        self._object_is_found_flag = True
                        self._last_thread_image_copy = copy.deepcopy(self._last_thread_image)
                        return self._get_performance()


                if time_elapsed > timeout_value and self._flag_thread_started is False:
                    self._last_thread_image = self._uncompress_image(self._find_thread_images[-1][1])
                    #from alyvix.finders.cv.rectfinder import RectFinder
                    #from alyvix.finders.cv.imagefinder import ImageFinder
                    #from alyvix.finders.cv.textfinder import TextFinder
                    from alyvix.finders.cv.objectfinder import ObjectFinder

                    #if not isinstance(self, ObjectFinder):
                    self._log_manager.save_timedout_objects(self._name + "_timedout", self.get_source_image_gray(), self._timedout_main_components, self._timedout_sub_components, self._main_extra_img_log, self._sub_extra_imgages_log)
                    #else:
                    if isinstance(self, ObjectFinder):

                        #self._log_manager.save_timedout_objects(self._name + "_timedout", self._last_thread_image, self._main_component[0]._timedout_main_components, self._main_component[0]._timedout_sub_components, self._main_component[0]._main_extra_img_log, self._main_component[0]._sub_extra_imgages_log, True, self._main_component[0]._name)

                        if len(self._main_component[0]._objects_found) == 0:
                            self._log_manager.save_timedout_objects(self._name + "_timedout", self._last_thread_image, self._main_component[0]._timedout_main_components, self._main_component[0]._timedout_sub_components, self._main_component[0]._main_extra_img_log, self._main_component[0]._sub_extra_imgages_log, True, self._main_component[0]._name)

                        for t_sub in self._sub_components:
                            self._log_manager.save_timedout_objects(self._name + "_timedout", self._last_thread_image, t_sub[0]._timedout_main_components, t_sub[0]._timedout_sub_components, t_sub[0]._main_extra_img_log, t_sub[0]._sub_extra_imgages_log, True, t_sub[0]._name)

                    self._heartbeat_images_copy = copy.deepcopy(self._heartbeat_images)
                    return -1

                t0 = time.time()

                #cv2.imwrite('img2.png', img2)

                #if time.time() - thread_t0 >= thread_interval:
                if time_elapsed < timeout_value and time.time() - thread_t0 >= thread_interval and self._flag_thread_started is False:
                    thread_t0 = time.time()

                    self._flag_thread_started = True

                    """
                    folder = 'c:\\log\\buffer_images'
                    for the_file in os.listdir(folder):
                        file_path = os.path.join(folder, the_file)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                        except Exception, e:
                            print e
                    """


                    #for i in range(len(self._find_thread_images)):
                        #cv2.imwrite("c:\\log\\buffer_images\\_old_" + str(self._find_thread_images[i][0]) + ".png", self._uncompress_image(self._find_thread_images[i][1]))


                    self._find_thread_images = copy.deepcopy(self._heartbeat_images)
                    self._heartbeat_images = []

                    self.set_source_image_color(img2_color)
                    self.set_source_image_gray(img2_gray)
                    if self._log_manager.is_log_enable() is True:
                        self._log_manager.delete_all_items(keep_items=20, exclude_item="difference")
                    worker = Thread(target=self.find)
                    worker.setDaemon(True)
                    worker.start()

                img2_color = self._screen_capture.grab_desktop(self._screen_capture.get_color_mat)
                img2_gray = cv2.cvtColor(img2_color, cv2.COLOR_BGR2GRAY)
                self._heartbeat_images.append((time_elapsed, self._compress_image(img2_gray)))


                t1 = time.time() - t0
                time_sleep = check_diff_interval - t1
                if time_sleep < 0:
                    time_sleep = 0

                time.sleep(time_sleep)

                time_elapsed = time.time() - time_before_loop
                #print time_elapsed

            except Exception, err:
                #print str(err) + " on line " + str(sys.exc_traceback.tb_lineno)
                self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
                return None

            #print "time loop:", time.time() - txx

    def wait_disappear(self, timeout=-1):

        #time.sleep(5)

        """
        wait until the object appears on the screen.
        if timeout value is -1 (default value) then timeout value will be read from config file.
        if configuration file doesn't exist, then timeout value will be 15 sec.

        :param timeout: timeout in seconds
        :type timeout: int
        """

        timer_offset = 0

        add_wait_delay = False

        if self._object_is_found_flag is True:
            add_wait_delay = True
            wait_time = 0
        else:
            wait_time = self.wait(timeout, wait_disappear=True)
            timer_offset = self._heartbeat_images_copy[-1][0]

        if wait_time == -1:
            return -1

        find_thread_images_of_wait = copy.deepcopy(self._find_thread_images)

        #disappear_timeout = timeout - wait_time

        obj_found = copy.deepcopy(self._objects_found)
        last_thread_img = copy.deepcopy(self._last_thread_image)

        self._heartbeat_images = []
        self._find_thread_images = []
        self._objects_found = []

        #cv2.imwrite()

        #self._robot_manager.write_log_message("wait method: " + self.get_name(), "ERROR", False)
        #self._robot_manager.write_log_message("wait method: " + self.get_name(), "ERROR", False)
        #sss = self._robot_manager.get_suite_name()
        #ttt = self._robot_manager.get_testcase_name()

        #self._robot_manager.method1().method2()

        timeout_value = 15

        if timeout == -1:
            timeout_value = self._configReader.get_finder_wait_timeout()
        else:
            timeout_value = timeout

            #self._perf_manager.set_last_timeout_value(self._name, timeout_value)
            current_keyword_timeout_array = self._info_manager.get_info('KEYWORD TIMEOUT')

            # current_keyword_timestamp_array_copy = copy.deepcopy(current_keyword_timestamp_array)

            timeout_modified = False
            for cnt_kts in xrange(len(current_keyword_timeout_array)):
                if current_keyword_timeout_array[cnt_kts][0] == self._name:
                    timeout_modified = True
                    current_keyword_timeout_array[cnt_kts] = (self._name, timeout_value)
                    break

            if timeout_modified is False:
                current_keyword_timeout_array.append((self._name, timeout_value))

            self._info_manager.set_info('KEYWORD TIMEOUT',
                                        current_keyword_timeout_array)

        timeout_value = timeout_value - wait_time

        self._objects_found = []
        self._flag_thread_started = False
        self._flag_thread_have_to_exit = False

        time_elapsed = 0.0
        #time_of_last_change = 0.0
        self._time_checked_before_exit_start = None

        #screenCapture = ScreenManager()
        thread_interval = self._info_manager.get_info("FINDER THREAD INTERVAL DISAPPEAR")
        check_diff_interval = self._info_manager.get_info("CHECK DIFF INTERVAL DISAPPEAR")

        img1 = self._cacheManager.GetLastObjFoundFullImg()

        if img1 is None:
            img1 = self._screen_capture.grab_desktop(self._screen_capture.get_gray_mat)

        thread_t0 = time.time()
        time_before_loop = time.time()

        one_thread_started = False

        while True:
            #txx = time.time()
            try:

                try: #for object finder only
                    self._main_indexes_to_keep = []
                    self._sub_indexes_to_keep = []
                except:
                    pass

                if len(self._objects_found) == 0 and self._flag_thread_started is False and one_thread_started is True:
                    txxxxxxxx = time.time()
                    #do analysis cjecl_time()
                    """
                    print "len main:", len(self._objects_found)

                    print "main x, y, w, h:", self._objects_found[0][0].x, self._objects_found[0][0].y, self._objects_found[0][0].width, self._objects_found[0][0].height


                    if self._objects_found[0][1] is not None:
                        print "len secodn:", len(self._objects_found[0][1])
                        for sub_obj in self._objects_found[0][1]:
                            print "sub x, y, w, h:", sub_obj.x, sub_obj.y, sub_obj.width, sub_obj.height
                    """

                    self._objects_found = copy.deepcopy(obj_found)

                    self._last_thread_image = self._uncompress_image(self._find_thread_images_disappear[-1][1])

                    #self._log_manager.save_timedout_objects(self._name, self.get_source_image_gray(), self._timedout_main_components, self._timedout_sub_components, self._main_extra_img_log, self._sub_extra_imgages_log, disappear_mode=True)

                    #for i in range(len(self._find_thread_images)):
                    #    cv2.imwrite("c:\\log\\buffer_images\\_oldd_" + str(self._find_thread_images[i][0]) + ".png", self._uncompress_image(self._find_thread_images[i][1]))


                    #perf_appear = self._get_performance(wait_disappear=True)

                    perf_disappear = self._get_disappear_performance()

                    self._find_thread_images = copy.deepcopy(find_thread_images_of_wait)

                    self._last_thread_image = copy.deepcopy(self._last_thread_image_copy)

                    perf_wait = None
                    if self._object_is_found_flag is True:
                        perf_wait = 0.0
                    else:
                        """
                        from alyvix.finders.cv.objectfinder import ObjectFinder

                        if isinstance(self, ObjectFinder):
                            self._log_manager.save_objects_found(self._name, self.get_source_image_gray(),
                                                                 self._objects_found,
                                                                 [x[1] for x in self._sub_components],
                                                                 self.main_xy_coordinates, self.sub_xy_coordinates,
                                                                 finder_type=3)
                        else:
                            self._log_manager.save_objects_found(self._name, self.get_source_image_gray(),
                                                                 self._objects_found,
                                                                 [x[1] for x in self._sub_components],
                                                                 self.main_xy_coordinates, self.sub_xy_coordinates,
                                                                 finder_type=None)
                        """
                        self._log_manager.save_objects_found(self._name, self._last_thread_image_copy, self._objects_found, [x[1] for x in self._sub_components])

                        perf_wait = self._get_performance()

                    self._log_manager.save_timedout_objects(self._name, self.get_source_image_gray(), self._timedout_main_components, self._timedout_sub_components, self._main_extra_img_log, self._sub_extra_imgages_log, disappear_mode=True)

                    perf_disappear = perf_disappear - perf_wait

                    #print "PERF WAIT:", perf_wait
                    #print "PERF DISAPP", perf_disappear

                    wait_delay_time = 0

                    try:
                        wait_delay_time = self._info_manager.get_info('DISAPP START')  - self._info_manager.get_info('WAIT FINISH')
                        wait_delay_time = wait_delay_time + self._last_finder_time

                        self._info_manager.set_info('DISAPP START', None)
                    except:
                        pass

                    self._last_finder_time = None

                    return perf_wait + perf_disappear + wait_delay_time

                    #return self._get_disappear_performance()
                    #return self._get_performance()


                if time_elapsed > timeout_value and self._flag_thread_started is False:
                    self._last_thread_image = self._uncompress_image(self._find_thread_images_disappear[-1][1])
                    #from alyvix.finders.cv.rectfinder import RectFinder
                    #from alyvix.finders.cv.imagefinder import ImageFinder
                    #from alyvix.finders.cv.textfinder import TextFinder
                    from alyvix.finders.cv.objectfinder import ObjectFinder

                    #if not isinstance(self, ObjectFinder):
                    #self._log_manager.save_timedout_objects(self._name + "_timedout", self.get_source_image_gray(), self._timedout_main_components, self._timedout_sub_components, self._main_extra_img_log, self._sub_extra_imgages_log)
                    self._log_manager.save_objects_found(self._name + "_timedout", self.get_source_image_gray(), self._objects_found, [x[1] for x in self._sub_components], disappear_mode=True)

                    #else:
                    """
                    if isinstance(self, ObjectFinder):

                        #self._log_manager.save_timedout_objects(self._name + "_timedout", self._last_thread_image, self._main_component[0]._timedout_main_components, self._main_component[0]._timedout_sub_components, self._main_component[0]._main_extra_img_log, self._main_component[0]._sub_extra_imgages_log, True, self._main_component[0]._name)

                        if len(self._main_component[0]._objects_found) == 0:
                            self._log_manager.save_timedout_objects(self._name + "_timedout", self._last_thread_image, self._main_component[0]._timedout_main_components, self._main_component[0]._timedout_sub_components, self._main_component[0]._main_extra_img_log, self._main_component[0]._sub_extra_imgages_log, True, self._main_component[0]._name)

                        for t_sub in self._sub_components:
                            self._log_manager.save_timedout_objects(self._name + "_timedout", self._last_thread_image, t_sub[0]._timedout_main_components, t_sub[0]._timedout_sub_components, t_sub[0]._main_extra_img_log, t_sub[0]._sub_extra_imgages_log, True, t_sub[0]._name)
                    """
                    self._info_manager.set_info('DISAPP START', None)
                    return -1

                t0 = time.time()

                #cv2.imwrite('img2.png', img2)

                #if time.time() - thread_t0 >= thread_interval:
                if time_elapsed < timeout_value and time.time() - thread_t0 >= thread_interval and self._flag_thread_started is False:
                    thread_t0 = time.time()

                    self._flag_thread_started = True

                    """
                    folder = 'c:\\log\\buffer_images'
                    for the_file in os.listdir(folder):
                        file_path = os.path.join(folder, the_file)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                        except Exception, e:
                            print e
                    """


                    #for i in range(len(self._find_thread_images)):
                    #    cv2.imwrite("c:\\log\\buffer_images\\_old_" + str(self._find_thread_images[i][0]) + ".png", self._uncompress_image(self._find_thread_images[i][1]))

                    if one_thread_started is False:
                        #timer_offset = self._heartbeat_images_copy[-1][0]
                        self._find_thread_images_disappear = copy.deepcopy(self._heartbeat_images_copy)

                        self._find_thread_images_disappear.extend(copy.deepcopy(self._heartbeat_images))
                    else:
                        self._find_thread_images_disappear = copy.deepcopy(self._heartbeat_images)

                    #self._find_thread_images_disappear = copy.deepcopy(self._heartbeat_images)

                    self._heartbeat_images = []

                    self.set_source_image_color(img2_color)
                    self.set_source_image_gray(img2_gray)
                    if self._log_manager.is_log_enable() is True:
                        self._log_manager.delete_all_items(keep_items=20, exclude_item="difference")
                    worker = Thread(target=self.find)
                    worker.setDaemon(True)
                    worker.start()
                    one_thread_started = True

                img2_color = self._screen_capture.grab_desktop(self._screen_capture.get_color_mat)
                img2_gray = cv2.cvtColor(img2_color, cv2.COLOR_BGR2GRAY)
                #self._timer_for_disappear += time_elapsed
                self._heartbeat_images.append((time_elapsed + timer_offset, self._compress_image(img2_gray)))

                if self._info_manager.get_info('DISAPP START') is None and add_wait_delay is True:
                    self._info_manager.set_info('DISAPP START', time.time())
                    #a = self._info_manager.get_info('DISAPP START')  - self._info_manager.get_info('WAIT FINISH')

                t1 = time.time() - t0
                time_sleep = check_diff_interval - t1
                if time_sleep < 0:
                    time_sleep = 0

                time.sleep(time_sleep)

                time_elapsed = time.time() - time_before_loop
                #print time_elapsed

            except Exception, err:
                #print str(err) + " on line " + str(sys.exc_traceback.tb_lineno)
                self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
                return None



    def _check_object_presence(self, img, offset_border, crop_value, wait_disappear=False):
        """
        check if the object is present into the image.

        :rtype: bool
        :return: returns true if the object is present
        """

        img_height, img_width = img.shape

        #t0 = time.time()
        check_presence = CheckPresence()

        check_presence.set_source_image_gray(img, (crop_value[0], crop_value[1], crop_value[2], crop_value[3])) #(img)#, (crop_value[0], crop_value[1], crop_value[2], crop_value[3]))

        main_offset_border = offset_border

        y1 = self._objects_found[0][0].y - offset_border
        y2 = y1 + self._objects_found[0][0].height + (offset_border * 2)
        x1 = self._objects_found[0][0].x - offset_border #10
        x2 = x1 + self._objects_found[0][0].width + (offset_border * 2)

        if x1 < 0:
            x1 = 0

        if y1 < 0:
            y1 = 0

        if x2 > img_width:
            x2 = img_width

        if y2 > img_height:
            y2 = img_height

        if wait_disappear is False:
            main_template = self._last_thread_image[y1:y2, x1:x2] #self._uncompress_image(self._find_thread_images[-1][1])[y1:y2, x1:x2]
        else:
            main_template = self._last_thread_image_copy[y1:y2, x1:x2] #self._uncompress_image(self._find_thread_images[-1][1])[y1:y2, x1:x2]

        cv2.imwrite("c:\\log\\buffer_images\\main_template.png",main_template)

        check_presence.set_xy(x1 - crop_value[0], y1 - crop_value[1]) #(x1, y1) #(x1 - crop_value[0], y1 - crop_value[1])


        check_presence.set_main_component(main_template, {"roi_x": self._objects_found[0][0].x - (offset_border * 4),
                                                     "roi_y": self._objects_found[0][0].y - (offset_border * 4),
                                                     "roi_width": self._objects_found[0][0].width +(offset_border * 4 * 2),
                                                     "roi_height": self._objects_found[0][0].height + (offset_border * 4 * 2)})

        if self._objects_found[0][1] is not None:

            for sub_obj in self._objects_found[0][1]:

                offset_border = sub_obj.width

                if offset_border > sub_obj.height:
                    offset_border = sub_obj.height

                offset_border = int(offset_border/10)

                if offset_border < 8:
                    offset_border = 8

                y1 = sub_obj.y - offset_border
                y2 = y1 + sub_obj.height + (offset_border * 2)
                x1 = sub_obj.x - offset_border
                x2 = x1 + sub_obj.width + (offset_border * 2)

                if x1 < 0:
                    x1 = 0

                if y1 < 0:
                    y1 = 0

                if x2 > img_width:
                    x2 = img_width

                if y2 > img_height:
                    y2 = img_height

                if wait_disappear is False:
                    sub_img = self._last_thread_image[y1:y2, x1:x2] #self._uncompress_image(self._find_thread_images[-1][1])[y1:y2, x1:x2]
                else:
                    sub_img = self._last_thread_image_copy[y1:y2, x1:x2]

                sub_x = sub_obj.x - (offset_border * 4)
                sub_y = sub_obj.y - (offset_border * 4)

                sub_x2 = self._objects_found[0][0].x - main_offset_border #- crop_value[0]
                sub_y2 = self._objects_found[0][0].y - main_offset_border #- crop_value[1]

                check_presence.add_sub_component(sub_img, {"roi_x": sub_x - sub_x2,
                                                     "roi_y": sub_y - sub_y2,
                                                     "roi_width": sub_obj.width + (offset_border * 4 * 2),
                                                     "roi_height": sub_obj.height + (offset_border * 4 * 2)})

        is_pesent =  check_presence.find()

        #print "calc perf time:", time.time() - t0

        return is_pesent

    def _get_performance(self, wait_disappear=False):
        """
        get the performance.

        :rtype: float
        :return: returns the performance in seconds
        """

        t0 = time.time()

        if self.__enable_debug_calcperf is True:
            for i in range(len(self._find_thread_images)):
                cv2.imwrite("c:\\log\\buffer_images\\" + str(self._find_thread_images[i][0]) + ".png", self._uncompress_image(self._find_thread_images[i][1]))


        offset_border = self._objects_found[0][0].width

        if offset_border > self._objects_found[0][0].height:
            offset_border = self._objects_found[0][0].height

        offset_border = int(offset_border/10)

        if offset_border < 8:
            offset_border = 8

        min_x = self._objects_found[0][0].x
        min_y = self._objects_found[0][0].y
        max_width = self._objects_found[0][0].x + self._objects_found[0][0].width
        max_height = self._objects_found[0][0].y + self._objects_found[0][0].height

        if self._objects_found[0][1] is not None:

            for sub_obj in self._objects_found[0][1]:

                if sub_obj.x < min_x:
                    min_x = sub_obj.x

                if sub_obj.y < min_y:
                    min_y = sub_obj.y

                if sub_obj.x + sub_obj.width > max_width:
                    max_width = sub_obj.x + sub_obj.width

                if sub_obj.y + sub_obj.height > max_height:
                    max_height = sub_obj.y + sub_obj.height

        min_x = min_x - (offset_border * 6)
        min_y = min_y - (offset_border * 6)
        max_width = max_width + (offset_border * 6 * 2)
        max_height = max_height + (offset_border * 6 * 2)

        img_height, img_width = self._last_thread_image.shape

        if min_x < 0:
            min_x = 0

        if min_y < 0:
            min_y = 0

        if max_width > img_width:
            max_width = img_width

        if max_height > img_height:
            max_height = img_height

        #cv2.imwrite("c:\\log\\buffer_images\\cropped.png", self._uncompress_image(self._find_thread_images[0][1])[min_y:max_height, min_x:max_width] )

        if self._check_object_presence(self._uncompress_image(self._find_thread_images[0][1]), offset_border, (min_x, min_y, max_width, max_height), wait_disappear) is True:
            return self._find_thread_images[0][0]

        frame_step = 10
        loop_step = round(float(len(self._find_thread_images))/float(frame_step))
        loop_step = int(loop_step)

        #print "loop step", int(loop_step)

        if loop_step < 1:
            loop_step = 1

        last_found_index = len(self._find_thread_images) -1
        last_notfound_index = 0

        for i in range(loop_step):

            if i == 0:
                continue

            index = (len(self._find_thread_images) - (frame_step * i))
            #print index

            if self._check_object_presence(self._uncompress_image(self._find_thread_images[index][1]), offset_border, (min_x, min_y, max_width, max_height), wait_disappear) is True:
                last_found_index = index
            else: #elif last_notfound_index == 0:
                last_notfound_index = index
                break



        #print "last found", last_found_index
        #print "last not found", last_notfound_index

        for i in range(last_found_index):
            if i > last_notfound_index:
                #print "index searching:", i
                if self._check_object_presence(self._uncompress_image(self._find_thread_images[i][1]), offset_border, (min_x, min_y, max_width, max_height), wait_disappear) is True:
                    #print "get performance time:", time.time() - t0
                    return self._find_thread_images[i][0]

        #print "get performance time:", time.time() - t0

        return self._find_thread_images[-1][0]

    def _get_disappear_performance(self):
        """
        get the performance.

        :rtype: float
        :return: returns the performance in seconds
        """

        t0 = time.time()

        if self.__enable_debug_calcperf is True:
            for i in range(len(self._find_thread_images_disappear)):
                cv2.imwrite("c:\\log\\buffer_disapp_images\\" + str(self._find_thread_images_disappear[i][0]) + ".png", self._uncompress_image(self._find_thread_images_disappear[i][1]))


        offset_border = self._objects_found[0][0].width

        if offset_border > self._objects_found[0][0].height:
            offset_border = self._objects_found[0][0].height

        offset_border = int(offset_border/10)

        if offset_border < 8:
            offset_border = 8

        min_x = self._objects_found[0][0].x
        min_y = self._objects_found[0][0].y
        max_width = self._objects_found[0][0].x + self._objects_found[0][0].width
        max_height = self._objects_found[0][0].y + self._objects_found[0][0].height

        if self._objects_found[0][1] is not None:

            for sub_obj in self._objects_found[0][1]:

                if sub_obj.x < min_x:
                    min_x = sub_obj.x

                if sub_obj.y < min_y:
                    min_y = sub_obj.y

                if sub_obj.x + sub_obj.width > max_width:
                    max_width = sub_obj.x + sub_obj.width

                if sub_obj.y + sub_obj.height > max_height:
                    max_height = sub_obj.y + sub_obj.height

        min_x = min_x - (offset_border * 6)
        min_y = min_y - (offset_border * 6)
        max_width = max_width + (offset_border * 6 * 2)
        max_height = max_height + (offset_border * 6 * 2)

        img_height, img_width = self._last_thread_image.shape

        if min_x < 0:
            min_x = 0

        if min_y < 0:
            min_y = 0

        if max_width > img_width:
            max_width = img_width

        if max_height > img_height:
            max_height = img_height

        cv2.imwrite("c:\\log\\buffer_images\\cropped.png", self._uncompress_image(self._find_thread_images_disappear[0][1])[min_y:max_height, min_x:max_width] )

        if self._check_object_presence(self._uncompress_image(self._find_thread_images_disappear[0][1]), offset_border, (min_x, min_y, max_width, max_height), wait_disappear=True) is False:
            return self._find_thread_images_disappear[0][0]

        frame_step = 10
        loop_step = round(float(len(self._find_thread_images_disappear))/float(frame_step))
        loop_step = int(loop_step)

        #print "loop step", int(loop_step)

        if loop_step < 1:
            loop_step = 1

        last_found_index = 0
        last_notfound_index = len(self._find_thread_images_disappear) -1

        for i in range(loop_step):

            if i == 0:
                continue

            index = (len(self._find_thread_images_disappear) - (frame_step * i))
            #print index

            if self._check_object_presence(self._uncompress_image(self._find_thread_images_disappear[index][1]), offset_border, (min_x, min_y, max_width, max_height), wait_disappear=True) is False:
                last_notfound_index = index
            else: #elif last_notfound_index == 0:
                last_found_index = index
                break



        #print "last found", last_found_index
        #print "last not found", last_notfound_index

        for i in range(last_notfound_index):
            if i > last_found_index:
                #print "index searching:", i
                if self._check_object_presence(self._uncompress_image(self._find_thread_images_disappear[i][1]), offset_border, (min_x, min_y, max_width, max_height), wait_disappear=True) is False:
                    #print "get performance time:", time.time() - t0
                    return self._find_thread_images_disappear[i][0]

        #print "get performance time:", time.time() - t0

        return self._find_thread_images_disappear[-1][0]

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

    def rebuild_result(self, indexes_to_keep):

        objects_to_keep = []
        #self._objects_found = []

        cnt = 0
        for object in self._objects_found:

            for index_to_keep in indexes_to_keep:
                if cnt == index_to_keep:
                    objects_to_keep.append(copy.deepcopy(object))
            cnt = cnt + 1


        self._objects_found = []
        self._objects_found = copy.deepcopy(objects_to_keep)

    def rebuild_result_for_sub_component(self, indexes_to_keep):

        if len(self._sub_components) == 0:
            return

        for sub_obj in self._sub_components:
            sub_obj[0]._objects_found = []

        for result in self._objects_found:

            sub_list = result[1]

            #sub_main_coords = result[1]

            cnt_sub_obj = 0
            for sub_obj in self._sub_components:

                objects_to_keep = []

                sub_main_coords = sub_list[cnt_sub_obj]

                #sub_obj[0]._objects_found.extend(sub_main_coords)

                for extended_obj_found in sub_obj[0]._objects_found_of_sub_object_finder:

                    if extended_obj_found[0].x == sub_main_coords.x \
                            and extended_obj_found[0].y == sub_main_coords.y \
                            and extended_obj_found[0].width == sub_main_coords.width \
                            and  extended_obj_found[0].height == sub_main_coords.height:
                        objects_to_keep.append(copy.deepcopy(extended_obj_found))

                sub_obj[0]._objects_found.extend(objects_to_keep)
                sub_obj[0]._is_object_finder = False

                cnt_sub_obj += 1

    def replace_result(self, results):
        self._objects_found = copy.deepcopy(results)

