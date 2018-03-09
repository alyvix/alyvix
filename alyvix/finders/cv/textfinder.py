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
from cv2 import cv
import numpy
import copy
import time
import datetime
import os
from threading import Thread
import re
import tesseract
import xml.etree.ElementTree as ET
from PIL import Image
from distutils.sysconfig import get_python_lib

from alyvix.finders.cv.basefinder import BaseFinder
from alyvix.finders.cv.basefinder import Roi
from alyvix.finders.cv.basefinder import MatchResult
from alyvix.tools.screen import ScreenManager

class _Text():

    debug_folder = None

    def __init__(self, text_dict):

        self.text = ""
        self.lang = ""
        self.whitelist = ""
        self.api = None

        self.set_text_dictionary(text_dict)

    def set_text_dictionary(self, text_dict):
        """
        converts the dictionary into the rectangles properties

        :type text_dict: dict
        :param text_dict: the dictionary that defines the text properties
        """

        if ("text" in text_dict):

            self.text = text_dict['text']

            if ("lang" in text_dict):
                self.lang = text_dict['lang']
            else:
                self.lang = "eng"

            if ("whitelist" in text_dict):
                self.whitelist = text_dict['whitelist']
            else:
                self.whitelist = "'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&:/-_\,+()*.=[]<>@"

        else:
            raise Exception("Rect dictionary has an incorrect format!")


