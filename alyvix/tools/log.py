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

import sys
import cv2
import cv2.cv as cv
import os
import shutil
import time
import numpy
from PIL import Image
from images2gif import writeGif
from datetime import datetime, timedelta
from alyvix.tools.configreader import ConfigReader
from alyvix.bridge.robot import RobotManager
from alyvix.tools.info import InfoManager

log_path = None

class LogManager:

    #__image = None
    #__main_object_points = None
    #__sub_objects_points = []

    def __init__(self):

        self._config_reader = ConfigReader()

        self.__enable_log = self._config_reader.get_log_enable_value()

        self.__set_log_path()

        self._robot_manager = RobotManager()

        self._info_manager = InfoManager()
        self._info_manager.tiny_update()

        self._robot_context = self._info_manager.get_info("ROBOT CONTEXT")

        if self._robot_context:
            if self._info_manager.get_robot_log_deleted_flag() is False:
                filelist = [f for f in os.listdir( self._info_manager.get_info('OUTPUT DIR'))]
                for f in filelist:
                    try:
                        os.remove(self._info_manager.get_info('OUTPUT DIR') + os.sep + f)
                    except:
                        pass

                self._info_manager.set_robot_log_deleted_flag(True)


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

    def save_objects_found(self, image_name, image_data, objects_found, roi, disappear_mode=False):
        """
        save the image into the test case log folder.

        :type sub_dir: string
        :param sub_dir: the subdir to create inside the test case log folder
        :type image_name: string
        :param image_name: the name of the image
        :type image_data: numpy.ndarray or Image.Image or cv.iplimage
        :param image_data: the image data to save
        :type objects_found: list[(int, int, int, int), list[(int, int, int, int), ...]]
        :param objects_found: coordinates of objects found
        :type roi: Roi
        :param roi: sub components roi
        """

        if self.__enable_log is True or self._robot_context is True:
            
            
            scaling_factor = self._info_manager.get_info("SCALING FACTOR INT")

            overwrite_images = self._info_manager.get_info("OVERWRITE LOG IMAGES")

            if overwrite_images is None:
                overwrite_images = True

            img_gray = image_data.copy()
            img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)


            img_h, img_w = img_gray.shape

            #main_color = [(0, 0, 255), (0, 255, 0), (0, 255, 255), (255, 0, 0)]   #red, green, yellow ,blue
            #sub_color = [(255, 0, 255), (255, 255, 0), (0, 170, 255), (255, 85, 170) ]  #violet, light blue, orange, dark violet

            rect_border_color = (0, 0, 255)
            rect_fill_color = (255, 0, 255)

            """
            main_rect_border = (0, 0, 255)
            main_rect_fill = (255, 0, 255)

            sub_rect_border = (198, 0, 255)
            sub_rect_fill = (246, 96, 172)
            """

            index = 1
            for object in objects_found:

                main_x = object[0].x
                main_y = object[0].y
                w = object[0].width
                h = object[0].height

                x2 = main_x + object[0].width
                y2 = main_y + object[0].height

                """
                if index >= 3:
                    color = main_color[3]
                else:
                    color = main_color[index]
                """

                text_color = rect_border_color  #(255, 255, 255)

                cv2.rectangle(img_color, (main_x, main_y), (main_x+w, main_y+h), rect_border_color, scaling_factor)

                image = numpy.zeros((img_h, img_w, 3), numpy.uint8)
                image[:] = rect_fill_color
                alpha = 0.5
                cv2.addWeighted(image[main_y:y2, main_x:x2], alpha, img_color[main_y:y2, main_x:x2], 1.0 - alpha, 0,
                                img_color[main_y:y2, main_x:x2])

                font = cv2.FONT_HERSHEY_PLAIN
                text = str(index) + ":0"

                cv2.putText(img_color, text, (main_x, main_y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)

                sub_index = 0
                if object[1] is not None:

                    for sub_obj in object[1]:

                        """
                        if index >= 3:
                            color = sub_color[3]
                        else:
                            color = sub_color[index]
                        """

                        text_color = rect_border_color  #(255, 255, 255)

                        x = sub_obj.x
                        y = sub_obj.y
                        w = sub_obj.width
                        h = sub_obj.height

                        x2 = x + sub_obj.width
                        y2 = y + sub_obj.height

                        roi_x = main_x + roi[sub_index].x
                        roi_y = main_y + roi[sub_index].y
                        roi_width = roi[sub_index].width
                        roi_height = roi[sub_index].height
                        cv2.rectangle(img_color, (roi_x, roi_y), (roi_x+roi_width, roi_y+roi_height),
                                      rect_border_color, scaling_factor)

                        cv2.rectangle(img_color, (x, y), (x+w, y+h), rect_border_color, scaling_factor)

                        image = numpy.zeros((img_h, img_w, 3), numpy.uint8)
                        image[:] = rect_fill_color
                        alpha = 0.5
                        cv2.addWeighted(image[y:y2, x:x2], alpha, img_color[y:y2, x:x2], 1.0 - alpha, 0, img_color[y:y2, x:x2])

                        text = str(index) + ":" + str(sub_index + 1)

                        #cv2.rectangle(img_color, (box_text_x, box_text_y - 2), (box_text_x+text_size[0], box_text_y+text_size[1]), color, -1)
                        #cv2.putText(img_color, text, (x + scaling_factor,y - scaling_factor), font, scaling_factor, (0, 0, 0), scaling_factor, cv2.CV_AA)
                        cv2.putText(img_color, text, (roi_x,roi_y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)
                        cv2.putText(img_color, text, (x,y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)
                        sub_index = sub_index + 1

                index = index + 1

            if self._robot_context is True:
                outputdir = self._robot_manager.get_output_directory()

                index = 1
                file_name = image_name

                if overwrite_images is False:
                    while os.path.isfile(outputdir + os.sep + file_name + ".png"):

                        file_name = image_name + "_" + str(index)
                        index = index + 1

                file_name = file_name + ".png"

                cv2.imwrite(outputdir + os.sep + file_name, img_color)  #, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

                if disappear_mode is False:
                    self._robot_manager.write_log_message("<a href=\"" + file_name + "\"><img width=\"800\" src=\"" + file_name + "\"></a>", "INFO", True)
                else:
                    self._robot_manager.write_log_message("<a href=\"" + file_name + "\"><img width=\"800\" src=\"" + file_name + "\"></a>", "ERROR", True)

    def save_timedout_objects(self, image_name, image_data, main_components, sub_components, main_extra_img, sub_extra_images, save_only_extra=False, object_name=None, disappear_mode=False):
        """
        save the image into the test case log folder.

        :type sub_dir: string
        :param sub_dir: the subdir to create inside the test case log folder
        :type image_name: string
        :param image_name: the name of the image
        :type image_data: numpy.ndarray or Image.Image or cv.iplimage
        :param image_data: the image data to save
        :type objects_found: list[(int, int, int, int), list[(int, int, int, int), ...]]
        :param objects_found: coordinates of objects found
        :type roi: Roi
        :param roi: sub components roi
        """

        gif_images = []
        gif_images_extra = []

        if self.__enable_log is True or self._robot_context is True:

            if self._robot_context is True:

                outputdir = self._robot_manager.get_output_directory()

            else:
                outputdir = "."

            scaling_factor = self._info_manager.get_info("SCALING FACTOR INT")

            overwrite_images = self._info_manager.get_info("OVERWRITE LOG IMAGES")

            if overwrite_images is None:
                overwrite_images = True

            img_gray = image_data.copy()
            img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)

            img_h, img_w = img_gray.shape

            extra_img_color = None
            extra_img_roi_xy = None

            if main_extra_img is not None:
                extra_img_roi_xy = main_extra_img[1]

            if extra_img_roi_xy is None and main_extra_img is not None:
                extra_img_gray = main_extra_img[0].copy()
                extra_img_color = cv2.cvtColor(extra_img_gray, cv2.COLOR_GRAY2RGB)
            elif main_extra_img is not None:
                extra_img_gray = main_extra_img[0].copy()
                extra_img_color = numpy.zeros((img_h, img_w, 3), numpy.uint8)
                extra_img_color[:] = (0, 0, 0)
                extra_img_color[extra_img_roi_xy[1]:extra_img_roi_xy[3], extra_img_roi_xy[0]:extra_img_roi_xy[2]] = cv2.cvtColor(extra_img_gray, cv2.COLOR_GRAY2RGB)
                cv2.imwrite("c:\\log\\rrr_kkk.png", extra_img_color)

            #cv2.imwrite("c:\\log\\ssasasa.png", extra_img_color)

            #file_name = self._check_if_img_exists(outputdir, image_name)
            #cv2.imwrite(outputdir + os.sep + file_name, img_color)

            #gif_images.append(Image.fromarray(cv2.cvtColor(img_color,cv2.COLOR_BGR2RGB)))

            #extra_img_black = numpy.zeros((img_h, img_w, 3), numpy.uint8)
            #extra_img_black[:] = (0, 0, 0)

            #main_color = [(0, 0, 255), (0, 255, 0), (0, 255, 255), (255, 0, 0)]   #red, green, yellow ,blue
            #sub_color = [(255, 0, 255), (255, 255, 0), (0, 170, 255), (255, 85, 170) ]  #violet, light blue, orange, dark violet

            rect_border_color = (0, 0, 255)
            rect_fill_color = (255, 0, 255)

            """
            main_rect_border = (0, 0, 255)
            main_rect_fill = (255, 0, 255)

            sub_rect_border = (198, 0, 255)
            sub_rect_fill = (246, 96, 172)
            """

            index = 0

            for object in main_components:

                try:

                    main_rect = None
                    sub_rect = []

                    main_x = object.x
                    main_y = object.y
                    w = object.width
                    h = object.height

                    x2 = main_x + object.width
                    y2 = main_y + object.height

                    """
                    if index >= 3:
                        color = main_color[3]
                    else:
                        color = main_color[index]
                    """

                    text_color = rect_border_color  #(255, 255, 255)

                    cv2.rectangle(img_color, (main_x, main_y), (main_x+w, main_y+h), rect_border_color, scaling_factor)

                    cv2.imwrite("c:\\log\\ttt.png", img_color)
                    cv2.imwrite("c:\\log\\rrr.png", extra_img_color)

                    cv2.rectangle(extra_img_color, (main_x, main_y), (main_x+w, main_y+h), rect_border_color, scaling_factor)

                    cv2.imwrite("c:\\log\\rrr.png", extra_img_color)

                    image = numpy.zeros((img_h, img_w, 3), numpy.uint8)
                    image[:] = rect_fill_color
                    alpha = 0.5
                    cv2.addWeighted(image[main_y:y2, main_x:x2], alpha, img_color[main_y:y2, main_x:x2], 1.0 - alpha, 0,
                                    img_color[main_y:y2, main_x:x2])

                    if extra_img_color is not None:
                        cv2.addWeighted(image[main_y:y2, main_x:x2], alpha, extra_img_color[main_y:y2, main_x:x2], 1.0 - alpha, 0,
                                        extra_img_color[main_y:y2, main_x:x2])

                    font = cv2.FONT_HERSHEY_PLAIN
                    text = "1:0" #str(index + 1) + ":0"

                    cv2.putText(img_color, text, (main_x, main_y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)
                    cv2.putText(extra_img_color, text, (main_x, main_y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)

                    main_rect = (main_x, main_y, w, h, text)

                    #file_name = self._check_if_img_exists(outputdir, image_name)
                    cv2.imwrite("c:\\log\\rrr.png", extra_img_color)

                    #gif_images.append(outputdir + os.sep + file_name)

                    """
                    if edges_img is not None:
                        img2 = numpy.zeros_like(img_color)
                        img2[:,:,0] = edges_img
                        img2[:,:,1] = edges_img
                        img2[:,:,2] = edges_img
                        gif_images.append(Image.fromarray(img2))
                    """
                    gif_images.append(Image.fromarray(cv2.cvtColor(img_color,cv2.COLOR_BGR2RGB)))

                    if extra_img_color is not None:
                        gif_images_extra.append(Image.fromarray(cv2.cvtColor(extra_img_color,cv2.COLOR_BGR2RGB)))

                    #img_gray = image_data.copy()
                    #img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)

                    sub_index = 0

                    for sub_obj in sub_components[index]:

                        text_color = rect_border_color  #(255, 255, 255)

                        """
                        if index >= 3:
                            color = sub_color[3]
                        else:
                            color = sub_color[index]
                        """

                        obj = sub_obj[0]
                        roi = sub_obj[1]

                        #extra_img_roi_xy = sub_extra_images[sub_index][1]

                        if extra_img_roi_xy is None and main_extra_img is not None:
                            extra_img_gray = main_extra_img[0].copy()
                            extra_img_color = cv2.cvtColor(extra_img_gray, cv2.COLOR_GRAY2RGB)
                        elif main_extra_img is not None:
                            extra_img_gray = main_extra_img[0].copy()
                            extra_img_color = numpy.zeros((img_h, img_w, 3), numpy.uint8)
                            extra_img_color[:] = (0, 0, 0)
                            extra_img_color[extra_img_roi_xy[1]:extra_img_roi_xy[3], extra_img_roi_xy[0]:extra_img_roi_xy[2]] = cv2.cvtColor(extra_img_gray, cv2.COLOR_GRAY2RGB)


                        if len(sub_extra_images) > 0:
                            sub_extra_img_gray = sub_extra_images[index][sub_index][0].copy()
                            sub_extra_img_color = cv2.cvtColor(sub_extra_img_gray, cv2.COLOR_GRAY2RGB)

                        #extra_black_image = numpy.zeros((img_h, img_w, 3), numpy.uint8)
                        #extra_black_image[:] = (0, 0, 0)

                        roi_x = main_x + roi.x
                        roi_y = main_y + roi.y
                        roi_width = roi.width
                        roi_height = roi.height

                        #ex_x1 = sub_extra_images[index][sub_index][1][0]
                        #ex_y1 = sub_extra_images[index][sub_index][1][1]

                        if roi_x < 0:
                            roi_width = roi_width + roi_x
                            roi_x = 0

                        if len(sub_extra_images) > 0:
                            ex_x2 = roi_x + sub_extra_img_color.shape[1]
                            ex_y2 = roi_y + sub_extra_img_color.shape[0]

                            if ex_x2 > img_w:
                                ex_x2 = img_w

                            if ex_y2 > img_h:
                                ex_y2 = img_h


                        if roi_y < 0:
                            continue

                        if len(sub_extra_images) > 0:
                            extra_img_color[roi_y:ex_y2, roi_x:ex_x2] = sub_extra_img_color

                            for extra_sub in sub_rect:
                                se_x = extra_sub[0]
                                se_y = extra_sub[1]
                                se_w = extra_sub[2]
                                se_h = extra_sub[3]
                                se_roi_x = extra_sub[4]
                                se_roi_y = extra_sub[5]
                                se_roi_w = extra_sub[6]
                                se_roi_h = extra_sub[7]
                                se_text = extra_sub[8]

                                cv2.rectangle(extra_img_color, (se_roi_x, se_roi_y), (se_roi_x+se_roi_w, se_roi_y+se_roi_h),
                                              rect_border_color, scaling_factor)

                                cv2.putText(extra_img_color, se_text, (se_roi_x,se_roi_y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)

                                if se_x is not None:

                                    se_x2 = se_x + se_w
                                    se_y2 = se_y + se_h

                                    cv2.rectangle(extra_img_color, (se_x, se_y), (se_x+se_w, se_y+se_h), rect_border_color, scaling_factor)

                                    image = numpy.zeros((img_h, img_w, 3), numpy.uint8)
                                    image[:] = rect_fill_color
                                    alpha = 0.5

                                    cv2.addWeighted(image[se_y:se_y2, se_x:se_x2], alpha, extra_img_color[se_y:se_y2, se_x:se_x2], 1.0 - alpha, 0, extra_img_color[se_y:se_y2, se_x:se_x2])

                                    cv2.putText(extra_img_color, se_text, (se_x,se_y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)

                            #main_rect = (main_x, main_y, w, h, text)

                        if extra_img_color is not None:
                            cv2.rectangle(extra_img_color, (main_rect[0], main_rect[1]), (main_rect[0]+main_rect[2], main_rect[1]+main_rect[3]),
                                          rect_border_color, scaling_factor)

                            m_y2 = main_rect[1] + main_rect[3]
                            m_x2 = main_rect[0] + main_rect[2]
                            cv2.addWeighted(image[main_rect[1]:m_y2, main_rect[0]:m_x2], alpha, extra_img_color[main_rect[1]:m_y2, main_rect[0]:m_x2], 1.0 - alpha, 0,
                                        extra_img_color[main_rect[1]:m_y2, main_rect[0]:m_x2])

                            cv2.rectangle(extra_img_color, (roi_x, roi_y), (roi_x+roi_width, roi_y+roi_height),
                                          rect_border_color, scaling_factor)

                        cv2.rectangle(img_color, (roi_x, roi_y), (roi_x+roi_width, roi_y+roi_height),
                                      rect_border_color, scaling_factor)

                        text = "1:" + str(sub_index + 1) #str(index + 1) + ":" + str(sub_index + 1)

                        cv2.putText(img_color, text, (roi_x,roi_y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)

                        if extra_img_color is not None:
                            cv2.putText(extra_img_color, main_rect[4],  (main_rect[0], main_rect[1]), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)
                            cv2.putText(extra_img_color, text, (roi_x,roi_y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)

                        #file_name = self._check_if_img_exists(outputdir, image_name)
                        #cv2.imwrite(outputdir + os.sep + file_name, img_color)

                        #gif_images.append(outputdir + os.sep + file_name)

                        """
                        if edges_img is not None:
                            img2 = numpy.zeros_like(img_color)
                            img2[:,:,0] = edges_img
                            img2[:,:,1] = edges_img
                            img2[:,:,2] = edges_img
                            gif_images.append(Image.fromarray(img2))
                        """
                        gif_images.append(Image.fromarray(cv2.cvtColor(img_color,cv2.COLOR_BGR2RGB)))

                        if extra_img_color is not None:
                            gif_images_extra.append(Image.fromarray(cv2.cvtColor(extra_img_color,cv2.COLOR_BGR2RGB)))

                        if obj is not None:
                            x = obj.x
                            y = obj.y
                            w = obj.width
                            h = obj.height

                            x2 = x + obj.width
                            y2 = y + obj.height

                            cv2.rectangle(img_color, (x, y), (x+w, y+h), rect_border_color, scaling_factor)

                            if extra_img_color is not None:
                                cv2.rectangle(extra_img_color, (x, y), (x+w, y+h), rect_border_color, scaling_factor)

                            image = numpy.zeros((img_h, img_w, 3), numpy.uint8)
                            image[:] = rect_fill_color
                            alpha = 0.5
                            cv2.addWeighted(image[y:y2, x:x2], alpha, img_color[y:y2, x:x2], 1.0 - alpha, 0, img_color[y:y2, x:x2])

                            if extra_img_color is not None:
                                cv2.addWeighted(image[y:y2, x:x2], alpha, extra_img_color[y:y2, x:x2], 1.0 - alpha, 0, extra_img_color[y:y2, x:x2])

                                cv2.putText(extra_img_color, text, (x,y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)

                            cv2.putText(img_color, text, (x,y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)

                            #file_name = self._check_if_img_exists(outputdir, image_name)
                            #cv2.imwrite(outputdir + os.sep + file_name, img_color)

                            #gif_images.append(outputdir + os.sep + file_name)

                            """
                            if edges_img is not None:
                                img2 = numpy.zeros_like(img_color)
                                img2[:,:,0] = edges_img
                                img2[:,:,1] = edges_img
                                img2[:,:,2] = edges_img
                                gif_images.append(Image.fromarray(img2))
                            """
                            gif_images.append(Image.fromarray(cv2.cvtColor(img_color,cv2.COLOR_BGR2RGB)))

                            if extra_img_color is not None:
                                gif_images_extra.append(Image.fromarray(cv2.cvtColor(extra_img_color,cv2.COLOR_BGR2RGB)))
                            sub_rect.append((x, y, w, h, roi_x, roi_y, roi_width, roi_height, text))

                        else:
                            sub_rect.append((None, None, None, None, roi_x, roi_y, roi_width, roi_height, text))


                        #cv2.rectangle(img_color, (box_text_x, box_text_y - 2), (box_text_x+text_size[0], box_text_y+text_size[1]), color, -1)
                        #cv2.putText(img_color, text, (x + scaling_factor,y - scaling_factor), font, scaling_factor, (0, 0, 0), scaling_factor, cv2.CV_AA)
                        #cv2.putText(img_color, text, (roi_x,roi_y), font, scaling_factor, text_color, scaling_factor, cv2.CV_AA)

                        sub_index = sub_index + 1

                    index = index + 1

                    #img_gray = image_data.copy()
                    #img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)

                    """
                    if self._robot_context is True:
                        outputdir = self._robot_manager.get_output_directory()

                        imgname_index = 1
                        file_name = image_name
                        while os.path.isfile(outputdir + os.sep + file_name + ".png"):

                            file_name = image_name + "_" + str(imgname_index)
                            imgname_index = imgname_index + 1

                        file_name = file_name + ".png"

                        cv2.imwrite(outputdir + os.sep + file_name, img_color)  #, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

                        if index == 0:
                            msg_type = "ERROR"
                        else:
                            msg_type = "INFO"
                        #self._robot_manager.write_log_message("<a href=\"" + file_name + "\"><img width=\"800\" src=\"" + file_name + "\"></a>", msg_type, True)
                        """

                    img_gray = image_data.copy()
                    img_color = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)

                    if main_extra_img is not None:
                        extra_img_roi_xy = main_extra_img[1]

                    if extra_img_roi_xy is None and main_extra_img is not None:
                        extra_img_gray = main_extra_img[0].copy()
                        extra_img_color = cv2.cvtColor(extra_img_gray, cv2.COLOR_GRAY2RGB)

                    #index = index + 1

                #images = [Image.open(fn) for fn in gif_images]


                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    #print(exc_type, fname, exc_tb.tb_lineno)
                    index = index + 1


            if len(main_components) == 0:
                gif_images.append(Image.fromarray(cv2.cvtColor(img_color,cv2.COLOR_BGR2RGB)))

            if extra_img_color is not None and len(main_components) == 0:
                gif_images_extra.append(Image.fromarray(cv2.cvtColor(extra_img_color,cv2.COLOR_BGR2RGB)))

            if save_only_extra is False:

                if overwrite_images is False:
                    file_name = self._check_if_img_exists(outputdir, image_name, "gif")
                else:
                    file_name = image_name + ".gif"

                writeGif(outputdir + os.sep + file_name, gif_images, duration=1)

                if disappear_mode is False:
                    self._robot_manager.write_log_message("<a href=\"" + file_name + "\"><img width=\"800\" src=\"" + file_name + "\"></a>", "ERROR", True)
                else:
                    self._robot_manager.write_log_message("<a href=\"" + file_name + "\"><img width=\"800\" src=\"" + file_name + "\"></a>", "INFO", True)

            if overwrite_images is False:
                file_name = self._check_if_img_exists(outputdir, image_name + "_extra", "gif")
            else:
                file_name = image_name + "_extra.gif"

            if extra_img_color is not None:
                writeGif(outputdir + os.sep + file_name, gif_images_extra, duration=1)

                if object_name is None:
                    self._robot_manager.write_log_message("click <a href=\"" + file_name + "\">here</a> to see the extra image", "INFO", True)
                else:
                    self._robot_manager.write_log_message("click <a href=\"" + file_name + "\">here</a> to see the extra image of " + object_name, "INFO", True)


            """
            if edges_img is not None:
                file_name = self._check_if_img_exists(outputdir, image_name + "_edges", "png")
                cv2.imwrite(outputdir + os.sep + file_name, edges_img)
                self._robot_manager.write_log_message("click <a href=\"" + file_name + "\">here</a> to see the edges image", "INFO", True)
            """

    def _check_if_img_exists(self, outputdir, image_name, ext="gif"):

        file_name = image_name + "_1"

        imgname_index = 1

        while os.path.isfile(outputdir + os.sep + file_name + "." + ext):

            file_name = image_name + "_" + str(imgname_index)
            imgname_index = imgname_index + 1

        file_name = file_name + "." + ext

        return file_name


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