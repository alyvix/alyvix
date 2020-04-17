# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2019 Alan Pipitone
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
import time
import cv2
import numpy as np
import re
import difflib
import datetime
import base64
import alyvix.core.tesserocr as tesserocr
from PIL import Image
from alyvix.core.utilities.args import ArgsManager
from alyvix.tools.screen import ScreenManager
from alyvix.tools.crypto import CryptoManager
from alyvix.core.contouring import ContouringManager


class Result():
    def __init__(self):
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.type = "T"
        self.scraped_text = None
        self.group = 0
        self.is_main = False
        self.index_in_tree = 0
        self.index_in_group = 0
        self.mouse = {}
        self.keyboard = {}
        self.roi = None
        self.extract_text = None
        self.check = False


class TextManager():

    def __init__(self, cipher_key=None, cipher_iv=None):

        self._color_screen = None
        self._gray_screen = None
        self._scaling_factor = None

        self._scale_for_tesseract = 2

        self._regexp = ""

        self._arguments = None

        self._tessdata_path = os.path.dirname(__file__) + os.sep + "tessdata"

        self._map = None

        self._crypto_manager = CryptoManager()
        self._crypto_manager.set_key(cipher_key)
        self._crypto_manager.set_iv(cipher_iv)

        self._dict_month = {
            "ja(m|n|nn)uar(y|v)": "1",
            "(7|f|t)ebruar(y|v)": "2",
            "(m|n|nn)arch": "3",
            "apr(l|1|i)(l|1|i)": "4",
            "(m|n|nn)a(y|v)": "5",
            "ju(m|n|nn)e": "6",
            "ju(l|1|i)(y|v)": "7",
            "au(g|q)u(5|s)(7|f|t)": "8",
            "(5|s)ep(7|f|t)e(m|n|nn)ber": "9",
            "(o|0)c(7|f|t)(o|0)ber": "10",
            "(m|n|nn)(o|0)(y|v)e(m|n|nn)ber": "11",
            "dece(m|n|nn)ber": "12",

            "ja(m|n|nn).": "1",
            "(7|f|t)eb.": "2",
            "(m|n|nn)ar.": "3",
            "apr.": "4",
            "(m|n|nn)a(y|v).": "5",
            "ju(m|n|nn).": "6",
            "ju(l|1|i).": "7",
            "au(g|q).": "8",
            "(5|s)ep.": "9",
            "(o|0)c(7|f|t).": "10",
            "(m|n|nn)(o|0)(v|y).": "11",
            "dec.": "12",

            "(g|q)e((m|n|nn)(m|n|nn)|m|nn)a(l|1|i)(o|0)": "1",
            "(7|f|t)ebbra(l|1|i)(o|0)": "2",
            "(m|n|nn)arz(o|0)": "3",
            "apr(l|1|i)(l|1|i)e": "4",
            "(m|n|nn)a(g|q)(g|q)(l|1|i)(o|0)": "5",
            "(g|q)(l|1|i)u(g|q)n(o|0)": "6",
            "lu(g|q)(l|1|i)(l|1|i)(o|0)": "7",
            "a(g|q)(o|0)(5|s)(7|f|t)(o|0)": "8",
            "(5|s)e(7|f|t)(7|f|t)e(m|n|nn)bre": "9",
            "(o|0)(7|f|t)(7|f|t)(o|0)bre": "10",
            "(m|n|nn)(o|0)ve(m|n|nn)bre": "11",
            "d(l|1|i)ce(m|n|nn)bre": "12",

            "(g|q)e(m|n|nn).": "1",
            "(7|f|t)eb.": "2",
            "(m|n|nn)ar.": "3",
            "apr.": "4",
            "(m|n|nn)a(g|q).": "5",
            "(g|q)(l|1|i)u.": "6",
            "(l|1|i)u(g|q).": "7",
            "a(g|q)(o|0).": "8",
            "(5|s)e(7|f|t).": "9",
            "(o|0)(7|f|t)(7|f|t).": "10",
            "(m|n|nn)(o|0)(y|v).": "11",
            "d(l|1|i)c.": "12"
        }

    def set_color_screen(self, screen):
        self._color_screen = screen

    def set_gray_screen(self, screen):
        self._gray_screen = screen

    def set_scaling_factor(self, scaling_factor):
        self._scaling_factor = scaling_factor

    def set_regexp(self, regexp, args = None, maps={}, performances=[]):
        am = ArgsManager()
        self._regexp = am.get_string(regexp,args,performances, maps, self._crypto_manager)

        a = None

    def _build_regexp(self, string):

        regexp = ""

        for char in string:

            if char in ['a', '4']:
                regexp += '[a4]'
            elif char in ['b', 'h', '6', 'g','8']:
                regexp += '[bh6g8]'
            elif char in ['d', 'o', '0']:
                regexp += '[do0]'
            elif char in ['e', '3']:
                regexp += '[e3]'
            elif char in ['f', 't', '7']:
                regexp += '[ft7]'
            elif char in ['i', 'l', '1','|']:
                regexp += '[il1|]'
            elif char in ['s', '5']:
                regexp += '[s5]'
            elif char in ['z', '2', 'k']:
                regexp += '[z2l1k]'
            else:
                regexp += char

        return regexp

    def _build_month_regexp(self):
        regexp = "("

        for month in self._dict_month:
            regexp += month.replace(".", "\.") + "|"

        regexp = regexp[:-1]
        regexp += ")"

        return regexp

    def _char_to_number(self, string):
        return string.replace("z", "2").replace("s", "5").replace("o", "0").replace(
                "i", "1").replace("l", "1").replace("f","7").replace("t", "7")

    def _get_char_as_number(self):
        return "([0-9]|b|[li]|z|o|e|t|s)"

    def _get_hour_str(self, hour_str):
        reg_number = self._get_char_as_number()

        hour = re.search("(" + reg_number + "{2}:" + reg_number + "{2}:" + reg_number + "{2}.*(pm|am))", hour_str,
                         re.IGNORECASE)

        if hour is not None:
            hour = hour.group(0).replace(" ", "")

            hour = self._char_to_number(hour)

            return (hour, "%I:%M:%S%p")

        hour = re.search("(" + reg_number + "{2}:" + reg_number + "{2}\\." + reg_number + "{2}.*(pm|am))", hour_str,
                         re.IGNORECASE)

        if hour is not None:
            hour = hour.group(0).replace(" ", "")

            hour = self._char_to_number(hour)

            return (hour, "%I:%M:%S%p")

        # europe date
        hour = re.search("(" + reg_number + "{2}:" + reg_number + "{2}:" + reg_number + "{2})", hour_str)

        if hour is not None:
            hour = hour.group(0)

            hour = self._char_to_number(hour)

            return (hour, "%H:%M:%S")

        hour = re.search("(" + reg_number + "{2}:" + reg_number + "{2})", hour_str)

        if hour is not None:
            hour = hour.group(0)

            hour = self._char_to_number(hour)

            return (hour, "%H:%M")

        hour = re.search("(" + reg_number + "{2}:" + reg_number + "{2}." + reg_number + "{2})", hour_str)

        if hour is not None:
            hour = hour.group(0)

            hour = self._char_to_number(hour)

            return (hour, "%H:%M:%S")

        hour = re.search("(" + reg_number + "{6})", hour_str)

        if hour is not None:
            hour = hour.group(0)

            hour = self._char_to_number(hour)

            return (hour, "%H%M%S")

        return ("", "")

    def _get_date_str(self, date_str):

        reg_number = self._get_char_as_number()

        # europe date
        date = re.search("(" + reg_number + "{2}/" + reg_number + "{2}/" + reg_number + "{4})", date_str)

        if date is not None:
            date = date.group(0)

            date = self._char_to_number(date)

            return (date, '%d/%m/%Y')

        month_reg = self._build_month_regexp()

        # date with extended month eu/us
        date = re.search("(" + reg_number + "{1,2} " + month_reg + " " + reg_number + "{4})", date_str)

        if date is not None:

            date = date.group(0)

            arr = date.split(" ")
            day = arr[0]
            month = arr[1]
            year = arr[2]

            day = self._char_to_number(day)
            year = self._char_to_number(year)
            # number_of_month = dict_date[month]

            for month_reg in self._dict_month:
                res = re.search(month_reg, month)

                if res is not None:
                    number_of_month = self._dict_month[month_reg]
                    break

            # date = date.replace(month, number_of_month)

            return (day + " " + number_of_month + " " + year, '%d %m %Y')

        # date with extended month us
        date = re.search("(" + month_reg + " " + reg_number + "{1,2}, " + reg_number + "{4})", date_str)

        if date is not None:

            date = date.group(0)

            arr = date.split(" ")
            day = arr[1].replace(",", "")
            month = arr[0]
            year = arr[2]

            day = self._char_to_number(day)
            year = self._char_to_number(year)
            # number_of_month = dict_date[month]

            for month_reg in self._dict_month:
                res = re.search(month_reg, month)

                if res is not None:
                    number_of_month = self._dict_month[month_reg]
                    break

            return (number_of_month + " " + day + ", " + year, '%m %d, %Y')

        # american date
        date = re.search("(" + reg_number + "{4}/" + reg_number + "{2}/" + reg_number + "{2})", date_str)

        if date is not None:
            date = date.group(0)
            date = self._char_to_number(date)

            return (date, '%Y/%m/%d')

        date = re.search("(" + reg_number + "{8})", date_str)

        if date is not None:
            date = date.group(0)
            date = self._char_to_number(date)
            return (date, "%Y%m%d")

        return ("", "")

    def scrape(self, roi, map_dict=None, logic=None):

        if map_dict is not None:
            result_list = []
            scraped_text = self._find_sub(roi, scrape=True)

            for s_text in scraped_text:

                if s_text.scraped_text != "":

                    for key in map_dict:

                        if len(s_text.scraped_text) >= len(key):

                            regexp = self._build_regexp(key)
                            # regexp = regexp.replace("][","]|[")

                            result = re.match(".*" + regexp + ".*", s_text.scraped_text.replace(' ', ".*"), re.DOTALL | re.IGNORECASE)
                        else:

                            regexp = self._build_regexp(s_text.scraped_text.replace(' ', ".*"))

                            result = re.match(".*" + regexp + ".*", key, re.DOTALL | re.IGNORECASE)

                        if result is not None:
                            result_list.append({"key": key, "score": 0.2})
                            # filter_string = maps_dict[key]

                        #print(key)

                    for result in result_list:
                        #print(result)
                        score = result["score"]
                        best_match = difflib.get_close_matches(s_text.scraped_text, [result["key"]], 1, 0.2)
                        if len(best_match) > 0:
                            score = difflib.SequenceMatcher(None, s_text.scraped_text, best_match[0]).ratio()

                        #perc_len_key_mystr = (100 * len(result["key"])) / len(
                        #    s_text.scraped_text)  # if scores are equal, take also len of string

                        #l1 = len(result["key"])
                        #l2 = len(s_text.scraped_text)

                        diff_len = abs(len(s_text.scraped_text) - len(result["key"]))

                        result["score"] = score - (diff_len / 1000000000000)

                    # best_match = difflib.get_close_matches(my_str,str_list,1,0.2)
                    # score = difflib.SequenceMatcher(None, my_str, best_match).ratio()
                    result_list = sorted(result_list, key=lambda k: k['score'], reverse=True)


                    if len(result_list) > 0:
                        s_text.extract_text = map_dict[result_list[0]["key"]]
                        s_text.check = True

        elif logic is not None:
            if "date" in logic:
                scraped_text = self._find_sub(roi, scrape=True)

                for s_text in scraped_text:

                    if s_text.scraped_text != "":

                        scraped_text_one_space = re.sub(r'\s+', ' ', s_text.scraped_text.lower()).strip()

                        date = self._get_date_str(scraped_text_one_space)

                        hour = self._get_hour_str(scraped_text_one_space)

                        extract_text = ""
                        if date[0] != "" and hour[0] != "":
                            date_time = datetime.datetime.strptime(date[0] + " " + hour[0], date[1] + " " + hour[1])
                            extract_text = date_time.strftime("%Y%m%d%H%M%S")

                        elif date[0] != "" and hour[0] == "":
                            date_time = datetime.datetime.strptime(date[0], date[1])
                            extract_text = date_time.strftime("%Y%m%d%H%M%S")

                        elif date[0] == "" and hour[0] != "":
                            date_time = datetime.datetime.strptime(hour[0], hour[1])
                            date_now = datetime.datetime.now()
                            date_now = date_now.replace(hour=date_time.hour, minute=date_time.minute, second=date_time.second)
                            date_time = date_now
                            extract_text = date_time.strftime("%Y%m%d%H%M%S")

                        if extract_text != "":

                            date_now = datetime.datetime.now()
                            if date_time.hour == 0 and date_time.minute == 0 and date_time.second == 0:
                                date_time = date_time.replace(hour=date_now.hour, minute=date_now.minute,
                                                              second=date_now.second,
                                                              microsecond=date_now.microsecond)

                            if logic == "date_last_hour":
                                if date_time >= date_now - datetime.timedelta(hours=1):
                                    s_text.check = True
                                    s_text.extract_text = extract_text
                            elif logic == "date_last_day":
                                if date_time >= date_now - datetime.timedelta(days=1):
                                    s_text.check = True
                                    s_text.extract_text = extract_text
                            elif logic == "date_last_week":
                                if date_time >= date_now - datetime.timedelta(days=7):
                                    s_text.check = True
                                    s_text.extract_text = extract_text
                            elif logic == "date_last_month":
                                if date_time >= date_now - datetime.timedelta(days=31):
                                    s_text.check = True
                                    s_text.extract_text = extract_text

            elif "number" in logic:
                scraped_text = self._find_sub(roi, scrape=True)

                for s_text in scraped_text:

                    if s_text.scraped_text != "":

                        """
                        scraped_text_one_space = re.sub(r'\s+', ' ', s_text.scraped_text.lower()).strip()

                        result = re.search(r'-\d+', scraped_text_one_space)
                        """
                        result = re.search(r'(-[ ]{0,}\d+|\d+)', s_text.scraped_text)

                        if result is not None:

                            result = result.group(0)

                            int_result = int(result.replace(" ",""))

                            if logic == "number_more_than_zero":
                                if int_result > 0:
                                    s_text.check = True
                                    s_text.extract_text = result


        else:
            scraped_text = self._find_sub(roi, scrape=True)

            for s_text in scraped_text:
                s_text.check = True

        return scraped_text


    def set_scaling_factor(self, scaling_factor):
        self._scaling_factor = scaling_factor


    def find(self, detection, roi=None):

        ret_value = []

        if roi is None:
            ret_value = self._find_main()
        else:
            ret_value = self._find_sub(roi)

        return ret_value

    def _find_main(self):

        source_image = self._color_screen

        objects_found = []

        new_width = int(source_image.shape[1] * self._scale_for_tesseract)
        new_height = int(source_image.shape[0] * self._scale_for_tesseract)
        dim = (new_width, new_height)

        # resize image
        bigger_image = cv2.resize(source_image, dim, interpolation=cv2.INTER_CUBIC)

        bw_matrix = np.zeros((source_image.shape[0], source_image.shape[1], 1), np.uint8)
        bigger_bw_matrix = np.zeros((int(source_image.shape[0] * self._scale_for_tesseract),
                                     int(source_image.shape[1] * self._scale_for_tesseract), 1),
                             np.uint8)

        contouring_manager = ContouringManager(
            canny_threshold1=250 * 0.2,
            canny_threshold2=250 * 0.3,
            canny_apertureSize=3,
            hough_threshold=10,
            hough_minLineLength=30,
            hough_maxLineGap=1,
            line_angle_tolerance=0,
            ellipse_width=2,
            ellipse_height=2,
            text_roi_emptiness=0.45,
            text_roi_proportion=1.3,
            image_roi_emptiness=0.1,
            vline_hw_proportion=2,
            vline_w_maxsize=10,
            hline_wh_proportion=2,
            hline_h_maxsize=10,
            rect_w_minsize=5,
            rect_h_minsize=5,
            rect_w_maxsize_01=800,
            rect_h_maxsize_01=100,
            rect_w_maxsize_02=100,
            rect_h_maxsize_02=800,
            rect_hw_proportion=2,
            rect_hw_w_maxsize=10,
            rect_wh_proportion=2,
            rect_wh_h_maxsize=10,
            hrect_proximity=10,
            vrect_proximity=10,
            vrect_others_proximity=40,
            hrect_others_proximity=80)

        contouring_manager.auto_contouring(source_image)

        boxes = contouring_manager.getTextBoxes()

        # loop over the bounding boxes
        for (x, y, w, h) in boxes:
            endX = x + w

            endY = y + h

            # draw the bounding box on the image
            #cv2.rectangle(orig, (x, y), (endX, endY), (0, 255, 0), 2)
            cv2.rectangle(bw_matrix, (x + 2, y + 2), (endX - 4, endY - 4), (255, 255, 255), -1)

        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (55, 3))
        dilation = cv2.dilate(bw_matrix, rect_kernel, iterations=1)

        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        boundingBoxes = [cv2.boundingRect(c) for c in contours]

        (contours, boundingBoxes) = zip(*sorted(zip(contours, boundingBoxes),
                                                key=lambda b: b[1][1], reverse=False))

        cnt = 0
        # print main_rect.min_width, main_rect.max_width, main_rect.min_height, main_rect.max_height
        # For each contour, find the bounding rectangle and draw it
        t0 = time.time()
        # with PyTessBaseAPI(path='D:\\python\\tessdata\\tessdata400', lang='eng') as api:
        image_pil = Image.fromarray(cv2.cvtColor(bigger_image, cv2.COLOR_BGR2RGB).astype('uint8'))

        (H, W) = source_image.shape[:2]

        # with PyTessBaseAPI(path='C:\\ProgramData\\python36\\tessdata', lang='eng') as api:
        with tesserocr.PyTessBaseAPI(path=self._tessdata_path, lang='eng') as api:

            api.SetImage(image_pil)
            api.SetPageSegMode(tesserocr.PSM.AUTO)
            cnt = 0

            text_list = []
            results = []
            text = ""

            for box in boundingBoxes:
                x, y, w, h = box
                x = x * self._scale_for_tesseract
                y = y * self._scale_for_tesseract
                w = w * self._scale_for_tesseract
                h = h * self._scale_for_tesseract

                x = x - 2 * self._scale_for_tesseract
                w = w + 7 * self._scale_for_tesseract

                y = y - 2 * self._scale_for_tesseract
                h = h + 7 * self._scale_for_tesseract

                # end_x = x+w
                # end_y = y+h

                if h > H * self._scale_for_tesseract:
                    h = H * self._scale_for_tesseract

                if w > W * self._scale_for_tesseract:
                    w = W * self._scale_for_tesseract

                if x < 0:
                    x = 0

                if y < 0:
                    y = 0

                api.SetRectangle(x, y, w, h)

                # crop = image_3[y:end_y, x:end_x]
                # if len(crop) == 0:
                #	continue
                # cv2.imwrite("crop_"+str(cnt)+".png", crop)

                # ocrResult = api.GetUTF8Text()
                # ocrResult = api.G
                api.Recognize()
                ri = api.GetIterator()
                level = tesserocr.RIL.WORD

                #boxes = api.GetComponentImages(tesserocr.RIL.TEXTLINE, True)

                # print('Found {} textline image components.'.format(len(boxes)))
                i = 0
                for r in tesserocr.iterate_level(ri, level):
                    try:
                        symbol = r.GetUTF8Text(level)
                    except:
                        continue

                    conf = r.Confidence(level)
                    if conf > 45:
                        pass #print('Word: {}'.format(symbol))
                    else:
                        continue
                    bbox = r.BoundingBoxInternal(level)
                    # im = Image.fromarray(img[bbox[1]:bbox[3], bbox[0]:bbox[2]])
                    # im.save("../out/" + str(i) + ".tif")

                    bbox = (int((bbox[0] + x) / self._scale_for_tesseract),
                            int((bbox[1] + y) / self._scale_for_tesseract),
                            int(bbox[2] / self._scale_for_tesseract),
                            int(bbox[3] / self._scale_for_tesseract))

                    text_list.append(((bbox), symbol, conf))
                    text += " " + symbol

                    result = re.match(".*" + self._regexp + ".*", text, re.DOTALL | re.IGNORECASE)

                    if result is not None:
                        text_for_result = ""
                        boxes_for_result = []

                        for box in reversed(text_list):

                            text_for_result = box[1] + " " + text_for_result
                            boxes_for_result.append(box)

                            result2 = re.match(".*" + self._regexp + ".*", text_for_result,
                                               re.DOTALL | re.IGNORECASE)

                            if result2 is not None:
                                boxes_for_result = boxes_for_result[::-1]  # reverse array
                                text_list = []
                                text = ""
                                #results.append(boxes_for_result) all words of a result

                                first_word = boxes_for_result[0]
                                bounding_box = first_word[0]
                                return_value = Result()
                                return_value.x = bounding_box[0]
                                return_value.y = bounding_box[1]
                                return_value.w = bounding_box[2]
                                return_value.h = bounding_box[3]

                                objects_found.append(return_value)

                                break

                        a = "bb"
                        pass

                    i += 1
                # print(ocrResult)
                cnt += 1

        end_T = time.time() - t0

        return objects_found

    def _find_sub(self, roi, scrape=False):

        offset_x = 0
        offset_y = 0

        objects_found = []
        scraped_words = []

        source_img_h, source_img_w = self._gray_screen.shape

        y1 = roi.y
        y2 = y1 + roi.h

        x1 = roi.x
        x2 = x1 + roi.w

        if roi.unlimited_up is True:
            y1 = 0
            y2 = roi.y + roi.h

        if roi.unlimited_down is True:
            y2 = source_img_h

        if roi.unlimited_left is True:
            x1 = 0
            x2 = roi.x + roi.w

        if roi.unlimited_right is True:
            x2 = source_img_w

        if y1 < 0:
            y1 = 0
        elif y1 > source_img_h:
            y1 = source_img_h

        if y2 < 0:
            y2 = 0
        elif y2 > source_img_h:
            y2 = source_img_h

        if x1 < 0:
            x1 = 0
        elif x1 > source_img_w:
            x1 = source_img_w

        if x2 < 0:
            x2 = 0
        elif x2 > source_img_w:
            x2 = source_img_w

        offset_x = x1
        offset_y = y1

        source_image = self._color_screen[y1:y2, x1:x2]

        new_width = int(source_image.shape[1] * self._scale_for_tesseract)
        new_height = int(source_image.shape[0] * self._scale_for_tesseract)
        dim = (new_width, new_height)
        #cv2.imwrite("D:\\alyvix_testcase\\test3.png", source_image)

        # resize image
        try:
            bigger_image = cv2.resize(source_image, dim, interpolation=cv2.INTER_CUBIC)
            #cv2.imwrite("D:\\alyvix_testcase\\test3_2.png", bigger_image)
        except:
            return_value = Result()
            return_value.x = 0 #offset_x + 0
            return_value.y = 0 #offset_y + 0
            return_value.w = 0 #roi.w - 0
            return_value.h = 0 #roi.h - 0
            return_value.scraped_text = ""
            objects_found.append(return_value)

            return objects_found

        t0 = time.time()
        # with PyTessBaseAPI(path='D:\\python\\tessdata\\tessdata400', lang='eng') as api:
        image_pil = Image.fromarray(cv2.cvtColor(bigger_image, cv2.COLOR_BGR2RGB).astype('uint8'))

        text = ""
        text_for_finder = ""

        obj_found = True

        # with PyTessBaseAPI(path='C:\\ProgramData\\python36\\tessdata', lang='eng') as api:
        with tesserocr.PyTessBaseAPI(path=self._tessdata_path, lang='eng') as api:

            api.SetImage(image_pil)
            api.SetPageSegMode(tesserocr.PSM.AUTO)
            cnt = 0

            text_list = []
            results = []


            api.Recognize()
            ri = api.GetIterator()
            level = tesserocr.RIL.WORD
            #level = tesserocr.RIL.SYMBOL

            #boxes = api.GetComponentImages(tesserocr.RIL.TEXTLINE, True)

            # print('Found {} textline image components.'.format(len(boxes)))
            i = 0
            for r in tesserocr.iterate_level(ri, level):
                try:
                    symbol = r.GetUTF8Text(level)
                    #print(symbol)
                except:
                    continue

                conf = r.Confidence(level)
                #print(str(conf))

                """
                if conf > 45:
                    pass #print('Word: {}'.format(symbol))
                else:
                    continue
                """

                bbox = r.BoundingBoxInternal(level)
                # im = Image.fromarray(img[bbox[1]:bbox[3], bbox[0]:bbox[2]])
                # im.save("../out/" + str(i) + ".tif")

                bbox = (int((bbox[0]) / self._scale_for_tesseract),
                        int((bbox[1]) / self._scale_for_tesseract),
                        int(bbox[2] / self._scale_for_tesseract),
                        int(bbox[3] / self._scale_for_tesseract))

                symbol = symbol.replace("—", "-")
                text_list.append(((bbox), symbol, conf))
                text += " " + symbol
                text_for_finder += " " + symbol

                if scrape is False:
                    result = re.search(self._regexp, text_for_finder, re.DOTALL | re.IGNORECASE)

                    if result is not None:
                        text_for_result = ""
                        boxes_for_result = []

                        for box in reversed(text_list):

                            text_for_result = box[1] + " " + text_for_result
                            boxes_for_result.append(box)

                            result2 = re.match(".*" + self._regexp, text_for_result + ".*",
                                               re.DOTALL | re.IGNORECASE)

                            if result2 is not None:
                                boxes_for_result = boxes_for_result[::-1]  # reverse array
                                text_list = []
                                text_for_finder = ""
                                #results.append(boxes_for_result) all words of a result

                                first_word = boxes_for_result[0]
                                bounding_box = first_word[0]
                                return_value = Result()
                                return_value.x = offset_x + bounding_box[0]
                                return_value.y = offset_y + bounding_box[1]
                                return_value.w = bounding_box[2] - bounding_box[0]
                                return_value.h = bounding_box[3] - bounding_box[1]
                                return_value.extract_text = result.group(0)



                                objects_found.append(return_value)

                                break

                        a = "bb"
                        pass

                else:
                    scraped_words.append(bbox)
                #scraped_words.append(bbox)
                i += 1
            # print(ocrResult)
            cnt += 1

        end_T = time.time() - t0


        if scrape is True:
            x1 = 999999999
            y1 = 999999999
            x2 = 0
            y2 = 0

            if len(scraped_words) == 0:
                return_value = Result()
                return_value.x = 0 #offset_x + 0
                return_value.y = 0 #offset_y + 0
                return_value.w = 0 #roi.w - 0
                return_value.h = 0 #roi.h - 0
                return_value.scraped_text = text.lstrip().rstrip()
                objects_found.append(return_value)
            else:
                for word in scraped_words:

                    if word[2] + 5 > roi.w and word[3] + 5 > roi.h and word[0] - 5 < roi.x and word[1] - 5 < roi.y:
                        continue

                    if word[0] < x1:
                        x1 = word[0]

                    if word[1] < y1:
                        y1 = word[1]

                    if word[2] > x2:
                        x2 = word[2]

                    if word[3] > y2:
                        y2 = word[3]

                return_value = Result()
                return_value.x = offset_x + x1
                return_value.y = offset_y + y1
                return_value.w = x2 - x1
                return_value.h = y2 - y1
                return_value.scraped_text = text.lstrip().rstrip()
                objects_found.append(return_value)

            return objects_found
        else:


            if len(objects_found) > 0:
                for obj_found in objects_found:
                    obj_found.scraped_text = text.lstrip().rstrip()

            else:
                return_value = Result()
                return_value.x = 0 #offset_x + 0
                return_value.y = 0 #offset_y + 0
                return_value.w = 0 #roi.w - 0
                return_value.h = 0 #roi.h - 0
                return_value.scraped_text = text.lstrip().rstrip()
                objects_found.append(return_value)

            return objects_found