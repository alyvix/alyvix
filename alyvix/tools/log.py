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
import cv2.cv as cv
import os
import shutil
import time
import numpy
from PIL import Image
from datetime import datetime, timedelta
from alyvix.tools.configreader import ConfigReader

log_path = None

class LogManager:

    #__image = None
    #__main_object_points = None
    #__sub_objects_points = []

    def __init__(self):

        self._config_reader = ConfigReader()

        self.__enable_log = self._config_reader.get_log_enable_value()

        self.__set_log_path()

    def set_object_name(self, name):
        """
        set the object name.

        :type name: string
        :param name: the object name
        """

        current_time = datetime.now().strftime("%H_%M_%S.%f")

        current_time = current_time[:-4]

        self.__name = name
        self.__name_with_time = current_time + "_" + name

    def __set_log_path(self, path=None):

        global log_path

        #print "log_path:", root_log_path

        test_case_name = os.getenv("alyvix_test_case_name", "generic")
        #print test_case_name

        #set testcase root log folder
        if log_path is None and self.__enable_log is True:

            day_time = time.strftime("%d-%m-%y")
            hh_mm_ss = time.strftime("%H_%M_%S")

            root_log_path = self._config_reader.get_log_folder()

            #print root_log_path
            path = root_log_path + os.sep + test_case_name + os.sep + day_time + os.sep + hh_mm_ss

            try:
                if not os.path.exists(path):
                    os.makedirs(path)
            except:
                pass

            log_path = path
            #print path

            self.__delete_old_folders(root_log_path + os.sep + test_case_name)

    def __delete_old_folders(self, root_path):

        daily_folders = os.listdir(root_path)

        for daily_folder in daily_folders:

        
            try:
                if not "-" in daily_folder:
                    continue
                daily_folder_datetime = datetime.strptime(daily_folder, "%d-%m-%y")
                current_datetime = datetime.now()

                current_full_path = root_path + os.sep + daily_folder

                log_max_days = os.getenv("alyvix_log_max_days", "7")
                log_max_days_int = int(log_max_days)

                #if log folder are too old, then delete it
                if daily_folder_datetime <= current_datetime + timedelta(days=(log_max_days_int * -1)):
                    shutil.rmtree(current_full_path)
                #otherwise, check if we have to delete hours folder
                elif daily_folder == time.strftime("%d-%m-%y"):
                    minutes_folders = os.listdir(current_full_path)

                    for minutes_folder in minutes_folders:
                        try:

                            if not "-" in minutes_folder:
                                continue

                            #create fake datetime, that because we need only to compare hours
                            minutes_folder_datetime = datetime.strptime(daily_folder + "_" + minutes_folder,
                                                                        "%d-%m-%y_%H_%M_%S")
                            log_max_hours = os.getenv("alyvix_log_max_hours_per_days", "24")
                            log_max_hours_int = int(log_max_hours)

                            #if hours folder are too old, then delete it
                            if minutes_folder_datetime <= current_datetime + timedelta(hours=(log_max_hours_int * -1)):
                                shutil.rmtree(current_full_path + os.sep + minutes_folder)
                        except:
                            pass
            except:
                pass

    def __delete_items_but(self, path, max_items=None, exclude_item=None):
        if max_items is not None:

            if not os.path.exists(path):
                return

            items = os.listdir(path)

            if exclude_item is not None:
                new_items = [item for item in items if item != exclude_item]
            else:
                new_items = items

            while len(new_items) >= max_items:
            
                try:

                    items = os.listdir(path)

                    if exclude_item is not None:
                        new_items = [item for item in items if item != exclude_item]
                    else:
                        new_items = items

                    full_name = path + os.sep + new_items[0]

                    if os.path.isdir(full_name) is True:
                        shutil.rmtree(full_name)
                    else:
                        os.remove(full_name)
                        
                except:
                    pass

    def __delete_files(self, path, max_files=None):

        if not os.path.exists(path):
            return

        if max_files is not None:
            while len(os.listdir(path)) > max_files:
            
                try:

                    files = os.listdir(path)
                    os.remove(path + os.sep + files[0])
                except:
                    pass

    def is_log_enable(self):
        """
        check if log is enabled.

        :rtype: bool
        :return: a boolean
        """
        return self.__enable_log

    def save_exception(self, type, text_data):

        """
        save the exception into the test case log folder.

        :type sub_dir: string
        :param sub_dir: the subdir to create inside the test case log folder
        :type file_name: string
        :param file_name: the name of the image
        :type text_data: string
        :param text_data: the text to write
        """

        global log_path

        if self.__enable_log is True:

            current_time = datetime.now().strftime("%H:%M:%S.%f")

            fullname = log_path + os.sep + "log.txt"
            #print fullname

            if not os.path.exists(log_path):
                os.makedirs(log_path)

            text_file = open(fullname, "a")
            text_file.write(type + "|" + current_time + "|" + self.__name + "|" + text_data)
            text_file.close()

    def save_image(self, sub_dir, image_name, image_data):
        """
        save the image into the test case log folder.

        :type sub_dir: string
        :param sub_dir: the subdir to create inside the test case log folder
        :type image_name: string
        :param image_name: the name of the image
        :type image_data: numpy.ndarray or Image.Image or cv.iplimage
        :param image_data: the image data to save
        """

        try:
            if isinstance(image_data, numpy.ndarray):
                self.__save_numpy_image(sub_dir, image_name, image_data)

            if isinstance(image_data, Image.Image):
                self.__save_pil_image(sub_dir, image_name, image_data)

            if isinstance(image_data, cv.iplimage):
                self.__save_cv_image(sub_dir, image_name, image_data)
        except Exception, err:
            pass
            #import traceback
            #self.save_exception("ERROR", traceback.format_exc())

    def save_info_file(self, sub_dir, file_name, text_data):

        """
        save a text file into the test case log folder.

        :type sub_dir: string
        :param sub_dir: the subdir to create inside the test case log folder
        :type file_name: string
        :param file_name: the name of the image
        :type text_data: string
        :param text_data: the text to write
        """

        if self.__enable_log is True:

            folder_name = log_path + os.sep + self.__name_with_time + os.sep + sub_dir

            fullname = folder_name + os.sep + file_name

            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

        text_file = open(fullname, "w")
        text_file.write(text_data)
        text_file.close()

    def __save_numpy_image(self, sub_dir, image_name, cv2_image):
        global log_path

        #"max_file"

        if self.__enable_log is True:

            current_time = datetime.now().strftime("%H_%M_%S.%f")

            folder_name = log_path + os.sep + self.__name_with_time + os.sep + sub_dir

            fullname = folder_name + os.sep + current_time[:-3] + "_" + image_name

            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            cv2.imwrite(fullname, cv2_image)

    def __save_pil_image(self, sub_dir, image_name, pil_image):
        global log_path

        #"max_file"

        if self.__enable_log is True:

            current_time = datetime.now().strftime("%H_%M_%S.%f")

            folder_name = log_path + os.sep + self.__name_with_time + os.sep + sub_dir

            fullname = folder_name + os.sep + current_time[:-3] + "_" + image_name

            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            pil_image.save(fullname)

    def __save_cv_image(self, sub_dir, image_name, cv_image):
        global log_path

        #"max_file"

        if self.__enable_log is True:

            current_time = datetime.now().strftime("%H_%M_%S.%f")

            folder_name = log_path + os.sep + self.__name_with_time + os.sep + sub_dir

            fullname = folder_name + os.sep + current_time[:-3] + "_" + image_name

            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            cv.SaveImage(fullname, cv_image)

    def delete_all_items(self, sub_dir=None, keep_items=None, exclude_item=None):
        """
        delete old files inside the test case log folder or in its sub directory.

        :type sub_dir: string
        :param sub_dir: specify a sub folder inside the test case log folder
        :type keep_items: int
        :param keep_items: the number of items to keep
        :type exclude_item: string
        :param exclude_item: exclude a specific folder
        """

        if sub_dir is not None:
            folder_name = log_path + os.sep + self.__name_with_time + os.sep + sub_dir
        else:
            folder_name = log_path + os.sep + self.__name_with_time

        self.__delete_items_but(folder_name, keep_items, exclude_item)