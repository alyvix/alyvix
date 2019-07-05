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
import tesserocr
from PIL import Image
from alyvix.tools.screen import ScreenManager
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

class TextManager():

    def __init__(self):

        self._color_screen = None
        self._gray_screen = None
        self._scaling_factor = None

        self._scale_for_tesseract = 1.7

        self._regexp = ""

        self._arguments = None

        self._tessdata_path = os.path.dirname(__file__) + os.sep + "tessdata"

    def set_color_screen(self, screen):
        self._color_screen = screen

    def set_gray_screen(self, screen):
        self._gray_screen = screen

    def set_scaling_factor(self, scaling_factor):
        self._scaling_factor = scaling_factor

    def set_regexp(self, regexp, args = None):
        self._regexp = regexp

        args_in_string = re.findall("\\{[0-9]+\\}", self._regexp, re.IGNORECASE)

        for arg_pattern in args_in_string:

            try:
                i = int(arg_pattern.lower().replace("{", "").replace("}", ""))

                self._regexp = self._regexp.replace(arg_pattern, args[i - 1])
            except:
                pass  # not enought arguments

    def scrape(self, roi):

        scraped_text = self._find_sub(roi, scrape=True)

        return scraped_text

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

        # resize image
        bigger_image = cv2.resize(source_image, dim, interpolation=cv2.INTER_CUBIC)


        t0 = time.time()
        # with PyTessBaseAPI(path='D:\\python\\tessdata\\tessdata400', lang='eng') as api:
        image_pil = Image.fromarray(cv2.cvtColor(bigger_image, cv2.COLOR_BGR2RGB).astype('uint8'))

        text = ""

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

                text_list.append(((bbox), symbol, conf))
                text += " " + symbol

                if scrape is False:
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
                                return_value.x = offset_x + bounding_box[0]
                                return_value.y = offset_y + bounding_box[1]
                                return_value.w = bounding_box[2] - bounding_box[0]
                                return_value.h = bounding_box[3] - bounding_box[1]

                                objects_found.append(return_value)

                                break

                        a = "bb"
                        pass

                else:
                    scraped_words.append(bbox)
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
                return_value.scraped_text = text
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
                return_value.scraped_text = text
                objects_found.append(return_value)

            return objects_found
        else:
            return objects_found