class TextFinder(BaseFinder):

    name = None

    def __init__(self, name=None):
        """
        init the class

        :type name: string
        :param name: the object name
        """

        self.is_textfinder = True

        the_name = "text_finder"

        if name is not None:
            the_name = name

        super(TextFinder, self).__init__(the_name)
        #BaseFinder.__init__(self, the_name)

        self.api = None

        self.__phrase_backup = ""

        #self._main_component = None
        #self._sub_components = []

        self._scraper_enable = False

    def get_last_read(self):
        return self.__phrase_backup


    def set_main_component(self, text_dict, roi_dict=None):
        """
        Set the text that the find method has to find into the source Image.

        :type text_dict: dict
        :param text_dict: the dictionary that defines the main text
        :type roi_dict: dict
        :param roi_dict: the dictionary that defines the ROI
        """

        main_text = _Text(text_dict)

        if roi_dict is not None:
            roi = Roi(roi_dict)
        else:
            roi = None

        self._main_component = (main_text, roi)

    def add_sub_component(self, text_dict, roi_dict):
        """
        Add a text that the find method has to find if it has also find the main text.
        A ROI (region of interest) will be cropped from the source image according to the roi_dict.
        The find method will search the sub rectangle only inside the roi area.
        roi_x and roi_y are relative to the main rect x,y coordinates.

        :type text_dict: dict
        :param text_dict: the dictionary that defines the sub text
        :type roi_dict: dict
        :param roi_dict: the dictionary that defines the ROI
        """

        roi = Roi(roi_dict)
        sub_text = _Text(text_dict)
        self._sub_components.append((sub_text, roi))

    def scraper(self):
        if self._is_object_finder is False:
            raise Exception("A Text Scraper is out of an Object Finder")

        self._info_manager.set_info("ALYVIX SCRAPER", True)
        self._scraper_enable = True
        self.find()
        sc_text = self.get_last_read()

        roi = self._main_component[1]

        if roi is not None:

            y1 = roi.y
            y2 = y1 + roi.height
            x1 = roi.x
            x2 = x1 + roi.width

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

            # print x1,x2,y1,y2
            source_image = self._source_image_gray[y1:y2, x1:x2]
        else:
            source_image = self._source_image_gray

        self._info_manager.set_info("ALYVIX SCRAPER SOURCE IMG", source_image)

        self._log_manager.save_objects_found(self._name, source_image,
                                             [],
                                             [],
                                             self.main_xy_coordinates, self.sub_xy_coordinates, finder_type=None)

        print "text from scraper: " + sc_text

        source_image = self._source_image_gray

        self._log_manager.save_objects_found(self._name, source_image,
                                             self._objects_found,
                                             [],
                                             self.main_xy_coordinates, self.sub_xy_coordinates, finder_type=None)

        self._scraper_enable = False
        self._source_image_color = None
        self._source_image_gray = None

        if self._is_object_finder is False:
            sc_collection = self._info_manager.get_info('SCRAPER COLLECTION')
            sc_collection.append((self.get_name(), self.timestamp, sc_text))

            self._info_manager.set_info('SCRAPER COLLECTION', sc_collection)

        return sc_text

    def find(self):
        """
        find the main text and sub texts into the source image.

        :rtype: list[[MatchResult, list[MatchResult]]]
        :return: a list that contains x, y, height, width of rectangle(s) found
        """

        try:
            time_before_find = time.time()
            #print "into find"
            self._timedout_main_components = []
            self._timedout_sub_components = []

            self._objects_found = []

            source_img_auto_set = False

            res = self._info_manager.get_info("RESOLUTION")

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

            main_text = self._main_component[0]
            roi = self._main_component[1]

            if roi is not None:

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


            if self._log_manager.is_log_enable() is True:
                self._log_manager.save_image(self.__find_log_folder, "source_img.png", source_image)

            source_image = cv2.cvtColor(source_image, cv2.COLOR_BGR2RGB)
            source_image_pil = Image.fromarray(source_image)
            width = source_image_pil.size[0]
            height = source_image_pil.size[1]
            source_image = source_image_pil.resize((width * 3, height * 3), Image.BICUBIC)

            """
            if self._log_manager.is_log_enable() is True:
                self._log_manager.save_image(self.__find_log_folder, "resized.png", source_image)
            """

            objects_found = []
            analyzed_points = []
            self._objects_found = []

            cnt = 0

            self.api = tesseract.TessBaseAPI()
            self.api.Init(get_python_lib() + os.sep + "alyvix" + os.sep + "extra" + os.sep +
                          "Tesseract-OCR" + os.sep, main_text.lang, tesseract.OEM_DEFAULT)
            self.api.SetPageSegMode(tesseract.PSM_AUTO)
            self.api.SetVariable("tessedit_char_whitelist", main_text.whitelist)

            phrase = ""
            concatWord = False
            wordLine = None

            timex = time.time()

            color_img = cv.CreateImageHeader(source_image.size, cv.IPL_DEPTH_8U, 3)

            cv.SetData(color_img, source_image.tobytes())

            grey_img = cv.CreateImage(cv.GetSize(color_img), 8, 1)

            cv.CvtColor(color_img, grey_img, cv.CV_RGB2GRAY)

            if self._log_manager.is_log_enable() is True:
                self._log_manager.save_image(self.__find_log_folder, "resized.png", grey_img)

            #cv.SaveImage('c:\\alan\\image2.jpg', grey_img)
            tesseract.SetCvImage(grey_img, self.api)

            #write debug image
            #LogManager.WriteCvImage(datetime.now().strftime("%H_%M_%S_%f") + '_Grey.png', grey_img)

            #text=Ocr.Api.GetUTF8Text()
            
            if self._log_manager.is_log_enable() is True:
                textfile_log_name = datetime.datetime.now().strftime("%H_%M_%S.%f")[:-3] + "_resized.txt"

            text = self.api.GetHOCRText(0)

            #print text
            root = ET.fromstring(text)

            line_sep = ""
            break_loop = False
            self.__phrase_backup = ""
            for span in root.iter('span'):
                object_found = []
                object_found.append([])
                object_found.append([])

                """
                if self._flag_thread_have_to_exit is True:
                    self._flag_thread_have_to_exit = False
                    self._flag_thread_started = False
                    self._source_image_color = None
                    self._source_image_gray = None
                    return []
                """

                try:
                    #print span.attrib,span.text
                    #print span.get('title')

                    title = span.get('title')
                    title = title.replace(';', '')
                    coordinates = title.split(' ')

                    if span.get('class') == 'ocr_line':
                        line = span.get('id')
                        line = line.replace('line_','')
                        lineNr = line
                        line_sep = "\n" #"RRRRRRR" #os.linesep

                    if not span.find('strong') ==  None:
                        span.text = span.find('strong').text

                    if not span.find('em') ==  None:
                        span.text = span.find('em').text

                    if not span.find('strong/em') ==  None:
                        span.text = span.find('strong/em').text

                    if span.text == None:
                        continue

                    phrase = phrase + " " + span.text #+ line_sep
                    self.__phrase_backup = self.__phrase_backup + " " + line_sep + span.text

                    if line_sep != "":
                        line_sep = ""

                    #print phrase
                    #print main_text.text

                    result = re.match(".*" + unicode(main_text.text, "UTF-8") + ".*", phrase, re.DOTALL | re.IGNORECASE)

                    #print span.text," >> line:",lineNr,"coordinates:",int(coordinates[1])/3,int(coordinates[2])/3,int(coordinates[3])/3,int(coordinates[4])/3
                    #print "text found:",phrase
                    

                    #print "tempo ocr", time.time() - timex
                    if result != None:

                        x = offset_x + (int(coordinates[1])/3)
                        y = offset_y + (int(coordinates[2])/3)
                        #print "offset x, x", offset_x, (int(coordinates[1])/3)
                        #print "offset y, y", offset_y, (int(coordinates[2])/3)


                        w = (int(coordinates[3])/3) - (int(coordinates[1])/3)
                        h = (int(coordinates[4])/3) - (int(coordinates[2])/3)

                        self._timedout_main_components.append(MatchResult((x, y, w, h)))

                        try:
                            #print "text from Ocr engine:",phrase
                            #print "ocr time:",time.time() - timex,"sec."
                            #phrase = phrase.replace(main_text.text,"")
                            insensitive_phrase = re.compile(main_text.text, re.IGNORECASE)
                            #insensitive_phrase = re.compile(re.escape(main_text.text), re.IGNORECASE)
                            phrase = insensitive_phrase.sub('', phrase)
                            #print phrase

                        except Exception, err:
                            pass #print err

                        sub_texts_len = len(self._sub_components)

                        if sub_texts_len == 0:
                            #good_points.append((x, y, w, h))

                            main_object_result = MatchResult((x, y, w, h))
                            object_found[0] = main_object_result

                            object_found[1] = None
                            objects_found.append(object_found)
                        else:

                            total_sub_template_found = 0

                            sub_objects_found = []
                            timed_out_objects = []
                            for sub_text in self._sub_components:
                                #print "entering in sub text"

                                """
                                if self._flag_thread_have_to_exit is True:
                                    self._flag_thread_have_to_exit = False
                                    self._flag_thread_started = False
                                    self._source_image_color = None
                                    self._source_image_gray = None
                                    return []
                                """

                                sub_template_coordinates = self._find_sub_text((x, y), sub_text)

                                if sub_template_coordinates is not None:
                                    sub_objects_found.append(sub_template_coordinates)
                                    total_sub_template_found = total_sub_template_found + 1
                                    timed_out_objects.append((sub_template_coordinates, sub_text[1]))
                                else:
                                    timed_out_objects.append((None, sub_text[1]))

                                if total_sub_template_found == sub_texts_len:
                                    #good_points.append((x, y, w, h))

                                    main_object_result = MatchResult((x, y, w, h))
                                    object_found[0] = main_object_result

                                    object_found[1] = sub_objects_found

                                    objects_found.append(object_found)
                                    #print "len obj found:", len(objects_found)
                                    #print "appended"
                                    break_loop = True

                            self._timedout_sub_components.append(timed_out_objects)
                            #if break_loop is True:
                            #    break

                        # write debug message
                        #LogManager.WriteMessage("debug", "text from Ocr engine: " + phrase)
                        #return int(coordinates[1]),int(coordinates[2]),int(coordinates[3]),int(coordinates[4])

                except Exception, err:
                    pass #print err
                    #LogManager.IsInError = True
                    #LogManager.WriteMessage("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))


            if self._log_manager.is_log_enable() is True:
                self._log_manager.save_info_file(self.__find_log_folder, textfile_log_name, self.__phrase_backup)

            #print len(objects_found)
            if len(objects_found) > 0:
                self._objects_found = copy.deepcopy(objects_found)
                if self._is_object_finder is True:
                    self._objects_found_of_sub_object_finder.extend(copy.deepcopy(objects_found))
                    #gray_source_img = cv2.cvtColor(self._source_image, cv2.COLOR_BGR2GRAY)

                    #if self._info_manager.get_info('LOG OBJ IS FOUND') is False:
                    if self._info_manager.get_info('LOG OBJ FINDER TYPE') is None:
                        self._info_manager.set_info('LOG OBJ FINDER TYPE', 2)

                    # if wait_disappear is False:
                    self._log_manager.save_objects_found(self._name, self.get_source_image_gray(),
                                                         self._objects_found, [x[1] for x in self._sub_components],
                                                         self.main_xy_coordinates, self.sub_xy_coordinates, finder_type=2)

                self._cacheManager.SetLastObjFoundFullImg(self._source_image_gray)

            if source_img_auto_set is True and self._scraper_enable is False:
                self._source_image_color = None
                self._source_image_gray = None
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

            return self._objects_found

        except Exception, err:
            self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
            return None

    def _find_sub_text(self, main_template_xy=None, sub_text=None):
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
            sub_text_arg = sub_text[0]
            roi = sub_text[1]

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

            if self._log_manager.is_log_enable() is True:
                self._log_manager.save_image(self.__find_log_folder, "sub_source_img.png", source_image_cropped)

            source_image = cv2.cvtColor(source_image_cropped, cv2.COLOR_BGR2RGB)
            source_image_pil = Image.fromarray(source_image)
            width = source_image_pil.size[0]
            height = source_image_pil.size[1]
            source_image = source_image_pil.resize((width * 3, height * 3), Image.BICUBIC)

            """
            self.api = tesseract.TessBaseAPI()
            self.api.Init("C:\\Program Files (x86)\\Tesseract-OCR\\", main_text.lang, tesseract.OEM_DEFAULT)
            self.api.SetPageSegMode(tesseract.PSM_AUTO)
            self.api.SetVariable("tessedit_char_whitelist", main_text.whitelist)
            """

            self.api.Init(get_python_lib() + os.sep + "alyvix" + os.sep + "extra" + os.sep +
                          "Tesseract-OCR" + os.sep, sub_text_arg.lang, tesseract.OEM_DEFAULT)
            self.api.SetPageSegMode(tesseract.PSM_AUTO)
            self.api.SetVariable("tessedit_char_whitelist", sub_text_arg.whitelist)

            phrase = ""
            concatWord = False
            wordLine = None

            timex = time.time()

            color_img = cv.CreateImageHeader(source_image.size, cv.IPL_DEPTH_8U, 3)

            cv.SetData(color_img, source_image.tobytes())

            grey_img = cv.CreateImage(cv.GetSize(color_img), 8, 1)

            cv.CvtColor(color_img, grey_img, cv.CV_RGB2GRAY)

            if self._log_manager.is_log_enable() is True:
                self._log_manager.save_image(self.__find_log_folder, "sub_resized.png", grey_img)
                textfile_sub_log_name = datetime.datetime.now().strftime("%H_%M_%S.%f")[:-3] + "_sub_resized.txt"

            #cv.SaveImage('c:\\alan\\image2.jpg', grey_img)
            tesseract.SetCvImage(grey_img, self.api)

            #write debug image
            #LogManager.WriteCvImage(datetime.now().strftime("%H_%M_%S_%f") + '_Grey.png', grey_img)

            #text=Ocr.Api.GetUTF8Text()

            text = self.api.GetHOCRText(0)

            #print text
            root = ET.fromstring(text)

            for span in root.iter('span'):

                try:
                    #print span.attrib,span.text
                    #print span.get('title')

                    title = span.get('title')
                    title = title.replace(';', '')
                    coordinates = title.split(' ')

                    if span.get('class') == 'ocr_line':
                        line = span.get('id')
                        line = line.replace('line_','')
                        lineNr = line

                    if not span.find('strong') ==  None:
                        span.text = span.find('strong').text

                    if not span.find('em') ==  None:
                        span.text = span.find('em').text

                    if not span.find('strong/em') ==  None:
                        span.text = span.find('strong/em').text

                    if span.text == None:
                        continue

                    phrase = phrase + " " + span.text
                    #print phrase

                    result = re.match(".*" + unicode(sub_text_arg.text, "UTF-8") + ".*", phrase, re.DOTALL | re.IGNORECASE)

                    #print span.text," >> line:",lineNr,"coordinates:",int(coordinates[1])/3,int(coordinates[2])/3,int(coordinates[3])/3,int(coordinates[4])/3
                    #print "text found:",phrase

                    #print "tempo ocr", time.time() - timex

                    if self._log_manager.is_log_enable() is True:
                        self._log_manager.save_info_file(self.__find_log_folder, textfile_sub_log_name, phrase)

                    if result != None:

                        """
                        try:
                            #print "text from Ocr engine SUBBB:",phrase
                            #print "ocr time:",time.time() - timex,"sec."
                            #phrase = phrase.replace(sub_text_arg.text,"")
                            insensitive_phrase = re.compile(re.escape(sub_text_arg.text), re.IGNORECASE)
                            phrase = insensitive_phrase.sub('', phrase)
                        except:
                            pass
                        """

                        #good_points.append((x, y, w, h))

                        x = int(coordinates[1])/3
                        y = int(coordinates[2])/3
                        w = (int(coordinates[3])/3) - x
                        h = (int(coordinates[4])/3) - y

                        sub_object_result = MatchResult((x1 + x, y1 + y, w, h))

                        #print "sub offset x, x, w", x1, (int(coordinates[1])/3), w
                        #print "sub offset y, y, h", y1, (int(coordinates[2])/3), h

                        #print "founded"
                        return sub_object_result
                except Exception, err:
                    pass #print "error:", err

            return None
        except Exception, err:
            self._log_manager.save_exception("ERROR", "an exception has occurred: " + str(err) + " on line " + str(sys.exc_traceback.tb_lineno))
            return None